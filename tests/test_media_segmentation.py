import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.media_segmentation import (
    DEFAULT_SPLIT_THRESHOLD_BYTES,
    MediaSegment,
    archive_audio_segments,
    archive_media_segments,
    archived_audio_segment_path,
    build_segment_command,
    list_archived_audio_segments,
    list_archived_media_segments,
    media_requires_segmentation,
    media_segment_seconds,
)


class MediaSegmentationTests(unittest.TestCase):
    def test_audio_over_default_size_threshold_is_segmented(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "long-meeting.m4a"
            with path.open("wb") as output:
                output.seek(DEFAULT_SPLIT_THRESHOLD_BYTES)
                output.write(b"x")

            with patch.dict(os.environ, {}, clear=True):
                self.assertTrue(media_requires_segmentation(path, "audio", None))

    def test_long_duration_is_segmented_even_when_file_is_small(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "compressed.m4a"
            path.write_bytes(b"audio")

            with patch.dict(os.environ, {}, clear=True):
                self.assertTrue(media_requires_segmentation(path, "audio", 1801.0))

    def test_short_media_stays_as_one_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "short.mp4"
            path.write_bytes(b"video")

            with patch.dict(os.environ, {}, clear=True):
                self.assertFalse(media_requires_segmentation(path, "video", 120.0))

    def test_audio_segment_duration_can_be_configured(self) -> None:
        with patch.dict(os.environ, {"AUDIO_SEGMENT_SECONDS": "300"}, clear=True):
            self.assertEqual(media_segment_seconds("audio"), 300)

    def test_audio_segments_are_normalized_for_asr(self) -> None:
        command = build_segment_command(
            "ffmpeg",
            Path("meeting.m4a"),
            Path("segment-%04d.wav"),
            "audio",
            600,
            copy_video=True,
        )

        self.assertIn("pcm_s16le", command)
        self.assertIn("16000", command)
        self.assertIn("600", command)

    def test_audio_segments_are_archived_with_playback_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "source-0000.wav"
            second = root / "source-0001.wav"
            first.write_bytes(b"first")
            second.write_bytes(b"second")
            segments = [
                MediaSegment(first, 0, 0.0, 600.0),
                MediaSegment(second, 1, 600.0, 120.5),
            ]

            with patch.dict(os.environ, {"AUDIO_SEGMENT_ARCHIVE_DIR": str(root / "archive")}):
                archived = archive_audio_segments(36, segments)
                listed = list_archived_audio_segments(36)
                second_path = archived_audio_segment_path(36, 1)

            self.assertEqual(len(archived), 2)
            self.assertEqual(listed[0]["filename"], "segment-0001.wav")
            self.assertEqual(listed[1]["start_seconds"], 600.0)
            self.assertEqual(second_path.read_bytes(), b"second")

    def test_video_segments_are_archived_for_download(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source-0000.mkv"
            source.write_bytes(b"video-segment")
            segments = [MediaSegment(source, 0, 0.0, 300.0)]

            with patch.dict(os.environ, {"VIDEO_SEGMENT_ARCHIVE_DIR": str(root / "archive")}):
                archived = archive_media_segments(52, "video", segments)
                listed = list_archived_media_segments(52, "video")

            self.assertEqual(archived[0]["filename"], "segment-0001.mkv")
            self.assertEqual(listed[0]["file_size"], len(b"video-segment"))


if __name__ == "__main__":
    unittest.main()
