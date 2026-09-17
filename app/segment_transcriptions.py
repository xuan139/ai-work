from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from app.media_segmentation import media_segment_directory


_LOCKS: dict[int, threading.Lock] = {}
_LOCKS_GUARD = threading.Lock()


def list_audio_segment_transcriptions(asset_id: int) -> dict[int, dict]:
    path = transcription_path(asset_id)
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    result: dict[int, dict] = {}
    for key, value in payload.items():
        if not isinstance(value, dict):
            continue
        try:
            result[int(key)] = value
        except (TypeError, ValueError):
            continue
    return result


def update_audio_segment_transcription(asset_id: int, segment_index: int, **changes: object) -> dict:
    lock = asset_lock(asset_id)
    with lock:
        current = list_audio_segment_transcriptions(asset_id)
        record = {
            **current.get(segment_index, {}),
            "segment_index": segment_index,
            **changes,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        current[segment_index] = record
        path = transcription_path(asset_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({str(index): item for index, item in sorted(current.items())}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(path)
        return record


def transcription_path(asset_id: int) -> Path:
    return media_segment_directory(asset_id, "audio") / "transcriptions.json"


def asset_lock(asset_id: int) -> threading.Lock:
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(asset_id, threading.Lock())
