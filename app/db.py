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
                is_active INTEGER NOT NULL DEFAULT 1,
                session_version INTEGER NOT NULL DEFAULT 1,
                last_login_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _ensure_column(conn, "users", "is_active", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "users", "session_version", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "users", "last_login_at", "TEXT")
        _ensure_column(conn, "users", "updated_at", "TEXT")
        conn.execute("UPDATE users SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)")
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
                nas_asset_id INTEGER,
                asr_model_id TEXT,
                asr_provider TEXT,
                asr_model TEXT,
                asr_engine TEXT,
                asr_metadata_json TEXT,
                translation_enabled INTEGER NOT NULL DEFAULT 0,
                translation_target TEXT,
                translation TEXT,
                translation_model_id TEXT,
                translation_provider TEXT,
                translation_model TEXT,
                translation_status TEXT,
                translation_error TEXT,
                translation_metadata_json TEXT,
                line_push_enabled INTEGER NOT NULL DEFAULT 0,
                line_group_id TEXT,
                line_group_name TEXT,
                line_push_full_transcript INTEGER NOT NULL DEFAULT 0,
                line_summary TEXT,
                line_push_status TEXT NOT NULL DEFAULT 'disabled',
                line_push_error TEXT,
                line_pushed_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        _ensure_column(conn, "meetings", "nas_asset_id", "INTEGER")
        _ensure_column(conn, "meetings", "asr_model_id", "TEXT")
        _ensure_column(conn, "meetings", "asr_provider", "TEXT")
        _ensure_column(conn, "meetings", "asr_model", "TEXT")
        _ensure_column(conn, "meetings", "asr_engine", "TEXT")
        _ensure_column(conn, "meetings", "asr_metadata_json", "TEXT")
        _ensure_column(conn, "meetings", "translation_enabled", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "meetings", "translation_target", "TEXT")
        _ensure_column(conn, "meetings", "translation", "TEXT")
        _ensure_column(conn, "meetings", "translation_model_id", "TEXT")
        _ensure_column(conn, "meetings", "translation_provider", "TEXT")
        _ensure_column(conn, "meetings", "translation_model", "TEXT")
        _ensure_column(conn, "meetings", "translation_status", "TEXT")
        _ensure_column(conn, "meetings", "translation_error", "TEXT")
        _ensure_column(conn, "meetings", "translation_metadata_json", "TEXT")
        _ensure_column(conn, "meetings", "line_push_enabled", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "meetings", "line_group_id", "TEXT")
        _ensure_column(conn, "meetings", "line_group_name", "TEXT")
        _ensure_column(conn, "meetings", "line_push_full_transcript", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "meetings", "line_summary", "TEXT")
        _ensure_column(conn, "meetings", "line_push_status", "TEXT NOT NULL DEFAULT 'disabled'")
        _ensure_column(conn, "meetings", "line_push_error", "TEXT")
        _ensure_column(conn, "meetings", "line_pushed_at", "TEXT")
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
        _ensure_column(conn, "llm_calls", "channel", "TEXT")
        _ensure_column(conn, "llm_calls", "external_caller", "TEXT")
        _ensure_column(conn, "llm_calls", "source_ref", "TEXT")
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
                processor_config_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        _ensure_column(conn, "nas_assets", "processor_config_json", "TEXT")
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                model_id TEXT NOT NULL,
                query_text TEXT NOT NULL,
                normalized_query TEXT NOT NULL,
                query_embedding BLOB,
                embedding_model TEXT,
                result_json TEXT NOT NULL,
                contexts_json TEXT NOT NULL,
                hit_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_hit_at TEXT,
                UNIQUE(asset_id, model_id, normalized_query),
                FOREIGN KEY(asset_id) REFERENCES nas_assets(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                model_id TEXT NOT NULL,
                prompt_text TEXT NOT NULL,
                normalized_prompt TEXT NOT NULL,
                prompt_embedding BLOB,
                embedding_model TEXT,
                result_json TEXT NOT NULL,
                hit_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_hit_at TEXT,
                UNIQUE(user_id, model_id, normalized_prompt),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS asset_ai_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                llm_call_id INTEGER,
                model_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                model_name TEXT NOT NULL,
                question TEXT NOT NULL,
                normalized_question TEXT NOT NULL,
                answer TEXT NOT NULL,
                access_mode TEXT,
                embedding_status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(asset_id, model_id, normalized_question),
                FOREIGN KEY(asset_id) REFERENCES nas_assets(id),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(llm_call_id) REFERENCES llm_calls(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS line_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL UNIQUE,
                source_type TEXT NOT NULL,
                display_name TEXT,
                owner_user_id INTEGER NOT NULL,
                is_approved INTEGER NOT NULL DEFAULT 0,
                auto_pdf_summary INTEGER NOT NULL DEFAULT 1,
                rag_queries_enabled INTEGER NOT NULL DEFAULT 1,
                default_model_id TEXT NOT NULL DEFAULT 'local:qwen3-4b',
                monthly_call_limit INTEGER NOT NULL DEFAULT 500,
                monthly_token_limit INTEGER NOT NULL DEFAULT 200000,
                content_version INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(owner_user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS line_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_source_id INTEGER NOT NULL,
                line_message_id TEXT NOT NULL UNIQUE,
                line_event_id TEXT,
                sender_id TEXT,
                sender_name TEXT,
                asset_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                summary TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(line_source_id) REFERENCES line_sources(id),
                FOREIGN KEY(asset_id) REFERENCES nas_assets(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS line_query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_source_id INTEGER NOT NULL,
                content_version INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                model_id TEXT NOT NULL,
                query_text TEXT NOT NULL,
                normalized_query TEXT NOT NULL,
                query_embedding BLOB,
                embedding_model TEXT,
                answer TEXT NOT NULL,
                contexts_json TEXT NOT NULL,
                hit_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_hit_at TEXT,
                UNIQUE(line_source_id, content_version, model_id, normalized_query),
                FOREIGN KEY(line_source_id) REFERENCES line_sources(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS custom_models (
                id TEXT PRIMARY KEY,
                model_type TEXT NOT NULL,
                name TEXT NOT NULL,
                engine TEXT NOT NULL,
                model_alias TEXT,
                model_file TEXT,
                storage_subdir TEXT,
                download_url TEXT,
                expected_bytes INTEGER,
                sha256 TEXT,
                api_base TEXT,
                max_input_tokens INTEGER,
                supports_tokenize INTEGER NOT NULL DEFAULT 0,
                languages TEXT,
                recommended_for TEXT,
                recommendation TEXT,
                validation_status TEXT NOT NULL DEFAULT 'registered',
                validation_error TEXT,
                is_enabled INTEGER NOT NULL DEFAULT 1,
                created_by INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
            """
        )
        _ensure_column(conn, "document_chunks", "page_number", "INTEGER")
        _ensure_column(conn, "document_chunks", "chunk_type", "TEXT NOT NULL DEFAULT 'text'")
        _ensure_column(conn, "document_chunks", "image_path", "TEXT")
        _ensure_column(conn, "document_chunks", "embedding", "BLOB")
        _ensure_column(conn, "document_chunks", "embedding_model", "TEXT")
        _ensure_column(conn, "line_sources", "is_approved", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "line_sources", "monthly_call_limit", "INTEGER NOT NULL DEFAULT 500")
        _ensure_column(conn, "line_sources", "monthly_token_limit", "INTEGER NOT NULL DEFAULT 200000")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meetings_user_id ON meetings(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_calls_user_id ON llm_calls(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_calls_created_at ON llm_calls(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nas_assets_user_id ON nas_assets(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nas_assets_created_at ON nas_assets(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_asset_id ON document_chunks(asset_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rag_query_cache_asset_model ON rag_query_cache(asset_id, model_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_query_cache_user_model ON llm_query_cache(user_id, model_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_asset_ai_analyses_asset ON asset_ai_analyses(asset_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_line_documents_source ON line_documents(line_source_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_line_query_cache_source ON line_query_cache(line_source_id, content_version, model_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_custom_models_type ON custom_models(model_type, is_enabled, validation_status)")


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
        row = conn.execute("SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def list_users(q: str | None = None) -> list[dict[str, Any]]:
    params: list[Any] = []
    where_sql = ""
    if q:
        where_sql = "WHERE users.username LIKE ? OR users.role LIKE ?"
        pattern = f"%{q}%"
        params.extend([pattern, pattern])

    with connect() as conn:
        rows = conn.execute(
            f"""
            SELECT users.id, users.username, users.role, users.is_active,
                   users.last_login_at, users.created_at, users.updated_at,
                   (SELECT COUNT(*) FROM meetings WHERE meetings.user_id = users.id) AS meeting_count,
                   (SELECT COUNT(*) FROM nas_assets WHERE nas_assets.user_id = users.id) AS asset_count,
                   (SELECT COUNT(*) FROM llm_calls WHERE llm_calls.user_id = users.id) AS llm_call_count
            FROM users
            {where_sql}
            ORDER BY CASE WHEN users.role = 'admin' THEN 0 ELSE 1 END,
                     users.username COLLATE NOCASE
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def create_user(*, username: str, password_hash: str, role: str) -> dict[str, Any]:
    with connect() as conn:
        existing = conn.execute("SELECT id FROM users WHERE username = ? COLLATE NOCASE", (username,)).fetchone()
        if existing:
            raise sqlite3.IntegrityError("username already exists")
        cursor = conn.execute(
            """
            INSERT INTO users (username, password_hash, role, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (username, password_hash, role),
        )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    user = _row_to_dict(row)
    if user is None:
        raise RuntimeError("User creation failed")
    return user


def update_user_access(user_id: int, *, role: str, is_active: bool) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE users
            SET role = ?, is_active = ?, session_version = session_version + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (role, int(is_active), user_id),
        )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def reset_user_password(user_id: int, password_hash: str) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, session_version = session_version + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (password_hash, user_id),
        )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def mark_user_login(user_id: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE users SET last_login_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )


def user_owned_record_count(user_id: int) -> int:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM meetings WHERE user_id = ?) +
                (SELECT COUNT(*) FROM nas_assets WHERE user_id = ?) +
                (SELECT COUNT(*) FROM llm_calls WHERE user_id = ?) AS total
            """,
            (user_id, user_id, user_id),
        ).fetchone()
    return int(row["total"] if row else 0)


def delete_user(user_id: int) -> bool:
    with connect() as conn:
        cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return cursor.rowcount > 0


def create_custom_model(values: dict[str, Any]) -> dict[str, Any]:
    columns = (
        "id", "model_type", "name", "engine", "model_alias", "model_file",
        "storage_subdir", "download_url", "expected_bytes", "sha256", "api_base",
        "max_input_tokens", "supports_tokenize", "languages", "recommended_for",
        "recommendation", "validation_status", "validation_error", "is_enabled", "created_by",
    )
    with connect() as conn:
        conn.execute(
            f"INSERT INTO custom_models ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
            tuple(values.get(column) for column in columns),
        )
        row = conn.execute("SELECT * FROM custom_models WHERE id = ?", (values["id"],)).fetchone()
    model = _row_to_dict(row)
    if model is None:
        raise RuntimeError("Custom model creation failed")
    return model


def list_custom_models(
    model_type: str | None = None,
    *,
    enabled_only: bool = False,
    ready_only: bool = False,
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []
    if model_type:
        where.append("model_type = ?")
        params.append(model_type)
    if enabled_only:
        where.append("is_enabled = 1")
    if ready_only:
        where.append("validation_status = 'ready'")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    with connect() as conn:
        rows = conn.execute(
            f"SELECT * FROM custom_models {where_sql} ORDER BY datetime(created_at) DESC, id",
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def get_custom_model(model_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM custom_models WHERE id = ?", (model_id,)).fetchone()
    return _row_to_dict(row)


def update_custom_model_validation(
    model_id: str,
    *,
    status: str,
    error_message: str | None = None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE custom_models
            SET validation_status = ?, validation_error = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, error_message, model_id),
        )
        row = conn.execute("SELECT * FROM custom_models WHERE id = ?", (model_id,)).fetchone()
    return _row_to_dict(row)


def delete_custom_model(model_id: str) -> bool:
    with connect() as conn:
        cursor = conn.execute("DELETE FROM custom_models WHERE id = ?", (model_id,))
    return cursor.rowcount > 0


def create_meeting(
    *,
    user_id: int,
    source: str,
    title: str,
    original_filename: str,
    audio_path: str,
    status: str = "processing",
    nas_asset_id: int | None = None,
    asr_model_id: str | None = None,
    asr_provider: str | None = None,
    asr_model: str | None = None,
    asr_engine: str | None = None,
    translation_enabled: bool = False,
    translation_target: str | None = None,
    translation_model_id: str | None = None,
    translation_provider: str | None = None,
    translation_model: str | None = None,
    line_push_enabled: bool = False,
    line_group_id: str | None = None,
    line_group_name: str | None = None,
    line_push_full_transcript: bool = False,
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO meetings (
                user_id, source, title, original_filename, audio_path, status,
                nas_asset_id, asr_model_id, asr_provider, asr_model, asr_engine,
                translation_enabled, translation_target, translation_model_id,
                translation_provider, translation_model, translation_status,
                line_push_enabled, line_group_id, line_group_name,
                line_push_full_transcript, line_push_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                source,
                title,
                original_filename,
                audio_path,
                status,
                nas_asset_id,
                asr_model_id,
                asr_provider,
                asr_model,
                asr_engine,
                int(translation_enabled),
                translation_target,
                translation_model_id,
                translation_provider,
                translation_model,
                "pending" if translation_enabled else "disabled",
                int(line_push_enabled),
                line_group_id,
                line_group_name,
                int(line_push_full_transcript),
                "pending" if line_push_enabled else "disabled",
            ),
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
    asr_metadata_json: str | None = None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE meetings
            SET status = ?, transcript = COALESCE(?, transcript), error_message = ?,
                asr_metadata_json = COALESCE(?, asr_metadata_json), updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, transcript, error_message, asr_metadata_json, meeting_id),
        )
        row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
    return _row_to_dict(row)


def update_meeting_translation(
    meeting_id: int,
    *,
    translation_status: str,
    translation: str | None = None,
    translation_error: str | None = None,
    translation_metadata_json: str | None = None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE meetings
            SET translation_status = ?, translation = COALESCE(?, translation),
                translation_error = ?,
                translation_metadata_json = COALESCE(?, translation_metadata_json),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                translation_status,
                translation,
                translation_error,
                translation_metadata_json,
                meeting_id,
            ),
        )
        row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
    return _row_to_dict(row)


def update_meeting_line_push(
    meeting_id: int,
    *,
    status: str,
    summary: str | None = None,
    error_message: str | None = None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE meetings
            SET line_push_status = ?, line_summary = COALESCE(?, line_summary),
                line_push_error = ?,
                line_pushed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE line_pushed_at END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, summary, error_message, status, meeting_id),
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
        where.append("(title LIKE ? OR original_filename LIKE ? OR transcript LIKE ? OR translation LIKE ?)")
        pattern = f"%{q}%"
        params.extend([pattern, pattern, pattern, pattern])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT id, user_id, source, title, original_filename, transcript, status, error_message,
               nas_asset_id, asr_model_id, asr_provider, asr_model, asr_engine,
               asr_metadata_json, translation_enabled, translation_target, translation,
               translation_model_id, translation_provider, translation_model,
               translation_status, translation_error, translation_metadata_json,
               line_push_enabled, line_group_id, line_group_name,
               line_push_full_transcript, line_summary, line_push_status,
               line_push_error, line_pushed_at,
               created_at, updated_at
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
    processor_config_json: str | None = None,
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO nas_assets (
                user_id, category, title, original_filename, stored_path, mime_type,
                file_size, status, analyzer, processor_config_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                category,
                title,
                original_filename,
                stored_path,
                mime_type,
                file_size,
                status,
                analyzer,
                processor_config_json,
            ),
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
             OR analyzer LIKE ? OR summary LIKE ? OR users.username LIKE ?
             OR EXISTS (
                 SELECT 1 FROM asset_ai_analyses
                 WHERE asset_ai_analyses.asset_id = nas_assets.id
                   AND (asset_ai_analyses.question LIKE ? OR asset_ai_analyses.answer LIKE ?)
             ))
            """
        )
        pattern = f"%{q}%"
        params.extend([pattern, pattern, pattern, pattern, pattern, pattern, pattern, pattern])

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


def upsert_line_source(
    *,
    source_id: str,
    source_type: str,
    display_name: str | None,
    owner_user_id: int,
    is_approved: bool = True,
) -> dict[str, Any]:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO line_sources (source_id, source_type, display_name, owner_user_id, is_approved)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET
                source_type = excluded.source_type,
                display_name = COALESCE(excluded.display_name, line_sources.display_name),
                updated_at = CURRENT_TIMESTAMP
            """,
            (source_id, source_type, display_name, owner_user_id, int(is_approved)),
        )
        row = conn.execute("SELECT * FROM line_sources WHERE source_id = ?", (source_id,)).fetchone()
    source = _row_to_dict(row)
    if source is None:
        raise RuntimeError("LINE source creation failed")
    return source


def get_line_source(source_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM line_sources WHERE source_id = ?", (source_id,)).fetchone()
    return _row_to_dict(row)


def list_line_sources() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT line_sources.*, users.username AS owner_username,
                   (SELECT COUNT(*) FROM line_documents
                    WHERE line_documents.line_source_id = line_sources.id) AS document_count,
                   (SELECT COUNT(*) FROM llm_calls
                    WHERE llm_calls.channel = 'LINE'
                      AND llm_calls.source_ref = line_sources.source_id
                      AND datetime(llm_calls.created_at) >= datetime('now', 'start of month')) AS monthly_call_count,
                   (SELECT COALESCE(SUM(llm_calls.total_tokens), 0) FROM llm_calls
                    WHERE llm_calls.channel = 'LINE'
                      AND llm_calls.source_ref = line_sources.source_id
                      AND datetime(llm_calls.created_at) >= datetime('now', 'start of month')) AS monthly_token_count
            FROM line_sources
            JOIN users ON users.id = line_sources.owner_user_id
            ORDER BY line_sources.is_approved DESC,
                     line_sources.display_name COLLATE NOCASE,
                     line_sources.source_id
            """
        ).fetchall()
    return [dict(row) for row in rows]


def update_line_source_policy(
    source_id: int,
    *,
    is_approved: bool,
    auto_pdf_summary: bool,
    rag_queries_enabled: bool,
    default_model_id: str,
    monthly_call_limit: int,
    monthly_token_limit: int,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE line_sources
            SET is_approved = ?, auto_pdf_summary = ?, rag_queries_enabled = ?,
                default_model_id = ?, monthly_call_limit = ?, monthly_token_limit = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND source_type = 'group'
            """,
            (
                int(is_approved),
                int(auto_pdf_summary),
                int(rag_queries_enabled),
                default_model_id,
                monthly_call_limit,
                monthly_token_limit,
                source_id,
            ),
        )
        row = conn.execute("SELECT * FROM line_sources WHERE id = ?", (source_id,)).fetchone()
    return _row_to_dict(row)


def get_line_source_month_usage(source_id: str) -> dict[str, int]:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS call_count, COALESCE(SUM(total_tokens), 0) AS token_count
            FROM llm_calls
            WHERE channel = 'LINE' AND source_ref = ?
              AND datetime(created_at) >= datetime('now', 'start of month')
            """,
            (source_id,),
        ).fetchone()
    return {"call_count": int(row["call_count"]), "token_count": int(row["token_count"])}


def create_line_document(
    *,
    line_source_id: int,
    line_message_id: str,
    line_event_id: str | None,
    sender_id: str | None,
    sender_name: str | None,
    asset_id: int,
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO line_documents (
                line_source_id, line_message_id, line_event_id, sender_id,
                sender_name, asset_id, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'processing')
            """,
            (line_source_id, line_message_id, line_event_id, sender_id, sender_name, asset_id),
        )
        row = conn.execute("SELECT * FROM line_documents WHERE id = ?", (cursor.lastrowid,)).fetchone()
    document = _row_to_dict(row)
    if document is None:
        raise RuntimeError("LINE document creation failed")
    return document


def get_line_document(line_message_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT line_documents.*, line_sources.source_id, line_sources.display_name,
                   nas_assets.title AS asset_title, nas_assets.original_filename
            FROM line_documents
            JOIN line_sources ON line_sources.id = line_documents.line_source_id
            JOIN nas_assets ON nas_assets.id = line_documents.asset_id
            WHERE line_documents.line_message_id = ?
            """,
            (line_message_id,),
        ).fetchone()
    return _row_to_dict(row)


def finish_line_document(document_id: int, *, status: str, summary: str | None, error_message: str | None) -> dict[str, Any]:
    with connect() as conn:
        previous = conn.execute(
            "SELECT status FROM line_documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        conn.execute(
            """
            UPDATE line_documents
            SET status = ?, summary = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, summary, error_message, document_id),
        )
        if status == "completed" and previous and previous["status"] != "completed":
            conn.execute(
                """
                UPDATE line_sources
                SET content_version = content_version + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = (SELECT line_source_id FROM line_documents WHERE id = ?)
                """,
                (document_id,),
            )
        row = conn.execute("SELECT * FROM line_documents WHERE id = ?", (document_id,)).fetchone()
    document = _row_to_dict(row)
    if document is None:
        raise RuntimeError("LINE document update failed")
    return document


def list_line_source_assets(line_source_id: int, limit: int = 20) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT nas_assets.*, line_documents.sender_name, line_documents.created_at AS line_received_at
            FROM line_documents
            JOIN nas_assets ON nas_assets.id = line_documents.asset_id
            WHERE line_documents.line_source_id = ?
              AND line_documents.status = 'completed'
              AND nas_assets.status = 'completed'
              AND nas_assets.chunk_count > 0
            ORDER BY datetime(line_documents.created_at) DESC, line_documents.id DESC
            LIMIT ?
            """,
            (line_source_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_exact_line_query_cache(
    line_source_id: int,
    content_version: int,
    model_id: str,
    normalized_query: str,
) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM line_query_cache
            WHERE line_source_id = ? AND content_version = ?
              AND model_id = ? AND normalized_query = ?
            """,
            (line_source_id, content_version, model_id, normalized_query),
        ).fetchone()
    return _row_to_dict(row)


def list_line_query_cache_candidates(
    line_source_id: int,
    content_version: int,
    model_id: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM line_query_cache
            WHERE line_source_id = ? AND content_version = ? AND model_id = ?
              AND query_embedding IS NOT NULL
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
            """,
            (line_source_id, content_version, model_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def mark_line_query_cache_hit(cache_id: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE line_query_cache
            SET hit_count = hit_count + 1, last_hit_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (cache_id,),
        )


def save_line_query_cache(
    *,
    line_source_id: int,
    content_version: int,
    user_id: int,
    model_id: str,
    query_text: str,
    normalized_query: str,
    query_embedding: bytes | None,
    embedding_model: str | None,
    answer: str,
    contexts_json: str,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO line_query_cache (
                line_source_id, content_version, user_id, model_id, query_text,
                normalized_query, query_embedding, embedding_model, answer, contexts_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(line_source_id, content_version, model_id, normalized_query) DO UPDATE SET
                user_id = excluded.user_id,
                query_text = excluded.query_text,
                query_embedding = excluded.query_embedding,
                embedding_model = excluded.embedding_model,
                answer = excluded.answer,
                contexts_json = excluded.contexts_json,
                created_at = CURRENT_TIMESTAMP
            """,
            (
                line_source_id,
                content_version,
                user_id,
                model_id,
                query_text,
                normalized_query,
                query_embedding,
                embedding_model,
                answer,
                contexts_json,
            ),
        )


def replace_document_chunks(asset_id: int, chunks: list[dict[str, Any]]) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM rag_query_cache WHERE asset_id = ?", (asset_id,))
        conn.execute("DELETE FROM asset_ai_analyses WHERE asset_id = ?", (asset_id,))
        conn.execute("DELETE FROM document_chunks WHERE asset_id = ?", (asset_id,))
        conn.executemany(
            """
            INSERT INTO document_chunks (
                asset_id, chunk_index, content, token_estimate, page_number,
                chunk_type, image_path, metadata_json, embedding, embedding_model
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    chunk.get("embedding"),
                    chunk.get("embedding_model"),
                )
                for chunk in chunks
            ],
        )


def save_asset_ai_analysis(
    *,
    asset_id: int,
    user_id: int,
    llm_call_id: int | None,
    model_id: str,
    provider: str,
    model_name: str,
    question: str,
    normalized_question: str,
    answer: str,
    access_mode: str | None,
    embedded: bool,
    chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO asset_ai_analyses (
                asset_id, user_id, llm_call_id, model_id, provider, model_name,
                question, normalized_question, answer, access_mode, embedding_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                user_id,
                llm_call_id,
                model_id,
                provider,
                model_name,
                question,
                normalized_question,
                answer,
                access_mode,
                "completed" if embedded else "pending",
            ),
        )
        created = cursor.rowcount > 0
        row = conn.execute(
            """
            SELECT * FROM asset_ai_analyses
            WHERE asset_id = ? AND model_id = ? AND normalized_question = ?
            """,
            (asset_id, model_id, normalized_question),
        ).fetchone()
        if row is None:
            raise RuntimeError("AI analysis persistence failed")

        if created:
            next_index_row = conn.execute(
                "SELECT COALESCE(MAX(chunk_index), -1) + 1 AS next_index FROM document_chunks WHERE asset_id = ?",
                (asset_id,),
            ).fetchone()
            next_index = int(next_index_row["next_index"])
            conn.executemany(
                """
                INSERT INTO document_chunks (
                    asset_id, chunk_index, content, token_estimate, page_number,
                    chunk_type, image_path, metadata_json, embedding, embedding_model
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        asset_id,
                        next_index + offset,
                        chunk["content"],
                        chunk.get("token_estimate", 0),
                        None,
                        "ai_analysis",
                        None,
                        chunk.get("metadata_json"),
                        chunk.get("embedding"),
                        chunk.get("embedding_model"),
                    )
                    for offset, chunk in enumerate(chunks)
                ],
            )
            conn.execute(
                """
                UPDATE nas_assets
                SET chunk_count = (SELECT COUNT(*) FROM document_chunks WHERE asset_id = ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (asset_id, asset_id),
            )
        chunk_count_row = conn.execute(
            "SELECT COUNT(*) AS total FROM document_chunks WHERE asset_id = ? AND chunk_type = 'ai_analysis'",
            (asset_id,),
        ).fetchone()
        asset_chunk_count_row = conn.execute(
            "SELECT COUNT(*) AS total FROM document_chunks WHERE asset_id = ?",
            (asset_id,),
        ).fetchone()
    return {
        "analysis": dict(row),
        "created": created,
        "analysis_chunk_count": int(chunk_count_row["total"]),
        "asset_chunk_count": int(asset_chunk_count_row["total"]),
    }


def get_asset_ai_analysis(asset_id: int, model_id: str, normalized_question: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM asset_ai_analyses
            WHERE asset_id = ? AND model_id = ? AND normalized_question = ?
            """,
            (asset_id, model_id, normalized_question),
        ).fetchone()
    return _row_to_dict(row)


def list_asset_ai_analyses(asset_id: int, limit: int = 20) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM asset_ai_analyses
            WHERE asset_id = ?
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
            """,
            (asset_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def list_document_chunks(asset_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, asset_id, chunk_index, content, token_estimate, page_number,
                   chunk_type, image_path, metadata_json, embedding, embedding_model, created_at
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
                   chunk_type, image_path, metadata_json, embedding, embedding_model, created_at
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


def list_chunks_missing_embedding(limit: int = 64) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT document_chunks.id, document_chunks.asset_id, document_chunks.chunk_index,
                   document_chunks.content, nas_assets.user_id
            FROM document_chunks
            JOIN nas_assets ON nas_assets.id = document_chunks.asset_id
            WHERE document_chunks.embedding IS NULL
            ORDER BY document_chunks.id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def update_chunk_embeddings(chunks: list[dict[str, Any]]) -> None:
    if not chunks:
        return
    with connect() as conn:
        conn.executemany(
            """
            UPDATE document_chunks
            SET embedding = ?, embedding_model = ?
            WHERE id = ?
            """,
            [
                (chunk["embedding"], chunk["embedding_model"], chunk["id"])
                for chunk in chunks
            ],
        )


def embedding_coverage() -> dict[str, int]:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN embedding IS NOT NULL THEN 1 ELSE 0 END) AS embedded
            FROM document_chunks
            """
        ).fetchone()
    return {"total": int(row["total"] or 0), "embedded": int(row["embedded"] or 0)}


def get_exact_rag_cache(asset_id: int, model_id: str, normalized_query: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM rag_query_cache
            WHERE asset_id = ? AND model_id = ? AND normalized_query = ?
            """,
            (asset_id, model_id, normalized_query),
        ).fetchone()
    return _row_to_dict(row)


def list_rag_cache_candidates(asset_id: int, model_id: str, limit: int = 200) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM rag_query_cache
            WHERE asset_id = ? AND model_id = ? AND query_embedding IS NOT NULL
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
            """,
            (asset_id, model_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def mark_rag_cache_hit(cache_id: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE rag_query_cache
            SET hit_count = hit_count + 1, last_hit_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (cache_id,),
        )


def save_rag_query_cache(
    *,
    asset_id: int,
    user_id: int,
    model_id: str,
    query_text: str,
    normalized_query: str,
    query_embedding: bytes | None,
    embedding_model: str | None,
    result_json: str,
    contexts_json: str,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO rag_query_cache (
                asset_id, user_id, model_id, query_text, normalized_query,
                query_embedding, embedding_model, result_json, contexts_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(asset_id, model_id, normalized_query) DO UPDATE SET
                user_id = excluded.user_id,
                query_text = excluded.query_text,
                query_embedding = excluded.query_embedding,
                embedding_model = excluded.embedding_model,
                result_json = excluded.result_json,
                contexts_json = excluded.contexts_json,
                created_at = CURRENT_TIMESTAMP
            """,
            (
                asset_id,
                user_id,
                model_id,
                query_text,
                normalized_query,
                query_embedding,
                embedding_model,
                result_json,
                contexts_json,
            ),
        )


def get_exact_llm_cache(user_id: int, model_id: str, normalized_prompt: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM llm_query_cache
            WHERE user_id = ? AND model_id = ? AND normalized_prompt = ?
            """,
            (user_id, model_id, normalized_prompt),
        ).fetchone()
    return _row_to_dict(row)


def list_llm_cache_candidates(user_id: int, model_id: str, limit: int = 200) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM llm_query_cache
            WHERE user_id = ? AND model_id = ? AND prompt_embedding IS NOT NULL
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
            """,
            (user_id, model_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def list_llm_prompt_history(user_id: int, model_id: str, limit: int = 200) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            WITH prompt_history AS (
                SELECT prompt_text AS prompt, created_at, hit_count, 1 AS cached
                FROM llm_query_cache
                WHERE user_id = ? AND model_id = ?
                UNION ALL
                SELECT prompt, created_at, 0 AS hit_count, 0 AS cached
                FROM llm_calls
                WHERE user_id = ? AND model_id = ? AND status = 'completed'
                  AND response IS NOT NULL AND channel IS NULL
            )
            SELECT prompt, MAX(created_at) AS created_at,
                   MAX(hit_count) AS hit_count, MAX(cached) AS cached
            FROM prompt_history
            GROUP BY prompt
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (user_id, model_id, user_id, model_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def list_llm_cache_seed_calls(user_id: int, model_id: str, limit: int = 100) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM llm_calls
            WHERE user_id = ? AND model_id = ? AND status = 'completed'
              AND response IS NOT NULL AND channel IS NULL
              AND access_mode NOT LIKE 'cache_%'
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
            """,
            (user_id, model_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def mark_llm_cache_hit(cache_id: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE llm_query_cache
            SET hit_count = hit_count + 1, last_hit_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (cache_id,),
        )


def save_llm_query_cache(
    *,
    user_id: int,
    model_id: str,
    prompt_text: str,
    normalized_prompt: str,
    prompt_embedding: bytes | None,
    embedding_model: str | None,
    result_json: str,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO llm_query_cache (
                user_id, model_id, prompt_text, normalized_prompt,
                prompt_embedding, embedding_model, result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, model_id, normalized_prompt) DO UPDATE SET
                prompt_text = excluded.prompt_text,
                prompt_embedding = COALESCE(excluded.prompt_embedding, llm_query_cache.prompt_embedding),
                embedding_model = COALESCE(excluded.embedding_model, llm_query_cache.embedding_model),
                result_json = excluded.result_json,
                created_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                model_id,
                prompt_text,
                normalized_prompt,
                prompt_embedding,
                embedding_model,
                result_json,
            ),
        )


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
    channel: str | None = None,
    external_caller: str | None = None,
    source_ref: str | None = None,
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO llm_calls (
                user_id, provider, model_name, model_id, prompt, response, status, access_mode,
                error_message, input_tokens, output_tokens, total_tokens, remaining_tokens,
                remaining_requests, remaining_balance, raw_usage_json, channel,
                external_caller, source_ref
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                channel,
                external_caller,
                source_ref,
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
               raw_usage_json, channel, external_caller, source_ref, llm_calls.created_at
        FROM llm_calls
        JOIN users ON users.id = llm_calls.user_id
        {where_sql}
        ORDER BY datetime(llm_calls.created_at) DESC, llm_calls.id DESC
        LIMIT 100
    """

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]
