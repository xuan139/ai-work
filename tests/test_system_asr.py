import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from app import db, main
from app.auth import hash_password
from app.system_asr import current_asr_model, current_asr_state


class SystemAsrTests(unittest.TestCase):
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

    def test_default_model_is_whisper_cpp_small(self) -> None:
        self.assertEqual(current_asr_model()["id"], "local:whisper-cpp-small")
        self.assertTrue(current_asr_state()["is_default"])

    def test_admin_can_set_installed_local_model(self) -> None:
        with patch.object(main, "local_model_status", return_value={"installed": True}):
            result = asyncio.run(
                main.set_current_asr(
                    {"model_id": "local:funasr-paraformer-zh"},
                    admin=self.admin,
                )
            )

        self.assertEqual(result["model"]["id"], "local:funasr-paraformer-zh")
        self.assertEqual(result["updated_by"], "admin")
        self.assertFalse(result["is_default"])

    def test_uninstalled_local_model_is_rejected(self) -> None:
        with patch.object(main, "local_model_status", return_value={"installed": False}):
            with self.assertRaises(HTTPException) as context:
                asyncio.run(
                    main.set_current_asr(
                        {"model_id": "local:sensevoice-small"},
                        admin=self.admin,
                    )
                )

        self.assertEqual(context.exception.status_code, 400)

    def test_cloud_model_without_company_key_is_rejected(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaises(HTTPException) as context:
                asyncio.run(
                    main.set_current_asr(
                        {"model_id": "cloud:openai-gpt-4o-transcribe"},
                        admin=self.admin,
                    )
                )

        self.assertEqual(context.exception.status_code, 400)

    def test_catalog_exposes_current_system_model(self) -> None:
        db.set_system_setting("current_asr_model_id", "local:sensevoice-small", self.admin["id"])

        result = asyncio.run(main.asr_models(user=self.admin))

        self.assertEqual(result["current_model"]["id"], "local:sensevoice-small")
        self.assertEqual(result["current_model_updated_by"], "admin")


if __name__ == "__main__":
    unittest.main()
