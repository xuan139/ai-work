from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
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
    if model["id"] == "cloud:deepgram-nova-3":
        return transcribe_with_deepgram(path, model, api_key)
    if model["id"] == "cloud:assemblyai-universal":
        return transcribe_with_assemblyai(path, model, api_key)
    if model["id"].startswith("local:whisper-cpp-"):
        return transcribe_with_whisper_cpp(path, model)
    if model["id"].startswith("local:faster-whisper-"):
        return transcribe_with_faster_whisper(path, model)
    if model["id"] == "local:sensevoice-small":
        return transcribe_with_sensevoice(path, model)
    if model["id"] == "local:funasr-paraformer-zh":
        return transcribe_with_paraformer(path, model)
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


def transcribe_with_deepgram(path: Path, model: dict[str, Any], api_key: str | None) -> dict[str, Any]:
    if not api_key:
        raise AsrRuntimeError(f"{model['name']} 需要 Deepgram API Key 才能執行雲端語音轉文字")

    request = urllib.request.Request(
        "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true&detect_language=true",
        data=path.read_bytes(),
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": content_type_for(path),
        },
        method="POST",
    )
    payload = request_json(request, "Deepgram transcription", timeout=300)
    try:
        channel = payload["results"]["channels"][0]
        alternative = channel["alternatives"][0]
        text = str(alternative.get("transcript", "")).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise AsrRuntimeError("Deepgram transcription returned an invalid response") from exc
    if not text:
        raise AsrRuntimeError("Deepgram transcription completed but returned no text")
    metadata = {
        "request_id": payload.get("metadata", {}).get("request_id"),
        "duration": payload.get("metadata", {}).get("duration"),
        "detected_language": channel.get("detected_language"),
        "confidence": alternative.get("confidence"),
    }
    return {"text": text, "model": model, "engine": model["engine"], "metadata": metadata}


def transcribe_with_assemblyai(path: Path, model: dict[str, Any], api_key: str | None) -> dict[str, Any]:
    if not api_key:
        raise AsrRuntimeError(f"{model['name']} 需要 AssemblyAI API Key 才能執行雲端語音轉文字")

    upload_request = urllib.request.Request(
        "https://api.assemblyai.com/v2/upload",
        data=path.read_bytes(),
        headers={"Authorization": api_key, "Content-Type": "application/octet-stream"},
        method="POST",
    )
    upload_payload = request_json(upload_request, "AssemblyAI upload", timeout=300)
    audio_url = str(upload_payload.get("upload_url", "")).strip()
    if not audio_url:
        raise AsrRuntimeError("AssemblyAI upload completed but returned no audio URL")

    create_request = urllib.request.Request(
        "https://api.assemblyai.com/v2/transcript",
        data=json.dumps({"audio_url": audio_url, "speech_models": ["universal"]}).encode("utf-8"),
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    transcript_job = request_json(create_request, "AssemblyAI transcription", timeout=120)
    transcript_id = str(transcript_job.get("id", "")).strip()
    if not transcript_id:
        raise AsrRuntimeError("AssemblyAI transcription did not return a job ID")

    deadline = time.monotonic() + 900
    payload = transcript_job
    while payload.get("status") not in {"completed", "error"}:
        if time.monotonic() >= deadline:
            raise AsrRuntimeError("AssemblyAI transcription timed out")
        time.sleep(2)
        poll_request = urllib.request.Request(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers={"Authorization": api_key},
            method="GET",
        )
        payload = request_json(poll_request, "AssemblyAI transcription status", timeout=120)

    if payload.get("status") == "error":
        raise AsrRuntimeError(f"AssemblyAI transcription failed: {payload.get('error') or 'unknown error'}")
    text = str(payload.get("text", "")).strip()
    if not text:
        raise AsrRuntimeError("AssemblyAI transcription completed but returned no text")
    metadata = {
        "transcript_id": transcript_id,
        "speech_model_used": payload.get("speech_model_used"),
        "language_code": payload.get("language_code"),
        "audio_duration": payload.get("audio_duration"),
    }
    return {"text": text, "model": model, "engine": model["engine"], "metadata": metadata}


def request_json(request: urllib.request.Request, operation: str, timeout: int) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AsrRuntimeError(f"{operation} failed: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise AsrRuntimeError(f"{operation} request failed: {exc.reason}") from exc
    except (TimeoutError, json.JSONDecodeError) as exc:
        raise AsrRuntimeError(f"{operation} request failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise AsrRuntimeError(f"{operation} returned an invalid response")
    return payload


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
        temp_dir = Path(tmpdir)
        input_path = prepare_whisper_cpp_input(path, temp_dir)
        output_prefix = temp_dir / "transcript"
        command = [
            binary,
            "-m",
            model_path,
            "-f",
            str(input_path),
            "-l",
            "auto",
            "-otxt",
            "-of",
            str(output_prefix),
        ]
        use_gpu = os.environ.get("WHISPER_CPP_USE_GPU", "0").strip().lower() in {"1", "true", "yes", "on"}
        if not use_gpu:
            command.insert(1, "-ng")
        completed = subprocess.run(command, capture_output=True, text=True, timeout=600, check=False)
        if completed.returncode != 0:
            raise AsrRuntimeError(f"whisper.cpp transcription failed: {completed.stderr or completed.stdout}")
        text_path = output_prefix.with_suffix(".txt")
        text = text_path.read_text(encoding="utf-8").strip() if text_path.exists() else completed.stdout.strip()
        if not text:
            raise AsrRuntimeError("whisper.cpp transcription completed but returned no text")
    return {
        "text": text,
        "model": model,
        "engine": model["engine"],
        "metadata": {"runtime": binary, "model_path": model_path, "device": "gpu" if use_gpu else "cpu"},
    }


def prepare_whisper_cpp_input(path: Path, temp_dir: Path) -> Path:
    if path.suffix.lower() in {".flac", ".mp3", ".ogg", ".wav"}:
        return path

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise AsrRuntimeError(
            f"whisper.cpp 不支援 {path.suffix or '此'} 音訊格式，請安裝 ffmpeg 以轉換為 WAV"
        )

    converted_path = temp_dir / "input.wav"
    completed = subprocess.run(
        [ffmpeg, "-y", "-i", str(path), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(converted_path)],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    if completed.returncode != 0 or not converted_path.is_file():
        raise AsrRuntimeError(f"音訊格式轉換失敗：{completed.stderr or completed.stdout}")
    return converted_path


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
    stored_model = str(PROJECT_ROOT / "storage/models/whisper" / str(model.get("model_file") or ""))
    if model.get("custom_model"):
        candidates = [stored_model]
    else:
        candidates = [
            os.environ.get("WHISPER_CPP_MODEL"),
            stored_model,
            str(PROJECT_ROOT / "storage/runtime/whisper.cpp/models" / str(model.get("model_file") or "")),
        ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if model.get("requires_complete_marker") and not path.with_suffix(path.suffix + ".complete").is_file():
            continue
        if model_file_is_complete(path, model.get("expected_bytes")):
            return str(path)
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


def transcribe_with_paraformer(path: Path, model: dict[str, Any]) -> dict[str, Any]:
    try:
        from funasr import AutoModel
    except ImportError as exc:
        raise AsrRuntimeError("需要本地 Paraformer runtime：請安裝 funasr 並取得 Paraformer 模型") from exc

    model_path = os.environ.get("PARAFORMER_MODEL_PATH", str(model.get("runtime_model") or "paraformer-zh"))
    vad_model = os.environ.get("PARAFORMER_VAD_MODEL", "fsmn-vad")
    punc_model = os.environ.get("PARAFORMER_PUNC_MODEL", "ct-punc")
    recognizer = AutoModel(model=model_path, vad_model=vad_model, punc_model=punc_model)
    result = recognizer.generate(input=str(path), batch_size_s=300)
    text = collect_sensevoice_text(result)
    if not text:
        raise AsrRuntimeError("Paraformer transcription completed but returned no text")
    metadata = {"model_path": model_path, "vad_model": vad_model, "punc_model": punc_model}
    return {"text": text, "model": model, "engine": model["engine"], "metadata": metadata}


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
