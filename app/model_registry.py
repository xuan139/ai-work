from __future__ import annotations

import re
import secrets
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.db import create_custom_model, get_custom_model, list_custom_models


MODEL_TYPES = {"whisper_cpp", "yolo", "openai_compatible_llm"}
DOWNLOAD_HOSTS = {
    "huggingface.co",
    "github.com",
    "objects.githubusercontent.com",
    "release-assets.githubusercontent.com",
}
DOWNLOAD_HOST_SUFFIXES = (".huggingface.co", ".hf.co", ".github.com", ".githubusercontent.com")
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
MODEL_SUFFIXES = {
    "whisper_cpp": {".bin", ".ggml", ".gguf"},
    "yolo": {".pt"},
}


def register_custom_model(payload: dict[str, Any], user_id: int) -> dict[str, Any]:
    model_type = str(payload.get("model_type") or "").strip()
    if model_type not in MODEL_TYPES:
        raise ValueError("不支援此模型類型")

    name = str(payload.get("name") or "").strip()
    if not 2 <= len(name) <= 100:
        raise ValueError("模型名稱需為 2 至 100 個字元")

    model_id = build_model_id(model_type, str(payload.get("slug") or name))
    common = {
        "id": model_id,
        "model_type": model_type,
        "name": name,
        "languages": clean_optional(payload.get("languages"), 200),
        "recommended_for": clean_optional(payload.get("recommended_for"), 300),
        "recommendation": clean_optional(payload.get("recommendation"), 500),
        "validation_status": "registered",
        "validation_error": None,
        "is_enabled": 1,
        "created_by": user_id,
        "supports_tokenize": 0,
    }

    if model_type in {"whisper_cpp", "yolo"}:
        model_file = validate_model_file(model_type, payload.get("model_file"))
        validate_model_file_is_available(model_type, model_file)
        download_url = validate_download_url(payload.get("download_url"))
        expected_bytes = parse_expected_bytes(payload.get("expected_size_mb"))
        sha256 = validate_sha256(payload.get("sha256"))
        values = {
            **common,
            "engine": "whisper.cpp" if model_type == "whisper_cpp" else "Ultralytics YOLO",
            "model_alias": None,
            "model_file": model_file,
            "storage_subdir": "whisper" if model_type == "whisper_cpp" else "video",
            "download_url": download_url,
            "expected_bytes": expected_bytes,
            "sha256": sha256,
            "api_base": None,
            "max_input_tokens": None,
        }
    else:
        api_base = validate_loopback_api_base(payload.get("api_base"))
        model_alias = clean_required(payload.get("model_alias"), "模型 alias", 160)
        context_tokens = parse_context_tokens(payload.get("max_input_tokens"))
        values = {
            **common,
            "engine": "OpenAI Compatible API",
            "model_alias": model_alias,
            "model_file": None,
            "storage_subdir": None,
            "download_url": None,
            "expected_bytes": None,
            "sha256": None,
            "api_base": api_base,
            "max_input_tokens": context_tokens,
            "supports_tokenize": int(bool(payload.get("supports_tokenize"))),
        }
    return create_custom_model(values)


def custom_catalog_models(model_type: str, *, ready_only: bool) -> list[dict[str, Any]]:
    return [
        custom_model_to_catalog(model)
        for model in list_custom_models(model_type, enabled_only=True, ready_only=ready_only)
    ]


def get_custom_catalog_model(model_id: str) -> dict[str, Any] | None:
    record = get_custom_model(model_id)
    return custom_model_to_catalog(record) if record and record.get("is_enabled") else None


def custom_model_to_catalog(record: dict[str, Any]) -> dict[str, Any]:
    model_type = record["model_type"]
    common = {
        "id": record["id"],
        "name": record["name"],
        "engine": record["engine"],
        "requires_api_key": False,
        "custom_model": True,
        "validation_status": record["validation_status"],
        "validation_error": record.get("validation_error"),
        "created_by": record["created_by"],
    }
    if model_type == "whisper_cpp":
        return {
            **common,
            "provider": "Local",
            "runtime": "Local whisper.cpp CLI",
            "model_file": record["model_file"],
            "storage_subdir": "whisper",
            "expected_bytes": record.get("expected_bytes"),
            "download_url": record.get("download_url"),
            "sha256": record.get("sha256"),
            "requires_complete_marker": True,
            "languages": record.get("languages") or "多語言，自動偵測",
            "languages_en": record.get("languages") or "Multilingual with auto detection",
            "recommended_for": record.get("recommended_for") or "NAS 本地會議轉寫",
            "recommended_for_en": record.get("recommended_for") or "Local NAS meeting transcription",
            "recommendation": record.get("recommendation") or "由管理員新增的 NAS whisper.cpp 模型。",
            "recommendation_en": record.get("recommendation") or "Administrator-registered NAS whisper.cpp model.",
        }
    if model_type == "yolo":
        return {
            **common,
            "provider": "Local",
            "runtime": "Local ultralytics + OpenCV frame extraction",
            "model_file": record["model_file"],
            "storage_subdir": "video",
            "expected_bytes": record.get("expected_bytes"),
            "download_url": record.get("download_url"),
            "sha256": record.get("sha256"),
            "requires_complete_marker": True,
        }
    return {
        **common,
        "provider": "Local NAS",
        "family": "OpenAI Compatible",
        "model": record["model_alias"],
        "execution": "local",
        "currency": "USD",
        "unit": "request",
        "input": 0.0,
        "output": 0.0,
        "context": f"{record.get('max_input_tokens') or 4096:,} tokens",
        "max_input_tokens": record.get("max_input_tokens") or 4096,
        "api_base": record["api_base"],
        "supports_tokenize": bool(record.get("supports_tokenize")),
        "note": record.get("recommendation") or "Administrator-registered loopback OpenAI-compatible model.",
        "source_url": None,
    }


def build_model_id(model_type: str, source: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", source.lower()).strip("-")[:40]
    if not slug:
        slug = secrets.token_hex(4)
    prefix = {
        "whisper_cpp": "local:whisper-cpp-custom-",
        "yolo": "local:yolo-custom-",
        "openai_compatible_llm": "local:openai-custom-",
    }[model_type]
    return f"{prefix}{slug}"


def validate_model_file(model_type: str, value: object) -> str:
    filename = str(value or "").strip()
    if not filename or filename != Path(filename).name or not re.fullmatch(r"[A-Za-z0-9._-]{2,160}", filename):
        raise ValueError("模型檔名只能包含英文字母、數字、句點、底線與連字號")
    if Path(filename).suffix.lower() not in MODEL_SUFFIXES[model_type]:
        allowed = ", ".join(sorted(MODEL_SUFFIXES[model_type]))
        raise ValueError(f"此模型類型只接受 {allowed} 檔案")
    return filename


def validate_download_url(value: object) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    hostname = parsed.hostname or ""
    trusted_host = hostname in DOWNLOAD_HOSTS or hostname.endswith(DOWNLOAD_HOST_SUFFIXES)
    if parsed.scheme != "https" or not trusted_host or parsed.username or parsed.password:
        raise ValueError("下載網址只允許可信任的 Hugging Face 或 GitHub HTTPS 來源")
    return raw


def validate_model_file_is_available(model_type: str, filename: str) -> None:
    subdir = "whisper" if model_type == "whisper_cpp" else "video"
    if any(
        model.get("storage_subdir") == subdir and model.get("model_file") == filename
        for model in list_custom_models()
    ):
        raise ValueError("此 NAS 模型檔名已被其他自訂模型登錄")
    if model_type == "whisper_cpp":
        from app.asr_catalog import ASR_MODELS

        built_in_files = {model.get("model_file") for model in ASR_MODELS.values()}
    else:
        from app.video_catalog import VIDEO_MODELS

        built_in_files = {model.get("model_file") for model in VIDEO_MODELS.values()}
    if filename in built_in_files:
        raise ValueError("此 NAS 模型檔名已由內建模型使用")


def validate_loopback_api_base(value: object) -> str:
    raw = str(value or "").strip().rstrip("/")
    parsed = urlparse(raw)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in LOOPBACK_HOSTS
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("API endpoint 必須是 NAS 本機的 loopback 根位址，例如 http://127.0.0.1:8080")
    return raw


def parse_expected_bytes(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        megabytes = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("模型大小必須是數字") from exc
    if megabytes <= 0 or megabytes > 102400:
        raise ValueError("模型大小需介於 0 與 102400 MB")
    return int(megabytes * 1024 * 1024)


def parse_context_tokens(value: object) -> int:
    try:
        tokens = int(value or 4096)
    except (TypeError, ValueError) as exc:
        raise ValueError("Context tokens 必須是整數") from exc
    if tokens < 256 or tokens > 1_048_576:
        raise ValueError("Context tokens 需介於 256 與 1048576")
    return tokens


def validate_sha256(value: object) -> str | None:
    checksum = str(value or "").strip().lower()
    if checksum and not re.fullmatch(r"[0-9a-f]{64}", checksum):
        raise ValueError("SHA256 必須是 64 位十六進位字串")
    return checksum or None


def clean_required(value: object, label: str, limit: int) -> str:
    text = str(value or "").strip()
    if not text or len(text) > limit:
        raise ValueError(f"{label} 為必填且不可超過 {limit} 個字元")
    return text


def clean_optional(value: object, limit: int) -> str | None:
    text = str(value or "").strip()
    if len(text) > limit:
        raise ValueError(f"欄位不可超過 {limit} 個字元")
    return text or None
