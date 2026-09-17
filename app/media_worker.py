from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Literal

from app.db import list_pending_media_jobs, update_meeting_status, update_nas_asset
from app.document_processing import process_nas_asset
from app.transcription import process_meeting_transcription


JobType = Literal["meeting", "asset"]


@dataclass
class MediaJob:
    job_type: JobType
    record_id: int
    audio_api_key: str | None = field(default=None, repr=False)
    video_api_key: str | None = field(default=None, repr=False)
    translation_api_key: str | None = field(default=None, repr=False)


_queue: asyncio.Queue[MediaJob] | None = None
_workers: list[asyncio.Task[None]] = []


async def start_media_workers() -> None:
    global _queue, _workers
    if _queue is not None:
        return
    _queue = asyncio.Queue()
    _workers = [
        asyncio.create_task(media_worker_loop(index + 1), name=f"media-worker-{index + 1}")
        for index in range(positive_int("MEDIA_WORKER_COUNT", 1))
    ]
    for pending in list_pending_media_jobs():
        await _queue.put(MediaJob(job_type=pending["job_type"], record_id=pending["record_id"]))


async def stop_media_workers() -> None:
    global _queue, _workers
    workers = _workers
    _workers = []
    _queue = None
    for worker in workers:
        worker.cancel()
    if workers:
        await asyncio.gather(*workers, return_exceptions=True)


async def enqueue_media_job(
    job_type: JobType,
    record_id: int,
    *,
    audio_api_key: str | None = None,
    video_api_key: str | None = None,
    translation_api_key: str | None = None,
) -> None:
    if _queue is None:
        raise RuntimeError("媒體 Worker 尚未啟動")
    await _queue.put(
        MediaJob(
            job_type=job_type,
            record_id=record_id,
            audio_api_key=audio_api_key,
            video_api_key=video_api_key,
            translation_api_key=translation_api_key,
        )
    )


async def media_worker_loop(worker_number: int) -> None:
    del worker_number
    while True:
        queue = _queue
        if queue is None:
            return
        job = await queue.get()
        try:
            if job.job_type == "meeting":
                await process_meeting_transcription(
                    job.record_id,
                    job.audio_api_key,
                    job.translation_api_key,
                )
            else:
                await process_nas_asset(
                    job.record_id,
                    job.audio_api_key,
                    job.video_api_key,
                    job.translation_api_key,
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if job.job_type == "meeting":
                update_meeting_status(job.record_id, status="failed", error_message=str(exc))
            else:
                update_nas_asset(job.record_id, status="failed", error_message=str(exc))
        finally:
            queue.task_done()


def positive_int(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default
