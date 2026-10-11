import asyncio
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.error import HTTPError

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import db, main, notion_demo, notion_mcp
from app.auth import current_user, hash_password

PAGE_ID = "12345678-1234-1234-1234-123456789abc"
PAGE = {"id": PAGE_ID, "properties": {"Name": {"type": "title", "title": [{"plain_text": "採購 SOP"}]}},
        "url": "https://evil.example/", "last_edited_time": "2026-10-12T00:00:00Z"}


class NotionMcpTests(unittest.TestCase):
    def test_discovery_needs_no_provider_key_and_exposes_only_reads(self):
        result = notion_mcp.handle_notion_mcp_request({"id": 1, "method": "tools/list"}, "")
        self.assertEqual(len(result["result"]["tools"]), 3)
        self.assertTrue(all(t["annotations"]["readOnlyHint"] for t in result["result"]["tools"]))
        self.assertIsNone(notion_mcp.handle_notion_mcp_request({"method": "notifications/initialized"}, ""))

    @patch.object(notion_mcp, "_request")
    def test_search_preserves_pagination_and_uses_title_filter(self, request):
        request.return_value = {"results": [PAGE], "has_more": True, "next_cursor": "next-token"}
        result = notion_mcp.call_notion_tool("notion_search", {"query": "採購", "start_cursor": "cursor", "page_size": 3}, "secret")
        self.assertEqual(result["next_cursor"], "next-token")
        self.assertTrue(result["has_more"])
        self.assertEqual(result["pages"][0]["title"], "採購 SOP")
        self.assertTrue(result["pages"][0]["url"].startswith("https://www.notion.so/"))
        self.assertEqual(request.call_args.args[2]["filter"], {"property": "object", "value": "page"})
        self.assertEqual(request.call_args.args[2]["start_cursor"], "cursor")

    @patch.object(notion_mcp, "_request")
    def test_page_reads_text_and_exposes_nested_blocks(self, request):
        request.side_effect = [PAGE, {"results": [{"id": PAGE_ID, "type": "to_do", "has_children": True,
                                                  "to_do": {"checked": True, "rich_text": [{"plain_text": "驗收"}]}}],
                                     "has_more": True, "next_cursor": "next"}]
        result = notion_mcp.call_notion_tool("notion_read_page", {"page_id": PAGE_ID}, "secret")
        self.assertEqual(result["blocks"][0]["text"], "[x] 驗收")
        self.assertTrue(result["blocks"][0]["has_children"])
        self.assertEqual(result["next_cursor"], "next")
        self.assertEqual(request.call_count, 2)

    @patch.object(notion_mcp, "_request")
    def test_invalid_ids_types_and_write_tools_never_reach_network(self, request):
        for name, arguments in [("notion_read_page", {"page_id": "../../users"}),
                                ("notion_search", {"page_size": True}),
                                ("notion_search", {"page_size": 999}),
                                ("notion_search", {"query": None}),
                                ("notion_search", {"url": "http://localhost"}),
                                ("notion_search", {"query": "x" * 201}),
                                ("notion_create_page", {})]:
            with self.subTest(name=name, arguments=arguments):
                result = notion_mcp.handle_notion_mcp_request({"id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}, "secret")
                self.assertTrue(result["result"]["isError"])
        request.assert_not_called()

    def test_oversize_block_text_reports_truncation(self):
        result = notion_mcp._blocks({"results": [{"id": PAGE_ID, "type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "字" * 7000}]}}]})
        self.assertEqual(len(result["blocks"][0]["text"]), notion_mcp.MAX_TEXT_CHARS)
        self.assertTrue(result["text_truncated"])

    @patch.object(notion_mcp, "build_opener")
    def test_api_errors_hide_upstream_body_and_credentials(self, opener):
        for status in (401, 403, 404, 429, 500, 302):
            opener.return_value.open.side_effect = HTTPError("https://api.notion.com", status, "SECRET", {}, io.BytesIO(b"secret-key"))
            with self.assertRaises(notion_mcp.NotionApiError) as raised:
                notion_mcp._request("search", "secret-key", {})
            self.assertNotIn("secret", str(raised.exception).lower())

    @patch.object(notion_mcp, "build_opener")
    def test_transport_is_versioned_bounded_and_disallows_redirects(self, opener):
        response = opener.return_value.open.return_value.__enter__.return_value
        response.read.return_value = b'{"results": []}'
        notion_mcp._request("search", "secret", {})
        req = opener.return_value.open.call_args.args[0]
        self.assertEqual(req.full_url, "https://api.notion.com/v1/search")
        self.assertEqual(req.get_header("Notion-version"), "2025-09-03")
        self.assertEqual(req.get_method(), "POST")
        response.read.assert_called_once_with(notion_mcp.MAX_RESPONSE_BYTES + 1)
        self.assertIsNone(opener.call_args.args[0].redirect_request(None, None, 302, "", {}, "https://evil.example"))


class NotionDemoTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "test.db")
        self.db_patch.start()
        self.env = patch.dict(os.environ, {"NOTION_API_KEY": "test-secret"})
        self.env.start()
        db.init_db(); db.seed_admin(hash_password("test-password"))
        self.admin = db.get_user_by_username("admin")
        self.server = notion_demo.demo_server()
        self.client = TestClient(main.app)
        main.app.dependency_overrides[current_user] = lambda: self.admin

    def tearDown(self):
        main.app.dependency_overrides.clear()
        self.client.close(); self.env.stop(); self.db_patch.stop(); self.directory.cleanup()

    def plan(self, name, args):
        return {"call_id": 10, "answer": json.dumps({"action": "tool", "server_id": self.server["id"], "tool_name": name, "arguments": args})}

    @patch.object(notion_mcp, "_request")
    def test_search_read_answer_and_audit(self, request):
        request.side_effect = [{"results": [PAGE]}, PAGE, {"results": [{"id": PAGE_ID, "type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "倉管驗收"}]}}]}]
        model = AsyncMock(side_effect=[self.plan("notion_search", {"query": "採購"}), self.plan("notion_read_page", {"page_id": PAGE_ID}),
                                     {"call_id": 11, "answer": '{"action":"answer"}'},
                                     {"call_id": 12, "model": "Qwen", "answer": "由倉管驗收。"}])
        result = asyncio.run(notion_demo.run_notion_demo(prompt="採購 SOP", model_id="local:qwen3-4b", user=self.admin, run_model=model))
        self.assertEqual([step["tool"] for step in result["steps"]], ["notion_search", "notion_read_page"])
        self.assertEqual(result["sources"][0]["page_id"], PAGE_ID)
        self.assertIn("倉管驗收", model.await_args_list[-1].kwargs["prompt"])
        self.assertIn("untrusted data", model.await_args_list[-1].kwargs["system_prompt"])
        self.assertNotIn("test-secret", json.dumps(result))
        with db.connect() as conn:
            rows = conn.execute("SELECT status FROM mcp_audit_logs").fetchall()
        self.assertEqual([row["status"] for row in rows], ["completed", "completed"])

    @patch.object(notion_mcp, "_request", side_effect=notion_mcp.NotionApiError("Notion 404"))
    def test_failure_is_audited_and_no_final_answer_generated(self, request):
        model = AsyncMock(return_value=self.plan("notion_search", {}))
        with self.assertRaises(HTTPException):
            asyncio.run(notion_demo.run_notion_demo(prompt="最近頁面", model_id="local:qwen3-4b", user=self.admin, run_model=model))
        self.assertEqual(model.await_count, 1)
        with db.connect() as conn:
            self.assertEqual(conn.execute("SELECT status FROM mcp_audit_logs").fetchone()["status"], "failed")

    def test_admin_routes_and_regular_user_mcp_visibility(self):
        main.app.dependency_overrides[current_user] = lambda: {"id": 99, "role": "user"}
        for path, payload in [("/api/notion-demo/status", None), ("/api/notion-demo/ask", {"prompt": "hi"}),
                              ("/api/notion-demo/tools/call", {"name": "notion_search"})]:
            response = self.client.get(path) if payload is None else self.client.post(path, json=payload)
            self.assertEqual(response.status_code, 403)
        self.assertNotIn("notion-readonly", [s["slug"] for s in main.mcp_servers_for_user({"role": "user"})])
        with patch.object(main, "run_model_with_audit", new_callable=AsyncMock) as model:
            with self.assertRaises(HTTPException):
                asyncio.run(main.run_model_with_mcp(model_id="local:qwen3-4b", prompt="read", api_key=None,
                    user={"id": 99, "role": "user"}, selected_server_id=self.server["id"]))
            model.assert_not_awaited()

    def test_missing_configuration_does_not_claim_connected(self):
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}), patch.object(main, "run_model_with_audit", new_callable=AsyncMock) as model:
            status = self.client.get("/api/notion-demo/status").json()
            self.assertFalse(status["configured"]); self.assertFalse(status["connection_verified"])
            response = self.client.post("/api/notion-demo/ask", json={"prompt": "最近頁面"})
            self.assertEqual(response.status_code, 503)
            model.assert_not_awaited()

    def test_mcp_requires_separate_key(self):
        with patch.dict(os.environ, {"NOTION_LOCAL_MCP_KEY": "internal-key"}):
            payload = {"id": 1, "method": "tools/list"}
            self.assertEqual(self.client.post("/mcp/notion", json=payload).status_code, 401)
            response = self.client.post("/mcp/notion", json=payload, headers={"Authorization": "Bearer internal-key"})
            self.assertEqual(len(response.json()["result"]["tools"]), 3)

    def test_bad_input_and_unauthed_user(self):
        self.assertEqual(self.client.post("/api/notion-demo/ask", json={"prompt": "x" * 1001}).status_code, 400)
        main.app.dependency_overrides.clear()
        self.assertEqual(self.client.get("/api/notion-demo/status").status_code, 401)


if __name__ == "__main__":
    unittest.main()
