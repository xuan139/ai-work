# Ubuntu 自託管安裝指南

## 系統要求

- Ubuntu 22.04 LTS 或 24.04 LTS。
- 64 位 CPU、至少 4 核。
- Core 建議至少 8 GB RAM；執行本地模型時需依模型增加記憶體或 GPU。
- Core 建議至少 20 GB 可用空間，使用者檔案與模型空間另計。
- Docker Engine 和 Docker Compose v2。
- 對外使用時準備域名、HTTPS 和 Nginx。

## 從 GitHub Release 安裝

下載版本包及校驗檔案後執行：

```bash
sha256sum -c ai-work-VERSION-ubuntu.tar.gz.sha256
mkdir ai-work
tar -xzf ai-work-VERSION-ubuntu.tar.gz -C ai-work
cd ai-work
./deploy/self-hosted/install.sh
```

安裝器會：

- 建立 `data`、`storage` 和 `mock_nas` 持久化目錄。
- 生成隨機 Session 金鑰。
- 生成首次管理員密碼。
- 優先拉取 GitHub Container Registry 映象；不可用時從安裝包構建。
- 啟動服務並等待 `/healthz` 透過。

安裝完成後開啟：

```text
http://SERVER_IP:8000
```

首次賬號為 `admin`。安裝器只在首次建立 `.env` 時顯示隨機密碼；登入後應立即在賬號管理中修改。

## 從 Git 倉庫安裝

授權客戶也可以從私有倉庫安裝：

```bash
git clone https://github.com/xuan139/ai-work.git
cd ai-work
./deploy/self-hosted/install.sh
```

## 配置

安裝配置位於：

```text
deploy/self-hosted/.env
```

常用設定：

```dotenv
AI_WORK_HTTP_PORT=8000
AI_WORK_PUBLIC_URL=https://ai.example.com
AI_WORK_MAX_UPLOAD_BYTES=2147483648
MEDIA_WORKER_COUNT=1
NAS_LLM_BASE_URL=http://host.docker.internal:8080
EMBEDDING_BASE_URL=http://host.docker.internal:8081
```

本地 llama.cpp 與 Embedding 服務可以繼續繫結 Ubuntu 主機的 `127.0.0.1`；容器透過 `host.docker.internal` 訪問，不需要把模型埠開放到公網。

## 狀態與日誌

```bash
./deploy/self-hosted/status.sh
docker compose --env-file deploy/self-hosted/.env \
  -f deploy/self-hosted/compose.yml logs -f ai-work
```

健康檢查：

```bash
curl http://127.0.0.1:8000/healthz
```

## 備份

```bash
./deploy/self-hosted/backup.sh
```

備份指令碼會短暫停止 AI Work，打包 SQLite、NAS 資產、模型及設定，再重新啟動服務。備份檔案儲存在 `backups/`。

## 升級

將 `AI_WORK_VERSION` 改為目標版本後執行：

```bash
./deploy/self-hosted/update.sh
```

升級指令碼會先備份，再拉取新映象並重建容器。正式版本必須在 Release Notes 中說明不可逆資料庫變更。

## Nginx 與 HTTPS

生產環境不要直接把 8000 埠暴露到網際網路。使用 Nginx 反向代理到 `127.0.0.1:8000`，並配置有效的 TLS 證書。大檔案上傳引數可以參考：

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

Core 啟動不要求本地 LLM、Embedding、Whisper、PaddleOCR 或 YOLO。管理員可以在 Web 後臺配置雲端模型；需要資料留在本地時，再分別部署本地模型服務和可選依賴。
