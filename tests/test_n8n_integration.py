import asyncio
import json
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import main
from app import n8n_service


ROOT = Path(__file__).resolve().parent.parent


class N8nIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.admin = {"id": 1, "username": "admin", "role": "admin"}

    def test_admin_status_reports_n8n_service(self) -> None:
        status = {
            "status": "connected",
            "version": "2.39.8",
            "public_url": "/n8n/",
            "test_workflow": "AI Work NAS 處理完成通知 Demo",
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
        self.assertIn('step4Title: "推送企業 LINE"', app)

    def test_completed_pdf_is_sent_to_n8n(self) -> None:
        asset = {
            "id": 21,
            "category": "pdf",
            "status": "completed",
            "title": "季度報告",
            "original_filename": "report.pdf",
            "analyzer": "PyMuPDF + RAG",
            "summary": "摘要",
            "chunk_count": 1,
            "owner_username": "admin",
            "updated_at": "2026-09-21 12:00:00",
        }
        chunks = [{"content": "第一季營收成長。"}]
        with patch.object(n8n_service, "_post_asset_event", return_value={"status": "pushed"}) as post:
            result = asyncio.run(n8n_service.notify_n8n_asset_completed(asset, chunks))

        self.assertEqual(result["status"], "pushed")
        self.assertEqual(post.call_args.args[0]["asset_id"], 21)
        self.assertEqual(post.call_args.args[0]["result_preview"], "第一季營收成長。")

    def test_n8n_callback_pushes_to_first_approved_group(self) -> None:
        groups = [
            {"source_id": "blocked", "source_type": "group", "is_approved": 0, "display_name": "Blocked"},
            {"source_id": "approved", "source_type": "group", "is_approved": 1, "display_name": "Company"},
        ]
        payload = {
            "event": "nas.asset.completed",
            "asset_id": 21,
            "category": "pdf",
            "title": "季度報告",
            "analyzer": "RAG",
            "uploader": "admin",
            "summary": "摘要",
        }
        with (
            patch.object(main, "list_line_sources", return_value=groups),
            patch.object(main, "get_meeting_by_nas_asset_id", return_value=None),
            patch.object(main, "push_line_messages", new=AsyncMock(return_value={"ok": True})) as push,
        ):
            result = asyncio.run(main.n8n_push_result(payload, None))

        self.assertEqual(result["status"], "pushed")
        self.assertEqual(push.await_args.args[0], "approved")
        self.assertIn("季度報告", push.await_args.args[1][0])

    def test_n8n_callback_skips_when_no_group_is_approved(self) -> None:
        payload = {"event": "nas.asset.completed", "asset_id": 21, "category": "audio"}
        with (
            patch.object(main, "list_line_sources", return_value=[]),
            patch.object(main, "get_meeting_by_nas_asset_id", return_value=None),
        ):
            result = asyncio.run(main.n8n_push_result(payload, None))
        self.assertEqual(result, {"status": "skipped", "reason": "no_approved_line_group"})

    def test_compose_is_pinned_and_loopback_only(self) -> None:
        compose = (ROOT / "deploy" / "n8n" / "compose.yml").read_text(encoding="utf-8")
        self.assertIn("docker.n8n.io/n8nio/n8n:2.39.8", compose)
        self.assertIn('"127.0.0.1:5678:5678"', compose)
        self.assertIn("AI_WORK_N8N_TOKEN", compose)

        workflow = json.loads(
            (ROOT / "deploy/n8n/bootstrap/ai-work-nas-asset-completed.json").read_text(encoding="utf-8")
        )
        self.assertTrue(workflow["id"])
        self.assertEqual(workflow["nodes"][0]["parameters"]["path"], "ai-work-nas-asset-completed")
        self.assertIn("/api/internal/n8n/push-result", json.dumps(workflow))
        self.assertIn("https://goldsys.io/api/internal/n8n/push-result", json.dumps(workflow))
        self.assertIn("__AI_WORK_N8N_TOKEN__", json.dumps(workflow))
        self.assertIn("N8N_PATH: /n8n/", compose)

        nginx = (ROOT / "deploy" / "n8n" / "nginx-location.conf").read_text(encoding="utf-8")
        self.assertIn("proxy_pass http://127.0.0.1:5678/;", nginx)


if __name__ == "__main__":
    unittest.main()
