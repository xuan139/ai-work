import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from app import db
from app.auth import authenticate, create_session_token, current_user, hash_password, require_admin
from app.main import admin_delete_user, admin_update_user


class AccountManagementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.admin = db.get_user_by_username("admin")
        assert self.admin is not None

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def create_standard_user(self, username: str = "test.user") -> dict:
        return db.create_user(
            username=username,
            password_hash=hash_password("password123"),
            role="user",
        )

    def test_disabled_user_cannot_authenticate(self) -> None:
        user = self.create_standard_user()
        db.update_user_access(user["id"], role="user", is_active=False)

        self.assertIsNone(authenticate("test.user", "password123"))

    def test_access_change_revokes_existing_session(self) -> None:
        user = self.create_standard_user()
        token = create_session_token(user["id"], user["session_version"])
        self.assertEqual(current_user(session=token)["id"], user["id"])

        db.update_user_access(user["id"], role="user", is_active=True)

        with self.assertRaises(HTTPException) as context:
            current_user(session=token)
        self.assertEqual(context.exception.status_code, 401)

    def test_standard_user_cannot_use_admin_dependency(self) -> None:
        user = self.create_standard_user()

        with self.assertRaises(HTTPException) as context:
            require_admin(user)
        self.assertEqual(context.exception.status_code, 403)

    def test_admin_cannot_deactivate_self(self) -> None:
        with self.assertRaises(HTTPException) as context:
            asyncio.run(
                admin_update_user(
                    self.admin["id"],
                    {"role": "admin", "is_active": False},
                    admin=self.admin,
                )
            )
        self.assertEqual(context.exception.status_code, 400)

    def test_account_with_nas_records_cannot_be_deleted(self) -> None:
        user = self.create_standard_user()
        db.create_nas_asset(
            user_id=user["id"],
            category="pdf",
            title="Policy",
            original_filename="policy.pdf",
            stored_path="/nas/policy.pdf",
            mime_type="application/pdf",
            file_size=1,
        )

        with self.assertRaises(HTTPException) as context:
            asyncio.run(admin_delete_user(user["id"], admin=self.admin))
        self.assertEqual(context.exception.status_code, 409)

if __name__ == "__main__":
    unittest.main()
