from __future__ import annotations

import unittest
from unittest.mock import patch

from app.gmail_mcp import _call_tool, normalize_gmail_query


class GmailMcpTests(unittest.TestCase):
    def test_normalizes_common_model_generated_queries(self) -> None:
        self.assertEqual(normalize_gmail_query("recent:10"), "newer_than:10d")
        self.assertEqual(
            normalize_gmail_query("within:30days after:invoice"),
            "newer_than:30d invoice",
        )
        self.assertEqual(normalize_gmail_query("最近 7 天內"), "newer_than:7d")
        self.assertEqual(normalize_gmail_query("最近的郵件"), "newer_than:30d")

    def test_preserves_valid_after_date(self) -> None:
        self.assertEqual(
            normalize_gmail_query("after:2026/09/01 subject:invoice"),
            "after:2026/09/01 subject:invoice",
        )

    @patch("app.gmail_mcp._gmail_request")
    def test_search_uses_normalized_query(self, gmail_request) -> None:
        gmail_request.return_value = {"threads": []}

        result = _call_tool(
            "gmail_search_threads",
            {"query": "recent:10", "max_results": 3},
            "access-token",
        )

        gmail_request.assert_called_once_with(
            "threads",
            "access-token",
            [("q", "newer_than:10d"), ("maxResults", "3")],
        )
        self.assertEqual(result["requested_query"], "recent:10")
        self.assertEqual(result["query"], "newer_than:10d")
        self.assertTrue(result["query_normalized"])


if __name__ == "__main__":
    unittest.main()
