from __future__ import annotations

from typing import Any

from app.db import (
    get_meeting_by_nas_asset_id,
    list_document_chunks,
    update_document_chunk_contents,
    update_meeting_status,
    update_meeting_translation,
    update_nas_asset,
)
from app.embedding_runtime import attach_embeddings
from app.text_normalization import convert_to_traditional


async def convert_asset_to_traditional(asset: dict[str, Any]) -> dict[str, Any]:
    chunks = list_document_chunks(asset["id"])
    changed_chunks = 0
    for chunk in chunks:
        converted = convert_to_traditional(chunk["content"])
        if converted != chunk["content"]:
            changed_chunks += 1
        chunk["content"] = converted
        chunk["token_estimate"] = max(1, len(converted) // 4)
        chunk["embedding"] = None
        chunk["embedding_model"] = None

    meeting = get_meeting_by_nas_asset_id(asset["id"])
    changed_meeting_fields = 0
    if meeting:
        transcript = convert_to_traditional(meeting.get("transcript") or "")
        translation = convert_to_traditional(meeting.get("translation") or "")
        if transcript and transcript != (meeting.get("transcript") or ""):
            update_meeting_status(
                meeting["id"],
                status=meeting["status"],
                transcript=transcript,
                error_message=meeting.get("error_message"),
            )
            changed_meeting_fields += 1
        if translation and translation != (meeting.get("translation") or ""):
            update_meeting_translation(
                meeting["id"],
                translation_status=meeting.get("translation_status") or "completed",
                translation=translation,
                translation_error=meeting.get("translation_error"),
            )
            changed_meeting_fields += 1

    embedded = True
    if chunks and changed_chunks:
        embedded = await attach_embeddings(chunks, asset["user_id"])
        update_document_chunk_contents(asset["id"], chunks)

    changed_total = changed_chunks + changed_meeting_fields
    message = (
        f"OpenCC 簡轉繁完成：更新 {changed_chunks} 個 RAG chunks"
        f"及 {changed_meeting_fields} 個會議文字欄位；"
        f"{'向量已重新建立' if embedded else '向量服務暫時不可用，已排入背景補建'}。"
        if changed_total
        else "OpenCC 檢查完成：目前內容已是繁體中文，沒有需要更新的文字。"
    )
    updated = asset
    if changed_total:
        previous_summary = (asset.get("summary") or "").strip()
        summary = f"{previous_summary} {message}".strip()
        updated = update_nas_asset(
            asset["id"],
            status=asset["status"],
            analyzer=asset.get("analyzer"),
            summary=summary,
            error_message=asset.get("error_message"),
            chunk_count=asset.get("chunk_count"),
        )
    return {
        "asset": updated,
        "changed_chunks": changed_chunks,
        "changed_meeting_fields": changed_meeting_fields,
        "embedding_rebuilt": embedded,
        "message": message,
    }
