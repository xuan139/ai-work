from __future__ import annotations

import asyncio
import json
import mimetypes
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from app.db import finalize_network_asset, get_nas_asset, update_nas_asset
from app.media_worker import enqueue_media_job
from app.notifications import manager
from app.llm_runtime import company_api_key_for_model
from app.system_asr import current_asr_model
from app.video_catalog import get_video_model


BASE_DIR = Path(__file__).resolve().parent.parent
NAS_ASSETS_DIR = BASE_DIR / "storage" / "nas_assets"
ALLOWED_YOUTUBE_HOSTS = {"youtube.com", "youtu.be"}


class NetworkImportError(RuntimeError):
    pass


def validate_youtube_url(value: str) -> str:
    url = value.strip()
    if not url:
        raise ValueError("請輸入 YouTube 網址")
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    registrable_host = next((item for item in ALLOWED_YOUTUBE_HOSTS if host == item or host.endswith(f".{item}")), None)
    if parsed.scheme not in {"http", "https"} or not registrable_host:
        raise ValueError("目前只接受 youtube.com 或 youtu.be 網址")
    if parsed.username or parsed.password or parsed.port not in {None, 80, 443}:
        raise ValueError("YouTube 網址格式不正確")
    if not parsed.path or parsed.path == "/":
        raise ValueError("請輸入單一 YouTube 影片網址")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def _download_youtube(asset_id: int, url: str, media_type: str) -> dict[str, Any]:
    try:
        import yt_dlp
    except ImportError as exc:
        raise NetworkImportError("伺服器需要安裝 yt-dlp 才能下載 YouTube 內容") from exc

    NAS_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    prefix = f"youtube-{asset_id}"
    output_template = str(NAS_ASSETS_DIR / f"{prefix}.%(ext)s")
    max_bytes = int(os.environ.get("NETWORK_IMPORT_MAX_BYTES", str(2 * 1024 * 1024 * 1024)))
    last_percent = -1

    def reject_live(info: dict[str, Any], *, incomplete: bool) -> str | None:
        del incomplete
        if info.get("is_live") or info.get("live_status") in {"is_live", "is_upcoming"}:
            return "目前不支援直播或尚未開始的影片"
        return None

    def progress_hook(progress: dict[str, Any]) -> None:
        nonlocal last_percent
        if progress.get("status") != "downloading":
            return
        total = progress.get("total_bytes") or progress.get("total_bytes_estimate")
        downloaded = progress.get("downloaded_bytes") or 0
        if not total:
            return
        percent = min(99, int(downloaded * 100 / total))
        if percent < last_percent + 5:
            return
        last_percent = percent
        update_nas_asset(
            asset_id,
            status="downloading",
            analyzer="YouTube Downloader",
            summary=f"YouTube 內容下載中：{percent}%",
        )

    options: dict[str, Any] = {
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,
        "max_filesize": max_bytes,
        "match_filter": reject_live,
        "progress_hooks": [progress_hook],
    }
    if media_type == "audio":
        options.update(
            {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            }
        )
    else:
        options.update(
            {
                "format": (
                    "bestvideo[ext=mp4][vcodec^=avc1][height<=1080]+bestaudio[ext=m4a]"
                    "/best[ext=mp4][vcodec^=avc1][height<=1080]"
                    "/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
                ),
                "merge_output_format": "mp4",
            }
        )

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=True)
    except Exception as exc:
        raise NetworkImportError(str(exc)[:600]) from exc

    candidates = [
        path
        for path in NAS_ASSETS_DIR.glob(f"{prefix}.*")
        if path.is_file() and path.suffix not in {".part", ".ytdl", ".json"}
    ]
    if not candidates:
        raise NetworkImportError("YouTube 下載完成，但找不到輸出檔案")
    output_path = max(candidates, key=lambda item: item.stat().st_size)
    return {
        "path": output_path,
        "title": str(info.get("title") or "YouTube 網路資料").strip(),
        "filename": output_path.name,
        "mime_type": mimetypes.guess_type(output_path.name)[0] or "application/octet-stream",
        "file_size": output_path.stat().st_size,
    }


async def download_youtube_asset(asset_id: int, url: str, media_type: str, requested_title: str = "") -> None:
    asset = get_nas_asset(asset_id)
    if not asset:
        return
    try:
        downloaded = await asyncio.to_thread(_download_youtube, asset_id, url, media_type)
        if media_type == "audio":
            model = current_asr_model()
            analyzer = model["name"]
            processor_config = {
                "asr_model_id": model["id"],
                "asr_provider": model["provider"],
                "asr_model": model["name"],
                "asr_engine": model["engine"],
                "asr_requires_api_key": model["requires_api_key"],
                "translation_enabled": False,
            }
        else:
            model = get_video_model("local:yolov8n")
            analyzer = model["name"]
            processor_config = {
                "video_model_id": model["id"],
                "video_provider": model["provider"],
                "video_model": model["name"],
                "video_engine": model["engine"],
                "video_requires_api_key": model["requires_api_key"],
            }

        updated = finalize_network_asset(
            asset_id,
            title=requested_title.strip() or downloaded["title"],
            original_filename=downloaded["filename"],
            stored_path=str(downloaded["path"]),
            mime_type=downloaded["mime_type"],
            file_size=downloaded["file_size"],
            analyzer=analyzer,
            processor_config_json=json.dumps(processor_config, ensure_ascii=False),
        )
        await manager.broadcast(
            {
                "type": "nas_asset_uploaded",
                "asset_id": asset_id,
                "title": updated["title"] if updated else asset["title"],
                "message": "YouTube 內容已保存至 NAS，正在進入媒體分析流程。",
                "asset": updated or asset,
            }
        )
        await enqueue_media_job(
            "asset",
            asset_id,
            audio_api_key=company_api_key_for_model(model) if media_type == "audio" else None,
        )
    except Exception as exc:
        failed = update_nas_asset(
            asset_id,
            status="failed",
            analyzer="YouTube Downloader",
            summary=None,
            error_message=str(exc)[:600],
        )
        await manager.broadcast(
            {
                "type": "nas_asset_failed",
                "asset_id": asset_id,
                "title": asset["title"],
                "message": str(exc)[:600],
                "asset": failed or asset,
            }
        )
