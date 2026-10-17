import asyncio
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app import db
from app.manufacturing_mes_demo import electronics_schedule_snapshot
from app.manufacturing_schedule_mcp import ManufacturingMcpError, run_mcp_schedule
from app.mcp_runtime import McpConnectionError


def mcp_result(value):
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}]}


class ManufacturingScheduleMcpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.temp.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin("unused-test-hash")
        self.user = db.get_user_by_username("admin")
        servers = {row["slug"]: row for row in db.list_mcp_servers()}
        self.odoo = {**servers["odoo"], "name": "Goldsys Odoo", "slug": "odoo"}
        self.mes = {**servers["factory-mes"], "name": "FactorySemantics MES 唯讀", "slug": "factory-mes"}
        self.now = datetime(2026, 10, 19, 8, 0)
        self.calls = []

    def tearDown(self):
        self.db_patch.stop()
        self.temp.cleanup()

    def fake_call(self, _server, tool, arguments):
        self.calls.append((tool, arguments))
        if tool == "mes_electronics_schedule_snapshot":
            return mcp_result(electronics_schedule_snapshot(self.now))
        model = arguments.get("model")
        if model == "sale.order":
            return mcp_result([
                {"id": 10, "name": "S00010", "partner_id": [1, "Acme"], "date_order": "2026-10-15T09:00:00",
                 "commitment_date": "2026-10-21T16:00:00", "expected_date": None, "state": "sale",
                 "amount_total": 300000, "currency_id": [1, "TWD"], "order_line": [100]},
                {"id": 11, "name": "S00011", "partner_id": [2, "Beta"], "date_order": "2026-10-16T10:00:00",
                 "commitment_date": None, "expected_date": None, "state": "sale",
                 "amount_total": 80000, "currency_id": [1, "TWD"], "order_line": [101]},
            ])
        if model == "sale.order.line":
            return mcp_result([
                {"id": 100, "order_id": [10, "S00010"], "product_id": [200, "Control PCB"], "product_uom_qty": 4},
                {"id": 101, "order_id": [11, "S00011"], "product_id": [201, "Vision Station"], "product_uom_qty": 3},
            ])
        if model == "stock.quant":
            return mcp_result([
                {"id": 300, "product_id": [200, "Control PCB"], "quantity": 10, "available_quantity": 10},
                {"id": 301, "product_id": [201, "Vision Station"], "quantity": 1, "available_quantity": 1},
            ])
        raise AssertionError((tool, arguments))

    def test_reads_all_sources_via_mcp_and_schedules_locally(self):
        result = asyncio.run(run_mcp_schedule(
            {}, user=self.user, odoo_server=self.odoo, mes_server=self.mes,
            call_tool=self.fake_call, now=self.now,
        ))
        self.assertEqual(result["data_mode"], "live_mcp")
        self.assertEqual(result["summary"]["order_count"], 5)
        self.assertEqual({row["source_kind"] for row in result["orders"]}, {"odoo_mcp", "mes_mcp_demo"})
        self.assertEqual([center["id"] for center in result["work_centers"]], ["SMT-01", "ASSY-01", "TEST-01"])
        self.assertEqual(result["mes_snapshot"]["dataset_type"], "synthetic_electronics_schedule")
        self.assertIn("短缺 2", {item["status"] for item in result["inventory"]})
        self.assertEqual([step["tool"] for step in result["trace"][:4]], [
            "search_read", "search_read", "search_read", "mes_electronics_schedule_snapshot",
        ])
        self.assertEqual(result["trace"][-1]["kind"], "local")
        self.assertTrue(any("MES MCP 補入 3 筆" in warning for warning in result["integration_warnings"]))
        stock_call = next(arguments for tool, arguments in self.calls if arguments.get("model") == "stock.quant")
        self.assertEqual(json.loads(stock_call["domain"])[1], ["product_id", "in", [200, 201]])
        with db.connect() as connection:
            audit = connection.execute(
                "SELECT status, tool_name FROM mcp_audit_logs ORDER BY id"
            ).fetchall()
        self.assertEqual(len(audit), 4)
        self.assertTrue(all(row["status"] == "completed" for row in audit))
        self.assertNotIn("create_records", {row["tool_name"] for row in audit})

    def test_mcp_failure_is_audited_and_never_falls_back(self):
        def fail(*_args):
            raise McpConnectionError("offline")

        with self.assertRaisesRegex(ManufacturingMcpError, "查詢失敗"):
            asyncio.run(run_mcp_schedule(
                {}, user=self.user, odoo_server=self.odoo, mes_server=self.mes,
                call_tool=fail, now=self.now,
            ))
        with db.connect() as connection:
            row = connection.execute("SELECT status, error_message FROM mcp_audit_logs").fetchone()
        self.assertEqual(row["status"], "failed")
        self.assertIn("offline", row["error_message"])

    def test_invalid_scenario_is_rejected_before_mcp_calls(self):
        with self.assertRaises(ValueError):
            asyncio.run(run_mcp_schedule(
                {"smt_downtime_hours": 99}, user=self.user, odoo_server=self.odoo,
                mes_server=self.mes, call_tool=self.fake_call, now=self.now,
            ))
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
