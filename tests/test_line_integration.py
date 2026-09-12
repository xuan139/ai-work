import asyncio
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.datastructures import Headers, UploadFile
from fastapi import HTTPException

from app import db, main
from app.auth import hash_password


class LineIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.storage_patch = patch.object(main, "NAS_ASSETS_DIR", Path(self.directory.name) / "nas_assets")
        self.db_patch.start()
        self.storage_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        assert self.admin is not None

    def tearDown(self) -> None:
        self.storage_patch.stop()
        self.db_patch.stop()
        self.directory.cleanup()

    def test_pdf_is_processed_summarized_and_deduplicated(self) -> None:
        db.upsert_line_source(
            source_id="G1", source_type="group", display_name="大群組",
            owner_user_id=self.admin["id"], is_approved=True,
        )
        async def fake_process(asset_id, *args):
            db.replace_document_chunks(
                asset_id,
                [{
                    "chunk_index": 0,
                    "content": "本文件說明 NAS 備份政策。",
                    "token_estimate": 10,
                    "page_number": 1,
                    "chunk_type": "text",
                    "image_path": None,
                    "metadata_json": "{}",
                }],
            )
            db.update_nas_asset(asset_id, status="completed", analyzer="RAG Builder", summary="ready", chunk_count=1)

        upload = UploadFile(
            io.BytesIO(b"%PDF-test"),
            filename="policy.pdf",
            headers=Headers({"content-type": "application/pdf"}),
        )
        with patch.object(main, "process_nas_asset", fake_process), patch.object(
            main,
            "run_model_with_audit",
            AsyncMock(return_value={"answer": "NAS 備份政策摘要", "model": "Qwen3-4B"}),
        ) as llm:
            result = asyncio.run(
                main.ingest_line_pdf(
                    source_id="G1",
                    source_type="group",
                    source_name="大群組",
                    sender_id="U1",
                    sender_name="Claire",
                    line_message_id="M1",
                    line_event_id="E1",
                    file=upload,
                    _=None,
                )
            )
            duplicate = asyncio.run(
                main.ingest_line_pdf(
                    source_id="G1",
                    source_type="group",
                    source_name="大群組",
                    sender_id="U1",
                    sender_name="Claire",
                    line_message_id="M1",
                    line_event_id="E1",
                    file=UploadFile(io.BytesIO(b"unused"), filename="policy.pdf"),
                    _=None,
                )
            )

        self.assertEqual(result["summary"], "NAS 備份政策摘要")
        self.assertEqual(result["chunk_count"], 1)
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(llm.await_count, 1)
        self.assertEqual(db.get_line_source("G1")["content_version"], 1)

    def test_unapproved_group_and_direct_chat_are_blocked(self) -> None:
        with self.assertRaises(HTTPException) as pending_error:
            asyncio.run(
                main.ingest_line_pdf(
                    source_id="G2", source_type="group", source_name="新群組",
                    sender_id="U2", sender_name="Member", line_message_id="M2",
                    line_event_id="E2", file=UploadFile(io.BytesIO(b"%PDF"), filename="new.pdf"), _=None,
                )
            )
        self.assertEqual(pending_error.exception.status_code, 403)
        self.assertFalse(db.get_line_source("G2")["is_approved"])

        with self.assertRaises(HTTPException) as direct_error:
            asyncio.run(
                main.ingest_line_pdf(
                    source_id="U2", source_type="user", source_name="個人聊天室",
                    sender_id="U2", sender_name="Member", line_message_id="M3",
                    line_event_id="E3", file=UploadFile(io.BytesIO(b"%PDF"), filename="direct.pdf"), _=None,
                )
            )
        self.assertEqual(direct_error.exception.status_code, 403)
        self.assertIsNone(db.get_line_source("U2"))

    def test_group_query_uses_exact_and_semantic_cache(self) -> None:
        source = db.upsert_line_source(
            source_id="G1", source_type="group", display_name="大群組", owner_user_id=self.admin["id"]
        )
        asset = db.create_nas_asset(
            user_id=self.admin["id"], category="pdf", title="政策", original_filename="policy.pdf",
            stored_path="/nas/policy.pdf", mime_type="application/pdf", file_size=1,
            status="completed", analyzer="RAG Builder",
        )
        db.replace_document_chunks(
            asset["id"],
            [{
                "chunk_index": 0, "content": "備份保留三十天", "token_estimate": 5,
                "page_number": 2, "chunk_type": "text", "image_path": None, "metadata_json": "{}",
            }],
        )
        db.update_nas_asset(asset["id"], status="completed", analyzer="RAG Builder", summary="ready", chunk_count=1)
        document = db.create_line_document(
            line_source_id=source["id"], line_message_id="M1", line_event_id="E1",
            sender_id="U1", sender_name="Claire", asset_id=asset["id"],
        )
        db.finish_line_document(document["id"], status="completed", summary="摘要", error_message=None)

        llm = AsyncMock(return_value={"answer": "保留三十天（policy.pdf，第 2 頁）", "model": "Qwen3-4B"})
        with patch.object(main, "embed_query", AsyncMock(return_value=[1.0, 0.0])), patch.object(
            main, "run_model_with_audit", llm
        ):
            first = asyncio.run(main.query_line_documents({"source_id": "G1", "question": "備份保留多久？"}, _=None))
            exact = asyncio.run(main.query_line_documents({"source_id": "G1", "question": "備份保留多久？"}, _=None))
            semantic = asyncio.run(main.query_line_documents({"source_id": "G1", "question": "資料會留幾天？"}, _=None))

        self.assertFalse(first["cache"]["hit"])
        self.assertEqual(exact["cache"]["match_type"], "exact")
        self.assertEqual(semantic["cache"]["match_type"], "semantic")
        self.assertEqual(llm.await_count, 1)

    def test_admin_can_approve_group_and_set_company_policy(self) -> None:
        with patch.object(main, "list_line_groups", AsyncMock(return_value=[{"id": "G9", "name": "財務群組"}])):
            result = asyncio.run(main.admin_line_sources(admin=self.admin))
        source = next(item for item in result["sources"] if item["source_id"] == "G9")
        self.assertFalse(source["is_approved"])
        self.assertTrue(any(model["id"] == "local:qwen3-4b" for model in result["models"]))

        updated = asyncio.run(
            main.admin_update_line_source(
                source["id"],
                {
                    "is_approved": True,
                    "auto_pdf_summary": False,
                    "rag_queries_enabled": True,
                    "default_model_id": "local:qwen3-4b",
                    "monthly_call_limit": 25,
                    "monthly_token_limit": 50000,
                },
                admin=self.admin,
            )
        )
        self.assertTrue(updated["is_approved"])
        self.assertFalse(updated["auto_pdf_summary"])
        self.assertEqual(updated["monthly_call_limit"], 25)
        self.assertEqual(updated["monthly_token_limit"], 50000)


if __name__ == "__main__":
    unittest.main()
