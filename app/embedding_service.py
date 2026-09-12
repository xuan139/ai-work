from __future__ import annotations

import os
import threading
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
MODEL_ALIAS = os.getenv("EMBEDDING_MODEL_ALIAS", "qwen3-embedding-0.6b")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "4"))
MAX_BATCH_ITEMS = int(os.getenv("EMBEDDING_MAX_BATCH_ITEMS", "64"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    from sentence_transformers import SentenceTransformer

    started_at = time.monotonic()
    app.state.model = SentenceTransformer(
        MODEL_NAME,
        device="cpu",
        truncate_dim=EMBEDDING_DIMENSION,
    )
    app.state.inference_lock = threading.Lock()
    app.state.loaded_in_seconds = round(time.monotonic() - started_at, 2)
    yield


app = FastAPI(title="NAS Qwen3 Embedding Service", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model": MODEL_ALIAS,
        "source_model": MODEL_NAME,
        "device": "cpu",
        "dimension": EMBEDDING_DIMENSION,
        "loaded_in_seconds": app.state.loaded_in_seconds,
    }


@app.get("/v1/models")
async def models() -> dict[str, Any]:
    return {
        "object": "list",
        "data": [{"id": MODEL_ALIAS, "object": "model", "owned_by": "local-nas"}],
    }


@app.post("/v1/embeddings")
def embeddings(payload: dict[str, Any]) -> dict[str, Any]:
    values = payload.get("input")
    texts = [values] if isinstance(values, str) else values
    if not isinstance(texts, list) or not texts or not all(isinstance(item, str) and item.strip() for item in texts):
        raise HTTPException(status_code=400, detail="input must be a non-empty string or string array")
    if len(texts) > MAX_BATCH_ITEMS:
        raise HTTPException(status_code=400, detail=f"batch exceeds {MAX_BATCH_ITEMS} items")

    input_type = str(payload.get("input_type", "document")).lower()
    if input_type not in {"query", "document"}:
        raise HTTPException(status_code=400, detail="input_type must be query or document")

    encode_options: dict[str, Any] = {
        "batch_size": BATCH_SIZE,
        "show_progress_bar": False,
        "normalize_embeddings": True,
        "convert_to_numpy": True,
    }
    if input_type == "query":
        encode_options["prompt_name"] = "query"

    with app.state.inference_lock:
        vectors = app.state.model.encode(texts, **encode_options)
    data = [
        {"object": "embedding", "index": index, "embedding": vector.tolist()}
        for index, vector in enumerate(vectors)
    ]
    return {
        "object": "list",
        "model": MODEL_ALIAS,
        "data": data,
        "usage": {"prompt_tokens": None, "total_tokens": None},
    }
