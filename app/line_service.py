from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from typing import Any


class LineServiceError(RuntimeError):
    pass


def _config() -> tuple[str, str]:
    base_url = os.getenv("LINE_SERVICE_URL", "http://127.0.0.1:8090").rstrip("/")
    token = os.getenv("LINE_INTEGRATION_TOKEN", "")
    if not token:
        raise LineServiceError("LINE integration token is not configured")
    return base_url, token


async def list_line_groups() -> list[dict[str, Any]]:
    return await asyncio.to_thread(_request, "/internal/groups", None)


async def push_line_messages(group_id: str, messages: list[str]) -> dict[str, Any]:
    if not group_id or not messages:
        raise LineServiceError("LINE group and messages are required")
    return await asyncio.to_thread(_request, "/internal/push", {"group_id": group_id, "messages": messages})


def _request(path: str, payload: dict[str, Any] | None) -> Any:
    base_url, token = _config()
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        method="POST" if payload is not None else "GET",
        headers={"Content-Type": "application/json", "X-AI-Work-Token": token},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("detail")
        except (ValueError, UnicodeDecodeError):
            detail = None
        raise LineServiceError(detail or f"LINE service returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise LineServiceError(f"LINE service unavailable: {exc}") from exc
