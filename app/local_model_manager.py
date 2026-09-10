from __future__ import annotations

import importlib.util
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from app.asr_catalog import ASR_MODELS
from app.asr_runtime import PROJECT_ROOT, resolve_whisper_cpp_binary

MODEL_ROOT = PROJECT_ROOT / "storage" / "models" / "whisper"
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
    return [local_model_status(model_id) for model_id, model in ASR_MODELS.items() if model_id.startswith("local:")]


def local_model_status(model_id: str) -> dict[str, Any]:
    model = _require_local_model(model_id)
    job = _jobs.get(model_id)
    if model_id.startswith("local:whisper-cpp-"):
        status = whisper_cpp_model_status(model, job)
    elif model_id.startswith("local:faster-whisper-"):
        status = python_runtime_status(model, "faster_whisper", "pip install -r requirements-asr.txt")
    else:
        status = python_runtime_status(model, "funasr", "pip install -r requirements-asr.txt")
    status["model"] = model
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
    installed = is_complete_model_file(path, expected_bytes)

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
        "downloadable": True,
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


def whisper_model_path(model: dict[str, Any]) -> Path:
    return MODEL_ROOT / str(model.get("model_file") or "")


def is_complete_model_file(path: Path, expected_bytes: int | None) -> bool:
    if not path.exists() or not path.is_file():
        return False
    if expected_bytes:
        return path.stat().st_size >= expected_bytes
    return path.stat().st_size > 0


def _download_model_file(model: dict[str, Any], job: DownloadJob) -> None:
    url = str(model["download_url"])
    path = whisper_model_path(model)
    expected_bytes = int(model.get("expected_bytes") or 0) or None
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        while not job.cancel_event.is_set():
            current_bytes = path.stat().st_size if path.exists() else 0
            if is_complete_model_file(path, expected_bytes):
                job.status = "completed"
                job.downloaded_bytes = current_bytes
                job.total_bytes = expected_bytes or current_bytes
                job.touch()
                return

            request = urllib.request.Request(url)
            if current_bytes:
                request.add_header("Range", f"bytes={current_bytes}-")

            with urllib.request.urlopen(request, timeout=45) as response:
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

            if is_complete_model_file(path, expected_bytes):
                job.status = "completed"
                job.downloaded_bytes = path.stat().st_size
                job.total_bytes = expected_bytes or job.downloaded_bytes
                job.touch()
                return
            if not job.cancel_event.is_set():
                time.sleep(3)

        job.status = "cancelled"
        job.downloaded_bytes = path.stat().st_size if path.exists() else job.downloaded_bytes
        job.touch()
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        job.status = "failed"
        job.error = str(exc)
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


def _require_local_model(model_id: str) -> dict[str, Any]:
    model = ASR_MODELS.get(model_id)
    if not model or not model_id.startswith("local:"):
        raise ValueError("Local model not found")
    return model
