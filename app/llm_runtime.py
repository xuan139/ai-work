from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class LlmRuntimeError(RuntimeError):
    pass


async def run_llm(model: dict[str, Any], prompt: str, api_key: str | None) -> dict[str, Any]:
    return await asyncio.to_thread(_run_llm_sync, model, prompt, api_key)


def _run_llm_sync(model: dict[str, Any], prompt: str, api_key: str | None) -> dict[str, Any]:
    provider = model["provider"]
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

    openai_compatible = {
        "DeepSeek": "https://api.deepseek.com/chat/completions",
        "Alibaba Cloud": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
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


def _request_json(request: Request) -> tuple[dict[str, Any], dict[str, str]]:
    text, headers = _request_text(request)
    try:
        return json.loads(text), headers
    except json.JSONDecodeError as exc:
        raise LlmRuntimeError("Provider returned a non-JSON response") from exc


def _request_text(request: Request) -> tuple[str, dict[str, str]]:
    try:
        with urlopen(request, timeout=45) as response:
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
