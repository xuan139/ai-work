import os
import unittest
from unittest.mock import patch

from app.main import APP_VERSION, healthz, initial_admin_password


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
