from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.asr_runtime import PROJECT_ROOT
from app.video_catalog import get_video_model

NAS_ASSETS_DIR = PROJECT_ROOT / "storage" / "nas_assets"
VIDEO_MODEL_ROOT = PROJECT_ROOT / "storage" / "models" / "video"
DEFAULT_FRAME_INTERVAL_SECONDS = 2.0
MAX_ANALYZED_FRAMES = 12


class VideoRuntimeError(RuntimeError):
    pass


def analyze_video(path: Path, model_id: str | None, api_key: str | None = None) -> dict[str, Any]:
    model = get_video_model(model_id)
    if model["requires_api_key"] and not api_key:
        raise VideoRuntimeError(f"{model['name']} 需要 API Key，請先在 video 模型設定中輸入。")
    if model["id"].startswith("cloud:"):
        raise VideoRuntimeError(f"{model['name']} 已置入選項；目前尚未接入此雲端影片分析 API。")
    if model["engine"] != "Ultralytics YOLO":
        raise VideoRuntimeError(f"{model['name']} 需要安裝對應本地視覺語言 runtime 後才能執行。")

    return analyze_video_with_yolo(path, model)


def resolve_yolo_model_path(model: dict[str, Any]) -> Path | None:
    filename = model.get("model_file")
    if not filename:
        return None
    path = VIDEO_MODEL_ROOT / str(filename)
    marker = path.with_suffix(path.suffix + ".complete")
    if model.get("requires_complete_marker"):
        return path if path.exists() and marker.exists() else None
    return path if path.exists() and path.is_file() else None


def analyze_video_with_yolo(path: Path, model: dict[str, Any]) -> dict[str, Any]:
    try:
        import cv2
    except ImportError as exc:
        raise VideoRuntimeError("需要安裝 OpenCV：請執行 pip install -r requirements-video.txt") from exc
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise VideoRuntimeError("需要安裝 Ultralytics YOLO：請執行 pip install -r requirements-video.txt") from exc

    model_path = resolve_yolo_model_path(model)
    if model_path is None:
        raise VideoRuntimeError(f"需要先在 NAS 模型管理下載完整的 {model['name']} 模型檔。")

    frames = extract_sample_frames(path, cv2)
    if not frames:
        raise VideoRuntimeError("影片無法抽取可分析畫面，請確認檔案格式可被 OpenCV 讀取。")

    detector = YOLO(str(model_path))
    detections: list[dict[str, Any]] = []
    object_counts: dict[str, int] = {}
    for frame in frames:
        results = detector.predict(source=str(frame["image_path"]), verbose=False, conf=0.25)
        labels: list[dict[str, Any]] = []
        for result in results:
            names = getattr(result, "names", {}) or {}
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            for box in boxes:
                cls_value = int(box.cls[0].item()) if getattr(box, "cls", None) is not None else -1
                confidence = float(box.conf[0].item()) if getattr(box, "conf", None) is not None else 0.0
                label = str(names.get(cls_value, f"class_{cls_value}"))
                labels.append({"label": label, "confidence": round(confidence, 3)})
                object_counts[label] = object_counts.get(label, 0) + 1
        detections.append({**frame, "objects": labels})

    summary = summarize_detections(detections, object_counts, model)
    return {
        "engine": model["engine"],
        "model": model,
        "detections": detections,
        "object_counts": object_counts,
        "summary": summary,
    }


def extract_sample_frames(path: Path, cv2: Any) -> list[dict[str, Any]]:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        return []

    fps = capture.get(cv2.CAP_PROP_FPS) or 0
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if fps <= 0 or frame_count <= 0:
        capture.release()
        return []

    interval = max(1, int(fps * DEFAULT_FRAME_INTERVAL_SECONDS))
    indexes = list(range(0, frame_count, interval))[:MAX_ANALYZED_FRAMES]
    output_dir = path.parent / f"{path.stem}_video_frames"
    output_dir.mkdir(parents=True, exist_ok=True)

    frames: list[dict[str, Any]] = []
    for index in indexes:
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = capture.read()
        if not ok:
            continue
        timestamp = index / fps
        image_path = output_dir / f"frame-{len(frames) + 1:03d}.jpg"
        cv2.imwrite(str(image_path), frame)
        frames.append({"frame_index": index, "timestamp_seconds": round(timestamp, 2), "image_path": image_path})
    capture.release()
    return frames


def summarize_detections(detections: list[dict[str, Any]], object_counts: dict[str, int], model: dict[str, Any]) -> str:
    if not detections:
        return f"已使用 {model['name']} 完成影片抽幀，但沒有取得可用偵測結果。"
    if not object_counts:
        return f"已使用 {model['name']} 分析 {len(detections)} 個影片畫面；未偵測到高信心物件。"
    top_objects = sorted(object_counts.items(), key=lambda item: (-item[1], item[0]))[:8]
    object_text = "、".join(f"{label} {count} 次" for label, count in top_objects)
    return f"已使用 {model['name']} 分析 {len(detections)} 個影片畫面；主要偵測物件：{object_text}。"


def build_video_detection_chunks(path: Path, result: dict[str, Any]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    model = result["model"]
    for detection in result["detections"]:
        objects = detection.get("objects", [])
        if objects:
            object_text = "、".join(f"{item['label']}({item['confidence']})" for item in objects[:12])
        else:
            object_text = "此畫面未偵測到高信心物件"
        content = f"影片 {path.name} 在 {detection['timestamp_seconds']} 秒的畫面分析：{object_text}"
        chunks.append(
            {
                "chunk_index": len(chunks),
                "content": content,
                "token_estimate": max(1, len(content) // 4),
                "page_number": None,
                "chunk_type": "video_detection",
                "image_path": str(detection["image_path"]),
                "metadata_json": json.dumps(
                    {
                        "source": path.name,
                        "category": "video",
                        "timestamp_seconds": detection["timestamp_seconds"],
                        "frame_index": detection["frame_index"],
                        "video_model_id": model["id"],
                        "video_model": model["name"],
                        "video_engine": result["engine"],
                        "objects": objects,
                    },
                    ensure_ascii=False,
                ),
            }
        )
    return chunks
