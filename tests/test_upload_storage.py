import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.upload_storage import (
    UploadTooLargeError,
    max_upload_bytes,
    save_upload_stream,
)


class UploadStorageTests(unittest.TestCase):
    def test_default_limit_accepts_a_126_mb_recording(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertGreater(max_upload_bytes(), 126 * 1024 * 1024)

    def test_streams_upload_to_disk(self) -> None:
        payload = b"meeting-audio" * 100000
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "meeting.m4a"
            copied = save_upload_stream(io.BytesIO(payload), destination, limit=len(payload))

            self.assertEqual(copied, len(payload))
            self.assertEqual(destination.read_bytes(), payload)

    def test_removes_partial_file_when_limit_is_exceeded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "too-large.m4a"
            with self.assertRaises(UploadTooLargeError):
                save_upload_stream(io.BytesIO(b"x" * 2048), destination, limit=1024)

            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
