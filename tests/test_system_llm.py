import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app import db, main
from app.auth import hash_password
from app.system_llm import current_llm_model, current_llm_state


class SystemLlmTests(unittest.TestCase):
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

    def test_default_model_is_local_qwen(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(current_llm_model()["id"], "local:qwen3-4b")
            self.assertTrue(current_llm_state()["is_default"])

    def test_installer_can_select_smaller_default_local_model(self) -> None:
        with patch.dict(os.environ, {"AI_WORK_DEFAULT_LLM_MODEL_ID": "local:qwen3-1.7b"}):
            self.assertEqual(current_llm_model()["id"], "local:qwen3-1.7b")

    def test_admin_can_set_company_model(self) -> None:
        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "company-key"}):
            result = asyncio.run(
                main.set_current_llm({"model_id": "alibaba:qwen-plus"}, admin=self.admin)
            )

        self.assertEqual(result["model"]["id"], "alibaba:qwen-plus")
        self.assertEqual(result["updated_by"], "admin")
        self.assertFalse(result["is_default"])

    def test_cloud_model_without_company_key_is_rejected(self) -> None:
        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": ""}):
            with self.assertRaises(HTTPException) as context:
                asyncio.run(
                    main.set_current_llm({"model_id": "alibaba:qwen-plus"}, admin=self.admin)
                )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(current_llm_model()["id"], "local:qwen3-4b")

    def test_ai_work_request_uses_system_model_instead_of_client_model(self) -> None:
        db.set_system_setting("current_llm_model_id", "free:openai-fast", self.admin["id"])
        run = AsyncMock(return_value={"answer": "ok"})
        with patch.object(main, "run_model_with_audit", run):
            asyncio.run(
                main.llm_run(
                    {"model_id": "local:qwen3-4b", "prompt": "hello"},
                    user=self.admin,
                )
            )

        self.assertEqual(run.await_args.kwargs["model_id"], "free:openai-fast")

    def test_translation_and_line_expose_only_system_model(self) -> None:
        db.set_system_setting("current_llm_model_id", "free:openai-fast", self.admin["id"])

        enabled, translation_model, api_key = main.validate_translation_selection(
            enabled="true",
            target="zh-Hant",
            model_id="local:qwen3-4b",
            api_key="",
        )

        self.assertTrue(enabled)
        self.assertEqual(translation_model["id"], "free:openai-fast")
        self.assertIsNone(api_key)
        self.assertEqual([model["id"] for model in main.company_line_models()], ["free:openai-fast"])


if __name__ == "__main__":
    unittest.main()
