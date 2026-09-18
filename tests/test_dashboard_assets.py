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

    def test_assets_include_uploader_and_newest_is_first(self) -> None:
        older = db.create_nas_asset(
            user_id=self.admin["id"],
            category="file",
            title="Older file",
            original_filename="older.txt",
            stored_path="/nas/older.txt",
            mime_type="text/plain",
            file_size=10,
            status="completed",
        )
        newer = db.create_nas_asset(
            user_id=self.admin["id"],
            category="file",
            title="Newer file",
            original_filename="newer.txt",
            stored_path="/nas/newer.txt",
            mime_type="text/plain",
            file_size=5,
            status="completed",
        )
        with db.connect() as conn:
            conn.execute("UPDATE nas_assets SET created_at = '2026-09-17 08:00:00' WHERE id = ?", (older["id"],))
            conn.execute("UPDATE nas_assets SET created_at = '2026-09-18 08:00:00' WHERE id = ?", (newer["id"],))

        assets = db.list_nas_assets(user_id=self.admin["id"], role="admin")

        self.assertEqual([asset["id"] for asset in assets[:2]], [newer["id"], older["id"]])
        self.assertEqual(assets[0]["owner_username"], "admin")

    def test_dashboard_renders_upload_metadata(self) -> None:
        script = (Path(__file__).resolve().parents[1] / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('class="dashboard-asset-upload"', script)
        self.assertIn('t("dashboardAssets.uploader")', script)
        self.assertIn('t("dashboardAssets.uploadedAt")', script)
        self.assertNotIn('Number(right.file_size || 0) - Number(left.file_size || 0)', script)


if __name__ == "__main__":
    unittest.main()
