from __future__ import annotations

import asyncio
import hashlib
import json
import time
import uuid
from typing import Any

from app.db import (
    create_rag_eval_case,
    current_knowledge_revision,
    get_exact_knowledge_cache,
    list_accessible_asset_versions,
    list_knowledge_cache_candidates,
    list_rag_eval_cases,
    mark_knowledge_cache_hit,
    save_knowledge_query_cache,
    save_rag_eval_run,
    user_can_read_asset,
)
from app.embedding_runtime import (
    EMBEDDING_MODEL,
    cosine_similarity,
    embed_query,
    hybrid_search_knowledge_chunks,
    pack_embedding,
    unpack_embedding,
)
from app.rag_cache import normalize_query

KNOWLEDGE_PROMPT_VERSION = "knowledge-rag-v1"
KNOWLEDGE_RETRIEVAL_VERSION = "hybrid-acl-v1"
SEMANTIC_CACHE_THRESHOLD = 0.80
VALID_SCOPES = {"all_accessible", "mine", "company", "group", "selected"}


def normalize_scope(payload: dict[str, Any]) -> dict[str, Any]:
    scope = str(payload.get("scope") or "all_accessible")
    if scope not in VALID_SCOPES:
        raise ValueError("Invalid knowledge scope")
    asset_ids = sorted({int(item) for item in payload.get("asset_ids") or []})
    group_id = payload.get("group_id")
    return {
        "scope": scope,
        "asset_ids": asset_ids,
        "group_id": int(group_id) if group_id not in (None, "") else None,
    }


async def knowledge_context(user: dict[str, Any], scope: dict[str, Any]) -> dict[str, Any]:
    revision, assets = await asyncio.gather(
        asyncio.to_thread(current_knowledge_revision),
        asyncio.to_thread(
            list_accessible_asset_versions,
            user_id=user["id"],
            role=user["role"],
        ),
    )
    permission_payload = [
        {
            "id": item["id"],
            "content": item["content_version"],
            "index": item["index_version"],
            "visibility": item["visibility"],
            "group": item["owner_group_id"],
        }
        for item in assets
    ]
    canonical_scope = json.dumps(scope, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    canonical_permissions = json.dumps(
        permission_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return {
        "knowledge_revision": revision,
        "scope_json": canonical_scope,
        "scope_digest": _digest(canonical_scope),
        "permission_digest": _digest(canonical_permissions),
        "accessible_asset_count": len(assets),
    }


async def search_knowledge(
    *,
    user: dict[str, Any],
    question: str,
    scope: dict[str, Any],
    limit: int = 8,
    query_vector: list[float] | None = None,
) -> list[dict[str, Any]]:
    return await hybrid_search_knowledge_chunks(
        user_id=user["id"],
        role=user["role"],
        query=question,
        scope=scope["scope"],
        asset_ids=scope["asset_ids"],
        group_id=scope["group_id"],
        limit=limit,
        query_vector=query_vector,
    )


async def lookup_knowledge_cache(
    *,
    user: dict[str, Any],
    model_id: str,
    question: str,
    scope: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[float] | None, dict[str, Any]]:
    context = await knowledge_context(user, scope)
    normalized = normalize_query(question)
    cache_key = _cache_key(user["id"], model_id, normalized, context)
    exact = await asyncio.to_thread(get_exact_knowledge_cache, cache_key)
    if exact:
        await asyncio.to_thread(mark_knowledge_cache_hit, exact["id"])
        return _deserialize_cache(exact, "exact", 1.0), None, context

    query_vector = await embed_query(question, user["id"])
    if query_vector is None:
        return None, None, context
    candidates = await asyncio.to_thread(
        list_knowledge_cache_candidates,
        user_id=user["id"],
        model_id=model_id,
        scope_digest=context["scope_digest"],
        permission_digest=context["permission_digest"],
        knowledge_revision=context["knowledge_revision"],
        prompt_version=KNOWLEDGE_PROMPT_VERSION,
        retrieval_version=KNOWLEDGE_RETRIEVAL_VERSION,
    )
    best: tuple[float, dict[str, Any]] | None = None
    for candidate in candidates:
        similarity = cosine_similarity(query_vector, unpack_embedding(candidate.get("query_embedding")))
        if similarity is None or similarity < SEMANTIC_CACHE_THRESHOLD:
            continue
        if best is None or similarity > best[0]:
            best = (similarity, candidate)
    if best is None:
        return None, query_vector, context
    similarity, candidate = best
    await asyncio.to_thread(mark_knowledge_cache_hit, candidate["id"])
    return _deserialize_cache(candidate, "semantic", similarity), query_vector, context


async def store_knowledge_cache(
    *,
    user: dict[str, Any],
    model_id: str,
    question: str,
    scope: dict[str, Any],
    context: dict[str, Any],
    query_vector: list[float] | None,
    result: dict[str, Any],
    contexts: list[dict[str, Any]],
) -> None:
    normalized = normalize_query(question)
    await asyncio.to_thread(
        save_knowledge_query_cache,
        cache_key=_cache_key(user["id"], model_id, normalized, context),
        user_id=user["id"],
        model_id=model_id,
        query_text=question,
        normalized_query=normalized,
        query_embedding=pack_embedding(query_vector) if query_vector else None,
        embedding_model=EMBEDDING_MODEL if query_vector else None,
        scope_json=context["scope_json"],
        scope_digest=context["scope_digest"],
        permission_digest=context["permission_digest"],
        knowledge_revision=context["knowledge_revision"],
        prompt_version=KNOWLEDGE_PROMPT_VERSION,
        retrieval_version=KNOWLEDGE_RETRIEVAL_VERSION,
        result_json=json.dumps(result, ensure_ascii=False),
        contexts_json=json.dumps(contexts, ensure_ascii=False),
    )


def serialize_knowledge_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    serialized = []
    for chunk in chunks:
        item = {key: value for key, value in chunk.items() if key != "embedding"}
        if item.get("image_path"):
            item["image_url"] = (
                f"/api/nas-assets/{item['asset_id']}/chunk-images/{item['id']}"
            )
        try:
            item["metadata"] = json.loads(item.get("metadata_json") or "{}")
        except json.JSONDecodeError:
            item["metadata"] = {}
        serialized.append(item)
    return serialized


async def create_eval_case(payload: dict[str, Any], admin: dict[str, Any]) -> dict[str, Any]:
    question = str(payload.get("question") or "").strip()
    if not question:
        raise ValueError("Question is required")
    expected_assets = sorted({int(item) for item in payload.get("expected_asset_ids") or []})
    expected_keywords = [str(item).strip() for item in payload.get("expected_keywords") or [] if str(item).strip()]
    scope = normalize_scope(payload.get("scope") or {})
    return await asyncio.to_thread(
        create_rag_eval_case,
        question=question,
        expected_asset_ids_json=json.dumps(expected_assets),
        expected_keywords_json=json.dumps(expected_keywords, ensure_ascii=False),
        reference_answer=str(payload.get("reference_answer") or "").strip() or None,
        scope_json=json.dumps(scope, ensure_ascii=False),
        created_by=admin["id"],
    )


async def run_evaluation(admin: dict[str, Any]) -> dict[str, Any]:
    cases = await asyncio.to_thread(list_rag_eval_cases, active_only=True)
    run_group = uuid.uuid4().hex
    results = []
    for case in cases:
        started = time.perf_counter()
        scope = normalize_scope(json.loads(case["scope_json"]))
        chunks = await search_knowledge(
            user=admin,
            question=case["question"],
            scope=scope,
            limit=5,
        )
        expected_assets = set(json.loads(case["expected_asset_ids_json"] or "[]"))
        expected_keywords = json.loads(case["expected_keywords_json"] or "[]")
        retrieved_assets = [int(chunk["asset_id"]) for chunk in chunks]
        found_assets = expected_assets.intersection(retrieved_assets)
        recall = len(found_assets) / len(expected_assets) if expected_assets else 1.0
        first_rank = next(
            (index for index, asset_id in enumerate(retrieved_assets, start=1) if asset_id in expected_assets),
            None,
        )
        reciprocal_rank = 1.0 / first_rank if first_rank else (1.0 if not expected_assets else 0.0)
        retrieved_text = "\n".join(str(chunk.get("content") or "") for chunk in chunks).casefold()
        matched_keywords = sum(1 for keyword in expected_keywords if keyword.casefold() in retrieved_text)
        keyword_score = matched_keywords / len(expected_keywords) if expected_keywords else 1.0
        citation_valid = int(all(chunk.get("id") and chunk.get("asset_id") for chunk in chunks))
        permission_checks = await asyncio.gather(
            *[
                asyncio.to_thread(
                    user_can_read_asset,
                    asset_id,
                    user_id=admin["id"],
                    role=admin["role"],
                )
                for asset_id in set(retrieved_assets)
            ]
        )
        permission_leak = int(not all(permission_checks))
        latency_ms = round((time.perf_counter() - started) * 1000)
        saved = await asyncio.to_thread(
            save_rag_eval_run,
            case_id=case["id"],
            run_group=run_group,
            retrieval_version=KNOWLEDGE_RETRIEVAL_VERSION,
            model_id=None,
            retrieved_chunks_json=json.dumps(serialize_knowledge_chunks(chunks), ensure_ascii=False),
            answer=None,
            recall_at_5=recall,
            reciprocal_rank=reciprocal_rank,
            keyword_score=keyword_score,
            citation_valid=citation_valid,
            permission_leak=permission_leak,
            latency_ms=latency_ms,
        )
        results.append(saved)
    return {
        "run_group": run_group,
        "case_count": len(results),
        "recall_at_5": _average(results, "recall_at_5"),
        "mrr": _average(results, "reciprocal_rank"),
        "keyword_score": _average(results, "keyword_score"),
        "citation_accuracy": _average(results, "citation_valid"),
        "permission_leaks": sum(int(item["permission_leak"]) for item in results),
        "average_latency_ms": _average(results, "latency_ms"),
        "results": results,
    }


def _cache_key(user_id: int, model_id: str, normalized: str, context: dict[str, Any]) -> str:
    payload = "|".join(
        [
            str(user_id), model_id, normalized, context["scope_digest"],
            context["permission_digest"], str(context["knowledge_revision"]),
            KNOWLEDGE_PROMPT_VERSION, KNOWLEDGE_RETRIEVAL_VERSION,
        ]
    )
    return _digest(payload)


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
            "knowledge_revision": row["knowledge_revision"],
        },
    }


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _average(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return round(sum(float(row[key]) for row in rows) / len(rows), 4)
