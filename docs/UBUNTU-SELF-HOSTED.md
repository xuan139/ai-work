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

Core 啟動不要求本地 LLM、Embedding、Whisper、PaddleOCR 或 YOLO。管理員可以先在 Web 後臺配置雲端模型；需要資料留在本地時，再分別安裝本地模型服務和可選依賴。
