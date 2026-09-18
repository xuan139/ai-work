from __future__ import annotations

import base64
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
MAX_API_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_MESSAGE_TEXT_CHARS = 12000
MAX_THREAD_TEXT_CHARS = 30000

GMAIL_MCP_TOOLS = [
    {
        "name": "gmail_search_threads",
        "title": "Search Gmail Threads",
        "description": (
            "Search Gmail threads and return message metadata. The query must use Gmail search syntax, "
            "for example newer_than:10d, from:user@example.com, subject:invoice, or is:unread. "
            "Use newer_than:30d for general recent mail; never use recent: or within:."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gmail search query, such as 'newer_than:30d invoice' or 'is:unread'.",
                },
                "max_results": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "gmail_get_thread",
        "title": "Read Gmail Thread",
        "description": "Read messages and text content from one Gmail thread.",
        "inputSchema": {
            "type": "object",
            "properties": {"thread_id": {"type": "string"}},
            "required": ["thread_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "gmail_get_message",
        "title": "Read Gmail Message",
        "description": "Read metadata and text content from one Gmail message.",
        "inputSchema": {
            "type": "object",
            "properties": {"message_id": {"type": "string"}},
            "required": ["message_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "gmail_list_labels",
        "title": "List Gmail Labels",
        "description": "List Gmail system and user labels.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
]


class GmailApiError(RuntimeError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def handle_gmail_mcp_request(payload: dict[str, Any], access_token: str) -> dict[str, Any] | None:
    method = str(payload.get("method") or "")
    request_id = payload.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "AI Work Gmail Read-only MCP", "version": "1.0.0"},
                "instructions": "Read-only Gmail access through the stable Gmail API.",
            },
        )
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": GMAIL_MCP_TOOLS})
    if method == "tools/call":
        params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
        name = str(params.get("name") or "")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        try:
            output = _call_tool(name, arguments, access_token)
        except (ValueError, GmailApiError) as exc:
            return _error(request_id, -32602, str(exc))
        return _result(
            request_id,
            {
                "content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}],
                "structuredContent": output,
                "isError": False,
            },
        )
    return _error(request_id, -32601, f"Method not found: {method}")


def _call_tool(name: str, arguments: dict[str, Any], access_token: str) -> dict[str, Any]:
    if name == "gmail_list_labels":
        result = _gmail_request("labels", access_token)
        return {
            "labels": [
                {key: label.get(key) for key in ("id", "name", "type") if label.get(key) is not None}
                for label in result.get("labels") or []
            ]
        }
    if name == "gmail_search_threads":
        requested_query = str(arguments.get("query") or "").strip()
        if not requested_query:
            raise ValueError("query is required")
        query = normalize_gmail_query(requested_query)
        limit = _bounded_limit(arguments.get("max_results"), 5)
        result = _gmail_request(
            "threads",
            access_token,
            [("q", query), ("maxResults", str(limit))],
        )
        threads = []
        for item in result.get("threads") or []:
            thread_id = str(item.get("id") or "")
            if not thread_id:
                continue
            metadata = _gmail_request(
                f"threads/{quote(thread_id, safe='')}",
                access_token,
                [("format", "metadata"), ("metadataHeaders", "Subject"), ("metadataHeaders", "From"), ("metadataHeaders", "Date")],
            )
            threads.append(_thread_summary(metadata))
        return {
            "requested_query": requested_query,
            "query": query,
            "query_normalized": query != requested_query,
            "count": len(threads),
            "threads": threads,
        }
    if name == "gmail_get_thread":
        thread_id = _required_id(arguments, "thread_id")
        result = _gmail_request(f"threads/{quote(thread_id, safe='')}", access_token, [("format", "full")])
        messages = [_message_content(message) for message in result.get("messages") or []]
        return {"thread_id": thread_id, "messages": _truncate_thread(messages)}
    if name == "gmail_get_message":
        message_id = _required_id(arguments, "message_id")
        result = _gmail_request(f"messages/{quote(message_id, safe='')}", access_token, [("format", "full")])
        return _message_content(result)
    raise ValueError(f"Unknown tool: {name}")


def _gmail_request(
    path: str,
    access_token: str,
    query: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    url = f"{GMAIL_API_BASE}/{path}"
    if query:
        url += "?" + urlencode(query)
    request = Request(
        url,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
    )
    try:
        with build_opener(_NoRedirect).open(request, timeout=15) as response:
            raw = response.read(MAX_API_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace").strip()
        raise GmailApiError(f"Gmail API HTTP {exc.code}: {detail or exc.reason}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise GmailApiError(f"Gmail API connection failed: {exc}") from exc
    if len(raw) > MAX_API_RESPONSE_BYTES:
        raise GmailApiError("Gmail API response exceeded 2 MB")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GmailApiError("Gmail API returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise GmailApiError("Gmail API returned an invalid response")
    return result


def _thread_summary(thread: dict[str, Any]) -> dict[str, Any]:
    messages = thread.get("messages") or []
    latest = messages[-1] if messages else {}
    headers = _headers(latest.get("payload") or {})
    return {
        "thread_id": thread.get("id"),
        "message_count": len(messages),
        "subject": headers.get("subject", ""),
        "from": headers.get("from", ""),
        "date": headers.get("date", ""),
        "snippet": str(latest.get("snippet") or "")[:500],
    }


def _message_content(message: dict[str, Any]) -> dict[str, Any]:
    payload = message.get("payload") if isinstance(message.get("payload"), dict) else {}
    headers = _headers(payload)
    text = _extract_text(payload).strip()
    return {
        "message_id": message.get("id"),
        "thread_id": message.get("threadId"),
        "subject": headers.get("subject", ""),
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "date": headers.get("date", ""),
        "snippet": str(message.get("snippet") or "")[:500],
        "text": text[:MAX_MESSAGE_TEXT_CHARS],
        "truncated": len(text) > MAX_MESSAGE_TEXT_CHARS,
    }


def _headers(payload: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in payload.get("headers") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").lower()
        if name in {"subject", "from", "to", "date"}:
            result[name] = str(item.get("value") or "")
    return result


def _extract_text(part: dict[str, Any]) -> str:
    mime_type = str(part.get("mimeType") or "")
    body = part.get("body") if isinstance(part.get("body"), dict) else {}
    data = str(body.get("data") or "")
    if data and mime_type in {"text/plain", "text/html"}:
        try:
            decoded = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")
        except (ValueError, UnicodeDecodeError):
            decoded = ""
        if mime_type == "text/plain":
            return decoded
    texts = [_extract_text(child) for child in part.get("parts") or [] if isinstance(child, dict)]
    plain = "\n".join(item for item in texts if item.strip())
    if plain:
        return plain
    if data and mime_type == "text/html":
        return decoded
    return ""


def _truncate_thread(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    remaining = MAX_THREAD_TEXT_CHARS
    output = []
    for message in messages:
        item = dict(message)
        text = str(item.get("text") or "")
        item["text"] = text[:remaining]
        item["truncated"] = bool(item.get("truncated") or len(text) > remaining)
        output.append(item)
        remaining -= len(item["text"])
        if remaining <= 0:
            break
    return output


def _required_id(arguments: dict[str, Any], key: str) -> str:
    value = str(arguments.get(key) or "").strip()
    if not value:
        raise ValueError(f"{key} is required")
    return value


def normalize_gmail_query(query: str) -> str:
    normalized = " ".join(query.split())
    normalized = re.sub(
        r"\brecent:(\d+)(?:\s*(?:days?|d))?\b",
        lambda match: f"newer_than:{match.group(1)}d",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"\bwithin:(\d+)\s*(?:days?|d)\b",
        lambda match: f"newer_than:{match.group(1)}d",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"(?:最近|近)\s*(\d+)\s*(?:天|日)(?:內|内)?",
        lambda match: f"newer_than:{match.group(1)}d",
        normalized,
    )
    normalized = re.sub(r"最近(?:的)?(?:郵件|邮件|信件)", "newer_than:30d", normalized)

    def replace_invalid_date_operator(match: re.Match[str]) -> str:
        operator, value = match.groups()
        if re.fullmatch(r"(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{9,})", value):
            return f"{operator}:{value}"
        return value

    normalized = re.sub(
        r"\b(after|before):([^\s]+)",
        replace_invalid_date_operator,
        normalized,
        flags=re.IGNORECASE,
    )
    return " ".join(normalized.split())


def _bounded_limit(value: object, default: int) -> int:
    try:
        limit = int(value) if value is not None else default
    except (TypeError, ValueError) as exc:
        raise ValueError("max_results must be an integer") from exc
    return max(1, min(limit, 10))


def _result(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
