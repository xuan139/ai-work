from __future__ import annotations

from typing import Any

from app.asr_catalog import DEFAULT_ASR_MODEL_ID, find_asr_model, get_asr_model
from app.db import get_system_setting, set_system_setting


CURRENT_ASR_SETTING = "current_asr_model_id"


def current_asr_model() -> dict[str, Any]:
    setting = get_system_setting(CURRENT_ASR_SETTING)
    return get_asr_model(str((setting or {}).get("value") or DEFAULT_ASR_MODEL_ID))


def current_asr_state() -> dict[str, Any]:
    setting = get_system_setting(CURRENT_ASR_SETTING)
    model = current_asr_model()
    return {
        "model": model,
        "updated_at": (setting or {}).get("updated_at"),
        "updated_by": (setting or {}).get("updated_by_username"),
        "is_default": setting is None,
    }


def update_current_asr(model_id: str, user_id: int) -> dict[str, Any]:
    model = find_asr_model(model_id.strip())
    if not model:
        raise ValueError("ASR model not found")
    set_system_setting(CURRENT_ASR_SETTING, model["id"], user_id)
    return current_asr_state()
