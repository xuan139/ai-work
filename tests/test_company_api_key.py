import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import db, main
from app.auth import hash_password
from app.llm_cache import lookup_llm_cache, normalize_llm_prompt, suggest_llm_prompts


class CompanyApiKeyTests(unittest.TestCase):
    def test_qwen_uses_server_key_when_request_has_no_key(self) -> None:
        model = {
            "id": "alibaba:qwen-plus",
            "provider": "Alibaba Cloud",
            "name": "Qwen Plus",
            "free_tier": {"requires_api_key_for_real_call": True},
        }
        runtime_result = {
            "access_mode": "api_key",
            "answer": "company response",
            "usage": {},
        }

        with (
            patch.dict(os.environ, {"DASHSCOPE_API_KEY": "company-qwen-key"}),
            patch.object(main, "get_model", return_value=model),
            patch.object(main, "run_llm", new=AsyncMock(return_value=runtime_result)) as run_llm,
            patch.object(main, "create_llm_call", return_value={"id": 42}),
        ):
            result = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="Summarize the NAS document",
                    api_key=None,
                    user={"id": 1, "username": "admin"},
                )
            )

        run_llm.assert_awaited_once_with(model, "Summarize the NAS document", "company-qwen-key")
        self.assertEqual(result["access_mode"], "company_api_key")

    def test_server_key_status_never_exposes_secret(self) -> None:
        model = {"provider": "Alibaba Cloud", "name": "Qwen Plus"}
        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "company-qwen-key"}):
            public_model = main.with_server_key_status(model)

        self.assertTrue(public_model["server_key_configured"])
        self.assertNotIn("api_key", public_model)
        self.assertNotIn("company-qwen-key", repr(public_model))


class LlmSemanticCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", Path(self.directory.name) / "app.db")
        self.db_patch.start()
        db.init_db()
        db.seed_admin(hash_password("admin123"))
        self.user = db.get_user_by_username("admin")
        assert self.user is not None

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.directory.cleanup()

    def test_polite_and_semantically_similar_prompts_call_provider_once(self) -> None:
        model = {
            "id": "alibaba:qwen-plus",
            "provider": "Alibaba Cloud",
            "name": "Qwen Plus",
            "free_tier": {"requires_api_key_for_real_call": True},
        }
        runtime_result = {
            "access_mode": "api_key",
            "answer": "Hello World examples",
            "usage": {"input_tokens": 22, "output_tokens": 100, "total_tokens": 122},
        }

        with (
            patch.dict(os.environ, {"DASHSCOPE_API_KEY": "company-qwen-key"}),
            patch.object(main, "get_model", return_value=model),
            patch.object(main, "run_llm", new=AsyncMock(return_value=runtime_result)) as run_llm,
            patch.object(main, "embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
            patch("app.llm_cache.embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
        ):
            first = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="帮我写一段 java python c c++ js 的 hello world 代码",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )
            polite = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="请帮我写一段 java python c c++ js 的 hello world 代码",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )
            similar = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="帮我写一下 java python c c++ js 的 hello world 代码",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )
            repeated = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="再请帮我写一段 java python c c++ js 的 hello world 代码",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )
            forced = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="帮我写一段 java python c c++ js 的 hello world 代码",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                    force_refresh=True,
                )
            )

        self.assertEqual(run_llm.await_count, 2)
        self.assertFalse(first["cache"]["hit"])
        self.assertEqual(polite["cache"]["match_type"], "exact")
        self.assertEqual(similar["cache"]["match_type"], "semantic")
        self.assertEqual(repeated["cache"]["match_type"], "exact")
        self.assertTrue(forced["cache"]["bypassed"])
        self.assertEqual(polite["usage"]["total_tokens"], 0)
        self.assertEqual(similar["usage"]["total_tokens"], 0)
        self.assertEqual(repeated["usage"]["total_tokens"], 0)
        self.assertEqual(forced["usage"]["total_tokens"], 122)
        calls = db.list_llm_calls(user_id=self.user["id"], role="admin")
        self.assertEqual(
            [call["access_mode"] for call in calls],
            ["company_api_key", "cache_exact", "cache_semantic", "cache_exact", "company_api_key"],
        )

    def test_lookup_request_prefix_reuses_exact_cache(self) -> None:
        model = {
            "id": "alibaba:qwen3.5-plus",
            "provider": "Alibaba Cloud",
            "name": "Qwen3.5 Plus",
            "free_tier": {"requires_api_key_for_real_call": True},
        }
        runtime_result = {
            "access_mode": "api_key",
            "answer": "NAS is network-attached storage.",
            "usage": {"input_tokens": 13, "output_tokens": 20, "total_tokens": 33},
        }

        with (
            patch.dict(os.environ, {"DASHSCOPE_API_KEY": "company-qwen-key"}),
            patch.object(main, "get_model", return_value=model),
            patch.object(main, "run_llm", new=AsyncMock(return_value=runtime_result)) as run_llm,
            patch.object(main, "embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
            patch("app.llm_cache.embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
        ):
            first = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="NAS 是什么",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )
            repeated = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="帮我查一下 NAS 是什么",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )

        self.assertEqual(run_llm.await_count, 1)
        self.assertFalse(first["cache"]["hit"])
        self.assertEqual(repeated["cache"]["match_type"], "exact")
        self.assertEqual(repeated["usage"]["total_tokens"], 0)

    def test_local_keywords_and_embedding_reuse_semantic_cache(self) -> None:
        model = {
            "id": "alibaba:qwen3.5-plus",
            "provider": "Alibaba Cloud",
            "name": "Qwen3.5 Plus",
            "free_tier": {"requires_api_key_for_real_call": True},
        }
        runtime_result = {
            "access_mode": "api_key",
            "answer": "A NAS provides shared network storage.",
            "usage": {"input_tokens": 15, "output_tokens": 20, "total_tokens": 35},
        }

        with (
            patch.dict(os.environ, {"DASHSCOPE_API_KEY": "company-qwen-key"}),
            patch.object(main, "get_model", return_value=model),
            patch.object(main, "run_llm", new=AsyncMock(return_value=runtime_result)) as run_llm,
            patch.object(main, "embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
            patch("app.llm_cache.embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
        ):
            first = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="NAS 有哪些主要用途",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )
            repeated = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="请说明一下 NAS 的主要用途是什么",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )

        self.assertEqual(run_llm.await_count, 1)
        self.assertFalse(first["cache"]["hit"])
        self.assertEqual(repeated["cache"]["match_type"], "semantic")
        self.assertGreaterEqual(repeated["cache"]["keyword_similarity"], 0.5)
        self.assertEqual(repeated["usage"]["total_tokens"], 0)

    def test_local_generation_model_also_uses_cache_preflight(self) -> None:
        model = {
            "id": "local:qwen3-4b",
            "provider": "Local NAS",
            "name": "Qwen3 4B",
            "free_tier": {"requires_api_key_for_real_call": False},
        }
        runtime_result = {
            "access_mode": "local_nas",
            "answer": "NAS is network-attached storage.",
            "usage": {"input_tokens": 12, "output_tokens": 18, "total_tokens": 30},
        }

        with (
            patch.object(main, "get_model", return_value=model),
            patch.object(main, "run_llm", new=AsyncMock(return_value=runtime_result)) as run_llm,
            patch.object(main, "embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
            patch("app.llm_cache.embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
        ):
            first = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="NAS 是什么",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )
            repeated = asyncio.run(
                main.run_model_with_audit(
                    model_id=model["id"],
                    prompt="帮我查一下 NAS 是什么",
                    api_key=None,
                    user=self.user,
                    use_semantic_cache=True,
                )
            )

        self.assertEqual(run_llm.await_count, 1)
        self.assertFalse(first["cache"]["hit"])
        self.assertEqual(repeated["cache"]["match_type"], "exact")
        self.assertEqual(repeated["usage"]["total_tokens"], 0)

    def test_prompt_suggestions_rank_cached_local_keywords(self) -> None:
        for prompt in ("NAS 有哪些主要用途", "如何建立 NAS 備份"):
            db.save_llm_query_cache(
                user_id=self.user["id"],
                model_id="alibaba:qwen3.5-plus",
                prompt_text=prompt,
                normalized_prompt=normalize_llm_prompt(prompt),
                prompt_embedding=None,
                embedding_model=None,
                result_json="{}",
            )

        suggestions = asyncio.run(
            suggest_llm_prompts(
                user_id=self.user["id"],
                model_id="alibaba:qwen3.5-plus",
                query="NAS 主要",
            )
        )

        self.assertEqual(suggestions[0]["prompt"], "NAS 有哪些主要用途")
        self.assertTrue(suggestions[0]["cached"])
        self.assertEqual(
            asyncio.run(
                suggest_llm_prompts(
                    user_id=self.user["id"],
                    model_id="openai:gpt-5",
                    query="NAS 主要",
                )
            ),
            [],
        )

    def test_historical_call_is_embedded_before_cloud_fallback(self) -> None:
        historical = db.create_llm_call(
            user_id=self.user["id"],
            provider="Alibaba Cloud",
            model_name="Qwen Plus",
            model_id="alibaba:qwen-plus",
            prompt="帮我写一段 java python c c++ js 的 hello world 代码",
            response="Historical response",
            status="completed",
            access_mode="company_api_key",
            input_tokens=22,
            output_tokens=100,
            total_tokens=122,
        )

        with (
            patch("app.llm_cache.embed_query", new=AsyncMock(return_value=[1.0, 0.0])),
            patch("app.llm_cache.request_embeddings", return_value=[[1.0, 0.0]]) as embeddings,
        ):
            cached, _ = asyncio.run(
                lookup_llm_cache(
                    user_id=self.user["id"],
                    model_id="alibaba:qwen-plus",
                    prompt="帮我写一下 java python c c++ js 的 hello world 代码",
                )
            )

        self.assertIsNotNone(cached)
        assert cached is not None
        self.assertEqual(cached["cache"]["match_type"], "semantic")
        self.assertEqual(cached["cache"]["source_call_id"], historical["id"])
        self.assertEqual(cached["result"]["answer"], "Historical response")
        embeddings.assert_called_once()


if __name__ == "__main__":
    unittest.main()
