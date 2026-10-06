import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import db, langchain_demo, main
from app.auth import create_session_token, hash_password
from app.mcp_orchestrator import available_mcp_servers


class LangChainDemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.user = db.get_user_by_username("admin")
        assert self.user is not None
        self.other_user = db.create_user(username="other", password_hash=hash_password("password123"), role="user")
        self.server = {
            "id": 42,
            "slug": "odoo",
            "name": "Goldsys Odoo",
            "is_enabled": True,
            "status": "connected",
            "transport": "streamable_http",
            "endpoint": "https://odoo.example.com/mcp",
            "tools_json": json.dumps(
                [
                    {"name": "search_read", "description": "Search Odoo records", "inputSchema": {"type": "object"}},
                    {"name": "create_records", "inputSchema": {"type": "object"}},
                ]
            ),
        }
        self.server = available_mcp_servers([self.server])[0]

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_langchain_chain_calls_read_only_odoo_and_audits_both_model_and_tool(self) -> None:
        run_model = AsyncMock(
            side_effect=[
                {"call_id": 11, "answer": json.dumps({
                    "action": "tool", "server_id": 42, "tool_name": "search_read",
                    "arguments": {"model": "sale.order", "domain": "[]", "limit": 10},
                })},
                {"call_id": 12, "model": "Qwen3 4B", "answer": "最新銷售訂單為 S00001。"},
            ]
        )
        result_data = {"structuredContent": {"orders": [{"name": "S00001"}]}, "isError": False}
        with patch.object(langchain_demo, "call_streamable_http_tool", return_value=result_data) as tool:
            result = asyncio.run(langchain_demo.run_odoo_langchain_demo(
                prompt="查詢最新銷售訂單", model_id="local:qwen3-4b", user=self.user,
                server=self.server, run_model=run_model,
                history=[{"role": "user", "content": "請查銷售"}, {"role": "assistant", "content": "上一筆 S00001"}],
            ))

        self.assertEqual(result["pipeline"], "LangChain LCEL")
        self.assertEqual(result["source"]["tool"], "search_read")
        self.assertEqual(len(result["steps"]), 3)
        self.assertEqual(run_model.await_count, 2)
        self.assertIn("RECENT CONVERSATION", run_model.await_args_list[0].kwargs["prompt"])
        self.assertIn("S00001", run_model.await_args_list[1].kwargs["prompt"])
        self.assertIn("untrusted data", run_model.await_args_list[1].kwargs["system_prompt"])
        tool.assert_called_once()
        with db.connect() as conn:
            audit = conn.execute("SELECT * FROM mcp_audit_logs WHERE user_id = ?", (self.user["id"],)).fetchone()
        self.assertEqual(audit["status"], "completed")

    def test_tool_error_does_not_generate_answer(self) -> None:
        run_model = AsyncMock(return_value={"call_id": 13, "model": "Qwen3 4B", "answer": "should not run"})
        with patch.object(langchain_demo, "call_streamable_http_tool", return_value={"isError": True, "content": []}):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(langchain_demo.run_odoo_langchain_demo(
                    prompt="查詢 Odoo 聯絡人", model_id="local:qwen3-4b", user=self.user,
                    server=self.server, run_model=run_model,
                ))
        self.assertEqual(raised.exception.status_code, 502)
        run_model.assert_not_awaited()
        with db.connect() as conn:
            audit = conn.execute("SELECT status FROM mcp_audit_logs ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(audit["status"], "failed")

    def test_memory_is_persistent_and_private_per_user(self) -> None:
        db.save_langchain_demo_exchange(self.user["id"], "訂單是什麼？", "S00001", {"server": "Odoo", "tool": "search_read"})
        db.save_langchain_demo_exchange(self.other_user["id"], "我的訂單？", "P00001", {"server": "Odoo", "tool": "search_read"})
        self.assertEqual(len(db.list_langchain_demo_messages(self.user["id"])), 2)
        self.assertEqual(db.list_langchain_demo_messages(self.other_user["id"])[0]["content"], "我的訂單？")
        db.clear_langchain_demo_messages(self.user["id"])
        self.assertEqual(db.list_langchain_demo_messages(self.user["id"]), [])
        self.assertEqual(len(db.list_langchain_demo_messages(self.other_user["id"])), 2)

    def test_page_and_history_require_login(self) -> None:
        client = TestClient(main.app)
        self.assertEqual(client.get("/langchain-demo").status_code, 401)
        self.assertEqual(client.get("/api/langchain-demo/messages").status_code, 401)
        token = create_session_token(self.user["id"], self.user["session_version"])
        client.cookies.set("ai_work_session", token)
        self.assertEqual(client.get("/langchain-demo").status_code, 200)
        self.assertEqual(client.get("/api/langchain-demo/messages").json(), {"messages": []})

    def test_http_answer_persists_memory_and_reuses_it_on_follow_up(self) -> None:
        client = TestClient(main.app)
        token = create_session_token(self.user["id"], self.user["session_version"])
        client.cookies.set("ai_work_session", token)
        run_chain = AsyncMock(side_effect=[
            {"answer": "S00001", "source": {"server": "Goldsys Odoo", "tool": "search_read"}},
            {"answer": "客戶為甲公司", "source": {"server": "Goldsys Odoo", "tool": "search_read"}},
        ])
        with (
            patch.object(main, "list_mcp_servers", return_value=[self.server]),
            patch.object(main, "run_odoo_langchain_demo", new=run_chain),
        ):
            self.assertEqual(client.get("/api/langchain-demo/status").json()["odoo"]["slug"], "odoo")
            self.assertEqual(client.post("/api/langchain-demo/ask", json={"prompt": "最新訂單？"}).status_code, 200)
            self.assertEqual(client.post("/api/langchain-demo/ask", json={"prompt": "第一筆客戶？"}).status_code, 200)
        self.assertEqual(run_chain.await_args_list[0].kwargs["history"], [])
        self.assertEqual(len(run_chain.await_args_list[1].kwargs["history"]), 2)
        self.assertEqual(len(client.get("/api/langchain-demo/messages").json()["messages"]), 4)
        self.assertEqual(client.delete("/api/langchain-demo/messages").json(), {"ok": True})
        self.assertEqual(client.get("/api/langchain-demo/messages").json(), {"messages": []})


if __name__ == "__main__":
    unittest.main()
