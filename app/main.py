import asyncio
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.auth import SESSION_COOKIE, authenticate, create_session_token, current_user, hash_password, require_admin, require_meeting_access, websocket_user
from app.analysis_persistence import persist_cloud_asset_analysis
from app.asr_catalog import asr_model_summary, get_asr_model
from app.db import (
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
    list_nas_assets,
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
from app.line_service import LineServiceError, list_line_groups
from app.local_model_manager import (
    cancel_download,
    download_in_progress,
    list_local_model_statuses,
    local_model_status,
    start_download,
    validate_custom_file_model,
)
from app.model_registry import custom_model_to_catalog, register_custom_model
from app.nas import ensure_storage_dirs, nas_discovery_loop
from app.notifications import manager
from app.rag_cache import lookup_rag_cache, normalize_query, store_rag_cache
from app.transcription import process_meeting_transcription
from app.translation_service import TARGET_LANGUAGES
from app.video_catalog import get_video_model, video_model_summary

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
RECORDINGS_DIR = BASE_DIR / "storage" / "recordings"
NAS_ASSETS_DIR = BASE_DIR / "storage" / "nas_assets"
LLM_RUN_LOCKS: dict[tuple[int, str], asyncio.Lock] = {}


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
    tasks = [
        asyncio.create_task(nas_discovery_loop(BASE_DIR)),
        asyncio.create_task(embedding_backfill_loop()),
    ]
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


app = FastAPI(title="AI Work Meeting Demo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


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


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,31}$")
VALID_ROLES = {"admin", "user"}


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


@app.post("/api/meetings/upload")
async def upload_meeting(
    background_tasks: BackgroundTasks,
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
    asr_model = get_asr_model(asr_model_id.strip() or None)
    selected_key = asr_api_key.strip() or None
    if asr_model["requires_api_key"] and not selected_key:
        raise HTTPException(status_code=400, detail=f"{asr_model['name']} 需要 {asr_model.get('api_key_label') or 'API Key'}")
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

    with stored_path.open("wb") as destination:
        shutil.copyfileobj(audio.file, destination)

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
    background_tasks.add_task(
        process_meeting_transcription,
        meeting["id"],
        selected_key,
        selected_translation_key,
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
    return FileResponse(audio_path, filename=meeting["original_filename"], media_type="audio/*")


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

    with stored_path.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)

    category = classify_asset(stored_path, file.content_type)
    processor_config = {}
    selected_audio_key = audio_api_key.strip() or None
    selected_video_key = video_api_key.strip() or None
    selected_translation_key = None
    if category == "audio":
        asr_model = get_asr_model(audio_model_id.strip() or None)
        if asr_model["requires_api_key"] and not selected_audio_key:
            raise HTTPException(status_code=400, detail=f"{asr_model['name']} 需要 {asr_model.get('api_key_label') or 'API Key'}")
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
    model = get_model(model_id.strip())
    if not model:
        raise HTTPException(status_code=400, detail="請選擇翻譯模型")
    selected_key = api_key.strip() or None
    if model["free_tier"]["requires_api_key_for_real_call"] and not selected_key:
        raise HTTPException(status_code=400, detail=f"{model['name']} 翻譯需要 API Key")
    return True, model, selected_key


@app.get("/api/nas-assets")
async def nas_assets(q: str | None = None, user: dict = Depends(current_user)) -> list[dict]:
    return list_nas_assets(user_id=user["id"], role=user["role"], q=q)


@app.get("/api/asr/models")
async def asr_models(user: dict = Depends(current_user)) -> dict:
    return {"models": asr_model_summary()}


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
    return {
        **asset,
        "processor_config": parse_processor_config(asset),
        "chunks": serialize_document_chunks(asset_id, unique_preview),
        "ai_analyses": analyses,
    }


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
    model_id = str(payload.get("model_id", "")).strip()
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
    return {
        "updated_at": PRICING_UPDATED_AT,
        "providers": provider_summary(),
        "models": [with_server_key_status(model) for model in model_summary()],
    }


@app.get("/api/llm/suggestions")
async def llm_suggestions(q: str = "", model_id: str = "", user: dict = Depends(current_user)) -> dict:
    clean_model_id = model_id.strip()
    if not clean_model_id or not get_model(clean_model_id):
        raise HTTPException(status_code=404, detail="Model not found")
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
    model_id = str(payload.get("model_id", "")).strip()
    force_refresh = payload.get("force_refresh") is True
    lock = LLM_RUN_LOCKS.setdefault((user["id"], model_id), asyncio.Lock())
    async with lock:
        return await run_model_with_audit(
            model_id=model_id,
            prompt=str(payload.get("prompt", "")),
            api_key=str(payload.get("api_key", "")).strip() or None,
            user=user,
            use_semantic_cache=True,
            force_refresh=force_refresh,
        )


async def run_model_with_audit(
    *,
    model_id: str,
    prompt: str,
    api_key: str | None,
    user: dict,
    audit_context: dict | None = None,
    use_semantic_cache: bool = False,
    force_refresh: bool = False,
) -> dict:
    requested_model_id = model_id.strip()
    model = get_model(requested_model_id)
    raw_prompt = prompt
    clean_prompt = raw_prompt.strip()
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
            prompt=clean_prompt,
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
            query_vector = await embed_query(clean_prompt, user["id"])
        else:
            cached, query_vector = await lookup_llm_cache(
                user_id=user["id"],
                model_id=model["id"],
                prompt=clean_prompt,
            )
            if cached:
                return record_llm_cache_hit(model=model, prompt=clean_prompt, user=user, cached=cached)

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
            prompt=clean_prompt,
            response=None,
            status="blocked",
            access_mode="no_api_key",
            error_message="API key is required for this model",
            **audit_fields,
        )
        raise HTTPException(status_code=402, detail="API key is required for this model")

    try:
        result = await run_llm(model, clean_prompt, api_key)
        if using_server_key:
            result["access_mode"] = "company_api_key"
    except LlmRuntimeError as exc:
        create_llm_call(
            user_id=user["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=clean_prompt,
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
            prompt=clean_prompt,
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
        prompt=clean_prompt,
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
            model_id=model["id"],
            prompt=clean_prompt,
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
    models = []
    for summary in model_summary():
        model = get_model(summary["id"])
        if not model:
            continue
        if model["provider"] == "Local NAS":
            models.append({**summary, "access_mode": "local_nas"})
        elif company_api_key_for_model(model):
            models.append({**summary, "access_mode": "company_api_key"})
    return models


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

    model_id = str(payload.get("default_model_id", source["default_model_id"])).strip()
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
    with stored_path.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)

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
                model_id=source["default_model_id"],
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
    model_id = source["default_model_id"]
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
