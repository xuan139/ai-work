from __future__ import annotations

import asyncio
import json
import re
from difflib import SequenceMatcher
from typing import Any

from app.db import (
    get_exact_llm_cache,
    list_llm_cache_candidates,
    list_llm_prompt_history,
    list_llm_cache_seed_calls,
    mark_llm_cache_hit,
    save_llm_query_cache,
)
from app.embedding_runtime import (
    EMBEDDING_MODEL,
    EmbeddingRuntimeError,
    cosine_similarity,
    embed_query,
    pack_embedding,
    request_embeddings,
    unpack_embedding,
)

SEMANTIC_CACHE_THRESHOLD = 0.94
TEXT_SIMILARITY_THRESHOLD = 0.72
KEYWORD_SIMILARITY_THRESHOLD = 0.5
POLITE_PREFIX = re.compile(
    r"^(?:(?:幫我|帮我)(?:查一下|查詢一下|查询一下|查詢|查询)|(?:查一下|查詢一下|查询一下)|"
    r"再次?(?:請問|请问|請|请)|再(?=幫我|帮我)|請問|请问|請|请|麻煩你?|麻烦你?|"
    r"勞駕|劳驾|please|couldyou|canyou|wouldyou)+",
    re.IGNORECASE,
)


def normalize_llm_prompt(prompt: str) -> str:
    normalized = re.sub(r"[^\w]+", "", prompt.casefold(), flags=re.UNICODE)
    previous = None
    while normalized and normalized != previous:
        previous = normalized
        normalized = POLITE_PREFIX.sub("", normalized)
    return normalized


async def suggest_llm_prompts(
    *,
    user_id: int,
    model_id: str,
    query: str,
    limit: int = 6,
) -> list[dict[str, Any]]:
    normalized_query = normalize_llm_prompt(query)
    if len(normalized_query) < 2:
        return []

    history = await asyncio.to_thread(list_llm_prompt_history, user_id, model_id)
    suggestions = []
    seen = set()
    for row in history:
        prompt = str(row["prompt"] or "").strip()
        normalized_prompt = normalize_llm_prompt(prompt)
        if not normalized_prompt or normalized_prompt in seen:
            continue
        seen.add(normalized_prompt)

        text_similarity = SequenceMatcher(None, normalized_query, normalized_prompt).ratio()
        keyword_similarity = _keyword_similarity(normalized_query, normalized_prompt)
        if normalized_prompt == normalized_query:
            match_type = "exact"
            score = 1.0
        elif normalized_prompt.startswith(normalized_query):
            match_type = "prefix"
            score = 0.98
        else:
            match_type = "keyword"
            score = 0.65 * keyword_similarity + 0.35 * text_similarity
            if score < 0.35:
                continue

        suggestions.append(
            {
                "prompt": prompt,
                "match_type": match_type,
                "score": round(score, 4),
                "keyword_similarity": round(keyword_similarity, 4),
                "cached": bool(row["cached"]),
                "hit_count": int(row["hit_count"] or 0),
                "created_at": row["created_at"],
            }
        )

    suggestions.sort(key=lambda item: (-item["score"], -int(item["cached"]), item["prompt"]))
    return suggestions[: max(1, min(limit, 10))]


async def lookup_llm_cache(
    *,
    user_id: int,
    model_id: str,
    prompt: str,
) -> tuple[dict[str, Any] | None, list[float] | None]:
    normalized = normalize_llm_prompt(prompt)
    exact = await asyncio.to_thread(get_exact_llm_cache, user_id, model_id, normalized)
    if exact:
        await asyncio.to_thread(mark_llm_cache_hit, exact["id"])
        return _deserialize_cache(exact, "exact", 1.0), None

    seed_calls = await asyncio.to_thread(list_llm_cache_seed_calls, user_id, model_id)
    seed = next((call for call in seed_calls if normalize_llm_prompt(call["prompt"]) == normalized), None)
    if seed:
        query_vector = await embed_query(prompt, user_id)
        result = _result_from_call(seed)
        await store_llm_cache(
            user_id=user_id,
            model_id=model_id,
            prompt=prompt,
            query_vector=query_vector,
            result=result,
        )
        return {
            "result": result,
            "cache": _cache_metadata(seed["prompt"], seed["created_at"], seed["id"], "exact", 1.0, 1),
        }, query_vector

    query_vector = await embed_query(prompt, user_id)
    if query_vector is None:
        return None, None

    candidates = await asyncio.to_thread(list_llm_cache_candidates, user_id, model_id)
    best: tuple[float, float, dict[str, Any]] | None = None
    for candidate in candidates:
        if not _text_compatible(prompt, normalized, candidate["prompt_text"], candidate["normalized_prompt"]):
            continue
        similarity = cosine_similarity(query_vector, unpack_embedding(candidate.get("prompt_embedding")))
        if similarity is None or similarity < SEMANTIC_CACHE_THRESHOLD:
            continue
        keyword_similarity = _keyword_similarity(normalized, candidate["normalized_prompt"])
        if best is None or similarity > best[0]:
            best = (similarity, keyword_similarity, candidate)
    if best is None:
        best = await _backfill_and_match_seed_calls(
            seed_calls=seed_calls,
            user_id=user_id,
            model_id=model_id,
            prompt=prompt,
            normalized_prompt=normalized,
            query_vector=query_vector,
        )
        if best is None:
            return None, query_vector

    similarity, keyword_similarity, candidate = best
    if candidate.get("cache_id"):
        await asyncio.to_thread(mark_llm_cache_hit, candidate["cache_id"])
    if candidate.get("result"):
        return {
            "result": candidate["result"],
            "cache": _cache_metadata(
                candidate["prompt_text"],
                candidate["created_at"],
                candidate["result"].get("call_id"),
                "semantic",
                similarity,
                1,
                keyword_similarity,
            ),
        }, query_vector
    await asyncio.to_thread(mark_llm_cache_hit, candidate["id"])
    return _deserialize_cache(candidate, "semantic", similarity, keyword_similarity), query_vector


async def store_llm_cache(
    *,
    user_id: int,
    model_id: str,
    prompt: str,
    query_vector: list[float] | None,
    result: dict[str, Any],
) -> None:
    await asyncio.to_thread(
        save_llm_query_cache,
        user_id=user_id,
        model_id=model_id,
        prompt_text=prompt,
        normalized_prompt=normalize_llm_prompt(prompt),
        prompt_embedding=pack_embedding(query_vector) if query_vector else None,
        embedding_model=EMBEDDING_MODEL if query_vector else None,
        result_json=json.dumps(result, ensure_ascii=False),
    )


def _deserialize_cache(
    row: dict[str, Any],
    match_type: str,
    similarity: float,
    keyword_similarity: float | None = None,
) -> dict[str, Any]:
    return {
        "result": json.loads(row["result_json"]),
        "cache": _cache_metadata(
            row["prompt_text"],
            row["created_at"],
            json.loads(row["result_json"]).get("call_id"),
            match_type,
            similarity,
            int(row["hit_count"] or 0) + 1,
            keyword_similarity,
        ),
    }


def _cache_metadata(
    original_prompt: str,
    created_at: str,
    source_call_id: int | None,
    match_type: str,
    similarity: float,
    hit_count: int,
    keyword_similarity: float | None = None,
) -> dict[str, Any]:
    metadata = {
        "hit": True,
        "match_type": match_type,
        "similarity": round(similarity, 4),
        "original_prompt": original_prompt,
        "original_created_at": created_at,
        "source_call_id": source_call_id,
        "hit_count": hit_count,
    }
    if keyword_similarity is not None:
        metadata["keyword_similarity"] = round(keyword_similarity, 4)
    return metadata


def _result_from_call(call: dict[str, Any]) -> dict[str, Any]:
    raw_usage = None
    if call.get("raw_usage_json"):
        try:
            raw_usage = json.loads(call["raw_usage_json"])
        except json.JSONDecodeError:
            raw_usage = None
    return {
        "call_id": call["id"],
        "model_id": call["model_id"],
        "provider": call["provider"],
        "model": call["model_name"],
        "access_mode": call["access_mode"],
        "answer": call["response"],
        "usage": {
            "input_tokens": call.get("input_tokens"),
            "output_tokens": call.get("output_tokens"),
            "total_tokens": call.get("total_tokens"),
            "remaining_tokens": call.get("remaining_tokens"),
            "remaining_requests": call.get("remaining_requests"),
            "remaining_balance": call.get("remaining_balance"),
            "raw_usage": raw_usage,
        },
    }


def _same_ascii_terms(left: str, right: str) -> bool:
    return _ascii_terms(left) == _ascii_terms(right)


def _ascii_terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z][a-z0-9+#.-]*|\d+", text.casefold()))


def _text_compatible(prompt: str, normalized: str, candidate_prompt: str, candidate_normalized: str) -> bool:
    if not _same_ascii_terms(prompt, candidate_prompt):
        return False
    if SequenceMatcher(None, normalized, candidate_normalized).ratio() >= TEXT_SIMILARITY_THRESHOLD:
        return True
    return _keyword_similarity(normalized, candidate_normalized) >= KEYWORD_SIMILARITY_THRESHOLD


def _keyword_similarity(left: str, right: str) -> float:
    left_terms = _keyword_terms(left)
    right_terms = _keyword_terms(right)
    if not left_terms or not right_terms:
        return 0.0
    return len(left_terms & right_terms) / min(len(left_terms), len(right_terms))


def _keyword_terms(text: str) -> set[str]:
    normalized = text.casefold()
    terms = _ascii_terms(normalized)
    for sequence in re.findall(r"[\u3400-\u9fff]+", normalized):
        if len(sequence) == 1:
            terms.add(sequence)
        else:
            terms.update(sequence[index : index + 2] for index in range(len(sequence) - 1))
    return terms


async def _backfill_and_match_seed_calls(
    *,
    seed_calls: list[dict[str, Any]],
    user_id: int,
    model_id: str,
    prompt: str,
    normalized_prompt: str,
    query_vector: list[float],
) -> tuple[float, float, dict[str, Any]] | None:
    eligible = []
    seen_normalized = set()
    for call in seed_calls:
        candidate_normalized = normalize_llm_prompt(call["prompt"])
        if candidate_normalized in seen_normalized:
            continue
        if _text_compatible(
            prompt,
            normalized_prompt,
            call["prompt"],
            candidate_normalized,
        ):
            eligible.append(call)
            seen_normalized.add(candidate_normalized)
        if len(eligible) == 20:
            break
    if not eligible:
        return None
    try:
        vectors = await asyncio.to_thread(
            request_embeddings,
            [call["prompt"] for call in eligible],
            "query",
            user_id,
        )
    except EmbeddingRuntimeError:
        return None

    best: tuple[float, float, dict[str, Any]] | None = None
    for call, vector in zip(eligible, vectors, strict=True):
        result = _result_from_call(call)
        await store_llm_cache(
            user_id=user_id,
            model_id=model_id,
            prompt=call["prompt"],
            query_vector=vector,
            result=result,
        )
        similarity = cosine_similarity(query_vector, vector)
        if similarity is None or similarity < SEMANTIC_CACHE_THRESHOLD:
            continue
        keyword_similarity = _keyword_similarity(normalized_prompt, normalize_llm_prompt(call["prompt"]))
        candidate = {
            "prompt_text": call["prompt"],
            "created_at": call["created_at"],
            "result": result,
        }
        if best is None or similarity > best[0]:
            best = (similarity, keyword_similarity, candidate)
    return best
