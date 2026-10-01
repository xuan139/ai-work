"""Generate the latest Traditional Chinese AI Work NAS product sheet."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "AI-Work-NAS-Product-Sheet-ZH-Hant.pdf"

NAVY = colors.HexColor("#153755")
BLUE = colors.HexColor("#2F9FDC")
BLUE_DARK = colors.HexColor("#1672B5")
SKY = colors.HexColor("#EAF6FD")
PALE = colors.HexColor("#F7FAFD")
TEAL = colors.HexColor("#168B80")
TEAL_LIGHT = colors.HexColor("#EAF7F5")
AMBER = colors.HexColor("#A86C00")
AMBER_LIGHT = colors.HexColor("#FFF7E7")
INK = colors.HexColor("#18324A")
MUTED = colors.HexColor("#667D93")
LINE = colors.HexColor("#C9E1F1")
WHITE = colors.white


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("HeitiTC", "/System/Library/Fonts/STHeiti Light.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont("HeitiTCBold", "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0))


def make_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    base = ParagraphStyle(
        "BaseTC",
        parent=styles["BodyText"],
        fontName="HeitiTC",
        fontSize=9.2,
        leading=14.5,
        textColor=INK,
        wordWrap="CJK",
        spaceAfter=4,
    )
    return {
        "base": base,
        "small": ParagraphStyle("SmallTC", parent=base, fontSize=7.7, leading=11.5, textColor=MUTED),
        "tiny": ParagraphStyle("TinyTC", parent=base, fontSize=6.8, leading=9.5, textColor=MUTED),
        "cover_kicker": ParagraphStyle(
            "CoverKicker", parent=base, fontName="HeitiTCBold", fontSize=10,
            leading=14, textColor=BLUE_DARK, spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base, fontName="HeitiTCBold", fontSize=29,
            leading=38, textColor=NAVY, spaceAfter=9,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle", parent=base, fontSize=13.5, leading=21,
            textColor=MUTED, spaceAfter=19,
        ),
        "h1": ParagraphStyle(
            "Heading1TC", parent=base, fontName="HeitiTCBold", fontSize=19,
            leading=27, textColor=NAVY, spaceBefore=2, spaceAfter=9,
        ),
        "h2": ParagraphStyle(
            "Heading2TC", parent=base, fontName="HeitiTCBold", fontSize=12.5,
            leading=18, textColor=BLUE_DARK, spaceBefore=7, spaceAfter=5,
        ),
        "card_title": ParagraphStyle(
            "CardTitleTC", parent=base, fontName="HeitiTCBold", fontSize=9.2,
            leading=13, textColor=BLUE_DARK, spaceAfter=3,
        ),
        "table": ParagraphStyle("TableTC", parent=base, fontSize=7.6, leading=11, spaceAfter=0),
        "table_head": ParagraphStyle(
            "TableHeadTC", parent=base, fontName="HeitiTCBold", fontSize=7.8,
            leading=11, textColor=WHITE, spaceAfter=0,
        ),
        "metric": ParagraphStyle(
            "MetricTC", parent=base, fontName="HeitiTCBold", fontSize=14,
            leading=18, textColor=BLUE_DARK, alignment=TA_CENTER, spaceAfter=2,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabelTC", parent=base, fontSize=7.2, leading=10,
            textColor=MUTED, alignment=TA_CENTER,
        ),
        "callout": ParagraphStyle(
            "CalloutTC", parent=base, fontSize=8.8, leading=14,
            leftIndent=4 * mm, rightIndent=4 * mm, borderColor=TEAL,
            borderWidth=0.8, borderPadding=4 * mm, backColor=TEAL_LIGHT,
            spaceBefore=4, spaceAfter=8,
        ),
        "warning": ParagraphStyle(
            "WarningTC", parent=base, fontSize=8.5, leading=13.5,
            leftIndent=4 * mm, rightIndent=4 * mm, borderColor=AMBER,
            borderWidth=0.8, borderPadding=4 * mm, backColor=AMBER_LIGHT,
            spaceBefore=4, spaceAfter=8,
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullets(items: list[str], styles: dict[str, ParagraphStyle]) -> list[Paragraph]:
    return [
        Paragraph(
            f"- {item}",
            ParagraphStyle(
                f"Bullet{index}", parent=styles["base"], leftIndent=5 * mm,
                firstLineIndent=-3.5 * mm, spaceAfter=3,
            ),
        )
        for index, item in enumerate(items)
    ]


def table(rows, widths, styles, *, header=True, font_size=None) -> Table:
    converted = []
    for row_index, row in enumerate(rows):
        style = styles["table_head"] if header and row_index == 0 else styles["table"]
        if font_size and not (header and row_index == 0):
            style = ParagraphStyle(
                f"Table{row_index}x{font_size}", parent=style, fontSize=font_size,
                leading=font_size + 3,
            )
        converted.append([p(str(cell), style) for cell in row])
    result = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4 * mm),
        ("GRID", (0, 0), (-1, -1), 0.55, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK if header else PALE),
    ]
    if header and len(rows) > 1:
        commands.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]))
    result.setStyle(TableStyle(commands))
    return result


def card_grid(cards, styles, widths=(82 * mm, 82 * mm)) -> Table:
    rows = []
    for index in range(0, len(cards), 2):
        row = []
        for title, body in cards[index:index + 2]:
            row.append([p(title, styles["card_title"]), p(body, styles["small"])])
        while len(row) < 2:
            row.append("")
        rows.append(row)
    result = Table(rows, colWidths=list(widths), hAlign="LEFT")
    result.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.7, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5 * mm),
    ]))
    return result


class PlatformFlow(Flowable):
    def __init__(self, width=170 * mm, height=62 * mm):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        canvas = self.canv
        labels = [
            ("資料入口", "上傳 / LINE / API / NAS 收件", SKY, BLUE_DARK),
            ("多模態處理", "OCR / ASR / Video / Parser", TEAL_LIGHT, TEAL),
            ("企業知識", "Chunk / Embedding / Wiki / Cache", SKY, BLUE_DARK),
            ("AI 與工具", "Local / Cloud LLM / MCP / n8n", PALE, NAVY),
        ]
        gap = 7 * mm
        box_width = (self.width - gap * 3) / 4
        box_height = 34 * mm
        y = 17 * mm
        for index, (title, subtitle, fill, stroke) in enumerate(labels):
            x = index * (box_width + gap)
            canvas.setFillColor(fill)
            canvas.setStrokeColor(stroke)
            canvas.setLineWidth(1.1)
            canvas.roundRect(x, y, box_width, box_height, 2.5 * mm, fill=1, stroke=1)
            canvas.setFillColor(INK)
            canvas.setFont("HeitiTCBold", 9.3)
            canvas.drawCentredString(x + box_width / 2, y + 21 * mm, title)
            canvas.setFillColor(MUTED)
            canvas.setFont("HeitiTC", 6.6)
            canvas.drawCentredString(x + box_width / 2, y + 10.5 * mm, subtitle)
            if index < len(labels) - 1:
                start = x + box_width + 1.1 * mm
                end = x + box_width + gap - 1.1 * mm
                mid = y + box_height / 2
                canvas.setStrokeColor(BLUE_DARK)
                canvas.line(start, mid, end, mid)
                canvas.line(end - 2 * mm, mid + 1.5 * mm, end, mid)
                canvas.line(end - 2 * mm, mid - 1.5 * mm, end, mid)
        canvas.setFillColor(MUTED)
        canvas.setFont("HeitiTC", 7.4)
        canvas.drawCentredString(self.width / 2, 5 * mm, "原始檔、索引、回答、稽核與版本資訊預設保存在客戶 NAS")


class SecurityLayers(Flowable):
    def __init__(self, width=170 * mm, height=73 * mm):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        canvas = self.canv
        layers = [
            ("身分與入口", "帳號角色、Session、Rate Limit、HTTPS", NAVY),
            ("資料權限", "ACL 先於檢索、下載與 Wiki 共用權限", BLUE_DARK),
            ("AI 邊界", "Prompt 檢查、RAG 不可信內容隔離", TEAL),
            ("工具治理", "MCP 白名單、唯讀限制、Schema 驗證", colors.HexColor("#4E7EA5")),
            ("主機與稽核", "systemd 強化、加密備份、安全事件", colors.HexColor("#65798C")),
        ]
        h = 10.5 * mm
        gap = 2.2 * mm
        for index, (title, body, fill) in enumerate(layers):
            y = self.height - (index + 1) * h - index * gap
            canvas.setFillColor(fill)
            canvas.roundRect(0, y, self.width, h, 2 * mm, fill=1, stroke=0)
            canvas.setFillColor(WHITE)
            canvas.setFont("HeitiTCBold", 8.4)
            canvas.drawString(4 * mm, y + 3.5 * mm, title)
            canvas.setFont("HeitiTC", 7.5)
            canvas.drawString(40 * mm, y + 3.5 * mm, body)


def page_decorator(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(BLUE)
    canvas.rect(0, height - 7 * mm, width, 7 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#E8F5FC"))
    canvas.rect(0, 0, width, 13 * mm, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.rect(18 * mm, 11 * mm, 31 * mm, 1.8 * mm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("HeitiTC", 6.8)
    canvas.drawString(20 * mm, 5.2 * mm, "AI Work NAS | 企業資料主權與 AI 工作平台")
    canvas.drawRightString(width - 20 * mm, 5.2 * mm, str(doc.page))
    canvas.restoreState()


def build_story(styles):
    story = []

    # Cover
    story.extend([
        Spacer(1, 31 * mm),
        p("AI WORK NAS PRODUCT SHEET", styles["cover_kicker"]),
        p("AI Work NAS", styles["cover_title"]),
        p("以資料主權、企業知識與受控 AI 為核心的自建工作平台", styles["cover_subtitle"]),
        p(
            "整合 NAS 資產管理、多模態文件處理、Hybrid RAG、企業 Wiki、本地／雲端模型、MCP 工具、LINE 與 n8n 自動化。資料、索引、模型回覆與稽核紀錄預設保存在客戶管理的儲存環境。",
            styles["base"],
        ),
        Spacer(1, 7 * mm),
    ])
    metrics = [
        [p("Local + Cloud", styles["metric"]), p("Hybrid RAG", styles["metric"]), p("7+ 類型", styles["metric"]), p("繁中 / EN", styles["metric"])],
        [p("模型執行策略", styles["metric_label"]), p("跨檔知識檢索", styles["metric_label"]), p("企業檔案支援", styles["metric_label"]), p("操作介面", styles["metric_label"])],
    ]
    metric_table = Table(metrics, colWidths=[42 * mm] * 4)
    metric_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.7, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("TOPPADDING", (0, 0), (-1, 0), 4 * mm),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 3 * mm),
    ]))
    story.extend([
        metric_table,
        Spacer(1, 8 * mm),
        p("NAS 資料主權", styles["h2"]),
        p(
            "原始檔、媒體切片、逐字稿、OCR 文字、頁面預覽、RAG chunks、Embedding、Wiki、模型輸入／輸出、快取、版本與安全事件均由 NAS 保存。只有使用者主動選擇雲端模型或外部 MCP 時，必要內容才會送往指定服務。",
            styles["callout"],
        ),
        card_grid([
            ("企業知識入口", "跨檔搜尋、來源引用、Wiki 與對話整合，將散落資料轉成可追溯知識。"),
            ("多模態工作流", "PDF、DOCX、圖片、音訊、影片、CSV、TSV 與一般文件依類型自動處理。"),
            ("本地優先 AI", "LLM、Embedding、ASR、OCR 與 Video 模型可部署於 NAS，也可依政策使用雲端 API。"),
            ("受控企業整合", "MCP、Odoo、Google、Monday、LINE、n8n 與 Webhook 皆可納入權限及稽核。"),
        ], styles),
        Spacer(1, 8 * mm),
        p("產品版本：2026-10-01　部署型態：Ubuntu 原生單機 Self-hosted Pilot", styles["small"]),
        PageBreak(),
    ])

    # Platform
    story.extend([
        p("01　NAS 為核心的企業 AI 平台", styles["h1"]),
        p("從資料進入、內容解析、知識建庫，到模型與工具執行，全程保留來源、狀態與稽核。", styles["base"]),
        Spacer(1, 3 * mm),
        PlatformFlow(),
        p("資料與媒體處理", styles["h2"]),
        table([
            ["資料類型", "處理能力", "NAS 保存內容"],
            ["PDF / DOCX / 文件", "文字抽取、PyMuPDF 頁面渲染、掃描 PDF OCR、分段與索引", "原始檔、頁碼、chunk 類型、圖片預覽、OCR 結果"],
            ["圖片", "PaddleOCR 文字辨識、圖片預覽與 RAG 建庫", "原圖、辨識文字、索引與引用"],
            ["Audio / 會議", "大檔串流上傳、自動切片、背景 ASR、繁簡轉換、逐字稿", "原音訊、切片、進度、逐字稿、模型紀錄"],
            ["Video", "大檔切片、播放／下載、YOLO 分析與 CPU fallback", "原影片、切片、偵測結果與處理歷程"],
            ["Excel / CSV / TSV", "NAS Excel SQL MCP，以表格與 SQL 方式進行企業資料分析", "來源檔、工具呼叫與查詢結果"],
            ["網路資料", "YouTube 等來源下載後進入音訊／影片處理流程", "下載檔、處理狀態、逐字稿或分析結果"],
        ], [34 * mm, 73 * mm, 61 * mm], styles),
        p("NAS 操作特性", styles["h2"]),
        card_grid([
            ("即時收件與背景工作", "NAS inbox 或網頁上傳後即時顯示狀態；長媒體由 worker 分段處理。"),
            ("可重處理與下載", "每份資產可進入詳情頁播放、查看進度、重跑模型並下載原檔、切片與逐字稿。"),
            ("Storage MCP", "自動辨識 mdadm、ZFS、Btrfs 或硬體 RAID；提供 SSD、容量與健康唯讀工具。"),
            ("完整處理歷程", "每一步記錄解析器、模型、時間、輸入、輸出、呼叫者、狀態及錯誤。"),
        ], styles),
        PageBreak(),
    ])

    # Enterprise knowledge
    story.extend([
        p("02　企業知識、RAG 與治理", styles["h1"]),
        p("AI Work NAS 不只展示 chunks，而是建立可閱讀、可維護、可追溯並受權限控制的企業知識層。", styles["base"]),
        p("第一階段企業 RAG 五項核心能力", styles["h2"]),
        table([
            ["能力", "目前實作", "企業價值"],
            ["權限", "private、group、company；ACL 在檢索前執行，並套用至下載、預覽、Wiki 與 RAG", "防止先取得機密內容再於回答階段過濾"],
            ["跨檔查詢", "對使用者可讀的所有現行版本執行向量相似度＋關鍵字混合檢索", "以一個問題整合多份會議、文件與資料來源"],
            ["版本", "document key、版本號、內容版本、索引版本、取代關係與現行版本", "更新資料不破壞來源追溯及既有引用"],
            ["快取失效", "Prompt、內容、索引、權限摘要與知識庫 revision 共同組成快取條件", "相似問句可重用結果；內容或權限改變時不沿用舊答案"],
            ["評測", "Recall@5、MRR、關鍵字覆蓋、引用有效性、權限洩漏、延遲", "以固定案例追蹤 RAG 品質，而非只靠人工感覺"],
        ], [29 * mm, 83 * mm, 56 * mm], styles),
        p("企業 Wiki", styles["h2"]),
        card_grid([
            ("自動生成與增量更新", "完成處理的文件、音訊、影片與圖片自動形成 Wiki；來源重處理後更新現有頁面與版本。"),
            ("引用與頁面預覽", "回答及 Wiki 顯示檔名、頁碼、chunk 類型與圖片預覽，可返回原始來源核對。"),
            ("權限繼承", "Wiki 不建立旁路權限；頁面可見性繼承 NAS 資產與群組 ACL。"),
            ("全文與向量搜尋", "Embedding 可用時執行 Hybrid Search；服務離線時保留關鍵字搜尋。"),
        ], styles),
        p("回答快取策略", styles["h2"]),
        p(
            "使用者提問前先查詢 NAS 既有模型回答與企業知識。完全相同或語意相近且版本／權限一致時可直接重用；使用者仍可選擇「強制送出」重新呼叫模型。此策略特別用於降低雲端 API 重複費用。",
            styles["callout"],
        ),
        PageBreak(),
    ])

    # Models and integrations
    story.extend([
        p("03　模型、MCP 與企業自動化", styles["h1"]),
        p("管理員在設定與管理區統一決定系統 LLM 與語音模型，使用者不必在每個工作頁面重複選擇。", styles["base"]),
        p("模型執行選擇", styles["h2"]),
        table([
            ["層級", "選項", "適用方式"],
            ["本地 LLM", "llama.cpp / Qwen 等 OpenAI 相容服務", "資料不離開 NAS，適合日常問答、摘要與 MCP 規劃"],
            ["雲端 LLM", "OpenAI、Claude、Gemini、DeepSeek、Qwen 等", "需要公司核准 API Key；輸入／輸出與費用紀錄保存於 NAS"],
            ["Embedding", "Qwen3-Embedding 等本地服務", "語意相似快取、跨檔 Hybrid RAG 與 Wiki 搜尋"],
            ["ASR", "whisper.cpp、faster-whisper、SenseVoice、Paraformer 或雲端 ASR", "本地／雲端政策由管理員設定；長音訊分段背景轉寫"],
            ["OCR / Video", "PaddleOCR、YOLO", "掃描文件、圖片與影片分析；YOLO 非 CPU 失敗時自動回退 CPU"],
        ], [30 * mm, 61 * mm, 77 * mm], styles),
        p("LLM 到企業工具的受控鏈路", styles["h2"]),
        table([
            ["步驟", "執行內容"],
            ["1. 使用者提問", "AI Work 套用身分、權限、Prompt 風險檢查及快取判斷"],
            ["2. LLM 規劃", "模型只能從已同步、啟用且允許的 MCP 工具選擇"],
            ["3. MCP 執行", "後端驗證 Server、唯讀政策與 JSON Schema 參數後呼叫工具"],
            ["4. 最終回答", "工具結果視為不可信資料，由 LLM 整理成答案並保留呼叫稽核"],
        ], [32 * mm, 136 * mm], styles),
        p("企業連接與自動化", styles["h2"]),
        card_grid([
            ("Odoo", "唯讀查詢聯絡人、CRM、銷售、採購、製造、庫存、會計、HR、專案、品質與維修等白名單 Model。"),
            ("Google / PM", "Gmail、Google Drive、Monday、Linear，以及後續 OAuth 型企業連線。"),
            ("LINE", "文件摘要、逐字稿與流程結果可推送企業群組；群組提問受公司管理與稽核。"),
            ("n8n / Webhook", "以事件串接 AI Work、LINE、Email、Odoo 與其他系統，Executions 可查看整條流程。"),
        ], styles),
        PageBreak(),
    ])

    # Security
    story.extend([
        p("04　商用 Pilot 資安基線", styles["h1"]),
        p("核心原則：LLM 不是授權系統。權限、工具範圍、參數、網路與稽核皆由後端程式執行。", styles["base"]),
        Spacer(1, 2 * mm),
        SecurityLayers(),
        p("已內建的產品控制", styles["h2"]),
        card_grid([
            ("Prompt Injection 防護", "攔截覆寫規則、秘密外洩、權限繞過與角色偽造；可疑 RAG chunk 不送入 LLM。"),
            ("MCP 防護", "唯讀工具白名單、Odoo Model 白名單、JSON Schema 參數驗證及完整工具稽核。"),
            ("Web 與帳號", "HttpOnly／SameSite Cookie、HTTPS Secure Cookie、登入與 LLM Rate Limit、安全標頭。"),
            ("主機與備份", "systemd 最小權限、loopback 服務、限制 forwarded IP、備份驗證與可選 AES-256 加密。"),
            ("正式模式閘門", "拒絕弱 APP_SECRET_KEY、預設管理員密碼與非 HTTPS 公開網址。"),
            ("安全事件", "高風險事件記錄雜湊、原因、使用者與來源，不複製可能含機密的 Prompt 原文。"),
        ], styles),
        p("客戶正式資料上線前", styles["h2"]),
        table([
            ["必做項目", "驗收要求"],
            ["網路與身分", "443 對外；8000／8080／8081／5678 僅 loopback；SSH Key；管理入口走 VPN；規劃 SSO／MFA"],
            ["惡意檔案", "ClamAV 或企業端點防護掃描上傳與解壓內容；可疑檔案隔離"],
            ["秘密管理", "API Key／OAuth Token 放 root 限制環境檔或 Vault／KMS，不進 Prompt、SQLite 或 Git"],
            ["營運韌性", "每日加密異機備份、保留政策、實際還原演練、集中日誌與告警"],
            ["驗證", "權限穿透、Prompt Injection、依賴掃描、弱點掃描與外部滲透測試"],
        ], [39 * mm, 129 * mm], styles),
        p(
            "產品已具備客戶 Pilot 所需的應用層基線，但不宣稱取代客戶的端點防護、IAM、SOC、備援或外部資安認證。",
            styles["warning"],
        ),
        PageBreak(),
    ])

    # Deployment
    story.extend([
        p("05　部署、系統需求與 Pilot 範圍", styles["h1"]),
        p("第一版採 Ubuntu 原生部署，不要求 Docker。安裝器建立 Python venv、systemd 服務、持久化 NAS 目錄、隨機 Secret 與一次性管理員密碼。", styles["base"]),
        p("支援基線", styles["h2"]),
        table([
            ["項目", "第一版支援"],
            ["作業系統", "Ubuntu 22.04 LTS / 24.04 LTS，x86_64；ARM64 需另做套件相容性驗證"],
            ["部署", "單機 Self-hosted、systemd、Python 虛擬環境、Nginx HTTPS Reverse Proxy"],
            ["資料庫", "SQLite 單機 Pilot；資料量及並行提高後建議 PostgreSQL + pgvector"],
            ["選配模組", "OCR、Embedding、Whisper／ASR、本地 LLM、YOLO、n8n 與企業 Connectors"],
            ["硬體推薦", "安裝前偵測 CPU、RAM、GPU VRAM 與磁碟空間，再推薦可用本地模型"],
            ["釋出", "授權客戶取得 Ubuntu 安裝包、SHA-256、升級／備份／狀態腳本與版本說明"],
        ], [39 * mm, 129 * mm], styles),
        p("客戶 Pilot 建議流程", styles["h2"]),
        table([
            ["階段", "內容", "完成條件"],
            ["1. 環境盤點", "網域、TLS、CPU／RAM／GPU、容量、備份、Identity 與資料分類", "確認本地／雲端模型政策"],
            ["2. 安裝與預檢", "原生安裝、選配 AI 模組、Reverse Proxy、資安預檢", "security-check 全部 PASS"],
            ["3. 小範圍資料", "選 20 至 100 份可控文件與數個會議錄音", "權限、引用、版本與重處理正確"],
            ["4. RAG 評測", "建立固定問題、預期來源與關鍵字", "無權限洩漏且品質達公司門檻"],
            ["5. 整合驗證", "Odoo／Google／LINE／n8n 只開必要權限", "每次工具呼叫均可追溯"],
            ["6. 上線決策", "還原演練、弱點掃描、外部測試與使用者培訓", "風險接受與責任人簽核"],
        ], [27 * mm, 78 * mm, 63 * mm], styles, font_size=7.2),
        p("正式環境自動預檢", styles["h2"]),
        p(
            "執行：<font name='HeitiTCBold'>sudo /opt/ai-work/deploy/self-hosted/security-check.sh</font><br/>"
            "檢查 production、HTTPS、loopback、Secret、管理員密碼、設定檔權限、systemd、健康端點與 HSTS。",
            styles["callout"],
        ),
        p("授權與產品邊界", styles["h2"]),
        p(
            "本產品採專有授權。Core 不包含大型模型權重、GPU 驅動、第三方商業 API 額度、Kubernetes、多節點高可用或多租戶 SaaS 隔離。Enterprise 擴充可依客戶規模導入 PostgreSQL／pgvector、集中式 Queue、SSO／MFA、Vault／KMS、DLP 與 SIEM。",
            styles["base"],
        ),
        Spacer(1, 5 * mm),
        p("AI Work NAS　企業資料留在可控環境，AI 使用進入可管理流程。", styles["cover_subtitle"]),
    ])
    return story


def main() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=17 * mm,
        bottomMargin=19 * mm,
        title="AI Work NAS 最新產品資料表",
        subject="企業 NAS、多模態 AI、RAG、MCP 與資安基線",
        author="AI Work NAS",
    )
    document.build(build_story(styles), onFirstPage=page_decorator, onLaterPages=page_decorator)
    print(OUTPUT)


if __name__ == "__main__":
    main()
