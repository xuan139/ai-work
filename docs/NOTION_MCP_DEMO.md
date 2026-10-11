# Notion MCP Demo：從零開始

## Notion 是什麼？

Notion 是整合文件、Wiki、資料庫與專案協作的工作區。頁面可以放 SOP、會議紀錄、產品說明及待辦事項；資料庫可把資料組織成不同檢視。

- Odoo 管理訂單、物料、生產、庫存與會計交易。
- Notion 適合管理「如何做」的文件、政策、專案背景與知識。
- AI Work 透過 MCP 讀取被授權的 Notion 資料，由目前設定的 LLM 整理答案。
- Notion 不是 Odoo 的替代 ERP，也不會自動與 NAS 知識庫同步。

## 本次 Demo

登入 AI Work 管理員帳號，從左側開啟 **Notion MCP Demo**，路徑 `/notion-demo`。

```text
使用者問題
   → AI Work 目前的 LLM 規劃工具
   → Notion 唯讀 MCP Adapter
   → Notion REST API（僅已授權頁面）
   → LLM 整理答案
   → 顯示來源頁面、工具參數與結果、保存呼叫稽核
```

本次是 AI Work 自有的唯讀 MCP Adapter，使用固定版本 `2025-09-03` 的 Notion REST API；不是假稱已連接 Notion 官方 OAuth MCP。原 MCP 管理內的 `Notion` 官方服務仍保留，設定與金鑰不同。

目前提供三個工具：

| 工具 | 用途 | 限制 |
| --- | --- | --- |
| `notion_search` | 搜尋頁面標題，或列出最近更新頁面 | 不是內文全文搜尋；每批最多 10 筆，可分頁 |
| `notion_read_page` | 讀取標題及前 30 個內容區塊 | 子區塊與後續分頁另讀；文字有上限 |
| `notion_read_blocks` | 讀取子區塊或下一批區塊 | 每批最多 10 個；不抓外部網址或附件 |

未實作建立、修改、刪除頁面；未實作資料庫列篩選、附件 OCR、NAS 匯入、對話記憶或 Notion OAuth。每次問答最多 3 次工具呼叫；完整原始工具結果可展開查看，傳給小模型的摘錄有長度上限，不能視為完整工作區審查。

## 1. 建立帳號與教學頁面

1. 到 [Notion](https://www.notion.com/) 註冊帳號，建立工作區。
2. 建立父頁面 `AI Work Demo`。先不要放個資、客戶秘密或真實財務資料。
3. 在下面建立 `採購 SOP`、`SC-100 產品說明`、`每週製造會議` 三個子頁面。
4. 各頁輸入下列教學資料。這些是建議自行建立的內容，不是已存在於你的工作區，也不是既有 Odoo 事實。

### 採購 SOP

> 請購由生管提出，填寫料號、數量、用途與需求日期。
> 採購比價後交部門主管核准，核准後向供應商下單。
> 倉管核對到貨數量；品保執行必要檢驗。
> 不合格物料放入待處理區，不得直接領用。
> 會計核對採購單、實收紀錄及供應商憑證後安排付款。

### SC-100 產品說明

> SC-100 是教學用智慧輸送機，使用控制箱及驅動模組。
> 出貨前需完成外觀、配線與基本運轉檢查。
> 本頁未設定正式交期、保固期間或售價。

### 每週製造會議

> 生管：確認下週製造需求與缺料清單。
> 採購：回覆馬達供應商的到貨日期。
> 品保：追蹤上週來料異常。
> 尚未指定各項工作的完成期限。

## 2. 建立唯讀 Internal Integration

依 [Notion Internal connections 官方說明](https://developers.notion.com/guides/get-started/internal-connections) 操作：

1. 開啟 Notion 開發者／Integration 管理頁，建立工作區內部連線，命名 `AI Work Read-only Demo`。
2. 指定你的測試工作區。
3. 在 Capabilities 只保留 **Read content**；不要勾選 Insert content、Update content 等寫入能力。
4. 取得 Integration Token，保管在自己的密碼管理器或受限伺服器設定中，不要貼在聊天、文件、截圖或 Git。
5. 回到 `AI Work Demo` 頁面的選單，在 Connections 加入此 Integration；確認需要測試的子頁面都在授權範圍。

只有 Token 不夠，沒有分享頁面通常會搜尋不到或回傳 404。Notion 畫面名稱可能隨版本／語言調整；以官方連線說明為準。

## 3. 設定 AI Work

在 AI Work 的 `.env` 設定（不要把真實值提交到 Git）：

```dotenv
NOTION_API_KEY=你的唯讀IntegrationToken
```

限制 `.env` 檔案讀取權限，重新啟動原本的 AI Work 服務。此 Demo 不需要安裝額外 Python 套件，也不需要 Docker。

- 本機執行方式與專案 README 相同：`.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000`。
- Ubuntu 如已使用 systemd，由管理員依實際服務名稱重啟；不要另外開一個重複監聽的服務。
- 「已設定，尚未驗證」只代表伺服器有讀到環境變數。按「最近更新的頁面」，API 成功後才顯示「最近一次讀取成功」。
- Notion 需要連網。使用本地 LLM 時，讀到的頁面由本地模型處理；選用雲端 LLM 時，問題及頁面摘錄會傳給該供應商，須先取得公司核准。

## 4. 演示

1. 以管理員登入 AI Work，開啟左側 Notion MCP Demo。
2. 按「最近更新的頁面」或搜尋標題 `採購`；這一步只讀 MCP，不呼叫 LLM。
3. 點選 `採購 SOP`，問題框填入：`請整理請購、核准、收貨、驗收和付款的分工。`
4. 送出後會使用「設定與管理」目前指定的 LLM；查看答案、來源連結與 MCP 執行軌跡。
5. 也可以清除選取後問：`找出 SC-100 產品說明，出貨前需要做哪些檢查？`
6. 測試不足證據：`SC-100 的正式保固期限是多少？` 正確行為應是說明文件未提供，而非編造期限。

若小模型未選到正確工具，先搜尋並點選頁面，讓問題帶上精確 page ID。LLM 仍可能答錯，頁面來源與工具結果才是核對依據。

## 5. MCP 管理／外部 MCP 用戶端（選用）

獨立 Demo 在同一 FastAPI 程序內呼叫 JSON-RPC MCP handler，不必先啟用目錄項目，也不需要自己連回固定的 8000 埠。它與 `/mcp/notion` 使用同一套三個唯讀工具。

如需讓既有 AI Work 通用 MCP 客戶端呼叫此 Adapter：

1. 另設定 `NOTION_LOCAL_MCP_KEY` 為隨機金鑰，不能與 `NOTION_API_KEY` 共用。
2. MCP 管理選擇 **Notion Read-only Demo**，Endpoint 設為服務實際可達的 `http://127.0.0.1:8000/mcp/notion`（不同埠需調整）。
3. 保留 Bearer 驗證與 `NOTION_LOCAL_MCP_KEY` 環境變數名稱，啟用並同步工具。
4. 外部 MCP 用戶端使用 `Authorization: Bearer <NOTION_LOCAL_MCP_KEY>`，以 Streamable HTTP JSON-RPC 呼叫。

未設定內部金鑰時，`/mcp/notion` 關閉。對外需透過 HTTPS 與網路存取控制；優先僅使用本機。持有內部金鑰等於獲得 Integration 的全部已分享頁面讀取權，不代表個別 Notion 使用者權限。

## 安全與資料保存

- Demo 與相關 API 僅管理員可用；一般員工的通用 MCP 清單／執行路徑也會排除此 Adapter。
- 只有 Notion Integration 已授權頁面能被讀取；本期不提供逐員工 OAuth 或 Notion 原生權限映射。
- Token 不傳給 LLM、不回傳瀏覽器、不寫入 MCP 目錄或 Git。環境變數只在伺服器端使用。
- Demo 的工具成功／失敗及 LLM 呼叫保存於 NAS 稽核資料庫。工具結果可能包含文件內容；應納入公司稽核存取與留存政策。
- 原始 Notion 頁面仍在 Notion；本 Demo 沒有自動將它們納入 NAS RAG 或 Wiki。
- 不接受任意 API URL、寫入工具或命令；HTTP redirect 禁用，避免 Token 被轉送到其他站。
- 頁面文字視為不可信資料；Prompt 防護不能保證所有 Injection 都被辨識，因此硬性唯讀工具、最小授權與管理員限制才是主要界線。

## 常見問題

| 現象 | 檢查 |
| --- | --- |
| 尚未設定 | `.env` 位置、變數名稱、服務是否已重新啟動 |
| 401 | Token 是否完整、有效，是否填成官方 MCP OAuth token |
| 403／404 | Integration 的 Read content 權限，以及頁面的 Connections 授權 |
| 搜不到內文關鍵字 | 本期搜尋是標題搜尋，改用頁面標題，選中後讀取內文 |
| 空結果 | 工作區與頁面授權是否正確；新分享的頁面可能尚未進搜尋索引 |
| 回答缺少後段 | 區塊分頁、巢狀內容、3 次工具限制與小模型摘錄上限 |
| 模型連線失敗 | AI Work 目前 LLM 是否已啟動、雲端 Key 是否已設定 |
| 429 | 降低頻率，稍後再試；不要不停按送出 |

## 官方參考

- [Notion MCP](https://developers.notion.com/guides/mcp/overview)：官方遠端服務與 OAuth。
- [Search by title](https://developers.notion.com/reference/post-search)：標題搜尋與分頁。
- [Retrieve block children](https://developers.notion.com/reference/get-block-children)：子區塊及後續分頁。

本次尚無使用者的 Notion 工作區及 Integration，未進行真實 Notion／LLM 串接驗收。自動化測試使用獨立測試回應，未當成線上資料展示。
