const messages = {
  "zh-Hant": {
    documentTitle: "AI Work 會議入口",
    language: { label: "語言切換" },
    login: {
      eyebrow: "安全工作區",
      title: "AI Work 會議入口",
      copy: "登入後錄製會議、接收 NAS 新錄音提醒，並查詢歷史會議轉寫結果。",
      username: "使用者名稱",
      password: "密碼",
      submit: "登入系統",
    },
    sidebar: {
      subtitle: "會議智慧工作台",
      navLabel: "主導覽",
    },
    nav: {
      dashboard: "總覽",
      record: "會議記錄",
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
      eyebrow: "Demo 範圍",
      title: "錄音保存、NAS 發現、會議轉寫查詢",
      copy: "第一版聚焦會議資產進入系統後的完整鏈路：瀏覽器錄音上傳、NAS 檔案進入提醒、後台處理狀態，以及可搜尋的歷史會議記錄。",
    },
    metrics: {
      total: "會議記錄",
      processing: "處理中",
      completed: "已完成",
    },
    modules: {
      record: {
        title: "會議記錄",
        copy: "開啟麥克風錄製整場會議，保存原始語音並啟動轉寫。",
      },
      meetings: {
        title: "資料庫查詢",
        copy: "檢索會議標題、原始檔名和轉寫文本。",
      },
      aiwork: {
        copy: "預留入口，後續接會議摘要、行動項和問答。",
      },
    },
    record: {
      eyebrow: "瀏覽器錄音",
      title: "新建會議錄音",
      meetingTitle: "會議標題",
      titlePlaceholder: "例如：產品週會 09/09",
      start: "開始錄音",
      pause: "暫停",
      resume: "繼續",
      stop: "停止並保存",
      hint: "瀏覽器會請求麥克風權限。停止後系統會保存原始錄音並進入處理佇列。",
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
    meetings: {
      eyebrow: "知識查詢",
      title: "會議資料庫",
      searchLabel: "搜尋",
      searchPlaceholder: "輸入關鍵字查詢會議記錄",
      emptyList: "暫無會議記錄",
      emptyDetail: "選擇一條會議查看錄音和轉寫內容",
      waitingExcerpt: "等待處理完成後顯示轉寫內容",
      processingText: "正在處理轉寫，請稍候。",
      failedText: "處理失敗",
      sourceNas: "NAS 發現",
      sourceWeb: "網頁錄音",
    },
    aiwork: {
      eyebrow: "模型接入",
      copy: "選擇主流大模型後，系統會查詢該模型目前的公開費用，並提示輸入對應供應商 API Key。",
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
      sourcesCopy: "價格會變動，目前 demo 使用官方公開定價頁整理的快照。正式版建議做每日同步或管理員手動刷新。",
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
    },
    toast: {
      meetingDetected: "會議動態",
      meetingCompleted: "會議動態",
      meetingFailed: "處理失敗",
      savedFailed: "保存失敗",
      detected: "發現新的會議錄音《{title}》，已經開始處理",
      uploaded: "錄音《{title}》已保存，正在處理",
      completed: "會議《{title}》轉寫完成",
      failed: "會議《{title}》處理失敗",
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
      eyebrow: "Secure Workspace",
      title: "AI Work Meeting Portal",
      copy: "Sign in to record meetings, receive NAS audio alerts, and search meeting transcripts.",
      username: "Username",
      password: "Password",
      submit: "Sign In",
    },
    sidebar: {
      subtitle: "Meeting intelligence workspace",
      navLabel: "Main navigation",
    },
    nav: {
      dashboard: "Overview",
      record: "Meeting Recording",
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
      eyebrow: "Demo Scope",
      title: "Audio capture, NAS discovery, transcript search",
      copy: "The first version focuses on the complete intake flow: browser recording upload, NAS file alerts, processing status, and searchable meeting history.",
    },
    metrics: {
      total: "Meeting Records",
      processing: "Processing",
      completed: "Completed",
    },
    modules: {
      record: {
        title: "Meeting Recording",
        copy: "Record a full meeting from the microphone, preserve the source audio, and start transcription.",
      },
      meetings: {
        title: "Knowledge Search",
        copy: "Search meeting titles, source filenames, and transcript text.",
      },
      aiwork: {
        copy: "Reserved for meeting summaries, action items, and Q&A workflows.",
      },
    },
    record: {
      eyebrow: "Browser Recorder",
      title: "New Meeting Recording",
      meetingTitle: "Meeting Title",
      titlePlaceholder: "Example: Product Weekly 09/09",
      start: "Start Recording",
      pause: "Pause",
      resume: "Resume",
      stop: "Stop and Save",
      hint: "The browser will request microphone access. After stopping, the system saves the source audio and queues it for processing.",
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
    meetings: {
      eyebrow: "Knowledge Search",
      title: "Meeting Library",
      searchLabel: "Search",
      searchPlaceholder: "Search meeting records",
      emptyList: "No meeting records yet",
      emptyDetail: "Select a meeting to review audio and transcript",
      waitingExcerpt: "Transcript will appear after processing finishes",
      processingText: "Transcription is processing. Please wait.",
      failedText: "Processing failed",
      sourceNas: "NAS Discovery",
      sourceWeb: "Web Recording",
    },
    aiwork: {
      eyebrow: "Model Access",
      copy: "Choose a mainstream LLM, view the current public pricing snapshot, and enter the provider API key.",
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
      sourcesCopy: "Prices change over time. This demo uses a snapshot compiled from official public pricing pages. A production version should sync daily or allow admin refreshes.",
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
    },
    toast: {
      meetingDetected: "Meeting Update",
      meetingCompleted: "Meeting Update",
      meetingFailed: "Processing Failed",
      savedFailed: "Save Failed",
      detected: "New meeting audio \"{title}\" found. Processing has started.",
      uploaded: "Recording \"{title}\" saved. Processing has started.",
      completed: "Meeting \"{title}\" transcription completed.",
      failed: "Meeting \"{title}\" processing failed.",
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
              <span>${escapeHtml(formatDate(call.created_at))} · ${escapeHtml(call.access_mode || "-")}</span>
            </div>
            <span class="badge ${escapeHtml(call.status)}">${callStatusLabel(call.status)}</span>
          </div>
          <p class="llm-call-prompt">${escapeHtml(call.prompt)}</p>
          <p class="llm-call-response">${escapeHtml(call.response || call.error_message || "-")}</p>
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
  renderKeyModal();
  els.apiKeyModal.hidden = false;
  els.apiKeyInput.focus();
}

function closeKeyModal() {
  els.apiKeyModal.hidden = true;
  els.apiKeyInput.value = "";
}

function renderKeyModal() {
  const model = state.selectedPricing?.model;
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

  const model = state.selectedPricing.model;
  state.apiKeys[providerKeyId(model.provider)] = key;
  renderKeyStatus();
  renderModelUsePanel();
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
  }[type] || t("toast.meetingDetected");
}

function notificationMessage(payload) {
  const title = payload.title || "";
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
els.meetingList.addEventListener("click", (event) => {
  const row = event.target.closest("[data-meeting-id]");
  if (row) selectMeeting(Number(row.dataset.meetingId));
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
