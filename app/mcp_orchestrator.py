from __future__ import annotations

import json
from typing import Any


class McpPlanningError(RuntimeError):
    pass


ODOO_READ_ONLY_TOOLS = {
    "describe_model",
    "export_records",
    "get_access_rights",
    "get_messages",
    "list_languages",
    "list_models",
    "list_modules",
    "print_report",
    "read_group",
    "read_records",
    "read_resource",
    "search_count",
    "search_read",
    "system_info",
    "whoami",
}


def available_mcp_servers(
    servers: list[dict[str, Any]],
    selected_server_id: int | None = None,
) -> list[dict[str, Any]]:
    available: list[dict[str, Any]] = []
    for server in servers:
        if selected_server_id is not None and int(server["id"]) != selected_server_id:
            continue
        if not (
            server.get("is_enabled")
            and server.get("status") == "connected"
            and server.get("transport") == "streamable_http"
            and server.get("endpoint")
        ):
            continue
        try:
            raw_tools = json.loads(server.get("tools_json") or "[]")
        except (TypeError, json.JSONDecodeError):
            raw_tools = []
        tools = [tool for tool in raw_tools if _is_read_only_tool(tool, server)]
        if tools:
            available.append({**server, "tools": tools})
    if selected_server_id is not None and not available:
        raise McpPlanningError("所選 MCP Server 目前沒有可自動執行的唯讀工具")
    return available


def public_mcp_server(server: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": server["id"],
        "slug": server["slug"],
        "name": server["name"],
        "description": server.get("description"),
        "description_en": server.get("description_en"),
        "tool_count": len(server.get("tools") or []),
        "tools": [
            {
                "name": tool.get("name"),
                "title": tool.get("title"),
                "description": tool.get("description"),
            }
            for tool in server.get("tools") or []
        ],
    }


def build_planner_prompt(user_prompt: str, servers: list[dict[str, Any]]) -> str:
    catalog = []
    for server in servers:
        catalog.append(
            {
                "server_id": server["id"],
                "server_name": server["name"],
                "tools": [
                    {
                        "name": tool.get("name"),
                        "description": str(tool.get("description") or "")[:400],
                        "input_schema": _compact_schema(tool.get("inputSchema") or {}),
                    }
                    for tool in server.get("tools") or []
                ],
            }
        )
    return (
        "You are a tool router. Decide whether one read-only MCP tool is needed to answer the user.\n"
        "Return exactly one JSON object and no markdown or explanation.\n"
        "If a tool is useful, return: "
        '{"action":"tool","server_id":1,"tool_name":"name","arguments":{}}.\n'
        "If none is relevant, return: "
        '{"action":"answer","reason":"brief reason"}.\n'
        "Use only the listed server_id and tool name. Arguments must satisfy the input schema.\n\n"
        f"AVAILABLE TOOLS:\n{json.dumps(catalog, ensure_ascii=False, separators=(',', ':'))}\n\n"
        f"USER REQUEST:\n{user_prompt}"
    )


def parse_mcp_plan(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            candidates.append(value)
    if not candidates:
        raise McpPlanningError("LLM 未回傳有效的 MCP 工具規劃")

    plan = next((candidate for candidate in candidates if "action" in candidate), candidates[0])
    action = str(plan.get("action") or "").strip().lower()
    if action == "answer":
        return {"action": "answer", "reason": str(plan.get("reason") or "")[:500]}
    if action != "tool":
        raise McpPlanningError("LLM 回傳的 MCP action 不受支援")
    try:
        server_id = int(plan.get("server_id"))
    except (TypeError, ValueError) as exc:
        raise McpPlanningError("LLM 未指定有效的 MCP Server") from exc
    tool_name = str(plan.get("tool_name") or "").strip()
    arguments = plan.get("arguments")
    if not tool_name or not isinstance(arguments, dict):
        raise McpPlanningError("LLM 未回傳有效的 MCP 工具名稱與參數")
    return {
        "action": "tool",
        "server_id": server_id,
        "tool_name": tool_name,
        "arguments": arguments,
    }


def resolve_planned_tool(
    plan: dict[str, Any],
    servers: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    for server in servers:
        if int(server["id"]) != plan["server_id"]:
            continue
        for tool in server.get("tools") or []:
            if tool.get("name") == plan["tool_name"]:
                return server, tool
    raise McpPlanningError("LLM 選擇了未授權、非唯讀或不存在的 MCP 工具")


def build_final_prompt(
    user_prompt: str,
    server: dict[str, Any],
    tool: dict[str, Any],
    tool_result: dict[str, Any],
) -> str:
    result_text = json.dumps(tool_result, ensure_ascii=False, separators=(",", ":"))
    if len(result_text) > 20000:
        result_text = result_text[:20000] + "...[truncated]"
    return (
        "Answer the user's original request using the MCP tool result below. "
        "Answer in the same language as the user, using Traditional Chinese for Chinese. "
        "Do not invent facts not present in the tool result. Mention the MCP source and tool once.\n\n"
        f"ORIGINAL USER REQUEST:\n{user_prompt}\n\n"
        f"MCP SOURCE:\n{server['name']} / {tool['name']}\n\n"
        f"MCP TOOL RESULT:\n{result_text}"
    )


def _is_read_only_tool(tool: object, server: dict[str, Any]) -> bool:
    if not isinstance(tool, dict) or not tool.get("name"):
        return False
    endpoint = str(server.get("endpoint") or "").rstrip("/")
    if server.get("slug") == "linear" and endpoint == "https://mcp.linear.app/mcp/readonly":
        return True
    if server.get("slug") == "odoo":
        return str(tool["name"]) in ODOO_READ_ONLY_TOOLS
    annotations = tool.get("annotations")
    return bool(
        isinstance(annotations, dict)
        and annotations.get("readOnlyHint") is True
        and annotations.get("destructiveHint") is not True
    )


def _compact_schema(schema: object) -> dict[str, Any]:
    if not isinstance(schema, dict):
        return {"type": "object"}
    compact: dict[str, Any] = {"type": schema.get("type", "object")}
    properties = schema.get("properties")
    if isinstance(properties, dict):
        compact["properties"] = {
            name: {
                key: value
                for key, value in definition.items()
                if key in {"type", "enum", "minimum", "maximum", "default"}
            }
            for name, definition in properties.items()
            if isinstance(definition, dict)
        }
    if isinstance(schema.get("required"), list):
        compact["required"] = schema["required"]
    if schema.get("additionalProperties") is False:
        compact["additionalProperties"] = False
    return compact
