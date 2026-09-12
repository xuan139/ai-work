import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.document_processing import build_image_rag_chunks, classify_asset


class ImageRagTests(unittest.TestCase):
    def test_classifies_supported_image_suffix_and_mime(self) -> None:
        self.assertEqual(classify_asset(Path("scan.JPG")), "image")
        self.assertEqual(classify_asset(Path("upload.bin"), "image/webp"), "image")

    @patch("app.document_processing.run_paddle_ocr", return_value="NAS 維護報告\n磁碟狀態正常")
    @patch("app.document_processing.paddle_ocr_engine", return_value=object())
    def test_builds_image_ocr_chunks_with_source_preview(self, _engine, _ocr) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "report.png"
            image_path.touch()
            chunks = build_image_rag_chunks(image_path)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["chunk_type"], "image_ocr")
        self.assertEqual(chunks[0]["image_path"], str(image_path))
        self.assertIn("NAS 維護報告", chunks[0]["content"])
        self.assertEqual(json.loads(chunks[0]["metadata_json"])["extraction_mode"], "paddleocr")

    @patch("app.document_processing.run_paddle_ocr", return_value="")
    @patch("app.document_processing.paddle_ocr_engine", return_value=object())
    def test_rejects_image_without_recognizable_text(self, _engine, _ocr) -> None:
        with self.assertRaisesRegex(RuntimeError, "未辨識出"):
            build_image_rag_chunks(Path("photo.png"))


if __name__ == "__main__":
    unittest.main()
