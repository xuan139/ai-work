"""Synthetic electronics planning snapshot exposed only through the read-only MES MCP."""

from __future__ import annotations

from datetime import datetime, time, timedelta


def _next_weekday(value: datetime) -> datetime:
    current = value
    while current.weekday() >= 5:
        current += timedelta(days=1)
    return current


def electronics_schedule_snapshot(now: datetime | None = None) -> dict:
    snapshot_at = (now or datetime.now()).replace(second=0, microsecond=0)
    maintenance_day = _next_weekday(snapshot_at + timedelta(days=1)).date()
    maintenance_start = datetime.combine(maintenance_day, time(13, 0))
    maintenance_end = datetime.combine(maintenance_day, time(14, 30))
    work_centers = [
        {"id": "SMT-01", "name": "SMT", "shift": "08:00-17:00", "units_per_hour": 70,
         "setup_minutes": 30, "state": "running"},
        {"id": "ASSY-01", "name": "組裝", "shift": "08:00-17:00", "units_per_hour": 45,
         "setup_minutes": 20, "state": "running"},
        {"id": "TEST-01", "name": "測試", "shift": "08:00-17:00", "units_per_hour": 55,
         "setup_minutes": 15, "state": "maintenance_planned"},
    ]
    return {
        "source": "AI Work MES MCP",
        "dataset_type": "synthetic_electronics_schedule",
        "read_only": True,
        "snapshot_at": snapshot_at.isoformat(timespec="minutes"),
        "plant": "ELECTRONICS-DEMO-01",
        "plant_timezone": "Asia/Taipei",
        "notice": "教學模擬資料；由 MES MCP 提供，不代表真實工廠設備狀態。",
        "work_centers": work_centers,
        "downtimes": [
            {
                "center_id": "TEST-01",
                "start": maintenance_start.isoformat(timespec="minutes"),
                "end": maintenance_end.isoformat(timespec="minutes"),
                "reason": "MES 模擬預防保養",
            }
        ],
        "routing": ["SMT-01", "ASSY-01", "TEST-01"],
        "supplemental_orders": [
            {"order": "MES-DEMO-1001", "product": "電子控制板教學批", "family": "A", "quantity": 120,
             "due_workdays": 2, "priority": "high", "material": "MES 模擬物料齊套"},
            {"order": "MES-DEMO-1002", "product": "IoT Gateway 教學批", "family": "B", "quantity": 80,
             "due_workdays": 3, "priority": "normal", "material": "MES 模擬物料齊套"},
            {"order": "MES-DEMO-1003", "product": "Sensor Hub 教學批", "family": "C", "quantity": 160,
             "due_workdays": 4, "priority": "normal", "material": "MES 模擬物料齊套"},
            {"order": "MES-DEMO-1004", "product": "工業控制器教學批", "family": "B", "quantity": 60,
             "due_workdays": 2, "priority": "urgent", "material": "MES 模擬物料齊套"},
            {"order": "MES-DEMO-1005", "product": "電源模組教學批", "family": "A", "quantity": 200,
             "due_workdays": 5, "priority": "normal", "material": "MES 模擬物料齊套"},
        ],
    }
