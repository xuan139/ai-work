import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class McpCategoryUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

    def test_mcp_connectors_are_grouped_by_purpose(self) -> None:
        for key in ("nas", "office", "spreadsheet", "finance", "project", "technical", "other"):
            self.assertIn(f'key: "{key}"', self.script)
        self.assertIn('data-mcp-category="${escapeHtml(category.key)}"', self.script)

    def test_mcp_categories_are_collapsed_until_searching(self) -> None:
        self.assertIn('${query ? "open" : ""}', self.script)
        self.assertNotIn('<section class="mcp-server-group enterprise">', self.script)

    def test_category_labels_are_bilingual(self) -> None:
        self.assertIn('title: "NAS 與知識資料"', self.script)
        self.assertIn('title: "財務會計與 ERP"', self.script)
        self.assertIn('title: "試算表與 Excel"', self.script)
        self.assertIn('title: "NAS and Knowledge"', self.script)
        self.assertIn('title: "Accounting and ERP"', self.script)
        self.assertIn('title: "Spreadsheets and Excel"', self.script)


if __name__ == "__main__":
    unittest.main()
