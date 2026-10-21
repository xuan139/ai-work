import json
import unittest
from unittest.mock import patch

from app.excel_pro_agent import ExcelProAgentError, run_excel_pro_agent


class ExcelProAgentTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = {"id": 9, "username": "sales", "role": "user"}
        self.server = {"id": 3, "slug": "nas-excel-pro", "name": "NAS Excel Pro MCP"}
        self.tool_calls = []
        self.sources = [
            {"asset_id": 41, "title": "销售明细", "filename": "sales.xlsx", "uploader": "sales"},
            {"asset_id": 52, "title": "库存", "filename": "inventory.csv", "uploader": "warehouse"},
        ]

    def call_tool(self, server, name, arguments, delegated_user):
        self.assertEqual(delegated_user["id"], self.user["id"])
        self.tool_calls.append((name, arguments))
        if name == "excel_pro_list_sources":
            value = {"count": 2, "sources": self.sources}
        elif name == "excel_pro_describe_sources":
            value = {
                "source_count": len(arguments["sources"]), "table_count": 2,
                "tables": [
                    {"table_name": "asset_41__Sales", "filename": "sales.xlsx", "sheet_name": "Sales", "columns": ["Product", "Quantity"], "row_count": 2, "range": "Sales!A2:B3"},
                    {"table_name": "asset_52__data", "filename": "inventory.csv", "sheet_name": "data", "columns": ["Product", "Available"], "row_count": 2, "range": "data!A2:B3"},
                ],
            }
        elif name == "excel_pro_query":
            value = {
                "engine": "DuckDB 1.5.6", "columns": ["Product", "Quantity", "Available"],
                "rows": [["NAS B", 20, 12]], "row_count": 1, "truncated": False,
                "citations": [
                    {"filename": "sales.xlsx", "range": "Sales!A2:B3", "uploader": "sales"},
                    {"filename": "inventory.csv", "range": "data!A2:B3", "uploader": "warehouse"},
                ],
            }
        else:
            self.fail(f"Unexpected tool call: {name}")
        return {"structuredContent": value}

    def model_runner(self, answers):
        calls = []

        async def run_model(**kwargs):
            calls.append(kwargs)
            answer = answers[len(calls) - 1]
            return {
                "call_id": 100 + len(calls), "model_id": kwargs["model_id"],
                "model": "Qwen3 4B", "answer": answer,
            }

        return calls, run_model

    async def test_explicit_sources_run_read_only_chain_without_export(self):
        calls, runner = self.model_runner([
            json.dumps({"goal": "比较销售与库存", "search_terms": ["销售", "库存"]}),
            json.dumps({"sql": 'SELECT * FROM "asset_41__Sales" LIMIT 200', "explanation": "读取销售"}),
            "NAS B 库存可能不足。来源：sales.xlsx 与 inventory.csv。",
        ])
        with patch("app.excel_pro_agent.create_mcp_audit_log"):
            result = await run_excel_pro_agent(
                "比较销售和库存", [41, 52], model_id="qwen3-4b", user=self.user,
                server=self.server, run_model=runner, call_tool=self.call_tool,
            )
        self.assertEqual([item[0] for item in self.tool_calls], [
            "excel_pro_list_sources", "excel_pro_describe_sources", "excel_pro_query",
        ])
        self.assertNotIn("excel_pro_start_export", [item[0] for item in self.tool_calls])
        self.assertEqual(len(calls), 3)
        self.assertFalse(result["export_created"])
        self.assertEqual(result["result"]["row_count"], 1)
        self.assertEqual(len(result["trace"]), 6)
        self.assertEqual(result["citations"][0]["range"], "Sales!A2:B3")

    async def test_auto_selection_uses_planner_terms(self):
        calls, runner = self.model_runner([
            '```json\n{"goal":"检查库存","search_terms":["库存"]}\n```',
            json.dumps({"sql": 'SELECT * FROM "asset_52__data" LIMIT 200', "explanation": "读取库存"}),
            "目前有一项库存风险。",
        ])
        with patch("app.excel_pro_agent.create_mcp_audit_log"):
            result = await run_excel_pro_agent(
                "目前有哪些库存风险？", [], model_id="qwen3-4b", user=self.user,
                server=self.server, run_model=runner, call_tool=self.call_tool,
            )
        self.assertEqual([item["asset_id"] for item in result["selected_sources"]], [52])
        describe_call = next(item for item in self.tool_calls if item[0] == "excel_pro_describe_sources")
        self.assertEqual(describe_call[1]["sources"], [{"asset_id": 52}])

    async def test_rejects_selected_source_hidden_by_mcp_permissions(self):
        _, runner = self.model_runner([
            json.dumps({"goal": "读取资料", "search_terms": []}),
        ])
        with patch("app.excel_pro_agent.create_mcp_audit_log"):
            with self.assertRaisesRegex(ExcelProAgentError, "无权读取"):
                await run_excel_pro_agent(
                    "读取隐藏资料", [999], model_id="qwen3-4b", user=self.user,
                    server=self.server, run_model=runner, call_tool=self.call_tool,
                )

    async def test_schema_question_uses_deterministic_sample_query(self):
        self.sources = [
            {
                "asset_id": 72, "title": "excel-pro-analysis",
                "filename": "excel-pro-analysis.xlsx", "uploader": "admin",
                "source_type": "excel_pro_export",
            }
        ]

        def call_tool(server, name, arguments, delegated_user):
            self.tool_calls.append((name, arguments))
            if name == "excel_pro_list_sources":
                value = {"count": 1, "sources": self.sources}
            elif name == "excel_pro_describe_sources":
                value = {
                    "source_count": 1, "table_count": 2,
                    "tables": [
                        {
                            "table_name": "asset_72__Query_Result", "filename": "excel-pro-analysis.xlsx",
                            "sheet_name": "Query Result", "columns": ["選取", "權限代碼"],
                            "row_count": 100, "range": "Query Result!A2:B101",
                            "source_type": "excel_pro_export",
                        },
                        {
                            "table_name": "asset_72__Sources", "filename": "excel-pro-analysis.xlsx",
                            "sheet_name": "Sources", "columns": ["DuckDB SQL", "column_2"],
                            "row_count": 3, "range": "Sources!A2:B4",
                            "source_type": "excel_pro_export",
                        },
                    ],
                }
            elif name == "excel_pro_query":
                self.assertEqual(arguments["sql"], 'SELECT * FROM "asset_72__Query_Result" LIMIT 5')
                value = {
                    "engine": "DuckDB 1.5.6", "columns": ["選取", "權限代碼"],
                    "rows": [["A", "R1"]], "row_count": 1, "truncated": False,
                    "citations": [{"filename": "excel-pro-analysis.xlsx", "range": "Query Result!A2:B101"}],
                }
            else:
                self.fail(f"Unexpected tool call: {name}")
            return {"structuredContent": value}

        calls, runner = self.model_runner([
            json.dumps({"goal": "识别栏位", "search_terms": ["栏位"]}),
            "主要欄位為選取與權限代碼。",
        ])
        with patch("app.excel_pro_agent.create_mcp_audit_log"):
            result = await run_excel_pro_agent(
                "当前文件的主要栏位是什么", [72], model_id="qwen3-4b", user=self.user,
                server=self.server, run_model=runner, call_tool=call_tool,
            )
        self.assertEqual(len(calls), 2)
        self.assertNotIn("Sources", calls[-1]["prompt"])
        self.assertIn("source_row_count", calls[-1]["prompt"])
        self.assertEqual(result["generated_sql"], 'SELECT * FROM "asset_72__Query_Result" LIMIT 5')
        self.assertEqual(result["llm_call_ids"], [101, None, 102])

    async def test_zero_query_result_does_not_claim_source_is_empty(self):
        def call_tool(server, name, arguments, delegated_user):
            if name == "excel_pro_list_sources":
                value = {"count": 1, "sources": [self.sources[0]]}
            elif name == "excel_pro_describe_sources":
                value = {
                    "source_count": 1, "table_count": 1,
                    "tables": [{
                        "table_name": "asset_41__Sales", "filename": "sales.xlsx",
                        "sheet_name": "Sales", "columns": ["Product", "Quantity"],
                        "row_count": 100, "range": "Sales!A2:B101",
                    }],
                }
            elif name == "excel_pro_query":
                value = {
                    "engine": "DuckDB 1.5.6", "columns": ["Product"], "rows": [],
                    "row_count": 0, "truncated": False,
                    "citations": [{"filename": "sales.xlsx", "range": "Sales!A2:B101"}],
                }
            else:
                self.fail(f"Unexpected tool call: {name}")
            return {"structuredContent": value}

        _, runner = self.model_runner([
            json.dumps({"goal": "查询产品", "search_terms": ["销售"]}),
            json.dumps({"sql": 'SELECT * FROM "asset_41__Sales" WHERE "Product" = \'missing\'', "explanation": "筛选产品"}),
            "错误地声称来源工作表没有资料。",
        ])
        with patch("app.excel_pro_agent.create_mcp_audit_log"):
            result = await run_excel_pro_agent(
                "找出 missing 产品", [41], model_id="qwen3-4b", user=self.user,
                server=self.server, run_model=runner, call_tool=call_tool,
            )
        self.assertIn("查詢條件沒有匹配", result["answer"])
        self.assertIn("100 筆", result["answer"])
        self.assertNotIn("來源工作表沒有資料", result["answer"])


if __name__ == "__main__":
    unittest.main()
