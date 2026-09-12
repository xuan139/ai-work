from __future__ import annotations

import asyncio
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class LlmRuntimeError(RuntimeError):
    pass


LOCAL_NAS_SYSTEM_PROMPT = (
    "You are the AI assistant for a Network Attached Storage (NAS) meeting and document system. "
    "Unless the user explicitly says otherwise, NAS means Network Attached Storage. "
    "Answer in the same language as the user and prefer Traditional Chinese when the user writes Chinese."
)


def company_api_key_for_model(model: dict[str, Any]) -> str | None:
    env_name = {
        "Alibaba Cloud": "DASHSCOPE_API_KEY",
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY",
        "Google": "GEMINI_API_KEY",
        "DeepSeek": "DEEPSEEK_API_KEY",
        "Mistral AI": "MISTRAL_API_KEY",
        "Cohere": "COHERE_API_KEY",
        "xAI": "XAI_API_KEY",
        "Perplexity": "PERPLEXITY_API_KEY",
        "Groq": "GROQ_API_KEY",
        "Cerebras": "CEREBRAS_API_KEY",
    }.get(model.get("provider"))
    return (os.getenv(env_name) or None) if env_name else None


async def run_llm(model: dict[str, Any], prompt: str, api_key: str | None) -> dict[str, Any]:
    return await asyncio.to_thread(_run_llm_sync, model, prompt, api_key)


def _run_llm_sync(model: dict[str, Any], prompt: str, api_key: str | None) -> dict[str, Any]:
    provider = model["provider"]
    if provider == "Local NAS":
        answer, usage = _call_local_nas(model, prompt)
        return {"access_mode": "local_nas", "answer": answer, "usage": usage}

    if provider == "Free Gateway":
        answer, headers = _call_pollinations(model["model"], prompt)
        return {"access_mode": "free_no_key", "answer": answer, "usage": usage_from_headers(headers)}

    if not api_key:
        raise LlmRuntimeError("API key is required for this model")

    if provider == "OpenAI":
        answer, usage = _call_openai(model["model"], prompt, api_key)
        return {"access_mode": "api_key", "answer": answer, "usage": usage}
    if provider == "Anthropic":
        answer, usage = _call_anthropic(model["model"], prompt, api_key)
        return {"access_mode": "api_key", "answer": answer, "usage": usage}
    if provider == "Google":
        answer, usage = _call_gemini(model["model"], prompt, api_key)
        return {"access_mode": "api_key", "answer": answer, "usage": usage}
    if provider == "Cohere":
        answer, usage = _call_cohere(model["model"], prompt, api_key)
        return {"access_mode": "api_key", "answer": answer, "usage": usage}

    dashscope_base_url = os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    ).rstrip("/")
    openai_compatible = {
        "DeepSeek": "https://api.deepseek.com/chat/completions",
        "Alibaba Cloud": f"{dashscope_base_url}/chat/completions",
        "Mistral AI": "https://api.mistral.ai/v1/chat/completions",
        "xAI": "https://api.x.ai/v1/chat/completions",
        "Perplexity": "https://api.perplexity.ai/chat/completions",
        "Groq": "https://api.groq.com/openai/v1/chat/completions",
        "Cerebras": "https://api.cerebras.ai/v1/chat/completions",
    }
    if provider in openai_compatible:
        answer, usage = _call_openai_compatible(openai_compatible[provider], model["model"], prompt, api_key)
        return {
            "access_mode": "api_key",
            "answer": answer,
            "usage": usage,
        }

    raise LlmRuntimeError(f"Provider is not supported: {provider}")


def _call_local_nas(model: dict[str, Any], prompt: str) -> tuple[str, dict[str, Any]]:
    base_url = (
        str(model["api_base"])
        if model.get("custom_model")
        else os.getenv("NAS_LLM_BASE_URL", str(model["api_base"]))
    ).rstrip("/")
    tokenizer_content = f"{LOCAL_NAS_SYSTEM_PROMPT}\n\n{prompt}"
    tokenizer_used = bool(model.get("supports_tokenize", model.get("id") == "local:qwen3-4b"))
    if tokenizer_used:
        token_payload, _ = _request_json(
            _json_request(f"{base_url}/tokenize", {"content": tokenizer_content}, {}),
            timeout=30,
        )
        tokens = token_payload.get("tokens")
        if not isinstance(tokens, list):
            raise LlmRuntimeError("Local NAS tokenizer did not return a token list")
        input_tokens = len(tokens)
    else:
        input_tokens = estimate_prompt_tokens(tokenizer_content)
    max_input_tokens = int(model.get("max_input_tokens", 4096))
    if input_tokens > max_input_tokens:
        raise LlmRuntimeError(
            f"Prompt has {input_tokens} tokens; local model input limit is {max_input_tokens} tokens"
        )

    request_payload = {
        "model": model["model"],
        "messages": [
            {"role": "system", "content": LOCAL_NAS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 800,
    }
    if model.get("id") == "local:qwen3-4b":
        request_payload["chat_template_kwargs"] = {"enable_thinking": False}

    payload, headers = _request_json(
        _json_request(
            f"{base_url}/v1/chat/completions",
            request_payload,
            {},
        ),
        timeout=180,
    )
    try:
        answer = str(payload["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmRuntimeError("Local NAS model response did not include chat text output") from exc
    if not answer:
        raise LlmRuntimeError("Local NAS model response did not include chat text output")

    usage = usage_from_openai_chat(payload, headers)
    if usage["input_tokens"] is None:
        usage["input_tokens"] = input_tokens
        usage["total_tokens"] = _sum_ints(input_tokens, usage["output_tokens"])
    reported_input_tokens = usage["input_tokens"] if isinstance(usage["input_tokens"], int) else input_tokens
    usage["remaining_tokens"] = max(0, max_input_tokens - reported_input_tokens)
    usage["raw_usage"] = {
        **(usage["raw_usage"] or {}),
        "tokenizer_input_tokens": input_tokens,
        "token_count_method": "endpoint" if tokenizer_used else "utf8_estimate",
        "max_input_tokens": max_input_tokens,
    }
    return answer, usage


def estimate_prompt_tokens(text: str) -> int:
    return max(1, (len(text.encode("utf-8")) + 2) // 3)


def _call_pollinations(model: str, prompt: str) -> tuple[str, dict[str, str]]:
    query = urlencode({"model": model})
    url = f"https://text.pollinations.ai/{quote(prompt)}?{query}"
    request = Request(url, headers={"User-Agent": "ai-work-demo/0.1"})
    return _request_text(request)


def _call_openai(model: str, prompt: str, api_key: str) -> tuple[str, dict[str, Any]]:
    data = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 800,
    }
    request = _json_request(
        "https://api.openai.com/v1/responses",
        data,
        {"Authorization": f"Bearer {api_key}"},
    )
    payload, headers = _request_json(request)
    if payload.get("output_text"):
        return str(payload["output_text"]), usage_from_openai_responses(payload, headers)
    texts: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                texts.append(str(content["text"]))
    if texts:
        return "\n".join(texts), usage_from_openai_responses(payload, headers)
    raise LlmRuntimeError("OpenAI response did not include text output")


def _call_anthropic(model: str, prompt: str, api_key: str) -> tuple[str, dict[str, Any]]:
    data = {
        "model": model,
        "max_tokens": 800,
        "messages": [{"role": "user", "content": prompt}],
    }
    request = _json_request(
        "https://api.anthropic.com/v1/messages",
        data,
        {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    payload, headers = _request_json(request)
    texts = [part.get("text", "") for part in payload.get("content", []) if part.get("type") == "text"]
    if texts:
        return "\n".join(texts), usage_from_anthropic(payload, headers)
    raise LlmRuntimeError("Anthropic response did not include text output")


def _call_gemini(model: str, prompt: str, api_key: str) -> tuple[str, dict[str, Any]]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model)}:generateContent?{urlencode({'key': api_key})}"
    request = _json_request(
        url,
        {"contents": [{"parts": [{"text": prompt}]}]},
        {},
    )
    payload, headers = _request_json(request)
    texts: list[str] = []
    for candidate in payload.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if part.get("text"):
                texts.append(str(part["text"]))
    if texts:
        return "\n".join(texts), usage_from_gemini(payload, headers)
    raise LlmRuntimeError("Gemini response did not include text output")


def _call_cohere(model: str, prompt: str, api_key: str) -> tuple[str, dict[str, Any]]:
    request = _json_request(
        "https://api.cohere.com/v2/chat",
        {"model": model, "messages": [{"role": "user", "content": prompt}]},
        {"Authorization": f"Bearer {api_key}"},
    )
    payload, headers = _request_json(request)
    texts = [item.get("text", "") for item in payload.get("message", {}).get("content", []) if item.get("type") == "text"]
    if texts:
        return "\n".join(texts), usage_from_headers(headers)
    raise LlmRuntimeError("Cohere response did not include text output")


def _call_openai_compatible(url: str, model: str, prompt: str, api_key: str) -> tuple[str, dict[str, Any]]:
    request = _json_request(
        url,
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
        },
        {"Authorization": f"Bearer {api_key}"},
    )
    payload, headers = _request_json(request)
    try:
        return str(payload["choices"][0]["message"]["content"]), usage_from_openai_chat(payload, headers)
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmRuntimeError("Provider response did not include chat text output") from exc


def _json_request(url: str, data: dict[str, Any], headers: dict[str, str]) -> Request:
    body = json.dumps(data).encode("utf-8")
    return Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ai-work-demo/0.1",
            **headers,
        },
    )


def _request_json(request: Request, *, timeout: int = 45) -> tuple[dict[str, Any], dict[str, str]]:
    text, headers = _request_text(request, timeout=timeout)
    try:
        return json.loads(text), headers
    except json.JSONDecodeError as exc:
        raise LlmRuntimeError("Provider returned a non-JSON response") from exc


def _request_text(request: Request, *, timeout: int = 45) -> tuple[str, dict[str, str]]:
    try:
        with urlopen(request, timeout=timeout) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.read().decode("utf-8", errors="replace").strip(), headers
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise LlmRuntimeError(f"Provider request failed with HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise LlmRuntimeError(f"Provider request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise LlmRuntimeError("Provider request timed out") from exc


def usage_from_openai_chat(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    usage = payload.get("usage") or {}
    return {
        **usage_from_headers(headers),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "raw_usage": usage or None,
    }


def usage_from_openai_responses(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    usage = payload.get("usage") or {}
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    return {
        **usage_from_headers(headers),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": usage.get("total_tokens") or _sum_ints(input_tokens, output_tokens),
        "raw_usage": usage or None,
    }


def usage_from_anthropic(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    usage = payload.get("usage") or {}
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    return {
        **usage_from_headers(headers),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": _sum_ints(input_tokens, output_tokens),
        "raw_usage": usage or None,
    }


def usage_from_gemini(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    usage = payload.get("usageMetadata") or {}
    input_tokens = usage.get("promptTokenCount")
    output_tokens = usage.get("candidatesTokenCount")
    return {
        **usage_from_headers(headers),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": usage.get("totalTokenCount") or _sum_ints(input_tokens, output_tokens),
        "raw_usage": usage or None,
    }


def usage_from_headers(headers: dict[str, str]) -> dict[str, Any]:
    return {
        "remaining_tokens": _first_int_header(headers, ("x-ratelimit-remaining-tokens", "x-ratelimit-remaining-tokens-remaining")),
        "remaining_requests": _first_int_header(headers, ("x-ratelimit-remaining-requests", "x-ratelimit-remaining-requests-remaining")),
        "remaining_balance": headers.get("x-ratelimit-remaining-balance") or headers.get("x-balance-remaining"),
        "raw_usage": None,
    }


def _first_int_header(headers: dict[str, str], names: tuple[str, ...]) -> int | None:
    for name in names:
        value = headers.get(name)
        if value is None:
            continue
        try:
            return int(float(value))
        except ValueError:
            continue
    return None


def _sum_ints(*values: int | None) -> int | None:
    if any(value is None for value in values):
        return None
    return sum(value for value in values if value is not None)
