from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from app.asr_catalog import get_asr_model
from app.asr_runtime import AsrRuntimeError, transcribe_audio
from app.db import create_llm_call


async def run_asr_with_audit(
    *,
    path: Path,
    model_id: str | None,
    api_key: str | None,
    user_id: int,
) -> dict[str, Any]:
    model = get_asr_model(model_id)
    prompt = f"Transcribe audio file: {path.name} ({path.stat().st_size if path.exists() else 0} bytes)"
    access_mode = "local_nas" if model["id"].startswith("local:") else "api_key"

    try:
        result = await asyncio.to_thread(transcribe_audio, path, model["id"], api_key)
    except Exception as exc:
        create_llm_call(
            user_id=user_id,
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=prompt,
            response=None,
            status="failed",
            access_mode=access_mode,
            error_message=str(exc),
        )
        if isinstance(exc, AsrRuntimeError):
            raise
        raise AsrRuntimeError(f"ASR runtime failed: {exc}") from exc

    metadata = result.get("metadata") if isinstance(result, dict) else None
    create_llm_call(
        user_id=user_id,
        provider=model["provider"],
        model_name=model["name"],
        model_id=model["id"],
        prompt=prompt,
        response=result["text"],
        status="completed",
        access_mode=access_mode,
        output_tokens=max(1, len(result["text"]) // 4),
        raw_usage_json=_metadata_json(metadata),
    )
    return result


def _metadata_json(metadata: Any) -> str | None:
    if metadata is None:
        return None
    try:
        return json.dumps(metadata, ensure_ascii=False, default=str)[:20000]
    except (TypeError, ValueError):
        return json.dumps({"metadata": str(metadata)}, ensure_ascii=False)
