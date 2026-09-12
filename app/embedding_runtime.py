from __future__ import annotations

import asyncio
import json
import math
import os
import re
import urllib.error
import urllib.request
from array import array
from typing import Any

from app.db import create_llm_call, list_chunks_missing_embedding, list_document_chunks, update_chunk_embeddings

EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://127.0.0.1:8081").rstrip("/")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL_ALIAS", "qwen3-embedding-0.6b")
SEMANTIC_WEIGHT = 0.75
KEYWORD_WEIGHT = 0.25
REQUEST_BATCH_SIZE = 4


class EmbeddingRuntimeError(RuntimeError):
    pass


def pack_embedding(values: list[float]) -> bytes:
    vector = array("f", values)
    if vector.itemsize != 4:
        raise EmbeddingRuntimeError("unexpected float32 storage size")
    return vector.tobytes()


def unpack_embedding(value: bytes | None) -> list[float] | None:
    if not value:
        return None
    vector = array("f")
    vector.frombytes(value)
    return vector.tolist()


def request_embeddings(texts: list[str], input_type: str, user_id: int | None = None) -> list[list[float]]:
    vectors: list[list[float]] = []
    try:
        for start in range(0, len(texts), REQUEST_BATCH_SIZE):
            vectors.extend(_request_embedding_batch(texts[start : start + REQUEST_BATCH_SIZE], input_type))
    except EmbeddingRuntimeError as exc:
        _record_embedding_call(user_id, texts, input_type, None, str(exc))
        raise
    _record_embedding_call(user_id, texts, input_type, vectors, None)
    return vectors


def _request_embedding_batch(texts: list[str], input_type: str) -> list[list[float]]:
    payload = json.dumps(
        {"model": EMBEDDING_MODEL, "input": texts, "input_type": input_type},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{EMBEDDING_BASE_URL}/v1/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EmbeddingRuntimeError(f"embedding service unavailable: {exc}") from exc

    rows = result.get("data") if isinstance(result, dict) else None
    if not isinstance(rows, list):
        raise EmbeddingRuntimeError("embedding service returned invalid data")
    ordered = sorted(rows, key=lambda item: item.get("index", 0))
    vectors = [item.get("embedding") for item in ordered]
    if len(vectors) != len(texts) or not all(isinstance(vector, list) and vector for vector in vectors):
        raise EmbeddingRuntimeError("embedding count does not match input count")
    return vectors


def embedding_service_status() -> dict[str, Any]:
    request = urllib.request.Request(f"{EMBEDDING_BASE_URL}/health", method="GET")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "model": EMBEDDING_MODEL, "error": str(exc)}


async def attach_embeddings(chunks: list[dict[str, Any]], user_id: int | None = None) -> bool:
    if not chunks:
        return True
    try:
        vectors = await asyncio.to_thread(
            request_embeddings,
            [chunk["content"] for chunk in chunks],
            "document",
            user_id,
        )
    except EmbeddingRuntimeError:
        return False
    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk["embedding"] = pack_embedding(vector)
        chunk["embedding_model"] = EMBEDDING_MODEL
    return True


async def backfill_missing_embeddings(batch_size: int = 4) -> int:
    missing = await asyncio.to_thread(list_chunks_missing_embedding, batch_size)
    if not missing:
        return 0
    grouped: dict[int, list[dict[str, Any]]] = {}
    for chunk in missing:
        grouped.setdefault(chunk["user_id"], []).append(chunk)
    updates = []
    for user_id, user_chunks in grouped.items():
        vectors = await asyncio.to_thread(
            request_embeddings,
            [chunk["content"] for chunk in user_chunks],
            "document",
            user_id,
        )
        updates.extend(
            {"id": chunk["id"], "embedding": pack_embedding(vector), "embedding_model": EMBEDDING_MODEL}
            for chunk, vector in zip(user_chunks, vectors, strict=True)
        )
    await asyncio.to_thread(update_chunk_embeddings, updates)
    return len(updates)


async def embedding_backfill_loop() -> None:
    while True:
        try:
            processed = await backfill_missing_embeddings()
            await asyncio.sleep(1 if processed else 30)
        except EmbeddingRuntimeError:
            await asyncio.sleep(30)


async def hybrid_search_document_chunks(
    asset_id: int,
    query: str,
    limit: int = 5,
    user_id: int | None = None,
    query_vector: list[float] | None = None,
) -> list[dict[str, Any]]:
    chunks = await asyncio.to_thread(list_document_chunks, asset_id)
    if not chunks:
        return []

    if query_vector is None:
        query_vector = await embed_query(query, user_id)

    keyword_scores = [_keyword_score(query, chunk["content"]) for chunk in chunks]
    max_keyword = max(keyword_scores, default=0.0)
    scored: list[tuple[float, dict[str, Any]]] = []
    for chunk, keyword_raw in zip(chunks, keyword_scores, strict=True):
        document_vector = unpack_embedding(chunk.get("embedding"))
        semantic_score = cosine_similarity(query_vector, document_vector)
        keyword_score = keyword_raw / max_keyword if max_keyword else 0.0
        if semantic_score is None:
            combined = keyword_score
            method = "keyword"
        else:
            semantic_score = max(0.0, semantic_score)
            combined = SEMANTIC_WEIGHT * semantic_score + KEYWORD_WEIGHT * keyword_score
            method = "hybrid"
        item = dict(chunk)
        item["retrieval_method"] = method
        item["retrieval_score"] = round(combined, 4)
        item["semantic_score"] = round(semantic_score, 4) if semantic_score is not None else None
        item["keyword_score"] = round(keyword_score, 4)
        scored.append((combined, item))

    scored.sort(key=lambda item: (-item[0], item[1]["chunk_index"]))
    return [chunk for _, chunk in scored[:limit]]


async def embed_query(query: str, user_id: int | None = None) -> list[float] | None:
    try:
        return (await asyncio.to_thread(request_embeddings, [query], "query", user_id))[0]
    except EmbeddingRuntimeError:
        return None


def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float | None:
    if not left or not right or len(left) != len(right):
        return None
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return None
    return dot / (left_norm * right_norm)


def _keyword_score(query: str, content: str) -> float:
    query_terms = _search_terms(query)
    if not query_terms:
        return 0.0
    normalized = content.lower()
    return float(sum(normalized.count(term) * max(1, len(term)) for term in query_terms))


def _search_terms(text: str) -> list[str]:
    normalized = text.lower()
    terms = set(re.findall(r"[a-z0-9][a-z0-9_.+-]*", normalized))
    for sequence in re.findall(r"[\u3400-\u9fff]+", normalized):
        if len(sequence) == 1:
            terms.add(sequence)
        else:
            terms.update(sequence[index : index + 2] for index in range(len(sequence) - 1))
    return sorted(terms)


def _record_embedding_call(
    user_id: int | None,
    texts: list[str],
    input_type: str,
    vectors: list[list[float]] | None,
    error: str | None,
) -> None:
    if user_id is None:
        return
    dimension = len(vectors[0]) if vectors else None
    output = None
    if vectors is not None:
        output = json.dumps(
            {
                "vector_count": len(vectors),
                "dimension": dimension,
                "storage": "document_chunks.embedding" if input_type == "document" else "request_memory",
            },
            ensure_ascii=False,
        )
    create_llm_call(
        user_id=user_id,
        provider="Local NAS",
        model_name="Qwen3-Embedding-0.6B",
        model_id="local:qwen3-embedding-0.6b",
        prompt=json.dumps({"input_type": input_type, "input": texts}, ensure_ascii=False),
        response=output,
        status="failed" if error else "success",
        access_mode="local_nas",
        error_message=error,
        raw_usage_json=json.dumps(
            {"input_count": len(texts), "dimension": dimension, "normalized": True},
            ensure_ascii=False,
        ),
    )
