import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                audio_path TEXT NOT NULL,
                transcript TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                provider TEXT NOT NULL,
                model_name TEXT NOT NULL,
                model_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT,
                status TEXT NOT NULL,
                access_mode TEXT,
                error_message TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                remaining_tokens INTEGER,
                remaining_requests INTEGER,
                remaining_balance TEXT,
                raw_usage_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS nas_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                mime_type TEXT,
                file_size INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                analyzer TEXT,
                summary TEXT,
                error_message TEXT,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                token_estimate INTEGER NOT NULL DEFAULT 0,
                page_number INTEGER,
                chunk_type TEXT NOT NULL DEFAULT 'text',
                image_path TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(asset_id) REFERENCES nas_assets(id)
            )
            """
        )
        _ensure_column(conn, "document_chunks", "page_number", "INTEGER")
        _ensure_column(conn, "document_chunks", "chunk_type", "TEXT NOT NULL DEFAULT 'text'")
        _ensure_column(conn, "document_chunks", "image_path", "TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meetings_user_id ON meetings(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_calls_user_id ON llm_calls(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_calls_created_at ON llm_calls(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nas_assets_user_id ON nas_assets(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nas_assets_created_at ON nas_assets(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_asset_id ON document_chunks(asset_id)")


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if column not in {row["name"] for row in rows}:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def seed_admin(password_hash: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (username, password_hash, role)
            VALUES ('admin', ?, 'admin')
            """,
            (password_hash,),
        )


def get_user_by_username(username: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def create_meeting(
    *,
    user_id: int,
    source: str,
    title: str,
    original_filename: str,
    audio_path: str,
    status: str = "processing",
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO meetings (user_id, source, title, original_filename, audio_path, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, source, title, original_filename, audio_path, status),
        )
        row = conn.execute("SELECT * FROM meetings WHERE id = ?", (cursor.lastrowid,)).fetchone()
    meeting = _row_to_dict(row)
    if meeting is None:
        raise RuntimeError("Meeting creation failed")
    return meeting


def update_meeting_status(
    meeting_id: int,
    *,
    status: str,
    transcript: str | None = None,
    error_message: str | None = None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE meetings
            SET status = ?, transcript = COALESCE(?, transcript), error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, transcript, error_message, meeting_id),
        )
        row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
    return _row_to_dict(row)


def list_meetings(*, user_id: int, role: str, q: str | None = None) -> list[dict[str, Any]]:
    params: list[Any] = []
    where = []

    if role != "admin":
        where.append("user_id = ?")
        params.append(user_id)

    if q:
        where.append("(title LIKE ? OR original_filename LIKE ? OR transcript LIKE ?)")
        pattern = f"%{q}%"
        params.extend([pattern, pattern, pattern])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT id, user_id, source, title, original_filename, transcript, status, error_message, created_at, updated_at
        FROM meetings
        {where_sql}
        ORDER BY datetime(created_at) DESC, id DESC
        LIMIT 100
    """

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def get_meeting(meeting_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
    return _row_to_dict(row)


def create_nas_asset(
    *,
    user_id: int,
    category: str,
    title: str,
    original_filename: str,
    stored_path: str,
    mime_type: str | None,
    file_size: int,
    status: str = "processing",
    analyzer: str | None = None,
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO nas_assets (
                user_id, category, title, original_filename, stored_path, mime_type,
                file_size, status, analyzer
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, category, title, original_filename, stored_path, mime_type, file_size, status, analyzer),
        )
        row = conn.execute("SELECT * FROM nas_assets WHERE id = ?", (cursor.lastrowid,)).fetchone()
    asset = _row_to_dict(row)
    if asset is None:
        raise RuntimeError("NAS asset creation failed")
    return asset


def update_nas_asset(
    asset_id: int,
    *,
    status: str,
    analyzer: str | None = None,
    summary: str | None = None,
    error_message: str | None = None,
    chunk_count: int | None = None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE nas_assets
            SET status = ?,
                analyzer = COALESCE(?, analyzer),
                summary = ?,
                error_message = ?,
                chunk_count = COALESCE(?, chunk_count),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, analyzer, summary, error_message, chunk_count, asset_id),
        )
        row = conn.execute("SELECT * FROM nas_assets WHERE id = ?", (asset_id,)).fetchone()
    return _row_to_dict(row)


def get_nas_asset(asset_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT nas_assets.*, users.username AS owner_username, users.role AS owner_role
            FROM nas_assets
            JOIN users ON users.id = nas_assets.user_id
            WHERE nas_assets.id = ?
            """,
            (asset_id,),
        ).fetchone()
    return _row_to_dict(row)


def list_nas_assets(*, user_id: int, role: str, q: str | None = None) -> list[dict[str, Any]]:
    params: list[Any] = []
    where = []

    if role != "admin":
        where.append("nas_assets.user_id = ?")
        params.append(user_id)

    if q:
        where.append(
            """
            (title LIKE ? OR original_filename LIKE ? OR category LIKE ?
             OR analyzer LIKE ? OR summary LIKE ? OR users.username LIKE ?)
            """
        )
        pattern = f"%{q}%"
        params.extend([pattern, pattern, pattern, pattern, pattern, pattern])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT nas_assets.*, users.username AS owner_username, users.role AS owner_role
        FROM nas_assets
        JOIN users ON users.id = nas_assets.user_id
        {where_sql}
        ORDER BY datetime(nas_assets.created_at) DESC, nas_assets.id DESC
        LIMIT 100
    """

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def replace_document_chunks(asset_id: int, chunks: list[dict[str, Any]]) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM document_chunks WHERE asset_id = ?", (asset_id,))
        conn.executemany(
            """
            INSERT INTO document_chunks (
                asset_id, chunk_index, content, token_estimate, page_number,
                chunk_type, image_path, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    asset_id,
                    chunk["chunk_index"],
                    chunk["content"],
                    chunk.get("token_estimate", 0),
                    chunk.get("page_number"),
                    chunk.get("chunk_type", "text"),
                    chunk.get("image_path"),
                    chunk.get("metadata_json"),
                )
                for chunk in chunks
            ],
        )


def list_document_chunks(asset_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, asset_id, chunk_index, content, token_estimate, page_number,
                   chunk_type, image_path, metadata_json, created_at
            FROM document_chunks
            WHERE asset_id = ?
            ORDER BY chunk_index ASC
            """,
            (asset_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_document_chunk(chunk_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT id, asset_id, chunk_index, content, token_estimate, page_number,
                   chunk_type, image_path, metadata_json, created_at
            FROM document_chunks
            WHERE id = ?
            """,
            (chunk_id,),
        ).fetchone()
    return _row_to_dict(row)


def search_document_chunks(asset_id: int, query: str, limit: int = 5) -> list[dict[str, Any]]:
    terms = [term.lower() for term in query.split() if term.strip()]
    chunks = list_document_chunks(asset_id)
    if not terms:
        return chunks[:limit]

    scored = []
    for chunk in chunks:
        text = chunk["content"].lower()
        score = sum(text.count(term) for term in terms)
        if score:
            scored.append((score, chunk))

    if not scored:
        return chunks[:limit]
    scored.sort(key=lambda item: (-item[0], item[1]["chunk_index"]))
    return [chunk for _, chunk in scored[:limit]]


def create_llm_call(
    *,
    user_id: int,
    provider: str,
    model_name: str,
    model_id: str,
    prompt: str,
    response: str | None,
    status: str,
    access_mode: str | None = None,
    error_message: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    total_tokens: int | None = None,
    remaining_tokens: int | None = None,
    remaining_requests: int | None = None,
    remaining_balance: str | None = None,
    raw_usage_json: str | None = None,
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO llm_calls (
                user_id, provider, model_name, model_id, prompt, response, status, access_mode,
                error_message, input_tokens, output_tokens, total_tokens, remaining_tokens,
                remaining_requests, remaining_balance, raw_usage_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                provider,
                model_name,
                model_id,
                prompt,
                response,
                status,
                access_mode,
                error_message,
                input_tokens,
                output_tokens,
                total_tokens,
                remaining_tokens,
                remaining_requests,
                remaining_balance,
                raw_usage_json,
            ),
        )
        row = conn.execute("SELECT * FROM llm_calls WHERE id = ?", (cursor.lastrowid,)).fetchone()
    call = _row_to_dict(row)
    if call is None:
        raise RuntimeError("LLM call creation failed")
    return call


def list_llm_calls(*, user_id: int, role: str, q: str | None = None) -> list[dict[str, Any]]:
    params: list[Any] = []
    where = []

    if role != "admin":
        where.append("llm_calls.user_id = ?")
        params.append(user_id)

    if q:
        where.append(
            """
            (provider LIKE ? OR model_name LIKE ? OR model_id LIKE ? OR prompt LIKE ?
             OR response LIKE ? OR error_message LIKE ? OR users.username LIKE ?)
            """
        )
        pattern = f"%{q}%"
        params.extend([pattern, pattern, pattern, pattern, pattern, pattern, pattern])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT llm_calls.id, llm_calls.user_id, users.username AS caller_username,
               users.role AS caller_role, provider, model_name, model_id, prompt,
               response, status, access_mode, error_message, input_tokens, output_tokens,
               total_tokens, remaining_tokens, remaining_requests, remaining_balance,
               raw_usage_json, llm_calls.created_at
        FROM llm_calls
        JOIN users ON users.id = llm_calls.user_id
        {where_sql}
        ORDER BY datetime(llm_calls.created_at) DESC, llm_calls.id DESC
        LIMIT 100
    """

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]
