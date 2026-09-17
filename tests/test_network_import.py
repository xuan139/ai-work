import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import BackgroundTasks, HTTPException

from app import db
from app.auth import hash_password
from app.main import import_youtube
from app.network_import import validate_youtube_url


class NetworkImportTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.main_db_patch = patch("app.main.create_nas_asset", side_effect=db.create_nas_asset)
        self.main_update_patch = patch("app.main.update_nas_asset", side_effect=db.update_nas_asset)
        self.db_patch.start()
        self.main_db_patch.start()
        self.main_update_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        assert self.admin is not None

    def tearDown(self) -> None:
        self.main_update_patch.stop()
        self.main_db_patch.stop()
        self.db_patch.stop()
        self.directory.cleanup()

    def test_accepts_video_and_short_youtube_urls(self) -> None:
        self.assertEqual(
            validate_youtube_url("https://www.youtube.com/watch?v=abc123#chapter"),
            "https://www.youtube.com/watch?v=abc123",
        )
        self.assertEqual(validate_youtube_url("https://youtu.be/abc123"), "https://youtu.be/abc123")

    def test_rejects_non_youtube_urls(self) -> None:
        with self.assertRaises(ValueError):
            validate_youtube_url("https://example.com/video")

    async def test_creates_persistent_download_record(self) -> None:
        background_tasks = BackgroundTasks()
        with patch("app.main.manager.broadcast", new=AsyncMock()) as broadcast:
            result = await import_youtube(
                {
                    "url": "https://www.youtube.com/watch?v=abc123",
                    "title": "Company training",
                    "media_type": "audio",
                    "authorized": True,
                },
                background_tasks,
                self.admin,
            )

        self.assertEqual(result["status"], "downloading")
        self.assertEqual(result["category"], "audio")
        self.assertEqual(result["source_type"], "youtube")
        self.assertEqual(len(background_tasks.tasks), 1)
        self.assertEqual(db.list_network_assets(user_id=self.admin["id"], role="admin")[0]["id"], result["id"])
        broadcast.assert_awaited_once()

    async def test_requires_rights_confirmation(self) -> None:
        with self.assertRaises(HTTPException) as caught:
            await import_youtube(
                {
                    "url": "https://youtu.be/abc123",
                    "media_type": "video",
                    "authorized": False,
                },
                BackgroundTasks(),
                self.admin,
            )
        self.assertEqual(caught.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
