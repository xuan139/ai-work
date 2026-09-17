import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.main import (
    audio_content_type,
    browser_video_path,
    download_nas_media,
    download_nas_media_segment,
    merge_transcript_chunks,
    nas_asset_video,
    video_content_type,
)


class AudioPlaybackTests(unittest.TestCase):
    def test_infers_m4a_type_when_upload_mime_is_generic(self):
        self.assertTrue(audio_content_type("meeting126.m4a", "application/octet-stream").startswith("audio/"))

    def test_preserves_declared_audio_type(self):
        self.assertEqual(audio_content_type("recording.bin", "audio/webm"), "audio/webm")

    def test_merges_overlapping_transcript_chunks(self):
        first = "A" * 120 + "會議確認第一項工作。"
        second = first[-120:] + "接著確認第二項工作。"

        transcript = merge_transcript_chunks(
            [
                {"content": first, "chunk_type": "audio_transcript"},
                {"content": second, "chunk_type": "audio_transcript"},
            ]
        )

        self.assertEqual(transcript, first + "接著確認第二項工作。")


class VideoPlaybackTests(unittest.IsolatedAsyncioTestCase):
    def test_infers_mp4_type_when_upload_mime_is_generic(self):
        self.assertEqual(video_content_type("meeting.mp4", "application/octet-stream"), "video/mp4")

    def test_native_browser_video_does_not_create_a_proxy(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "meeting.webm"
            path.write_bytes(b"video")
            self.assertEqual(browser_video_path({"id": 17, "stored_path": str(path)}), path)

    async def test_serves_authorized_video_inline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "meeting.mp4"
            path.write_bytes(b"video")
            asset = {
                "id": 17,
                "user_id": 3,
                "category": "video",
                "stored_path": str(path),
                "original_filename": "meeting.mp4",
                "mime_type": "video/mp4",
            }
            with patch("app.main.get_nas_asset", return_value=asset):
                response = await nas_asset_video(17, {"id": 3, "role": "user"})

        self.assertEqual(response.media_type, "video/mp4")
        self.assertEqual(response.headers["content-disposition"], 'inline; filename="meeting.mp4"')

    async def test_downloads_source_video_as_attachment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "meeting.mp4"
            path.write_bytes(b"video")
            asset = {
                "id": 17,
                "user_id": 3,
                "category": "video",
                "stored_path": str(path),
                "original_filename": "meeting.mp4",
                "mime_type": "video/mp4",
            }
            with patch("app.main.get_nas_asset", return_value=asset):
                response = await download_nas_media(17, {"id": 3, "role": "user"})

        self.assertEqual(response.media_type, "video/mp4")
        self.assertEqual(response.headers["content-disposition"], 'attachment; filename="meeting.mp4"')

    async def test_downloads_video_segment_as_attachment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "segment-0001.mkv"
            path.write_bytes(b"video")
            asset = {
                "id": 17,
                "user_id": 3,
                "category": "video",
                "stored_path": str(Path(directory) / "meeting.mp4"),
                "original_filename": "meeting.mp4",
                "mime_type": "video/mp4",
            }
            with patch("app.main.get_nas_asset", return_value=asset), patch(
                "app.main.archived_media_segment_path",
                return_value=path,
            ):
                response = await download_nas_media_segment(17, 0, {"id": 3, "role": "user"})

        self.assertEqual(response.headers["content-disposition"], 'attachment; filename="segment-0001.mkv"')


if __name__ == "__main__":
    unittest.main()
