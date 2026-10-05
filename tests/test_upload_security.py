import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db
from app.file_security import (
    UploadScanResult,
    UploadSecurityError,
    inspect_uploaded_file,
    scan_uploaded_file,
    validated_upload_filename,
)


class UploadSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.db_patch = patch.object(db, "DB_PATH", self.root / "app.db")
        self.db_patch.start()
        db.init_db()

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_rejects_path_and_control_characters_in_filename(self) -> None:
        for filename in ("../secret.pdf", "folder/file.pdf", "folder\\file.pdf", "bad\x00.pdf"):
            with self.subTest(filename=filename), self.assertRaises(UploadSecurityError):
                validated_upload_filename(filename, "upload.bin")

    def test_optional_mode_allows_missing_clamav_with_explicit_status(self) -> None:
        path = self.root / "safe.pdf"
        path.write_bytes(b"safe")
        with (
            patch.dict(
                os.environ,
                {"AI_WORK_UPLOAD_SCAN_MODE": "optional", "AI_WORK_CLAMAV_COMMAND": "missing-clamscan"},
                clear=False,
            ),
            patch("app.file_security.shutil.which", return_value=None),
        ):
            result = scan_uploaded_file(path)
        self.assertEqual(result.status, "unavailable")
        self.assertTrue(path.exists())

    def test_infected_file_is_quarantined_and_audited(self) -> None:
        path = self.root / "infected.pdf"
        path.write_bytes(b"malware-test")
        quarantine = self.root / "quarantine"
        with (
            patch.dict(
                os.environ,
                {
                    "AI_WORK_UPLOAD_SCAN_MODE": "required",
                    "AI_WORK_QUARANTINE_DIR": str(quarantine),
                },
                clear=False,
            ),
            patch(
                "app.file_security.scan_uploaded_file",
                return_value=UploadScanResult("infected", "clamscan", "Test.Signature FOUND"),
            ),
        ):
            with self.assertRaises(UploadSecurityError) as raised:
                inspect_uploaded_file(
                    path,
                    original_filename="invoice.pdf",
                    user_id=None,
                    remote_addr="127.0.0.1",
                )

        self.assertTrue(raised.exception.quarantined)
        self.assertFalse(path.exists())
        quarantined = list(quarantine.glob("*.quarantine"))
        self.assertEqual(len(quarantined), 1)
        self.assertEqual(quarantined[0].read_bytes(), b"malware-test")
        with db.connect() as conn:
            quarantine_count = conn.execute("SELECT COUNT(*) FROM quarantined_uploads").fetchone()[0]
            event = conn.execute("SELECT event_type, severity FROM security_events").fetchone()
        self.assertEqual(quarantine_count, 1)
        self.assertEqual(dict(event), {"event_type": "upload_quarantined", "severity": "critical"})


if __name__ == "__main__":
    unittest.main()
