from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from app.asr_catalog import get_asr_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AsrRuntimeError(RuntimeError):
    pass


def transcribe_audio(path: Path, model_id: str | None, api_key: str | None = None) -> dict[str, Any]:
    model = get_asr_model(model_id)
    if model["id"].startswith("cloud:openai-"):
        return transcribe_with_openai(path, model, api_key)
    if model["id"].startswith("local:whisper-cpp-"):
        return transcribe_with_whisper_cpp(path, model)
    if model["id"].startswith("local:faster-whisper-"):
        return transcribe_with_faster_whisper(path, model)
    if model["id"] == "local:sensevoice-small":
        return transcribe_with_sensevoice(path, model)
    raise AsrRuntimeError(f"Unsupported ASR model: {model['id']}")


def transcribe_with_openai(path: Path, model: dict[str, Any], api_key: str | None) -> dict[str, Any]:
    if not api_key:
        raise AsrRuntimeError(f"{model['name']} 需要 OpenAI API Key 才能執行雲端語音轉文字")

    boundary = f"----aiwork{uuid.uuid4().hex}"
    body = multipart_body(
        boundary,
        fields={"model": model["name"], "response_format": "json"},
        files={"file": path},
    )
    request = urllib.request.Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AsrRuntimeError(f"OpenAI transcription failed: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise AsrRuntimeError(f"OpenAI transcription request failed: {exc.reason}") from exc

    text = str(payload.get("text", "")).strip()
    if not text:
        raise AsrRuntimeError("OpenAI transcription completed but returned no text")
    return {"text": text, "model": model, "engine": model["engine"], "metadata": payload}


def multipart_body(boundary: str, *, fields: dict[str, str], files: dict[str, Path]) -> bytes:
    lines: list[bytes] = []
    for name, value in fields.items():
        lines.extend(
            [
                f"--{boundary}".encode(),
                f'Content-Disposition: form-data; name="{name}"'.encode(),
                b"",
                value.encode(),
            ]
        )
    for name, path in files.items():
        filename = path.name
        content_type = content_type_for(path)
        lines.extend(
            [
                f"--{boundary}".encode(),
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode(),
                f"Content-Type: {content_type}".encode(),
                b"",
                path.read_bytes(),
            ]
        )
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    return b"\r\n".join(lines)


def content_type_for(path: Path) -> str:
    return {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".mpeg": "audio/mpeg",
        ".mpga": "audio/mpeg",
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
    }.get(path.suffix.lower(), "application/octet-stream")


def transcribe_with_whisper_cpp(path: Path, model: dict[str, Any]) -> dict[str, Any]:
    binary = resolve_whisper_cpp_binary()
    model_path = resolve_whisper_cpp_model(model)
    if not binary:
        raise AsrRuntimeError(
            "需要本地 whisper.cpp runtime：請安裝 whisper-cli，或設定 WHISPER_CPP_BIN"
        )
    if not model_path:
        raise AsrRuntimeError(
            f"需要完整模型檔 {model.get('model_file') or ''}：可在 NAS 模型管理面板下載，或設定 WHISPER_CPP_MODEL"
        )

    with tempfile.TemporaryDirectory(prefix="aiwork-whisper-") as tmpdir:
        output_prefix = Path(tmpdir) / "transcript"
        command = [
            binary,
            "-m",
            model_path,
            "-f",
            str(path),
            "-otxt",
            "-of",
            str(output_prefix),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=600, check=False)
        if completed.returncode != 0:
            raise AsrRuntimeError(f"whisper.cpp transcription failed: {completed.stderr or completed.stdout}")
        text_path = output_prefix.with_suffix(".txt")
        text = text_path.read_text(encoding="utf-8").strip() if text_path.exists() else completed.stdout.strip()
        if not text:
            raise AsrRuntimeError("whisper.cpp transcription completed but returned no text")
    return {"text": text, "model": model, "engine": model["engine"], "metadata": {"runtime": binary, "model_path": model_path}}


def resolve_whisper_cpp_binary() -> str | None:
    candidates = [
        os.environ.get("WHISPER_CPP_BIN"),
        shutil.which("whisper-cli"),
        shutil.which("whisper"),
        str(PROJECT_ROOT / "storage/runtime/whisper.cpp/build/bin/whisper-cli"),
        str(PROJECT_ROOT / "storage/runtime/whisper.cpp/build/bin/main"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def model_file_is_complete(path: Path, expected_bytes: Any) -> bool:
    if not path.is_file():
        return False
    try:
        expected = int(expected_bytes or 0)
    except (TypeError, ValueError):
        expected = 0
    return path.stat().st_size >= expected if expected else path.stat().st_size > 0


def resolve_whisper_cpp_model(model: dict[str, Any]) -> str | None:
    env_model = os.environ.get("WHISPER_CPP_MODEL")
    candidates = [
        env_model,
        str(PROJECT_ROOT / "storage/models/whisper" / str(model.get("model_file") or "")),
        str(PROJECT_ROOT / "storage/runtime/whisper.cpp/models" / str(model.get("model_file") or "")),
    ]
    for candidate in candidates:
        if candidate and model_file_is_complete(Path(candidate), model.get("expected_bytes")):
            return candidate
    return None


def transcribe_with_faster_whisper(path: Path, model: dict[str, Any]) -> dict[str, Any]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise AsrRuntimeError("需要本地 faster-whisper runtime：請安裝 faster-whisper 後再執行") from exc

    runtime_model = str(model.get("runtime_model") or "small")
    device = os.environ.get("FASTER_WHISPER_DEVICE", "cpu")
    compute_type = os.environ.get("FASTER_WHISPER_COMPUTE_TYPE", "int8")
    recognizer = WhisperModel(runtime_model, device=device, compute_type=compute_type)
    segments, info = recognizer.transcribe(str(path), vad_filter=True)
    text = "\n".join(segment.text.strip() for segment in segments if segment.text.strip())
    if not text:
        raise AsrRuntimeError("faster-whisper transcription completed but returned no text")
    metadata = {
        "runtime_model": runtime_model,
        "device": device,
        "compute_type": compute_type,
        "language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
    }
    return {"text": text, "model": model, "engine": model["engine"], "metadata": metadata}


def transcribe_with_sensevoice(path: Path, model: dict[str, Any]) -> dict[str, Any]:
    try:
        from funasr import AutoModel
    except ImportError as exc:
        raise AsrRuntimeError("需要本地 SenseVoiceSmall runtime：請安裝 funasr 並下載 SenseVoiceSmall 模型") from exc

    model_path = os.environ.get("SENSEVOICE_MODEL_PATH", "iic/SenseVoiceSmall")
    vad_model = os.environ.get("SENSEVOICE_VAD_MODEL", "fsmn-vad")
    recognizer = AutoModel(model=model_path, vad_model=vad_model)
    result = recognizer.generate(input=str(path), language="auto", use_itn=True)
    text = collect_sensevoice_text(result)
    if not text:
        raise AsrRuntimeError("SenseVoiceSmall transcription completed but returned no text")
    return {"text": text, "model": model, "engine": model["engine"], "metadata": {"model_path": model_path, "vad_model": vad_model}}


def collect_sensevoice_text(value: Any) -> str:
    parts: list[str] = []
    if isinstance(value, dict):
        text = value.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())
        for item in value.values():
            if isinstance(item, (dict, list, tuple)):
                nested = collect_sensevoice_text(item)
                if nested:
                    parts.append(nested)
    elif isinstance(value, (list, tuple)):
        for item in value:
            nested = collect_sensevoice_text(item)
            if nested:
                parts.append(nested)
    return "\n".join(dict.fromkeys(parts))
