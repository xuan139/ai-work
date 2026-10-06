const copy = {
  "zh-Hant": {
    title: "企業資料問答", description: "透過 LangChain 串接現有模型與 Odoo 唯讀 MCP，查詢真實企業資料。",
    stepPlan: "規劃查詢工具", stepMcp: "讀取 Odoo 資料", stepAnswer: "生成引用答案",
    examples: "連續提問範例", contactExample: "查詢最新 3 位聯絡人", salesExample: "1. 查詢最新銷售訂單",
    salesFollowupExample: "2. 剛才那筆訂單的客戶是誰？", purchaseExample: "1. 查詢最新採購訂單",
    purchaseFollowupExample: "2. 剛才那筆採購單的供應商是誰？", back: "返回 AI Work", eyebrow: "獨立體驗頁面",
    modelLabel: "目前模型", odooLabel: "Odoo MCP", checking: "檢查中", connected: "已連線", unavailable: "尚未連線",
    readOnly: "唯讀存取", memoryLabel: "對話記憶", turns: (count) => `${count} 輪`, emptyTitle: "向 Odoo 提問", emptyCopy: "選擇左側範例，或輸入要查詢的企業資料。結果會標明實際使用的 MCP 工具。",
    inputLabel: "您的問題", placeholder: "例如：查詢最新 10 筆銷售訂單與總額", send: "送出", sending: "查詢中…",
    hint: "保留最近對話脈絡；僅讀取 Odoo，不會修改資料。", clear: "清空記憶", traceEyebrow: "執行追蹤",
    traceTitle: "LangChain 流程", traceCopy: "送出問題後，這裡會顯示實際執行的查詢鏈。", traceIdle: "等待提問",
    auditTitle: "企業稽核", auditCopy: "模型與 MCP 呼叫沿用 AI Work 的登入身分與稽核記錄。",
    pending: "LangChain 正在查詢 Odoo 並生成答案…", memoryCleared: "對話記憶已清空。",
    examplesText: {
      contacts: "請查詢 Odoo 最新 3 位聯絡人，列出名稱、電子郵件與電話。",
      sales: "請查詢 Odoo 最新 1 筆銷售訂單，列出訂單編號、客戶、狀態與總額。",
      salesFollowup: "剛才那筆銷售訂單的客戶是誰？總額是多少？",
      purchases: "請查詢 Odoo 最新 1 筆採購訂單，列出訂單編號、供應商、狀態與總額。",
      purchaseFollowup: "剛才那筆採購訂單的供應商是誰？總額是多少？",
    },
  },
  en: {
    title: "Business Q&A", description: "LangChain connects the selected model to read-only Odoo MCP for real business data.",
    stepPlan: "Plan a read-only tool", stepMcp: "Read Odoo data", stepAnswer: "Generate a sourced answer",
    examples: "Follow-up examples", contactExample: "Find the latest 3 contacts", salesExample: "1. Find the latest sales order",
    salesFollowupExample: "2. Who is that order's customer?", purchaseExample: "1. Find the latest purchase order",
    purchaseFollowupExample: "2. Who is that order's vendor?", back: "Back to AI Work", eyebrow: "Standalone demo",
    modelLabel: "Current model", odooLabel: "Odoo MCP", checking: "Checking", connected: "Connected", unavailable: "Unavailable",
    readOnly: "Read-only", memoryLabel: "Chat memory", turns: (count) => `${count} turns`, emptyTitle: "Ask Odoo", emptyCopy: "Choose an example or ask about company data. Answers show the MCP tool actually used.",
    inputLabel: "Your question", placeholder: "For example: List the latest 10 sales orders and totals", send: "Send", sending: "Querying…",
    hint: "Recent context is remembered. Odoo data is read-only.", clear: "Clear memory", traceEyebrow: "Execution trace",
    traceTitle: "LangChain flow", traceCopy: "The actual query steps appear here after you send a question.", traceIdle: "Waiting for a question",
    auditTitle: "Enterprise audit", auditCopy: "Model and MCP calls use your AI Work identity and audit logs.",
    pending: "LangChain is querying Odoo and generating an answer…", memoryCleared: "Conversation memory cleared.",
    examplesText: {
      contacts: "List the latest 3 Odoo contacts with name, email, and phone.",
      sales: "List the latest Odoo sales order with number, customer, status, and total.",
      salesFollowup: "Who was the customer of that sales order, and what was the total?",
      purchases: "List the latest Odoo purchase order with number, vendor, status, and total.",
      purchaseFollowup: "Who was the vendor of that purchase order, and what was the total?",
    },
  },
};

const el = (id) => document.getElementById(id);
const state = { language: localStorage.getItem("ai-work-lang") === "en" ? "en" : "zh-Hant", ready: false, busy: false, turns: 0 };
const t = (key) => copy[state.language][key];

function setLanguage(language) {
  state.language = language;
  localStorage.setItem("ai-work-lang", language);
  document.documentElement.lang = language;
  for (const node of document.querySelectorAll("[data-i18n]")) node.textContent = t(node.dataset.i18n);
  for (const node of document.querySelectorAll("[data-i18n-placeholder]")) node.placeholder = t(node.dataset.i18nPlaceholder);
  for (const button of document.querySelectorAll("[data-lang]")) button.classList.toggle("active", button.dataset.lang === language);
  el("sendButton").textContent = state.busy ? t("sending") : t("send");
  el("memoryCount").textContent = t("turns")(state.turns);
  renderStatus();
}

async function request(path, options = {}) {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  if (response.status === 401) { window.location.href = "/"; throw new Error("Not authenticated"); }
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
  return data;
}

function renderStatus() {
  const status = el("odooStatus");
  status.classList.toggle("connected", state.ready);
  status.classList.toggle("unavailable", !state.ready);
  status.querySelector("span:last-child").textContent = t(state.ready ? "connected" : "unavailable");
  el("sendButton").disabled = !state.ready || state.busy;
  for (const button of document.querySelectorAll("[data-example]")) button.disabled = !state.ready || state.busy;
}

function appendMessage(role, content, source = null) {
  el("emptyState").hidden = true;
  const item = document.createElement("article");
  item.className = `message ${role}`;
  if (source?.server && source?.tool) {
    const label = document.createElement("div");
    label.className = "source";
    label.textContent = `${source.server} · ${source.tool}`;
    item.appendChild(label);
  }
  const body = document.createElement("p");
  body.textContent = content;
  item.appendChild(body);
  el("messages").appendChild(item);
  el("messages").scrollTop = el("messages").scrollHeight;
  return item;
}

function renderTrace(steps) {
  const list = el("traceList");
  list.replaceChildren();
  if (!steps?.length) {
    const item = document.createElement("li");
    item.textContent = t("traceIdle");
    list.appendChild(item);
    return;
  }
  for (const [index, step] of steps.entries()) {
    const item = document.createElement("li");
    item.textContent = [t("stepPlan"), t("stepMcp"), t("stepAnswer")][index] || step.name;
    if (step.detail) {
      const detail = document.createElement("small");
      detail.textContent = step.detail;
      item.appendChild(detail);
    }
    list.appendChild(item);
  }
}

function setBusy(busy) {
  state.busy = busy;
  el("sendButton").textContent = t(busy ? "sending" : "send");
  el("question").disabled = busy;
  el("clearButton").disabled = busy;
  renderStatus();
}

async function ask(event) {
  event.preventDefault();
  const question = el("question").value.trim();
  if (!question || state.busy || !state.ready) return;
  appendMessage("user", question);
  el("question").value = "";
  el("question").style.height = "";
  setBusy(true);
  const pending = appendMessage("assistant pending", t("pending"));
  renderTrace([{ name: t("stepPlan"), detail: t("pending") }]);
  try {
    const response = await request("/api/langchain-demo/ask", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ prompt: question }),
    });
    pending.remove();
    appendMessage("assistant", response.answer, response.source);
    state.turns += 1;
    el("memoryCount").textContent = t("turns")(state.turns);
    renderTrace(response.steps);
  } catch (error) {
    pending.remove();
    appendMessage("error", error.message);
    renderTrace([]);
  } finally {
    setBusy(false);
    el("question").focus();
  }
}

async function clearMemory() {
  if (state.busy) return;
  setBusy(true);
  try {
    await request("/api/langchain-demo/messages", { method: "DELETE" });
    el("messages").replaceChildren(el("emptyState"));
    el("emptyState").hidden = false;
    state.turns = 0;
    el("memoryCount").textContent = t("turns")(0);
    renderTrace([]);
    el("formHint").textContent = t("memoryCleared");
  } catch (error) {
    appendMessage("error", error.message);
  } finally { setBusy(false); }
}

async function boot() {
  setLanguage(state.language);
  for (const button of document.querySelectorAll("[data-lang]")) button.addEventListener("click", () => setLanguage(button.dataset.lang));
  for (const button of document.querySelectorAll("[data-example]")) button.addEventListener("click", () => {
    el("question").value = t("examplesText")[button.dataset.example];
    el("askForm").requestSubmit();
  });
  el("askForm").addEventListener("submit", ask);
  el("clearButton").addEventListener("click", clearMemory);
  el("question").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); el("askForm").requestSubmit(); }
  });
  el("question").addEventListener("input", () => {
    el("question").style.height = "auto";
    el("question").style.height = `${Math.min(el("question").scrollHeight, 150)}px`;
  });
  try {
    const [user, status, history] = await Promise.all([
      request("/auth/me"), request("/api/langchain-demo/status"), request("/api/langchain-demo/messages"),
    ]);
    el("username").textContent = user.username;
    el("modelName").textContent = status.model;
    state.ready = Boolean(status.odoo);
    state.turns = Math.floor(history.messages.length / 2);
    el("memoryCount").textContent = t("turns")(state.turns);
    renderStatus();
    for (const message of history.messages) {
      let source = null;
      if (message.source_json) { try { source = JSON.parse(message.source_json); } catch { /* legacy data */ } }
      appendMessage(message.role, message.content, source);
    }
    if (history.messages.length) {
      const last = history.messages.at(-1);
      if (last.source_json) {
        const source = JSON.parse(last.source_json);
        renderTrace([
          { name: t("stepPlan") },
          { name: t("stepMcp"), detail: `${source.server} / ${source.tool}` },
          { name: t("stepAnswer"), detail: status.model },
        ]);
      }
    }
  } catch (error) {
    appendMessage("error", error.message);
  }
}

boot();
