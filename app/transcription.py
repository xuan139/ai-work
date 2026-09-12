import json
from pathlib import Path
from typing import Any

from app.asr_catalog import get_asr_model
from app.asr_runtime import AsrRuntimeError
from app.asr_service import run_asr_with_audit
from app.db import (
    get_meeting,
    get_nas_asset,
    replace_document_chunks,
    update_meeting_status,
    update_meeting_translation,
    update_nas_asset,
)
from app.document_processing import build_transcript_chunks, build_translation_chunks
from app.embedding_runtime import attach_embeddings
from app.llm_runtime import LlmRuntimeError
from app.meeting_line import push_completed_meeting_to_line
from app.notifications import manager
from app.translation_service import translate_transcript_with_audit


async def process_meeting_transcription(
    meeting_id: int,
    api_key: str | None = None,
    translation_api_key: str | None = None,
) -> None:
    meeting = get_meeting(meeting_id)
    if not meeting:
        return

    model = get_asr_model(meeting.get("asr_model_id"))
    audio_path = Path(meeting["audio_path"])
    try:
        result = await run_asr_with_audit(
            path=audio_path,
            model_id=model["id"],
            api_key=api_key,
            user_id=meeting["user_id"],
        )
        chunks = build_transcript_chunks(result["text"], audio_path, model, result)
        translation_text = None
        translation_error = None
        translation_metadata = None
        if meeting.get("translation_enabled"):
            try:
                translated = await translate_transcript_with_audit(
                    text=result["text"],
                    target=meeting.get("translation_target") or "zh-Hant",
                    model_id=meeting.get("translation_model_id") or "local:qwen3-4b",
                    api_key=translation_api_key,
                    user_id=meeting["user_id"],
                )
                translation_text = translated["text"]
                translation_metadata = translated["metadata"]
                chunks.extend(
                    build_translation_chunks(
                        translation_text,
                        audio_path,
                        translated["model"],
                        meeting.get("translation_target") or "zh-Hant",
                        start_index=len(chunks),
                    )
                )
            except LlmRuntimeError as exc:
                translation_error = str(exc)
        embedded = await attach_embeddings(chunks, meeting["user_id"])
        await update_linked_asset(meeting, model, chunks, embedded, translation_text, translation_error)
        updated = update_meeting_status(
            meeting_id,
            status="completed",
            transcript=result["text"],
            asr_metadata_json=json.dumps(result.get("metadata") or {}, ensure_ascii=False, default=str),
        )
        if meeting.get("translation_enabled"):
            updated = update_meeting_translation(
                meeting_id,
                translation_status="completed" if translation_text else "failed",
                translation=translation_text,
                translation_error=translation_error,
                translation_metadata_json=(
                    json.dumps(translation_metadata, ensure_ascii=False, default=str)
                    if translation_metadata
                    else None
                ),
                )
        await push_completed_meeting_to_line(meeting_id)
        updated = get_meeting(meeting_id)
        await manager.broadcast(
            {
                "type": "meeting_completed",
                "meeting_id": meeting_id,
                "title": meeting["title"],
                "message": completion_message(meeting, model, translation_text, translation_error),
                "meeting": updated,
            }
        )
    except AsrRuntimeError as exc:
        local_model = model["id"].startswith("local:")
        status = "needs_model" if local_model else "failed"
        updated = update_meeting_status(meeting_id, status=status, error_message=str(exc))
        await fail_linked_asset(meeting, model, status, str(exc))
        await manager.broadcast(
            {
                "type": "meeting_needs_model" if local_model else "meeting_failed",
                "meeting_id": meeting_id,
                "title": meeting["title"],
                "message": f"會議《{meeting['title']}》需要完成 {model['name']} 設定" if local_model else f"會議《{meeting['title']}》轉寫失敗",
                "meeting": updated,
            }
        )
    except Exception as exc:
        updated = update_meeting_status(meeting_id, status="failed", error_message=str(exc))
        await fail_linked_asset(meeting, model, "failed", str(exc))
        await manager.broadcast(
            {
                "type": "meeting_failed",
                "meeting_id": meeting_id,
                "title": meeting["title"],
                "message": f"會議《{meeting['title']}》處理失敗",
                "meeting": updated,
            }
        )


async def update_linked_asset(
    meeting: dict[str, Any],
    model: dict[str, Any],
    chunks: list[dict[str, Any]],
    embedded: bool,
    translation_text: str | None,
    translation_error: str | None,
) -> None:
    asset_id = meeting.get("nas_asset_id")
    if not asset_id:
        return
    replace_document_chunks(asset_id, chunks)
    asset = update_nas_asset(
        asset_id,
        status="completed",
        analyzer=model["name"],
        summary=(
            f"已使用 {model['name']} 完成會議語音轉文字，建立逐字稿 RAG chunks：{len(chunks)} 段；"
            f"{translation_asset_summary(meeting, translation_text, translation_error)}"
            f"{'Qwen3 Embedding 向量已寫入' if embedded else '向量服務暫時不可用，已排入背景補建'}。"
        ),
        chunk_count=len(chunks),
    )
    if asset:
        await manager.broadcast(
            {
                "type": "nas_asset_processed",
                "asset_id": asset_id,
                "title": asset["title"],
                "message": f"NAS 會議資產《{asset['title']}》已完成轉寫與索引",
                "asset": asset,
            }
        )


async def fail_linked_asset(meeting: dict[str, Any], model: dict[str, Any], status: str, error: str) -> None:
    asset_id = meeting.get("nas_asset_id")
    if not asset_id or not get_nas_asset(asset_id):
        return
    asset = update_nas_asset(
        asset_id,
        status=status,
        analyzer=model["name"],
        summary=f"已選擇 {model['name']}。{error}",
        error_message=error if status == "failed" else None,
        chunk_count=0,
    )
    if asset:
        await manager.broadcast(
            {
                "type": "nas_asset_failed" if status == "failed" else "nas_asset_processed",
                "asset_id": asset_id,
                "title": asset["title"],
                "message": f"NAS 會議資產《{asset['title']}》需要完成語音模型設定" if status == "needs_model" else f"NAS 會議資產《{asset['title']}》處理失敗",
                "asset": asset,
            }
        )


def translation_asset_summary(
    meeting: dict[str, Any],
    translation_text: str | None,
    translation_error: str | None,
) -> str:
    if not meeting.get("translation_enabled"):
        return ""
    if translation_text:
        return f"已由 {meeting.get('translation_model') or 'LLM'} 完成翻譯；"
    return f"逐字稿已保存，但翻譯失敗：{translation_error or '未知錯誤'}；"


def completion_message(
    meeting: dict[str, Any],
    model: dict[str, Any],
    translation_text: str | None,
    translation_error: str | None,
) -> str:
    if translation_text:
        return f"會議《{meeting['title']}》已由 {model['name']} 完成轉寫，並完成指定語言翻譯與 RAG 建庫"
    if meeting.get("translation_enabled") and translation_error:
        return f"會議《{meeting['title']}》轉寫與 RAG 建庫完成，但翻譯失敗"
    return f"會議《{meeting['title']}》已由 {model['name']} 完成轉寫與 RAG 建庫"
