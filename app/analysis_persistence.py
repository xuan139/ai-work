from __future__ import annotations

import asyncio
import json
from typing import Any

from app.db import get_asset_ai_analysis, save_asset_ai_analysis
from app.document_processing import chunk_text
from app.embedding_runtime import attach_embeddings
from app.rag_cache import normalize_query


async def persist_cloud_asset_analysis(
    *,
    asset: dict[str, Any],
    model: dict[str, Any],
    question: str,
    result: dict[str, Any],
    contexts: list[dict[str, Any]],
    user_id: int,
) -> dict[str, Any]:
    if model.get("execution", "cloud") != "cloud":
        return {"saved": False, "reason": "local_model"}

    normalized_question = normalize_query(question)
    existing = await asyncio.to_thread(
        get_asset_ai_analysis,
        asset["id"],
        model["id"],
        normalized_question,
    )
    if existing:
        return {
            "saved": True,
            "created": False,
            "analysis_id": existing["id"],
            "embedding_status": existing["embedding_status"],
        }

    answer = str(result.get("answer") or "").strip()
    if not answer:
        return {"saved": False, "reason": "empty_answer"}

    chunks = build_analysis_chunks(
        asset=asset,
        model=model,
        question=question,
        answer=answer,
        call_id=result.get("call_id"),
        contexts=contexts,
    )
    embedded = await attach_embeddings(chunks, user_id)
    stored = await asyncio.to_thread(
        save_asset_ai_analysis,
        asset_id=asset["id"],
        user_id=user_id,
        llm_call_id=result.get("call_id"),
        model_id=model["id"],
        provider=model["provider"],
        model_name=model["name"],
        question=question,
        normalized_question=normalized_question,
        answer=answer,
        access_mode=result.get("access_mode"),
        embedded=embedded,
        chunks=chunks,
    )
    analysis = stored["analysis"]
    return {
        "saved": True,
        "created": stored["created"],
        "analysis_id": analysis["id"],
        "analysis_chunk_count": stored["analysis_chunk_count"],
        "asset_chunk_count": stored["asset_chunk_count"],
        "embedding_status": analysis["embedding_status"],
    }


def build_analysis_chunks(
    *,
    asset: dict[str, Any],
    model: dict[str, Any],
    question: str,
    answer: str,
    call_id: int | None,
    contexts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    source_contexts = [
        {
            "chunk_id": context.get("id"),
            "chunk_index": context.get("chunk_index"),
            "page_number": context.get("page_number"),
            "chunk_type": context.get("chunk_type"),
        }
        for context in contexts
    ]
    answer_chunks = chunk_text(answer, max_chars=1200, overlap=120) or [answer]
    return [
        {
            "content": (
                f"AI 分析來源：{asset['title']}\n"
                f"分析模型：{model['provider']} · {model['name']}\n"
                f"使用者問題：{question}\n\n"
                f"分析結果：\n{answer_chunk}"
            ),
            "token_estimate": max(1, (len(question) + len(answer_chunk)) // 4),
            "chunk_type": "ai_analysis",
            "metadata_json": json.dumps(
                {
                    "source_asset_id": asset["id"],
                    "source_asset_title": asset["title"],
                    "llm_call_id": call_id,
                    "model_id": model["id"],
                    "provider": model["provider"],
                    "model_name": model["name"],
                    "question": question,
                    "answer_part": index + 1,
                    "answer_parts": len(answer_chunks),
                    "source_contexts": source_contexts,
                },
                ensure_ascii=False,
            ),
        }
        for index, answer_chunk in enumerate(answer_chunks)
    ]
