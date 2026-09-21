import asyncio
import unittest
from pathlib import Path
from unittest.mock import patch

from app import main


ROOT = Path(__file__).resolve().parent.parent


class N8nIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.admin = {"id": 1, "username": "admin", "role": "admin"}

    def test_admin_status_reports_n8n_service(self) -> None:
        status = {
            "status": "connected",
            "version": "2.39.8",
            "public_url": "/n8n/",
            "test_workflow": "AI Work NAS 測試流程",
            "response_ms": 12,
        }
        with patch.object(main, "n8n_service_status", return_value=status):
            response = asyncio.run(main.admin_n8n_status(admin=self.admin))

        self.assertEqual(response, status)

    def test_nginx_auth_endpoint_accepts_admin_dependency(self) -> None:
        response = asyncio.run(main.n8n_proxy_auth(admin=self.admin))
        self.assertEqual(response.status_code, 204)

    def test_admin_menu_and_bilingual_page_are_present(self) -> None:
        index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="n8nNav"', index)
        self.assertIn('id="n8nSection"', index)
        self.assertIn('href="/n8n/"', index)
        self.assertIn('n8n: "n8n 自動化"', app)
        self.assertIn('n8n: "n8n Automation"', app)
        self.assertIn('/api/admin/n8n/status', app)

    def test_compose_is_pinned_and_loopback_only(self) -> None:
        compose = (ROOT / "deploy" / "n8n" / "compose.yml").read_text(encoding="utf-8")
        self.assertIn("docker.n8n.io/n8nio/n8n:2.39.8", compose)
        self.assertIn('"127.0.0.1:5678:5678"', compose)
        self.assertIn("N8N_PATH: /n8n/", compose)


if __name__ == "__main__":
    unittest.main()
