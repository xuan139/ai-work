from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
MAX_API_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_TEXT_CHARS = 20000
FILE_FIELDS = (
    "id,name,mimeType,createdTime,modifiedTime,size,webViewLink,"
    "owners(displayName,emailAddress),parents,shared,trashed"
)
GOOGLE_EXPORT_TYPES = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}

DRIVE_MCP_TOOLS = [
    {
        "name": "drive_list_recent_files",
        "title": "List Recent Drive Files",
        "description": "List recently modified files accessible to the authorized Google Drive user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "minimum": 1, "maximum": 20, "default": 10},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "drive_search_files",
        "title": "Search Drive Files",
        "description": "Search accessible Google Drive files by a plain title or full-text keyword.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Plain search keyword, not raw Drive query syntax."},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 20, "default": 10},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "drive_get_file_metadata",
        "title": "Get Drive File Metadata",
        "description": "Read metadata for one Google Drive file without downloading its content.",
        "inputSchema": {
            "type": "object",
            "properties": {"file_id": {"type": "string"}},
            "required": ["file_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "drive_read_text_content",
        "title": "Read Drive Text Content",
        "description": (
            "Read bounded text from a Google Doc, Sheet, Slide, or stored text file. "
            "Binary PDF and Office files must first be imported into the NAS document pipeline."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"file_id": {"type": "string"}},
            "required": ["file_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
]


class DriveApiError(RuntimeError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def handle_drive_mcp_request(payload: dict[str, Any], access_token: str) -> dict[str, Any] | None:
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
                "serverInfo": {"name": "AI Work Google Drive Read-only MCP", "version": "1.0.0"},
                "instructions": "Read-only Google Drive access through the stable Drive API.",
            },
        )
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": DRIVE_MCP_TOOLS})
    if method == "tools/call":
        params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
        name = str(params.get("name") or "")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        try:
            output = _call_tool(name, arguments, access_token)
        except (ValueError, DriveApiError) as exc:
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
    if name == "drive_list_recent_files":
        limit = _bounded_limit(arguments.get("max_results"), 10)
        result = _drive_json_request(
            "files",
            access_token,
            _list_query(limit, "modifiedTime desc"),
        )
        files = [_file_summary(item) for item in result.get("files") or [] if isinstance(item, dict)]
        return {"requested_count": limit, "count": len(files), "files": files}
    if name == "drive_search_files":
        keyword = str(arguments.get("query") or "").strip()
        if not keyword:
            raise ValueError("query is required")
        limit = _bounded_limit(arguments.get("max_results"), 10)
        escaped = keyword.replace("\\", "\\\\").replace("'", "\\'")
        drive_query = f"trashed = false and (name contains '{escaped}' or fullText contains '{escaped}')"
        result = _drive_json_request(
            "files",
            access_token,
            _list_query(limit, "modifiedTime desc", drive_query),
        )
        files = [_file_summary(item) for item in result.get("files") or [] if isinstance(item, dict)]
        return {"query": keyword, "count": len(files), "files": files}
    if name == "drive_get_file_metadata":
        file_id = _required_id(arguments)
        return _file_summary(_file_metadata(file_id, access_token))
    if name == "drive_read_text_content":
        file_id = _required_id(arguments)
        metadata = _file_metadata(file_id, access_token)
        mime_type = str(metadata.get("mimeType") or "")
        export_type = GOOGLE_EXPORT_TYPES.get(mime_type)
        if export_type:
            raw, response_type = _drive_bytes_request(
                f"files/{quote(file_id, safe='')}/export",
                access_token,
                [("mimeType", export_type)],
            )
        elif mime_type.startswith("text/") or mime_type in {
            "application/json",
            "application/xml",
            "application/yaml",
            "application/javascript",
        }:
            raw, response_type = _drive_bytes_request(
                f"files/{quote(file_id, safe='')}",
                access_token,
                [("alt", "media"), ("supportsAllDrives", "true")],
            )
            export_type = response_type.split(";", 1)[0] or mime_type
        else:
            raise ValueError(
                "This file is binary. Download it into the NAS document pipeline before asking an LLM to read it."
            )
        text = raw.decode("utf-8-sig", errors="replace")
        return {
            "file": _file_summary(metadata),
            "content_type": export_type,
            "text": text[:MAX_TEXT_CHARS],
            "truncated": len(text) > MAX_TEXT_CHARS,
        }
    raise ValueError(f"Unknown tool: {name}")


def _file_metadata(file_id: str, access_token: str) -> dict[str, Any]:
    return _drive_json_request(
        f"files/{quote(file_id, safe='')}",
        access_token,
        [("fields", FILE_FIELDS), ("supportsAllDrives", "true")],
    )


def _list_query(limit: int, order_by: str, drive_query: str = "trashed = false") -> list[tuple[str, str]]:
    return [
        ("pageSize", str(limit)),
        ("orderBy", order_by),
        ("q", drive_query),
        ("fields", f"nextPageToken,files({FILE_FIELDS})"),
        ("spaces", "drive"),
        ("includeItemsFromAllDrives", "true"),
        ("supportsAllDrives", "true"),
    ]


def _drive_json_request(
    path: str,
    access_token: str,
    query: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    raw, _ = _drive_bytes_request(path, access_token, query)
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DriveApiError("Drive API returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise DriveApiError("Drive API returned an invalid response")
    return result


def _drive_bytes_request(
    path: str,
    access_token: str,
    query: list[tuple[str, str]] | None = None,
) -> tuple[bytes, str]:
    url = f"{DRIVE_API_BASE}/{path}"
    if query:
        url += "?" + urlencode(query)
    request = Request(
        url,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json, text/plain, text/csv"},
    )
    try:
        with build_opener(_NoRedirect).open(request, timeout=20) as response:
            raw = response.read(MAX_API_RESPONSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
    except HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace").strip()
        raise DriveApiError(f"Drive API HTTP {exc.code}: {detail or exc.reason}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise DriveApiError(f"Drive API connection failed: {exc}") from exc
    if len(raw) > MAX_API_RESPONSE_BYTES:
        raise DriveApiError("Drive API response exceeded 2 MB")
    return raw, content_type


def _file_summary(file: dict[str, Any]) -> dict[str, Any]:
    owners = []
    for owner in file.get("owners") or []:
        if isinstance(owner, dict):
            owners.append(
                {key: owner.get(key) for key in ("displayName", "emailAddress") if owner.get(key) is not None}
            )
    return {
        key: value
        for key, value in {
            "file_id": file.get("id"),
            "name": file.get("name"),
            "mime_type": file.get("mimeType"),
            "created_time": file.get("createdTime"),
            "modified_time": file.get("modifiedTime"),
            "size": file.get("size"),
            "web_view_link": file.get("webViewLink"),
            "owners": owners,
            "parents": file.get("parents") or [],
            "shared": file.get("shared"),
        }.items()
        if value is not None
    }


def _required_id(arguments: dict[str, Any]) -> str:
    value = str(arguments.get("file_id") or "").strip()
    if not value:
        raise ValueError("file_id is required")
    return value


def _bounded_limit(value: object, default: int) -> int:
    try:
        limit = int(value) if value is not None else default
    except (TypeError, ValueError) as exc:
        raise ValueError("max_results must be an integer") from exc
    return max(1, min(limit, 20))


def _result(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
