# AI Work NAS 產品線方案

## 產品定位

AI Work NAS 是部署在客戶自有 Ubuntu 伺服器或 NAS 主機上的企業 AI 入口。原始檔案、索引、Wiki、模型呼叫記錄和工具審計預設儲存在客戶管理的儲存空間；客戶可以選擇本地模型，或配置經過公司批准的雲端模型。

## 第一版產品線

### AI Work Core Self-hosted

第一版只發佈一個可獨立安裝的 Core 產品，降低客戶選型和維護複雜度。

包含：

- 企業賬號與管理員許可權。
- AI Work 統一問答入口。
- 本地模型與雲端 API 配置。
- NAS 檔案上傳、資產總覽和企業 Wiki。
- PDF、DOCX、文字、圖片、音訊和影片的基礎處理入口。
- RAG、回答快取、來源引用和模型呼叫審計。
- MCP 管理與內建 NAS、Excel SQL 工具。
- Odoo、Gmail、Google Drive、Monday 等連線配置入口。
- LINE 與 n8n 整合介面。
- 繁體中文與英文介面。

預設不包含大型模型權重、GPU 驅動或第三方商業 API 額度。

### 可選能力包

以下能力與 Core 解耦，客戶有需要時再安裝：

| 能力包 | 內容 | 基礎要求 |
| --- | --- | --- |
| Local LLM | llama.cpp、Qwen 等本地問答模型 | 依模型決定 CPU/GPU 與記憶體 |
| Embedding | Qwen3-Embedding 本地向量服務 | CPU 可執行，建議獨立服務 |
| Speech | whisper.cpp、faster-whisper、SenseVoice | FFmpeg；GPU 可選 |
| OCR | PaddleOCR 掃描 PDF 與圖片識別 | Python 擴充套件與模型空間 |
| Video | YOLO 影片物件分析 | CPU 可執行，GPU 建議 |
| Automation | n8n 固定跨系統流程 | Docker、獨立資料庫建議 |
| Enterprise Connectors | Odoo、Google、Monday、LINE 等 | 對應賬號、API 或 OAuth 授權 |

## 釋出方式

每個版本由 GitHub Release 提供：

1. `ai-work-VERSION-ubuntu.tar.gz` 安裝包。
2. 對應 SHA-256 校驗檔案。
3. `ghcr.io/xuan139/ai-work:VERSION` 容器映象。
4. 版本說明和升級注意事項。

本專案採用專有授權。公開 GitHub 倉庫的 Release 無法限制下載者；商業釋出應使用私有 GitHub 倉庫、客戶專用倉庫或需要登入的下載門戶，並在合同中授予客戶指定伺服器的安裝權。

## 支援邊界

第一版支援：

- Ubuntu 22.04 LTS 和 24.04 LTS。
- Docker Engine 與 Docker Compose v2。
- 單機部署。
- x86_64；ARM64 映象需在釋出流程中另行驗證。
- SQLite 作為 Core 單機資料庫。

第一版暫不承諾：

- Kubernetes 叢集。
- 多節點高可用。
- 自動安裝 NVIDIA 驅動。
- 自動購買或管理第三方 API 額度。
- 多租戶 SaaS 隔離。

當客戶數量、併發或資料規模提高後，再提供 PostgreSQL/pgvector、持久化任務佇列、SSO 和集中可觀測性的 Enterprise 部署方案。
