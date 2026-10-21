from __future__ import annotations

import asyncio
import json

from app.db import claim_next_excel_pro_job, recover_excel_pro_jobs, update_excel_pro_job
from app.excel_pro import execute_export_job


_worker_task: asyncio.Task | None = None


async def start_excel_pro_worker() -> None:
    global _worker_task
    recover_excel_pro_jobs()
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_worker_loop(), name="excel-pro-worker")


async def stop_excel_pro_worker() -> None:
    global _worker_task
    if _worker_task is None:
        return
    _worker_task.cancel()
    try:
        await _worker_task
    except asyncio.CancelledError:
        pass
    _worker_task = None


async def _worker_loop() -> None:
    while True:
        job = claim_next_excel_pro_job()
        if not job:
            await asyncio.sleep(1)
            continue
        try:
            def progress(value: int, stage: str) -> None:
                update_excel_pro_job(job["id"], progress=max(0, min(value, 99)), stage=stage)

            result = await asyncio.to_thread(execute_export_job, job, progress)
            update_excel_pro_job(
                job["id"], status="completed", progress=100, stage="completed",
                output_asset_id=int(result["output_asset_id"]),
                result_json=json.dumps(result, ensure_ascii=False),
            )
        except InterruptedError:
            update_excel_pro_job(job["id"], status="cancelled", progress=100, stage="cancelled")
        except asyncio.CancelledError:
            update_excel_pro_job(job["id"], status="queued", stage="interrupted")
            raise
        except Exception as exc:
            update_excel_pro_job(
                job["id"], status="failed", progress=100, stage="failed",
                error_message=str(exc)[:1000],
            )
