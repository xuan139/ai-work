const $ = (id) => document.getElementById(id);
const copy = {
  "zh-Hant": {
    back: "返回工作區", title: "電子製造排程 Demo", badge: "LIVE MCP · 唯讀", connected: "資料已連線",
    intro: "透過唯讀 MCP 整合 Odoo、MES、WMS 追溯、PLM／ECO、QMS、SPC 與 CMMS，再由本地有限產能排程引擎計算交期風險。",
    notice: "資料由 MCP 即時讀取；製造周邊系統為明確標示的教學模擬。本頁不會寫入企業系統或 PLC。", warnings: "資料邊界與假設", expand: "展開",
    navControls: "情境與問答", navEngines: "引擎比較", navSchedule: "排程結果", navSystems: "系統證據",
    scenarioEyebrow: "WHAT-IF 模擬", scenarioTitle: "選擇情境並重新排程", run: "產生有限產能排程",
    rush: "加入模擬急單", rushHelp: "沿用最新 MCP 訂單的產品條件，建立 WHAT-IF 急單", downtime: "SMT-01 模擬停機",
    materialDelay: "短缺物料到料延後", none: "不增加", twoHours: "2 小時", fourHours: "4 小時", twoDays: "2 個工作日", threeDays: "3 個工作日",
    baseline: "目前顯示基準情境。", currentScenario: "目前排程情境", dirty: "情境已變更，請重新產生排程。",
    comparisonEyebrow: "DUAL ENGINE · SAME MCP SNAPSHOT", comparisonTitle: "雙引擎排程比較",
    comparisonHelp: "現有規則引擎與 OR-Tools 使用完全相同的 MCP 資料與情境。",
    ruleEngine: "現有規則引擎", ortoolsEngine: "OR-Tools CP-SAT", solverStatus: "求解狀態", solveTime: "求解時間",
    weightedLate: "加權延期", changeoverMinutes: "換線分鐘", makespan: "總完工跨度", defaultEngine: "系統預設引擎",
    saveDefault: "儲存預設", saved: "預設引擎已更新", active: "目前使用", validated: "比較通過：OR-Tools 未增加延期或換線，且至少一項改善。",
    notValidated: "尚未通過改善條件；保留規則引擎為預設。", unavailable: "OR-Tools 無法使用，已回退規則引擎。",
    ruleGantt: "規則引擎甘特圖", ortoolsGantt: "OR-Tools 甘特圖", minutesShort: "分鐘",
    qaEyebrow: "LOCAL LLM · 可追溯", qaTitle: "AI 排程問答", sample: "範例問題", prompt: "您的問題",
    promptPlaceholder: "例如：目前哪些訂單可能延期？", ask: "詢問目前排程", answer: "模型回答",
    resultsEyebrow: "SCHEDULE OUTPUT", resultsTitle: "排程結果與交期風險", resultsHelp: "先查看訂單風險，再以工作中心時間軸確認產能配置。", readOnlyData: "唯讀決策資料",
    orders: "訂單與預測交期", order: "訂單", customer: "客戶", product: "產品", quantity: "數量", priority: "優先級", sourceType: "來源",
    due: "要求交期", predicted: "預測完成", risk: "延期風險", reason: "主要原因", gantt: "工作中心甘特圖",
    ganttHelp: "包含工序順序、班次、換線與停機避讓", legend: "色彩代表產品家族；條形內顯示訂單。",
    centers: "工作中心與停機", inventory: "庫存與缺料", quality: "品質與預期返工", maintenance: "設備健康與維護",
    wms: "倉儲、批次與序號追溯", plm: "BOM 版本與工程變更", spc: "製程能力與失控點",
    systemsEyebrow: "CONNECTED OPERATIONS", systemsTitle: "製造系統證據", systemsHelp: "依需要展開各系統快照；關鍵風險已納入排程計算。", viewData: "查看資料",
    sources: "資料來源與工具軌跡", trace: "查看完整工具呼叫軌跡", auditReady: "可追溯",
    generating: "正在計算有限產能排程…", thinking: "模型正在根據目前排程產生說明…", failed: "操作失敗",
    metrics: ["訂單", "預計延期", "準時", "換線", "最晚完成"], riskLabels: { low: "低", medium: "中", high: "高" },
    metricDetailEyebrow: "SCHEDULE METRIC", viewDetails: "查看詳情", close: "關閉", records: "筆明細",
    center: "工作中心", start: "開始", end: "結束", setupTime: "換線時間", noDetails: "目前沒有符合條件的明細。",
    metricDescriptions: ["目前情境中的全部訂單", "預測完成時間超過要求交期的訂單", "預測可在要求交期前完成的訂單", "排程中需要換線準備的工序", "依預測完成時間由晚至早排列"],
    priorityLabels: { normal: "一般", high: "高", urgent: "急單" }, shift: "班次", capacity: "產能", setup: "換線",
    downtimeLabel: "停機", noDowntime: "無停機", hours: "件／小時", minutes: "分鐘", onHand: "現有", available: "可用", required: "需求",
    orderSources: { odoo_mcp: "Odoo MCP", mes_mcp_demo: "MES 教學", what_if: "WHAT-IF" },
    samples: ["選擇範例問題", "目前哪些訂單可能延期？", "訂單 S00003 為什麼無法準時交付？",
      "如果 SMT-01 停機兩小時，會影響哪些訂單？", "如何調整排程可以減少換線？",
      "哪個產品家族的品質風險最高？", "目前哪些設備維護會影響交期？",
      "家族 C 的物料在哪個倉位，何時齊套？", "ECO-2026-014 會影響哪些訂單？",
      "哪個製程的 Cpk 低於 1.33，會增加多少檢驗時間？",
      "本地有限產能排程引擎是什麼？它根據哪些資料計算？",
      "目前排程使用了哪些 MCP 資料來源？",
      "哪張訂單的延期風險最高？主要原因是什麼？",
      "物料到料延後三個工作日，會影響哪些訂單？",
      "加入模擬急單後，哪些原有訂單會被延後？",
      "批次 LOT-MCU-C-2610 影響哪些序號與訂單？",
      "SMT-01 的設備健康與維護工單目前如何？",
      "要求交期與預測完成時間有什麼差別？",
      "請依訂單列出物料、工程變更、品質與設備風險摘要。"],
  },
  en: {
    back: "Back to workspace", title: "Electronics Scheduling Demo", badge: "LIVE MCP · READ-ONLY", connected: "Data connected",
    intro: "Combine Odoo, MES, WMS traceability, PLM/ECO, QMS, SPC, and CMMS through read-only MCP, then calculate delivery risk locally.",
    notice: "Data is fetched through MCP. Manufacturing support systems are explicitly synthetic teaching data. This page never writes to enterprise systems or PLCs.", warnings: "Data boundaries and assumptions", expand: "Expand",
    navControls: "Scenario and Q&A", navEngines: "Engine comparison", navSchedule: "Schedule output", navSystems: "System evidence",
    scenarioEyebrow: "WHAT-IF SIMULATION", scenarioTitle: "Select a scenario and reschedule", run: "Generate finite-capacity schedule",
    rush: "Add a simulated rush order", rushHelp: "Copy the latest MCP order conditions into a WHAT-IF order", downtime: "SMT-01 simulated downtime",
    materialDelay: "Delay shortage replenishment", none: "No addition", twoHours: "2 hours", fourHours: "4 hours", twoDays: "2 workdays", threeDays: "3 workdays",
    baseline: "Showing the baseline scenario.", currentScenario: "Current schedule scenario", dirty: "Scenario changed. Generate the schedule again.",
    comparisonEyebrow: "DUAL ENGINE · SAME MCP SNAPSHOT", comparisonTitle: "Dual-engine schedule comparison",
    comparisonHelp: "The rule engine and OR-Tools use the exact same MCP data and scenario.",
    ruleEngine: "Current rule engine", ortoolsEngine: "OR-Tools CP-SAT", solverStatus: "Solver status", solveTime: "Solve time",
    weightedLate: "Weighted lateness", changeoverMinutes: "Changeover minutes", makespan: "Makespan", defaultEngine: "System default engine",
    saveDefault: "Save default", saved: "Default engine updated", active: "Active", validated: "Validation passed: OR-Tools improves at least one metric without worsening lateness or changeovers.",
    notValidated: "Improvement condition not yet met; keep the rule engine as default.", unavailable: "OR-Tools is unavailable; the rule engine was used as fallback.",
    ruleGantt: "Rule-engine Gantt", ortoolsGantt: "OR-Tools Gantt", minutesShort: "min",
    qaEyebrow: "LOCAL LLM · TRACEABLE", qaTitle: "AI scheduling Q&A", sample: "Sample question", prompt: "Your question",
    promptPlaceholder: "Example: Which orders may be late?", ask: "Ask about this schedule", answer: "Model answer",
    resultsEyebrow: "SCHEDULE OUTPUT", resultsTitle: "Schedule output and delivery risk", resultsHelp: "Review order risk first, then confirm capacity allocation on the work-center timeline.", readOnlyData: "Read-only decision data",
    orders: "Orders and predicted delivery", order: "Order", customer: "Customer", product: "Product", quantity: "Qty", priority: "Priority", sourceType: "Source",
    due: "Requested due", predicted: "Predicted finish", risk: "Delay risk", reason: "Primary reason", gantt: "Work-center Gantt",
    ganttHelp: "Includes routing, shifts, changeovers and downtime avoidance", legend: "Colors identify product families; bars show order IDs.",
    centers: "Work centers and downtime", inventory: "Inventory and shortages", quality: "Quality and expected rework", maintenance: "Asset health and maintenance",
    wms: "Warehouse, lot, and serial traceability", plm: "BOM revisions and engineering changes", spc: "Process capability and control violations",
    systemsEyebrow: "CONNECTED OPERATIONS", systemsTitle: "Manufacturing system evidence", systemsHelp: "Expand system snapshots as needed; material risks are already included in scheduling.", viewData: "View data",
    sources: "Sources and tool trace", trace: "View full tool-call trace", auditReady: "Traceable",
    generating: "Calculating the finite-capacity schedule…", thinking: "The model is explaining the current schedule…", failed: "Operation failed",
    metrics: ["Orders", "Late", "On time", "Changeovers", "Latest finish"], riskLabels: { low: "Low", medium: "Medium", high: "High" },
    metricDetailEyebrow: "SCHEDULE METRIC", viewDetails: "View details", close: "Close", records: "records",
    center: "Work center", start: "Start", end: "End", setupTime: "Changeover", noDetails: "No matching details in the current schedule.",
    metricDescriptions: ["All orders in the current scenario", "Orders predicted to finish after their requested due time", "Orders predicted to finish by their requested due time", "Scheduled operations that require changeover preparation", "Orders sorted from latest to earliest predicted completion"],
    priorityLabels: { normal: "Normal", high: "High", urgent: "Rush" }, shift: "Shift", capacity: "Capacity", setup: "Changeover",
    downtimeLabel: "Downtime", noDowntime: "No downtime", hours: "units/hour", minutes: "minutes", onHand: "On hand", available: "Available", required: "Required",
    orderSources: { odoo_mcp: "Odoo MCP", mes_mcp_demo: "MES teaching", what_if: "WHAT-IF" },
    samples: ["Choose a sample question", "Which orders may be late?", "Why can order S00003 not finish on time?",
      "Which orders are affected if SMT-01 stops for two hours?", "How can the schedule reduce changeovers?",
      "Which product family has the highest quality risk?", "Which maintenance windows affect delivery?",
      "Where is family C material and when is it ready?", "Which orders are affected by ECO-2026-014?",
      "Which process has Cpk below 1.33 and how much inspection time is added?",
      "What is the local finite-capacity scheduling engine and which inputs does it use?",
      "Which MCP data sources are used by this schedule?",
      "Which order has the highest delay risk and why?",
      "Which orders are affected by a three-workday material delay?",
      "Which existing orders move later after adding the simulated rush order?",
      "Which serials and orders are affected by lot LOT-MCU-C-2610?",
      "What is the current health and maintenance order for SMT-01?",
      "What is the difference between requested due time and predicted completion?",
      "Summarize material, engineering-change, quality, and equipment risks by order."],
  },
};
const state = { language: localStorage.getItem("ai-work-lang") === "en" ? "en" : "zh-Hant", schedule: null, trace: [], engineSetting: null };
const t = (key) => copy[state.language][key];

function scenario() {
  return { rush_order: $("rushOrder").checked, smt_downtime_hours: Number($("downtimeHours").value), material_delay_days: Number($("materialDelay").value) };
}
async function request(path, payload, method = "POST") {
  const response = await fetch(path, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (response.status === 401) { location.href = "/"; throw new Error("Login required"); }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
  return data;
}
function setBusy(message = "") {
  const busy = Boolean(message);
  $("busy").hidden = !busy; $("busy").textContent = message;
  if (busy) $("error").hidden = true;
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

function detailTable(columns, rows) {
  if (!rows.length) return text("p", t("noDetails"), "dialog-empty");
  const scroll = document.createElement("div"); scroll.className = "dialog-table-scroll";
  const table = document.createElement("table"); table.className = "detail-table";
  const head = document.createElement("thead"); const headRow = document.createElement("tr");
  for (const column of columns) headRow.append(text("th", column));
  head.append(headRow); table.append(head);
  const body = document.createElement("tbody");
  for (const values of rows) {
    const row = document.createElement("tr");
    for (const value of values) cell(row, value);
    body.append(row);
  }
  table.append(body); scroll.append(table); return scroll;
}
function orderDetailRows(orders) {
  return orders.map((order) => [order.order, order.customer || "-", order.product, String(order.quantity), fmt(order.due_at), fmt(order.predicted_completion_at), `${t("riskLabels")[order.risk_level]} · ${order.risk_probability}%`, order.reasons.join("；")]);
}
function openMetricDetail(index, data) {
  const labels = t("metrics");
  let columns; let rows;
  if (index === 3) {
    columns = [t("order"), t("center"), t("start"), t("end"), t("setupTime")];
    rows = data.operations.filter((operation) => operation.setup_minutes > 0).map((operation) => [operation.order, operation.center_id, fmt(operation.start_at), fmt(operation.end_at), `${operation.setup_minutes} ${t("minutes")}`]);
  } else {
    columns = [t("order"), t("customer"), t("product"), t("quantity"), t("due"), t("predicted"), t("risk"), t("reason")];
    const late = (order) => Number(order.late_minutes || 0) > 0;
    let orders = index === 1 ? data.orders.filter(late) : index === 2 ? data.orders.filter((order) => !late(order)) : [...data.orders];
    if (index === 4) orders.sort((a, b) => new Date(b.predicted_completion_at) - new Date(a.predicted_completion_at));
    rows = orderDetailRows(orders);
  }
  $("metricDialogTitle").textContent = labels[index];
  $("metricDialogSummary").textContent = `${t("metricDescriptions")[index]} · ${rows.length} ${t("records")}`;
  $("metricDialogBody").replaceChildren(detailTable(columns, rows));
  $("closeMetricDialog").ariaLabel = t("close");
  $("closeMetricDialog").title = t("close");
  $("metricDialog").showModal();
}
function renderMetrics(data) {
  const values = [data.summary.order_count, data.summary.late_count, data.summary.on_time_count,
    data.summary.setup_count, fmt(data.summary.latest_completion_at)];
  $("metrics").replaceChildren(...values.map((value, index) => {
    const item = document.createElement("button"); item.type = "button"; item.className = "metric";
    item.ariaLabel = `${t("metrics")[index]}：${value}。${t("viewDetails")}`;
    item.append(text("span", String(value), "metric-value"), text("small", t("metrics")[index], "metric-label"), text("span", t("viewDetails"), "metric-action"));
    item.addEventListener("click", () => openMetricDetail(index, data));
    return item;
  }));
}
function renderOrders(data) {
  $("ordersBody").replaceChildren(...data.orders.map((order) => {
    const row = document.createElement("tr");
    cell(row, order.order); cell(row, order.customer || "-"); cell(row, order.product); cell(row, String(order.quantity));
    cell(row, t("priorityLabels")[order.priority]); cell(row, fmt(order.due_at)); cell(row, fmt(order.predicted_completion_at));
    const risk = document.createElement("td"); risk.append(text("span", `${t("riskLabels")[order.risk_level]} · ${order.risk_probability}%`, `risk risk-${order.risk_level}`)); row.append(risk);
    const origin = document.createElement("td"); origin.append(text("span", t("orderSources")[order.source_kind] || order.source_kind || "-", "origin")); row.append(origin);
    cell(row, order.reasons.join("；")); return row;
  }));
}
function renderGanttInto(targetId, data) {
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
  $(targetId).replaceChildren(board);
}
function renderGantt(data) { renderGanttInto("gantt", data); }

function metricLine(label, value) {
  const row = document.createElement("div"); row.className = "engine-metric";
  row.append(text("span", label), text("strong", value)); return row;
}
function renderEngineComparison(data) {
  const comparison = data.engine_comparison;
  if (!comparison) { $("engineComparison").hidden = true; return; }
  $("engineComparison").hidden = false;
  if (data.engine_setting) state.engineSetting = data.engine_setting;
  const setting = state.engineSetting;
  if (setting) {
    const selected = $("defaultEngine").value || setting.current.id;
    $("defaultEngine").replaceChildren(...setting.options.map((option) => {
      const node = document.createElement("option"); node.value = option.id; node.textContent = option.name;
      node.disabled = option.id === "ortools-cp-sat-v1" && !comparison.validated_better && setting.current.id !== option.id;
      return node;
    }));
    $("defaultEngine").value = setting.options.some((item) => item.id === selected) ? selected : setting.current.id;
    $("engineSettingControls").hidden = !setting.can_manage;
  }
  const rule = comparison.metrics.rule;
  const optimized = comparison.metrics.ortools;
  $("ruleEngineName").textContent = `${t("ruleEngine")}${comparison.active_engine === "finite-capacity-mcp-v4" ? ` · ${t("active")}` : ""}`;
  $("ruleMetrics").replaceChildren(
    metricLine(t("weightedLate"), `${rule.weighted_late_minutes} ${t("minutesShort")}`),
    metricLine(t("changeoverMinutes"), `${rule.changeover_minutes} ${t("minutesShort")}`),
    metricLine(t("makespan"), `${rule.makespan_minutes} ${t("minutesShort")}`),
  );
  if (optimized && comparison.ortools) {
    const engine = comparison.ortools.engine;
    $("ortoolsEngineName").textContent = `${t("ortoolsEngine")}${comparison.active_engine === "ortools-cp-sat-v1" ? ` · ${t("active")}` : ""}`;
    $("ortoolsMetrics").replaceChildren(
      metricLine(t("weightedLate"), `${optimized.weighted_late_minutes} ${t("minutesShort")}`),
      metricLine(t("changeoverMinutes"), `${optimized.changeover_minutes} ${t("minutesShort")}`),
      metricLine(t("makespan"), `${optimized.makespan_minutes} ${t("minutesShort")}`),
      metricLine(t("solverStatus"), engine.solver_status || "-"),
      metricLine(t("solveTime"), `${engine.solve_time_ms || 0} ms`),
    );
    $("ortoolsGanttWrap").hidden = false;
    renderGanttInto("ruleGantt", comparison.rule);
    renderGanttInto("ortoolsGantt", comparison.ortools);
  } else {
    $("ortoolsEngineName").textContent = t("ortoolsEngine");
    $("ortoolsMetrics").replaceChildren(text("p", comparison.ortools_error || t("unavailable"), "shortage"));
    $("ortoolsGanttWrap").hidden = true;
    renderGanttInto("ruleGantt", comparison.rule);
  }
  const delta = comparison.delta || {};
  const deltaText = comparison.validated_better
    ? ` ${t("weightedLate")} ↓ ${delta.weighted_late_minutes_reduced ?? "-"} ${t("minutesShort")} · ${t("changeoverMinutes")} ↓ ${delta.changeover_minutes_reduced ?? "-"} ${t("minutesShort")}`
    : "";
  const message = !comparison.ortools_available ? t("unavailable") : comparison.validated_better ? `${t("validated")}${deltaText}` : t("notValidated");
  $("comparisonVerdict").textContent = message;
  $("comparisonVerdict").className = comparison.validated_better ? "comparison-verdict passed" : "comparison-verdict";
}
function renderCenters(data) {
  const mes = data.mes_snapshot || {};
  $("mesStatus").textContent = mes.plant ? `${mes.plant} · ${mes.notice || ""}` : "";
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
    const available = item.available === undefined ? "" : ` · ${t("available")} ${item.available}`;
    row.append(text("span", `${t("onHand")} ${item.on_hand}${available} · ${t("required")} ${item.required} · ${item.status}`, item.status.includes("短缺") ? "shortage" : "")); list.append(row);
  }
  $("inventory").replaceChildren(list);
}
function renderQuality(data) {
  const snapshot = data.qms_snapshot || {};
  $("qmsStatus").textContent = snapshot.notice || "";
  const list = document.createElement("div"); list.className = "plain-list";
  for (const item of snapshot.profiles || []) {
    const row = document.createElement("div"); row.className = "plain-row";
    row.append(text("strong", `Family ${item.family} · FPY ${item.first_pass_yield_pct}%`),
      text("span", `${item.top_defect} · ${item.expected_rework_minutes_per_100} min / 100 units`, item.quality_level === "alert" ? "shortage" : ""));
    list.append(row);
  }
  $("quality").replaceChildren(list);
}
function renderMaintenance(data) {
  const snapshot = data.cmms_snapshot || {};
  $("cmmsStatus").textContent = snapshot.notice || "";
  const list = document.createElement("div"); list.className = "plain-list";
  for (const item of snapshot.assets || []) {
    const row = document.createElement("div"); row.className = "plain-row";
    const workOrder = item.open_work_order ? ` · ${item.open_work_order}` : "";
    row.append(text("strong", `${item.center_id} · ${item.health}`),
      text("span", `${item.reason}${workOrder}`, item.health === "watch" ? "shortage" : ""));
    list.append(row);
  }
  $("maintenance").replaceChildren(list);
}
function renderWms(data) {
  const snapshot = data.wms_snapshot || {};
  $("wmsStatus").textContent = snapshot.notice || "";
  const list = document.createElement("div"); list.className = "plain-list";
  for (const item of snapshot.material_profiles || []) {
    const row = document.createElement("div"); row.className = "plain-row";
    const lots = (item.lot_ids || []).join(", ") || "-";
    row.append(text("strong", `Family ${item.family} · ${item.item}`),
      text("span", `${item.location} · available ${item.available_units} · ${lots} · ready ${fmt(item.ready_at)}`, item.status === "inbound" ? "shortage" : ""));
    list.append(row);
  }
  const genealogy = snapshot.serial_genealogy || [];
  if (genealogy.length) {
    const row = document.createElement("div"); row.className = "plain-row";
    row.append(text("strong", genealogy[0].serial), text("span", `${genealogy[0].order} · ${(genealogy[0].consumed_lots || []).join(" + ")}`));
    list.append(row);
  }
  $("wms").replaceChildren(list);
}
function renderPlm(data) {
  const snapshot = data.plm_snapshot || {};
  $("plmStatus").textContent = snapshot.notice || "";
  const list = document.createElement("div"); list.className = "plain-list";
  for (const item of snapshot.revisions || []) {
    const row = document.createElement("div"); row.className = "plain-row";
    row.append(text("strong", `Family ${item.family} · ${item.bom}`),
      text("span", `${item.revision} · ${item.status} · +${item.extra_setup_minutes + item.extra_operation_minutes} min`, item.status !== "released" ? "shortage" : ""));
    list.append(row);
  }
  for (const eco of snapshot.open_ecos || []) {
    const row = document.createElement("div"); row.className = "plain-row";
    row.append(text("strong", eco.eco_id), text("span", `${eco.status} · ${eco.summary}`, eco.risk === "high" ? "shortage" : ""));
    list.append(row);
  }
  $("plm").replaceChildren(list);
}
function renderSpc(data) {
  const snapshot = data.spc_snapshot || {};
  $("spcStatus").textContent = snapshot.notice || "";
  const list = document.createElement("div"); list.className = "plain-list";
  for (const item of snapshot.profiles || []) {
    const row = document.createElement("div"); row.className = "plain-row";
    row.append(text("strong", `Family ${item.family} · ${item.center_id}`),
      text("span", `Cp ${item.cp} · Cpk ${item.cpk} · ${item.metric} · +${item.extra_inspection_minutes_per_100} min / 100`, item.cpk < 1.33 ? "shortage" : ""));
    list.append(row);
  }
  for (const point of snapshot.out_of_control_points || []) {
    const row = document.createElement("div"); row.className = "plain-row";
    row.append(text("strong", point.point_id), text("span", `${point.center_id} · ${point.rule} · ${point.observed_at}`, "shortage"));
    list.append(row);
  }
  $("spc").replaceChildren(list);
}
function renderSources(data, trace = data.trace) {
  $("sources").replaceChildren(...data.sources.map((source) => {
    const node = document.createElement("div"); node.className = "source"; node.append(text("strong", source.name), text("span", source.detail)); return node;
  }));
  $("trace").textContent = JSON.stringify(trace, null, 2);
}
function scheduledScenarioText(data) {
  const items = [];
  if (data.scenario.rush_order) items.push("WHAT-IF rush order");
  if (data.scenario.smt_downtime_hours) items.push(`SMT-01 +${data.scenario.smt_downtime_hours}h`);
  if (data.scenario.material_delay_days) items.push(`shortage +${data.scenario.material_delay_days}d`);
  return items.length ? `${t("currentScenario")}：${items.join(" · ")}` : t("baseline");
}
function renderSchedule(data, trace = data.trace) {
  state.schedule = data; state.trace = trace;
  renderEngineComparison(data);
  renderMetrics(data); renderOrders(data); renderGantt(data); renderCenters(data); renderInventory(data);
  renderQuality(data); renderMaintenance(data); renderWms(data); renderPlm(data); renderSpc(data); renderSources(data, trace);
  $("snapshotNotice").textContent = `${t("notice")} Snapshot: ${fmt(data.snapshot_at)}.`;
  const warnings = data.integration_warnings || [];
  $("warningList").replaceChildren(...warnings.map((warning) => text("li", warning)));
  $("integrationWarnings").hidden = warnings.length === 0;
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
$("saveEngine").addEventListener("click", async () => {
  const engineId = $("defaultEngine").value;
  await work(t("generating"), async () => {
    const current = await request("/api/admin/manufacturing-schedule-engine", { engine_id: engineId }, "PUT");
    state.engineSetting = { ...state.engineSetting, current };
    $("engineSaveStatus").textContent = t("saved");
    renderSchedule(await request("/api/manufacturing-schedule-demo/schedule", { scenario: scenario() }));
  });
});
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
$("closeMetricDialog").addEventListener("click", () => $("metricDialog").close());
$("metricDialog").addEventListener("click", (event) => { if (event.target === $("metricDialog")) $("metricDialog").close(); });
$("askForm").addEventListener("submit", async (event) => {
  event.preventDefault(); const prompt = $("prompt").value.trim(); if (!prompt) return;
  $("answerPanel").hidden = false;
  $("answerPanel").classList.remove("answer-error");
  $("answer").textContent = t("thinking");
  $("modelName").textContent = "";
  $("answerPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
  setBusy(t("thinking"));
  try {
    const result = await request("/api/manufacturing-schedule-demo/ask", { prompt, scenario: scenario() });
    renderSchedule(result.schedule, result.steps);
    $("answer").textContent = result.answer;
    $("modelName").textContent = result.model || "";
  } catch (error) {
    $("answerPanel").classList.add("answer-error");
    $("answer").textContent = `${t("failed")}：${error.message}`;
    $("error").textContent = `${t("failed")}：${error.message}`;
    $("error").hidden = false;
  } finally {
    setBusy();
    $("answerPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
});
$("language").addEventListener("click", () => { if ($("metricDialog").open) $("metricDialog").close(); state.language = state.language === "en" ? "zh-Hant" : "en"; localStorage.setItem("ai-work-lang", state.language); renderLanguage(); });
renderLanguage(); generate();
