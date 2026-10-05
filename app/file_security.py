from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

from app.db import create_quarantined_upload, create_security_event


BASE_DIR = Path(__file__).resolve().parent.parent
CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class UploadScanResult:
    status: str
    engine: str | None
    detail: str | None = None


class UploadSecurityError(RuntimeError):
    def __init__(self, message: str, *, quarantined: bool, unavailable: bool = False):
        super().__init__(message)
        self.quarantined = quarantined
        self.unavailable = unavailable


def validated_upload_filename(filename: str | None, fallback: str) -> str:
    candidate = str(filename or fallback).strip()
    if not candidate or candidate in {".", ".."}:
        raise UploadSecurityError("檔名無效", quarantined=False)
    if "/" in candidate or "\\" in candidate or CONTROL_CHARACTERS.search(candidate):
        raise UploadSecurityError("檔名包含路徑或控制字元", quarantined=False)
    if len(candidate.encode("utf-8")) > 240:
        raise UploadSecurityError("檔名過長", quarantined=False)
    return candidate


def upload_scan_mode() -> str:
    configured = os.environ.get("AI_WORK_UPLOAD_SCAN_MODE", "").strip().lower()
    if configured in {"disabled", "optional", "required"}:
        return configured
    return "required" if os.environ.get("AI_WORK_ENV", "development").lower() == "production" else "optional"


def scan_uploaded_file(path: Path) -> UploadScanResult:
    mode = upload_scan_mode()
    if mode == "disabled":
        return UploadScanResult("skipped", None, "upload scanning disabled")

    configured = os.environ.get("AI_WORK_CLAMAV_COMMAND", "clamscan").strip() or "clamscan"
    command = shlex.split(configured)
    executable = shutil.which(command[0])
    if not executable:
        return UploadScanResult("unavailable", command[0], "ClamAV command not found")
    command[0] = executable
    timeout = _positive_int("AI_WORK_CLAMAV_TIMEOUT_SECONDS", 600)
    try:
        result = subprocess.run(
            [*command, "--no-summary", "--infected", "--", str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return UploadScanResult("error", Path(executable).name, str(exc))

    detail = (result.stdout or result.stderr or "").strip()[-1000:] or None
    if result.returncode == 0:
        return UploadScanResult("clean", Path(executable).name, detail)
    if result.returncode == 1:
        return UploadScanResult("infected", Path(executable).name, detail or "malware detected")
    return UploadScanResult(
        "error",
        Path(executable).name,
        detail or f"ClamAV exited with status {result.returncode}",
    )


def inspect_uploaded_file(
    path: Path,
    *,
    original_filename: str,
    user_id: int | None,
    remote_addr: str | None = None,
) -> UploadScanResult:
    result = scan_uploaded_file(path)
    mode = upload_scan_mode()
    must_quarantine = result.status == "infected" or (
        mode == "required" and result.status in {"unavailable", "error"}
    )
    if not must_quarantine:
        return result

    quarantine_path = quarantine_upload(path)
    digest = _file_sha256(quarantine_path)
    reason = result.detail or result.status
    create_quarantined_upload(
        user_id=user_id,
        original_filename=original_filename,
        stored_path=str(quarantine_path),
        file_size=quarantine_path.stat().st_size,
        content_sha256=digest,
        scan_engine=result.engine,
        reason=reason,
    )
    create_security_event(
        user_id=user_id,
        event_type="upload_quarantined",
        severity="critical" if result.status == "infected" else "high",
        source="upload_security",
        detail_json=json.dumps(
            {
                "filename_sha256": hashlib.sha256(original_filename.encode("utf-8")).hexdigest(),
                "content_sha256": digest,
                "scan_status": result.status,
                "scan_engine": result.engine,
                "reason": reason,
            },
            ensure_ascii=False,
        ),
        remote_addr=remote_addr,
    )
    message = "上傳檔案偵測到惡意內容，已移入隔離區"
    if result.status != "infected":
        message = "正式模式無法完成上傳安全掃描，檔案已移入隔離區"
    raise UploadSecurityError(
        message,
        quarantined=True,
        unavailable=result.status in {"unavailable", "error"},
    )


def quarantine_upload(path: Path) -> Path:
    root = Path(
        os.environ.get("AI_WORK_QUARANTINE_DIR", str(BASE_DIR / "storage" / "quarantine"))
    )
    root.mkdir(parents=True, exist_ok=True)
    destination = root / f"{uuid.uuid4().hex}.quarantine"
    path.replace(destination)
    destination.chmod(0o600)
    return destination


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _positive_int(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default
