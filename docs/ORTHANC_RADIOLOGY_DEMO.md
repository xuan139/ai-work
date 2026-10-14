# Orthanc 放射影像唯讀 Demo

## 使用流程

左側「放射影像／Orthanc Demo」開啟 `/radiology-demo`。登入後選擇教學病患，
再選一筆檢查，即可讀取 Orthanc 預覽與教學報告，最後按「產生摘要」。
選擇範例問題只填入文字，不會自動呼叫 LLM。

資料流：瀏覽器 → 登入驗證 → MCP HTTP 工具 → Orthanc REST → 報告 → 目前系統 LLM。
每次摘要重新讀取檢查與報告，不依賴先前回答快取。輸出包含來源清單、Study UID、
報告 ID／版本與 MCP 軌跡；若模型沒有附 `[R1]`，畫面顯示引用警告。
來源清單表示模型收到哪些證據，不等於答案已經由醫師驗證。

## 教學資料與影像來源

- 病患對應既有 HIS Demo 的 `demo-p001`、`demo-p002`、`demo-p003`。
- 檢查為 `demo-xr001` 至 `demo-xr003`；第三筆報告待完成，後端禁止為其產生摘要。
- 三筆重用同一張 CC0 公開 X 光圖，不是這些虛構病患實際拍攝的影像，也不可拿來比較病程。
- 作者：Mikael Häggström；來源：[Wikimedia Commons 原圖及 CC0 授權](https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg)。
- 圖片來源頁 SHA-1：`3124c4cf4c55eb3d2defa9b909f08f94e941ec43`。匯入前驗證，變更時中止。
- 公開 JPEG 封裝為 DICOM Secondary Capture（Modality OT），不是原始 DX／CR 採集資料。
- 教學報告由程式作者撰寫，不是來源影像的正式放射科報告，沒有診斷或治療結論。
- 本頁使用 Orthanc PNG 預覽，可縮放及調整顯示對比；不是 OHIF，也不是診斷級 DICOM 檢視器。
- LLM 只收到文字報告與檢查中繼資料，不會收到影像像素，不能宣稱已判讀影像。

## MCP 工具

| 工具 | 參數 | 功能 |
| --- | --- | --- |
| radiology_search_patients | 無 | HIS 教學病患清單 |
| radiology_search_studies | patient_id | 從 Orthanc 查詢教學檢查 |
| radiology_get_study | study_id | 檢查詳情與 UID |
| radiology_get_report | study_id | 教學報告與狀態 |
| radiology_patient_timeline | patient_id | 教學檢查時間序列 |
| radiology_open_viewer | study_id | 需登入的同源影像連結 |

端點 `/mcp/radiology-demo` 使用獨立 `RADIOLOGY_MCP_KEY`。工具僅接受上述固定資源 ID。
介面不接受任意 URL、Orthanc 路徑、SQL 或新增／刪除動作。
所有已登入使用者可看這批教學資料；這不是正式病患級授權方案。
一般 MCP 工具路徑與專屬頁面共用 adapter。影像走登入驗證的 PNG proxy，不向瀏覽器提供 Orthanc 帳密。
成功／失敗工具呼叫及影像讀取都有 MCP audit，LLM 呼叫沿用既有模型審計。

## Ubuntu 部署（不使用 Docker）

目前目標：Ubuntu x86_64、專案 `/home/ubuntu/ai-work`、服務帳號 `ubuntu`。
先備份將更新的程式、`.env`、SQLite；檢查遠端沒有其他未整合程式修改。
不得把本機 `.env`、資料庫、模型或 uploads 蓋到伺服器。

1. 上傳本次程式與 static 檔案，執行測試。
2. 檢查 8043 未被占用、磁碟至少預留 512 MB，且沒有既有 `aiwork-orthanc` 服務。
3. 在伺服器專案目錄執行 `bash deploy/orthanc/install.sh`。

安裝腳本下載 [官方 Orthanc 1.13.0 LSB binary](https://orthanc.uclouvain.be/book/users/debian-packages.html)，
放入專案 `storage/orthanc/bin`，不修改系統既有 Orthanc。無需在 Mac 安裝任何影像伺服器。
設定只綁 `127.0.0.1:8043`、Basic auth、關閉 DICOM 收件、WebDAV、Explorer、Lua 及外掛。
啟動後以 `ss` 確認唯一監聽為 loopback，不符合就停止。不要替此埠開防火牆或公網反向代理。

`prepare` 會在伺服器產生隨機帳密與 MCP key，保存在權限 600 的設定及 `.env`，
原 `.env` 備份到 `backups/orthanc-prepare-*`。若已有設定或相同環境變數則中止，不輪替既有憑證。
`seed` 透過 Orthanc 的建立 DICOM API 匯入固定 UID，重跑不重複建立；寫入工具只在 CLI 中，MCP 不提供。
`activate` 必須在重啟 AI Work 後執行，確認所有影像可讀，再同步並啟用六個工具。

如果 seed 失敗或偵測到背景任務，安裝流程會停止 Orthanc，保留資料與設定供診斷，不會自動重寫或重試部署。
處理原因後可手動依序執行：

```bash
sudo systemctl start aiwork-orthanc.service
.venv/bin/python tools/orthanc_demo.py seed
# 確認沒有待處理／執行中任務後才重啟既有服務
sudo systemctl restart ai-work.service
.venv/bin/python tools/orthanc_demo.py activate
sudo systemctl enable aiwork-orthanc.service
```

## 驗證與回退

單元測試：`.venv/bin/python -m unittest discover -s tests -p test_radiology_mcp.py`。
正式驗證應確認三筆檢查、PNG 成功顯示、待完成報告拒絕摘要、真實模型摘要與來源、
未登入 API 回 401、外部無法連接 8043，以及審計記錄。用雲端模型時，教學報告文字會送至所選供應商。
此版本尚不包含病患級授權、正式報告簽署、DICOM Worklist、PACS 寫入或臨床驗證。

回退：停用 `orthanc-radiology` catalog；停止並 disable `aiwork-orthanc.service`；
還原本次 core/static 程式並重啟 AI Work。只移除本次新增的四個 `.env` 變數，
不要以舊 `.env` 或資料庫覆蓋後續使用者活動。保留影像、憑證備份與 audit，待確認後再刪除。

## 本次部署結果

- 已部署至 <https://goldsys.io/radiology-demo>；左側選單「放射影像／Orthanc Demo」。
- 備份：`/home/ubuntu/backups/radiology-20261014-233940`，包含 core 程式、環境與 SQLite。
- Orthanc 1.13.0 由 `aiwork-orthanc.service` 管理，僅監聽 `127.0.0.1:8043`，已啟用開機啟動。
- 三筆檢查及六個工具均通過實際 MCP 呼叫；HTTPS 圖片回傳 PNG，未登入回 401，待完成報告摘要回 409。
- 已以目前的 Qwen3 4B 完成附來源摘要，模型呼叫紀錄 ID `457`。此測試不代表臨床有效性。
- 桌面／手機瀏覽器測試使用測試資料，已驗證互動與排版；實站登入後畫面人工驗收尚未完成。
- 2026-10-15 使用者授權將此功能獨立提交並推送；Hospital 同頁整合另以獨立變更記錄。
