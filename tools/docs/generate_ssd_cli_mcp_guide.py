"""Generate the Traditional Chinese NAS SSD CLI MCP deployment guide."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
OUTPUT = ROOT / "output" / "pdf" / "AI-Work-NAS-SSD-CLI-MCP-部署與操作指南.pdf"

NAVY = colors.HexColor("#163A5F")
BLUE = colors.HexColor("#2F9DDB")
BLUE_DARK = colors.HexColor("#176EA8")
BLUE_LIGHT = colors.HexColor("#EAF6FD")
PALE = colors.HexColor("#F6FAFE")
TEAL = colors.HexColor("#168A80")
TEAL_LIGHT = colors.HexColor("#EAF7F5")
INK = colors.HexColor("#18324A")
MUTED = colors.HexColor("#62788E")
LINE = colors.HexColor("#C7DFEF")
WHITE = colors.white
AMBER = colors.HexColor("#A46A00")
AMBER_LIGHT = colors.HexColor("#FFF7E8")


def register_fonts() -> None:
    pdfmetrics.registerFont(
        TTFont("HeitiTC", "/System/Library/Fonts/STHeiti Light.ttc", subfontIndex=0)
    )
    pdfmetrics.registerFont(
        TTFont("HeitiTCBold", "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0)
    )


class ArchitectureFlow(Flowable):
    def __init__(self, width: float = 170 * mm, height: float = 68 * mm):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        canvas = self.canv
        labels = [
            ("AI Work / LLM", "自然語言提問", BLUE_LIGHT, BLUE_DARK),
            ("MCP Gateway", "Bearer 驗證與工具白名單", TEAL_LIGHT, TEAL),
            ("SSD CLI", "固定唯讀命令", BLUE_LIGHT, BLUE_DARK),
            ("Ubuntu NAS", "lsblk / df / SMART / NVMe", PALE, NAVY),
        ]
        gap = 7 * mm
        box_width = (self.width - gap * 3) / 4
        y = 15 * mm
        box_height = 37 * mm
        for index, (title, subtitle, fill, stroke) in enumerate(labels):
            x = index * (box_width + gap)
            canvas.setFillColor(fill)
            canvas.setStrokeColor(stroke)
            canvas.setLineWidth(1.2)
            canvas.roundRect(x, y, box_width, box_height, 3 * mm, fill=1, stroke=1)
            canvas.setFillColor(INK)
            canvas.setFont("HeitiTCBold", 10)
            canvas.drawCentredString(x + box_width / 2, y + 23 * mm, title)
            canvas.setFillColor(MUTED)
            canvas.setFont("HeitiTC", 7.4)
            canvas.drawCentredString(x + box_width / 2, y + 12 * mm, subtitle)
            if index < len(labels) - 1:
                start = x + box_width + 1 * mm
                end = x + box_width + gap - 1 * mm
                mid = y + box_height / 2
                canvas.setStrokeColor(BLUE_DARK)
                canvas.setLineWidth(1.5)
                canvas.line(start, mid, end, mid)
                canvas.line(end - 2 * mm, mid + 1.6 * mm, end, mid)
                canvas.line(end - 2 * mm, mid - 1.6 * mm, end, mid)
        canvas.setFillColor(MUTED)
        canvas.setFont("HeitiTC", 7.8)
        canvas.drawString(0, 4 * mm, "回傳：結構化 JSON、來源裝置、容量、健康、溫度與耗損指標")


def make_styles():
    styles = getSampleStyleSheet()
    base = ParagraphStyle(
        "BaseTC",
        parent=styles["BodyText"],
        fontName="HeitiTC",
        fontSize=9.5,
        leading=15,
        textColor=INK,
        spaceAfter=4,
        wordWrap="CJK",
    )
    return {
        "base": base,
        "cover_kicker": ParagraphStyle(
            "CoverKicker", parent=base, fontName="HeitiTCBold", fontSize=10,
            leading=14, textColor=BLUE_DARK, spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base, fontName="HeitiTCBold", fontSize=27,
            leading=36, textColor=NAVY, spaceAfter=12,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle", parent=base, fontSize=12.5, leading=20,
            textColor=MUTED, spaceAfter=22,
        ),
        "h1": ParagraphStyle(
            "Heading1TC", parent=base, fontName="HeitiTCBold", fontSize=18,
            leading=25, textColor=NAVY, spaceBefore=4, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "Heading2TC", parent=base, fontName="HeitiTCBold", fontSize=12.5,
            leading=18, textColor=BLUE_DARK, spaceBefore=9, spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "SmallTC", parent=base, fontSize=8, leading=12.5, textColor=MUTED,
        ),
        "table": ParagraphStyle(
            "TableTC", parent=base, fontSize=8, leading=11.5, spaceAfter=0,
        ),
        "table_head": ParagraphStyle(
            "TableHeadTC", parent=base, fontName="HeitiTCBold", fontSize=8,
            leading=11, textColor=WHITE, spaceAfter=0,
        ),
        "code": ParagraphStyle(
            "CodeTC", parent=base, fontName="HeitiTC", fontSize=7.4,
            leading=11, leftIndent=3 * mm, rightIndent=3 * mm,
            borderColor=LINE, borderWidth=0.8, borderPadding=3 * mm,
            backColor=PALE, spaceBefore=3, spaceAfter=6,
        ),
        "callout": ParagraphStyle(
            "CalloutTC", parent=base, fontSize=9.2, leading=14.5,
            leftIndent=4 * mm, rightIndent=4 * mm, borderColor=BLUE,
            borderWidth=0.8, borderPadding=4 * mm, backColor=BLUE_LIGHT,
            spaceBefore=4, spaceAfter=8,
        ),
        "warning": ParagraphStyle(
            "WarningTC", parent=base, fontSize=9, leading=14,
            leftIndent=4 * mm, rightIndent=4 * mm, borderColor=AMBER,
            borderWidth=0.8, borderPadding=4 * mm, backColor=AMBER_LIGHT,
            spaceBefore=4, spaceAfter=8,
        ),
        "center": ParagraphStyle(
            "CenterTC", parent=base, alignment=TA_CENTER,
        ),
    }


def p(text: str, style) -> Paragraph:
    return Paragraph(text, style)


def bullet(items: list[str], styles) -> list[Paragraph]:
    return [
        Paragraph(f"- {item}", ParagraphStyle(
            f"Bullet{index}", parent=styles["base"], leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm, spaceAfter=3,
        ))
        for index, item in enumerate(items)
    ]


def styled_table(rows, widths, styles, *, header: bool = True) -> Table:
    converted = []
    for row_index, row in enumerate(rows):
        style = styles["table_head"] if header and row_index == 0 else styles["table"]
        converted.append([cell if isinstance(cell, Flowable) else p(str(cell), style) for cell in row])
    table = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("BACKGROUND", (0, 1 if header else 0), (-1, -1), WHITE),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for index in range(1 if header else 0, len(rows)):
        if index % 2 == 0:
            commands.append(("BACKGROUND", (0, index), (-1, index), PALE))
    table.setStyle(TableStyle(commands))
    return table


def card(title: str, body: str, styles, color=BLUE_LIGHT) -> Table:
    table = Table(
        [[p(title, styles["h2"]), p(body, styles["base"])]],
        colWidths=[46 * mm, 116 * mm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def page_frame(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(19 * mm, height - 15 * mm, width - 19 * mm, height - 15 * mm)
    canvas.setFillColor(BLUE_DARK)
    canvas.setFont("HeitiTCBold", 8)
    canvas.drawString(19 * mm, height - 11 * mm, "AI Work NAS  |  SSD CLI MCP")
    canvas.setFillColor(MUTED)
    canvas.setFont("HeitiTC", 7.5)
    canvas.drawRightString(width - 19 * mm, 10 * mm, f"部署與操作指南  |  {doc.page}")
    canvas.restoreState()


def build_pdf() -> None:
    register_fonts()
    styles = make_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=23 * mm, bottomMargin=18 * mm,
        title="AI Work NAS SSD CLI MCP 部署與操作指南",
        author="Goldsys AI Work",
        subject="NAS SSD 唯讀 CLI 與 MCP 部署文件",
    )
    story = []

    story.extend([
        Spacer(1, 18 * mm),
        p("GOLDSYS · AI WORK NAS", styles["cover_kicker"]),
        p("NAS SSD CLI MCP<br/>部署與操作指南", styles["cover_title"]),
        p("讓本地 LLM 以受控、唯讀方式查詢 Ubuntu NAS 的 SSD 清單、容量使用率與 SMART / NVMe 健康狀態。", styles["cover_subtitle"]),
        ArchitectureFlow(),
        Spacer(1, 9 * mm),
        styled_table([
            ["文件版本", "部署版本", "驗證日期"],
            ["1.0", "Git commit f42d073", "2026-09-27"],
        ], [45 * mm, 72 * mm, 45 * mm], styles),
        Spacer(1, 7 * mm),
        p("安全定位", styles["h2"]),
        p("此功能不是通用 shell。所有操作由固定工具白名單、裝置路徑驗證、Bearer 驗證與 root-owned helper 共同限制；不提供格式化、刪除、寫入、韌體更新或任意指令執行。", styles["callout"]),
        PageBreak(),
    ])

    story.extend([
        p("1. 功能總覽", styles["h1"]),
        p("NAS SSD CLI MCP 將 Linux 原生磁碟工具包裝成可被 AI Work、LLM 與 Agent 呼叫的結構化唯讀服務。使用者可用自然語言詢問容量、健康與耗損，模型不需要直接取得作業系統 shell 權限。", styles["base"]),
        Spacer(1, 3 * mm),
        card("裝置盤點", "辨識實體非旋轉式磁碟與 NVMe，回傳型號、容量、介面、分割區、檔案系統及掛載點。", styles),
        Spacer(1, 3 * mm),
        card("容量監控", "只統計由已辨識 SSD 承載的檔案系統，包含 LVM 根磁碟、/boot 與 /boot/efi。", styles, TEAL_LIGHT),
        Spacer(1, 3 * mm),
        card("健康檢查", "透過 smartctl 或 nvme-cli 取得健康、溫度、通電時數、耗損、備援、非正常關機與媒體錯誤。", styles),
        p("適用情境", styles["h2"]),
        *bullet([
            "管理者詢問 NAS 儲存狀態，例如：目前 SSD 使用多少？健康是否正常？",
            "LangGraph 或監控 Agent 在執行資料處理前確認磁碟空間與健康。",
            "n8n 工作流定期取得唯讀狀態，超過公司門檻後再通知管理者。",
            "为未来的 NAS 仪表板提供统一且可审计的结构化资料来源。".replace("为", "為").replace("仪", "儀").replace("审", "稽").replace("资", "資"),
        ], styles),
        p("刻意不提供的能力", styles["h2"]),
        styled_table([
            ["不提供", "理由"],
            ["任意 shell 指令", "避免 Prompt Injection 轉成主機指令執行。"],
            ["格式化、刪除、掛載寫入", "防止資料破壞與權限旁路。"],
            ["SMART 長測試、韌體更新", "這些操作可能長時間佔用裝置或造成營運風險。"],
            ["任意 /dev 路徑", "只接受即時 lsblk 清單中的整顆 SSD 裝置。"],
        ], [58 * mm, 104 * mm], styles),
        PageBreak(),
    ])

    story.extend([
        p("2. 架構與資料流", styles["h1"]),
        ArchitectureFlow(),
        p("元件職責", styles["h2"]),
        styled_table([
            ["元件", "職責", "權限"],
            ["AI Work / LLM", "理解使用者問題，決定是否需要 SSD 工具。", "無 shell、無 root"],
            ["/mcp/ssd", "驗證 Bearer token，處理 MCP initialize、tools/list、tools/call。", "應用程式使用者"],
            ["app/ssd_mcp.py", "參數白名單、lsblk/df 解析、SMART/NVMe 結果摘要。", "固定命令"],
            ["ai-work-ssd-cli", "root-owned helper，只接受 health 與合法整顆裝置路徑。", "受限 sudo"],
            ["Ubuntu CLI", "lsblk、df、smartctl、nvme 提供實際主機資料。", "唯讀查詢"],
        ], [34 * mm, 82 * mm, 46 * mm], styles),
        p("MCP 工具", styles["h2"]),
        styled_table([
            ["工具", "輸入", "主要輸出"],
            ["ssd_list_devices", "無", "裝置、容量、型號、傳輸介面、分割區與掛載點"],
            ["ssd_get_usage", "無", "來源裝置、檔案系統、總量、已用、可用、使用率與掛載點"],
            ["ssd_get_health", "device", "SMART/NVMe 健康、溫度、通電、耗損、備援與錯誤"],
        ], [42 * mm, 27 * mm, 93 * mm], styles),
        p("端點與協定", styles["h2"]),
        p("- MCP endpoint：<b>POST /mcp/ssd</b><br/>- 資訊 endpoint：<b>GET /mcp/ssd</b><br/>- Transport：Streamable HTTP<br/>- MCP protocol：2025-06-18<br/>- 認證：Authorization: Bearer &lt;NAS_SSD_LOCAL_MCP_KEY&gt;", styles["callout"]),
        PageBreak(),
    ])

    story.extend([
        p("3. 安全設計", styles["h1"]),
        styled_table([
            ["控制層", "實作"],
            ["API 驗證", "NAS_SSD_LOCAL_MCP_KEY 與 Authorization header 使用常數時間比較。"],
            ["工具白名單", "MCP 僅公開 3 個唯讀工具；未知 method 或 tool 直接拒絕。"],
            ["參數驗證", "device 必須符合 /dev/nvmeNnN、/dev/sdX 或 /dev/vdX，且存在於即時 SSD 清單。"],
            ["程序執行", "subprocess 使用 shell=False、固定 PATH、15 秒逾時及 512 KiB 輸出上限。"],
            ["權限提升", "sudo 只允許 root-owned helper 的 health 操作；helper 再次驗證參數。"],
            ["資料面", "不執行寫入、刪除、格式化、掛載變更、韌體更新或 SMART 長測試。"],
        ], [42 * mm, 120 * mm], styles),
        p("威脅與處理", styles["h2"]),
        styled_table([
            ["威脅", "控制結果"],
            ["Prompt 要求執行 reboot 或 rm", "沒有相對應工具，無法轉成 shell。"],
            ["device 傳入 /dev/nvme0n1; reboot", "正規表示式驗證失敗，tools/call 回傳參數錯誤。"],
            ["直接呼叫 MCP endpoint", "缺少或錯誤 Bearer token 時回傳 401。"],
            ["偽造其他區塊裝置", "即使格式合法，也必須存在於 lsblk 的非旋轉式磁碟清單。"],
            ["工具卡住或輸出過大", "15 秒逾時，stdout/stderr 各限制 512 KiB。"],
        ], [60 * mm, 102 * mm], styles),
        p("管理建議", styles["warning"]),
        *bullet([
            "MCP Key 應存放於 root 可讀的環境檔，不要寫入 Git、前端或 PDF。",
            "對外只公開 AI Work HTTPS；/mcp/ssd 目前使用 localhost endpoint 供同機服務呼叫。",
            "生产环境应记录工具调用者、工具名称、装置与时间，但不要在一般日志完整输出序号。".replace("生产", "生產").replace("应", "應").replace("调", "調").replace("号", "號").replace("序", "序"),
            "若未来增加告警或写入功能，应建立独立工具、独立权限与人工确认，不应扩充现有只读工具。".replace("未来", "未來").replace("应", "應").replace("独", "獨").replace("权", "權").replace("读", "讀").replace("扩", "擴"),
        ], styles),
        PageBreak(),
    ])

    story.extend([
        p("4. Ubuntu 全新部署", styles["h1"]),
        p("适用于 AI Work Core Self-hosted 安装包。安装脚本会建立 aiwork 系统使用者、Python 虚拟环境、systemd 服务与 SSD helper。".replace("适", "適").replace("于", "用於").replace("会", "會").replace("统", "統").replace("虚", "虛").replace("环", "環"), styles["base"]),
        p("必要套件", styles["h2"]),
        p("sudo apt-get update<br/>sudo apt-get install -y smartmontools nvme-cli sudo", styles["code"]),
        p("安装包执行".replace("安装", "安裝").replace("执行", "執行"), styles["h2"]),
        p("sudo bash deploy/self-hosted/install.sh", styles["code"]),
        p("安装脚本的 SSD 步骤".replace("安装", "安裝").replace("骤", "驟"), styles["h2"]),
        styled_table([
            ["步驟", "动作".replace("动", "動")],
            ["1", "安装 smartmontools、nvme-cli 与 sudo。".replace("安装", "安裝").replace("与", "與")],
            ["2", "生成独立 NAS_SSD_LOCAL_MCP_KEY，不与 APP_SECRET_KEY 共用。".replace("独", "獨").replace("与", "與")],
            ["3", "安装 root-owned helper 至 /usr/local/sbin/ai-work-ssd-cli。".replace("安装", "安裝")],
            ["4", "安装 /etc/sudoers.d/ai-work-ssd-cli，并用 visudo 验证。".replace("安装", "安裝").replace("并", "並").replace("验证", "驗證")],
            ["5", "启动 ai-work.service；启动时自动登记 NAS SSD CLI MCP 与 3 个工具。".replace("启动", "啟動").replace("时", "時").replace("动登", "動登").replace("与", "與")],
        ], [18 * mm, 144 * mm], styles),
        p("环境变量".replace("环", "環").replace("变", "變"), styles["h2"]),
        styled_table([
            ["變數", "用途", "示例"],
            ["NAS_SSD_LOCAL_MCP_KEY", "MCP 内部 Bearer token".replace("内", "內"), "至少 32 bytes 随机值".replace("随", "隨")],
            ["SSD_CLI_HELPER", "受限健康读取 helper".replace("读", "讀"), "/usr/local/sbin/ai-work-ssd-cli"],
        ], [51 * mm, 60 * mm, 51 * mm], styles),
        p("systemd 服务必须载入存放上述变量的 EnvironmentFile。变更后执行：".replace("服务", "服務").replace("须", "須").replace("载", "載").replace("变", "變").replace("执行", "執行"), styles["base"]),
        p("sudo systemctl daemon-reload<br/>sudo systemctl restart ai-work.service<br/>systemctl is-active ai-work.service", styles["code"]),
        PageBreak(),
    ])

    story.extend([
        p("5. 既有 Goldsys 伺服器部署紀錄", styles["h1"]),
        p("本次部署目标为现有非 Git 发布目录 /home/ubuntu/ai-work。为避免影响 NAS 数据库、上传档案与既有凭证，只替换本功能相关应用文件，并在变更前建立备份。".replace("目标", "目標").replace("现", "現").replace("为", "為").replace("发", "發").replace("目录", "目錄").replace("数据", "資料").replace("上传", "上傳").replace("档", "檔").replace("凭证", "憑證").replace("并", "並").replace("变", "變"), styles["base"]),
        styled_table([
            ["項目", "部署結果"],
            ["程式版本", "GitHub branch codex/seed-odoo-manufacturing-demo；commit f42d073"],
            ["应用目录".replace("应", "應").replace("目录", "目錄"), "/home/ubuntu/ai-work"],
            ["服务".replace("服务", "服務"), "ai-work.service；127.0.0.1:8000；状态 active".replace("状态", "狀態")],
            ["系统套件".replace("系统", "系統"), "smartmontools 7.4、nvme-cli 2.8"],
            ["权限 helper".replace("权限", "權限"), "/usr/local/sbin/ai-work-ssd-cli；root:root；0755"],
            ["sudo 限制", "/etc/sudoers.d/ai-work-ssd-cli；visudo 验证通过".replace("验证通过", "驗證通過")],
            ["MCP", "http://127.0.0.1:8000/mcp/ssd；Bearer 已配置；3 tools"],
            ["测试".replace("测试", "測試"), "本机完整测试 155 项通过；服务器 SSD 单元测试 5 项通过".replace("项通过", "項通過").replace("单元", "單元").replace("测试", "測試")],
        ], [48 * mm, 114 * mm], styles),
        p("部署流程摘要", styles["h2"]),
        *bullet([
            "确认本机改动与测试，提交 f42d073 并推送 GitHub。".replace("确认", "確認").replace("动", "動").replace("测试", "測試").replace("并", "並"),
            "建立只含 SSD 相关文件的发布包，并核对 SHA-256。".replace("相关", "相關").replace("发", "發").replace("并", "並").replace("对", "對"),
            "远端备份既有 app/db.py、app/main.py、README 与测试文件。".replace("远", "遠").replace("与", "與").replace("测试", "測試"),
            "安装 smartmontools 与 nvme-cli，部署 root-owned helper 和 sudoers。".replace("安装", "安裝").replace("与", "與"),
            "生成独立 MCP Key、配置 helper 路径并重启 ai-work.service。".replace("独", "獨").replace("并", "並").replace("启", "啟"),
            "调用 tools/list、ssd_list_devices、ssd_get_usage、ssd_get_health 完成验收。".replace("调用", "呼叫").replace("验收", "驗收"),
        ], styles),
        p("未执行的操作".replace("执行", "執行"), styles["h2"]),
        p("没有重新分割磁碟、没有变更挂载点、没有写入 SMART 参数、没有修改数据库内容，也没有在日志或文件中保存 MCP Key。".replace("没有", "沒有").replace("变", "變").replace("挂载", "掛載").replace("写", "寫").replace("参数", "參數").replace("数据", "資料"), styles["callout"]),
        PageBreak(),
    ])

    story.extend([
        p("6. 实测结果与判读".replace("实测", "實測").replace("与", "與").replace("读", "讀"), styles["h1"]),
        p("测试时间：2026-09-27。以下结果来自 59.120.2.102 的实际 SSD MCP 调用，序号与密钥已隐藏。".replace("测试", "測試").replace("结果", "結果").replace("实际", "實際").replace("调用", "呼叫").replace("序号", "序號").replace("与", "與"), styles["base"]),
        styled_table([
            ["指标".replace("指标", "指標"), "实测值".replace("实测值", "實測值"), "判读".replace("读", "讀")],
            ["装置".replace("装", "裝"), "Samsung NVMe 512 GB", "已正确辨识为非旋转式 NVMe".replace("正确", "正確").replace("识", "識").replace("为", "為").replace("转", "轉")],
            ["根档案系统".replace("档", "檔").replace("系统", "系統"), "约 500 GB，使用率 14%", "可用空间约 408 GB".replace("空间", "空間")],
            ["SMART 健康", "passed = true", "目前整体健康检查通过".replace("体", "體").replace("检查通过", "檢查通過")],
            ["温度".replace("温", "溫"), "21°C", "正常"],
            ["通电时间".replace("电", "電").replace("时间", "時間"), "6,995 小時", "约 291 天累计通电".replace("约", "約").replace("累计", "累計").replace("电", "電")],
            ["耗损指标".replace("损", "損").replace("指标", "指標"), "percentage_used = 52%", "表示厂商估算耐用度已使用约 52%，建议持续监控".replace("厂", "廠").replace("约", "約").replace("议", "議").replace("续监", "續監")],
            ["可用备用空间".replace("备", "備").replace("空间", "空間"), "100%", "正常"],
            ["媒体错误".replace("媒体错误", "媒體錯誤"), "0", "未发现媒体错误".replace("发现", "發現").replace("错误", "錯誤")],
            ["非正常关机".replace("关机", "關機"), "106", "历史累计值，应搭配 UPS 与关机流程改善".replace("历", "歷").replace("应", "應").replace("与", "與").replace("关", "關")],
        ], [42 * mm, 48 * mm, 72 * mm], styles),
        p(
            "<b>重要說明</b><br/>percentage_used 不是即時故障預測，也不等於"
            "「剩餘壽命精確為 48%」。它是裝置廠商依寫入耐久度計算的標準化指標。"
            "建議設定趨勢告警，並結合 media_errors、available_spare、溫度、I/O 錯誤與備份狀態判斷。",
            styles["warning"],
        ),
        p("建议阈值（初始值）".replace("建议阈值", "建議閾值").replace("初始值", "初始值"), styles["h2"]),
        styled_table([
            ["项目".replace("项目", "項目"), "提醒", "严重".replace("严重", "嚴重")],
            ["文件系统使用率".replace("文件系统", "檔案系統"), ">= 80%", ">= 90%"],
            ["温度".replace("温", "溫"), ">= 60°C", ">= 70°C"],
            ["percentage_used", ">= 80%", ">= 95%"],
            ["available_spare", "< 20%", "低于厂商阈值".replace("低于", "低於").replace("厂", "廠").replace("阈", "閾")],
            ["media_errors", "> 0", "持续增加".replace("续", "續")],
        ], [62 * mm, 48 * mm, 52 * mm], styles),
        PageBreak(),
    ])

    story.extend([
        p("7. 使用范例".replace("范", "範"), styles["h1"]),
        p("AI Work 提问".replace("问", "問"), styles["h2"]),
        *bullet([
            "请检查这台 NAS 有哪些 SSD，并列出容量与挂载点。".replace("请", "請").replace("检查", "檢查").replace("这", "這").replace("并", "並").replace("与", "與").replace("挂载", "掛載"),
            "请检查 /dev/nvme0n1 的健康、温度、耗损与媒体错误，只能读取。".replace("请", "請").replace("检查", "檢查").replace("温", "溫").replace("损", "損").replace("与", "與").replace("错误", "錯誤").replace("读", "讀"),
            "NAS 的根磁碟还剩多少空间？使用率超过 80% 时提醒我。".replace("还", "還").replace("空间", "空間").replace("过", "過").replace("时", "時"),
        ], styles),
        p("MCP tools/list", styles["h2"]),
        p(
            "curl -s http://127.0.0.1:8000/mcp/ssd &#92;<br/>"
            "  -H 'Authorization: Bearer &lt;key&gt;' &#92;<br/>"
            "  -H 'Content-Type: application/json' &#92;<br/>"
            "  -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}'",
            styles["code"],
        ),
        p("读取健康".replace("读", "讀"), styles["h2"]),
        p(
            "curl -s http://127.0.0.1:8000/mcp/ssd &#92;<br/>"
            "  -H 'Authorization: Bearer &lt;key&gt;' &#92;<br/>"
            "  -H 'Content-Type: application/json' &#92;<br/>"
            "  -d '{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\","
            "\"params\":{\"name\":\"ssd_get_health\",\"arguments\":{\"device\":\"/dev/nvme0n1\"}}}'",
            styles["code"],
        ),
        p("典型回覆", styles["h2"]),
        p("{<br/>  \"read_only\": true,<br/>  \"device\": \"/dev/nvme0n1\",<br/>  \"passed\": true,<br/>  \"temperature_c\": 21.0,<br/>  \"percentage_used\": 52,<br/>  \"available_spare_percent\": 100,<br/>  \"media_errors\": 0<br/>}", styles["code"]),
        p(
            "<b>呼叫順序</b><br/>LLM 應先呼叫 ssd_list_devices，再把回傳的整顆 device path "
            "傳給 ssd_get_health。服務端也會再次查詢即時清單，因此無法用不存在或非 SSD 的路徑繞過限制。",
            styles["callout"],
        ),
        PageBreak(),
    ])

    story.extend([
        p("8. 运维与故障排查".replace("运维", "運維").replace("与", "與").replace("障", "障"), styles["h1"]),
        styled_table([
            ["现象".replace("现", "現"), "检查".replace("检查", "檢查"), "处理".replace("处理", "處理")],
            ["MCP 显示未连接".replace("显", "顯").replace("连", "連"), "确认 NAS_SSD_LOCAL_MCP_KEY 已由 systemd 载入".replace("确认", "確認").replace("载", "載"), "重启 ai-work.service".replace("启", "啟")],
            ["找不到 SSD", "执行 lsblk -o NAME,PATH,TYPE,SIZE,ROTA,TRAN".replace("执行", "執行"), "确认装置为 disk 且 ROTA=0 或 TRAN=nvme".replace("确认", "確認").replace("装", "裝").replace("为", "為")],
            ["health unavailable", "command -v smartctl；command -v nvme", "安装 smartmontools 与 nvme-cli".replace("安装", "安裝").replace("与", "與")],
            ["sudo 要求密码".replace("密码", "密碼"), "sudo -n /usr/local/sbin/ai-work-ssd-cli health /dev/nvme0n1", "检查 sudoers 使用者、权限与 visudo".replace("检查", "檢查").replace("权", "權").replace("与", "與")],
            ["SMART exit code 非 0", "查看 structuredContent 的 exit_code 与 warnings".replace("与", "與"), "部分 SMART 位元代表警告；结合 passed 与错误指标判断".replace("结", "結").replace("与", "與").replace("错误指标", "錯誤指標")],
            ["容量遗漏".replace("遗漏", "遺漏"), "检查 lsblk 是否呈现 LVM / mapper 子装置".replace("检查", "檢查").replace("现", "現").replace("装", "裝"), "确认应用版本已递归收集 children".replace("确认", "確認").replace("应", "應").replace("递归", "遞迴")],
        ], [42 * mm, 68 * mm, 52 * mm], styles),
        p("验收清单".replace("验", "驗").replace("单", "單"), styles["h2"]),
        styled_table([
            ["检查项".replace("检查项", "檢查項"), "通过条件".replace("通过条", "通過條")],
            ["服务".replace("服务", "服務"), "systemctl is-active ai-work.service 回传 active".replace("传", "傳")],
            ["资讯 endpoint".replace("资", "資"), "GET /mcp/ssd 显示 read_only=true 与 3 tools".replace("显", "顯").replace("与", "與")],
            ["认证".replace("认证", "認證"), "无 Bearer 或错误 Key 回传 401".replace("无", "無").replace("错误", "錯誤").replace("传", "傳")],
            ["装置盘点".replace("装", "裝").replace("盘", "盤"), "ssd_list_devices 仅显示实际非旋转式磁碟".replace("仅", "僅").replace("显", "顯").replace("实际", "實際").replace("转", "轉")],
            ["容量", "ssd_get_usage 包含正确挂载点与使用率".replace("正确", "正確").replace("挂载", "掛載").replace("与", "與")],
            ["健康", "ssd_get_health 回传 available=true 与 passed/温度/错误".replace("传", "傳").replace("与", "與").replace("温", "溫").replace("错误", "錯誤")],
            ["安全", "注入式 device 参数遭拒绝，任意工具名遭拒绝".replace("参数", "參數").replace("绝", "絕")],
        ], [62 * mm, 100 * mm], styles),
        p("后续建议".replace("后续建议", "後續建議"), styles["h2"]),
        *bullet([
            "把 SSD 指标写入时序数据库，建立 30/90 天趋势，而不是只看单次快照。".replace("指标", "指標").replace("写", "寫").replace("时", "時").replace("数据", "資料").replace("势", "勢").replace("单", "單"),
            "由 n8n 或 LangGraph 依阈值发送 LINE、邮件或管理后台告警。".replace("阈", "閾").replace("发", "發").replace("邮", "郵").replace("后", "後"),
            "增加角色权限与审计页面，让每次 SSD 查询都能追溯调用者。".replace("权", "權").replace("与", "與").replace("审计", "稽核").replace("询", "詢").replace("调", "調"),
            "维持读取与维护操作分离；任何写入能力必须是独立服务并加入人工确认。".replace("维", "維").replace("读", "讀").replace("与", "與").replace("写", "寫").replace("须", "須").replace("独", "獨").replace("服务", "服務").replace("并", "並"),
        ], styles),
        Spacer(1, 8 * mm),
        p("文件结束".replace("结", "結"), styles["center"]),
    ])

    doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
