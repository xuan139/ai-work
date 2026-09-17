import json
import unittest
from unittest.mock import patch

from app import llm_runtime
from app.llm_cache import _user_prompt_for_suggestion


class LlmSystemPromptTests(unittest.TestCase):
    def test_suggestions_hide_the_system_prompt_audit_prefix(self) -> None:
        self.assertEqual(
            _user_prompt_for_suggestion(
                "[System Prompt]\n請用繁體中文回答\n\n[User Prompt]\n整理本月報告"
            ),
            "整理本月報告",
        )

    def test_openai_compatible_request_uses_system_role(self) -> None:
        response = {"choices": [{"message": {"content": "完成"}}], "usage": {}}
        with patch.object(llm_runtime, "_request_json", return_value=(response, {})) as request_json:
            answer, _ = llm_runtime._call_openai_compatible(
                "https://example.test/chat/completions",
                "qwen-plus",
                "整理本月報告",
                "secret",
                "請用繁體中文條列回答",
            )

        request = request_json.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(answer, "完成")
        self.assertEqual(
            payload["messages"],
            [
                {"role": "system", "content": "請用繁體中文條列回答"},
                {"role": "user", "content": "整理本月報告"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
