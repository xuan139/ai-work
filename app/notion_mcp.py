from __future__ import annotations

import json
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from app.mcp_orchestrator import McpPlanningError, resolve_planned_tool

NOTION_VERSION = "2025-09-03"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_TEXT_CHARS = 6000


def _tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "name": name, "description": description,
        "inputSchema": {"type": "object", "properties": properties,
                        "required": required, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    }


PAGING = {
    "page_size": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
    "start_cursor": {"type": "string", "description": "Opaque next_cursor from the previous result."},
}
NOTION_MCP_TOOLS = [
    _tool("notion_search", "Search shared page titles, not full text. Empty query lists recently edited pages. Returns IDs and source URLs.",
          {"query": {"type": "string"}, **PAGING}, []),
    _tool("notion_read_page", "Read a page's title and first 30 content blocks. Use a page_id returned by search. Nested content and pagination are explicit.",
          {"page_id": {"type": "string"}}, ["page_id"]),
    _tool("notion_read_blocks", "Read child blocks or the next page of blocks. Use block IDs / next_cursor returned by previous tools. Does not follow external URLs.",
          {"block_id": {"type": "string"}, **PAGING}, ["block_id"]),
]


class NotionApiError(RuntimeError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _request(path: str, token: str, payload: dict | None = None) -> dict:
    if not token:
        raise NotionApiError("Notion 尚未設定 NOTION_API_KEY；請管理員設定唯讀 Integration 並授權頁面。")
    request = Request(
        "https://api.notion.com/v1/" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION,
                 "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with build_opener(_NoRedirect()).open(request, timeout=25) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        messages = {401: "Notion Token 無效或已撤銷。", 403: "Notion Integration 沒有讀取權限。",
                    404: "Notion 頁面不存在，或尚未分享給此 Integration。",
                    429: "Notion 請求過於頻繁，請稍後重試。"}
        raise NotionApiError(messages.get(exc.code, f"Notion API HTTP {exc.code}，請稍後重試。")) from None
    except (URLError, TimeoutError, OSError):
        raise NotionApiError("無法連線至 Notion API，請檢查網路後重試。") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise NotionApiError("Notion 回傳內容超過大小限制。")
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError):
        raise NotionApiError("Notion API 回傳無效 JSON。") from None
    if not isinstance(result, dict) or result.get("object") == "error":
        raise NotionApiError("Notion API 回傳無效結果。")
    return result


def _id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Notion ID 必須是 UUID，不接受 URL 或路徑。")
    try:
        return str(uuid.UUID(value))
    except ValueError:
        raise ValueError("Notion ID 必須是 UUID，不接受 URL 或路徑。") from None


def _rich_text(items: list) -> str:
    return "".join(str(item.get("plain_text") or (item.get("text") or {}).get("content") or "")
                   for item in items if isinstance(item, dict))


def _page(page: dict) -> dict:
    title = next((_rich_text(prop.get("title") or []) for prop in (page.get("properties") or {}).values()
                  if isinstance(prop, dict) and prop.get("type") == "title"), "")
    page_id = _id(page["id"])
    return {"page_id": page_id, "title": title[:250] or "Untitled",
            "url": "https://www.notion.so/" + page_id.replace("-", ""),
            "last_edited_time": page.get("last_edited_time")}


def _blocks(result: dict) -> dict:
    blocks = []
    remaining = MAX_TEXT_CHARS
    truncated = False
    for item in result.get("results") or []:
        kind = item.get("type", "unknown")
        data = item.get(kind) or {}
        text = _rich_text(data.get("rich_text") or [])
        if kind == "table_row":
            text = " | ".join(_rich_text(cell) for cell in data.get("cells") or [])
        if kind in {"child_page", "child_database"}:
            text = str(data.get("title") or "")
        if kind == "to_do":
            text = ("[x] " if data.get("checked") else "[ ] ") + text
        if len(text) > remaining:
            truncated = True
        clipped = text[:remaining]
        remaining -= len(clipped)
        blocks.append({"block_id": item["id"], "type": kind, "text": clipped,
                       "has_children": bool(item.get("has_children"))})
    return {"blocks": blocks, "has_more": bool(result.get("has_more")),
            "next_cursor": result.get("next_cursor"), "text_truncated": truncated,
            "coverage": "This batch only; nested blocks, linked pages, files and database rows are not expanded."}


def call_notion_tool(name: str, arguments: dict, token: str) -> dict:
    server = {"id": 1, "tools": NOTION_MCP_TOOLS}
    resolve_planned_tool({"server_id": 1, "tool_name": name, "arguments": arguments}, [server])
    cursor = arguments.get("start_cursor")
    if cursor is not None and (not cursor or len(cursor) > 200):
        raise ValueError("start_cursor 必須是前次回傳的游標，長度 1–200。")
    if name == "notion_search":
        query = arguments.get("query", "").strip()
        if len(query) > 200:
            raise ValueError("搜尋標題最多 200 個字元。")
        params = {"query": query, "page_size": arguments.get("page_size", 5),
                  "filter": {"property": "object", "value": "page"},
                  "sort": {"direction": "descending", "timestamp": "last_edited_time"}}
        if cursor:
            params["start_cursor"] = cursor
        result = _request("search", token, params)
        return {"pages": [_page(page) for page in result.get("results") or []],
                "has_more": bool(result.get("has_more")), "next_cursor": result.get("next_cursor"),
                "scope": "Shared page titles only; not full-text search or a complete workspace inventory."}
    if name == "notion_read_page":
        page_id = _id(arguments["page_id"])
        page = _page(_request(f"pages/{page_id}", token))
        return {**page, **_blocks(_request(f"blocks/{page_id}/children?page_size=30", token))}
    block_id = _id(arguments["block_id"])
    params = {"page_size": arguments.get("page_size", 10)}
    if cursor:
        params["start_cursor"] = cursor
    return {"block_id": block_id, **_blocks(_request(f"blocks/{block_id}/children?{urlencode(params)}", token))}


def handle_notion_mcp_request(payload: dict, token: str) -> dict | None:
    request_id = payload.get("id")
    method = payload.get("method")
    envelope = {"jsonrpc": "2.0", "id": request_id}
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return {**envelope, "result": {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                "serverInfo": {"name": "AI Work Notion Read-only", "version": "1.0.0"}}}
    if method == "ping":
        return {**envelope, "result": {}}
    if method == "tools/list":
        return {**envelope, "result": {"tools": NOTION_MCP_TOOLS}}
    if method != "tools/call":
        return {**envelope, "error": {"code": -32601, "message": "Method not found"}}
    params = payload.get("params")
    if not isinstance(params, dict) or not isinstance(params.get("arguments", {}), dict):
        return {**envelope, "error": {"code": -32602, "message": "Invalid tool arguments"}}
    try:
        output = call_notion_tool(str(params.get("name") or ""), params.get("arguments", {}), token)
    except (ValueError, McpPlanningError, NotionApiError) as exc:
        return {**envelope, "result": {"isError": True, "content": [{"type": "text", "text": str(exc)}]}}
    return {**envelope, "result": {"isError": False, "structuredContent": output,
            "content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}]}}
