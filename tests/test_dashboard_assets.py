import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db
from app.auth import hash_password


class DashboardAssetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        assert self.admin is not None

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_audio_asset_includes_transcript_preview(self) -> None:
        asset = db.create_nas_asset(
            user_id=self.admin["id"],
            category="audio",
            title="Weekly meeting",
            original_filename="meeting.m4a",
            stored_path="/nas/meeting.m4a",
            mime_type="audio/mp4",
            file_size=1024,
            status="completed",
        )
        db.replace_document_chunks(
            asset["id"],
            [
                {
                    "chunk_index": 0,
                    "content": "會議確認本週交付項目與負責人。",
                    "token_estimate": 12,
                    "chunk_type": "audio_transcript",
                }
            ],
        )

        assets = db.list_nas_assets(user_id=self.admin["id"], role="admin")

        self.assertEqual(assets[0]["transcript_preview"], "會議確認本週交付項目與負責人。")


if __name__ == "__main__":
    unittest.main()
