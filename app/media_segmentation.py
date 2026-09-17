from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SPLIT_THRESHOLD_BYTES = 100 * 1024 * 1024
DEFAULT_AUDIO_SPLIT_THRESHOLD_SECONDS = 30 * 60
DEFAULT_VIDEO_SPLIT_THRESHOLD_SECONDS = 10 * 60
DEFAULT_AUDIO_SEGMENT_SECONDS = 10 * 60
DEFAULT_VIDEO_SEGMENT_SECONDS = 5 * 60
BASE_DIR = Path(__file__).resolve().parent.parent


class MediaSegmentationError(RuntimeError):
    pass


@dataclass(frozen=True)
class MediaSegment:
    path: Path
    index: int
    start_seconds: float
    duration_seconds: float | None


@dataclass
class SegmentBatch:
    segments: list[MediaSegment]
    segmented: bool
    source_duration_seconds: float | None
    working_dir: Path | None = None

    def cleanup(self) -> None:
        if self.working_dir:
            shutil.rmtree(self.working_dir, ignore_errors=True)


def prepare_media_segments(path: Path, category: str) -> SegmentBatch:
    duration = probe_media_duration(path)
    if not media_requires_segmentation(path, category, duration):
        return SegmentBatch(
            segments=[MediaSegment(path=path, index=0, start_seconds=0.0, duration_seconds=duration)],
            segmented=False,
            source_duration_seconds=duration,
        )

    ffmpeg = os.environ.get("FFMPEG_BIN", "").strip() or shutil.which("ffmpeg")
    if not ffmpeg:
        raise MediaSegmentationError("大型媒體需要 ffmpeg 才能自動切分")

    segment_seconds = media_segment_seconds(category)
    working_dir = path.parent / ".media_segments" / f"{path.stem}-{uuid.uuid4().hex[:10]}"
    working_dir.mkdir(parents=True, exist_ok=True)
    suffix = ".wav" if category == "audio" else ".mkv"
    output_pattern = working_dir / f"segment-%04d{suffix}"
    try:
        command = build_segment_command(ffmpeg, path, output_pattern, category, segment_seconds, copy_video=True)
        completed = run_segment_command(command)
        copied_video_paths = sorted(working_dir.glob(f"segment-*{suffix}"))
        copy_needs_reencode = (
            category == "video"
            and completed.returncode == 0
            and video_segments_exceed_target(copied_video_paths, segment_seconds)
        )
        if category == "video" and (completed.returncode != 0 or copy_needs_reencode):
            for partial in working_dir.glob("segment-*.*"):
                partial.unlink(missing_ok=True)
            command = build_segment_command(ffmpeg, path, output_pattern, category, segment_seconds, copy_video=False)
            completed = run_segment_command(command)
        if completed.returncode != 0:
            raise MediaSegmentationError(f"媒體切分失敗：{command_error(completed)}")

        paths = sorted(working_dir.glob(f"segment-*{suffix}"))
        if not paths:
            raise MediaSegmentationError("媒體切分完成但沒有產生片段")
        segments = describe_segments(paths, segment_seconds)
        if not segments:
            raise MediaSegmentationError("媒體切分後沒有足夠長度的有效片段")
        return SegmentBatch(
            segments=segments,
            segmented=True,
            source_duration_seconds=duration,
            working_dir=working_dir,
        )
    except Exception:
        shutil.rmtree(working_dir, ignore_errors=True)
        raise


def archive_media_segments(asset_id: int, category: str, segments: list[MediaSegment]) -> list[dict]:
    if category not in {"audio", "video"}:
        raise ValueError(f"不支援的媒體切片類型：{category}")
    root = media_segment_root(category)
    root.mkdir(parents=True, exist_ok=True)
    target = root / str(asset_id)
    staging = root / f".{asset_id}-{uuid.uuid4().hex[:10]}"
    backup = root / f".{asset_id}-old-{uuid.uuid4().hex[:10]}"
    staging.mkdir(parents=True, exist_ok=False)
    manifest: list[dict] = []
    try:
        for segment in segments:
            suffix = ".wav" if category == "audio" else segment.path.suffix.lower() or ".mkv"
            filename = f"segment-{segment.index + 1:04d}{suffix}"
            destination = staging / filename
            shutil.copy2(segment.path, destination)
            manifest.append(
                {
                    "index": segment.index,
                    "filename": filename,
                    "start_seconds": segment.start_seconds,
                    "duration_seconds": segment.duration_seconds,
                    "file_size": destination.stat().st_size,
                }
            )
        (staging / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if target.exists():
            target.replace(backup)
        staging.replace(target)
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        if backup.exists() and not target.exists():
            backup.replace(target)
        raise


def list_archived_media_segments(asset_id: int, category: str) -> list[dict]:
    directory = media_segment_directory(asset_id, category)
    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(manifest, list):
        return []
    result = []
    for item in manifest:
        if not isinstance(item, dict) or not isinstance(item.get("filename"), str):
            continue
        if Path(item["filename"]).name != item["filename"]:
            continue
        path = directory / item["filename"]
        if path.parent != directory or not path.is_file():
            continue
        result.append({**item, "file_size": path.stat().st_size})
    return result


def archived_media_segment_path(asset_id: int, category: str, segment_index: int) -> Path | None:
    for segment in list_archived_media_segments(asset_id, category):
        if segment.get("index") == segment_index:
            return media_segment_directory(asset_id, category) / segment["filename"]
    return None


def media_segment_root(category: str) -> Path:
    if category not in {"audio", "video"}:
        raise ValueError(f"不支援的媒體切片類型：{category}")
    return Path(
        os.environ.get(
            f"{category.upper()}_SEGMENT_ARCHIVE_DIR",
            str(BASE_DIR / "storage" / "media_segments" / category),
        )
    )


def media_segment_directory(asset_id: int, category: str) -> Path:
    return media_segment_root(category) / str(asset_id)


def archive_audio_segments(asset_id: int, segments: list[MediaSegment]) -> list[dict]:
    return archive_media_segments(asset_id, "audio", segments)


def list_archived_audio_segments(asset_id: int) -> list[dict]:
    return list_archived_media_segments(asset_id, "audio")


def archived_audio_segment_path(asset_id: int, segment_index: int) -> Path | None:
    return archived_media_segment_path(asset_id, "audio", segment_index)


def audio_segment_directory(asset_id: int) -> Path:
    return media_segment_directory(asset_id, "audio")


def media_requires_segmentation(path: Path, category: str, duration_seconds: float | None) -> bool:
    if category not in {"audio", "video"}:
        return False
    size_threshold = environment_positive_int(
        f"{category.upper()}_SPLIT_THRESHOLD_BYTES",
        environment_positive_int("MEDIA_SPLIT_THRESHOLD_BYTES", DEFAULT_SPLIT_THRESHOLD_BYTES),
    )
    duration_default = (
        DEFAULT_AUDIO_SPLIT_THRESHOLD_SECONDS
        if category == "audio"
        else DEFAULT_VIDEO_SPLIT_THRESHOLD_SECONDS
    )
    duration_threshold = environment_positive_int(
        f"{category.upper()}_SPLIT_THRESHOLD_SECONDS",
        duration_default,
    )
    file_size = path.stat().st_size if path.is_file() else 0
    return file_size > size_threshold or bool(duration_seconds and duration_seconds > duration_threshold)


def media_segment_seconds(category: str) -> int:
    default = DEFAULT_AUDIO_SEGMENT_SECONDS if category == "audio" else DEFAULT_VIDEO_SEGMENT_SECONDS
    return environment_positive_int(f"{category.upper()}_SEGMENT_SECONDS", default)


def probe_media_duration(path: Path) -> float | None:
    ffprobe = os.environ.get("FFPROBE_BIN", "").strip() or shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        completed = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=environment_positive_int("MEDIA_PROBE_TIMEOUT_SECONDS", 60),
            check=False,
        )
        value = float(completed.stdout.strip())
        return value if completed.returncode == 0 and value > 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def build_segment_command(
    ffmpeg: str,
    source: Path,
    output_pattern: Path,
    category: str,
    segment_seconds: int,
    *,
    copy_video: bool,
) -> list[str]:
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source)]
    if category == "audio":
        command.extend(["-map", "0:a:0", "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le"])
    elif copy_video:
        command.extend(["-map", "0:v:0", "-an", "-c:v", "copy"])
    else:
        command.extend(
            [
                "-map",
                "0:v:0",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-force_key_frames",
                f"expr:gte(t,n_forced*{segment_seconds})",
            ]
        )
    command.extend(
        [
            "-f",
            "segment",
            "-segment_time",
            str(segment_seconds),
            "-reset_timestamps",
            "1",
            str(output_pattern),
        ]
    )
    return command


def run_segment_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=environment_positive_int("MEDIA_SPLIT_TIMEOUT_SECONDS", 7200),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise MediaSegmentationError("媒體切分逾時") from exc


def describe_segments(paths: list[Path], default_duration: int) -> list[MediaSegment]:
    segments: list[MediaSegment] = []
    elapsed = 0.0
    minimum_duration = environment_positive_float("MEDIA_MIN_SEGMENT_SECONDS", 0.25)
    for segment_path in paths:
        duration = probe_media_duration(segment_path)
        if duration is not None and duration < minimum_duration:
            segment_path.unlink(missing_ok=True)
            continue
        segments.append(
            MediaSegment(
                path=segment_path,
                index=len(segments),
                start_seconds=round(elapsed, 3),
                duration_seconds=duration,
            )
        )
        elapsed += duration if duration else float(default_duration)
    return segments


def video_segments_exceed_target(paths: list[Path], target_seconds: int) -> bool:
    if not paths:
        return True
    for path in paths:
        duration = probe_media_duration(path)
        if duration and duration > target_seconds * 1.5:
            return True
    return False


def command_error(completed: subprocess.CompletedProcess[str]) -> str:
    text = " ".join((completed.stderr or completed.stdout or "未知錯誤").split())
    return text[:500]


def environment_positive_int(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


def environment_positive_float(name: str, default: float) -> float:
    try:
        value = float(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default
