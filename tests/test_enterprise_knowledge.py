import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import db
from app.auth import hash_password
from app.embedding_runtime import hybrid_search_knowledge_chunks, pack_embedding
from app.knowledge_service import (
    create_eval_case,
    knowledge_context,
    lookup_knowledge_cache,
    normalize_scope,
    run_evaluation,
    store_knowledge_cache,
)


class EnterpriseKnowledgeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        self.alice = db.create_user(
            username="alice", password_hash=hash_password("password123"), role="user"
        )
        self.bob = db.create_user(
            username="bob", password_hash=hash_password("password123"), role="user"
        )

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_private_group_company_permissions_and_audit(self) -> None:
        private = self._asset(self.alice["id"], "私人規劃", "private", "私人 NAS 規劃")
        company = self._asset(self.alice["id"], "公司制度", "company", "全公司報銷制度")
        group = db.create_user_group(name="財務部", created_by=self.admin["id"])
        db.set_user_group_members(group["id"], [self.bob["id"]])
        grouped = self._asset(self.alice["id"], "財務資料", "group", "財務月結流程")
        db.set_asset_permissions(
            grouped["id"],
            actor_user_id=self.alice["id"],
            visibility="group",
            owner_group_id=group["id"],
            grants=[],
        )

        self.assertFalse(db.user_can_read_asset(private["id"], user_id=self.bob["id"], role="user"))
        self.assertTrue(db.user_can_read_asset(company["id"], user_id=self.bob["id"], role="user"))
        self.assertTrue(db.user_can_read_asset(grouped["id"], user_id=self.bob["id"], role="user"))
        visible = db.list_accessible_document_chunks(user_id=self.bob["id"], role="user")
        self.assertEqual({item["asset_id"] for item in visible}, {company["id"], grouped["id"]})

    def test_new_document_version_becomes_current_only_after_completion(self) -> None:
        first = self._asset(self.alice["id"], "產品規格", "company", "第一版規格")
        second = db.create_nas_asset(
            user_id=self.alice["id"], category="pdf", title="產品規格",
            original_filename="spec-v2.pdf", stored_path="/nas/spec-v2.pdf",
            mime_type="application/pdf", file_size=200, status="processing",
            analyzer="RAG Builder", supersedes_asset_id=first["id"],
            visibility="company", content_sha256="v2",
        )
        self.assertEqual(db.get_nas_asset(first["id"])["is_current"], 1)
        db.replace_document_chunks(second["id"], [self._chunk("第二版規格")])
        db.update_nas_asset(second["id"], status="completed", chunk_count=1)

        first_after = db.get_nas_asset(first["id"])
        second_after = db.get_nas_asset(second["id"])
        self.assertEqual(first_after["is_current"], 0)
        self.assertEqual(second_after["is_current"], 1)
        self.assertEqual(second_after["version_no"], 2)
        self.assertEqual(second_after["document_key"], first_after["document_key"])

    async def test_cross_file_hybrid_search_only_scores_accessible_chunks(self) -> None:
        allowed = self._asset(self.alice["id"], "NAS 手冊", "company", "NAS 快照與備份")
        denied = self._asset(self.alice["id"], "薪資資料", "private", "機密薪資明細")
        with patch("app.embedding_runtime.embed_query", new=AsyncMock(return_value=[1.0, 0.0])):
            results = await hybrid_search_knowledge_chunks(
                user_id=self.bob["id"], role="user", query="NAS 備份", limit=8
            )
        self.assertEqual([item["asset_id"] for item in results], [allowed["id"]])
        self.assertNotIn(denied["id"], {item["asset_id"] for item in results})

    async def test_permission_change_invalidates_exact_knowledge_cache(self) -> None:
        asset = self._asset(self.alice["id"], "共用知識", "company", "企業 NAS 知識")
        scope = normalize_scope({"scope": "all_accessible"})
        context = await knowledge_context(self.bob, scope)
        await store_knowledge_cache(
            user=self.bob, model_id="local:qwen", question="NAS 是什麼", scope=scope,
            context=context, query_vector=[1.0, 0.0], result={"answer": "舊答案"}, contexts=[],
        )
        cached, _, _ = await lookup_knowledge_cache(
            user=self.bob, model_id="local:qwen", question="NAS 是什麼", scope=scope
        )
        self.assertIsNotNone(cached)

        db.set_asset_permissions(
            asset["id"], actor_user_id=self.alice["id"], visibility="private",
            owner_group_id=None, grants=[],
        )
        with patch("app.knowledge_service.embed_query", new=AsyncMock(return_value=None)):
            stale, _, refreshed_context = await lookup_knowledge_cache(
                user=self.bob, model_id="local:qwen", question="NAS 是什麼", scope=scope
            )
        self.assertIsNone(stale)
        self.assertGreater(refreshed_context["knowledge_revision"], context["knowledge_revision"])

    async def test_evaluation_records_recall_mrr_citations_and_permission_leaks(self) -> None:
        asset = self._asset(self.alice["id"], "報銷制度", "company", "報銷需要發票與主管核准")
        await create_eval_case(
            {
                "question": "報銷需要什麼？",
                "expected_asset_ids": [asset["id"]],
                "expected_keywords": ["發票", "主管核准"],
                "allowed_asset_ids": [asset["id"]],
                "required_facts": ["發票", "主管核准"],
                "reference_answer": "報銷需要發票與主管核准。[來源 1]",
                "test_user_id": self.bob["id"],
                "approval_status": "approved",
                "scope": {"scope": "all_accessible"},
            },
            self.admin,
        )
        with patch("app.embedding_runtime.embed_query", new=AsyncMock(return_value=[1.0, 0.0])):
            report = await run_evaluation(self.admin)
        self.assertEqual(report["case_count"], 1)
        self.assertEqual(report["recall_at_5"], 1.0)
        self.assertEqual(report["mrr"], 1.0)
        self.assertEqual(report["citation_accuracy"], 1.0)
        self.assertEqual(report["permission_leaks"], 0)

    async def test_final_answer_evaluation_uses_employee_and_checks_grounding(self) -> None:
        asset = self._asset(self.alice["id"], "差旅規範", "company", "住宿上限為三千元")
        case = await create_eval_case(
            {
                "question": "住宿費上限是多少？",
                "case_type": "normal",
                "test_user_id": self.bob["id"],
                "expected_behavior": "answer",
                "required_facts": ["三千元"],
                "allowed_asset_ids": [asset["id"]],
                "expected_asset_ids": [asset["id"]],
                "approval_status": "approved",
            },
            self.admin,
        )
        seen_users = []

        async def answerer(eval_case: dict, user: dict) -> dict:
            seen_users.append(user["id"])
            chunks = db.list_accessible_document_chunks(user_id=user["id"], role=user["role"])
            return {
                "answer": "住宿費上限為三千元。[來源 1]",
                "contexts": chunks,
                "model_contexts": chunks,
                "model_id": "local:qwen3-4b",
                "retrieval": {"knowledge_revision": 7},
            }

        report = await run_evaluation(self.admin, answerer=answerer, case_ids=[case["id"]])
        self.assertEqual(seen_users, [self.bob["id"]])
        self.assertEqual(report["fact_accuracy"], 1.0)
        self.assertEqual(report["citation_support"], 1.0)
        self.assertEqual(report["automatic_pass_rate"], 1.0)
        reviewed = db.review_rag_eval_run(
            report["results"][0]["id"],
            human_result="pass",
            review_comment="業務確認答案與來源一致",
            reviewed_by=self.admin["id"],
        )
        self.assertEqual(reviewed["human_result"], "pass")
        self.assertEqual(reviewed["reviewed_by_username"], "admin")

    async def test_approved_case_requires_real_standard_employee(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not exist"):
            await create_eval_case(
                {
                    "question": "測試不存在的員工",
                    "test_user_id": 999999,
                    "approval_status": "approved",
                    "expected_behavior": "refuse",
                },
                self.admin,
            )

    async def test_access_control_evaluation_records_leak_stage(self) -> None:
        secret = self._asset(self.alice["id"], "財務薪資", "private", "王小明薪資九萬元")
        case = await create_eval_case(
            {
                "question": "王小明薪資是多少？",
                "case_type": "access_control",
                "test_user_id": self.bob["id"],
                "expected_behavior": "refuse",
                "prohibited_facts": ["九萬元"],
                "approval_status": "approved",
            },
            self.admin,
        )
        leaked_chunk = db.list_document_chunks(secret["id"])[0]
        leaked_chunk.update({"asset_title": secret["title"], "version_no": 1})

        async def unsafe_answerer(eval_case: dict, user: dict) -> dict:
            return {
                "answer": "王小明薪資是九萬元。[來源 1]",
                "contexts": [leaked_chunk],
                "model_contexts": [leaked_chunk],
                "model_id": "unsafe-model",
                "retrieval": {"knowledge_revision": 8},
            }

        report = await run_evaluation(self.admin, answerer=unsafe_answerer, case_ids=[case["id"]])
        result = report["results"][0]
        self.assertEqual(report["permission_leaks"], 1)
        self.assertEqual(result["automatic_result"], "fail")
        self.assertIn("retrieval", result["permission_leak_stage"])
        self.assertIn("model_context", result["permission_leak_stage"])
        self.assertIn("answer", result["permission_leak_stage"])

    def _asset(self, user_id: int, title: str, visibility: str, content: str) -> dict:
        asset = db.create_nas_asset(
            user_id=user_id, category="pdf", title=title,
            original_filename=f"{title}.pdf", stored_path=f"/nas/{title}.pdf",
            mime_type="application/pdf", file_size=100, status="processing",
            analyzer="RAG Builder", visibility=visibility, content_sha256=title,
        )
        chunk = self._chunk(content)
        chunk["embedding"] = pack_embedding([1.0, 0.0])
        chunk["embedding_model"] = "qwen3-embedding-0.6b"
        db.replace_document_chunks(asset["id"], [chunk])
        return db.update_nas_asset(asset["id"], status="completed", chunk_count=1)

    @staticmethod
    def _chunk(content: str) -> dict:
        return {
            "chunk_index": 0,
            "content": content,
            "token_estimate": len(content),
            "page_number": 1,
            "chunk_type": "text",
        }


if __name__ == "__main__":
    unittest.main()
