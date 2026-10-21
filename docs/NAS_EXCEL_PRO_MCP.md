# NAS Excel Pro MCP

`NAS Excel Pro MCP` lets an authenticated AI Work user query multiple NAS-managed XLSX, CSV, and TSV files with DuckDB. It never updates a source file. An export creates a separate private XLSX NAS asset.

## Access and security

- Every source is checked with the existing NAS asset policy before it is opened.
- Administrators can read all assets. Other users can read assets they uploaded, company-visible assets, assets owned by one of their department groups, and assets explicitly granted to them or their group.
- The MCP bearer key identifies the internal service. A short-lived HMAC-signed user delegation identifies the calling AI Work user. A bearer key alone cannot read a file.
- SQL is restricted to one `SELECT` or `WITH` statement. File-reading functions, DDL, DML, extensions, comments, and DuckDB configuration statements are blocked.
- Generated files are private to the requesting user by default and contain a `Sources` sheet with the query and source ranges.

In this application, a department is represented by an AI Work user group. File access therefore follows uploader, department group, company visibility, and explicit file grants without maintaining a second permission model.

## MCP endpoint and tools

- Endpoint: `/mcp/excel-pro`
- Environment key: `NAS_EXCEL_PRO_LOCAL_MCP_KEY`
- `excel_pro_list_sources`: list only accessible spreadsheet assets.
- `excel_pro_describe_sources`: return DuckDB table aliases, columns, and citable worksheet ranges.
- `excel_pro_query`: execute a bounded cross-file read-only query and return rows with citations.
- `excel_pro_start_export`: enqueue a non-destructive XLSX export with optional pivot summary and chart.
- `excel_pro_job_status`: read progress and the download link for an owned job.

## Web use

1. Open **NAS Excel Pro** from the left navigation.
2. In **選擇查詢範圍**, keep **自動選擇** when the system may find relevant files, or choose **指定檔案** to open a searchable multi-select file dialog. Selected filenames remain visible above the question field; a specific-file query cannot run with an empty selection.
3. The page displays the final answer, selected files, worksheet/range citations, generated SQL, and the complete LLM/MCP trace.
4. Open **DuckDB SQL 進階查詢** only when you want to edit and run SQL manually. This section is collapsed by default.
5. Check the returned source references such as `銷售明細!A2:G850`.
6. To create a file, explicitly open the export section, enter pivot/chart options, and select **建立背景匯出**.
7. Follow the persistent progress bar. When complete, download the new XLSX from the job row.

The question flow is deliberately separate from export:

1. The configured system LLM extracts the analysis goal and source keywords.
2. `excel_pro_list_sources` returns only files visible to the current user.
3. `excel_pro_describe_sources` returns table aliases, columns, and citable ranges.
4. The LLM produces one restricted DuckDB `SELECT`/`WITH` statement.
5. `excel_pro_query` executes the statement through MCP.
6. The LLM writes the final answer from the bounded result and citations.

The agent never receives permission to call `excel_pro_start_export`. Natural-language questions therefore cannot create files; only the explicit export button can enqueue an XLSX job.

Example cross-file query:

```sql
SELECT
  s.產品,
  SUM(s.數量) AS 銷售數量,
  MAX(i.可用庫存) AS 可用庫存
FROM "asset_41__銷售明細" AS s
LEFT JOIN "asset_52__data" AS i ON i.產品 = s.產品
GROUP BY s.產品
ORDER BY 銷售數量 DESC
```

For a pivot summary, use `產品` as the row field, `銷售數量` as the value field, and `sum` as the aggregate. A bar chart can then use `產品` as its category and `sum_銷售數量` as its value.

## Large files and recovery

Interactive queries return at most 500 rows. Background exports support up to 200,000 result rows and 500,000 rows per selected source table in this first release. XLSX input is streamed in read-only mode; CSV/TSV is loaded through DuckDB. Only one export runs at a time to control NAS memory pressure.

Queued and running jobs are stored in SQLite. After an application restart, interrupted jobs return to the queue. Users can cancel queued jobs immediately or request cancellation between processing stages.

## Deployment

Install `duckdb` from `requirements.txt`, set a strong `NAS_EXCEL_PRO_LOCAL_MCP_KEY`, restart AI Work, and verify `/mcp/excel-pro`. The database migration and MCP catalog registration run through `init_db()`.

Rollback: disable `nas-excel-pro` in MCP management, remove the navigation entry, and stop the Excel Pro worker. Existing generated XLSX assets remain ordinary NAS files and are not deleted.

## Implementation record

- **Trigger:** The original NAS Excel MCP queried one workbook through SQLite, had no cross-file export, no background progress, and did not bind tool calls to the current NAS user's asset permissions.
- **Root cause:** It was intentionally built as a small read-only inspection adapter before asset groups, explicit grants, and durable job processing were required.
- **Fix:** Add a separate DuckDB-based permission-aware MCP, signed internal user delegation, a persistent export queue, new XLSX output with source ranges, a natural-language LLM-to-MCP query chain, and an operator page. Keep the original MCP available for compatibility.
- **Verification:** Dedicated tests cover owner/group isolation, denied access, XLSX/CSV joins, citations, read-only SQL controls, signed delegation, the three-stage LLM flow, absence of agent-triggered exports, output ownership, pivot/chart generation, and source-file hashes. The complete Python suite and desktop/mobile browser fixture must pass before deployment.
- **Not yet verified:** Performance against customer files near the documented row limits depends on NAS CPU, memory, disk, and workbook complexity. Formula cells use the workbook's last saved cached value; encrypted or damaged workbooks are not supported. Natural-language SQL accuracy still depends on the selected system LLM and each customer's real column naming conventions.
- **Rollback:** Disable the new catalog entry and worker, restore the changed runtime/static files, and restart AI Work. The schema addition is additive and may remain unused; do not delete completed export assets without their owners' approval.
- **Deployment (2026-10-21):** Confirmed the remote core files matched Git HEAD and no media job was active. Backed up code, SQLite, and `.env` under `/home/ubuntu/backups/nas-excel-pro-20261021-112333`; installed DuckDB 1.5.6, generated the internal key only on the server, ran all seven dedicated tests, and restarted `ai-work.service`. The MCP is connected with five tools, the migration created the persistent job table, the public static resource returns 200, anonymous page access returns 401, and every deployed runtime/static hash matches the verified local release.
- **Natural-language chain deployment (2026-10-21):** Verified the remote files matched Git HEAD before replacement and backed up code, SQLite, and `.env` under `/home/ubuntu/backups/excel-pro-llm-20261021-v2`. Ten Excel Pro tests and the desktop/mobile browser fixture passed. The full remote suite ran 208 tests with two pre-existing failures in PDF reprocessing and enterprise-knowledge evaluation state; neither failing test imports or exercises this change. After restart, `ai-work.service` is active, the static resource returns 200, anonymous page/API access returns 401, and `nas-excel-pro` is connected with five tools.
