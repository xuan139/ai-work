import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AiworkQueryModeUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        cls.script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

    def test_three_query_modes_are_available_and_knowledge_is_default(self) -> None:
        for mode in ("knowledge", "asset", "direct"):
            self.assertIn(f'data-aiwork-query-mode="{mode}"', self.html)
        self.assertIn('aiworkQueryMode: "knowledge"', self.script)

    def test_each_mode_routes_to_the_expected_endpoint(self) -> None:
        self.assertIn('api("/api/knowledge/ask"', self.script)
        self.assertIn('api(`/api/nas-assets/${selectedAsset.id}/ask`', self.script)
        self.assertIn('api("/api/llm/run"', self.script)

    def test_rag_modes_render_sources_and_direct_chat_discloses_no_sources(self) -> None:
        self.assertIn('renderAnswerSources(contexts, result.retrieval || {})', self.script)
        self.assertIn('sourceReference: "來源"', self.script)
        self.assertIn('directNoSources: "本回答未使用 NAS 資料，因此沒有來源。"', self.script)

    def test_current_file_mode_only_lists_completed_indexed_assets(self) -> None:
        self.assertIn('asset.status === "completed"', self.script)
        self.assertIn('Number(asset.chunk_count || 0) > 0', self.script)
        self.assertIn('id="aiworkAssetSelect"', self.html)


if __name__ == "__main__":
    unittest.main()
