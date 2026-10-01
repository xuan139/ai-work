import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db
from app.audit_context import reset_audit_context, set_audit_context
from app.auth import hash_password


class EnterpriseAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        self.user = db.create_user(username="analyst", password_hash=hash_password("test1234"), role="user")
        assert self.admin is not None

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_request_context_links_llm_and_mcp_audit_records(self) -> None:
        token = set_audit_context(
            {
                "trace_id": "trace-enterprise-001",
                "request_method": "POST",
                "request_path": "/api/llm/demo-run",
                "client_ip": "127.0.0.1",
                "user_agent": "audit-test",
            }
        )
        try:
            call = db.create_llm_call(
                user_id=self.admin["id"], provider="Local NAS", model_name="Qwen",
                model_id="local:qwen", prompt="查詢訂單", response="完成", status="completed",
                operation_type="mcp_llm", duration_ms=42,
            )
            server = db.list_mcp_servers()[0]
            db.create_mcp_audit_log(
                server_id=server["id"], user_id=self.admin["id"], action="tools/call",
                status="completed", tool_name="search_read", input_json="{}",
                output_json="{}", parent_call_id=call["id"],
            )
        finally:
            reset_audit_context(token)

        with sqlite3.connect(db.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            llm = conn.execute("SELECT * FROM llm_calls WHERE id = ?", (call["id"],)).fetchone()
            mcp = conn.execute("SELECT * FROM mcp_audit_logs ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(llm["trace_id"], "trace-enterprise-001")
        self.assertEqual(llm["request_path"], "/api/llm/demo-run")
        self.assertEqual(llm["duration_ms"], 42)
        self.assertEqual(len(llm["prompt_sha256"]), 64)
        self.assertEqual(mcp["trace_id"], llm["trace_id"])
        self.assertEqual(mcp["parent_call_id"], call["id"])
        trace_page = db.search_llm_calls(
            user_id=self.admin["id"], role="admin", trace_id="trace-enterprise-001",
        )
        self.assertEqual(len(trace_page["mcp_events_by_trace"]["trace-enterprise-001"]), 1)
        self.assertEqual(
            trace_page["mcp_events_by_trace"]["trace-enterprise-001"][0]["tool_name"],
            "search_read",
        )

    def test_multi_condition_search_paginates_and_enforces_user_scope(self) -> None:
        for index in range(26):
            db.create_llm_call(
                user_id=self.admin["id"], provider="Alibaba Cloud", model_name="Qwen Plus",
                model_id="alibaba:qwen-plus", prompt=f"monthly report {index}", response="ok",
                status="completed", access_mode="company_api_key", operation_type="llm",
            )
        db.create_llm_call(
            user_id=self.user["id"], provider="Local NAS", model_name="Qwen Local",
            model_id="local:qwen", prompt="private report", response="private", status="failed",
        )

        admin_page = db.search_llm_calls(
            user_id=self.admin["id"], role="admin", page=2, page_size=10,
            provider="Alibaba Cloud", status="completed", q="monthly report",
        )
        user_page = db.search_llm_calls(user_id=self.user["id"], role="user", page=1, page_size=25)

        self.assertEqual(admin_page["total"], 26)
        self.assertEqual(admin_page["pages"], 3)
        self.assertEqual(len(admin_page["items"]), 10)
        self.assertEqual(user_page["total"], 1)
        self.assertEqual(user_page["items"][0]["caller_username"], "analyst")


if __name__ == "__main__":
    unittest.main()
