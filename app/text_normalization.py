from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from opencc import OpenCC


SCRIPT_CONFIGS = {
    "traditional": "s2t",
    "simplified": "t2s",
}


def normalize_asr_text(text: str) -> tuple[str, dict[str, Any]]:
    target = os.environ.get("ASR_CHINESE_SCRIPT", "traditional").strip().lower()
    if target in {"", "none", "off", "disabled"}:
        return text, {"target": "none", "converter": None, "changed": False}

    config = SCRIPT_CONFIGS.get(target, SCRIPT_CONFIGS["traditional"])
    normalized = _converter(config).convert(text)
    return normalized, {
        "target": target if target in SCRIPT_CONFIGS else "traditional",
        "converter": f"OpenCC {config}",
        "changed": normalized != text,
    }


def convert_to_traditional(text: str) -> str:
    return _converter(SCRIPT_CONFIGS["traditional"]).convert(text)


@lru_cache(maxsize=len(SCRIPT_CONFIGS))
def _converter(config: str) -> OpenCC:
    return OpenCC(config)
