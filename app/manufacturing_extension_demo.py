"""Synthetic read-only WMS, PLM, and SPC data for the manufacturing demo."""

from __future__ import annotations

import math
import re
from datetime import datetime, time, timedelta


IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
FAMILIES = {"A", "B", "C"}


def _safe_identifier(value: str, field: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"{field} must be a safe identifier")
    return value.upper()


def _family(value: str) -> str:
    family = _safe_identifier(value, "family")
    if family not in FAMILIES:
        raise ValueError("family must be A, B or C")
    return family


def _quantity(value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 < float(value) <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    return float(value)


def _next_work_start(value: datetime, workdays: int) -> datetime:
    current = datetime.combine(value.date(), time(8, 0))
    added = 0
    while added < workdays:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    while current.weekday() >= 5:
        current += timedelta(days=1)
    return current


def warehouse_snapshot(now: datetime | None = None) -> dict:
    snapshot_at = (now or datetime.now()).replace(second=0, microsecond=0)
    c_ready = _next_work_start(snapshot_at, 2)
    return {
        "source": "AI Work WMS Traceability Demo MCP",
        "dataset_type": "synthetic_electronics_wms_traceability",
        "read_only": True,
        "snapshot_at": snapshot_at.isoformat(timespec="minutes"),
        "notice": "教學模擬倉儲與追溯資料；不得視為真實庫存、批次或召回依據。",
        "material_profiles": [
            {
                "family": "A", "item": "PCB-A", "available_units": 520,
                "location": "WH-A-01", "lot_ids": ["LOT-PCB-A-2609"],
                "ready_at": snapshot_at.isoformat(timespec="minutes"), "status": "available",
            },
            {
                "family": "B", "item": "MCU-B", "available_units": 210,
                "location": "WH-B-03", "lot_ids": ["LOT-MCU-B-2610"],
                "ready_at": snapshot_at.isoformat(timespec="minutes"), "status": "available",
            },
            {
                "family": "C", "item": "MCU-C", "available_units": 40,
                "inbound_units": 200, "location": "WH-C-02",
                "lot_ids": ["LOT-MCU-C-2610"],
                "ready_at": c_ready.isoformat(timespec="minutes"), "status": "inbound",
            },
        ],
        "lots": [
            {"lot_id": "LOT-PCB-A-2609", "item": "PCB-A", "location": "WH-A-01", "quantity": 520, "quality_status": "released"},
            {"lot_id": "LOT-MCU-B-2610", "item": "MCU-B", "location": "WH-B-03", "quantity": 210, "quality_status": "released"},
            {"lot_id": "LOT-MCU-C-2610", "item": "MCU-C", "location": "WH-C-02", "quantity": 40, "quality_status": "hold"},
        ],
        "serial_genealogy": [
            {
                "serial": "SN-DEMO-C-0001", "order": "MES-DEMO-1003", "family": "C",
                "status": "in_process", "work_order": "WO-DEMO-C-1003",
                "consumed_lots": ["LOT-MCU-C-2610", "LOT-PCB-A-2609"],
                "current_location": "WIP-TEST-01",
            },
            {
                "serial": "SN-DEMO-B-0001", "order": "MES-DEMO-1002", "family": "B",
                "status": "finished", "work_order": "WO-DEMO-B-1002",
                "consumed_lots": ["LOT-MCU-B-2610", "LOT-PCB-A-2609"],
                "current_location": "WH-FG-01",
            },
        ],
    }


def material_availability(family: str, quantity: float, now: datetime | None = None) -> dict:
    family = _family(family)
    quantity = _quantity(quantity)
    snapshot = warehouse_snapshot(now)
    profile = next(item for item in snapshot["material_profiles"] if item["family"] == family)
    shortage = max(0, quantity - float(profile["available_units"]))
    return {
        "source": snapshot["source"], "read_only": True, "family": family,
        "requested_units": quantity, "available_units": profile["available_units"],
        "shortage_units": shortage, "ready_at": profile["ready_at"],
        "location": profile["location"], "lot_ids": profile["lot_ids"],
        "status": "shortage" if shortage else "available", "notice": snapshot["notice"],
    }


def lot_location(lot_id: str, now: datetime | None = None) -> dict:
    lot_id = _safe_identifier(lot_id, "lot_id")
    snapshot = warehouse_snapshot(now)
    lot = next((item for item in snapshot["lots"] if item["lot_id"] == lot_id), None)
    if lot is None:
        raise ValueError("unknown lot")
    return {"source": snapshot["source"], "read_only": True, "lot": lot, "notice": snapshot["notice"]}


def serial_history(serial: str, now: datetime | None = None) -> dict:
    serial = _safe_identifier(serial, "serial")
    snapshot = warehouse_snapshot(now)
    record = next((item for item in snapshot["serial_genealogy"] if item["serial"] == serial), None)
    if record is None:
        raise ValueError("unknown serial")
    return {"source": snapshot["source"], "read_only": True, "genealogy": record, "notice": snapshot["notice"]}


def order_genealogy(order: str, now: datetime | None = None) -> dict:
    order = _safe_identifier(order, "order")
    snapshot = warehouse_snapshot(now)
    records = [item for item in snapshot["serial_genealogy"] if item["order"] == order]
    return {"source": snapshot["source"], "read_only": True, "order": order, "serials": records, "notice": snapshot["notice"]}


def recall_impact(lot_id: str, now: datetime | None = None) -> dict:
    lot_id = _safe_identifier(lot_id, "lot_id")
    snapshot = warehouse_snapshot(now)
    if not any(item["lot_id"] == lot_id for item in snapshot["lots"]):
        raise ValueError("unknown lot")
    records = [item for item in snapshot["serial_genealogy"] if lot_id in item["consumed_lots"]]
    return {
        "source": snapshot["source"], "read_only": True, "lot_id": lot_id,
        "affected_serials": [item["serial"] for item in records],
        "affected_orders": sorted({item["order"] for item in records}),
        "notice": snapshot["notice"],
    }


def engineering_snapshot(now: datetime | None = None) -> dict:
    snapshot_at = (now or datetime.now()).replace(second=0, microsecond=0)
    revisions = [
        {"family": "A", "product": "Control PCB", "bom": "BOM-A-004", "revision": "A.04", "status": "released", "extra_setup_minutes": 0, "extra_operation_minutes": 0},
        {"family": "B", "product": "IoT Gateway", "bom": "BOM-B-007", "revision": "B.07", "status": "released", "extra_setup_minutes": 5, "extra_operation_minutes": 0},
        {"family": "C", "product": "Sensor Hub", "bom": "BOM-C-012", "revision": "C.12", "status": "controlled_release", "extra_setup_minutes": 10, "extra_operation_minutes": 20},
    ]
    ecos = [
        {
            "eco_id": "ECO-2026-014", "family": "C", "status": "verification",
            "effective": "pending_approval", "risk": "high",
            "summary": "BGA 焊墊設計與 AOI 檢查參數調整。",
            "changes": ["BOM-C-011 → BOM-C-012", "SMT 換線 +10 分鐘", "首件檢查 +20 分鐘"],
            "affected_orders": ["MES-DEMO-1003"],
        },
        {
            "eco_id": "ECO-2026-009", "family": "B", "status": "effective",
            "effective": "2026-10-01", "risk": "low",
            "summary": "連接器替代料與組裝治具版本更新。",
            "changes": ["BOM-B-006 → BOM-B-007", "SMT 換線 +5 分鐘"],
            "affected_orders": [],
        },
    ]
    return {
        "source": "AI Work PLM ECO Demo MCP",
        "dataset_type": "synthetic_electronics_plm",
        "read_only": True,
        "snapshot_at": snapshot_at.isoformat(timespec="minutes"),
        "notice": "教學模擬 PLM／ECO 資料；不得視為正式 BOM、圖紙或工程放行依據。",
        "revisions": revisions,
        "open_ecos": [item for item in ecos if item["status"] != "effective"],
        "ecos": ecos,
    }


def current_bom(family: str, now: datetime | None = None) -> dict:
    family = _family(family)
    snapshot = engineering_snapshot(now)
    revision = next(item for item in snapshot["revisions"] if item["family"] == family)
    return {"source": snapshot["source"], "read_only": True, "bom": revision, "notice": snapshot["notice"]}


def product_revision(family: str, now: datetime | None = None) -> dict:
    return current_bom(family, now)


def open_ecos(now: datetime | None = None) -> dict:
    snapshot = engineering_snapshot(now)
    return {"source": snapshot["source"], "read_only": True, "ecos": snapshot["open_ecos"], "notice": snapshot["notice"]}


def revision_difference(eco_id: str, now: datetime | None = None) -> dict:
    eco_id = _safe_identifier(eco_id, "eco_id")
    snapshot = engineering_snapshot(now)
    eco = next((item for item in snapshot["ecos"] if item["eco_id"] == eco_id), None)
    if eco is None:
        raise ValueError("unknown ECO")
    return {"source": snapshot["source"], "read_only": True, "eco_id": eco_id, "changes": eco["changes"], "notice": snapshot["notice"]}


def change_impact(eco_id: str, now: datetime | None = None) -> dict:
    eco_id = _safe_identifier(eco_id, "eco_id")
    snapshot = engineering_snapshot(now)
    eco = next((item for item in snapshot["ecos"] if item["eco_id"] == eco_id), None)
    if eco is None:
        raise ValueError("unknown ECO")
    revision = next(item for item in snapshot["revisions"] if item["family"] == eco["family"])
    return {
        "source": snapshot["source"], "read_only": True, "eco": eco,
        "schedule_impact": {"extra_setup_minutes": revision["extra_setup_minutes"], "extra_operation_minutes": revision["extra_operation_minutes"]},
        "notice": snapshot["notice"],
    }


def process_snapshot(now: datetime | None = None) -> dict:
    snapshot_at = (now or datetime.now()).replace(second=0, microsecond=0)
    return {
        "source": "AI Work SPC Demo MCP",
        "dataset_type": "synthetic_electronics_spc",
        "read_only": True,
        "snapshot_at": snapshot_at.isoformat(timespec="minutes"),
        "notice": "教學模擬 SPC 統計資料；不得取代正式量測、管制圖或製程放行。",
        "profiles": [
            {"family": "A", "center_id": "SMT-01", "metric": "solder_paste_height", "cp": 1.82, "cpk": 1.67, "status": "stable", "extra_inspection_minutes_per_100": 0},
            {"family": "B", "center_id": "ASSY-01", "metric": "connector_alignment", "cp": 1.36, "cpk": 1.21, "status": "watch", "extra_inspection_minutes_per_100": 12},
            {"family": "C", "center_id": "TEST-01", "metric": "bga_joint_resistance", "cp": 1.08, "cpk": 0.91, "status": "alert", "extra_inspection_minutes_per_100": 35},
        ],
        "out_of_control_points": [
            {"point_id": "SPC-OOC-027", "family": "C", "center_id": "TEST-01", "observed_at": "2026-10-18T14:20", "rule": "Western Electric Rule 2", "value": 3.8, "limit": 3.2},
        ],
    }


def process_capability(family: str, now: datetime | None = None) -> dict:
    family = _family(family)
    snapshot = process_snapshot(now)
    profile = next(item for item in snapshot["profiles"] if item["family"] == family)
    return {"source": snapshot["source"], "read_only": True, "profile": profile, "notice": snapshot["notice"]}


def out_of_control_points(now: datetime | None = None) -> dict:
    snapshot = process_snapshot(now)
    return {"source": snapshot["source"], "read_only": True, "points": snapshot["out_of_control_points"], "notice": snapshot["notice"]}


def order_quality_risk(order: str, family: str, quantity: float, now: datetime | None = None) -> dict:
    order = _safe_identifier(order, "order")
    family = _family(family)
    quantity = _quantity(quantity)
    snapshot = process_snapshot(now)
    profile = next(item for item in snapshot["profiles"] if item["family"] == family)
    inspection = math.ceil(quantity / 100 * float(profile["extra_inspection_minutes_per_100"]))
    return {
        "source": snapshot["source"], "read_only": True, "order": order,
        "family": family, "quantity": quantity, "profile": profile,
        "extra_inspection_minutes": inspection,
        "matching_points": [item for item in snapshot["out_of_control_points"] if item["family"] == family],
        "notice": snapshot["notice"],
    }
