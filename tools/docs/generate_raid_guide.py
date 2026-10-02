"""Generate a concise RAID selection guide for AI Work NAS."""

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
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "AI-Work-NAS-儲存與RAID-選型指南.pdf"

NAVY = colors.HexColor("#15324F")
BLUE = colors.HexColor("#1786C7")
SKY = colors.HexColor("#EAF6FE")
PALE = colors.HexColor("#F6F9FC")
INK = colors.HexColor("#17252E")
MUTED = colors.HexColor("#61768A")
LINE = colors.HexColor("#C9DFEF")
GREEN = colors.HexColor("#167B67")
GREEN_PALE = colors.HexColor("#EAF7F3")
AMBER = colors.HexColor("#A76608")
AMBER_PALE = colors.HexColor("#FFF7E8")
RED = colors.HexColor("#B5413C")
RED_PALE = colors.HexColor("#FFF0EF")
WHITE = colors.white


def register_fonts() -> None:
    font = "/System/Library/Fonts/STHeiti Light.ttc"
    font_bold = "/System/Library/Fonts/STHeiti Medium.ttc"
    pdfmetrics.registerFont(TTFont("HeitiTC", font, subfontIndex=0))
    pdfmetrics.registerFont(TTFont("HeitiTCBold", font_bold, subfontIndex=0))


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", parent=base["Normal"], fontName="HeitiTCBold",
            fontSize=10, leading=14, textColor=BLUE, spaceAfter=5 * mm,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="HeitiTCBold",
            fontSize=29, leading=37, textColor=NAVY, spaceAfter=7 * mm,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", parent=base["Normal"], fontName="HeitiTC",
            fontSize=12, leading=21, textColor=MUTED, spaceAfter=10 * mm,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="HeitiTCBold",
            fontSize=20, leading=27, textColor=NAVY, spaceAfter=6 * mm,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="HeitiTCBold",
            fontSize=13, leading=19, textColor=NAVY, spaceBefore=5 * mm,
            spaceAfter=3 * mm,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontName="HeitiTC",
            fontSize=9.4, leading=16, textColor=INK, spaceAfter=3 * mm,
        ),
        "small": ParagraphStyle(
            "small", parent=base["BodyText"], fontName="HeitiTC",
            fontSize=7.4, leading=11, textColor=MUTED,
        ),
        "table": ParagraphStyle(
            "table", parent=base["BodyText"], fontName="HeitiTC",
            fontSize=7.5, leading=11, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "table_head", parent=base["BodyText"], fontName="HeitiTCBold",
            fontSize=7.5, leading=10, textColor=WHITE, alignment=TA_CENTER,
        ),
        "callout": ParagraphStyle(
            "callout", parent=base["BodyText"], fontName="HeitiTC",
            fontSize=9.5, leading=16, textColor=NAVY,
            borderColor=LINE, borderWidth=0.8, borderPadding=9,
            backColor=SKY, spaceBefore=3 * mm, spaceAfter=4 * mm,
        ),
        "warning": ParagraphStyle(
            "warning", parent=base["BodyText"], fontName="HeitiTC",
            fontSize=9, leading=15, textColor=RED,
            borderColor=colors.HexColor("#F0B8B4"), borderWidth=0.8,
            borderPadding=9, backColor=RED_PALE, spaceBefore=3 * mm,
            spaceAfter=4 * mm,
        ),
    }


def P(text: str, style) -> Paragraph:
    return Paragraph(text, style)


def raid_table(rows, widths, s) -> Table:
    cooked = []
    for row_index, row in enumerate(rows):
        style = s["table_head"] if row_index == 0 else s["table"]
        cooked.append([P(str(cell), style) for cell in row])
    table = Table(cooked, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


class RaidDiagram(Flowable):
    def __init__(self, title: str, labels: list[list[str]], color, width=166 * mm, height=55 * mm):
        super().__init__()
        self.title = title
        self.labels = labels
        self.color = color
        self.width = width
        self.height = height

    def draw(self) -> None:
        c = self.canv
        c.setFillColor(NAVY)
        c.setFont("HeitiTCBold", 10)
        c.drawString(0, self.height - 6 * mm, self.title)
        gap = 5 * mm
        disk_width = (self.width - gap * (len(self.labels) - 1)) / len(self.labels)
        disk_height = 36 * mm
        y = 4 * mm
        for index, blocks in enumerate(self.labels):
            x = index * (disk_width + gap)
            c.setFillColor(PALE)
            c.setStrokeColor(LINE)
            c.roundRect(x, y, disk_width, disk_height, 2 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont("HeitiTCBold", 8)
            c.drawCentredString(x + disk_width / 2, y + disk_height - 7 * mm, f"硬碟 {index + 1}")
            block_height = 6 * mm
            for block_index, label in enumerate(blocks):
                by = y + disk_height - 15 * mm - block_index * 7 * mm
                fill = self.color if not label.startswith("P") else AMBER
                c.setFillColor(fill)
                c.roundRect(x + 3 * mm, by, disk_width - 6 * mm, block_height, 1 * mm, fill=1, stroke=0)
                c.setFillColor(WHITE)
                c.setFont("HeitiTCBold", 6.8)
                c.drawCentredString(x + disk_width / 2, by + 2 * mm, label)


def page_frame(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
    canvas.setFillColor(BLUE)
    canvas.setFont("HeitiTCBold", 8)
    canvas.drawString(20 * mm, height - 11 * mm, "AI WORK NAS  |  RAID 選型指南")
    canvas.setFillColor(MUTED)
    canvas.setFont("HeitiTC", 7.5)
    canvas.drawRightString(width - 20 * mm, 10 * mm, f"Goldsys  |  {doc.page}")
    canvas.restoreState()


def build_pdf() -> None:
    register_fonts()
    s = styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=22 * mm, rightMargin=22 * mm,
        topMargin=23 * mm, bottomMargin=18 * mm,
        title="AI Work NAS 儲存與 RAID 選型指南",
        author="Goldsys AI Work",
        subject="RAID 0 至 RAID 6 與 RAID 10 的比較及 2-bay、4-bay NAS 選型建議",
    )
    story = [
        Spacer(1, 18 * mm),
        P("GOLDSYS · AI WORK NAS", s["cover_kicker"]),
        P("SSD、NAS 與 RAID<br/>選型指南", s["cover_title"]),
        P(
            "先釐清 SSD、NAS 與 RAID 的角色，再從 RAID 0–4 的基本原理，到 4-bay NAS 常用的 "
            "RAID 5、RAID 6 與 RAID 10，整理容量、效能、故障容忍與企業應用情境。",
            s["cover_subtitle"],
        ),
        RaidDiagram("四碟資料與校驗分布示意", [
            ["A1", "A2", "P3"], ["B1", "P2", "B3"],
            ["P1", "C2", "C3"], ["D1", "D2", "D3"],
        ], BLUE),
        Spacer(1, 9 * mm),
        raid_table([
            ["適用設備", "優先建議", "核心理由"],
            ["2-bay NAS", "RAID 1", "架構簡單；可容忍一顆硬碟故障"],
            ["4-bay／容量優先", "RAID 5", "可用容量較高；可容忍一顆硬碟故障"],
            ["4-bay／安全優先", "RAID 6", "可容忍任意兩顆硬碟故障"],
            ["4-bay／效能優先", "RAID 10", "讀寫與重建較快；故障容忍取決於位置"],
        ], [43 * mm, 42 * mm, 79 * mm], s),
        Spacer(1, 6 * mm),
        P(
            "<b>最重要的原則：</b>RAID 提供可用性與硬碟故障容忍，但不是備份。"
            "誤刪、勒索軟體、應用錯誤及主機損壞仍可能影響整個陣列。",
            s["warning"],
        ),
        PageBreak(),

        P("1. SSD、NAS 與 RAID 是什麼", s["h1"]),
        raid_table([
            ["概念", "它是什麼", "主要用途", "常見形式"],
            ["SSD", "使用快閃記憶體的儲存裝置", "保存作業系統、應用、資料庫、模型及檔案", "SATA SSD、NVMe SSD、企業級 SSD"],
            ["NAS", "透過網路提供檔案與資料服務的專用主機", "集中儲存、共享、權限、備份、快照及應用服務", "2-bay、4-bay、機架式 NAS"],
            ["RAID", "把多顆硬碟組成一個邏輯儲存空間的方式", "提升效能、容量或硬碟故障容忍", "RAID 0、1、5、6、10"],
        ], [25 * mm, 50 * mm, 55 * mm, 34 * mm], s),
        P("三者的關係", s["h2"]),
        P(
            "SSD 是一顆儲存裝置；NAS 是包含 CPU、記憶體、網路、作業系統及硬碟槽位的完整系統；"
            "RAID 則是 NAS 或伺服器管理多顆 HDD／SSD 的資料配置方式。NAS 可以只使用 HDD、只使用 SSD，"
            "也可以讓 HDD 保存大量資料、SSD 負責快取或高頻工作負載。",
            s["callout"],
        ),
        raid_table([
            ["項目", "一般 SSD", "NAS"],
            ["設備範圍", "單一儲存裝置", "完整網路儲存主機"],
            ["連接方式", "SATA、NVMe／PCIe、USB", "Ethernet 網路；可提供 SMB、NFS、Web、API"],
            ["主要使用者", "通常由一台電腦或伺服器使用", "可供多名使用者與多台裝置共同存取"],
            ["資料管理", "本身不負責帳號、共享與企業權限", "可提供帳號、群組、權限、快照、備份及稽核"],
            ["容量與容錯", "單顆容量；故障時可能直接中斷", "可安裝多顆 HDD／SSD 並使用 RAID"],
            ["AI Work 角色", "模型、向量索引、資料庫或快取的高速儲存", "保存原始資料、逐字稿、RAG、Wiki、模型與稽核記錄"],
        ], [35 * mm, 61 * mm, 68 * mm], s),
        P("NAS 使用 HDD 還是 SSD？", s["h2"]),
        raid_table([
            ["配置", "優點", "適合內容"],
            ["全 HDD", "成本低、單碟容量大", "原始影片、錄音、文件與備份"],
            ["全 SSD", "延遲低、安靜、隨機讀寫快", "資料庫、向量檢索、多人高頻存取"],
            ["HDD＋SSD", "兼顧容量與效能", "HDD 保存原始資料；SSD 保存熱資料、索引與快取"],
        ], [37 * mm, 56 * mm, 71 * mm], s),
        P(
            "SSD 速度快，但不等於 NAS，也不自動提供多人共享或容錯。NAS 使用 SSD 後仍需要考慮 RAID、"
            "備份、SSD 寫入耐久度（TBW／DWPD）、斷電保護及企業級工作負載。",
            s["warning"],
        ),
        PageBreak(),

        P("2. RAID 0–4 快速比較", s["h1"]),
        raid_table([
            ["RAID", "最少硬碟", "可用容量公式", "容忍故障", "主要特點", "現行建議"],
            ["RAID 0", "2", "N × S", "0 顆", "分條；速度與容量高，但沒有容錯", "僅限暫存或可重建資料"],
            ["RAID 1", "2", "1 × S", "1 顆", "鏡像；資料同步保存在兩顆硬碟", "2-bay NAS 首選"],
            ["RAID 2", "多顆", "依配置", "依配置", "位元級分條＋Hamming Code", "已淘汰"],
            ["RAID 3", "3", "(N−1) × S", "1 顆", "位元組級分條＋專用校驗碟", "少用；多由 RAID 5 取代"],
            ["RAID 4", "3", "(N−1) × S", "1 顆", "區塊級分條＋專用校驗碟", "少用；校驗碟易成瓶頸"],
        ], [17 * mm, 19 * mm, 25 * mm, 22 * mm, 48 * mm, 33 * mm], s),
        P("公式說明", s["h2"]),
        P(
            "N 代表硬碟數量，S 代表陣列中最小硬碟的容量。不同容量硬碟混用時，"
            "多數傳統 RAID 會以最小容量計算；格式化、檔案系統與系統保留空間也會使實際容量略低。",
            s["body"],
        ),
        P("RAID 0 與 RAID 1", s["h2"]),
        raid_table([
            ["項目", "RAID 0", "RAID 1"],
            ["資料方式", "資料分散到多顆硬碟", "每顆硬碟保存相同資料"],
            ["2 × 8 TB 可用容量", "約 16 TB", "約 8 TB"],
            ["單碟故障", "整個陣列可能失效", "服務可繼續，由存活碟重建"],
            ["AI Work 用途", "快取、暫存、可重新生成的索引", "原始文件、逐字稿、知識庫"],
        ], [40 * mm, 62 * mm, 62 * mm], s),
        P(
            "RAID 2、3、4 是理解 RAID 發展的重要概念，但現代 NAS 幾乎不會把它們作為新部署選項。"
            "實務上會直接評估 RAID 1、5、6、10，或 ZFS/Btrfs 提供的相應儲存配置。",
            s["callout"],
        ),
        PageBreak(),

        P("3. 4-bay：RAID 5、6、10", s["h1"]),
        P("以下以 4 × 8 TB 同規格硬碟為例。容量為理論值，實際格式化後會略少。", s["body"]),
        raid_table([
            ["項目", "RAID 5", "RAID 6", "RAID 10"],
            ["最少硬碟", "3", "4", "4"],
            ["4 × 8 TB 可用容量", "約 24 TB", "約 16 TB", "約 16 TB"],
            ["容忍故障", "任意 1 顆", "任意 2 顆", "至少 1 顆；最多 2 顆，取決於鏡像組"],
            ["讀取", "快", "快", "快"],
            ["寫入", "需計算單組校驗", "需計算雙組校驗", "不需校驗；通常較快"],
            ["重建風險", "重建期間再壞 1 顆即失效", "重建期間仍可再容忍 1 顆", "通常只需從鏡像成員複製"],
            ["適合", "一般檔案、容量優先", "重要企業資料、安全優先", "資料庫、VM、向量索引、高頻 I/O"],
        ], [34 * mm, 43 * mm, 43 * mm, 44 * mm], s),
        P("RAID 5", s["h2"]),
        P(
            "資料與單組校驗分散在全部硬碟上，可用容量為 (N−1) × S。容量利用率高，"
            "但只能承受一顆硬碟故障；大容量硬碟重建時間較長時，風險需特別評估。",
            s["body"],
        ),
        P("RAID 6", s["h2"]),
        P(
            "保存兩組分散式校驗，可用容量為 (N−2) × S。能容忍任意兩顆硬碟故障，"
            "但寫入校驗成本高於 RAID 5，四碟配置的容量利用率為 50%。",
            s["body"],
        ),
        P("RAID 10", s["h2"]),
        P(
            "先建立兩組鏡像，再跨鏡像組分條。可用容量為總容量的一半。讀寫與重建通常較快；"
            "若損壞硬碟分屬不同鏡像組，最多可承受兩顆，但同一鏡像組兩顆同時損壞會使陣列失效。",
            s["body"],
        ),
        RaidDiagram("RAID 10 鏡像組示意", [
            ["鏡像 A", "資料 1"], ["鏡像 A", "資料 1"],
            ["鏡像 B", "資料 2"], ["鏡像 B", "資料 2"],
        ], GREEN, height=48 * mm),
        PageBreak(),

        P("4. AI Work NAS 選型建議", s["h1"]),
        raid_table([
            ["情境", "建議", "原因", "需要注意"],
            ["2-bay 辦公室 NAS", "RAID 1", "簡單、易維護；可容忍一顆碟故障", "容量只有總容量的一半"],
            ["4-bay 文件與多媒體庫", "RAID 6", "原始錄音、影片、PDF 需要更高容錯", "寫入較慢；容量利用率 50%"],
            ["4-bay AI／資料庫節點", "RAID 10", "適合向量資料庫、快取與高頻 I/O", "同鏡像組雙碟故障仍會失效"],
            ["4-bay 容量優先的次要資料", "RAID 5", "比 RAID 6、10 提供更多可用容量", "只容忍一顆碟；需可靠備份"],
            ["模型快取／可重建暫存", "RAID 0（選配）", "追求吞吐及全部容量", "不能保存唯一副本"],
        ], [39 * mm, 31 * mm, 57 * mm, 37 * mm], s),
        P("建議的資料分層", s["h2"]),
        raid_table([
            ["資料類型", "建議儲存層", "備份原則"],
            ["原始錄音、影片、PDF、DOCX", "RAID 6 或 RAID 1", "至少保留一份異機或離線副本"],
            ["逐字稿、OCR、會議紀要、Wiki", "RAID 6／10", "資料庫與檔案同步備份"],
            ["向量索引、縮圖、切片與模型快取", "RAID 10 或高速暫存區", "可重建，但需保存來源與設定"],
            ["系統資料庫、權限與稽核記錄", "RAID 10 或可靠鏡像", "定期快照＋異機備份＋還原演練"],
        ], [55 * mm, 50 * mm, 59 * mm], s),
        P("部署前檢查清單", s["h2"]),
        P(
            "① 使用相同容量與相近規格的 NAS／企業級硬碟。<br/>"
            "② 啟用 SMART、溫度、壞軌及 RAID 降級告警。<br/>"
            "③ 準備熱備碟或明確的故障更換流程。<br/>"
            "④ 設定快照與不可變備份，並定期測試還原。<br/>"
            "⑤ 監控重建進度、I/O 延遲與剩餘容量；避免長期接近滿載。",
            s["callout"],
        ),
        P(
            "<b>結論：</b>2-bay 以 RAID 1 為基準；4-bay 的企業資料優先採 RAID 6，"
            "資料庫及 AI 高頻工作負載優先採 RAID 10。RAID 5 適合容量較重要、且已有可靠備份的情境。",
            s["warning"],
        ),
        Spacer(1, 5 * mm),
        P("文件版本 1.0 · 2026-10-02 · 本文件為架構選型參考，實際配置仍需依硬體控制器、檔案系統、工作負載及備份政策確認。", s["small"]),
    ]

    doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
