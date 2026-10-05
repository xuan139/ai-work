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
OUTPUT = ROOT / "output" / "pdf" / "AI-Work-NAS-2026年9月已完成工作记录-李轩.pdf"

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
    canvas.drawString(20 * mm, 5.2 * mm, "AI Work NAS | 2026 年 9 月已完成工作记录")
    canvas.drawRightString(width - 20 * mm, 5.2 * mm, str(doc.page))
    canvas.restoreState()


def build_story(styles):
    story = []

    story.extend(
        [
            Spacer(1, 28 * mm),
            p("AI WORK NAS MONTHLY DELIVERY REPORT", styles["cover_kicker"]),
            p("AI Work NAS<br/>已完成工作记录", styles["cover_title"]),
            p("报告期间：2026 年 9 月 1 日至 9 月 30 日", styles["cover_subtitle"]),
            p("负责人：李轩", styles["h2"]),
            p(
                "本报告依据项目 Git 提交记录、产品说明与部署文件整理，记录 AI Work NAS 在 2026 年 9 月完成的研发、整合、产品化与交付成果。",
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
            p("期间 Git 提交", styles["metric_label"]),
            p("新增代码行", styles["metric_label"]),
            p("首个 Demo 提交", styles["metric_label"]),
            p("期间最后交付", styles["metric_label"]),
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
                "9 月完成了从概念 Demo 到可在 Ubuntu 原生部署的 AI Work NAS 产品雏形。系统已具备 NAS 文件收件、多模态处理、会议转写、RAG、模型调用审计、企业整合、自动化工作流、企业 Wiki 与本地模型管理等核心能力。",
                styles["callout"],
            ),
            card_grid(
                [
                    ("企业 AI 入口", "完成统一 AI Work 门户、账号登录、繁体中文与英文界面，以及全域模型配置。"),
                    ("NAS 数据处理", "完成 PDF、DOCX、图片、音频、视频和一般文件的上传、处理与状态展示。"),
                    ("企业系统整合", "完成 LINE、Odoo、Gmail、Google Drive、Excel SQL 与 MCP 的主要连接能力。"),
                    ("产品化部署", "完成 Ubuntu 原生安装、systemd 服务、可选 AI 模块及硬件规格推荐。"),
                ],
                styles,
            ),
            Spacer(1, 8 * mm),
            p("报告状态：研发完成记录　统计来源：Git 历史与项目文档", styles["small"]),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("01　月度里程碑", styles["h1"]),
            p("9 月的工作按基础能力、企业整合、自动化知识库及产品化四个阶段推进。", styles["base"]),
            Spacer(1, 4 * mm),
            Timeline(),
            Spacer(1, 4 * mm),
            make_table(
                [
                    ["期间", "完成重点", "代表性交付"],
                    ["9/9-9/10", "核心 Demo 与 NAS 多模态处理", "登录、会议记录、模型选择、上传入口、文档 RAG、PDF 页面渲染、PaddleOCR、NAS 模型管理"],
                    ["9/12", "企业工作流与 LINE 治理", "企业 NAS AI 场景、LINE 群组流程、权限及管理入口"],
                    ["9/18-9/20", "MCP 与企业数据连接", "MCP 管理、Odoo 唯读工具、Gmail、Google Drive、Excel SQL、CSV 与 TSV"],
                    ["9/21", "统一模型与自动化", "系统 LLM/ASR 设置、录音入口优化、n8n 工作区与处理完成回调"],
                    ["9/23", "企业知识与 Odoo 展示", "自动企业 Wiki、内容清理、Odoo 联系人兼容及制造企业数据种子"],
                    ["9/26-9/27", "Ubuntu 产品化", "原生 self-hosted 安装、可选 AI 模块、硬件推荐、Odoo 指南、SSD CLI MCP 与 Storage MCP 方案"],
                ],
                [24 * mm, 46 * mm, 98 * mm],
                styles,
                font_size=7.3,
            ),
            Spacer(1, 8 * mm),
            p("版本与代码治理", styles["h2"]),
            *bullets(
                [
                    "项目建立 Git 版本历史，并持续推送至 GitHub 远端仓库。",
                    "9 月期间累计 49 次提交，变更统计为新增 35,760 行、删除 1,722 行。",
                    "9 月 18 日采用专有授权条款，明确未经授权不得复制、修改、散布、托管或商业使用。",
                    "功能以小步提交方式持续验证，提交记录可追溯到具体日期和交付主题。",
                ],
                styles,
            ),
            p(
                "说明：代码行统计来自 Git numstat 汇总，用于呈现研发规模，不等同于功能质量或测试覆盖率。",
                styles["note"],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("02　核心平台与 NAS 能力", styles["h1"]),
            p("本月完成 AI Work NAS 的主要业务入口，并建立文件进入、处理、保存、检索与再次利用的闭环。", styles["base"]),
            p("门户、账号与体验", styles["h2"]),
            *bullets(
                [
                    "完成 FastAPI Web 门户、身份验证、管理员与一般账号基础能力。",
                    "完成繁体中文界面，并支持切换英文；主视觉统一为蓝白企业风格。",
                    "完成 AI Work、会议记录、NAS 上传、模型管理及设置管理等主要菜单结构。",
                    "关键按钮及菜单加入处理中状态，降低长任务期间的不确定感。",
                ],
                styles,
            ),
            p("会议录音与音视频处理", styles["h2"]),
            *bullets(
                [
                    "浏览器录音保存原始音频，并进入 NAS 会议归档与转写流程。",
                    "建立本地与云端 ASR 目录，可配置 whisper.cpp、faster-whisper、SenseVoice、Paraformer 及云端转写服务。",
                    "完成大文件串流上传、后台 Worker、长音频及视频自动切片、切片进度和逐片转写能力。",
                    "完成简体转繁体 OpenCC 处理、原始音视频播放、分段播放、分段下载及逐字稿下载。",
                    "视频分析支持 YOLO，并加入非 CPU 推理失败后自动回退 CPU 的路由逻辑。",
                ],
                styles,
            ),
            p("文档、图片与 RAG", styles["h2"]),
            *bullets(
                [
                    "PDF 以 PyMuPDF 渲染每页图片；有文字层时使用 pypdf，扫描件则调用 PaddleOCR。",
                    "RAG chunk 保存页码、内容类型及页面图片路径，查询结果可显示来源页码与预览。",
                    "图片文件进入 OCR 与 RAG 流程；DOCX、文字及一般文件进入统一 NAS 资产管理。",
                    "音频逐字稿写入知识库，使会议内容能够与文件内容采用同一查询入口。",
                    "完成 Qwen Embedding 连接方案，并使用向量相似度加关键字的混合检索。",
                ],
                styles,
            ),
            p("模型调用、快取与审计", styles["h2"]),
            *bullets(
                [
                    "接入本地 Qwen3 4B OpenAI 兼容接口，并纳入本地与云端模型下拉选择。",
                    "模型调用无论成功或失败均记录时间、调用者、供应商、模型、输入、输出与状态。",
                    "建立相似问题快取，优先查询 NAS 既有结果，减少重复云端 API 调用。",
                    "提供强制发送选项，让使用者可绕过快取重新调用模型。",
                    "系统层统一选择 LLM 与 ASR，其他页面复用管理员配置。",
                ],
                styles,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("03　企业整合、MCP 与自动化", styles["h1"]),
            p("本月已从单一问答工具扩展为可连接企业资料、协作平台和自动化流程的受控入口。", styles["base"]),
            make_table(
                [
                    ["整合项目", "9 月完成内容", "使用边界"],
                    ["LINE", "PDF 摘要、会议逐字稿及处理结果推送；企业群组查询与管理入口", "以企业管理场景为主，保留调用记录"],
                    ["Odoo MCP", "Goldsys Odoo 唯读连接、联系人查询修正、Odoo 19 字段兼容、制造企业示范数据", "只读优先；不允许模型任意修改业务资料"],
                    ["Gmail", "OAuth Token 更新、稳定 REST API 唯读 MCP、搜索规范化及最近邮件数量修正", "读取邮件；控制送入本地模型的上下文长度"],
                    ["Google Drive", "基于 Drive REST API 的本地唯读 MCP", "使用 drive.readonly 授权"],
                    ["Excel SQL", "NAS Excel SQL MCP，并扩充 XLSX、CSV、TSV 数据查询", "面向用户上传表格的数据分析"],
                    ["Monday / Linear", "企业项目管理 MCP 注册与只读连接结构", "统一纳入 MCP 管理分类"],
                    ["NAS Demo MCP", "NAS 资源查询工具及 LLM 到 MCP 再到最终答案的完整链路", "工具白名单与审计"],
                ],
                [30 * mm, 91 * mm, 47 * mm],
                styles,
                font_size=7.1,
            ),
            Spacer(1, 8 * mm),
            p("LLM 到 MCP 完整链路", styles["h2"]),
            p(
                "使用者提出问题后，系统由当前 LLM 判断是否需要工具，选择已启用的 MCP Server 与唯读工具，取得企业资料，再由 LLM 结合工具结果生成最终答案。工具输入、输出与最终模型调用均保留记录。",
                styles["callout"],
            ),
            p("n8n 自动化", styles["h2"]),
            *bullets(
                [
                    "完成受保护的 n8n 工作区，并修正子路径静态资源代理。",
                    "完成 AI Work NAS 文件处理工作流：上传音频或 PDF 后，由 AI Work 处理，再触发 n8n Execution。",
                    "完成 n8n 回调 Token 注入及 HTTPS 保护回调端点。",
                    "流程可将处理结果回传 AI Work，并继续调用 LINE 推送服务。",
                    "当 LINE 群组状态过期时，n8n Execution 仍可正常结束并保留执行记录。",
                ],
                styles,
            ),
            p("企业 Wiki", styles["h2"]),
            *bullets(
                [
                    "完成 NAS 已处理资产自动生成企业 Wiki 页面及既有资料回填。",
                    "完成 Wiki 增量更新、来源引用、全文与向量检索结构。",
                    "修正旧静态资源、内容乱码、重叠显示与抽取噪声。",
                    "Wiki 以可阅读知识页呈现资料，而不是直接暴露原始 RAG chunks。",
                ],
                styles,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("04　模型管理与 Ubuntu 产品化", styles["h1"]),
            p("9 月底完成第一版可交付产品线与 Ubuntu 原生安装方式，为客户自行下载安装和测试建立基础。", styles["base"]),
            p("NAS 模型管理", styles["h2"]),
            *bullets(
                [
                    "模型管理独立为管理员菜单，显示本地模型安装状态、文件大小、下载进度及运行时状态。",
                    "提供下载、取消和重试操作；模型文件不完整时不会被识别为已安装。",
                    "集中管理系统 LLM 与语音模型，实际业务页面直接使用管理员选择的优先模型。",
                    "支持本地 Qwen3 4B、Qwen3 Embedding、whisper.cpp 及可扩展的 OCR、ASR、YOLO 能力。",
                ],
                styles,
            ),
            p("Ubuntu 原生 Self-hosted", styles["h2"]),
            *bullets(
                [
                    "完成无需 Docker 的 Ubuntu 22.04/24.04 原生安装方案。",
                    "安装器建立 aiwork 系统账号、Python 虚拟环境、持久化目录、环境配置与 systemd 服务。",
                    "安装完成后自动执行健康检查，并生成随机 Session Key 与首次管理员密码。",
                    "提供 Core、Knowledge、Meetings、Complete 与 Custom 安装方案。",
                    "可选安装 OCR、Embedding、Whisper 和本地 LLM；核心门户不依赖这些模型也能启动。",
                    "提供安装、状态检查、备份及升级脚本，为后续 GitHub Release 产品包做准备。",
                ],
                styles,
            ),
            p("硬件自动检测与模型推荐", styles["h2"]),
            *bullets(
                [
                    "检测 CPU 核心、系统 RAM、可用磁盘、NVIDIA GPU、VRAM 与 CUDA Toolkit。",
                    "依据资源建议 Qwen3 0.6B、1.7B 或 4B 等本地模型，并预留运行空间。",
                    "本地 LLM 与 Embedding 服务默认只绑定 127.0.0.1，避免直接暴露到公网。",
                    "不自动安装 NVIDIA 驱动或 CUDA，降低安装器对主机环境的破坏风险。",
                ],
                styles,
            ),
            p("NAS 存储工具", styles["h2"]),
            *bullets(
                [
                    "完成只读 NAS SSD CLI MCP，可查询 SSD/NVMe 设备、空间使用及 SMART/NVMe 健康状态。",
                    "工具不接受任意 Shell 指令，不执行格式化、固件更新、写入或删除。",
                    "完成 NAS Storage MCP 扩充方案，规划自动识别 mdadm、ZFS、Btrfs 或硬件 RAID。",
                ],
                styles,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("05　交付清单与阶段结论", styles["h1"]),
            p("截至 2026 年 9 月 30 日，项目已形成可展示、可继续部署验证的企业 AI NAS 产品雏形。", styles["base"]),
            make_table(
                [
                    ["交付物", "完成状态", "说明"],
                    ["AI Work NAS Web Portal", "已完成", "账号登录、繁中/英文、主要业务菜单与蓝白企业界面"],
                    ["NAS 多模态资料处理", "已完成", "音频、视频、PDF、DOCX、图片及一般文件处理入口"],
                    ["会议记录与逐字稿", "已完成", "录音、上传、后台切片、ASR、播放、下载与知识库查询"],
                    ["RAG 与模型调用", "已完成", "混合检索、来源引用、相似问题快取、调用审计"],
                    ["企业系统连接", "已完成首阶段", "LINE、Odoo、Gmail、Drive、Excel SQL、Monday/Linear 结构"],
                    ["MCP Agent 链路", "已完成", "LLM 选工具、执行唯读 MCP、LLM 生成最终回答"],
                    ["n8n 自动化", "已完成 Demo", "文件处理完成后建立 Execution 并回调 AI Work/LINE"],
                    ["企业 Wiki", "已完成首阶段", "自动生成、增量更新、来源引用及搜索"],
                    ["Ubuntu 原生安装包", "已完成首阶段", "systemd、自助安装、可选模块、硬件推荐、备份与升级"],
                    ["专有授权与文档", "已完成", "LICENSE、产品线、安装指南、Odoo/SSD/Storage MCP 文档"],
                ],
                [54 * mm, 28 * mm, 86 * mm],
                styles,
                font_size=7.2,
            ),
            Spacer(1, 8 * mm),
            p("阶段结论", styles["h2"]),
            Spacer(1, 2 * mm),
            p(
                "9 月完成的成果证明 AI Work NAS 已能围绕 NAS 数据主权建立完整 Demo：资料进入 NAS 后，可由本地或云端模型处理，形成逐字稿、RAG、Wiki 与企业查询结果，并通过 MCP、LINE 与 n8n 对接外部流程。月底进一步完成 Ubuntu 原生安装及硬件推荐，使项目从开发环境迈入可交付测试阶段。",
                styles["callout"],
            ),
            p("后续阶段建议", styles["h2"]),
            *bullets(
                [
                    "建立正式版本号、签名安装包与 GitHub Release 校验流程。",
                    "扩大跨用户权限、审计分页、Prompt Injection 防护及企业安全验收。",
                    "补齐生产监控、备份还原、依赖扫描与外部渗透测试。",
                ],
                styles,
            ),
            Spacer(1, 5 * mm),
            p(
                "本报告仅记录 2026 年 9 月 1 日至 9 月 30 日期间已经提交或形成文档的成果。正式商业上线仍需完成生产环境安全、性能、备份与运维验收。",
                styles["note"],
            ),
            Spacer(1, 3 * mm),
            make_table(
                [
                    ["项目", "内容"],
                    ["项目名称", "AI Work NAS"],
                    ["报告期间", "2026 年 9 月 1 日至 9 月 30 日"],
                    ["负责人", "李轩"],
                    ["报告信息", "月度研发与交付完成记录 | 整理日期：2026 年 10 月 5 日"],
                ],
                [45 * mm, 123 * mm],
                styles,
                font_size=7.0,
            ),
            Spacer(1, 4 * mm),
            p("负责人：李轩", styles["right"]),
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
        title="AI Work NAS 2026 年 9 月已完成工作记录",
        author="李轩",
        subject="AI Work NAS 月度研发与交付完成记录",
    )
    doc.build(build_story(styles), onFirstPage=page_decorator, onLaterPages=page_decorator)
    print(OUTPUT)


if __name__ == "__main__":
    main()
