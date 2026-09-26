# Ubuntu 原生自託管安裝指南

AI Work Core 直接安裝到 Ubuntu OS，使用 Python 虛擬環境與 systemd，不需要 Docker。

## 系統要求

- Ubuntu 22.04 LTS 或 24.04 LTS。
- 64 位 CPU、至少 4 核。
- Core 建議至少 8 GB RAM；執行本地模型時需依模型增加記憶體或 GPU。
- Core 建議至少 20 GB 可用空間，使用者檔案與模型空間另計。
- 可使用 `sudo` 的管理員帳號。
- 對外使用時準備域名、HTTPS 和 Nginx。

安裝器會透過 Ubuntu `apt` 安裝 Python、venv、pip、FFmpeg、curl、CA 憑證和 OpenSSL。

## 從 GitHub Release 安裝

下載版本包及校驗檔案後執行：

```bash
sha256sum -c ai-work-VERSION-ubuntu.tar.gz.sha256
mkdir ai-work-installer
tar -xzf ai-work-VERSION-ubuntu.tar.gz -C ai-work-installer
cd ai-work-installer
sudo ./deploy/self-hosted/install.sh
```

安裝器會：

- 建立專用的 `aiwork` Linux 系統帳號。
- 將程式安裝到 `/opt/ai-work`。
- 在 `/opt/ai-work/.venv` 建立 Python 虛擬環境。
- 將資料保存到 `/var/lib/ai-work`。
- 將密鑰與環境設定保存到 `/etc/ai-work/ai-work.env`。
- 生成隨機 Session 金鑰和首次管理員密碼。
- 安裝並啟用 `ai-work.service`。
- 等待 `/healthz` 健康檢查通過。
- 在首次互動安裝時提示選擇 OCR、Embedding、Whisper 與本地 LLM。

### 可選 AI 模組

首次安裝提供以下方案。PDF、DOCX 與純文字解析已包含在 Core，不需要另外下載模型。

| 方案 | 安裝內容 | 適用情境 |
| --- | --- | --- |
| Core | Core 內建 PDF／DOCX 解析 | 先使用雲端模型或稍後配置 |
| Knowledge | PaddleOCR、Qwen3 Embedding 0.6B | 掃描 PDF、圖片 OCR、向量檢索 |
| Meetings | whisper.cpp small、Qwen3 Embedding 0.6B | 會議錄音轉寫與語意查詢 |
| Complete | OCR、Embedding、Whisper，並提示選擇本地 LLM | 完整單機展示 |
| Custom | 逐項詢問 | 自訂資源用量 |

本地 LLM 可選 Qwen3 0.6B Q8_0（約 0.7 GB）、Qwen3 1.7B Q8_0（約 1.9 GB）或 Qwen3 4B Q4_K_M（約 2.6 GB）。模型由 llama.cpp 提供 OpenAI 相容 API，且只綁定 `127.0.0.1:8080`。Embedding 服務只綁定 `127.0.0.1:8081`。

模組下載會在終端顯示進度。中斷後可重新執行：

```bash
sudo /opt/ai-work/deploy/self-hosted/install-modules.sh
```

安裝器不會自動安裝 NVIDIA 驅動或 CUDA。預設以 CPU 建置 llama.cpp；主機已安裝 CUDA toolkit 時，可設定 `AI_WORK_LLAMA_CUDA=1` 使用 GPU。

### 無人值守安裝

自動化部署可用環境變數略過互動問答：

```bash
sudo env \
  AI_WORK_INSTALL_PROFILE=complete \
  AI_WORK_LOCAL_LLM=qwen3-1.7b \
  ./deploy/self-hosted/install.sh
```

支援的 profile 為 `core`、`knowledge`、`meeting`、`complete`、`custom`。也可用 `AI_WORK_INSTALL_OCR=1`、`AI_WORK_INSTALL_EMBEDDING=1`、`AI_WORK_INSTALL_WHISPER=1` 個別啟用模組。本地模型值為 `none`、`qwen3-0.6b`、`qwen3-1.7b` 或 `qwen3-4b`。

安裝完成後開啟：

```text
http://SERVER_IP:8000
```

首次帳號為 `admin`。安裝器只在首次安裝時顯示隨機密碼；登入後應立即在帳號管理中修改。

## 從 Git 倉庫安裝

授權客戶也可以從私有倉庫安裝：

```bash
git clone https://github.com/xuan139/ai-work.git
cd ai-work
sudo ./deploy/self-hosted/install.sh
```

## 安裝目錄

```text
/opt/ai-work/                 程式、靜態檔案與 Python venv
/opt/ai-work/runtime/         whisper.cpp、llama.cpp runtime
/var/lib/ai-work/data/        SQLite 資料庫
/var/lib/ai-work/storage/     NAS 資產、模型與處理結果
/var/lib/ai-work/mock_nas/    NAS 收件與歸檔目錄
/etc/ai-work/ai-work.env      系統配置與密鑰
/var/backups/ai-work/         備份檔案
```

## 配置

編輯：

```bash
sudoedit /etc/ai-work/ai-work.env
sudo systemctl restart ai-work
```

常用設定：

```dotenv
AI_WORK_BIND_HOST=0.0.0.0
AI_WORK_HTTP_PORT=8000
AI_WORK_PUBLIC_URL=https://ai.example.com
AI_WORK_MAX_UPLOAD_BYTES=2147483648
MEDIA_WORKER_COUNT=1
NAS_LLM_BASE_URL=http://127.0.0.1:8080
EMBEDDING_BASE_URL=http://127.0.0.1:8081
```

本地 llama.cpp 與 Embedding 服務可繼續綁定 `127.0.0.1:8080` 和 `127.0.0.1:8081`，不需要將模型服務埠開放到公網。

## 服務管理

```bash
sudo systemctl status ai-work
sudo systemctl status ai-work-embedding
sudo systemctl status ai-work-llm
sudo systemctl restart ai-work
sudo journalctl -u ai-work -f
sudo ./deploy/self-hosted/status.sh
```

健康檢查：

```bash
curl http://127.0.0.1:8000/healthz
```

## 備份

```bash
sudo ./deploy/self-hosted/backup.sh
```

備份指令碼會在服務執行時短暫停止 AI Work，打包 `/var/lib/ai-work` 和 `/etc/ai-work`，再恢復服務。備份檔案保存於 `/var/backups/ai-work/`。

## 升級

下載並解壓縮新的 GitHub Release，再從新版本目錄執行：

```bash
sudo ./deploy/self-hosted/update.sh
```

升級指令碼會先備份目前資料，再把新版本安裝到 `/opt/ai-work`。`/var/lib/ai-work` 與 `/etc/ai-work` 不會被覆蓋。

## Nginx 與 HTTPS

正式環境建議將 `AI_WORK_BIND_HOST` 改為 `127.0.0.1`，由 Nginx 反向代理並提供 HTTPS。大檔案上傳參數可參考：

```text
deploy/nginx-ai-work-upload.conf
```

至少需要保留：

```nginx
client_max_body_size 2g;
proxy_request_buffering off;
proxy_read_timeout 3600s;
```

## 可選能力

Core 啟動不要求本地 LLM、Embedding、Whisper、PaddleOCR 或 YOLO。選配模組安裝失敗不會刪除 Core 與 NAS 資料；修正網路、磁碟或套件問題後，可重跑 `install-modules.sh`。YOLO 與第三方雲端模型仍由管理介面配置。
