import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"

MCP_CATALOG_TEMPLATES = (
    {
        "slug": "nas-demo", "name": "NAS Demo MCP", "transport": "streamable_http",
        "endpoint": "http://127.0.0.1:8000/mcp/nas", "auth_type": "none", "auth_env_var": None,
        "description": "AI Work 內建唯讀 NAS 示範工具，可查詢系統狀態、共享資料夾、示範檔案與近期活動。",
        "description_en": "Built-in read-only NAS demo tools for system status, shares, demo files, and recent activity.",
        "source_url": None, "is_enabled": True,
    },
    {
        "slug": "nas-excel", "name": "NAS Excel SQL", "transport": "streamable_http",
        "endpoint": "http://127.0.0.1:8000/mcp/excel", "auth_type": "bearer",
        "auth_env_var": "NAS_EXCEL_LOCAL_MCP_KEY",
        "description": "Ubuntu/NAS 內建試算表唯讀 MCP，可檢視、搜尋、統計及以 SELECT SQL 查詢使用者上傳的 XLSX、XLSM、CSV 與 TSV，不需安裝 Excel。",
        "description_en": "Built-in Ubuntu/NAS read-only spreadsheet MCP for inspecting, searching, profiling, and querying uploaded XLSX, XLSM, CSV, and TSV files with SELECT SQL. Microsoft Excel is not required.",
        "source_url": "https://openpyxl.readthedocs.io/en/stable/", "is_enabled": False,
    },
    {
        "slug": "gmail", "name": "Gmail Read-only", "transport": "streamable_http",
        "endpoint": "http://127.0.0.1:8000/mcp/gmail", "auth_type": "bearer", "auth_env_var": "GMAIL_LOCAL_MCP_KEY",
        "description": "AI Work 受保護的 Gmail 唯讀 MCP，透過正式 Gmail API 搜尋與讀取郵件、討論串及標籤。",
        "description_en": "Protected AI Work read-only Gmail MCP backed by the stable Gmail API for messages, threads, search, and labels.",
        "source_url": "https://developers.google.com/workspace/gmail/api/guides", "is_enabled": False,
    },
    {
        "slug": "google-drive", "name": "Google Drive Read-only", "transport": "streamable_http",
        "endpoint": "http://127.0.0.1:8000/mcp/google-drive", "auth_type": "bearer", "auth_env_var": "GOOGLE_DRIVE_LOCAL_MCP_KEY",
        "description": "AI Work 受保護的 Google Drive 唯讀 MCP，透過正式 Drive API 搜尋、列出及讀取檔案。",
        "description_en": "Protected AI Work read-only Google Drive MCP backed by the stable Drive API for file listing, search, metadata, and text reads.",
        "source_url": "https://developers.google.com/drive/api/guides/about-sdk", "is_enabled": False,
    },
    {
        "slug": "google-docs", "name": "Google Docs", "transport": "streamable_http",
        "endpoint": "https://docsmcp.googleapis.com/mcp/v1", "auth_type": "oauth2", "auth_env_var": "GOOGLE_DOCS_MCP_TOKEN",
        "description": "Google Docs 官方遠端 MCP（Developer Preview），用於企業文件讀取與編輯流程。",
        "description_en": "Official Google Docs remote MCP (Developer Preview) for document reading and editing workflows.",
        "source_url": "https://developers.google.com/workspace/guides/configure-mcp-servers", "is_enabled": False,
    },
    {
        "slug": "google-sheets", "name": "Google Sheets", "transport": "streamable_http",
        "endpoint": "https://sheetsmcp.googleapis.com/mcp/v1", "auth_type": "oauth2", "auth_env_var": "GOOGLE_SHEETS_MCP_TOKEN",
        "description": "Google Sheets 官方遠端 MCP（Developer Preview），用於試算表查詢與更新。",
        "description_en": "Official Google Sheets remote MCP (Developer Preview) for spreadsheet queries and updates.",
        "source_url": "https://developers.google.com/workspace/guides/configure-mcp-servers", "is_enabled": False,
    },
    {
        "slug": "microsoft-365-excel", "name": "Microsoft 365 Excel Online", "transport": "streamable_http",
        "endpoint": None, "auth_type": "oauth2", "auth_env_var": "MICROSOFT_365_EXCEL_MCP_TOKEN",
        "description": "供公司自架 Microsoft Graph 唯讀 Adapter 使用，查詢 OneDrive／SharePoint 內的 XLSX 活頁簿；需 Files.Read 授權，不需在 Ubuntu 安裝 Excel。",
        "description_en": "For a company-hosted read-only Microsoft Graph adapter that queries XLSX workbooks in OneDrive or SharePoint with Files.Read. No Excel installation is required on Ubuntu.",
        "source_url": "https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0", "is_enabled": False,
    },
    {
        "slug": "microsoft-markitdown", "name": "Microsoft MarkItDown", "transport": "stdio",
        "endpoint": None, "auth_type": "none", "auth_env_var": None,
        "description": "Microsoft 開源文件轉換 MCP，可將 Excel 與 Office 文件轉為 Markdown 供 LLM/RAG 使用；預設停用，僅應在受信任的本機檔案環境啟用。",
        "description_en": "Microsoft open-source conversion MCP for turning Excel and Office files into Markdown for LLM/RAG use. Disabled by default and intended only for trusted local files.",
        "source_url": "https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp", "is_enabled": False,
    },
    {
        "slug": "google-slides", "name": "Google Slides", "transport": "streamable_http",
        "endpoint": "https://slidesmcp.googleapis.com/mcp/v1", "auth_type": "oauth2", "auth_env_var": "GOOGLE_SLIDES_MCP_TOKEN",
        "description": "Google Slides 官方遠端 MCP（Developer Preview），用於簡報內容讀取與製作。",
        "description_en": "Official Google Slides remote MCP (Developer Preview) for presentation access and authoring.",
        "source_url": "https://developers.google.com/workspace/guides/configure-mcp-servers", "is_enabled": False,
    },
    {
        "slug": "google-calendar", "name": "Google Calendar", "transport": "streamable_http",
        "endpoint": "https://calendarmcp.googleapis.com/mcp/v1", "auth_type": "oauth2", "auth_env_var": "GOOGLE_CALENDAR_MCP_TOKEN",
        "description": "Google Calendar 官方遠端 MCP（Developer Preview），支援行事曆搜尋、建立與更新事件。",
        "description_en": "Official Google Calendar remote MCP (Developer Preview) for calendar search and event management.",
        "source_url": "https://developers.google.com/workspace/calendar/api/guides/configure-mcp-server", "is_enabled": False,
    },
    {
        "slug": "google-chat", "name": "Google Chat", "transport": "streamable_http",
        "endpoint": "https://chatmcp.googleapis.com/mcp/v1", "auth_type": "oauth2", "auth_env_var": "GOOGLE_CHAT_MCP_TOKEN",
        "description": "Google Chat 官方遠端 MCP（Developer Preview），用於企業訊息與空間協作。",
        "description_en": "Official Google Chat remote MCP (Developer Preview) for company messaging and spaces.",
        "source_url": "https://developers.google.com/workspace/guides/configure-mcp-servers", "is_enabled": False,
    },
    {
        "slug": "google-people", "name": "Google People", "transport": "streamable_http",
        "endpoint": "https://people.googleapis.com/mcp/v1", "auth_type": "oauth2", "auth_env_var": "GOOGLE_PEOPLE_MCP_TOKEN",
        "description": "Google People 官方遠端 MCP（Developer Preview），用於聯絡人與組織人員資料。",
        "description_en": "Official Google People remote MCP (Developer Preview) for contacts and people data.",
        "source_url": "https://developers.google.com/workspace/guides/configure-mcp-servers", "is_enabled": False,
    },
    {
        "slug": "slack", "name": "Slack", "transport": "streamable_http",
        "endpoint": None, "auth_type": "managed", "auth_env_var": None,
        "description": "Slack 官方 MCP 採合作夥伴與企業 OAuth 安裝流程，目前沒有公開通用 Endpoint；請由 Slack 管理介面完成連接。",
        "description_en": "Slack MCP uses partner and enterprise OAuth installation. No universal public endpoint is currently published.",
        "source_url": "https://slack.com/help/articles/48855576908307-Guide-to-the-Slack-MCP-server", "is_enabled": False,
    },
    {
        "slug": "github", "name": "GitHub", "transport": "streamable_http",
        "endpoint": "https://api.githubcopilot.com/mcp/", "auth_type": "oauth2", "auth_env_var": "GITHUB_MCP_TOKEN",
        "description": "GitHub 官方遠端 MCP，可查詢程式碼、Issue、Pull Request 與儲存庫資訊。",
        "description_en": "Official GitHub remote MCP for code, issues, pull requests, and repository information.",
        "source_url": "https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp-in-your-ide/extend-copilot-chat-with-mcp", "is_enabled": False,
    },
    {
        "slug": "notion", "name": "Notion", "transport": "streamable_http",
        "endpoint": "https://mcp.notion.com/mcp", "auth_type": "oauth2", "auth_env_var": "NOTION_MCP_TOKEN",
        "description": "Notion 遠端 MCP，用於搜尋與處理工作區頁面、資料庫及企業知識。",
        "description_en": "Notion remote MCP for workspace pages, databases, search, and company knowledge.",
        "source_url": "https://developers.notion.com/docs/mcp", "is_enabled": False,
    },
    {
        "slug": "stripe", "name": "Stripe", "transport": "streamable_http",
        "endpoint": "https://mcp.stripe.com", "auth_type": "bearer", "auth_env_var": "STRIPE_MCP_TOKEN",
        "description": "Stripe 遠端 MCP，用於受控查詢付款、客戶、訂閱與帳務資料。",
        "description_en": "Stripe remote MCP for controlled access to payments, customers, subscriptions, and billing data.",
        "source_url": "https://docs.stripe.com/mcp", "is_enabled": False,
    },
    {
        "slug": "atlassian", "name": "Atlassian", "transport": "streamable_http",
        "endpoint": "https://mcp.atlassian.com/v2/mcp", "auth_type": "oauth2", "auth_env_var": "ATLASSIAN_MCP_TOKEN",
        "description": "Atlassian 官方遠端 MCP v2，可連接 Jira、Confluence、Bitbucket 與 Loom。",
        "description_en": "Official Atlassian remote MCP v2 for Jira, Confluence, Bitbucket, and Loom.",
        "source_url": "https://support.atlassian.com/atlassian-ai-gateway/docs/get-started-with-the-atlassian-remote-mcp-server/", "is_enabled": False,
    },
    {
        "slug": "xero", "name": "Xero Accounting", "transport": "stdio",
        "endpoint": None, "auth_type": "bearer", "auth_env_var": "XERO_CLIENT_BEARER_TOKEN",
        "description": "Xero 官方開源 MCP，支援會計科目、聯絡人、發票、付款、銀行交易、損益表、資產負債表與試算表；預設停用，需先完成 Xero 授權。",
        "description_en": "Official open-source Xero MCP for accounts, contacts, invoices, payments, bank transactions, profit and loss, balance sheets, and trial balances. Disabled until Xero authorization is configured.",
        "source_url": "https://github.com/XeroAPI/xero-mcp-server", "is_enabled": False,
    },
    {
        "slug": "odoo", "name": "Odoo Accounting", "transport": "streamable_http",
        "endpoint": None, "auth_type": "custom", "auth_env_var": "ODOO_MCP_TOKEN",
        "description": "連接公司自行部署的 Odoo MCP，提供唯讀財務、發票、應收應付、總帳、銷售、庫存與營運查詢。",
        "description_en": "Connect a company-hosted Odoo MCP for read-only finance, invoices, receivables, payables, ledger, sales, inventory, and operations queries.",
        "source_url": "https://www.odoo.com/documentation/19.0/developer/reference/external_api.html", "is_enabled": False,
    },
    {
        "slug": "quickbooks", "name": "QuickBooks Online", "transport": "streamable_http",
        "endpoint": None, "auth_type": "oauth2", "auth_env_var": "QUICKBOOKS_MCP_TOKEN",
        "description": "供公司自架 QuickBooks MCP Adapter 使用，以 OAuth 2.0 受控查詢會計科目、客戶、供應商、發票、費用與財務報表。",
        "description_en": "For a company-hosted QuickBooks MCP adapter using OAuth 2.0 to query accounts, customers, vendors, invoices, expenses, and financial reports under company policy.",
        "source_url": "https://developer.intuit.com/app/developer/qbo/docs/get-started", "is_enabled": False,
    },
    {
        "slug": "netsuite", "name": "Oracle NetSuite", "transport": "streamable_http",
        "endpoint": None, "auth_type": "oauth2", "auth_env_var": "NETSUITE_MCP_TOKEN",
        "description": "供公司自架 NetSuite MCP Adapter 使用，透過 SuiteTalk REST 與 OAuth 2.0 查詢財務、訂單、庫存及 ERP 資料。",
        "description_en": "For a company-hosted NetSuite MCP adapter using SuiteTalk REST and OAuth 2.0 to query finance, orders, inventory, and ERP data.",
        "source_url": "https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html", "is_enabled": False,
    },
    {
        "slug": "monday", "name": "Monday.com", "transport": "streamable_http",
        "endpoint": "https://mcp.monday.com/mcp", "auth_type": "bearer", "auth_env_var": "MONDAY_MCP_TOKEN",
        "headers_json": '{"Api-Version":"2026-07"}',
        "description": "Monday.com 官方 Hosted MCP，以 Bearer Token 連接工作區，供公司 LLM 查詢已授權的工作管理資料。",
        "description_en": "Official Monday.com Hosted MCP using a bearer token for authorized work-management data.",
        "source_url": "https://developer.monday.com/api-reference/docs/integrate-with-monday-mcp", "is_enabled": False,
    },
    {
        "slug": "linear", "name": "Linear", "transport": "streamable_http",
        "endpoint": "https://mcp.linear.app/mcp/readonly", "auth_type": "bearer", "auth_env_var": "LINEAR_MCP_TOKEN",
        "description": "Linear 官方唯讀遠端 MCP，用於查詢 Issue、專案、里程碑與產品規劃資料。",
        "description_en": "Official read-only Linear remote MCP for issues, projects, milestones, and product planning.",
        "source_url": "https://linear.app/docs/mcp", "is_enabled": False,
    },
    {
        "slug": "cloudflare", "name": "Cloudflare", "transport": "streamable_http",
        "endpoint": "https://mcp.cloudflare.com/mcp", "auth_type": "oauth2", "auth_env_var": "CLOUDFLARE_MCP_TOKEN",
        "description": "Cloudflare 官方 API MCP，可管理 DNS、Workers、R2、Zero Trust 與其他平台服務。",
        "description_en": "Official Cloudflare API MCP for DNS, Workers, R2, Zero Trust, and platform services.",
        "source_url": "https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/", "is_enabled": False,
    },
    {
        "slug": "cloudflare-docs", "name": "Cloudflare Docs", "transport": "streamable_http",
        "endpoint": "https://docs.mcp.cloudflare.com/mcp", "auth_type": "none", "auth_env_var": None,
        "description": "Cloudflare 官方文件 MCP，用於查詢最新產品文件與技術參考。",
        "description_en": "Official Cloudflare documentation MCP for current product and technical references.",
        "source_url": "https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/", "is_enabled": False,
    },
    {
        "slug": "vercel", "name": "Vercel", "transport": "streamable_http",
        "endpoint": "https://mcp.vercel.com", "auth_type": "oauth2", "auth_env_var": "VERCEL_MCP_TOKEN",
        "description": "Vercel 官方遠端 MCP（Beta），用於專案、部署、日誌及文件查詢。",
        "description_en": "Official Vercel remote MCP (Beta) for projects, deployments, logs, and documentation.",
        "source_url": "https://vercel.com/docs/agent-resources/vercel-mcp", "is_enabled": False,
    },
    {
        "slug": "supabase", "name": "Supabase", "transport": "streamable_http",
        "endpoint": "https://mcp.supabase.com/mcp?read_only=true", "auth_type": "oauth2", "auth_env_var": "SUPABASE_ACCESS_TOKEN",
        "description": "Supabase 官方遠端 MCP，預設使用唯讀模式查詢資料庫、文件、日誌與專案資訊。",
        "description_en": "Official Supabase remote MCP, defaulting to read-only access for database, docs, logs, and project data.",
        "source_url": "https://supabase.com/docs/guides/ai-tools/mcp", "is_enabled": False,
    },
    {
        "slug": "context7", "name": "Context7", "transport": "streamable_http",
        "endpoint": "https://mcp.context7.com/mcp", "auth_type": "none", "auth_env_var": None,
        "description": "Context7 遠端 MCP，用於查詢最新程式庫與框架文件。",
        "description_en": "Context7 remote MCP for up-to-date library and framework documentation.",
        "source_url": "https://context7.com/docs", "is_enabled": False,
    },
    {
        "slug": "nas-filesystem", "name": "NAS Filesystem", "transport": "stdio",
        "endpoint": None, "auth_type": "none", "auth_env_var": None,
        "description": "以受控 stdio 工具讀取 NAS 檔案、目錄與企業文件。",
        "description_en": "Access NAS files, directories, and company documents through controlled stdio tools.",
        "source_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem", "is_enabled": False,
    },
    {
        "slug": "postgresql", "name": "PostgreSQL", "transport": "stdio",
        "endpoint": None, "auth_type": "custom", "auth_env_var": None,
        "description": "依資料庫權限執行唯讀查詢與結構探索。",
        "description_en": "Run permission-scoped read-only queries and schema discovery.",
        "source_url": "https://github.com/modelcontextprotocol/servers-archived/tree/main/src/postgres", "is_enabled": False,
    },
)


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
        _ensure_column(conn, "nas_assets", "source_type", "TEXT")
        _ensure_column(conn, "nas_assets", "source_url", "TEXT")
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
            CREATE TABLE IF NOT EXISTS wiki_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                slug TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                body TEXT NOT NULL,
                keywords_json TEXT NOT NULL DEFAULT '[]',
                embedding BLOB,
                embedding_model TEXT,
                source_count INTEGER NOT NULL DEFAULT 0,
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(owner_user_id, slug),
                FOREIGN KEY(owner_user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS wiki_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER NOT NULL,
                asset_id INTEGER NOT NULL,
                chunk_id INTEGER NOT NULL,
                citation_key TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                page_number INTEGER,
                chunk_type TEXT NOT NULL,
                image_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(page_id, asset_id, chunk_id),
                FOREIGN KEY(page_id) REFERENCES wiki_pages(id),
                FOREIGN KEY(asset_id) REFERENCES nas_assets(id),
                FOREIGN KEY(chunk_id) REFERENCES document_chunks(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS wiki_page_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                summary TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(page_id, version),
                FOREIGN KEY(page_id) REFERENCES wiki_pages(id)
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_by INTEGER,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(updated_by) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mcp_servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                description_en TEXT,
                transport TEXT NOT NULL DEFAULT 'streamable_http',
                endpoint TEXT,
                source_url TEXT,
                auth_type TEXT NOT NULL DEFAULT 'none',
                auth_env_var TEXT,
                headers_json TEXT,
                is_enabled INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'unconfigured',
                protocol_version TEXT,
                tools_json TEXT,
                tool_count INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                last_checked_at TEXT,
                created_by INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mcp_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                tool_name TEXT,
                input_json TEXT,
                output_json TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(server_id) REFERENCES mcp_servers(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
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
        _ensure_column(conn, "mcp_servers", "source_url", "TEXT")
        _ensure_column(conn, "mcp_servers", "auth_type", "TEXT NOT NULL DEFAULT 'none'")
        _ensure_column(conn, "mcp_servers", "headers_json", "TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meetings_user_id ON meetings(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_calls_user_id ON llm_calls(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_calls_created_at ON llm_calls(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nas_assets_user_id ON nas_assets(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nas_assets_created_at ON nas_assets(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nas_assets_source_type ON nas_assets(source_type, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_asset_id ON document_chunks(asset_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_wiki_pages_owner ON wiki_pages(owner_user_id, updated_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_wiki_sources_page ON wiki_sources(page_id, asset_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_wiki_sources_asset ON wiki_sources(asset_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rag_query_cache_asset_model ON rag_query_cache(asset_id, model_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_query_cache_user_model ON llm_query_cache(user_id, model_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_asset_ai_analyses_asset ON asset_ai_analyses(asset_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_line_documents_source ON line_documents(line_source_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_line_query_cache_source ON line_query_cache(line_source_id, content_version, model_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_custom_models_type ON custom_models(model_type, is_enabled, validation_status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mcp_servers_status ON mcp_servers(status, is_enabled)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mcp_audit_server ON mcp_audit_logs(server_id, created_at)")


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
        admin = conn.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
        for template in MCP_CATALOG_TEMPLATES:
            conn.execute(
                """
                INSERT OR IGNORE INTO mcp_servers (
                    slug, name, description, description_en, transport, endpoint,
                    source_url, auth_type, auth_env_var, headers_json, is_enabled, status, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    template["slug"], template["name"], template["description"], template["description_en"],
                    template["transport"], template["endpoint"], template["source_url"], template["auth_type"],
                    template["auth_env_var"], template.get("headers_json"), int(template["is_enabled"]),
                    "unchecked" if template["endpoint"] else "unconfigured", admin["id"] if admin else None,
                ),
            )
            conn.execute(
                """
                UPDATE mcp_servers
                SET endpoint = COALESCE(endpoint, ?),
                    source_url = COALESCE(source_url, ?),
                    auth_type = CASE WHEN auth_type = 'none' THEN ? ELSE auth_type END,
                    auth_env_var = COALESCE(auth_env_var, ?),
                    headers_json = COALESCE(headers_json, ?),
                    status = CASE
                        WHEN endpoint IS NULL AND ? IS NOT NULL THEN 'unchecked'
                        ELSE status
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE slug = ?
                """,
                (
                    template["endpoint"], template["source_url"], template["auth_type"],
                    template["auth_env_var"], template.get("headers_json"), template["endpoint"], template["slug"],
                ),
            )
        conn.execute(
            """
            UPDATE mcp_servers
            SET endpoint = 'https://mcp.linear.app/mcp/readonly',
                auth_type = 'bearer',
                status = 'unchecked',
                protocol_version = NULL,
                tools_json = NULL,
                tool_count = 0,
                last_error = NULL,
                last_checked_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = 'linear' AND endpoint = 'https://mcp.linear.app/mcp'
            """
        )
        conn.execute(
            """
            UPDATE mcp_servers
            SET name = 'Google Drive Read-only',
                description = 'AI Work 受保護的 Google Drive 唯讀 MCP，透過正式 Drive API 搜尋、列出及讀取檔案。',
                description_en = 'Protected AI Work read-only Google Drive MCP backed by the stable Drive API for file listing, search, metadata, and text reads.',
                endpoint = 'http://127.0.0.1:8000/mcp/google-drive',
                source_url = 'https://developers.google.com/drive/api/guides/about-sdk',
                auth_type = 'bearer',
                auth_env_var = 'GOOGLE_DRIVE_LOCAL_MCP_KEY',
                status = 'unchecked',
                protocol_version = NULL,
                tools_json = NULL,
                tool_count = 0,
                last_error = NULL,
                last_checked_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = 'google-drive'
              AND endpoint = 'https://drivemcp.googleapis.com/mcp/v1'
            """
        )
        conn.execute(
            """
            UPDATE mcp_servers
            SET name = 'Gmail Read-only',
                description = 'AI Work 受保護的 Gmail 唯讀 MCP，透過正式 Gmail API 搜尋與讀取郵件、討論串及標籤。',
                description_en = 'Protected AI Work read-only Gmail MCP backed by the stable Gmail API for messages, threads, search, and labels.',
                endpoint = 'http://127.0.0.1:8000/mcp/gmail',
                source_url = 'https://developers.google.com/workspace/gmail/api/guides',
                auth_type = 'bearer',
                auth_env_var = 'GMAIL_LOCAL_MCP_KEY',
                status = 'unchecked',
                protocol_version = NULL,
                tools_json = NULL,
                tool_count = 0,
                last_error = NULL,
                last_checked_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = 'gmail'
              AND endpoint = 'https://gmailmcp.googleapis.com/mcp/v1'
            """
        )
        conn.execute(
            """
            UPDATE mcp_servers
            SET description = 'Ubuntu/NAS 內建試算表唯讀 MCP，可檢視、搜尋、統計及以 SELECT SQL 查詢使用者上傳的 XLSX、XLSM、CSV 與 TSV，不需安裝 Excel。',
                description_en = 'Built-in Ubuntu/NAS read-only spreadsheet MCP for inspecting, searching, profiling, and querying uploaded XLSX, XLSM, CSV, and TSV files with SELECT SQL. Microsoft Excel is not required.',
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = 'nas-excel'
              AND description = 'Ubuntu/NAS 內建 Excel 唯讀 MCP，可檢視、搜尋、統計及以 SELECT SQL 查詢使用者上傳的 XLSX/XLSM，不需安裝 Excel。'
            """
        )
        conn.execute(
            """
            UPDATE mcp_servers
            SET description = 'Linear 官方唯讀遠端 MCP，用於查詢 Issue、專案、里程碑與產品規劃資料。',
                description_en = 'Official read-only Linear remote MCP for issues, projects, milestones, and product planning.',
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = 'linear'
              AND endpoint = 'https://mcp.linear.app/mcp/readonly'
              AND description = 'Linear 官方遠端 MCP，用於 Issue、專案、里程碑與產品規劃協作。'
            """
        )
        conn.execute(
            """
            UPDATE mcp_servers
            SET name = 'Odoo Accounting',
                description = '連接公司自行部署的 Odoo MCP，提供唯讀財務、發票、應收應付、總帳、銷售、庫存與營運查詢。',
                description_en = 'Connect a company-hosted Odoo MCP for read-only finance, invoices, receivables, payables, ledger, sales, inventory, and operations queries.',
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = 'odoo'
              AND name = 'Odoo'
              AND description IN (
                  '連接公司自行部署的 Odoo MCP，提供財務、銷售、庫存與營運工具。',
                  '連接 Odoo ERP 的財務、銷售、庫存與營運工具。'
              )
            """
        )


def get_user_by_username(username: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def get_system_setting(key: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT system_settings.key, system_settings.value, system_settings.updated_by,
                   system_settings.updated_at, users.username AS updated_by_username
            FROM system_settings
            LEFT JOIN users ON users.id = system_settings.updated_by
            WHERE system_settings.key = ?
            """,
            (key,),
        ).fetchone()
    return _row_to_dict(row)


def set_system_setting(key: str, value: str, updated_by: int | None) -> dict[str, Any]:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO system_settings (key, value, updated_by)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_by = excluded.updated_by,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, value, updated_by),
        )
    setting = get_system_setting(key)
    if setting is None:
        raise RuntimeError("System setting update failed")
    return setting


def list_mcp_servers() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT mcp_servers.*, users.username AS created_by_username
            FROM mcp_servers
            LEFT JOIN users ON users.id = mcp_servers.created_by
            ORDER BY CASE status
                WHEN 'connected' THEN 0
                WHEN 'failed' THEN 1
                WHEN 'unchecked' THEN 2
                ELSE 3
            END, name COLLATE NOCASE
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_mcp_server(server_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM mcp_servers WHERE id = ?", (server_id,)).fetchone()
    return _row_to_dict(row)


def create_mcp_server(values: dict[str, Any]) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mcp_servers (
                slug, name, description, description_en, transport, endpoint,
                source_url, auth_type, auth_env_var, is_enabled, status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                values["slug"], values["name"], values.get("description"),
                values.get("description_en"), values["transport"], values.get("endpoint"),
                values.get("source_url"), values.get("auth_type", "none"), values.get("auth_env_var"),
                int(bool(values.get("is_enabled"))),
                "unchecked" if values.get("endpoint") else "unconfigured", values.get("created_by"),
            ),
        )
        row = conn.execute("SELECT * FROM mcp_servers WHERE id = ?", (cursor.lastrowid,)).fetchone()
    result = _row_to_dict(row)
    if result is None:
        raise RuntimeError("MCP server creation failed")
    return result


def update_mcp_server(server_id: int, values: dict[str, Any]) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE mcp_servers
            SET slug = ?, name = ?, description = ?, description_en = ?, transport = ?,
                endpoint = ?, source_url = ?, auth_type = ?, auth_env_var = ?, is_enabled = ?,
                status = CASE
                    WHEN COALESCE(?, '') = '' THEN 'unconfigured'
                    WHEN endpoint IS NOT ? OR transport IS NOT ? OR auth_env_var IS NOT ? THEN 'unchecked'
                    ELSE status
                END,
                tool_count = CASE
                    WHEN endpoint IS NOT ? OR transport IS NOT ? OR auth_env_var IS NOT ? THEN 0
                    ELSE tool_count
                END,
                tools_json = CASE
                    WHEN endpoint IS NOT ? OR transport IS NOT ? OR auth_env_var IS NOT ? THEN NULL
                    ELSE tools_json
                END,
                last_error = CASE
                    WHEN endpoint IS NOT ? OR transport IS NOT ? OR auth_env_var IS NOT ? THEN NULL
                    ELSE last_error
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                values["slug"], values["name"], values.get("description"), values.get("description_en"),
                values["transport"], values.get("endpoint"), values.get("source_url"),
                values.get("auth_type", "none"), values.get("auth_env_var"),
                int(bool(values.get("is_enabled"))), values.get("endpoint"),
                values.get("endpoint"), values["transport"], values.get("auth_env_var"),
                values.get("endpoint"), values["transport"], values.get("auth_env_var"),
                values.get("endpoint"), values["transport"], values.get("auth_env_var"),
                values.get("endpoint"), values["transport"], values.get("auth_env_var"),
                server_id,
            ),
        )
        row = conn.execute("SELECT * FROM mcp_servers WHERE id = ?", (server_id,)).fetchone()
    return _row_to_dict(row)


def update_mcp_server_sync(
    server_id: int,
    *,
    status: str,
    protocol_version: str | None,
    tools_json: str | None,
    tool_count: int,
    last_error: str | None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE mcp_servers
            SET status = ?, protocol_version = COALESCE(?, protocol_version),
                tools_json = ?, tool_count = ?, last_error = ?,
                last_checked_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, protocol_version, tools_json, tool_count, last_error, server_id),
        )
        row = conn.execute("SELECT * FROM mcp_servers WHERE id = ?", (server_id,)).fetchone()
    return _row_to_dict(row)


def delete_mcp_server(server_id: int) -> bool:
    with connect() as conn:
        conn.execute("DELETE FROM mcp_audit_logs WHERE server_id = ?", (server_id,))
        cursor = conn.execute("DELETE FROM mcp_servers WHERE id = ?", (server_id,))
    return cursor.rowcount > 0


def create_mcp_audit_log(
    *,
    server_id: int,
    user_id: int,
    action: str,
    status: str,
    tool_name: str | None = None,
    input_json: str | None = None,
    output_json: str | None = None,
    error_message: str | None = None,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO mcp_audit_logs (
                server_id, user_id, action, status, tool_name,
                input_json, output_json, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                server_id, user_id, action, status, tool_name,
                input_json, output_json, error_message,
            ),
        )


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
    translation_model_id: str | None = None,
    translation_provider: str | None = None,
    translation_model: str | None = None,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE meetings
            SET translation_status = ?, translation = COALESCE(?, translation),
                translation_error = ?,
                translation_metadata_json = COALESCE(?, translation_metadata_json),
                translation_model_id = COALESCE(?, translation_model_id),
                translation_provider = COALESCE(?, translation_provider),
                translation_model = COALESCE(?, translation_model),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                translation_status,
                translation,
                translation_error,
                translation_metadata_json,
                translation_model_id,
                translation_provider,
                translation_model,
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


def update_meeting_asr_selection(
    meeting_id: int,
    *,
    model_id: str,
    provider: str,
    model_name: str,
    engine: str,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE meetings
            SET asr_model_id = ?, asr_provider = ?, asr_model = ?, asr_engine = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (model_id, provider, model_name, engine, meeting_id),
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


def get_meeting_by_nas_asset_id(asset_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM meetings WHERE nas_asset_id = ? ORDER BY id DESC LIMIT 1",
            (asset_id,),
        ).fetchone()
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
    source_type: str | None = None,
    source_url: str | None = None,
) -> dict[str, Any]:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO nas_assets (
                user_id, category, title, original_filename, stored_path, mime_type,
                file_size, status, analyzer, processor_config_json, source_type, source_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                source_type,
                source_url,
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


def update_nas_asset_processor_config(
    asset_id: int,
    *,
    analyzer: str,
    processor_config_json: str,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE nas_assets
            SET analyzer = ?, processor_config_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (analyzer, processor_config_json, asset_id),
        )
        row = conn.execute("SELECT * FROM nas_assets WHERE id = ?", (asset_id,)).fetchone()
    return _row_to_dict(row)


def finalize_network_asset(
    asset_id: int,
    *,
    title: str,
    original_filename: str,
    stored_path: str,
    mime_type: str | None,
    file_size: int,
    analyzer: str,
    processor_config_json: str,
) -> dict[str, Any] | None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE nas_assets
            SET title = ?,
                original_filename = ?,
                stored_path = ?,
                mime_type = ?,
                file_size = ?,
                status = 'processing',
                analyzer = ?,
                summary = 'YouTube 內容已保存至 NAS，正在進入媒體分析流程。',
                error_message = NULL,
                processor_config_json = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                title,
                original_filename,
                stored_path,
                mime_type,
                file_size,
                analyzer,
                processor_config_json,
                asset_id,
            ),
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


def list_pending_media_jobs() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT 'meeting' AS job_type, meetings.id AS record_id
            FROM meetings
            WHERE meetings.status = 'processing'
            UNION ALL
            SELECT 'asset' AS job_type, nas_assets.id AS record_id
            FROM nas_assets
            WHERE nas_assets.status = 'processing'
              AND nas_assets.category IN ('audio', 'video')
              AND NOT EXISTS (
                  SELECT 1 FROM meetings WHERE meetings.nas_asset_id = nas_assets.id
              )
            ORDER BY record_id
            """
        ).fetchall()
    return [dict(row) for row in rows]


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
        SELECT nas_assets.*, users.username AS owner_username, users.role AS owner_role,
               CASE WHEN nas_assets.category = 'audio' THEN (
                   SELECT substr(document_chunks.content, 1, 360)
                   FROM document_chunks
                   WHERE document_chunks.asset_id = nas_assets.id
                     AND document_chunks.chunk_type = 'audio_transcript'
                   ORDER BY document_chunks.chunk_index ASC
                   LIMIT 1
               ) END AS transcript_preview
        FROM nas_assets
        JOIN users ON users.id = nas_assets.user_id
        {where_sql}
        ORDER BY datetime(nas_assets.created_at) DESC, nas_assets.id DESC
        LIMIT 100
    """

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def list_network_assets(*, user_id: int, role: str) -> list[dict[str, Any]]:
    params: list[Any] = []
    ownership_sql = ""
    if role != "admin":
        ownership_sql = "AND nas_assets.user_id = ?"
        params.append(user_id)
    with connect() as conn:
        rows = conn.execute(
            f"""
            SELECT nas_assets.*, users.username AS owner_username
            FROM nas_assets
            JOIN users ON users.id = nas_assets.user_id
            WHERE nas_assets.source_type = 'youtube'
            {ownership_sql}
            ORDER BY datetime(nas_assets.created_at) DESC, nas_assets.id DESC
            LIMIT 50
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def list_pending_network_assets() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM nas_assets
            WHERE source_type = 'youtube' AND status = 'downloading'
            ORDER BY id
            """
        ).fetchall()
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


def get_wiki_page_by_owner_slug(owner_user_id: int, slug: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM wiki_pages WHERE owner_user_id = ? AND slug = ?",
            (owner_user_id, slug),
        ).fetchone()
    return _row_to_dict(row)


def list_wiki_asset_ids(page_id: int) -> list[int]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT asset_id FROM wiki_sources WHERE page_id = ? ORDER BY asset_id",
            (page_id,),
        ).fetchall()
    return [int(row["asset_id"]) for row in rows]


def save_wiki_page(
    *,
    owner_user_id: int,
    slug: str,
    title: str,
    summary: str,
    body: str,
    keywords_json: str,
    embedding: bytes | None,
    embedding_model: str | None,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    with connect() as conn:
        existing = conn.execute(
            "SELECT * FROM wiki_pages WHERE owner_user_id = ? AND slug = ?",
            (owner_user_id, slug),
        ).fetchone()
        changed = existing is None or existing["summary"] != summary or existing["body"] != body
        if existing is None:
            cursor = conn.execute(
                """
                INSERT INTO wiki_pages (
                    owner_user_id, slug, title, summary, body, keywords_json,
                    embedding, embedding_model, source_count, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    owner_user_id, slug, title, summary, body, keywords_json,
                    embedding, embedding_model, len({source["asset_id"] for source in sources}),
                ),
            )
            page_id = int(cursor.lastrowid)
            version = 1
        else:
            page_id = int(existing["id"])
            version = int(existing["version"]) + (1 if changed else 0)
            conn.execute(
                """
                UPDATE wiki_pages
                SET title = ?, summary = ?, body = ?, keywords_json = ?,
                    embedding = COALESCE(?, embedding),
                    embedding_model = COALESCE(?, embedding_model),
                    source_count = ?, version = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    title, summary, body, keywords_json, embedding, embedding_model,
                    len({source["asset_id"] for source in sources}), version, page_id,
                ),
            )

        conn.execute("DELETE FROM wiki_sources WHERE page_id = ?", (page_id,))
        conn.executemany(
            """
            INSERT INTO wiki_sources (
                page_id, asset_id, chunk_id, citation_key, excerpt,
                page_number, chunk_type, image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    page_id, source["asset_id"], source["chunk_id"], source["citation_key"],
                    source["excerpt"], source.get("page_number"), source["chunk_type"],
                    source.get("image_path"),
                )
                for source in sources
            ],
        )
        if changed:
            conn.execute(
                """
                INSERT INTO wiki_page_versions (page_id, version, summary, body)
                VALUES (?, ?, ?, ?)
                """,
                (page_id, version, summary, body),
            )
        row = conn.execute(
            """
            SELECT wiki_pages.*, users.username AS owner_username
            FROM wiki_pages JOIN users ON users.id = wiki_pages.owner_user_id
            WHERE wiki_pages.id = ?
            """,
            (page_id,),
        ).fetchone()
    if row is None:
        raise RuntimeError("Wiki page persistence failed")
    return dict(row)


def list_wiki_pages(*, user_id: int, role: str) -> list[dict[str, Any]]:
    where = "" if role == "admin" else "WHERE wiki_pages.owner_user_id = ?"
    params: tuple[Any, ...] = () if role == "admin" else (user_id,)
    with connect() as conn:
        rows = conn.execute(
            f"""
            SELECT wiki_pages.*, users.username AS owner_username,
                   (SELECT COUNT(*) FROM wiki_page_versions WHERE page_id = wiki_pages.id) AS version_count
            FROM wiki_pages
            JOIN users ON users.id = wiki_pages.owner_user_id
            {where}
            ORDER BY datetime(wiki_pages.updated_at) DESC, wiki_pages.id DESC
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def get_wiki_page(page_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT wiki_pages.*, users.username AS owner_username,
                   (SELECT COUNT(*) FROM wiki_page_versions WHERE page_id = wiki_pages.id) AS version_count
            FROM wiki_pages
            JOIN users ON users.id = wiki_pages.owner_user_id
            WHERE wiki_pages.id = ?
            """,
            (page_id,),
        ).fetchone()
    return _row_to_dict(row)


def list_wiki_sources(page_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT wiki_sources.*, nas_assets.title AS asset_title,
                   nas_assets.original_filename, nas_assets.category,
                   nas_assets.user_id AS asset_user_id, users.username AS owner_username
            FROM wiki_sources
            JOIN nas_assets ON nas_assets.id = wiki_sources.asset_id
            JOIN users ON users.id = nas_assets.user_id
            WHERE wiki_sources.page_id = ?
            ORDER BY wiki_sources.asset_id, wiki_sources.chunk_id
            """,
            (page_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_completed_assets_without_wiki(limit: int = 10) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT nas_assets.*
            FROM nas_assets
            WHERE nas_assets.status = 'completed'
              AND nas_assets.chunk_count > 0
              AND NOT EXISTS (
                  SELECT 1 FROM wiki_sources WHERE wiki_sources.asset_id = nas_assets.id
              )
            ORDER BY nas_assets.id
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


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


def update_document_chunk_contents(asset_id: int, chunks: list[dict[str, Any]]) -> None:
    if not chunks:
        return
    with connect() as conn:
        conn.execute("DELETE FROM rag_query_cache WHERE asset_id = ?", (asset_id,))
        conn.executemany(
            """
            UPDATE document_chunks
            SET content = ?, token_estimate = ?, embedding = ?, embedding_model = ?
            WHERE id = ? AND asset_id = ?
            """,
            [
                (
                    chunk["content"],
                    chunk.get("token_estimate", 0),
                    chunk.get("embedding"),
                    chunk.get("embedding_model"),
                    chunk["id"],
                    asset_id,
                )
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
