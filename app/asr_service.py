from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Callable

from app.asr_catalog import get_asr_model
from app.asr_runtime import AsrRuntimeError, transcribe_audio
from app.db import create_llm_call
from app.media_segmentation import MediaSegmentationError, archive_audio_segments, prepare_media_segments
from app.segment_transcriptions import update_audio_segment_transcription
from app.text_normalization import normalize_asr_text


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
        normalized_text, normalization = normalize_asr_text(result["text"])
        result["text"] = normalized_text
        result["metadata"] = {
            **(result.get("metadata") or {}),
            "chinese_script_normalization": normalization,
        }
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


async def run_segmented_asr_with_audit(
    *,
    path: Path,
    model_id: str | None,
    api_key: str | None,
    user_id: int,
    progress: Callable[[int, int], None] | None = None,
    segment_archive_asset_id: int | None = None,
) -> dict[str, Any]:
    try:
        batch = await asyncio.to_thread(prepare_media_segments, path, "audio")
    except MediaSegmentationError as exc:
        raise AsrRuntimeError(str(exc)) from exc

    try:
        if not batch.segmented:
            result = await run_asr_with_audit(
                path=path,
                model_id=model_id,
                api_key=api_key,
                user_id=user_id,
            )
            result["metadata"] = {
                **(result.get("metadata") or {}),
                "segmented": False,
                "segment_count": 1,
                "source_duration_seconds": batch.source_duration_seconds,
            }
            if progress:
                progress(1, 1)
            return result

        archived_segments = []
        if segment_archive_asset_id is not None:
            archived_segments = await asyncio.to_thread(
                archive_audio_segments,
                segment_archive_asset_id,
                batch.segments,
            )

        segment_results: list[dict[str, Any]] = []
        transcript_parts: list[str] = []
        total = len(batch.segments)
        for completed, segment in enumerate(batch.segments, start=1):
            if segment_archive_asset_id is not None:
                update_audio_segment_transcription(
                    segment_archive_asset_id,
                    segment.index,
                    status="processing",
                    progress=15,
                    model_id=model_id,
                    error_message=None,
                )
            try:
                result = await run_asr_with_audit(
                    path=segment.path,
                    model_id=model_id,
                    api_key=api_key,
                    user_id=user_id,
                )
            except Exception as exc:
                if segment_archive_asset_id is not None:
                    update_audio_segment_transcription(
                        segment_archive_asset_id,
                        segment.index,
                        status="failed",
                        progress=100,
                        error_message=str(exc),
                    )
                raise
            if segment_archive_asset_id is not None:
                update_audio_segment_transcription(
                    segment_archive_asset_id,
                    segment.index,
                    status="completed",
                    progress=100,
                    model_id=result["model"]["id"],
                    model_name=result["model"].get("name") or result["model"]["id"],
                    transcript=result["text"],
                    error_message=None,
                )
            segment_results.append(
                {
                    "index": segment.index,
                    "start_seconds": segment.start_seconds,
                    "duration_seconds": segment.duration_seconds,
                    "text_length": len(result["text"]),
                    "metadata": result.get("metadata") or {},
                }
            )
            transcript_parts.append(result["text"].strip())
            if progress:
                progress(completed, total)

        last_result = result
        return {
            "text": "\n".join(part for part in transcript_parts if part),
            "model": last_result["model"],
            "engine": last_result["engine"],
            "metadata": {
                "segmented": True,
                "segment_count": total,
                "source_duration_seconds": batch.source_duration_seconds,
                "segments": segment_results,
                "archived_segments": archived_segments,
            },
        }
    finally:
        await asyncio.to_thread(batch.cleanup)


def _metadata_json(metadata: Any) -> str | None:
    if metadata is None:
        return None
    try:
        return json.dumps(metadata, ensure_ascii=False, default=str)[:20000]
    except (TypeError, ValueError):
        return json.dumps({"metadata": str(metadata)}, ensure_ascii=False)
