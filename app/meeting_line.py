from __future__ import annotations

import json
import os
from typing import Any

from app.db import (
    create_line_document,
    create_llm_call,
    finish_line_document,
    get_line_document,
    get_line_source,
    get_line_source_month_usage,
    get_meeting,
    get_user_by_id,
    update_meeting_line_push,
)
from app.line_service import push_line_messages
from app.llm_catalog import get_model
from app.llm_runtime import LlmRuntimeError, company_api_key_for_model, run_llm


async def push_completed_meeting_to_line(meeting_id: int) -> None:
    meeting = get_meeting(meeting_id)
    if (
        not meeting
        or not meeting.get("line_push_enabled")
        or not meeting.get("line_group_id")
        or meeting.get("line_push_status") == "completed"
    ):
        return
    user = get_user_by_id(meeting["user_id"])
    caller = user["username"] if user else f"user-{meeting['user_id']}"
    document = None
    try:
        source = get_line_source(meeting["line_group_id"])
        if not source or source.get("source_type") != "group" or not source.get("is_approved"):
            raise LlmRuntimeError("LINE group is not approved for company AI")
        usage = get_line_source_month_usage(source["source_id"])
        if source.get("monthly_call_limit") and usage["call_count"] >= source["monthly_call_limit"]:
            raise LlmRuntimeError("LINE group monthly model call quota is exhausted")
        if source.get("monthly_token_limit") and usage["token_count"] >= source["monthly_token_limit"]:
            raise LlmRuntimeError("LINE group monthly token quota is exhausted")
        summary = await summarize_meeting_for_line(meeting, caller, source)
        document_key = f"meeting:{meeting_id}"
        existing = get_line_document(document_key)
        if not existing:
            document = create_line_document(
                line_source_id=source["id"],
                line_message_id=document_key,
                line_event_id=None,
                sender_id=f"portal-user:{meeting['user_id']}",
                sender_name=caller,
                asset_id=meeting["nas_asset_id"],
            )
        else:
            document = existing

        messages = build_line_messages(meeting, summary, caller)
        await push_line_messages(meeting["line_group_id"], messages)
        finish_line_document(document["id"], status="completed", summary=summary, error_message=None)
        update_meeting_line_push(meeting_id, status="completed", summary=summary, error_message=None)
    except Exception as exc:
        if document:
            finish_line_document(document["id"], status="failed", summary=None, error_message=str(exc))
        update_meeting_line_push(meeting_id, status="failed", error_message=str(exc))


async def summarize_meeting_for_line(meeting: dict[str, Any], caller: str, source: dict[str, Any]) -> str:
    model = get_model(source["default_model_id"])
    if not model:
        raise LlmRuntimeError("Meeting summary model is unavailable")
    company_key = company_api_key_for_model(model)
    if model["provider"] != "Local NAS" and not company_key:
        raise LlmRuntimeError("Company API key is unavailable for the selected LINE model")
    transcript = str(meeting.get("transcript") or "").strip()
    if not transcript:
        raise LlmRuntimeError("Meeting transcript is empty")
    prompt = (
        "你是企業 NAS 會議助理。只能根據下方逐字稿，以繁體中文整理 LINE 群組通知。"
        "依序輸出「會議摘要」「決議」「待辦事項」三節；沒有明確決議或待辦時必須寫『逐字稿未明確提及』。"
        "不得杜撰負責人、日期、數字或結論，總長不超過 1,200 字。\n\n"
        f"會議：{meeting['title']}\n轉寫模型：{meeting.get('asr_model') or '-'}\n\n"
        f"逐字稿重點取樣：\n{meeting_summary_excerpt(transcript)}"
    )
    expected_mode = "local_nas" if model["provider"] == "Local NAS" else "company_api_key"
    audit_user_id = source["owner_user_id"]
    try:
        result = await run_llm(model, prompt, company_key)
        if company_key:
            result["access_mode"] = "company_api_key"
    except Exception as exc:
        create_llm_call(
            user_id=audit_user_id, provider=model["provider"], model_name=model["name"],
            model_id=model["id"], prompt=prompt, response=None, status="failed",
            access_mode=expected_mode, error_message=str(exc), channel="LINE",
            external_caller=caller, source_ref=meeting["line_group_id"],
            raw_usage_json=json.dumps({"task": "meeting_summary", "meeting_id": meeting["id"]}),
        )
        raise LlmRuntimeError(str(exc)) from exc

    usage = result.get("usage") or {}
    create_llm_call(
        user_id=audit_user_id, provider=model["provider"], model_name=model["name"],
        model_id=model["id"], prompt=prompt, response=result["answer"], status="completed",
        access_mode=result["access_mode"], input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"), total_tokens=usage.get("total_tokens"),
        remaining_tokens=usage.get("remaining_tokens"), remaining_requests=usage.get("remaining_requests"),
        remaining_balance=usage.get("remaining_balance"), channel="LINE", external_caller=caller,
        source_ref=meeting["line_group_id"],
        raw_usage_json=json.dumps({"task": "meeting_summary", "meeting_id": meeting["id"], "provider_usage": usage.get("raw_usage")}, ensure_ascii=False),
    )
    return str(result["answer"]).strip()


def meeting_summary_excerpt(transcript: str, max_chars: int = 2800) -> str:
    if len(transcript) <= max_chars:
        return transcript
    section_size = max_chars // 3
    middle_start = max(0, (len(transcript) - section_size) // 2)
    sections = (
        ("開頭", transcript[:section_size]),
        ("中段", transcript[middle_start : middle_start + section_size]),
        ("結尾", transcript[-section_size:]),
    )
    return "\n\n".join(f"[{label}]\n{text}" for label, text in sections)


def build_line_messages(meeting: dict[str, Any], summary: str, caller: str) -> list[str]:
    public_url = os.getenv("AI_WORK_PUBLIC_URL", "https://59.120.2.102").rstrip("/")
    translation_note = "已保存翻譯版本" if meeting.get("translation") else "未啟用翻譯"
    headline = (
        "NAS 會議處理完成\n"
        f"會議：{meeting['title']}\n"
        f"錄音者：{caller}\n"
        f"轉寫：{meeting.get('asr_provider') or 'ASR'} · {meeting.get('asr_model') or '-'}\n"
        f"NAS：原始錄音、逐字稿、向量與稽核記錄已保存\n"
        f"翻譯：{translation_note}\n\n"
        f"{summary}\n\n"
        f"完整內容：{public_url}/\n"
        "可在本群組輸入 @Claire 加上問題，查詢這場會議與群組文件。"
    )
    messages = [headline]
    if meeting.get("line_push_full_transcript"):
        parts = split_line_transcript(str(meeting.get("transcript") or ""))
        messages.extend(
            f"會議逐字稿 {index}/{len(parts)}｜{meeting['title']}\n\n{part}"
            for index, part in enumerate(parts, start=1)
        )
    return messages


def split_line_transcript(text: str, max_chars: int = 4200) -> list[str]:
    clean = text.strip()
    return [clean[index : index + max_chars] for index in range(0, len(clean), max_chars)] if clean else []
