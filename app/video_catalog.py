from __future__ import annotations

VIDEO_MODELS = {
    "local:yolov8n": {
        "id": "local:yolov8n",
        "provider": "Local",
        "name": "YOLOv8n",
        "engine": "Ultralytics YOLO",
        "requires_api_key": False,
        "runtime": "Local ultralytics + OpenCV frame extraction",
        "model_file": "yolov8n.pt",
        "storage_subdir": "video",
        "download_url": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt",
        "requires_complete_marker": True,
    },
    "local:yolo11n": {
        "id": "local:yolo11n",
        "provider": "Local",
        "name": "YOLO11n",
        "engine": "Ultralytics YOLO",
        "requires_api_key": False,
        "runtime": "Local ultralytics + OpenCV frame extraction",
        "model_file": "yolo11n.pt",
        "storage_subdir": "video",
        "download_url": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
        "requires_complete_marker": True,
    },
    "local:qwen2.5-vl-3b": {
        "id": "local:qwen2.5-vl-3b",
        "provider": "Local",
        "name": "Qwen2.5-VL-3B-Instruct",
        "engine": "Transformers Vision-Language",
        "requires_api_key": False,
        "runtime": "Local transformers vision-language runtime",
        "storage_subdir": "video",
    },
    "cloud:gemini-flash-video": {
        "id": "cloud:gemini-flash-video",
        "provider": "Google Gemini",
        "name": "Gemini Flash Video",
        "engine": "Gemini multimodal video analysis API",
        "requires_api_key": True,
        "runtime": "Cloud API",
    },
    "cloud:openai-vision-frame-summary": {
        "id": "cloud:openai-vision-frame-summary",
        "provider": "OpenAI",
        "name": "OpenAI vision frame summary",
        "engine": "Frame extraction + OpenAI vision API",
        "requires_api_key": True,
        "runtime": "Cloud API",
    },
    "cloud:claude-vision-frame-summary": {
        "id": "cloud:claude-vision-frame-summary",
        "provider": "Anthropic",
        "name": "Claude vision frame summary",
        "engine": "Frame extraction + Claude vision API",
        "requires_api_key": True,
        "runtime": "Cloud API",
    },
}

DEFAULT_VIDEO_MODEL_ID = "local:yolov8n"


def get_video_model(model_id: str | None) -> dict:
    if not model_id:
        return VIDEO_MODELS[DEFAULT_VIDEO_MODEL_ID]
    if model_id in VIDEO_MODELS:
        return VIDEO_MODELS[model_id]
    from app.model_registry import get_custom_catalog_model

    custom = get_custom_catalog_model(model_id)
    return custom if custom and custom.get("engine") == "Ultralytics YOLO" else VIDEO_MODELS[DEFAULT_VIDEO_MODEL_ID]


def video_model_summary() -> list[dict]:
    from app.model_registry import custom_catalog_models

    return [*VIDEO_MODELS.values(), *custom_catalog_models("yolo", ready_only=True)]
