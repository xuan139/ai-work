from __future__ import annotations

import os
from typing import Any

from app.db import get_system_setting, set_system_setting
from app.llm_catalog import get_model


CURRENT_LLM_SETTING = "current_llm_model_id"
DEFAULT_LLM_MODEL_ID = "local:qwen3-4b"


def default_llm_model_id() -> str:
    return os.getenv("AI_WORK_DEFAULT_LLM_MODEL_ID", DEFAULT_LLM_MODEL_ID).strip() or DEFAULT_LLM_MODEL_ID


def current_llm_model() -> dict[str, Any]:
    setting = get_system_setting(CURRENT_LLM_SETTING)
    default_model_id = default_llm_model_id()
    model = get_model(str((setting or {}).get("value") or default_model_id))
    if model:
        return model
    fallback = get_model(default_model_id) or get_model(DEFAULT_LLM_MODEL_ID)
    if not fallback:
        raise RuntimeError("The default system LLM is unavailable")
    return fallback


def current_llm_state() -> dict[str, Any]:
    setting = get_system_setting(CURRENT_LLM_SETTING)
    model = current_llm_model()
    return {
        "model": model,
        "updated_at": (setting or {}).get("updated_at"),
        "updated_by": (setting or {}).get("updated_by_username"),
        "is_default": setting is None,
    }


def update_current_llm(model_id: str, user_id: int) -> dict[str, Any]:
    model = get_model(model_id.strip())
    if not model:
        raise ValueError("Model not found")
    set_system_setting(CURRENT_LLM_SETTING, model["id"], user_id)
    return current_llm_state()
