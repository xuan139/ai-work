const messages = {
  "zh-Hant": {
    documentTitle: "AI Work 會議入口",
    language: { label: "語言切換" },
    loading: { active: "正在載入資料..." },
    login: {
      eyebrow: "NAS 安全工作區",
      title: "AI Work NAS 會議入口",
      copy: "登入後可使用瀏覽器錄音，也可接收 NAS 共享資料夾的新錄音提醒，並查詢已入庫的會議轉寫結果。",
      username: "使用者名稱",
      password: "密碼",
      submit: "登入系統",
    },
    sidebar: {
      subtitle: "NAS 會議智慧工作台",
      navLabel: "主導覽",
    },
    nav: {
      dashboard: "總覽",
      record: "會議記錄",
      upload: "NAS 上傳",
      network: "網路資料",
      models: "模型管理",
      meetings: "資料庫查詢",
      aiwork: "AI Work",
      settings: "設定與管理",
      mcp: "MCP 管理",
      n8n: "n8n 自動化",
      lineAdmin: "LINE 企業管理",
      accounts: "帳號管理",
    },
    nas: {
      title: "NAS 發現服務",
      subtitle: "監聽 mock_nas/inbox",
    },
    topbar: {
      eyebrow: "會議智慧",
    },
    auth: {
      logout: "登出",
    },
    network: {
      eyebrow: "NAS 網路收件",
      title: "下載 YouTube 內容",
      copy: "貼上單一 YouTube 影片網址，內容會由 NAS 背景下載並保存原始檔，再交給既有音訊轉寫或影片分析流程。",
      urlLabel: "YouTube 網址",
      urlPlaceholder: "https://www.youtube.com/watch?v=...",
      titleLabel: "NAS 顯示名稱（選填）",
      titlePlaceholder: "留空時使用 YouTube 影片標題",
      mediaLabel: "保存格式與後續流程",
      videoOption: "影片 · 保存 MP4 並交給 YOLO 分析",
      audioOption: "音訊 · 轉為 M4A 並交給 Whisper 轉寫",
      rightsConfirm: "我確認有權下載、保存及處理此內容",
      submit: "下載到 NAS",
      submitting: "正在建立下載任務...",
      pipelineLabel: "網路資料處理流程",
      stepDownload: "NAS 背景下載",
      stepArchive: "原始內容歸檔",
      stepAnalyze: "Whisper / YOLO 分析",
      stepRag: "建立 RAG 索引",
      policy: "僅支援公開、非直播的單一 YouTube 影片。請遵守著作權、YouTube 服務條款及公司資料政策。",
      jobsEyebrow: "下載與處理記錄",
      jobsTitle: "網路資料佇列",
      refresh: "刷新",
      empty: "尚無網路資料下載記錄",
      openAsset: "查看 NAS 資產",
      source: "YouTube 來源",
      queued: "YouTube 下載任務已建立",
      failed: "建立下載任務失敗",
    },
    accounts: {
      eyebrow: "NAS 存取控制",
      title: "帳號與權限管理",
      copy: "集中管理 Portal 登入、NAS 資產存取範圍與管理員權限。停用、角色或密碼變更會撤銷既有 Session。",
      metricsLabel: "帳號摘要",
      total: "帳號總數",
      active: "啟用中",
      admins: "管理員",
      createEyebrow: "新增存取身分",
      createTitle: "建立帳號",
      username: "使用者名稱",
      usernamePlaceholder: "user.name",
      password: "初始密碼",
      passwordPlaceholder: "至少 8 個字元",
      role: "角色",
      create: "建立帳號",
      directoryEyebrow: "使用者目錄",
      directoryTitle: "Portal 帳號",
      search: "搜尋",
      searchPlaceholder: "搜尋帳號或角色",
      account: "帳號",
      status: "狀態",
      activity: "活動",
      actions: "操作",
      roles: { admin: "管理員", user: "一般使用者" },
      statuses: { active: "啟用", inactive: "已停用" },
      created: "建立",
      lastLogin: "最後登入",
      never: "尚未登入",
      records: "{assets} 項 NAS 資產 · {meetings} 場會議 · {calls} 次模型呼叫",
      save: "儲存權限",
      reset: "重設密碼",
      delete: "刪除",
      empty: "沒有符合條件的帳號",
      current: "目前登入",
      protected: "帳號已有 NAS 資料，請改為停用",
      resetEyebrow: "帳號安全",
      resetTitle: "重設密碼",
      newPassword: "新密碼",
      resetHint: "重設後，該帳號目前的登入 Session 將立即失效。",
      confirmReset: "確認重設",
      resetFor: "為 {username} 設定新密碼",
      confirmDelete: "確定刪除帳號 {username}？此操作無法復原。",
      createdSuccess: "帳號已建立",
      updatedSuccess: "帳號權限已更新",
      resetSuccess: "密碼已重設",
      deletedSuccess: "帳號已刪除",
      operationFailed: "帳號操作失敗",
      duplicate: "使用者名稱已存在",
      invalidUsername: "使用者名稱需為 3–32 個字元，只能使用英文字母、數字、句點、底線或連字號",
      invalidPassword: "密碼長度必須為 8–128 個字元",
      selfProtection: "不能停用自己或移除自己的管理員權限",
      ownsRecords: "此帳號已有 NAS 資料，請改為停用",
    },
    lineAdmin: {
      eyebrow: "LINE 公司治理",
      title: "LINE 企業管理",
      copy: "只有管理員核准的群組能使用公司 NAS、RAG 與模型。個人聊天室不會取得公司資料或公司 API Key。",
      metricsLabel: "LINE 管理摘要",
      totalGroups: "已發現群組",
      approvedGroups: "已核准",
      monthlyCalls: "本月呼叫",
      monthlyTokens: "本月 Token",
      directoryEyebrow: "公司群組目錄",
      directoryTitle: "模型與資料存取政策",
      refresh: "重新同步",
      serviceReady: "LINE 服務已連線；新群組會以待核准狀態加入。",
      serviceUnavailable: "LINE 服務目前無法同步，以下顯示 NAS 已保存的群組政策。",
      empty: "尚未發現 LINE 群組",
      pending: "待核准",
      approved: "已核准",
      groupId: "群組 ID",
      owner: "管理帳號",
      documents: "NAS 文件",
      usage: "本月用量",
      approve: "允許使用公司 AI",
      pdfSummary: "PDF 上傳後自動摘要",
      ragQueries: "允許 @Claire 查詢群組資料",
      model: "系統目前模型",
      localModel: "NAS 本地",
      companyApi: "公司 API",
      callLimit: "每月呼叫上限",
      tokenLimit: "每月 Token 上限",
      unlimitedHint: "輸入 0 表示不限額",
      save: "儲存群組政策",
      saved: "LINE 群組政策已更新",
      saveFailed: "無法更新 LINE 群組政策",
      personalBlocked: "個人聊天室固定禁止使用公司 NAS、RAG 與公司 API Key。",
    },
    n8n: {
      eyebrow: "NAS 工作流程自動化",
      title: "n8n 自動化",
      copy: "將 NAS 檔案事件、模型處理結果與企業服務串成可追蹤的工作流程。n8n 獨立執行，入口只對 AI Work 管理員開放。",
      serviceLabel: "服務狀態",
      checking: "檢查中",
      connected: "運行中",
      unavailable: "無法連線",
      consoleEyebrow: "AUTOMATION CONSOLE",
      consoleTitle: "開啟流程設計器",
      consoleCopy: "首次進入需建立 n8n Owner 帳號；之後可在視覺化編輯器建立、測試與查看每次執行結果。",
      refresh: "重新檢查",
      open: "開啟 n8n",
      versionLabel: "部署版本",
      endpointLabel: "企業入口",
      accessLabel: "存取政策",
      adminOnly: "只限管理員",
      latencyLabel: "服務回應",
      trialEyebrow: "已匯入範例",
      manualTest: "自動觸發",
      flowLabel: "n8n NAS 自動處理流程",
      step1Title: "上傳至 NAS",
      step1Copy: "上傳音訊或 PDF，不需進入 n8n 手動啟動。",
      step2Title: "完成模型處理",
      step2Copy: "音訊完成 ASR；PDF 完成文字抽取、OCR 與 RAG 建庫。",
      step3Title: "建立 Execution",
      step3Copy: "NAS 送出事件，n8n 保存每次執行的輸入與回傳結果。",
      step4Title: "推送企業 LINE",
      step4Copy: "將摘要或逐字稿預覽推送到已核准的企業群組。",
      readyNotice: "服務已就緒。上傳音訊或 PDF，處理完成後可在 n8n Executions 查看整條流程。",
      unavailableNotice: "n8n 服務目前無法連線，請重新檢查或查看伺服器狀態。",
    },
    odoo: {
      eyebrow: "企業流程連接器",
      title: "Odoo MCP",
      copy: "讓 LLM 在權限控管下呼叫 Odoo MCP 工具，查詢企業流程與營運資料；目前僅提供介面占位，尚未建立實際連線。",
      statusLabel: "Odoo MCP 狀態",
      notConnected: "尚未連線",
      placeholderStatus: "MCP Server、驗證與工具清單待設定",
      flowEyebrow: "預定呼叫流程",
      flowTitle: "LLM 如何存取 Odoo",
      stage: "規劃中",
      steps: {
        requestTitle: "LLM 接收企業問題",
        requestCopy: "使用者以自然語言提出財務、銷售、庫存或營運查詢。",
        policyTitle: "身分與權限檢查",
        policyCopy: "NAS 依登入者、部門與工具白名單判斷可讀取的 Odoo 資料範圍。",
        mcpTitle: "呼叫 Odoo MCP 工具",
        mcpCopy: "核准後由 MCP Server 將模型請求轉換為受控的 Odoo API 操作。",
        auditTitle: "回覆與 NAS 稽核",
        auditCopy: "LLM 整理結果，並在 NAS 保存呼叫者、工具、輸入、輸出與時間。",
      },
      promptLabel: "LLM 指令",
      promptPlaceholder: "例如：整理本月銷售額與未收款客戶",
      runDisabled: "設定 MCP 後啟用",
      notice: "此頁目前不會向 Odoo、MCP Server 或任何模型送出資料。",
    },
    mcp: {
      eyebrow: "NAS 工具連接器",
      title: "MCP 管理",
      copy: "集中管理可供公司 LLM 使用的 MCP Server、連線狀態、工具清單與權限入口；認證內容只由 NAS 環境變數提供。",
      metricsLabel: "MCP 摘要",
      total: "連接器",
      connected: "已連線",
      enabled: "已啟用",
      tools: "工具",
      directoryEyebrow: "公司 MCP Registry",
      directoryTitle: "Server 與工具清單",
      refresh: "重新整理",
      add: "新增 MCP",
      search: "搜尋",
      searchPlaceholder: "搜尋名稱、Endpoint 或服務",
      securityNote: "官方 Endpoint 已預先列入安全清單；OAuth 服務仍需完成企業授權或設定 Access Token。SSE 與 stdio 第一階段只保存設定。",
      empty: "尚未登錄 MCP Server",
      categories: {
        nas: { title: "NAS 與知識資料", copy: "存取 NAS 檔案、企業文件與內部知識庫。" },
        office: { title: "辦公與通訊", copy: "電子郵件、Google Workspace、行事曆與團隊訊息。" },
        spreadsheet: { title: "試算表與 Excel", copy: "分析 NAS Excel、CSV、TSV、Google Sheets 與 Microsoft 365 活頁簿。" },
        finance: { title: "財務會計與 ERP", copy: "會計、付款、發票、財務報表與企業資源管理。" },
        project: { title: "專案管理與協作", copy: "專案、任務、Issue、里程碑與跨部門協作。" },
        technical: { title: "開發、雲端與資料庫", copy: "程式碼、部署、雲端基礎設施與資料庫工具。" },
        other: { title: "其他連接器", copy: "公司自行新增或尚未歸類的 MCP Server。" },
      },
      connectorCount: "{count} 個連接器",
      status: { connected: "已連線", failed: "連線失敗", unchecked: "待測試", unconfigured: "未設定" },
      transport: "Transport",
      endpoint: "Endpoint／設定參考",
      endpointPlaceholder: "http://127.0.0.1:9000/mcp",
      auth: "認證",
      requestHeaders: "固定 Headers",
      authType: "認證類型",
      authTypes: { none: "無", bearer: "Bearer Token", oauth2: "OAuth 2.0", managed: "供應商管理流程", custom: "自訂" },
      authReady: "環境變數已設定",
      authMissing: "環境變數未設定",
      authNone: "不使用認證",
      protocol: "Protocol",
      lastChecked: "最後同步",
      neverChecked: "尚未同步",
      enabledForLlm: "允許公司 LLM 使用",
      disabledForLlm: "未開放給公司 LLM",
      edit: "編輯",
      sync: "測試並同步工具",
      syncing: "正在連線...",
      syncSuccess: "MCP 工具清單已同步",
      syncFailed: "MCP 連線或同步失敗",
      copyEndpoint: "複製 Endpoint",
      endpointCopied: "Endpoint 已複製",
      officialSource: "官方文件",
      noTools: "尚無已同步工具",
      toolInput: "輸入 Schema",
      modalEyebrow: "MCP Registry",
      modalAddTitle: "新增 MCP Server",
      modalEditTitle: "編輯 MCP Server",
      name: "顯示名稱",
      namePlaceholder: "例如：Odoo Production",
      slug: "識別碼",
      authEnv: "認證環境變數",
      sourceUrl: "官方文件來源",
      enableServer: "允許公司 LLM 使用",
      descriptionZh: "繁體中文說明",
      descriptionEn: "English description",
      authHint: "只保存環境變數名稱；Token 或密碼必須由伺服器 .env 提供，不會寫入資料庫。",
      save: "儲存 MCP",
      saved: "MCP 設定已儲存",
      duplicate: "MCP 識別碼已存在",
    },
    dashboard: {
      eyebrow: "NAS Demo 範圍",
      title: "NAS 檔案發現、語音歸檔、會議轉寫查詢",
      copy: "第一版聚焦 NAS 會議資產進入系統後的完整鏈路：瀏覽器錄音或共享資料夾檔案進站、NAS inbox 即時提醒、後台搬移與處理狀態，以及可搜尋的歷史會議記錄。",
    },
    dashboardAssets: {
      eyebrow: "NAS 資產庫",
      title: "所有已上傳檔案",
      copy: "依上傳時間由新到舊顯示 audio、video、文件與圖片；點擊即可查看分析結果與重新處理。",
      filterLabel: "資產類型",
      all: "全部",
      audio: "Audio",
      video: "Video",
      documents: "文件",
      images: "圖片",
      upload: "上傳新檔案",
      newest: "最新上傳",
      uploader: "上傳者",
      uploadedAt: "上傳時間",
      open: "查看詳情",
      transcript: "逐字稿預覽",
      transcriptDetail: "逐字稿詳情",
      transcriptProcessing: "逐字稿正在背景處理中。",
      transcriptUnavailable: "此音訊尚無逐字稿。",
      empty: "此分類尚無 NAS 資產",
    },
    nasFeatures: {
      eyebrow: "NAS Demo",
      title: "企業 NAS 會議資料入口",
      copy: "把共享資料夾當作語音資產進站點：檔案一進 inbox 就被發現、通知、搬移、入庫、轉寫，後續可依權限查詢。",
      dropzoneTitle: "共享目錄 Drop Zone",
      dropzoneCopy: "使用 mock_nas/inbox 作為 SMB / NFS 共享資料夾入口，會議錄音可由錄音筆、會議室主機或同步工具放入。",
      watchTitle: "熱資料夾監聽",
      watchCopy: "後台輪詢 NAS inbox，偵測新檔後立即在前端 popup，表示檔案已進入處理佇列。",
      archiveTitle: "原始音訊歸檔",
      archiveCopy: "保存原始 voice 檔到 storage/recordings，並把 NAS 原檔移到 processed，保留可追蹤的處理路徑。",
      indexTitle: "索引與權限查詢",
      indexCopy: "轉寫結果、來源、狀態與時間寫入資料庫，登入後才能依權限檢索會議資料。",
    },
    metrics: {
      total: "會議記錄",
      processing: "處理中",
      completed: "已完成",
    },
    modules: {
      record: {
        title: "會議記錄",
        copy: "網頁錄音會像 NAS 進站檔案一樣保存原始 voice，並啟動同一條轉寫處理流程。",
      },
      upload: {
        title: "NAS 上傳",
        copy: "上傳 audio、video、文件與試算表，NAS 收件後進入 ASR、影片分析、RAG 或 SQL 查詢流程。",
      },
      meetings: {
        title: "資料庫查詢",
        copy: "查詢來自 NAS 或網頁錄音的會議標題、原始檔名、來源與轉寫文本。",
      },
      aiwork: {
        copy: "後續可基於 NAS 會議資料庫做摘要、行動項提取、問答與模型呼叫審計。",
      },
    },
    record: {
      eyebrow: "NAS 同步錄音",
      title: "新建會議錄音並歸檔",
      meetingTitle: "會議標題",
      titlePlaceholder: "例如：產品週會 09/09",
      asrTitle: "步驟 1：選擇轉寫模型",
      asrCopy: "錄音停止後，NAS 會使用此模型建立逐字稿、向量與 RAG 索引。",
      asrModeLabel: "執行位置",
      asrModeLocal: "本地 NAS",
      asrModeCloud: "雲端 API",
      asrModelLabel: "語音模型",
      systemAsrTitle: "系統語音模型",
      systemAsrCopy: "此錄音會使用管理員在「設定與管理」選定的語音模型。",
      asrKeyPlaceholder: "只用於本次會議錄音",
      asrLanguages: "語言",
      asrBestFor: "適合",
      asrReady: "本地模型已就緒，可直接處理錄音。",
      asrDownloading: "模型正在下載：{progress}%。錄音可先保存，但轉寫需等下載完成。",
      asrNotReady: "本地模型尚未就緒，請到 NAS 模型管理完成安裝，或改選已就緒模型。",
      asrCloud: "此模型由雲端處理，必須先由管理員設定公司 API Key。",
      asrKeyRequired: "{model} 需要 API Key，請先輸入後再開始錄音。",
      asrModelRequired: "請先選擇語音處理模型。",
      translationTitle: "步驟 2：逐字稿翻譯",
      translationCopy: "選擇目標語言後，由系統目前 LLM 統一翻譯；原文與譯文會分開保存。",
      translationEnable: "啟用翻譯",
      translationTarget: "目標語言",
      translationMode: "翻譯位置",
      translationModel: "翻譯模型",
      translationSystemModel: "系統翻譯模型",
      translationKey: "翻譯模型 API Key",
      translationKeyPlaceholder: "只用於本次翻譯",
      translationModelRequired: "請先選擇翻譯模型。",
      translationKeyRequired: "{model} 需要 API Key，請先輸入後再開始。",
      translationLocalHint: "逐字稿會由 NAS 本地模型處理，不會傳送到外部服務。",
      translationCloudHint: "逐字稿會傳送至 {provider}；API Key 只用於本次工作，不會寫入資料庫。",
      lineTitle: "步驟 3：推送至 LINE 群組",
      lineCopy: "轉寫完成後，由 NAS 本地 Qwen 產生摘要、決議與待辦事項，再推送到指定群組。",
      lineEnable: "啟用推送",
      lineGroup: "LINE 群組",
      lineMessages: "{count} 則記錄",
      lineFullTranscript: "同時分段推送完整原文逐字稿",
      lineSummaryOnly: "預設只推送摘要與 NAS 查看入口，群組可用 @Claire 查詢這場會議。",
      lineFullWarning: "完整逐字稿會拆成多則 LINE 訊息；長會議建議保留在 NAS 中查閱。",
      lineUnavailable: "目前無法取得 LINE 群組，請確認 LINE webhook 服務。",
      lineNoGroups: "尚未發現 Claire 已加入且有訊息記錄的 LINE 群組。",
      lineGroupRequired: "請先選擇要接收會議摘要的 LINE 群組。",
      linePushStatus: "LINE 推送",
      lineSummaryTitle: "LINE 會議摘要",
      lineWaiting: "等待轉寫與摘要完成後推送。",
      lineError: "推送失敗：{error}",
      lineSummaryMode: "摘要、決議與待辦",
      lineFullMode: "摘要與完整文字稿",
      languages: {
        zhHant: "繁體中文",
        en: "英文",
        zhHans: "簡體中文",
        ja: "日文",
        ko: "韓文",
        es: "西班牙文",
        fr: "法文",
        de: "德文",
      },
      optionsTitle: "錄音處理設定",
      optionsCopy: "查看系統語音模型，並設定翻譯與 LINE 推送。",
      start: "開始錄音",
      pause: "暫停",
      resume: "繼續",
      stop: "停止並保存",
      hint: "瀏覽器會請求麥克風權限。停止後系統會把原始錄音保存到本地 storage，按照 NAS 會議音訊歸檔流程進入轉寫佇列。",
      defaultTitle: "瀏覽器錄音",
      uploadFailed: "錄音上傳失敗，請重試",
      saved: "錄音已保存，正在處理",
      unavailable: "無法錄音",
      secureRequired: "麥克風錄音需要 HTTPS 安全連線，請改用 HTTPS 或透過 localhost 開啟此系統。",
      mediaUnavailable: "此瀏覽器不支援麥克風存取，請使用最新版 Chrome、Edge 或 Safari。",
      secureHint: "目前頁面使用 HTTP 公網連線，瀏覽器已停用麥克風。請改用 HTTPS 或 SSH Tunnel 的 localhost 位址。",
      states: {
        idle: "待開始",
        recording: "正在錄音",
        paused: "已暫停",
        saving: "保存中",
      },
    },
    activity: {
      eyebrow: "即時動態",
      title: "即時處理動態",
      fallbackTitle: "會議處理",
    },
    upload: {
      eyebrow: "NAS 收件",
      title: "上傳 NAS 資料",
      copy: "支援 audio、video、圖片、PDF、DOCX、Excel、CSV 與 TSV。試算表可透過 NAS Excel SQL MCP 查詢與分析。",
      fileLabel: "選擇檔案",
      titleLabel: "資料名稱",
      titlePlaceholder: "例如：董事會錄音、產品簡報 PDF",
      asrTitle: "步驟 1：音訊轉寫模型",
      asrCopy: "上傳 audio 時可選本地或雲端 ASR；其他檔案會自動略過此設定。",
      asrModeLabel: "執行位置",
      asrModeLocal: "本地 NAS",
      asrModeCloud: "雲端 API",
      asrModelLabel: "ASR 模型",
      systemAsrTitle: "音訊轉寫模型",
      systemAsrCopy: "Audio 會使用管理員在「設定與管理」選定的系統語音模型。",
      asrKeyLabel: "API Key",
      asrKeyPlaceholder: "只用於本次 audio 上傳",
      asrHint: "本地模型適合 NAS 私有化；雲端模型需要 API Key，Key 只用於本次上傳，不寫入資料庫。",
      translationTitle: "步驟 2：逐字稿翻譯",
      translationCopy: "只套用於 audio；可指定目標語言，翻譯使用系統目前 LLM。",
      videoTitle: "影片分析模型",
      videoCopy: "上傳 video 時可選本地或雲端模型；其他檔案會自動略過此設定。",
      videoModeLabel: "執行位置",
      videoModeLocal: "本地 NAS",
      videoModeCloud: "雲端 API",
      videoModelLabel: "Video 模型",
      videoKeyLabel: "Video API Key",
      videoKeyPlaceholder: "只用於本次 video 上傳",
      videoHint: "本地 YOLO 會在 NAS 主機抽幀與偵測物件；雲端模型需要 API Key，Key 只用於本次上傳，不寫入資料庫。",
      modelManagerTitle: "NAS 模型管理",
      modelManagerCopy: "管理可由 NAS 主機執行的本地 ASR 與 video 模型。下載只會在按下按鈕後開始。",
      refreshModels: "刷新",
      runtimeReady: "Runtime 已就緒",
      runtimeMissing: "Runtime 未就緒",
      modelPath: "模型路徑",
      modelSize: "模型大小",
      modelProgress: "下載進度",
      modelSetupHint: "設定方式",
      downloadModel: "下載",
      cancelDownload: "取消",
      retryDownload: "重試",
      installedModel: "已安裝",
      noPanelDownload: "需依設定安裝",
      modelActionFailed: "模型操作失敗",
      modelStatus: {
        installed: "已安裝",
        registered: "已登錄",
        testing: "測試中",
        ready: "可使用",
        runtime_missing: "缺少 Runtime",
        partial: "部分下載",
        missing: "未安裝",
        downloading: "下載中",
        cancelling: "取消中",
        cancelled: "已取消",
        failed: "失敗",
      },
      setupHints: {
        whisper_cpp_setup: "需要 whisper-cli 與完整 ggml 模型檔",
        python_asr_setup: "執行 pip install -r requirements-asr.txt",
        python_video_setup: "執行 pip install -r requirements-video.txt，並下載完整 YOLO 權重",
        openai_endpoint_setup: "需要可回應 /v1/chat/completions 的 NAS loopback 服務",
      },
      submit: "上傳到 NAS",
      uploading: "正在上傳 {progress}%",
      largeFileHint: "大型 audio/video 上傳完成後會由 NAS 自動切片，交給背景 Worker 逐段處理。",
      connectionFailed: "上傳連線中斷，請檢查網路後重試",
      reprocess: "重新處理",
      reprocessing: "正在加入佇列...",
      reprocessConfirm: "將使用目前的系統模型重新處理原始檔。現有結果會保留到新結果完成，是否繼續？",
      reprocessQueued: "原始檔已重新加入 NAS 媒體 Worker 佇列",
      openccTraditional: "OpenCC 簡轉繁",
      openccRunning: "正在轉換...",
      openccConfirm: "將現有逐字稿、翻譯與 RAG 片段統一轉為繁體中文，並重建向量索引。是否繼續？",
      actionFailed: "資產操作失敗",
      nasVolumeLabel: "NAS Volume",
      shareProtocolLabel: "共享協議",
      snapshotLabel: "快照策略",
      snapshotValue: "每日 02:00，保留 30 版",
      aclLabel: "權限來源",
      aclValue: "登入使用者 + NAS ACL",
      assetsEyebrow: "NAS 資產",
      assetsTitle: "收件與處理狀態",
      searchLabel: "搜尋",
      searchPlaceholder: "搜尋檔名、類型或分析結果",
      emptyList: "尚無 NAS 資產",
      emptyDetail: "選擇一個 NAS 資產查看處理結果",
      uploadRequired: "請先選擇檔案",
      uploadFailed: "NAS 上傳失敗",
      dialogEyebrow: "NAS 已收件",
      dialogTitle: "NAS 收到上傳成功",
      dialogAction: "查看處理狀態",
      dialogMessage: "NAS 已收到《{title}》，目前交給 {analyzer} 處理。",
      owner: "上傳者",
      filename: "原始檔名",
      selectedAsr: "選用 ASR",
      selectedTranslation: "選用翻譯",
      selectedVideo: "選用 Video",
      sourceAudioTitle: "原始音訊",
      sourceAudioCopy: "直接播放保存在 NAS 的完整原始檔。",
      sourceVideoTitle: "原始影片",
      sourceVideoCopy: "直接播放保存在 NAS 的 YouTube 下載影片或上傳影片。",
      downloadSource: "下載原始檔",
      downloadSegment: "下載此片段",
      wholeFile: "完整檔案",
      audioSegmentsTitle: "音訊切片",
      audioSegmentsCopy: "大型音訊可逐段播放與下載；未切分的音訊會以完整檔案作為單一片段。",
      transcribeSegment: "單獨轉寫",
      retranscribeSegment: "重新轉寫",
      segmentTranscriptionQueued: "等待 Whisper Worker",
      segmentTranscriptionProcessing: "Whisper 轉寫中",
      segmentTranscriptionCompleted: "片段逐字稿已保存",
      segmentTranscriptionFailed: "片段轉寫失敗",
      segmentTranscript: "片段逐字稿",
      segmentTranscriptionQueuedToast: "此片段已加入 Whisper 轉寫佇列",
      videoSegmentsTitle: "影片切片",
      videoSegmentsCopy: "大型影片可逐段下載；未切分的影片會以完整檔案作為單一片段。",
      audioSegment: "第 {number} 段",
      audioSegmentRange: "{start} 至 {end}",
      noAudioSegments: "目前沒有播放切片。短音訊可直接播放原始檔；大型音訊完成重新處理後會在此顯示切片。",
      transcriptTitle: "完整逐字稿",
      downloadTranscript: "下載完整逐字稿",
      downloadSegmentTranscript: "下載此段逐字稿",
      transcriptMeta: "{chunks} 個逐字稿片段 · {characters} 字",
      transcriptEmpty: "此音訊尚未產生逐字稿。",
      category: "類型",
      analyzer: "分析器",
      fileSize: "大小",
      chunkCount: "RAG chunks",
      summary: "處理結果",
      processTitle: "NAS 處理流程",
      processCopy: "下方顯示此檔案進站後經過的 NAS 服務、解析器與模型調用狀態。",
      stepDone: "已完成",
      stepActive: "執行中",
      stepPending: "待處理",
      stepBlocked: "需要設定",
      stepSkipped: "已略過",
      stepConfigured: "已選定",
      chunks: "RAG 片段",
      page: "頁碼",
      type: "類型",
      pagePreview: "頁面預覽",
      answerSources: "引用來源",
      retrievalHybrid: "混合檢索",
      retrievalKeyword: "關鍵字檢索",
      retrievalScore: "綜合分數",
      semanticScore: "語意",
      keywordScore: "關鍵字",
      cacheHit: "NAS 回答快取命中",
      cacheExact: "相同問題",
      cacheSemantic: "語意相近",
      questionTitle: "用 LLM 處理此資產",
      questionEyebrow: "RAG 文件問答",
      questionCopy: "圖片、文件或逐字稿已建立 RAG chunks，提問時會使用管理員指定的系統 LLM。",
      modelRequired: "需要先選擇模型",
      questionRequired: "請先輸入問題",
      ask: "處理文件",
      questionPlaceholder: "例如：請整理這份文件的重點與待辦事項",
      answerTitle: "文件處理結果",
      analysisHistoryTitle: "NAS AI 分析知識",
      analysisHistoryCopy: "以下雲端分析結果已保存於 NAS，並建立可供後續查詢的 RAG chunks。",
      analysisQuestion: "分析問題",
      analysisSaved: "分析結果已自動保存到 NAS 並加入 RAG",
      analysisAlreadySaved: "已使用 NAS 中相同的分析知識，不會重複建庫",
      analysisEmbeddingQueued: "分析已保存，Embedding 已排入 NAS 背景補建",
      modelNeedsKey: "此模型需要 API Key，請先設定模型",
      noRag: "此檔案尚未建立 RAG chunks；圖片、audio、video、PDF 或 DOCX 完成處理後才能做 RAG 問答。",
      timeline: {
        intakeTitle: "NAS 收件與權限檢查",
        intakeEngine: "FastAPI Upload + SQLite Audit",
        intakeCopy: "檔案寫入 storage/nas_assets，紀錄上傳者、原始檔名、大小、MIME type 與處理狀態。",
        archiveTitle: "NAS 歸檔與索引",
        archiveEngine: "NAS Asset Indexer",
        archiveCopy: "建立資產 ID，保存來源路徑，後續可依登入權限查詢。",
        audioNormalizeTitle: "音訊標準化",
        audioNormalizeEngine: "FFmpeg Audio Normalize",
        audioNormalizeCopy: "正式部署會轉成 16kHz mono WAV，方便長會議穩定進入 ASR。此 demo 保留原始音訊並把標準化列入處理流程。",
        vadTitle: "長音訊切段",
        vadEngine: "FSMN-VAD / Silero VAD",
        vadCopy: "正式部署會先偵測語音區段，長會議分段後再送入語音模型，降低超時與漏字風險。",
        pdfRenderTitle: "PDF 頁面渲染",
        pdfRenderEngine: "PyMuPDF",
        pdfRenderCopy: "把 PDF 每頁渲染成 PNG，提供 OCR 輸入與 RAG 來源頁面預覽。",
        pdfTextTitle: "PDF 文字層抽取",
        pdfTextEngine: "pypdf",
        pdfTextCopy: "如果 PDF 內有可選文字，直接抽取文字並切成頁級 RAG chunks。",
        ocrTitle: "圖片型 PDF OCR",
        ocrEngine: "PaddleOCR PP-OCRv6",
        ocrCopy: "當 pypdf 抽不到文字層時，對每頁圖片執行 OCR，產生 image_ocr chunks。",
        ragTitle: "RAG 建庫",
        ragEngine: "Qwen3-Embedding-0.6B + SQLite document_chunks",
        ragCopy: "寫入 chunk 內容、頁碼、類型、圖片路徑與 1024 維向量；服務中斷時由 NAS 背景工作補建。",
        docxTitle: "DOCX 文件解析",
        docxEngine: "python-docx",
        docxCopy: "抽取段落與表格文字，轉成可查詢的 RAG chunks。",
        imageDecodeTitle: "圖片格式與完整性檢查",
        imageDecodeEngine: "NAS Image Intake",
        imageDecodeCopy: "辨識 JPG、PNG、WebP、TIFF、BMP 與 image MIME type，保存原圖並確認可供 OCR 讀取。",
        imageOcrTitle: "圖片文字辨識",
        imageOcrEngine: "PaddleOCR PP-OCRv6",
        imageOcrCopy: "在 NAS 本地辨識圖片中的中英文文字，寫入 image_ocr chunks，並保留原圖作為 RAG 引用預覽。",
        audioTitle: "語音轉文字",
        audioEngine: "Selected ASR Model",
        audioCopy: "依使用者選擇調用本地 whisper.cpp、faster-whisper、SenseVoiceSmall、Paraformer，或雲端語音轉文字服務。",
        translationTitle: "逐字稿翻譯",
        translationEngine: "Selected Translation LLM",
        translationCopy: "依使用者指定的目標語言調用系統目前 LLM；原文與譯文分開入庫。",
        audioRagTitle: "逐字稿 RAG 建庫",
        audioRagEngine: "Transcript Chunker + Qwen3 Embedding",
        audioRagCopy: "ASR 結果切成 audio_transcript chunks 並建立向量，後續可用 LLM 查詢會議內容。",
        videoTitle: "影片內容分析",
        videoEngine: "Selected Video Model",
        videoCopy: "依使用者選擇調用本地 YOLO 抽幀偵測，或等待雲端影片分析 API 設定後執行。",
        videoRagTitle: "影片結果 RAG 建庫",
        videoRagEngine: "Detection Chunker + Qwen3 Embedding",
        videoRagCopy: "把影片時間點、偵測物件、信心分數與畫面預覽寫入 chunks，並建立可檢索向量。",
        llmTitle: "文件問答",
        llmEngine: "向量相似度 75% + 關鍵字 25%",
        llmCopy: "使用 Qwen3 query 向量與中英文關鍵字混合排序，將命中的頁碼與內容交給系統 LLM 回答。",
      },
    },
    models: {
      globalSetting: "全域模型設定",
      systemLlmTitle: "系統 LLM 設定與費用",
      systemLlmHeading: "系統預設 LLM",
      systemLlmCopy: "管理員選定後，AI Work、RAG、翻譯、LINE 與 MCP 都使用同一個模型。",
      systemAsrTitle: "系統語音模型設定",
      systemAsrHeading: "系統預設語音轉寫模型",
      systemAsrCopy: "設定一次後，會議錄音、NAS 上傳、網路音訊、熱資料夾與切片重轉都使用此模型。",
      currentAsrLabel: "系統目前語音模型",
      setSystemAsr: "設為系統語音模型",
      settingSystemAsr: "正在套用...",
      systemAsrSaved: "系統語音模型已更新",
      addModel: "新增模型",
      eyebrow: "NAS 模型登錄",
      title: "新增本地模型",
      copy: "模型會先保存於 NAS 登錄庫，通過檔案、Runtime 或 API 測試後才會出現在工作選單。",
      type: "模型類型",
      typeWhisper: "whisper.cpp 語音模型",
      typeYolo: "YOLO 影片模型",
      typeLlm: "OpenAI 相容本地 LLM",
      name: "顯示名稱",
      namePlaceholder: "例如：Whisper medium",
      slug: "模型識別碼（選填）",
      slugPlaceholder: "例如：whisper-medium",
      recommendation: "用途說明（選填）",
      recommendationPlaceholder: "例如：中文長會議轉寫",
      fileName: "NAS 模型檔名",
      filePlaceholder: "ggml-medium.bin",
      downloadUrl: "可信任下載網址（選填）",
      downloadUrlPlaceholder: "https://huggingface.co/...",
      expectedSize: "預期大小 MB（選填）",
      sha256: "SHA256（選填）",
      apiBase: "Loopback API 根位址",
      modelAlias: "API 模型 alias",
      contextTokens: "輸入上限 tokens",
      supportsTokenize: "端點支援 /tokenize",
      securityHint: "下載僅允許 Hugging Face 或 GitHub HTTPS；LLM 僅允許 NAS 本機 loopback 端點。",
      create: "建立登錄",
      customBadge: "自訂",
      test: "測試",
      remove: "移除登錄",
      saved: "模型已保存於 NAS 登錄庫",
      testReady: "模型測試完成，可在工作選單使用",
      testIncomplete: "模型檔完整，但 Runtime 尚未就緒",
      removed: "模型登錄已移除，NAS 模型檔仍保留",
      removeConfirm: "要移除此模型登錄嗎？NAS 上的模型檔不會刪除。",
      actionFailed: "自訂模型操作失敗",
    },
    meetings: {
      eyebrow: "NAS 索引查詢",
      title: "NAS 會議資料庫",
      searchLabel: "搜尋",
      searchPlaceholder: "輸入關鍵字查詢 NAS 會議記錄",
      emptyList: "暫無會議記錄",
      emptyDetail: "選擇一條 NAS 會議資產查看錄音和轉寫內容",
      waitingExcerpt: "等待處理完成後顯示轉寫內容",
      transcriptTitle: "原始逐字稿",
      translationTitle: "翻譯結果",
      translationPending: "等待轉寫完成後開始翻譯。",
      translationFailed: "翻譯失敗：{error}",
      processingText: "正在處理轉寫，請稍候。",
      failedText: "處理失敗",
      sourceNas: "NAS 發現",
      sourceWeb: "網頁錄音",
    },
    aiwork: {
      eyebrow: "NAS AI Work",
      copy: "選擇主流大模型後，可對 NAS 會議資料進行摘要、問答或審計測試；系統會查詢公開費用，並提示輸入對應供應商 API Key。",
      providerLabel: "模型供應商",
      modelLabel: "模型",
      executionLabel: "執行位置",
      localModels: "本地 NAS",
      cloudModels: "雲端 API",
      loading: "載入中...",
      allProviders: "全部供應商",
      selectProviderFirst: "請先選擇供應商",
      selectModel: "請選擇模型",
      configureKey: "設定 API Key",
      keyNotSet: "尚未設定 API Key",
      keyNotRequired: "本地模型不需要 API Key",
      keyReady: "{provider} API Key 已套用到本次工作階段",
      companyKeyReady: "公司 API Key 已由 NAS 伺服器安全配置",
      systemModelLabel: "系統目前模型",
      systemModelDefault: "NAS 預設值",
      systemModelUpdated: "由 {user} 於 {time} 設定",
      systemModelAdminHint: "管理員可從上方選擇模型，再套用到 AI Work、文件 RAG、逐字稿翻譯及 LINE。",
      systemModelUserHint: "此模型由公司管理員統一設定，所有 LLM 工作共用。",
      setSystemModel: "設為系統目前模型",
      settingSystemModel: "正在套用...",
      systemModelSaved: "系統目前模型已更新",
      selectBeforeSet: "請先選擇要套用的模型",
      saveBeforeRun: "請先將所選模型設為系統目前模型",
      emptyPricing: "選擇模型後顯示費用資訊",
      sourcesEyebrow: "Pricing Sources",
      sourcesTitle: "費用資料來源",
      sourcesCopy: "價格會變動，目前 demo 使用官方公開定價頁整理的快照。正式版可把模型費用同步任務接入 NAS 管理後台，由管理員定期刷新。",
      updatedAt: "價格快照日期",
      modelId: "模型 ID",
      context: "上下文",
      input: "輸入",
      cachedInput: "快取輸入",
      cacheWrite: "快取寫入",
      output: "輸出",
      perUnit: "每 {unit}",
      source: "官方來源",
      noCachedPrice: "未公開",
      freeQuota: "免費額度",
      freeQuotaAvailable: "可直接使用免費模型",
      freeQuotaListed: "有免費額度，但需要 API Key",
      freeQuotaUnavailable: "未列出免費額度",
      realCallNeedsKey: "此供應商的免費額度仍需 API Key，因此未設定 Key 前不能直接送出。",
      tryEyebrow: "模型試用",
      setupTitle: "模型設定與費用",
      collapseSetup: "收合",
      expandSetup: "展開",
      promptLabel: "使用者 Prompt",
      promptPlaceholder: "請輸入要交給模型處理的內容",
      promptSearchHint: "先輸入關鍵字，再查詢",
      systemPromptLabel: "系統 Prompt（選填）",
      systemPromptPlaceholder: "例如：你是企業知識助理，請以繁體中文條列回答。",
      systemPromptHint: "設定角色、語氣與輸出格式",
      suggestionsLabel: "相似歷史問題",
      suggestionCached: "NAS 快取",
      suggestionHistory: "歷史問題",
      runModel: "送出",
      forceRunModel: "強制送出",
      forceRunHint: "忽略快取並實際呼叫模型，可能產生費用",
      useMcp: "使用 MCP 工具",
      useMcpHint: "先由目前 LLM 選擇唯讀工具，取得資料後再產生最終答案",
      mcpServer: "MCP Server",
      mcpAuto: "自動選擇",
      mcpReady: "{servers} 個 Server、{tools} 個唯讀工具可用",
      mcpUnavailable: "目前沒有已連線的唯讀 MCP 工具",
      mcpTrace: "MCP 執行軌跡",
      mcpNotUsed: "LLM 判斷本次問題不需要工具",
      mcpArguments: "工具參數",
      mcpResult: "工具結果",
      useTitle: "使用 {model}",
      useSelectModel: "請先選擇模型",
      useWaiting: "等待選擇模型",
      useLocalNas: "本地 NAS GPU 模型",
      useWithKey: "API Key 模式",
      useWithFreeQuota: "免費真實模型模式",
      useNeedsKey: "需要 API Key",
      promptRequired: "請先輸入內容",
      noAccess: "此模型需要 API Key，請先設定後再送出",
      responseTitle: "模型回覆",
      responseFailed: "模型呼叫失敗",
      cacheBypassed: "已繞過快取",
      usageInput: "輸入 tokens",
      usageOutput: "輸出 tokens",
      usageTotal: "總 tokens",
      remainingTokens: "剩餘 tokens",
      remainingRequests: "剩餘請求",
      remainingBalance: "剩餘餘額",
      unknown: "未知",
      historyEyebrow: "呼叫記錄",
      historyTitle: "模型呼叫資料庫",
      historySearchLabel: "搜尋",
      historySearchPlaceholder: "搜尋模型、提示詞或回覆",
      historyEmpty: "尚無模型呼叫記錄",
      historyCaller: "呼叫者",
      historyInput: "輸入",
      historyOutput: "輸出",
      statusCompleted: "完成",
      statusFailed: "失敗",
      statusBlocked: "已阻擋",
      freeTierDescriptions: {
        "Local NAS": "提示詞與回覆只在 NAS 主機及其本機 GPU 上處理，不需要 API Key，也不會傳送到外部模型服務。",
        "Free Gateway": "公開 no-key 文字生成端點，適合 demo 快速驗證。提示詞會送到公開服務，不要輸入機密內容。",
        Google: "Gemini API 對符合資格的模型提供有限免費輸入與輸出 token。",
        "Alibaba Cloud": "阿里雲百鍊新使用者可能取得各模型獨立免費額度，通常有效期 90 天，且受地域與服務範圍限制。",
        "Mistral AI": "Mistral free mode 適合評估和原型測試，API 速率限制較低。",
        Cohere: "Cohere trial key 可免費試用，但有月度呼叫次數與速率限制。",
        default: "此供應商在目前 demo 中未列出通用模型級免費額度。",
      },
    },
    keyModal: {
      eyebrow: "API Key",
      title: "輸入模型 API Key",
      close: "關閉",
      keyLabel: "API Key",
      keyPlaceholder: "貼上供應商 API Key",
      securityHint: "Demo 只把 API Key 保存在目前瀏覽器工作階段，不會寫入後端資料庫。",
      cancel: "取消",
      save: "套用到本次工作階段",
      selectedModel: "目前選擇：{provider} · {model}",
      missingKey: "請先輸入 API Key",
      saved: "API Key 已套用",
    },
    status: {
      downloading: "下載中",
      processing: "處理中",
      pending: "等待中",
      completed: "已完成",
      failed: "失敗",
      needs_model: "需要模型",
    },
    toast: {
      meetingDetected: "會議動態",
      meetingCompleted: "會議動態",
      meetingFailed: "處理失敗",
      nasReceived: "NAS 收件",
      nasProcessed: "NAS 處理",
      savedFailed: "保存失敗",
      detected: "發現新的會議錄音《{title}》，已經開始處理",
      uploaded: "錄音《{title}》已保存，正在處理",
      completed: "會議《{title}》轉寫完成",
      failed: "會議《{title}》處理失敗",
      assetUploaded: "NAS 已收到《{title}》，已加入處理佇列",
      assetProcessed: "NAS 資產《{title}》處理狀態已更新",
    },
    errors: {
      requestFailed: "請求失敗",
      invalidLogin: "帳號或密碼錯誤",
    },
  },
  en: {
    documentTitle: "AI Work Meeting Portal",
    language: { label: "Language switcher" },
    loading: { active: "Loading data..." },
    login: {
      eyebrow: "NAS Secure Workspace",
      title: "AI Work NAS Meeting Portal",
      copy: "Sign in to record from the browser, receive new audio alerts from the NAS shared folder, and search indexed meeting transcripts.",
      username: "Username",
      password: "Password",
      submit: "Sign In",
    },
    sidebar: {
      subtitle: "NAS meeting intelligence",
      navLabel: "Main navigation",
    },
    nav: {
      dashboard: "Overview",
      record: "Meeting Recording",
      upload: "NAS Upload",
      network: "Online Sources",
      models: "Model Management",
      meetings: "Knowledge Search",
      aiwork: "AI Work",
      settings: "Settings & Management",
      mcp: "MCP Management",
      n8n: "n8n Automation",
      lineAdmin: "LINE Enterprise",
      accounts: "Account Management",
    },
    nas: {
      title: "NAS Discovery Service",
      subtitle: "Watching mock_nas/inbox",
    },
    topbar: {
      eyebrow: "Meeting Intelligence",
    },
    auth: {
      logout: "Sign Out",
    },
    network: {
      eyebrow: "NAS Online Intake",
      title: "Download YouTube Content",
      copy: "Paste a single YouTube video URL. The NAS downloads and archives the source in the background, then routes it through the existing transcription or video analysis pipeline.",
      urlLabel: "YouTube URL",
      urlPlaceholder: "https://www.youtube.com/watch?v=...",
      titleLabel: "NAS display name (optional)",
      titlePlaceholder: "Leave blank to use the YouTube video title",
      mediaLabel: "Storage format and processing",
      videoOption: "Video · save as MP4 and run YOLO analysis",
      audioOption: "Audio · convert to M4A and run Whisper transcription",
      rightsConfirm: "I confirm that I have permission to download, store, and process this content",
      submit: "Download to NAS",
      submitting: "Creating download task...",
      pipelineLabel: "Online source processing flow",
      stepDownload: "NAS background download",
      stepArchive: "Source archive",
      stepAnalyze: "Whisper / YOLO analysis",
      stepRag: "RAG indexing",
      policy: "Only public, non-live, single YouTube videos are supported. Follow copyright law, YouTube terms, and company data policy.",
      jobsEyebrow: "Download and processing records",
      jobsTitle: "Online Source Queue",
      refresh: "Refresh",
      empty: "No online source downloads yet",
      openAsset: "Open NAS Asset",
      source: "YouTube source",
      queued: "YouTube download task created",
      failed: "Unable to create download task",
    },
    accounts: {
      eyebrow: "NAS Access Control",
      title: "Accounts and Permissions",
      copy: "Manage Portal sign-in, NAS asset scope, and administrator access. Disabling an account or changing its role or password revokes existing sessions.",
      metricsLabel: "Account summary",
      total: "Total Accounts",
      active: "Active",
      admins: "Administrators",
      createEyebrow: "New Access Identity",
      createTitle: "Create Account",
      username: "Username",
      usernamePlaceholder: "user.name",
      password: "Initial Password",
      passwordPlaceholder: "At least 8 characters",
      role: "Role",
      create: "Create Account",
      directoryEyebrow: "User Directory",
      directoryTitle: "Portal Accounts",
      search: "Search",
      searchPlaceholder: "Search account or role",
      account: "Account",
      status: "Status",
      activity: "Activity",
      actions: "Actions",
      roles: { admin: "Administrator", user: "Standard User" },
      statuses: { active: "Active", inactive: "Disabled" },
      created: "Created",
      lastLogin: "Last sign-in",
      never: "Never signed in",
      records: "{assets} NAS assets · {meetings} meetings · {calls} model calls",
      save: "Save Access",
      reset: "Reset Password",
      delete: "Delete",
      empty: "No accounts match this search",
      current: "Signed in",
      protected: "This account owns NAS data; disable it instead",
      resetEyebrow: "Account Security",
      resetTitle: "Reset Password",
      newPassword: "New Password",
      resetHint: "Resetting the password immediately revokes this account's current sessions.",
      confirmReset: "Reset Password",
      resetFor: "Set a new password for {username}",
      confirmDelete: "Delete account {username}? This action cannot be undone.",
      createdSuccess: "Account created",
      updatedSuccess: "Account access updated",
      resetSuccess: "Password reset",
      deletedSuccess: "Account deleted",
      operationFailed: "Account operation failed",
      duplicate: "Username already exists",
      invalidUsername: "Username must be 3–32 characters using letters, numbers, dot, underscore, or hyphen",
      invalidPassword: "Password must be 8–128 characters",
      selfProtection: "You cannot deactivate yourself or remove your administrator access",
      ownsRecords: "This account owns NAS data and must be disabled instead",
    },
    lineAdmin: {
      eyebrow: "LINE Company Governance",
      title: "LINE Enterprise Management",
      copy: "Only administrator-approved groups can use company NAS data, RAG, and models. Direct chats never receive company data or company API keys.",
      metricsLabel: "LINE management summary",
      totalGroups: "Discovered Groups",
      approvedGroups: "Approved",
      monthlyCalls: "Calls This Month",
      monthlyTokens: "Tokens This Month",
      directoryEyebrow: "Company Group Directory",
      directoryTitle: "Model and Data Access Policies",
      refresh: "Sync Again",
      serviceReady: "LINE service is connected. Newly discovered groups are added as pending approval.",
      serviceUnavailable: "LINE service cannot be synchronized right now. Saved NAS group policies are shown below.",
      empty: "No LINE groups have been discovered",
      pending: "Pending Approval",
      approved: "Approved",
      groupId: "Group ID",
      owner: "Managed By",
      documents: "NAS Documents",
      usage: "Monthly Usage",
      approve: "Allow Company AI",
      pdfSummary: "Automatically summarize uploaded PDFs",
      ragQueries: "Allow @Claire to query group data",
      model: "Current System Model",
      localModel: "NAS Local",
      companyApi: "Company API",
      callLimit: "Monthly Call Limit",
      tokenLimit: "Monthly Token Limit",
      unlimitedHint: "Enter 0 for unlimited usage",
      save: "Save Group Policy",
      saved: "LINE group policy updated",
      saveFailed: "Unable to update the LINE group policy",
      personalBlocked: "Direct chats are always blocked from company NAS, RAG, and company API keys.",
    },
    n8n: {
      eyebrow: "NAS Workflow Automation",
      title: "n8n Automation",
      copy: "Connect NAS file events, model results, and business services into traceable workflows. n8n runs independently and is available only to AI Work administrators.",
      serviceLabel: "Service status",
      checking: "Checking",
      connected: "Running",
      unavailable: "Unavailable",
      consoleEyebrow: "AUTOMATION CONSOLE",
      consoleTitle: "Open the workflow editor",
      consoleCopy: "Create the n8n Owner account on first access, then build, test, and inspect every execution in the visual editor.",
      refresh: "Check Again",
      open: "Open n8n",
      versionLabel: "Deployed Version",
      endpointLabel: "Company Entry Point",
      accessLabel: "Access Policy",
      adminOnly: "Administrators Only",
      latencyLabel: "Response Time",
      trialEyebrow: "Imported Example",
      manualTest: "Automatic Trigger",
      flowLabel: "n8n NAS automated processing workflow",
      step1Title: "Upload to NAS",
      step1Copy: "Upload audio or a PDF without manually starting n8n.",
      step2Title: "Complete Model Processing",
      step2Copy: "Run ASR for audio, or extraction, OCR, and RAG indexing for PDFs.",
      step3Title: "Create an Execution",
      step3Copy: "The NAS emits an event and n8n stores the input and callback result.",
      step4Title: "Push to Company LINE",
      step4Copy: "Send the summary or transcript preview to an approved company group.",
      readyNotice: "The service is ready. Upload audio or a PDF, then inspect the complete run in n8n Executions.",
      unavailableNotice: "The n8n service is unavailable. Check again or inspect the server status.",
    },
    odoo: {
      eyebrow: "Enterprise Workflow Connector",
      title: "Odoo MCP",
      copy: "Allow an LLM to call Odoo MCP tools under access control to query enterprise workflows and operational data. This is currently a placeholder and no live connection has been configured.",
      statusLabel: "Odoo MCP status",
      notConnected: "Not connected",
      placeholderStatus: "MCP server, authentication, and tool catalog are pending",
      flowEyebrow: "Planned call flow",
      flowTitle: "How the LLM accesses Odoo",
      stage: "Planned",
      steps: {
        requestTitle: "LLM receives a business question",
        requestCopy: "The user asks about finance, sales, inventory, or operations in natural language.",
        policyTitle: "Identity and access check",
        policyCopy: "The NAS applies user, department, and tool allowlist policies to determine the permitted Odoo data scope.",
        mcpTitle: "Call an Odoo MCP tool",
        mcpCopy: "After approval, the MCP server converts the model request into a controlled Odoo API operation.",
        auditTitle: "Response and NAS audit",
        auditCopy: "The LLM prepares the response while the NAS records the caller, tool, input, output, and timestamp.",
      },
      promptLabel: "LLM instruction",
      promptPlaceholder: "Example: summarize this month's sales and overdue customers",
      runDisabled: "Enable after MCP setup",
      notice: "This page does not currently send data to Odoo, an MCP server, or any model.",
    },
    mcp: {
      eyebrow: "NAS Tool Connectors",
      title: "MCP Management",
      copy: "Manage MCP servers, connection health, tool catalogs, and company LLM access. Credentials are referenced only through NAS environment variables.",
      metricsLabel: "MCP summary",
      total: "Connectors",
      connected: "Connected",
      enabled: "Enabled",
      tools: "Tools",
      directoryEyebrow: "Company MCP Registry",
      directoryTitle: "Servers and Tool Catalogs",
      refresh: "Refresh",
      add: "Add MCP",
      search: "Search",
      searchPlaceholder: "Search names, endpoints, or services",
      securityNote: "Official endpoints are pre-approved. OAuth services still require enterprise authorization or an access token. SSE and stdio remain configuration-only in phase one.",
      empty: "No MCP servers are registered",
      categories: {
        nas: { title: "NAS and Knowledge", copy: "Access NAS files, company documents, and internal knowledge bases." },
        office: { title: "Office and Communication", copy: "Email, Google Workspace, calendars, and team messaging." },
        spreadsheet: { title: "Spreadsheets and Excel", copy: "Analyze NAS Excel, CSV, TSV, Google Sheets, and Microsoft 365 workbooks." },
        finance: { title: "Accounting and ERP", copy: "Accounting, payments, invoices, financial reports, and enterprise resource planning." },
        project: { title: "Project Management and Collaboration", copy: "Projects, tasks, issues, milestones, and cross-team collaboration." },
        technical: { title: "Development, Cloud, and Databases", copy: "Code, deployments, cloud infrastructure, and database tools." },
        other: { title: "Other Connectors", copy: "Company-added or uncategorized MCP servers." },
      },
      connectorCount: "{count} connectors",
      status: { connected: "Connected", failed: "Connection Failed", unchecked: "Not Tested", unconfigured: "Not Configured" },
      transport: "Transport",
      endpoint: "Endpoint / Configuration Reference",
      endpointPlaceholder: "http://127.0.0.1:9000/mcp",
      auth: "Authentication",
      requestHeaders: "Fixed Headers",
      authType: "Authentication Type",
      authTypes: { none: "None", bearer: "Bearer Token", oauth2: "OAuth 2.0", managed: "Provider-managed flow", custom: "Custom" },
      authReady: "Environment variable configured",
      authMissing: "Environment variable missing",
      authNone: "No authentication",
      protocol: "Protocol",
      lastChecked: "Last Sync",
      neverChecked: "Never synchronized",
      enabledForLlm: "Available to the company LLM",
      disabledForLlm: "Not available to the company LLM",
      edit: "Edit",
      sync: "Test and Sync Tools",
      syncing: "Connecting...",
      syncSuccess: "MCP tool catalog synchronized",
      syncFailed: "MCP connection or synchronization failed",
      copyEndpoint: "Copy Endpoint",
      endpointCopied: "Endpoint copied",
      officialSource: "Official Documentation",
      noTools: "No synchronized tools",
      toolInput: "Input Schema",
      modalEyebrow: "MCP Registry",
      modalAddTitle: "Add MCP Server",
      modalEditTitle: "Edit MCP Server",
      name: "Display Name",
      namePlaceholder: "Example: Odoo Production",
      slug: "Identifier",
      authEnv: "Authentication Environment Variable",
      sourceUrl: "Official Documentation Source",
      enableServer: "Allow the company LLM to use this server",
      descriptionZh: "Traditional Chinese Description",
      descriptionEn: "English Description",
      authHint: "Only the environment variable name is stored. Tokens and passwords must be supplied through the server .env and are never written to the database.",
      save: "Save MCP",
      saved: "MCP settings saved",
      duplicate: "MCP identifier already exists",
    },
    dashboard: {
      eyebrow: "NAS Demo Scope",
      title: "NAS discovery, audio archive, transcript search",
      copy: "The first version focuses on the NAS meeting asset intake flow: browser recording or shared-folder file arrival, NAS inbox alerts, backend move and processing status, and searchable meeting history.",
    },
    dashboardAssets: {
      eyebrow: "NAS Asset Library",
      title: "All Uploaded Files",
      copy: "Audio, video, documents, and images are ordered from newest to oldest. Open a file to review results or reprocess it.",
      filterLabel: "Asset type",
      all: "All",
      audio: "Audio",
      video: "Video",
      documents: "Documents",
      images: "Images",
      upload: "Upload New File",
      newest: "Newest upload",
      uploader: "Uploaded by",
      uploadedAt: "Uploaded at",
      open: "View Details",
      transcript: "Transcript Preview",
      transcriptDetail: "Transcript Details",
      transcriptProcessing: "The transcript is being processed in the background.",
      transcriptUnavailable: "No transcript is available for this audio yet.",
      empty: "No NAS assets in this category",
    },
    nasFeatures: {
      eyebrow: "NAS Demo",
      title: "Enterprise NAS meeting intake",
      copy: "The shared folder acts as the audio asset entry point: files landing in inbox are discovered, notified, moved, indexed, transcribed, and then searchable with login permissions.",
      dropzoneTitle: "Shared Folder Drop Zone",
      dropzoneCopy: "mock_nas/inbox acts as an SMB / NFS shared-folder entry point where recorders, room PCs, or sync tools can place meeting audio.",
      watchTitle: "Hot Folder Watcher",
      watchCopy: "The backend polls the NAS inbox and shows a frontend popup as soon as a new file enters the processing queue.",
      archiveTitle: "Source Audio Archive",
      archiveCopy: "The original voice file is preserved in storage/recordings, while the NAS source file moves to processed for traceable handling.",
      indexTitle: "Indexed Access Control",
      indexCopy: "Transcript, source, status, and timestamps are written to the database and exposed only after authenticated access.",
    },
    metrics: {
      total: "Meeting Records",
      processing: "Processing",
      completed: "Completed",
    },
    modules: {
      record: {
        title: "Meeting Recording",
        copy: "Browser recordings are archived like NAS intake files, preserving the source voice and starting the same transcription pipeline.",
      },
      upload: {
        title: "NAS Upload",
        copy: "Upload audio, video, documents, and spreadsheets into ASR, video analysis, RAG, or SQL query workflows.",
      },
      meetings: {
        title: "Knowledge Search",
        copy: "Search NAS and browser-recorded meetings by title, source filename, origin, and transcript text.",
      },
      aiwork: {
        copy: "Use the NAS meeting database for summaries, action items, Q&A, and model-call audit trails.",
      },
    },
    record: {
      eyebrow: "NAS-Synced Recorder",
      title: "New Meeting Recording Archive",
      meetingTitle: "Meeting Title",
      titlePlaceholder: "Example: Product Weekly 09/09",
      asrTitle: "Step 1: Choose a Transcription Model",
      asrCopy: "After recording stops, the NAS uses this model to build a transcript, vectors, and a RAG index.",
      asrModeLabel: "Execution Location",
      asrModeLocal: "Local NAS",
      asrModeCloud: "Cloud API",
      asrModelLabel: "Speech Model",
      systemAsrTitle: "System Speech Model",
      systemAsrCopy: "This recording uses the speech model selected under Settings & Management.",
      asrKeyPlaceholder: "Used only for this meeting recording",
      asrLanguages: "Languages",
      asrBestFor: "Best for",
      asrReady: "The local model is ready and can process recordings.",
      asrDownloading: "Model download in progress: {progress}%. The recording can be saved, but transcription waits for completion.",
      asrNotReady: "The local model is not ready. Complete setup in NAS Model Management or choose a ready model.",
      asrCloud: "This model runs in the cloud and requires a company API key configured by an administrator.",
      asrKeyRequired: "{model} requires an API key. Enter it before recording.",
      asrModelRequired: "Choose a speech model first.",
      translationTitle: "Step 2: Transcript Translation",
      translationCopy: "Choose a target language. The current system LLM performs the translation, and both versions are stored separately.",
      translationEnable: "Enable translation",
      translationTarget: "Target language",
      translationMode: "Translation location",
      translationModel: "Translation model",
      translationSystemModel: "System Translation Model",
      translationKey: "Translation model API key",
      translationKeyPlaceholder: "Used only for this translation",
      translationModelRequired: "Choose a translation model first.",
      translationKeyRequired: "{model} requires an API key. Enter it before starting.",
      translationLocalHint: "The transcript is processed by the local NAS model and is not sent to an external service.",
      translationCloudHint: "The transcript is sent to {provider}. The API key is used only for this job and is not stored.",
      lineTitle: "Step 3: Push to a LINE Group",
      lineCopy: "After transcription, the local NAS Qwen model creates a summary, decisions, and action items for the selected group.",
      lineEnable: "Enable push",
      lineGroup: "LINE group",
      lineMessages: "{count} records",
      lineFullTranscript: "Also push the full source transcript in sections",
      lineSummaryOnly: "By default, only the summary and NAS entry are pushed. The group can query the meeting with @Claire.",
      lineFullWarning: "A full transcript is split across multiple LINE messages. Keep long meetings on the NAS for easier review.",
      lineUnavailable: "LINE groups are unavailable. Check the LINE webhook service.",
      lineNoGroups: "No LINE group with Claire and recorded activity was found.",
      lineGroupRequired: "Choose the LINE group that should receive the meeting summary.",
      linePushStatus: "LINE push",
      lineSummaryTitle: "LINE meeting summary",
      lineWaiting: "Waiting for transcription and summary generation.",
      lineError: "Push failed: {error}",
      lineSummaryMode: "Summary, decisions, and action items",
      lineFullMode: "Summary and full transcript",
      languages: {
        zhHant: "Traditional Chinese",
        en: "English",
        zhHans: "Simplified Chinese",
        ja: "Japanese",
        ko: "Korean",
        es: "Spanish",
        fr: "French",
        de: "German",
      },
      optionsTitle: "Recording Processing Settings",
      optionsCopy: "Review the system speech model and configure translation or LINE delivery.",
      start: "Start Recording",
      pause: "Pause",
      resume: "Resume",
      stop: "Stop and Save",
      hint: "The browser will request microphone access. After stopping, the system saves the source audio into local storage as a NAS-style archive and queues it for transcription.",
      defaultTitle: "Browser Recording",
      uploadFailed: "Recording upload failed. Please try again.",
      saved: "Recording saved and processing started.",
      unavailable: "Recording unavailable",
      secureRequired: "Microphone recording requires a secure HTTPS connection. Open this system over HTTPS or localhost.",
      mediaUnavailable: "This browser does not support microphone access. Use the latest Chrome, Edge, or Safari.",
      secureHint: "This page is using public HTTP, so the browser has disabled microphone access. Use HTTPS or a localhost address through an SSH tunnel.",
      states: {
        idle: "Ready",
        recording: "Recording",
        paused: "Paused",
        saving: "Saving",
      },
    },
    activity: {
      eyebrow: "Live Activity",
      title: "Live Processing Activity",
      fallbackTitle: "Meeting Processing",
    },
    upload: {
      eyebrow: "NAS Intake",
      title: "Upload NAS Assets",
      copy: "Supports audio, video, images, PDF, DOCX, Excel, CSV, and TSV. Spreadsheet data can be queried through the NAS Excel SQL MCP.",
      fileLabel: "File",
      titleLabel: "Asset Name",
      titlePlaceholder: "Example: board audio, product PDF",
      asrTitle: "Step 1: Audio Transcription Model",
      asrCopy: "For audio uploads, choose local or cloud ASR. Other file types ignore this setting.",
      asrModeLabel: "Execution Location",
      asrModeLocal: "Local NAS",
      asrModeCloud: "Cloud API",
      asrModelLabel: "ASR Model",
      systemAsrTitle: "Audio Transcription Model",
      systemAsrCopy: "Audio uses the system speech model selected under Settings & Management.",
      asrKeyLabel: "API Key",
      asrKeyPlaceholder: "Only used for this audio upload",
      asrHint: "Local models fit private NAS deployments. Cloud models need an API key, used only for this upload and not written to the database.",
      translationTitle: "Step 2: Transcript Translation",
      translationCopy: "Applies to audio only. Choose the target language; translation uses the current system LLM.",
      videoTitle: "Video Analysis Model",
      videoCopy: "For video uploads, choose a local or cloud model. Other file types ignore this setting.",
      videoModeLabel: "Execution Location",
      videoModeLocal: "Local NAS",
      videoModeCloud: "Cloud API",
      videoModelLabel: "Video Model",
      videoKeyLabel: "Video API Key",
      videoKeyPlaceholder: "Only used for this video upload",
      videoHint: "Local YOLO extracts frames and detects objects on the NAS host. Cloud models need an API key, used only for this upload and not written to the database.",
      modelManagerTitle: "NAS Model Management",
      modelManagerCopy: "Manage local ASR and video models that run on the NAS host. Downloads start only after pressing a button.",
      refreshModels: "Refresh",
      runtimeReady: "Runtime ready",
      runtimeMissing: "Runtime missing",
      modelPath: "Model path",
      modelSize: "Model size",
      modelProgress: "Progress",
      modelSetupHint: "Setup",
      downloadModel: "Download",
      cancelDownload: "Cancel",
      retryDownload: "Retry",
      installedModel: "Installed",
      noPanelDownload: "Install from setup",
      modelActionFailed: "Model action failed",
      modelStatus: {
        installed: "Installed",
        registered: "Registered",
        testing: "Testing",
        ready: "Ready",
        runtime_missing: "Runtime missing",
        partial: "Partial",
        missing: "Missing",
        downloading: "Downloading",
        cancelling: "Cancelling",
        cancelled: "Cancelled",
        failed: "Failed",
      },
      setupHints: {
        whisper_cpp_setup: "Requires whisper-cli and a complete ggml model file",
        python_asr_setup: "Run pip install -r requirements-asr.txt",
        python_video_setup: "Run pip install -r requirements-video.txt, then download complete YOLO weights",
        openai_endpoint_setup: "Requires a NAS loopback service that responds to /v1/chat/completions",
      },
      submit: "Upload to NAS",
      uploading: "Uploading {progress}%",
      largeFileHint: "After upload, large audio/video files are segmented by the NAS and processed by the background worker.",
      connectionFailed: "The upload connection was interrupted. Check the network and try again.",
      reprocess: "Reprocess",
      reprocessing: "Adding to queue...",
      reprocessConfirm: "Reprocess the source file with the current system models? Existing results remain available until the new result completes.",
      reprocessQueued: "The source file was added to the NAS media worker queue again.",
      openccTraditional: "OpenCC to Traditional",
      openccRunning: "Converting...",
      openccConfirm: "Convert the current transcript, translation, and RAG chunks to Traditional Chinese and rebuild vector indexes?",
      actionFailed: "Asset action failed",
      nasVolumeLabel: "NAS Volume",
      shareProtocolLabel: "Share Protocols",
      snapshotLabel: "Snapshot Policy",
      snapshotValue: "Daily 02:00, 30 versions",
      aclLabel: "Access Source",
      aclValue: "Signed-in user + NAS ACL",
      assetsEyebrow: "NAS Assets",
      assetsTitle: "Intake and Processing Status",
      searchLabel: "Search",
      searchPlaceholder: "Search filenames, types, or analysis results",
      emptyList: "No NAS assets yet",
      emptyDetail: "Select a NAS asset to review processing results",
      uploadRequired: "Choose a file first",
      uploadFailed: "NAS upload failed",
      dialogEyebrow: "NAS Received",
      dialogTitle: "NAS Upload Received",
      dialogAction: "View Processing Status",
      dialogMessage: "NAS received \"{title}\" and routed it to {analyzer}.",
      owner: "Uploader",
      filename: "Source filename",
      selectedAsr: "Selected ASR",
      selectedTranslation: "Selected translation",
      selectedVideo: "Selected Video",
      sourceAudioTitle: "Source Audio",
      sourceAudioCopy: "Play the complete source file stored on the NAS.",
      sourceVideoTitle: "Source Video",
      sourceVideoCopy: "Play the YouTube download or uploaded source video stored on the NAS.",
      downloadSource: "Download source",
      downloadSegment: "Download segment",
      wholeFile: "Complete file",
      audioSegmentsTitle: "Audio Segments",
      audioSegmentsCopy: "Play and download large audio by segment. Unsplit audio is shown as one complete-file segment.",
      transcribeSegment: "Transcribe segment",
      retranscribeSegment: "Transcribe again",
      segmentTranscriptionQueued: "Waiting for Whisper worker",
      segmentTranscriptionProcessing: "Whisper transcription in progress",
      segmentTranscriptionCompleted: "Segment transcript saved",
      segmentTranscriptionFailed: "Segment transcription failed",
      segmentTranscript: "Segment transcript",
      segmentTranscriptionQueuedToast: "This segment was added to the Whisper queue",
      videoSegmentsTitle: "Video Segments",
      videoSegmentsCopy: "Download large video by segment. Unsplit video is shown as one complete-file segment.",
      audioSegment: "Segment {number}",
      audioSegmentRange: "{start} to {end}",
      noAudioSegments: "No playable segments yet. Short audio can use the source player; segments appear here after large audio is reprocessed.",
      transcriptTitle: "Full Transcript",
      downloadTranscript: "Download full transcript",
      downloadSegmentTranscript: "Download segment transcript",
      transcriptMeta: "{chunks} transcript chunks · {characters} characters",
      transcriptEmpty: "This audio does not have a transcript yet.",
      category: "Type",
      analyzer: "Analyzer",
      fileSize: "Size",
      chunkCount: "RAG chunks",
      summary: "Processing result",
      processTitle: "NAS Processing Flow",
      processCopy: "The flow below shows the NAS services, parsers, and model calls used for this asset.",
      stepDone: "Done",
      stepActive: "Running",
      stepPending: "Pending",
      stepBlocked: "Needs setup",
      stepSkipped: "Skipped",
      stepConfigured: "Selected",
      chunks: "RAG chunks",
      page: "Page",
      type: "Type",
      pagePreview: "Page preview",
      answerSources: "Sources",
      retrievalHybrid: "Hybrid retrieval",
      retrievalKeyword: "Keyword retrieval",
      retrievalScore: "Combined",
      semanticScore: "Semantic",
      keywordScore: "Keyword",
      cacheHit: "NAS answer cache hit",
      cacheExact: "Exact question",
      cacheSemantic: "Semantic match",
      questionTitle: "Use LLM on this asset",
      questionEyebrow: "RAG Document Q&A",
      questionCopy: "This image, document, or transcript has RAG chunks. Questions use the system LLM selected by an administrator.",
      modelRequired: "A model is required",
      questionRequired: "Enter a question first",
      ask: "Process Document",
      questionPlaceholder: "Example: summarize key points and action items",
      answerTitle: "Document Result",
      analysisHistoryTitle: "NAS AI Analysis Knowledge",
      analysisHistoryCopy: "These cloud analysis results are stored on the NAS and indexed as RAG chunks for later queries.",
      analysisQuestion: "Analysis Question",
      analysisSaved: "Analysis automatically saved to the NAS and added to RAG",
      analysisAlreadySaved: "Matching NAS analysis knowledge was reused without duplicate indexing",
      analysisEmbeddingQueued: "Analysis saved; embedding is queued for NAS background processing",
      modelNeedsKey: "This model needs an API key. Set a model key first.",
      noRag: "This file has no RAG chunks yet. Image, audio, video, PDF, and DOCX assets can be queried after processing completes.",
      timeline: {
        intakeTitle: "NAS Intake and Access Check",
        intakeEngine: "FastAPI Upload + SQLite Audit",
        intakeCopy: "The file is written to storage/nas_assets with uploader, source filename, size, MIME type, and status.",
        archiveTitle: "NAS Archive and Index",
        archiveEngine: "NAS Asset Indexer",
        archiveCopy: "Creates the asset ID, keeps the source path, and makes it searchable according to login permissions.",
        audioNormalizeTitle: "Audio Normalize",
        audioNormalizeEngine: "FFmpeg Audio Normalize",
        audioNormalizeCopy: "Production deployment converts audio to 16kHz mono WAV before ASR. This demo preserves the source audio and shows the normalization stage in the flow.",
        vadTitle: "Long Audio Segmentation",
        vadEngine: "FSMN-VAD / Silero VAD",
        vadCopy: "Production deployment detects speech ranges and splits long meetings before ASR to reduce timeouts and missed text.",
        pdfRenderTitle: "PDF Page Rendering",
        pdfRenderEngine: "PyMuPDF",
        pdfRenderCopy: "Renders each PDF page to PNG for OCR input and RAG source page previews.",
        pdfTextTitle: "PDF Text Layer Extraction",
        pdfTextEngine: "pypdf",
        pdfTextCopy: "If selectable text exists, it is extracted directly and split into page-level RAG chunks.",
        ocrTitle: "Image PDF OCR",
        ocrEngine: "PaddleOCR PP-OCRv6",
        ocrCopy: "When pypdf finds no text layer, each page image is OCR processed into image_ocr chunks.",
        ragTitle: "RAG Index Build",
        ragEngine: "Qwen3-Embedding-0.6B + SQLite document_chunks",
        ragCopy: "Stores chunk content, page, type, preview path, and a 1024-dimensional vector. The NAS background worker fills any missing vectors.",
        docxTitle: "DOCX Parsing",
        docxEngine: "python-docx",
        docxCopy: "Extracts paragraph and table text, then stores it as searchable RAG chunks.",
        imageDecodeTitle: "Image Format and Integrity Check",
        imageDecodeEngine: "NAS Image Intake",
        imageDecodeCopy: "Recognizes JPG, PNG, WebP, TIFF, BMP, and image MIME types, preserves the source image, and verifies OCR input.",
        imageOcrTitle: "Image Text Recognition",
        imageOcrEngine: "PaddleOCR PP-OCRv6",
        imageOcrCopy: "Recognizes Chinese and English text locally on the NAS, writes image_ocr chunks, and preserves the image as the RAG source preview.",
        audioTitle: "Speech-to-Text",
        audioEngine: "Selected ASR Model",
        audioCopy: "Calls the selected local whisper.cpp, faster-whisper, SenseVoiceSmall, or Paraformer model, or a cloud speech service.",
        translationTitle: "Transcript Translation",
        translationEngine: "Selected Translation LLM",
        translationCopy: "Uses the current system LLM for the selected language and stores source and translated text separately.",
        audioRagTitle: "Transcript RAG Index",
        audioRagEngine: "Transcript Chunker + Qwen3 Embedding",
        audioRagCopy: "Splits ASR output into audio_transcript chunks and builds vectors for later LLM queries.",
        videoTitle: "Video Content Analysis",
        videoEngine: "Selected Video Model",
        videoCopy: "Calls the selected local YOLO frame detection path, or waits for cloud video analysis API setup.",
        videoRagTitle: "Video Result RAG Index",
        videoRagEngine: "Detection Chunker + Qwen3 Embedding",
        videoRagCopy: "Stores timestamps, detected objects, confidence scores, and frame previews, then builds searchable vectors.",
        llmTitle: "Document Q&A",
        llmEngine: "75% vector similarity + 25% keywords",
        llmCopy: "Ranks chunks with a Qwen3 query vector and multilingual keywords, then sends matched pages to the system LLM.",
      },
    },
    models: {
      globalSetting: "Global Model Settings",
      systemLlmTitle: "System LLM Settings and Pricing",
      systemLlmHeading: "Default System LLM",
      systemLlmCopy: "Once selected by an administrator, AI Work, RAG, translation, LINE, and MCP use the same model.",
      systemAsrTitle: "System Speech Model Settings",
      systemAsrHeading: "Default Speech-to-Text Model",
      systemAsrCopy: "Meeting recordings, NAS uploads, network audio, hot folders, and segment retranscription all use this model.",
      currentAsrLabel: "Current System Speech Model",
      setSystemAsr: "Set as System Speech Model",
      settingSystemAsr: "Applying...",
      systemAsrSaved: "System speech model updated",
      addModel: "Add Model",
      eyebrow: "NAS Model Registry",
      title: "Add Local Model",
      copy: "The model is stored in the NAS registry first and appears in work selectors only after file, runtime, or API validation.",
      type: "Model Type",
      typeWhisper: "whisper.cpp speech model",
      typeYolo: "YOLO video model",
      typeLlm: "OpenAI-compatible local LLM",
      name: "Display Name",
      namePlaceholder: "Example: Whisper medium",
      slug: "Model Identifier (optional)",
      slugPlaceholder: "Example: whisper-medium",
      recommendation: "Usage Note (optional)",
      recommendationPlaceholder: "Example: long Chinese meetings",
      fileName: "NAS Model Filename",
      filePlaceholder: "ggml-medium.bin",
      downloadUrl: "Trusted Download URL (optional)",
      downloadUrlPlaceholder: "https://huggingface.co/...",
      expectedSize: "Expected Size MB (optional)",
      sha256: "SHA256 (optional)",
      apiBase: "Loopback API Base URL",
      modelAlias: "API Model Alias",
      contextTokens: "Input Limit in Tokens",
      supportsTokenize: "Endpoint supports /tokenize",
      securityHint: "Downloads are restricted to Hugging Face or GitHub HTTPS. LLM endpoints must use NAS loopback.",
      create: "Create Registry Entry",
      customBadge: "Custom",
      test: "Test",
      remove: "Remove Entry",
      saved: "Model saved in the NAS registry",
      testReady: "Model validation passed and is available in work selectors",
      testIncomplete: "The model file is complete, but its runtime is not ready",
      removed: "Registry entry removed; the NAS model file was preserved",
      removeConfirm: "Remove this model registry entry? The model file on the NAS will not be deleted.",
      actionFailed: "Custom model action failed",
    },
    meetings: {
      eyebrow: "NAS Index Search",
      title: "NAS Meeting Library",
      searchLabel: "Search",
      searchPlaceholder: "Search NAS meeting records",
      emptyList: "No meeting records yet",
      emptyDetail: "Select a NAS meeting asset to review audio and transcript",
      waitingExcerpt: "Transcript will appear after processing finishes",
      transcriptTitle: "Source Transcript",
      translationTitle: "Translation",
      translationPending: "Translation starts after transcription is complete.",
      translationFailed: "Translation failed: {error}",
      processingText: "Transcription is processing. Please wait.",
      failedText: "Processing failed",
      sourceNas: "NAS Discovery",
      sourceWeb: "Web Recording",
    },
    aiwork: {
      eyebrow: "NAS AI Work",
      copy: "Choose a mainstream LLM for NAS meeting summaries, Q&A, or audit tests. The demo shows public pricing and prompts for the provider API key when needed.",
      providerLabel: "Provider",
      modelLabel: "Model",
      executionLabel: "Execution Location",
      localModels: "Local NAS",
      cloudModels: "Cloud API",
      loading: "Loading...",
      allProviders: "All Providers",
      selectProviderFirst: "Select a provider first",
      selectModel: "Select a model",
      configureKey: "Set API Key",
      keyNotSet: "API Key not set",
      keyNotRequired: "No API key required for the local model",
      keyReady: "{provider} API Key is active for this session",
      companyKeyReady: "The company API key is securely configured on the NAS server",
      systemModelLabel: "Current System Model",
      systemModelDefault: "NAS default",
      systemModelUpdated: "Set by {user} at {time}",
      systemModelAdminHint: "Administrators can choose a model above and apply it to AI Work, document RAG, transcript translation, and LINE.",
      systemModelUserHint: "The company administrator controls this model. All LLM tasks use it.",
      setSystemModel: "Set as Current System Model",
      settingSystemModel: "Applying...",
      systemModelSaved: "The current system model has been updated",
      selectBeforeSet: "Select a model to apply first",
      saveBeforeRun: "Set the selected model as the current system model first",
      emptyPricing: "Select a model to view pricing",
      sourcesEyebrow: "Pricing Sources",
      sourcesTitle: "Pricing Data Sources",
      sourcesCopy: "Prices change over time. This demo uses a snapshot compiled from official public pricing pages. A production version can attach this sync task to the NAS admin workflow.",
      updatedAt: "Pricing snapshot date",
      modelId: "Model ID",
      context: "Context",
      input: "Input",
      cachedInput: "Cached Input",
      cacheWrite: "Cache Write",
      output: "Output",
      perUnit: "per {unit}",
      source: "Official Source",
      noCachedPrice: "Not listed",
      freeQuota: "Free Quota",
      freeQuotaAvailable: "Free model available",
      freeQuotaListed: "Free quota listed, API key required",
      freeQuotaUnavailable: "No free quota listed",
      realCallNeedsKey: "This provider's free quota still requires an API key, so requests stay disabled until a key is set.",
      tryEyebrow: "Model Test",
      setupTitle: "Model Setup and Pricing",
      collapseSetup: "Collapse",
      expandSetup: "Expand",
      promptLabel: "Prompt",
      promptPlaceholder: "Enter content to send to the selected model",
      promptSearchHint: "Enter keywords, then search",
      systemPromptLabel: "System Prompt (Optional)",
      systemPromptPlaceholder: "Example: You are an enterprise knowledge assistant. Answer with concise bullet points.",
      systemPromptHint: "Set the role, tone, and output format",
      suggestionsLabel: "Similar Previous Questions",
      suggestionCached: "NAS Cache",
      suggestionHistory: "History",
      runModel: "Send",
      forceRunModel: "Force Send",
      forceRunHint: "Bypass the cache and call the model; charges may apply",
      useMcp: "Use MCP Tools",
      useMcpHint: "Let the current LLM select a read-only tool, retrieve data, then generate the final answer",
      mcpServer: "MCP Server",
      mcpAuto: "Automatic",
      mcpReady: "{servers} servers and {tools} read-only tools available",
      mcpUnavailable: "No connected read-only MCP tools are available",
      mcpTrace: "MCP Execution Trace",
      mcpNotUsed: "The LLM determined that this request did not need a tool",
      mcpArguments: "Tool Arguments",
      mcpResult: "Tool Result",
      useTitle: "Use {model}",
      useSelectModel: "Select a model to begin",
      useWaiting: "Waiting for model",
      useLocalNas: "Local NAS GPU Model",
      useWithKey: "API Key Mode",
      useWithFreeQuota: "Free Real Model Mode",
      useNeedsKey: "API Key Required",
      promptRequired: "Enter a prompt first",
      noAccess: "This model requires an API key. Set a key before sending.",
      responseTitle: "Model Response",
      responseFailed: "Model Call Failed",
      cacheBypassed: "Cache bypassed",
      usageInput: "Input tokens",
      usageOutput: "Output tokens",
      usageTotal: "Total tokens",
      remainingTokens: "Remaining tokens",
      remainingRequests: "Remaining requests",
      remainingBalance: "Remaining balance",
      unknown: "Unknown",
      historyEyebrow: "Call History",
      historyTitle: "Model Call Database",
      historySearchLabel: "Search",
      historySearchPlaceholder: "Search model, prompt, or response",
      historyEmpty: "No model calls yet",
      historyCaller: "Caller",
      historyInput: "Input",
      historyOutput: "Output",
      statusCompleted: "Completed",
      statusFailed: "Failed",
      statusBlocked: "Blocked",
      freeTierDescriptions: {
        default: "",
      },
    },
    keyModal: {
      eyebrow: "API Key",
      title: "Enter Model API Key",
      close: "Close",
      keyLabel: "API Key",
      keyPlaceholder: "Paste provider API key",
      securityHint: "For this demo, the API key is kept only in the current browser session and is not written to the backend database.",
      cancel: "Cancel",
      save: "Apply to This Session",
      selectedModel: "Selected: {provider} · {model}",
      missingKey: "Enter an API key first",
      saved: "API Key applied",
    },
    status: {
      downloading: "Downloading",
      processing: "Processing",
      pending: "Pending",
      completed: "Completed",
      failed: "Failed",
      needs_model: "Needs Model",
    },
    toast: {
      meetingDetected: "Meeting Update",
      meetingCompleted: "Meeting Update",
      meetingFailed: "Processing Failed",
      nasReceived: "NAS Intake",
      nasProcessed: "NAS Processing",
      savedFailed: "Save Failed",
      detected: "New meeting audio \"{title}\" found. Processing has started.",
      uploaded: "Recording \"{title}\" saved. Processing has started.",
      completed: "Meeting \"{title}\" transcription completed.",
      failed: "Meeting \"{title}\" processing failed.",
      assetUploaded: "NAS received \"{title}\" and queued it for processing.",
      assetProcessed: "NAS asset \"{title}\" processing status has been updated.",
    },
    errors: {
      requestFailed: "Request failed",
      invalidLogin: "Invalid username or password",
    },
  },
};

const state = {
  user: null,
  meetings: [],
  selectedMeetingId: null,
  ws: null,
  mediaRecorder: null,
  chunks: [],
  recordStartedAt: null,
  timerId: null,
  elapsedBeforePause: 0,
  recordMode: "idle",
  lang: localStorage.getItem("ai-work-lang") || "zh-Hant",
  llmCatalog: null,
  asrCatalog: null,
  currentAsrId: "local:whisper-cpp-small",
  currentAsrModel: null,
  videoCatalog: null,
  localModels: null,
  localModelPollTimer: null,
  selectedRecordAsrMode: "local",
  selectedRecordAsrModelId: "local:whisper-cpp-small",
  recordTranslationEnabled: false,
  recordTranslationMode: "local",
  recordTranslationModelId: "local:qwen3-4b",
  recordTranslationTarget: "en",
  lineGroups: [],
  recordLinePushEnabled: false,
  recordLineGroupId: "",
  recordLineFullTranscript: false,
  selectedAsrMode: "local",
  selectedAsrModelId: "local:whisper-cpp-small",
  audioTranslationEnabled: false,
  audioTranslationMode: "local",
  audioTranslationModelId: "local:qwen3-4b",
  audioTranslationTarget: "en",
  selectedVideoMode: "local",
  selectedVideoModelId: "local:yolov8n",
  selectedLlmMode: "local",
  selectedProvider: "Local NAS",
  selectedLlmId: "local:qwen3-4b",
  currentLlmId: "local:qwen3-4b",
  currentLlmModel: null,
  selectedPricing: null,
  apiKeys: {},
  llmCalls: [],
  llmSuggestions: [],
  activeLlmSuggestion: -1,
  llmSuggestionRequestId: 0,
  nasAssets: [],
  networkAssets: [],
  networkPollTimer: null,
  assetSegmentPollTimer: null,
  dashboardAssetFilter: "all",
  selectedAssetId: null,
  selectedAsset: null,
  keyModalPricing: null,
  users: [],
  passwordResetUserId: null,
  lineAdminSources: [],
  lineAdminModels: [],
  lineServiceConnected: false,
  mcpServers: [],
  availableMcpServers: [],
  useMcp: false,
  selectedMcpServerId: "auto",
  editingMcpServerId: null,
  mcpSearchQuery: "",
  n8nStatus: null,
};

const els = {
  globalBusyIndicator: document.querySelector("#globalBusyIndicator"),
  globalBusyText: document.querySelector("#globalBusyText"),
  loginView: document.querySelector("#loginView"),
  appView: document.querySelector("#appView"),
  loginForm: document.querySelector("#loginForm"),
  loginError: document.querySelector("#loginError"),
  currentUser: document.querySelector("#currentUser"),
  logoutButton: document.querySelector("#logoutButton"),
  viewTitle: document.querySelector("#viewTitle"),
  langOptions: [...document.querySelectorAll(".lang-option")],
  navItems: [...document.querySelectorAll(".nav-item[data-view]")],
  settingsNav: document.querySelector("#settingsNav"),
  managementNavGroup: document.querySelector("#managementNavGroup"),
  sections: {
    dashboard: document.querySelector("#dashboardSection"),
    record: document.querySelector("#recordSection"),
    upload: document.querySelector("#uploadSection"),
    network: document.querySelector("#networkSection"),
    models: document.querySelector("#modelsSection"),
    meetings: document.querySelector("#meetingsSection"),
    aiwork: document.querySelector("#aiworkSection"),
    mcp: document.querySelector("#mcpSection"),
    n8n: document.querySelector("#n8nSection"),
    lineAdmin: document.querySelector("#lineAdminSection"),
    accounts: document.querySelector("#accountsSection"),
  },
  totalMeetings: document.querySelector("#totalMeetings"),
  processingMeetings: document.querySelector("#processingMeetings"),
  completedMeetings: document.querySelector("#completedMeetings"),
  meetingTitleInput: document.querySelector("#meetingTitleInput"),
  startRecord: document.querySelector("#startRecord"),
  pauseRecord: document.querySelector("#pauseRecord"),
  stopRecord: document.querySelector("#stopRecord"),
  recordTimer: document.querySelector("#recordTimer"),
  recordState: document.querySelector("#recordState"),
  recordPulse: document.querySelector("#recordPulse"),
  recordPreview: document.querySelector("#recordPreview"),
  recordHint: document.querySelector("#recordHint"),
  recordAsrModeSelect: document.querySelector("#recordAsrModeSelect"),
  recordAsrModelSelect: document.querySelector("#recordAsrModelSelect"),
  recordAsrKeyField: document.querySelector("#recordAsrKeyField"),
  recordAsrKeyLabel: document.querySelector("#recordAsrKeyLabel"),
  recordAsrApiKeyInput: document.querySelector("#recordAsrApiKeyInput"),
  recordAsrRecommendation: document.querySelector("#recordAsrRecommendation"),
  currentSystemAsrName: document.querySelector("#currentSystemAsrName"),
  currentSystemAsrMeta: document.querySelector("#currentSystemAsrMeta"),
  setCurrentAsrButton: document.querySelector("#setCurrentAsrButton"),
  recordCurrentAsrName: document.querySelector("#recordCurrentAsrName"),
  uploadCurrentAsrName: document.querySelector("#uploadCurrentAsrName"),
  recordTranslationCurrentLlmName: document.querySelector("#recordTranslationCurrentLlmName"),
  audioTranslationCurrentLlmName: document.querySelector("#audioTranslationCurrentLlmName"),
  recordTranslationToggle: document.querySelector("#recordTranslationToggle"),
  recordTranslationControls: document.querySelector("#recordTranslationControls"),
  recordTranslationTargetSelect: document.querySelector("#recordTranslationTargetSelect"),
  recordTranslationModeSelect: document.querySelector("#recordTranslationModeSelect"),
  recordTranslationModelSelect: document.querySelector("#recordTranslationModelSelect"),
  recordTranslationKeyField: document.querySelector("#recordTranslationKeyField"),
  recordTranslationApiKeyInput: document.querySelector("#recordTranslationApiKeyInput"),
  recordTranslationRecommendation: document.querySelector("#recordTranslationRecommendation"),
  recordLinePushToggle: document.querySelector("#recordLinePushToggle"),
  recordLinePushControls: document.querySelector("#recordLinePushControls"),
  recordLineGroupSelect: document.querySelector("#recordLineGroupSelect"),
  recordLineFullTranscriptToggle: document.querySelector("#recordLineFullTranscriptToggle"),
  recordLineStatus: document.querySelector("#recordLineStatus"),
  activityFeed: document.querySelector("#activityFeed"),
  meetingSearch: document.querySelector("#meetingSearch"),
  meetingList: document.querySelector("#meetingList"),
  meetingDetail: document.querySelector("#meetingDetail"),
  toastHost: document.querySelector("#toastHost"),
  llmProviderSelect: document.querySelector("#llmProviderSelect"),
  llmModelSelect: document.querySelector("#llmModelSelect"),
  llmModeButtons: [...document.querySelectorAll("[data-llm-mode]")],
  pricingPanel: document.querySelector("#pricingPanel"),
  providerSummary: document.querySelector("#providerSummary"),
  openKeyModalButton: document.querySelector("#openKeyModalButton"),
  keyStatus: document.querySelector("#keyStatus"),
  currentSystemModelName: document.querySelector("#currentSystemModelName"),
  currentSystemModelMeta: document.querySelector("#currentSystemModelMeta"),
  setCurrentLlmButton: document.querySelector("#setCurrentLlmButton"),
  apiKeyModal: document.querySelector("#apiKeyModal"),
  closeKeyModal: document.querySelector("#closeKeyModal"),
  cancelKeyButton: document.querySelector("#cancelKeyButton"),
  saveKeyButton: document.querySelector("#saveKeyButton"),
  apiKeyInput: document.querySelector("#apiKeyInput"),
  keyModalModelName: document.querySelector("#keyModalModelName"),
  modelUsePanel: document.querySelector("#modelUsePanel"),
  modelUseTitle: document.querySelector("#modelUseTitle"),
  modelUseMode: document.querySelector("#modelUseMode"),
  llmPromptInput: document.querySelector("#llmPromptInput"),
  llmSystemPromptInput: document.querySelector("#llmSystemPromptInput"),
  llmPromptSuggestions: document.querySelector("#llmPromptSuggestions"),
  runModelButton: document.querySelector("#runModelButton"),
  forceRunModelButton: document.querySelector("#forceRunModelButton"),
  useMcpToggle: document.querySelector("#useMcpToggle"),
  aiworkMcpServerSelect: document.querySelector("#aiworkMcpServerSelect"),
  aiworkMcpStatus: document.querySelector("#aiworkMcpStatus"),
  modelResponseBox: document.querySelector("#modelResponseBox"),
  llmCallSearch: document.querySelector("#llmCallSearch"),
  llmCallHistory: document.querySelector("#llmCallHistory"),
  nasUploadForm: document.querySelector("#nasUploadForm"),
  networkImportForm: document.querySelector("#networkImportForm"),
  networkUrlInput: document.querySelector("#networkUrlInput"),
  networkTitleInput: document.querySelector("#networkTitleInput"),
  networkMediaType: document.querySelector("#networkMediaType"),
  networkAuthorized: document.querySelector("#networkAuthorized"),
  networkImportSubmit: document.querySelector("#networkImportSubmit"),
  refreshNetworkAssets: document.querySelector("#refreshNetworkAssets"),
  networkAssetList: document.querySelector("#networkAssetList"),
  nasUploadSubmit: document.querySelector("#nasUploadSubmit"),
  nasUploadProgress: document.querySelector("#nasUploadProgress"),
  nasUploadProgressBar: document.querySelector("#nasUploadProgressBar"),
  nasUploadProgressText: document.querySelector("#nasUploadProgressText"),
  nasFileInput: document.querySelector("#nasFileInput"),
  nasAssetTitleInput: document.querySelector("#nasAssetTitleInput"),
  audioAsrModeSelect: document.querySelector("#audioAsrModeSelect"),
  audioAsrModelSelect: document.querySelector("#audioAsrModelSelect"),
  audioAsrKeyField: document.querySelector("#audioAsrKeyField"),
  audioAsrKeyLabel: document.querySelector("#audioAsrKeyLabel"),
  audioAsrApiKeyInput: document.querySelector("#audioAsrApiKeyInput"),
  audioAsrRecommendation: document.querySelector("#audioAsrRecommendation"),
  audioTranslationToggle: document.querySelector("#audioTranslationToggle"),
  audioTranslationControls: document.querySelector("#audioTranslationControls"),
  audioTranslationTargetSelect: document.querySelector("#audioTranslationTargetSelect"),
  audioTranslationModeSelect: document.querySelector("#audioTranslationModeSelect"),
  audioTranslationModelSelect: document.querySelector("#audioTranslationModelSelect"),
  audioTranslationKeyField: document.querySelector("#audioTranslationKeyField"),
  audioTranslationApiKeyInput: document.querySelector("#audioTranslationApiKeyInput"),
  audioTranslationRecommendation: document.querySelector("#audioTranslationRecommendation"),
  videoModelModeSelect: document.querySelector("#videoModelModeSelect"),
  videoModelSelect: document.querySelector("#videoModelSelect"),
  videoApiKeyField: document.querySelector("#videoApiKeyField"),
  videoApiKeyInput: document.querySelector("#videoApiKeyInput"),
  localModelList: document.querySelector("#localModelList"),
  refreshLocalModelsButton: document.querySelector("#refreshLocalModelsButton"),
  addCustomModelButton: document.querySelector("#addCustomModelButton"),
  customModelModal: document.querySelector("#customModelModal"),
  customModelForm: document.querySelector("#customModelForm"),
  closeCustomModelModal: document.querySelector("#closeCustomModelModal"),
  cancelCustomModel: document.querySelector("#cancelCustomModel"),
  customModelType: document.querySelector("#customModelType"),
  customModelName: document.querySelector("#customModelName"),
  customModelSlug: document.querySelector("#customModelSlug"),
  customModelRecommendation: document.querySelector("#customModelRecommendation"),
  customFileModelFields: document.querySelector("#customFileModelFields"),
  customEndpointModelFields: document.querySelector("#customEndpointModelFields"),
  customModelFile: document.querySelector("#customModelFile"),
  customModelDownloadUrl: document.querySelector("#customModelDownloadUrl"),
  customModelExpectedSize: document.querySelector("#customModelExpectedSize"),
  customModelSha256: document.querySelector("#customModelSha256"),
  customModelApiBase: document.querySelector("#customModelApiBase"),
  customModelAlias: document.querySelector("#customModelAlias"),
  customModelContext: document.querySelector("#customModelContext"),
  customModelSupportsTokenize: document.querySelector("#customModelSupportsTokenize"),
  customModelError: document.querySelector("#customModelError"),
  nasAssetSearch: document.querySelector("#nasAssetSearch"),
  nasAssetList: document.querySelector("#nasAssetList"),
  nasAssetDetail: document.querySelector("#nasAssetDetail"),
  dashboardAssetGrid: document.querySelector("#dashboardAssetGrid"),
  nasUploadDialog: document.querySelector("#nasUploadDialog"),
  closeNasUploadDialog: document.querySelector("#closeNasUploadDialog"),
  confirmNasUploadDialog: document.querySelector("#confirmNasUploadDialog"),
  nasUploadDialogMessage: document.querySelector("#nasUploadDialogMessage"),
  accountNav: document.querySelector("#accountNav"),
  lineAdminNav: document.querySelector("#lineAdminNav"),
  mcpNav: document.querySelector("#mcpNav"),
  n8nNav: document.querySelector("#n8nNav"),
  modelNav: document.querySelector("#modelNav"),
  lineGroupTotal: document.querySelector("#lineGroupTotal"),
  lineGroupApproved: document.querySelector("#lineGroupApproved"),
  lineMonthlyCalls: document.querySelector("#lineMonthlyCalls"),
  lineMonthlyTokens: document.querySelector("#lineMonthlyTokens"),
  refreshLineAdmin: document.querySelector("#refreshLineAdmin"),
  lineServiceNotice: document.querySelector("#lineServiceNotice"),
  lineAdminList: document.querySelector("#lineAdminList"),
  mcpServerTotal: document.querySelector("#mcpServerTotal"),
  mcpConnectedTotal: document.querySelector("#mcpConnectedTotal"),
  mcpEnabledTotal: document.querySelector("#mcpEnabledTotal"),
  mcpToolTotal: document.querySelector("#mcpToolTotal"),
  mcpSearchInput: document.querySelector("#mcpSearchInput"),
  refreshMcpServers: document.querySelector("#refreshMcpServers"),
  addMcpServer: document.querySelector("#addMcpServer"),
  mcpServerList: document.querySelector("#mcpServerList"),
  mcpServerModal: document.querySelector("#mcpServerModal"),
  mcpServerModalTitle: document.querySelector("#mcpServerModalTitle"),
  closeMcpServerModal: document.querySelector("#closeMcpServerModal"),
  cancelMcpServer: document.querySelector("#cancelMcpServer"),
  mcpServerForm: document.querySelector("#mcpServerForm"),
  mcpServerName: document.querySelector("#mcpServerName"),
  mcpServerSlug: document.querySelector("#mcpServerSlug"),
  mcpServerTransport: document.querySelector("#mcpServerTransport"),
  mcpServerEndpoint: document.querySelector("#mcpServerEndpoint"),
  mcpServerAuthEnv: document.querySelector("#mcpServerAuthEnv"),
  mcpServerAuthType: document.querySelector("#mcpServerAuthType"),
  mcpServerSourceUrl: document.querySelector("#mcpServerSourceUrl"),
  mcpServerEnabled: document.querySelector("#mcpServerEnabled"),
  mcpServerDescription: document.querySelector("#mcpServerDescription"),
  mcpServerDescriptionEn: document.querySelector("#mcpServerDescriptionEn"),
  mcpServerFormError: document.querySelector("#mcpServerFormError"),
  refreshN8nStatus: document.querySelector("#refreshN8nStatus"),
  openN8nButton: document.querySelector("#openN8nButton"),
  n8nStatusDot: document.querySelector("#n8nStatusDot"),
  n8nStatusText: document.querySelector("#n8nStatusText"),
  n8nVersion: document.querySelector("#n8nVersion"),
  n8nEndpoint: document.querySelector("#n8nEndpoint"),
  n8nLatency: document.querySelector("#n8nLatency"),
  n8nWorkflowName: document.querySelector("#n8nWorkflowName"),
  n8nNotice: document.querySelector("#n8nNotice"),
  accountTotal: document.querySelector("#accountTotal"),
  accountActive: document.querySelector("#accountActive"),
  accountAdmins: document.querySelector("#accountAdmins"),
  accountCreateForm: document.querySelector("#accountCreateForm"),
  newAccountUsername: document.querySelector("#newAccountUsername"),
  newAccountPassword: document.querySelector("#newAccountPassword"),
  newAccountRole: document.querySelector("#newAccountRole"),
  accountFormError: document.querySelector("#accountFormError"),
  accountSearch: document.querySelector("#accountSearch"),
  accountList: document.querySelector("#accountList"),
  passwordResetModal: document.querySelector("#passwordResetModal"),
  closePasswordReset: document.querySelector("#closePasswordReset"),
  cancelPasswordReset: document.querySelector("#cancelPasswordReset"),
  confirmPasswordReset: document.querySelector("#confirmPasswordReset"),
  passwordResetAccount: document.querySelector("#passwordResetAccount"),
  passwordResetInput: document.querySelector("#passwordResetInput"),
  passwordResetError: document.querySelector("#passwordResetError"),
};

function t(key, replacements = {}) {
  const value = key.split(".").reduce((current, part) => current?.[part], messages[state.lang]);
  const text = typeof value === "string" ? value : key;
  return Object.entries(replacements).reduce((result, [name, replacement]) => {
    return result.replaceAll(`{${name}}`, replacement);
  }, text);
}

function translateRaw(key) {
  return key.split(".").reduce((current, part) => current?.[part], messages[state.lang]);
}

function applyLanguage(lang) {
  state.lang = messages[lang] ? lang : "zh-Hant";
  localStorage.setItem("ai-work-lang", state.lang);
  document.documentElement.lang = state.lang;
  document.title = t("documentTitle");

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-attr]").forEach((node) => {
    node.dataset.i18nAttr.split(";").forEach((entry) => {
      const [attribute, key] = entry.split(":");
      if (attribute && key) node.setAttribute(attribute, t(key));
    });
  });
  els.langOptions.forEach((button) => button.classList.toggle("active", button.dataset.lang === state.lang));
  els.viewTitle.textContent = t(`nav.${currentViewName()}`);
  updateRecordingUi(state.recordMode);
  updateRecordingAvailability();
  renderMeetingList();
  if (state.selectedMeetingId) {
    selectMeeting(state.selectedMeetingId);
  } else {
    renderSelectedMeetingEmptyState();
  }
  renderLlmControls();
  renderPricingPanel();
  renderKeyStatus();
  renderModelUsePanel();
  renderAiworkMcpControls();
  renderLlmSuggestions();
  renderLlmCallHistory();
  renderDashboardAssets();
  renderNetworkAssets();
  renderNasAssetList();
  renderNasAssetDetail();
  renderRecordingAsrControls();
  renderAsrControls();
  renderTranslationControls("record");
  renderTranslationControls("audio");
  renderLinePushControls();
  renderVideoControls();
  renderLocalModelManager();
  renderMcpServers();
  renderN8nStatus();
  renderLineAdmin();
  renderAccountList();
  if (state.passwordResetUserId) {
    const resetUser = state.users.find((user) => user.id === state.passwordResetUserId);
    if (resetUser) els.passwordResetAccount.textContent = t("accounts.resetFor", { username: resetUser.username });
  }
  if (!els.apiKeyModal.hidden) renderKeyModal();
  if (state.user) renderCurrentUser();
}

let globalBusyCount = 0;
let globalBusyShownAt = 0;
let globalBusyHideTimer = null;
const GLOBAL_BUSY_MINIMUM_MS = 360;

function beginGlobalBusy() {
  globalBusyCount += 1;
  if (globalBusyHideTimer) {
    window.clearTimeout(globalBusyHideTimer);
    globalBusyHideTimer = null;
  }
  if (globalBusyCount === 1) {
    globalBusyShownAt = Date.now();
    els.globalBusyText.textContent = t("loading.active");
    els.globalBusyIndicator.hidden = false;
    document.documentElement.classList.add("is-busy");
  }
  let finished = false;
  return () => {
    if (finished) return;
    finished = true;
    globalBusyCount = Math.max(0, globalBusyCount - 1);
    if (globalBusyCount) return;
    const remaining = Math.max(0, GLOBAL_BUSY_MINIMUM_MS - (Date.now() - globalBusyShownAt));
    globalBusyHideTimer = window.setTimeout(() => {
      if (globalBusyCount) return;
      els.globalBusyIndicator.hidden = true;
      document.documentElement.classList.remove("is-busy");
      globalBusyHideTimer = null;
    }, remaining);
  };
}

async function api(path, options = {}) {
  const { busy = true, ...requestOptions } = options;
  const finishBusy = busy ? beginGlobalBusy() : () => {};
  try {
    const response = await fetch(path, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...(requestOptions.headers || {}) },
      ...requestOptions,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || t("errors.requestFailed"));
    }
    return response.json();
  } finally {
    finishBusy();
  }
}

function uploadFormData(path, formData, onProgress) {
  return new Promise((resolve, reject) => {
    const finishBusy = beginGlobalBusy();
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      finishBusy();
    };
    const request = new XMLHttpRequest();
    request.open("POST", path);
    request.withCredentials = true;
    request.timeout = 0;
    request.upload.addEventListener("progress", (event) => {
      if (!event.lengthComputable || !onProgress) return;
      onProgress(Math.min(100, Math.round((event.loaded / event.total) * 100)));
    });
    request.addEventListener("load", () => {
      finish();
      let payload = {};
      try {
        payload = request.responseText ? JSON.parse(request.responseText) : {};
      } catch {
        payload = {};
      }
      if (request.status >= 200 && request.status < 300) {
        resolve(payload);
        return;
      }
      reject(new Error(payload.detail || `${t("upload.uploadFailed")} (HTTP ${request.status})`));
    });
    request.addEventListener("error", () => {
      finish();
      reject(new Error(t("upload.connectionFailed")));
    });
    request.addEventListener("abort", () => {
      finish();
      reject(new Error(t("upload.connectionFailed")));
    });
    request.send(formData);
  });
}

function setNasUploadProgress(progress, visible) {
  els.nasUploadProgress.hidden = !visible;
  els.nasUploadProgressBar.value = progress;
  els.nasUploadProgressBar.textContent = `${progress}%`;
  els.nasUploadProgressText.textContent = t("upload.uploading", { progress });
}

async function bootstrap() {
  applyLanguage(state.lang);
  try {
    state.user = await api("/auth/me");
    showApp();
  } catch {
    showLogin();
  }
}

function showLogin() {
  els.loginView.hidden = false;
  els.appView.hidden = true;
  if (state.networkPollTimer) window.clearTimeout(state.networkPollTimer);
  state.networkPollTimer = null;
  closeWebSocket();
}

function setManagementMenuExpanded(expanded) {
  els.managementNavGroup.hidden = !expanded;
  els.settingsNav.setAttribute("aria-expanded", String(expanded));
  els.settingsNav.classList.toggle("expanded", expanded);
}

async function showApp() {
  els.loginView.hidden = true;
  els.appView.hidden = false;
  renderCurrentUser();
  const isAdmin = state.user.role === "admin";
  els.settingsNav.hidden = !isAdmin;
  els.modelNav.hidden = !isAdmin;
  els.accountNav.hidden = !isAdmin;
  els.lineAdminNav.hidden = !isAdmin;
  els.mcpNav.hidden = !isAdmin;
  els.n8nNav.hidden = !isAdmin;
  els.addCustomModelButton.hidden = !isAdmin;
  setManagementMenuExpanded(false);
  switchView("dashboard");
  connectWebSocket();
  await loadMeetings();
  await loadLlmCatalog();
  await loadAsrCatalog();
  await loadVideoCatalog();
  await loadLocalModels();
  await loadLineGroups();
  await loadLlmCalls();
  await loadAvailableMcpServers();
  await loadNasAssets();
  if (state.user.role === "admin") {
    await loadLineAdmin();
    await loadMcpServers();
    await loadAccounts();
  }
}

function renderCurrentUser() {
  els.currentUser.textContent = `${state.user.username} · ${t(`accounts.roles.${state.user.role}`)}`;
}

function switchView(name) {
  if (["models", "mcp", "n8n", "lineAdmin", "accounts"].includes(name) && state.user?.role !== "admin") name = "dashboard";
  const isManagementView = ["models", "mcp", "n8n", "lineAdmin", "accounts"].includes(name);
  Object.entries(els.sections).forEach(([key, section]) => {
    section.hidden = key !== name;
  });
  els.navItems.forEach((item) => item.classList.toggle("active", item.dataset.view === name));
  els.settingsNav.classList.toggle("active", isManagementView);
  if (isManagementView) setManagementMenuExpanded(true);
  els.viewTitle.textContent = t(`nav.${name}`);
}

async function refreshViewData(name) {
  if (name === "dashboard") return Promise.all([loadMeetings(), loadNasAssets()]);
  if (name === "record") return Promise.all([loadAsrCatalog(), loadLineGroups()]);
  if (name === "upload") return loadNasAssets();
  if (name === "network") return loadNetworkAssets();
  if (name === "models") return loadLocalModels();
  if (name === "meetings") return loadMeetings();
  if (name === "aiwork") return Promise.all([loadLlmCatalog(), loadLlmCalls(), loadAvailableMcpServers()]);
  if (name === "mcp") return loadMcpServers();
  if (name === "n8n") return loadN8nStatus();
  if (name === "lineAdmin") return loadLineAdmin();
  if (name === "accounts") return loadAccounts();
}

async function navigateFromSidebar(name, trigger = null) {
  const finishBusy = beginGlobalBusy();
  trigger?.classList.add("navigation-loading");
  trigger?.setAttribute("aria-busy", "true");
  try {
    if (name !== "network" && state.networkPollTimer) {
      window.clearTimeout(state.networkPollTimer);
      state.networkPollTimer = null;
    }
    if (name === "upload") {
      state.selectedAssetId = null;
      state.selectedAsset = null;
      renderNasAssetList();
      renderNasAssetDetail();
    }
    if (name === "meetings") {
      state.selectedMeetingId = null;
      renderMeetingList();
      renderSelectedMeetingEmptyState();
    }

    switchView(name);
    window.scrollTo({ top: 0, behavior: "smooth" });
    await refreshViewData(name);
  } finally {
    trigger?.classList.remove("navigation-loading");
    trigger?.removeAttribute("aria-busy");
    finishBusy();
  }
}

function currentViewName() {
  const active = els.navItems.find((item) => item.classList.contains("active"));
  return active?.dataset.view || "dashboard";
}

async function loadMeetings({ background = false } = {}) {
  const params = new URLSearchParams();
  const query = els.meetingSearch.value.trim();
  if (query) params.set("q", query);
  state.meetings = await api(`/api/meetings${params.toString() ? `?${params}` : ""}`, { busy: !background });
  renderMetrics();
  renderMeetingList();
}

async function loadLineGroups() {
  try {
    const result = await api("/api/line/groups");
    state.lineGroups = result.groups || [];
    if (!state.lineGroups.some((group) => group.id === state.recordLineGroupId)) {
      state.recordLineGroupId = state.lineGroups[0]?.id || "";
    }
  } catch {
    state.lineGroups = [];
    state.recordLineGroupId = "";
  }
  renderLinePushControls();
}

async function loadLineAdmin() {
  if (state.user?.role !== "admin") return;
  const result = await api("/api/admin/line/sources");
  state.lineAdminSources = result.sources || [];
  state.lineAdminModels = result.models || [];
  state.lineServiceConnected = Boolean(result.service_connected);
  renderLineAdmin();
}

async function loadMcpServers() {
  if (state.user?.role !== "admin") return;
  const result = await api("/api/admin/mcp/servers");
  state.mcpServers = result.servers || [];
  renderMcpServers();
}

async function loadN8nStatus() {
  if (state.user?.role !== "admin") return;
  state.n8nStatus = await api("/api/admin/n8n/status");
  renderN8nStatus();
}

function renderN8nStatus() {
  if (!els.n8nStatusText) return;
  if (!state.n8nStatus) {
    els.n8nStatusDot.classList.remove("connected", "unavailable");
    els.n8nStatusText.textContent = t("n8n.checking");
    els.n8nNotice.textContent = "";
    els.openN8nButton.setAttribute("aria-disabled", "true");
    els.openN8nButton.classList.add("disabled");
    return;
  }
  const status = state.n8nStatus;
  const connected = status.status === "connected";
  els.n8nStatusDot.classList.toggle("connected", connected);
  els.n8nStatusDot.classList.toggle("unavailable", !connected);
  els.n8nStatusText.textContent = t(connected ? "n8n.connected" : "n8n.unavailable");
  els.n8nVersion.textContent = status.version || "--";
  els.n8nEndpoint.textContent = status.public_url || "/n8n/";
  els.n8nLatency.textContent = Number.isFinite(status.response_ms) ? `${status.response_ms} ms` : "--";
  els.n8nWorkflowName.textContent = status.test_workflow || "AI Work NAS 處理完成通知 Demo";
  els.n8nNotice.textContent = t(connected ? "n8n.readyNotice" : "n8n.unavailableNotice");
  els.n8nNotice.classList.toggle("ready", connected);
  els.openN8nButton.setAttribute("aria-disabled", String(!connected));
  els.openN8nButton.classList.toggle("disabled", !connected);
}

async function loadAvailableMcpServers() {
  const result = await api("/api/mcp/available");
  state.availableMcpServers = result.servers || [];
  if (
    state.selectedMcpServerId !== "auto"
    && !state.availableMcpServers.some((server) => String(server.id) === state.selectedMcpServerId)
  ) {
    state.selectedMcpServerId = "auto";
  }
  renderAiworkMcpControls();
}

function renderAiworkMcpControls() {
  if (!els.useMcpToggle) return;
  const servers = state.availableMcpServers;
  const toolCount = servers.reduce((sum, server) => sum + Number(server.tool_count || 0), 0);
  els.useMcpToggle.checked = state.useMcp;
  els.useMcpToggle.disabled = !servers.length;
  els.aiworkMcpServerSelect.disabled = !state.useMcp || !servers.length;
  els.aiworkMcpServerSelect.innerHTML = `
    <option value="auto">${escapeHtml(t("aiwork.mcpAuto"))}</option>
    ${servers.map((server) => `
      <option value="${server.id}">${escapeHtml(server.name)} · ${Number(server.tool_count || 0)}</option>
    `).join("")}
  `;
  els.aiworkMcpServerSelect.value = state.selectedMcpServerId;
  els.aiworkMcpStatus.textContent = servers.length
    ? t("aiwork.mcpReady", { servers: servers.length, tools: toolCount })
    : t("aiwork.mcpUnavailable");
  els.aiworkMcpStatus.classList.toggle("unavailable", !servers.length);
}

function renderMcpServers() {
  if (!els.mcpServerList || state.user?.role !== "admin") return;
  els.mcpServerTotal.textContent = state.mcpServers.length;
  els.mcpConnectedTotal.textContent = state.mcpServers.filter((server) => server.status === "connected").length;
  els.mcpEnabledTotal.textContent = state.mcpServers.filter((server) => server.is_enabled).length;
  els.mcpToolTotal.textContent = state.mcpServers.reduce((sum, server) => sum + Number(server.tool_count || 0), 0);

  const query = state.mcpSearchQuery.trim().toLowerCase();
  const visibleServers = query
    ? state.mcpServers.filter((server) => [
        server.name, server.slug, server.endpoint, server.description, server.description_en,
      ].some((value) => String(value || "").toLowerCase().includes(query)))
    : state.mcpServers;

  if (!visibleServers.length) {
    els.mcpServerList.innerHTML = `<div class="empty-state compact">${escapeHtml(t("mcp.empty"))}</div>`;
    return;
  }

  const categories = [
    { key: "nas", slugs: ["nas-demo", "nas-filesystem", "notion"] },
    {
      key: "office",
      slugs: [
        "gmail", "google-drive", "google-docs", "google-slides",
        "google-calendar", "google-chat", "google-people", "slack",
      ],
    },
    {
      key: "spreadsheet",
      slugs: ["nas-excel", "google-sheets", "microsoft-365-excel", "microsoft-markitdown"],
    },
    { key: "finance", slugs: ["xero", "odoo", "quickbooks", "netsuite", "stripe"] },
    { key: "project", slugs: ["monday", "linear", "atlassian"] },
    {
      key: "technical",
      slugs: ["github", "cloudflare", "cloudflare-docs", "vercel", "supabase", "context7", "postgresql"],
    },
  ];
  const categorizedSlugs = new Set(categories.flatMap((category) => category.slugs));
  const sortByCategory = (servers, slugs) => servers.slice().sort((left, right) => {
    const leftIndex = slugs.indexOf(left.slug);
    const rightIndex = slugs.indexOf(right.slug);
    const leftRank = leftIndex === -1 ? slugs.length : leftIndex;
    const rightRank = rightIndex === -1 ? slugs.length : rightIndex;
    return leftRank - rightRank || left.name.localeCompare(right.name);
  });
  const renderServerCard = (server) => {
    const description = state.lang === "en"
      ? server.description_en || server.description
      : server.description || server.description_en;
    const authState = server.auth_env_var
      ? server.auth_configured ? t("mcp.authReady") : t("mcp.authMissing")
      : t("mcp.authNone");
    const canSync = server.transport === "streamable_http" && Boolean(server.endpoint) && server.is_enabled;
    const tools = server.tools || [];
    const endpoint = server.public_endpoint
      ? new URL(server.public_endpoint, window.location.origin).href
      : server.endpoint || "";
    const authType = t(`mcp.authTypes.${server.auth_type || "none"}`);
    const fixedHeaders = Object.entries(server.headers || {})
      .map(([name, value]) => `${name}: ${value}`)
      .join(" · ");
    return `
      <article class="mcp-server-card ${escapeHtml(server.status)}" data-mcp-server-id="${server.id}">
        <div class="mcp-server-head">
          <div>
            <span class="mcp-status-badge ${escapeHtml(server.status)}">${escapeHtml(t(`mcp.status.${server.status}`))}</span>
            <h4>${escapeHtml(server.name)}</h4>
            <p>${escapeHtml(description || "-")}</p>
          </div>
          <div class="mcp-server-actions">
            <button class="secondary-button compact-button" type="button" data-mcp-action="edit">${escapeHtml(t("mcp.edit"))}</button>
            <button class="primary-button compact-button" type="button" data-mcp-action="sync" ${canSync ? "" : "disabled"}>${escapeHtml(t("mcp.sync"))}</button>
          </div>
        </div>
        <div class="mcp-server-meta">
          <span><b>${escapeHtml(t("mcp.transport"))}</b>${escapeHtml(server.transport)}</span>
          <span class="mcp-endpoint-meta"><b>${escapeHtml(t("mcp.endpoint"))}</b><code>${escapeHtml(endpoint || "-")}</code>${endpoint ? `<button class="text-action" type="button" data-mcp-action="copy" data-mcp-endpoint="${escapeHtml(endpoint)}">${escapeHtml(t("mcp.copyEndpoint"))}</button>` : ""}</span>
          <span class="${server.auth_env_var && !server.auth_configured ? "warning" : ""}"><b>${escapeHtml(t("mcp.auth"))}</b>${escapeHtml(authType)} · ${escapeHtml(authState)}${server.auth_env_var ? ` · ${escapeHtml(server.auth_env_var)}` : ""}</span>
          ${fixedHeaders ? `<span><b>${escapeHtml(t("mcp.requestHeaders"))}</b><code>${escapeHtml(fixedHeaders)}</code></span>` : ""}
          <span><b>${escapeHtml(t("mcp.protocol"))}</b>${escapeHtml(server.protocol_version || "-")}</span>
          <span><b>${escapeHtml(t("mcp.lastChecked"))}</b>${escapeHtml(server.last_checked_at ? formatDate(server.last_checked_at) : t("mcp.neverChecked"))}</span>
          <span><b>${escapeHtml(t("mcp.enabled"))}</b>${escapeHtml(t(server.is_enabled ? "mcp.enabledForLlm" : "mcp.disabledForLlm"))}${server.source_url ? `<a class="mcp-source-link" href="${escapeHtml(server.source_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(t("mcp.officialSource"))}</a>` : ""}</span>
        </div>
        ${server.last_error ? `<p class="mcp-server-error">${escapeHtml(server.last_error)}</p>` : ""}
        <details class="mcp-tool-catalog" ${tools.length ? "" : "disabled"}>
          <summary>${escapeHtml(t("mcp.tools"))} · ${tools.length}</summary>
          ${tools.length ? `<div class="mcp-tool-list">${tools.map((tool) => `
            <article>
              <strong>${escapeHtml(tool.title || tool.name)}</strong>
              <code>${escapeHtml(tool.name)}</code>
              <p>${escapeHtml(tool.description || "-")}</p>
            </article>
          `).join("")}</div>` : `<p>${escapeHtml(t("mcp.noTools"))}</p>`}
        </details>
      </article>
    `;
  };
  const groupedCategories = categories.map((category) => ({
    ...category,
    servers: sortByCategory(
      visibleServers.filter((server) => category.slugs.includes(server.slug)),
      category.slugs,
    ),
  }));
  groupedCategories.push({
    key: "other",
    slugs: [],
    servers: visibleServers
      .filter((server) => !categorizedSlugs.has(server.slug))
      .sort((left, right) => left.name.localeCompare(right.name)),
  });
  els.mcpServerList.innerHTML = groupedCategories
    .filter((category) => category.servers.length)
    .map((category) => `
      <details class="mcp-server-group ${escapeHtml(category.key)}" data-mcp-category="${escapeHtml(category.key)}" ${query ? "open" : ""}>
        <summary class="mcp-group-heading">
          <div>
            <h4>${escapeHtml(t(`mcp.categories.${category.key}.title`))}</h4>
            <p>${escapeHtml(t(`mcp.categories.${category.key}.copy`))}</p>
          </div>
          <span>${escapeHtml(t("mcp.connectorCount", { count: category.servers.length }))}</span>
        </summary>
        <div class="mcp-server-group-list">${category.servers.map(renderServerCard).join("")}</div>
      </details>
    `).join("");
}

function openMcpServerModal(server = null) {
  state.editingMcpServerId = server?.id || null;
  els.mcpServerModalTitle.textContent = t(server ? "mcp.modalEditTitle" : "mcp.modalAddTitle");
  els.mcpServerName.value = server?.name || "";
  els.mcpServerSlug.value = server?.slug || "";
  els.mcpServerTransport.value = server?.transport || "streamable_http";
  els.mcpServerEndpoint.value = server?.endpoint || "";
  els.mcpServerAuthEnv.value = server?.auth_env_var || "";
  els.mcpServerAuthType.value = server?.auth_type || "none";
  els.mcpServerSourceUrl.value = server?.source_url || "";
  els.mcpServerEnabled.checked = Boolean(server?.is_enabled);
  els.mcpServerDescription.value = server?.description || "";
  els.mcpServerDescriptionEn.value = server?.description_en || "";
  els.mcpServerFormError.textContent = "";
  els.mcpServerModal.hidden = false;
  window.setTimeout(() => els.mcpServerName.focus(), 0);
}

function closeMcpServerModal() {
  els.mcpServerModal.hidden = true;
  state.editingMcpServerId = null;
  els.mcpServerForm.reset();
  els.mcpServerFormError.textContent = "";
}

async function saveMcpServer(event) {
  event.preventDefault();
  const payload = {
    name: els.mcpServerName.value.trim(),
    slug: els.mcpServerSlug.value.trim().toLowerCase(),
    transport: els.mcpServerTransport.value,
    endpoint: els.mcpServerEndpoint.value.trim(),
    auth_env_var: els.mcpServerAuthEnv.value.trim(),
    auth_type: els.mcpServerAuthType.value,
    source_url: els.mcpServerSourceUrl.value.trim(),
    is_enabled: els.mcpServerEnabled.checked,
    description: els.mcpServerDescription.value.trim(),
    description_en: els.mcpServerDescriptionEn.value.trim(),
  };
  const editing = state.editingMcpServerId;
  const submit = els.mcpServerForm.querySelector('button[type="submit"]');
  submit.disabled = true;
  els.mcpServerFormError.textContent = "";
  try {
    await api(editing ? `/api/admin/mcp/servers/${editing}` : "/api/admin/mcp/servers", {
      method: editing ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    closeMcpServerModal();
    showToast(t("mcp.saved"), t("nav.mcp"));
    await loadMcpServers();
  } catch (error) {
    els.mcpServerFormError.textContent = error.message.includes("slug") ? t("mcp.duplicate") : error.message;
  } finally {
    submit.disabled = false;
  }
}

async function syncMcpServer(button, server) {
  button.disabled = true;
  button.textContent = t("mcp.syncing");
  try {
    await api(`/api/admin/mcp/servers/${server.id}/sync`, { method: "POST" });
    showToast(t("mcp.syncSuccess"), server.name);
  } catch (error) {
    showToast(error.message, t("mcp.syncFailed"));
  } finally {
    await loadMcpServers();
  }
}

async function copyMcpEndpoint(endpoint) {
  try {
    await navigator.clipboard.writeText(endpoint);
    showToast(t("mcp.endpointCopied"), t("nav.mcp"));
  } catch {
    showToast(endpoint, t("mcp.copyEndpoint"));
  }
}

function renderLineAdmin() {
  if (!els.lineAdminList || state.user?.role !== "admin") return;
  const sources = state.lineAdminSources;
  const totalCalls = sources.reduce((sum, source) => sum + Number(source.monthly_call_count || 0), 0);
  const totalTokens = sources.reduce((sum, source) => sum + Number(source.monthly_token_count || 0), 0);
  els.lineGroupTotal.textContent = sources.length;
  els.lineGroupApproved.textContent = sources.filter((source) => Boolean(source.is_approved)).length;
  els.lineMonthlyCalls.textContent = formatCompactNumber(totalCalls);
  els.lineMonthlyTokens.textContent = formatCompactNumber(totalTokens);
  els.lineServiceNotice.className = `line-service-notice ${state.lineServiceConnected ? "ready" : "unavailable"}`;
  els.lineServiceNotice.textContent = t(state.lineServiceConnected ? "lineAdmin.serviceReady" : "lineAdmin.serviceUnavailable");

  if (!sources.length) {
    els.lineAdminList.innerHTML = `<div class="empty-state compact">${escapeHtml(t("lineAdmin.empty"))}</div>`;
    return;
  }

  els.lineAdminList.innerHTML = sources.map((source) => {
    const approved = Boolean(source.is_approved);
    const callCount = Number(source.monthly_call_count || 0);
    const tokenCount = Number(source.monthly_token_count || 0);
    const callLimit = Number(source.monthly_call_limit || 0);
    const tokenLimit = Number(source.monthly_token_limit || 0);
    const modelOptions = state.lineAdminModels.map((model) => {
      const mode = model.access_mode === "local_nas" ? t("lineAdmin.localModel") : t("lineAdmin.companyApi");
      return `<option value="${escapeHtml(model.id)}" ${model.id === source.default_model_id ? "selected" : ""}>${escapeHtml(mode)} · ${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</option>`;
    }).join("");
    return `
      <article class="line-group-card ${approved ? "approved" : "pending"}" data-line-source-id="${source.id}">
        <div class="line-group-header">
          <div>
            <span class="line-group-status">${escapeHtml(t(approved ? "lineAdmin.approved" : "lineAdmin.pending"))}</span>
            <h4>${escapeHtml(source.display_name || source.source_id)}</h4>
          </div>
          <div class="line-group-meta">
            <span>${escapeHtml(t("lineAdmin.documents"))}: <strong>${source.document_count}</strong></span>
            <span>${escapeHtml(t("lineAdmin.usage"))}: <strong>${formatCompactNumber(callCount)} / ${callLimit ? formatCompactNumber(callLimit) : "∞"}</strong> · <strong>${formatCompactNumber(tokenCount)} / ${tokenLimit ? formatCompactNumber(tokenLimit) : "∞"} Token</strong></span>
          </div>
        </div>
        <div class="line-group-reference">
          <span>${escapeHtml(t("lineAdmin.groupId"))}: ${escapeHtml(source.source_id)}</span>
          <span>${escapeHtml(t("lineAdmin.owner"))}: ${escapeHtml(source.owner_username)}</span>
        </div>
        <div class="line-policy-switches">
          <label><input type="checkbox" data-line-approved ${approved ? "checked" : ""} /><span>${escapeHtml(t("lineAdmin.approve"))}</span></label>
          <label><input type="checkbox" data-line-pdf-summary ${source.auto_pdf_summary ? "checked" : ""} /><span>${escapeHtml(t("lineAdmin.pdfSummary"))}</span></label>
          <label><input type="checkbox" data-line-rag ${source.rag_queries_enabled ? "checked" : ""} /><span>${escapeHtml(t("lineAdmin.ragQueries"))}</span></label>
        </div>
        <div class="line-policy-grid">
          <label>
            <span>${escapeHtml(t("lineAdmin.model"))}</span>
            <select data-line-model>${modelOptions}</select>
          </label>
          <label>
            <span>${escapeHtml(t("lineAdmin.callLimit"))}</span>
            <input data-line-call-limit type="number" min="0" max="1000000" step="1" value="${callLimit}" />
          </label>
          <label>
            <span>${escapeHtml(t("lineAdmin.tokenLimit"))}</span>
            <input data-line-token-limit type="number" min="0" max="1000000000" step="1000" value="${tokenLimit}" />
          </label>
          <button class="primary-button" type="button" data-line-action="save">${escapeHtml(t("lineAdmin.save"))}</button>
        </div>
        <small class="line-policy-hint">${escapeHtml(t("lineAdmin.unlimitedHint"))}</small>
      </article>
    `;
  }).join("");
}

function formatCompactNumber(value) {
  return new Intl.NumberFormat(state.lang, { notation: value >= 10000 ? "compact" : "standard", maximumFractionDigits: 1 }).format(value);
}

async function saveLineSourcePolicy(button) {
  const card = button.closest("[data-line-source-id]");
  if (!card) return;
  button.disabled = true;
  try {
    await api(`/api/admin/line/sources/${card.dataset.lineSourceId}`, {
      method: "PATCH",
      body: JSON.stringify({
        is_approved: card.querySelector("[data-line-approved]").checked,
        auto_pdf_summary: card.querySelector("[data-line-pdf-summary]").checked,
        rag_queries_enabled: card.querySelector("[data-line-rag]").checked,
        default_model_id: card.querySelector("[data-line-model]").value,
        monthly_call_limit: Number(card.querySelector("[data-line-call-limit]").value),
        monthly_token_limit: Number(card.querySelector("[data-line-token-limit]").value),
      }),
    });
    showToast(t("lineAdmin.saved"), t("nav.lineAdmin"));
    await Promise.all([loadLineAdmin(), loadLineGroups()]);
  } catch (error) {
    showToast(error.message || t("lineAdmin.saveFailed"), t("lineAdmin.saveFailed"));
    await loadLineAdmin();
  } finally {
    button.disabled = false;
  }
}

async function loadAccounts() {
  if (state.user?.role !== "admin") return;
  state.users = await api("/api/admin/users");
  renderAccountList();
}

function renderAccountList() {
  if (!els.accountList || state.user?.role !== "admin") return;
  els.accountTotal.textContent = state.users.length;
  els.accountActive.textContent = state.users.filter((user) => Boolean(user.is_active)).length;
  els.accountAdmins.textContent = state.users.filter((user) => user.role === "admin" && user.is_active).length;

  const query = els.accountSearch.value.trim().toLocaleLowerCase();
  const visibleUsers = query
    ? state.users.filter((user) => `${user.username} ${user.role} ${t(`accounts.roles.${user.role}`)}`.toLocaleLowerCase().includes(query))
    : state.users;

  if (!visibleUsers.length) {
    els.accountList.innerHTML = `<div class="empty-state compact">${escapeHtml(t("accounts.empty"))}</div>`;
    return;
  }

  els.accountList.innerHTML = visibleUsers.map((user) => {
    const isSelf = user.id === state.user.id;
    const ownedRecords = Number(user.asset_count) + Number(user.meeting_count) + Number(user.llm_call_count);
    const canDelete = !isSelf && user.role !== "admin" && ownedRecords === 0;
    const lastLogin = user.last_login_at ? formatDate(user.last_login_at) : t("accounts.never");
    const deleteTitle = canDelete ? t("accounts.delete") : t("accounts.protected");
    return `
      <article class="account-row ${user.is_active ? "" : "inactive"}" data-user-id="${user.id}">
        <div class="account-identity">
          <div class="account-avatar">${escapeHtml(user.username.slice(0, 2).toUpperCase())}</div>
          <div>
            <strong>${escapeHtml(user.username)}</strong>
            ${isSelf ? `<span class="current-account-label">${escapeHtml(t("accounts.current"))}</span>` : ""}
            <small>#${user.id} · ${escapeHtml(t("accounts.created"))} ${escapeHtml(formatDate(user.created_at))}</small>
          </div>
        </div>
        <label class="account-role-field">
          <span class="sr-only">${escapeHtml(t("accounts.role"))}</span>
          <select data-account-role ${isSelf ? "disabled" : ""}>
            <option value="user" ${user.role === "user" ? "selected" : ""}>${escapeHtml(t("accounts.roles.user"))}</option>
            <option value="admin" ${user.role === "admin" ? "selected" : ""}>${escapeHtml(t("accounts.roles.admin"))}</option>
          </select>
        </label>
        <label class="account-status-control">
          <input type="checkbox" data-account-active ${user.is_active ? "checked" : ""} ${isSelf ? "disabled" : ""} />
          <span>${escapeHtml(t(`accounts.statuses.${user.is_active ? "active" : "inactive"}`))}</span>
        </label>
        <div class="account-activity">
          <strong>${escapeHtml(t("accounts.lastLogin"))}: ${escapeHtml(lastLogin)}</strong>
          <small>${escapeHtml(t("accounts.records", {
            assets: user.asset_count,
            meetings: user.meeting_count,
            calls: user.llm_call_count,
          }))}</small>
        </div>
        <div class="account-actions">
          <button class="secondary-button" type="button" data-account-action="save" ${isSelf ? "disabled" : ""}>${escapeHtml(t("accounts.save"))}</button>
          <button class="secondary-button" type="button" data-account-action="reset">${escapeHtml(t("accounts.reset"))}</button>
          <button class="danger-button" type="button" data-account-action="delete" title="${escapeHtml(deleteTitle)}" ${canDelete ? "" : "disabled"}>${escapeHtml(t("accounts.delete"))}</button>
        </div>
      </article>
    `;
  }).join("");
}

function accountErrorMessage(message) {
  if (message === "Username already exists") return t("accounts.duplicate");
  if (message.includes("Username must be")) return t("accounts.invalidUsername");
  if (message.includes("Password must be")) return t("accounts.invalidPassword");
  if (message.includes("cannot deactivate")) return t("accounts.selfProtection");
  if (message.includes("owns NAS records")) return t("accounts.ownsRecords");
  return t("accounts.operationFailed");
}

function openPasswordReset(userId) {
  const user = state.users.find((item) => item.id === userId);
  if (!user) return;
  state.passwordResetUserId = userId;
  els.passwordResetAccount.textContent = t("accounts.resetFor", { username: user.username });
  els.passwordResetInput.value = "";
  els.passwordResetError.textContent = "";
  els.passwordResetModal.hidden = false;
  window.setTimeout(() => els.passwordResetInput.focus(), 0);
}

function closePasswordReset() {
  state.passwordResetUserId = null;
  els.passwordResetInput.value = "";
  els.passwordResetError.textContent = "";
  els.passwordResetModal.hidden = true;
}

async function resetSelectedAccountPassword() {
  const userId = state.passwordResetUserId;
  const password = els.passwordResetInput.value;
  if (!userId || password.length < 8 || password.length > 128) {
    els.passwordResetError.textContent = t("accounts.invalidPassword");
    return;
  }
  try {
    await api(`/api/admin/users/${userId}/reset-password`, {
      method: "POST",
      body: JSON.stringify({ password }),
    });
    closePasswordReset();
    showToast(t("accounts.resetSuccess"), t("nav.accounts"));
    if (userId === state.user.id) {
      state.user = null;
      showLogin();
      return;
    }
    await loadAccounts();
  } catch (error) {
    els.passwordResetError.textContent = accountErrorMessage(error.message);
  }
}

async function handleAccountAction(button) {
  const row = button.closest("[data-user-id]");
  const userId = Number(row?.dataset.userId);
  const user = state.users.find((item) => item.id === userId);
  if (!user) return;

  if (button.dataset.accountAction === "reset") {
    openPasswordReset(userId);
    return;
  }

  try {
    if (button.dataset.accountAction === "save") {
      await api(`/api/admin/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({
          role: row.querySelector("[data-account-role]").value,
          is_active: row.querySelector("[data-account-active]").checked,
        }),
      });
      showToast(t("accounts.updatedSuccess"), t("nav.accounts"));
    }
    if (button.dataset.accountAction === "delete") {
      if (!window.confirm(t("accounts.confirmDelete", { username: user.username }))) return;
      await api(`/api/admin/users/${userId}`, { method: "DELETE" });
      showToast(t("accounts.deletedSuccess"), t("nav.accounts"));
    }
    await loadAccounts();
  } catch (error) {
    showToast(accountErrorMessage(error.message), t("accounts.operationFailed"));
    await loadAccounts();
  }
}

async function loadLlmCatalog() {
  state.llmCatalog = await api("/api/llm/models");
  const current = state.llmCatalog.current_model || defaultLlmModelForMode("local");
  state.currentLlmModel = current;
  state.currentLlmId = current?.id || "";
  state.selectedLlmMode = current?.execution || "local";
  state.selectedProvider = current?.provider || "";
  state.selectedLlmId = current?.id || "";
  state.recordTranslationMode = state.selectedLlmMode;
  state.recordTranslationModelId = state.currentLlmId;
  state.audioTranslationMode = state.selectedLlmMode;
  state.audioTranslationModelId = state.currentLlmId;
  renderLlmControls();
  renderTranslationControls("record");
  renderTranslationControls("audio");
  if (state.selectedLlmId) {
    await selectLlmModel(state.selectedLlmId);
  } else {
    renderPricingPanel();
    renderKeyStatus();
  }
}

async function loadAsrCatalog() {
  state.asrCatalog = await api("/api/asr/models");
  const current = state.asrCatalog.current_model || state.asrCatalog.models?.[0] || null;
  state.currentAsrModel = current;
  state.currentAsrId = current?.id || "";
  state.selectedRecordAsrMode = current?.id?.startsWith("cloud:") ? "cloud" : "local";
  state.selectedRecordAsrModelId = state.currentAsrId;
  state.selectedAsrMode = state.selectedRecordAsrMode;
  state.selectedAsrModelId = state.currentAsrId;
  renderRecordingAsrControls();
  renderAsrControls();
}

async function loadVideoCatalog() {
  state.videoCatalog = await api("/api/video/models");
  renderVideoControls();
}

async function loadLocalModels({ background = false } = {}) {
  state.localModels = await api("/api/local-models", { busy: !background });
  renderLocalModelManager();
  renderRecordingAsrControls();
  renderAsrControls();
  scheduleLocalModelPolling();
}

async function loadLlmCalls() {
  const params = new URLSearchParams();
  const query = els.llmCallSearch.value.trim();
  if (query) params.set("q", query);
  state.llmCalls = await api(`/api/llm/calls${params.toString() ? `?${params}` : ""}`);
  renderLlmCallHistory();
}

async function loadNasAssets({ background = false } = {}) {
  const params = new URLSearchParams();
  const query = els.nasAssetSearch.value.trim();
  if (query) params.set("q", query);
  state.nasAssets = await api(`/api/nas-assets${params.toString() ? `?${params}` : ""}`, { busy: !background });
  renderDashboardAssets();
  renderNasAssetList();
  if (state.selectedAssetId) {
    const stillExists = state.nasAssets.some((asset) => asset.id === state.selectedAssetId);
    if (stillExists) await selectNasAsset(state.selectedAssetId);
  }
}

async function loadNetworkAssets({ background = false } = {}) {
  state.networkAssets = await api("/api/network-assets", { busy: !background });
  renderNetworkAssets();
  scheduleNetworkAssetPolling();
}

function renderNetworkAssets() {
  if (!els.networkAssetList) return;
  if (!state.networkAssets.length) {
    els.networkAssetList.innerHTML = `<div class="empty-state compact">${escapeHtml(t("network.empty"))}</div>`;
    return;
  }
  els.networkAssetList.innerHTML = state.networkAssets
    .map((asset) => {
      const canOpen = Number(asset.file_size || 0) > 0 && asset.status !== "downloading";
      const detail = asset.error_message || asset.summary || t("meetings.processingText");
      return `
        <article class="network-asset-row">
          <div class="network-asset-heading">
            <div>
              <strong>${escapeHtml(asset.title)}</strong>
              <span>${escapeHtml(asset.category.toUpperCase())} · ${escapeHtml(formatDate(asset.created_at))}</span>
            </div>
            <span class="badge ${escapeHtml(asset.status)}">${escapeHtml(statusLabel(asset.status))}</span>
          </div>
          <p>${escapeHtml(detail)}</p>
          <div class="network-asset-meta">
            <a href="${escapeHtml(asset.source_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(t("network.source"))}</a>
            <span>${escapeHtml(asset.owner_username || "-")}</span>
            ${asset.file_size ? `<span>${escapeHtml(formatBytes(asset.file_size))}</span>` : ""}
          </div>
          <button class="secondary-button compact-button" type="button" data-network-asset-id="${asset.id}" ${canOpen ? "" : "disabled"}>
            ${escapeHtml(t("network.openAsset"))}
          </button>
        </article>
      `;
    })
    .join("");
}

function scheduleNetworkAssetPolling() {
  if (state.networkPollTimer) window.clearTimeout(state.networkPollTimer);
  state.networkPollTimer = null;
  const active = state.networkAssets.some((asset) => ["downloading", "processing"].includes(asset.status));
  if (!active || currentViewName() !== "network") return;
  state.networkPollTimer = window.setTimeout(() => {
    loadNetworkAssets({ background: true }).catch(() => {});
  }, 3000);
}

async function submitNetworkImport(event) {
  event.preventDefault();
  els.networkImportSubmit.disabled = true;
  els.networkImportSubmit.textContent = t("network.submitting");
  try {
    await api("/api/network-assets/youtube", {
      method: "POST",
      body: JSON.stringify({
        url: els.networkUrlInput.value.trim(),
        title: els.networkTitleInput.value.trim(),
        media_type: els.networkMediaType.value,
        authorized: els.networkAuthorized.checked,
      }),
    });
    els.networkImportForm.reset();
    showToast(t("network.queued"), t("nav.network"));
    await loadNetworkAssets();
  } catch (error) {
    showToast(error.message, t("network.failed"));
  } finally {
    els.networkImportSubmit.disabled = false;
    els.networkImportSubmit.textContent = t("network.submit");
  }
}

function renderNasAssetList() {
  if (!state.nasAssets.length) {
    els.nasAssetList.innerHTML = `<div class="empty-state compact">${t("upload.emptyList")}</div>`;
    return;
  }

  els.nasAssetList.innerHTML = state.nasAssets
    .map((asset) => {
      return `
        <button class="nas-asset-row ${asset.id === state.selectedAssetId ? "active" : ""}" data-asset-id="${asset.id}">
          <div class="meeting-row-header">
            <strong>${escapeHtml(asset.title)}</strong>
            <span class="badge ${escapeHtml(asset.status)}">${statusLabel(asset.status)}</span>
          </div>
          <p>${escapeHtml(asset.category.toUpperCase())} · ${escapeHtml(asset.analyzer || "-")} · ${escapeHtml(formatDate(asset.created_at))}</p>
          <p>${escapeHtml(asset.original_filename)}</p>
        </button>
      `;
    })
    .join("");
}

async function selectNasAsset(id, { scroll = false } = {}) {
  state.selectedAssetId = id;
  renderNasAssetList();
  state.selectedAsset = await api(`/api/nas-assets/${id}`);
  renderNasAssetDetail();
  if (scroll) els.nasAssetDetail.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function openNasAsset(id, { transcript = false } = {}) {
  switchView("upload");
  await selectNasAsset(id, { scroll: !transcript });
  if (transcript) {
    document.querySelector("#assetTranscript")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function dashboardAssetMatches(asset, filter) {
  if (filter === "all") return true;
  if (filter === "document") return ["pdf", "docx", "excel", "file"].includes(asset.category);
  return asset.category === filter;
}

function renderDashboardAssets() {
  if (!els.dashboardAssetGrid) return;
  document.querySelectorAll("[data-dashboard-asset-filter]").forEach((button) => {
    button.classList.toggle("active", button.dataset.dashboardAssetFilter === state.dashboardAssetFilter);
  });
  const assets = state.nasAssets
    .filter((asset) => dashboardAssetMatches(asset, state.dashboardAssetFilter))
    .sort((left, right) => (
      String(right.created_at || "").localeCompare(String(left.created_at || ""))
      || Number(right.id || 0) - Number(left.id || 0)
    ));
  if (!assets.length) {
    els.dashboardAssetGrid.innerHTML = `<div class="empty-state compact">${escapeHtml(t("dashboardAssets.empty"))}</div>`;
    return;
  }
  els.dashboardAssetGrid.innerHTML = assets
    .map((asset, index) => {
      const transcript = String(asset.transcript_preview || "").replace(/\s+/g, " ").trim();
      const transcriptFallback = asset.status === "processing"
        ? t("dashboardAssets.transcriptProcessing")
        : t("dashboardAssets.transcriptUnavailable");
      return `
      <article class="dashboard-asset-row">
        <span class="asset-kind">${escapeHtml(asset.category.toUpperCase())}</span>
        <span class="dashboard-asset-name">
          <strong>${escapeHtml(asset.title)}</strong>
          <small>${escapeHtml(asset.original_filename)}</small>
        </span>
        <span class="dashboard-asset-upload">
          <small><b>${escapeHtml(t("dashboardAssets.uploader"))}</b>${escapeHtml(asset.owner_username || "-")}</small>
          <small><b>${escapeHtml(t("dashboardAssets.uploadedAt"))}</b>${escapeHtml(formatDate(asset.created_at))}</small>
        </span>
        <span class="dashboard-asset-size">
          <b>${escapeHtml(formatBytes(asset.file_size))}</b>
          ${index === 0 ? `<small>${escapeHtml(t("dashboardAssets.newest"))}</small>` : ""}
        </span>
        <span class="badge ${escapeHtml(asset.status)}">${escapeHtml(statusLabel(asset.status))}</span>
        <button class="dashboard-asset-open" type="button" data-dashboard-asset-id="${asset.id}">
          ${escapeHtml(t("dashboardAssets.open"))}
        </button>
        ${asset.category === "audio" ? `
          <div class="dashboard-transcript-preview">
            <strong>${escapeHtml(t("dashboardAssets.transcript"))}</strong>
            <p class="${transcript ? "" : "is-empty"}">${escapeHtml(transcript || transcriptFallback)}</p>
            <button class="dashboard-transcript-open" type="button" data-dashboard-transcript-id="${asset.id}">
              ${escapeHtml(t("dashboardAssets.transcriptDetail"))}
            </button>
          </div>
        ` : ""}
      </article>
    `;
    })
    .join("");
}

function apiKeyForProvider(provider) {
  const normalized = providerKeyId(provider || "");
  const aliases = {
    "google-gemini": ["google"],
    google: ["google-gemini"],
  };
  return [normalized, ...(aliases[normalized] || [])]
    .map((key) => state.apiKeys[key] || "")
    .find(Boolean) || "";
}

function reprocessCredentials(asset) {
  const config = asset.processor_config || {};
  let videoApiKey = apiKeyForProvider(config.video_provider);
  if (config.video_model_id === state.selectedVideoModelId) {
    videoApiKey ||= els.videoApiKeyInput?.value.trim() || "";
  }
  return {
    audio_api_key: "",
    video_api_key: videoApiKey,
    translation_api_key: "",
  };
}

async function reprocessSelectedAsset() {
  const asset = state.selectedAsset;
  if (!asset || !window.confirm(t("upload.reprocessConfirm"))) return;
  const button = document.querySelector("#reprocessAssetButton");
  if (button) {
    button.disabled = true;
    button.textContent = t("upload.reprocessing");
  }
  try {
    await api(`/api/nas-assets/${asset.id}/reprocess`, {
      method: "POST",
      body: JSON.stringify(reprocessCredentials(asset)),
    });
    await loadNasAssets();
    await loadMeetings();
    showToast(t("upload.reprocessQueued"), t("upload.assetsTitle"));
  } finally {
    if (button?.isConnected) {
      button.disabled = false;
      button.textContent = t("upload.reprocess");
    }
  }
}

async function convertSelectedAssetToTraditional() {
  const asset = state.selectedAsset;
  if (!asset || !window.confirm(t("upload.openccConfirm"))) return;
  const button = document.querySelector("#openccAssetButton");
  if (button) {
    button.disabled = true;
    button.textContent = t("upload.openccRunning");
  }
  try {
    const result = await api(`/api/nas-assets/${asset.id}/opencc-traditional`, {
      method: "POST",
      body: "{}",
    });
    await loadNasAssets();
    await loadMeetings();
    showToast(result.message, t("upload.openccTraditional"));
  } finally {
    if (button?.isConnected) {
      button.disabled = false;
      button.textContent = t("upload.openccTraditional");
    }
  }
}

function renderNasAssetDetail() {
  const asset = state.selectedAsset;
  if (!asset) {
    els.nasAssetDetail.hidden = true;
    els.nasAssetDetail.innerHTML = "";
    return;
  }

  els.nasAssetDetail.hidden = false;
  const chunks = asset.chunks || [];
  const canAsk = ["audio", "video", "pdf", "docx", "image"].includes(asset.category) && asset.chunk_count > 0;
  const isMedia = ["audio", "video"].includes(asset.category);
  const canReprocess = ["audio", "video", "pdf", "docx", "image"].includes(asset.category);
  const mediaBusy = asset.status === "processing";
  els.nasAssetDetail.innerHTML = `
    <div class="asset-detail-header">
      <div>
        <p class="eyebrow">${escapeHtml(asset.category.toUpperCase())} · ${escapeHtml(asset.analyzer || "-")}</p>
        <h3>${escapeHtml(asset.title)}</h3>
      </div>
      <span class="badge ${escapeHtml(asset.status)}">${statusLabel(asset.status)}</span>
    </div>
    ${canReprocess ? `
      <div class="asset-detail-actions">
        <button id="reprocessAssetButton" class="secondary-button" type="button" ${mediaBusy ? "disabled" : ""}>${escapeHtml(t("upload.reprocess"))}</button>
        ${isMedia ? `<button id="openccAssetButton" class="opencc-button" type="button" ${mediaBusy ? "disabled" : ""}>${escapeHtml(t("upload.openccTraditional"))}</button>` : ""}
      </div>
    ` : ""}
    <div class="asset-meta-grid">
      ${assetMeta(t("upload.owner"), asset.owner_username || `#${asset.user_id}`)}
      ${assetMeta(t("upload.filename"), asset.original_filename)}
      ${assetMeta(t("upload.fileSize"), formatBytes(asset.file_size))}
      ${assetMeta(t("upload.chunkCount"), asset.chunk_count)}
      ${asset.category === "audio" ? assetMeta(t("upload.selectedAsr"), selectedAsrLabel(asset)) : ""}
      ${asset.category === "audio" && asset.processor_config?.translation_enabled ? assetMeta(t("upload.selectedTranslation"), selectedTranslationLabel(asset)) : ""}
      ${asset.category === "video" ? assetMeta(t("upload.selectedVideo"), selectedVideoLabel(asset)) : ""}
    </div>
    ${asset.category === "audio" ? renderAudioPlayback(asset) : ""}
    ${asset.category === "video" ? renderVideoPlayback(asset) : ""}
    ${asset.category === "audio" ? renderAssetTranscript(asset) : ""}
    <section class="asset-summary">
      <strong>${escapeHtml(t("upload.summary"))}</strong>
      <p>${escapeHtml(asset.summary || asset.error_message || processingText(asset.status, asset.error_message))}</p>
    </section>
    ${renderAiAnalysisHistory(asset.ai_analyses || [])}
    ${renderAssetProcessTimeline(asset, chunks)}
    ${chunks.length ? renderRagChunks(chunks) : ""}
    ${canAsk ? renderDocumentAskPanel() : `<div class="empty-state compact">${t("upload.noRag")}</div>`}
  `;
  scheduleAssetSegmentPolling();
}

function renderAssetTranscript(asset) {
  const transcript = String(asset.transcript || "").trim();
  return `
    <section id="assetTranscript" class="asset-transcript-section">
      <div class="asset-transcript-heading">
        <strong>${escapeHtml(t("upload.transcriptTitle"))}</strong>
        ${transcript ? `<div class="transcript-heading-actions">
          <span>${escapeHtml(t("upload.transcriptMeta", {
            chunks: Number(asset.transcript_chunk_count || 0),
            characters: transcript.length.toLocaleString(state.lang),
          }))}</span>
          ${renderMediaDownloadButton(asset.transcript_download_url, t("upload.downloadTranscript"))}
        </div>` : ""}
      </div>
      <div class="transcript-box ${transcript ? "" : "is-empty"}">${escapeHtml(transcript || t("upload.transcriptEmpty"))}</div>
    </section>
  `;
}

function renderAiAnalysisHistory(analyses) {
  if (!analyses.length) return "";
  return `
    <section class="ai-analysis-history">
      <div>
        <strong>${escapeHtml(t("upload.analysisHistoryTitle"))}</strong>
        <p>${escapeHtml(t("upload.analysisHistoryCopy"))}</p>
      </div>
      <div class="ai-analysis-list">
        ${analyses.map((analysis) => `
          <article>
            <div class="chunk-source-line">
              <b>${escapeHtml(analysis.provider)} · ${escapeHtml(analysis.model_name)}</b>
              <span>${escapeHtml(formatDate(analysis.created_at))}</span>
            </div>
            <strong>${escapeHtml(t("upload.analysisQuestion"))}</strong>
            <p>${escapeHtml(analysis.question)}</p>
            <pre>${escapeHtml(analysis.answer)}</pre>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function assetMeta(label, value) {
  return `<span><b>${escapeHtml(label)}</b>${escapeHtml(value ?? "-")}</span>`;
}

function selectedAsrLabel(asset) {
  const config = asset.processor_config || {};
  if (!config.asr_model) return asset.analyzer || "-";
  return `${config.asr_provider || "ASR"} · ${config.asr_model}`;
}

function selectedVideoLabel(asset) {
  const config = asset.processor_config || {};
  if (!config.video_model) return asset.analyzer || "-";
  return `${config.video_provider || "Video"} · ${config.video_model}`;
}

function selectedTranslationLabel(asset) {
  const config = asset.processor_config || {};
  return `${config.translation_provider || "LLM"} · ${config.translation_model || "-"} → ${translationTargetLabel(config.translation_target)}`;
}

function renderAudioPlayback(asset) {
  const segments = asset.audio_segments || [];
  return `
    <section class="audio-playback-panel">
      <div class="audio-playback-heading">
        <div>
          <strong>${escapeHtml(t("upload.sourceAudioTitle"))}</strong>
          <p>${escapeHtml(t("upload.sourceAudioCopy"))}</p>
        </div>
        <div class="media-heading-actions">
          <span>${escapeHtml(formatBytes(asset.file_size))}</span>
          ${renderMediaDownloadButton(asset.download_url, t("upload.downloadSource"))}
        </div>
      </div>
      <audio class="asset-audio-player" controls preload="metadata" src="${escapeHtml(asset.audio_url)}"></audio>
      <div class="audio-segment-heading">
        <strong>${escapeHtml(t("upload.audioSegmentsTitle"))}</strong>
        <p>${escapeHtml(t("upload.audioSegmentsCopy"))}</p>
      </div>
      ${segments.length ? `
        <div class="audio-segment-list">
          ${segments.map((segment) => {
            const start = Number(segment.start_seconds || 0);
            const duration = Number(segment.duration_seconds || 0);
            return `
              <div class="audio-segment-row" data-audio-segment-index="${Number(segment.index)}">
                <div>
                  <strong>${escapeHtml(segment.is_source ? t("upload.wholeFile") : t("upload.audioSegment", { number: Number(segment.index) + 1 }))}</strong>
                  <span>${duration > 0 ? `${escapeHtml(t("upload.audioSegmentRange", {
                    start: formatMediaTime(start),
                    end: formatMediaTime(start + duration),
                  }))} · ` : ""}${escapeHtml(formatBytes(segment.file_size))}</span>
                </div>
                <div class="segment-media-control">
                  <audio controls preload="metadata" src="${escapeHtml(segment.audio_url)}"></audio>
                  <div class="segment-action-row">
                    ${renderMediaDownloadButton(segment.download_url, t("upload.downloadSegment"))}
                    ${renderSegmentTranscriptionButton(segment)}
                  </div>
                  <div class="segment-transcription-slot" data-segment-transcription-slot="${Number(segment.index)}">
                    ${renderSegmentTranscription(segment)}
                  </div>
                </div>
              </div>
            `;
          }).join("")}
        </div>
      ` : `<p class="audio-segment-empty">${escapeHtml(t("upload.noAudioSegments"))}</p>`}
    </section>
  `;
}

function renderVideoPlayback(asset) {
  const segments = asset.video_segments || [];
  return `
    <section class="video-playback-panel">
      <div class="audio-playback-heading">
        <div>
          <strong>${escapeHtml(t("upload.sourceVideoTitle"))}</strong>
          <p>${escapeHtml(t("upload.sourceVideoCopy"))}</p>
        </div>
        <div class="media-heading-actions">
          <span>${escapeHtml(formatBytes(asset.file_size))}</span>
          ${renderMediaDownloadButton(asset.download_url, t("upload.downloadSource"))}
        </div>
      </div>
      <video class="asset-video-player" controls preload="metadata" playsinline src="${escapeHtml(asset.video_url)}"></video>
      <div class="audio-segment-heading">
        <strong>${escapeHtml(t("upload.videoSegmentsTitle"))}</strong>
        <p>${escapeHtml(t("upload.videoSegmentsCopy"))}</p>
      </div>
      <div class="audio-segment-list">
        ${segments.map((segment) => {
          const start = Number(segment.start_seconds || 0);
          const duration = Number(segment.duration_seconds || 0);
          return `
            <div class="audio-segment-row media-download-row">
              <div>
                <strong>${escapeHtml(segment.is_source ? t("upload.wholeFile") : t("upload.audioSegment", { number: Number(segment.index) + 1 }))}</strong>
                <span>${duration > 0 ? `${escapeHtml(t("upload.audioSegmentRange", {
                  start: formatMediaTime(start),
                  end: formatMediaTime(start + duration),
                }))} · ` : ""}${escapeHtml(formatBytes(segment.file_size))}</span>
              </div>
              ${renderMediaDownloadButton(segment.download_url, t("upload.downloadSegment"))}
            </div>
          `;
        }).join("")}
      </div>
    </section>
  `;
}

function renderSegmentTranscriptionButton(segment) {
  const status = segment.transcription?.status || "";
  const active = ["queued", "processing"].includes(status);
  const label = active
    ? (status === "queued" ? t("upload.segmentTranscriptionQueued") : t("upload.segmentTranscriptionProcessing"))
    : (status === "completed" ? t("upload.retranscribeSegment") : t("upload.transcribeSegment"));
  return `<button class="segment-transcribe-button" type="button" data-transcribe-segment="${Number(segment.index)}" ${active ? "disabled" : ""}>${escapeHtml(label)}</button>`;
}

function renderSegmentTranscription(segment) {
  const result = segment.transcription || {};
  if (!result.status) return "";
  const progress = Math.max(0, Math.min(100, Number(result.progress || 0)));
  const statusLabels = {
    queued: t("upload.segmentTranscriptionQueued"),
    processing: t("upload.segmentTranscriptionProcessing"),
    completed: t("upload.segmentTranscriptionCompleted"),
    failed: t("upload.segmentTranscriptionFailed"),
  };
  const active = ["queued", "processing"].includes(result.status);
  return `
    <div class="segment-transcription-status ${escapeHtml(result.status)}">
      <div>
        <strong>${escapeHtml(statusLabels[result.status] || result.status)}</strong>
        <div class="segment-transcription-heading-actions">
          <span>${escapeHtml(result.model_name || result.model_id || "")}</span>
          ${result.download_url ? renderMediaDownloadButton(result.download_url, t("upload.downloadSegmentTranscript")) : ""}
        </div>
      </div>
      <div class="segment-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}">
        <span class="${active ? "active" : ""}" style="width:${progress}%"></span>
      </div>
      ${result.transcript ? `<details class="segment-transcript"><summary>${escapeHtml(t("upload.segmentTranscript"))}</summary><p>${escapeHtml(result.transcript)}</p></details>` : ""}
      ${result.error_message ? `<p class="segment-transcription-error">${escapeHtml(result.error_message)}</p>` : ""}
    </div>
  `;
}

async function transcribeAudioSegment(segmentIndex) {
  const asset = state.selectedAsset;
  if (!asset || asset.category !== "audio") return;
  const credentials = reprocessCredentials(asset);
  await api(`/api/nas-assets/${asset.id}/audio-segments/${segmentIndex}/transcribe`, {
    method: "POST",
    body: JSON.stringify({
      model_id: asset.processor_config?.asr_model_id || "",
      api_key: credentials.audio_api_key || "",
    }),
  });
  showToast(t("upload.segmentTranscriptionQueuedToast"), t("upload.audioSegmentsTitle"));
  await refreshAssetSegmentTranscriptions();
}

async function refreshAssetSegmentTranscriptions() {
  if (!state.selectedAssetId) return;
  const selectedId = state.selectedAssetId;
  const asset = await api(`/api/nas-assets/${selectedId}`);
  if (state.selectedAssetId !== selectedId) return;
  state.selectedAsset = asset;
  (asset.audio_segments || []).forEach((segment) => {
    const row = els.nasAssetDetail.querySelector(`[data-audio-segment-index="${Number(segment.index)}"]`);
    if (!row) return;
    const slot = row.querySelector("[data-segment-transcription-slot]");
    const button = row.querySelector("[data-transcribe-segment]");
    if (slot) slot.innerHTML = renderSegmentTranscription(segment);
    if (button) button.outerHTML = renderSegmentTranscriptionButton(segment);
  });
  scheduleAssetSegmentPolling();
}

function scheduleAssetSegmentPolling() {
  if (state.assetSegmentPollTimer) window.clearTimeout(state.assetSegmentPollTimer);
  state.assetSegmentPollTimer = null;
  const active = (state.selectedAsset?.audio_segments || []).some((segment) =>
    ["queued", "processing"].includes(segment.transcription?.status)
  );
  if (!active || currentViewName() !== "upload") return;
  state.assetSegmentPollTimer = window.setTimeout(() => {
    refreshAssetSegmentTranscriptions().catch(() => {});
  }, 2000);
}

function renderMediaDownloadButton(url, label) {
  if (!url) return "";
  return `<a class="media-download-button" href="${escapeHtml(url)}" download>${escapeHtml(label)}</a>`;
}

function formatMediaTime(seconds) {
  const value = Math.max(0, Math.round(Number(seconds) || 0));
  const hours = Math.floor(value / 3600);
  const minutes = Math.floor((value % 3600) / 60);
  const remainder = value % 60;
  return hours
    ? `${hours}:${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`
    : `${minutes}:${String(remainder).padStart(2, "0")}`;
}

function asrModelsForMode(mode) {
  return (state.asrCatalog?.models || []).filter((model) => {
    return mode === "cloud" ? model.id.startsWith("cloud:") : model.id.startsWith("local:");
  });
}

function renderRecordingAsrControls() {
  if (!els.recordAsrModeSelect || !els.recordAsrModelSelect) return;
  els.recordAsrModeSelect.value = state.selectedRecordAsrMode;
  const models = asrModelsForMode(state.selectedRecordAsrMode);
  els.recordAsrModelSelect.innerHTML = models
    .map((model) => `<option value="${escapeHtml(model.id)}">${escapeHtml(model.name)}</option>`)
    .join("");
  if (!models.some((model) => model.id === state.selectedRecordAsrModelId)) {
    state.selectedRecordAsrModelId = models[0]?.id || "";
  }
  els.recordAsrModelSelect.value = state.selectedRecordAsrModelId;
  const selected = models.find((model) => model.id === state.selectedRecordAsrModelId);
  els.recordAsrKeyField.hidden = true;
  if (selected) els.recordAsrKeyLabel.textContent = selected.api_key_label || t("upload.asrKeyLabel");
  renderAsrRecommendation(els.recordAsrRecommendation, selected);
  renderSystemAsrSetting();
}

function renderAsrControls() {
  if (!els.audioAsrModeSelect || !els.audioAsrModelSelect) return;
  els.audioAsrModeSelect.value = state.selectedAsrMode;
  const models = asrModelsForMode(state.selectedAsrMode);
  els.audioAsrModelSelect.innerHTML = models
    .map((model) => `<option value="${escapeHtml(model.id)}">${escapeHtml(model.name)}</option>`)
    .join("");
  if (!models.some((model) => model.id === state.selectedAsrModelId)) {
    state.selectedAsrModelId = models[0]?.id || "";
  }
  els.audioAsrModelSelect.value = state.selectedAsrModelId;
  const selected = models.find((model) => model.id === state.selectedAsrModelId);
  els.audioAsrKeyField.hidden = true;
  if (selected) els.audioAsrKeyLabel.textContent = selected.api_key_label || t("upload.asrKeyLabel");
  renderAsrRecommendation(els.audioAsrRecommendation, selected);
}

function renderSystemAsrSetting() {
  const current = state.currentAsrModel;
  const label = current ? `${current.provider} · ${current.name}` : "-";
  if (els.currentSystemAsrName) els.currentSystemAsrName.textContent = label;
  if (els.recordCurrentAsrName) els.recordCurrentAsrName.textContent = label;
  if (els.uploadCurrentAsrName) els.uploadCurrentAsrName.textContent = label;
  if (els.currentSystemAsrMeta) {
    const updatedBy = state.asrCatalog?.current_model_updated_by;
    const updatedAt = state.asrCatalog?.current_model_updated_at;
    els.currentSystemAsrMeta.textContent = updatedBy && updatedAt
      ? t("aiwork.systemModelUpdated", { user: updatedBy, time: formatDate(updatedAt) })
      : t("aiwork.systemModelDefault");
  }
  if (els.setCurrentAsrButton) {
    els.setCurrentAsrButton.hidden = state.user?.role !== "admin";
    els.setCurrentAsrButton.disabled = !state.selectedRecordAsrModelId || state.selectedRecordAsrModelId === state.currentAsrId;
    els.setCurrentAsrButton.textContent = t("models.setSystemAsr");
  }
}

async function saveCurrentAsrModel() {
  if (!state.selectedRecordAsrModelId) return;
  els.setCurrentAsrButton.disabled = true;
  els.setCurrentAsrButton.textContent = t("models.settingSystemAsr");
  try {
    await api("/api/admin/asr/current-model", {
      method: "PUT",
      body: JSON.stringify({ model_id: state.selectedRecordAsrModelId }),
    });
    showToast(t("models.systemAsrSaved"), t("models.systemAsrTitle"));
    await loadAsrCatalog();
  } finally {
    renderSystemAsrSetting();
  }
}

function renderTranslationControls(surface) {
  const isRecord = surface === "record";
  const toggle = isRecord ? els.recordTranslationToggle : els.audioTranslationToggle;
  const controls = isRecord ? els.recordTranslationControls : els.audioTranslationControls;
  const targetSelect = isRecord ? els.recordTranslationTargetSelect : els.audioTranslationTargetSelect;
  const modeSelect = isRecord ? els.recordTranslationModeSelect : els.audioTranslationModeSelect;
  const modelSelect = isRecord ? els.recordTranslationModelSelect : els.audioTranslationModelSelect;
  const keyField = isRecord ? els.recordTranslationKeyField : els.audioTranslationKeyField;
  const recommendation = isRecord ? els.recordTranslationRecommendation : els.audioTranslationRecommendation;
  if (!toggle || !controls || !targetSelect || !modeSelect || !modelSelect) return;

  const enabled = isRecord ? state.recordTranslationEnabled : state.audioTranslationEnabled;
  const mode = isRecord ? state.recordTranslationMode : state.audioTranslationMode;
  const selectedId = isRecord ? state.recordTranslationModelId : state.audioTranslationModelId;
  const target = isRecord ? state.recordTranslationTarget : state.audioTranslationTarget;
  toggle.checked = enabled;
  controls.hidden = !enabled;
  targetSelect.value = target;
  modeSelect.value = mode;
  modeSelect.disabled = true;
  modelSelect.disabled = true;

  const models = llmModelsForMode(mode);
  let currentId = selectedId;
  if (!models.some((model) => model.id === currentId)) {
    currentId = defaultLlmModelForMode(mode)?.id || "";
    if (isRecord) state.recordTranslationModelId = currentId;
    else state.audioTranslationModelId = currentId;
  }
  modelSelect.innerHTML = models
    .map((model) => `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</option>`)
    .join("");
  modelSelect.value = currentId;
  const selected = models.find((model) => model.id === currentId);
  keyField.hidden = true;
  renderTranslationRecommendation(recommendation, selected, target);
}

function renderLinePushControls() {
  if (!els.recordLinePushToggle || !els.recordLinePushControls) return;
  const hasGroups = state.lineGroups.length > 0;
  if (!hasGroups) state.recordLinePushEnabled = false;
  els.recordLinePushToggle.checked = state.recordLinePushEnabled;
  els.recordLinePushToggle.disabled = !hasGroups;
  els.recordLinePushControls.hidden = !state.recordLinePushEnabled;
  els.recordLineGroupSelect.innerHTML = hasGroups
    ? state.lineGroups.map((group) => (
      `<option value="${escapeHtml(group.id)}">${escapeHtml(group.name)} · ${escapeHtml(t("record.lineMessages", { count: group.message_count }))}</option>`
    )).join("")
    : `<option value="">${escapeHtml(t("record.lineNoGroups"))}</option>`;
  els.recordLineGroupSelect.value = state.recordLineGroupId;
  els.recordLineFullTranscriptToggle.checked = state.recordLineFullTranscript;
  els.recordLineStatus.textContent = hasGroups
    ? t(state.recordLineFullTranscript ? "record.lineFullWarning" : "record.lineSummaryOnly")
    : t("record.lineUnavailable");
}

function renderTranslationRecommendation(target, model, language) {
  if (!target || !model) {
    if (target) target.innerHTML = "";
    return;
  }
  const local = model.execution === "local";
  target.innerHTML = `
    <div>
      <strong>${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</strong>
      <span>${escapeHtml(translationTargetLabel(language))}</span>
    </div>
    <p>${escapeHtml(local ? t("record.translationLocalHint") : t("record.translationCloudHint", { provider: model.provider }))}</p>
  `;
}

function translationTargetLabel(target) {
  const keys = {
    "zh-Hant": "zhHant",
    en: "en",
    "zh-Hans": "zhHans",
    ja: "ja",
    ko: "ko",
    es: "es",
    fr: "fr",
    de: "de",
  };
  return t(`record.languages.${keys[target] || "en"}`);
}

function validateTranslationSelection(surface) {
  const isRecord = surface === "record";
  const enabled = isRecord ? state.recordTranslationEnabled : state.audioTranslationEnabled;
  if (!enabled) return;
  const modelId = isRecord ? state.recordTranslationModelId : state.audioTranslationModelId;
  const model = (state.llmCatalog?.models || []).find((item) => item.id === modelId);
  if (!model) throw new Error(t("record.translationModelRequired"));
  if (model.free_tier?.requires_api_key_for_real_call && !model.server_key_configured) {
    throw new Error(t("record.translationKeyRequired", { model: model.name }));
  }
}

function renderAsrRecommendation(target, model) {
  if (!target) return;
  if (!model) {
    target.innerHTML = "";
    return;
  }
  const localStatus = (state.localModels?.models || []).find((item) => item.id === model.id);
  let readiness = t("record.asrCloud");
  let readinessClass = "cloud";
  if (model.id.startsWith("local:")) {
    if (localStatus?.status === "downloading" || localStatus?.status === "cancelling") {
      readiness = t("record.asrDownloading", { progress: String(localStatus.progress || 0) });
      readinessClass = "downloading";
    } else if (localStatus?.installed) {
      readiness = t("record.asrReady");
      readinessClass = "ready";
    } else {
      readiness = t("record.asrNotReady");
      readinessClass = "not-ready";
    }
  }
  const recommendation = state.lang === "en" ? model.recommendation_en : model.recommendation;
  const languages = state.lang === "en" ? model.languages_en : model.languages;
  const bestFor = state.lang === "en" ? model.recommended_for_en : model.recommended_for;
  target.innerHTML = `
    <div class="asr-recommendation-head">
      <strong>${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</strong>
      <span class="asr-readiness ${readinessClass}">${escapeHtml(readiness)}</span>
    </div>
    <p>${escapeHtml(recommendation || "")}</p>
    <div class="asr-recommendation-meta">
      <span><b>${escapeHtml(t("record.asrLanguages"))}</b>${escapeHtml(languages || "-")}</span>
      <span><b>${escapeHtml(t("record.asrBestFor"))}</b>${escapeHtml(bestFor || "-")}</span>
    </div>
  `;
}

function renderVideoControls() {
  if (!els.videoModelModeSelect || !els.videoModelSelect) return;
  els.videoModelModeSelect.value = state.selectedVideoMode;
  const models = (state.videoCatalog?.models || []).filter((model) => {
    return state.selectedVideoMode === "cloud" ? model.id.startsWith("cloud:") : model.id.startsWith("local:");
  });
  els.videoModelSelect.innerHTML = models
    .map((model) => `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</option>`)
    .join("");
  if (!models.some((model) => model.id === state.selectedVideoModelId)) {
    state.selectedVideoModelId = models[0]?.id || "";
  }
  els.videoModelSelect.value = state.selectedVideoModelId;
  const selected = models.find((model) => model.id === state.selectedVideoModelId);
  els.videoApiKeyField.hidden = !selected?.requires_api_key;
}

function renderLocalModelManager() {
  if (!els.localModelList) return;
  const models = state.localModels?.models || [];
  if (!models.length) {
    els.localModelList.innerHTML = `<div class="empty-state compact">${escapeHtml(t("upload.emptyList"))}</div>`;
    return;
  }

  els.localModelList.innerHTML = models
    .map((item) => {
      const model = item.model || {};
      const progress = Number(item.progress || 0);
      const statusText = localModelStatusLabel(item.status);
      return `
        <article class="local-model-row">
          <div class="local-model-main">
            <div class="local-model-title-line">
              <strong>${escapeHtml(model.provider || "Local")} · ${escapeHtml(model.name || item.id)}</strong>
              <div class="model-manager-actions">
                ${model.custom_model ? `<span class="custom-badge">${escapeHtml(t("models.customBadge"))}</span>` : ""}
                <span class="badge ${escapeHtml(item.status)}">${escapeHtml(statusText)}</span>
              </div>
            </div>
            <div class="model-progress-track" aria-label="${escapeHtml(t("upload.modelProgress"))}">
              <span style="width: ${Math.max(0, Math.min(100, progress))}%"></span>
            </div>
            <div class="local-model-meta">
              <span>${escapeHtml(t("upload.modelSize"))}: ${escapeHtml(formatModelBytes(item.downloaded_bytes, item.total_bytes))}</span>
              <span>${escapeHtml(item.runtime_installed ? t("upload.runtimeReady") : t("upload.runtimeMissing"))}</span>
              ${item.path ? `<span>${escapeHtml(t("upload.modelPath"))}: ${escapeHtml(item.path)}</span>` : ""}
              ${model.custom_model ? `<span>${escapeHtml(localModelStatusLabel(item.validation_status))}</span>` : ""}
              ${item.setup_hint || item.setup_hint_key ? `<span>${escapeHtml(t("upload.modelSetupHint"))}: ${escapeHtml(localModelSetupHint(item))}</span>` : ""}
              ${item.error ? `<span class="error-line">${escapeHtml(item.error)}</span>` : ""}
              ${item.validation_error && item.validation_error !== item.error ? `<span class="error-line">${escapeHtml(item.validation_error)}</span>` : ""}
            </div>
          </div>
          <div class="local-model-actions">
            ${renderLocalModelActions(item)}
          </div>
        </article>
      `;
    })
    .join("");
}

function localModelStatusLabel(status) {
  const labels = translateRaw("upload.modelStatus") || {};
  return labels[status] || status || "-";
}

function localModelSetupHint(item) {
  const hints = translateRaw("upload.setupHints") || {};
  return hints[item.setup_hint_key] || item.setup_hint || "";
}

function localModelAction(item) {
  if (item.status === "downloading" || item.status === "cancelling") return "cancel";
  if (!item.downloadable) return "";
  if (item.installed) return "installed";
  if (item.status === "partial" || item.status === "failed" || item.status === "cancelled") return "retry";
  return "download";
}

function renderLocalModelActionButton(item, action) {
  if (action === "cancel") {
    return `<button class="secondary-button compact-button" type="button" data-model-action="cancel" data-model-id="${escapeHtml(item.id)}">${escapeHtml(t("upload.cancelDownload"))}</button>`;
  }
  if (action === "retry") {
    return `<button class="primary-button compact-button" type="button" data-model-action="retry" data-model-id="${escapeHtml(item.id)}">${escapeHtml(t("upload.retryDownload"))}</button>`;
  }
  if (action === "download") {
    return `<button class="primary-button compact-button" type="button" data-model-action="download" data-model-id="${escapeHtml(item.id)}">${escapeHtml(t("upload.downloadModel"))}</button>`;
  }
  if (action === "installed") {
    return `<button class="secondary-button compact-button" type="button" disabled>${escapeHtml(t("upload.installedModel"))}</button>`;
  }
  return `<button class="secondary-button compact-button" type="button" disabled>${escapeHtml(t("upload.noPanelDownload"))}</button>`;
}

function renderLocalModelActions(item) {
  const custom = Boolean(item.model?.custom_model);
  const canManage = state.user?.role === "admin";
  const action = localModelAction(item);
  const buttons = [];
  if (action || !custom) buttons.push(renderLocalModelActionButton(item, action));
  if (custom && canManage && item.status !== "downloading" && item.status !== "cancelling") {
    buttons.push(`<button class="secondary-button compact-button" type="button" data-model-action="test" data-model-id="${escapeHtml(item.id)}">${escapeHtml(t("models.test"))}</button>`);
    buttons.push(`<button class="danger-button compact-button" type="button" data-model-action="remove" data-model-id="${escapeHtml(item.id)}">${escapeHtml(t("models.remove"))}</button>`);
  }
  return buttons.join("");
}

function formatModelBytes(downloaded, total) {
  const left = formatBytes(downloaded || 0);
  return total ? `${left} / ${formatBytes(total)}` : left;
}

function scheduleLocalModelPolling() {
  if (state.localModelPollTimer) {
    clearInterval(state.localModelPollTimer);
    state.localModelPollTimer = null;
  }
  const active = (state.localModels?.models || []).some((item) => item.status === "downloading" || item.status === "cancelling");
  if (active) {
    state.localModelPollTimer = window.setInterval(() => {
      loadLocalModels({ background: true }).catch(() => {});
    }, 1800);
  }
}

async function runLocalModelAction(modelId, action) {
  if (action === "test") {
    await testCustomModel(modelId);
    return;
  }
  if (action === "remove") {
    await removeCustomModel(modelId);
    return;
  }
  const endpoint = action === "retry" ? "retry" : action;
  try {
    await api(`/api/local-models/${encodeURIComponent(modelId)}/${endpoint}`, {
      method: "POST",
      body: "{}",
    });
    await loadLocalModels();
  } catch (error) {
    showToast(error.message, t("upload.modelActionFailed"));
  }
}

function openCustomModelModal() {
  els.customModelForm.reset();
  els.customModelType.value = "whisper_cpp";
  els.customModelApiBase.value = "http://127.0.0.1:8080";
  els.customModelContext.value = "4096";
  els.customModelError.textContent = "";
  renderCustomModelFields();
  els.customModelModal.hidden = false;
  els.customModelName.focus();
}

function closeCustomModelModal() {
  els.customModelModal.hidden = true;
  els.customModelError.textContent = "";
}

function renderCustomModelFields() {
  const isEndpoint = els.customModelType.value === "openai_compatible_llm";
  els.customFileModelFields.hidden = isEndpoint;
  els.customEndpointModelFields.hidden = !isEndpoint;
  els.customModelFile.required = !isEndpoint;
  els.customModelApiBase.required = isEndpoint;
  els.customModelAlias.required = isEndpoint;
  if (!isEndpoint) {
    els.customModelFile.placeholder = els.customModelType.value === "yolo" ? "custom-yolo.pt" : t("models.filePlaceholder");
  }
}

async function createCustomModel(event) {
  event.preventDefault();
  els.customModelError.textContent = "";
  const isEndpoint = els.customModelType.value === "openai_compatible_llm";
  const payload = {
    model_type: els.customModelType.value,
    name: els.customModelName.value.trim(),
    slug: els.customModelSlug.value.trim(),
    recommendation: els.customModelRecommendation.value.trim(),
  };
  if (isEndpoint) {
    payload.api_base = els.customModelApiBase.value.trim();
    payload.model_alias = els.customModelAlias.value.trim();
    payload.max_input_tokens = Number(els.customModelContext.value);
    payload.supports_tokenize = els.customModelSupportsTokenize.checked;
  } else {
    payload.model_file = els.customModelFile.value.trim();
    payload.download_url = els.customModelDownloadUrl.value.trim();
    payload.expected_size_mb = els.customModelExpectedSize.value ? Number(els.customModelExpectedSize.value) : null;
    payload.sha256 = els.customModelSha256.value.trim();
  }
  try {
    await api("/api/admin/models", { method: "POST", body: JSON.stringify(payload) });
    closeCustomModelModal();
    await loadLocalModels();
    showToast(t("models.saved"), t("models.title"));
  } catch (error) {
    els.customModelError.textContent = error.message;
  }
}

async function testCustomModel(modelId) {
  try {
    const result = await api(`/api/admin/models/${encodeURIComponent(modelId)}/test`, { method: "POST", body: "{}" });
    await Promise.all([loadLocalModels(), loadAsrCatalog(), loadVideoCatalog(), loadLlmCatalog()]);
    showToast(result.ok ? t("models.testReady") : t("models.testIncomplete"), t("models.title"));
  } catch (error) {
    await loadLocalModels();
    showToast(error.message, t("models.actionFailed"));
  }
}

async function removeCustomModel(modelId) {
  if (!window.confirm(t("models.removeConfirm"))) return;
  try {
    await api(`/api/admin/models/${encodeURIComponent(modelId)}`, { method: "DELETE", body: "{}" });
    await Promise.all([loadLocalModels(), loadAsrCatalog(), loadVideoCatalog(), loadLlmCatalog()]);
    showToast(t("models.removed"), t("models.title"));
  } catch (error) {
    showToast(error.message, t("models.actionFailed"));
  }
}

function renderAssetProcessTimeline(asset, chunks) {
  const steps = assetProcessSteps(asset, chunks);
  return `
    <section class="asset-process-panel">
      <div>
        <strong>${escapeHtml(t("upload.processTitle"))}</strong>
        <p>${escapeHtml(t("upload.processCopy"))}</p>
      </div>
      <div class="process-timeline">
        ${steps
          .map(
            (step) => `
              <article class="process-step ${escapeHtml(step.state)}">
                <div class="process-step-head">
                  <span>${escapeHtml(step.badge)}</span>
                  <b>${escapeHtml(step.title)}</b>
                </div>
                <strong>${escapeHtml(step.engine)}</strong>
                <p>${escapeHtml(step.copy)}</p>
              </article>
            `
          )
          .join("")}
      </div>
    </section>
  `;
}

function assetProcessSteps(asset, chunks) {
  const timeline = translateRaw("upload.timeline") || {};
  const done = t("upload.stepDone");
  const active = t("upload.stepActive");
  const pending = t("upload.stepPending");
  const blocked = t("upload.stepBlocked");
  const skipped = t("upload.stepSkipped");
  const configured = t("upload.stepConfigured");
  const completed = asset.status === "completed";
  const failed = asset.status === "failed";
  const processing = asset.status === "processing";
  const needsModel = asset.status === "needs_model";
  const chunkTypes = new Set(chunks.map((chunk) => chunk.chunk_type).filter(Boolean));
  const hasTextLayer = chunkTypes.has("text_layer");
  const hasOcr = chunkTypes.has("image_ocr");
  const baseSteps = [
    step(timeline.intakeTitle, timeline.intakeEngine, timeline.intakeCopy, "done", done),
    step(timeline.archiveTitle, timeline.archiveEngine, timeline.archiveCopy, completed || failed || needsModel ? "done" : "active", completed || failed || needsModel ? done : active),
  ];

  if (asset.category === "pdf") {
    return [
      ...baseSteps,
      step(timeline.pdfRenderTitle, timeline.pdfRenderEngine, timeline.pdfRenderCopy, completed || failed ? "done" : "active", completed || failed ? done : active),
      step(timeline.pdfTextTitle, timeline.pdfTextEngine, timeline.pdfTextCopy, hasTextLayer ? "done" : hasOcr ? "skipped" : processing ? "active" : failed ? "done" : "pending", hasTextLayer ? done : hasOcr ? skipped : processing ? active : failed ? done : pending),
      step(timeline.ocrTitle, timeline.ocrEngine, timeline.ocrCopy, hasOcr ? "done" : hasTextLayer ? "skipped" : failed ? "blocked" : processing ? "active" : "pending", hasOcr ? done : hasTextLayer ? skipped : failed ? blocked : processing ? active : pending),
      step(timeline.ragTitle, timeline.ragEngine, timeline.ragCopy, asset.chunk_count > 0 ? "done" : failed ? "blocked" : "pending", asset.chunk_count > 0 ? done : failed ? blocked : pending),
      step(timeline.llmTitle, timeline.llmEngine, timeline.llmCopy, asset.chunk_count > 0 ? "pending" : "blocked", asset.chunk_count > 0 ? pending : blocked),
    ];
  }

  if (asset.category === "docx") {
    return [
      ...baseSteps,
      step(timeline.docxTitle, timeline.docxEngine, timeline.docxCopy, asset.chunk_count > 0 ? "done" : failed ? "blocked" : "active", asset.chunk_count > 0 ? done : failed ? blocked : active),
      step(timeline.ragTitle, timeline.ragEngine, timeline.ragCopy, asset.chunk_count > 0 ? "done" : failed ? "blocked" : "pending", asset.chunk_count > 0 ? done : failed ? blocked : pending),
      step(timeline.llmTitle, timeline.llmEngine, timeline.llmCopy, asset.chunk_count > 0 ? "pending" : "blocked", asset.chunk_count > 0 ? pending : blocked),
    ];
  }

  if (asset.category === "image") {
    return [
      ...baseSteps,
      step(timeline.imageDecodeTitle, timeline.imageDecodeEngine, timeline.imageDecodeCopy, failed ? "blocked" : "done", failed ? blocked : done),
      step(timeline.imageOcrTitle, timeline.imageOcrEngine, timeline.imageOcrCopy, hasOcr ? "done" : failed ? "blocked" : processing ? "active" : "pending", hasOcr ? done : failed ? blocked : processing ? active : pending),
      step(timeline.ragTitle, timeline.ragEngine, timeline.ragCopy, asset.chunk_count > 0 ? "done" : failed ? "blocked" : "pending", asset.chunk_count > 0 ? done : failed ? blocked : pending),
      step(timeline.llmTitle, timeline.llmEngine, timeline.llmCopy, asset.chunk_count > 0 ? "pending" : "blocked", asset.chunk_count > 0 ? pending : blocked),
    ];
  }

  if (asset.category === "audio") {
    const config = asset.processor_config || {};
    const asrEngine = config.asr_model ? `${config.asr_provider || "ASR"} · ${config.asr_model}` : timeline.audioEngine;
    const hasTranslation = chunkTypes.has("audio_translation");
    const translationEngine = config.translation_model
      ? `${config.translation_provider || "LLM"} · ${config.translation_model} → ${translationTargetLabel(config.translation_target)}`
      : timeline.translationEngine;
    const translationSteps = config.translation_enabled
      ? [step(timeline.translationTitle, translationEngine, timeline.translationCopy, hasTranslation ? "done" : completed || failed ? "blocked" : "pending", hasTranslation ? done : completed || failed ? blocked : pending)]
      : [];
    return [
      ...baseSteps,
      step(timeline.audioNormalizeTitle, timeline.audioNormalizeEngine, timeline.audioNormalizeCopy, "pending", configured),
      step(timeline.vadTitle, timeline.vadEngine, timeline.vadCopy, "pending", configured),
      step(timeline.audioTitle, asrEngine, timeline.audioCopy, needsModel ? "blocked" : processing ? "active" : completed ? "done" : failed ? "blocked" : "pending", needsModel ? blocked : processing ? active : completed ? done : failed ? blocked : pending),
      ...translationSteps,
      step(timeline.audioRagTitle, timeline.audioRagEngine, timeline.audioRagCopy, asset.chunk_count > 0 ? "done" : needsModel || failed ? "blocked" : "pending", asset.chunk_count > 0 ? done : needsModel || failed ? blocked : pending),
      step(timeline.llmTitle, timeline.llmEngine, timeline.llmCopy, asset.chunk_count > 0 ? "pending" : "blocked", asset.chunk_count > 0 ? pending : blocked),
    ];
  }

  if (asset.category === "video") {
    const config = asset.processor_config || {};
    const videoEngine = config.video_model ? `${config.video_provider || "Video"} · ${config.video_model}` : timeline.videoEngine;
    return [
      ...baseSteps,
      step(timeline.videoTitle, videoEngine, timeline.videoCopy, needsModel ? "blocked" : processing ? "active" : completed ? "done" : failed ? "blocked" : "pending", needsModel ? blocked : processing ? active : completed ? done : failed ? blocked : pending),
      step(timeline.videoRagTitle, timeline.videoRagEngine, timeline.videoRagCopy, asset.chunk_count > 0 ? "done" : needsModel || failed ? "blocked" : "pending", asset.chunk_count > 0 ? done : needsModel || failed ? blocked : pending),
      step(timeline.llmTitle, timeline.llmEngine, timeline.llmCopy, asset.chunk_count > 0 ? "pending" : "blocked", asset.chunk_count > 0 ? pending : blocked),
    ];
  }

  return baseSteps;
}

function step(title, engine, copy, state, badge) {
  return { title, engine, copy, state, badge };
}

function renderRagChunks(chunks) {
  return `
    <section class="rag-chunk-panel">
      <strong>${escapeHtml(t("upload.chunks"))}</strong>
      <div class="rag-chunk-list">
        ${chunks
          .map(
            (chunk) => `
              <article class="rag-chunk-card">
                <div class="chunk-source-line">
                  <b>#${escapeHtml(chunk.chunk_index)}</b>
                  ${chunk.page_number ? `<span>${escapeHtml(t("upload.page"))} ${escapeHtml(chunk.page_number)}</span>` : ""}
                  ${chunk.chunk_type ? `<span>${escapeHtml(t("upload.type"))} ${escapeHtml(chunk.chunk_type)}</span>` : ""}
                </div>
                <p>${escapeHtml(chunk.content.slice(0, 260))}</p>
                ${chunk.image_url ? `<img src="${escapeHtml(chunk.image_url)}" alt="${escapeHtml(t("upload.pagePreview"))}" loading="lazy" />` : ""}
              </article>
            `
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderDocumentAskPanel() {
  return `
    <section class="document-ask-panel">
      <div class="section-heading">
        <p class="eyebrow">${escapeHtml(t("upload.questionEyebrow"))}</p>
        <h3>${escapeHtml(t("upload.questionTitle"))}</h3>
        <p>${escapeHtml(t("upload.questionCopy"))}</p>
      </div>
      <div class="asset-system-model">
        <span>${escapeHtml(t("aiwork.systemModelLabel"))}</span>
        <strong>${escapeHtml(state.currentLlmModel?.provider || "-")} · ${escapeHtml(state.currentLlmModel?.name || "-")}</strong>
      </div>
      <label class="prompt-field">
        <span>${escapeHtml(t("aiwork.promptLabel"))}</span>
        <textarea id="assetQuestionInput" rows="4" placeholder="${escapeHtml(t("upload.questionPlaceholder"))}"></textarea>
      </label>
      <div class="button-row">
        <button id="askAssetButton" class="primary-button" type="button">${escapeHtml(t("upload.ask"))}</button>
      </div>
      <div id="assetAnswerBox" class="model-response-box" hidden></div>
    </section>
  `;
}

async function uploadNasAsset(event) {
  event.preventDefault();
  const file = els.nasFileInput.files[0];
  if (!file) {
    showToast(t("upload.uploadRequired"), t("toast.nasReceived"));
    return;
  }
  const isAudio = file.type.startsWith("audio/") || /\.(wav|mp3|m4a|webm|ogg|flac|aac)$/i.test(file.name);
  if (isAudio) {
    try {
      validateTranslationSelection("audio");
    } catch (error) {
      showToast(error.message, t("upload.translationTitle"));
      return;
    }
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", els.nasAssetTitleInput.value.trim());
  formData.append("audio_model_id", state.currentAsrId);
  formData.append("audio_api_key", "");
  formData.append("audio_translation_enabled", String(state.audioTranslationEnabled));
  formData.append("audio_translation_target", state.audioTranslationTarget);
  formData.append("audio_translation_model_id", state.audioTranslationModelId);
  formData.append("audio_translation_api_key", "");
  formData.append("video_model_id", state.selectedVideoModelId);
  formData.append("video_api_key", els.videoApiKeyInput.value.trim());
  els.nasUploadSubmit.disabled = true;
  setNasUploadProgress(0, true);
  let asset;
  try {
    asset = await uploadFormData("/api/nas-assets/upload", formData, (progress) => {
      setNasUploadProgress(progress, true);
    });
  } catch (error) {
    showToast(error.message || t("upload.uploadFailed"), t("toast.savedFailed"));
    setNasUploadProgress(0, false);
    els.nasUploadSubmit.disabled = false;
    return;
  }
  setNasUploadProgress(100, false);
  els.nasUploadSubmit.disabled = false;
  els.nasUploadForm.reset();
  state.audioTranslationEnabled = false;
  renderAsrControls();
  renderTranslationControls("audio");
  renderVideoControls();
  state.selectedAssetId = asset.id;
  showNasUploadDialog(asset);
  await loadNasAssets();
}

function showNasUploadDialog(asset) {
  els.nasUploadDialogMessage.textContent = t("upload.dialogMessage", {
    title: asset.title,
    analyzer: asset.analyzer || "-",
  });
  els.nasUploadDialog.hidden = false;
}

function closeNasUploadDialog() {
  els.nasUploadDialog.hidden = true;
}

async function askSelectedAsset() {
  if (!state.selectedAsset) return;
  const questionInput = document.querySelector("#assetQuestionInput");
  const answerBox = document.querySelector("#assetAnswerBox");
  const question = questionInput?.value.trim() || "";
  if (!state.currentLlmModel) {
    showToast(t("upload.modelRequired"), t("upload.questionTitle"));
    return;
  }
  if (!question) {
    showToast(t("upload.questionRequired"), t("upload.questionTitle"));
    return;
  }

  try {
    const result = await api(`/api/nas-assets/${state.selectedAsset.id}/ask`, {
      method: "POST",
      body: JSON.stringify({
        question,
        api_key: "",
      }),
    });
    answerBox.hidden = false;
    answerBox.classList.remove("error");
    answerBox.innerHTML = `
      <strong>${escapeHtml(t("upload.answerTitle"))} · ${escapeHtml(result.model)}${renderCacheHitLabel(result.cache)}</strong>
      ${renderNasPersistenceNotice(result.nas_persistence)}
      <pre>${escapeHtml(result.answer)}</pre>
      ${renderAnswerSources(result.contexts || [], result.retrieval || {})}
    `;
    await loadLlmCalls();
  } catch (error) {
    answerBox.hidden = false;
    answerBox.classList.add("error");
    answerBox.innerHTML = `<strong>${escapeHtml(t("aiwork.responseFailed"))}</strong><pre>${escapeHtml(error.message)}</pre>`;
    await loadLlmCalls();
  }
}

function renderNasPersistenceNotice(persistence) {
  if (!persistence?.saved) return "";
  let message = persistence.created ? t("upload.analysisSaved") : t("upload.analysisAlreadySaved");
  if (persistence.embedding_status === "pending") message = t("upload.analysisEmbeddingQueued");
  return `<div class="nas-persistence-notice">${escapeHtml(message)}</div>`;
}

function renderCacheHitLabel(cache) {
  if (cache?.bypassed) return ` · ${escapeHtml(t("aiwork.cacheBypassed"))}`;
  if (!cache?.hit) return "";
  const match = cache.match_type === "exact" ? t("upload.cacheExact") : t("upload.cacheSemantic");
  const similarity = cache.similarity !== undefined ? ` ${cache.similarity}` : "";
  return ` · ${escapeHtml(t("upload.cacheHit"))} (${escapeHtml(match)}${escapeHtml(similarity)})`;
}

function renderAnswerSources(contexts, retrieval) {
  if (!contexts.length) return "";
  const retrievalLabel = retrieval.method === "hybrid" ? t("upload.retrievalHybrid") : t("upload.retrievalKeyword");
  return `
    <div class="answer-source-panel">
      <strong>${escapeHtml(t("upload.answerSources"))} · ${escapeHtml(retrievalLabel)}${retrieval.embedding_model ? ` · ${escapeHtml(retrieval.embedding_model)}` : ""}</strong>
      <div class="answer-source-list">
        ${contexts
          .map(
            (chunk) => `
              <article class="answer-source-card">
                <div class="chunk-source-line">
                  <b>#${escapeHtml(chunk.chunk_index)}</b>
                  ${chunk.page_number ? `<span>${escapeHtml(t("upload.page"))} ${escapeHtml(chunk.page_number)}</span>` : ""}
                  ${chunk.chunk_type ? `<span>${escapeHtml(t("upload.type"))} ${escapeHtml(chunk.chunk_type)}</span>` : ""}
                  ${chunk.retrieval_score !== undefined ? `<span>${escapeHtml(t("upload.retrievalScore"))} ${escapeHtml(chunk.retrieval_score)}</span>` : ""}
                  ${chunk.semantic_score !== null && chunk.semantic_score !== undefined ? `<span>${escapeHtml(t("upload.semanticScore"))} ${escapeHtml(chunk.semantic_score)}</span>` : ""}
                  ${chunk.keyword_score !== undefined ? `<span>${escapeHtml(t("upload.keywordScore"))} ${escapeHtml(chunk.keyword_score)}</span>` : ""}
                </div>
                <p>${escapeHtml(chunk.content.slice(0, 220))}</p>
                ${chunk.image_url ? `<img src="${escapeHtml(chunk.image_url)}" alt="${escapeHtml(t("upload.pagePreview"))}" loading="lazy" />` : ""}
              </article>
            `
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderLlmControls() {
  if (!state.llmCatalog) {
    els.llmProviderSelect.innerHTML = `<option value="">${t("aiwork.loading")}</option>`;
    els.llmModelSelect.innerHTML = `<option value="">${t("aiwork.selectProviderFirst")}</option>`;
    els.llmModelSelect.disabled = true;
    return;
  }

  els.llmModeButtons.forEach((button) => {
    const active = button.dataset.llmMode === state.selectedLlmMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
    button.disabled = state.user?.role !== "admin";
  });
  const modeModels = llmModelsForMode(state.selectedLlmMode);
  const providers = [...new Set(modeModels.map((model) => model.provider))].map((name) => ({
    name,
    model_count: modeModels.filter((model) => model.provider === name).length,
  }));
  els.llmProviderSelect.innerHTML = [
    `<option value="">${t("aiwork.allProviders")}</option>`,
    ...providers.map((provider) => {
      return `<option value="${escapeHtml(provider.name)}">${escapeHtml(provider.name)} (${provider.model_count})</option>`;
    }),
  ].join("");
  els.llmProviderSelect.value = state.selectedProvider;

  const models = filteredLlmModels();
  els.llmProviderSelect.disabled = state.user?.role !== "admin";
  els.llmModelSelect.disabled = models.length === 0 || state.user?.role !== "admin";
  els.llmModelSelect.innerHTML = [
    `<option value="">${t("aiwork.selectModel")}</option>`,
    ...models.map((model) => {
      return `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</option>`;
    }),
  ].join("");
  els.llmModelSelect.value = state.selectedLlmId;

  els.providerSummary.innerHTML = state.llmCatalog.providers
    .map((provider) => `<span>${escapeHtml(provider.name)} · ${provider.model_count}</span>`)
    .join("");
  renderSystemLlmSetting();
}

function renderSystemLlmSetting() {
  if (!els.currentSystemModelName) return;
  const model = state.currentLlmModel;
  const label = model ? `${model.provider} · ${model.name}` : "-";
  els.currentSystemModelName.textContent = label;
  if (els.recordTranslationCurrentLlmName) els.recordTranslationCurrentLlmName.textContent = label;
  if (els.audioTranslationCurrentLlmName) els.audioTranslationCurrentLlmName.textContent = label;
  const updatedBy = state.llmCatalog?.current_model_updated_by;
  const updatedAt = state.llmCatalog?.current_model_updated_at;
  els.currentSystemModelMeta.textContent = updatedBy && updatedAt
    ? t("aiwork.systemModelUpdated", { user: updatedBy, time: formatDate(updatedAt) })
    : t("aiwork.systemModelDefault");
  els.currentSystemModelMeta.title = state.user?.role === "admin"
    ? t("aiwork.systemModelAdminHint")
    : t("aiwork.systemModelUserHint");
  const isAdmin = state.user?.role === "admin";
  els.setCurrentLlmButton.hidden = !isAdmin;
  els.setCurrentLlmButton.disabled = !state.selectedLlmId || state.selectedLlmId === state.currentLlmId;
  els.setCurrentLlmButton.textContent = t("aiwork.setSystemModel");
}

async function saveCurrentLlmModel() {
  if (!state.selectedLlmId) {
    showToast(t("aiwork.selectBeforeSet"), t("aiwork.systemModelLabel"));
    return;
  }
  els.setCurrentLlmButton.disabled = true;
  els.setCurrentLlmButton.textContent = t("aiwork.settingSystemModel");
  try {
    await api("/api/admin/llm/current-model", {
      method: "PUT",
      body: JSON.stringify({ model_id: state.selectedLlmId }),
    });
    showToast(t("aiwork.systemModelSaved"), t("aiwork.systemModelLabel"));
    await loadLlmCatalog();
  } finally {
    renderSystemLlmSetting();
  }
}

function llmModelsForMode(mode) {
  if (!state.llmCatalog) return [];
  return state.llmCatalog.models.filter((model) => model.execution === mode);
}

function defaultLlmModelForMode(mode) {
  const models = llmModelsForMode(mode);
  const preferredId = mode === "local" ? "local:qwen3-4b" : "free:openai-fast";
  return models.find((model) => model.id === preferredId) || models[0] || null;
}

function filteredLlmModels() {
  const models = llmModelsForMode(state.selectedLlmMode);
  if (!state.selectedProvider) return models;
  return models.filter((model) => model.provider === state.selectedProvider);
}

async function selectLlmMode(mode) {
  state.selectedLlmMode = mode;
  const fallback = defaultLlmModelForMode(mode);
  state.selectedProvider = fallback?.provider || "";
  state.selectedLlmId = fallback?.id || "";
  state.selectedPricing = null;
  renderLlmControls();
  if (fallback) {
    await selectLlmModel(fallback.id);
  } else {
    renderPricingPanel();
    renderKeyStatus();
  }
}

async function selectLlmModel(modelId) {
  state.selectedLlmId = modelId;
  state.selectedPricing = null;
  renderPricingPanel();
  renderKeyStatus();
  renderModelUsePanel();
  renderSystemLlmSetting();
  if (!modelId) return;

  const pricing = await api(`/api/llm/pricing/${encodeURIComponent(modelId)}`);
  state.selectedPricing = pricing;
  renderPricingPanel();
  renderKeyStatus();
  renderModelUsePanel();
  renderSystemLlmSetting();
  const model = state.selectedPricing.model;
  const hasKey = modelHasApiAccess(model);
  if (model.free_tier.requires_api_key_for_real_call && !hasKey) {
    openKeyModal();
  }
}

function renderPricingPanel() {
  if (!state.selectedPricing) {
    els.pricingPanel.innerHTML = `<div class="empty-state">${t("aiwork.emptyPricing")}</div>`;
    return;
  }

  const model = state.selectedPricing.model;
  const unitText = t("aiwork.perUnit", { unit: model.unit });
  els.pricingPanel.innerHTML = `
    <div class="pricing-header">
      <div>
        <p class="eyebrow">${escapeHtml(model.provider)} · ${escapeHtml(model.family)}</p>
        <h3>${escapeHtml(model.name)}</h3>
        <span>${t("aiwork.modelId")}: ${escapeHtml(model.model)}</span>
      </div>
      <span class="pricing-date">${t("aiwork.updatedAt")}: ${escapeHtml(state.selectedPricing.updated_at)}</span>
    </div>
    <div class="price-grid">
      ${priceTile(t("aiwork.input"), model.input, model.currency, unitText)}
      ${priceTile(t("aiwork.cachedInput"), model.cached_input, model.currency, unitText)}
      ${priceTile(t("aiwork.cacheWrite"), model.cache_write, model.currency, unitText)}
      ${priceTile(t("aiwork.output"), model.output, model.currency, unitText)}
    </div>
    <div class="pricing-meta">
      <span>${t("aiwork.context")}: ${escapeHtml(model.context)}</span>
      <div class="free-quota-line ${model.free_tier.available && !model.free_tier.requires_api_key_for_real_call ? "available" : ""}">
        <strong>${t("aiwork.freeQuota")}: ${freeTierLabel(model)}</strong>
        <span>${escapeHtml(freeTierDescription(model))}</span>
        ${model.free_tier.requires_api_key_for_real_call ? `<small>${t("aiwork.realCallNeedsKey")}</small>` : ""}
      </div>
      <p>${escapeHtml(modelNote(model))}</p>
      <a href="${escapeHtml(model.source_url)}" target="_blank" rel="noreferrer">${t("aiwork.source")}</a>
    </div>
  `;
}

function priceTile(label, value, currency, unitText) {
  const amount = typeof value === "number" ? `${currency} ${value.toLocaleString(undefined, { maximumFractionDigits: 4 })}` : t("aiwork.noCachedPrice");
  return `
    <article class="price-tile">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(amount)}</strong>
      <small>${escapeHtml(unitText)}</small>
    </article>
  `;
}

function freeTierDescription(model) {
  if (state.lang === "en") return model.free_tier.description;
  const descriptions = messages[state.lang].aiwork.freeTierDescriptions;
  return descriptions[model.provider] || descriptions.default;
}

function modelNote(model) {
  return state.lang === "zh-Hant" ? model.note_zh_hant || model.note : model.note;
}

function freeTierLabel(model) {
  if (!model.free_tier.available) return t("aiwork.freeQuotaUnavailable");
  if (model.free_tier.requires_api_key_for_real_call) return t("aiwork.freeQuotaListed");
  return t("aiwork.freeQuotaAvailable");
}

function renderKeyStatus() {
  const model = state.selectedPricing?.model;
  els.openKeyModalButton.disabled = !model;
  if (!model) {
    els.keyStatus.textContent = t("aiwork.keyNotSet");
    els.keyStatus.classList.remove("ready");
    return;
  }

  if (!model.free_tier.requires_api_key_for_real_call) {
    els.openKeyModalButton.disabled = true;
    els.keyStatus.textContent = t("aiwork.keyNotRequired");
    els.keyStatus.classList.add("ready");
    renderModelUsePanel();
    return;
  }

  const providerKey = providerKeyId(model.provider);
  if (state.apiKeys[providerKey]) {
    els.keyStatus.textContent = t("aiwork.keyReady", { provider: model.provider });
    els.keyStatus.classList.add("ready");
  } else if (model.server_key_configured) {
    els.keyStatus.textContent = t("aiwork.companyKeyReady");
    els.keyStatus.classList.add("ready");
  } else {
    els.keyStatus.textContent = t("aiwork.keyNotSet");
    els.keyStatus.classList.remove("ready");
  }
  renderModelUsePanel();
}

function renderModelUsePanel() {
  const model = state.selectedPricing?.model;
  if (!model) {
    els.modelUsePanel.hidden = false;
    els.modelUseTitle.textContent = t("aiwork.useSelectModel");
    els.modelUseMode.textContent = t("aiwork.useWaiting");
    els.modelUseMode.classList.remove("ready");
    els.runModelButton.disabled = true;
    els.forceRunModelButton.disabled = true;
    els.modelResponseBox.hidden = true;
    return;
  }

  const isCurrent = model.id === state.currentLlmId;
  const hasKey = modelHasApiAccess(model);
  const canUseFreeQuota = Boolean(model.free_tier.available && !model.free_tier.requires_api_key_for_real_call);
  els.modelUsePanel.hidden = false;
  els.modelUseTitle.textContent = t("aiwork.useTitle", { model: model.name });
  els.modelUseMode.textContent = !isCurrent
    ? t("aiwork.saveBeforeRun")
    : model.provider === "Local NAS"
    ? t("aiwork.useLocalNas")
    : hasKey
    ? t("aiwork.useWithKey")
    : canUseFreeQuota
      ? t("aiwork.useWithFreeQuota")
      : t("aiwork.useNeedsKey");
  els.modelUseMode.classList.toggle("ready", isCurrent && (hasKey || canUseFreeQuota));
  els.runModelButton.disabled = !isCurrent || (!hasKey && !canUseFreeQuota);
  els.forceRunModelButton.disabled = !isCurrent || (!hasKey && !canUseFreeQuota);
}

function renderLlmCallHistory() {
  if (!state.llmCalls.length) {
    els.llmCallHistory.innerHTML = `<div class="empty-state compact">${t("aiwork.historyEmpty")}</div>`;
    return;
  }

  els.llmCallHistory.innerHTML = state.llmCalls
    .map((call) => {
      return `
        <article class="llm-call-row ${escapeHtml(call.status)}">
          <div class="llm-call-header">
            <div>
              <strong>${escapeHtml(call.provider)} · ${escapeHtml(call.model_name)}</strong>
              <span>${escapeHtml(formatDate(call.created_at))} · ${escapeHtml(t("aiwork.historyCaller"))}: ${escapeHtml(call.caller_username || `#${call.user_id}`)} · ${escapeHtml(call.access_mode || "-")}</span>
            </div>
            <span class="badge ${escapeHtml(call.status)}">${callStatusLabel(call.status)}</span>
          </div>
          <p class="llm-call-prompt"><b>${escapeHtml(t("aiwork.historyInput"))}</b>${escapeHtml(call.prompt || "-")}</p>
          <p class="llm-call-response"><b>${escapeHtml(t("aiwork.historyOutput"))}</b>${escapeHtml(call.response || call.error_message || "-")}</p>
          <div class="llm-usage-grid">
            ${usageChip(t("aiwork.usageInput"), call.input_tokens)}
            ${usageChip(t("aiwork.usageOutput"), call.output_tokens)}
            ${usageChip(t("aiwork.usageTotal"), call.total_tokens)}
            ${usageChip(t("aiwork.remainingTokens"), call.remaining_tokens)}
            ${usageChip(t("aiwork.remainingRequests"), call.remaining_requests)}
            ${usageChip(t("aiwork.remainingBalance"), call.remaining_balance)}
          </div>
        </article>
      `;
    })
    .join("");
}

function usageChip(label, value) {
  return `<span><b>${escapeHtml(label)}</b>${escapeHtml(value ?? t("aiwork.unknown"))}</span>`;
}

function callStatusLabel(status) {
  return {
    completed: t("aiwork.statusCompleted"),
    failed: t("aiwork.statusFailed"),
    blocked: t("aiwork.statusBlocked"),
  }[status] || status;
}

function openKeyModal() {
  if (!state.selectedPricing) return;
  state.keyModalPricing = state.selectedPricing;
  renderKeyModal();
  els.apiKeyModal.hidden = false;
  els.apiKeyInput.focus();
}

function openKeyModalForPricing(pricing) {
  if (!pricing) return;
  state.keyModalPricing = pricing;
  renderKeyModal();
  els.apiKeyModal.hidden = false;
  els.apiKeyInput.focus();
}

function closeKeyModal() {
  els.apiKeyModal.hidden = true;
  els.apiKeyInput.value = "";
  state.keyModalPricing = null;
}

function renderKeyModal() {
  const model = (state.keyModalPricing || state.selectedPricing)?.model;
  if (!model) return;
  els.keyModalModelName.textContent = t("keyModal.selectedModel", {
    provider: model.provider,
    model: model.name,
  });
}

function saveApiKeyForSession() {
  const key = els.apiKeyInput.value.trim();
  if (!key) {
    showToast(t("keyModal.missingKey"), t("keyModal.title"));
    return;
  }

  const model = (state.keyModalPricing || state.selectedPricing).model;
  state.apiKeys[providerKeyId(model.provider)] = key;
  renderKeyStatus();
  renderModelUsePanel();
  closeKeyModal();
  showToast(t("keyModal.saved"), model.provider);
}

function hideLlmSuggestions() {
  state.llmSuggestions = [];
  state.activeLlmSuggestion = -1;
  els.llmPromptSuggestions.hidden = true;
  els.llmPromptSuggestions.innerHTML = "";
  els.llmPromptInput.setAttribute("aria-expanded", "false");
}

function renderLlmSuggestions() {
  if (!state.llmSuggestions.length) {
    els.llmPromptSuggestions.hidden = true;
    els.llmPromptInput.setAttribute("aria-expanded", "false");
    return;
  }
  els.llmPromptSuggestions.innerHTML = state.llmSuggestions
    .map((suggestion, index) => {
      const active = index === state.activeLlmSuggestion;
      const sourceLabel = suggestion.cached ? t("aiwork.suggestionCached") : t("aiwork.suggestionHistory");
      return `
        <button class="prompt-suggestion${active ? " active" : ""}" type="button" role="option"
          aria-selected="${active}" data-suggestion-index="${index}">
          <span>${escapeHtml(suggestion.prompt)}</span>
          <small>${escapeHtml(sourceLabel)}</small>
        </button>
      `;
    })
    .join("");
  els.llmPromptSuggestions.hidden = false;
  els.llmPromptInput.setAttribute("aria-expanded", "true");
}

async function loadLlmSuggestions() {
  const query = els.llmPromptInput.value.trim();
  const modelId = state.selectedPricing?.model?.id;
  const requestId = ++state.llmSuggestionRequestId;
  if (query.length < 2 || !modelId) {
    hideLlmSuggestions();
    return;
  }
  try {
    const result = await api(`/api/llm/suggestions?model_id=${encodeURIComponent(modelId)}&q=${encodeURIComponent(query)}`, { busy: false });
    if (requestId !== state.llmSuggestionRequestId || query !== els.llmPromptInput.value.trim()) return;
    state.llmSuggestions = result.suggestions || [];
    state.activeLlmSuggestion = -1;
    renderLlmSuggestions();
  } catch {
    if (requestId === state.llmSuggestionRequestId) hideLlmSuggestions();
  }
}

function selectLlmSuggestion(index) {
  const suggestion = state.llmSuggestions[index];
  if (!suggestion) return;
  els.llmPromptInput.value = suggestion.prompt;
  hideLlmSuggestions();
  els.llmPromptInput.focus();
}

function renderMcpExecutionTrace(mcp) {
  if (!mcp?.enabled) return "";
  if (!mcp.used) {
    return `
      <details class="mcp-execution-trace">
        <summary>${escapeHtml(t("aiwork.mcpTrace"))} · ${escapeHtml(t("aiwork.mcpNotUsed"))}</summary>
        <p>${escapeHtml(mcp.reason || t("aiwork.mcpNotUsed"))}</p>
      </details>
    `;
  }
  return `
    <details class="mcp-execution-trace">
      <summary>${escapeHtml(t("aiwork.mcpTrace"))} · ${escapeHtml(mcp.server)} / ${escapeHtml(mcp.tool)}</summary>
      <strong>${escapeHtml(t("aiwork.mcpArguments"))}</strong>
      <pre>${escapeHtml(JSON.stringify(mcp.arguments || {}, null, 2))}</pre>
      <strong>${escapeHtml(t("aiwork.mcpResult"))}</strong>
      <pre>${escapeHtml(JSON.stringify(mcp.result || {}, null, 2))}</pre>
    </details>
  `;
}

async function runSelectedModel(forceRefresh = false) {
  const model = state.selectedPricing?.model;
  if (!model) return;

  const prompt = els.llmPromptInput.value.trim();
  if (!prompt) {
    showToast(t("aiwork.promptRequired"), t("aiwork.responseTitle"));
    return;
  }

  const hasApiKey = modelHasApiAccess(model);
  const canUseFreeQuota = Boolean(model.free_tier.available && !model.free_tier.requires_api_key_for_real_call);
  if (!hasApiKey && !canUseFreeQuota) {
    showToast(t("aiwork.noAccess"), model.provider);
    openKeyModal();
    return;
  }

  hideLlmSuggestions();
  els.runModelButton.disabled = true;
  els.forceRunModelButton.disabled = true;
  try {
    const result = await api("/api/llm/run", {
      method: "POST",
      body: JSON.stringify({
        model_id: model.id,
        prompt,
        system_prompt: els.llmSystemPromptInput.value.trim(),
        api_key: state.apiKeys[providerKeyId(model.provider)] || "",
        force_refresh: forceRefresh,
        use_mcp: state.useMcp,
        mcp_server_id: state.selectedMcpServerId,
      }),
    });
    els.modelResponseBox.hidden = false;
    els.modelResponseBox.classList.remove("error");
    els.modelResponseBox.innerHTML = `
      <strong>${t("aiwork.responseTitle")} · ${escapeHtml(result.model)}${renderCacheHitLabel(result.cache)}</strong>
      <div class="llm-usage-grid inline">
        ${usageChip(t("aiwork.usageInput"), result.usage?.input_tokens)}
        ${usageChip(t("aiwork.usageOutput"), result.usage?.output_tokens)}
        ${usageChip(t("aiwork.usageTotal"), result.usage?.total_tokens)}
        ${usageChip(t("aiwork.remainingTokens"), result.usage?.remaining_tokens)}
        ${usageChip(t("aiwork.remainingBalance"), result.usage?.remaining_balance)}
      </div>
      <pre>${escapeHtml(result.answer)}</pre>
      ${renderMcpExecutionTrace(result.mcp)}
    `;
    await loadLlmCalls();
  } catch (error) {
    els.modelResponseBox.hidden = false;
    els.modelResponseBox.classList.add("error");
    els.modelResponseBox.innerHTML = `
      <strong>${t("aiwork.responseFailed")}</strong>
      <pre>${escapeHtml(error.message)}</pre>
    `;
    await loadLlmCalls();
    showToast(error.message, t("errors.requestFailed"));
  } finally {
    renderModelUsePanel();
  }
}

function providerKeyId(provider) {
  return provider.toLowerCase().replaceAll(/[^a-z0-9]+/g, "-");
}

function modelHasApiAccess(model) {
  if (!model) return false;
  return Boolean(model.server_key_configured || state.apiKeys[providerKeyId(model.provider)]);
}

function renderMetrics() {
  els.totalMeetings.textContent = state.meetings.length;
  els.processingMeetings.textContent = state.meetings.filter((meeting) => meeting.status === "processing").length;
  els.completedMeetings.textContent = state.meetings.filter((meeting) => meeting.status === "completed").length;
}

function openDashboardMeetings(status) {
  switchView("meetings");
  const meeting = status === "all"
    ? state.meetings[0]
    : state.meetings.find((item) => item.status === status);
  if (meeting) selectMeeting(meeting.id);
}

function renderMeetingList() {
  if (!state.meetings.length) {
    els.meetingList.innerHTML = `<div class="empty-state">${t("meetings.emptyList")}</div>`;
    return;
  }

  els.meetingList.innerHTML = state.meetings
    .map((meeting) => {
      const created = formatDate(meeting.created_at);
      const excerpt = meeting.transcript ? meeting.transcript.slice(0, 72) : t("meetings.waitingExcerpt");
      return `
        <button class="meeting-row ${meeting.id === state.selectedMeetingId ? "active" : ""}" data-meeting-id="${meeting.id}">
          <div class="meeting-row-header">
            <strong>${escapeHtml(meeting.title)}</strong>
            <span class="badge ${meeting.status}">${statusLabel(meeting.status)}</span>
          </div>
          <p>${sourceLabel(meeting.source)} · ${created}${meeting.asr_model ? ` · ${escapeHtml(meeting.asr_model)}` : ""}</p>
          <p>${escapeHtml(excerpt)}</p>
        </button>
      `;
    })
    .join("");
}

async function selectMeeting(id) {
  state.selectedMeetingId = id;
  renderMeetingList();
  const meeting = await api(`/api/meetings/${id}`);
  const created = formatDate(meeting.created_at);
  els.meetingDetail.innerHTML = `
    <h3>${escapeHtml(meeting.title)}</h3>
    <div class="detail-meta">
      <span>${sourceLabel(meeting.source)}</span>
      <span>${created}</span>
      <span>${escapeHtml(meeting.original_filename)}</span>
      <span class="badge ${meeting.status}">${statusLabel(meeting.status)}</span>
      ${meeting.asr_model ? `<span>${escapeHtml(meeting.asr_provider || "ASR")} · ${escapeHtml(meeting.asr_model)}</span>` : ""}
      ${meeting.translation_enabled ? `<span>${escapeHtml(meeting.translation_provider || "LLM")} · ${escapeHtml(meeting.translation_model || "-")} → ${escapeHtml(translationTargetLabel(meeting.translation_target))}</span>` : ""}
      ${meeting.line_push_enabled ? `<span>LINE · ${escapeHtml(meeting.line_group_name || meeting.line_group_id)} · ${escapeHtml(statusLabel(meeting.line_push_status))}</span>` : ""}
    </div>
    ${meeting.nas_asset_id ? `<div class="meeting-asset-actions"><button class="secondary-button" type="button" data-open-nas-asset="${meeting.nas_asset_id}">${escapeHtml(t("dashboardAssets.open"))}</button></div>` : ""}
    <audio controls src="/api/meetings/${meeting.id}/audio"></audio>
    <section class="meeting-text-section">
      <strong>${escapeHtml(t("meetings.transcriptTitle"))}</strong>
      <div class="transcript-box">${escapeHtml(meeting.transcript || processingText(meeting.status, meeting.error_message))}</div>
    </section>
    ${renderMeetingTranslation(meeting)}
    ${renderMeetingLinePush(meeting)}
  `;
}

function renderMeetingTranslation(meeting) {
  if (!meeting.translation_enabled) return "";
  let content = meeting.translation;
  if (!content && meeting.translation_status === "failed") {
    content = t("meetings.translationFailed", { error: meeting.translation_error || t("aiwork.unknown") });
  }
  if (!content) content = t("meetings.translationPending");
  return `
    <section class="meeting-text-section translation-result-section">
      <div class="meeting-text-heading">
        <strong>${escapeHtml(t("meetings.translationTitle"))} · ${escapeHtml(translationTargetLabel(meeting.translation_target))}</strong>
        <span class="badge ${escapeHtml(meeting.translation_status || "processing")}">${escapeHtml(statusLabel(meeting.translation_status === "disabled" ? "completed" : meeting.translation_status || "processing"))}</span>
      </div>
      <div class="transcript-box">${escapeHtml(content)}</div>
    </section>
  `;
}

function renderMeetingLinePush(meeting) {
  if (!meeting.line_push_enabled) return "";
  let content = meeting.line_summary;
  if (!content && meeting.line_push_status === "failed") {
    content = t("record.lineError", { error: meeting.line_push_error || t("aiwork.unknown") });
  }
  if (!content) content = t("record.lineWaiting");
  const mode = meeting.line_push_full_transcript ? t("record.lineFullMode") : t("record.lineSummaryMode");
  return `
    <section class="meeting-text-section line-summary-section">
      <div class="meeting-text-heading">
        <strong>${escapeHtml(t("record.lineSummaryTitle"))} · ${escapeHtml(meeting.line_group_name || meeting.line_group_id)}</strong>
        <span class="badge ${escapeHtml(meeting.line_push_status || "pending")}">${escapeHtml(statusLabel(meeting.line_push_status || "pending"))}</span>
      </div>
      <small>${escapeHtml(mode)}</small>
      <div class="transcript-box">${escapeHtml(content)}</div>
    </section>
  `;
}

function renderSelectedMeetingEmptyState() {
  if (!state.selectedMeetingId && els.meetingDetail.querySelector(".empty-state")) {
    els.meetingDetail.innerHTML = `<div class="empty-state">${t("meetings.emptyDetail")}</div>`;
  }
}

function connectWebSocket() {
  closeWebSocket();
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  state.ws = new WebSocket(`${protocol}://${window.location.host}/ws/notifications`);
  state.ws.onmessage = async (event) => {
    const payload = JSON.parse(event.data);
    const message = notificationMessage(payload);
    const title = notificationTitle(payload.type);
    addActivity(message, payload.title || t("activity.fallbackTitle"));
    showToast(message, title);
    if (payload.type.startsWith("nas_asset_")) {
      await loadNasAssets({ background: true });
      if (currentViewName() === "network") await loadNetworkAssets({ background: true });
      return;
    }
    await loadMeetings({ background: true });
    if (state.selectedMeetingId && payload.meeting_id === state.selectedMeetingId) {
      await selectMeeting(state.selectedMeetingId);
    }
  };
  state.ws.onclose = () => {
    if (state.user) window.setTimeout(connectWebSocket, 2500);
  };
}

function closeWebSocket() {
  if (state.ws) {
    state.ws.onclose = null;
    state.ws.close();
    state.ws = null;
  }
}

async function startRecording() {
  const availabilityError = recordingAvailabilityError();
  if (availabilityError) throw new Error(availabilityError);
  const model = state.currentAsrModel;
  if (!model) throw new Error(t("record.asrModelRequired"));
  validateTranslationSelection("record");
  if (state.recordLinePushEnabled && !state.recordLineGroupId) {
    throw new Error(t("record.lineGroupRequired"));
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "";
  state.mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  state.chunks = [];
  state.elapsedBeforePause = 0;
  state.recordStartedAt = Date.now();

  state.mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) state.chunks.push(event.data);
  };
  state.mediaRecorder.onstop = async () => {
    stream.getTracks().forEach((track) => track.stop());
    await uploadRecording();
  };

  state.mediaRecorder.start();
  updateRecordingUi("recording");
  startTimer();
}

function recordingAvailabilityError() {
  if (!window.isSecureContext) return t("record.secureRequired");
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    return t("record.mediaUnavailable");
  }
  return "";
}

function updateRecordingAvailability() {
  const availabilityError = recordingAvailabilityError();
  els.recordHint.textContent = availabilityError ? t("record.secureHint") : t("record.hint");
  els.recordHint.classList.toggle("error-text", Boolean(availabilityError));
}

function pauseRecording() {
  if (!state.mediaRecorder) return;
  if (state.mediaRecorder.state === "recording") {
    state.mediaRecorder.pause();
    state.elapsedBeforePause += Date.now() - state.recordStartedAt;
    state.recordStartedAt = null;
    updateRecordingUi("paused");
  } else if (state.mediaRecorder.state === "paused") {
    state.mediaRecorder.resume();
    state.recordStartedAt = Date.now();
    updateRecordingUi("recording");
  }
}

function stopRecording() {
  if (!state.mediaRecorder || state.mediaRecorder.state === "inactive") return;
  if (state.mediaRecorder.state === "recording") {
    state.elapsedBeforePause += Date.now() - state.recordStartedAt;
  }
  state.mediaRecorder.stop();
  state.recordStartedAt = null;
  stopTimer();
  updateRecordingUi("saving");
}

async function uploadRecording() {
  const blob = new Blob(state.chunks, { type: state.mediaRecorder.mimeType || "audio/webm" });
  els.recordPreview.src = URL.createObjectURL(blob);
  els.recordPreview.hidden = false;

  const formData = new FormData();
  const timestamp = new Date().toISOString().slice(0, 19).replaceAll(":", "-");
  formData.append("title", els.meetingTitleInput.value.trim() || `${t("record.defaultTitle")} ${timestamp}`);
  formData.append("asr_model_id", state.currentAsrId);
  formData.append("asr_api_key", "");
  formData.append("translation_enabled", String(state.recordTranslationEnabled));
  formData.append("translation_target", state.recordTranslationTarget);
  formData.append("translation_model_id", state.recordTranslationModelId);
  formData.append("translation_api_key", "");
  const lineGroup = state.lineGroups.find((group) => group.id === state.recordLineGroupId);
  formData.append("line_push_enabled", String(state.recordLinePushEnabled));
  formData.append("line_group_id", state.recordLineGroupId);
  formData.append("line_group_name", lineGroup?.name || "");
  formData.append("line_push_full_transcript", String(state.recordLineFullTranscript));
  formData.append("audio", blob, `browser-recording-${timestamp}.webm`);

  try {
    await uploadFormData("/api/meetings/upload", formData);
  } catch (error) {
    updateRecordingUi("idle");
    showToast(error.message || t("record.uploadFailed"), t("toast.savedFailed"));
    return;
  }

  updateRecordingUi("idle");
  els.meetingTitleInput.value = "";
  showToast(t("record.saved"), t("toast.meetingDetected"));
  await loadMeetings();
}

function updateRecordingUi(mode) {
  state.recordMode = mode;
  els.recordPulse.className = `record-pulse ${mode === "recording" ? "recording" : mode === "paused" ? "paused" : "idle"}`;
  els.startRecord.disabled = mode === "recording" || mode === "paused" || mode === "saving";
  els.pauseRecord.disabled = mode === "idle" || mode === "saving";
  els.stopRecord.disabled = mode === "idle" || mode === "saving";
  els.pauseRecord.textContent = mode === "paused" ? t("record.resume") : t("record.pause");
  els.recordState.textContent = t(`record.states.${mode}`);
}

function startTimer() {
  stopTimer();
  state.timerId = window.setInterval(() => {
    const current = state.recordStartedAt ? Date.now() - state.recordStartedAt : 0;
    const seconds = Math.floor((state.elapsedBeforePause + current) / 1000);
    els.recordTimer.textContent = formatSeconds(seconds);
  }, 250);
}

function stopTimer() {
  if (state.timerId) window.clearInterval(state.timerId);
  state.timerId = null;
}

function addActivity(message, title) {
  const item = document.createElement("div");
  item.className = "activity-item";
  item.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(message)}</span>`;
  els.activityFeed.prepend(item);
  while (els.activityFeed.children.length > 8) els.activityFeed.lastElementChild.remove();
}

function showToast(message, title) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(message)}</span>`;
  els.toastHost.append(toast);
  window.setTimeout(() => toast.remove(), 4200);
}

function notificationTitle(type) {
  return {
    meeting_detected: t("toast.meetingDetected"),
    meeting_completed: t("toast.meetingCompleted"),
    meeting_needs_model: t("toast.meetingFailed"),
    meeting_failed: t("toast.meetingFailed"),
    nas_asset_uploaded: t("toast.nasReceived"),
    nas_asset_processed: t("toast.nasProcessed"),
    nas_asset_failed: t("toast.meetingFailed"),
  }[type] || t("toast.meetingDetected");
}

function notificationMessage(payload) {
  const title = payload.title || "";
  if (payload.type === "nas_asset_uploaded") return t("toast.assetUploaded", { title });
  if (payload.type === "nas_asset_processed" || payload.type === "nas_asset_failed") return t("toast.assetProcessed", { title });
  if (payload.type === "meeting_completed") return t("toast.completed", { title });
  if (payload.type === "meeting_needs_model") return payload.message || t("toast.failed", { title });
  if (payload.type === "meeting_failed") return t("toast.failed", { title });
  if (payload.meeting?.source === "web_upload") return t("toast.uploaded", { title });
  return t("toast.detected", { title });
}

function statusLabel(status) {
  return t(`status.${status}`);
}

function sourceLabel(source) {
  return source === "nas_discovery" ? t("meetings.sourceNas") : t("meetings.sourceWeb");
}

function processingText(status, error) {
  if (status === "failed" || status === "needs_model") return error || t("meetings.failedText");
  return t("meetings.processingText");
}

function formatDate(value) {
  const locale = state.lang === "en" ? "en-US" : "zh-Hant";
  return new Date(`${value.replace(" ", "T")}Z`).toLocaleString(locale);
}

function formatSeconds(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function formatBytes(bytes) {
  const value = Number(bytes || 0);
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  if (value < 1024 * 1024 * 1024) return `${(value / 1024 / 1024).toFixed(1)} MB`;
  return `${(value / 1024 / 1024 / 1024).toFixed(1)} GB`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

els.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  els.loginError.textContent = "";
  const formData = new FormData(els.loginForm);
  try {
    state.user = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: formData.get("username"),
        password: formData.get("password"),
      }),
    });
    await showApp();
  } catch {
    els.loginError.textContent = t("errors.invalidLogin");
  }
});

els.logoutButton.addEventListener("click", async () => {
  await api("/auth/logout", { method: "POST", body: "{}" });
  state.user = null;
  showLogin();
});

els.langOptions.forEach((button) => {
  button.addEventListener("click", () => applyLanguage(button.dataset.lang));
});
els.navItems.forEach((item) => item.addEventListener("click", () => {
  navigateFromSidebar(item.dataset.view, item).catch((error) => showToast(error.message, t("errors.requestFailed")));
}));
els.settingsNav.addEventListener("click", () => {
  setManagementMenuExpanded(els.settingsNav.getAttribute("aria-expanded") !== "true");
});
els.networkImportForm.addEventListener("submit", submitNetworkImport);
els.refreshNetworkAssets.addEventListener("click", () => {
  loadNetworkAssets().catch((error) => showToast(error.message, t("errors.requestFailed")));
});
els.networkAssetList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-network-asset-id]");
  if (button && !button.disabled) {
    openNasAsset(Number(button.dataset.networkAssetId)).catch((error) => showToast(error.message, t("upload.actionFailed")));
  }
});
document.querySelectorAll("[data-jump]").forEach((item) => {
  item.addEventListener("click", () => {
    navigateFromSidebar(item.dataset.jump, item).catch((error) => showToast(error.message, t("errors.requestFailed")));
  });
});
document.querySelectorAll("[data-dashboard-meeting-status]").forEach((item) => {
  item.addEventListener("click", () => openDashboardMeetings(item.dataset.dashboardMeetingStatus));
});
document.querySelectorAll("[data-dashboard-asset-filter]").forEach((item) => {
  item.addEventListener("click", () => {
    state.dashboardAssetFilter = item.dataset.dashboardAssetFilter;
    renderDashboardAssets();
  });
});
els.dashboardAssetGrid.addEventListener("click", (event) => {
  const transcriptButton = event.target.closest("[data-dashboard-transcript-id]");
  if (transcriptButton) {
    openNasAsset(Number(transcriptButton.dataset.dashboardTranscriptId), { transcript: true })
      .catch((error) => showToast(error.message, t("upload.actionFailed")));
    return;
  }
  const row = event.target.closest("[data-dashboard-asset-id]");
  if (row) openNasAsset(Number(row.dataset.dashboardAssetId)).catch((error) => showToast(error.message, t("upload.actionFailed")));
});
els.startRecord.addEventListener("click", () => startRecording().catch((error) => showToast(error.message, t("record.unavailable"))));
els.pauseRecord.addEventListener("click", pauseRecording);
els.stopRecord.addEventListener("click", stopRecording);
els.meetingSearch.addEventListener("input", debounce(loadMeetings, 220));
els.llmCallSearch.addEventListener("input", debounce(loadLlmCalls, 220));
els.nasAssetSearch.addEventListener("input", debounce(loadNasAssets, 220));
els.accountSearch.addEventListener("input", renderAccountList);
els.refreshLineAdmin.addEventListener("click", () => loadLineAdmin().catch((error) => showToast(error.message, t("lineAdmin.serviceUnavailable"))));
els.refreshN8nStatus.addEventListener("click", () => {
  loadN8nStatus().catch((error) => showToast(error.message, t("errors.requestFailed")));
});
els.openN8nButton.addEventListener("click", (event) => {
  if (state.n8nStatus?.status === "connected") return;
  event.preventDefault();
  showToast(t("n8n.unavailableNotice"), t("nav.n8n"));
});
els.lineAdminList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-line-action='save']");
  if (button && !button.disabled) saveLineSourcePolicy(button);
});
els.accountCreateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  els.accountFormError.textContent = "";
  try {
    await api("/api/admin/users", {
      method: "POST",
      body: JSON.stringify({
        username: els.newAccountUsername.value,
        password: els.newAccountPassword.value,
        role: els.newAccountRole.value,
      }),
    });
    els.accountCreateForm.reset();
    showToast(t("accounts.createdSuccess"), t("nav.accounts"));
    await loadAccounts();
  } catch (error) {
    els.accountFormError.textContent = accountErrorMessage(error.message);
  }
});
els.accountList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-account-action]");
  if (button && !button.disabled) handleAccountAction(button);
});
els.closePasswordReset.addEventListener("click", closePasswordReset);
els.cancelPasswordReset.addEventListener("click", closePasswordReset);
els.confirmPasswordReset.addEventListener("click", resetSelectedAccountPassword);
els.passwordResetModal.addEventListener("click", (event) => {
  if (event.target === els.passwordResetModal) closePasswordReset();
});
els.passwordResetInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") resetSelectedAccountPassword();
});
els.recordAsrModeSelect.addEventListener("change", () => {
  state.selectedRecordAsrMode = els.recordAsrModeSelect.value;
  state.selectedRecordAsrModelId = "";
  renderRecordingAsrControls();
});
els.recordAsrModelSelect.addEventListener("change", () => {
  state.selectedRecordAsrModelId = els.recordAsrModelSelect.value;
  renderRecordingAsrControls();
});
els.recordTranslationToggle.addEventListener("change", () => {
  state.recordTranslationEnabled = els.recordTranslationToggle.checked;
  renderTranslationControls("record");
});
els.recordTranslationTargetSelect.addEventListener("change", () => {
  state.recordTranslationTarget = els.recordTranslationTargetSelect.value;
  renderTranslationControls("record");
});
els.recordTranslationModeSelect.addEventListener("change", () => {
  state.recordTranslationMode = els.recordTranslationModeSelect.value;
  state.recordTranslationModelId = defaultLlmModelForMode(state.recordTranslationMode)?.id || "";
  renderTranslationControls("record");
});
els.recordTranslationModelSelect.addEventListener("change", () => {
  state.recordTranslationModelId = els.recordTranslationModelSelect.value;
  renderTranslationControls("record");
});
els.recordLinePushToggle.addEventListener("change", () => {
  state.recordLinePushEnabled = els.recordLinePushToggle.checked;
  renderLinePushControls();
});
els.recordLineGroupSelect.addEventListener("change", () => {
  state.recordLineGroupId = els.recordLineGroupSelect.value;
  renderLinePushControls();
});
els.recordLineFullTranscriptToggle.addEventListener("change", () => {
  state.recordLineFullTranscript = els.recordLineFullTranscriptToggle.checked;
  renderLinePushControls();
});
els.audioAsrModeSelect.addEventListener("change", () => {
  state.selectedAsrMode = els.audioAsrModeSelect.value;
  state.selectedAsrModelId = "";
  renderAsrControls();
});
els.audioAsrModelSelect.addEventListener("change", () => {
  state.selectedAsrModelId = els.audioAsrModelSelect.value;
  renderAsrControls();
});
els.audioTranslationToggle.addEventListener("change", () => {
  state.audioTranslationEnabled = els.audioTranslationToggle.checked;
  renderTranslationControls("audio");
});
els.audioTranslationTargetSelect.addEventListener("change", () => {
  state.audioTranslationTarget = els.audioTranslationTargetSelect.value;
  renderTranslationControls("audio");
});
els.audioTranslationModeSelect.addEventListener("change", () => {
  state.audioTranslationMode = els.audioTranslationModeSelect.value;
  state.audioTranslationModelId = defaultLlmModelForMode(state.audioTranslationMode)?.id || "";
  renderTranslationControls("audio");
});
els.audioTranslationModelSelect.addEventListener("change", () => {
  state.audioTranslationModelId = els.audioTranslationModelSelect.value;
  renderTranslationControls("audio");
});
els.videoModelModeSelect.addEventListener("change", () => {
  state.selectedVideoMode = els.videoModelModeSelect.value;
  state.selectedVideoModelId = "";
  renderVideoControls();
});
els.videoModelSelect.addEventListener("change", () => {
  state.selectedVideoModelId = els.videoModelSelect.value;
  renderVideoControls();
});
els.refreshLocalModelsButton.addEventListener("click", () => loadLocalModels().catch((error) => showToast(error.message, t("upload.modelActionFailed"))));
els.addCustomModelButton.addEventListener("click", openCustomModelModal);
els.closeCustomModelModal.addEventListener("click", closeCustomModelModal);
els.cancelCustomModel.addEventListener("click", closeCustomModelModal);
els.customModelType.addEventListener("change", renderCustomModelFields);
els.customModelForm.addEventListener("submit", createCustomModel);
els.customModelModal.addEventListener("click", (event) => {
  if (event.target === els.customModelModal) closeCustomModelModal();
});
els.localModelList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-model-action]");
  if (!button || button.disabled) return;
  runLocalModelAction(button.dataset.modelId, button.dataset.modelAction);
});
els.refreshMcpServers.addEventListener("click", () => loadMcpServers().catch((error) => showToast(error.message, t("mcp.syncFailed"))));
els.mcpSearchInput.addEventListener("input", () => {
  state.mcpSearchQuery = els.mcpSearchInput.value;
  renderMcpServers();
});
els.addMcpServer.addEventListener("click", () => openMcpServerModal());
els.closeMcpServerModal.addEventListener("click", closeMcpServerModal);
els.cancelMcpServer.addEventListener("click", closeMcpServerModal);
els.mcpServerForm.addEventListener("submit", saveMcpServer);
els.mcpServerModal.addEventListener("click", (event) => {
  if (event.target === els.mcpServerModal) closeMcpServerModal();
});
els.mcpServerList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-mcp-action]");
  const card = button?.closest("[data-mcp-server-id]");
  const server = state.mcpServers.find((item) => item.id === Number(card?.dataset.mcpServerId));
  if (!button || !server) return;
  if (button.dataset.mcpAction === "copy") copyMcpEndpoint(button.dataset.mcpEndpoint || "");
  if (button.dataset.mcpAction === "edit") openMcpServerModal(server);
  if (button.dataset.mcpAction === "sync") syncMcpServer(button, server);
});
els.nasUploadForm.addEventListener("submit", (event) => uploadNasAsset(event).catch((error) => showToast(error.message, t("upload.uploadFailed"))));
els.meetingList.addEventListener("click", (event) => {
  const row = event.target.closest("[data-meeting-id]");
  if (row) selectMeeting(Number(row.dataset.meetingId));
});
els.meetingDetail.addEventListener("click", (event) => {
  const button = event.target.closest("[data-open-nas-asset]");
  if (button) openNasAsset(Number(button.dataset.openNasAsset)).catch((error) => showToast(error.message, t("upload.actionFailed")));
});
els.nasAssetList.addEventListener("click", (event) => {
  const row = event.target.closest("[data-asset-id]");
  if (row) selectNasAsset(Number(row.dataset.assetId), { scroll: true });
});
els.nasAssetDetail.addEventListener("click", (event) => {
  if (event.target.id === "reprocessAssetButton") {
    reprocessSelectedAsset().catch((error) => showToast(error.message, t("upload.actionFailed")));
    return;
  }
  if (event.target.id === "openccAssetButton") {
    convertSelectedAssetToTraditional().catch((error) => showToast(error.message, t("upload.actionFailed")));
    return;
  }
  const segmentButton = event.target.closest("[data-transcribe-segment]");
  if (segmentButton) {
    transcribeAudioSegment(Number(segmentButton.dataset.transcribeSegment))
      .catch((error) => showToast(error.message, t("upload.segmentTranscriptionFailed")));
    return;
  }
  if (event.target.id === "askAssetButton") {
    askSelectedAsset().catch((error) => showToast(error.message, t("errors.requestFailed")));
  }
});
els.llmModeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    hideLlmSuggestions();
    selectLlmMode(button.dataset.llmMode).catch((error) => showToast(error.message, t("errors.requestFailed")));
  });
});
els.llmProviderSelect.addEventListener("change", () => {
  hideLlmSuggestions();
  state.selectedProvider = els.llmProviderSelect.value;
  state.selectedLlmId = "";
  state.selectedPricing = null;
  renderLlmControls();
  renderPricingPanel();
  renderKeyStatus();
});
els.llmModelSelect.addEventListener("change", () => {
  hideLlmSuggestions();
  selectLlmModel(els.llmModelSelect.value).catch((error) => showToast(error.message, t("errors.requestFailed")));
});
els.openKeyModalButton.addEventListener("click", openKeyModal);
els.closeKeyModal.addEventListener("click", closeKeyModal);
els.cancelKeyButton.addEventListener("click", closeKeyModal);
els.saveKeyButton.addEventListener("click", saveApiKeyForSession);
els.setCurrentLlmButton.addEventListener("click", () => saveCurrentLlmModel().catch((error) => showToast(error.message, t("errors.requestFailed"))));
els.setCurrentAsrButton.addEventListener("click", () => saveCurrentAsrModel().catch((error) => showToast(error.message, t("errors.requestFailed"))));
els.runModelButton.addEventListener("click", () => runSelectedModel().catch((error) => showToast(error.message, t("errors.requestFailed"))));
els.forceRunModelButton.addEventListener("click", () => runSelectedModel(true).catch((error) => showToast(error.message, t("errors.requestFailed"))));
els.useMcpToggle.addEventListener("change", () => {
  state.useMcp = els.useMcpToggle.checked;
  renderAiworkMcpControls();
});
els.aiworkMcpServerSelect.addEventListener("change", () => {
  state.selectedMcpServerId = els.aiworkMcpServerSelect.value;
});
els.llmPromptInput.addEventListener("input", debounce(loadLlmSuggestions, 220));
els.llmPromptInput.addEventListener("focus", () => loadLlmSuggestions());
els.llmPromptInput.addEventListener("keydown", (event) => {
  if (!els.llmPromptSuggestions.hidden && event.key === "ArrowDown") {
    event.preventDefault();
    state.activeLlmSuggestion = Math.min(state.activeLlmSuggestion + 1, state.llmSuggestions.length - 1);
    renderLlmSuggestions();
    return;
  }
  if (!els.llmPromptSuggestions.hidden && event.key === "ArrowUp") {
    event.preventDefault();
    state.activeLlmSuggestion = Math.max(state.activeLlmSuggestion - 1, 0);
    renderLlmSuggestions();
    return;
  }
  if (event.key === "Escape") {
    hideLlmSuggestions();
    return;
  }
  if (event.key === "Enter" && !event.isComposing) {
    event.preventDefault();
    if (state.activeLlmSuggestion >= 0) {
      selectLlmSuggestion(state.activeLlmSuggestion);
      return;
    }
    runSelectedModel().catch((error) => showToast(error.message, t("errors.requestFailed")));
  }
});
els.llmPromptSuggestions.addEventListener("click", (event) => {
  const option = event.target.closest("[data-suggestion-index]");
  if (option) selectLlmSuggestion(Number(option.dataset.suggestionIndex));
});
document.addEventListener("click", (event) => {
  if (!event.target.closest(".prompt-input-wrap")) hideLlmSuggestions();
});
els.apiKeyModal.addEventListener("click", (event) => {
  if (event.target === els.apiKeyModal) closeKeyModal();
});
els.closeNasUploadDialog.addEventListener("click", closeNasUploadDialog);
els.confirmNasUploadDialog.addEventListener("click", () => {
  closeNasUploadDialog();
  navigateFromSidebar("upload").catch((error) => showToast(error.message, t("errors.requestFailed")));
});
els.nasUploadDialog.addEventListener("click", (event) => {
  if (event.target === els.nasUploadDialog) closeNasUploadDialog();
});
els.apiKeyInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") saveApiKeyForSession();
});

function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), delay);
  };
}

const buttonFeedbackTimers = new WeakMap();

function showButtonFeedback(button) {
  if (!button || button.disabled) return;
  const previousTimer = buttonFeedbackTimers.get(button);
  if (previousTimer) window.clearTimeout(previousTimer);
  button.querySelector(":scope > .button-feedback-spinner")?.remove();
  const spinner = document.createElement("span");
  spinner.className = "button-feedback-spinner";
  spinner.setAttribute("aria-hidden", "true");
  button.appendChild(spinner);
  button.classList.add("has-interaction-feedback");
  const timer = window.setTimeout(() => {
    spinner.remove();
    button.classList.remove("has-interaction-feedback");
    buttonFeedbackTimers.delete(button);
  }, 520);
  buttonFeedbackTimers.set(button, timer);
}

document.addEventListener("click", (event) => {
  showButtonFeedback(event.target.closest("button"));
}, true);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch((error) => {
      console.warn("PWA service worker registration failed", error);
    });
  });
}

bootstrap();
