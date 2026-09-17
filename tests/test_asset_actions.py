import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import BackgroundTasks

from app.asset_normalization import convert_asset_to_traditional
from app.main import reprocess_nas_asset


class AssetNormalizationTests(unittest.IsolatedAsyncioTestCase):
    async def test_opencc_updates_chunks_and_linked_meeting(self):
        asset = {
            "id": 7,
            "user_id": 3,
            "status": "completed",
            "analyzer": "whisper.cpp small",
            "summary": "原始處理完成。",
            "error_message": None,
            "chunk_count": 1,
        }
        chunks = [{"id": 21, "content": "这个会议讨论网络存储。"}]
        meeting = {
            "id": 9,
            "status": "completed",
            "transcript": "这个会议讨论网络存储。",
            "translation": "会议结论。",
            "translation_status": "completed",
            "error_message": None,
            "translation_error": None,
        }

        with (
            patch("app.asset_normalization.list_document_chunks", return_value=chunks),
            patch("app.asset_normalization.get_meeting_by_nas_asset_id", return_value=meeting),
            patch("app.asset_normalization.attach_embeddings", new=AsyncMock(return_value=True)) as attach,
            patch("app.asset_normalization.update_document_chunk_contents") as update_chunks,
            patch("app.asset_normalization.update_meeting_status") as update_meeting,
            patch("app.asset_normalization.update_meeting_translation") as update_translation,
            patch("app.asset_normalization.update_nas_asset", return_value={**asset, "summary": "已轉換"}) as update_asset,
        ):
            result = await convert_asset_to_traditional(asset)

        self.assertEqual(result["changed_chunks"], 1)
        self.assertEqual(result["changed_meeting_fields"], 2)
        self.assertEqual(chunks[0]["content"], "這個會議討論網絡存儲。")
        attach.assert_awaited_once_with(chunks, 3)
        update_chunks.assert_called_once_with(7, chunks)
        self.assertEqual(update_meeting.call_args.kwargs["transcript"], "這個會議討論網絡存儲。")
        self.assertEqual(update_translation.call_args.kwargs["translation"], "會議結論。")
        update_asset.assert_called_once()

    async def test_opencc_noop_does_not_rewrite_indexes(self):
        asset = {
            "id": 7,
            "user_id": 3,
            "status": "completed",
            "analyzer": "YOLO11n",
            "summary": "已完成。",
            "error_message": None,
            "chunk_count": 1,
        }
        chunks = [{"id": 21, "content": "NAS 已完成影片分析。"}]

        with (
            patch("app.asset_normalization.list_document_chunks", return_value=chunks),
            patch("app.asset_normalization.get_meeting_by_nas_asset_id", return_value=None),
            patch("app.asset_normalization.attach_embeddings", new=AsyncMock()) as attach,
            patch("app.asset_normalization.update_document_chunk_contents") as update_chunks,
            patch("app.asset_normalization.update_nas_asset") as update_asset,
        ):
            result = await convert_asset_to_traditional(asset)

        self.assertEqual(result["changed_chunks"], 0)
        self.assertIs(result["asset"], asset)
        attach.assert_not_awaited()
        update_chunks.assert_not_called()
        update_asset.assert_not_called()


class AssetReprocessTests(unittest.IsolatedAsyncioTestCase):
    async def test_video_reprocess_reuses_original_model_and_preserves_chunk_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "meeting.mp4"
            source.write_bytes(b"video")
            asset = {
                "id": 12,
                "user_id": 3,
                "category": "video",
                "title": "會議影片",
                "status": "completed",
                "stored_path": str(source),
                "analyzer": "YOLO11n",
                "chunk_count": 8,
                "processor_config_json": json.dumps({"video_model_id": "local:yolo11n"}),
            }
            queued = {**asset, "status": "processing"}

            with (
                patch("app.main.get_nas_asset", return_value=asset),
                patch("app.main.update_nas_asset", return_value=queued) as update_asset,
                patch("app.main.enqueue_media_job", new=AsyncMock()) as enqueue,
                patch("app.main.manager.broadcast", new=AsyncMock()),
            ):
                result = await reprocess_nas_asset(12, {}, BackgroundTasks(), {"id": 1, "role": "admin"})

        self.assertEqual(result["status"], "processing")
        self.assertEqual(update_asset.call_args.kwargs["chunk_count"], 8)
        enqueue.assert_awaited_once_with(
            "asset",
            12,
            audio_api_key=None,
            video_api_key=None,
            translation_api_key=None,
        )

    async def test_pdf_reprocess_uses_background_document_pipeline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "manual.pdf"
            source.write_bytes(b"%PDF")
            asset = {
                "id": 13,
                "user_id": 3,
                "category": "pdf",
                "title": "操作手冊",
                "status": "completed",
                "stored_path": str(source),
                "analyzer": "RAG Builder",
                "chunk_count": 4,
                "processor_config_json": None,
            }
            queued = {**asset, "status": "processing"}
            background_tasks = BackgroundTasks()

            with (
                patch("app.main.get_nas_asset", return_value=asset),
                patch("app.main.update_nas_asset", return_value=queued),
                patch("app.main.enqueue_media_job", new=AsyncMock()) as enqueue,
                patch("app.main.manager.broadcast", new=AsyncMock()),
            ):
                result = await reprocess_nas_asset(
                    13,
                    {},
                    background_tasks,
                    {"id": 1, "role": "admin"},
                )

        self.assertEqual(result["status"], "processing")
        enqueue.assert_not_awaited()
        self.assertEqual(len(background_tasks.tasks), 1)


if __name__ == "__main__":
    unittest.main()
