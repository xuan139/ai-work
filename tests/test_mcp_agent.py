import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import db, main
from app.auth import hash_password
from app.mcp_orchestrator import (
    McpPlanningError,
    available_mcp_servers,
    build_final_prompt,
    parse_mcp_plan,
    resolve_planned_tool,
)
from app.nas_mcp import NAS_MCP_TOOLS


class McpAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.user = db.get_user_by_username("admin")
        assert self.user is not None
        self.server = next(item for item in db.list_mcp_servers() if item["slug"] == "nas-demo")
        db.update_mcp_server_sync(
            self.server["id"],
            status="connected",
            protocol_version="2025-06-18",
            tools_json=json.dumps(NAS_MCP_TOOLS, ensure_ascii=False),
            tool_count=len(NAS_MCP_TOOLS),
            last_error=None,
        )
        self.server = db.get_mcp_server(self.server["id"])
        assert self.server is not None

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_only_explicit_read_only_tools_are_available(self) -> None:
        servers = available_mcp_servers([self.server])
        self.assertEqual(len(servers), 1)
        self.assertEqual(len(servers[0]["tools"]), 4)

        unsafe = dict(self.server)
        unsafe["tools_json"] = json.dumps([{"name": "delete_file", "annotations": {"destructiveHint": True}}])
        self.assertEqual(available_mcp_servers([unsafe]), [])

    def test_linear_read_only_endpoint_accepts_unannotated_tools(self) -> None:
        linear = {
            **self.server,
            "slug": "linear",
            "endpoint": "https://mcp.linear.app/mcp/readonly",
            "tools_json": json.dumps([{"name": "list_issues", "inputSchema": {"type": "object"}}]),
        }
        self.assertEqual(available_mcp_servers([linear])[0]["tools"][0]["name"], "list_issues")
        linear["endpoint"] = "https://mcp.linear.app/mcp"
        self.assertEqual(available_mcp_servers([linear]), [])

    def test_odoo_allows_only_known_read_only_tools(self) -> None:
        odoo = {
            **self.server,
            "slug": "odoo",
            "endpoint": "https://odoo.example.com/mcp",
            "tools_json": json.dumps(
                [
                    {"name": "search_read", "annotations": {}},
                    {"name": "whoami", "annotations": {}},
                    {"name": "create_records", "annotations": {}},
                    {"name": "call_method", "annotations": {}},
                ]
            ),
        }
        tools = available_mcp_servers([odoo])[0]["tools"]
        self.assertEqual([tool["name"] for tool in tools], ["search_read", "whoami"])

    def test_plan_parser_handles_model_reasoning_and_rejects_unknown_tool(self) -> None:
        plan = parse_mcp_plan(
            '<think>choose status</think>\n```json\n'
            f'{{"action":"tool","server_id":{self.server["id"]},"tool_name":"nas_get_system_status","arguments":{{}}}}\n```'
        )
        servers = available_mcp_servers([self.server])
        server, tool = resolve_planned_tool(plan, servers)
        self.assertEqual(server["slug"], "nas-demo")
        self.assertEqual(tool["name"], "nas_get_system_status")
        plan["tool_name"] = "nas_delete_everything"
        with self.assertRaises(McpPlanningError):
            resolve_planned_tool(plan, servers)

    def test_final_prompt_uses_structured_result_without_duplicate_content(self) -> None:
        tool_result = {
            "content": [{"type": "text", "text": "duplicate text that should not be included"}],
            "structuredContent": {"count": 1, "messages": [{"subject": "Status"}]},
            "isError": False,
        }

        prompt = build_final_prompt(
            "列出最近郵件",
            {"name": "Gmail Read-only"},
            {"name": "gmail_list_recent_messages"},
            tool_result,
        )

        self.assertIn('"subject":"Status"', prompt)
        self.assertNotIn("duplicate text that should not be included", prompt)

    def test_complete_llm_mcp_llm_chain_writes_tool_audit(self) -> None:
        planner = {
            "call_id": 101,
            "answer": json.dumps(
                {
                    "action": "tool",
                    "server_id": self.server["id"],
                    "tool_name": "nas_get_system_status",
                    "arguments": {},
                }
            ),
        }
        final = {
            "call_id": 102,
            "model": "Qwen3 4B",
            "answer": "NAS 目前連線正常。",
            "usage": {"total_tokens": 42},
        }
        tool_result = {
            "content": [{"type": "text", "text": "online"}],
            "structuredContent": {"status": "online"},
            "isError": False,
        }
        with (
            patch.object(main, "run_model_with_audit", new=AsyncMock(side_effect=[planner, final])) as run,
            patch.object(main, "call_streamable_http_tool", return_value=tool_result) as call,
        ):
            result = asyncio.run(
                main.run_model_with_mcp(
                    model_id="local:qwen3-4b",
                    prompt="請查詢 NAS 狀態",
                    api_key=None,
                    user=self.user,
                    selected_server_id=self.server["id"],
                )
            )

        self.assertEqual(run.await_count, 2)
        call.assert_called_once()
        self.assertEqual(result["answer"], "NAS 目前連線正常。")
        self.assertTrue(result["mcp"]["used"])
        self.assertEqual(result["mcp"]["tool"], "nas_get_system_status")
        self.assertTrue(result["cache"]["bypassed"])
        with db.connect() as conn:
            audit = conn.execute("SELECT * FROM mcp_audit_logs WHERE action = 'tools/call'").fetchone()
        self.assertIsNotNone(audit)
        self.assertEqual(audit["status"], "completed")
        self.assertEqual(audit["tool_name"], "nas_get_system_status")


if __name__ == "__main__":
    unittest.main()
