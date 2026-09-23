import asyncio
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote, urlparse

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.auth import SESSION_COOKIE, authenticate, create_session_token, current_user, hash_password, require_admin, require_meeting_access, websocket_user
from app.analysis_persistence import persist_cloud_asset_analysis
from app.asset_normalization import convert_asset_to_traditional
from app.asr_catalog import asr_model_summary, find_asr_model
from app.asr_service import run_asr_with_audit
from app.db import (
    create_mcp_audit_log,
    create_mcp_server,
    create_llm_call,
    create_line_document,
    create_meeting,
    create_nas_asset,
    create_user,
    delete_custom_model,
    delete_user,
    finish_line_document,
    get_exact_line_query_cache,
    get_line_document,
    get_line_source,
    get_line_source_month_usage,
    get_document_chunk,
    get_meeting,
    get_meeting_by_nas_asset_id,
    get_mcp_server,
    get_nas_asset,
    get_custom_model,
    get_user_by_id,
    get_user_by_username,
    embedding_coverage,
    init_db,
    list_document_chunks,
    list_asset_ai_analyses,
    list_line_query_cache_candidates,
    list_line_sources,
    list_line_source_assets,
    list_llm_calls,
    list_meetings,
    list_mcp_servers,
    list_nas_assets,
    list_network_assets,
    list_pending_network_assets,
    list_custom_models,
    list_users,
    mark_line_query_cache_hit,
    mark_user_login,
    reset_user_password,
    save_line_query_cache,
    search_document_chunks,
    seed_admin,
    update_user_access,
    update_line_source_policy,
    update_custom_model_validation,
    update_meeting_asr_selection,
    update_meeting_status,
    update_mcp_server,
    update_mcp_server_sync,
    update_nas_asset,
    update_nas_asset_processor_config,
    upsert_line_source,
    user_owned_record_count,
)
from app.document_processing import analyzer_for_category, classify_asset, process_nas_asset
from app.embedding_runtime import (
    EMBEDDING_MODEL,
    cosine_similarity,
    embed_query,
    embedding_backfill_loop,
    embedding_service_status,
    hybrid_search_document_chunks,
    pack_embedding,
    unpack_embedding,
)
from app.llm_catalog import PRICING_UPDATED_AT, get_model, model_summary, provider_summary
from app.llm_cache import lookup_llm_cache, normalize_llm_prompt, store_llm_cache, suggest_llm_prompts
from app.llm_runtime import LlmRuntimeError, company_api_key_for_model, run_llm
from app.drive_mcp import DRIVE_MCP_TOOLS, handle_drive_mcp_request
from app.excel_mcp import EXCEL_MCP_TOOLS, handle_excel_mcp_request
from app.gmail_mcp import GMAIL_MCP_TOOLS, handle_gmail_mcp_request
from app.line_service import LineServiceError, list_line_groups, push_line_messages
from app.local_model_manager import (
    cancel_download,
    download_in_progress,
    list_local_model_statuses,
    local_model_status,
    start_download,
    validate_custom_file_model,
)
from app.media_segmentation import archived_media_segment_path, list_archived_media_segments
from app.media_worker import enqueue_media_job, start_media_workers, stop_media_workers
from app.mcp_orchestrator import (
    McpPlanningError,
    available_mcp_servers,
    build_final_prompt,
    build_planner_prompt,
    parse_mcp_plan,
    public_mcp_server,
    resolve_planned_tool,
)
from app.mcp_runtime import (
    McpConnectionError,
    call_streamable_http_tool,
    mcp_auth_configured,
    oauth_access_token,
    sync_streamable_http_tools,
    validate_mcp_endpoint,
)
from app.model_registry import custom_model_to_catalog, register_custom_model
from app.nas import ensure_storage_dirs, nas_discovery_loop
from app.nas_mcp import NAS_MCP_TOOLS, handle_nas_mcp_request
from app.network_import import download_youtube_asset, validate_youtube_url
from app.n8n_service import n8n_service_status
from app.notifications import manager
from app.rag_cache import lookup_rag_cache, normalize_query, store_rag_cache
from app.segment_transcriptions import list_audio_segment_transcriptions, update_audio_segment_transcription
from app.system_asr import current_asr_model, current_asr_state, update_current_asr
from app.system_llm import current_llm_model, current_llm_state, update_current_llm
from app.translation_service import TARGET_LANGUAGES
from app.upload_storage import UploadTooLargeError, save_upload_stream
from app.video_catalog import get_video_model, video_model_summary
from app.wiki_service import search_wiki, wiki_backfill_loop, wiki_detail

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
RECORDINGS_DIR = BASE_DIR / "storage" / "recordings"
NAS_ASSETS_DIR = BASE_DIR / "storage" / "nas_assets"
LLM_RUN_LOCKS: dict[tuple[int, str], asyncio.Lock] = {}
VIDEO_PREVIEWS_DIR = BASE_DIR / "storage" / "video_previews"
NATIVE_BROWSER_VIDEO_SUFFIXES = {".mp4", ".m4v", ".mov", ".webm"}
VIDEO_PLAYBACK_LOCKS: dict[int, asyncio.Lock] = {}
ACTIVE_SEGMENT_TRANSCRIPTIONS: set[tuple[int, int]] = set()


def save_uploaded_file(upload: UploadFile, destination: Path) -> int:
    try:
        return save_upload_stream(upload.file, destination)
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc


def audio_content_type(filename: str, declared_type: str | None = None) -> str:
    if declared_type and declared_type.startswith("audio/"):
        return declared_type
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def video_content_type(filename: str, declared_type: str | None = None) -> str:
    if declared_type and declared_type.startswith("video/"):
        return declared_type
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def browser_video_path(asset: dict) -> Path:
    source = Path(asset["stored_path"])
    if source.suffix.lower() in NATIVE_BROWSER_VIDEO_SUFFIXES:
        return source
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("此影片格式需要 FFmpeg 轉換為瀏覽器可播放的 MP4")
    VIDEO_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    preview = VIDEO_PREVIEWS_DIR / f"asset-{asset['id']}.mp4"
    if preview.is_file() and preview.stat().st_mtime_ns >= source.stat().st_mtime_ns:
        return preview
    temporary = preview.with_suffix(".tmp.mp4")
    completed = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(temporary),
        ],
        capture_output=True,
        text=True,
        timeout=int(os.environ.get("VIDEO_PLAYBACK_TRANSCODE_TIMEOUT_SECONDS", "14400")),
        check=False,
    )
    if completed.returncode != 0 or not temporary.is_file():
        temporary.unlink(missing_ok=True)
        detail = " ".join((completed.stderr or completed.stdout or "未知錯誤").split())[-500:]
        raise RuntimeError(f"影片播放格式轉換失敗：{detail}")
    temporary.replace(preview)
    return preview


def merge_transcript_chunks(chunks: list[dict]) -> str:
    parts = [str(chunk.get("content") or "").strip() for chunk in chunks]
    parts = [part for part in parts if part]
    if not parts:
        return ""
    transcript = parts[0]
    for part in parts[1:]:
        overlap = 0
        for size in range(min(len(transcript), len(part), 240), 0, -1):
            if transcript.endswith(part[:size]):
                overlap = size
                break
        transcript += part[overlap:] if overlap else f"\n\n{part}"
    return transcript.strip()


def transcript_download_response(content: str, filename: str) -> Response:
    fallback = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip("-") or "transcript.txt"
    disposition = f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename)}"
    return Response(
        content=("\ufeff" + content).encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": disposition},
    )


def segment_transcription_payload(asset_id: int, segment_index: int, record: dict | None) -> dict | None:
    if not record:
        return None
    result = dict(record)
    if str(result.get("transcript") or "").strip():
        result["download_url"] = (
            f"/api/nas-assets/{asset_id}/audio-segments/{segment_index}/transcript/download"
        )
    return result


def load_project_env(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


load_project_env(BASE_DIR / ".env")


def server_api_key_for_model(model: dict) -> str | None:
    return company_api_key_for_model(model)


def with_server_key_status(model: dict) -> dict:
    return {**model, "server_key_configured": bool(server_api_key_for_model(model))}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage_dirs(BASE_DIR)
    init_db()
    seed_admin(hash_password("admin123"))
    nas_demo_server = next((item for item in list_mcp_servers() if item.get("slug") == "nas-demo"), None)
    if nas_demo_server:
        update_mcp_server_sync(
            nas_demo_server["id"],
            status="connected",
            protocol_version="2025-06-18",
            tools_json=json.dumps(NAS_MCP_TOOLS, ensure_ascii=False),
            tool_count=len(NAS_MCP_TOOLS),
            last_error=None,
        )
    gmail_server = next((item for item in list_mcp_servers() if item.get("slug") == "gmail"), None)
    if (
        gmail_server
        and gmail_server.get("is_enabled")
        and gmail_server.get("endpoint") == "http://127.0.0.1:8000/mcp/gmail"
        and mcp_auth_configured(gmail_server)
        and all(os.getenv(name) for name in ("GMAIL_MCP_CLIENT_ID", "GMAIL_MCP_CLIENT_SECRET", "GMAIL_MCP_REFRESH_TOKEN"))
    ):
        update_mcp_server_sync(
            gmail_server["id"],
            status="connected",
            protocol_version="2025-06-18",
            tools_json=json.dumps(GMAIL_MCP_TOOLS, ensure_ascii=False),
            tool_count=len(GMAIL_MCP_TOOLS),
            last_error=None,
        )
    drive_server = next((item for item in list_mcp_servers() if item.get("slug") == "google-drive"), None)
    if (
        drive_server
        and drive_server.get("is_enabled")
        and drive_server.get("endpoint") == "http://127.0.0.1:8000/mcp/google-drive"
        and mcp_auth_configured(drive_server)
        and all(
            os.getenv(name)
            for name in (
                "GOOGLE_DRIVE_MCP_CLIENT_ID",
                "GOOGLE_DRIVE_MCP_CLIENT_SECRET",
                "GOOGLE_DRIVE_MCP_REFRESH_TOKEN",
            )
        )
    ):
        update_mcp_server_sync(
            drive_server["id"],
            status="connected",
            protocol_version="2025-06-18",
            tools_json=json.dumps(DRIVE_MCP_TOOLS, ensure_ascii=False),
            tool_count=len(DRIVE_MCP_TOOLS),
            last_error=None,
        )
    excel_server = next((item for item in list_mcp_servers() if item.get("slug") == "nas-excel"), None)
    if (
        excel_server
        and excel_server.get("is_enabled")
        and excel_server.get("endpoint") == "http://127.0.0.1:8000/mcp/excel"
        and mcp_auth_configured(excel_server)
    ):
        update_mcp_server_sync(
            excel_server["id"],
            status="connected",
            protocol_version="2025-06-18",
            tools_json=json.dumps(EXCEL_MCP_TOOLS, ensure_ascii=False),
            tool_count=len(EXCEL_MCP_TOOLS),
            last_error=None,
        )
    await start_media_workers()
    tasks = [
        asyncio.create_task(nas_discovery_loop(BASE_DIR)),
        asyncio.create_task(embedding_backfill_loop()),
        asyncio.create_task(wiki_backfill_loop()),
    ]
    for asset in list_pending_network_assets():
        config = parse_processor_config(asset)
        tasks.append(
            asyncio.create_task(
                download_youtube_asset(
                    asset["id"],
                    asset["source_url"],
                    asset["category"],
                    str(config.get("requested_title") or ""),
                )
            )
        )
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        await stop_media_workers()


app = FastAPI(title="AI Work Meeting Demo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/mcp/nas")
async def nas_demo_mcp_info() -> dict:
    return {
        "name": "AI Work NAS Demo MCP",
        "transport": "streamable_http",
        "endpoint": "/mcp/nas",
        "protocol_version": "2025-06-18",
        "read_only": True,
        "demo_data_only": True,
        "tools": [tool["name"] for tool in NAS_MCP_TOOLS],
    }


@app.post("/mcp/nas")
async def nas_demo_mcp(payload: dict) -> Response:
    result = handle_nas_mcp_request(payload)
    if result is None:
        return Response(status_code=204)
    return JSONResponse(result)


@app.get("/mcp/gmail")
async def gmail_mcp_info() -> dict:
    return {
        "name": "AI Work Gmail Read-only MCP",
        "transport": "streamable_http",
        "endpoint": "/mcp/gmail",
        "protocol_version": "2025-06-18",
        "read_only": True,
        "tools": [tool["name"] for tool in GMAIL_MCP_TOOLS],
    }


@app.post("/mcp/gmail")
async def gmail_mcp(request: Request, payload: dict) -> Response:
    expected_key = os.getenv("GMAIL_LOCAL_MCP_KEY", "")
    supplied = request.headers.get("authorization", "")
    if not expected_key:
        raise HTTPException(status_code=503, detail="Gmail MCP 尚未設定內部存取金鑰")
    if not hmac.compare_digest(supplied, f"Bearer {expected_key}"):
        raise HTTPException(status_code=401, detail="Gmail MCP authorization failed")
    try:
        token = await asyncio.to_thread(oauth_access_token, "GMAIL_MCP_TOKEN")
    except McpConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    result = await asyncio.to_thread(handle_gmail_mcp_request, payload, token)
    if result is None:
        return Response(status_code=204)
    return JSONResponse(result)


@app.get("/mcp/google-drive")
async def google_drive_mcp_info() -> dict:
    return {
        "name": "AI Work Google Drive Read-only MCP",
        "transport": "streamable_http",
        "endpoint": "/mcp/google-drive",
        "protocol_version": "2025-06-18",
        "read_only": True,
        "tools": [tool["name"] for tool in DRIVE_MCP_TOOLS],
    }


@app.post("/mcp/google-drive")
async def google_drive_mcp(request: Request, payload: dict) -> Response:
    expected_key = os.getenv("GOOGLE_DRIVE_LOCAL_MCP_KEY", "")
    supplied = request.headers.get("authorization", "")
    if not expected_key:
        raise HTTPException(status_code=503, detail="Google Drive MCP 尚未設定內部存取金鑰")
    if not hmac.compare_digest(supplied, f"Bearer {expected_key}"):
        raise HTTPException(status_code=401, detail="Google Drive MCP authorization failed")
    try:
        token = await asyncio.to_thread(oauth_access_token, "GOOGLE_DRIVE_MCP_TOKEN")
    except McpConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    result = await asyncio.to_thread(handle_drive_mcp_request, payload, token)
    if result is None:
        return Response(status_code=204)
    return JSONResponse(result)


@app.get("/mcp/excel")
async def excel_mcp_info() -> dict:
    return {
        "name": "AI Work NAS Excel/CSV SQL MCP",
        "transport": "streamable_http",
        "endpoint": "/mcp/excel",
        "protocol_version": "2025-06-18",
        "read_only": True,
        "tools": [tool["name"] for tool in EXCEL_MCP_TOOLS],
    }


@app.post("/mcp/excel")
async def excel_mcp(request: Request, payload: dict) -> Response:
    expected_key = os.getenv("NAS_EXCEL_LOCAL_MCP_KEY", "")
    supplied = request.headers.get("authorization", "")
    if not expected_key:
        raise HTTPException(status_code=503, detail="NAS Excel MCP 尚未設定內部存取金鑰")
    if not hmac.compare_digest(supplied, f"Bearer {expected_key}"):
        raise HTTPException(status_code=401, detail="NAS Excel MCP authorization failed")
    result = await asyncio.to_thread(handle_excel_mcp_request, payload)
    if result is None:
        return Response(status_code=204)
    return JSONResponse(result)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(
        STATIC_DIR / "index.html",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/manifest.webmanifest", include_in_schema=False)
async def web_app_manifest() -> FileResponse:
    return FileResponse(
        STATIC_DIR / "manifest.webmanifest",
        media_type="application/manifest+json",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/sw.js", include_in_schema=False)
async def service_worker() -> FileResponse:
    return FileResponse(
        STATIC_DIR / "sw.js",
        media_type="application/javascript",
        headers={
            "Cache-Control": "no-cache",
            "Service-Worker-Allowed": "/",
        },
    )


@app.post("/auth/login")
async def login(payload: dict[str, str]) -> JSONResponse:
    user = authenticate(payload.get("username", ""), payload.get("password", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    mark_user_login(user["id"])
    response = JSONResponse({"id": user["id"], "username": user["username"], "role": user["role"]})
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user["id"], int(user.get("session_version", 1))),
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return response


@app.post("/auth/logout")
async def logout() -> JSONResponse:
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/auth/me")
async def me(user: dict = Depends(current_user)) -> dict:
    return {"id": user["id"], "username": user["username"], "role": user["role"]}


@app.get("/auth/n8n", include_in_schema=False)
async def n8n_proxy_auth(admin: dict = Depends(require_admin)) -> Response:
    return Response(status_code=204)


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,31}$")
VALID_ROLES = {"admin", "user"}
MCP_SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
MCP_ENV_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")
MCP_TRANSPORTS = {"streamable_http", "sse", "stdio"}
MCP_AUTH_TYPES = {"none", "bearer", "oauth2", "managed", "custom"}


def validate_username(value: object) -> str:
    username = str(value or "").strip()
    if not USERNAME_PATTERN.fullmatch(username):
        raise HTTPException(status_code=400, detail="Username must be 3-32 characters using letters, numbers, dot, underscore, or hyphen")
    return username


def validate_password(value: object) -> str:
    password = str(value or "")
    if len(password) < 8 or len(password) > 128:
        raise HTTPException(status_code=400, detail="Password must be 8-128 characters")
    return password


def validate_role(value: object) -> str:
    role = str(value or "user").strip().lower()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Role must be admin or user")
    return role


@app.get("/api/admin/users")
async def admin_users(q: str | None = None, admin: dict = Depends(require_admin)) -> list[dict]:
    return list_users(q=q)


@app.get("/api/admin/n8n/status")
async def admin_n8n_status(admin: dict = Depends(require_admin)) -> dict:
    return await asyncio.to_thread(n8n_service_status)


@app.post("/api/admin/users", status_code=201)
async def admin_create_user(payload: dict, admin: dict = Depends(require_admin)) -> dict:
    username = validate_username(payload.get("username"))
    password = validate_password(payload.get("password"))
    role = validate_role(payload.get("role"))
    try:
        user = create_user(username=username, password_hash=hash_password(password), role=role)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Username already exists") from exc
    return {"id": user["id"], "username": user["username"], "role": user["role"], "is_active": user["is_active"]}


@app.patch("/api/admin/users/{user_id}")
async def admin_update_user(user_id: int, payload: dict, admin: dict = Depends(require_admin)) -> dict:
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    role = validate_role(payload.get("role", target["role"]))
    if "is_active" in payload and not isinstance(payload["is_active"], bool):
        raise HTTPException(status_code=400, detail="is_active must be a boolean")
    is_active = payload.get("is_active", bool(target["is_active"]))
    if user_id == admin["id"] and (role != "admin" or not is_active):
        raise HTTPException(status_code=400, detail="You cannot deactivate or remove your own administrator access")
    updated = update_user_access(user_id, role=role, is_active=is_active)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": updated["id"], "username": updated["username"], "role": updated["role"], "is_active": updated["is_active"]}


@app.post("/api/admin/users/{user_id}/reset-password")
async def admin_reset_password(user_id: int, payload: dict, admin: dict = Depends(require_admin)) -> dict:
    if not get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    password = validate_password(payload.get("password"))
    updated = reset_user_password(user_id, hash_password(password))
    return {"ok": bool(updated)}


@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: int, admin: dict = Depends(require_admin)) -> dict:
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id == admin["id"] or target["role"] == "admin":
        raise HTTPException(status_code=400, detail="Administrator accounts cannot be deleted")
    if user_owned_record_count(user_id):
        raise HTTPException(status_code=409, detail="This account owns NAS records and must be deactivated instead")
    return {"ok": delete_user(user_id)}


def serialize_mcp_server(server: dict) -> dict:
    result = dict(server)
    try:
        result["tools"] = json.loads(result.pop("tools_json") or "[]")
    except json.JSONDecodeError:
        result["tools"] = []
    try:
        result["headers"] = json.loads(result.pop("headers_json") or "{}")
    except json.JSONDecodeError:
        result["headers"] = {}
    result["auth_configured"] = mcp_auth_configured(result)
    result["is_enabled"] = bool(result.get("is_enabled"))
    public_endpoints = {
        "nas-demo": "/mcp/nas",
        "gmail": "/mcp/gmail",
        "google-drive": "/mcp/google-drive",
        "nas-excel": "/mcp/excel",
    }
    result["public_endpoint"] = public_endpoints.get(result.get("slug"))
    return result


def validate_mcp_server_payload(payload: dict, existing: dict | None = None) -> dict:
    current = existing or {}
    slug = str(payload.get("slug", current.get("slug", ""))).strip().lower()
    name = str(payload.get("name", current.get("name", ""))).strip()
    description = str(payload.get("description", current.get("description", ""))).strip()
    description_en = str(payload.get("description_en", current.get("description_en", ""))).strip()
    transport = str(payload.get("transport", current.get("transport", "streamable_http"))).strip()
    endpoint = str(payload.get("endpoint", current.get("endpoint", "")) or "").strip()
    source_url = str(payload.get("source_url", current.get("source_url", "")) or "").strip()
    auth_type = str(payload.get("auth_type", current.get("auth_type", "none")) or "none").strip()
    auth_env_var = str(payload.get("auth_env_var", current.get("auth_env_var", "")) or "").strip()
    is_enabled = payload.get("is_enabled", bool(current.get("is_enabled", False)))

    if not MCP_SLUG_PATTERN.fullmatch(slug):
        raise HTTPException(status_code=400, detail="MCP slug 必須是 2–64 個小寫英數字或連字號")
    if not 2 <= len(name) <= 100:
        raise HTTPException(status_code=400, detail="MCP 名稱必須是 2–100 個字元")
    if len(description) > 500 or len(description_en) > 500:
        raise HTTPException(status_code=400, detail="MCP 說明不可超過 500 個字元")
    if transport not in MCP_TRANSPORTS:
        raise HTTPException(status_code=400, detail="不支援此 MCP transport")
    if auth_type not in MCP_AUTH_TYPES:
        raise HTTPException(status_code=400, detail="不支援此 MCP 認證類型")
    if not isinstance(is_enabled, bool):
        raise HTTPException(status_code=400, detail="is_enabled 必須是 boolean")
    if auth_env_var and not MCP_ENV_PATTERN.fullmatch(auth_env_var):
        raise HTTPException(status_code=400, detail="認證環境變數名稱格式不正確")
    if endpoint and transport in {"streamable_http", "sse"}:
        try:
            endpoint = validate_mcp_endpoint(endpoint)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if len(endpoint) > 500:
        raise HTTPException(status_code=400, detail="MCP Endpoint 不可超過 500 個字元")
    if source_url:
        source = urlparse(source_url)
        if source.scheme not in {"http", "https"} or not source.hostname:
            raise HTTPException(status_code=400, detail="官方來源必須是有效的 HTTP 或 HTTPS URL")
    if len(source_url) > 500:
        raise HTTPException(status_code=400, detail="官方來源 URL 不可超過 500 個字元")
    return {
        "slug": slug,
        "name": name,
        "description": description or None,
        "description_en": description_en or None,
        "transport": transport,
        "endpoint": endpoint or None,
        "source_url": source_url or None,
        "auth_type": auth_type,
        "auth_env_var": auth_env_var or None,
        "is_enabled": is_enabled,
    }


@app.get("/api/admin/mcp/servers")
async def admin_mcp_servers(admin: dict = Depends(require_admin)) -> dict:
    return {"servers": [serialize_mcp_server(server) for server in list_mcp_servers()]}


@app.get("/api/mcp/available")
async def available_mcp_tools(user: dict = Depends(current_user)) -> dict:
    servers = available_mcp_servers(list_mcp_servers())
    return {"servers": [public_mcp_server(server) for server in servers]}


@app.post("/api/admin/mcp/servers", status_code=201)
async def admin_create_mcp_server(payload: dict, admin: dict = Depends(require_admin)) -> dict:
    values = validate_mcp_server_payload(payload)
    values["created_by"] = admin["id"]
    try:
        server = create_mcp_server(values)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="MCP slug 已存在") from exc
    return serialize_mcp_server(server)


@app.patch("/api/admin/mcp/servers/{server_id}")
async def admin_update_mcp_server(
    server_id: int,
    payload: dict,
    admin: dict = Depends(require_admin),
) -> dict:
    existing = get_mcp_server(server_id)
    if not existing:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    values = validate_mcp_server_payload(payload, existing)
    try:
        server = update_mcp_server(server_id, values)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="MCP slug 已存在") from exc
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    return serialize_mcp_server(server)


@app.post("/api/admin/mcp/servers/{server_id}/sync")
async def admin_sync_mcp_server(server_id: int, admin: dict = Depends(require_admin)) -> dict:
    server = get_mcp_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    if not server.get("endpoint"):
        raise HTTPException(status_code=400, detail="請先設定 MCP Endpoint")
    if not server.get("is_enabled"):
        raise HTTPException(status_code=400, detail="請先啟用 MCP Server")
    try:
        result = await asyncio.to_thread(sync_streamable_http_tools, server)
    except (McpConnectionError, ValueError) as exc:
        updated = update_mcp_server_sync(
            server_id,
            status="failed",
            protocol_version=None,
            tools_json=None,
            tool_count=0,
            last_error=str(exc),
        )
        create_mcp_audit_log(
            server_id=server_id,
            user_id=admin["id"],
            action="tools/list",
            status="failed",
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    tools_json = json.dumps(result["tools"], ensure_ascii=False)
    updated = update_mcp_server_sync(
        server_id,
        status="connected",
        protocol_version=result["protocol_version"],
        tools_json=tools_json,
        tool_count=len(result["tools"]),
        last_error=None,
    )
    create_mcp_audit_log(
        server_id=server_id,
        user_id=admin["id"],
        action="tools/list",
        status="completed",
        output_json=json.dumps(
            {
                "protocol_version": result["protocol_version"],
                "server_info": result["server_info"],
                "tool_names": [tool["name"] for tool in result["tools"]],
            },
            ensure_ascii=False,
        ),
    )
    return serialize_mcp_server(updated or server)


@app.post("/api/meetings/upload")
async def upload_meeting(
    title: str = Form(default=""),
    asr_model_id: str = Form(default=""),
    asr_api_key: str = Form(default=""),
    translation_enabled: str = Form(default="false"),
    translation_target: str = Form(default="zh-Hant"),
    translation_model_id: str = Form(default="local:qwen3-4b"),
    translation_api_key: str = Form(default=""),
    line_push_enabled: str = Form(default="false"),
    line_group_id: str = Form(default=""),
    line_group_name: str = Form(default=""),
    line_push_full_transcript: str = Form(default="false"),
    audio: UploadFile = File(...),
    user: dict = Depends(current_user),
) -> dict:
    asr_model = current_asr_model()
    selected_key = server_api_key_for_model(asr_model)
    if asr_model["requires_api_key"] and not selected_key:
        raise HTTPException(status_code=400, detail=f"系統語音模型 {asr_model['name']} 需要公司 API Key")
    translate, translation_model, selected_translation_key = validate_translation_selection(
        enabled=translation_enabled,
        target=translation_target,
        model_id=translation_model_id,
        api_key=translation_api_key,
    )
    push_to_line = line_push_enabled.strip().lower() in {"1", "true", "yes", "on"}
    push_full_transcript = line_push_full_transcript.strip().lower() in {"1", "true", "yes", "on"}
    selected_line_group = line_group_id.strip() or None
    if push_to_line and not selected_line_group:
        raise HTTPException(status_code=400, detail="請選擇要接收會議摘要的 LINE 群組")

    suffix = Path(audio.filename or "recording.webm").suffix.lower() or ".webm"
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    stored_path = RECORDINGS_DIR / stored_name

    save_uploaded_file(audio, stored_path)

    meeting_title = title.strip() or Path(audio.filename or "瀏覽器錄音").stem or "瀏覽器錄音"
    processor_config = {
        "asr_model_id": asr_model["id"],
        "asr_provider": asr_model["provider"],
        "asr_model": asr_model["name"],
        "asr_engine": asr_model["engine"],
        "asr_requires_api_key": asr_model["requires_api_key"],
        "source": "browser_recording",
        "translation_enabled": translate,
        "translation_target": translation_target if translate else None,
        "translation_model_id": translation_model["id"] if translation_model else None,
        "translation_provider": translation_model["provider"] if translation_model else None,
        "translation_model": translation_model["name"] if translation_model else None,
        "line_push_enabled": push_to_line,
        "line_group_id": selected_line_group,
        "line_group_name": line_group_name.strip() or None,
        "line_push_full_transcript": push_full_transcript,
    }
    asset = create_nas_asset(
        user_id=user["id"],
        category="audio",
        title=meeting_title,
        original_filename=audio.filename or stored_name,
        stored_path=str(stored_path),
        mime_type=audio.content_type,
        file_size=stored_path.stat().st_size,
        status="processing",
        analyzer=asr_model["name"],
        processor_config_json=json.dumps(processor_config, ensure_ascii=False),
    )
    meeting = create_meeting(
        user_id=user["id"],
        source="web_upload",
        title=meeting_title,
        original_filename=audio.filename or stored_name,
        audio_path=str(stored_path),
        status="processing",
        nas_asset_id=asset["id"],
        asr_model_id=asr_model["id"],
        asr_provider=asr_model["provider"],
        asr_model=asr_model["name"],
        asr_engine=asr_model["engine"],
        translation_enabled=translate,
        translation_target=translation_target if translate else None,
        translation_model_id=translation_model["id"] if translation_model else None,
        translation_provider=translation_model["provider"] if translation_model else None,
        translation_model=translation_model["name"] if translation_model else None,
        line_push_enabled=push_to_line,
        line_group_id=selected_line_group,
        line_group_name=line_group_name.strip() or None,
        line_push_full_transcript=push_full_transcript,
    )
    await enqueue_media_job(
        "meeting",
        meeting["id"],
        audio_api_key=selected_key,
        translation_api_key=selected_translation_key,
    )
    await manager.broadcast(
        {
            "type": "meeting_detected",
            "meeting_id": meeting["id"],
            "title": meeting["title"],
            "message": f"錄音《{meeting['title']}》已保存，正在交給 {asr_model['name']} 處理",
            "meeting": meeting,
        }
    )
    return meeting


@app.get("/api/meetings")
async def meetings(q: str | None = None, user: dict = Depends(current_user)) -> list[dict]:
    return list_meetings(user_id=user["id"], role=user["role"], q=q)


@app.get("/api/line/groups")
async def line_groups(user: dict = Depends(current_user)) -> dict:
    try:
        groups = await list_line_groups()
    except LineServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    owner = line_integration_owner()
    approved_groups = []
    for group in groups:
        group_id = str(group.get("id", "")).strip()
        if not group_id:
            continue
        source = upsert_line_source(
            source_id=group_id,
            source_type="group",
            display_name=str(group.get("name", "")).strip() or None,
            owner_user_id=owner["id"],
            is_approved=False,
        )
        if source.get("is_approved"):
            approved_groups.append(group)
    return {"groups": approved_groups}


@app.get("/api/meetings/{meeting_id}")
async def meeting_detail(meeting_id: int, user: dict = Depends(current_user)) -> dict:
    return require_meeting_access(get_meeting(meeting_id), user)


@app.get("/api/meetings/{meeting_id}/audio")
async def meeting_audio(meeting_id: int, user: dict = Depends(current_user)) -> FileResponse:
    meeting = require_meeting_access(get_meeting(meeting_id), user)
    audio_path = Path(meeting["audio_path"])
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        audio_path,
        filename=meeting["original_filename"],
        media_type=audio_content_type(meeting["original_filename"]),
        content_disposition_type="inline",
    )


@app.post("/api/nas-assets/upload")
async def upload_nas_asset(
    background_tasks: BackgroundTasks,
    title: str = Form(default=""),
    audio_model_id: str = Form(default=""),
    audio_api_key: str = Form(default=""),
    audio_translation_enabled: str = Form(default="false"),
    audio_translation_target: str = Form(default="zh-Hant"),
    audio_translation_model_id: str = Form(default="local:qwen3-4b"),
    audio_translation_api_key: str = Form(default=""),
    video_model_id: str = Form(default=""),
    video_api_key: str = Form(default=""),
    file: UploadFile = File(...),
    user: dict = Depends(current_user),
) -> dict:
    suffix = Path(file.filename or "nas-file").suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    stored_path = NAS_ASSETS_DIR / stored_name
    stored_path.parent.mkdir(parents=True, exist_ok=True)

    save_uploaded_file(file, stored_path)

    category = classify_asset(stored_path, file.content_type)
    processor_config = {}
    selected_audio_key = audio_api_key.strip() or None
    selected_video_key = video_api_key.strip() or None
    selected_translation_key = None
    if category == "audio":
        asr_model = current_asr_model()
        selected_audio_key = server_api_key_for_model(asr_model)
        if asr_model["requires_api_key"] and not selected_audio_key:
            raise HTTPException(status_code=400, detail=f"系統語音模型 {asr_model['name']} 需要公司 API Key")
        translate, translation_model, selected_translation_key = validate_translation_selection(
            enabled=audio_translation_enabled,
            target=audio_translation_target,
            model_id=audio_translation_model_id,
            api_key=audio_translation_api_key,
        )
        processor_config = {
            "asr_model_id": asr_model["id"],
            "asr_provider": asr_model["provider"],
            "asr_model": asr_model["name"],
            "asr_engine": asr_model["engine"],
            "asr_requires_api_key": asr_model["requires_api_key"],
            "translation_enabled": translate,
            "translation_target": audio_translation_target if translate else None,
            "translation_model_id": translation_model["id"] if translation_model else None,
            "translation_provider": translation_model["provider"] if translation_model else None,
            "translation_model": translation_model["name"] if translation_model else None,
        }
        analyzer = asr_model["name"]
    elif category == "video":
        video_model = get_video_model(video_model_id.strip() or None)
        processor_config = {
            "video_model_id": video_model["id"],
            "video_provider": video_model["provider"],
            "video_model": video_model["name"],
            "video_engine": video_model["engine"],
            "video_requires_api_key": video_model["requires_api_key"],
        }
        analyzer = video_model["name"]
    else:
        analyzer = analyzer_for_category(category)
    asset_title = title.strip() or Path(file.filename or stored_name).stem or "NAS asset"
    asset = create_nas_asset(
        user_id=user["id"],
        category=category,
        title=asset_title,
        original_filename=file.filename or stored_name,
        stored_path=str(stored_path),
        mime_type=file.content_type,
        file_size=stored_path.stat().st_size,
        status="processing",
        analyzer=analyzer,
        processor_config_json=json.dumps(processor_config, ensure_ascii=False) if processor_config else None,
    )
    if category in {"audio", "video"}:
        await enqueue_media_job(
            "asset",
            asset["id"],
            audio_api_key=selected_audio_key,
            video_api_key=selected_video_key,
            translation_api_key=selected_translation_key,
        )
    else:
        background_tasks.add_task(
            process_nas_asset,
            asset["id"],
            selected_audio_key,
            selected_video_key,
            selected_translation_key,
        )
    await manager.broadcast(
        {
            "type": "nas_asset_uploaded",
            "asset_id": asset["id"],
            "title": asset["title"],
            "message": f"NAS 已收到上傳檔案《{asset['title']}》，正在交給 {asset['analyzer']} 處理",
            "asset": asset,
        }
    )
    return asset


@app.get("/api/network-assets")
async def network_assets(user: dict = Depends(current_user)) -> list[dict]:
    return list_network_assets(user_id=user["id"], role=user["role"])


@app.post("/api/network-assets/youtube")
async def import_youtube(
    payload: dict,
    background_tasks: BackgroundTasks,
    user: dict = Depends(current_user),
) -> dict:
    try:
        url = validate_youtube_url(str(payload.get("url", "")))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    media_type = str(payload.get("media_type", "video")).strip().lower()
    if media_type not in {"audio", "video"}:
        raise HTTPException(status_code=400, detail="下載類型必須是 audio 或 video")
    if payload.get("authorized") is not True:
        raise HTTPException(status_code=400, detail="請先確認您有權下載及保存此內容")

    requested_title = str(payload.get("title", "")).strip()[:180]
    pending_name = f"youtube-{uuid.uuid4().hex}.pending"
    asset = create_nas_asset(
        user_id=user["id"],
        category=media_type,
        title=requested_title or "YouTube 網路資料",
        original_filename=pending_name,
        stored_path=str(NAS_ASSETS_DIR / pending_name),
        mime_type=None,
        file_size=0,
        status="downloading",
        analyzer="YouTube Downloader",
        processor_config_json=json.dumps({"requested_title": requested_title}, ensure_ascii=False),
        source_type="youtube",
        source_url=url,
    )
    asset = update_nas_asset(
        asset["id"],
        status="downloading",
        analyzer="YouTube Downloader",
        summary="YouTube 下載任務已建立，正在取得影片資訊。",
    ) or asset
    background_tasks.add_task(download_youtube_asset, asset["id"], url, media_type, requested_title)
    await manager.broadcast(
        {
            "type": "nas_asset_uploaded",
            "asset_id": asset["id"],
            "title": asset["title"],
            "message": "YouTube 下載任務已建立，完成後會保存到 NAS。",
            "asset": asset,
        }
    )
    return asset


def validate_translation_selection(
    *,
    enabled: str,
    target: str,
    model_id: str,
    api_key: str,
) -> tuple[bool, dict | None, str | None]:
    translate = enabled.strip().lower() in {"1", "true", "yes", "on"}
    if not translate:
        return False, None, None
    if target not in TARGET_LANGUAGES:
        raise HTTPException(status_code=400, detail="不支援所選翻譯目標語言")
    model = current_llm_model()
    selected_key = api_key.strip() or server_api_key_for_model(model)
    if model["free_tier"]["requires_api_key_for_real_call"] and not selected_key:
        raise HTTPException(status_code=400, detail=f"系統目前模型 {model['name']} 需要公司 API Key")
    return True, model, selected_key


@app.get("/api/nas-assets")
async def nas_assets(q: str | None = None, user: dict = Depends(current_user)) -> list[dict]:
    return list_nas_assets(user_id=user["id"], role=user["role"], q=q)


@app.get("/api/wiki/pages")
async def wiki_pages(q: str = "", user: dict = Depends(current_user)) -> dict:
    return {"pages": await search_wiki(user, q, limit=50), "query": q}


@app.get("/api/wiki/pages/{page_id}")
async def wiki_page_detail(page_id: int, user: dict = Depends(current_user)) -> dict:
    page = await wiki_detail(page_id, user)
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return page


@app.get("/api/asr/models")
async def asr_models(user: dict = Depends(current_user)) -> dict:
    current = current_asr_state()
    return {
        "models": [with_server_key_status(model) for model in asr_model_summary()],
        "current_model": with_server_key_status(current["model"]),
        "current_model_updated_at": current["updated_at"],
        "current_model_updated_by": current["updated_by"],
        "current_model_is_default": current["is_default"],
    }


@app.put("/api/admin/asr/current-model")
async def set_current_asr(payload: dict, admin: dict = Depends(require_admin)) -> dict:
    model_id = str(payload.get("model_id", "")).strip()
    model = find_asr_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="ASR model not found")
    if model["requires_api_key"] and not server_api_key_for_model(model):
        raise HTTPException(status_code=400, detail="此雲端語音模型尚未設定公司 API Key")
    if model["id"].startswith("local:"):
        status = local_model_status(model["id"])
        if not status.get("installed"):
            raise HTTPException(status_code=400, detail="此本地語音模型尚未安裝完成")
    return update_current_asr(model_id, admin["id"])


@app.get("/api/video/models")
async def video_models(user: dict = Depends(current_user)) -> dict:
    return {"models": video_model_summary()}


@app.get("/api/admin/models")
async def admin_custom_models(admin: dict = Depends(require_admin)) -> dict:
    return {"models": list_custom_models()}


@app.post("/api/admin/models")
async def admin_create_custom_model(payload: dict, admin: dict = Depends(require_admin)) -> dict:
    try:
        model = register_custom_model(payload, admin["id"])
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="模型 ID 或模型檔名已存在") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"model": model, "status": local_model_status(model["id"])}


@app.post("/api/admin/models/{model_id}/test")
async def admin_test_custom_model(model_id: str, admin: dict = Depends(require_admin)) -> dict:
    record = get_custom_model(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="找不到自訂模型")
    update_custom_model_validation(model_id, status="testing", error_message=None)

    if record["model_type"] in {"whisper_cpp", "yolo"}:
        try:
            status = await asyncio.to_thread(validate_custom_file_model, model_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        refreshed = get_custom_model(model_id)
        return {
            "ok": bool(refreshed and refreshed["validation_status"] == "ready"),
            "model": refreshed,
            "status": status,
        }

    model = custom_model_to_catalog(record)
    prompt = "Respond with exactly: AIWORK_MODEL_OK"
    try:
        result = await run_llm(model, prompt, None)
    except Exception as exc:
        error_message = str(exc)
        update_custom_model_validation(model_id, status="failed", error_message=error_message)
        create_llm_call(
            user_id=admin["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=prompt,
            response=None,
            status="failed",
            access_mode="local_nas",
            error_message=error_message,
            channel="model_validation",
        )
        raise HTTPException(status_code=400, detail=error_message) from exc

    usage = result.get("usage") or {}
    create_llm_call(
        user_id=admin["id"],
        provider=model["provider"],
        model_name=model["name"],
        model_id=model["id"],
        prompt=prompt,
        response=result["answer"],
        status="completed",
        access_mode=result["access_mode"],
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        total_tokens=usage.get("total_tokens"),
        remaining_tokens=usage.get("remaining_tokens"),
        raw_usage_json=json.dumps(usage.get("raw_usage"), ensure_ascii=False) if usage.get("raw_usage") else None,
        channel="model_validation",
    )
    refreshed = update_custom_model_validation(model_id, status="ready", error_message=None)
    return {"ok": True, "model": refreshed, "answer": result["answer"], "status": local_model_status(model_id)}


@app.delete("/api/admin/models/{model_id}")
async def admin_delete_custom_model(model_id: str, admin: dict = Depends(require_admin)) -> dict:
    record = get_custom_model(model_id)
    if not record:
        raise HTTPException(status_code=404, detail="找不到自訂模型")
    if download_in_progress(model_id):
        raise HTTPException(status_code=409, detail="請先取消模型下載")
    delete_custom_model(model_id)
    return {"ok": True, "model_file_preserved": True}


@app.get("/api/local-models")
async def local_models(user: dict = Depends(current_user)) -> dict:
    return {"models": list_local_model_statuses()}


@app.post("/api/local-models/{model_id}/download")
async def download_local_model(model_id: str, user: dict = Depends(current_user)) -> dict:
    require_admin_for_custom_model(model_id, user)
    try:
        return start_download(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/local-models/{model_id}/retry")
async def retry_local_model_download(model_id: str, user: dict = Depends(current_user)) -> dict:
    require_admin_for_custom_model(model_id, user)
    try:
        return start_download(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/local-models/{model_id}/cancel")
async def cancel_local_model_download(model_id: str, user: dict = Depends(current_user)) -> dict:
    require_admin_for_custom_model(model_id, user)
    try:
        return cancel_download(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/local-models/{model_id}")
async def get_local_model(model_id: str, user: dict = Depends(current_user)) -> dict:
    try:
        return local_model_status(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def require_admin_for_custom_model(model_id: str, user: dict) -> None:
    if get_custom_model(model_id) and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="只有管理員可以操作自訂模型")


@app.get("/api/nas-assets/{asset_id}")
async def nas_asset_detail(asset_id: int, user: dict = Depends(current_user)) -> dict:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    chunks = list_document_chunks(asset_id) if asset["category"] in {"audio", "video", "pdf", "docx", "image"} else []
    analyses = list_asset_ai_analyses(asset_id)
    analysis_chunks = [chunk for chunk in chunks if chunk.get("chunk_type") == "ai_analysis"][-4:]
    preview_chunks = [*chunks[:8], *analysis_chunks]
    unique_preview = list({chunk["id"]: chunk for chunk in preview_chunks}.values())
    media_segments = []
    transcript = ""
    transcript_chunk_count = 0
    if asset["category"] == "audio":
        transcript_chunks = [chunk for chunk in chunks if chunk.get("chunk_type") == "audio_transcript"]
        transcript_chunk_count = len(transcript_chunks)
        linked_meeting = get_meeting_by_nas_asset_id(asset_id)
        transcript = str((linked_meeting or {}).get("transcript") or "").strip()
        if not transcript:
            transcript = merge_transcript_chunks(transcript_chunks)
    if asset["category"] in {"audio", "video"}:
        segment_transcriptions = list_audio_segment_transcriptions(asset_id) if asset["category"] == "audio" else {}
        media_segments = [
            {
                **segment,
                "audio_url": (
                    f"/api/nas-assets/{asset_id}/audio-segments/{segment['index']}"
                    if asset["category"] == "audio"
                    else None
                ),
                "download_url": f"/api/nas-assets/{asset_id}/media-segments/{segment['index']}/download",
                "is_source": False,
                "transcription": segment_transcription_payload(
                    asset_id,
                    segment["index"],
                    segment_transcriptions.get(segment["index"]),
                ),
            }
            for segment in list_archived_media_segments(asset_id, asset["category"])
        ]
        if not media_segments:
            media_segments = [
                {
                    "index": 0,
                    "filename": asset["original_filename"],
                    "start_seconds": 0,
                    "duration_seconds": None,
                    "file_size": asset["file_size"],
                    "audio_url": f"/api/nas-assets/{asset_id}/audio" if asset["category"] == "audio" else None,
                    "download_url": f"/api/nas-assets/{asset_id}/download",
                    "is_source": True,
                    "transcription": segment_transcription_payload(asset_id, 0, segment_transcriptions.get(0)),
                }
            ]
    return {
        **asset,
        "processor_config": parse_processor_config(asset),
        "chunks": serialize_document_chunks(asset_id, unique_preview),
        "ai_analyses": analyses,
        "audio_url": f"/api/nas-assets/{asset_id}/audio" if asset["category"] == "audio" else None,
        "video_url": f"/api/nas-assets/{asset_id}/video" if asset["category"] == "video" else None,
        "download_url": f"/api/nas-assets/{asset_id}/download" if asset["category"] in {"audio", "video"} else None,
        "audio_segments": media_segments if asset["category"] == "audio" else [],
        "video_segments": media_segments if asset["category"] == "video" else [],
        "transcript": transcript or None,
        "transcript_download_url": f"/api/nas-assets/{asset_id}/transcript/download" if transcript else None,
        "transcript_chunk_count": transcript_chunk_count,
    }


@app.get("/api/nas-assets/{asset_id}/download")
async def download_nas_media(asset_id: int, user: dict = Depends(current_user)) -> FileResponse:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] not in {"audio", "video"}:
        raise HTTPException(status_code=400, detail="此 NAS 資產不是音訊或影片檔")
    source_path = Path(asset["stored_path"])
    if not source_path.is_file():
        raise HTTPException(status_code=404, detail="NAS 原始媒體不存在")
    content_type = (
        audio_content_type(asset["original_filename"], asset.get("mime_type"))
        if asset["category"] == "audio"
        else video_content_type(asset["original_filename"], asset.get("mime_type"))
    )
    return FileResponse(
        source_path,
        filename=asset["original_filename"],
        media_type=content_type,
        content_disposition_type="attachment",
    )


@app.get("/api/nas-assets/{asset_id}/media-segments/{segment_index}/download")
async def download_nas_media_segment(
    asset_id: int,
    segment_index: int,
    user: dict = Depends(current_user),
) -> FileResponse:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] not in {"audio", "video"}:
        raise HTTPException(status_code=400, detail="此 NAS 資產不是音訊或影片檔")
    segment_path = archived_media_segment_path(asset_id, asset["category"], segment_index)
    if not segment_path:
        raise HTTPException(status_code=404, detail="找不到指定的媒體切片")
    content_type = (
        audio_content_type(segment_path.name)
        if asset["category"] == "audio"
        else video_content_type(segment_path.name)
    )
    return FileResponse(
        segment_path,
        filename=segment_path.name,
        media_type=content_type,
        content_disposition_type="attachment",
    )


@app.get("/api/nas-assets/{asset_id}/audio")
async def nas_asset_audio(asset_id: int, user: dict = Depends(current_user)) -> FileResponse:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] != "audio":
        raise HTTPException(status_code=400, detail="此 NAS 資產不是音訊檔")
    audio_path = Path(asset["stored_path"])
    if not audio_path.is_file():
        raise HTTPException(status_code=404, detail="NAS 原始音訊不存在")
    return FileResponse(
        audio_path,
        filename=asset["original_filename"],
        media_type=audio_content_type(asset["original_filename"], asset.get("mime_type")),
        content_disposition_type="inline",
    )


@app.get("/api/nas-assets/{asset_id}/video")
async def nas_asset_video(asset_id: int, user: dict = Depends(current_user)) -> FileResponse:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] != "video":
        raise HTTPException(status_code=400, detail="此 NAS 資產不是影片檔")
    source_path = Path(asset["stored_path"])
    if not source_path.is_file():
        raise HTTPException(status_code=404, detail="NAS 原始影片不存在")
    try:
        lock = VIDEO_PLAYBACK_LOCKS.setdefault(asset_id, asyncio.Lock())
        async with lock:
            video_path = await asyncio.to_thread(browser_video_path, asset)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return FileResponse(
        video_path,
        filename=video_path.name,
        media_type=video_content_type(video_path.name, asset.get("mime_type") if video_path == source_path else "video/mp4"),
        content_disposition_type="inline",
    )


@app.get("/api/nas-assets/{asset_id}/audio-segments/{segment_index}")
async def nas_asset_audio_segment(
    asset_id: int,
    segment_index: int,
    user: dict = Depends(current_user),
) -> FileResponse:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] != "audio":
        raise HTTPException(status_code=400, detail="此 NAS 資產不是音訊檔")
    segment_path = archived_media_segment_path(asset_id, "audio", segment_index)
    if not segment_path:
        raise HTTPException(status_code=404, detail="找不到指定的音訊切片")
    return FileResponse(
        segment_path,
        filename=segment_path.name,
        media_type="audio/wav",
        content_disposition_type="inline",
    )


@app.get("/api/nas-assets/{asset_id}/transcript/download")
async def download_nas_asset_transcript(asset_id: int, user: dict = Depends(current_user)) -> Response:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] != "audio":
        raise HTTPException(status_code=400, detail="此 NAS 資產不是音訊檔")
    linked_meeting = get_meeting_by_nas_asset_id(asset_id)
    transcript = str((linked_meeting or {}).get("transcript") or "").strip()
    if not transcript:
        chunks = [
            chunk
            for chunk in list_document_chunks(asset_id)
            if chunk.get("chunk_type") == "audio_transcript"
        ]
        transcript = merge_transcript_chunks(chunks)
    if not transcript:
        raise HTTPException(status_code=404, detail="此音訊尚未產生逐字稿")
    filename = f"{Path(asset['original_filename']).stem}-transcript.txt"
    return transcript_download_response(transcript, filename)


@app.get("/api/nas-assets/{asset_id}/audio-segments/{segment_index}/transcript/download")
async def download_nas_audio_segment_transcript(
    asset_id: int,
    segment_index: int,
    user: dict = Depends(current_user),
) -> Response:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] != "audio":
        raise HTTPException(status_code=400, detail="此 NAS 資產不是音訊檔")
    record = list_audio_segment_transcriptions(asset_id).get(segment_index) or {}
    transcript = str(record.get("transcript") or "").strip()
    if not transcript:
        raise HTTPException(status_code=404, detail="此音訊切片尚未產生逐字稿")
    filename = f"{Path(asset['original_filename']).stem}-segment-{segment_index + 1:04d}-transcript.txt"
    return transcript_download_response(transcript, filename)


@app.post("/api/nas-assets/{asset_id}/audio-segments/{segment_index}/transcribe")
async def transcribe_nas_audio_segment(
    asset_id: int,
    segment_index: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    user: dict = Depends(current_user),
) -> dict:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] != "audio":
        raise HTTPException(status_code=400, detail="此 NAS 資產不是音訊檔")
    segment_path = archived_media_segment_path(asset_id, "audio", segment_index)
    if not segment_path and segment_index == 0:
        source_path = Path(asset["stored_path"])
        segment_path = source_path if source_path.is_file() else None
    if not segment_path:
        raise HTTPException(status_code=404, detail="找不到指定的音訊切片")

    existing = list_audio_segment_transcriptions(asset_id).get(segment_index) or {}
    job_key = (asset_id, segment_index)
    if job_key in ACTIVE_SEGMENT_TRANSCRIPTIONS:
        raise HTTPException(status_code=409, detail="此音訊切片正在轉寫")
    model = current_asr_model()
    api_key = server_api_key_for_model(model)
    if model["requires_api_key"] and not api_key:
        raise HTTPException(status_code=400, detail=f"系統語音模型 {model['name']} 需要公司 API Key")

    record = update_audio_segment_transcription(
        asset_id,
        segment_index,
        status="queued",
        progress=5,
        model_id=model["id"],
        model_name=model["name"],
        transcript=existing.get("transcript"),
        error_message=None,
    )
    ACTIVE_SEGMENT_TRANSCRIPTIONS.add(job_key)
    background_tasks.add_task(
        run_single_audio_segment_transcription,
        asset,
        segment_index,
        segment_path,
        model["id"],
        api_key,
    )
    return record


async def run_single_audio_segment_transcription(
    asset: dict,
    segment_index: int,
    segment_path: Path,
    model_id: str,
    api_key: str | None,
) -> None:
    update_audio_segment_transcription(
        asset["id"],
        segment_index,
        status="processing",
        progress=15,
        error_message=None,
    )
    try:
        result = await run_asr_with_audit(
            path=segment_path,
            model_id=model_id,
            api_key=api_key,
            user_id=asset["user_id"],
        )
        update_audio_segment_transcription(
            asset["id"],
            segment_index,
            status="completed",
            progress=100,
            model_id=result["model"]["id"],
            model_name=result["model"].get("name") or result["model"]["id"],
            transcript=result["text"],
            error_message=None,
        )
        await manager.broadcast(
            {
                "type": "nas_asset_segment_transcribed",
                "asset_id": asset["id"],
                "segment_index": segment_index,
                "title": asset["title"],
            }
        )
    except Exception as exc:
        update_audio_segment_transcription(
            asset["id"],
            segment_index,
            status="failed",
            progress=100,
            error_message=str(exc),
        )
    finally:
        ACTIVE_SEGMENT_TRANSCRIPTIONS.discard((asset["id"], segment_index))


@app.post("/api/nas-assets/{asset_id}/reprocess")
async def reprocess_nas_asset(
    asset_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    user: dict = Depends(current_user),
) -> dict:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] not in {"audio", "video", "pdf", "docx", "image"}:
        raise HTTPException(status_code=400, detail="此檔案類型目前沒有可重新執行的分析流程")
    if asset["status"] == "processing":
        raise HTTPException(status_code=409, detail="此資產已在媒體 Worker 處理中")
    if not Path(asset["stored_path"]).is_file():
        raise HTTPException(status_code=404, detail="NAS 原始檔不存在，無法重新處理")

    config = parse_processor_config(asset)
    audio_api_key = str(payload.get("audio_api_key", "")).strip() or None
    video_api_key = str(payload.get("video_api_key", "")).strip() or None
    translation_api_key = str(payload.get("translation_api_key", "")).strip() or None

    if asset["category"] == "audio":
        asr_model = current_asr_model()
        audio_api_key = server_api_key_for_model(asr_model)
        if asr_model["requires_api_key"] and not audio_api_key:
            raise HTTPException(status_code=400, detail=f"系統語音模型 {asr_model['name']} 需要公司 API Key")
        config.update(
            {
                "asr_model_id": asr_model["id"],
                "asr_provider": asr_model["provider"],
                "asr_model": asr_model["name"],
                "asr_engine": asr_model["engine"],
                "asr_requires_api_key": asr_model["requires_api_key"],
            }
        )
        asset = update_nas_asset_processor_config(
            asset_id,
            analyzer=asr_model["name"],
            processor_config_json=json.dumps(config, ensure_ascii=False),
        ) or asset
        if config.get("translation_enabled"):
            translation_model = current_llm_model()
            translation_api_key = translation_api_key or server_api_key_for_model(translation_model)
            if translation_model["free_tier"]["requires_api_key_for_real_call"] and not translation_api_key:
                raise HTTPException(status_code=400, detail=f"系統目前模型需要 {translation_model['provider']} 公司 API Key")
    elif asset["category"] == "video":
        video_model = get_video_model(config.get("video_model_id"))
        video_api_key = video_api_key or server_api_key_for_model(video_model)
        if video_model["requires_api_key"] and not video_api_key:
            raise HTTPException(status_code=400, detail=f"重新處理需要 {video_model.get('api_key_label') or 'API Key'}")

    updated = update_nas_asset(
        asset_id,
        status="processing",
        analyzer=asset.get("analyzer"),
        summary="已保留現有結果，原始檔已重新加入媒體 Worker 佇列。",
        error_message=None,
        chunk_count=asset.get("chunk_count"),
    )
    meeting = get_meeting_by_nas_asset_id(asset_id) if asset["category"] == "audio" else None
    if meeting:
        update_meeting_asr_selection(
            meeting["id"],
            model_id=asr_model["id"],
            provider=asr_model["provider"],
            model_name=asr_model["name"],
            engine=asr_model["engine"],
        )
        update_meeting_status(meeting["id"], status="processing", error_message=None)
        await enqueue_media_job(
            "meeting",
            meeting["id"],
            audio_api_key=audio_api_key,
            translation_api_key=translation_api_key,
        )
    elif asset["category"] == "video":
        await enqueue_media_job(
            "asset",
            asset_id,
            audio_api_key=audio_api_key,
            video_api_key=video_api_key,
            translation_api_key=translation_api_key,
        )
    else:
        background_tasks.add_task(process_nas_asset, asset_id)
    await manager.broadcast(
        {
            "type": "nas_asset_uploaded",
            "asset_id": asset_id,
            "title": asset["title"],
            "message": "NAS 原始檔已重新加入媒體 Worker 佇列",
            "asset": updated,
        }
    )
    return updated or asset


@app.post("/api/nas-assets/{asset_id}/opencc-traditional")
async def opencc_nas_asset(asset_id: int, user: dict = Depends(current_user)) -> dict:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    if asset["category"] not in {"audio", "video"}:
        raise HTTPException(status_code=400, detail="OpenCC 按鈕目前適用於 audio 與 video 資產")
    if asset["status"] == "processing":
        raise HTTPException(status_code=409, detail="請等待媒體 Worker 完成後再執行 OpenCC")
    result = await convert_asset_to_traditional(asset)
    await manager.broadcast(
        {
            "type": "nas_asset_processed",
            "asset_id": asset_id,
            "title": asset["title"],
            "message": result["message"],
            "asset": result["asset"],
        }
    )
    return result


@app.get("/api/nas-assets/{asset_id}/chunk-images/{chunk_id}")
async def nas_asset_chunk_image(asset_id: int, chunk_id: int, user: dict = Depends(current_user)) -> FileResponse:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    chunk = get_document_chunk(chunk_id)
    if not chunk or chunk["asset_id"] != asset["id"]:
        raise HTTPException(status_code=404, detail="Chunk image not found")

    raw_path = chunk.get("image_path")
    if not raw_path:
        raise HTTPException(status_code=404, detail="Chunk image not found")

    image_path = Path(raw_path)
    try:
        image_path.resolve().relative_to(NAS_ASSETS_DIR.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Invalid image path") from exc
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Chunk image not found")
    media_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    return FileResponse(image_path, media_type=media_type)


@app.post("/api/nas-assets/{asset_id}/ask")
async def ask_nas_asset(asset_id: int, payload: dict, user: dict = Depends(current_user)) -> dict:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    question = str(payload.get("question", "")).strip()
    model_id = current_llm_model()["id"]
    api_key = str(payload.get("api_key", "")).strip() or None

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    selected_model = get_model(model_id)
    if not selected_model:
        raise HTTPException(status_code=400, detail="Model not found")
    if asset["category"] not in {"audio", "video", "pdf", "docx", "image"} or asset["chunk_count"] < 1:
        raise HTTPException(status_code=400, detail="This file has no RAG chunks")

    cached, query_vector = await lookup_rag_cache(
        asset_id=asset_id,
        model_id=model_id,
        question=question,
        user_id=user["id"],
    )
    if cached:
        persistence = await persist_cloud_asset_analysis(
            asset=asset,
            model=selected_model,
            question=question,
            result=cached["result"],
            contexts=cached["contexts"],
            user_id=user["id"],
        )
        return {
            **cached["result"],
            "asset_id": asset_id,
            "asset_title": asset["title"],
            "question": question,
            "contexts": cached["contexts"],
            "cache": cached["cache"],
            "nas_persistence": persistence,
        }

    chunks = await hybrid_search_document_chunks(
        asset_id,
        question,
        limit=5,
        user_id=user["id"],
        query_vector=query_vector,
    )
    enriched_chunks = serialize_document_chunks(asset_id, chunks)
    context = "\n\n".join(format_rag_context(chunk) for chunk in enriched_chunks)
    rag_prompt = (
        "你是 NAS 資產資料庫助理。請只根據下方 RAG context 回答問題；"
        "如果 context 不足，請明確說明缺少資料。\n\n"
        f"資產：{asset['title']} ({asset['original_filename']})\n\n"
        f"RAG context:\n{context}\n\n"
        f"問題：{question}"
    )
    result = await run_model_with_audit(model_id=model_id, prompt=rag_prompt, api_key=api_key, user=user)
    response = {
        **result,
        "asset_id": asset_id,
        "asset_title": asset["title"],
        "question": question,
        "contexts": enriched_chunks,
        "retrieval": {
            "method": enriched_chunks[0].get("retrieval_method", "keyword") if enriched_chunks else "keyword",
            "embedding_model": enriched_chunks[0].get("embedding_model") if enriched_chunks else None,
            "semantic_weight": 0.75,
            "keyword_weight": 0.25,
        },
        "cache": {"hit": False},
    }
    persistence = await persist_cloud_asset_analysis(
        asset=asset,
        model=selected_model,
        question=question,
        result=result,
        contexts=enriched_chunks,
        user_id=user["id"],
    )
    response["nas_persistence"] = persistence
    await store_rag_cache(
        asset_id=asset_id,
        user_id=user["id"],
        model_id=model_id,
        question=question,
        query_vector=query_vector,
        result={**result, "retrieval": response["retrieval"]},
        contexts=enriched_chunks,
    )
    return response


@app.get("/api/embedding/status")
async def embedding_status(user: dict = Depends(current_user)) -> dict:
    service, coverage = await asyncio.gather(
        asyncio.to_thread(embedding_service_status),
        asyncio.to_thread(embedding_coverage),
    )
    return {"service": service, "coverage": coverage}


@app.get("/api/llm/models")
async def llm_models(user: dict = Depends(current_user)) -> dict:
    current = current_llm_state()
    return {
        "updated_at": PRICING_UPDATED_AT,
        "providers": provider_summary(),
        "models": [with_server_key_status(model) for model in model_summary()],
        "current_model": with_server_key_status(current["model"]),
        "current_model_updated_at": current["updated_at"],
        "current_model_updated_by": current["updated_by"],
        "current_model_is_default": current["is_default"],
    }


@app.put("/api/admin/llm/current-model")
async def set_current_llm(payload: dict, admin: dict = Depends(require_admin)) -> dict:
    model_id = str(payload.get("model_id", "")).strip()
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if model["free_tier"]["requires_api_key_for_real_call"] and not server_api_key_for_model(model):
        raise HTTPException(status_code=400, detail="此雲端模型尚未設定公司 API Key，不能設為系統目前模型")
    return update_current_llm(model_id, admin["id"])


@app.get("/api/llm/suggestions")
async def llm_suggestions(q: str = "", model_id: str = "", user: dict = Depends(current_user)) -> dict:
    clean_model_id = current_llm_model()["id"]
    return {
        "suggestions": await suggest_llm_prompts(
            user_id=user["id"],
            model_id=clean_model_id,
            query=q[:300],
        )
    }


@app.get("/api/llm/pricing/{model_id}")
async def llm_pricing(model_id: str, user: dict = Depends(current_user)) -> dict:
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"updated_at": PRICING_UPDATED_AT, "model": with_server_key_status(model)}


@app.post("/api/llm/run")
async def llm_run(payload: dict, user: dict = Depends(current_user)) -> dict:
    model_id = current_llm_model()["id"]
    system_prompt = str(payload.get("system_prompt", "")).strip()
    if len(system_prompt) > 4000:
        raise HTTPException(status_code=400, detail="System prompt must be 4,000 characters or fewer")
    force_refresh = payload.get("force_refresh") is True
    use_mcp = payload.get("use_mcp") is True
    selected_server_id = payload.get("mcp_server_id")
    if selected_server_id in {None, "", "auto"}:
        selected_server_id = None
    else:
        try:
            selected_server_id = int(selected_server_id)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="MCP Server 選擇無效") from exc
    lock = LLM_RUN_LOCKS.setdefault((user["id"], model_id), asyncio.Lock())
    async with lock:
        if use_mcp:
            return await run_model_with_mcp(
                model_id=model_id,
                prompt=str(payload.get("prompt", "")),
                api_key=str(payload.get("api_key", "")).strip() or None,
                user=user,
                selected_server_id=selected_server_id,
                system_prompt=system_prompt or None,
            )
        return await run_model_with_audit(
            model_id=model_id,
            prompt=str(payload.get("prompt", "")),
            api_key=str(payload.get("api_key", "")).strip() or None,
            user=user,
            system_prompt=system_prompt or None,
            use_semantic_cache=True,
            force_refresh=force_refresh,
        )


async def run_model_with_mcp(
    *,
    model_id: str,
    prompt: str,
    api_key: str | None,
    user: dict,
    selected_server_id: int | None,
    system_prompt: str | None = None,
) -> dict:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return await run_model_with_audit(
            model_id=model_id,
            prompt=prompt,
            api_key=api_key,
            user=user,
            system_prompt=system_prompt,
            audit_context={"channel": "mcp_planner"},
        )
    try:
        servers = available_mcp_servers(list_mcp_servers(), selected_server_id)
    except McpPlanningError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not servers:
        raise HTTPException(status_code=400, detail="目前沒有已啟用、已連線的唯讀 MCP 工具")

    planner = await run_model_with_audit(
        model_id=model_id,
        prompt=build_planner_prompt(clean_prompt, servers),
        api_key=api_key,
        user=user,
        audit_context={"channel": "mcp_planner", "source_ref": clean_prompt[:500]},
    )
    try:
        plan = parse_mcp_plan(planner["answer"])
    except McpPlanningError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if plan["action"] == "answer":
        final = await run_model_with_audit(
            model_id=model_id,
            prompt=clean_prompt,
            api_key=api_key,
            user=user,
            system_prompt=system_prompt,
            audit_context={"channel": "mcp_final", "source_ref": "no_relevant_tool"},
        )
        final["cache"] = {"hit": False, "bypassed": True, "reason": "mcp"}
        final["mcp"] = {
            "enabled": True,
            "used": False,
            "planner_call_id": planner["call_id"],
            "reason": plan.get("reason") or "No relevant MCP tool selected",
        }
        return final

    try:
        server, tool = resolve_planned_tool(plan, servers)
    except McpPlanningError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    audit_input = json.dumps(plan["arguments"], ensure_ascii=False)
    try:
        tool_result = await asyncio.to_thread(
            call_streamable_http_tool,
            server,
            tool["name"],
            plan["arguments"],
        )
    except (McpConnectionError, ValueError) as exc:
        create_mcp_audit_log(
            server_id=server["id"],
            user_id=user["id"],
            action="tools/call",
            status="failed",
            tool_name=tool["name"],
            input_json=audit_input,
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    create_mcp_audit_log(
        server_id=server["id"],
        user_id=user["id"],
        action="tools/call",
        status="completed",
        tool_name=tool["name"],
        input_json=audit_input,
        output_json=json.dumps(tool_result, ensure_ascii=False),
    )
    final = await run_model_with_audit(
        model_id=model_id,
        prompt=build_final_prompt(clean_prompt, server, tool, tool_result),
        api_key=api_key,
        user=user,
        system_prompt=system_prompt,
        audit_context={
            "channel": "mcp_final",
            "source_ref": f"mcp:{server['slug']}:{tool['name']}",
        },
    )
    final["cache"] = {"hit": False, "bypassed": True, "reason": "mcp"}
    final["mcp"] = {
        "enabled": True,
        "used": True,
        "planner_call_id": planner["call_id"],
        "server_id": server["id"],
        "server": server["name"],
        "tool": tool["name"],
        "arguments": plan["arguments"],
        "result": tool_result,
    }
    return final


async def run_model_with_audit(
    *,
    model_id: str,
    prompt: str,
    api_key: str | None,
    user: dict,
    system_prompt: str | None = None,
    audit_context: dict | None = None,
    use_semantic_cache: bool = False,
    force_refresh: bool = False,
) -> dict:
    requested_model_id = model_id.strip()
    model = get_model(requested_model_id)
    raw_prompt = prompt
    clean_prompt = raw_prompt.strip()
    clean_system_prompt = (system_prompt or "").strip()
    audit_prompt = (
        f"[System Prompt]\n{clean_system_prompt}\n\n[User Prompt]\n{clean_prompt}"
        if clean_system_prompt
        else clean_prompt
    )
    cache_model_id = model["id"] if model else requested_model_id
    if clean_system_prompt:
        prompt_namespace = hashlib.sha256(clean_system_prompt.encode("utf-8")).hexdigest()[:16]
        cache_model_id = f"{cache_model_id}::system:{prompt_namespace}"
    audit_fields = {
        key: value
        for key, value in (audit_context or {}).items()
        if key in {"channel", "external_caller", "source_ref"}
    }

    if not model:
        create_llm_call(
            user_id=user["id"],
            provider="Unknown",
            model_name="Unknown model",
            model_id=requested_model_id or "-",
            prompt=audit_prompt,
            response=None,
            status="failed",
            error_message="Model is required" if not requested_model_id else "Model not found",
            **audit_fields,
        )
        raise HTTPException(status_code=404, detail="Model is required" if not requested_model_id else "Model not found")
    if not clean_prompt:
        create_llm_call(
            user_id=user["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=raw_prompt,
            response=None,
            status="failed",
            error_message="Prompt is required",
            **audit_fields,
        )
        raise HTTPException(status_code=400, detail="Prompt is required")

    cacheable = use_semantic_cache
    query_vector = None
    if cacheable:
        if force_refresh:
            query_vector = await embed_query(audit_prompt, user["id"])
        else:
            cached, query_vector = await lookup_llm_cache(
                user_id=user["id"],
                model_id=cache_model_id,
                prompt=audit_prompt,
            )
            if cached:
                return record_llm_cache_hit(model=model, prompt=audit_prompt, user=user, cached=cached)

    free_tier = model["free_tier"]
    server_api_key = server_api_key_for_model(model)
    using_server_key = not api_key and bool(server_api_key)
    api_key = api_key or server_api_key
    expected_access_mode = (
        "local_nas"
        if model["provider"] == "Local NAS"
        else "company_api_key"
        if using_server_key
        else "api_key"
        if api_key
        else "free_no_key"
    )
    if not api_key and free_tier["requires_api_key_for_real_call"]:
        create_llm_call(
            user_id=user["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=audit_prompt,
            response=None,
            status="blocked",
            access_mode="no_api_key",
            error_message="API key is required for this model",
            **audit_fields,
        )
        raise HTTPException(status_code=402, detail="API key is required for this model")

    try:
        if clean_system_prompt:
            result = await run_llm(model, clean_prompt, api_key, clean_system_prompt)
        else:
            result = await run_llm(model, clean_prompt, api_key)
        if using_server_key:
            result["access_mode"] = "company_api_key"
    except LlmRuntimeError as exc:
        create_llm_call(
            user_id=user["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=audit_prompt,
            response=None,
            status="failed",
            access_mode=expected_access_mode,
            error_message=str(exc),
            **audit_fields,
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        create_llm_call(
            user_id=user["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=audit_prompt,
            response=None,
            status="failed",
            access_mode=expected_access_mode,
            error_message=f"Unexpected runtime error: {exc}",
            **audit_fields,
        )
        raise HTTPException(status_code=500, detail="Unexpected runtime error") from exc

    usage = result.get("usage") or {}
    if force_refresh:
        usage["raw_usage"] = {**(usage.get("raw_usage") or {}), "cache_bypassed": True}
    call = create_llm_call(
        user_id=user["id"],
        provider=model["provider"],
        model_name=model["name"],
        model_id=model["id"],
        prompt=audit_prompt,
        response=result["answer"],
        status="completed",
        access_mode=result["access_mode"],
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        total_tokens=usage.get("total_tokens"),
        remaining_tokens=usage.get("remaining_tokens"),
        remaining_requests=usage.get("remaining_requests"),
        remaining_balance=usage.get("remaining_balance"),
        raw_usage_json=json.dumps(usage.get("raw_usage"), ensure_ascii=False) if usage.get("raw_usage") else None,
        **audit_fields,
    )
    response = {
        "call_id": call["id"],
        "model_id": model["id"],
        "provider": model["provider"],
        "model": model["name"],
        "caller": user["username"],
        "access_mode": result["access_mode"],
        "answer": result["answer"],
        "usage": usage,
    }
    if cacheable:
        await store_llm_cache(
            user_id=user["id"],
            model_id=cache_model_id,
            prompt=audit_prompt,
            query_vector=query_vector,
            result=response,
        )
        response["cache"] = {"hit": False, "bypassed": force_refresh}
    return response


def record_llm_cache_hit(*, model: dict, prompt: str, user: dict, cached: dict) -> dict:
    source = cached["result"]
    cache = cached["cache"]
    source_usage = source.get("usage") or {}
    access_mode = f"cache_{cache['match_type']}"
    usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "remaining_tokens": source_usage.get("remaining_tokens"),
        "remaining_requests": source_usage.get("remaining_requests"),
        "remaining_balance": source_usage.get("remaining_balance"),
        "raw_usage": {
            "cache_hit": True,
            "match_type": cache["match_type"],
            "similarity": cache["similarity"],
            "keyword_similarity": cache.get("keyword_similarity"),
            "source_call_id": cache.get("source_call_id"),
            "normalized_prompt": normalize_llm_prompt(prompt),
        },
    }
    call = create_llm_call(
        user_id=user["id"],
        provider=model["provider"],
        model_name=model["name"],
        model_id=model["id"],
        prompt=prompt,
        response=source["answer"],
        status="completed",
        access_mode=access_mode,
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        remaining_tokens=usage["remaining_tokens"],
        remaining_requests=usage["remaining_requests"],
        remaining_balance=usage["remaining_balance"],
        raw_usage_json=json.dumps(usage["raw_usage"], ensure_ascii=False),
    )
    return {
        "call_id": call["id"],
        "model_id": model["id"],
        "provider": model["provider"],
        "model": model["name"],
        "caller": user["username"],
        "access_mode": access_mode,
        "answer": source["answer"],
        "usage": usage,
        "cache": cache,
    }


def require_line_integration(x_ai_work_token: str | None = Header(default=None)) -> None:
    expected = os.getenv("LINE_INTEGRATION_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="LINE integration is not configured")
    if not x_ai_work_token or not secrets.compare_digest(x_ai_work_token, expected):
        raise HTTPException(status_code=401, detail="Invalid LINE integration token")


def require_n8n_integration(x_ai_work_n8n_token: str | None = Header(default=None)) -> None:
    expected = os.getenv("N8N_WEBHOOK_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="n8n integration token is not configured")
    if not x_ai_work_n8n_token or not secrets.compare_digest(x_ai_work_n8n_token, expected):
        raise HTTPException(status_code=401, detail="Invalid n8n integration token")


@app.post("/api/internal/n8n/push-result")
async def n8n_push_result(payload: dict, _: None = Depends(require_n8n_integration)) -> dict:
    if payload.get("event") != "nas.asset.completed":
        raise HTTPException(status_code=400, detail="Unsupported n8n event")

    asset_id = int(payload.get("asset_id") or 0)
    meeting = get_meeting_by_nas_asset_id(asset_id) if asset_id else None
    if meeting and meeting.get("line_push_enabled"):
        return {"status": "delegated", "reason": "meeting_line_push_enabled"}

    approved_groups = [
        source
        for source in list_line_sources()
        if source["source_type"] == "group" and bool(source["is_approved"])
    ]
    configured_group_id = os.getenv("N8N_LINE_GROUP_ID", "").strip()
    if configured_group_id:
        approved_groups = [source for source in approved_groups if source["source_id"] == configured_group_id]
    if not approved_groups:
        return {"status": "skipped", "reason": "no_approved_line_group"}

    category_label = "音訊" if payload.get("category") == "audio" else "PDF"
    public_url = os.getenv("AI_WORK_PUBLIC_URL", "https://goldsys.io").rstrip("/")
    preview = str(payload.get("result_preview") or payload.get("summary") or "處理已完成").strip()
    message = "\n".join(
        [
            "AI Work NAS 自動處理完成",
            f"類型：{category_label}",
            f"檔案：{payload.get('title') or payload.get('filename') or '未命名'}",
            f"處理模型：{payload.get('analyzer') or 'NAS 預設模型'}",
            f"上傳者：{payload.get('uploader') or '未知'}",
            f"結果：{preview[:3200]}",
            f"NAS 資產：{public_url}/#asset-{asset_id}",
        ]
    )
    last_error = "LINE push failed"
    for group in approved_groups:
        try:
            await push_line_messages(group["source_id"], [message[:4500]])
        except LineServiceError as exc:
            last_error = str(exc)
            continue
        return {
            "status": "pushed",
            "group_id": group["source_id"],
            "group_name": group.get("display_name"),
        }
    return {"status": "skipped", "reason": "line_push_failed", "error": last_error}


def line_integration_owner() -> dict:
    username = os.getenv("LINE_INTEGRATION_OWNER", "admin")
    owner = get_user_by_username(username)
    if not owner or not owner.get("is_active"):
        raise HTTPException(status_code=503, detail="LINE integration owner is unavailable")
    return owner


def line_audit_context(source_id: str, sender_name: str | None, sender_id: str | None) -> dict:
    return {
        "channel": "LINE",
        "external_caller": sender_name or sender_id or "LINE member",
        "source_ref": source_id,
    }


def company_line_models() -> list[dict]:
    model = current_llm_model()
    access_mode = (
        "local_nas"
        if model["provider"] == "Local NAS"
        else "company_api_key"
        if company_api_key_for_model(model)
        else "free_no_key"
    )
    return [{**with_server_key_status(model), "access_mode": access_mode}]


def require_company_line_source(source: dict | None) -> dict:
    if not source or source.get("source_type") != "group":
        raise HTTPException(status_code=403, detail="個人聊天室不能使用公司 NAS、RAG 或公司模型")
    if not source.get("is_approved"):
        raise HTTPException(status_code=403, detail="此 LINE 群組尚未經管理員核准")
    return source


def enforce_line_quota(source: dict) -> dict[str, int]:
    usage = get_line_source_month_usage(source["source_id"])
    call_limit = int(source.get("monthly_call_limit") or 0)
    token_limit = int(source.get("monthly_token_limit") or 0)
    if call_limit and usage["call_count"] >= call_limit:
        raise HTTPException(status_code=429, detail="此 LINE 群組本月模型呼叫額度已用完")
    if token_limit and usage["token_count"] >= token_limit:
        raise HTTPException(status_code=429, detail="此 LINE 群組本月 Token 額度已用完")
    return usage


@app.get("/api/admin/line/sources")
async def admin_line_sources(admin: dict = Depends(require_admin)) -> dict:
    service_error = None
    try:
        groups = await list_line_groups()
        owner = line_integration_owner()
        for group in groups:
            group_id = str(group.get("id", "")).strip()
            if group_id:
                upsert_line_source(
                    source_id=group_id,
                    source_type="group",
                    display_name=str(group.get("name", "")).strip() or None,
                    owner_user_id=owner["id"],
                    is_approved=False,
                )
    except (LineServiceError, HTTPException) as exc:
        service_error = str(getattr(exc, "detail", exc))

    sources = [source for source in list_line_sources() if source["source_type"] == "group"]
    return {
        "sources": sources,
        "models": company_line_models(),
        "service_connected": service_error is None,
        "service_error": service_error,
    }


@app.patch("/api/admin/line/sources/{line_source_id}")
async def admin_update_line_source(
    line_source_id: int,
    payload: dict,
    admin: dict = Depends(require_admin),
) -> dict:
    source = next((item for item in list_line_sources() if item["id"] == line_source_id), None)
    if not source or source["source_type"] != "group":
        raise HTTPException(status_code=404, detail="LINE group not found")

    boolean_fields = ("is_approved", "auto_pdf_summary", "rag_queries_enabled")
    for field in boolean_fields:
        if field in payload and not isinstance(payload[field], bool):
            raise HTTPException(status_code=400, detail=f"{field} must be a boolean")

    model_id = current_llm_model()["id"]
    allowed_model_ids = {model["id"] for model in company_line_models()}
    if model_id not in allowed_model_ids:
        raise HTTPException(status_code=400, detail="模型必須是 NAS 本地模型或已設定公司 API Key 的雲端模型")

    try:
        call_limit = int(payload.get("monthly_call_limit", source["monthly_call_limit"]))
        token_limit = int(payload.get("monthly_token_limit", source["monthly_token_limit"]))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="LINE quota must be an integer") from exc
    if not 0 <= call_limit <= 1_000_000 or not 0 <= token_limit <= 1_000_000_000:
        raise HTTPException(status_code=400, detail="LINE quota is out of range")

    updated = update_line_source_policy(
        line_source_id,
        is_approved=payload.get("is_approved", bool(source["is_approved"])),
        auto_pdf_summary=payload.get("auto_pdf_summary", bool(source["auto_pdf_summary"])),
        rag_queries_enabled=payload.get("rag_queries_enabled", bool(source["rag_queries_enabled"])),
        default_model_id=model_id,
        monthly_call_limit=call_limit,
        monthly_token_limit=token_limit,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="LINE group not found")
    return next(item for item in list_line_sources() if item["id"] == line_source_id)


@app.post("/api/internal/line/pdf")
async def ingest_line_pdf(
    source_id: str = Form(...),
    source_type: str = Form(default="group"),
    source_name: str = Form(default=""),
    sender_id: str = Form(default=""),
    sender_name: str = Form(default=""),
    line_message_id: str = Form(...),
    line_event_id: str = Form(default=""),
    file: UploadFile = File(...),
    _: None = Depends(require_line_integration),
) -> dict:
    filename = file.filename or "line-upload.pdf"
    if Path(filename).suffix.lower() != ".pdf" and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted by this endpoint")

    if source_type != "group":
        raise HTTPException(status_code=403, detail="個人聊天室不能使用公司 NAS、RAG 或公司模型")
    owner = line_integration_owner()
    source = upsert_line_source(
        source_id=source_id,
        source_type=source_type,
        display_name=source_name.strip() or None,
        owner_user_id=owner["id"],
        is_approved=False,
    )
    require_company_line_source(source)

    duplicate = get_line_document(line_message_id)
    if duplicate:
        if duplicate["status"] == "completed":
            return {
                "duplicate": True,
                "asset_id": duplicate["asset_id"],
                "filename": duplicate["original_filename"],
                "summary": duplicate["summary"],
            }
        raise HTTPException(status_code=409, detail=f"LINE PDF is already {duplicate['status']}")

    stored_path = NAS_ASSETS_DIR / f"{uuid.uuid4().hex}.pdf"
    stored_path.parent.mkdir(parents=True, exist_ok=True)
    save_uploaded_file(file, stored_path)

    title = Path(filename).stem or "LINE PDF"
    asset = create_nas_asset(
        user_id=owner["id"],
        category="pdf",
        title=title,
        original_filename=filename,
        stored_path=str(stored_path),
        mime_type="application/pdf",
        file_size=stored_path.stat().st_size,
        status="processing",
        analyzer="RAG Builder",
    )
    document = create_line_document(
        line_source_id=source["id"],
        line_message_id=line_message_id,
        line_event_id=line_event_id or None,
        sender_id=sender_id or None,
        sender_name=sender_name or None,
        asset_id=asset["id"],
    )
    try:
        await manager.send_to_user(
            owner["id"],
            {
                "type": "line_pdf_received",
                "asset_id": asset["id"],
                "title": title,
                "message": f"NAS 已收到 LINE PDF《{title}》，正在執行文字抽取、OCR 與向量建庫",
            },
        )
        await process_nas_asset(asset["id"])
        processed = get_nas_asset(asset["id"])
        if not processed or processed["status"] != "completed" or processed["chunk_count"] < 1:
            reason = (processed or {}).get("error_message") or (processed or {}).get("summary") or "PDF processing failed"
            finish_line_document(document["id"], status="failed", summary=None, error_message=reason)
            raise HTTPException(status_code=422, detail=reason)

        if source.get("auto_pdf_summary"):
            enforce_line_quota(source)
            chunks = list_document_chunks(asset["id"])
            context = _line_summary_context(chunks)
            prompt = (
                "你是企業 NAS 文件助理。請根據下方 PDF 內容，以繁體中文撰寫適合發送到 LINE 群組的摘要。"
                "先用一句話說明文件主旨，再列出內容中可直接證實的重點。重點可以只有 1 項，絕對不要為了湊數而推論"
                "文件未提及的流程、目的、期限或安全措施；每項附來源頁碼，總長不超過 900 字。\n\n"
                f"檔名：{filename}\n上傳者：{sender_name or sender_id or 'LINE member'}\n\n"
                f"PDF 內容：\n{context}"
            )
            result = await run_model_with_audit(
                model_id=current_llm_model()["id"],
                prompt=prompt,
                api_key=None,
                user=owner,
                audit_context=line_audit_context(source_id, sender_name, sender_id),
            )
            summary = result["answer"].strip()
        else:
            summary = f"NAS 已保存《{filename}》並完成 RAG 建庫；此群組的自動 PDF 摘要已由管理員停用。"
        finish_line_document(document["id"], status="completed", summary=summary, error_message=None)
        await manager.send_to_user(
            owner["id"],
            {
                "type": "line_pdf_completed",
                "asset_id": asset["id"],
                "title": title,
                "message": f"LINE PDF《{title}》已完成 RAG 建庫並產生群組摘要",
            },
        )
        return {
            "duplicate": False,
            "asset_id": asset["id"],
            "filename": filename,
            "chunk_count": processed["chunk_count"],
            "analyzer": processed["analyzer"],
            "summary": summary,
        }
    except HTTPException:
        raise
    except Exception as exc:
        finish_line_document(document["id"], status="failed", summary=None, error_message=str(exc))
        raise HTTPException(status_code=500, detail="LINE PDF processing failed") from exc


@app.post("/api/internal/line/query")
async def query_line_documents(payload: dict, _: None = Depends(require_line_integration)) -> dict:
    source_id = str(payload.get("source_id", "")).strip()
    question = str(payload.get("question", "")).strip()
    sender_id = str(payload.get("sender_id", "")).strip() or None
    sender_name = str(payload.get("sender_name", "")).strip() or None
    if not source_id or not question:
        raise HTTPException(status_code=400, detail="source_id and question are required")

    source = require_company_line_source(get_line_source(source_id))
    if not source["rag_queries_enabled"]:
        raise HTTPException(status_code=403, detail="這個 LINE 群組的資料查詢已停用")
    assets = list_line_source_assets(source["id"])
    if not assets:
        raise HTTPException(status_code=404, detail="這個 LINE 群組尚未有可查詢的 PDF 或會議文字稿")

    owner = get_user_by_id(source["owner_user_id"])
    if not owner or not owner.get("is_active"):
        raise HTTPException(status_code=503, detail="LINE integration owner is unavailable")
    model_id = current_llm_model()["id"]
    normalized = normalize_query(question)
    exact = get_exact_line_query_cache(source["id"], source["content_version"], model_id, normalized)
    if exact:
        mark_line_query_cache_hit(exact["id"])
        return _line_cached_response(exact, "exact", 1.0)

    query_vector = await embed_query(question, owner["id"])
    semantic_candidate: tuple[float, dict] | None = None
    if query_vector:
        candidates = list_line_query_cache_candidates(source["id"], source["content_version"], model_id)
        best: tuple[float, dict] | None = None
        for candidate in candidates:
            similarity = cosine_similarity(query_vector, unpack_embedding(candidate.get("query_embedding")))
            if similarity is not None and similarity >= 0.70 and (best is None or similarity > best[0]):
                best = (similarity, candidate)
        semantic_candidate = best

    ranked: list[dict] = []
    for asset in assets:
        if query_vector:
            chunks = await hybrid_search_document_chunks(
                asset["id"], question, limit=3, user_id=owner["id"], query_vector=query_vector
            )
        else:
            chunks = search_document_chunks(asset["id"], question, limit=3)
        for chunk in serialize_document_chunks(asset["id"], chunks):
            chunk["asset_title"] = asset["title"]
            chunk["original_filename"] = asset["original_filename"]
            ranked.append(chunk)
    ranked.sort(key=lambda item: float(item.get("retrieval_score") or 0), reverse=True)
    contexts = ranked[:6]
    if not contexts:
        raise HTTPException(status_code=404, detail="群組資料庫中沒有可用內容")
    if semantic_candidate and _line_contexts_overlap(semantic_candidate[1]["contexts_json"], contexts):
        mark_line_query_cache_hit(semantic_candidate[1]["id"])
        return _line_cached_response(semantic_candidate[1], "semantic", semantic_candidate[0])

    context_text = "\n\n".join(_format_line_context(chunk) for chunk in contexts)
    prompt = (
        "你是企業 NAS 文件問答助理。只能根據提供的 RAG 內容，以繁體中文簡潔回答。"
        "每個要點要附上（檔名，第 X 頁）；若資料不足，直接說明不足，不得自行補充。"
        "回答適合 LINE 閱讀，最多 900 字。\n\n"
        f"RAG 內容：\n{context_text[:10000]}\n\n問題：{question}"
    )
    enforce_line_quota(source)
    result = await run_model_with_audit(
        model_id=model_id,
        prompt=prompt,
        api_key=None,
        user=owner,
        audit_context=line_audit_context(source_id, sender_name, sender_id),
    )
    save_line_query_cache(
        line_source_id=source["id"],
        content_version=source["content_version"],
        user_id=owner["id"],
        model_id=model_id,
        query_text=question,
        normalized_query=normalized,
        query_embedding=pack_embedding(query_vector) if query_vector else None,
        embedding_model=EMBEDDING_MODEL if query_vector else None,
        answer=result["answer"],
        contexts_json=json.dumps(contexts, ensure_ascii=False),
    )
    return {
        "answer": result["answer"],
        "contexts": contexts,
        "model": result["model"],
        "cache": {"hit": False},
    }


def _line_summary_context(chunks: list[dict], max_chars: int = 9000) -> str:
    parts: list[str] = []
    used = 0
    for chunk in chunks:
        page = f"第 {chunk['page_number']} 頁" if chunk.get("page_number") else f"段落 {chunk['chunk_index'] + 1}"
        part = f"[{page}]\n{chunk['content'].strip()}"
        if used + len(part) > max_chars:
            remaining = max_chars - used
            if remaining > 100:
                parts.append(part[:remaining])
            break
        parts.append(part)
        used += len(part)
    return "\n\n".join(parts)


def _format_line_context(chunk: dict) -> str:
    page = f"第 {chunk['page_number']} 頁" if chunk.get("page_number") else f"段落 {chunk['chunk_index'] + 1}"
    return f"[{chunk['original_filename']}，{page}]\n{chunk['content']}"


def _line_cached_response(row: dict, match_type: str, similarity: float) -> dict:
    return {
        "answer": row["answer"],
        "contexts": json.loads(row["contexts_json"]),
        "model": row["model_id"],
        "cache": {
            "hit": True,
            "match_type": match_type,
            "similarity": round(similarity, 4),
            "original_question": row["query_text"],
            "hit_count": int(row["hit_count"] or 0) + 1,
        },
    }


def _line_contexts_overlap(cached_contexts_json: str, current_contexts: list[dict]) -> bool:
    try:
        cached_contexts = json.loads(cached_contexts_json)
    except (TypeError, json.JSONDecodeError):
        return False
    if not cached_contexts or not current_contexts:
        return False
    cached_top = cached_contexts[0]
    current_top = current_contexts[0]
    return cached_top.get("asset_id") == current_top.get("asset_id") and cached_top.get("id") == current_top.get("id")


def require_nas_asset_access(asset: dict | None, user: dict) -> dict:
    if not asset:
        raise HTTPException(status_code=404, detail="NAS asset not found")
    if user["role"] != "admin" and asset["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return asset


def serialize_document_chunks(asset_id: int, chunks: list[dict]) -> list[dict]:
    serialized = []
    for chunk in chunks:
        item = dict(chunk)
        item.pop("embedding", None)
        item["metadata"] = {}
        if item.get("metadata_json"):
            try:
                item["metadata"] = json.loads(item["metadata_json"])
            except json.JSONDecodeError:
                item["metadata"] = {}
        if item.get("image_path"):
            item["image_url"] = f"/api/nas-assets/{asset_id}/chunk-images/{item['id']}"
        serialized.append(item)
    return serialized


def parse_processor_config(asset: dict) -> dict:
    raw = asset.get("processor_config_json")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def format_rag_context(chunk: dict) -> str:
    source = f"Chunk {chunk['chunk_index']}"
    if chunk.get("page_number"):
        source += f", Page {chunk['page_number']}"
    if chunk.get("chunk_type"):
        source += f", Type {chunk['chunk_type']}"
    if chunk.get("retrieval_score") is not None:
        source += f", Retrieval score {chunk['retrieval_score']}"
    return f"[{source}]\n{chunk['content']}"


@app.post("/api/llm/demo-run")
async def llm_demo_run(payload: dict, user: dict = Depends(current_user)) -> dict:
    return await llm_run(payload, user)


@app.get("/api/llm/calls")
async def llm_calls(q: str | None = None, user: dict = Depends(current_user)) -> list[dict]:
    return list_llm_calls(user_id=user["id"], role=user["role"], q=q)


@app.websocket("/ws/notifications")
async def notifications(websocket: WebSocket) -> None:
    user = websocket_user(websocket)
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(user["id"], websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user["id"], websocket)
