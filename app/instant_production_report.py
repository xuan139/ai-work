from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.daily_production_report import (
    REPORTS_DIR,
    REPORT_TIMEZONE,
    ProductionReportError,
    build_daily_report,
    render_report_pdf,
)
from app.db import (
    complete_instant_production_report,
    create_instant_production_report,
    create_nas_asset,
    fail_instant_production_report,
    get_instant_production_report,
    list_instant_report_questions,
    update_nas_asset,
)


DEFAULT_ALERT_RULES: dict[str, float] = {
    "plan_attainment_min": 90.0,
    "first_pass_yield_min": 95.0,
    "oee_min": 75.0,
    "predicted_on_time_min": 95.0,
    "late_orders_max": 0.0,
    "shortage_items_max": 0.0,
    "downtime_minutes_max": 60.0,
}

ALERT_RULE_FIELDS: dict[str, dict[str, str]] = {
    "plan_attainment_min": {"metric": "plan_attainment", "operator": "min", "label": "生產計畫達成率"},
    "first_pass_yield_min": {"metric": "first_pass_yield", "operator": "min", "label": "一次通過率 FPY"},
    "oee_min": {"metric": "oee", "operator": "min", "label": "設備綜合效率 OEE"},
    "predicted_on_time_min": {"metric": "predicted_on_time", "operator": "min", "label": "預測準交率"},
    "late_orders_max": {"metric": "late_orders", "operator": "max", "label": "預計延期訂單"},
    "shortage_items_max": {"metric": "shortage_items", "operator": "max", "label": "缺料項目"},
    "downtime_minutes_max": {"metric": "downtime_minutes", "operator": "max", "label": "停機與保養時間"},
}


def normalize_alert_rules(raw: Any) -> dict[str, float]:
    if raw is None:
        return dict(DEFAULT_ALERT_RULES)
    if not isinstance(raw, dict):
        raise ProductionReportError("告警設定必須是 JSON object")
    unknown = set(raw) - set(DEFAULT_ALERT_RULES)
    if unknown:
        raise ProductionReportError(f"不支援的告警欄位：{', '.join(sorted(unknown))}")
    rules = dict(DEFAULT_ALERT_RULES)
    for key, value in raw.items():
        if isinstance(value, bool):
            raise ProductionReportError(f"告警門檻 {key} 必須是數字")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ProductionReportError(f"告警門檻 {key} 必須是數字") from exc
        maximum = 100.0 if key.endswith("_min") else 100_000.0
        if not 0 <= number <= maximum:
            raise ProductionReportError(f"告警門檻 {key} 必須介於 0 與 {maximum:g} 之間")
        rules[key] = number
    return rules


def evaluate_alerts(report: dict[str, Any], rules: dict[str, float]) -> list[dict[str, Any]]:
    alerts = []
    for rule_key, threshold in rules.items():
        definition = ALERT_RULE_FIELDS[rule_key]
        metric = (report.get("kpis") or {}).get(definition["metric"]) or {}
        actual = metric.get("value")
        if not isinstance(actual, (int, float)) or isinstance(actual, bool):
            continue
        triggered = actual < threshold if definition["operator"] == "min" else actual > threshold
        if not triggered:
            continue
        comparison = "低於" if definition["operator"] == "min" else "高於"
        unit = str(metric.get("unit") or "")
        severity = "critical" if rule_key in {"predicted_on_time_min", "late_orders_max", "shortage_items_max"} else "warning"
        alerts.append({
            "field": rule_key,
            "metric": definition["metric"],
            "label": definition["label"],
            "operator": definition["operator"],
            "threshold": threshold,
            "actual": actual,
            "unit": unit,
            "actual_display": str(metric.get("display") or actual),
            "rule_display": f"{comparison} {threshold:g}{unit}",
            "severity": severity,
            "message": f"{definition['label']} {metric.get('display')}，{comparison}告警門檻 {threshold:g}{unit}。",
            "sources": list(metric.get("sources") or []),
        })
    return alerts


def build_instant_report(
    schedule: dict[str, Any], *, generated_by: str, alert_rules: dict[str, float],
) -> dict[str, Any]:
    report = build_daily_report(schedule, generated_by=generated_by)
    report.update({
        "schema_version": "instant-production-report-v1",
        "report_title": "即時生產報告",
        "report_type": "instant",
        "alert_rules": alert_rules,
    })
    report["alerts"] = evaluate_alerts(report, alert_rules)
    report["status"] = "attention" if report["alerts"] else "normal"
    return report


def generate_and_store_instant_report(
    schedule: dict[str, Any], user: dict[str, Any], alert_rules: Any = None,
) -> dict[str, Any]:
    rules = normalize_alert_rules(alert_rules)
    now = datetime.now(REPORT_TIMEZONE)
    plant = str((schedule.get("mes_snapshot") or {}).get("plant") or "unknown")
    record = create_instant_production_report(user_id=int(user["id"]), plant=plant, alert_rules=rules)
    report_dir = REPORTS_DIR / now.strftime("%Y/%m/%d") / f"instant-{record['id']:06d}"
    snapshot_path = report_dir / "snapshot.json"
    pdf_path = report_dir / f"instant-production-report-{now.strftime('%Y%m%d-%H%M%S')}.pdf"
    try:
        report = build_instant_report(
            schedule, generated_by=str(user.get("username") or user["id"]), alert_rules=rules,
        )
        report["report_id"] = int(record["id"])
        snapshot = {"report": report, "schedule_snapshot": schedule}
        report_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        render_report_pdf(report, pdf_path)

        timestamp_label = now.strftime("%Y-%m-%d %H:%M:%S")
        snapshot_asset = create_nas_asset(
            user_id=int(user["id"]), category="document", title=f"即時生產報告資料快照 {timestamp_label}",
            original_filename=f"instant-production-report-{now.strftime('%Y%m%d-%H%M%S')}-snapshot.json",
            stored_path=str(snapshot_path), mime_type="application/json", file_size=snapshot_path.stat().st_size,
            status="processing", analyzer="instant_production_report", source_type="generated",
            content_sha256=hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
            scan_status="clean", scan_engine="internal-generated",
        )
        update_nas_asset(
            int(snapshot_asset["id"]), status="completed", analyzer="instant_production_report",
            summary="即時生產報告使用的不可變 MCP 快照、告警規則與工具軌跡。",
        )
        pdf_asset = create_nas_asset(
            user_id=int(user["id"]), category="document", title=f"即時生產報告 {timestamp_label}",
            original_filename=pdf_path.name, stored_path=str(pdf_path), mime_type="application/pdf",
            file_size=pdf_path.stat().st_size, status="processing", analyzer="instant_production_report",
            source_type="generated", content_sha256=hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
            scan_status="clean", scan_engine="internal-generated",
        )
        update_nas_asset(
            int(pdf_asset["id"]), status="completed", analyzer="instant_production_report",
            summary="由唯讀企業 MCP 即時取數，以固定 KPI 與管理告警產生的可追溯 PDF。",
        )
        complete_instant_production_report(
            int(record["id"]), snapshot_path=str(snapshot_path), pdf_path=str(pdf_path),
            snapshot_asset_id=int(snapshot_asset["id"]), pdf_asset_id=int(pdf_asset["id"]),
            kpis=report["kpis"], alerts=report["alerts"], source_count=len(report["sources"]),
        )
    except Exception as exc:
        fail_instant_production_report(int(record["id"]), str(exc)[:1000])
        raise
    completed = get_instant_production_report(
        int(record["id"]), user_id=int(user["id"]), role=str(user["role"]),
    )
    if completed is None:
        raise ProductionReportError("即時報告已產生但無法讀取記錄")
    completed["report"] = report
    return completed


def load_instant_report_payload(record: dict[str, Any]) -> dict[str, Any]:
    raw_path = Path(str(record.get("snapshot_path") or ""))
    try:
        resolved = raw_path.resolve(strict=True)
        resolved.relative_to(REPORTS_DIR.resolve())
    except (FileNotFoundError, ValueError) as exc:
        raise ProductionReportError("即時報告資料快照不存在或路徑無效") from exc
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductionReportError("即時報告資料快照無法讀取") from exc
    report = payload.get("report") if isinstance(payload, dict) else None
    if not isinstance(report, dict):
        raise ProductionReportError("即時報告資料快照格式錯誤")
    return report


def instant_report_record_for_api(record: dict[str, Any], *, include_report: bool = False) -> dict[str, Any]:
    result = {key: value for key, value in record.items() if key not in {"snapshot_path", "pdf_path"}}
    result["download_url"] = (
        f"/api/instant-production-reports/{record['id']}/download"
        if record.get("status") == "completed" else None
    )
    if include_report and "report" not in result:
        result["report"] = load_instant_report_payload(record)
    if include_report:
        result["questions"] = list_instant_report_questions(int(record["id"]))
    return result


def management_context(report: dict[str, Any]) -> str:
    kpis = {
        key: {
            "label": item.get("label"), "display": item.get("display"),
            "formula": item.get("formula"), "sources": item.get("sources"),
        }
        for key, item in (report.get("kpis") or {}).items()
        if isinstance(item, dict)
    }
    payload = {
        "report_id": report.get("report_id"),
        "generated_at": report.get("generated_at"),
        "snapshot_at": report.get("snapshot_at"),
        "plant": report.get("plant"),
        "executive_summary": report.get("executive_summary"),
        "kpis": kpis,
        "alerts": (report.get("alerts") or [])[:10],
        "delivery_risks": (report.get("delivery_risks") or [])[:10],
        "material_shortages": (report.get("material_shortages") or [])[:10],
        "quality_events": (report.get("quality_events") or [])[:5],
        "equipment_risks": (report.get("equipment_risks") or [])[:5],
        "sources": report.get("sources"),
    }
    context = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if len(context) <= 4500:
        return context
    payload["delivery_risks"] = payload["delivery_risks"][:5]
    payload["material_shortages"] = payload["material_shortages"][:5]
    payload["quality_events"] = payload["quality_events"][:3]
    payload["equipment_risks"] = payload["equipment_risks"][:3]
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
