# Hospital HIS / FHIR Demo

## 病患影像與照護資料 Demo（2026-10-15，已部署）

Hospital 頁面在連線狀態下方提供病患與檢查選單。同頁顯示 Orthanc X 光預覽、教學報告與完整影像頁入口；選定病患後同步顯示虛構訪談對話、住院歷史、飲食偏好／注意事項。這是文字訪談 Demo，沒有新增錄音或語音辨識。

照護資料透過既有 `his_patient_overview` 的 `teaching_profile` 回傳，包含病患 ID、來源 ID、時間與版本；並非新增 FHIR 資源，原有 18 筆關聯資源與五個唯讀工具數量不變。本次部署已重新同步 Hospital MCP 的工具描述。

- 病患甲：兩筆教學住院歷史、外食習慣與待核對的花生相關不適自述。
- 病患乙：一筆教學住院歷史與蛋奶素餐食偏好；偏好不代表醫療禁忌。
- 病患丙：住院與飲食資料待補，影像報告待完成；未提供不代表不存在。

所有資料均由作者編寫，非正式病歷或醫囑。頁面載入與切換不呼叫 LLM。影像沿用公開 CC0 教學素材，不代表這些病患的實際影像。Orthanc 不可用時，文字訪談與照護資料仍可顯示。

入口：<https://goldsys.io/hospital-demo>。備份位於 `/home/ubuntu/backups/hospital-panel-20261015-035726`，包含更新前程式與 SQLite。實站驗證三位病患的資料、報告及 PNG 均成功；匿名 API 回 401，未呼叫 LLM。回退時還原此備份的程式、移除新檔 `app/hospital_demo_profiles.py`、重啟 AI Work 並重新同步 Hospital 工具描述；勿以舊資料庫覆蓋後續活動。瀏覽器互動驗證使用測試資料，尚未完成登入後的實站視覺驗收。

## 範圍

「FAIR」在本次依前文理解為 **FHIR**。這是 HIS 業務查詢與 FHIR R4
資源外觀的唯讀 MCP 示範，不是完整 HIS，也不是通過驗證的 FHIR REST Server。
全數為程式內建虛構資料，快照時間為 2026-10-14；不會連接院所、讀取上傳病歷、
呼叫外部網址或寫入醫囑。三位示範病患各有一次就診、體溫與血紅素觀察值、
一筆占位藥品紀錄與一次回診預約。不包含診斷、治療或劑量建議。

## 啟用

1. 在伺服器受保護的 `.env` 新增 `HOSPITAL_DEMO_MCP_KEY`，值為隨機產生的長金鑰；
   可用 `python -c 'import secrets; print(secrets.token_urlsafe(32))'` 產生。
   不將值填入資料庫、前端或 Git，限制 `.env` 權限為 600。
2. 重啟現有 FastAPI 服務。啟動時會新增停用的 catalog 項目，不修改其他 MCP。
3. 管理員進入「設定與管理 → MCP 管理」，搜尋 `Hospital HIS / FHIR Demo`。
   預設 endpoint 是 `http://127.0.0.1:8000/mcp/hospital-demo`，依實際內部埠調整。
   認證選 Bearer，環境變數名稱為 `HOSPITAL_DEMO_MCP_KEY`。
4. 啟用並同步工具，應顯示 5 個唯讀工具。缺少 key 時端點回傳 503，錯誤 key 回傳 401。
5. AI Work 選「一般模型對話」、勾選 MCP，指定此 Server，再輸入下列問題。
   沿用既有 MCP 工具軌跡、呼叫審計及模型設定；需已有可用的 LLM。

## 問題範例

### 獨立示範入口

左側「AI Work」下方的「醫療 HIS／FHIR Demo」可直接開啟 `/hospital-demo`。
頁面顯示五個唯讀工具：搜尋病患、病患總覽、回診預約、FHIR 搜尋與單筆資源。
按鈕使用固定示範參數直接呼叫 MCP，不需要 LLM；查詢表格保留資源 ID，
並可展開工具回傳內容。自然語言問答則沿用系統目前的 LLM 與既有 MCP 流程。
問答區提供「範例問題」下拉選單，可選病患名單、病患概覽、回診預約、
FHIR 檢驗資料或單筆就診紀錄。選取後填入完整問題，可修改後再按「查詢示範資料」；
選取本身不會呼叫模型。繁英切換只更新選單文字，不覆蓋正在編輯的問題。
若模型沒有使用工具，頁面會提示，不能將該答案視為已查證的 HIS 資料。

必須先登入 AI Work，且管理員已啟用並同步 `hospital-demo`。
瀏覽器以登入身分呼叫 `/api/hospital-demo/tools/call`，金鑰只在伺服器使用；
成功與失敗的工具執行均寫入 MCP 審計記錄。所有資料仍為虛構教學資料。

- 請用 Hospital HIS / FHIR Demo 搜尋所有示範病患，列出病患 ID 與姓名。
- 請查 demo-p001 的就診、檢驗、用藥紀錄與預約，只整理資料，不提供醫療建議。
- 請列出 2026-10-15 的所有示範回診預約，保留來源 ID。
- 請透過 fhir_search_resources 查 demo-p002 的 Observation，列出數值、單位及時間。
- 請用 fhir_read_resource 讀取 Encounter/demo-e001。

## 工具

| 工具 | 參數與用途 |
| --- | --- |
| his_search_patients | query（可選）：姓名、ID、DEMO-001 病歷號；offset / limit |
| his_patient_overview | patient_id（必要），限定一位病患的關聯資源 |
| his_list_appointments | patient_id / date（可選）；offset / limit |
| fhir_search_resources | resource_type（必要）、patient_id（可選）；offset / limit |
| fhir_read_resource | resource_type / resource_id（必要），讀取單一資源 |

FHIR 類型白名單：Patient、Encounter、Observation、MedicationRequest、Appointment。
搜尋回傳 `Bundle.type=searchset`；總筆數與 `next_offset` 可供逐頁查詢。
這是 MCP 的分頁參數，不是完整的 FHIR HTTP search 規格。limit 為 1–20，預設 10。
回覆帶有 `demo`、`notice`、`snapshot_at`、來源及資源 ID。
不支援任意 SQL、URL、路徑、資源類型或新增／修改／刪除工具。

## 安全界線

金鑰僅限制存取示範端點，不代表已實作病患級授權。平台中啟用後可供有 MCP
使用權的員工查詢這批虛構資料。未授權者不可直接存取端點。
正式病歷接入前必須另做照護關係與病患範圍授權、同意與使用依據、臨床驗證、
存取稽核、FHIR profile 驗證及資安驗收。不要把 fixture 替換成真實病歷。

參考：https://hl7.org/fhir/R4/bundle-example.json.html

## 驗證與回退

執行 `.venv/bin/python -m unittest tests.test_hospital_mcp`。
回退時先停用 `hospital-demo`，移除本次 route、import、catalog entry 與模組，
移除金鑰並重啟；保留既有審計記錄，不回復整個資料庫。
