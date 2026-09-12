import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db
from app.asr_catalog import asr_model_summary, get_asr_model
from app.auth import hash_password
from app.llm_catalog import get_model, model_summary
from app.local_model_manager import validate_custom_file_model
from app import local_model_manager
from app.model_registry import register_custom_model
from app.video_catalog import video_model_summary


class CustomModelRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.db_patch = patch.object(db, "DB_PATH", self.root / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        admin = db.get_user_by_username("admin")
        assert admin is not None
        self.admin = admin

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_whisper_file_must_validate_before_catalog_use(self) -> None:
        content = b"custom-whisper-model"
        model = register_custom_model(
            {
                "model_type": "whisper_cpp",
                "name": "Whisper Custom Small",
                "slug": "meeting-small",
                "model_file": "meeting-small.bin",
                "expected_size_mb": len(content) / 1024 / 1024,
                "sha256": hashlib.sha256(content).hexdigest(),
            },
            self.admin["id"],
        )
        self.assertNotIn(model["id"], {item["id"] for item in asr_model_summary()})

        model_root = self.root / "models"
        model_path = model_root / "whisper" / "meeting-small.bin"
        model_path.parent.mkdir(parents=True)
        model_path.write_bytes(content)
        with (
            patch.object(local_model_manager, "MODEL_ROOT", model_root),
            patch.object(local_model_manager, "resolve_whisper_cpp_binary", return_value="/usr/local/bin/whisper-cli"),
        ):
            status = validate_custom_file_model(model["id"])

        self.assertTrue(status["installed"])
        self.assertTrue(model_path.with_suffix(".bin.complete").is_file())
        self.assertIn(model["id"], {item["id"] for item in asr_model_summary()})
        self.assertEqual(get_asr_model(model["id"])["model_file"], "meeting-small.bin")

    def test_llm_endpoint_is_loopback_only_and_hidden_until_ready(self) -> None:
        with self.assertRaises(ValueError):
            register_custom_model(
                {
                    "model_type": "openai_compatible_llm",
                    "name": "External Endpoint",
                    "api_base": "https://example.com",
                    "model_alias": "unsafe",
                },
                self.admin["id"],
            )

        model = register_custom_model(
            {
                "model_type": "openai_compatible_llm",
                "name": "Local Qwen Service",
                "slug": "qwen-service",
                "api_base": "http://127.0.0.1:8090",
                "model_alias": "qwen-local",
                "max_input_tokens": 8192,
            },
            self.admin["id"],
        )
        self.assertIsNone(get_model(model["id"]))
        self.assertNotIn(model["id"], {item["id"] for item in model_summary()})

        db.update_custom_model_validation(model["id"], status="ready")
        catalog_model = get_model(model["id"])
        self.assertIsNotNone(catalog_model)
        self.assertEqual(catalog_model["model"], "qwen-local")
        self.assertEqual(catalog_model["max_input_tokens"], 8192)

    def test_yolo_and_download_source_validation(self) -> None:
        model = register_custom_model(
            {
                "model_type": "yolo",
                "name": "Factory Safety YOLO",
                "model_file": "factory-safety.pt",
                "download_url": "https://github.com/example/models/releases/download/v1/factory-safety.pt",
            },
            self.admin["id"],
        )
        self.assertNotIn(model["id"], {item["id"] for item in video_model_summary()})

        with self.assertRaises(ValueError):
            register_custom_model(
                {
                    "model_type": "yolo",
                    "name": "Unsafe Download",
                    "model_file": "unsafe.pt",
                    "download_url": "https://downloads.example.com/unsafe.pt",
                },
                self.admin["id"],
            )

        with self.assertRaises(ValueError):
            register_custom_model(
                {
                    "model_type": "whisper_cpp",
                    "name": "Path Escape",
                    "model_file": "../outside.bin",
                },
                self.admin["id"],
            )


if __name__ == "__main__":
    unittest.main()
