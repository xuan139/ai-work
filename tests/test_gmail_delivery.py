import json
import os
import tempfile
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path
from unittest.mock import patch

from app.gmail_delivery import (
    GmailDeliveryError,
    build_gmail_message,
    gmail_sender_account,
    list_gmail_sender_accounts,
    normalize_gmail_recipients,
    public_gmail_sender_accounts,
)


class GmailDeliveryTests(unittest.TestCase):
    def account_env(self) -> dict[str, str]:
        return {
            "GMAIL_SEND_ACCOUNTS_JSON": json.dumps([{
                "id": "operations",
                "label": "營運 Gmail",
                "email": "operations@example.com",
                "oauth_env": "GMAIL_OPERATIONS_TOKEN",
                "allowed_recipients": ["manager@example.net"],
                "allowed_domains": ["example.com"],
            }]),
            "GMAIL_OPERATIONS_CLIENT_ID": "client-id",
            "GMAIL_OPERATIONS_CLIENT_SECRET": "client-secret",
            "GMAIL_OPERATIONS_REFRESH_TOKEN": "refresh-token",
        }

    def test_lists_configured_accounts_without_exposing_oauth_reference(self):
        with patch.dict(os.environ, self.account_env(), clear=False):
            account = gmail_sender_account("operations")
            public = public_gmail_sender_accounts()[0]
        self.assertTrue(account["configured"])
        self.assertEqual(public["email"], "operations@example.com")
        self.assertNotIn("oauth_env", public)
        self.assertNotIn("allowed_recipients", public)

    def test_recipient_policy_allows_self_exact_and_domain_only(self):
        with patch.dict(os.environ, self.account_env(), clear=False):
            account = list_gmail_sender_accounts()[0]
        self.assertEqual(
            normalize_gmail_recipients(
                "operations@example.com, manager@example.net; staff@example.com", account,
            ),
            ["operations@example.com", "manager@example.net", "staff@example.com"],
        )
        with self.assertRaises(GmailDeliveryError):
            normalize_gmail_recipients("outsider@external.test", account)

    def test_disabled_account_requires_reauthorization(self):
        values = self.account_env()
        config = json.loads(values["GMAIL_SEND_ACCOUNTS_JSON"])
        config[0]["send_enabled"] = False
        values["GMAIL_SEND_ACCOUNTS_JSON"] = json.dumps(config)
        with patch.dict(os.environ, values, clear=False):
            public = public_gmail_sender_accounts()[0]
            self.assertEqual(public["status"], "reauthorization_required")
            with self.assertRaisesRegex(GmailDeliveryError, "gmail.send"):
                gmail_sender_account("operations")

    def test_builds_plain_text_message_with_pdf_attachment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.pdf"
            path.write_bytes(b"%PDF-1.4\nexample")
            raw = build_gmail_message(
                sender="operations@example.com", recipients=["manager@example.net"],
                subject="即時生產報告", body="請參閱附件。", attachment_path=path,
            )
        message = BytesParser(policy=policy.default).parsebytes(raw)
        self.assertEqual(message["From"], "operations@example.com")
        self.assertEqual(message["To"], "manager@example.net")
        attachments = list(message.iter_attachments())
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].get_content_type(), "application/pdf")
        self.assertEqual(attachments[0].get_filename(), "report.pdf")


if __name__ == "__main__":
    unittest.main()
