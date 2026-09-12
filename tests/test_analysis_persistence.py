import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import db
from app.analysis_persistence import persist_cloud_asset_analysis
from app.auth import hash_password


class AnalysisPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        admin = db.get_user_by_username("admin")
        assert admin is not None
        self.admin = admin
        self.asset = db.create_nas_asset(
            user_id=admin["id"],
            category="pdf",
            title="NAS Product Guide",
            original_filename="guide.pdf",
            stored_path="/nas/guide.pdf",
            mime_type="application/pdf",
            file_size=2048,
            status="completed",
        )
        db.replace_document_chunks(
            self.asset["id"],
            [
                {
                    "chunk_index": 0,
                    "content": "The NAS supports snapshots and RAG indexing.",
                    "token_estimate": 12,
                    "chunk_type": "text_layer",
                }
            ],
        )
        db.update_nas_asset(self.asset["id"], status="completed", chunk_count=1)

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_cloud_answer_is_saved_once_and_added_to_source_rag(self) -> None:
        async def attach(chunks: list[dict], user_id: int) -> bool:
            for chunk in chunks:
                chunk["embedding"] = b"vector"
                chunk["embedding_model"] = "qwen3-embedding-0.6b"
            return True

        model = {
            "id": "google:gemini-flash",
            "provider": "Google",
            "name": "Gemini Flash",
            "execution": "cloud",
        }
        call = db.create_llm_call(
            user_id=self.admin["id"],
            provider=model["provider"],
            model_name=model["name"],
            model_id=model["id"],
            prompt="Summarize this document",
            response="The document recommends daily snapshots and hybrid RAG search.",
            status="completed",
        )
        result = {
            "call_id": call["id"],
            "access_mode": "api_key",
            "answer": "The document recommends daily snapshots and hybrid RAG search.",
        }
        contexts = [{"id": 1, "chunk_index": 0, "page_number": 2, "chunk_type": "text_layer"}]

        with patch("app.analysis_persistence.attach_embeddings", new=AsyncMock(side_effect=attach)):
            saved = asyncio.run(
                persist_cloud_asset_analysis(
                    asset=self.asset,
                    model=model,
                    question="Summarize this document",
                    result=result,
                    contexts=contexts,
                    user_id=self.admin["id"],
                )
            )
            duplicate = asyncio.run(
                persist_cloud_asset_analysis(
                    asset=self.asset,
                    model=model,
                    question="Summarize this document!",
                    result=result,
                    contexts=contexts,
                    user_id=self.admin["id"],
                )
            )

        self.assertTrue(saved["saved"])
        self.assertTrue(saved["created"])
        self.assertEqual(saved["embedding_status"], "completed")
        self.assertFalse(duplicate["created"])
        analyses = db.list_asset_ai_analyses(self.asset["id"])
        self.assertEqual(len(analyses), 1)
        chunks = db.list_document_chunks(self.asset["id"])
        self.assertEqual(len(chunks), 2)
        analysis_chunk = chunks[1]
        self.assertEqual(analysis_chunk["chunk_type"], "ai_analysis")
        self.assertIn("daily snapshots", analysis_chunk["content"])
        metadata = json.loads(analysis_chunk["metadata_json"])
        self.assertEqual(metadata["model_id"], model["id"])
        self.assertEqual(metadata["source_contexts"][0]["page_number"], 2)
        self.assertEqual(db.get_nas_asset(self.asset["id"])["chunk_count"], 2)
        matches = db.list_nas_assets(user_id=self.admin["id"], role="admin", q="daily snapshots")
        self.assertEqual([item["id"] for item in matches], [self.asset["id"]])

    def test_local_answer_is_not_promoted_to_cloud_analysis_knowledge(self) -> None:
        saved = asyncio.run(
            persist_cloud_asset_analysis(
                asset=self.asset,
                model={
                    "id": "local:qwen3-4b",
                    "provider": "Local NAS",
                    "name": "Qwen3 4B",
                    "execution": "local",
                },
                question="Summarize",
                result={"answer": "Local result"},
                contexts=[],
                user_id=self.admin["id"],
            )
        )
        self.assertFalse(saved["saved"])
        self.assertEqual(len(db.list_asset_ai_analyses(self.asset["id"])), 0)
        self.assertEqual(len(db.list_document_chunks(self.asset["id"])), 1)


if __name__ == "__main__":
    unittest.main()
