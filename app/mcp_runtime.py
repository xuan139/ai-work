from __future__ import annotations

import ipaddress
import json
import os
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


class McpConnectionError(RuntimeError):
    pass


SUPPORTED_PROTOCOL_VERSION = "2025-06-18"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
TRUSTED_PUBLIC_MCP_HOSTS = {
    "api.githubcopilot.com",
    "gmailmcp.googleapis.com",
    "drivemcp.googleapis.com",
    "docsmcp.googleapis.com",
    "sheetsmcp.googleapis.com",
    "slidesmcp.googleapis.com",
    "calendarmcp.googleapis.com",
    "chatmcp.googleapis.com",
    "people.googleapis.com",
    "mcp.notion.com",
    "mcp.stripe.com",
    "mcp.atlassian.com",
    "mcp.linear.app",
    "mcp.monday.com",
    "mcp.cloudflare.com",
    "docs.mcp.cloudflare.com",
    "mcp.vercel.com",
    "mcp.supabase.com",
    "mcp.context7.com",
}


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def validate_mcp_endpoint(endpoint: str) -> str:
    clean = endpoint.strip()
    parsed = urlparse(clean)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("MCP Endpoint 必須是有效的 HTTP 或 HTTPS URL")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("MCP Endpoint 不可包含帳密或 URL fragment")

    hostname = parsed.hostname.lower()
    allowed_hosts = {
        item.strip().lower()
        for item in os.getenv("MCP_ALLOWED_HOSTS", "").split(",")
        if item.strip()
    }
    allowed_hosts.update(TRUSTED_PUBLIC_MCP_HOSTS)
    if hostname in TRUSTED_PUBLIC_MCP_HOSTS:
        if parsed.scheme != "https":
            raise ValueError("官方公網 MCP Endpoint 必須使用 HTTPS")
        return clean
    if hostname in allowed_hosts or hostname == "localhost" or hostname.endswith(".local"):
        return clean

    try:
        default_port = 443 if parsed.scheme == "https" else 80
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(hostname, parsed.port or default_port, type=socket.SOCK_STREAM)
        }
    except socket.gaierror as exc:
        raise ValueError("MCP Endpoint 主機名稱無法解析") from exc
    if not addresses:
        raise ValueError("MCP Endpoint 沒有可用位址")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if ip.is_link_local or ip.is_multicast or ip.is_unspecified or ip.is_reserved:
            raise ValueError("MCP Endpoint 不可使用 link-local、multicast 或保留位址")
        if not (ip.is_private or ip.is_loopback):
            raise ValueError("公網 MCP Endpoint 必須先加入伺服器 MCP_ALLOWED_HOSTS")
    return clean


def sync_streamable_http_tools(server: dict[str, Any]) -> dict[str, Any]:
    endpoint, token, extra_headers = _server_connection(server)
    result, session_id = _initialize_session(endpoint, token, extra_headers)
    protocol_version = str(result.get("protocolVersion") or SUPPORTED_PROTOCOL_VERSION)

    tools: list[dict[str, Any]] = []
    cursor = None
    for request_id in range(2, 12):
        params = {"cursor": cursor} if cursor else {}
        response, next_session_id = _json_rpc_request(
            endpoint,
            {"jsonrpc": "2.0", "id": request_id, "method": "tools/list", "params": params},
            token=token,
            session_id=session_id,
            extra_headers=extra_headers,
        )
        session_id = next_session_id or session_id
        if response.get("error"):
            raise McpConnectionError(_rpc_error(response["error"]))
        page = response.get("result") or {}
        for tool in page.get("tools") or []:
            tools.append(
                {
                    "name": str(tool.get("name") or ""),
                    "title": str(tool.get("title") or ""),
                    "description": str(tool.get("description") or ""),
                    "inputSchema": tool.get("inputSchema") or {},
                    "annotations": tool.get("annotations") or {},
                }
            )
        cursor = page.get("nextCursor")
        if not cursor:
            break
    return {
        "protocol_version": protocol_version,
        "server_info": result.get("serverInfo") or {},
        "capabilities": result.get("capabilities") or {},
        "tools": tools,
    }


def call_streamable_http_tool(
    server: dict[str, Any],
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    endpoint, token, extra_headers = _server_connection(server)
    _, session_id = _initialize_session(endpoint, token, extra_headers)
    response, _ = _json_rpc_request(
        endpoint,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        },
        token=token,
        session_id=session_id,
        extra_headers=extra_headers,
    )
    if response.get("error"):
        raise McpConnectionError(_rpc_error(response["error"]))
    result = response.get("result")
    if not isinstance(result, dict):
        raise McpConnectionError("MCP tools/call 沒有回傳有效結果")
    if result.get("isError"):
        raise McpConnectionError(_tool_error(result))
    return result


def _server_connection(server: dict[str, Any]) -> tuple[str, str | None, dict[str, str]]:
    if server.get("transport") != "streamable_http":
        raise McpConnectionError("目前只支援 Streamable HTTP 的實際連線與工具呼叫")
    endpoint = validate_mcp_endpoint(str(server.get("endpoint") or ""))
    token = None
    auth_env_var = str(server.get("auth_env_var") or "").strip()
    if auth_env_var:
        token = os.getenv(auth_env_var)
        if not token:
            raise McpConnectionError(f"伺服器環境變數 {auth_env_var} 尚未設定")
    return endpoint, token, _parse_extra_headers(server.get("headers_json"))


def _initialize_session(
    endpoint: str,
    token: str | None,
    extra_headers: dict[str, str],
) -> tuple[dict[str, Any], str | None]:
    initialize, session_id = _json_rpc_request(
        endpoint,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": SUPPORTED_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "AI Work NAS", "version": "1.0"},
            },
        },
        token=token,
        session_id=None,
        extra_headers=extra_headers,
    )
    result = initialize.get("result") or {}
    if initialize.get("error"):
        raise McpConnectionError(_rpc_error(initialize["error"]))

    _json_rpc_request(
        endpoint,
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        token=token,
        session_id=session_id,
        extra_headers=extra_headers,
        allow_empty=True,
    )
    return result, session_id


def _json_rpc_request(
    endpoint: str,
    payload: dict[str, Any],
    *,
    token: str | None,
    session_id: str | None,
    extra_headers: dict[str, str] | None = None,
    allow_empty: bool = False,
) -> tuple[dict[str, Any], str | None]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "AI-Work-NAS/1.0",
    }
    if token:
        headers["Authorization"] = token if token.lower().startswith(("bearer ", "basic ")) else f"Bearer {token}"
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    headers.update(extra_headers or {})
    request = Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with build_opener(_NoRedirect).open(
            request,
            timeout=float(os.getenv("MCP_CONNECT_TIMEOUT_SECONDS", "10")),
        ) as response:
            content_length = int(response.headers.get("Content-Length") or 0)
            if content_length > MAX_RESPONSE_BYTES:
                raise McpConnectionError("MCP 回應超過 2 MB 上限")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise McpConnectionError("MCP 回應超過 2 MB 上限")
            next_session_id = response.headers.get("Mcp-Session-Id") or session_id
            content_type = response.headers.get("Content-Type", "")
    except HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace").strip()
        raise McpConnectionError(f"MCP HTTP {exc.code}: {detail or exc.reason}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise McpConnectionError(f"MCP 連線失敗：{exc}") from exc

    if not raw.strip() and allow_empty:
        return {}, next_session_id
    if "text/event-stream" in content_type:
        return _parse_sse_json(raw), next_session_id
    try:
        return json.loads(raw.decode("utf-8")), next_session_id
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise McpConnectionError("MCP 回應不是有效的 JSON-RPC") from exc


def _parse_extra_headers(raw: object) -> dict[str, str]:
    if not raw:
        return {}
    try:
        values = json.loads(str(raw))
    except json.JSONDecodeError as exc:
        raise McpConnectionError("MCP 固定 Header 設定不是有效 JSON") from exc
    if not isinstance(values, dict):
        raise McpConnectionError("MCP 固定 Header 設定必須是 JSON object")
    reserved = {
        "authorization", "cookie", "host", "content-length", "connection",
        "proxy-authorization", "transfer-encoding", "mcp-session-id",
    }
    headers: dict[str, str] = {}
    for name, value in values.items():
        clean_name = str(name).strip()
        if not clean_name or clean_name.lower() in reserved or not isinstance(value, str):
            raise McpConnectionError(f"MCP 固定 Header 不允許使用：{clean_name or '(empty)'}")
        headers[clean_name] = value
    return headers


def _parse_sse_json(raw: bytes) -> dict[str, Any]:
    for line in raw.decode("utf-8", errors="replace").splitlines():
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
    raise McpConnectionError("MCP SSE 回應沒有有效的 JSON-RPC data")


def _rpc_error(error: object) -> str:
    if isinstance(error, dict):
        return str(error.get("message") or error)
    return str(error)


def _tool_error(result: dict[str, Any]) -> str:
    texts = [
        str(item.get("text"))
        for item in result.get("content") or []
        if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
    ]
    return "\n".join(texts) or "MCP 工具回報執行失敗"
