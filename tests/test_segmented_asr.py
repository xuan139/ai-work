import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.asr_service import run_segmented_asr_with_audit
from app.media_segmentation import MediaSegment, SegmentBatch


class SegmentedAsrTests(unittest.IsolatedAsyncioTestCase):
    async def test_segment_transcripts_are_merged_in_order(self) -> None:
        batch = SegmentBatch(
            segments=[
                MediaSegment(Path("segment-0000.wav"), 0, 0.0, 600.0),
                MediaSegment(Path("segment-0001.wav"), 1, 600.0, 300.0),
            ],
            segmented=True,
            source_duration_seconds=900.0,
        )
        run_segment = AsyncMock(
            side_effect=[
                {"text": "第一段", "model": {"id": "local:test"}, "engine": "test", "metadata": {}},
                {"text": "第二段", "model": {"id": "local:test"}, "engine": "test", "metadata": {}},
            ]
        )
        progress: list[tuple[int, int]] = []

        with patch("app.asr_service.prepare_media_segments", return_value=batch), patch(
            "app.asr_service.run_asr_with_audit",
            run_segment,
        ), patch("app.asr_service.update_audio_segment_transcription") as update_segment, patch(
            "app.asr_service.archive_audio_segments",
            return_value=[{"index": 0}, {"index": 1}],
        ) as archive:
            result = await run_segmented_asr_with_audit(
                path=Path("meeting.m4a"),
                model_id="local:test",
                api_key=None,
                user_id=1,
                progress=lambda completed, total: progress.append((completed, total)),
                segment_archive_asset_id=36,
            )

        self.assertEqual(result["text"], "第一段\n第二段")
        self.assertTrue(result["metadata"]["segmented"])
        self.assertEqual(result["metadata"]["segment_count"], 2)
        self.assertEqual(result["metadata"]["archived_segments"], [{"index": 0}, {"index": 1}])
        self.assertEqual(progress, [(1, 2), (2, 2)])
        archive.assert_called_once_with(36, batch.segments)
        self.assertEqual(update_segment.call_count, 4)
        self.assertEqual(update_segment.call_args.kwargs["status"], "completed")


if __name__ == "__main__":
    unittest.main()
