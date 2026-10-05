# AI Work NAS 商業部署資安基線

本文件區分「產品已落實的控制」與「客戶正式上線前必須完成的環境控制」。任何單一 Prompt 過濾器都不能取代權限、網路隔離、工具白名單與稽核。

## 1. 已落實的產品控制

### 身分與資料權限

- Session Cookie 使用 `HttpOnly`、`SameSite=Strict`，HTTPS 部署自動加上 `Secure`。
- 登入失敗採 IP＋帳號滑動視窗限制，事件寫入 `security_events`。
- NAS 資產採 `private`、`group`、`company` 三層可見範圍。
- 跨檔檢索在讀取 Chunk 前完成 ACL SQL 過濾，不會先檢索機密內容再事後移除。
- 檔案、預覽、媒體、逐字稿、RAG、Wiki 均使用相同資產權限檢查。
- 權限變更會提高知識庫 revision，使既有跨檔快取自動失效。

### Prompt Injection 與 LLM

- 使用者 Prompt 會檢查「覆寫系統規則、取得秘密、繞過權限、偽造管理員角色」等高風險模式。
- 被攔截事件只保存 Prompt SHA-256、長度與原因，不把可能含機密的原文複製到安全事件中。
- RAG Chunk 與 MCP 回傳均被標示為不可信資料，不能取代系統指令。
- 可疑的間接 Prompt Injection Chunk 會從 LLM Context 隔離，並保存來源 asset/chunk 稽核資料。
- MCP 僅允許已同步、已啟用且標示唯讀的工具；Odoo 另有明確唯讀工具白名單。
- LLM 產生的 MCP 參數會再依工具 JSON Schema 驗證 required、型別、enum、上下限及額外欄位。
- MCP 呼叫與輸入／輸出均保存稽核紀錄；一般使用者不能自行啟用 MCP Server。
- 每位使用者的 LLM 呼叫有基本頻率限制，避免費用與資源濫用。

### Web、主機與備份

- HTTP 回應包含 CSP、HSTS（HTTPS）、`nosniff`、禁止 iframe、Referrer 與 Permissions Policy。
- 正式模式會拒絕弱 `APP_SECRET_KEY`、預設管理員密碼與非 HTTPS 公開網址。
- systemd 使用獨立 `aiwork` 帳號、`NoNewPrivileges`、唯讀系統目錄及 Kernel／SUID 限制。
- Proxy forwarded IP 只信任設定值，預設 `127.0.0.1`，不再信任任意來源。
- 上傳採串流與容量上限，儲存檔名使用隨機 UUID，不使用使用者檔名作為實體路徑。
- 上傳、NAS 收件與網路匯入會檢查檔名及執行 ClamAV 掃描；正式模式設為 `AI_WORK_UPLOAD_SCAN_MODE=required`，掃描失敗時檔案進隔離區，不進解析流程。
- 隔離檔以隨機名稱保存，隔離原因、雜湊及操作者寫入安全事件與資料庫；一般使用者不能從資產頁下載隔離檔。
- OCR、語音與影片處理由 SQLite 持久化佇列追蹤；重啟後恢復未完成任務，長音訊逐片續跑，掃描型 PDF 逐頁續跑，缺失向量由背景循環補建。
- 備份建立後先驗證；設定 passphrase file 時使用 AES-256-CBC、PBKDF2 加密。

## 2. Prompt 攻擊分層防護

```text
使用者／LINE／API
  -> 身分、角色、Rate Limit
  -> Prompt 風險檢查
  -> ACL 過濾後才檢索
  -> RAG/MCP 不可信內容隔離
  -> 唯讀工具白名單＋參數 Schema 驗證
  -> LLM 生成答案
  -> 引用、呼叫、安全事件稽核
```

防護原則：

1. 不把 LLM 當成授權系統；授權只能由後端程式判定。
2. 不讓模型自由組合任意 URL、Shell 或 SQL；只能選已註冊工具與受限參數。
3. 文件文字、Email、網頁、MCP 結果全部視為資料，不視為指令。
4. 高風險動作即使未來開放寫入，也必須採使用者確認、最小權限與可回復交易。
5. API Key、OAuth refresh token、資料庫密碼不得放進 Prompt、回傳、SQLite 或 Git。

## 3. 客戶測試環境上線前必做

- 使用正式網域與有效 TLS 憑證，設定 `AI_WORK_PUBLIC_URL=https://...`、`AI_WORK_ENV=production`。
- 將 8000、8080、8081、5678 僅綁 loopback；外部只開 443。
- 更換首次 admin 密碼，另外建立日常管理帳號，不共用 admin。
- 公司 API Key 放 `/etc/ai-work/ai-work.env`，權限維持 `0640 root:aiwork`。
- 啟用 Ubuntu 自動安全更新、SSH Key、停用 SSH 密碼登入與 root 遠端登入。
- 防火牆只允許必要來源；管理介面建議限制公司 VPN 或 Tailscale。
- 確認 ClamAV 病毒碼已更新，對 EICAR 測試檔驗證隔離流程；含壓縮檔的深層掃描能力需依 ClamAV 設定另行驗收。
- 設定每日加密備份、異機保存、保留週期，並至少實際演練一次還原。
- 將 Nginx、systemd、登入、安全事件與 MCP audit 導入集中式日誌／SIEM。
- 執行弱點掃描、依賴套件掃描與外部滲透測試，修正後才能放正式資料。

## 4. 第二階段商用強化

- OIDC／Microsoft Entra ID／Google Workspace SSO 與 MFA。
- Redis 型分散式 Rate Limit、工作佇列與 Session 撤銷。
- PostgreSQL row-level security 與 pgvector；資料量及並行增加後取代 SQLite。
- KMS／Vault 管理雲端 API Key、OAuth Token 定期輪替。
- 檔案 DLP、PII 分類、保留政策、法律封存與可驗證刪除。
- 寫入型 MCP 採雙人覆核、一次性授權、交易上限與完整 before/after audit。
- SBOM、簽章安裝包、版本升級簽章驗證與 CVE 修補 SLA。

## 5. 驗收條件

- 不同使用者以直接 URL、Wiki、RAG、下載與 MCP 均無法取得未授權資產。
- 權限或文件版本改變後，舊知識快取命中數為零。
- 測試 Prompt 嘗試取得 system prompt、API Key 或繞過權限時回傳 400，並產生安全事件。
- RAG 文件包含「忽略之前指令」時，該 Chunk 不會送入 LLM。
- MCP 無法呼叫未標示唯讀的工具，額外或超限參數會被拒絕。
- 正式模式使用 HTTP、弱 Secret 或預設管理員密碼時服務拒絕啟動。
- 備份可在隔離主機完成解密與還原。

## 6. 自動預檢

在包含 `.git` 與 `tests/` 的原始碼 checkout 先執行自動審計；部署後再於 Ubuntu 執行正式環境預檢：

```bash
cd /path/to/ai-work-source
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-security.txt
./deploy/self-hosted/security-audit.sh
sudo /opt/ai-work/deploy/self-hosted/security-check.sh
```

預檢會驗證正式模式、HTTPS、loopback 綁定、Secret、初始管理員密碼、ClamAV、隔離區、設定檔權限、systemd 服務、公開健康檢查與 HSTS。自動審計會檢查 Python 依賴漏洞、高風險靜態告警、Git 已追蹤密鑰，以及安全回歸測試。惡意檔案實測、備份還原、權限穿透、外部弱點掃描與滲透測試仍需在獲授權的客戶測試環境完成。

單台 NAS 可先使用內建 SQLite 佇列；此版本不宣稱多主機 Worker 共享佇列。取消長時間的單次 OCR／ASR／影片推論會在該階段返回後生效；已完成的音訊片段與 OCR 頁面仍保留，手動「重新處理」則重新執行相應階段。若雲端 ASR 只提供單次上傳的 API Key，服務重啟後須有公司環境變數中的 Key 才能自動續跑。
