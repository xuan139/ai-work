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
      models: "模型管理",
      meetings: "資料庫查詢",
      aiwork: "AI Work",
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
      model: "公司模型",
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
        copy: "上傳 audio、video、PDF、DOCX 等資料，NAS 收件後進入所選 ASR、影片分析或 RAG 流程。",
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
      asrKeyPlaceholder: "只用於本次會議錄音",
      asrLanguages: "語言",
      asrBestFor: "適合",
      asrReady: "本地模型已就緒，可直接處理錄音。",
      asrDownloading: "模型正在下載：{progress}%。錄音可先保存，但轉寫需等下載完成。",
      asrNotReady: "本地模型尚未就緒，請到 NAS 模型管理完成安裝，或改選已就緒模型。",
      asrCloud: "此模型由雲端處理，API Key 只用於本次錄音，不會寫入資料庫。",
      asrKeyRequired: "{model} 需要 API Key，請先輸入後再開始錄音。",
      asrModelRequired: "請先選擇語音處理模型。",
      translationTitle: "步驟 2：逐字稿翻譯",
      translationCopy: "可選擇目標語言與本地或雲端 LLM；原文與譯文會分開保存。",
      translationEnable: "啟用翻譯",
      translationTarget: "目標語言",
      translationMode: "翻譯位置",
      translationModel: "翻譯模型",
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
      copy: "支援 audio、video、圖片、PDF、DOCX 與一般文件。NAS 收到圖片後會執行 OCR、建立向量與可追溯原圖的 RAG 索引。",
      fileLabel: "選擇檔案",
      titleLabel: "資料名稱",
      titlePlaceholder: "例如：董事會錄音、產品簡報 PDF",
      asrTitle: "步驟 1：音訊轉寫模型",
      asrCopy: "上傳 audio 時可選本地或雲端 ASR；其他檔案會自動略過此設定。",
      asrModeLabel: "執行位置",
      asrModeLocal: "本地 NAS",
      asrModeCloud: "雲端 API",
      asrModelLabel: "ASR 模型",
      asrKeyLabel: "API Key",
      asrKeyPlaceholder: "只用於本次 audio 上傳",
      asrHint: "本地模型適合 NAS 私有化；雲端模型需要 API Key，Key 只用於本次上傳，不寫入資料庫。",
      translationTitle: "步驟 2：逐字稿翻譯",
      translationCopy: "只套用於 audio；可指定目標語言與翻譯 LLM。",
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
      questionCopy: "圖片、文件或逐字稿已建立 RAG chunks，可選擇模型後對此資產提問。",
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
        translationCopy: "依使用者指定的目標語言，調用 NAS 本地 Qwen 或所選雲端 LLM；原文與譯文分開入庫。",
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
        llmCopy: "使用 Qwen3 query 向量與中英文關鍵字混合排序，將命中的頁碼與內容交給選定大模型回答。",
      },
    },
    models: {
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
      promptLabel: "輸入內容",
      promptPlaceholder: "請輸入要交給模型處理的內容",
      promptSearchHint: "先輸入關鍵字，再查詢",
      suggestionsLabel: "相似歷史問題",
      suggestionCached: "NAS 快取",
      suggestionHistory: "歷史問題",
      runModel: "送出",
      forceRunModel: "強制送出",
      forceRunHint: "忽略快取並實際呼叫模型，可能產生費用",
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
      models: "Model Management",
      meetings: "Knowledge Search",
      aiwork: "AI Work",
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
      model: "Company Model",
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
        copy: "Upload audio, video, PDF, DOCX, and other assets into the selected ASR, video analysis, or RAG workflow.",
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
      asrKeyPlaceholder: "Used only for this meeting recording",
      asrLanguages: "Languages",
      asrBestFor: "Best for",
      asrReady: "The local model is ready and can process recordings.",
      asrDownloading: "Model download in progress: {progress}%. The recording can be saved, but transcription waits for completion.",
      asrNotReady: "The local model is not ready. Complete setup in NAS Model Management or choose a ready model.",
      asrCloud: "This model runs in the cloud. The API key is used only for this recording and is not stored in the database.",
      asrKeyRequired: "{model} requires an API key. Enter it before recording.",
      asrModelRequired: "Choose a speech model first.",
      translationTitle: "Step 2: Transcript Translation",
      translationCopy: "Choose a target language and a local or cloud LLM. The source transcript and translation are stored separately.",
      translationEnable: "Enable translation",
      translationTarget: "Target language",
      translationMode: "Translation location",
      translationModel: "Translation model",
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
      copy: "Supports audio, video, images, PDF, DOCX, and general files. Images are OCR processed, embedded, and indexed for RAG with traceable source previews.",
      fileLabel: "File",
      titleLabel: "Asset Name",
      titlePlaceholder: "Example: board audio, product PDF",
      asrTitle: "Step 1: Audio Transcription Model",
      asrCopy: "For audio uploads, choose local or cloud ASR. Other file types ignore this setting.",
      asrModeLabel: "Execution Location",
      asrModeLocal: "Local NAS",
      asrModeCloud: "Cloud API",
      asrModelLabel: "ASR Model",
      asrKeyLabel: "API Key",
      asrKeyPlaceholder: "Only used for this audio upload",
      asrHint: "Local models fit private NAS deployments. Cloud models need an API key, used only for this upload and not written to the database.",
      translationTitle: "Step 2: Transcript Translation",
      translationCopy: "Applies to audio only. Choose the target language and translation LLM.",
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
      questionCopy: "This image, document, or transcript has RAG chunks. Select a model and ask a question.",
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
        translationCopy: "Uses the chosen local Qwen or cloud LLM for the selected language and stores source and translated text separately.",
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
        llmCopy: "Ranks chunks with a Qwen3 query vector and multilingual keywords, then sends matched pages to the selected model.",
      },
    },
    models: {
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
      suggestionsLabel: "Similar Previous Questions",
      suggestionCached: "NAS Cache",
      suggestionHistory: "History",
      runModel: "Send",
      forceRunModel: "Force Send",
      forceRunHint: "Bypass the cache and call the model; charges may apply",
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
  selectedPricing: null,
  apiKeys: {},
  llmCalls: [],
  llmSuggestions: [],
  activeLlmSuggestion: -1,
  llmSuggestionRequestId: 0,
  nasAssets: [],
  selectedAssetId: null,
  selectedAsset: null,
  assetSelectedLlmMode: "local",
  assetSelectedProvider: "Local NAS",
  assetSelectedLlmId: "local:qwen3-4b",
  assetSelectedPricing: null,
  keyModalPricing: null,
  users: [],
  passwordResetUserId: null,
  lineAdminSources: [],
  lineAdminModels: [],
  lineServiceConnected: false,
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
    models: document.querySelector("#modelsSection"),
    meetings: document.querySelector("#meetingsSection"),
    aiwork: document.querySelector("#aiworkSection"),
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
  llmPromptSuggestions: document.querySelector("#llmPromptSuggestions"),
  runModelButton: document.querySelector("#runModelButton"),
  forceRunModelButton: document.querySelector("#forceRunModelButton"),
  modelResponseBox: document.querySelector("#modelResponseBox"),
  llmCallSearch: document.querySelector("#llmCallSearch"),
  llmCallHistory: document.querySelector("#llmCallHistory"),
  nasUploadForm: document.querySelector("#nasUploadForm"),
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
  nasUploadDialog: document.querySelector("#nasUploadDialog"),
  closeNasUploadDialog: document.querySelector("#closeNasUploadDialog"),
  confirmNasUploadDialog: document.querySelector("#confirmNasUploadDialog"),
  nasUploadDialogMessage: document.querySelector("#nasUploadDialogMessage"),
  accountNav: document.querySelector("#accountNav"),
  lineAdminNav: document.querySelector("#lineAdminNav"),
  lineGroupTotal: document.querySelector("#lineGroupTotal"),
  lineGroupApproved: document.querySelector("#lineGroupApproved"),
  lineMonthlyCalls: document.querySelector("#lineMonthlyCalls"),
  lineMonthlyTokens: document.querySelector("#lineMonthlyTokens"),
  refreshLineAdmin: document.querySelector("#refreshLineAdmin"),
  lineServiceNotice: document.querySelector("#lineServiceNotice"),
  lineAdminList: document.querySelector("#lineAdminList"),
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
  renderLlmSuggestions();
  renderLlmCallHistory();
  renderNasAssetList();
  renderNasAssetDetail();
  renderRecordingAsrControls();
  renderAsrControls();
  renderTranslationControls("record");
  renderTranslationControls("audio");
  renderLinePushControls();
  renderVideoControls();
  renderLocalModelManager();
  renderLineAdmin();
  renderAccountList();
  if (state.passwordResetUserId) {
    const resetUser = state.users.find((user) => user.id === state.passwordResetUserId);
    if (resetUser) els.passwordResetAccount.textContent = t("accounts.resetFor", { username: resetUser.username });
  }
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
  els.accountNav.hidden = state.user.role !== "admin";
  els.lineAdminNav.hidden = state.user.role !== "admin";
  els.addCustomModelButton.hidden = state.user.role !== "admin";
  switchView("dashboard");
  connectWebSocket();
  await loadMeetings();
  await loadLlmCatalog();
  await loadAsrCatalog();
  await loadVideoCatalog();
  await loadLocalModels();
  await loadLineGroups();
  await loadLlmCalls();
  await loadNasAssets();
  if (state.user.role === "admin") {
    await loadLineAdmin();
    await loadAccounts();
  }
}

function renderCurrentUser() {
  els.currentUser.textContent = `${state.user.username} · ${t(`accounts.roles.${state.user.role}`)}`;
}

function switchView(name) {
  if (["lineAdmin", "accounts"].includes(name) && state.user?.role !== "admin") name = "dashboard";
  Object.entries(els.sections).forEach(([key, section]) => {
    section.hidden = key !== name;
  });
  els.navItems.forEach((item) => item.classList.toggle("active", item.dataset.view === name));
  els.viewTitle.textContent = t(`nav.${name}`);
  if (name === "meetings") loadMeetings();
  if (name === "upload") loadNasAssets();
  if (name === "models") loadLocalModels();
  if (name === "lineAdmin") loadLineAdmin();
  if (name === "accounts") loadAccounts();
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
  const selectedModelExists = state.llmCatalog.models.some(
    (model) => model.id === state.selectedLlmId && model.execution === state.selectedLlmMode
  );
  if (!selectedModelExists) {
    const fallback = defaultLlmModelForMode(state.selectedLlmMode);
    state.selectedProvider = fallback?.provider || "";
    state.selectedLlmId = fallback?.id || "";
  }
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
  renderRecordingAsrControls();
  renderAsrControls();
}

async function loadVideoCatalog() {
  state.videoCatalog = await api("/api/video/models");
  renderVideoControls();
}

async function loadLocalModels() {
  state.localModels = await api("/api/local-models");
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
  const canAsk = ["audio", "video", "pdf", "docx", "image"].includes(asset.category) && asset.chunk_count > 0;
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
      ${asset.category === "audio" ? assetMeta(t("upload.selectedAsr"), selectedAsrLabel(asset)) : ""}
      ${asset.category === "audio" && asset.processor_config?.translation_enabled ? assetMeta(t("upload.selectedTranslation"), selectedTranslationLabel(asset)) : ""}
      ${asset.category === "video" ? assetMeta(t("upload.selectedVideo"), selectedVideoLabel(asset)) : ""}
    </div>
    <section class="asset-summary">
      <strong>${escapeHtml(t("upload.summary"))}</strong>
      <p>${escapeHtml(asset.summary || asset.error_message || processingText(asset.status, asset.error_message))}</p>
    </section>
    ${renderAiAnalysisHistory(asset.ai_analyses || [])}
    ${renderAssetProcessTimeline(asset, chunks)}
    ${chunks.length ? renderRagChunks(chunks) : ""}
    ${canAsk ? renderDocumentAskPanel() : `<div class="empty-state compact">${t("upload.noRag")}</div>`}
  `;
  renderAssetLlmControls();
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
  els.recordAsrKeyField.hidden = !selected?.requires_api_key;
  if (selected) els.recordAsrKeyLabel.textContent = selected.api_key_label || t("upload.asrKeyLabel");
  renderAsrRecommendation(els.recordAsrRecommendation, selected);
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
  els.audioAsrKeyField.hidden = !selected?.requires_api_key;
  if (selected) els.audioAsrKeyLabel.textContent = selected.api_key_label || t("upload.asrKeyLabel");
  renderAsrRecommendation(els.audioAsrRecommendation, selected);
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
  const needsKey = Boolean(selected?.free_tier?.requires_api_key_for_real_call);
  keyField.hidden = !enabled || !needsKey;
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
  const keyInput = isRecord ? els.recordTranslationApiKeyInput : els.audioTranslationApiKeyInput;
  const model = (state.llmCatalog?.models || []).find((item) => item.id === modelId);
  if (!model) throw new Error(t("record.translationModelRequired"));
  if (model.free_tier?.requires_api_key_for_real_call && !keyInput.value.trim()) {
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
      loadLocalModels().catch(() => {});
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
      <div class="model-mode-switch compact" role="group" aria-label="${escapeHtml(t("aiwork.executionLabel"))}">
        <button class="${state.assetSelectedLlmMode === "local" ? "active" : ""}" type="button" data-asset-llm-mode="local" aria-pressed="${state.assetSelectedLlmMode === "local"}">${escapeHtml(t("aiwork.localModels"))}</button>
        <button class="${state.assetSelectedLlmMode === "cloud" ? "active" : ""}" type="button" data-asset-llm-mode="cloud" aria-pressed="${state.assetSelectedLlmMode === "cloud"}">${escapeHtml(t("aiwork.cloudModels"))}</button>
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

  document.querySelectorAll("[data-asset-llm-mode]").forEach((button) => {
    const active = button.dataset.assetLlmMode === state.assetSelectedLlmMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  const modeModels = llmModelsForMode(state.assetSelectedLlmMode);
  const providers = [...new Set(modeModels.map((model) => model.provider))];
  providerSelect.innerHTML = [
    `<option value="">${t("aiwork.allProviders")}</option>`,
    ...providers.map((provider) => `<option value="${escapeHtml(provider)}">${escapeHtml(provider)}</option>`),
  ].join("");
  providerSelect.value = state.assetSelectedProvider;

  const models = state.assetSelectedProvider
    ? modeModels.filter((model) => model.provider === state.assetSelectedProvider)
    : modeModels;
  modelSelect.innerHTML = [
    `<option value="">${t("aiwork.selectModel")}</option>`,
    ...models.map((model) => `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)} · ${escapeHtml(model.name)}</option>`),
  ].join("");
  modelSelect.value = state.assetSelectedLlmId;
}

async function selectAssetLlmMode(mode) {
  state.assetSelectedLlmMode = mode;
  const fallback = defaultLlmModelForMode(mode);
  state.assetSelectedProvider = fallback?.provider || "";
  state.assetSelectedLlmId = fallback?.id || "";
  state.assetSelectedPricing = null;
  renderAssetLlmControls();
  if (fallback) await selectAssetLlmModel(fallback.id);
}

async function selectAssetLlmModel(modelId) {
  state.assetSelectedLlmId = modelId;
  state.assetSelectedPricing = null;
  if (!modelId) return;
  state.assetSelectedPricing = await api(`/api/llm/pricing/${encodeURIComponent(modelId)}`);
  const model = state.assetSelectedPricing.model;
  const hasKey = modelHasApiAccess(model);
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
  const isAudio = file.type.startsWith("audio/") || /\.(wav|mp3|m4a|webm|ogg|flac|aac)$/i.test(file.name);
  const selectedAsr = (state.asrCatalog?.models || []).find((model) => model.id === state.selectedAsrModelId);
  if (isAudio && selectedAsr?.requires_api_key && !els.audioAsrApiKeyInput.value.trim()) {
    showToast(t("record.asrKeyRequired", { model: selectedAsr.name }), t("upload.asrTitle"));
    return;
  }
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
  formData.append("audio_model_id", state.selectedAsrModelId);
  formData.append("audio_api_key", els.audioAsrApiKeyInput.value.trim());
  formData.append("audio_translation_enabled", String(state.audioTranslationEnabled));
  formData.append("audio_translation_target", state.audioTranslationTarget);
  formData.append("audio_translation_model_id", state.audioTranslationModelId);
  formData.append("audio_translation_api_key", els.audioTranslationApiKeyInput.value.trim());
  formData.append("video_model_id", state.selectedVideoModelId);
  formData.append("video_api_key", els.videoApiKeyInput.value.trim());
  const response = await fetch("/api/nas-assets/upload", {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: t("upload.uploadFailed") }));
    showToast(error.detail || t("upload.uploadFailed"), t("toast.savedFailed"));
    return;
  }

  const asset = await response.json();
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
  const hasKey = modelHasApiAccess(model);
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
  els.llmModelSelect.disabled = models.length === 0;
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
  if (!modelId) return;

  const pricing = await api(`/api/llm/pricing/${encodeURIComponent(modelId)}`);
  state.selectedPricing = pricing;
  renderPricingPanel();
  renderKeyStatus();
  renderModelUsePanel();
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

  const hasKey = modelHasApiAccess(model);
  const canUseFreeQuota = Boolean(model.free_tier.available && !model.free_tier.requires_api_key_for_real_call);
  els.modelUsePanel.hidden = false;
  els.modelUseTitle.textContent = t("aiwork.useTitle", { model: model.name });
  els.modelUseMode.textContent = model.provider === "Local NAS"
    ? t("aiwork.useLocalNas")
    : hasKey
    ? t("aiwork.useWithKey")
    : canUseFreeQuota
      ? t("aiwork.useWithFreeQuota")
      : t("aiwork.useNeedsKey");
  els.modelUseMode.classList.toggle("ready", hasKey || canUseFreeQuota);
  els.runModelButton.disabled = !hasKey && !canUseFreeQuota;
  els.forceRunModelButton.disabled = !hasKey && !canUseFreeQuota;
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
    const result = await api(`/api/llm/suggestions?model_id=${encodeURIComponent(modelId)}&q=${encodeURIComponent(query)}`);
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
        api_key: state.apiKeys[providerKeyId(model.provider)] || "",
        force_refresh: forceRefresh,
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
  const availabilityError = recordingAvailabilityError();
  if (availabilityError) throw new Error(availabilityError);
  const model = (state.asrCatalog?.models || []).find((item) => item.id === state.selectedRecordAsrModelId);
  if (!model) throw new Error(t("record.asrModelRequired"));
  if (model.requires_api_key && !els.recordAsrApiKeyInput.value.trim()) {
    throw new Error(t("record.asrKeyRequired", { model: model.name }));
  }
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
  formData.append("asr_model_id", state.selectedRecordAsrModelId);
  formData.append("asr_api_key", els.recordAsrApiKeyInput.value.trim());
  formData.append("translation_enabled", String(state.recordTranslationEnabled));
  formData.append("translation_target", state.recordTranslationTarget);
  formData.append("translation_model_id", state.recordTranslationModelId);
  formData.append("translation_api_key", els.recordTranslationApiKeyInput.value.trim());
  const lineGroup = state.lineGroups.find((group) => group.id === state.recordLineGroupId);
  formData.append("line_push_enabled", String(state.recordLinePushEnabled));
  formData.append("line_group_id", state.recordLineGroupId);
  formData.append("line_group_name", lineGroup?.name || "");
  formData.append("line_push_full_transcript", String(state.recordLineFullTranscript));
  formData.append("audio", blob, `browser-recording-${timestamp}.webm`);

  const response = await fetch("/api/meetings/upload", {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: t("record.uploadFailed") }));
    updateRecordingUi("idle");
    showToast(error.detail || t("record.uploadFailed"), t("toast.savedFailed"));
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
els.accountSearch.addEventListener("input", renderAccountList);
els.refreshLineAdmin.addEventListener("click", () => loadLineAdmin().catch((error) => showToast(error.message, t("lineAdmin.serviceUnavailable"))));
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
  const modeButton = event.target.closest("[data-asset-llm-mode]");
  if (modeButton) {
    selectAssetLlmMode(modeButton.dataset.assetLlmMode).catch((error) => showToast(error.message, t("errors.requestFailed")));
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
els.runModelButton.addEventListener("click", () => runSelectedModel().catch((error) => showToast(error.message, t("errors.requestFailed"))));
els.forceRunModelButton.addEventListener("click", () => runSelectedModel(true).catch((error) => showToast(error.message, t("errors.requestFailed"))));
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

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch((error) => {
      console.warn("PWA service worker registration failed", error);
    });
  });
}

bootstrap();
