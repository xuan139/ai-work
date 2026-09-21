import asyncio
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


N8N_INTERNAL_URL = os.getenv("N8N_INTERNAL_URL", "http://127.0.0.1:5678").rstrip("/")
N8N_PUBLIC_URL = os.getenv("N8N_PUBLIC_URL", "/n8n/")
N8N_VERSION = os.getenv("N8N_VERSION", "2.39.8")
N8N_TEST_WORKFLOW = os.getenv("N8N_TEST_WORKFLOW", "AI Work NAS 處理完成通知 Demo")
class N8nDeliveryError(RuntimeError):
    pass


async def notify_n8n_asset_completed(asset: dict[str, Any], chunks: list[dict[str, Any]]) -> dict[str, Any]:
    if asset.get("status") != "completed" or asset.get("category") not in {"audio", "pdf"}:
        return {"status": "skipped", "reason": "unsupported_asset"}
    try:
        return await asyncio.to_thread(_post_asset_event, build_asset_completed_payload(asset, chunks))
    except Exception as exc:
        return {"status": "failed", "error": str(exc)}


def build_asset_completed_payload(asset: dict[str, Any], chunks: list[dict[str, Any]]) -> dict[str, Any]:
    preview = "\n\n".join(str(chunk.get("content") or "").strip() for chunk in chunks if chunk.get("content"))
    return {
        "event": "nas.asset.completed",
        "asset_id": asset["id"],
        "category": asset["category"],
        "title": asset["title"],
        "filename": asset["original_filename"],
        "analyzer": asset.get("analyzer"),
        "summary": asset.get("summary"),
        "chunk_count": asset.get("chunk_count") or 0,
        "uploader": asset.get("owner_username"),
        "completed_at": asset.get("updated_at"),
        "result_preview": preview[:1800],
        "asset_url": f"/api/nas-assets/{asset['id']}",
    }


def _post_asset_event(payload: dict[str, Any]) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    token = os.getenv("N8N_WEBHOOK_TOKEN", "")
    if token:
        headers["X-AI-Work-N8N-Token"] = token
    webhook_url = os.getenv(
        "N8N_ASSET_WEBHOOK_URL",
        "http://127.0.0.1:5678/webhook/ai-work-nas-asset-completed",
    )
    request = Request(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    try:
        with urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body) if body else {}
            return parsed if isinstance(parsed, dict) else {"status": "completed", "result": parsed}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise N8nDeliveryError(f"n8n webhook returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise N8nDeliveryError(f"n8n webhook unavailable: {exc}") from exc


def _health_candidates() -> list[str]:
    return [
        f"{N8N_INTERNAL_URL}/healthz/readiness",
        f"{N8N_INTERNAL_URL}/healthz",
        f"{N8N_INTERNAL_URL}/n8n/healthz/readiness",
        f"{N8N_INTERNAL_URL}/n8n/healthz",
    ]


def n8n_service_status(timeout: float = 2.0) -> dict:
    started_at = time.monotonic()
    last_error = "n8n service is unavailable"

    for endpoint in _health_candidates():
        try:
            request = Request(endpoint, headers={"Accept": "application/json"})
            with urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                if response.status >= 400:
                    continue
                try:
                    health = json.loads(body) if body else {"status": "ok"}
                except json.JSONDecodeError:
                    health = {"status": body or "ok"}
                return {
                    "status": "connected",
                    "version": N8N_VERSION,
                    "public_url": N8N_PUBLIC_URL,
                    "test_workflow": N8N_TEST_WORKFLOW,
                    "response_ms": round((time.monotonic() - started_at) * 1000),
                    "health": health,
                }
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            last_error = str(error)

    return {
        "status": "unavailable",
        "version": N8N_VERSION,
        "public_url": N8N_PUBLIC_URL,
        "test_workflow": N8N_TEST_WORKFLOW,
        "response_ms": round((time.monotonic() - started_at) * 1000),
        "error": last_error,
    }
