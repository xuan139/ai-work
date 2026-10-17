import unittest
from datetime import datetime

from app.manufacturing_extension_demo import (
    change_impact,
    current_bom,
    lot_location,
    material_availability,
    order_genealogy,
    order_quality_risk,
    process_capability,
    recall_impact,
    revision_difference,
    serial_history,
    warehouse_snapshot,
)
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

    def test_wms_snapshot_and_traceability_queries_are_bounded(self):
        snapshot = warehouse_snapshot(self.now)
        self.assertTrue(snapshot["read_only"])
        self.assertEqual(snapshot["dataset_type"], "synthetic_electronics_wms_traceability")
        availability = material_availability("C", 160, self.now)
        self.assertEqual(availability["shortage_units"], 120)
        self.assertEqual(lot_location("LOT-MCU-C-2610", self.now)["lot"]["location"], "WH-C-02")
        self.assertEqual(serial_history("SN-DEMO-C-0001", self.now)["genealogy"]["order"], "MES-DEMO-1003")
        self.assertEqual(len(order_genealogy("MES-DEMO-1003", self.now)["serials"]), 1)
        self.assertIn("MES-DEMO-1003", recall_impact("LOT-MCU-C-2610", self.now)["affected_orders"])
        for callback, value in ((lot_location, "../lot"), (serial_history, "SN/unsafe"), (recall_impact, "unknown")):
            with self.subTest(callback=callback.__name__), self.assertRaises(ValueError):
                callback(value, self.now)

    def test_plm_revision_and_change_impact_are_read_only(self):
        bom = current_bom("C", self.now)["bom"]
        self.assertEqual(bom["revision"], "C.12")
        self.assertEqual(bom["status"], "controlled_release")
        difference = revision_difference("ECO-2026-014", self.now)
        self.assertIn("SMT 換線 +10 分鐘", difference["changes"])
        impact = change_impact("ECO-2026-014", self.now)
        self.assertEqual(impact["schedule_impact"]["extra_operation_minutes"], 20)
        for callback, value in ((current_bom, "D"), (revision_difference, "../ECO"), (change_impact, "ECO-404")):
            with self.subTest(callback=callback.__name__), self.assertRaises(ValueError):
                callback(value, self.now)

    def test_spc_capability_and_order_risk_are_bounded(self):
        capability = process_capability("C", self.now)["profile"]
        self.assertEqual(capability["cpk"], 0.91)
        risk = order_quality_risk("SO-1003", "C", 160, self.now)
        self.assertEqual(risk["extra_inspection_minutes"], 56)
        self.assertEqual(risk["matching_points"][0]["point_id"], "SPC-OOC-027")
        for arguments in (("../SO", "C", 1), ("SO-1", "D", 1), ("SO-1", "A", 0)):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                order_quality_risk(*arguments, now=self.now)


if __name__ == "__main__":
    unittest.main()
