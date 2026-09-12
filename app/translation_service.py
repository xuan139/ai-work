from __future__ import annotations

import json
from typing import Any

from app.db import create_llm_call
from app.llm_catalog import get_model
from app.llm_runtime import LlmRuntimeError, run_llm


TARGET_LANGUAGES = {
    "zh-Hant": "Traditional Chinese",
    "en": "English",
    "zh-Hans": "Simplified Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
}


async def translate_transcript_with_audit(
    *,
    text: str,
    target: str,
    model_id: str,
    api_key: str | None,
    user_id: int,
) -> dict[str, Any]:
    model = get_model(model_id)
    if not model:
        raise LlmRuntimeError("Translation model not found")
    target_name = TARGET_LANGUAGES.get(target)
    if not target_name:
        raise LlmRuntimeError("Translation target language is not supported")

    parts = split_translation_text(text, max_chars=600)
    if not parts:
        raise LlmRuntimeError("Transcript is empty and cannot be translated")
    translated_parts: list[str] = []
    call_ids: list[int] = []
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    for index, part in enumerate(parts, start=1):
        prompt = build_translation_prompt(part, target_name, index, len(parts))
        result, call_id = await run_translation_call(
            model=model,
            prompt=prompt,
            api_key=api_key,
            user_id=user_id,
            target=target,
            segment=index,
            segment_count=len(parts),
        )
        translated_parts.append(result["answer"].strip())
        call_ids.append(call_id)
        usage = result.get("usage") or {}
        for key in totals:
            if isinstance(usage.get(key), int):
                totals[key] += usage[key]

    return {
        "text": "\n\n".join(part for part in translated_parts if part),
        "model": model,
        "metadata": {
            "target": target,
            "target_name": target_name,
            "segment_count": len(parts),
            "call_ids": call_ids,
            "usage": totals,
        },
    }


async def run_translation_call(
    *,
    model: dict[str, Any],
    prompt: str,
    api_key: str | None,
    user_id: int,
    target: str,
    segment: int,
    segment_count: int,
) -> tuple[dict[str, Any], int]:
    expected_mode = "local_nas" if model["provider"] == "Local NAS" else ("api_key" if api_key else "free_no_key")
    try:
        result = await run_llm(model, prompt, api_key)
    except Exception as exc:
        create_llm_call(
            user_id=user_id,
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=prompt,
            response=None,
            status="failed",
            access_mode=expected_mode,
            error_message=str(exc),
            raw_usage_json=json.dumps(
                {"task": "translation", "target": target, "segment": segment, "segment_count": segment_count},
                ensure_ascii=False,
            ),
        )
        if isinstance(exc, LlmRuntimeError):
            raise
        raise LlmRuntimeError(str(exc)) from exc

    usage = result.get("usage") or {}
    raw_usage = usage.get("raw_usage") or {}
    call = create_llm_call(
        user_id=user_id,
        provider=model["provider"],
        model_name=model["name"],
        model_id=model["id"],
        prompt=prompt,
        response=result["answer"],
        status="completed",
        access_mode=result["access_mode"],
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        total_tokens=usage.get("total_tokens"),
        remaining_tokens=usage.get("remaining_tokens"),
        remaining_requests=usage.get("remaining_requests"),
        remaining_balance=usage.get("remaining_balance"),
        raw_usage_json=json.dumps(
            {
                "task": "translation",
                "target": target,
                "segment": segment,
                "segment_count": segment_count,
                "provider_usage": raw_usage,
            },
            ensure_ascii=False,
        ),
    )
    return result, call["id"]


def split_translation_text(text: str, *, max_chars: int) -> list[str]:
    clean = text.strip()
    if not clean:
        return []
    paragraphs = [part.strip() for part in clean.split("\n") if part.strip()]
    parts: list[str] = []
    current = ""
    for paragraph in paragraphs:
        while len(paragraph) > max_chars:
            if current:
                parts.append(current)
                current = ""
            parts.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if len(candidate) > max_chars:
            parts.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def build_translation_prompt(text: str, target_name: str, segment: int, segment_count: int) -> str:
    return (
        f"Translate this meeting transcript into {target_name}. "
        "Preserve speaker labels, paragraph structure, names, product names, numbers, dates, and technical terms. "
        "Do not summarize, explain, or add commentary. Output only the translated transcript. "
        f"This is segment {segment} of {segment_count}.\n\n{text}"
    )
