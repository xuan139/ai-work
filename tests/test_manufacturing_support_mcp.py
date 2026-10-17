import unittest
from datetime import datetime

from app.manufacturing_support_demo import (
    maintenance_asset_detail,
    maintenance_snapshot,
    quality_order_detail,
    quality_snapshot,
)


class ManufacturingSupportMcpTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 19, 8, 0)

    def test_quality_snapshot_is_fixed_read_only_teaching_data(self):
        result = quality_snapshot(self.now)
        self.assertTrue(result["read_only"])
        self.assertEqual(result["dataset_type"], "synthetic_electronics_quality")
        self.assertEqual({item["family"] for item in result["profiles"]}, {"A", "B", "C"})
        detail = quality_order_detail("SO-1003", "C", 160, self.now)
        self.assertEqual(detail["expected_rework_minutes"], 152)
        self.assertEqual(detail["matching_events"][0]["event_id"], "QMS-NCR-2026-017")

    def test_quality_detail_rejects_unsafe_or_unbounded_input(self):
        for arguments in (("../SO-1", "A", 1), ("SO-1", "D", 1), ("SO-1", "A", -1)):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                quality_order_detail(*arguments, now=self.now)

    def test_maintenance_snapshot_has_bounded_assets_and_windows(self):
        result = maintenance_snapshot(self.now)
        self.assertTrue(result["read_only"])
        self.assertEqual(result["dataset_type"], "synthetic_electronics_maintenance")
        self.assertEqual({item["center_id"] for item in result["assets"]}, {"SMT-01", "ASSY-01", "TEST-01"})
        detail = maintenance_asset_detail("SMT-01", self.now)
        self.assertEqual(detail["asset"]["open_work_order"], "MWO-2026-018")
        self.assertEqual(len(detail["maintenance_windows"]), 1)

    def test_maintenance_detail_rejects_unknown_or_unsafe_center(self):
        for center in ("../SMT-01", "UNKNOWN-01"):
            with self.subTest(center=center), self.assertRaises(ValueError):
                maintenance_asset_detail(center, self.now)


if __name__ == "__main__":
    unittest.main()
