import copy
import tempfile
import unittest
import unicodedata
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pymupdf
from fastapi.testclient import TestClient

from app import db, main
from app.auth import current_user
from app.daily_production_report import (
    build_daily_report,
    calculate_fixed_kpis,
    generate_and_store_report,
    render_report_pdf,
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


class DailyProductionReportTests(unittest.TestCase):
    def test_fixed_kpis_use_raw_counts_and_schedule(self):
        kpis = calculate_fixed_kpis(report_schedule())
        self.assertEqual(kpis["plan_attainment"]["value"], 82.0)
        self.assertEqual(kpis["first_pass_yield"]["value"], 94.6)
        self.assertEqual(kpis["predicted_on_time"]["value"], 80.0)
        self.assertEqual(kpis["late_orders"]["value"], 1)
        self.assertEqual(kpis["shortage_items"]["value"], 1)
        self.assertGreater(kpis["oee"]["value"], 0)
        self.assertEqual(build_daily_report(report_schedule(), generated_by="admin")["schema_version"], "daily-production-report-v1")

    def test_missing_mes_actuals_are_not_invented(self):
        schedule = report_schedule()
        schedule["mes_snapshot"].pop("daily_production")
        kpis = calculate_fixed_kpis(schedule)
        self.assertIsNone(kpis["plan_attainment"]["value"])
        self.assertEqual(kpis["plan_attainment"]["display"], "N/A")
        self.assertIsNone(kpis["oee"]["value"])

    def test_pdf_contains_chinese_and_source_references(self):
        report = build_daily_report(report_schedule(), generated_by="admin")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.pdf"
            render_report_pdf(report, output)
            self.assertTrue(output.is_file())
            document = pymupdf.open(output)
            text = unicodedata.normalize("NFKC", "\n".join(page.get_text() for page in document))
            document.close()
        self.assertIn("每日生產報告", text)
        self.assertIn("資料來源與工具軌跡", text)
        self.assertIn("S1", text)

    def test_generate_stores_snapshot_and_pdf_as_nas_assets(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(db, "DB_PATH", Path(directory) / "app.db"), \
             patch("app.daily_production_report.REPORTS_DIR", Path(directory) / "reports"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            admin = db.get_user_by_username("admin")
            employee = db.create_user(username="operator", password_hash="test", role="user")
            result = generate_and_store_report(report_schedule(), admin)
            self.assertEqual(result["status"], "completed")
            self.assertTrue(Path(result["snapshot_path"]).is_file())
            self.assertTrue(Path(result["pdf_path"]).is_file())
            self.assertEqual(result["source_count"], 9)
            self.assertEqual(len(db.list_nas_assets(user_id=admin["id"], role="admin")), 2)
            self.assertIsNone(db.get_production_report(result["id"], user_id=employee["id"], role="user"))
            self.assertEqual(db.list_production_reports(user_id=employee["id"], role="user"), [])

            repeated = generate_and_store_report(report_schedule(), admin)
            self.assertEqual(repeated["id"], result["id"])
            self.assertEqual(len(db.list_nas_assets(user_id=admin["id"], role="admin")), 2)
            self.assertEqual(len(db.list_production_reports(user_id=admin["id"], role="admin")), 1)

    def test_page_generate_history_and_download_require_login(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(db, "DB_PATH", Path(directory) / "app.db"), \
             patch("app.daily_production_report.REPORTS_DIR", Path(directory) / "reports"), \
             patch.object(main, "REPORTS_DIR", Path(directory) / "reports"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            admin = db.get_user_by_username("admin")
            client = TestClient(main.app)
            try:
                self.assertEqual(client.get("/daily-production-report").status_code, 401)
                self.assertEqual(client.post("/api/daily-production-reports").status_code, 401)
                main.app.dependency_overrides[current_user] = lambda: admin
                self.assertEqual(client.get("/daily-production-report").status_code, 200)
                self.assertIn('/daily-production-report', client.get("/").text)
                with patch.object(main, "manufacturing_schedule_mcp_servers", return_value=({}, {}, {}, {}, {}, {}, {})), \
                     patch.object(main, "run_mcp_schedule", new=AsyncMock(return_value=report_schedule())):
                    created = client.post("/api/daily-production-reports")
                self.assertEqual(created.status_code, 200)
                report_id = created.json()["id"]
                self.assertEqual(client.get("/api/daily-production-reports").json()["reports"][0]["id"], report_id)
                detail = client.get(f"/api/daily-production-reports/{report_id}")
                self.assertEqual(detail.status_code, 200)
                self.assertIn("kpis", detail.json()["report"])
                download = client.get(f"/api/daily-production-reports/{report_id}/download")
                self.assertEqual(download.status_code, 200)
                self.assertEqual(download.headers["content-type"], "application/pdf")
            finally:
                main.app.dependency_overrides.clear()
                client.close()


if __name__ == "__main__":
    unittest.main()
