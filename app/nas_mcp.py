from __future__ import annotations

import json
from typing import Any


NAS_MCP_TOOLS = [
    {
        "name": "nas_get_system_status",
        "title": "NAS System Status",
        "description": "Return read-only demo health, storage, RAID, and service status for the AI Work NAS.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "nas_list_shared_folders",
        "title": "List NAS Shared Folders",
        "description": "List demo NAS shares and their data purpose without exposing real files.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "nas_search_demo_files",
        "title": "Search Demo NAS Files",
        "description": "Search a fixed demo file catalog by title or file type.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Title or file-type keyword."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "nas_get_recent_activity",
        "title": "Recent NAS Activity",
        "description": "Return fixed demo processing events for uploads, transcription, OCR, and backup.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
]


DEMO_FILES = [
    {"name": "2026-09-16-AI-Work-meeting.pdf", "type": "pdf", "share": "Documents", "status": "indexed"},
    {"name": "quarterly-product-review.m4a", "type": "audio", "share": "Meetings", "status": "transcribed"},
    {"name": "warehouse-camera-01.mp4", "type": "video", "share": "Media", "status": "analyzed"},
    {"name": "NAS-deployment-guide.docx", "type": "docx", "share": "Documents", "status": "indexed"},
    {"name": "rack-layout.png", "type": "image", "share": "Media", "status": "ocr_complete"},
]


def handle_nas_mcp_request(payload: dict[str, Any]) -> dict[str, Any] | None:
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
                "serverInfo": {"name": "AI Work NAS Demo MCP", "version": "1.0.0"},
                "instructions": "Read-only demo data. No real NAS files or company records are exposed.",
            },
        )
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": NAS_MCP_TOOLS})
    if method == "tools/call":
        params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
        name = str(params.get("name") or "")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        try:
            output = _call_tool(name, arguments)
        except ValueError as exc:
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


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "nas_get_system_status":
        return {
            "demo": True,
            "hostname": "ai-work-nas-demo",
            "status": "online",
            "raid": {"level": "RAID 5", "health": "normal", "disks": 4},
            "storage": {"total_tb": 16, "used_tb": 5.8, "free_tb": 10.2},
            "services": {"rag_index": "ready", "media_worker": "ready", "snapshot": "protected"},
        }
    if name == "nas_list_shared_folders":
        return {
            "demo": True,
            "shares": [
                {"name": "Documents", "path": "/AIWork/Documents", "purpose": "PDF, DOCX, and RAG sources"},
                {"name": "Meetings", "path": "/AIWork/Meetings", "purpose": "Audio, transcripts, and minutes"},
                {"name": "Media", "path": "/AIWork/Media", "purpose": "Video, images, and analysis results"},
            ],
        }
    if name == "nas_search_demo_files":
        query = str(arguments.get("query") or "").strip().lower()
        if not query:
            raise ValueError("query is required")
        limit = _bounded_limit(arguments.get("limit"), 5)
        matches = [item for item in DEMO_FILES if query in item["name"].lower() or query in item["type"]]
        return {"demo": True, "query": query, "count": len(matches[:limit]), "files": matches[:limit]}
    if name == "nas_get_recent_activity":
        limit = _bounded_limit(arguments.get("limit"), 5)
        activity = [
            {"time": "09:42", "event": "PDF indexed", "target": "2026-09-16-AI-Work-meeting.pdf"},
            {"time": "09:35", "event": "Transcript completed", "target": "quarterly-product-review.m4a"},
            {"time": "09:22", "event": "Video analysis completed", "target": "warehouse-camera-01.mp4"},
            {"time": "09:10", "event": "Snapshot completed", "target": "AIWork dataset"},
        ]
        return {"demo": True, "activity": activity[:limit]}
    raise ValueError(f"Unknown tool: {name}")


def _bounded_limit(value: object, default: int) -> int:
    try:
        limit = int(value) if value is not None else default
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    return max(1, min(limit, 10))


def _result(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
