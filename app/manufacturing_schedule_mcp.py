from __future__ import annotations

import asyncio
import json
import math
import time
from collections import defaultdict
from datetime import datetime, time as clock_time, timedelta
from typing import Any, Callable

from app.db import create_mcp_audit_log
from app.manufacturing_schedule_demo import normalize_scenario, run_schedule
from app.mcp_orchestrator import normalize_mes_result
from app.mcp_runtime import McpConnectionError, call_streamable_http_tool


class ManufacturingMcpError(RuntimeError):
    pass


ORDER_QUERY = {
    "model": "sale.order",
    "domain": '[["state","in",["draft","sent","sale","done"]]]',
    "fields": [
        "id", "name", "partner_id", "date_order", "commitment_date", "expected_date",
        "state", "amount_total", "currency_id", "order_line",
    ],
    "limit": 10,
    "order": "date_order desc, id desc",
}
STOCK_FIELDS = ["id", "product_id", "location_id", "quantity", "reserved_quantity", "available_quantity"]


def _extract_json(result: dict[str, Any], source: str) -> Any:
    structured = result.get("structuredContent")
    if isinstance(structured, (dict, list)):
        return structured
    blocks = result.get("content")
    if not isinstance(blocks, list) or len(blocks) != 1 or not isinstance(blocks[0], dict):
        raise ManufacturingMcpError(f"{source} 沒有回傳可解析的 JSON 資料")
    if blocks[0].get("type") != "text":
        raise ManufacturingMcpError(f"{source} 回傳格式不是 JSON 文字")
    try:
        value = json.loads(str(blocks[0].get("text") or ""))
    except json.JSONDecodeError as exc:
        raise ManufacturingMcpError(f"{source} 回傳的 JSON 格式錯誤") from exc
    if not isinstance(value, (dict, list)):
        raise ManufacturingMcpError(f"{source} 回傳資料類型不正確")
    return value


def _summary(value: Any) -> str:
    if isinstance(value, list):
        return f"{len(value)} records"
    if isinstance(value, dict):
        for key in ("overdue_count", "count", "total"):
            if key in value:
                return f"{key}={value[key]}"
        return ", ".join(sorted(str(key) for key in value)[:5]) or "object"
    return type(value).__name__


async def _call_mcp(
    server: dict[str, Any],
    tool_name: str,
    arguments: dict[str, Any],
    *,
    user: dict[str, Any],
    call_tool: Callable[[dict[str, Any], str, dict[str, Any]], dict[str, Any]],
) -> tuple[Any, dict[str, Any]]:
    started = time.perf_counter()
    audit = {
        "server_id": int(server["id"]),
        "user_id": int(user["id"]),
        "action": "tools/call",
        "tool_name": tool_name,
        "input_json": json.dumps(arguments, ensure_ascii=False, separators=(",", ":")),
    }
    try:
        raw = await asyncio.to_thread(call_tool, server, tool_name, arguments)
        if server.get("slug") == "factory-mes":
            raw = normalize_mes_result(raw)
        value = _extract_json(raw, f"{server['name']} / {tool_name}")
    except (McpConnectionError, ManufacturingMcpError, ValueError, OSError) as exc:
        create_mcp_audit_log(**audit, status="failed", error_message=str(exc)[:1000])
        raise ManufacturingMcpError(f"{server['name']} / {tool_name} 查詢失敗：{exc}") from exc
    summary = _summary(value)
    create_mcp_audit_log(
        **audit,
        status="completed",
        output_json=json.dumps({"summary": summary}, ensure_ascii=False),
    )
    trace = {
        "kind": "mcp",
        "server": server["name"],
        "server_id": int(server["id"]),
        "tool": tool_name,
        "arguments": arguments,
        "status": "completed",
        "duration_ms": round((time.perf_counter() - started) * 1000),
        "result": summary,
    }
    return value, trace


def _relation(value: Any) -> tuple[int | None, str]:
    if isinstance(value, list) and len(value) >= 2:
        try:
            identifier = int(value[0])
        except (TypeError, ValueError):
            identifier = None
        return identifier, str(value[1])
    return None, ""


def _record_id(row: Any) -> int | None:
    if not isinstance(row, dict):
        return None
    try:
        return int(row.get("id"))
    except (TypeError, ValueError):
        return None


def _as_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _add_workdays(value: datetime, days: int) -> datetime:
    current = value
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def _priority(amount: float) -> str:
    if amount >= 250_000:
        return "urgent"
    if amount >= 100_000:
        return "high"
    return "normal"


def _build_snapshot(
    order_rows: list[dict[str, Any]],
    line_rows: list[dict[str, Any]],
    quant_rows: list[dict[str, Any]],
    mes_snapshot: dict[str, Any],
    traces: list[dict[str, Any]],
    *,
    snapshot_at: datetime,
    odoo_name: str,
    mes_name: str,
) -> dict[str, Any]:
    lines_by_order: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for line in line_rows:
        if not isinstance(line, dict):
            continue
        order_id, _ = _relation(line.get("order_id"))
        if order_id is not None:
            lines_by_order[order_id].append(line)

    selected = [row for row in order_rows if (row_id := _record_id(row)) is not None and lines_by_order.get(row_id)][:5]
    if not selected:
        raise ManufacturingMcpError("Goldsys Odoo 沒有含產品明細的可排程銷售訂單")

    demand: dict[int, float] = defaultdict(float)
    product_names: dict[int, str] = {}
    for row in selected:
        for line in lines_by_order[int(row["id"])]:
            product_id, product_name = _relation(line.get("product_id"))
            if product_id is None:
                continue
            demand[product_id] += float(line.get("product_uom_qty") or 0)
            product_names[product_id] = product_name

    stock: dict[int, dict[str, float]] = defaultdict(lambda: {"on_hand": 0.0, "available": 0.0})
    for quant in quant_rows:
        if not isinstance(quant, dict):
            continue
        product_id, product_name = _relation(quant.get("product_id"))
        if product_id is None:
            continue
        stock[product_id]["on_hand"] += float(quant.get("quantity") or 0)
        stock[product_id]["available"] += float(quant.get("available_quantity") or 0)
        product_names.setdefault(product_id, product_name)

    inventory = []
    shortages: dict[int, float] = {}
    for product_id, required in sorted(demand.items()):
        available = stock[product_id]["available"]
        shortage = max(0.0, required - available)
        shortages[product_id] = shortage
        inventory.append({
            "item": product_names.get(product_id) or f"Odoo product {product_id}",
            "on_hand": round(stock[product_id]["on_hand"], 2),
            "available": round(available, 2),
            "required": round(required, 2),
            "status": f"短缺 {shortage:g}" if shortage else "充足",
            "source_id": f"stock.quant/product/{product_id}",
        })

    orders = []
    derived_due_count = 0
    for row in selected:
        row_lines = lines_by_order[int(row["id"])]
        products = []
        product_ids = []
        quantity = 0.0
        order_shortages = []
        for line in row_lines:
            product_id, product_name = _relation(line.get("product_id"))
            if product_id is None:
                continue
            product_ids.append(product_id)
            products.append(product_name)
            quantity += float(line.get("product_uom_qty") or 0)
            if shortages.get(product_id, 0) > 0:
                order_shortages.append(f"{product_name} 缺 {shortages[product_id]:g}")
        if not product_ids:
            continue
        order_date = _as_datetime(row.get("date_order")) or snapshot_at
        due = _as_datetime(row.get("commitment_date")) or _as_datetime(row.get("expected_date"))
        due_source = "Odoo commitment_date / expected_date"
        if due is None:
            due = datetime.combine(_add_workdays(order_date, 10).date(), clock_time(17, 0))
            due_source = "本地規則：訂單日後 10 個工作日"
            derived_due_count += 1
        ready = _add_workdays(snapshot_at, 2) if order_shortages else snapshot_at
        _, customer = _relation(row.get("partner_id"))
        amount = float(row.get("amount_total") or 0)
        orders.append({
            "order": str(row.get("name") or f"Odoo-{row['id']}"),
            "odoo_id": int(row["id"]),
            "odoo_state": str(row.get("state") or ""),
            "customer": customer,
            "product": " / ".join(dict.fromkeys(products)),
            "family": ("A", "B", "C")[product_ids[0] % 3],
            "quantity": int(quantity) if quantity.is_integer() else round(quantity, 2),
            "due_at": due.isoformat(timespec="minutes"),
            "due_source": due_source,
            "priority": _priority(amount),
            "priority_basis": "本地規則：依 Odoo amount_total 分級",
            "material": "；".join(order_shortages) if order_shortages else "Odoo 可用庫存足夠",
            "material_ready_at": ready.isoformat(timespec="minutes"),
            "source_kind": "odoo_mcp",
        })

    odoo_order_count = len(orders)
    supplemental = mes_snapshot.get("supplemental_orders")
    supplemental = supplemental if isinstance(supplemental, list) else []
    existing_order_ids = {item["order"] for item in orders}
    for item in supplemental:
        if len(orders) >= 5:
            break
        if not isinstance(item, dict) or str(item.get("order") or "") in existing_order_ids:
            continue
        try:
            quantity = float(item["quantity"])
            due_workdays = int(item["due_workdays"])
        except (KeyError, TypeError, ValueError):
            continue
        if quantity <= 0 or due_workdays < 1:
            continue
        due = datetime.combine(_add_workdays(snapshot_at, due_workdays).date(), clock_time(17, 0))
        order_id = str(item["order"])
        orders.append({
            "order": order_id,
            "odoo_id": None,
            "odoo_state": "mes_demo",
            "customer": "MES 教學客戶",
            "product": str(item.get("product") or "MES 教學產品"),
            "family": str(item.get("family")) if item.get("family") in {"A", "B", "C"} else "A",
            "quantity": int(quantity) if quantity.is_integer() else round(quantity, 2),
            "due_at": due.isoformat(timespec="minutes"),
            "due_source": "MES MCP 教學訂單參數",
            "priority": str(item.get("priority")) if item.get("priority") in {"normal", "high", "urgent"} else "normal",
            "priority_basis": "MES MCP 教學訂單參數",
            "material": str(item.get("material") or "MES 模擬物料齊套"),
            "material_ready_at": snapshot_at.isoformat(timespec="minutes"),
            "source_kind": "mes_mcp_demo",
        })
        existing_order_ids.add(order_id)
    supplemental_count = len(orders) - odoo_order_count

    work_centers = mes_snapshot.get("work_centers")
    if not isinstance(work_centers, list) or not work_centers:
        raise ManufacturingMcpError("MES MCP 沒有提供電子製造工作中心")
    required_center_fields = {"id", "name", "shift", "units_per_hour", "setup_minutes"}
    if any(not isinstance(center, dict) or not required_center_fields.issubset(center) for center in work_centers):
        raise ManufacturingMcpError("MES MCP 工作中心格式不正確")
    try:
        if any(float(center["units_per_hour"]) <= 0 or not 0 <= int(center["setup_minutes"]) <= 1440
               for center in work_centers):
            raise ManufacturingMcpError("MES MCP 工作中心產能或換線時間不正確")
    except (TypeError, ValueError) as exc:
        raise ManufacturingMcpError("MES MCP 工作中心產能或換線時間不正確") from exc
    if len({str(center["id"]) for center in work_centers}) != len(work_centers):
        raise ManufacturingMcpError("MES MCP 工作中心 ID 重複")
    work_centers = [{
        **center,
        "id": str(center["id"]),
        "name": str(center["name"]),
        "shift": str(center["shift"]),
        "units_per_hour": float(center["units_per_hour"]),
        "setup_minutes": int(center["setup_minutes"]),
    } for center in work_centers]
    center_ids = {str(item["id"]) for item in work_centers}
    mapped_downtimes = []
    for item in mes_snapshot.get("downtimes") or []:
        if not isinstance(item, dict) or str(item.get("center_id")) not in center_ids:
            continue
        start = _as_datetime(item.get("start"))
        end = _as_datetime(item.get("end"))
        if start is None or end is None or end <= start:
            continue
        mapped_downtimes.append({
            "center_id": str(item["center_id"]),
            "start": start.isoformat(timespec="minutes"),
            "end": end.isoformat(timespec="minutes"),
            "reason": str(item.get("reason") or "MES MCP 停機"),
            "source": "mes_mcp",
        })

    warnings = [str(mes_snapshot.get("notice") or "MES 工作中心為教學模擬資料。")]
    plant = str(mes_snapshot.get("plant") or "unknown")
    if len(orders) < 5:
        warnings.append(f"MCP 目前只提供 {len(orders)} 筆可排程訂單，未用程序內假資料補足。")
    elif supplemental_count:
        warnings.append(f"Odoo MCP 提供 {odoo_order_count} 筆訂單；另由 MES MCP 補入 {supplemental_count} 筆明確標示的教學訂單。")
    if derived_due_count:
        warnings.append(f"{derived_due_count} 筆訂單未設定 Odoo 承諾／預計交期，暫用『訂單日後 10 個工作日』本地規則。")

    return {
        "snapshot_at": snapshot_at.isoformat(timespec="minutes"),
        "orders": orders,
        "inventory": inventory,
        "work_centers": work_centers,
        "mes_snapshot": {
            "source": mes_snapshot.get("source"),
            "dataset_type": mes_snapshot.get("dataset_type"),
            "read_only": mes_snapshot.get("read_only"),
            "plant": plant,
            "plant_timezone": mes_snapshot.get("plant_timezone"),
            "notice": mes_snapshot.get("notice"),
            "work_centers": work_centers,
            "downtimes": mapped_downtimes,
        },
        "mapped_downtimes": mapped_downtimes,
        "warnings": warnings,
        "sources": [
            {"id": "odoo-orders-mcp", "name": f"{odoo_name} / search_read",
             "detail": f"sale.order + sale.order.line · {odoo_order_count} 筆可排程訂單"},
            {"id": "odoo-stock-mcp", "name": f"{odoo_name} / search_read",
             "detail": f"stock.quant · {len(inventory)} 項訂單相關產品"},
            {"id": "factory-mes-mcp", "name": f"{mes_name} / mes_electronics_schedule_snapshot",
             "detail": f"plant={plant} · {len(work_centers)} 個模擬工作中心 · {len(mapped_downtimes)} 筆停機 · {supplemental_count} 筆補充教學訂單"},
        ],
        "trace": traces,
    }


async def run_mcp_schedule(
    scenario: dict[str, Any] | None,
    *,
    user: dict[str, Any],
    odoo_server: dict[str, Any],
    mes_server: dict[str, Any],
    call_tool: Callable[[dict[str, Any], str, dict[str, Any]], dict[str, Any]] = call_streamable_http_tool,
    now: datetime | None = None,
) -> dict[str, Any]:
    selected_scenario = normalize_scenario(scenario)
    order_rows, order_trace = await _call_mcp(
        odoo_server, "search_read", ORDER_QUERY, user=user, call_tool=call_tool,
    )
    if not isinstance(order_rows, list):
        raise ManufacturingMcpError("Goldsys Odoo / sale.order 回傳格式不正確")
    schedulable_ids = [row_id for row in order_rows
                       if (row_id := _record_id(row)) is not None and row.get("order_line")][:5]
    if not schedulable_ids:
        raise ManufacturingMcpError("Goldsys Odoo 沒有含產品明細的可排程訂單")
    line_query = {
        "model": "sale.order.line",
        "domain": json.dumps([["order_id", "in", schedulable_ids]], ensure_ascii=False),
        "fields": ["id", "order_id", "product_id", "product_uom_qty", "qty_delivered", "price_unit"],
        "limit": 100,
        "order": "id asc",
    }
    line_task = _call_mcp(odoo_server, "search_read", line_query, user=user, call_tool=call_tool)
    mes_task = _call_mcp(mes_server, "mes_electronics_schedule_snapshot", {}, user=user, call_tool=call_tool)
    (line_rows, line_trace), (mes_snapshot, mes_trace) = await asyncio.gather(line_task, mes_task)
    if not isinstance(line_rows, list) or not isinstance(mes_snapshot, dict):
        raise ManufacturingMcpError("MCP 排程來源回傳格式不正確")
    product_ids = sorted({
        product_id for row in line_rows if isinstance(row, dict)
        for product_id, _name in [_relation(row.get("product_id"))] if product_id is not None
    })
    if not product_ids:
        raise ManufacturingMcpError("Goldsys Odoo 訂單明細沒有可查詢的產品")
    stock_query = {
        "model": "stock.quant",
        "domain": json.dumps([
            ["location_id.usage", "=", "internal"], ["product_id", "in", product_ids],
        ], ensure_ascii=False),
        "fields": STOCK_FIELDS,
        "limit": min(500, max(100, len(product_ids) * 20)),
        "order": "id desc",
    }
    quant_rows, stock_trace = await _call_mcp(
        odoo_server, "search_read", stock_query, user=user, call_tool=call_tool,
    )
    if not isinstance(quant_rows, list):
        raise ManufacturingMcpError("Goldsys Odoo / stock.quant 回傳格式不正確")
    snapshot = _build_snapshot(
        order_rows,
        line_rows,
        quant_rows,
        mes_snapshot,
        [order_trace, line_trace, stock_trace, mes_trace],
        snapshot_at=(now or datetime.now()).replace(second=0, microsecond=0),
        odoo_name=str(odoo_server["name"]),
        mes_name=str(mes_server["name"]),
    )
    return run_schedule(selected_scenario, snapshot=snapshot)
