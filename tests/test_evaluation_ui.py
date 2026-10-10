import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EvaluationUiTests(unittest.TestCase):
    def test_admin_evaluation_center_has_required_workflow_controls(self) -> None:
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        for element_id in (
            "evaluationNav",
            "evaluationSection",
            "evaluationCaseForm",
            "evaluationTestUser",
            "evaluationAllowedAssets",
            "bootstrapEvaluation",
            "runEvaluationSuite",
            "evaluationRunList",
        ):
            self.assertIn(f'id="{element_id}"', html)

    def test_evaluation_javascript_wires_case_run_and_human_review(self) -> None:
        script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("async function executeEvaluation", script)
        self.assertIn("async function bootstrapEvaluationBaseline", script)
        self.assertIn("/api/admin/rag-evaluations/bootstrap", script)
        self.assertIn("async function saveEvaluationReview", script)
        self.assertIn("data-evaluation-run", script)
        self.assertIn("data-review-save", script)
        self.assertNotIn("runRagEvaluationSuite", script)


if __name__ == "__main__":
    unittest.main()
