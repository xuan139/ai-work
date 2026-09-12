from __future__ import annotations

import hashlib
import importlib.util
import re
import shutil
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from app.asr_catalog import ASR_MODELS
from app.asr_runtime import PROJECT_ROOT, resolve_whisper_cpp_binary
from app.db import get_custom_model, update_custom_model_validation
from app.model_registry import custom_catalog_models, validate_download_url
from app.video_catalog import VIDEO_MODELS

MODEL_ROOT = PROJECT_ROOT / "storage" / "models"
CHUNK_SIZE = 1024 * 256


class DownloadJob:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.status = "downloading"
        self.error: str | None = None
        self.downloaded_bytes = 0
        self.total_bytes: int | None = None
        self.started_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.started_at
        self.cancel_event = threading.Event()
        self.thread: threading.Thread | None = None

    def touch(self) -> None:
        self.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")


_jobs: dict[str, DownloadJob] = {}
_lock = threading.Lock()


def list_local_model_statuses() -> list[dict[str, Any]]:
    return [local_model_status(model_id) for model_id in all_local_models()]


def local_model_status(model_id: str) -> dict[str, Any]:
    model = _require_local_model(model_id)
    job = _jobs.get(model_id)
    if model.get("engine") == "whisper.cpp":
        status = whisper_cpp_model_status(model, job)
    elif model.get("engine") == "OpenAI Compatible API":
        status = endpoint_model_status(model)
    elif model_id.startswith("local:faster-whisper-"):
        status = python_runtime_status(model, "faster_whisper", "pip install -r requirements-asr.txt")
    elif model.get("engine") == "Ultralytics YOLO":
        status = file_model_status(
            model,
            job,
            runtime_modules=["ultralytics", "cv2"],
            setup_hint_key="python_video_setup",
            setup_hint="執行 pip install -r requirements-video.txt，並下載完整 YOLO 權重",
        )
    else:
        status = python_runtime_status(model, "funasr", "pip install -r requirements-asr.txt")
    status["model"] = model
    status["validation_status"] = model.get("validation_status", "built_in")
    status["validation_error"] = model.get("validation_error")
    return status


def start_download(model_id: str) -> dict[str, Any]:
    model = _require_local_model(model_id)
    if not model.get("download_url"):
        raise ValueError("此模型沒有可由 NAS 面板下載的單一模型檔")

    with _lock:
        existing = _jobs.get(model_id)
        if existing and existing.status in {"downloading", "cancelling"}:
            return local_model_status(model_id)

        job = DownloadJob(model_id)
        _jobs[model_id] = job
        thread = threading.Thread(target=_download_model_file, args=(model, job), daemon=True)
        job.thread = thread
        thread.start()
    return local_model_status(model_id)


def cancel_download(model_id: str) -> dict[str, Any]:
    _require_local_model(model_id)
    with _lock:
        job = _jobs.get(model_id)
        if job and job.status == "downloading":
            job.cancel_event.set()
            job.status = "cancelling"
            job.touch()
    return local_model_status(model_id)


def whisper_cpp_model_status(model: dict[str, Any], job: DownloadJob | None = None) -> dict[str, Any]:
    path = whisper_model_path(model)
    expected_bytes = int(model.get("expected_bytes") or 0) or None
    current_bytes = path.stat().st_size if path.exists() else 0
    installed = is_complete_model_file(path, expected_bytes, bool(model.get("requires_complete_marker")))

    job_status = job.status if job else None
    status = "installed" if installed else "partial" if current_bytes else "missing"
    if job_status in {"downloading", "cancelling", "failed", "cancelled"}:
        status = job_status
    if job_status == "completed" and installed:
        status = "installed"

    total_bytes = job.total_bytes if job and job.total_bytes else expected_bytes
    downloaded_bytes = current_bytes if status != "downloading" else max(current_bytes, job.downloaded_bytes if job else 0)
    progress = int(min(100, downloaded_bytes * 100 / total_bytes)) if total_bytes else 0
    return {
        "id": model["id"],
        "status": status,
        "installed": installed,
        "downloadable": bool(model.get("download_url")),
        "runtime_installed": resolve_whisper_cpp_binary() is not None,
        "path": str(path),
        "downloaded_bytes": downloaded_bytes,
        "total_bytes": total_bytes,
        "progress": 100 if installed else progress,
        "error": job.error if job else None,
        "updated_at": job.updated_at if job else None,
        "setup_hint_key": "whisper_cpp_setup",
        "setup_hint": "需要 whisper-cli 與完整 ggml 模型檔",
    }


def file_model_status(
    model: dict[str, Any],
    job: DownloadJob | None,
    *,
    runtime_modules: list[str],
    setup_hint_key: str,
    setup_hint: str,
) -> dict[str, Any]:
    path = model_file_path(model)
    expected_bytes = int(model.get("expected_bytes") or 0) or None
    current_bytes = path.stat().st_size if path.exists() else 0
    installed = is_complete_model_file(path, expected_bytes, bool(model.get("requires_complete_marker")))

    job_status = job.status if job else None
    status = "installed" if installed else "partial" if current_bytes else "missing"
    if job_status in {"downloading", "cancelling", "failed", "cancelled"}:
        status = job_status
    if job_status == "completed" and installed:
        status = "installed"

    total_bytes = job.total_bytes if job and job.total_bytes else expected_bytes
    downloaded_bytes = current_bytes if status != "downloading" else max(current_bytes, job.downloaded_bytes if job else 0)
    progress = int(min(100, downloaded_bytes * 100 / total_bytes)) if total_bytes else 100 if installed else 0
    return {
        "id": model["id"],
        "status": status,
        "installed": installed,
        "downloadable": bool(model.get("download_url")),
        "runtime_installed": all(importlib.util.find_spec(module_name) is not None for module_name in runtime_modules),
        "path": str(path),
        "downloaded_bytes": downloaded_bytes,
        "total_bytes": total_bytes,
        "progress": 100 if installed else progress,
        "error": job.error if job else None,
        "updated_at": job.updated_at if job else None,
        "setup_hint_key": setup_hint_key,
        "setup_hint": setup_hint,
    }


def python_runtime_status(model: dict[str, Any], module_name: str, hint: str) -> dict[str, Any]:
    installed = importlib.util.find_spec(module_name) is not None
    return {
        "id": model["id"],
        "status": "installed" if installed else "missing",
        "installed": installed,
        "downloadable": False,
        "runtime_installed": installed,
        "path": None,
        "downloaded_bytes": 0,
        "total_bytes": None,
        "progress": 100 if installed else 0,
        "error": None,
        "updated_at": None,
        "setup_hint_key": "python_asr_setup",
        "setup_hint": hint,
    }


def endpoint_model_status(model: dict[str, Any]) -> dict[str, Any]:
    ready = model.get("validation_status") == "ready"
    return {
        "id": model["id"],
        "status": "installed" if ready else model.get("validation_status") or "registered",
        "installed": ready,
        "downloadable": False,
        "runtime_installed": True,
        "path": model.get("api_base"),
        "downloaded_bytes": 0,
        "total_bytes": None,
        "progress": 100 if ready else 0,
        "error": model.get("validation_error"),
        "updated_at": None,
        "setup_hint_key": "openai_endpoint_setup",
        "setup_hint": "需要可回應 /v1/chat/completions 的 NAS loopback 服務",
    }


def whisper_model_path(model: dict[str, Any]) -> Path:
    return MODEL_ROOT / "whisper" / str(model.get("model_file") or "")


def model_file_path(model: dict[str, Any]) -> Path:
    subdir = str(model.get("storage_subdir") or "whisper")
    return MODEL_ROOT / subdir / str(model.get("model_file") or "")


def is_complete_model_file(path: Path, expected_bytes: int | None, requires_complete_marker: bool = False) -> bool:
    if not path.exists() or not path.is_file():
        return False
    if requires_complete_marker and not path.with_suffix(path.suffix + ".complete").exists():
        return False
    if expected_bytes:
        return path.stat().st_size >= expected_bytes
    return path.stat().st_size > 0


def _download_model_file(model: dict[str, Any], job: DownloadJob) -> None:
    url = str(model["download_url"])
    path = model_file_path(model)
    expected_bytes = int(model.get("expected_bytes") or 0) or None
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        remaining_bytes = max(0, (expected_bytes or 0) - (path.stat().st_size if path.exists() else 0))
        if remaining_bytes and shutil.disk_usage(path.parent).free < remaining_bytes + 64 * 1024 * 1024:
            raise OSError("NAS 可用空間不足，無法下載此模型")
        while not job.cancel_event.is_set():
            current_bytes = path.stat().st_size if path.exists() else 0
            if (expected_bytes or model.get("sha256")) and is_complete_model_file(path, expected_bytes):
                verify_model_checksum(path, model)
                mark_complete_if_needed(path, model)
            if is_complete_model_file(path, expected_bytes, bool(model.get("requires_complete_marker"))):
                job.status = "completed"
                job.downloaded_bytes = current_bytes
                job.total_bytes = expected_bytes or current_bytes
                mark_complete_if_needed(path, model)
                job.touch()
                mark_custom_file_ready(model)
                return

            request = urllib.request.Request(url)
            if current_bytes:
                request.add_header("Range", f"bytes={current_bytes}-")

            with urllib.request.urlopen(request, timeout=45) as response:
                if model.get("custom_model"):
                    validate_download_url(response.geturl())
                status_code = getattr(response, "status", 200)
                if current_bytes and status_code == 200:
                    current_bytes = 0
                    file_mode = "wb"
                else:
                    file_mode = "ab" if current_bytes else "wb"
                total_bytes = _response_total_bytes(response, current_bytes) or expected_bytes
                job.total_bytes = total_bytes
                job.downloaded_bytes = current_bytes
                job.touch()

                with path.open(file_mode) as output:
                    while not job.cancel_event.is_set():
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        output.write(chunk)
                        current_bytes += len(chunk)
                        job.downloaded_bytes = current_bytes
                        job.touch()

            effective_expected_bytes = expected_bytes or job.total_bytes
            if is_complete_model_file(path, effective_expected_bytes):
                verify_model_checksum(path, model)
                mark_complete_if_needed(path, model)
            if is_complete_model_file(path, effective_expected_bytes, bool(model.get("requires_complete_marker"))):
                job.status = "completed"
                job.downloaded_bytes = path.stat().st_size
                job.total_bytes = effective_expected_bytes or job.downloaded_bytes
                job.touch()
                mark_custom_file_ready(model)
                return
            if not job.cancel_event.is_set():
                time.sleep(3)

        job.status = "cancelled"
        job.downloaded_bytes = path.stat().st_size if path.exists() else job.downloaded_bytes
        job.touch()
    except (OSError, ValueError, urllib.error.URLError, TimeoutError) as exc:
        job.status = "failed"
        job.error = str(exc)
        if model.get("custom_model"):
            update_custom_model_validation(model["id"], status="failed", error_message=str(exc))
        job.downloaded_bytes = path.stat().st_size if path.exists() else job.downloaded_bytes
        job.touch()


def _response_total_bytes(response: Any, resumed_from: int) -> int | None:
    content_range = response.headers.get("Content-Range")
    if content_range:
        match = re.search(r"/(\d+)$", content_range)
        if match:
            return int(match.group(1))
    content_length = response.headers.get("Content-Length")
    if content_length and content_length.isdigit():
        return resumed_from + int(content_length)
    return None


def mark_complete_if_needed(path: Path, model: dict[str, Any]) -> None:
    if model.get("requires_complete_marker"):
        path.with_suffix(path.suffix + ".complete").write_text("ok\n", encoding="utf-8")


def verify_model_checksum(path: Path, model: dict[str, Any]) -> None:
    expected = str(model.get("sha256") or "").lower()
    if not expected:
        return
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise ValueError("模型檔 SHA256 驗證失敗")


def mark_custom_file_ready(model: dict[str, Any]) -> None:
    if not model.get("custom_model"):
        return
    runtime_ready = (
        resolve_whisper_cpp_binary() is not None
        if model.get("engine") == "whisper.cpp"
        else all(importlib.util.find_spec(module) is not None for module in ("ultralytics", "cv2"))
    )
    if runtime_ready:
        update_custom_model_validation(model["id"], status="ready", error_message=None)
    else:
        update_custom_model_validation(model["id"], status="runtime_missing", error_message="模型檔完整，但 runtime 尚未安裝")


def validate_custom_file_model(model_id: str) -> dict[str, Any]:
    record = get_custom_model(model_id)
    if not record or record["model_type"] not in {"whisper_cpp", "yolo"}:
        raise ValueError("找不到可驗證的自訂檔案模型")
    model = _require_local_model(model_id)
    path = model_file_path(model)
    expected_bytes = int(model.get("expected_bytes") or 0) or None
    try:
        if not is_complete_model_file(path, expected_bytes):
            raise ValueError("模型檔不存在或大小不完整")
        verify_model_checksum(path, model)
        mark_complete_if_needed(path, model)
        mark_custom_file_ready(model)
        return local_model_status(model_id)
    except ValueError as exc:
        update_custom_model_validation(model_id, status="failed", error_message=str(exc))
        raise


def download_in_progress(model_id: str) -> bool:
    job = _jobs.get(model_id)
    return bool(job and job.status in {"downloading", "cancelling"})


def all_local_models() -> dict[str, dict[str, Any]]:
    built_in = {
        **{model_id: model for model_id, model in ASR_MODELS.items() if model_id.startswith("local:")},
        **{model_id: model for model_id, model in VIDEO_MODELS.items() if model_id.startswith("local:")},
    }
    custom = {
        model["id"]: model
        for model_type in ("whisper_cpp", "yolo", "openai_compatible_llm")
        for model in custom_catalog_models(model_type, ready_only=False)
    }
    return {**built_in, **custom}


def _require_local_model(model_id: str) -> dict[str, Any]:
    model = all_local_models().get(model_id)
    if not model:
        raise ValueError("Local model not found")
    return model
