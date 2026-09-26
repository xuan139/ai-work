import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.main import APP_VERSION, healthz, initial_admin_password


ROOT = Path(__file__).resolve().parents[1]


class SelfHostedDeploymentTests(unittest.IsolatedAsyncioTestCase):
    def test_admin_password_defaults_for_local_development(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(initial_admin_password(), "admin123")

    def test_admin_password_can_be_provided_by_installer(self) -> None:
        with patch.dict(os.environ, {"AI_WORK_ADMIN_PASSWORD": "customer-secret-123"}, clear=True):
            self.assertEqual(initial_admin_password(), "customer-secret-123")

    def test_short_installer_password_is_rejected(self) -> None:
        with patch.dict(os.environ, {"AI_WORK_ADMIN_PASSWORD": "short"}, clear=True):
            with self.assertRaises(RuntimeError):
                initial_admin_password()

    async def test_health_endpoint_is_public_and_versioned(self) -> None:
        self.assertEqual(
            await healthz(),
            {"status": "ok", "service": "ai-work-nas", "version": APP_VERSION},
        )

    def test_native_installer_offers_optional_ai_modules(self) -> None:
        installer = (ROOT / "deploy/self-hosted/install-modules.sh").read_text()
        for value in ("core", "knowledge", "meeting", "complete", "custom"):
            self.assertIn(value, installer)
        for variable in (
            "AI_WORK_INSTALL_OCR",
            "AI_WORK_INSTALL_EMBEDDING",
            "AI_WORK_INSTALL_WHISPER",
            "AI_WORK_LOCAL_LLM",
        ):
            self.assertIn(variable, installer)

    def test_optional_local_services_remain_loopback_only(self) -> None:
        embedding = (ROOT / "deploy/self-hosted/ai-work-embedding.service").read_text()
        llm = (ROOT / "deploy/self-hosted/ai-work-llm.service").read_text()
        self.assertIn("--host 127.0.0.1 --port 8081", embedding)
        self.assertIn("--host 127.0.0.1 --port 8080", llm)
