from __future__ import annotations

import asyncio
import hashlib
import json
import time
import uuid
import re
from collections.abc import Awaitable, Callable
from typing import Any

from app.db import (
    create_rag_eval_case,
    current_knowledge_revision,
    get_exact_knowledge_cache,
    get_nas_asset,
    get_rag_eval_case,
    get_user_by_id,
    list_accessible_asset_versions,
    list_knowledge_cache_candidates,
    list_rag_eval_cases,
    mark_knowledge_cache_hit,
    save_knowledge_query_cache,
    save_rag_eval_run,
    update_rag_eval_case,
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
VALID_EVAL_CASE_TYPES = {"normal", "cross_file", "insufficient", "access_control", "version"}
VALID_EXPECTED_BEHAVIORS = {"answer", "refuse"}
VALID_APPROVAL_STATUSES = {"draft", "approved"}
REFUSAL_MARKERS = (
    "資料不足", "沒有足夠", "無足夠", "找不到", "未找到", "無法根據", "無法回答",
    "沒有權限", "無權存取", "不能提供", "not enough information", "cannot answer",
    "no accessible", "do not have access",
)


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
    values = _validated_eval_case_values(payload, admin)
    return await asyncio.to_thread(
        create_rag_eval_case,
        **values,
        created_by=admin["id"],
    )


async def update_eval_case(
    case_id: int,
    payload: dict[str, Any],
    admin: dict[str, Any],
) -> dict[str, Any] | None:
    existing = await asyncio.to_thread(get_rag_eval_case, case_id)
    if not existing:
        return None
    merged = {
        "question": existing["question"],
        "expected_asset_ids": json.loads(existing["expected_asset_ids_json"] or "[]"),
        "expected_keywords": json.loads(existing["expected_keywords_json"] or "[]"),
        "reference_answer": existing.get("reference_answer"),
        "scope": json.loads(existing["scope_json"] or "{}"),
        "case_type": existing.get("case_type"),
        "test_user_id": existing.get("test_user_id"),
        "expected_behavior": existing.get("expected_behavior"),
        "required_facts": json.loads(existing.get("required_facts_json") or "[]"),
        "prohibited_facts": json.loads(existing.get("prohibited_facts_json") or "[]"),
        "allowed_asset_ids": json.loads(existing.get("allowed_asset_ids_json") or "[]"),
        "approval_status": existing.get("approval_status"),
        "is_active": bool(existing.get("is_active", 1)),
        **payload,
    }
    values = _validated_eval_case_values(merged, admin)
    values["is_active"] = int(bool(merged.get("is_active", True)))
    return await asyncio.to_thread(update_rag_eval_case, case_id, **values)


async def run_evaluation(
    admin: dict[str, Any],
    *,
    answerer: Callable[[dict[str, Any], dict[str, Any]], Awaitable[dict[str, Any]]] | None = None,
    case_ids: list[int] | None = None,
) -> dict[str, Any]:
    cases = await asyncio.to_thread(list_rag_eval_cases, active_only=True)
    selected_ids = {int(item) for item in (case_ids or [])}
    cases = [
        case for case in cases
        if case.get("approval_status") == "approved"
        and (not selected_ids or int(case["id"]) in selected_ids)
    ]
    run_group = uuid.uuid4().hex
    results = []
    for case in cases:
        started = time.perf_counter()
        test_user = await asyncio.to_thread(get_user_by_id, int(case.get("test_user_id") or 0))
        error_message = None
        response: dict[str, Any] = {}
        if not test_user or test_user.get("role") != "user" or not test_user.get("is_active", 1):
            error_message = "The evaluation employee is missing, inactive, or not a standard user"
        try:
            if not error_message and answerer:
                response = await answerer(case, test_user)
            elif not error_message:
                scope = normalize_scope(json.loads(case["scope_json"]))
                chunks = await search_knowledge(
                    user=test_user,
                    question=case["question"],
                    scope=scope,
                    limit=5,
                )
                response = {
                    "answer": case.get("reference_answer") or "",
                    "contexts": serialize_knowledge_chunks(chunks),
                    "model_contexts": serialize_knowledge_chunks(chunks),
                    "model_id": None,
                    "retrieval": {"knowledge_revision": current_knowledge_revision()},
                }
        except Exception as exc:  # Persist per-case failures so the suite can continue.
            error_message = str(exc)

        chunks = response.get("contexts") or []
        model_contexts = response.get("model_contexts") or chunks
        answer = str(response.get("answer") or "")
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
        required_facts = json.loads(case.get("required_facts_json") or "[]")
        prohibited_facts = json.loads(case.get("prohibited_facts_json") or "[]")
        allowed_assets = set(json.loads(case.get("allowed_asset_ids_json") or "[]"))
        answer_folded = _fold(answer)
        matched_facts = [fact for fact in required_facts if _fold(fact) in answer_folded]
        prohibited_hits = [fact for fact in prohibited_facts if _fold(fact) in answer_folded]
        fact_score = len(matched_facts) / len(required_facts) if required_facts else 1.0
        citations, citation_valid = _evaluate_citations(answer, chunks, allowed_assets)
        citation_support_score = _citation_support_score(required_facts, answer, citations, chunks)
        refused = _is_refusal(answer)
        expected_behavior = case.get("expected_behavior") or "answer"
        refusal_score = float(refused if expected_behavior == "refuse" else not refused)

        retrieval_leaks = await _unauthorized_asset_ids(chunks, test_user) if test_user else set()
        context_leaks = await _unauthorized_asset_ids(model_contexts, test_user) if test_user else set()
        leak_stages = []
        if retrieval_leaks:
            leak_stages.append("retrieval")
        if context_leaks:
            leak_stages.append("model_context")
        if prohibited_hits and case.get("case_type") == "access_control":
            leak_stages.append("answer")
        permission_leak = int(bool(leak_stages))
        answer_requires_citations = expected_behavior == "answer"
        automatic_pass = (
            not error_message
            and not permission_leak
            and not prohibited_hits
            and refusal_score == 1.0
            and (expected_behavior == "refuse" or fact_score == 1.0)
            and (not answer_requires_citations or citation_valid == 1)
            and (not answer_requires_citations or citation_support_score == 1.0)
        )
        latency_ms = round((time.perf_counter() - started) * 1000)
        serialized_chunks = serialize_knowledge_chunks(chunks)
        serialized_model_contexts = serialize_knowledge_chunks(model_contexts)
        saved = await asyncio.to_thread(
            save_rag_eval_run,
            case_id=case["id"],
            run_group=run_group,
            retrieval_version=KNOWLEDGE_RETRIEVAL_VERSION,
            model_id=response.get("model_id") or response.get("model") or None,
            retrieved_chunks_json=json.dumps(serialized_chunks, ensure_ascii=False),
            answer=answer,
            recall_at_5=recall,
            reciprocal_rank=reciprocal_rank,
            keyword_score=keyword_score,
            citation_valid=int(citation_valid),
            permission_leak=permission_leak,
            latency_ms=latency_ms,
            test_user_id=test_user["id"] if test_user else case.get("test_user_id"),
            expected_behavior=expected_behavior,
            prompt_version=response.get("prompt_version") or KNOWLEDGE_PROMPT_VERSION,
            knowledge_revision=(response.get("retrieval") or {}).get("knowledge_revision"),
            model_context_json=json.dumps(serialized_model_contexts, ensure_ascii=False),
            citations_json=json.dumps(citations, ensure_ascii=False),
            fact_score=fact_score,
            citation_support_score=citation_support_score,
            refusal_score=refusal_score,
            prohibited_fact_hits_json=json.dumps(prohibited_hits, ensure_ascii=False),
            permission_leak_stage=",".join(leak_stages) or None,
            automatic_result="pass" if automatic_pass else "fail",
            error_message=error_message,
        )
        results.append(saved)
    return {
        "run_group": run_group,
        "case_count": len(results),
        "recall_at_5": _average(results, "recall_at_5"),
        "mrr": _average(results, "reciprocal_rank"),
        "keyword_score": _average(results, "keyword_score"),
        "citation_accuracy": _average(results, "citation_valid"),
        "fact_accuracy": _average(results, "fact_score"),
        "citation_support": _average(results, "citation_support_score"),
        "refusal_accuracy": _average(results, "refusal_score"),
        "permission_leaks": sum(int(item["permission_leak"]) for item in results),
        "automatic_pass_rate": round(
            sum(item["automatic_result"] == "pass" for item in results) / len(results), 4
        ) if results else 0.0,
        "average_latency_ms": _average(results, "latency_ms"),
        "results": results,
    }


def _validated_eval_case_values(payload: dict[str, Any], admin: dict[str, Any]) -> dict[str, Any]:
    question = str(payload.get("question") or "").strip()
    if not question:
        raise ValueError("Question is required")
    case_type = str(payload.get("case_type") or "normal").strip()
    if case_type not in VALID_EVAL_CASE_TYPES:
        raise ValueError("Invalid evaluation case type")
    expected_behavior = str(payload.get("expected_behavior") or "answer").strip()
    if expected_behavior not in VALID_EXPECTED_BEHAVIORS:
        raise ValueError("Expected behavior must be answer or refuse")
    approval_status = str(payload.get("approval_status") or "draft").strip()
    if approval_status not in VALID_APPROVAL_STATUSES:
        raise ValueError("Approval status must be draft or approved")
    test_user_id = int(payload["test_user_id"]) if payload.get("test_user_id") not in (None, "") else None
    test_user = get_user_by_id(test_user_id) if test_user_id else None
    if test_user_id and not test_user:
        raise ValueError("Evaluation employee does not exist")
    if test_user and (test_user.get("role") != "user" or not test_user.get("is_active", 1)):
        raise ValueError("Evaluation identity must be an active standard employee")
    if approval_status == "approved" and not test_user:
        raise ValueError("An active standard employee is required before approval")

    expected_assets = _integer_list(payload.get("expected_asset_ids"))
    allowed_assets = _integer_list(payload.get("allowed_asset_ids")) or expected_assets
    for asset_id in set(expected_assets + allowed_assets):
        if not get_nas_asset(asset_id):
            raise ValueError(f"NAS asset {asset_id} does not exist")
    expected_keywords = _text_list(payload.get("expected_keywords"))
    required_facts = _text_list(payload.get("required_facts"))
    prohibited_facts = _text_list(payload.get("prohibited_facts"))
    if approval_status == "approved" and expected_behavior == "answer":
        if not required_facts:
            raise ValueError("Approved answer cases require at least one required fact")
        if not allowed_assets:
            raise ValueError("Approved answer cases require at least one allowed source")
    if approval_status == "approved" and case_type == "access_control" and not prohibited_facts:
        raise ValueError("Approved access-control cases require at least one prohibited fact")
    scope = normalize_scope(payload.get("scope") or {})
    return {
        "question": question,
        "expected_asset_ids_json": json.dumps(expected_assets),
        "expected_keywords_json": json.dumps(expected_keywords, ensure_ascii=False),
        "reference_answer": str(payload.get("reference_answer") or "").strip() or None,
        "scope_json": json.dumps(scope, ensure_ascii=False),
        "case_type": case_type,
        "test_user_id": test_user_id,
        "expected_behavior": expected_behavior,
        "required_facts_json": json.dumps(required_facts, ensure_ascii=False),
        "prohibited_facts_json": json.dumps(prohibited_facts, ensure_ascii=False),
        "allowed_asset_ids_json": json.dumps(allowed_assets),
        "approval_status": approval_status,
        "approved_by": admin["id"] if approval_status == "approved" else None,
    }


def _integer_list(value: Any) -> list[int]:
    return sorted({int(item) for item in (value or [])})


def _text_list(value: Any) -> list[str]:
    return list(dict.fromkeys(str(item).strip() for item in (value or []) if str(item).strip()))


def _fold(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _is_refusal(answer: str) -> bool:
    folded = _fold(answer)
    return any(marker in folded for marker in REFUSAL_MARKERS)


def _evaluate_citations(
    answer: str,
    contexts: list[dict[str, Any]],
    allowed_assets: set[int],
) -> tuple[list[dict[str, Any]], int]:
    indexes = [int(match) for match in re.findall(r"\[來源\s*(\d+)\]", answer)]
    citations = []
    valid = bool(indexes)
    for index in indexes:
        if index < 1 or index > len(contexts):
            valid = False
            citations.append({"index": index, "valid": False})
            continue
        context = contexts[index - 1]
        asset_id = int(context["asset_id"])
        source_allowed = not allowed_assets or asset_id in allowed_assets
        valid = valid and source_allowed
        citations.append(
            {
                "index": index,
                "valid": source_allowed,
                "asset_id": asset_id,
                "chunk_id": context.get("id"),
                "asset_title": context.get("asset_title"),
            }
        )
    return citations, int(valid)


def _citation_support_score(
    required_facts: list[str],
    answer: str,
    citations: list[dict[str, Any]],
    contexts: list[dict[str, Any]],
) -> float:
    cited_contexts = [
        contexts[item["index"] - 1]
        for item in citations
        if item.get("valid") and 1 <= int(item["index"]) <= len(contexts)
    ]
    if not required_facts:
        return float(bool(cited_contexts))
    answer_folded = _fold(answer)
    asserted_facts = [fact for fact in required_facts if _fold(fact) in answer_folded]
    if not asserted_facts:
        return 0.0
    supported = sum(
        1
        for fact in asserted_facts
        if any(_fold(fact) in _fold(context.get("content")) for context in cited_contexts)
    )
    return supported / len(required_facts)


async def _unauthorized_asset_ids(
    contexts: list[dict[str, Any]],
    user: dict[str, Any],
) -> set[int]:
    asset_ids = {int(item["asset_id"]) for item in contexts if item.get("asset_id") is not None}
    if not asset_ids:
        return set()
    checks = await asyncio.gather(
        *[
            asyncio.to_thread(
                user_can_read_asset,
                asset_id,
                user_id=user["id"],
                role=user["role"],
            )
            for asset_id in asset_ids
        ]
    )
    return {asset_id for asset_id, allowed in zip(asset_ids, checks, strict=True) if not allowed}


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
