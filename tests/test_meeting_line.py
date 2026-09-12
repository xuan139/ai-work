import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import db, meeting_line
from app.auth import hash_password
from app.line_service import LineServiceError


class MeetingLineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        assert self.admin is not None
        db.upsert_line_source(
            source_id="G1", source_type="group", display_name="大群組",
            owner_user_id=self.admin["id"], is_approved=True,
        )
        self.asset = db.create_nas_asset(
            user_id=self.admin["id"], category="audio", title="產品週會",
            original_filename="weekly.wav", stored_path="/nas/weekly.wav",
            mime_type="audio/wav", file_size=100, status="completed", analyzer="Whisper",
        )
        db.replace_document_chunks(
            self.asset["id"],
            [{
                "chunk_index": 0, "content": "決定週五發布。Claire 負責完成測試。",
                "token_estimate": 12, "page_number": None, "chunk_type": "audio_transcript",
                "image_path": None, "metadata_json": "{}",
            }],
        )
        db.update_nas_asset(
            self.asset["id"], status="completed", analyzer="Whisper", summary="ready", chunk_count=1
        )

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def create_meeting(self) -> dict:
        meeting = db.create_meeting(
            user_id=self.admin["id"], source="web_upload", title="產品週會",
            original_filename="weekly.wav", audio_path="/nas/weekly.wav", status="processing",
            nas_asset_id=self.asset["id"], asr_model_id="local:whisper-cpp-small",
            asr_provider="Local NAS", asr_model="whisper.cpp small", asr_engine="whisper.cpp",
            line_push_enabled=True, line_group_id="G1", line_group_name="大群組",
            line_push_full_transcript=True,
        )
        return db.update_meeting_status(
            meeting["id"], status="completed", transcript="決定週五發布。Claire 負責完成測試。"
        )

    def test_completed_meeting_is_linked_and_pushed(self) -> None:
        meeting = self.create_meeting()
        run_result = {
            "access_mode": "local_nas", "answer": "會議摘要\n決議：週五發布\n待辦：Claire 完成測試",
            "usage": {"input_tokens": 20, "output_tokens": 12, "total_tokens": 32},
        }
        push = AsyncMock(return_value={"ok": True, "sent_count": 2})
        with patch.object(meeting_line, "run_llm", AsyncMock(return_value=run_result)), patch.object(
            meeting_line, "push_line_messages", push
        ):
            asyncio.run(meeting_line.push_completed_meeting_to_line(meeting["id"]))

        updated = db.get_meeting(meeting["id"])
        self.assertEqual(updated["status"], "completed")
        self.assertEqual(updated["line_push_status"], "completed")
        self.assertIn("週五發布", updated["line_summary"])
        self.assertEqual(db.get_line_source("G1")["content_version"], 1)
        self.assertEqual(db.get_line_document(f"meeting:{meeting['id']}")["asset_id"], self.asset["id"])
        messages = push.await_args.args[1]
        self.assertIn("NAS 會議處理完成", messages[0])
        self.assertGreaterEqual(len(messages), 2)

    def test_line_failure_does_not_change_transcription_status(self) -> None:
        meeting = self.create_meeting()
        run_result = {"access_mode": "local_nas", "answer": "摘要", "usage": {}}
        with patch.object(meeting_line, "run_llm", AsyncMock(return_value=run_result)), patch.object(
            meeting_line,
            "push_line_messages",
            AsyncMock(side_effect=LineServiceError("LINE unavailable")),
        ):
            asyncio.run(meeting_line.push_completed_meeting_to_line(meeting["id"]))

        updated = db.get_meeting(meeting["id"])
        self.assertEqual(updated["status"], "completed")
        self.assertEqual(updated["line_push_status"], "failed")
        self.assertIn("LINE unavailable", updated["line_push_error"])

    def test_long_transcript_excerpt_covers_start_middle_and_end(self) -> None:
        transcript = "A" * 3000 + "MIDDLE" + "B" * 3000 + "ENDING"
        excerpt = meeting_line.meeting_summary_excerpt(transcript)
        self.assertLess(len(excerpt), 3000)
        self.assertIn("[開頭]", excerpt)
        self.assertIn("MIDDLE", excerpt)
        self.assertTrue(excerpt.endswith("ENDING"))

    def test_finishing_line_document_twice_only_versions_source_once(self) -> None:
        meeting = self.create_meeting()
        source = db.upsert_line_source(
            source_id="G1", source_type="group", display_name="大群組", owner_user_id=self.admin["id"]
        )
        document = db.create_line_document(
            line_source_id=source["id"], line_message_id=f"meeting:{meeting['id']}",
            line_event_id=None, sender_id="portal", sender_name="admin", asset_id=self.asset["id"],
        )
        db.finish_line_document(document["id"], status="completed", summary="摘要", error_message=None)
        db.finish_line_document(document["id"], status="completed", summary="摘要", error_message=None)
        self.assertEqual(db.get_line_source("G1")["content_version"], 1)


if __name__ == "__main__":
    unittest.main()
