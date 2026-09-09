import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from fastapi import Cookie, Depends, HTTPException, Request, WebSocket, status

from app.db import get_user_by_id, get_user_by_username

SESSION_COOKIE = "ai_work_session"
SESSION_TTL_SECONDS = 60 * 60 * 8
SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-demo-secret-change-me")


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
    return hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + SESSION_TTL_SECONDS,
    }
    raw_payload = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    return f"{raw_payload}.{_sign(raw_payload)}"


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
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return user


def current_user(session: str | None = Cookie(default=None, alias=SESSION_COOKIE)) -> dict[str, Any]:
    payload = read_session_token(session)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = get_user_by_id(int(payload["user_id"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user


def websocket_user(websocket: WebSocket) -> dict[str, Any] | None:
    payload = read_session_token(websocket.cookies.get(SESSION_COOKIE))
    if not payload:
        return None
    return get_user_by_id(int(payload["user_id"]))


def require_meeting_access(meeting: dict[str, Any] | None, user: dict[str, Any]) -> dict[str, Any]:
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    if user["role"] != "admin" and meeting["user_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return meeting
