"""Bounded, read-only FactorySemantics queries for the MES MCP service."""

from __future__ import annotations

from datetime import datetime, time, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx


class MesReadError(RuntimeError):
    pass


class MesReader:
    def __init__(self, base_url: str, analyst_password: str) -> None:
        if base_url.rstrip("/") != "http://127.0.0.1:8010":
            raise ValueError("MES API must remain on 127.0.0.1:8010")
        if not analyst_password:
            raise ValueError("FSMES_ANALYST_PASSWORD is required")
        self.base_url = base_url.rstrip("/")
        self.analyst_password = analyst_password

    def _get(self, client: httpx.Client, path: str, params: dict | None = None) -> dict | list:
        response = client.get(path, params=params)
        if response.status_code == 401:
            login = client.post(
                "/auth/login", json={"code": "ANALYST", "password": self.analyst_password}
            )
            if login.status_code != 200:
                raise MesReadError("MES analyst login failed")
            response = client.get(path, params=params)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise MesReadError(f"MES GET {path} failed ({response.status_code})") from exc
        return response.json()

    def _plant(self, client: httpx.Client) -> dict:
        health = self._get(client, "/health")
        if not isinstance(health, dict) or health.get("plant") != "bottling":
            raise MesReadError("MES plant identity does not match bottling")
        return health

    def overdue_orders(self) -> dict:
        now = datetime.now(timezone.utc)
        with httpx.Client(base_url=self.base_url, timeout=20.0) as client:
            plant = self._plant(client)
            records = []
            offset = 0
            total = 0
            while offset < 500:
                page = self._get(client, "/workorders", {
                    "due_before": now.isoformat(), "limit": 100, "offset": offset,
                })
                if not isinstance(page, dict):
                    raise MesReadError("MES work-order response is invalid")
                records.extend(
                    item for item in page.get("items", [])
                    if item.get("status") not in {"completed", "closed", "cancelled"}
                )
                total = int(page.get("total") or 0)
                offset += len(page.get("items", []))
                if not page.get("has_more") or not page.get("items"):
                    break
        return {
            "source": "FactorySemantics MES", "plant": plant["plant"],
            "plant_timezone": plant.get("timezone"), "as_of_utc": now.isoformat(),
            "orders": records, "overdue_count": len(records),
            "checked": min(offset, total), "total_due_before_now": total,
            "has_more": offset < total,
            "source_paths": ["GET /workorders?due_before=<as_of_utc>"],
        }

    def line_downtime_today(self) -> dict:
        with httpx.Client(base_url=self.base_url, timeout=20.0) as client:
            plant = self._plant(client)
            zone = ZoneInfo(str(plant.get("timezone") or "UTC"))
            now = datetime.now(zone)
            start = datetime.combine(now.date(), time.min, tzinfo=zone)
            hours = max((now - start).total_seconds() / 3600, 0.001)
            downtime = self._get(client, "/analysis/downtime", {"hours": hours})
            states = self._get(client, "/equipment/states")
        return {
            "source": "FactorySemantics MES", "plant": plant["plant"],
            "plant_timezone": str(zone), "local_date": now.date().isoformat(),
            "downtime": downtime, "current_equipment_states": states,
            "source_paths": ["GET /analysis/downtime", "GET /equipment/states"],
        }

    def work_order_production_quality(self, code: str) -> dict:
        code = code.strip()
        if not code or len(code) > 80 or not all(char.isalnum() or char in "-_" for char in code):
            raise ValueError("MES work-order code may contain only letters, digits, - and _")
        encoded = quote(code, safe="")
        with httpx.Client(base_url=self.base_url, timeout=20.0) as client:
            plant = self._plant(client)
            order = self._get(client, f"/workorders/{encoded}")
            genealogy = self._get(client, f"/execution/genealogy/{encoded}")
            checks = self._get(client, "/quality/checks", {"order": code, "limit": 50})
        return {
            "source": "FactorySemantics MES", "plant": plant["plant"],
            "plant_timezone": plant.get("timezone"), "order": order,
            "genealogy": genealogy, "quality_checks": checks,
            "source_paths": [f"GET /workorders/{encoded}",
                             f"GET /execution/genealogy/{encoded}",
                             "GET /quality/checks?order=<code>"],
        }
