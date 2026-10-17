import copy
import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app import db, main
from app.auth import current_user
from app.manufacturing_schedule_demo import BASE_ORDERS, WORK_CENTERS, answer_question, normalize_scenario, run_schedule


class ManufacturingScheduleDemoTests(unittest.TestCase):
    def test_baseline_is_deterministic_and_complete(self):
        first = run_schedule({})
        second = run_schedule({})
        self.assertEqual(first, second)
        self.assertEqual(len(first["orders"]), 5)
        self.assertEqual(len(first["work_centers"]), 3)
        self.assertEqual(len(first["operations"]), 15)
        self.assertEqual(len(first["sources"]), 4)
        self.assertEqual(len(first["trace"]), 3)
        self.assertEqual(first["summary"]["order_count"], 5)
        self.assertTrue(first["read_only"])
        self.assertTrue(first["demo"])
        self.assertIn("不是已訓練模型", first["engine"]["note"])
        self.assertEqual(tuple(BASE_ORDERS), BASE_ORDERS)
        self.assertEqual(tuple(WORK_CENTERS), WORK_CENTERS)

    def test_scenarios_change_schedule_without_mutating_baseline(self):
        baseline = run_schedule({})
        rush = run_schedule({"rush_order": True})
        downtime = run_schedule({"smt_downtime_hours": 2})
        material = run_schedule({"material_delay_days": 2})
        self.assertEqual(rush["summary"]["order_count"], 6)
        self.assertIn("SO-1006", {order["order"] for order in rush["orders"]})
        self.assertEqual(len(downtime["downtimes"]), 2)
        base_orders = {order["order"]: order for order in baseline["orders"]}
        down_orders = {order["order"]: order for order in downtime["orders"]}
        self.assertNotEqual(base_orders["SO-1001"]["predicted_completion_at"], down_orders["SO-1001"]["predicted_completion_at"])
        material_orders = {order["order"]: order for order in material["orders"]}
        self.assertGreater(material_orders["SO-1003"]["predicted_completion_at"], base_orders["SO-1003"]["predicted_completion_at"])
        self.assertEqual(material_orders["SO-1005"]["predicted_completion_at"], base_orders["SO-1005"]["predicted_completion_at"])
        self.assertEqual(run_schedule({}), baseline)

    def test_scenario_validation_is_bounded(self):
        for invalid in ({"rush_order": "yes"}, {"smt_downtime_hours": True}, {"smt_downtime_hours": 5},
                        {"material_delay_days": -1}, {"material_delay_days": 4}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                normalize_scenario(invalid)

    def test_page_and_api_require_login(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(db, "DB_PATH", Path(directory) / "app.db"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            admin = db.get_user_by_username("admin")
            client = TestClient(main.app)
            try:
                self.assertEqual(client.get("/manufacturing-schedule-demo").status_code, 401)
                self.assertEqual(client.post("/api/manufacturing-schedule-demo/schedule", json={"scenario": {}}).status_code, 401)
                main.app.dependency_overrides[current_user] = lambda: admin
                self.assertEqual(client.get("/manufacturing-schedule-demo").status_code, 200)
                self.assertIn('/manufacturing-schedule-demo', client.get("/").text)
                async def fake_schedule(scenario, **_kwargs):
                    return run_schedule(scenario)
                with patch.object(main, "manufacturing_schedule_mcp_servers", return_value=({}, {}, {}, {})), \
                     patch.object(main, "run_mcp_schedule", side_effect=fake_schedule):
                    result = client.post("/api/manufacturing-schedule-demo/schedule", json={"scenario": {}})
                    self.assertEqual(result.status_code, 200)
                    self.assertEqual(result.json()["summary"]["order_count"], 5)
                    self.assertEqual(client.post("/api/manufacturing-schedule-demo/schedule", json={"scenario": []}).status_code, 400)
                    self.assertEqual(client.post("/api/manufacturing-schedule-demo/schedule", json={"scenario": {"smt_downtime_hours": 9}}).status_code, 400)
            finally:
                main.app.dependency_overrides.clear()
                client.close()

    def test_question_evidence_is_bounded_and_read_only(self):
        captured = {}

        async def fake_model(**kwargs):
            captured.update(kwargs)
            return {"answer": "來源：Odoo Demo 快照。", "model": "demo", "call_id": 88}

        result = asyncio.run(answer_question(
            prompt="哪些訂單延期？", scenario={"smt_downtime_hours": 2}, model_id="demo",
            user={"id": 7}, run_model=fake_model,
        ))
        self.assertTrue(result["read_only"])
        self.assertEqual(result["steps"][-1]["tool"], "llm.explain_schedule")
        self.assertIn("SO-1003", captured["prompt"])
        self.assertIn("not a trained", captured["system_prompt"])
        self.assertLess(len(captured["prompt"]), 7000)

    def test_question_uses_current_model_path_and_returns_trace(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(db, "DB_PATH", Path(directory) / "app.db"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            admin = db.get_user_by_username("admin")
            client = TestClient(main.app)
            response_payload = {"answer": "SO-1003 因缺料延誤。", "model": "demo-model", "call_id": 9,
                                "schedule": run_schedule({}), "sources": run_schedule({})["sources"],
                                "steps": run_schedule({})["trace"] + [{"tool": "llm.explain_schedule"}], "read_only": True}
            try:
                main.app.dependency_overrides[current_user] = lambda: admin
                with patch.object(main, "manufacturing_schedule_mcp_servers", return_value=({}, {}, {}, {})), \
                     patch.object(main, "run_mcp_schedule", new=AsyncMock(return_value=run_schedule({}))), \
                     patch.object(main, "answer_manufacturing_question", new=AsyncMock(return_value=copy.deepcopy(response_payload))) as answer:
                    result = client.post("/api/manufacturing-schedule-demo/ask", json={"prompt": "SO-1003 為何延期？", "scenario": {}})
                    self.assertEqual(result.status_code, 200)
                    self.assertEqual(result.json()["model"], "demo-model")
                    answer.assert_awaited_once()
                    self.assertIn("schedule", answer.await_args.kwargs)
                self.assertEqual(client.post("/api/manufacturing-schedule-demo/ask", json={"prompt": "", "scenario": {}}).status_code, 400)
            finally:
                main.app.dependency_overrides.clear()
                client.close()


if __name__ == "__main__":
    unittest.main()
