"""Generate the AI Work NAS September 2026 completion report."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
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
OUTPUT = ROOT / "output" / "pdf" / "AI-Work-NAS-2026年9月已完成工作紀錄-李軒.pdf"

NAVY = colors.HexColor("#163A59")
BLUE = colors.HexColor("#2F9FDC")
BLUE_DARK = colors.HexColor("#1672B5")
SKY = colors.HexColor("#EAF6FD")
PALE = colors.HexColor("#F7FAFD")
TEAL = colors.HexColor("#168B80")
TEAL_LIGHT = colors.HexColor("#EAF7F5")
AMBER = colors.HexColor("#A96C00")
AMBER_LIGHT = colors.HexColor("#FFF7E8")
INK = colors.HexColor("#19334B")
MUTED = colors.HexColor("#667D93")
LINE = colors.HexColor("#C9E1F1")
WHITE = colors.white


def register_fonts() -> None:
    pdfmetrics.registerFont(
        TTFont("HeitiTC", "/System/Library/Fonts/STHeiti Light.ttc", subfontIndex=0)
    )
    pdfmetrics.registerFont(
        TTFont("HeitiTCBold", "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0)
    )


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    base = ParagraphStyle(
        "BaseTC",
        parent=sample["BodyText"],
        fontName="HeitiTC",
        fontSize=9.1,
        leading=14.4,
        textColor=INK,
        wordWrap="CJK",
        spaceAfter=4,
    )
    return {
        "base": base,
        "small": ParagraphStyle(
            "SmallTC", parent=base, fontSize=7.7, leading=11.7, textColor=MUTED
        ),
        "tiny": ParagraphStyle(
            "TinyTC", parent=base, fontSize=6.8, leading=9.8, textColor=MUTED
        ),
        "cover_kicker": ParagraphStyle(
            "CoverKicker",
            parent=base,
            fontName="HeitiTCBold",
            fontSize=10.5,
            leading=15,
            textColor=BLUE_DARK,
            spaceAfter=7,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base,
            fontName="HeitiTCBold",
            fontSize=27,
            leading=36,
            textColor=NAVY,
            spaceAfter=8,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base,
            fontSize=13,
            leading=20,
            textColor=MUTED,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "Heading1TC",
            parent=base,
            fontName="HeitiTCBold",
            fontSize=18,
            leading=26,
            textColor=NAVY,
            spaceBefore=2,
            spaceAfter=9,
        ),
        "h2": ParagraphStyle(
            "Heading2TC",
            parent=base,
            fontName="HeitiTCBold",
            fontSize=12.2,
            leading=18,
            textColor=BLUE_DARK,
            spaceBefore=7,
            spaceAfter=5,
        ),
        "card_title": ParagraphStyle(
            "CardTitleTC",
            parent=base,
            fontName="HeitiTCBold",
            fontSize=9.4,
            leading=13.5,
            textColor=BLUE_DARK,
            spaceAfter=3,
        ),
        "table": ParagraphStyle(
            "TableTC", parent=base, fontSize=7.5, leading=11, spaceAfter=0
        ),
        "table_head": ParagraphStyle(
            "TableHeadTC",
            parent=base,
            fontName="HeitiTCBold",
            fontSize=7.7,
            leading=11,
            textColor=WHITE,
            spaceAfter=0,
        ),
        "metric": ParagraphStyle(
            "MetricTC",
            parent=base,
            fontName="HeitiTCBold",
            fontSize=14.5,
            leading=19,
            textColor=BLUE_DARK,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabelTC",
            parent=base,
            fontSize=7.1,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "callout": ParagraphStyle(
            "CalloutTC",
            parent=base,
            fontSize=8.8,
            leading=14,
            leftIndent=4 * mm,
            rightIndent=4 * mm,
            borderColor=TEAL,
            borderWidth=0.8,
            borderPadding=4 * mm,
            backColor=TEAL_LIGHT,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "note": ParagraphStyle(
            "NoteTC",
            parent=base,
            fontSize=8.3,
            leading=13,
            leftIndent=4 * mm,
            rightIndent=4 * mm,
            borderColor=AMBER,
            borderWidth=0.8,
            borderPadding=4 * mm,
            backColor=AMBER_LIGHT,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "right": ParagraphStyle(
            "RightTC", parent=base, fontSize=8.3, leading=12, alignment=TA_RIGHT
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullets(items: list[str], styles: dict[str, ParagraphStyle]) -> list[Paragraph]:
    return [
        Paragraph(
            f"- {item}",
            ParagraphStyle(
                f"Bullet{index}",
                parent=styles["base"],
                leftIndent=5 * mm,
                firstLineIndent=-3.5 * mm,
                spaceAfter=3,
            ),
        )
        for index, item in enumerate(items)
    ]


def make_table(rows, widths, styles, *, header=True, font_size=None) -> Table:
    converted = []
    for row_index, row in enumerate(rows):
        style = styles["table_head"] if header and row_index == 0 else styles["table"]
        if font_size and not (header and row_index == 0):
            style = ParagraphStyle(
                f"Table{row_index}x{font_size}",
                parent=style,
                fontSize=font_size,
                leading=font_size + 3.2,
            )
        converted.append([p(str(cell), style) for cell in row])
    result = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3 * mm),
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
        for title, body in cards[index : index + 2]:
            row.append([p(title, styles["card_title"]), p(body, styles["small"])])
        while len(row) < 2:
            row.append("")
        rows.append(row)
    result = Table(rows, colWidths=list(widths), hAlign="LEFT")
    result.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.7, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5 * mm),
            ]
        )
    )
    return result


class Timeline(Flowable):
    def __init__(self, width=170 * mm, height=60 * mm):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        canvas = self.canv
        stages = [
            ("9/9-9/10", "核心 Demo", "登入、會議、上傳、RAG、OCR、模型管理"),
            ("9/12-9/20", "企業整合", "LINE、MCP、Odoo、Google、Excel SQL"),
            ("9/21-9/23", "自動化與知識", "全域模型、n8n、企業 Wiki"),
            ("9/26-9/27", "產品化", "Ubuntu 安裝包、硬體推薦、Storage MCP"),
        ]
        gap = 5 * mm
        box_width = (self.width - gap * 3) / 4
        y = 12 * mm
        for index, (date, title, body) in enumerate(stages):
            x = index * (box_width + gap)
            canvas.setFillColor(SKY if index % 2 == 0 else TEAL_LIGHT)
            canvas.setStrokeColor(BLUE_DARK if index % 2 == 0 else TEAL)
            canvas.setLineWidth(1)
            canvas.roundRect(x, y, box_width, 39 * mm, 2.5 * mm, fill=1, stroke=1)
            canvas.setFillColor(BLUE_DARK)
            canvas.setFont("HeitiTCBold", 8)
            canvas.drawString(x + 3 * mm, y + 30 * mm, date)
            canvas.setFillColor(NAVY)
            canvas.setFont("HeitiTCBold", 9)
            canvas.drawString(x + 3 * mm, y + 21 * mm, title)
            canvas.setFillColor(MUTED)
            canvas.setFont("HeitiTC", 6.4)
            for line_index, line in enumerate(body.split("、")):
                canvas.drawString(x + 3 * mm, y + (12 - line_index * 5) * mm, line)
            if index < 3:
                mid = y + 19.5 * mm
                start = x + box_width + 1 * mm
                end = x + box_width + gap - 1 * mm
                canvas.setStrokeColor(BLUE_DARK)
                canvas.line(start, mid, end, mid)
                canvas.line(end - 1.8 * mm, mid + 1.4 * mm, end, mid)
                canvas.line(end - 1.8 * mm, mid - 1.4 * mm, end, mid)


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
    canvas.drawString(20 * mm, 5.2 * mm, "AI Work NAS | 2026 年 9 月已完成工作紀錄")
    canvas.drawRightString(width - 20 * mm, 5.2 * mm, str(doc.page))
    canvas.restoreState()


def build_story(styles):
    story = []

    story.extend(
        [
            Spacer(1, 28 * mm),
            p("AI WORK NAS MONTHLY DELIVERY REPORT", styles["cover_kicker"]),
            p("AI Work NAS<br/>已完成工作紀錄", styles["cover_title"]),
            p("報告期間：2026 年 9 月 1 日至 9 月 30 日", styles["cover_subtitle"]),
            p("負責人：李軒", styles["h2"]),
            p(
                "本報告依據專案 Git 提交紀錄、產品說明與部署檔案整理，紀錄 AI Work NAS 在 2026 年 9 月完成的研發、整合、產品化與交付成果。",
                styles["base"],
            ),
            Spacer(1, 8 * mm),
        ]
    )
    metrics = [
        [
            p("49", styles["metric"]),
            p("35,760", styles["metric"]),
            p("9/9", styles["metric"]),
            p("9/27", styles["metric"]),
        ],
        [
            p("期間 Git 提交", styles["metric_label"]),
            p("新增程式碼行", styles["metric_label"]),
            p("首個 Demo 提交", styles["metric_label"]),
            p("期間最後交付", styles["metric_label"]),
        ],
    ]
    metric_table = Table(metrics, colWidths=[42 * mm] * 4)
    metric_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.7, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("TOPPADDING", (0, 0), (-1, 0), 4 * mm),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 3 * mm),
            ]
        )
    )
    story.extend(
        [
            metric_table,
            Spacer(1, 9 * mm),
            p("月度成果摘要", styles["h2"]),
            p(
                "9 月完成了從概念 Demo 到可在 Ubuntu 原生部署的 AI Work NAS 產品雛形。系統已具備 NAS 檔案收件、多模態處理、會議轉寫、RAG、模型呼叫審計、企業整合、自動化工作流、企業 Wiki 與本地模型管理等核心能力。",
                styles["callout"],
            ),
            card_grid(
                [
                    ("企業 AI 入口", "完成統一 AI Work 門戶、帳號登入、繁體中文與英文介面，以及全域模型配置。"),
                    ("NAS 資料處理", "完成 PDF、DOCX、圖片、音訊、影片和一般檔案的上傳、處理與狀態展示。"),
                    ("企業系統整合", "完成 LINE、Odoo、Gmail、Google Drive、Excel SQL 與 MCP 的主要連線能力。"),
                    ("產品化部署", "完成 Ubuntu 原生安裝、systemd 服務、可選 AI 模組及硬體規格推薦。"),
                ],
                styles,
            ),
            Spacer(1, 8 * mm),
            p("報告狀態：研發完成紀錄　統計來源：Git 歷史與專案文件", styles["small"]),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("01　月度里程碑", styles["h1"]),
            p("9 月的工作按基礎能力、企業整合、自動化知識庫及產品化四個階段推進。", styles["base"]),
            Spacer(1, 4 * mm),
            Timeline(),
            Spacer(1, 4 * mm),
            make_table(
                [
                    ["期間", "完成重點", "代表性交付"],
                    ["9/9-9/10", "核心 Demo 與 NAS 多模態處理", "登入、會議紀錄、模型選擇、上傳入口、文件 RAG、PDF 頁面渲染、PaddleOCR、NAS 模型管理"],
                    ["9/12", "企業工作流與 LINE 治理", "企業 NAS AI 場景、LINE 群組流程、權限及管理入口"],
                    ["9/18-9/20", "MCP 與企業資料連線", "MCP 管理、Odoo 唯讀工具、Gmail、Google Drive、Excel SQL、CSV 與 TSV"],
                    ["9/21", "統一模型與自動化", "系統 LLM/ASR 設定、錄音入口最佳化、n8n 工作區與處理完成回呼"],
                    ["9/23", "企業知識與 Odoo 展示", "自動企業 Wiki、內容清理、Odoo 聯絡人相容及製造企業資料種子"],
                    ["9/26-9/27", "Ubuntu 產品化", "原生 self-hosted 安裝、可選 AI 模組、硬體推薦、Odoo 指南、SSD CLI MCP 與 Storage MCP 方案"],
                ],
                [24 * mm, 46 * mm, 98 * mm],
                styles,
                font_size=7.3,
            ),
            Spacer(1, 8 * mm),
            p("版本與程式碼治理", styles["h2"]),
            *bullets(
                [
                    "專案建立 Git 版本歷史，並持續推送至 GitHub 遠端儲存庫。",
                    "9 月期間累計 49 次提交，變更統計為新增 35,760 行、刪除 1,722 行。",
                    "9 月 18 日採用專有授權條款，明確未經授權不得複製、修改、散佈、託管或商業使用。",
                    "功能以小步提交方式持續驗證，提交紀錄可追溯到具體日期和交付主題。",
                ],
                styles,
            ),
            p(
                "說明：程式碼行統計來自 Git numstat 彙總，用於呈現研發規模，不等同於功能品質或測試覆蓋率。",
                styles["note"],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("02　核心平台與 NAS 能力", styles["h1"]),
            p("本月完成 AI Work NAS 的主要業務入口，並建立檔案進入、處理、儲存、檢索與再次利用的閉環。", styles["base"]),
            p("門戶、帳號與體驗", styles["h2"]),
            *bullets(
                [
                    "完成 FastAPI Web 門戶、身份驗證、管理員與一般帳號基礎能力。",
                    "完成繁體中文介面，並支援切換英文；主視覺統一為藍白企業風格。",
                    "完成 AI Work、會議紀錄、NAS 上傳、模型管理及設定管理等主要選單結構。",
                    "關鍵按鈕及選單加入處理中狀態，降低長任務期間的不確定感。",
                ],
                styles,
            ),
            p("會議錄音與音影片處理", styles["h2"]),
            *bullets(
                [
                    "瀏覽器錄音儲存原始音訊，並進入 NAS 會議歸檔與轉寫流程。",
                    "建立本地與雲端 ASR 目錄，可配置 whisper.cpp、faster-whisper、SenseVoice、Paraformer 及雲端轉寫服務。",
                    "完成大檔案串流上傳、後臺 Worker、長音訊及影片自動切片、切片進度和逐片轉寫能力。",
                    "完成簡體轉繁體 OpenCC 處理、原始音影片播放、分段播放、分段下載及逐字稿下載。",
                    "影片分析支援 YOLO，並加入非 CPU 推理失敗後自動回退 CPU 的路由邏輯。",
                ],
                styles,
            ),
            p("文件、圖片與 RAG", styles["h2"]),
            *bullets(
                [
                    "PDF 以 PyMuPDF 渲染每頁圖片；有文字層時使用 pypdf，掃描件則呼叫 PaddleOCR。",
                    "RAG chunk 儲存頁碼、內容類型及頁面圖片路徑，查詢結果可顯示來源頁碼與預覽。",
                    "圖片檔案進入 OCR 與 RAG 流程；DOCX、文字及一般檔案進入統一 NAS 資產管理。",
                    "音訊逐字稿寫入知識庫，使會議內容能夠與檔案內容採用同一查詢入口。",
                    "完成 Qwen Embedding 連線方案，並使用向量相似度加關鍵字的混合檢索。",
                ],
                styles,
            ),
            p("模型呼叫、快取與審計", styles["h2"]),
            *bullets(
                [
                    "接入本地 Qwen3 4B OpenAI 相容介面，並納入本地與雲端模型下拉選擇。",
                    "模型呼叫無論成功或失敗均紀錄時間、呼叫者、供應商、模型、輸入、輸出與狀態。",
                    "建立相似問題快取，優先查詢 NAS 既有結果，減少重複雲端 API 呼叫。",
                    "提供強制傳送選項，讓使用者可繞過快取重新呼叫模型。",
                    "系統層統一選擇 LLM 與 ASR，其他頁面複用管理員配置。",
                ],
                styles,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("03　企業整合、MCP 與自動化", styles["h1"]),
            p("本月已從單一問答工具擴展為可連線企業資料、協作平台和自動化流程的受控入口。", styles["base"]),
            make_table(
                [
                    ["整合專案", "9 月完成內容", "使用邊界"],
                    ["LINE", "PDF 摘要、會議逐字稿及處理結果推送；企業群組查詢與管理入口", "以企業管理場景為主，保留呼叫紀錄"],
                    ["Odoo MCP", "Goldsys Odoo 唯讀連線、聯絡人查詢修正、Odoo 19 欄位相容、製造企業示範資料", "只讀優先；不允許模型任意修改業務資料"],
                    ["Gmail", "OAuth Token 更新、穩定 REST API 唯讀 MCP、搜尋規範化及最近郵件數量修正", "讀取郵件；控制送入本地模型的上下文長度"],
                    ["Google Drive", "基於 Drive REST API 的本地唯讀 MCP", "使用 drive.readonly 授權"],
                    ["Excel SQL", "NAS Excel SQL MCP，並擴充 XLSX、CSV、TSV 資料查詢", "面向使用者上傳表格的資料分析"],
                    ["Monday / Linear", "企業專案管理 MCP 註冊與只讀連線結構", "統一納入 MCP 管理分類"],
                    ["NAS Demo MCP", "NAS 資源查詢工具及 LLM 到 MCP 再到最終答案的完整鏈路", "工具白名單與審計"],
                ],
                [30 * mm, 91 * mm, 47 * mm],
                styles,
                font_size=7.1,
            ),
            Spacer(1, 8 * mm),
            p("LLM 到 MCP 完整鏈路", styles["h2"]),
            p(
                "使用者提出問題後，系統由當前 LLM 判斷是否需要工具，選擇已啟用的 MCP Server 與唯讀工具，取得企業資料，再由 LLM 結合工具結果生成最終答案。工具輸入、輸出與最終模型呼叫均保留紀錄。",
                styles["callout"],
            ),
            p("n8n 自動化", styles["h2"]),
            *bullets(
                [
                    "完成受保護的 n8n 工作區，並修正子路徑靜態資源代理。",
                    "完成 AI Work NAS 檔案處理工作流：上傳音訊或 PDF 後，由 AI Work 處理，再觸發 n8n Execution。",
                    "完成 n8n 回呼 Token 注入及 HTTPS 保護回呼端點。",
                    "流程可將處理結果回傳 AI Work，並繼續呼叫 LINE 推送服務。",
                    "當 LINE 群組狀態過期時，n8n Execution 仍可正常結束並保留執行紀錄。",
                ],
                styles,
            ),
            p("企業 Wiki", styles["h2"]),
            *bullets(
                [
                    "完成 NAS 已處理資產自動生成企業 Wiki 頁面及既有資料回填。",
                    "完成 Wiki 增量更新、來源引用、全文與向量檢索結構。",
                    "修正舊靜態資源、內容亂碼、重疊顯示與抽取噪聲。",
                    "Wiki 以可閱讀知識頁呈現資料，而不是直接暴露原始 RAG chunks。",
                ],
                styles,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("04　模型管理與 Ubuntu 產品化", styles["h1"]),
            p("9 月底完成第一版可交付產品線與 Ubuntu 原生安裝方式，為客戶自行下載安裝和測試建立基礎。", styles["base"]),
            p("NAS 模型管理", styles["h2"]),
            *bullets(
                [
                    "模型管理獨立為管理員選單，顯示本地模型安裝狀態、檔案大小、下載進度及執行時狀態。",
                    "提供下載、取消和重試操作；模型檔案不完整時不會被識別為已安裝。",
                    "集中管理系統 LLM 與語音模型，實際業務頁面直接使用管理員選擇的優先模型。",
                    "支援本地 Qwen3 4B、Qwen3 Embedding、whisper.cpp 及可擴展的 OCR、ASR、YOLO 能力。",
                ],
                styles,
            ),
            p("Ubuntu 原生 Self-hosted", styles["h2"]),
            *bullets(
                [
                    "完成無需 Docker 的 Ubuntu 22.04/24.04 原生安裝方案。",
                    "安裝器建立 aiwork 系統帳號、Python 虛擬環境、持久化目錄、環境配置與 systemd 服務。",
                    "安裝完成後自動執行健康檢查，並生成隨機 Session Key 與首次管理員密碼。",
                    "提供 Core、Knowledge、Meetings、Complete 與 Custom 安裝方案。",
                    "可選安裝 OCR、Embedding、Whisper 和本地 LLM；核心門戶不依賴這些模型也能啟動。",
                    "提供安裝、狀態檢查、備份及升級指令碼，為後續 GitHub Release 產品包做準備。",
                ],
                styles,
            ),
            p("硬體自動檢測與模型推薦", styles["h2"]),
            *bullets(
                [
                    "檢測 CPU 核心、系統 RAM、可用磁碟、NVIDIA GPU、VRAM 與 CUDA Toolkit。",
                    "依據資源建議 Qwen3 0.6B、1.7B 或 4B 等本地模型，並預留執行空間。",
                    "本地 LLM 與 Embedding 服務預設只繫結 127.0.0.1，避免直接暴露到公網。",
                    "不自動安裝 NVIDIA 驅動或 CUDA，降低安裝器對主機環境的破壞風險。",
                ],
                styles,
            ),
            p("NAS 儲存工具", styles["h2"]),
            *bullets(
                [
                    "完成只讀 NAS SSD CLI MCP，可查詢 SSD/NVMe 裝置、空間使用及 SMART/NVMe 健康狀態。",
                    "工具不接受任意 Shell 指令，不執行格式化、韌體更新、寫入或刪除。",
                    "完成 NAS Storage MCP 擴充方案，規劃自動識別 mdadm、ZFS、Btrfs 或硬體 RAID。",
                ],
                styles,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("05　交付清單與階段結論", styles["h1"]),
            p("截至 2026 年 9 月 30 日，專案已形成可展示、可繼續部署驗證的企業 AI NAS 產品雛形。", styles["base"]),
            make_table(
                [
                    ["交付物", "完成狀態", "說明"],
                    ["AI Work NAS Web Portal", "已完成", "帳號登入、繁中/英文、主要業務選單與藍白企業介面"],
                    ["NAS 多模態資料處理", "已完成", "音訊、影片、PDF、DOCX、圖片及一般檔案處理入口"],
                    ["會議紀錄與逐字稿", "已完成", "錄音、上傳、後臺切片、ASR、播放、下載與知識庫查詢"],
                    ["RAG 與模型呼叫", "已完成", "混合檢索、來源引用、相似問題快取、呼叫審計"],
                    ["企業系統連線", "已完成首階段", "LINE、Odoo、Gmail、Drive、Excel SQL、Monday/Linear 結構"],
                    ["MCP Agent 鏈路", "已完成", "LLM 選工具、執行唯讀 MCP、LLM 生成最終回答"],
                    ["n8n 自動化", "已完成 Demo", "檔案處理完成後建立 Execution 並回調 AI Work/LINE"],
                    ["企業 Wiki", "已完成首階段", "自動生成、增量更新、來源引用及搜尋"],
                    ["Ubuntu 原生安裝包", "已完成首階段", "systemd、自助安裝、可選模組、硬體推薦、備份與升級"],
                    ["專有授權與文件", "已完成", "LICENSE、產品線、安裝指南、Odoo/SSD/Storage MCP 文件"],
                ],
                [54 * mm, 28 * mm, 86 * mm],
                styles,
                font_size=7.2,
            ),
            Spacer(1, 8 * mm),
            p("階段結論", styles["h2"]),
            Spacer(1, 2 * mm),
            p(
                "9 月完成的成果證明 AI Work NAS 已能圍繞 NAS 資料主權建立完整 Demo：資料進入 NAS 後，可由本地或雲端模型處理，形成逐字稿、RAG、Wiki 與企業查詢結果，並透過 MCP、LINE 與 n8n 對接外部流程。月底進一步完成 Ubuntu 原生安裝及硬體推薦，使專案從開發環境邁入可交付測試階段。",
                styles["callout"],
            ),
            p("後續階段建議", styles["h2"]),
            *bullets(
                [
                    "建立正式版本號、簽名安裝包與 GitHub Release 校驗流程。",
                    "擴大跨使用者權限、審計分頁、Prompt Injection 防護及企業安全驗收。",
                    "補齊生產監控、備份還原、依賴掃描與外部滲透測試。",
                ],
                styles,
            ),
            Spacer(1, 5 * mm),
            p(
                "本報告僅紀錄 2026 年 9 月 1 日至 9 月 30 日期間已經提交或形成文件的成果。正式商業上線仍需完成生產環境安全、效能、備份與運維驗收。",
                styles["note"],
            ),
            Spacer(1, 3 * mm),
            make_table(
                [
                    ["專案", "內容"],
                    ["專案名稱", "AI Work NAS"],
                    ["報告期間", "2026 年 9 月 1 日至 9 月 30 日"],
                    ["負責人", "李軒"],
                    ["報告資訊", "月度研發與交付完成紀錄 | 整理日期：2026 年 10 月 5 日"],
                ],
                [45 * mm, 123 * mm],
                styles,
                font_size=7.0,
            ),
            Spacer(1, 4 * mm),
            p("負責人：李軒", styles["right"]),
        ]
    )
    return story


def main() -> None:
    register_fonts()
    styles = make_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
        title="AI Work NAS 2026 年 9 月已完成工作紀錄",
        author="李軒",
        subject="AI Work NAS 月度研發與交付完成紀錄",
    )
    doc.build(build_story(styles), onFirstPage=page_decorator, onLaterPages=page_decorator)
    print(OUTPUT)


if __name__ == "__main__":
    main()
