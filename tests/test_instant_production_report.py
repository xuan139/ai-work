import copy
import json
import tempfile
import unittest
import unicodedata
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pymupdf
from fastapi.testclient import TestClient

from app import db, main
from app.auth import current_user
from app.instant_production_report import (
    ProductionReportError,
    build_instant_report,
    generate_and_store_instant_report,
    management_context,
    normalize_alert_rules,
)
from app.manufacturing_mes_demo import electronics_schedule_snapshot
from app.manufacturing_schedule_demo import run_schedule


def report_schedule() -> dict:
    schedule = copy.deepcopy(run_schedule({}))
    schedule["data_mode"] = "mcp"
    schedule["mes_snapshot"] = electronics_schedule_snapshot()
    schedule["qms_snapshot"] = {
        "open_events": [{"event_id": "QMS-01", "summary": "焊點異常待確認"}],
    }
    schedule["cmms_snapshot"] = {
        "assets": [{"center_id": "SMT-01", "health": "watch", "reason": "真空值偏低"}],
    }
    schedule["sources"] = [
        {"id": "odoo-orders-mcp", "name": "Odoo / search_read", "detail": "sale.order"},
        {"id": "odoo-stock-mcp", "name": "Odoo / search_read", "detail": "stock.quant"},
        {"id": "factory-mes-mcp", "name": "MES / snapshot", "detail": "daily production"},
        {"id": "qms-demo-mcp", "name": "QMS / snapshot", "detail": "quality"},
        {"id": "cmms-demo-mcp", "name": "CMMS / snapshot", "detail": "maintenance"},
        {"id": "wms-demo-mcp", "name": "WMS / snapshot", "detail": "lots"},
        {"id": "plm-demo-mcp", "name": "PLM / snapshot", "detail": "ECO"},
        {"id": "spc-demo-mcp", "name": "SPC / snapshot", "detail": "capability"},
        {"id": "scheduler", "name": "Local scheduler", "detail": "finite capacity"},
    ]
    schedule["trace"] = [
        {"kind": "mcp", "server": "MES", "tool": "mes_electronics_schedule_snapshot", "status": "completed", "result": "snapshot"},
    ]
    return schedule


class InstantProductionReportTests(unittest.TestCase):
    def test_alert_rules_and_pdf_include_sources(self):
        rules = normalize_alert_rules({"oee_min": 80, "late_orders_max": 0})
        report = build_instant_report(report_schedule(), generated_by="admin", alert_rules=rules)
        self.assertEqual(report["schema_version"], "instant-production-report-v1")
        self.assertIn("late_orders_max", {item["field"] for item in report["alerts"]})
        self.assertTrue(all(item["sources"] for item in report["alerts"]))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "instant.pdf"
            from app.daily_production_report import render_report_pdf
            render_report_pdf(report, output)
            document = pymupdf.open(output)
            text = unicodedata.normalize("NFKC", "\n".join(page.get_text() for page in document))
            document.close()
        self.assertIn("即時生產報告", text)
        self.assertIn("管理告警", text)
        self.assertIn("資料來源與工具軌跡", text)
        context = management_context(report)
        self.assertLess(len(context), 6000)
        self.assertEqual(json.loads(context)["plant"], report["plant"])

    def test_rejects_unknown_or_out_of_range_alert_rules(self):
        with self.assertRaises(ProductionReportError):
            normalize_alert_rules({"unknown": 1})
        with self.assertRaises(ProductionReportError):
            normalize_alert_rules({"oee_min": 101})

    def test_same_day_generations_are_independent_nas_assets(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(db, "DB_PATH", Path(directory) / "app.db"), \
             patch("app.instant_production_report.REPORTS_DIR", Path(directory) / "reports"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            admin = db.get_user_by_username("admin")
            first = generate_and_store_instant_report(report_schedule(), admin)
            second = generate_and_store_instant_report(report_schedule(), admin)
            self.assertNotEqual(first["id"], second["id"])
            self.assertEqual(len(db.list_instant_production_reports(user_id=admin["id"], role="admin")), 2)
            self.assertEqual(len(db.list_nas_assets(user_id=admin["id"], role="admin")), 4)

    def test_http_generate_push_and_management_follow_up(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(db, "DB_PATH", Path(directory) / "app.db"), \
             patch("app.instant_production_report.REPORTS_DIR", Path(directory) / "reports"), \
             patch.object(main, "REPORTS_DIR", Path(directory) / "reports"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            admin = db.get_user_by_username("admin")
            client = TestClient(main.app)
            try:
                self.assertEqual(client.get("/instant-production-report").status_code, 401)
                main.app.dependency_overrides[current_user] = lambda: admin
                self.assertEqual(client.get("/instant-production-report").status_code, 200)
                self.assertIn('/instant-production-report', client.get("/").text)
                with patch.object(main, "manufacturing_schedule_mcp_servers", return_value=({}, {}, {}, {}, {}, {}, {})), \
                     patch.object(main, "run_mcp_schedule", new=AsyncMock(return_value=report_schedule())):
                    created = client.post("/api/instant-production-reports", json={"alert_rules": {"oee_min": 80}})
                self.assertEqual(created.status_code, 200, created.text)
                report_id = created.json()["id"]
                self.assertGreater(len(created.json()["report"]["alerts"]), 0)
                self.assertEqual(client.get("/api/instant-production-reports").json()["reports"][0]["id"], report_id)
                download = client.get(f"/api/instant-production-reports/{report_id}/download")
                self.assertEqual(download.status_code, 200)
                self.assertEqual(download.headers["content-type"], "application/pdf")

                with patch.object(main, "get_line_source", return_value={"source_type": "group", "is_approved": 1, "display_name": "管理群組"}), \
                     patch.object(main, "push_line_messages", new=AsyncMock(return_value={"ok": True})) as push:
                    pushed = client.post(
                        f"/api/instant-production-reports/{report_id}/push",
                        json={"group_id": "G-MANAGER", "alert_only": True},
                    )
                self.assertEqual(pushed.status_code, 200, pushed.text)
                self.assertEqual(pushed.json()["status"], "completed")
                self.assertIn("準交率", push.await_args.args[1][0])

                gmail_account = {
                    "id": "operations", "label": "營運 Gmail", "email": "operations@example.com",
                    "oauth_env": "GMAIL_OPERATIONS_TOKEN", "allowed_recipients": ["manager@example.com"],
                    "allowed_domains": [], "configured": True,
                }
                with patch.object(main, "gmail_sender_account", return_value=gmail_account), \
                     patch.object(main, "send_gmail_report", return_value={"message_id": "gmail-message-1", "thread_id": "thread-1"}) as send:
                    emailed = client.post(
                        f"/api/instant-production-reports/{report_id}/email",
                        json={"account_id": "operations", "recipients": "manager@example.com", "alert_only": True},
                    )
                self.assertEqual(emailed.status_code, 200, emailed.text)
                self.assertEqual(emailed.json()["message_id"], "gmail-message-1")
                self.assertEqual(send.call_args.kwargs["attachment_path"].suffix, ".pdf")

                model_result = {"answer": "SO-1003 可能延期 [S1][S9]", "call_id": 901}
                with patch.object(main, "current_llm_model", return_value={"id": "local:qwen", "name": "Qwen"}), \
                     patch.object(main, "run_model_with_audit", new=AsyncMock(return_value=model_result)):
                    answer = client.post(
                        f"/api/instant-production-reports/{report_id}/ask",
                        json={"question": "哪些订单可能延期？"},
                    )
                self.assertEqual(answer.status_code, 200, answer.text)
                self.assertIn("[S1]", answer.json()["answer"])
                detail = client.get(f"/api/instant-production-reports/{report_id}").json()
                self.assertEqual(len(detail["questions"]), 1)
                self.assertEqual(detail["deliveries"][0]["external_id"], "gmail-message-1")
                self.assertEqual(detail["deliveries"][0]["recipients"], ["manager@example.com"])
                self.assertEqual(detail["push_status"], "completed")
            finally:
                main.app.dependency_overrides.clear()
                client.close()


if __name__ == "__main__":
    unittest.main()
