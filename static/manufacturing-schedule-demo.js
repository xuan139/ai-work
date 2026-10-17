const $ = (id) => document.getElementById(id);
const copy = {
  "zh-Hant": {
    back: "返回工作區", title: "電子製造排程 Demo", badge: "虛構資料 · 唯讀模擬",
    intro: "使用 5 筆銷售訂單、3 個工作中心、庫存與停機快照，展示有限產能排程、交期風險與可追溯的 LLM 說明。",
    notice: "固定快照 2026-10-19。延期機率是規則式 Demo 風險分數，不是已訓練模型的預測；本頁不會寫入 Odoo、MES 或 PLC。",
    scenarioEyebrow: "WHAT-IF 模擬", scenarioTitle: "選擇情境並重新排程", run: "產生有限產能排程",
    rush: "加入急單 SO-1006", rushHelp: "70 件 Edge Gateway，要求 10/20 14:00 交付", downtime: "SMT-01 模擬停機",
    materialDelay: "MCU-C 到料延後", none: "不增加", twoHours: "2 小時", fourHours: "4 小時", twoDays: "2 個工作日", threeDays: "3 個工作日",
    baseline: "目前顯示基準情境。", currentScenario: "目前排程情境", dirty: "情境已變更，請重新產生排程。",
    qaEyebrow: "LOCAL LLM · 可追溯", qaTitle: "AI 排程問答", sample: "範例問題", prompt: "您的問題",
    promptPlaceholder: "例如：目前哪些訂單可能延期？", ask: "詢問目前排程", answer: "模型回答",
    orders: "訂單與預測交期", order: "訂單", product: "產品", quantity: "數量", priority: "優先級",
    due: "要求交期", predicted: "預測完成", risk: "延期風險", reason: "主要原因", gantt: "工作中心甘特圖",
    ganttHelp: "包含工序順序、班次、換線與停機避讓", legend: "色彩代表產品家族；條形內顯示訂單。",
    centers: "工作中心與停機", inventory: "庫存與缺料", sources: "資料來源與工具軌跡", trace: "查看完整工具呼叫軌跡",
    generating: "正在計算有限產能排程…", thinking: "模型正在根據目前排程產生說明…", failed: "操作失敗",
    metrics: ["訂單", "預計延期", "準時", "換線", "最晚完成"], riskLabels: { low: "低", medium: "中", high: "高" },
    priorityLabels: { normal: "一般", high: "高", urgent: "急單" }, shift: "班次", capacity: "產能", setup: "換線",
    downtimeLabel: "停機", noDowntime: "無停機", hours: "件／小時", minutes: "分鐘", onHand: "現有", required: "需求",
    samples: ["選擇範例問題", "目前哪些訂單可能延期？", "訂單 SO-1003 為什麼無法準時交付？",
      "如果 SMT-01 停機兩小時，會影響哪些訂單？", "如何調整排程可以減少換線？"],
  },
  en: {
    back: "Back to workspace", title: "Electronics Scheduling Demo", badge: "Fictional data · Read-only simulation",
    intro: "Use five sales orders, three work centers, inventory and downtime snapshots to demonstrate finite-capacity scheduling, delivery risk and traceable LLM explanations.",
    notice: "Fixed snapshot: 2026-10-19. Delay probability is a rule-based demo score, not a trained forecast. This page never writes to Odoo, MES or PLCs.",
    scenarioEyebrow: "WHAT-IF SIMULATION", scenarioTitle: "Select a scenario and reschedule", run: "Generate finite-capacity schedule",
    rush: "Add rush order SO-1006", rushHelp: "70 Edge Gateways due Oct 20 at 14:00", downtime: "SMT-01 simulated downtime",
    materialDelay: "MCU-C material delay", none: "No addition", twoHours: "2 hours", fourHours: "4 hours", twoDays: "2 workdays", threeDays: "3 workdays",
    baseline: "Showing the baseline scenario.", currentScenario: "Current schedule scenario", dirty: "Scenario changed. Generate the schedule again.",
    qaEyebrow: "LOCAL LLM · TRACEABLE", qaTitle: "AI scheduling Q&A", sample: "Sample question", prompt: "Your question",
    promptPlaceholder: "Example: Which orders may be late?", ask: "Ask about this schedule", answer: "Model answer",
    orders: "Orders and predicted delivery", order: "Order", product: "Product", quantity: "Qty", priority: "Priority",
    due: "Requested due", predicted: "Predicted finish", risk: "Delay risk", reason: "Primary reason", gantt: "Work-center Gantt",
    ganttHelp: "Includes routing, shifts, changeovers and downtime avoidance", legend: "Colors identify product families; bars show order IDs.",
    centers: "Work centers and downtime", inventory: "Inventory and shortages", sources: "Sources and tool trace", trace: "View full tool-call trace",
    generating: "Calculating the finite-capacity schedule…", thinking: "The model is explaining the current schedule…", failed: "Operation failed",
    metrics: ["Orders", "Late", "On time", "Changeovers", "Latest finish"], riskLabels: { low: "Low", medium: "Medium", high: "High" },
    priorityLabels: { normal: "Normal", high: "High", urgent: "Rush" }, shift: "Shift", capacity: "Capacity", setup: "Changeover",
    downtimeLabel: "Downtime", noDowntime: "No downtime", hours: "units/hour", minutes: "minutes", onHand: "On hand", required: "Required",
    samples: ["Choose a sample question", "Which orders may be late?", "Why can order SO-1003 not finish on time?",
      "Which orders are affected if SMT-01 stops for two hours?", "How can the schedule reduce changeovers?"],
  },
};
const state = { language: localStorage.getItem("ai-work-lang") === "en" ? "en" : "zh-Hant", schedule: null, trace: [] };
const t = (key) => copy[state.language][key];

function scenario() {
  return { rush_order: $("rushOrder").checked, smt_downtime_hours: Number($("downtimeHours").value), material_delay_days: Number($("materialDelay").value) };
}
async function request(path, payload) {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (response.status === 401) { location.href = "/"; throw new Error("Login required"); }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
  return data;
}
function setBusy(message = "") {
  const busy = Boolean(message);
  $("busy").hidden = !busy; $("busy").textContent = message;
  $("error").hidden = true;
  for (const element of document.querySelectorAll("button, input, select")) element.disabled = busy;
}
async function work(message, action) {
  setBusy(message);
  try { await action(); }
  catch (error) { $("error").textContent = `${t("failed")}：${error.message}`; $("error").hidden = false; }
  finally { setBusy(); }
}
function text(tag, value, className = "") {
  const node = document.createElement(tag); node.textContent = value;
  if (className) node.className = className;
  return node;
}
function fmt(value, includeTime = true) {
  const date = new Date(value);
  return new Intl.DateTimeFormat(state.language === "en" ? "en-US" : "zh-TW", includeTime
    ? { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }
    : { month: "2-digit", day: "2-digit" }).format(date);
}
function cell(row, value, className = "") { row.append(text("td", value, className)); }

function renderMetrics(data) {
  const values = [data.summary.order_count, data.summary.late_count, data.summary.on_time_count,
    data.summary.setup_count, fmt(data.summary.latest_completion_at)];
  $("metrics").replaceChildren(...values.map((value, index) => {
    const item = document.createElement("div"); item.className = "metric";
    item.append(text("span", String(value)), text("small", t("metrics")[index])); return item;
  }));
}
function renderOrders(data) {
  $("ordersBody").replaceChildren(...data.orders.map((order) => {
    const row = document.createElement("tr");
    cell(row, order.order); cell(row, order.product); cell(row, String(order.quantity));
    cell(row, t("priorityLabels")[order.priority]); cell(row, fmt(order.due_at)); cell(row, fmt(order.predicted_completion_at));
    const risk = document.createElement("td"); risk.append(text("span", `${t("riskLabels")[order.risk_level]} · ${order.risk_probability}%`, `risk risk-${order.risk_level}`)); row.append(risk);
    cell(row, order.reasons.join("；")); return row;
  }));
}
function renderGantt(data) {
  const start = new Date(data.snapshot_at).getTime();
  const ends = data.operations.map((op) => new Date(op.end_at).getTime()).concat(data.downtimes.map((d) => new Date(d.end).getTime()));
  const end = Math.max(...ends, start + 24 * 3600 * 1000);
  const span = end - start;
  const percent = (value) => Math.max(0, Math.min(100, (new Date(value).getTime() - start) / span * 100));
  const board = document.createElement("div"); board.className = "gantt-board";
  const axis = document.createElement("div"); axis.className = "gantt-axis"; axis.append(text("div", ""));
  const axisTrack = document.createElement("div"); axisTrack.className = "gantt-axis-track";
  for (let index = 0; index <= 5; index++) {
    const mark = document.createElement("span"); mark.className = "axis-mark"; mark.style.left = `${index * 20}%`;
    mark.textContent = fmt(new Date(start + span * index / 5).toISOString()); axisTrack.append(mark);
  }
  axis.append(axisTrack); board.append(axis);
  for (const center of data.work_centers) {
    const row = document.createElement("div"); row.className = "gantt-row"; row.append(text("div", center.id, "gantt-label"));
    const track = document.createElement("div"); track.className = "gantt-track";
    for (const down of data.downtimes.filter((item) => item.center_id === center.id)) {
      const block = document.createElement("div"); block.className = "downtime";
      block.style.left = `${percent(down.start)}%`; block.style.width = `${Math.max(0.8, percent(down.end) - percent(down.start))}%`;
      block.title = `${down.reason}: ${fmt(down.start)}–${fmt(down.end)}`; track.append(block);
    }
    for (const op of data.operations.filter((item) => item.center_id === center.id)) {
      const bar = document.createElement("div"); bar.className = `gantt-bar family-${op.family}`;
      bar.style.left = `${percent(op.start_at)}%`; bar.style.width = `${Math.max(1.8, percent(op.end_at) - percent(op.start_at))}%`;
      bar.textContent = op.order.replace("SO-", ""); bar.title = `${op.order} · ${op.product}\n${fmt(op.start_at)}–${fmt(op.end_at)}\n${t("setup")}: ${op.setup_minutes} ${t("minutes")}`;
      track.append(bar);
    }
    row.append(track); board.append(row);
  }
  $("gantt").replaceChildren(board);
}
function renderCenters(data) {
  const list = document.createElement("div"); list.className = "plain-list";
  for (const center of data.work_centers) {
    const details = `${t("shift")} ${center.shift} · ${t("capacity")} ${center.units_per_hour} ${t("hours")} · ${t("setup")} ${center.setup_minutes} ${t("minutes")}`;
    const downtime = data.downtimes.filter((item) => item.center_id === center.id).map((item) => `${item.reason} ${fmt(item.start)}–${fmt(item.end)}`).join("；") || t("noDowntime");
    const row = document.createElement("div"); row.className = "plain-row"; row.append(text("strong", `${center.id} · ${center.name}`), text("span", `${details}\n${t("downtimeLabel")}: ${downtime}`)); list.append(row);
  }
  $("centers").replaceChildren(list);
}
function renderInventory(data) {
  const list = document.createElement("div"); list.className = "plain-list";
  for (const item of data.inventory) {
    const row = document.createElement("div"); row.className = "plain-row"; row.append(text("strong", item.item));
    row.append(text("span", `${t("onHand")} ${item.on_hand} · ${t("required")} ${item.required} · ${item.status}`, item.status.includes("短缺") ? "shortage" : "")); list.append(row);
  }
  $("inventory").replaceChildren(list);
}
function renderSources(data, trace = data.trace) {
  $("sources").replaceChildren(...data.sources.map((source) => {
    const node = document.createElement("div"); node.className = "source"; node.append(text("strong", source.name), text("span", source.detail)); return node;
  }));
  $("trace").textContent = JSON.stringify(trace, null, 2);
}
function scheduledScenarioText(data) {
  const items = [];
  if (data.scenario.rush_order) items.push("SO-1006");
  if (data.scenario.smt_downtime_hours) items.push(`SMT-01 +${data.scenario.smt_downtime_hours}h`);
  if (data.scenario.material_delay_days) items.push(`MCU-C +${data.scenario.material_delay_days}d`);
  return items.length ? `${t("currentScenario")}：${items.join(" · ")}` : t("baseline");
}
function renderSchedule(data, trace = data.trace) {
  state.schedule = data; state.trace = trace;
  renderMetrics(data); renderOrders(data); renderGantt(data); renderCenters(data); renderInventory(data); renderSources(data, trace);
  $("scenarioState").textContent = scheduledScenarioText(data);
}
function renderLanguage() {
  document.documentElement.lang = state.language;
  document.title = `${t("title")} · AI Work`;
  for (const node of document.querySelectorAll("[data-copy]")) node.textContent = t(node.dataset.copy);
  for (const node of document.querySelectorAll("[data-copy-placeholder]")) node.placeholder = t(node.dataset.copyPlaceholder);
  $("language").textContent = state.language === "en" ? "繁" : "EN";
  const selected = $("sampleQuestion").value;
  $("sampleQuestion").replaceChildren(...t("samples").map((label, index) => {
    const option = document.createElement("option"); option.value = index ? String(index - 1) : ""; option.textContent = label; return option;
  }));
  $("sampleQuestion").value = selected;
  if (selected !== "") $("prompt").value = t("samples")[Number(selected) + 1];
  if (state.schedule) renderSchedule(state.schedule, state.trace);
}
async function generate() {
  await work(t("generating"), async () => renderSchedule(await request("/api/manufacturing-schedule-demo/schedule", { scenario: scenario() })));
}
$("runSchedule").addEventListener("click", generate);
for (const id of ["rushOrder", "downtimeHours", "materialDelay"]) $(id).addEventListener("change", () => { $("scenarioState").textContent = t("dirty"); });
$("sampleQuestion").addEventListener("change", () => {
  if ($("sampleQuestion").value !== "") {
    const index = Number($("sampleQuestion").value);
    $("prompt").value = t("samples")[index + 1];
    if (index === 2) { $("downtimeHours").value = "2"; $("scenarioState").textContent = t("dirty"); }
  }
  $("prompt").focus();
});
$("prompt").addEventListener("input", () => { $("sampleQuestion").value = ""; });
$("askForm").addEventListener("submit", (event) => {
  event.preventDefault(); const prompt = $("prompt").value.trim(); if (!prompt) return;
  work(t("thinking"), async () => {
    const result = await request("/api/manufacturing-schedule-demo/ask", { prompt, scenario: scenario() });
    renderSchedule(result.schedule, result.steps); $("answer").textContent = result.answer; $("modelName").textContent = result.model || ""; $("answerPanel").hidden = false;
  });
});
$("language").addEventListener("click", () => { state.language = state.language === "en" ? "zh-Hant" : "en"; localStorage.setItem("ai-work-lang", state.language); renderLanguage(); });
renderLanguage(); generate();
