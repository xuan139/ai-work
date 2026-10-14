const $ = (id) => document.getElementById(id);
const words = {
  "zh-Hant": { back: "返回工作區", readonly: "5 個唯讀工具", notice: "虛構教學資料 · 固定快照 2026-10-14 · 不供臨床決策", connectionLabel: "連線狀態", dataLabel: "資料範圍", dataValue: "3 位病患 · 18 筆關聯資料", refresh: "重新檢查", tools: "唯讀工具", qa: "醫療資料問答", question: "您的問題", ask: "查詢示範資料", sample: "範例問題", chooseSample: "請選擇問題範例", answer: "模型回答", results: "查詢結果與來源", waiting: "尚未查詢", trace: "MCP 工具參數與原始結果", setup: "尚未連線，請由管理員在 MCP 管理啟用並同步 Hospital HIS / FHIR Demo。", checking: "檢查中…", connected: "已連線", missing: "未連線", loading: "正在讀取 MCP 資料…", thinking: "正在查詢資料並產生回答…", unauthorized: "請先返回工作區登入。", failed: "查詢失敗", none: "沒有符合的資料。", noTool: "本次模型未呼叫 MCP，回答未取得醫療資料佐證。", titles: ["搜尋病患", "病患概覽", "回診預約", "FHIR 檢驗資料", "FHIR 就診紀錄"], examples: ["全部示範病患", "demo-p001", "2026-10-15", "demo-p001 · Observation", "Encounter/demo-e001"], columns: ["來源資源", "項目", "時間／狀態", "內容"] },
  en: { back: "Back to workspace", readonly: "5 read-only tools", notice: "Synthetic teaching data · Snapshot 2026-10-14 · Not for clinical decisions", connectionLabel: "Connection", dataLabel: "Dataset", dataValue: "3 patients · 18 linked records", refresh: "Check again", tools: "Read-only tools", qa: "Ask about hospital data", question: "Your question", ask: "Query demo data", sample: "Sample question", chooseSample: "Choose a sample question", answer: "Model answer", results: "Results and sources", waiting: "No query yet", trace: "MCP arguments and raw result", setup: "Not connected. Ask an administrator to enable and sync Hospital HIS / FHIR Demo in MCP Management.", checking: "Checking…", connected: "Connected", missing: "Not connected", loading: "Reading MCP data…", thinking: "Querying data and generating an answer…", unauthorized: "Return to the workspace and sign in first.", failed: "Query failed", none: "No matching records.", noTool: "The model did not call MCP; no hospital evidence was retrieved for this answer.", titles: ["Find patients", "Patient overview", "Appointments", "FHIR observations", "FHIR encounter"], examples: ["All demo patients", "demo-p001", "2026-10-15", "demo-p001 · Observation", "Encounter/demo-e001"], columns: ["Source resource", "Item", "Time / status", "Content"] },
};
const questionSamples = [
  { "zh-Hant": "請透過 Hospital HIS / FHIR Demo MCP 列出所有示範病患，顯示病患 ID、姓名、病歷號及來源資源 ID。不要自行補充資料。",
    en: "Use Hospital HIS / FHIR Demo MCP to list all demo patients with patient ID, name, medical record number and source resource ID. Do not invent missing data." },
  { "zh-Hant": "請透過 Hospital HIS / FHIR Demo MCP 查詢 demo-p001 的就診、檢驗、用藥紀錄、回診預約，以及教學訪談、住院歷史與飲食注意事項，按類型整理，並附上來源 ID。區分病患自述、待確認與未提供的資料，不提供診斷或治療建議。",
    en: "Use Hospital HIS / FHIR Demo MCP to read demo-p001's encounters, observations, medication records, appointments and teaching interview, admission history and dietary notes. Group by type and include source IDs. Distinguish self-reported, unconfirmed and missing information. Do not provide diagnosis or treatment advice." },
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
Object.assign(words["zh-Hant"], { imagingTitle: "病患影像與報告", imagingNotice: "虛構病患與教學報告；各檢查重用公開 CC0 X 光影像，不代表病患的實際影像，不供臨床診斷。", imagePatient: "影像病患", imageStudy: "檢查", imageReport: "教學影像報告", imageOpen: "開啟完整影像與報告摘要", imageMissing: "Orthanc 尚未連線，請由管理員啟用並同步放射影像 MCP。", imagePending: "報告待完成", imageFinal: "教學稿已完成", imageNoReport: "尚無報告內容，不推測檢查結果。", imageSource: "原圖與授權", imageAlt: "公開 CC0 胸部 X 光教學影像，非病患實際影像", imageInvalid: "影像來源或病患不符合所選範圍。", imageLoading: "讀取病患影像與報告…" });
Object.assign(words.en, { imagingTitle: "Patient images and reports", imagingNotice: "Fictional patients and teaching reports. Studies reuse a public CC0 radiograph, not actual patient images. Not for clinical diagnosis.", imagePatient: "Imaging patient", imageStudy: "Study", imageReport: "Teaching imaging report", imageOpen: "Open full image and report summary", imageMissing: "Orthanc is not connected. Ask an administrator to enable and sync the radiology MCP.", imagePending: "Report pending", imageFinal: "Teaching report complete", imageNoReport: "No report available. No findings are inferred.", imageSource: "Original image and license", imageAlt: "Public CC0 chest radiograph for teaching, not an actual patient image", imageInvalid: "Image source or patient does not match the selection.", imageLoading: "Reading patient image and report…" });
Object.assign(words["zh-Hant"], { profileTitle: "病患訪談與照護資料 Demo", profileNotice: "作者編寫的虛構教學紀錄，非正式病歷或醫囑；未提供資料不代表沒有相關病史或禁忌。", profileInterview: "訪談紀錄", profileAdmissions: "住院歷史", profileDiet: "飲食禁忌與注意事項", profileEmpty: "未提供住院歷史，不代表從未住院。", profileUnavailable: "尚未提供教學訪談與照護資料。" });
Object.assign(words.en, { profileTitle: "Patient interview and care notes demo", profileNotice: "Authored fictional teaching notes, not official medical records or orders. Missing information does not rule out prior admissions or dietary restrictions.", profileInterview: "Interview transcript", profileAdmissions: "Admission history", profileDiet: "Dietary restrictions and notes", profileEmpty: "Admission history not provided; this does not mean no previous admissions.", profileUnavailable: "Teaching interview and care notes are not available." });
const imaging = { connected: false, url: null, study: null, report: null, profile: null, steps: [], message: "", error: "" };
function controls() {
  for (const node of document.querySelectorAll("button, textarea, select")) node.disabled = state.busy;
  $("ask").disabled = state.busy || !state.server;
  for (const button of $("tools").querySelectorAll("button")) button.disabled = state.busy || !state.server || !state.server.tools.some((tool) => tool.name === button.dataset.tool);
  $("busy").hidden = !state.busy;
  $("imagePatient").disabled = state.busy || !$("imagePatient").options.length;
  $("imageStudy").disabled = state.busy || !imaging.connected || !$("imageStudy").options.length;
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
  renderImaging();
  renderProfile();
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
    const previousPatient = $("imagePatient").value;
    state.server = null; state.status = "checking"; $("connection").textContent = t(state.status);
    imaging.connected = false; clearImaging(); clearProfile(); $("imagePatient").replaceChildren(); $("imageStudy").replaceChildren();
    try { const data = await request("/api/mcp/available"); state.server = data.servers.find((s) => s.slug === "hospital-demo") || null;
      imaging.connected = data.servers.some((s) => s.slug === "orthanc-radiology");
      await imagingAction(() => loadImaging(previousPatient));
    }
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
  await work("loading", async () => { clearResults(); renderResult(await request("/api/hospital-demo/tools/call", { name, arguments: args }));
    if (args.patient_id && [...$("imagePatient").options].some(o => o.value === args.patient_id)) {
      $("imagePatient").value = args.patient_id; await imagingAction(loadImagingStudies);
    }
  });
}
function clearImaging() {
  imaging.study = null; imaging.report = null; imaging.steps = []; imaging.error = ""; imaging.message = "";
  $("imagingContent").hidden = true; $("imagingTraceSection").hidden = true;
  $("imagingReport").textContent = ""; $("imagingReportMeta").textContent = ""; $("imagingMeta").textContent = "";
  $("patientXray").hidden = true; $("patientXray").removeAttribute("src"); $("imagingLink").removeAttribute("href");
  if (imaging.url) URL.revokeObjectURL(imaging.url);
  imaging.url = null;
}
function renderImaging() {
  $("imagingMessage").textContent = imaging.error || (imaging.message ? t(imaging.message) : "");
  $("patientXray").alt = t("imageAlt");
  if (!imaging.study) return;
  const s = imaging.study, r = imaging.report;
  $("imagingMeta").textContent = `${s.patient_id} · ${s.accession} · ${s.date} · Study UID: ${s.study_uid}`;
  $("imagingReportMeta").textContent = `${r.id} · v${r.version} · ${r.date} · ${t(r.status === "final" ? "imageFinal" : "imagePending")}`;
  $("imagingReport").textContent = r.text || t("imageNoReport");
  $("imagingCredit").replaceChildren(document.createTextNode(`${s.image_source.author} · ${s.image_source.license} · `));
  const link = document.createElement("a"); link.textContent = t("imageSource");
  link.href = "https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg";
  link.target = "_blank"; link.rel = "noopener noreferrer"; $("imagingCredit").append(link);
}
async function imagingTool(name, args = {}) {
  const step = await request("/api/radiology-demo/tools/call", { name, arguments: args });
  imaging.steps.push(step); $("imagingTrace").textContent = JSON.stringify(imaging.steps, null, 2); $("imagingTraceSection").hidden = false;
  return step.result;
}
async function imagingAction(callback) {
  imaging.message = "";
  try { await callback(); } catch (error) { imaging.error = error.message; }
  finally { if (!imaging.connected) imaging.message = "imageMissing"; renderImaging(); }
}
async function loadImaging(previous = $("imagePatient").value) {
  clearImaging(); clearProfile(); $("imagePatient").replaceChildren(); $("imageStudy").replaceChildren();
  let patients = [];
  if (state.server) {
    const data = await request("/api/hospital-demo/tools/call", { name: "his_search_patients", arguments: {} });
    patients = (data.result.structuredContent.records || []).map(p => ({ id: p.id, name: p.name[0].text }));
  } else if (imaging.connected) patients = (await imagingTool("radiology_search_patients")).patients;
  for (const p of patients) $("imagePatient").append(new Option(`${p.name} · ${p.id}`, p.id));
  if (patients.some(p => p.id === previous)) $("imagePatient").value = previous;
  await loadImagingStudies();
}
async function loadImagingStudies() {
  clearImaging(); clearProfile(); $("imageStudy").replaceChildren();
  if (!$("imagePatient").value) { imaging.message = "none"; return; }
  if (state.server) {
    const step = await request("/api/hospital-demo/tools/call", { name: "his_patient_overview", arguments: { patient_id: $("imagePatient").value } });
    const profile = step.result.structuredContent.teaching_profile;
    if (profile && profile.patient_id !== $("imagePatient").value) throw Error(t("imageInvalid"));
    imaging.profile = profile || null; renderProfile();
  }
  if (!imaging.connected) return;
  const result = await imagingTool("radiology_search_studies", { patient_id: $("imagePatient").value });
  for (const s of result.studies) $("imageStudy").append(new Option(`${s.accession} · ${s.date}`, s.id));
  if ($("imageStudy").value) await openImaging();
  else imaging.message = "none";
}
async function openImaging() {
  clearImaging(); const id = $("imageStudy").value; if (!id) return;
  const s = (await imagingTool("radiology_get_study", { study_id: id })).study;
  if (s.patient_id !== $("imagePatient").value) throw Error(t("imageInvalid"));
  const r = (await imagingTool("radiology_get_report", { study_id: id })).report;
  const viewer = await imagingTool("radiology_open_viewer", { study_id: id });
  const path = `/api/radiology-demo/studies/${encodeURIComponent(id)}/image`;
  if (viewer.preview_url !== path) throw Error(t("imageInvalid"));
  imaging.study = s; imaging.report = r; renderImaging(); $("imagingContent").hidden = false;
  $("imagingLink").href = `/radiology-demo?study=${encodeURIComponent(id)}`;
  const response = await fetch(path, { credentials: "same-origin" });
  if (!response.ok) throw Error(response.status === 401 ? t("unauthorized") : `${t("failed")} (${response.status})`);
  imaging.url = URL.createObjectURL(await response.blob()); $("patientXray").src = imaging.url;
  await $("patientXray").decode(); $("patientXray").hidden = false;
}
$("imagePatient").addEventListener("change", () => work("imageLoading", () => imagingAction(loadImagingStudies)));
$("imageStudy").addEventListener("change", () => work("imageLoading", () => imagingAction(openImaging)));
$("imageRefresh").addEventListener("click", check);
function clearProfile() {
  imaging.profile = null; $("patientProfile").hidden = true;
  for (const id of ["profileMeta", "profileInterview", "profileAdmissions", "profileDiet"]) $(id).replaceChildren();
}
function renderProfile() {
  const p = imaging.profile; $("patientProfile").hidden = !p; if (!p) return;
  $("profileMeta").textContent = `${p.patient_id} · ${p.source_id} · v${p.version} · ${p.recorded_at} · ${p.source}`;
  $("profileInterview").replaceChildren();
  for (const line of p.interview) {
    const speaker = document.createElement("dt"), text = document.createElement("dd");
    speaker.textContent = line.speaker; text.textContent = line.text; $("profileInterview").append(speaker, text);
  }
  $("profileAdmissions").replaceChildren();
  if (!p.admissions.length) $("profileAdmissions").textContent = t("profileEmpty");
  for (const admission of p.admissions) {
    const text = document.createElement("p");
    text.textContent = `${admission.id} · ${admission.start} — ${admission.end} · ${admission.department} · ${admission.status}\n${admission.reason}\n${admission.note}`;
    $("profileAdmissions").append(text);
  }
  $("profileDiet").replaceChildren();
  for (const note of p.diet) {
    const text = document.createElement("p"); text.textContent = `${note.category} · ${note.status}\n${note.text}`; $("profileDiet").append(text);
  }
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
