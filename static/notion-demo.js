const $ = (id) => document.getElementById(id);
const words = {
  "zh-Hant": {
    back: "返回工作區", readonly: "管理員 · 唯讀", model: "目前 LLM", refresh: "重新檢查",
    setupTitle: "需要連接 Notion", setup1: "建立 Notion Internal Integration，只勾選 Read content。",
    setup2: "將示範頁面透過 Connections 授權給此 Integration。", setup3: "在伺服器 .env 設定 NOTION_API_KEY，重新啟動 AI Work。",
    integration: "Notion 整合設定", pages: "已授權頁面", searchLabel: "頁面標題", search: "搜尋",
    recent: "最近更新的頁面", more: "載入更多", waiting: "尚未查詢", qa: "Notion 問答", clear: "清除選取",
    prompt: "您的問題", ask: "查詢 Notion", sample: "填入摘要範例", answer: "模型回答", sources: "來源頁面", trace: "MCP 執行軌跡",
    partial: "本次僅使用部分內容，不能視為完整工作區或完整文件的結論。",
    checking: "檢查設定中…", configured: "已設定，尚未驗證", missing: "尚未設定", connected: "最近一次讀取成功",
    loading: "正在透過 MCP 讀取 Notion…", thinking: "LLM 正在規劃查詢、讀取 Notion 並產生回答…", none: "沒有找到已授權的頁面標題。", details: "參數與結果",
    sampleText: "找出採購 SOP，摘要請購、核准與驗收步驟。若找不到，請直接說明。", selectedSample: "摘要此頁面，列出重點、待辦事項及負責人；未提到的項目不要推測。",
    unauthorized: "請先登入 AI Work。", forbidden: "此 Demo 目前僅限管理員使用。", failed: "讀取失敗，請查看錯誤訊息",
    selectedContext: "只查此已選取頁面", queryPlaceholder: "例如：採購 SOP", promptPlaceholder: "找出採購 SOP，摘要請購與驗收步驟。",
  },
  en: {
    back: "Back to workspace", readonly: "Admin · Read-only", model: "Current LLM", refresh: "Check again",
    setupTitle: "Connect Notion", setup1: "Create a Notion Internal Integration with Read content only.",
    setup2: "Grant the integration access to your demo pages through Connections.", setup3: "Set NOTION_API_KEY in the server .env and restart AI Work.",
    integration: "Notion integrations", pages: "Shared pages", searchLabel: "Page title", search: "Search", recent: "Recently updated pages",
    more: "Load more", waiting: "No query yet", qa: "Ask Notion", clear: "Clear selection", prompt: "Your question", ask: "Ask Notion",
    sample: "Fill summary example", answer: "Model answer", sources: "Source pages", trace: "MCP execution trace",
    partial: "Only partial evidence was used. This is not an exhaustive workspace or document conclusion.",
    checking: "Checking configuration…", configured: "Configured, not verified", missing: "Not configured", connected: "Last read succeeded",
    loading: "Reading Notion through MCP…", thinking: "LLM is planning, reading Notion and generating an answer…", none: "No matching shared page titles found.", details: "Arguments and result",
    sampleText: "Find the purchasing SOP and summarize requisition, approval and receiving steps. Say if it cannot be found.", selectedSample: "Summarize this page, including key points, action items and owners. Do not infer missing facts.",
    unauthorized: "Please sign in to AI Work first.", forbidden: "This demo is currently restricted to administrators.", failed: "Read failed; see error details",
    selectedContext: "Read only this selected page", queryPlaceholder: "For example: Purchasing SOP", promptPlaceholder: "Find the purchasing SOP and summarize approval and receiving steps.",
  },
};
const state = { language: localStorage.getItem("ai-work-lang") === "en" ? "en" : "zh-Hant", ready: false, busy: false, status: "checking", selected: null, cursor: null, query: "" };
const t = (key) => words[state.language][key];
function language() {
  document.documentElement.lang = state.language;
  for (const node of document.querySelectorAll("[data-copy]")) node.textContent = t(node.dataset.copy);
  $("language").textContent = state.language === "en" ? "繁" : "EN";
  $("connection").textContent = t(state.status);
  $("query").placeholder = t("queryPlaceholder"); $("prompt").placeholder = t("promptPlaceholder");
}
function controls() {
  for (const id of ["search", "recent", "ask", "more"]) $(id).disabled = !state.ready || state.busy;
  for (const id of ["refresh", "query", "prompt", "sample", "clear"]) $(id).disabled = state.busy;
  for (const button of $("pageList").querySelectorAll("button")) button.disabled = state.busy;
  $("busy").hidden = !state.busy;
  document.querySelector("main").setAttribute("aria-busy", String(state.busy));
}
async function request(path, payload) {
  const response = await fetch(path, { credentials: "same-origin", ...(payload ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) } : {}) });
  if (response.status === 401) throw new Error(t("unauthorized"));
  if (response.status === 403) throw new Error(t("forbidden"));
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : `HTTP ${response.status}`);
  return data;
}
async function work(message, callback) {
  if (state.busy) return;
  state.busy = true; $("error").hidden = true; $("busy").textContent = t(message); controls();
  try { await callback(); } catch (error) { $("error").textContent = error.message; $("error").hidden = false; }
  finally { state.busy = false; controls(); }
}
async function check() {
  await work("checking", async () => {
    state.ready = false; state.status = "checking"; $("connection").textContent = t(state.status);
    try {
      const status = await request("/api/notion-demo/status"); state.ready = status.configured;
      state.status = state.ready ? "configured" : "missing";
      $("model").textContent = status.model; $("setup").hidden = state.ready;
    } catch (error) { state.status = "failed"; throw error; }
    finally { $("connection").textContent = t(state.status); }
  });
}
function renderTrace(steps) {
  $("trace").replaceChildren(); $("traceEmpty").hidden = steps.length > 0;
  for (const step of steps) {
    const item = document.createElement("li"); const title = document.createElement("strong"); title.textContent = step.tool;
    const details = document.createElement("details"); const summary = document.createElement("summary"); summary.textContent = t("details");
    const pre = document.createElement("pre"); pre.textContent = JSON.stringify({ arguments: step.arguments, result: step.result }, null, 2);
    details.append(summary, pre); item.append(title, details); $("trace").append(item);
  }
}
async function search(append = false) {
  if (!state.ready) return;
  await work("loading", async () => {
    if (!append) { state.query = $("query").value.trim(); state.cursor = null; $("pageList").replaceChildren(); $("more").hidden = true; }
    const arguments_ = { query: state.query, page_size: 5, ...(append && state.cursor ? { start_cursor: state.cursor } : {}) };
    let result;
    try { result = await request("/api/notion-demo/tools/call", { name: "notion_search", arguments: arguments_ }); }
    catch (error) { state.status = "failed"; $("connection").textContent = t(state.status); throw error; }
    state.status = "connected"; $("connection").textContent = t(state.status);
    for (const page of result.pages) {
      const item = document.createElement("li"); const button = document.createElement("button"); button.type = "button"; button.textContent = page.title;
      button.addEventListener("click", () => { state.selected = page; $("selectedTitle").textContent = page.title; $("selected").hidden = false; $("prompt").value = t("selectedSample"); $("prompt").focus(); });
      const date = document.createElement("small"); date.textContent = page.last_edited_time ? new Date(page.last_edited_time).toLocaleString(state.language) : "";
      item.append(button, date); $("pageList").append(item);
    }
    state.cursor = result.next_cursor; $("more").hidden = !(result.has_more && state.cursor);
    $("empty").hidden = $("pageList").children.length > 0; $("empty").textContent = t("none");
    renderTrace([{ tool: "notion_search", arguments: arguments_, result }]);
  });
}
async function ask(event) {
  event.preventDefault(); const question = $("prompt").value.trim(); if (!question || !state.ready) return;
  await work("thinking", async () => {
    $("answerSection").hidden = true; renderTrace([]);
    const prompt = question + (state.selected ? `\n${t("selectedContext")}: page_id=${state.selected.page_id}` : "");
    const result = await request("/api/notion-demo/ask", { prompt });
    $("answer").textContent = result.answer; $("answerSection").hidden = false;
    $("model").textContent = result.model; $("partial").hidden = !(result.context_truncated || result.steps.some((step) => step.result.has_more || step.result.text_truncated || step.result.blocks?.some((b) => b.has_children)));
    $("sources").replaceChildren();
    for (const source of result.sources) {
      const url = new URL(source.url); if (url.protocol !== "https:" || url.hostname !== "www.notion.so") continue;
      const li = document.createElement("li"); const a = document.createElement("a"); a.href = url.href; a.target = "_blank"; a.rel = "noopener noreferrer"; a.textContent = source.title; li.append(a); $("sources").append(li);
    }
    renderTrace(result.steps); state.status = "connected"; $("connection").textContent = t(state.status);
  });
}
$("searchForm").addEventListener("submit", (event) => { event.preventDefault(); search(); });
$("recent").addEventListener("click", () => { $("query").value = ""; search(); });
$("more").addEventListener("click", () => search(true));
$("askForm").addEventListener("submit", ask);
$("refresh").addEventListener("click", check);
$("clear").addEventListener("click", () => { state.selected = null; $("selected").hidden = true; });
$("sample").addEventListener("click", () => { $("prompt").value = t(state.selected ? "selectedSample" : "sampleText"); $("prompt").focus(); });
$("language").addEventListener("click", () => { state.language = state.language === "en" ? "zh-Hant" : "en"; localStorage.setItem("ai-work-lang", state.language); language(); });
language(); controls(); check();
