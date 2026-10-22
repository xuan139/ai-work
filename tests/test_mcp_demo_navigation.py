import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class McpDemoNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        cls.script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

    def test_demo_entries_are_inside_collapsed_mcp_demo_group(self):
        start = self.html.index('id="mcpDemoNavGroup"')
        end = self.html.index('id="settingsNav"')
        group = self.html[start:end]
        self.assertIn('id="mcpDemoNavGroup" class="nav-submenu" hidden', group)
        for label in (
            "NAS Excel Pro",
            "電子製造排程 Demo",
            "即時生產報告",
            "每日生產報告",
            "醫療 HIS／FHIR Demo",
            "放射影像／Orthanc Demo",
            "MES 產線演示",
            "LangChain Odoo Demo",
            "Notion MCP Demo",
        ):
            self.assertIn(label, group)

    def test_parent_toggle_and_mes_active_state_are_wired(self):
        self.assertIn("function setMcpDemoMenuExpanded(expanded)", self.script)
        self.assertIn("setMcpDemoMenuExpanded(false);", self.script)
        self.assertIn('const isMcpDemoView = name === "mes";', self.script)
        self.assertIn("if (isMcpDemoView) setMcpDemoMenuExpanded(true);", self.script)
        self.assertIn('els.mcpDemoNav.addEventListener("click"', self.script)


if __name__ == "__main__":
    unittest.main()
