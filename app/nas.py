import asyncio
import shutil
import uuid
from pathlib import Path

from app.db import create_meeting, get_user_by_username
from app.notifications import manager
from app.transcription import process_meeting_transcription

AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".webm", ".ogg", ".flac", ".aac"}


def ensure_storage_dirs(base_dir: Path) -> None:
    for directory in (
        base_dir / "data",
        base_dir / "storage" / "recordings",
        base_dir / "mock_nas" / "inbox",
        base_dir / "mock_nas" / "processed",
    ):
        directory.mkdir(parents=True, exist_ok=True)


def _is_audio_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES


async def wait_until_stable(path: Path, checks: int = 2, interval: float = 0.8) -> bool:
    previous_size = -1
    stable_count = 0
    while stable_count < checks:
        if not path.exists():
            return False
        current_size = path.stat().st_size
        if current_size == previous_size and current_size > 0:
            stable_count += 1
        else:
            stable_count = 0
        previous_size = current_size
        await asyncio.sleep(interval)
    return True


async def import_nas_file(base_dir: Path, path: Path) -> None:
    admin = get_user_by_username("admin")
    if not admin:
        return

    if not await wait_until_stable(path):
        return

    storage_dir = base_dir / "storage" / "recordings"
    stored_name = f"{uuid.uuid4().hex}{path.suffix.lower()}"
    stored_path = storage_dir / stored_name
    shutil.copy2(path, stored_path)

    processed_path = base_dir / "mock_nas" / "processed" / path.name
    if processed_path.exists():
        processed_path = processed_path.with_name(f"{processed_path.stem}-{uuid.uuid4().hex[:8]}{processed_path.suffix}")
    shutil.move(str(path), processed_path)

    meeting = create_meeting(
        user_id=admin["id"],
        source="nas_discovery",
        title=path.stem,
        original_filename=path.name,
        audio_path=str(stored_path),
        status="processing",
    )

    await manager.broadcast(
        {
            "type": "meeting_detected",
            "meeting_id": meeting["id"],
            "title": meeting["title"],
            "message": f"發現新的會議錄音《{meeting['title']}》，已經開始處理",
            "meeting": meeting,
        }
    )
    asyncio.create_task(process_meeting_transcription(meeting["id"]))


async def nas_discovery_loop(base_dir: Path, interval: float = 2.0) -> None:
    inbox = base_dir / "mock_nas" / "inbox"
    processing: set[Path] = set()

    while True:
        try:
            for path in sorted(inbox.iterdir()):
                if path in processing or not _is_audio_file(path):
                    continue
                processing.add(path)
                asyncio.create_task(_import_and_release(base_dir, path, processing))
        except FileNotFoundError:
            inbox.mkdir(parents=True, exist_ok=True)
        await asyncio.sleep(interval)


async def _import_and_release(base_dir: Path, path: Path, processing: set[Path]) -> None:
    try:
        await import_nas_file(base_dir, path)
    finally:
        processing.discard(path)
