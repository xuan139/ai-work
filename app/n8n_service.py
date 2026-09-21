import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


N8N_INTERNAL_URL = os.getenv("N8N_INTERNAL_URL", "http://127.0.0.1:5678").rstrip("/")
N8N_PUBLIC_URL = os.getenv("N8N_PUBLIC_URL", "/n8n/")
N8N_VERSION = os.getenv("N8N_VERSION", "2.39.8")
N8N_TEST_WORKFLOW = os.getenv("N8N_TEST_WORKFLOW", "AI Work NAS 測試流程")


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
