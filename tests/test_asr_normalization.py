import os
import unittest
from unittest.mock import patch

from app.text_normalization import normalize_asr_text


class AsrNormalizationTests(unittest.TestCase):
    def test_defaults_to_traditional_chinese(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            text, metadata = normalize_asr_text("会议记录已经保存到资料库")

        self.assertEqual(text, "會議記錄已經保存到資料庫")
        self.assertEqual(metadata["target"], "traditional")
        self.assertTrue(metadata["changed"])

    def test_can_normalize_to_simplified_chinese(self) -> None:
        with patch.dict(os.environ, {"ASR_CHINESE_SCRIPT": "simplified"}, clear=True):
            text, metadata = normalize_asr_text("會議記錄已經保存到資料庫")

        self.assertEqual(text, "会议记录已经保存到资料库")
        self.assertEqual(metadata["target"], "simplified")

    def test_can_disable_normalization(self) -> None:
        source = "会议記錄"
        with patch.dict(os.environ, {"ASR_CHINESE_SCRIPT": "none"}, clear=True):
            text, metadata = normalize_asr_text(source)

        self.assertEqual(text, source)
        self.assertEqual(metadata["target"], "none")


if __name__ == "__main__":
    unittest.main()
