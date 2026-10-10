import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from app import db
from app.auth import hash_password
from app.evaluation_baseline import (
    ASSET_DEFINITIONS,
    BASELINE_VERSION,
    CASE_DEFINITIONS,
    GROUP_DEFINITIONS,
    USER_DEFINITIONS,
    seed_enterprise_evaluation_baseline,
)


class EnterpriseEvaluationBaselineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        self.db_patch = patch.object(db, "DB_PATH", root / "app.db")
        self.fixture_patch = patch(
            "app.evaluation_baseline.FIXTURE_DIR", root / "evaluation_baseline"
        )
        self.db_patch.start()
        self.fixture_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")

    def tearDown(self) -> None:
        self.fixture_patch.stop()
        self.db_patch.stop()
        self.directory.cleanup()

    def test_bootstrap_is_idempotent_and_creates_approved_40_case_suite(self) -> None:
        first = seed_enterprise_evaluation_baseline(self.admin)
        second = seed_enterprise_evaluation_baseline(self.admin)

        self.assertEqual(first["users"], 4)
        self.assertEqual(first["groups"], 3)
        self.assertEqual(first["assets"], 16)
        self.assertEqual(first["cases"], 40)
        self.assertEqual(first["created_cases"], 40)
        self.assertEqual(second["created_cases"], 0)
        self.assertEqual(second["updated_cases"], 40)

        users = [
            db.get_user_by_username(username)
            for username in USER_DEFINITIONS.values()
        ]
        self.assertEqual(len({user["id"] for user in users}), 4)
        self.assertTrue(all(user["role"] == "user" and user["is_active"] for user in users))

        groups = [
            group for group in db.list_user_groups()
            if group["name"] in GROUP_DEFINITIONS.values()
        ]
        self.assertEqual(len(groups), 3)
        self.assertTrue(all(group["member_count"] == 1 for group in groups))

        assets = self._baseline_assets()
        self.assertEqual(len(assets), len(ASSET_DEFINITIONS))
        cases = self._baseline_cases()
        self.assertEqual(len(cases), len(CASE_DEFINITIONS))
        self.assertEqual(
            Counter(case["case_type"] for case in cases),
            Counter({
                "normal": 10,
                "cross_file": 10,
                "insufficient": 5,
                "access_control": 10,
                "version": 5,
            }),
        )
        self.assertTrue(all(case["approval_status"] == "approved" for case in cases))
        self.assertTrue(all(case["is_active"] == 1 for case in cases))

    def test_department_private_and_company_permissions_match_test_identities(self) -> None:
        seed_enterprise_evaluation_baseline(self.admin)
        assets = {asset["source_url"].rsplit("/", 1)[-1]: asset for asset in self._baseline_assets()}
        users = {
            key: db.get_user_by_username(username)
            for key, username in USER_DEFINITIONS.items()
        }

        for user in users.values():
            self.assertTrue(self._can_read(user, assets["company_travel"]))
            self.assertFalse(self._can_read(user, assets["executive_strategy"]))

        self.assertTrue(self._can_read(users["finance"], assets["finance_expense"]))
        self.assertFalse(self._can_read(users["finance"], assets["sales_pipeline"]))
        self.assertFalse(self._can_read(users["finance"], assets["manufacturing_plan"]))

        self.assertTrue(self._can_read(users["sales"], assets["sales_pipeline"]))
        self.assertFalse(self._can_read(users["sales"], assets["finance_expense"]))
        self.assertFalse(self._can_read(users["sales"], assets["manufacturing_plan"]))

        self.assertTrue(self._can_read(users["manufacturing"], assets["manufacturing_plan"]))
        self.assertFalse(self._can_read(users["manufacturing"], assets["finance_expense"]))
        self.assertFalse(self._can_read(users["manufacturing"], assets["sales_pipeline"]))

        self.assertFalse(self._can_read(users["employee"], assets["finance_expense"]))
        self.assertFalse(self._can_read(users["employee"], assets["sales_pipeline"]))
        self.assertFalse(self._can_read(users["employee"], assets["manufacturing_plan"]))

    def test_latest_policy_version_is_current_and_cases_only_allow_latest_source(self) -> None:
        seed_enterprise_evaluation_baseline(self.admin)
        assets = {asset["source_url"].rsplit("/", 1)[-1]: asset for asset in self._baseline_assets()}
        old = db.get_nas_asset(assets["purchase_policy_v1"]["id"])
        current = db.get_nas_asset(assets["purchase_policy_v2"]["id"])

        self.assertEqual(old["document_key"], current["document_key"])
        self.assertEqual(old["version_no"], 1)
        self.assertEqual(current["version_no"], 2)
        self.assertEqual(old["is_current"], 0)
        self.assertEqual(current["is_current"], 1)

        version_cases = [case for case in self._baseline_cases() if case["case_type"] == "version"]
        for case in version_cases:
            self.assertEqual(json.loads(case["allowed_asset_ids_json"]), [current["id"]])
            self.assertNotIn(old["id"], json.loads(case["expected_asset_ids_json"]))

    def _baseline_assets(self) -> list[dict]:
        with db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM nas_assets WHERE source_type = 'evaluation_fixture' ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def _baseline_cases(self) -> list[dict]:
        cases = []
        for case in db.list_rag_eval_cases(active_only=False):
            scope = json.loads(case["scope_json"] or "{}")
            if scope.get("evaluation_suite") == BASELINE_VERSION:
                cases.append(case)
        return cases

    @staticmethod
    def _can_read(user: dict, asset: dict) -> bool:
        return db.user_can_read_asset(asset["id"], user_id=user["id"], role=user["role"])


if __name__ == "__main__":
    unittest.main()
