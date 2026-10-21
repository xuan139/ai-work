from __future__ import annotations

import base64
import json
import os
import re
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from app.mcp_runtime import McpConnectionError, oauth_access_token


GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
MAX_ACCOUNTS = 20
MAX_RECIPIENTS = 10
MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024
ACCOUNT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
ENV_NAME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*_TOKEN$")


class GmailDeliveryError(RuntimeError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def list_gmail_sender_accounts() -> list[dict[str, Any]]:
    raw = os.getenv("GMAIL_SEND_ACCOUNTS_JSON", "").strip()
    if not raw:
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GmailDeliveryError("GMAIL_SEND_ACCOUNTS_JSON 不是有效 JSON") from exc
    if not isinstance(payload, list):
        raise GmailDeliveryError("GMAIL_SEND_ACCOUNTS_JSON 必須是陣列")
    if len(payload) > MAX_ACCOUNTS:
        raise GmailDeliveryError(f"Gmail 寄件帳號最多 {MAX_ACCOUNTS} 個")

    accounts = []
    seen_ids: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            raise GmailDeliveryError("Gmail 寄件帳號設定格式錯誤")
        account_id = str(item.get("id") or "").strip().lower()
        email = _email_address(item.get("email"), "寄件帳號")
        oauth_env = str(item.get("oauth_env") or "").strip()
        if not ACCOUNT_ID_PATTERN.fullmatch(account_id) or account_id in seen_ids:
            raise GmailDeliveryError("Gmail 寄件帳號 id 必須唯一且只含小寫英數、底線或連字號")
        if not ENV_NAME_PATTERN.fullmatch(oauth_env):
            raise GmailDeliveryError("Gmail oauth_env 必須是以 _TOKEN 結尾的環境變數名稱")
        send_enabled = item.get("send_enabled", True)
        if not isinstance(send_enabled, bool):
            raise GmailDeliveryError("Gmail send_enabled 必須是 true 或 false")
        seen_ids.add(account_id)
        allowed_recipients = _email_list(item.get("allowed_recipients") or [])
        allowed_domains = _domain_list(item.get("allowed_domains") or [])
        credentials_configured = _oauth_credentials_configured(oauth_env)
        accounts.append({
            "id": account_id,
            "label": str(item.get("label") or email).strip()[:100] or email,
            "email": email,
            "oauth_env": oauth_env,
            "allowed_recipients": allowed_recipients,
            "allowed_domains": allowed_domains,
            "configured": credentials_configured and send_enabled,
            "status": "ready" if credentials_configured and send_enabled else (
                "reauthorization_required" if credentials_configured else "missing_credentials"
            ),
        })
    return accounts


def public_gmail_sender_accounts() -> list[dict[str, Any]]:
    return [
        {
            "id": account["id"],
            "label": account["label"],
            "email": account["email"],
            "configured": account["configured"],
            "status": account["status"],
            "recipient_policy": _recipient_policy_label(account),
        }
        for account in list_gmail_sender_accounts()
    ]


def gmail_sender_account(account_id: object) -> dict[str, Any]:
    clean = str(account_id or "").strip().lower()
    account = next((item for item in list_gmail_sender_accounts() if item["id"] == clean), None)
    if account is None:
        raise GmailDeliveryError("找不到指定的 Gmail 寄件帳號")
    if not account["configured"]:
        if account["status"] == "reauthorization_required":
            raise GmailDeliveryError("此 Gmail 寄件帳號需要重新授權 gmail.send")
        raise GmailDeliveryError("此 Gmail 寄件帳號尚未完成 OAuth 憑證設定")
    return account


def normalize_gmail_recipients(raw: object, account: dict[str, Any]) -> list[str]:
    if isinstance(raw, str):
        values = re.split(r"[,;\n]", raw)
    elif isinstance(raw, list):
        values = raw
    else:
        raise GmailDeliveryError("收件人必須是 Email 陣列或以逗號分隔的文字")
    recipients = []
    for value in values:
        if not str(value or "").strip():
            continue
        address = _email_address(value, "收件人")
        if address not in recipients:
            recipients.append(address)
    if not recipients:
        raise GmailDeliveryError("至少需要一個收件人")
    if len(recipients) > MAX_RECIPIENTS:
        raise GmailDeliveryError(f"每次最多 {MAX_RECIPIENTS} 個收件人")

    exact = set(account.get("allowed_recipients") or []) | {str(account["email"]).lower()}
    domains = set(account.get("allowed_domains") or [])
    blocked = [
        address for address in recipients
        if address not in exact and address.rsplit("@", 1)[1] not in domains
    ]
    if blocked:
        raise GmailDeliveryError(f"收件人不在此寄件帳號白名單：{', '.join(blocked)}")
    return recipients


def build_gmail_message(
    *, sender: str, recipients: list[str], subject: str, body: str, attachment_path: Path,
) -> bytes:
    if not attachment_path.is_file():
        raise GmailDeliveryError("報告 PDF 不存在")
    size = attachment_path.stat().st_size
    if size > MAX_ATTACHMENT_BYTES:
        raise GmailDeliveryError("報告 PDF 超過 Gmail 附件安全上限 20 MB")
    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject[:160]
    message.set_content(body)
    message.add_attachment(
        attachment_path.read_bytes(), maintype="application", subtype="pdf", filename=attachment_path.name,
    )
    return message.as_bytes()


def send_gmail_report(
    *, account: dict[str, Any], recipients: list[str], subject: str, body: str, attachment_path: Path,
) -> dict[str, str]:
    try:
        token = oauth_access_token(str(account["oauth_env"]))
    except McpConnectionError as exc:
        raise GmailDeliveryError(str(exc)) from exc
    message = build_gmail_message(
        sender=str(account["email"]), recipients=recipients, subject=subject,
        body=body, attachment_path=attachment_path,
    )
    payload = json.dumps({"raw": base64.urlsafe_b64encode(message).decode("ascii").rstrip("=")}).encode("utf-8")
    request = Request(
        GMAIL_SEND_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with build_opener(_NoRedirect).open(request, timeout=20) as response:
            raw = response.read(64 * 1024)
    except HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace").strip()
        if exc.code == 403:
            detail = "Gmail OAuth 未包含 gmail.send 權限，請重新授權"
        raise GmailDeliveryError(f"Gmail API HTTP {exc.code}: {detail or exc.reason}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise GmailDeliveryError(f"Gmail API 連線失敗：{exc}") from exc
    try:
        result = json.loads(raw.decode("utf-8"))
        message_id = str(result["id"])
    except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GmailDeliveryError("Gmail API 未回傳有效 Message ID") from exc
    return {"message_id": message_id, "thread_id": str(result.get("threadId") or "")}


def _email_address(value: object, label: str) -> str:
    raw = str(value or "").strip()
    _, parsed = parseaddr(raw)
    address = parsed.lower()
    if parsed != raw or len(address) > 254 or address.count("@") != 1:
        raise GmailDeliveryError(f"{label} Email 格式不正確")
    local, domain = address.rsplit("@", 1)
    if not local or not domain or "." not in domain or any(char.isspace() for char in address):
        raise GmailDeliveryError(f"{label} Email 格式不正確")
    return address


def _email_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise GmailDeliveryError("allowed_recipients 必須是陣列")
    return list(dict.fromkeys(_email_address(item, "允許收件人") for item in value))


def _domain_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise GmailDeliveryError("allowed_domains 必須是陣列")
    domains = []
    for item in value:
        domain = str(item or "").strip().lower().lstrip("@")
        if not domain or "." not in domain or not re.fullmatch(r"[a-z0-9.-]+", domain):
            raise GmailDeliveryError("允許收件網域格式不正確")
        if domain not in domains:
            domains.append(domain)
    return domains


def _oauth_credentials_configured(oauth_env: str) -> bool:
    prefix = oauth_env[:-6]
    return all(os.getenv(f"{prefix}_{suffix}") for suffix in ("CLIENT_ID", "CLIENT_SECRET", "REFRESH_TOKEN"))


def _recipient_policy_label(account: dict[str, Any]) -> str:
    exact = len(account.get("allowed_recipients") or [])
    domains = account.get("allowed_domains") or []
    if exact or domains:
        parts = []
        if domains:
            parts.append("網域：" + "、".join(domains))
        if exact:
            parts.append(f"指定地址 {exact} 個")
        return "；".join(parts)
    return "僅寄件帳號本人"
