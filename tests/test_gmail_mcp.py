from __future__ import annotations

import unittest
from unittest.mock import patch

from app.gmail_mcp import _call_tool, normalize_gmail_query, normalize_gmail_search


class GmailMcpTests(unittest.TestCase):
    def test_normalizes_common_model_generated_queries(self) -> None:
        self.assertEqual(
            normalize_gmail_query("within:30days after:invoice"),
            "newer_than:30d invoice",
        )
        self.assertEqual(normalize_gmail_query("最近 7 天內"), "newer_than:7d")
        self.assertEqual(normalize_gmail_query("最近的郵件"), "newer_than:30d")

    def test_recent_count_is_not_treated_as_days(self) -> None:
        self.assertEqual(normalize_gmail_search("recent:10", 5), ("", 10))

    def test_preserves_valid_after_date(self) -> None:
        self.assertEqual(
            normalize_gmail_query("after:2026/09/01 subject:invoice"),
            "after:2026/09/01 subject:invoice",
        )

    @patch("app.gmail_mcp._gmail_request")
    def test_search_preserves_legacy_recent_count(self, gmail_request) -> None:
        gmail_request.return_value = {"threads": []}

        result = _call_tool(
            "gmail_search_threads",
            {"query": "recent:10", "max_results": 3},
            "access-token",
        )

        gmail_request.assert_called_once_with(
            "threads",
            "access-token",
            [("maxResults", "10")],
        )
        self.assertEqual(result["requested_query"], "recent:10")
        self.assertEqual(result["query"], "")
        self.assertTrue(result["query_normalized"])

    @patch("app.gmail_mcp._gmail_request")
    def test_lists_latest_individual_inbox_messages(self, gmail_request) -> None:
        gmail_request.side_effect = [
            {"messages": [{"id": "m2"}, {"id": "m1"}]},
            {
                "id": "m2",
                "threadId": "t2",
                "snippet": "Newest",
                "payload": {"headers": [{"name": "Subject", "value": "Second"}]},
            },
            {
                "id": "m1",
                "threadId": "t1",
                "snippet": "Older",
                "payload": {"headers": [{"name": "Subject", "value": "First"}]},
            },
        ]

        result = _call_tool("gmail_list_recent_messages", {"max_results": 10}, "access-token")

        self.assertEqual(result["requested_count"], 10)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["messages"][0]["message_id"], "m2")
        gmail_request.assert_any_call(
            "messages",
            "access-token",
            [("labelIds", "INBOX"), ("maxResults", "10")],
        )


if __name__ == "__main__":
    unittest.main()
