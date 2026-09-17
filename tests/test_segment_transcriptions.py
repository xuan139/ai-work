import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import BackgroundTasks, HTTPException

from app import main
from app.main import (
    download_nas_asset_transcript,
    download_nas_audio_segment_transcript,
    transcribe_nas_audio_segment,
)
from app.segment_transcriptions import (
    list_audio_segment_transcriptions,
    update_audio_segment_transcription,
)


class SegmentTranscriptionStoreTests(unittest.TestCase):
    def test_persists_segment_status_and_transcript(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ,
            {"AUDIO_SEGMENT_ARCHIVE_DIR": directory},
        ):
            update_audio_segment_transcription(
                36,
                2,
                status="completed",
                progress=100,
                model_name="whisper.cpp small",
                transcript="第三段逐字稿",
            )
            result = list_audio_segment_transcriptions(36)

        self.assertEqual(result[2]["status"], "completed")
        self.assertEqual(result[2]["transcript"], "第三段逐字稿")


class SegmentTranscriptionApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_downloads_full_transcript_as_utf8_attachment(self):
        asset = {
            "id": 36,
            "user_id": 3,
            "category": "audio",
            "original_filename": "董事會錄音.m4a",
        }
        with patch("app.main.get_nas_asset", return_value=asset), patch(
            "app.main.get_meeting_by_nas_asset_id",
            return_value={"transcript": "會議逐字稿"},
        ):
            response = await download_nas_asset_transcript(36, {"id": 3, "role": "user"})

        self.assertTrue(response.body.startswith(b"\xef\xbb\xbf"))
        self.assertIn("filename*=UTF-8''", response.headers["content-disposition"])
        self.assertIn("%E8%91%A3%E4%BA%8B%E6%9C%83", response.headers["content-disposition"])

    async def test_downloads_segment_transcript_as_attachment(self):
        asset = {
            "id": 36,
            "user_id": 3,
            "category": "audio",
            "original_filename": "meeting.m4a",
        }
        with patch("app.main.get_nas_asset", return_value=asset), patch(
            "app.main.list_audio_segment_transcriptions",
            return_value={1: {"transcript": "第二段逐字稿"}},
        ):
            response = await download_nas_audio_segment_transcript(36, 1, {"id": 3, "role": "user"})

        self.assertIn('filename="meeting-segment-0002-transcript.txt"', response.headers["content-disposition"])
        self.assertIn("第二段逐字稿", response.body.decode("utf-8-sig"))

    async def test_queues_authorized_segment_with_selected_model(self):
        with tempfile.TemporaryDirectory() as directory:
            segment = Path(directory) / "segment-0001.wav"
            segment.write_bytes(b"audio")
            asset = {
                "id": 36,
                "user_id": 3,
                "category": "audio",
                "stored_path": str(Path(directory) / "source.m4a"),
                "processor_config_json": '{"asr_model_id":"local:whisper-cpp-small"}',
            }
            queued = {"status": "queued", "progress": 5}
            tasks = BackgroundTasks()
            with patch.object(main, "ACTIVE_SEGMENT_TRANSCRIPTIONS", set()), patch("app.main.get_nas_asset", return_value=asset), patch(
                "app.main.archived_media_segment_path",
                return_value=segment,
            ), patch("app.main.list_audio_segment_transcriptions", return_value={}), patch(
                "app.main.update_audio_segment_transcription",
                return_value=queued,
            ) as update:
                result = await transcribe_nas_audio_segment(
                    36,
                    0,
                    {},
                    tasks,
                    {"id": 3, "role": "user"},
                )

        self.assertEqual(result, queued)
        self.assertEqual(len(tasks.tasks), 1)
        self.assertEqual(update.call_args.kwargs["model_id"], "local:whisper-cpp-small")

    async def test_rejects_duplicate_active_segment_job(self):
        asset = {
            "id": 36,
            "user_id": 3,
            "category": "audio",
            "stored_path": "/tmp/source.m4a",
            "processor_config_json": '{"asr_model_id":"local:whisper-cpp-small"}',
        }
        with patch.object(main, "ACTIVE_SEGMENT_TRANSCRIPTIONS", {(36, 0)}), patch("app.main.get_nas_asset", return_value=asset), patch(
            "app.main.archived_media_segment_path",
            return_value=Path("/tmp/segment-0001.wav"),
        ), patch("app.main.list_audio_segment_transcriptions", return_value={}):
            with self.assertRaises(HTTPException) as raised:
                await transcribe_nas_audio_segment(
                    36,
                    0,
                    {},
                    BackgroundTasks(),
                    {"id": 3, "role": "user"},
                )

        self.assertEqual(raised.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
