"""Generate the NAS Storage MCP expansion and deployment plan."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from generate_ssd_cli_mcp_guide import (
    BLUE,
    BLUE_DARK,
    BLUE_LIGHT,
    INK,
    LINE,
    MUTED,
    NAVY,
    PALE,
    TEAL,
    TEAL_LIGHT,
    WHITE,
    bullet,
    card,
    make_styles,
    p,
    register_fonts,
    styled_table,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "AI-Work-NAS-Storage-MCP-擴充與部署方案.pdf"


class DiscoveryFlow(Flowable):
    def __init__(self, width: float = 170 * mm, height: float = 76 * mm):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        canvas = self.canv
        stages = [
            ("主機探測", "lsblk / findmnt / lspci", BLUE_LIGHT, BLUE_DARK),
            ("後端識別", "mdadm / ZFS / Btrfs\nHardware RAID / LVM", TEAL_LIGHT, TEAL),
            ("唯讀收集", "固定 CLI / API\n逾時與輸出限制", BLUE_LIGHT, BLUE_DARK),
            ("統一模型", "pool / array / device\nvolume / alert", PALE, NAVY),
            ("MCP 工具", "LLM / Portal / n8n\n稽覈與權限", TEAL_LIGHT, TEAL),
        ]
        gap = 5 * mm
        box_width = (self.width - gap * 4) / 5
        y = 19 * mm
        box_height = 39 * mm
        for index, (title, subtitle, fill, stroke) in enumerate(stages):
            x = index * (box_width + gap)
            canvas.setFillColor(fill)
            canvas.setStrokeColor(stroke)
            canvas.setLineWidth(1.1)
            canvas.roundRect(x, y, box_width, box_height, 2.5 * mm, fill=1, stroke=1)
            canvas.setFillColor(INK)
            canvas.setFont("HeitiTCBold", 8.6)
            canvas.drawCentredString(x + box_width / 2, y + 25 * mm, title)
            canvas.setFillColor(MUTED)
            canvas.setFont("HeitiTC", 6.4)
            for line_index, line in enumerate(subtitle.split("\n")):
                canvas.drawCentredString(x + box_width / 2, y + (14 - line_index * 5) * mm, line)
            if index < len(stages) - 1:
                start = x + box_width + 0.5 * mm
                end = x + box_width + gap - 0.5 * mm
                mid = y + box_height / 2
                canvas.setStrokeColor(BLUE_DARK)
                canvas.line(start, mid, end, mid)
                canvas.line(end - 1.6 * mm, mid + 1.3 * mm, end, mid)
                canvas.line(end - 1.6 * mm, mid - 1.3 * mm, end, mid)
        canvas.setFillColor(MUTED)
        canvas.setFont("HeitiTC", 7.5)
        canvas.drawString(0, 6 * mm, "發現結果可同時包含多個後端；系統聚合資料，不強制只選擇一種 RAID 技術。".replace("發現", "發現").replace("結", "結").replace("資", "資").replace("統", "統").replace("選擇", "選擇"))


class StorageLayers(Flowable):
    def __init__(self, width: float = 170 * mm, height: float = 88 * mm):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        canvas = self.canv
        layers = [
            ("AI Work / LLM / n8n", "自然語言、監控流程、告警與報表", BLUE_LIGHT),
            ("NAS Storage MCP", "工具白名單、角色權限、稽覈、正規化輸出", TEAL_LIGHT),
            ("Backend Adapters", "mdadm | ZFS | Btrfs | Hardware RAID | LVM | Single Disk", BLUE_LIGHT),
            ("Ubuntu NAS", "實體磁碟、控制器、陣列、Pool、Volume、檔案系統", PALE),
        ]
        y = self.height - 18 * mm
        for title, subtitle, fill in layers:
            canvas.setFillColor(fill)
            canvas.setStrokeColor(LINE)
            canvas.roundRect(0, y - 14 * mm, self.width, 17 * mm, 2.5 * mm, fill=1, stroke=1)
            canvas.setFillColor(NAVY)
            canvas.setFont("HeitiTCBold", 9.5)
            canvas.drawString(6 * mm, y - 4 * mm, title)
            canvas.setFillColor(MUTED)
            canvas.setFont("HeitiTC", 7.5)
            canvas.drawRightString(self.width - 6 * mm, y - 4 * mm, subtitle)
            y -= 21 * mm


def page_frame(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(19 * mm, height - 15 * mm, width - 19 * mm, height - 15 * mm)
    canvas.setFillColor(BLUE_DARK)
    canvas.setFont("HeitiTCBold", 8)
    canvas.drawString(19 * mm, height - 11 * mm, "AI Work NAS  |  NAS Storage MCP")
    canvas.setFillColor(MUTED)
    canvas.setFont("HeitiTC", 7.5)
    canvas.drawRightString(width - 19 * mm, 10 * mm, f"擴充與部署方案  |  {doc.page}")
    canvas.restoreState()


def build_pdf() -> None:
    register_fonts()
    styles = make_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=23 * mm, bottomMargin=18 * mm,
        title="AI Work NAS Storage MCP 擴充與部署方案",
        author="Goldsys AI Work",
        subject="NAS SSD CLI MCP 擴充爲多後端 NAS Storage MCP 的實施規格".replace("爲", "為"),
    )
    story = []

    story.extend([
        Spacer(1, 17 * mm),
        p("GOLDSYS · AI WORK NAS", styles["cover_kicker"]),
        p("NAS Storage MCP<br/>擴充與部署方案", styles["cover_title"]),
        p("由現有 NAS SSD CLI MCP 擴充爲統一的 NAS 儲存控制面，自動發現 mdadm、ZFS、Btrfs、硬件 RAID、LVM 與單磁碟，並以唯讀工具提供給 LLM、Portal 與自動化流程。".replace("現", "現").replace("擴", "擴").replace("爲", "為").replace("統", "統").replace("儲", "儲").replace("動", "動").replace("發現", "發現").replace("硬件", "硬體").replace("與", "與").replace("單", "單").replace("並", "並").replace("讀", "讀").replace("給", "給"), styles["cover_subtitle"]),
        DiscoveryFlow(),
        Spacer(1, 9 * mm),
        styled_table([
            ["文件版本", "基礎版本", "盤點日期"],
            ["1.0", "NAS SSD CLI MCP · f42d073", "2026-09-27"],
        ], [46 * mm, 70 * mm, 46 * mm], styles),
        Spacer(1, 7 * mm),
        p("設計結論".replace("設計結論", "設計結論"), styles["h2"]),
        p("NAS Storage MCP 應採用“多後端發現 + 統一資料模型 + 受限唯讀 helper”。後端可同時存在，例如硬件 RAID 上建立 LVM，再提供 ext4 文件系統；系統必須保留每層來源關係，不能只顯示最上層容量。".replace("應", "應").replace("採", "採").replace("後", "後").replace("發現", "發現").replace("統", "統").replace("資", "資").replace("讀", "讀").replace("同時", "同時").replace("硬件", "硬體").replace("須", "須").replace("層", "層").replace("顯", "顯"), styles["callout"]),
        PageBreak(),
    ])

    story.extend([
        p("1. 目標與範圍".replace("目標與範圍", "目標與範圍"), styles["h1"]),
        p("當前 SSD MCP 已能讀取實體 SSD、文件系統容量與 SMART/NVMe 健康。擴充後的 NAS Storage MCP 需要從“單顆磁碟健康”提升爲“完整儲存拓撲與陣列狀態”。".replace("當前", "目前").replace("讀", "讀").replace("實體", "實體").replace("系統", "系統").replace("與", "與").replace("擴", "擴").replace("後", "後").replace("單", "單").replace("顆", "顆").replace("爲", "為").replace("儲", "儲").replace("陣", "陣").replace("態", "態"), styles["base"]),
        StorageLayers(),
        card("發現".replace("發現", "發現"), "識別主機上實際存在的儲存技術、控制器、陣列、Pool、Volume、LVM 與文件系統，不依賴人工選擇。".replace("識", "識").replace("實際", "實際").replace("儲", "儲").replace("陣", "陣").replace("與", "與").replace("系統", "系統").replace("選擇", "選擇"), styles),
        Spacer(1, 3 * mm),
        card("正規化", "把不同 CLI 與 API 輸出轉換爲統一的 pool、array、device、volume、filesystem、alert 資料結構。".replace("與", "與").replace("輸", "輸").replace("轉換爲", "轉換為").replace("統", "統").replace("資", "資"), styles, TEAL_LIGHT),
        Spacer(1, 3 * mm),
        card("安全", "延續 SSD MCP 的固定命令、參數驗證、Bearer 認證、逾時、輸出上限與受限 sudo helper。".replace("續", "續").replace("參數", "參數").replace("驗證", "驗證").replace("認證", "認證").replace("時", "時").replace("輸", "輸").replace("與", "與"), styles),
        p("第一階段包含".replace("階", "階"), styles["h2"]),
        *bullet([
            "自動發現可用後端及其 CLI 版本。".replace("動", "動").replace("發現", "發現").replace("後", "後"),
            "列出儲存拓撲、陣列、成員盤、Pool、Volume、文件系統與掛載點。".replace("儲", "儲").replace("陣", "陣").replace("員盤", "員碟").replace("系統", "系統").replace("與", "與").replace("掛載", "掛載"),
            "查詢降級、故障、重建、scrub/resilver 與容量狀態。".replace("詢", "詢").replace("級", "級").replace("與", "與").replace("態", "態"),
            "沿用 SSD SMART/NVMe 健康查詢，並保留裝置與陣列關係。".replace("詢", "詢").replace("並", "並").replace("裝", "裝").replace("與", "與").replace("陣", "陣"),
            "所有工具預設唯讀；不提供建立、刪除、格式化或強制重建。".replace("預設", "預設").replace("讀", "讀").replace("刪", "刪").replace("強", "強"),
        ], styles),
        PageBreak(),
    ])

    story.extend([
        p("2. 自動發現設計".replace("動", "動").replace("發現設計", "發現設計"), styles["h1"]),
        DiscoveryFlow(),
        p("發現原則".replace("發現", "發現").replace("則", "則"), styles["h2"]),
        *bullet([
            "先使用無特權命令盤點塊裝置、文件系統、掛載、PCI 控制器與已安裝工具。".replace("無", "無").replace("權", "權").replace("盤", "盤").replace("塊裝", "區塊裝").replace("系統", "系統").replace("掛載", "掛載").replace("與", "與").replace("安裝", "安裝"),
            "只對已發現且可用的後端執行進一步查詢；工具不存在時回傳 unavailable，不自動安裝。".replace("對", "對").replace("發現", "發現").replace("後", "後").replace("執行", "執行").replace("進", "進").replace("詢", "詢").replace("時", "時").replace("傳", "傳").replace("動", "動").replace("安裝", "安裝"),
            "多後端可同時啓用，結果依 parent_id、member_of 與 backing_device 建立拓撲。".replace("後", "後").replace("同時", "同時").replace("啓", "啟").replace("結", "結").replace("與", "與"),
            "發現結果設短期快取；實際狀態、重建進度與告警查詢必須即時執行。".replace("發現結", "發現結").replace("設", "設").replace("實際", "實際").replace("態", "態").replace("進", "進").replace("與", "與").replace("詢須時執", "詢必須即時執"),
        ], styles),
        p("後端判定矩陣".replace("後", "後").replace("陣", "陣"), styles["h2"]),
        styled_table([
            ["後端", "發現依據".replace("發現", "發現"), "只讀資料來源", "狀態".replace("狀態", "狀態")],
            ["mdadm", "/proc/mdstat、mdadm 存在", "mdadm --detail --scan；mdadm --detail", "Linux Software RAID"],
            ["ZFS", "zpool/zfs 存在且可列出 pool", "zpool list/status；zfs list", "Pool、vdev、scrub、resilver"],
            ["Btrfs", "btrfs 存在且發現 Btrfs FS".replace("發現", "發現"), "filesystem show/usage；device stats", "Profile、device、scrub、錯誤".replace("錯誤", "錯誤")],
            ["Hardware RAID", "lspci 控制器 + 廠商 CLI".replace("廠", "廠"), "storcli/perccli/arcconf/ssacli", "Controller、VD、PD、rebuild"],
            ["LVM", "pvs/vgs/lvs 存在", "pvs、vgs、lvs", "PV、VG、LV 與 backing device".replace("與", "與")],
            ["Single Disk", "lsblk disk 且不屬於陣列".replace("屬", "屬").replace("陣", "陣"), "lsblk、df、smartctl、nvme", "現有 SSD MCP 相容層".replace("現", "現").replace("層", "層")],
        ], [28 * mm, 45 * mm, 51 * mm, 38 * mm], styles),
        PageBreak(),
    ])

    story.extend([
        p("3. MCP 工具設計".replace("設計", "設計"), styles["h1"]),
        p("建議新增 /mcp/storage 與 slug nas-storage，同時保留 /mcp/ssd 作爲相容端點。舊工具不立即刪除，避免既有 Prompt、n8n 與 Agent 流程失效。".replace("建議", "建議").replace("與", "與").replace("同時", "同時").replace("爲", "為").replace("舊", "舊").replace("刪", "刪"), styles["callout"]),
        styled_table([
            ["工具", "輸入".replace("輸", "輸"), "用途"],
            ["storage_discover_backends", "無".replace("無", "無"), "列出已發現後端、版本、可用性與缺少的 CLI".replace("發現", "發現").replace("後", "後").replace("與", "與")],
            ["storage_get_topology", "scope?", "回傳 device -> controller/array/pool -> volume -> filesystem 拓撲".replace("傳", "傳").replace("系統", "系統")],
            ["storage_list_pools", "backend?", "統一列出 md array、ZFS pool、Btrfs FS、hardware VD、LVM VG".replace("統", "統")],
            ["storage_get_pool_status", "pool_id", "健康、降級、成員、容量、錯誤與最後檢查".replace("級", "級").replace("員", "員").replace("錯誤與", "錯誤與").replace("檢查", "檢查")],
            ["storage_get_rebuild_progress", "pool_id", "重建、resync、reshape、scrub 或 resilver 進度".replace("進", "進")],
            ["storage_list_devices", "pool_id?", "實體磁碟、角色、狀態與所屬陣列".replace("實體", "實體").replace("態與", "態與").replace("屬", "屬").replace("陣", "陣")],
            ["storage_get_device_health", "device_id", "沿用 SSD SMART/NVMe 摘要，並關聯上層陣列".replace("並", "並").replace("關", "關").replace("層", "層").replace("陣", "陣")],
            ["storage_get_capacity", "scope?", "Pool、Volume、filesystem 容量、使用率與掛載點".replace("系統", "系統").replace("與", "與").replace("掛載", "掛載")],
            ["storage_get_alerts", "severity?", "聚合 degraded、failed、I/O error、空間與溫度異常".replace("空間與溫", "空間與溫")],
        ], [54 * mm, 31 * mm, 77 * mm], styles),
        p("統一資料模型".replace("統", "統").replace("資", "資"), styles["h2"]),
        styled_table([
            ["對象".replace("對", "對"), "必要字段".replace("字段", "欄位")],
            ["backend", "id、type、version、available、privilege_mode、last_discovered_at"],
            ["pool", "id、backend、name、raid_level/profile、health、capacity、used、members"],
            ["device", "id、path、model、serial_masked、role、health、temperature、parent_id"],
            ["volume", "id、pool_id、type、size、filesystem、mountpoints、backing_devices"],
            ["operation", "type、status、progress_percent、eta_seconds、started_at"],
            ["alert", "severity、code、message、source_id、observed_at、recommended_action"],
        ], [38 * mm, 124 * mm], styles),
        PageBreak(),
    ])

    story.extend([
        p("4. 唯讀 CLI 與解析策略".replace("與", "與"), styles["h1"]),
        styled_table([
            ["後端".replace("後", "後"), "允許的命令類別".replace("許", "許").replace("類", "類"), "解析方式"],
            ["基礎".replace("基礎", "基礎"), "lsblk --json、findmnt --json、df、lspci", "優先 JSON；df 使用固定欄位".replace("優", "優").replace("欄", "欄")],
            ["mdadm", "cat /proc/mdstat、mdadm --detail --scan、mdadm --detail <device>", "狀態機 + key/value；device 必須來自發現結果".replace("態", "態").replace("須", "須").replace("發現結", "發現結")],
            ["ZFS", "zpool list/status、zfs list、zpool events", "使用 -H/-p 固定欄位；保留 vdev 樹關係".replace("欄", "欄").replace("樹關", "樹關")],
            ["Btrfs", "filesystem show/usage、device stats、scrub status", "固定語言環境；解析 profile/device/error".replace("語", "語").replace("環", "環")],
            ["StorCLI/PERCCLI", "/cALL show J、/cX/vALL show J、/cX/eALL/sALL show J", "強制 JSON；僅發現出的 controller id".replace("強", "強").replace("僅", "僅").replace("發現", "發現")],
            ["Arcconf/SSA", "getconfig、getstatus、ctrl show config/status", "版本化 parser；原始輸出限長保存於稽覈".replace("輸", "輸").replace("長", "長").replace("於", "於")],
            ["LVM", "pvs/vgs/lvs --reportformat json", "直接轉換 JSON 並關聯底層裝置".replace("轉換", "轉換").replace("並關", "並關").replace("層裝", "層裝")],
        ], [30 * mm, 79 * mm, 53 * mm], styles),
        p("實現規則".replace("實", "實").replace("則", "則"), styles["h2"]),
        *bullet([
            "每個 backend adapter 實作 discover()、topology()、pools()、status()、operations() 與 alerts()。".replace("個", "個").replace("實", "實").replace("與", "與"),
            "所有 subprocess 使用 shell=False、固定 PATH/LANG、逾時與輸出長度上限。".replace("時與輸", "時與輸").replace("長", "長"),
            "不接受 raw_command、controller_expression 或用戶自由輸入的 CLI 參數。".replace("用戶", "使用者").replace("輸", "輸").replace("參數", "參數"),
            "優先結構化輸出；文本 parser 必須配合真實樣本與 fixture 測試。".replace("優", "優").replace("結", "結").replace("輸", "輸").replace("須", "須").replace("真實", "真實").replace("與", "與").replace("測試", "測試"),
            "健康查詢失敗時回傳 backend、exit_code、可操作建議，不僞造 healthy。".replace("詢", "詢").replace("敗時", "敗時").replace("傳", "傳").replace("建議", "建議").replace("僞", "偽"),
        ], styles),
        p(
            "<b>嚴禁命令</b><br/>mdadm --create/--add/--remove/--fail、"
            "zpool create/destroy/attach/detach/replace、btrfs device add/delete、"
            "storcli set/delete/start、格式化、分割、掛載寫入與韌體更新均不屬於第一階段。",
            styles["warning"],
        ),
        PageBreak(),
    ])

    story.extend([
        p("5. 權限與安全模型".replace("權", "權").replace("與", "與"), styles["h1"]),
        styled_table([
            ["控制層".replace("層", "層"), "實施要求".replace("實", "實")],
            ["身份", "MCP Bearer 僅用於服務間調用；Portal 仍使用者登入與角色權限。".replace("僅", "僅").replace("服務間調用", "服務間呼叫").replace("與", "與").replace("權", "權")],
            ["工具", "只註冊唯讀工具；tool annotations 標示 readOnlyHint=true、destructiveHint=false。".replace("讀", "讀").replace("標", "標")],
            ["參數".replace("參數", "參數"), "pool_id、device_id 必須由發現清單映射，不直接拼接用戶輸入。".replace("須", "須").replace("發現清單", "發現清單").replace("用戶輸", "使用者輸")],
            ["權限 helper".replace("權", "權"), "每種 backend 對應固定 subcommand；sudoers 不授權廠商 CLI 通配執行。".replace("種", "種").replace("對", "對").replace("權廠", "權廠").replace("執行", "執行")],
            ["輸出".replace("輸", "輸"), "序號預設遮罩；原始輸出僅管理員稽覈可見；限制 512 KiB。".replace("預設", "預設").replace("僅", "僅").replace("見", "見")],
            ["審計".replace("審計", "稽覈"), "記錄調用者、工具、目標資源、後端、耗時、結果與錯誤，不記錄 Key。".replace("錄調用", "錄呼叫").replace("目標資", "目標資").replace("後", "後").replace("時", "時").replace("結", "結").replace("與", "與").replace("錯誤", "錯誤")],
            ["網絡".replace("絡", "路"), "MCP endpoint 綁定 localhost 或受保護內網；外部只經 HTTPS Portal / Gateway。".replace("綁", "綁").replace("護內", "護內").replace("經", "經")],
        ], [43 * mm, 119 * mm], styles),
        p("建議 helper 結構".replace("建議", "建議").replace("結", "結"), styles["h2"]),
        p("/usr/local/sbin/ai-work-storage-cli discover<br/>/usr/local/sbin/ai-work-storage-cli mdadm status &lt;array-id&gt;<br/>/usr/local/sbin/ai-work-storage-cli zfs status &lt;pool-id&gt;<br/>/usr/local/sbin/ai-work-storage-cli btrfs status &lt;filesystem-id&gt;<br/>/usr/local/sbin/ai-work-storage-cli storcli status &lt;controller-id&gt;<br/>/usr/local/sbin/ai-work-storage-cli lvm topology", styles["code"]),
        p("helper 自身必須再次驗證 backend、operation 與 ID，並確認目標存在於即時發現結果。即使 MCP 應用層遭繞過，也不能取得通用 root shell。".replace("須", "須").replace("驗證", "驗證").replace("與", "與").replace("並", "並").replace("目標", "目標").replace("於時發現結", "於即時發現結").replace("應", "應").replace("層", "層").replace("過", "過"), styles["callout"]),
        PageBreak(),
    ])

    story.extend([
        p("6. 現有服務器基線".replace("現", "現").replace("務", "務"), styles["h1"]),
        p("以下爲 2026-09-27 對 59.120.2.102 的唯讀盤點。過程中沒有安裝軟件、沒有寫入磁碟，也沒有變更 RAID 或掛載。".replace("爲", "為").replace("對", "對").replace("讀盤", "讀盤").replace("沒有", "沒有").replace("安裝", "安裝").replace("寫", "寫").replace("變", "變").replace("掛載", "掛載"), styles["base"]),
        styled_table([
            ["項目".replace("項目", "項目"), "檢測結果".replace("檢測結", "檢測結"), "Storage MCP 判定"],
            ["實體儲存".replace("實體儲", "實體儲"), "1 x Samsung NVMe，約 512 GB".replace("約", "約"), "single_disk"],
            ["分層".replace("層", "層"), "NVMe partition -> LVM PV/VG/LV -> ext4 /", "lvm + filesystem"],
            ["mdadm", "工具已安裝；/proc/mdstat 無活動陣列".replace("安裝", "安裝").replace("無", "無").replace("陣", "陣"), "available=true；arrays=0"],
            ["ZFS", "zpool/zfs 未安裝".replace("安裝", "安裝"), "available=false；reason=cli_missing"],
            ["Btrfs", "btrfs 工具存在；無 Btrfs 文件系統".replace("無", "無").replace("系統", "系統"), "available=true；filesystems=0"],
            ["Hardware RAID", "偵測到 Intel SATA AHCI 與 Samsung NVMe controller；無廠商 RAID CLI".replace("偵", "偵").replace("測", "測").replace("與", "與").replace("無廠", "無廠"), "controllers=0"],
            ["現有 SSD MCP".replace("現", "現"), "connected；3 tools；SMART passed", "保留相容端點"],
        ], [38 * mm, 83 * mm, 41 * mm], styles),
        p("當前結論".replace("當前結論", "目前結論"), styles["h2"]),
        p("本機目前沒有 RAID 陣列，因此擴充完成後不會憑空顯示 RAID。它應顯示 single_disk + LVM + ext4 拓撲，並明確報告 mdadm/Btrfs 可用但沒有資源、ZFS 與硬件 RAID backend 不可用。未來加入陣列或控制器後，無需改 Prompt 即可自動出現對應資源。".replace("沒有", "沒有").replace("陣", "陣").replace("擴", "擴").replace("後", "後").replace("顯", "顯").replace("應", "應").replace("並", "並").replace("資", "資").replace("與", "與").replace("硬件", "硬體").replace("未來", "未來").replace("動", "動").replace("現", "現").replace("對", "對"), styles["callout"]),
        p("套件策略", styles["h2"]),
        styled_table([
            ["後端".replace("後", "後"), "Ubuntu 套件", "安裝策略".replace("安裝", "安裝")],
            ["mdadm", "mdadm", "Core 建議安裝".replace("建議安裝", "建議安裝")],
            ["Btrfs", "btrfs-progs", "Core 可選".replace("選", "選")],
            ["ZFS", "zfsutils-linux", "用戶選擇使用 ZFS 時安裝".replace("用戶選擇", "使用者選擇").replace("時安裝", "時安裝")],
            ["LVM", "lvm2", "偵測到 LVM 時保留".replace("偵測", "偵測").replace("時", "時")],
            ["Hardware RAID", "廠商 CLI".replace("廠", "廠"), "依控制器型號與授權手動安裝".replace("號與授權手動安裝", "號與授權手動安裝")],
        ], [36 * mm, 48 * mm, 78 * mm], styles),
        PageBreak(),
    ])

    story.extend([
        p("7. 分階段實施".replace("階", "階").replace("實", "實"), styles["h1"]),
        styled_table([
            ["階段".replace("階", "階"), "範圍".replace("範圍", "範圍"), "驗收".replace("驗", "驗")],
            ["Phase 1", "抽象 adapter；single disk/LVM/mdadm；相容 SSD tools", "現有服務器拓撲正確；無陣列不誤報".replace("現", "現").replace("務", "務").replace("正確", "正確").replace("無陣", "無陣")],
            ["Phase 2", "ZFS 與 Btrfs adapter；scrub/resilver 與 device stats".replace("與", "與"), "fixture 與測試機結果一致".replace("與", "與").replace("測試", "測試").replace("結", "結")],
            ["Phase 3", "StorCLI/PERCCLI；Arcconf；SSA CLI", "按控制器型號通過真實輸出 fixture".replace("號通過真實輸", "號通過真實輸")],
            ["Phase 4", "Portal 儲存儀表板、告警、n8n/LINE 通知".replace("儲", "儲").replace("儀", "儀"), "容量/降級/重建事件可追溯".replace("級", "級")],
        ], [26 * mm, 79 * mm, 57 * mm], styles),
        p("建議代碼結構".replace("建議", "建議").replace("結", "結"), styles["h2"]),
        p("app/storage_mcp.py<br/>app/storage/backends/base.py<br/>app/storage/backends/linux.py<br/>app/storage/backends/mdadm.py<br/>app/storage/backends/zfs.py<br/>app/storage/backends/btrfs.py<br/>app/storage/backends/lvm.py<br/>app/storage/backends/storcli.py<br/>app/storage/normalizer.py<br/>deploy/self-hosted/ai-work-storage-cli<br/>tests/fixtures/storage/&lt;backend&gt;/", styles["code"]),
        p("測試要求".replace("測試", "測試"), styles["h2"]),
        *bullet([
            "每個 adapter 至少包含：無工具、無資源、healthy、degraded、rebuilding 與命令失敗案例。".replace("個", "個").replace("無", "無").replace("資", "資").replace("與", "與").replace("敗", "敗"),
            "惡意 ID、路徑穿越、分號、換行與超長輸入必須被拒絕。".replace("惡", "惡").replace("徑", "徑").replace("換", "換").replace("與", "與").replace("長輸須絕", "長輸入必須被拒絕"),
            "真實命令輸出必須保存去敏 fixture，避免只用手寫理想樣本。".replace("真實", "真實").replace("輸須", "輸出必須").replace("寫", "寫").replace("樣", "樣"),
            "端到端驗證 tools/list、每項 tools/call、Bearer 401、逾時與審計記錄。".replace("驗證", "驗證").replace("項", "項").replace("時與審計記錄", "時與稽覈紀錄"),
        ], styles),
        p("部署回退", styles["h2"]),
        p("新 endpoint 與 nas-storage registry 可獨立啓用。若 adapter 發生問題，可停用 nas-storage 並繼續使用原 /mcp/ssd；不需要回退數據庫或觸碰儲存陣列。".replace("與", "與").replace("獨", "獨").replace("啓", "啟").replace("發生問", "發生問").replace("並繼續", "並繼續").replace("數據", "資料").replace("觸", "觸").replace("儲", "儲").replace("陣", "陣"), styles["callout"]),
        PageBreak(),
    ])

    story.extend([
        p("8. 使用範例與驗收清單".replace("範", "範").replace("與驗收清單", "與驗收清單"), styles["h1"]),
        p("自然語言範例".replace("語", "語").replace("範", "範"), styles["h2"]),
        *bullet([
            "檢查所有 NAS 儲存後端，並畫出實體磁碟、陣列、LVM、Volume 與掛載點關係。".replace("檢查", "檢查").replace("儲", "儲").replace("後", "後").replace("並", "並").replace("實體", "實體").replace("陣", "陣").replace("與", "與").replace("掛載", "掛載"),
            "列出所有降級或重建中的 RAID，並顯示成員盤、進度與預計完成時間。".replace("級", "級").replace("並顯", "並顯").replace("員盤", "員碟").replace("進", "進").replace("與預計", "與預計").replace("時間", "時間"),
            "檢查 ZFS pool 的健康、容量、最近 scrub 與錯誤事件，只能讀取。".replace("檢查", "檢查").replace("與錯誤", "與錯誤").replace("讀", "讀"),
            "目前哪些磁碟的 SMART 異常，且它們屬於哪個陣列或 Pool？".replace("異", "異").replace("們屬", "們屬").replace("個陣", "個陣"),
        ], styles),
        p("預期自動發現回應".replace("預", "預").replace("動", "動").replace("發現", "發現").replace("應", "應"), styles["h2"]),
        p("{<br/>  \"backends\": [<br/>    {\"type\": \"single_disk\", \"available\": true, \"resources\": 1},<br/>    {\"type\": \"lvm\", \"available\": true, \"resources\": 1},<br/>    {\"type\": \"mdadm\", \"available\": true, \"resources\": 0},<br/>    {\"type\": \"btrfs\", \"available\": true, \"resources\": 0},<br/>    {\"type\": \"zfs\", \"available\": false, \"reason\": \"cli_missing\"},<br/>    {\"type\": \"hardware_raid\", \"available\": false, \"reason\": \"controller_not_detected\"}<br/>  ]<br/>}", styles["code"]),
        p("驗收清單".replace("驗", "驗").replace("單", "單"), styles["h2"]),
        styled_table([
            ["檢查項".replace("檢查項", "檢查項"), "通過條件".replace("通過條", "通過條")],
            ["發現".replace("發現", "發現"), "同時回報已啓用、無資源與缺少 CLI 的後端".replace("同時", "同時").replace("啓", "啟").replace("無資", "無資").replace("與", "與").replace("後", "後")],
            ["拓撲", "每個 Volume 可追溯到 Pool/Array 與實體磁碟".replace("個", "個").replace("與實體", "與實體")],
            ["狀態".replace("狀態", "狀態"), "healthy/degraded/failed/rebuilding 不因後端不同而改變語義".replace("後", "後").replace("變語", "變語")],
            ["安全", "所有工具唯讀；惡意參數被拒絕；無通用 sudo 或 shell".replace("讀", "讀").replace("惡", "惡").replace("參數", "參數").replace("絕", "絕").replace("無", "無")],
            ["相容", "原 ssd_list_devices、ssd_get_usage、ssd_get_health 繼續可用".replace("繼續", "繼續")],
            ["稽覈", "可查詢調用者、工具、目標、後端、時間與結果".replace("詢調用", "詢呼叫").replace("目標", "目標").replace("後", "後").replace("時間與結", "時間與結")],
            ["回退", "停用 nas-storage 後，原 NAS SSD CLI MCP 不受影響".replace("後", "後").replace("影響", "影響")],
        ], [55 * mm, 107 * mm], styles),
        Spacer(1, 6 * mm),
        p("結論".replace("結", "結"), styles["h2"]),
        p("此方案可以在不開放通用 CLI、不修改現有陣列的前提下，把 NAS 的實體磁碟、RAID、Pool、LVM 與文件系統統一提供給 LLM。建議先完成 Phase 1，在當前服務器驗證單磁碟 + LVM + ext4 拓撲，再進入 ZFS/Btrfs 與硬件 RAID。".replace("開放", "開放").replace("現", "現").replace("陣", "陣").replace("實體", "實體").replace("與", "與").replace("系統", "系統").replace("統", "統").replace("給", "給").replace("建議", "建議").replace("當前", "目前").replace("務", "務").replace("驗證單", "驗證單").replace("進", "進").replace("硬件", "硬體"), styles["callout"]),
    ])

    doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
