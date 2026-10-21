from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pymupdf

from app.db import (
    claim_daily_production_report,
    complete_production_report,
    create_nas_asset,
    fail_production_report,
    get_production_report,
    update_nas_asset,
)


BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "storage" / "production_reports"
REPORT_TIMEZONE = ZoneInfo(os.getenv("AI_WORK_REPORT_TIMEZONE", "Asia/Taipei"))
PDF_FONT_CANDIDATES = (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
)


class ProductionReportError(RuntimeError):
    pass


def resolve_pdf_font() -> Path:
    configured = os.getenv("AI_WORK_PDF_FONT", "").strip()
    candidates = (configured, *PDF_FONT_CANDIDATES) if configured else PDF_FONT_CANDIDATES
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path
    raise ProductionReportError(
        "找不到可嵌入的繁體中文字型；Ubuntu 請安裝 fonts-noto-cjk，或設定 AI_WORK_PDF_FONT"
    )


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _percent(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round(numerator / denominator * 100, 1)


def _metric(
    label: str,
    value: float | int | None,
    unit: str,
    formula: str,
    sources: list[str],
    *,
    precision: int = 1,
    note: str = "",
) -> dict[str, Any]:
    if value is None:
        display = "N/A"
        status = "unavailable"
    elif isinstance(value, float):
        display = f"{value:.{precision}f}{unit}"
        status = "available"
    else:
        display = f"{value}{unit}"
        status = "available"
    return {
        "label": label,
        "value": value,
        "unit": unit,
        "display": display,
        "status": status,
        "formula": formula,
        "sources": sources,
        "note": note,
    }


def _minutes_between(start: Any, end: Any) -> int:
    try:
        start_at = datetime.fromisoformat(str(start))
        end_at = datetime.fromisoformat(str(end))
    except (TypeError, ValueError):
        return 0
    return max(0, round((end_at - start_at).total_seconds() / 60))


def _source_catalog(schedule: dict[str, Any]) -> list[dict[str, Any]]:
    sources = []
    for index, item in enumerate(schedule.get("sources") or [], start=1):
        if not isinstance(item, dict):
            continue
        sources.append({
            "ref": f"S{index}",
            "id": str(item.get("id") or f"source-{index}"),
            "name": str(item.get("name") or "未命名來源"),
            "detail": str(item.get("detail") or ""),
        })
    return sources


def calculate_fixed_kpis(schedule: dict[str, Any]) -> dict[str, dict[str, Any]]:
    orders = [item for item in schedule.get("orders") or [] if isinstance(item, dict)]
    operations = [item for item in schedule.get("operations") or [] if isinstance(item, dict)]
    inventory = [item for item in schedule.get("inventory") or [] if isinstance(item, dict)]
    downtimes = [item for item in schedule.get("downtimes") or [] if isinstance(item, dict)]
    production = (schedule.get("mes_snapshot") or {}).get("daily_production") or {}
    source_refs = {item["id"]: item["ref"] for item in _source_catalog(schedule)}

    def ref(source_id: str, fallback: str) -> str:
        return source_refs.get(source_id, fallback)

    planned_units = _number(production.get("planned_units"))
    completed_units = _number(production.get("completed_units"))
    first_pass_good_units = _number(production.get("first_pass_good_units"))
    planned_minutes = _number(production.get("planned_production_minutes"))
    runtime_minutes = _number(production.get("runtime_minutes"))
    ideal_cycle_seconds = _number(production.get("ideal_cycle_seconds"))

    availability = _percent(runtime_minutes, planned_minutes)
    performance = None
    if completed_units is not None and ideal_cycle_seconds is not None and runtime_minutes:
        performance = min(100.0, round(completed_units * ideal_cycle_seconds / (runtime_minutes * 60) * 100, 1))
    first_pass_yield = _percent(first_pass_good_units, completed_units)
    oee = None
    if availability is not None and performance is not None and first_pass_yield is not None:
        oee = round(availability * performance * first_pass_yield / 10_000, 1)

    late_orders = [item for item in orders if _number(item.get("late_minutes")) and _number(item.get("late_minutes")) > 0]
    shortage_items = [
        item for item in inventory
        if "短缺" in str(item.get("status") or "")
        or ((_number(item.get("available")) or _number(item.get("on_hand")) or 0)
            < (_number(item.get("required")) or 0))
    ]
    setup_minutes = sum(int(_number(item.get("setup_minutes")) or 0) for item in operations)
    downtime_minutes = sum(_minutes_between(item.get("start"), item.get("end")) for item in downtimes)
    on_time_rate = _percent(len(orders) - len(late_orders), len(orders))

    return {
        "plan_attainment": _metric(
            "生產計畫達成率", _percent(completed_units, planned_units), "%",
            "MES 完成數量 ÷ MES 計畫數量", [ref("factory-mes-mcp", "S3")],
            note="MES 未提供當日實績時不計算。",
        ),
        "first_pass_yield": _metric(
            "一次通過率 FPY", first_pass_yield, "%",
            "MES 一次合格數量 ÷ MES 完成數量", [ref("factory-mes-mcp", "S3"), ref("qms-demo-mcp", "S4")],
            note="QMS 產品家族資料用於交叉核對。",
        ),
        "oee": _metric(
            "設備綜合效率 OEE", oee, "%",
            "可用率 × 效能率 × 一次通過率", [ref("factory-mes-mcp", "S3"), ref("cmms-demo-mcp", "S5")],
            note="以 MES 原始時間與產量計算；CMMS 用於設備事件佐證。",
        ),
        "predicted_on_time": _metric(
            "預測準交率", on_time_rate, "%",
            "預測準時訂單數 ÷ 排程訂單數", [ref("odoo-orders-mcp", "S1"), ref("scheduler", "S9")],
            note="這是有限產能排程預測，不是已出貨準交率。",
        ),
        "late_orders": _metric(
            "預計延期訂單", len(late_orders), " 筆",
            "預測完成時間晚於需求交期", [ref("odoo-orders-mcp", "S1"), ref("scheduler", "S9")], precision=0,
        ),
        "shortage_items": _metric(
            "缺料項目", len(shortage_items), " 項",
            "需求數量大於可用庫存", [ref("odoo-stock-mcp", "S2"), ref("wms-demo-mcp", "S6")], precision=0,
        ),
        "setup_minutes": _metric(
            "排程換線時間", setup_minutes, " 分鐘",
            "排程工序 setup_minutes 合計", [ref("factory-mes-mcp", "S3"), ref("scheduler", "S9")], precision=0,
        ),
        "downtime_minutes": _metric(
            "停機與保養時間", downtime_minutes, " 分鐘",
            "MES 停機與 CMMS 維護窗口分鐘數合計", [ref("factory-mes-mcp", "S3"), ref("cmms-demo-mcp", "S5")], precision=0,
        ),
    }


def build_daily_report(schedule: dict[str, Any], *, generated_by: str, report_date: date | None = None) -> dict[str, Any]:
    if not isinstance(schedule, dict) or not isinstance(schedule.get("orders"), list):
        raise ProductionReportError("排程結果不完整，無法建立生產日報")
    report_day = report_date or datetime.now(REPORT_TIMEZONE).date()
    sources = _source_catalog(schedule)
    source_refs = {item["id"]: item["ref"] for item in sources}
    kpis = calculate_fixed_kpis(schedule)
    orders = [item for item in schedule.get("orders") or [] if isinstance(item, dict)]
    risks = []
    for order in orders:
        if (_number(order.get("late_minutes")) or 0) <= 0 and str(order.get("risk_level")) != "high":
            continue
        risks.append({
            "order": str(order.get("order") or "-"),
            "customer": str(order.get("customer") or "-"),
            "product": str(order.get("product") or "-"),
            "due_at": order.get("due_at"),
            "predicted_completion_at": order.get("predicted_completion_at"),
            "late_minutes": int(_number(order.get("late_minutes")) or 0),
            "risk_probability": int(_number(order.get("risk_probability")) or 0),
            "reasons": [str(item) for item in order.get("reasons") or []],
            "sources": [source_refs.get("odoo-orders-mcp", "S1"), source_refs.get("scheduler", "S9")],
        })
    shortages = [
        {
            "item": str(item.get("item") or "-"),
            "on_hand": item.get("on_hand"),
            "available": item.get("available"),
            "required": item.get("required"),
            "status": str(item.get("status") or ""),
            "sources": [source_refs.get("odoo-stock-mcp", "S2"), source_refs.get("wms-demo-mcp", "S6")],
        }
        for item in schedule.get("inventory") or []
        if isinstance(item, dict) and "短缺" in str(item.get("status") or "")
    ]
    quality_events = [item for item in (schedule.get("qms_snapshot") or {}).get("open_events") or [] if isinstance(item, dict)]
    equipment_risks = [
        item for item in (schedule.get("cmms_snapshot") or {}).get("assets") or []
        if isinstance(item, dict) and str(item.get("health") or "normal") != "normal"
    ]
    status = "attention" if risks or shortages or quality_events or equipment_risks else "normal"
    summary = [
        f"本次納入 {len(orders)} 筆訂單，預測準交率 {kpis['predicted_on_time']['display']}。",
        f"目前有 {len(risks)} 筆交期風險、{len(shortages)} 項缺料、{len(quality_events)} 筆未結品質事件。",
        f"設備側有 {len(equipment_risks)} 台需關注，排程內停機與保養時間合計 {kpis['downtime_minutes']['display']}。",
    ]
    return {
        "schema_version": "daily-production-report-v1",
        "report_date": report_day.isoformat(),
        "generated_at": datetime.now(REPORT_TIMEZONE).isoformat(timespec="seconds"),
        "generated_by": generated_by,
        "plant": str((schedule.get("mes_snapshot") or {}).get("plant") or "unknown"),
        "status": status,
        "data_mode": str(schedule.get("data_mode") or "mcp"),
        "snapshot_at": schedule.get("snapshot_at"),
        "executive_summary": summary,
        "kpis": kpis,
        "delivery_risks": risks,
        "material_shortages": shortages,
        "quality_events": quality_events,
        "equipment_risks": equipment_risks,
        "sources": sources,
        "tool_trace": schedule.get("trace") or [],
        "data_warnings": schedule.get("integration_warnings") or [],
        "schedule_engine": schedule.get("engine") or {},
    }


class _PdfWriter:
    def __init__(self) -> None:
        self.document = pymupdf.open()
        self.font_path = resolve_pdf_font()
        self.font = pymupdf.Font(fontfile=str(self.font_path))
        self.font_name = "reportfont"
        self.page: pymupdf.Page | None = None
        self.y = 0.0
        self.margin = 42.0
        self.page_width = 595.0
        self.page_height = 842.0
        self.new_page()

    def new_page(self) -> None:
        self.page = self.document.new_page(width=self.page_width, height=self.page_height)
        self.page.insert_font(fontname=self.font_name, fontfile=str(self.font_path))
        self.y = self.margin
        self.page.draw_rect((0, 0, self.page_width, 14), color=(0.05, 0.48, 0.73), fill=(0.05, 0.48, 0.73))
        self.page.insert_text((self.margin, self.page_height - 22), "AI Work NAS · Daily Production Report", fontsize=7, fontname="helv", color=(0.35, 0.45, 0.55))

    def ensure(self, height: float) -> None:
        if self.y + height > self.page_height - 40:
            self.new_page()

    def _lines(self, text: str, width: float, size: float) -> list[str]:
        result: list[str] = []
        for paragraph in str(text).splitlines() or [""]:
            line = ""
            for char in paragraph:
                candidate = line + char
                if line and self.font.text_length(candidate, fontsize=size) > width:
                    result.append(line)
                    line = char
                else:
                    line = candidate
            result.append(line)
        return result or [""]

    def text(self, value: str, *, size: float = 10, color=(0.08, 0.18, 0.28), width: float | None = None, leading: float = 1.35, gap: float = 4) -> None:
        available = width or self.page_width - self.margin * 2
        lines = self._lines(value, available, size)
        height = len(lines) * size * leading
        self.ensure(height + gap)
        assert self.page is not None
        for line in lines:
            self.page.insert_text((self.margin, self.y + size), line, fontsize=size, fontname=self.font_name, color=color)
            self.y += size * leading
        self.y += gap

    def heading(self, value: str, *, size: float = 16) -> None:
        self.ensure(size * 2)
        self.text(value, size=size, color=(0.04, 0.32, 0.55), gap=8)

    def rule(self) -> None:
        self.ensure(10)
        assert self.page is not None
        self.page.draw_line((self.margin, self.y), (self.page_width - self.margin, self.y), color=(0.78, 0.86, 0.91), width=0.8)
        self.y += 10

    def table(self, headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
        def row(values: list[str], fill, text_color, size: float) -> None:
            line_sets = [self._lines(value, width - 10, size)[:3] for value, width in zip(values, widths)]
            height = max(22, max(len(lines) for lines in line_sets) * size * 1.25 + 10)
            self.ensure(height + 1)
            assert self.page is not None
            x = self.margin
            for lines, width in zip(line_sets, widths):
                self.page.draw_rect((x, self.y, x + width, self.y + height), color=(0.80, 0.87, 0.91), fill=fill, width=0.5)
                yy = self.y + 7 + size
                for line in lines:
                    self.page.insert_text((x + 5, yy), line, fontsize=size, fontname=self.font_name, color=text_color)
                    yy += size * 1.25
                x += width
            self.y += height
        row(headers, (0.91, 0.96, 0.99), (0.04, 0.30, 0.50), 8.5)
        for values in rows:
            row(values, (1, 1, 1), (0.10, 0.19, 0.27), 8)
        self.y += 8


def render_report_pdf(report: dict[str, Any], destination: Path) -> None:
    writer = _PdfWriter()
    report_title = str(report.get("report_title") or "每日生產報告")
    writer.text(report_title, size=24, color=(0.03, 0.25, 0.43), gap=2)
    writer.text(
        f"報告日期：{report['report_date']}　廠區：{report['plant']}　資料截止：{report.get('snapshot_at') or '-'}　產生時間：{report.get('generated_at') or '-'}",
        size=9, color=(0.35, 0.45, 0.55), gap=12,
    )
    writer.heading("管理摘要")
    for item in report["executive_summary"]:
        writer.text(f"• {item}", size=10)
    writer.rule()
    writer.heading("固定 KPI")
    rows = []
    for metric in report["kpis"].values():
        rows.append([metric["label"], metric["display"], metric["formula"], "、".join(metric["sources"])])
    writer.table(["指標", "結果", "固定公式", "來源"], rows, [100, 75, 245, 85])

    writer.heading("交期風險")
    risk_rows = [
        [item["order"], item["customer"], item["product"], str(item["late_minutes"]), "；".join(item["reasons"]), "、".join(item["sources"])]
        for item in report["delivery_risks"]
    ]
    if risk_rows:
        writer.table(["訂單", "客戶", "產品", "延遲分鐘", "原因", "來源"], risk_rows, [60, 70, 80, 55, 190, 50])
    else:
        writer.text("目前排程未發現預計延期訂單。")

    writer.heading("缺料、品質與設備")
    writer.text(f"缺料：{len(report['material_shortages'])} 項；未結品質事件：{len(report['quality_events'])} 筆；設備風險：{len(report['equipment_risks'])} 台。")
    for item in report["material_shortages"]:
        writer.text(f"• 缺料 {item['item']}：{item['status']} [{'/'.join(item['sources'])}]", size=9)
    for item in report["quality_events"]:
        writer.text(f"• 品質 {item.get('event_id', '-')}：{item.get('summary', '-')} [S4]", size=9)
    for item in report["equipment_risks"]:
        writer.text(f"• 設備 {item.get('center_id', '-')}：{item.get('reason', '-')} [S5]", size=9)

    alerts = report.get("alerts") or []
    if alerts:
        writer.heading("管理告警")
        alert_rows = [
            [item["label"], item["actual_display"], item["rule_display"], item["severity"], "、".join(item["sources"])]
            for item in alerts
        ]
        writer.table(["告警欄位", "實際值", "門檻", "等級", "來源"], alert_rows, [120, 90, 120, 75, 100])

    writer.new_page()
    writer.heading("資料來源與工具軌跡")
    source_rows = [[item["ref"], item["name"], item["detail"]] for item in report["sources"]]
    writer.table(["引用", "資料來源", "範圍"], source_rows, [45, 190, 270])
    for trace in report["tool_trace"]:
        if not isinstance(trace, dict):
            continue
        writer.text(
            f"• {trace.get('server', 'Local')} / {trace.get('tool', '-')} · {trace.get('status', 'completed')} · {trace.get('result', '')}",
            size=8, color=(0.32, 0.42, 0.50), gap=2,
        )
    writer.text("說明：報表 KPI 由固定公式計算；LLM 不參與關鍵數字計算。本報告為管理決策支援，不取代 ERP／MES 正式帳務與生產紀錄。", size=8, color=(0.35, 0.45, 0.55), gap=0)
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer.document.set_metadata({"title": f"{report_title} {report['report_date']}", "author": "AI Work NAS"})
    for index, page in enumerate(writer.document, start=1):
        page.insert_text(
            (writer.page_width - writer.margin - 42, writer.page_height - 22),
            f"{index} / {len(writer.document)}", fontsize=7, fontname=writer.font_name,
            color=(0.35, 0.45, 0.55),
        )
    writer.document.subset_fonts()
    writer.document.save(destination, garbage=4, deflate=True)
    writer.document.close()


def generate_and_store_report(schedule: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
    report_day = datetime.now(REPORT_TIMEZONE).date()
    plant = str((schedule.get("mes_snapshot") or {}).get("plant") or "unknown")
    record, claimed = claim_daily_production_report(
        user_id=int(user["id"]), report_date=report_day.isoformat(), plant=plant,
    )
    if not claimed:
        if record.get("status") == "completed":
            record["report"] = load_report_payload(record)
        return record
    report_dir = REPORTS_DIR / report_day.strftime("%Y/%m") / f"report-{record['id']:06d}"
    snapshot_path = report_dir / "snapshot.json"
    pdf_path = report_dir / f"daily-production-report-{report_day.isoformat()}.pdf"
    try:
        report = build_daily_report(schedule, generated_by=str(user.get("username") or user["id"]), report_date=report_day)
        snapshot = {"report": report, "schedule_snapshot": schedule}
        report_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        render_report_pdf(report, pdf_path)

        snapshot_asset = create_nas_asset(
            user_id=int(user["id"]), category="document", title=f"每日生產報告資料快照 {report_day}",
            original_filename=f"daily-production-report-{report_day}-snapshot.json",
            stored_path=str(snapshot_path), mime_type="application/json", file_size=snapshot_path.stat().st_size,
            status="processing", analyzer="daily_production_report", source_type="generated",
            content_sha256=hashlib.sha256(snapshot_path.read_bytes()).hexdigest(), scan_status="clean", scan_engine="internal-generated",
        )
        update_nas_asset(
            int(snapshot_asset["id"]), status="completed", analyzer="daily_production_report",
            summary="每日生產報告使用的不可變 MCP 資料快照與工具軌跡。",
        )
        pdf_asset = create_nas_asset(
            user_id=int(user["id"]), category="document", title=f"每日生產報告 {report_day}",
            original_filename=pdf_path.name, stored_path=str(pdf_path), mime_type="application/pdf",
            file_size=pdf_path.stat().st_size, status="processing", analyzer="daily_production_report",
            source_type="generated", content_sha256=hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
            scan_status="clean", scan_engine="internal-generated",
        )
        update_nas_asset(
            int(pdf_asset["id"]), status="completed", analyzer="daily_production_report",
            summary="由 Odoo、MES、QMS、CMMS 等唯讀 MCP 資料產生，含固定 KPI 與來源引用。",
        )
        complete_production_report(
            int(record["id"]), snapshot_path=str(snapshot_path), pdf_path=str(pdf_path),
            snapshot_asset_id=int(snapshot_asset["id"]), pdf_asset_id=int(pdf_asset["id"]),
            kpis_json=json.dumps(report["kpis"], ensure_ascii=False), source_count=len(report["sources"]),
        )
    except Exception as exc:
        fail_production_report(int(record["id"]), str(exc)[:1000])
        raise
    completed = get_production_report(int(record["id"]), user_id=int(user["id"]), role=str(user["role"]))
    if completed is None:
        raise ProductionReportError("日報已產生但無法讀取記錄")
    completed["report"] = report
    return completed


def load_report_payload(record: dict[str, Any]) -> dict[str, Any]:
    raw_path = Path(str(record.get("snapshot_path") or ""))
    try:
        resolved = raw_path.resolve(strict=True)
        resolved.relative_to(REPORTS_DIR.resolve())
    except (FileNotFoundError, ValueError) as exc:
        raise ProductionReportError("日報資料快照不存在或路徑無效") from exc
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductionReportError("日報資料快照無法讀取") from exc
    report = payload.get("report") if isinstance(payload, dict) else None
    if not isinstance(report, dict):
        raise ProductionReportError("日報資料快照格式錯誤")
    return report


def report_record_for_api(record: dict[str, Any], *, include_report: bool = False) -> dict[str, Any]:
    result = {key: value for key, value in record.items() if key not in {"snapshot_path", "pdf_path"}}
    result["download_url"] = f"/api/daily-production-reports/{record['id']}/download" if record.get("status") == "completed" else None
    if include_report and "report" not in result:
        result["report"] = load_report_payload(record)
    return result
