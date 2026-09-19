import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

from app import db, excel_mcp
from app.auth import hash_password
from app.excel_mcp import EXCEL_MCP_TOOLS, handle_excel_mcp_request


class ExcelMcpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.assets_dir = self.root / "nas_assets"
        self.assets_dir.mkdir()
        self.db_patch = patch.object(db, "DB_PATH", self.root / "app.db")
        self.storage_patch = patch.object(excel_mcp, "NAS_ASSETS_DIR", self.assets_dir)
        self.db_patch.start()
        self.storage_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        admin = db.get_user_by_username("admin")
        assert admin is not None

        self.path = self.assets_dir / "sales.xlsx"
        workbook = Workbook()
        sales = workbook.active
        sales.title = "Sales Data"
        sales.append(["Region", "Product", "Amount"])
        sales.append(["Taipei", "NAS A", 100])
        sales.append(["Taipei", "NAS B", 250])
        sales.append(["Kaohsiung", "NAS A", 150])
        targets = workbook.create_sheet("Targets")
        targets.append(["Region", "Target"])
        targets.append(["Taipei", 500])
        targets.append(["Kaohsiung", 200])
        workbook.save(self.path)
        workbook.close()
        self.asset = db.create_nas_asset(
            user_id=admin["id"],
            category="excel",
            title="Sales workbook",
            original_filename="sales.xlsx",
            stored_path=str(self.path),
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            file_size=self.path.stat().st_size,
            status="completed",
        )

        self.csv_path = self.assets_dir / "big5-sales.csv"
        self.csv_path.write_bytes("地區,金額\n台北,100\n高雄,200\n".encode("cp950"))
        self.csv_asset = db.create_nas_asset(
            user_id=admin["id"],
            category="excel",
            title="Big5 sales CSV",
            original_filename="big5-sales.csv",
            stored_path=str(self.csv_path),
            mime_type="text/csv",
            file_size=self.csv_path.stat().st_size,
            status="completed",
        )

        self.tsv_path = self.assets_dir / "inventory.tsv"
        self.tsv_path.write_text("Item\tQuantity\nNAS A\t5\nNAS B\t8\n", encoding="utf-8")
        self.tsv_asset = db.create_nas_asset(
            user_id=admin["id"],
            category="excel",
            title="Inventory TSV",
            original_filename="inventory.tsv",
            stored_path=str(self.tsv_path),
            mime_type="text/tab-separated-values",
            file_size=self.tsv_path.stat().st_size,
            status="completed",
        )

    def tearDown(self) -> None:
        self.storage_patch.stop()
        self.db_patch.stop()
        self.directory.cleanup()

    def call(self, name: str, arguments: dict) -> dict:
        response = handle_excel_mcp_request(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        )
        assert response is not None
        self.assertNotIn("error", response)
        return response["result"]["structuredContent"]

    def test_lists_six_read_only_tools(self) -> None:
        self.assertEqual(len(EXCEL_MCP_TOOLS), 6)
        self.assertTrue(all(tool["annotations"]["readOnlyHint"] for tool in EXCEL_MCP_TOOLS))
        listed = self.call("excel_list_workbooks", {})
        self.assertEqual(
            {item["asset_id"] for item in listed["workbooks"]},
            {self.asset["id"], self.csv_asset["id"], self.tsv_asset["id"]},
        )

    def test_reads_range_and_searches_cells(self) -> None:
        content = self.call(
            "excel_read_range",
            {"asset_id": self.asset["id"], "sheet_name": "Sales Data", "cell_range": "A1:C3"},
        )
        self.assertEqual(content["range"], "A1:C3")
        self.assertEqual(content["rows"][1], ["Taipei", "NAS A", 100])

        search = self.call("excel_search_cells", {"asset_id": self.asset["id"], "query": "Kaohsiung"})
        self.assertEqual(search["matches"][0]["cell"], "A4")

    def test_profiles_columns(self) -> None:
        profile = self.call(
            "excel_profile_sheet",
            {"asset_id": self.asset["id"], "sheet_name": "Sales Data"},
        )
        amount = next(column for column in profile["columns"] if column["column"] == "Amount")
        self.assertEqual(amount["numeric_min"], 100.0)
        self.assertEqual(amount["numeric_max"], 250.0)
        self.assertEqual(amount["numeric_average"], 166.666667)

    def test_queries_and_joins_worksheets_with_read_only_sql(self) -> None:
        result = self.call(
            "excel_query_sql",
            {
                "asset_id": self.asset["id"],
                "sql": (
                    'SELECT s.Region, SUM(s.Amount) AS total, t.Target '
                    'FROM "Sales_Data" s JOIN "Targets" t ON t.Region = s.Region '
                    'GROUP BY s.Region, t.Target ORDER BY total DESC'
                ),
            },
        )
        self.assertEqual(result["columns"], ["Region", "total", "Target"])
        self.assertEqual(result["rows"][0], ["Taipei", 350, 500])
        self.assertFalse(result["result_truncated"])

    def test_rejects_sql_that_can_modify_data(self) -> None:
        response = handle_excel_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "excel_query_sql",
                    "arguments": {"asset_id": self.asset["id"], "sql": 'DELETE FROM "Sales_Data"'},
                },
            }
        )
        assert response is not None
        self.assertIn("Only one read-only SELECT", response["error"]["message"])

    def test_tool_result_is_json_serializable(self) -> None:
        result = self.call("excel_get_workbook_info", {"asset_id": self.asset["id"]})
        json.dumps(result)

    def test_reads_big5_csv_and_queries_numeric_values(self) -> None:
        info = self.call("excel_get_workbook_info", {"asset_id": self.csv_asset["id"]})
        self.assertEqual(info["sheets"][0]["name"], "data")
        self.assertEqual(info["sheets"][0]["encoding"], "cp950")
        self.assertEqual(info["sheets"][0]["sql_table_name"], "big5_sales")
        self.assertEqual(info["sheets"][0]["sql_columns"], ["地區", "金額"])

        result = self.call(
            "excel_query_sql",
            {
                "asset_id": self.csv_asset["id"],
                "sql": 'SELECT 地區, 金額 * 2 AS doubled FROM "big5_sales" ORDER BY 金額 DESC',
            },
        )
        self.assertEqual(result["rows"], [["高雄", 400], ["台北", 200]])

        profile = self.call(
            "excel_profile_sheet",
            {"asset_id": self.csv_asset["id"], "sheet_name": "data"},
        )
        amount = next(column for column in profile["columns"] if column["column"] == "金額")
        self.assertEqual(amount["numeric_average"], 150.0)

    def test_reads_utf8_tsv_range_and_searches(self) -> None:
        content = self.call(
            "excel_read_range",
            {"asset_id": self.tsv_asset["id"], "sheet_name": "data", "cell_range": "A1:B3"},
        )
        self.assertEqual(content["delimiter_name"], "tab")
        self.assertEqual(content["rows"][2], ["NAS B", 8])

        search = self.call(
            "excel_search_cells",
            {"asset_id": self.tsv_asset["id"], "query": "NAS B"},
        )
        self.assertEqual(search["matches"][0]["cell"], "A3")


if __name__ == "__main__":
    unittest.main()
