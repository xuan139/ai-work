import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db
from app.auth import hash_password
from app.wiki_service import _clean_excerpt, search_wiki, upsert_wiki_for_asset


class WikiTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        self.user = db.create_user(username="employee", password_hash=hash_password("password123"), role="user")

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    async def test_generates_incremental_page_with_sources_and_versions(self) -> None:
        asset = self._asset(self.user["id"], "NAS 产品规划")
        db.replace_document_chunks(asset["id"], [self._chunk("NAS 保存企业资料，并提供权限管理。", page=2)])

        with patch("app.wiki_service.request_embeddings", return_value=[[1.0, 0.0]]):
            created = await upsert_wiki_for_asset(asset["id"])

        self.assertIsNotNone(created)
        self.assertEqual(created["version"], 1)
        sources = db.list_wiki_sources(created["id"])
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["page_number"], 2)

        db.replace_document_chunks(asset["id"], [self._chunk("NAS 新增自动 Wiki 与混合检索。", page=3)])
        with patch("app.wiki_service.request_embeddings", return_value=[[1.0, 0.0]]):
            updated = await upsert_wiki_for_asset(asset["id"])

        self.assertEqual(updated["id"], created["id"])
        self.assertEqual(updated["version"], 2)
        self.assertIn("混合检索", updated["body"])
        self.assertNotIn("权限管理", updated["body"])
        self.assertEqual(len(db.list_wiki_sources(created["id"])), 1)

    async def test_search_combines_full_text_and_vector_and_inherits_owner_access(self) -> None:
        employee_asset = self._asset(self.user["id"], "员工知识")
        admin_asset = self._asset(self.admin["id"], "管理知识")
        db.replace_document_chunks(employee_asset["id"], [self._chunk("报销与休假流程")])
        db.replace_document_chunks(admin_asset["id"], [self._chunk("服务器维护记录")])
        with patch("app.wiki_service.request_embeddings", return_value=[[1.0, 0.0]]):
            await upsert_wiki_for_asset(employee_asset["id"])
            await upsert_wiki_for_asset(admin_asset["id"])
            employee_results = await search_wiki(self.user, "报销", limit=10)
            admin_results = await search_wiki(self.admin, "记录", limit=10)

        self.assertEqual([page["title"] for page in employee_results], ["员工知识"])
        self.assertEqual({page["title"] for page in admin_results}, {"员工知识", "管理知识"})
        self.assertEqual(employee_results[0]["retrieval_method"], "hybrid")

    def test_excerpt_removes_repeated_extraction_noise(self) -> None:
        noisy = f"正常開頭 {'อ' * 40} 可讀結尾"

        self.assertEqual(_clean_excerpt(noisy), "正常開頭 可讀結尾")

    def test_excerpt_keeps_normal_unspaced_chinese(self) -> None:
        content = "企業知識庫會保留來源引用與權限設定"

        self.assertEqual(_clean_excerpt(content), content)

    def _asset(self, user_id: int, title: str) -> dict:
        return db.create_nas_asset(
            user_id=user_id,
            category="pdf",
            title=title,
            original_filename=f"{title}.pdf",
            stored_path=f"/nas/{title}.pdf",
            mime_type="application/pdf",
            file_size=100,
            status="completed",
            analyzer="RAG Builder",
        )

    @staticmethod
    def _chunk(content: str, page: int | None = None) -> dict:
        return {
            "chunk_index": 0,
            "content": content,
            "token_estimate": len(content),
            "page_number": page,
            "chunk_type": "text",
        }


if __name__ == "__main__":
    unittest.main()
