const messages = {
  "zh-Hant": {
    documentTitle: "AI Work 會議入口",
    language: { label: "語言切換" },
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
      meetings: "資料庫查詢",
      aiwork: "AI Work",
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
    dashboard: {
      eyebrow: "NAS Demo 範圍",
      title: "NAS 檔案發現、語音歸檔、會議轉寫查詢",
      copy: "第一版聚焦 NAS 會議資產進入系統後的完整鏈路：瀏覽器錄音或共享資料夾檔案進站、NAS inbox 即時提醒、後台搬移與處理狀態，以及可搜尋的歷史會議記錄。",
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
        copy: "上傳 audio、video、PDF、DOCX 等資料，NAS 收件後進入 Whisper、YOLO 或 RAG 流程。",
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
      start: "開始錄音",
      pause: "暫停",
      resume: "繼續",
      stop: "停止並保存",
      hint: "瀏覽器會請求麥克風權限。停止後系統會把原始錄音保存到本地 storage，按照 NAS 會議音訊歸檔流程進入轉寫佇列。",
      defaultTitle: "瀏覽器錄音",
      uploadFailed: "錄音上傳失敗，請重試",
      saved: "錄音已保存，正在處理",
      unavailable: "無法錄音",
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
      copy: "支援 audio、video、PDF、DOCX 與一般文件。NAS 收到檔案後會依類型送入 Whisper、YOLO 或 RAG 建庫流程。",
      fileLabel: "選擇檔案",
      titleLabel: "資料名稱",
      titlePlaceholder: "例如：董事會錄音、產品簡報 PDF",
      submit: "上傳到 NAS",
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
      category: "類型",
      analyzer: "分析器",
      fileSize: "大小",
      chunkCount: "RAG chunks",
      summary: "處理結果",
      chunks: "RAG 片段",
      questionTitle: "用 LLM 處理此文件",
      questionEyebrow: "RAG 文件問答",
      questionCopy: "文件已建立 RAG chunks，可選擇模型後對此文件提問。",
      modelRequired: "需要先選擇模型",
      questionRequired: "請先輸入問題",
      ask: "處理文件",
      questionPlaceholder: "例如：請整理這份文件的重點與待辦事項",
      answerTitle: "文件處理結果",
      modelNeedsKey: "此模型需要 API Key，請先設定模型",
      noRag: "此檔案尚未建立 RAG chunks；PDF/DOCX 完成處理後才能做文件問答。",
    },
    meetings: {
      eyebrow: "NAS 索引查詢",
      title: "NAS 會議資料庫",
      searchLabel: "搜尋",
      searchPlaceholder: "輸入關鍵字查詢 NAS 會議記錄",
      emptyList: "暫無會議記錄",
      emptyDetail: "選擇一條 NAS 會議資產查看錄音和轉寫內容",
      waitingExcerpt: "等待處理完成後顯示轉寫內容",
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
      loading: "載入中...",
      allProviders: "全部供應商",
      selectProviderFirst: "請先選擇供應商",
      selectModel: "請選擇模型",
      configureKey: "設定 API Key",
      keyNotSet: "尚未設定 API Key",
      keyReady: "{provider} API Key 已套用到本次工作階段",
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
      promptLabel: "輸入內容",
      promptPlaceholder: "請輸入要交給模型處理的內容",
      runModel: "送出",
      useTitle: "使用 {model}",
      useWithKey: "API Key 模式",
      useWithFreeQuota: "免費真實模型模式",
      useNeedsKey: "需要 API Key",
      promptRequired: "請先輸入內容",
      noAccess: "此模型需要 API Key，請先設定後再送出",
      responseTitle: "模型回覆",
      responseFailed: "模型呼叫失敗",
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
      processing: "處理中",
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
      meetings: "Knowledge Search",
      aiwork: "AI Work",
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
    dashboard: {
      eyebrow: "NAS Demo Scope",
      title: "NAS discovery, audio archive, transcript search",
      copy: "The first version focuses on the NAS meeting asset intake flow: browser recording or shared-folder file arrival, NAS inbox alerts, backend move and processing status, and searchable meeting history.",
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
        copy: "Upload audio, video, PDF, DOCX, and other assets into Whisper, YOLO, or RAG processing flows.",
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
      start: "Start Recording",
      pause: "Pause",
      resume: "Resume",
      stop: "Stop and Save",
      hint: "The browser will request microphone access. After stopping, the system saves the source audio into local storage as a NAS-style archive and queues it for transcription.",
      defaultTitle: "Browser Recording",
      uploadFailed: "Recording upload failed. Please try again.",
      saved: "Recording saved and processing started.",
      unavailable: "Recording unavailable",
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
      copy: "Supports audio, video, PDF, DOCX, and general files. After NAS receives a file, it is routed to Whisper, YOLO, or RAG indexing by type.",
      fileLabel: "File",
      titleLabel: "Asset Name",
      titlePlaceholder: "Example: board audio, product PDF",
      submit: "Upload to NAS",
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
      category: "Type",
      analyzer: "Analyzer",
      fileSize: "Size",
      chunkCount: "RAG chunks",
      summary: "Processing result",
      chunks: "RAG chunks",
      questionTitle: "Use LLM on this document",
      questionEyebrow: "RAG Document Q&A",
      questionCopy: "This document has RAG chunks. Select a model and ask a question.",
      modelRequired: "A model is required",
      questionRequired: "Enter a question first",
      ask: "Process Document",
      questionPlaceholder: "Example: summarize key points and action items",
      answerTitle: "Document Result",
      modelNeedsKey: "This model needs an API key. Set a model key first.",
      noRag: "This file has no RAG chunks yet. PDF/DOCX files can be queried after processing completes.",
    },
    meetings: {
      eyebrow: "NAS Index Search",
      title: "NAS Meeting Library",
      searchLabel: "Search",
      searchPlaceholder: "Search NAS meeting records",
      emptyList: "No meeting records yet",
      emptyDetail: "Select a NAS meeting asset to review audio and transcript",
      waitingExcerpt: "Transcript will appear after processing finishes",
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
      loading: "Loading...",
      allProviders: "All Providers",
      selectProviderFirst: "Select a provider first",
      selectModel: "Select a model",
      configureKey: "Set API Key",
      keyNotSet: "API Key not set",
      keyReady: "{provider} API Key is active for this session",
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
      promptLabel: "Prompt",
      promptPlaceholder: "Enter content to send to the selected model",
      runModel: "Send",
      useTitle: "Use {model}",
      useWithKey: "API Key Mode",
      useWithFreeQuota: "Free Real Model Mode",
      useNeedsKey: "API Key Required",
      promptRequired: "Enter a prompt first",
      noAccess: "This model requires an API key. Set a key before sending.",
      responseTitle: "Model Response",
      responseFailed: "Model Call Failed",
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
      processing: "Processing",
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
  selectedProvider: "",
  selectedLlmId: "",
  selectedPricing: null,
  apiKeys: {},
  llmCalls: [],
  nasAssets: [],
  selectedAssetId: null,
  selectedAsset: null,
  assetSelectedProvider: "",
  assetSelectedLlmId: "",
  assetSelectedPricing: null,
  keyModalPricing: null,
};

const els = {
  loginView: document.querySelector("#loginView"),
  appView: document.querySelector("#appView"),
  loginForm: document.querySelector("#loginForm"),
  loginError: document.querySelector("#loginError"),
  currentUser: document.querySelector("#currentUser"),
  logoutButton: document.querySelector("#logoutButton"),
  viewTitle: document.querySelector("#viewTitle"),
  langOptions: [...document.querySelectorAll(".lang-option")],
  navItems: [...document.querySelectorAll(".nav-item")],
  sections: {
    dashboard: document.querySelector("#dashboardSection"),
    record: document.querySelector("#recordSection"),
    upload: document.querySelector("#uploadSection"),
    meetings: document.querySelector("#meetingsSection"),
    aiwork: document.querySelector("#aiworkSection"),
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
  activityFeed: document.querySelector("#activityFeed"),
  meetingSearch: document.querySelector("#meetingSearch"),
  meetingList: document.querySelector("#meetingList"),
  meetingDetail: document.querySelector("#meetingDetail"),
  toastHost: document.querySelector("#toastHost"),
  llmProviderSelect: document.querySelector("#llmProviderSelect"),
  llmModelSelect: document.querySelector("#llmModelSelect"),
  pricingPanel: document.querySelector("#pricingPanel"),
  providerSummary: document.querySelector("#providerSummary"),
  openKeyModalButton: document.querySelector("#openKeyModalButton"),
  keyStatus: document.querySelector("#keyStatus"),
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
  runModelButton: document.querySelector("#runModelButton"),
  modelResponseBox: document.querySelector("#modelResponseBox"),
  llmCallSearch: document.querySelector("#llmCallSearch"),
  llmCallHistory: document.querySelector("#llmCallHistory"),
  nasUploadForm: document.querySelector("#nasUploadForm"),
  nasFileInput: document.querySelector("#nasFileInput"),
  nasAssetTitleInput: document.querySelector("#nasAssetTitleInput"),
  nasAssetSearch: document.querySelector("#nasAssetSearch"),
  nasAssetList: document.querySelector("#nasAssetList"),
  nasAssetDetail: document.querySelector("#nasAssetDetail"),
  nasUploadDialog: document.querySelector("#nasUploadDialog"),
  closeNasUploadDialog: document.querySelector("#closeNasUploadDialog"),
  confirmNasUploadDialog: document.querySelector("#confirmNasUploadDialog"),
  nasUploadDialogMessage: document.querySelector("#nasUploadDialogMessage"),
};

function t(key, replacements = {}) {
  const value = key.split(".").reduce((current, part) => current?.[part], messages[state.lang]);
  const text = typeof value === "string" ? value : key;
  return Object.entries(replacements).reduce((result, [name, replacement]) => {
    return result.replaceAll(`{${name}}`, replacement);
  }, text);
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
  renderLlmCallHistory();
  renderNasAssetList();
  renderNasAssetDetail();
  if (!els.apiKeyModal.hidden) renderKeyModal();
  if (state.user) renderCurrentUser();
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || t("errors.requestFailed"));
  }
  return response.json();
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
  closeWebSocket();
}

async function showApp() {
  els.loginView.hidden = true;
  els.appView.hidden = false;
  renderCurrentUser();
  switchView("dashboard");
  connectWebSocket();
  await loadMeetings();
  await loadLlmCatalog();
  await loadLlmCalls();
  await loadNasAssets();
}

function renderCurrentUser() {
  els.currentUser.textContent = `${state.user.username} · ${state.user.role}`;
}

function switchView(name) {
  Object.entries(els.sections).forEach(([key, section]) => {
    section.hidden = key !== name;
  });
  els.navItems.forEach((item) => item.classList.toggle("active", item.dataset.view === name));
  els.viewTitle.textContent = t(`nav.${name}`);
  if (name === "meetings") loadMeetings();
  if (name === "upload") loadNasAssets();
}

function currentViewName() {
  const active = els.navItems.find((item) => item.classList.contains("active"));
  return active?.dataset.view || "dashboard";
}

async function loadMeetings() {
  const params = new URLSearchParams();
  const query = els.meetingSearch.value.trim();
  if (query) params.set("q", query);
  state.meetings = await api(`/api/meetings${params.toString() ? `?${params}` : ""}`);
  renderMetrics();
  renderMeetingList();
}

async function loadLlmCatalog() {
  state.llmCatalog = await api("/api/llm/models");
  renderLlmControls();
  renderPricingPanel();
}

async function loadLlmCalls() {
  const params = new URLSearchParams();
  const query = els.llmCallSearch.value.trim();
  if (query) params.set("q", query);
  state.llmCalls = await api(`/api/llm/calls${params.toString() ? `?${params}` : ""}`);
  renderLlmCallHistory();
}

async function loadNasAssets() {
  const params = new URLSearchParams();
  const query = els.nasAssetSearch.value.trim();
  if (query) params.set("q", query);
  state.nasAssets = await api(`/api/nas-assets${params.toString() ? `?${params}` : ""}`);
  renderNasAssetList();
  if (state.selectedAssetId) {
    const stillExists = state.nasAssets.some((asset) => asset.id === state.selectedAssetId);
    if (stillExists) await selectNasAsset(state.selectedAssetId);
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

async function selectNasAsset(id) {
  state.selectedAssetId = id;
  renderNasAssetList();
  state.selectedAsset = await api(`/api/nas-assets/${id}`);
  renderNasAssetDetail();
}

function renderNasAssetDetail() {
  const asset = state.selectedAsset;
  if (!asset) {
    els.nasAssetDetail.innerHTML = `<div class="empty-state">${t("upload.emptyDetail")}</div>`;
    return;
  }

  const chunks = asset.chunks || [];
  const canAsk = ["pdf", "docx"].includes(asset.category) && asset.chunk_count > 0;
  els.nasAssetDetail.innerHTML = `
    <div class="asset-detail-header">
      <div>
        <p class="eyebrow">${escapeHtml(asset.category.toUpperCase())} · ${escapeHtml(asset.analyzer || "-")}</p>
        <h3>${escapeHtml(asset.title)}</h3>
      </div>
      <span class="badge ${escapeHtml(asset.status)}">${statusLabel(asset.status)}</span>
    </div>
    <div class="asset-meta-grid">
      ${assetMeta(t("upload.owner"), asset.owner_username || `#${asset.user_id}`)}
      ${assetMeta(t("upload.filename"), asset.original_filename)}
      ${assetMeta(t("upload.fileSize"), formatBytes(asset.file_size))}
      ${assetMeta(t("upload.chunkCount"), asset.chunk_count)}
    </div>
    <section class="asset-summary">
      <strong>${escapeHtml(t("upload.summary"))}</strong>
      <p>${escapeHtml(asset.summary || asset.error_message || processingText(asset.status, asset.error_message))}</p>
    </section>
    ${chunks.length ? renderRagChunks(chunks) : ""}
    ${canAsk ? renderDocumentAskPanel() : `<div class="empty-state compact">${t("upload.noRag")}</div>`}
  `;
  renderAssetLlmControls();
}

function assetMeta(label, value) {
  return `<span><b>${escapeHtml(label)}</b>${escapeHtml(value ?? "-")}</span>`;
}

function renderRagChunks(chunks) {
  return `
    <section class="rag-chunk-panel">
      <strong>${escapeHtml(t("upload.chunks"))}</strong>
      <div class="rag-chunk-list">
        ${chunks
          .map((chunk) => `<p><b>#${chunk.chunk_index}</b>${escapeHtml(chunk.content.slice(0, 260))}</p>`)
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
      <div class="llm-form-grid compact">
        <label>
          <span>${escapeHtml(t("aiwork.providerLabel"))}</span>
          <select id="assetLlmProviderSelect"></select>
        </label>
        <label>
          <span>${escapeHtml(t("aiwork.modelLabel"))}</span>
          <select id="assetLlmModelSelect"></select>
        </label>
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

function renderAssetLlmControls() {
  const providerSelect = document.querySelector("#assetLlmProviderSelect");
  const modelSelect = document.querySelector("#assetLlmModelSelect");
  if (!providerSelect || !modelSelect) return;
  if (!state.llmCatalog) {
    providerSelect.innerHTML = `<option value="">${t("aiwork.loading")}</option>`;
    modelSelect.innerHTML = `<option value="">${t("aiwork.loading")}</option>`;
    return;
  }

  providerSelect.innerHTML = [
    `<option value="">${t("aiwork.allProviders")}</option>`,
    ...state.llmCatalog.providers.map((provider) => `<option value="${escapeHtml(provider.name)}">${escapeHtml(provider.name)}</option>`),
  ].join("");
  providerSelect.value = state.assetSelectedProvider;

  const models = state.assetSelectedProvider
    ? state.llmCatalog.models.filter((model) => model.provider === state.assetSelectedProvider)
    : state.llmCatalog.models;
  modelSelect.innerHTML = [
    `<option value="">${t("aiwork.selectModel")}</option>`,
    ...models.map((model) => `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</option>`),
  ].join("");
  modelSelect.value = state.assetSelectedLlmId;
}

async function selectAssetLlmModel(modelId) {
  state.assetSelectedLlmId = modelId;
  state.assetSelectedPricing = null;
  if (!modelId) return;
  state.assetSelectedPricing = await api(`/api/llm/pricing/${encodeURIComponent(modelId)}`);
  const model = state.assetSelectedPricing.model;
  const hasKey = Boolean(state.apiKeys[providerKeyId(model.provider)]);
  if (model.free_tier.requires_api_key_for_real_call && !hasKey) {
    openKeyModalForPricing(state.assetSelectedPricing);
  }
}

async function uploadNasAsset(event) {
  event.preventDefault();
  const file = els.nasFileInput.files[0];
  if (!file) {
    showToast(t("upload.uploadRequired"), t("toast.nasReceived"));
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", els.nasAssetTitleInput.value.trim());
  const response = await fetch("/api/nas-assets/upload", {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    showToast(t("upload.uploadFailed"), t("toast.savedFailed"));
    return;
  }

  const asset = await response.json();
  els.nasUploadForm.reset();
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
  if (!state.assetSelectedLlmId) {
    showToast(t("upload.modelRequired"), t("upload.questionTitle"));
    return;
  }
  if (!question) {
    showToast(t("upload.questionRequired"), t("upload.questionTitle"));
    return;
  }

  if (!state.assetSelectedPricing) {
    await selectAssetLlmModel(state.assetSelectedLlmId);
  }
  const model = state.assetSelectedPricing?.model;
  const hasKey = model ? Boolean(state.apiKeys[providerKeyId(model.provider)]) : false;
  const canUseFreeQuota = Boolean(model?.free_tier.available && !model.free_tier.requires_api_key_for_real_call);
  if (model && !hasKey && !canUseFreeQuota) {
    showToast(t("upload.modelNeedsKey"), model.provider);
    openKeyModalForPricing(state.assetSelectedPricing);
    return;
  }

  try {
    const result = await api(`/api/nas-assets/${state.selectedAsset.id}/ask`, {
      method: "POST",
      body: JSON.stringify({
        model_id: state.assetSelectedLlmId,
        question,
        api_key: model ? state.apiKeys[providerKeyId(model.provider)] || "" : "",
      }),
    });
    answerBox.hidden = false;
    answerBox.classList.remove("error");
    answerBox.innerHTML = `<strong>${escapeHtml(t("upload.answerTitle"))} · ${escapeHtml(result.model)}</strong><pre>${escapeHtml(result.answer)}</pre>`;
    await loadLlmCalls();
  } catch (error) {
    answerBox.hidden = false;
    answerBox.classList.add("error");
    answerBox.innerHTML = `<strong>${escapeHtml(t("aiwork.responseFailed"))}</strong><pre>${escapeHtml(error.message)}</pre>`;
    await loadLlmCalls();
  }
}

function renderLlmControls() {
  if (!state.llmCatalog) {
    els.llmProviderSelect.innerHTML = `<option value="">${t("aiwork.loading")}</option>`;
    els.llmModelSelect.innerHTML = `<option value="">${t("aiwork.selectProviderFirst")}</option>`;
    els.llmModelSelect.disabled = true;
    return;
  }

  const providers = state.llmCatalog.providers;
  els.llmProviderSelect.innerHTML = [
    `<option value="">${t("aiwork.allProviders")}</option>`,
    ...providers.map((provider) => {
      return `<option value="${escapeHtml(provider.name)}">${escapeHtml(provider.name)} (${provider.model_count})</option>`;
    }),
  ].join("");
  els.llmProviderSelect.value = state.selectedProvider;

  const models = filteredLlmModels();
  els.llmModelSelect.disabled = models.length === 0;
  els.llmModelSelect.innerHTML = [
    `<option value="">${t("aiwork.selectModel")}</option>`,
    ...models.map((model) => {
      return `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</option>`;
    }),
  ].join("");
  els.llmModelSelect.value = state.selectedLlmId;

  els.providerSummary.innerHTML = providers
    .map((provider) => `<span>${escapeHtml(provider.name)} · ${provider.model_count}</span>`)
    .join("");
}

function filteredLlmModels() {
  if (!state.llmCatalog) return [];
  if (!state.selectedProvider) return state.llmCatalog.models;
  return state.llmCatalog.models.filter((model) => model.provider === state.selectedProvider);
}

async function selectLlmModel(modelId) {
  state.selectedLlmId = modelId;
  state.selectedPricing = null;
  renderPricingPanel();
  renderKeyStatus();
  renderModelUsePanel();
  if (!modelId) return;

  const pricing = await api(`/api/llm/pricing/${encodeURIComponent(modelId)}`);
  state.selectedPricing = pricing;
  renderPricingPanel();
  renderKeyStatus();
  renderModelUsePanel();
  const model = state.selectedPricing.model;
  const hasKey = Boolean(state.apiKeys[providerKeyId(model.provider)]);
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
      <p>${escapeHtml(model.note)}</p>
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

  const providerKey = providerKeyId(model.provider);
  if (state.apiKeys[providerKey]) {
    els.keyStatus.textContent = t("aiwork.keyReady", { provider: model.provider });
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
    els.modelUsePanel.hidden = true;
    els.modelResponseBox.hidden = true;
    return;
  }

  const hasKey = Boolean(state.apiKeys[providerKeyId(model.provider)]);
  const canUseFreeQuota = Boolean(model.free_tier.available && !model.free_tier.requires_api_key_for_real_call);
  els.modelUsePanel.hidden = false;
  els.modelUseTitle.textContent = t("aiwork.useTitle", { model: model.name });
  els.modelUseMode.textContent = hasKey
    ? t("aiwork.useWithKey")
    : canUseFreeQuota
      ? t("aiwork.useWithFreeQuota")
      : t("aiwork.useNeedsKey");
  els.modelUseMode.classList.toggle("ready", hasKey || canUseFreeQuota);
  els.runModelButton.disabled = !hasKey && !canUseFreeQuota;
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
  renderAssetLlmControls();
  closeKeyModal();
  showToast(t("keyModal.saved"), model.provider);
}

async function runSelectedModel() {
  const model = state.selectedPricing?.model;
  if (!model) return;

  const prompt = els.llmPromptInput.value.trim();
  if (!prompt) {
    showToast(t("aiwork.promptRequired"), t("aiwork.responseTitle"));
    return;
  }

  const hasApiKey = Boolean(state.apiKeys[providerKeyId(model.provider)]);
  const canUseFreeQuota = Boolean(model.free_tier.available && !model.free_tier.requires_api_key_for_real_call);
  if (!hasApiKey && !canUseFreeQuota) {
    showToast(t("aiwork.noAccess"), model.provider);
    openKeyModal();
    return;
  }

  els.runModelButton.disabled = true;
  try {
    const result = await api("/api/llm/run", {
      method: "POST",
      body: JSON.stringify({
        model_id: model.id,
        prompt,
        api_key: state.apiKeys[providerKeyId(model.provider)] || "",
      }),
    });
    els.modelResponseBox.hidden = false;
    els.modelResponseBox.classList.remove("error");
    els.modelResponseBox.innerHTML = `
      <strong>${t("aiwork.responseTitle")} · ${escapeHtml(result.model)}</strong>
      <div class="llm-usage-grid inline">
        ${usageChip(t("aiwork.usageInput"), result.usage?.input_tokens)}
        ${usageChip(t("aiwork.usageOutput"), result.usage?.output_tokens)}
        ${usageChip(t("aiwork.usageTotal"), result.usage?.total_tokens)}
        ${usageChip(t("aiwork.remainingTokens"), result.usage?.remaining_tokens)}
        ${usageChip(t("aiwork.remainingBalance"), result.usage?.remaining_balance)}
      </div>
      <pre>${escapeHtml(result.answer)}</pre>
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

function renderMetrics() {
  els.totalMeetings.textContent = state.meetings.length;
  els.processingMeetings.textContent = state.meetings.filter((meeting) => meeting.status === "processing").length;
  els.completedMeetings.textContent = state.meetings.filter((meeting) => meeting.status === "completed").length;
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
          <p>${sourceLabel(meeting.source)} · ${created}</p>
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
    </div>
    <audio controls src="/api/meetings/${meeting.id}/audio"></audio>
    <div class="transcript-box">${escapeHtml(meeting.transcript || processingText(meeting.status, meeting.error_message))}</div>
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
      await loadNasAssets();
      return;
    }
    await loadMeetings();
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
  formData.append("audio", blob, `browser-recording-${timestamp}.webm`);

  const response = await fetch("/api/meetings/upload", {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    updateRecordingUi("idle");
    showToast(t("record.uploadFailed"), t("toast.savedFailed"));
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
  if (status === "failed") return error || t("meetings.failedText");
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
els.navItems.forEach((item) => item.addEventListener("click", () => switchView(item.dataset.view)));
document.querySelectorAll("[data-jump]").forEach((item) => {
  item.addEventListener("click", () => switchView(item.dataset.jump));
});
els.startRecord.addEventListener("click", () => startRecording().catch((error) => showToast(error.message, t("record.unavailable"))));
els.pauseRecord.addEventListener("click", pauseRecording);
els.stopRecord.addEventListener("click", stopRecording);
els.meetingSearch.addEventListener("input", debounce(loadMeetings, 220));
els.llmCallSearch.addEventListener("input", debounce(loadLlmCalls, 220));
els.nasAssetSearch.addEventListener("input", debounce(loadNasAssets, 220));
els.nasUploadForm.addEventListener("submit", (event) => uploadNasAsset(event).catch((error) => showToast(error.message, t("upload.uploadFailed"))));
els.meetingList.addEventListener("click", (event) => {
  const row = event.target.closest("[data-meeting-id]");
  if (row) selectMeeting(Number(row.dataset.meetingId));
});
els.nasAssetList.addEventListener("click", (event) => {
  const row = event.target.closest("[data-asset-id]");
  if (row) selectNasAsset(Number(row.dataset.assetId));
});
els.nasAssetDetail.addEventListener("change", (event) => {
  if (event.target.id === "assetLlmProviderSelect") {
    state.assetSelectedProvider = event.target.value;
    state.assetSelectedLlmId = "";
    state.assetSelectedPricing = null;
    renderAssetLlmControls();
  }
  if (event.target.id === "assetLlmModelSelect") {
    selectAssetLlmModel(event.target.value).catch((error) => showToast(error.message, t("errors.requestFailed")));
  }
});
els.nasAssetDetail.addEventListener("click", (event) => {
  if (event.target.id === "askAssetButton") {
    askSelectedAsset().catch((error) => showToast(error.message, t("errors.requestFailed")));
  }
});
els.llmProviderSelect.addEventListener("change", () => {
  state.selectedProvider = els.llmProviderSelect.value;
  state.selectedLlmId = "";
  state.selectedPricing = null;
  renderLlmControls();
  renderPricingPanel();
  renderKeyStatus();
});
els.llmModelSelect.addEventListener("change", () => {
  selectLlmModel(els.llmModelSelect.value).catch((error) => showToast(error.message, t("errors.requestFailed")));
});
els.openKeyModalButton.addEventListener("click", openKeyModal);
els.closeKeyModal.addEventListener("click", closeKeyModal);
els.cancelKeyButton.addEventListener("click", closeKeyModal);
els.saveKeyButton.addEventListener("click", saveApiKeyForSession);
els.runModelButton.addEventListener("click", () => runSelectedModel().catch((error) => showToast(error.message, t("errors.requestFailed"))));
els.apiKeyModal.addEventListener("click", (event) => {
  if (event.target === els.apiKeyModal) closeKeyModal();
});
els.closeNasUploadDialog.addEventListener("click", closeNasUploadDialog);
els.confirmNasUploadDialog.addEventListener("click", () => {
  closeNasUploadDialog();
  switchView("upload");
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

bootstrap();
