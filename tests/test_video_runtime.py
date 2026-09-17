import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.video_runtime import (
    VideoRuntimeError,
    configured_yolo_device,
    predict_with_cpu_fallback,
)


class FakeDetector:
    def __init__(self, failing_devices: set[str]) -> None:
        self.failing_devices = failing_devices
        self.calls: list[str] = []

    def predict(self, *, source: str, verbose: bool, conf: float, device: str) -> list[str]:
        self.calls.append(device)
        if device in self.failing_devices:
            raise RuntimeError(f"{device} unavailable")
        return [source]


class VideoRuntimeTests(unittest.TestCase):
    def test_yolo_defaults_to_cpu(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(configured_yolo_device(), "cpu")

    def test_configured_device_can_be_overridden(self) -> None:
        with patch.dict(os.environ, {"YOLO_DEVICE": "cuda:0"}, clear=True):
            self.assertEqual(configured_yolo_device(), "cuda:0")

    def test_failed_gpu_prediction_retries_on_cpu(self) -> None:
        detector = FakeDetector({"cuda:0"})

        results, device, fallback_reason = predict_with_cpu_fallback(
            detector,
            Path("frame.jpg"),
            "cuda:0",
        )

        self.assertEqual(results, ["frame.jpg"])
        self.assertEqual(device, "cpu")
        self.assertIn("unavailable", fallback_reason or "")
        self.assertEqual(detector.calls, ["cuda:0", "cpu"])

    def test_failed_cpu_prediction_is_not_retried(self) -> None:
        detector = FakeDetector({"cpu"})

        with self.assertRaises(VideoRuntimeError):
            predict_with_cpu_fallback(detector, Path("frame.jpg"), "cpu")

        self.assertEqual(detector.calls, ["cpu"])


if __name__ == "__main__":
    unittest.main()
