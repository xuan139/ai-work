import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db, main
from app.auth import hash_password
from app.gmail_mcp import handle_gmail_mcp_request
from app.mcp_runtime import (
    call_streamable_http_tool,
    mcp_auth_configured,
    sync_streamable_http_tools,
    validate_mcp_endpoint,
)
from app.nas_mcp import handle_nas_mcp_request


class McpRegistryTests(unittest.TestCase):
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

    def test_seeded_registry_contains_expected_templates(self) -> None:
        servers = db.list_mcp_servers()
        slugs = {server["slug"] for server in servers}
        self.assertGreaterEqual(len(slugs), 20)
        self.assertTrue({
            "gmail", "slack", "github", "notion", "atlassian", "monday", "linear", "nas-demo",
            "xero", "odoo", "quickbooks", "netsuite",
        }.issubset(slugs))
        gmail = next(server for server in servers if server["slug"] == "gmail")
        self.assertEqual(gmail["endpoint"], "http://127.0.0.1:8000/mcp/gmail")
        self.assertEqual(gmail["auth_type"], "bearer")
        self.assertEqual(gmail["auth_env_var"], "GMAIL_LOCAL_MCP_KEY")
        monday = next(server for server in servers if server["slug"] == "monday")
        self.assertEqual(monday["endpoint"], "https://mcp.monday.com/mcp")
        self.assertEqual(monday["auth_type"], "bearer")
        self.assertEqual(monday["headers_json"], '{"Api-Version":"2026-07"}')
        linear = next(server for server in servers if server["slug"] == "linear")
        self.assertEqual(linear["endpoint"], "https://mcp.linear.app/mcp/readonly")
        self.assertEqual(linear["auth_type"], "bearer")
        xero = next(server for server in servers if server["slug"] == "xero")
        self.assertEqual(xero["transport"], "stdio")
        self.assertEqual(xero["auth_env_var"], "XERO_CLIENT_BEARER_TOKEN")
        self.assertFalse(xero["is_enabled"])
        quickbooks = next(server for server in servers if server["slug"] == "quickbooks")
        self.assertEqual(quickbooks["auth_type"], "oauth2")
        self.assertIsNone(quickbooks["endpoint"])
        netsuite = next(server for server in servers if server["slug"] == "netsuite")
        self.assertEqual(netsuite["auth_type"], "oauth2")
        self.assertIsNone(netsuite["endpoint"])
        slack = next(server for server in servers if server["slug"] == "slack")
        self.assertIsNone(slack["endpoint"])
        nas_demo = next(server for server in servers if server["slug"] == "nas-demo")
        self.assertTrue(nas_demo["is_enabled"])
        self.assertEqual(nas_demo["status"], "unchecked")

    def test_sync_updates_tools_and_writes_audit(self) -> None:
        server = next(item for item in db.list_mcp_servers() if item["slug"] == "odoo")
        updated = db.update_mcp_server(
            server["id"],
            {
                "slug": server["slug"],
                "name": server["name"],
                "description": server["description"],
                "description_en": server["description_en"],
                "transport": "streamable_http",
                "endpoint": "http://127.0.0.1:9000/mcp",
                "auth_env_var": None,
                "is_enabled": True,
            },
        )
        self.assertIsNotNone(updated)
        sync_result = {
            "protocol_version": "2025-06-18",
            "server_info": {"name": "odoo"},
            "capabilities": {"tools": {}},
            "tools": [{"name": "search_partners", "title": "", "description": "Search", "inputSchema": {}}],
        }
        with patch.object(main, "sync_streamable_http_tools", return_value=sync_result):
            response = asyncio.run(main.admin_sync_mcp_server(server["id"], admin=self.admin))

        self.assertEqual(response["status"], "connected")
        self.assertEqual(response["tool_count"], 1)
        self.assertEqual(response["tools"][0]["name"], "search_partners")
        with db.connect() as conn:
            audit = conn.execute("SELECT * FROM mcp_audit_logs").fetchall()
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["status"], "completed")

    def test_public_endpoint_requires_allowlist(self) -> None:
        address = [(2, 1, 6, "", ("8.8.8.8", 443))]
        with patch.dict(os.environ, {"MCP_ALLOWED_HOSTS": ""}), patch("socket.getaddrinfo", return_value=address):
            with self.assertRaises(ValueError):
                validate_mcp_endpoint("https://mcp.example.com/tools")
        with patch.dict(os.environ, {"MCP_ALLOWED_HOSTS": "mcp.example.com"}):
            self.assertEqual(
                validate_mcp_endpoint("https://mcp.example.com/tools"),
                "https://mcp.example.com/tools",
            )

    def test_official_public_endpoint_is_trusted(self) -> None:
        with patch.dict(os.environ, {"MCP_ALLOWED_HOSTS": ""}):
            self.assertEqual(
                validate_mcp_endpoint("https://mcp.linear.app/mcp"),
                "https://mcp.linear.app/mcp",
            )
            self.assertEqual(
                validate_mcp_endpoint("https://mcp.monday.com/mcp"),
                "https://mcp.monday.com/mcp",
            )

    def test_old_official_linear_endpoint_migrates_to_read_only(self) -> None:
        with db.connect() as conn:
            conn.execute(
                "UPDATE mcp_servers SET endpoint = ?, auth_type = 'oauth2', status = 'connected', "
                "tools_json = '[]', tool_count = 3 WHERE slug = 'linear'",
                ("https://mcp.linear.app/mcp",),
            )
        db.seed_admin(hash_password("ignored"))
        linear = next(server for server in db.list_mcp_servers() if server["slug"] == "linear")
        self.assertEqual(linear["endpoint"], "https://mcp.linear.app/mcp/readonly")
        self.assertEqual(linear["auth_type"], "bearer")
        self.assertEqual(linear["status"], "unchecked")
        self.assertIsNone(linear["tools_json"])
        self.assertIn("唯讀", linear["description"])

    def test_legacy_odoo_template_migrates_to_accounting_connector(self) -> None:
        with db.connect() as conn:
            conn.execute(
                "UPDATE mcp_servers SET name = 'Odoo', description = ? WHERE slug = 'odoo'",
                ("連接 Odoo ERP 的財務、銷售、庫存與營運工具。",),
            )
        db.seed_admin(hash_password("ignored"))
        odoo = next(server for server in db.list_mcp_servers() if server["slug"] == "odoo")
        self.assertEqual(odoo["name"], "Odoo Accounting")
        self.assertIn("應收應付", odoo["description"])
        self.assertEqual(odoo["auth_env_var"], "ODOO_MCP_TOKEN")

    def test_official_gmail_preview_endpoint_migrates_to_local_read_only_mcp(self) -> None:
        with db.connect() as conn:
            conn.execute(
                "UPDATE mcp_servers SET endpoint = ?, auth_type = 'oauth2', "
                "auth_env_var = 'GMAIL_MCP_TOKEN', status = 'connected' WHERE slug = 'gmail'",
                ("https://gmailmcp.googleapis.com/mcp/v1",),
            )
        db.seed_admin(hash_password("ignored"))
        gmail = next(server for server in db.list_mcp_servers() if server["slug"] == "gmail")
        self.assertEqual(gmail["endpoint"], "http://127.0.0.1:8000/mcp/gmail")
        self.assertEqual(gmail["auth_type"], "bearer")
        self.assertEqual(gmail["auth_env_var"], "GMAIL_LOCAL_MCP_KEY")
        self.assertEqual(gmail["status"], "unchecked")

    def test_streamable_http_sync_collects_tools(self) -> None:
        responses = [
            ({"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18", "serverInfo": {"name": "demo"}}}, "session-1"),
            ({}, "session-1"),
            ({"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "lookup", "description": "Lookup data", "inputSchema": {"type": "object"}, "annotations": {"readOnlyHint": True}}]}}, "session-1"),
        ]
        server = {
            "transport": "streamable_http",
            "endpoint": "http://127.0.0.1:9000/mcp",
            "auth_env_var": None,
            "headers_json": '{"Api-Version":"2026-07"}',
        }
        with patch("app.mcp_runtime._json_rpc_request", side_effect=responses) as request:
            result = sync_streamable_http_tools(server)
        self.assertEqual(result["protocol_version"], "2025-06-18")
        self.assertEqual(result["tools"][0]["name"], "lookup")
        self.assertTrue(result["tools"][0]["annotations"]["readOnlyHint"])
        self.assertEqual(request.call_args_list[-1].kwargs["extra_headers"], {"Api-Version": "2026-07"})

    def test_streamable_http_tool_call_returns_actual_result(self) -> None:
        responses = [
            ({"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18"}}, "session-1"),
            ({}, "session-1"),
            (
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "result": {
                        "content": [{"type": "text", "text": "online"}],
                        "structuredContent": {"status": "online"},
                        "isError": False,
                    },
                },
                "session-1",
            ),
        ]
        server = {"transport": "streamable_http", "endpoint": "http://127.0.0.1:9000/mcp", "auth_env_var": None}
        with patch("app.mcp_runtime._json_rpc_request", side_effect=responses) as request:
            result = call_streamable_http_tool(server, "status", {"detail": True})
        self.assertEqual(result["structuredContent"]["status"], "online")
        self.assertEqual(request.call_args_list[-1].args[1]["method"], "tools/call")
        self.assertEqual(request.call_args_list[-1].args[1]["params"]["arguments"], {"detail": True})

    def test_oauth_refresh_credentials_supply_access_token(self) -> None:
        responses = [
            ({"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18"}}, "session-1"),
            ({}, "session-1"),
            ({"jsonrpc": "2.0", "id": 2, "result": {"tools": []}}, "session-1"),
        ]
        server = {
            "transport": "streamable_http",
            "endpoint": "https://gmailmcp.googleapis.com/mcp/v1",
            "auth_type": "oauth2",
            "auth_env_var": "GMAIL_MCP_TOKEN",
        }
        env = {
            "GMAIL_MCP_CLIENT_ID": "client-id",
            "GMAIL_MCP_CLIENT_SECRET": "client-secret",
            "GMAIL_MCP_REFRESH_TOKEN": "refresh-token",
        }
        with (
            patch.dict(os.environ, env, clear=False),
            patch("app.mcp_runtime._oauth_access_token", return_value="fresh-access-token") as refresh,
            patch("app.mcp_runtime._json_rpc_request", side_effect=responses) as request,
        ):
            self.assertTrue(mcp_auth_configured(server))
            sync_streamable_http_tools(server)
        refresh.assert_called_once_with("GMAIL_MCP_TOKEN")
        self.assertEqual(request.call_args_list[0].kwargs["token"], "fresh-access-token")

    def test_nas_demo_mcp_lists_and_calls_read_only_tools(self) -> None:
        initialized = handle_nas_mcp_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(initialized["result"]["serverInfo"]["name"], "AI Work NAS Demo MCP")
        listed = handle_nas_mcp_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(listed["result"]["tools"]), 4)
        called = handle_nas_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "nas_search_demo_files", "arguments": {"query": "pdf"}},
            }
        )
        self.assertFalse(called["result"]["isError"])
        self.assertEqual(called["result"]["structuredContent"]["count"], 1)

    def test_gmail_mcp_lists_read_only_tools_and_reads_message(self) -> None:
        listed = handle_gmail_mcp_request(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            "access-token",
        )
        self.assertEqual(len(listed["result"]["tools"]), 4)
        self.assertTrue(all(tool["annotations"]["readOnlyHint"] for tool in listed["result"]["tools"]))
        encoded = "VGVzdCBtZXNzYWdl"
        response = {
            "id": "message-1",
            "threadId": "thread-1",
            "snippet": "Test",
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "Subject", "value": "Status"},
                    {"name": "From", "value": "sender@example.com"},
                ],
                "body": {"data": encoded},
            },
        }
        with patch("app.gmail_mcp._gmail_request", return_value=response):
            called = handle_gmail_mcp_request(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": "gmail_get_message", "arguments": {"message_id": "message-1"}},
                },
                "access-token",
            )
        self.assertEqual(called["result"]["structuredContent"]["subject"], "Status")
        self.assertEqual(called["result"]["structuredContent"]["text"], "Test message")


if __name__ == "__main__":
    unittest.main()
