from __future__ import annotations

import os
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any


PROMPT_PATTERNS = (
    ("instruction_override", re.compile(r"(?:ignore|disregard|forget|忽略|無視|无视).{0,40}(?:previous|system|developer|instructions?|先前|系統|系统|指令)", re.I | re.S)),
    ("secret_exfiltration", re.compile(r"(?:reveal|show|print|return|顯示|显示|輸出|输出|洩漏|泄露).{0,40}(?:system prompt|api[_ -]?key|password|secret|token|系統提示|系统提示|密碼|密码|金鑰|密钥)", re.I | re.S)),
    ("access_bypass", re.compile(r"(?:bypass|disable|override|繞過|绕过|停用|取消).{0,40}(?:permission|authorization|security|access control|權限|权限|安全|存取控制)", re.I | re.S)),
    ("role_spoofing", re.compile(r"(?:you are now|act as|pretend to be|現在你是|假裝你是|假设你是).{0,60}(?:system|developer|admin|root|系統|系统|管理員|管理员)", re.I | re.S)),
)

UNTRUSTED_CONTENT_PATTERNS = (
    re.compile(r"(?:ignore|disregard|忽略|無視|无视).{0,50}(?:previous|system|instructions?|先前|系統|系统|指令)", re.I | re.S),
    re.compile(r"<(?:system|assistant|developer)>|\[(?:system|assistant|developer)\]", re.I),
    re.compile(r"(?:send|upload|exfiltrate|傳送|上传|上傳|外傳).{0,60}(?:secret|token|password|api[_ -]?key|機密|秘密|密碼|密码|金鑰|密钥)", re.I | re.S),
)


@dataclass(frozen=True)
class PromptAssessment:
    blocked: bool
    reasons: tuple[str, ...]
    severity: str


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allowed(self, key: str) -> bool:
        now = time.monotonic()
        events = self._events[key]
        while events and now - events[0] >= self.window_seconds:
            events.popleft()
        return len(events) < self.limit

    def record(self, key: str) -> None:
        self._events[key].append(time.monotonic())

    def clear(self, key: str) -> None:
        self._events.pop(key, None)


def assess_prompt(prompt: str) -> PromptAssessment:
    reasons = tuple(name for name, pattern in PROMPT_PATTERNS if pattern.search(prompt or ""))
    return PromptAssessment(
        blocked=bool(reasons),
        reasons=reasons,
        severity="high" if reasons else "none",
    )


def filter_untrusted_contexts(contexts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    safe: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for context in contexts:
        content = str(context.get("content") or "")
        matches = [pattern.pattern for pattern in UNTRUSTED_CONTENT_PATTERNS if pattern.search(content)]
        if matches:
            rejected.append(
                {
                    "asset_id": context.get("asset_id"),
                    "chunk_id": context.get("id"),
                    "reasons": matches,
                }
            )
        else:
            safe.append(context)
    return safe, rejected


def validate_production_security() -> None:
    if os.getenv("AI_WORK_ENV", "development").strip().lower() != "production":
        return
    secret = os.getenv("APP_SECRET_KEY", "")
    if len(secret) < 32 or secret == "dev-demo-secret-change-me" or secret.startswith("replace-"):
        raise RuntimeError("Production requires a random APP_SECRET_KEY with at least 32 characters")
    public_url = os.getenv("AI_WORK_PUBLIC_URL", "")
    if not public_url.startswith("https://"):
        raise RuntimeError("Production requires an HTTPS AI_WORK_PUBLIC_URL")
    admin_password = os.getenv("AI_WORK_ADMIN_PASSWORD", "").strip()
    if len(admin_password) < 12 or admin_password == "admin123" or admin_password.startswith("replace-"):
        raise RuntimeError("Production requires a non-default AI_WORK_ADMIN_PASSWORD with at least 12 characters")


def security_headers() -> dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), geolocation=(), payment=(), usb=()",
        "Content-Security-Policy": (
            "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; "
            "form-action 'self'; img-src 'self' data: blob:; media-src 'self' blob:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self' wss: ws:"
        ),
    }
