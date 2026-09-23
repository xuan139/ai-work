from __future__ import annotations

import asyncio
import hashlib
import json
import re
from collections import Counter
from typing import Any

from app.db import (
    get_nas_asset,
    get_wiki_page,
    get_wiki_page_by_owner_slug,
    list_completed_assets_without_wiki,
    list_document_chunks,
    list_wiki_asset_ids,
    list_wiki_pages,
    list_wiki_sources,
    save_wiki_page,
)
from app.embedding_runtime import (
    EMBEDDING_MODEL,
    EmbeddingRuntimeError,
    cosine_similarity,
    pack_embedding,
    request_embeddings,
    unpack_embedding,
)

WIKI_BODY_CHUNKS_PER_ASSET = 5
WIKI_EXCERPT_CHARS = 520


def wiki_slug(title: str) -> str:
    normalized = re.sub(r"\s+", " ", title.strip().lower())
    readable = re.sub(r"[^a-z0-9\u3400-\u9fff]+", "-", normalized).strip("-")[:48]
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
    return f"{readable or 'page'}-{digest}"


async def upsert_wiki_for_asset(asset_id: int) -> dict[str, Any] | None:
    asset = await asyncio.to_thread(get_nas_asset, asset_id)
    if not asset or asset["status"] != "completed":
        return None

    slug = wiki_slug(asset["title"])
    existing = await asyncio.to_thread(get_wiki_page_by_owner_slug, asset["user_id"], slug)
    asset_ids = await asyncio.to_thread(list_wiki_asset_ids, existing["id"]) if existing else []
    asset_ids = sorted(set([*asset_ids, asset_id]))
    assets = [await asyncio.to_thread(get_nas_asset, current_id) for current_id in asset_ids]
    assets = [item for item in assets if item and item["user_id"] == asset["user_id"]]

    source_rows: list[dict[str, Any]] = []
    chunks_by_asset: dict[int, list[dict[str, Any]]] = {}
    for source_asset in assets:
        chunks = await asyncio.to_thread(list_document_chunks, source_asset["id"])
        chunks_by_asset[source_asset["id"]] = chunks
        for chunk in chunks:
            citation_key = f"A{source_asset['id']}-C{chunk['chunk_index'] + 1}"
            source_rows.append(
                {
                    "asset_id": source_asset["id"],
                    "chunk_id": chunk["id"],
                    "citation_key": citation_key,
                    "excerpt": _clean_excerpt(chunk["content"]),
                    "page_number": chunk.get("page_number"),
                    "chunk_type": chunk.get("chunk_type") or "text",
                    "image_path": chunk.get("image_path"),
                }
            )

    if not source_rows:
        return None

    summary = _page_summary(source_rows)
    body = _page_body(asset["title"], assets, chunks_by_asset)
    keywords = _keywords(" ".join([asset["title"], summary, body]))
    embedding = None
    embedding_model = None
    try:
        vectors = await asyncio.to_thread(
            request_embeddings,
            [f"{asset['title']}\n{summary}\n{body[:6000]}"],
            "document",
            asset["user_id"],
        )
        embedding = pack_embedding(vectors[0])
        embedding_model = EMBEDDING_MODEL
    except EmbeddingRuntimeError:
        pass

    return await asyncio.to_thread(
        save_wiki_page,
        owner_user_id=asset["user_id"],
        slug=slug,
        title=asset["title"],
        summary=summary,
        body=body,
        keywords_json=json.dumps(keywords, ensure_ascii=False),
        embedding=embedding,
        embedding_model=embedding_model,
        sources=source_rows,
    )


async def wiki_backfill_loop() -> None:
    while True:
        pending = await asyncio.to_thread(list_completed_assets_without_wiki, 4)
        if not pending:
            await asyncio.sleep(30)
            continue
        for asset in pending:
            try:
                await upsert_wiki_for_asset(asset["id"])
            except Exception:
                continue
        await asyncio.sleep(1)


async def search_wiki(user: dict[str, Any], query: str, limit: int = 30) -> list[dict[str, Any]]:
    pages = await asyncio.to_thread(list_wiki_pages, user_id=user["id"], role=user["role"])
    normalized_query = query.strip()
    query_vector = None
    if normalized_query:
        try:
            query_vector = (
                await asyncio.to_thread(request_embeddings, [normalized_query], "query", user["id"])
            )[0]
        except EmbeddingRuntimeError:
            pass

    results = []
    for page in pages:
        item = _public_page(page)
        if not normalized_query:
            item["retrieval_method"] = "recent"
            item["retrieval_score"] = None
            results.append(item)
            continue
        searchable = " ".join(
            [page["title"], page["summary"], page["body"], page.get("keywords_json") or ""]
        )
        keyword_score = _keyword_score(normalized_query, searchable)
        semantic_score = cosine_similarity(query_vector, unpack_embedding(page.get("embedding")))
        normalized_keyword = min(1.0, keyword_score / 12.0)
        combined = (
            0.7 * max(0.0, semantic_score) + 0.3 * normalized_keyword
            if semantic_score is not None
            else normalized_keyword
        )
        if combined <= 0:
            continue
        item["retrieval_method"] = "hybrid" if semantic_score is not None else "full_text"
        item["retrieval_score"] = round(combined, 4)
        item["semantic_score"] = round(semantic_score, 4) if semantic_score is not None else None
        item["keyword_score"] = round(normalized_keyword, 4)
        results.append(item)

    if normalized_query:
        results.sort(key=lambda item: (-float(item["retrieval_score"] or 0), item["title"]))
    return results[:limit]


async def wiki_detail(page_id: int, user: dict[str, Any]) -> dict[str, Any] | None:
    page = await asyncio.to_thread(get_wiki_page, page_id)
    if not page or (user["role"] != "admin" and page["owner_user_id"] != user["id"]):
        return None
    sources = await asyncio.to_thread(list_wiki_sources, page_id)
    detail = _public_page(page)
    detail["sources"] = [
        {
            **{key: value for key, value in source.items() if key != "image_path"},
            "image_url": (
                f"/api/nas-assets/{source['asset_id']}/chunk-images/{source['chunk_id']}"
                if source.get("image_path")
                else None
            ),
        }
        for source in sources
    ]
    related = await search_wiki(user, page["title"], limit=6)
    detail["related_pages"] = [item for item in related if item["id"] != page_id][:5]
    return detail


def _public_page(page: dict[str, Any]) -> dict[str, Any]:
    result = {key: value for key, value in page.items() if key != "embedding"}
    try:
        result["keywords"] = json.loads(result.pop("keywords_json", "[]"))
    except json.JSONDecodeError:
        result["keywords"] = []
    return result


def _page_summary(sources: list[dict[str, Any]]) -> str:
    text = " ".join(source["excerpt"] for source in sources[:3])
    return text[:360].rstrip() + ("…" if len(text) > 360 else "")


def _page_body(
    title: str,
    assets: list[dict[str, Any]],
    chunks_by_asset: dict[int, list[dict[str, Any]]],
) -> str:
    lines = [f"# {title}", "", "## 知識概覽", ""]
    lines.append(f"本頁由 NAS 中 {len(assets)} 份可追溯來源自動整理，內容隨來源重新處理而增量更新。")
    lines.extend(["", "## 來源內容", ""])
    for asset in assets:
        lines.extend(
            [
                f"### {asset['title']}",
                "",
                f"來源檔案：{asset['original_filename']} · 類型：{asset['category'].upper()} · 處理器：{asset.get('analyzer') or '-'}",
                "",
            ]
        )
        for chunk in chunks_by_asset.get(asset["id"], [])[:WIKI_BODY_CHUNKS_PER_ASSET]:
            citation = f"A{asset['id']}-C{chunk['chunk_index'] + 1}"
            location = f"第 {chunk['page_number']} 頁" if chunk.get("page_number") else chunk.get("chunk_type", "text")
            lines.append(f"- **[{citation}] {location}**：{_clean_excerpt(chunk['content'])}")
        lines.append("")
    return "\n".join(lines).strip()


def _clean_excerpt(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:WIKI_EXCERPT_CHARS].rstrip() + ("…" if len(cleaned) > WIKI_EXCERPT_CHARS else "")


def _keywords(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_.+-]{2,}|[\u3400-\u9fff]{2,8}", text.lower())
    ignored = {"本頁", "來源", "內容", "檔案", "處理器", "自動", "建立", "完成"}
    counts = Counter(token for token in tokens if token not in ignored)
    return [token for token, _ in counts.most_common(12)]


def _keyword_score(query: str, content: str) -> float:
    terms = re.findall(r"[a-z0-9][a-z0-9_.+-]*|[\u3400-\u9fff]{2,}", query.lower())
    normalized = content.lower()
    return float(sum(normalized.count(term) * min(6, len(term)) for term in terms))
