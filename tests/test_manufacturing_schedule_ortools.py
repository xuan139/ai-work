import unittest
from collections import defaultdict
from datetime import datetime

from app.manufacturing_schedule_demo import run_schedule
from app.manufacturing_schedule_ortools import compare_schedules, ortools_available, run_ortools_schedule


class ManufacturingScheduleOrToolsTests(unittest.TestCase):
    def test_missing_optional_dependency_uses_rule_engine(self):
        if ortools_available():
            self.skipTest("OR-Tools is installed in this interpreter")
        result = compare_schedules(run_schedule({}), "ortools-cp-sat-v1")
        comparison = result["engine_comparison"]
        self.assertEqual(comparison["active_engine"], "finite-capacity-mcp-v4")
        self.assertTrue(comparison["fallback_used"])
        self.assertIn("尚未安裝", comparison["ortools_error"])

    @unittest.skipUnless(ortools_available(), "OR-Tools optional dependency is not installed")
    def test_cp_sat_schedule_is_feasible_and_comparable(self):
        rule = run_schedule({"rush_order": True, "smt_downtime_hours": 2})
        optimized = run_ortools_schedule(rule)
        self.assertIn(optimized["engine"]["solver_status"], {"OPTIMAL", "FEASIBLE"})
        self.assertEqual(len(optimized["orders"]), 6)
        self.assertEqual(len(optimized["operations"]), 18)
        self.assertTrue(optimized["read_only"])

        by_center = defaultdict(list)
        for operation in optimized["operations"]:
            by_center[operation["center_id"]].append(operation)
            start = datetime.fromisoformat(operation["start_at"])
            end = datetime.fromisoformat(operation["end_at"])
            self.assertLess(start, end)
            self.assertGreaterEqual(start.hour, 8)
            self.assertLessEqual(end.hour, 17)
        for operations in by_center.values():
            ordered = sorted(operations, key=lambda item: item["start_at"])
            for left, right in zip(ordered, ordered[1:]):
                self.assertLessEqual(left["end_at"], right["start_at"])

        by_order = defaultdict(list)
        for operation in optimized["operations"]:
            by_order[operation["order"]].append(operation)
        for operations in by_order.values():
            ordered = sorted(operations, key=lambda item: item["sequence"])
            for left, right in zip(ordered, ordered[1:]):
                self.assertLessEqual(left["end_at"], right["start_at"])

        comparison = compare_schedules(rule, "finite-capacity-mcp-v4")["engine_comparison"]
        self.assertTrue(comparison["ortools_available"])
        self.assertIn("weighted_late_minutes", comparison["metrics"]["ortools"])
        self.assertEqual(
            comparison["delta"]["weighted_late_minutes_reduced"],
            comparison["metrics"]["rule"]["weighted_late_minutes"]
            - comparison["metrics"]["ortools"]["weighted_late_minutes"],
        )


if __name__ == "__main__":
    unittest.main()
