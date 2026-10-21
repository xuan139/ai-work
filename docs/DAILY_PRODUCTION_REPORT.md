# 每日生產報告工作流

## 範圍

第一階段提供只限管理員使用的 `/daily-production-report` 頁面。管理員按下「產生／查看今日報告」後，系統會：

1. 以既有唯讀 MCP 查詢 Odoo 訂單與庫存、MES 產線資料、QMS 品質、CMMS 維護，以及排程所需的 WMS／PLM／SPC 補充資料。
2. 使用目前選定的本地排程引擎建立同一份有限產能排程快照。
3. 以固定公式計算生產達成率、FPY、OEE、預測準交率、延期訂單、缺料、換線及停機時間。
4. 保存完整 JSON 快照及 PDF 到 `storage/production_reports/YYYY/MM/report-NNNNNN/`。
5. 將 JSON 與 PDF 同時登記為 NAS 資產，並保留來源編號和 MCP 工具軌跡。

伺服器另由 `ai-work-daily-production-report.timer` 在每天 18:00（Asia/Taipei）執行一次。`Persistent=true` 會在錯過執行時間後補跑；資料庫以 `report_date` 唯一索引和冪等生成流程保證同一天只有一份正式日報。手動按鈕只會生成缺少的今日日報，已有日報時直接返回既有結果。自動報告預設由 `admin` 擁有，可用 `AI_WORK_DAILY_REPORT_USER` 指定另一個既有管理員。

此階段不呼叫 LLM，也不會寫入 Odoo、MES、QMS、CMMS 或 PLC。管理摘要由固定規則生成，避免模型改寫關鍵數字。

## KPI 公式

| KPI | 公式 | 主要來源 |
| --- | --- | --- |
| 生產計畫達成率 | MES 完成數量 ÷ MES 計畫數量 | MES MCP |
| 一次通過率 FPY | MES 一次合格數量 ÷ MES 完成數量 | MES、QMS MCP |
| OEE | 可用率 × 效能率 × FPY | MES、CMMS MCP |
| 預測準交率 | 預測準時訂單數 ÷ 排程訂單數 | Odoo MCP、本地排程引擎 |
| 預計延期訂單 | 預測完成時間晚於需求交期 | Odoo MCP、本地排程引擎 |
| 缺料項目 | 需求數量大於可用庫存 | Odoo、WMS MCP |
| 排程換線時間 | 所有工序 `setup_minutes` 合計 | MES MCP、本地排程引擎 |
| 停機與保養時間 | MES 停機及 CMMS 維護窗口分鐘數合計 | MES、CMMS MCP |

來源缺失時，對應 KPI 顯示 `N/A`，不會使用 LLM 或預設值補造數字。Demo MES 的 `daily_production` 是明確標示的固定教學原始計數；正式接入時需由客戶 MES 提供相同欄位或建立映射。

## 權限與保存

- 左側「每日生產報告」入口只對管理員顯示。
- 報告頁面、產生、詳情及下載 API 均要求管理員權限。
- API 不向瀏覽器回傳伺服器檔案路徑。
- 下載前會再次驗證資料庫權限，並確認檔案位於受控報告目錄。
- JSON 快照包含產生當下的排程、來源與工具軌跡，供稽核與重現。

## API

- `POST /api/daily-production-reports`：取得目前 MCP 快照並產生報告。
- `GET /api/daily-production-reports?limit=50`：列出有權查看的歷史記錄。
- `GET /api/daily-production-reports/{id}`：讀取一份報告及來源。
- `GET /api/daily-production-reports/{id}/download`：下載 PDF。

## 定時器檢查

```bash
systemctl status ai-work-daily-production-report.timer
systemctl list-timers ai-work-daily-production-report.timer
journalctl -u ai-work-daily-production-report.service -n 100 --no-pager
```

## 尚未包含

- LINE／Email 定時推送。
- 管理層針對歷史報告的 LLM 追問。
- 報告審批、電子簽章及正式 MES 欄位映射。
- 背景持久化工作佇列與伺服器重啟後的報告任務恢復。

這些項目應在實際企業欄位與日報截止時間確認後實施，避免把 Demo 口徑直接當作正式管理指標。
