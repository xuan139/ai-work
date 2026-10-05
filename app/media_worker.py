from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import Literal

from app.asr_catalog import get_asr_model
from app.db import (
    claim_processing_job,
    enqueue_processing_job as persist_processing_job,
    get_meeting,
    get_nas_asset,
    get_processing_job,
    list_runnable_processing_jobs,
    processing_job_cancel_requested,
    recover_processing_jobs,
    request_processing_job_cancel,
    update_meeting_status,
    update_nas_asset,
    update_processing_job,
)
from app.document_processing import process_nas_asset
from app.llm_catalog import get_model
from app.llm_runtime import company_api_key_for_model
from app.transcription import process_meeting_transcription
from app.video_catalog import get_video_model


JobType = Literal["meeting", "asset"]
JobKey = tuple[JobType, int]


@dataclass
class MediaJob:
    job_type: JobType
    record_id: int
    audio_api_key: str | None = field(default=None, repr=False)
    video_api_key: str | None = field(default=None, repr=False)
    translation_api_key: str | None = field(default=None, repr=False)


_queue: asyncio.Queue[MediaJob] | None = None
_workers: list[asyncio.Task[None]] = []
_dispatcher: asyncio.Task[None] | None = None
_scheduled: set[JobKey] = set()
_active: dict[JobKey, asyncio.Task[None]] = {}
_credentials: dict[JobKey, tuple[str | None, str | None, str | None]] = {}


async def start_media_workers() -> None:
    global _queue, _workers, _dispatcher
    if _queue is not None:
        return
    recover_processing_jobs()
    _queue = asyncio.Queue()
    _workers = [
        asyncio.create_task(media_worker_loop(index + 1), name=f"media-worker-{index + 1}")
        for index in range(positive_int("MEDIA_WORKER_COUNT", 1))
    ]
    _dispatcher = asyncio.create_task(processing_job_dispatcher(), name="processing-job-dispatcher")
    await dispatch_runnable_jobs()


async def stop_media_workers() -> None:
    global _queue, _workers, _dispatcher
    dispatcher = _dispatcher
    _dispatcher = None
    if dispatcher:
        dispatcher.cancel()
        await asyncio.gather(dispatcher, return_exceptions=True)
    workers = _workers
    _workers = []
    for worker in workers:
        worker.cancel()
    if workers:
        await asyncio.gather(*workers, return_exceptions=True)
    _queue = None
    _scheduled.clear()
    _active.clear()
    _credentials.clear()


async def enqueue_media_job(
    job_type: JobType,
    record_id: int,
    *,
    audio_api_key: str | None = None,
    video_api_key: str | None = None,
    translation_api_key: str | None = None,
) -> dict:
    if _queue is None:
        raise RuntimeError("媒體 Worker 尚未啟動")
    job = persist_processing_job(
        job_type,
        record_id,
        max_attempts=positive_int("MEDIA_JOB_MAX_ATTEMPTS", 3),
    )
    key = (job_type, record_id)
    _credentials[key] = (audio_api_key, video_api_key, translation_api_key)
    await schedule_media_job(job_type, record_id)
    return job


async def cancel_media_job(job_type: JobType, record_id: int) -> dict | None:
    job = request_processing_job_cancel(job_type, record_id)
    if not job:
        return None
    if job["status"] == "cancelled":
        mark_record_cancelled(job_type, record_id)
    return job


async def processing_job_dispatcher() -> None:
    while True:
        await dispatch_runnable_jobs()
        await asyncio.sleep(1)


async def dispatch_runnable_jobs() -> None:
    for job in list_runnable_processing_jobs():
        await schedule_media_job(job["job_type"], int(job["record_id"]))


async def schedule_media_job(job_type: JobType, record_id: int) -> None:
    queue = _queue
    if queue is None:
        return
    key = (job_type, record_id)
    if key in _scheduled:
        return
    audio_key, video_key, translation_key = _credentials.get(key, (None, None, None))
    _scheduled.add(key)
    await queue.put(
        MediaJob(
            job_type=job_type,
            record_id=record_id,
            audio_api_key=audio_key,
            video_api_key=video_key,
            translation_api_key=translation_key,
        )
    )


async def media_worker_loop(worker_number: int) -> None:
    del worker_number
    while True:
        queue = _queue
        if queue is None:
            return
        job = await queue.get()
        key = (job.job_type, job.record_id)
        try:
            claimed = claim_processing_job(job.job_type, job.record_id)
            if not claimed:
                continue
            resolve_job_credentials(job)
            task = asyncio.create_task(execute_media_job(job), name=f"{job.job_type}-{job.record_id}")
            _active[key] = task
            await task
            if processing_job_cancel_requested(job.job_type, job.record_id):
                raise asyncio.CancelledError
            await finalize_job_from_record(job, claimed)
        except asyncio.CancelledError:
            if processing_job_cancel_requested(job.job_type, job.record_id):
                update_processing_job(
                    job.job_type,
                    job.record_id,
                    status="cancelled",
                    progress=100,
                    stage="cancelled",
                )
                mark_record_cancelled(job.job_type, job.record_id)
                continue
            update_processing_job(
                job.job_type,
                job.record_id,
                status="queued",
                stage="interrupted",
                retry_delay_seconds=0,
            )
            raise
        except Exception as exc:
            await retry_or_fail(job, str(exc))
        finally:
            _active.pop(key, None)
            _scheduled.discard(key)
            persisted = get_processing_job(job.job_type, job.record_id) or {}
            if persisted.get("status") != "retry_wait":
                _credentials.pop(key, None)
            queue.task_done()


async def execute_media_job(job: MediaJob) -> None:
    update_processing_job(job.job_type, job.record_id, progress=10, stage="processing")
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


async def finalize_job_from_record(job: MediaJob, claimed: dict) -> None:
    record = get_meeting(job.record_id) if job.job_type == "meeting" else get_nas_asset(job.record_id)
    status = str((record or {}).get("status") or "failed")
    if status == "completed":
        update_processing_job(
            job.job_type,
            job.record_id,
            status="completed",
            progress=100,
            stage="completed",
        )
        return
    if status == "cancelled":
        update_processing_job(
            job.job_type,
            job.record_id,
            status="cancelled",
            progress=100,
            stage="cancelled",
        )
        return
    error = str((record or {}).get("error_message") or (record or {}).get("summary") or "處理未完成")
    if status == "needs_model":
        update_processing_job(
            job.job_type,
            job.record_id,
            status="failed",
            progress=100,
            stage="needs_model",
            error_message=error,
        )
        return
    await retry_or_fail(job, error, claimed)


async def retry_or_fail(job: MediaJob, error: str, claimed: dict | None = None) -> None:
    current = get_processing_job(job.job_type, job.record_id) or claimed or {}
    attempts = int(current.get("attempts") or 1)
    max_attempts = int(current.get("max_attempts") or 3)
    if processing_job_cancel_requested(job.job_type, job.record_id):
        update_processing_job(
            job.job_type,
            job.record_id,
            status="cancelled",
            progress=100,
            stage="cancelled",
            error_message=error,
        )
        mark_record_cancelled(job.job_type, job.record_id)
        return
    if attempts < max_attempts:
        retry_base = nonnegative_int("MEDIA_JOB_RETRY_BASE_SECONDS", 5)
        delay = min(60, retry_base * (2 ** max(0, attempts - 1)))
        update_processing_job(
            job.job_type,
            job.record_id,
            status="retry_wait",
            progress=0,
            stage="retry_wait",
            error_message=error,
            retry_delay_seconds=delay,
        )
        mark_record_processing(job.job_type, job.record_id, attempts, max_attempts, error)
        return
    update_processing_job(
        job.job_type,
        job.record_id,
        status="failed",
        progress=100,
        stage="failed",
        error_message=error,
    )
    mark_record_failed(job.job_type, job.record_id, error)


def resolve_job_credentials(job: MediaJob) -> None:
    if job.job_type == "meeting":
        meeting = get_meeting(job.record_id) or {}
        asr_model = get_asr_model(meeting.get("asr_model_id"))
        translation_model = get_model(str(meeting.get("translation_model_id") or ""))
        job.audio_api_key = job.audio_api_key or company_api_key_for_model(asr_model)
        job.translation_api_key = job.translation_api_key or (
            company_api_key_for_model(translation_model) if translation_model else None
        )
        return
    asset = get_nas_asset(job.record_id) or {}
    try:
        config = json.loads(asset.get("processor_config_json") or "{}")
    except json.JSONDecodeError:
        config = {}
    if asset.get("category") == "audio":
        model = get_asr_model(config.get("asr_model_id"))
        job.audio_api_key = job.audio_api_key or company_api_key_for_model(model)
        translation_model = get_model(str(config.get("translation_model_id") or ""))
        job.translation_api_key = job.translation_api_key or (
            company_api_key_for_model(translation_model) if translation_model else None
        )
    elif asset.get("category") == "video":
        model = get_video_model(config.get("video_model_id"))
        job.video_api_key = job.video_api_key or company_api_key_for_model(model)


def mark_record_processing(job_type: JobType, record_id: int, attempts: int, max_attempts: int, error: str) -> None:
    message = f"處理失敗，將自動重試（{attempts}/{max_attempts}）：{error}"
    if job_type == "meeting":
        update_meeting_status(record_id, status="processing", error_message=message)
    else:
        record = get_nas_asset(record_id) or {}
        update_nas_asset(
            record_id,
            status="processing",
            analyzer=record.get("analyzer"),
            summary=message,
            error_message=None,
            chunk_count=record.get("chunk_count"),
        )


def mark_record_failed(job_type: JobType, record_id: int, error: str) -> None:
    if job_type == "meeting":
        update_meeting_status(record_id, status="failed", error_message=error)
    else:
        record = get_nas_asset(record_id) or {}
        update_nas_asset(record_id, status="failed", analyzer=record.get("analyzer"), error_message=error)


def mark_record_cancelled(job_type: JobType, record_id: int) -> None:
    if job_type == "meeting":
        update_meeting_status(record_id, status="cancelled", error_message="使用者已取消處理")
    else:
        record = get_nas_asset(record_id) or {}
        update_nas_asset(
            record_id,
            status="cancelled",
            analyzer=record.get("analyzer"),
            summary="使用者已取消背景處理。",
            error_message=None,
            chunk_count=record.get("chunk_count"),
        )


def positive_int(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


def nonnegative_int(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return value if value >= 0 else default
