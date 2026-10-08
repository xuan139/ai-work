import unittest
from unittest.mock import patch

from app.mes_readonly import MesReader


class MesReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reader = MesReader("http://127.0.0.1:8010", "analyst-secret")
        self.health = {"plant": "bottling", "timezone": "America/Chicago"}

    def test_overdue_orders_excludes_completed_orders(self) -> None:
        page = {"items": [
            {"code": "WO-1", "status": "running"},
            {"code": "WO-2", "status": "completed"},
        ], "total": 2, "has_more": False}
        with patch.object(self.reader, "_get", side_effect=[self.health, page]) as get:
            result = self.reader.overdue_orders()
        self.assertEqual(result["overdue_count"], 1)
        self.assertEqual(result["orders"][0]["code"], "WO-1")
        self.assertEqual(get.call_args_list[1].args[1], "/workorders")

    def test_work_order_query_returns_matching_quality_records(self) -> None:
        checks = {"items": [{"order": "WO-1", "result": "pass"}], "total": 1}
        with patch.object(self.reader, "_get", side_effect=[
            self.health, {"code": "WO-1"}, {"lots": []}, checks,
        ]) as get:
            result = self.reader.work_order_production_quality("WO-1")
        self.assertEqual(result["quality_checks"], checks)
        self.assertEqual(get.call_args_list[3].args[2]["order"], "WO-1")

    def test_work_order_query_rejects_path_injection(self) -> None:
        with self.assertRaises(ValueError):
            self.reader.work_order_production_quality("../admin")

    def test_downtime_uses_plant_time_zone_and_recorded_states(self) -> None:
        with patch.object(self.reader, "_get", side_effect=[
            self.health, {"reasons": [{"reason": "jam"}]},
            [{"equipment": "FILL", "state": "down"}],
        ]) as get:
            result = self.reader.line_downtime_today()
        self.assertEqual(result["plant_timezone"], "America/Chicago")
        self.assertEqual(result["current_equipment_states"][0]["state"], "down")
        self.assertGreater(get.call_args_list[1].args[2]["hours"], 0)


if __name__ == "__main__":
    unittest.main()
