const $ = (id) => document.getElementById(id);
const words = {
  "zh-Hant": { back: "返回工作區", readonly: "5 個唯讀工具", notice: "虛構教學資料 · 固定快照 2026-10-14 · 不供臨床決策", connectionLabel: "連線狀態", dataLabel: "資料範圍", dataValue: "3 位病患 · 18 筆關聯資料", refresh: "重新檢查", tools: "唯讀工具", qa: "醫療資料問答", question: "您的問題", ask: "查詢示範資料", sample: "範例問題", chooseSample: "請選擇問題範例", answer: "模型回答", results: "查詢結果與來源", waiting: "尚未查詢", trace: "MCP 工具參數與原始結果", setup: "尚未連線，請由管理員在 MCP 管理啟用並同步 Hospital HIS / FHIR Demo。", checking: "檢查中…", connected: "已連線", missing: "未連線", loading: "正在讀取 MCP 資料…", thinking: "正在查詢資料並產生回答…", unauthorized: "請先返回工作區登入。", failed: "查詢失敗", none: "沒有符合的資料。", noTool: "本次模型未呼叫 MCP，回答未取得醫療資料佐證。", titles: ["搜尋病患", "病患概覽", "回診預約", "FHIR 檢驗資料", "FHIR 就診紀錄"], examples: ["全部示範病患", "demo-p001", "2026-10-15", "demo-p001 · Observation", "Encounter/demo-e001"], columns: ["來源資源", "項目", "時間／狀態", "內容"] },
  en: { back: "Back to workspace", readonly: "5 read-only tools", notice: "Synthetic teaching data · Snapshot 2026-10-14 · Not for clinical decisions", connectionLabel: "Connection", dataLabel: "Dataset", dataValue: "3 patients · 18 linked records", refresh: "Check again", tools: "Read-only tools", qa: "Ask about hospital data", question: "Your question", ask: "Query demo data", sample: "Sample question", chooseSample: "Choose a sample question", answer: "Model answer", results: "Results and sources", waiting: "No query yet", trace: "MCP arguments and raw result", setup: "Not connected. Ask an administrator to enable and sync Hospital HIS / FHIR Demo in MCP Management.", checking: "Checking…", connected: "Connected", missing: "Not connected", loading: "Reading MCP data…", thinking: "Querying data and generating an answer…", unauthorized: "Return to the workspace and sign in first.", failed: "Query failed", none: "No matching records.", noTool: "The model did not call MCP; no hospital evidence was retrieved for this answer.", titles: ["Find patients", "Patient overview", "Appointments", "FHIR observations", "FHIR encounter"], examples: ["All demo patients", "demo-p001", "2026-10-15", "demo-p001 · Observation", "Encounter/demo-e001"], columns: ["Source resource", "Item", "Time / status", "Content"] },
};
const questionSamples = [
  { "zh-Hant": "請透過 Hospital HIS / FHIR Demo MCP 列出所有示範病患，顯示病患 ID、姓名、病歷號及來源資源 ID。不要自行補充資料。",
    en: "Use Hospital HIS / FHIR Demo MCP to list all demo patients with patient ID, name, medical record number and source resource ID. Do not invent missing data." },
  { "zh-Hant": "請透過 Hospital HIS / FHIR Demo MCP 查詢 demo-p001 的就診、檢驗、用藥紀錄及回診預約，按類型整理，並附上各筆來源資源 ID。只整理已有資料，不提供診斷或治療建議。",
    en: "Use Hospital HIS / FHIR Demo MCP to read demo-p001's encounters, observations, medication records and appointments. Group by type and include source resource IDs. Summarize existing records only; do not provide diagnosis or treatment advice." },
  { "zh-Hant": "請透過 Hospital HIS / FHIR Demo MCP 列出 2026-10-15 的所有回診預約，顯示病患 ID、預約時間、狀態與來源資源 ID。",
    en: "Use Hospital HIS / FHIR Demo MCP to list all appointments on 2026-10-15 with patient ID, appointment time, status and source resource ID." },
  { "zh-Hant": "請透過 Hospital HIS / FHIR Demo MCP 查詢 demo-p001 的 Observation 資源，列出項目、數值、單位、紀錄時間及來源資源 ID。沒有的資料請註明未提供，不要推測。",
    en: "Use Hospital HIS / FHIR Demo MCP to query Observation resources for demo-p001. List each item, value, unit, time and source resource ID. Mark missing data as not provided; do not infer it." },
  { "zh-Hant": "請透過 Hospital HIS / FHIR Demo MCP 讀取 Encounter/demo-e001，整理這筆就診的病患、時間、狀態及原始資料中的其他內容，並保留來源資源 ID。不要推測未提供的內容。",
    en: "Use Hospital HIS / FHIR Demo MCP to read Encounter/demo-e001. Summarize the patient, time, status and other available details, retaining the source resource ID. Do not infer missing information." },
];
const samples = [
  ["his_search_patients", {}], ["his_patient_overview", { patient_id: "demo-p001" }],
  ["his_list_appointments", { date: "2026-10-15" }],
  ["fhir_search_resources", { resource_type: "Observation", patient_id: "demo-p001" }],
  ["fhir_read_resource", { resource_type: "Encounter", resource_id: "demo-e001" }],
];
const state = { language: localStorage.getItem("ai-work-lang") === "en" ? "en" : "zh-Hant", server: null, busy: false, status: "checking", result: null };
const t = (key) => words[state.language][key];
function controls() {
  for (const node of document.querySelectorAll("button, textarea, select")) node.disabled = state.busy;
  $("ask").disabled = state.busy || !state.server;
  for (const button of $("tools").querySelectorAll("button")) button.disabled = state.busy || !state.server || !state.server.tools.some((tool) => tool.name === button.dataset.tool);
  $("busy").hidden = !state.busy;
  document.querySelector("main").setAttribute("aria-busy", String(state.busy));
}
function language() {
  document.documentElement.lang = state.language;
  document.querySelectorAll("[data-copy]").forEach((el) => { el.textContent = t(el.dataset.copy); });
  $("language").textContent = state.language === "en" ? "繁" : "EN";
  $("connection").textContent = t(state.status);
  const selectedSample = $("sample").value;
  $("sample").replaceChildren(new Option(t("chooseSample"), ""));
  questionSamples.forEach((_, index) => {
    $("sample").append(new Option(t("titles")[index], String(index)));
  });
  $("sample").value = selectedSample;
  $("tools").replaceChildren();
  samples.forEach(([name, args], index) => {
    const button = document.createElement("button"); button.type = "button"; button.dataset.tool = name;
    const title = document.createElement("strong"); title.textContent = t("titles")[index];
    const code = document.createElement("small"); code.textContent = name;
    const example = document.createElement("span"); example.textContent = t("examples")[index];
    button.append(title, code, example); button.addEventListener("click", () => query(name, args)); $("tools").append(button);
  });
  if (state.result) renderResult(state.result);
  controls();
}
async function request(path, payload) {
  const response = await fetch(path, { credentials: "same-origin", ...(payload ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) } : {}) });
  if (response.status === 401) throw new Error(t("unauthorized"));
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : `${t("failed")} (${response.status})`);
  return data;
}
async function work(message, callback) {
  if (state.busy) return;
  state.busy = true; $("busy").textContent = t(message); $("error").hidden = true; controls();
  try { await callback(); } catch (error) { $("error").textContent = error.message; $("error").hidden = false; }
  finally { state.busy = false; controls(); }
}
async function check() {
  await work("checking", async () => {
    state.server = null; state.status = "checking"; $("connection").textContent = t(state.status);
    try { const data = await request("/api/mcp/available"); state.server = data.servers.find((s) => s.slug === "hospital-demo") || null; }
    finally { state.status = state.server ? "connected" : "missing"; $("connection").textContent = t(state.status); $("setup").hidden = !!state.server; }
  });
}
function clearResults() {
  state.result = null; $("records").replaceChildren(); $("traceSection").hidden = true;
  $("answerSection").hidden = true; $("empty").hidden = false; $("empty").textContent = t("waiting");
}
function renderResult(step) {
  state.result = step; $("trace").textContent = JSON.stringify(step, null, 2); $("traceSection").hidden = false;
  const data = step.result?.structuredContent;
  const rows = data?.records || data?.bundle?.entry?.map((entry) => entry.resource) || (data?.resource ? [data.resource] : []);
  $("records").replaceChildren(); $("empty").hidden = rows.length > 0; $("empty").textContent = t("none");
  if (!rows.length) return;
  const table = document.createElement("table"); const head = table.createTHead().insertRow();
  t("columns").forEach((label) => { const th = document.createElement("th"); th.scope = "col"; th.textContent = label; head.append(th); });
  const body = table.createTBody();
  for (const r of rows) {
    const name = r.name?.[0]?.text || r.code?.text || r.code?.coding?.[0]?.display || r.medicationCodeableConcept?.text || r.type?.[0]?.text || r.description || "--";
    const date = r.effectiveDateTime || r.period?.start || r.start || r.authoredOn || "";
    const detail = r.valueQuantity ? `${r.valueQuantity.value} ${r.valueQuantity.unit}` : r.subject?.reference || r.participant?.[0]?.actor?.reference || r.identifier?.[0]?.value || "--";
    const row = body.insertRow();
    [`${r.resourceType}/${r.id}`, name, [date, r.status].filter(Boolean).join(" · "), detail].forEach((value) => { row.insertCell().textContent = value; });
  }
  $("records").append(table);
}
async function query(name, args) {
  if (!state.server) return;
  await work("loading", async () => { clearResults(); renderResult(await request("/api/hospital-demo/tools/call", { name, arguments: args })); });
}
$("askForm").addEventListener("submit", (event) => {
  event.preventDefault(); const prompt = $("prompt").value.trim(); if (!prompt || !state.server) return;
  work("thinking", async () => {
    clearResults();
    const result = await request("/api/llm/run", { prompt, use_mcp: true, mcp_server_id: state.server.id, system_prompt: "Use only synthetic hospital MCP evidence. Include resource IDs and snapshot dates. Do not diagnose, prescribe, or infer missing records. Clearly label all records as fictional teaching data." });
    $("answer").textContent = result.answer; $("answerSection").hidden = false;
    if (result.mcp?.used) renderResult({ tool: result.mcp.tool, arguments: result.mcp.arguments, result: result.mcp.result });
    else { $("error").textContent = t("noTool"); $("error").hidden = false; }
  });
});
$("refresh").addEventListener("click", check);
$("sample").addEventListener("change", () => {
  const sample = questionSamples[$("sample").value];
  if (!sample) return;
  $("prompt").value = sample[state.language];
  $("prompt").focus();
});
$("prompt").addEventListener("input", () => { $("sample").value = ""; });
$("language").addEventListener("click", () => { state.language = state.language === "en" ? "zh-Hant" : "en"; localStorage.setItem("ai-work-lang", state.language); language(); });
language(); check();
