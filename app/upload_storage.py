from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO


DEFAULT_MAX_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024
COPY_CHUNK_BYTES = 1024 * 1024


class UploadTooLargeError(ValueError):
    pass


def max_upload_bytes() -> int:
    raw = os.environ.get("AI_WORK_MAX_UPLOAD_BYTES", "").strip()
    if not raw:
        return DEFAULT_MAX_UPLOAD_BYTES
    try:
        configured = int(raw)
    except ValueError:
        return DEFAULT_MAX_UPLOAD_BYTES
    return configured if configured > 0 else DEFAULT_MAX_UPLOAD_BYTES


def save_upload_stream(
    source: BinaryIO,
    destination: Path,
    *,
    limit: int | None = None,
) -> int:
    maximum = limit if limit is not None else max_upload_bytes()
    copied = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("wb") as output:
            while chunk := source.read(COPY_CHUNK_BYTES):
                copied += len(chunk)
                if copied > maximum:
                    raise UploadTooLargeError(
                        f"檔案超過上傳上限 {format_bytes(maximum)}"
                    )
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return copied


def format_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"
