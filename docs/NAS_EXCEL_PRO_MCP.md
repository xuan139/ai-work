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
2. Select two or more files. The page shows each SQL table alias, for example `asset_41__銷售明細` and `asset_52__data`.
3. Enter DuckDB SQL and select **執行查詢**.
4. Check the returned source references such as `銷售明細!A2:G850`.
5. Optionally enter pivot row/value columns and chart columns, then select **建立背景匯出**.
6. Follow the persistent progress bar. When complete, download the new XLSX from the job row.

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
- **Fix:** Add a separate DuckDB-based permission-aware MCP, signed internal user delegation, a persistent export queue, new XLSX output with source ranges, and an operator page. Keep the original MCP available for compatibility.
- **Verification:** Dedicated tests cover owner/group isolation, denied access, XLSX/CSV joins, citations, read-only SQL controls, signed delegation, output ownership, pivot/chart generation, and source-file hashes. The complete Python suite and desktop/mobile browser fixture must pass before deployment.
- **Not yet verified:** Performance against customer files near the documented row limits depends on NAS CPU, memory, disk, and workbook complexity. Formula cells use the workbook's last saved cached value; encrypted or damaged workbooks are not supported.
- **Rollback:** Disable the new catalog entry and worker, restore the changed runtime/static files, and restart AI Work. The schema addition is additive and may remain unused; do not delete completed export assets without their owners' approval.
- **Deployment (2026-10-21):** Confirmed the remote core files matched Git HEAD and no media job was active. Backed up code, SQLite, and `.env` under `/home/ubuntu/backups/nas-excel-pro-20261021-112333`; installed DuckDB 1.5.6, generated the internal key only on the server, ran all seven dedicated tests, and restarted `ai-work.service`. The MCP is connected with five tools, the migration created the persistent job table, the public static resource returns 200, anonymous page access returns 401, and every deployed runtime/static hash matches the verified local release.
