import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import db, media_worker
from app.document_processing import ocr_pdf_pages
from app.auth import hash_password


class ProcessingJobTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")

    async def asyncTearDown(self) -> None:
        await media_worker.stop_media_workers()
        self.db_patch.stop()
        self.directory.cleanup()

    def create_asset(self, status: str = "processing") -> dict:
        return db.create_nas_asset(
            user_id=self.admin["id"],
            category="pdf",
            title="Queue test",
            original_filename="queue.pdf",
            stored_path=str(Path(self.directory.name) / "queue.pdf"),
            mime_type="application/pdf",
            file_size=10,
            status=status,
            analyzer="RAG Builder",
        )

    def test_enqueue_is_idempotent_and_exposes_progress_on_asset(self) -> None:
        asset = self.create_asset()
        first = db.enqueue_processing_job("asset", asset["id"], max_attempts=4)
        db.update_processing_job("asset", asset["id"], progress=35, stage="ocr")
        second = db.enqueue_processing_job("asset", asset["id"], max_attempts=4)

        self.assertEqual(first["id"], second["id"])
        processing_job = db.get_nas_asset(asset["id"])["processing_job"]
        self.assertEqual(processing_job["status"], "queued")
        self.assertEqual(processing_job["progress"], 35)
        self.assertEqual(processing_job["stage"], "ocr")
        with db.connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM processing_jobs").fetchone()[0]
        self.assertEqual(count, 1)

    def test_running_job_is_recovered_after_restart(self) -> None:
        asset = self.create_asset()
        db.enqueue_processing_job("asset", asset["id"])
        claimed = db.claim_processing_job("asset", asset["id"])
        self.assertEqual(claimed["status"], "running")

        recovered = db.recover_processing_jobs()
        job = db.get_processing_job("asset", asset["id"])

        self.assertEqual(recovered, 1)
        self.assertEqual(job["status"], "queued")
        self.assertEqual(job["stage"], "recovered")

    def test_queued_job_can_be_cancelled(self) -> None:
        asset = self.create_asset()
        db.enqueue_processing_job("asset", asset["id"])
        job = db.request_processing_job_cancel("asset", asset["id"])

        self.assertEqual(job["status"], "cancelled")
        self.assertEqual(job["progress"], 100)
        self.assertEqual(db.list_runnable_processing_jobs(), [])

    def test_pdf_ocr_resumes_from_saved_page(self) -> None:
        pages = {}
        for index in (1, 2):
            image = Path(self.directory.name) / f"page-{index}.png"
            image.write_bytes(b"image")
            pages[index] = image
        calls = 0

        def recognize(*args):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("interrupted")
            return f"page {calls}"

        with (
            patch("app.document_processing.paddle_ocr_engine", return_value=object()),
            patch("app.document_processing.run_paddle_ocr", side_effect=recognize),
        ):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                ocr_pdf_pages(pages)
            recovered = ocr_pdf_pages(pages)

        self.assertEqual(calls, 3)
        self.assertEqual([page["text"] for page in recovered], ["page 1", "page 3"])

    async def test_running_job_cancel_updates_record(self) -> None:
        asset = self.create_asset()
        started = asyncio.Event()
        release = asyncio.Event()

        async def slow_process(*args, **kwargs):
            del args, kwargs
            started.set()
            await release.wait()

        with (
            patch.dict(os.environ, {"MEDIA_WORKER_COUNT": "1"}),
            patch.object(media_worker, "process_nas_asset", new=AsyncMock(side_effect=slow_process)),
        ):
            await media_worker.start_media_workers()
            await media_worker.enqueue_media_job("asset", asset["id"])
            await asyncio.wait_for(started.wait(), timeout=2)
            await media_worker.cancel_media_job("asset", asset["id"])
            release.set()
            for _ in range(100):
                if db.get_processing_job("asset", asset["id"])["status"] == "cancelled":
                    break
                await asyncio.sleep(0.01)

        self.assertEqual(db.get_processing_job("asset", asset["id"])["status"], "cancelled")
        self.assertEqual(db.get_nas_asset(asset["id"])["status"], "cancelled")

    async def test_failed_attempt_waits_for_retry_and_preserves_credentials(self) -> None:
        asset = self.create_asset()
        attempts = 0

        async def fail_once(*args, **kwargs):
            nonlocal attempts
            del args, kwargs
            attempts += 1
            if attempts == 1:
                raise RuntimeError("temporary failure")
            db.update_nas_asset(
                asset["id"],
                status="completed",
                analyzer="RAG Builder",
                summary="done",
                chunk_count=1,
            )

        with (
            patch.dict(
                os.environ,
                {
                    "MEDIA_WORKER_COUNT": "1",
                    "MEDIA_JOB_MAX_ATTEMPTS": "2",
                    "MEDIA_JOB_RETRY_BASE_SECONDS": "0",
                },
            ),
            patch.object(media_worker, "process_nas_asset", new=AsyncMock(side_effect=fail_once)),
        ):
            await media_worker.start_media_workers()
            await media_worker.enqueue_media_job("asset", asset["id"], audio_api_key="temporary-key")
            for _ in range(300):
                job = db.get_processing_job("asset", asset["id"])
                if job and job["status"] == "completed":
                    break
                await asyncio.sleep(0.01)

        self.assertEqual(attempts, 2)
        self.assertEqual(db.get_processing_job("asset", asset["id"])["status"], "completed")


if __name__ == "__main__":
    unittest.main()
