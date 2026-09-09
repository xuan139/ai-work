from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any

from app.db import get_nas_asset, replace_document_chunks, update_nas_asset
from app.notifications import manager

AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".webm", ".ogg", ".flac", ".aac"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
PDF_SUFFIXES = {".pdf"}
DOCX_SUFFIXES = {".docx"}


def classify_asset(path: Path, mime_type: str | None = None) -> str:
    suffix = path.suffix.lower()
    mime = (mime_type or "").lower()
    if suffix in AUDIO_SUFFIXES or mime.startswith("audio/"):
        return "audio"
    if suffix in VIDEO_SUFFIXES or mime.startswith("video/"):
        return "video"
    if suffix in PDF_SUFFIXES or mime == "application/pdf":
        return "pdf"
    if suffix in DOCX_SUFFIXES or "wordprocessingml.document" in mime:
        return "docx"
    return "file"


def analyzer_for_category(category: str) -> str:
    return {
        "audio": "Whisper",
        "video": "YOLO",
        "pdf": "RAG Builder",
        "docx": "RAG Builder",
    }.get(category, "NAS Indexer")


async def process_nas_asset(asset_id: int) -> None:
    asset = get_nas_asset(asset_id)
    if not asset:
        return

    try:
        category = asset["category"]
        path = Path(asset["stored_path"])
        if category == "audio":
            updated = update_nas_asset(
                asset_id,
                status="needs_model",
                analyzer="Whisper",
                summary="已進入 Whisper 語音分析流程。需要配置 Whisper 語音模型或語音轉文字 API Key 後，才能產生真實逐字稿。",
                chunk_count=0,
            )
        elif category == "video":
            updated = update_nas_asset(
                asset_id,
                status="needs_model",
                analyzer="YOLO",
                summary="已進入 YOLO 影片分析流程。需要配置 YOLO 權重或影片分析服務後，才能產生真實物件偵測結果。",
                chunk_count=0,
            )
        elif category in {"pdf", "docx"}:
            chunks = await asyncio.to_thread(build_rag_chunks, path, category)
            replace_document_chunks(asset_id, chunks)
            updated = update_nas_asset(
                asset_id,
                status="completed",
                analyzer="RAG Builder",
                summary=f"已抽取文件文字並建立 RAG chunks：{len(chunks)} 段，可在此頁使用 LLM 進行文件問答。",
                chunk_count=len(chunks),
            )
        else:
            updated = update_nas_asset(
                asset_id,
                status="completed",
                analyzer="NAS Indexer",
                summary="檔案已保存並完成 NAS 索引。此類型目前只保留原始檔與中繼資料。",
                chunk_count=0,
            )
        await _notify(asset, updated, "nas_asset_processed")
    except Exception as exc:
        updated = update_nas_asset(
            asset_id,
            status="failed",
            analyzer=asset.get("analyzer"),
            summary=None,
            error_message=str(exc),
        )
        await _notify(asset, updated, "nas_asset_failed")


def build_rag_chunks(path: Path, category: str) -> list[dict[str, Any]]:
    text = extract_text(path, category)
    if not text.strip():
        raise RuntimeError("文件沒有可抽取的文字內容，無法建立 RAG chunks")

    chunks = chunk_text(text)
    return [
        {
            "chunk_index": index,
            "content": chunk,
            "token_estimate": max(1, len(chunk) // 4),
            "metadata_json": json.dumps({"source": path.name, "category": category}, ensure_ascii=False),
        }
        for index, chunk in enumerate(chunks)
    ]


def extract_text(path: Path, category: str) -> str:
    if category == "pdf":
        return extract_pdf_text(path)
    if category == "docx":
        return extract_docx_text(path)
    return ""


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("缺少 pypdf 套件，無法抽取 PDF 文字") from exc

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {index}]\n{text.strip()}")
    return "\n\n".join(pages)


def extract_docx_text(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("缺少 python-docx 套件，無法抽取 DOCX 文字") from exc

    document = Document(str(path))
    parts = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n\n".join(parts)


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 180) -> list[str]:
    normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(split_long_text(paragraph, max_chars, overlap))
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            tail = current[-overlap:] if overlap and len(current) > overlap else ""
            current = f"{tail}\n\n{paragraph}".strip() if tail else paragraph

    if current:
        chunks.append(current)
    return chunks


def split_long_text(text: str, max_chars: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(0, end - overlap)
    return [chunk for chunk in chunks if chunk]


async def _notify(asset: dict[str, Any], updated: dict[str, Any] | None, event_type: str) -> None:
    payload_asset = updated or asset
    await manager.broadcast(
        {
            "type": event_type,
            "asset_id": asset["id"],
            "title": asset["title"],
            "message": payload_asset.get("summary") or payload_asset.get("error_message") or asset["title"],
            "asset": payload_asset,
        }
    )
