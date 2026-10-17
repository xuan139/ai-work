"""Synthetic read-only QMS and CMMS data for the manufacturing demo."""

from __future__ import annotations

import re
from datetime import datetime, time, timedelta


IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _next_weekday(value: datetime) -> datetime:
    current = value
    while current.weekday() >= 5:
        current += timedelta(days=1)
    return current


def quality_snapshot(now: datetime | None = None) -> dict:
    snapshot_at = (now or datetime.now()).replace(second=0, microsecond=0)
    return {
        "source": "AI Work QMS Demo MCP",
        "dataset_type": "synthetic_electronics_quality",
        "read_only": True,
        "snapshot_at": snapshot_at.isoformat(timespec="minutes"),
        "notice": "教學模擬品質資料；不得視為真實檢驗、放行或客訴紀錄。",
        "profiles": [
            {
                "family": "A", "first_pass_yield_pct": 98.2, "defect_rate_pct": 1.8,
                "expected_rework_minutes_per_100": 18, "top_defect": "少錫",
                "quality_level": "stable",
            },
            {
                "family": "B", "first_pass_yield_pct": 95.8, "defect_rate_pct": 4.2,
                "expected_rework_minutes_per_100": 42, "top_defect": "連接器偏位",
                "quality_level": "watch",
            },
            {
                "family": "C", "first_pass_yield_pct": 91.2, "defect_rate_pct": 8.8,
                "expected_rework_minutes_per_100": 95, "top_defect": "BGA 焊點異常",
                "quality_level": "alert",
            },
        ],
        "open_events": [
            {
                "event_id": "QMS-NCR-2026-017", "family": "C", "station": "TEST-01",
                "severity": "major", "status": "containment",
                "summary": "抽樣發現 BGA 焊點異常，Demo 排程加入預期返工時間。",
            }
        ],
    }


def quality_order_detail(order: str, family: str, quantity: float, now: datetime | None = None) -> dict:
    if not IDENTIFIER_RE.fullmatch(order):
        raise ValueError("order must be a safe identifier")
    if family not in {"A", "B", "C"}:
        raise ValueError("family must be A, B or C")
    if not isinstance(quantity, (int, float)) or isinstance(quantity, bool) or not 0 < float(quantity) <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    snapshot = quality_snapshot(now)
    profile = next(item for item in snapshot["profiles"] if item["family"] == family)
    rework = round(float(quantity) / 100 * profile["expected_rework_minutes_per_100"])
    return {
        "source": snapshot["source"], "read_only": True, "order": order,
        "family": family, "quantity": quantity, "profile": profile,
        "expected_rework_minutes": rework,
        "matching_events": [item for item in snapshot["open_events"] if item["family"] == family],
        "notice": snapshot["notice"],
    }


def maintenance_snapshot(now: datetime | None = None) -> dict:
    snapshot_at = (now or datetime.now()).replace(second=0, microsecond=0)
    day = _next_weekday(snapshot_at + timedelta(days=1)).date()
    start = datetime.combine(day, time(10, 0))
    end = start + timedelta(hours=1)
    return {
        "source": "AI Work CMMS Demo MCP",
        "dataset_type": "synthetic_electronics_maintenance",
        "read_only": True,
        "snapshot_at": snapshot_at.isoformat(timespec="minutes"),
        "notice": "教學模擬維護資料；不得視為真實設備狀態或維修指令。",
        "assets": [
            {
                "center_id": "SMT-01", "asset_id": "EQ-SMT-01", "health": "watch",
                "open_work_order": "MWO-2026-018", "mtbf_hours": 412, "mttr_minutes": 48,
                "reason": "吸嘴真空值趨勢偏低，安排點檢。",
            },
            {
                "center_id": "ASSY-01", "asset_id": "EQ-ASSY-01", "health": "normal",
                "open_work_order": None, "mtbf_hours": 790, "mttr_minutes": 31,
                "reason": "無未結維護工單。",
            },
            {
                "center_id": "TEST-01", "asset_id": "EQ-TEST-01", "health": "planned",
                "open_work_order": "MWO-2026-021", "mtbf_hours": 605, "mttr_minutes": 40,
                "reason": "依週期安排校驗；MES 另有既定保養窗口。",
            },
        ],
        "maintenance_windows": [
            {
                "work_order": "MWO-2026-018", "center_id": "SMT-01",
                "start": start.isoformat(timespec="minutes"),
                "end": end.isoformat(timespec="minutes"),
                "reason": "CMMS 模擬吸嘴與真空系統點檢", "status": "planned",
            }
        ],
    }


def maintenance_asset_detail(center_id: str, now: datetime | None = None) -> dict:
    if not IDENTIFIER_RE.fullmatch(center_id):
        raise ValueError("center_id must be a safe identifier")
    snapshot = maintenance_snapshot(now)
    asset = next((item for item in snapshot["assets"] if item["center_id"] == center_id), None)
    if asset is None:
        raise ValueError("unknown work center")
    return {
        "source": snapshot["source"], "read_only": True, "asset": asset,
        "maintenance_windows": [
            item for item in snapshot["maintenance_windows"] if item["center_id"] == center_id
        ],
        "notice": snapshot["notice"],
    }
