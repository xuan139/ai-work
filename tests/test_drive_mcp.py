from __future__ import annotations

import unittest
from unittest.mock import patch

from app.drive_mcp import _call_tool


class DriveMcpTests(unittest.TestCase):
    @patch("app.drive_mcp._drive_json_request")
    def test_lists_recent_files(self, drive_request) -> None:
        drive_request.return_value = {
            "files": [
                {
                    "id": "file-1",
                    "name": "Plan",
                    "mimeType": "application/vnd.google-apps.document",
                    "modifiedTime": "2026-09-19T01:00:00Z",
                }
            ]
        }

        result = _call_tool("drive_list_recent_files", {"max_results": 5}, "access-token")

        self.assertEqual(result["requested_count"], 5)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["files"][0]["file_id"], "file-1")

    @patch("app.drive_mcp._drive_json_request")
    def test_search_escapes_plain_keyword(self, drive_request) -> None:
        drive_request.return_value = {"files": []}

        result = _call_tool("drive_search_files", {"query": "O'Reilly", "max_results": 3}, "access-token")

        self.assertEqual(result["query"], "O'Reilly")
        query = drive_request.call_args.args[2]
        self.assertIn(("q", "trashed = false and (name contains 'O\\'Reilly' or fullText contains 'O\\'Reilly')"), query)

    @patch("app.drive_mcp._drive_bytes_request")
    @patch("app.drive_mcp._drive_json_request")
    def test_reads_google_document_as_text(self, drive_request, bytes_request) -> None:
        drive_request.return_value = {
            "id": "file-1",
            "name": "Plan",
            "mimeType": "application/vnd.google-apps.document",
        }
        bytes_request.return_value = ("會議內容".encode("utf-8"), "text/plain")

        result = _call_tool("drive_read_text_content", {"file_id": "file-1"}, "access-token")

        self.assertEqual(result["content_type"], "text/plain")
        self.assertEqual(result["text"], "會議內容")
        self.assertFalse(result["truncated"])


if __name__ == "__main__":
    unittest.main()
