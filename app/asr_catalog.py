from __future__ import annotations

ASR_MODELS = {
    "local:whisper-cpp-small": {
        "id": "local:whisper-cpp-small",
        "provider": "Local",
        "name": "whisper.cpp small",
        "engine": "whisper.cpp",
        "requires_api_key": False,
        "runtime": "Local whisper.cpp CLI with WHISPER_CPP_BIN and WHISPER_CPP_MODEL",
        "model_file": "ggml-small.bin",
        "expected_bytes": 487601967,
        "download_url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
    },
    "local:whisper-cpp-base": {
        "id": "local:whisper-cpp-base",
        "provider": "Local",
        "name": "whisper.cpp base",
        "engine": "whisper.cpp",
        "requires_api_key": False,
        "runtime": "Local whisper.cpp CLI with WHISPER_CPP_BIN and WHISPER_CPP_MODEL",
        "model_file": "ggml-base.bin",
        "expected_bytes": 147951465,
        "download_url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
    },
    "local:faster-whisper-small": {
        "id": "local:faster-whisper-small",
        "provider": "Local",
        "name": "faster-whisper small",
        "engine": "faster-whisper",
        "requires_api_key": False,
        "runtime": "Local faster-whisper Python package",
        "runtime_model": "small",
    },
    "local:faster-whisper-base": {
        "id": "local:faster-whisper-base",
        "provider": "Local",
        "name": "faster-whisper base",
        "engine": "faster-whisper",
        "requires_api_key": False,
        "runtime": "Local faster-whisper Python package",
        "runtime_model": "base",
    },
    "local:sensevoice-small": {
        "id": "local:sensevoice-small",
        "provider": "Local",
        "name": "SenseVoiceSmall",
        "engine": "FunASR SenseVoice",
        "requires_api_key": False,
        "runtime": "Local FunASR Python package and SenseVoiceSmall model files",
    },
    "cloud:openai-gpt-4o-mini-transcribe": {
        "id": "cloud:openai-gpt-4o-mini-transcribe",
        "provider": "OpenAI",
        "name": "gpt-4o-mini-transcribe",
        "engine": "OpenAI Audio Transcriptions API",
        "requires_api_key": True,
        "runtime": "Cloud API",
    },
    "cloud:openai-gpt-4o-transcribe": {
        "id": "cloud:openai-gpt-4o-transcribe",
        "provider": "OpenAI",
        "name": "gpt-4o-transcribe",
        "engine": "OpenAI Audio Transcriptions API",
        "requires_api_key": True,
        "runtime": "Cloud API",
    },
    "cloud:openai-whisper-1": {
        "id": "cloud:openai-whisper-1",
        "provider": "OpenAI",
        "name": "whisper-1",
        "engine": "OpenAI Audio Transcriptions API",
        "requires_api_key": True,
        "runtime": "Cloud API",
    },
}

DEFAULT_ASR_MODEL_ID = "local:whisper-cpp-small"


def get_asr_model(model_id: str | None) -> dict:
    return ASR_MODELS.get(model_id or "", ASR_MODELS[DEFAULT_ASR_MODEL_ID])


def asr_model_summary() -> list[dict]:
    return list(ASR_MODELS.values())
