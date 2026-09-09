import asyncio
import json
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.auth import SESSION_COOKIE, authenticate, create_session_token, current_user, hash_password, require_meeting_access, websocket_user
from app.db import (
    create_llm_call,
    create_meeting,
    create_nas_asset,
    get_meeting,
    get_nas_asset,
    init_db,
    list_document_chunks,
    list_llm_calls,
    list_meetings,
    list_nas_assets,
    search_document_chunks,
    seed_admin,
)
from app.document_processing import analyzer_for_category, classify_asset, process_nas_asset
from app.llm_catalog import PRICING_UPDATED_AT, get_model, model_summary, provider_summary
from app.llm_runtime import LlmRuntimeError, run_llm
from app.nas import ensure_storage_dirs, nas_discovery_loop
from app.notifications import manager
from app.transcription import process_meeting_transcription

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
RECORDINGS_DIR = BASE_DIR / "storage" / "recordings"
NAS_ASSETS_DIR = BASE_DIR / "storage" / "nas_assets"


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage_dirs(BASE_DIR)
    init_db()
    seed_admin(hash_password("admin123"))
    task = asyncio.create_task(nas_discovery_loop(BASE_DIR))
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="AI Work Meeting Demo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/auth/login")
async def login(payload: dict[str, str]) -> JSONResponse:
    user = authenticate(payload.get("username", ""), payload.get("password", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    response = JSONResponse({"id": user["id"], "username": user["username"], "role": user["role"]})
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user["id"]),
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


@app.post("/api/meetings/upload")
async def upload_meeting(
    background_tasks: BackgroundTasks,
    title: str = Form(default=""),
    audio: UploadFile = File(...),
    user: dict = Depends(current_user),
) -> dict:
    suffix = Path(audio.filename or "recording.webm").suffix.lower() or ".webm"
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    stored_path = RECORDINGS_DIR / stored_name

    with stored_path.open("wb") as destination:
        shutil.copyfileobj(audio.file, destination)

    meeting_title = title.strip() or Path(audio.filename or "瀏覽器錄音").stem or "瀏覽器錄音"
    meeting = create_meeting(
        user_id=user["id"],
        source="web_upload",
        title=meeting_title,
        original_filename=audio.filename or stored_name,
        audio_path=str(stored_path),
        status="processing",
    )
    background_tasks.add_task(process_meeting_transcription, meeting["id"])
    await manager.broadcast(
        {
            "type": "meeting_detected",
            "meeting_id": meeting["id"],
            "title": meeting["title"],
            "message": f"錄音《{meeting['title']}》已保存，正在處理",
            "meeting": meeting,
        }
    )
    return meeting


@app.get("/api/meetings")
async def meetings(q: str | None = None, user: dict = Depends(current_user)) -> list[dict]:
    return list_meetings(user_id=user["id"], role=user["role"], q=q)


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
        analyzer=analyzer_for_category(category),
    )
    background_tasks.add_task(process_nas_asset, asset["id"])
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


@app.get("/api/nas-assets")
async def nas_assets(q: str | None = None, user: dict = Depends(current_user)) -> list[dict]:
    return list_nas_assets(user_id=user["id"], role=user["role"], q=q)


@app.get("/api/nas-assets/{asset_id}")
async def nas_asset_detail(asset_id: int, user: dict = Depends(current_user)) -> dict:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    chunks = list_document_chunks(asset_id) if asset["category"] in {"pdf", "docx"} else []
    return {**asset, "chunks": chunks[:8]}


@app.post("/api/nas-assets/{asset_id}/ask")
async def ask_nas_asset(asset_id: int, payload: dict, user: dict = Depends(current_user)) -> dict:
    asset = require_nas_asset_access(get_nas_asset(asset_id), user)
    question = str(payload.get("question", "")).strip()
    model_id = str(payload.get("model_id", "")).strip()
    api_key = str(payload.get("api_key", "")).strip() or None

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    if asset["category"] not in {"pdf", "docx"} or asset["chunk_count"] < 1:
        raise HTTPException(status_code=400, detail="This file has no RAG chunks")

    chunks = search_document_chunks(asset_id, question, limit=5)
    context = "\n\n".join(
        f"[Chunk {chunk['chunk_index']}]\n{chunk['content']}"
        for chunk in chunks
    )
    rag_prompt = (
        "你是 NAS 文件資料庫助理。請只根據下方 RAG context 回答問題；"
        "如果 context 不足，請明確說明缺少資料。\n\n"
        f"文件：{asset['title']} ({asset['original_filename']})\n\n"
        f"RAG context:\n{context}\n\n"
        f"問題：{question}"
    )
    result = await run_model_with_audit(model_id=model_id, prompt=rag_prompt, api_key=api_key, user=user)
    return {
        **result,
        "asset_id": asset_id,
        "asset_title": asset["title"],
        "question": question,
        "contexts": chunks,
    }


@app.get("/api/llm/models")
async def llm_models(user: dict = Depends(current_user)) -> dict:
    return {
        "updated_at": PRICING_UPDATED_AT,
        "providers": provider_summary(),
        "models": model_summary(),
    }


@app.get("/api/llm/pricing/{model_id}")
async def llm_pricing(model_id: str, user: dict = Depends(current_user)) -> dict:
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"updated_at": PRICING_UPDATED_AT, "model": model}


@app.post("/api/llm/run")
async def llm_run(payload: dict, user: dict = Depends(current_user)) -> dict:
    return await run_model_with_audit(
        model_id=str(payload.get("model_id", "")).strip(),
        prompt=str(payload.get("prompt", "")),
        api_key=str(payload.get("api_key", "")).strip() or None,
        user=user,
    )


async def run_model_with_audit(*, model_id: str, prompt: str, api_key: str | None, user: dict) -> dict:
    requested_model_id = model_id.strip()
    model = get_model(requested_model_id)
    raw_prompt = prompt
    clean_prompt = raw_prompt.strip()

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
        )
        raise HTTPException(status_code=400, detail="Prompt is required")

    free_tier = model["free_tier"]
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
        )
        raise HTTPException(status_code=402, detail="API key is required for this model")

    try:
        result = await run_llm(model, clean_prompt, api_key)
    except LlmRuntimeError as exc:
        create_llm_call(
            user_id=user["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt=clean_prompt,
            response=None,
            status="failed",
            access_mode="api_key" if api_key else "free_no_key",
            error_message=str(exc),
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
            access_mode="api_key" if api_key else "free_no_key",
            error_message=f"Unexpected runtime error: {exc}",
        )
        raise HTTPException(status_code=500, detail="Unexpected runtime error") from exc

    usage = result.get("usage") or {}
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
    )
    return {
        "call_id": call["id"],
        "model_id": model["id"],
        "provider": model["provider"],
        "model": model["name"],
        "caller": user["username"],
        "access_mode": result["access_mode"],
        "answer": result["answer"],
        "usage": usage,
    }


def require_nas_asset_access(asset: dict | None, user: dict) -> dict:
    if not asset:
        raise HTTPException(status_code=404, detail="NAS asset not found")
    if user["role"] != "admin" and asset["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return asset


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
