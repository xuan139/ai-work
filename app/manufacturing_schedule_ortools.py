from __future__ import annotations

import copy
import math
import time
from datetime import datetime, timedelta
from typing import Any

from app.manufacturing_schedule_demo import score_scheduled_order
from app.scheduling_engine import ORTOOLS_ENGINE_ID, RULE_ENGINE_ID

try:
    from ortools.sat.python import cp_model
except ImportError:  # Optional dependency: the rule engine remains the fallback.
    cp_model = None


class OrToolsScheduleError(RuntimeError):
    pass


PRIORITY_WEIGHT = {"urgent": 8, "high": 4, "normal": 1}


def ortools_available() -> bool:
    return cp_model is not None


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="minutes")


def _minute(snapshot_at: datetime, value: str) -> int:
    return max(0, math.ceil((_parse(value) - snapshot_at).total_seconds() / 60))


def _merged_ranges(ranges: list[tuple[int, int]], horizon: int) -> list[tuple[int, int]]:
    clipped = sorted((max(0, start), min(horizon, end)) for start, end in ranges if end > 0 and start < horizon)
    merged: list[list[int]] = []
    for start, end in clipped:
        if start >= end:
            continue
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def _off_shift_ranges(snapshot_at: datetime, horizon: int) -> list[tuple[int, int]]:
    windows = []
    day = snapshot_at.date()
    final = snapshot_at + timedelta(minutes=horizon)
    while datetime.combine(day, datetime.min.time()) <= final:
        if day.weekday() < 5:
            start = datetime.combine(day, datetime.min.time()).replace(hour=8)
            end = start.replace(hour=17)
            windows.append((max(0, math.ceil((start - snapshot_at).total_seconds() / 60)),
                            min(horizon, math.floor((end - snapshot_at).total_seconds() / 60))))
        day += timedelta(days=1)
    ranges = []
    cursor = 0
    for start, end in windows:
        if end <= 0 or start >= horizon:
            continue
        if cursor < start:
            ranges.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < horizon:
        ranges.append((cursor, horizon))
    return ranges


def _operation_components(order: dict[str, Any], center: dict[str, Any]) -> dict[str, int]:
    process = math.ceil(float(order["quantity"]) / float(center["units_per_hour"]) * 60)
    quality_rework = int(order.get("quality_rework_minutes") or 0) if center["id"] == "TEST-01" else 0
    plm_operation = int(order.get("plm_extra_operation_minutes") or 0) if center["id"] == "SMT-01" else 0
    spc = order.get("spc") or {}
    spc_inspection = int(order.get("spc_inspection_minutes") or 0) if center["id"] == spc.get("center_id") else 0
    plm_setup = int(order.get("plm_extra_setup_minutes") or 0) if center["id"] == "SMT-01" else 0
    return {
        "process": process + quality_rework + plm_operation + spc_inspection,
        "quality_rework": quality_rework,
        "plm_operation": plm_operation,
        "spc_inspection": spc_inspection,
        "plm_setup": plm_setup,
    }


def _summary(schedule: dict[str, Any]) -> dict[str, int]:
    orders = schedule["orders"]
    operations = schedule["operations"]
    weights = PRIORITY_WEIGHT
    return {
        "late_minutes": sum(int(item["late_minutes"]) for item in orders),
        "weighted_late_minutes": sum(int(item["late_minutes"]) * weights[item["priority"]] for item in orders),
        "changeover_minutes": sum(int(item.get("family_setup_minutes") or 0) for item in operations),
        "setup_minutes": sum(int(item.get("setup_minutes") or 0) for item in operations),
        "makespan_minutes": math.ceil(
            (_parse(schedule["summary"]["latest_completion_at"]) - _parse(schedule["snapshot_at"])).total_seconds() / 60
        ),
    }


def run_ortools_schedule(rule_schedule: dict[str, Any], *, timeout_seconds: float = 3.0) -> dict[str, Any]:
    if cp_model is None:
        raise OrToolsScheduleError("OR-Tools 尚未安裝")
    snapshot_at = _parse(rule_schedule["snapshot_at"])
    orders = [copy.deepcopy(item) for item in rule_schedule["orders"]]
    centers = [copy.deepcopy(item) for item in rule_schedule["work_centers"]]
    scenario = copy.deepcopy(rule_schedule["scenario"])
    max_input_minute = max(
        [_minute(snapshot_at, item["due_at"]) for item in orders]
        + [_minute(snapshot_at, item["material_ready_at"]) for item in orders]
        + [0]
    )
    horizon = max(45 * 24 * 60, max_input_minute + 14 * 24 * 60)
    model = cp_model.CpModel()
    variables: dict[tuple[int, str], dict[str, Any]] = {}
    intervals_by_center: dict[str, list[Any]] = {str(center["id"]): [] for center in centers}

    for order_index, order in enumerate(orders):
        previous_end = None
        for center in centers:
            center_id = str(center["id"])
            components = _operation_components(order, center)
            max_setup = components["plm_setup"] + int(center["setup_minutes"])
            start = model.new_int_var(0, horizon, f"start_{order_index}_{center_id}")
            end = model.new_int_var(0, horizon, f"end_{order_index}_{center_id}")
            setup = model.new_int_var(components["plm_setup"], max_setup, f"setup_{order_index}_{center_id}")
            size = model.new_int_var(components["process"] + components["plm_setup"],
                                     components["process"] + max_setup, f"size_{order_index}_{center_id}")
            model.add(size == components["process"] + setup)
            interval = model.new_interval_var(start, size, end, f"operation_{order_index}_{center_id}")
            variables[(order_index, center_id)] = {
                "start": start, "end": end, "setup": setup, "size": size,
                "interval": interval, "components": components,
            }
            intervals_by_center[center_id].append(interval)
            if previous_end is None:
                model.add(start >= _minute(snapshot_at, order["material_ready_at"]))
            else:
                model.add(start >= previous_end)
            previous_end = end

    changeover_terms = []
    for center in centers:
        center_id = str(center["id"])
        arcs = []
        incoming_changed: dict[int, list[Any]] = {index: [] for index in range(len(orders))}
        for index in range(len(orders)):
            first = model.new_bool_var(f"first_{center_id}_{index}")
            last = model.new_bool_var(f"last_{center_id}_{index}")
            arcs.extend(((0, index + 1, first), (index + 1, 0, last)))
        for left in range(len(orders)):
            for right in range(len(orders)):
                if left == right:
                    continue
                arc = model.new_bool_var(f"arc_{center_id}_{left}_{right}")
                arcs.append((left + 1, right + 1, arc))
                model.add(variables[(right, center_id)]["start"] >= variables[(left, center_id)]["end"]).only_enforce_if(arc)
                if orders[left]["family"] != orders[right]["family"]:
                    incoming_changed[right].append(arc)
                    changeover_terms.append(arc * int(center["setup_minutes"]))
        model.add_circuit(arcs)
        for index in range(len(orders)):
            fixed_setup = variables[(index, center_id)]["components"]["plm_setup"]
            changed = incoming_changed[index]
            model.add(variables[(index, center_id)]["setup"] == fixed_setup + int(center["setup_minutes"]) * sum(changed))

        blocked = _off_shift_ranges(snapshot_at, horizon)
        blocked.extend(
            (_minute(snapshot_at, item["start"]), _minute(snapshot_at, item["end"]))
            for item in rule_schedule["downtimes"] if item["center_id"] == center_id
        )
        fixed_intervals = []
        for block_index, (start, end) in enumerate(_merged_ranges(blocked, horizon)):
            fixed_intervals.append(model.new_fixed_size_interval_var(start, end - start, f"blocked_{center_id}_{block_index}"))
        model.add_no_overlap(intervals_by_center[center_id] + fixed_intervals)

    late_vars = []
    weighted_late_terms = []
    final_ends = []
    last_center_id = str(centers[-1]["id"])
    for index, order in enumerate(orders):
        finish = variables[(index, last_center_id)]["end"]
        late = model.new_int_var(0, horizon, f"late_{index}")
        model.add(late >= finish - _minute(snapshot_at, order["due_at"]))
        late_vars.append(late)
        weighted_late_terms.append(late * PRIORITY_WEIGHT[order["priority"]])
        final_ends.append(finish)
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, final_ends)
    model.minimize(sum(weighted_late_terms) * 100 + sum(changeover_terms) * 10 + makespan)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    started = time.perf_counter()
    status = solver.solve(model)
    solve_ms = round((time.perf_counter() - started) * 1000)
    status_name = solver.status_name(status)
    if status not in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
        raise OrToolsScheduleError(f"CP-SAT 沒有找到可行排程：{status_name}")

    operations = []
    scheduled = []
    for order_index, order in enumerate(orders):
        order_operations = []
        for sequence, center in enumerate(centers, start=1):
            center_id = str(center["id"])
            variable = variables[(order_index, center_id)]
            components = variable["components"]
            setup = solver.value(variable["setup"])
            family_setup = setup - components["plm_setup"]
            operation = {
                "order": order["order"], "product": order["product"], "family": order["family"],
                "sequence": sequence, "center_id": center_id, "center": center["name"],
                "start_at": _iso(snapshot_at + timedelta(minutes=solver.value(variable["start"]))),
                "end_at": _iso(snapshot_at + timedelta(minutes=solver.value(variable["end"]))),
                "process_minutes": components["process"], "setup_minutes": setup,
                "family_setup_minutes": family_setup, "plm_setup_minutes": components["plm_setup"],
                "quality_rework_minutes": components["quality_rework"],
                "plm_operation_minutes": components["plm_operation"],
                "spc_inspection_minutes": components["spc_inspection"],
                "duration_minutes": solver.value(variable["size"]),
            }
            operations.append(operation)
            order_operations.append(operation)
        clean_order = {key: value for key, value in order.items() if key not in {
            "predicted_completion_at", "late_minutes", "risk_probability", "risk_level", "reasons", "operations"
        }}
        scheduled.append(score_scheduled_order(
            clean_order, order_operations, snapshot_at=snapshot_at, scenario=scenario,
        ))

    result = copy.deepcopy(rule_schedule)
    operations.sort(key=lambda item: (item["start_at"], item["center_id"]))
    scheduled.sort(key=lambda item: item["order"])
    late_count = sum(item["late_minutes"] > 0 for item in scheduled)
    result.update({
        "engine": {
            "name": "Google OR-Tools CP-SAT",
            "version": ORTOOLS_ENGINE_ID,
            "note": "以整數約束最佳化加權延期、換線與完工時間；LLM 不參與排程計算。",
            "solver_status": status_name,
            "solve_time_ms": solve_ms,
            "objective_value": round(solver.objective_value),
        },
        "orders": scheduled,
        "operations": operations,
        "summary": {
            "order_count": len(scheduled), "late_count": late_count,
            "on_time_count": len(scheduled) - late_count,
            "high_risk_count": sum(item["risk_level"] == "high" for item in scheduled),
            "setup_count": sum(item["family_setup_minutes"] > 0 for item in operations),
            "latest_completion_at": max(item["predicted_completion_at"] for item in scheduled),
        },
    })
    result["sources"] = [
        ({**item, "name": "OR-Tools CP-SAT 排程引擎", "detail": f"{ORTOOLS_ENGINE_ID} · {status_name}"}
         if item.get("id") == "scheduler" else item)
        for item in result["sources"]
    ]
    result["trace"] = [
        item for item in result["trace"] if item.get("tool") != "schedule.run_finite_capacity"
    ] + [{
        "kind": "local", "tool": "schedule.solve_cp_sat", "arguments": scenario,
        "status": status_name, "duration_ms": solve_ms,
        "result": f"{len(operations)} operations, {late_count} late orders",
    }]
    result["optimization_metrics"] = _summary(result)
    return result


def compare_schedules(rule_schedule: dict[str, Any], default_engine: str) -> dict[str, Any]:
    rule = copy.deepcopy(rule_schedule)
    rule["optimization_metrics"] = _summary(rule)
    optimized = None
    error = None
    try:
        optimized = run_ortools_schedule(rule)
    except OrToolsScheduleError as exc:
        error = str(exc)

    active_engine = default_engine if default_engine == ORTOOLS_ENGINE_ID and optimized else RULE_ENGINE_ID
    active = copy.deepcopy(optimized if active_engine == ORTOOLS_ENGINE_ID else rule)
    rule_metrics = rule["optimization_metrics"]
    optimized_metrics = optimized["optimization_metrics"] if optimized else None
    comparison = {
        "default_engine": default_engine,
        "active_engine": active_engine,
        "fallback_used": default_engine == ORTOOLS_ENGINE_ID and optimized is None,
        "ortools_available": optimized is not None,
        "ortools_error": error,
        "rule": rule,
        "ortools": optimized,
        "metrics": {"rule": rule_metrics, "ortools": optimized_metrics},
        "delay_improved": bool(optimized_metrics and optimized_metrics["weighted_late_minutes"] < rule_metrics["weighted_late_minutes"]),
        "changeover_improved": bool(optimized_metrics and optimized_metrics["changeover_minutes"] < rule_metrics["changeover_minutes"]),
    }
    comparison["validated_better"] = bool(
        optimized_metrics
        and optimized_metrics["weighted_late_minutes"] <= rule_metrics["weighted_late_minutes"]
        and optimized_metrics["changeover_minutes"] <= rule_metrics["changeover_minutes"]
        and (comparison["delay_improved"] or comparison["changeover_improved"])
    )
    comparison["delta"] = {
        "weighted_late_minutes_reduced": (
            rule_metrics["weighted_late_minutes"] - optimized_metrics["weighted_late_minutes"]
            if optimized_metrics else None
        ),
        "changeover_minutes_reduced": (
            rule_metrics["changeover_minutes"] - optimized_metrics["changeover_minutes"]
            if optimized_metrics else None
        ),
        "makespan_minutes_reduced": (
            rule_metrics["makespan_minutes"] - optimized_metrics["makespan_minutes"]
            if optimized_metrics else None
        ),
    }
    comparison["verdict"] = (
        "ortools_validated_better" if comparison["validated_better"]
        else "ortools_unavailable" if not optimized_metrics
        else "no_pareto_improvement"
    )
    active["engine_comparison"] = comparison
    return active
