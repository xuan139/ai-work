from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from app.db import (
    get_exact_rag_cache,
    list_rag_cache_candidates,
    mark_rag_cache_hit,
    save_rag_query_cache,
)
from app.embedding_runtime import EMBEDDING_MODEL, cosine_similarity, embed_query, pack_embedding, unpack_embedding

SEMANTIC_CACHE_THRESHOLD = 0.76


def normalize_query(query: str) -> str:
    return re.sub(r"[^\w]+", "", query.casefold(), flags=re.UNICODE)


async def lookup_rag_cache(
    *,
    asset_id: int,
    model_id: str,
    question: str,
    user_id: int,
) -> tuple[dict[str, Any] | None, list[float] | None]:
    normalized = normalize_query(question)
    exact = await asyncio.to_thread(get_exact_rag_cache, asset_id, model_id, normalized)
    if exact:
        await asyncio.to_thread(mark_rag_cache_hit, exact["id"])
        return _deserialize_cache(exact, "exact", 1.0), None

    query_vector = await embed_query(question, user_id)
    if query_vector is None:
        return None, None

    candidates = await asyncio.to_thread(list_rag_cache_candidates, asset_id, model_id)
    best: tuple[float, dict[str, Any]] | None = None
    for candidate in candidates:
        similarity = cosine_similarity(query_vector, unpack_embedding(candidate.get("query_embedding")))
        if similarity is None or similarity < SEMANTIC_CACHE_THRESHOLD:
            continue
        if best is None or similarity > best[0]:
            best = (similarity, candidate)
    if best is None:
        return None, query_vector

    similarity, candidate = best
    await asyncio.to_thread(mark_rag_cache_hit, candidate["id"])
    return _deserialize_cache(candidate, "semantic", similarity), query_vector


async def store_rag_cache(
    *,
    asset_id: int,
    user_id: int,
    model_id: str,
    question: str,
    query_vector: list[float] | None,
    result: dict[str, Any],
    contexts: list[dict[str, Any]],
) -> None:
    await asyncio.to_thread(
        save_rag_query_cache,
        asset_id=asset_id,
        user_id=user_id,
        model_id=model_id,
        query_text=question,
        normalized_query=normalize_query(question),
        query_embedding=pack_embedding(query_vector) if query_vector else None,
        embedding_model=EMBEDDING_MODEL if query_vector else None,
        result_json=json.dumps(result, ensure_ascii=False),
        contexts_json=json.dumps(contexts, ensure_ascii=False),
    )


def _deserialize_cache(row: dict[str, Any], match_type: str, similarity: float) -> dict[str, Any]:
    return {
        "result": json.loads(row["result_json"]),
        "contexts": json.loads(row["contexts_json"]),
        "cache": {
            "hit": True,
            "match_type": match_type,
            "similarity": round(similarity, 4),
            "original_question": row["query_text"],
            "original_created_at": row["created_at"],
            "hit_count": int(row["hit_count"] or 0) + 1,
        },
    }
