from __future__ import annotations

from typing import Any

from app.db import get_system_setting, set_system_setting


CURRENT_SCHEDULING_ENGINE_SETTING = "current_scheduling_engine_id"
RULE_ENGINE_ID = "finite-capacity-mcp-v4"
ORTOOLS_ENGINE_ID = "ortools-cp-sat-v1"

SCHEDULING_ENGINES = (
    {
        "id": RULE_ENGINE_ID,
        "name": "確定性有限產能規則排程",
        "description": "現有規則式引擎；作為可靠回退。",
    },
    {
        "id": ORTOOLS_ENGINE_ID,
        "name": "Google OR-Tools CP-SAT",
        "description": "以整數約束最佳化延期、換線與完工時間。",
    },
)


def current_scheduling_engine() -> dict[str, Any]:
    setting = get_system_setting(CURRENT_SCHEDULING_ENGINE_SETTING)
    configured = setting["value"] if setting else RULE_ENGINE_ID
    engine = next((item for item in SCHEDULING_ENGINES if item["id"] == configured), SCHEDULING_ENGINES[0])
    return {
        **engine,
        "is_default": setting is None,
        "updated_at": setting.get("updated_at") if setting else None,
        "updated_by": setting.get("updated_by_username") if setting else None,
    }


def update_scheduling_engine(engine_id: str, user_id: int) -> dict[str, Any]:
    if engine_id not in {item["id"] for item in SCHEDULING_ENGINES}:
        raise ValueError("不支援的排程引擎")
    set_system_setting(CURRENT_SCHEDULING_ENGINE_SETTING, engine_id, user_id)
    return current_scheduling_engine()
