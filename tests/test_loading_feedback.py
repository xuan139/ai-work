import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class LoadingFeedbackTests(unittest.TestCase):
    def test_global_loading_indicator_is_present_and_bilingual(self) -> None:
        index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="globalBusyIndicator"', index)
        self.assertIn('data-i18n="loading.active"', index)
        self.assertIn('loading: { active: "正在載入資料..." }', app)
        self.assertIn('loading: { active: "Loading data..." }', app)

    def test_api_and_uploads_share_busy_feedback(self) -> None:
        app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("const { busy = true, ...requestOptions } = options;", app)
        self.assertIn("const finishBusy = busy ? beginGlobalBusy() : () => {};", app)
        self.assertIn("const finishBusy = beginGlobalBusy();", app)
        self.assertIn("{ busy: false }", app)

    def test_navigation_and_buttons_have_immediate_feedback(self) -> None:
        app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("async function navigateFromSidebar(name, trigger = null)", app)
        self.assertIn('trigger?.setAttribute("aria-busy", "true")', app)
        self.assertIn("showButtonFeedback(event.target.closest(\"button\"));", app)
        self.assertIn(".global-busy-indicator", styles)
        self.assertIn(".nav-item.navigation-loading", styles)


if __name__ == "__main__":
    unittest.main()
