import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Mapping

from fastapi import Cookie, Depends, HTTPException, Request, WebSocket, status

from app.db import get_user_by_id, get_user_by_username

SESSION_COOKIE = "ai_work_session"
SESSION_TTL_SECONDS = 60 * 60 * 8
MCP_DELEGATION_TTL_SECONDS = 60
def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}.{base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        encoded_salt, encoded_digest = stored.split(".", 1)
        salt = base64.urlsafe_b64decode(encoded_salt.encode())
        expected = base64.urlsafe_b64decode(encoded_digest.encode())
    except ValueError:
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(digest, expected)


def _sign(payload: str) -> str:
    secret = os.getenv("APP_SECRET_KEY", "dev-demo-secret-change-me")
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token(user_id: int, session_version: int = 1) -> str:
    payload = {
        "user_id": user_id,
        "session_version": session_version,
        "exp": int(time.time()) + SESSION_TTL_SECONDS,
    }
    raw_payload = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    return f"{raw_payload}.{_sign(raw_payload)}"


def create_mcp_delegation_headers(user: dict[str, Any]) -> dict[str, str]:
    timestamp = str(int(time.time()))
    user_id = str(int(user["id"]))
    payload = f"mcp-user:{user_id}:{timestamp}"
    return {
        "X-AI-Work-User-Id": user_id,
        "X-AI-Work-Timestamp": timestamp,
        "X-AI-Work-Signature": _sign(payload),
    }


def read_mcp_delegated_user(headers: Mapping[str, str]) -> dict[str, Any] | None:
    user_id = str(headers.get("x-ai-work-user-id") or headers.get("X-AI-Work-User-Id") or "")
    timestamp = str(headers.get("x-ai-work-timestamp") or headers.get("X-AI-Work-Timestamp") or "")
    signature = str(headers.get("x-ai-work-signature") or headers.get("X-AI-Work-Signature") or "")
    try:
        age = abs(int(time.time()) - int(timestamp))
        numeric_user_id = int(user_id)
    except ValueError:
        return None
    if age > MCP_DELEGATION_TTL_SECONDS:
        return None
    if not hmac.compare_digest(_sign(f"mcp-user:{user_id}:{timestamp}"), signature):
        return None
    user = get_user_by_id(numeric_user_id)
    if not user or not user.get("is_active", 1):
        return None
    return user


def read_session_token(token: str | None) -> dict[str, Any] | None:
    if not token or "." not in token:
        return None
    raw_payload, signature = token.rsplit(".", 1)
    if not hmac.compare_digest(_sign(raw_payload), signature):
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(raw_payload.encode()).decode())
    except (ValueError, json.JSONDecodeError):
        return None
    if payload.get("exp", 0) < int(time.time()):
        return None
    return payload


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    user = get_user_by_username(username)
    if not user or not user.get("is_active", 1) or not verify_password(password, user["password_hash"]):
        return None
    return user


def current_user(session: str | None = Cookie(default=None, alias=SESSION_COOKIE)) -> dict[str, Any]:
    payload = read_session_token(session)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = get_user_by_id(int(payload["user_id"]))
    if not user or not user.get("is_active", 1):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    if int(payload.get("session_version", 1)) != int(user.get("session_version", 1)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked")
    return user


def websocket_user(websocket: WebSocket) -> dict[str, Any] | None:
    payload = read_session_token(websocket.cookies.get(SESSION_COOKIE))
    if not payload:
        return None
    user = get_user_by_id(int(payload["user_id"]))
    if not user or not user.get("is_active", 1):
        return None
    if int(payload.get("session_version", 1)) != int(user.get("session_version", 1)):
        return None
    return user


def require_admin(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return user


def require_meeting_access(meeting: dict[str, Any] | None, user: dict[str, Any]) -> dict[str, Any]:
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    if user["role"] != "admin" and meeting["user_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return meeting
