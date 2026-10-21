from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any

from app.daily_production_report import REPORT_TIMEZONE, generate_and_store_report
from app.db import get_production_report_by_date, get_user_by_username, init_db, list_mcp_servers
from app.manufacturing_schedule_mcp import ManufacturingMcpError, run_mcp_schedule
from app.mcp_orchestrator import available_mcp_servers
from app.scheduling_engine import current_scheduling_engine


REQUIRED_SERVERS = (
    ("odoo", "search_read", "Goldsys Odoo"),
    ("factory-mes", "mes_electronics_schedule_snapshot", "FactorySemantics MES"),
    ("manufacturing-qms", "qms_quality_snapshot", "Electronics QMS"),
    ("manufacturing-cmms", "cmms_maintenance_snapshot", "Electronics CMMS"),
    ("manufacturing-wms", "wms_inventory_snapshot", "Electronics WMS"),
    ("manufacturing-plm", "plm_engineering_snapshot", "Electronics PLM"),
    ("manufacturing-spc", "spc_process_snapshot", "Electronics SPC"),
)


def schedule_servers() -> list[dict[str, Any]]:
    available = available_mcp_servers(list_mcp_servers())
    selected: list[dict[str, Any]] = []
    missing: list[str] = []
    for slug, tool_name, label in REQUIRED_SERVERS:
        server = next(
            (
                item for item in available
                if item.get("slug") == slug
                and any(tool.get("name") == tool_name for tool in item.get("tools") or [])
            ),
            None,
        )
        if server is None:
            missing.append(f"{label} / {tool_name}")
        else:
            selected.append(server)
    if missing:
        raise ManufacturingMcpError(f"每日生產報告所需 MCP 尚未連線：{', '.join(missing)}")
    return selected


async def generate_today_once() -> dict[str, Any]:
    init_db()
    report_date = datetime.now(REPORT_TIMEZONE).date().isoformat()
    existing = get_production_report_by_date(report_date)
    if existing and existing.get("status") == "completed":
        return {"result": "already_exists", "id": existing["id"], "report_date": report_date}

    username = os.getenv("AI_WORK_DAILY_REPORT_USER", "admin").strip() or "admin"
    user = get_user_by_username(username)
    if user is None or user.get("role") != "admin":
        raise RuntimeError("AI_WORK_DAILY_REPORT_USER 必須是現有管理員帳號")

    odoo, mes, qms, cmms, wms, plm, spc = schedule_servers()
    schedule = await run_mcp_schedule(
        {}, user=user, odoo_server=odoo, mes_server=mes, qms_server=qms,
        cmms_server=cmms, wms_server=wms, plm_server=plm, spc_server=spc,
        default_engine=current_scheduling_engine()["id"],
    )
    record = generate_and_store_report(schedule, user)
    return {"result": record["status"], "id": record["id"], "report_date": record["report_date"]}


def main() -> int:
    try:
        result = asyncio.run(generate_today_once())
    except Exception as exc:
        print(f"daily production report failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
