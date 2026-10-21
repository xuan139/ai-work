const $ = (id) => document.getElementById(id);

function dateTime(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("zh-TW", { dateStyle: "medium", timeStyle: "short", hour12: false }).format(new Date(value));
}

async function request(path, options = {}) {
  const response = await fetch(path, options);
  if (response.status === 401) {
    location.href = "/";
    throw new Error("登入已失效");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
  return data;
}

function setBusy(busy) {
  $("busy").hidden = !busy;
  $("generate").disabled = busy;
  $("refresh").disabled = busy;
  if (busy) $("error").hidden = true;
}

function node(tag, text = "", className = "") {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  return element;
}

function plainRows(items) {
  if (!items.length) return [node("p", "目前沒有需要關注的項目。", "empty")];
  return items.map(({ title, detail }) => {
    const row = node("div", "", "plain-row");
    row.append(node("strong", title), node("span", detail));
    return row;
  });
}

function renderReport(record) {
  const report = record.report;
  if (!report) return;
  $("current").hidden = false;
  $("download").href = record.download_url;
  $("reportStatus").textContent = report.status === "attention" ? "需要關注" : "正常";
  $("reportStatus").className = `badge ${report.status}`;
  $("reportMeta").textContent = `${report.report_date} · ${report.plant} · 截止 ${dateTime(report.snapshot_at)} · ${record.source_count} 個來源`;

  $("kpis").replaceChildren(...Object.values(report.kpis).map((metric) => {
    const card = node("article", "", `kpi ${metric.status}`);
    card.append(node("strong", metric.label), node("span", metric.display, "kpi-value"), node("small", `${metric.formula} · ${metric.sources.join("、")}`));
    card.title = metric.note || metric.formula;
    return card;
  }));
  $("summary").replaceChildren(...report.executive_summary.map((item) => node("li", item)));

  $("risks").replaceChildren(...plainRows(report.delivery_risks.map((item) => ({
    title: `${item.order} · ${item.customer}`,
    detail: `${item.product} · 預計延遲 ${item.late_minutes} 分鐘 · ${item.reasons.join("；")} · ${item.sources.join("、")}`,
  }))));
  const exceptions = [
    ...report.material_shortages.map((item) => ({ title: `缺料 · ${item.item}`, detail: `${item.status} · ${item.sources.join("、")}` })),
    ...report.quality_events.map((item) => ({ title: `品質 · ${item.event_id || "未編號"}`, detail: `${item.summary || "-"} · S4` })),
    ...report.equipment_risks.map((item) => ({ title: `設備 · ${item.center_id || "-"}`, detail: `${item.reason || "-"} · S5` })),
  ];
  $("exceptions").replaceChildren(...plainRows(exceptions));
  $("sources").replaceChildren(...report.sources.map((source) => {
    const item = node("div", "", "source-item");
    item.append(node("code", source.ref), document.createTextNode(` · ${source.name} · ${source.detail}`));
    return item;
  }));
  $("trace").textContent = JSON.stringify(report.tool_trace, null, 2);
  $("current").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderHistory(reports) {
  $("empty").hidden = reports.length > 0;
  $("historyBody").replaceChildren(...reports.map((report) => {
    const row = document.createElement("tr");
    const values = [report.report_date, report.plant, report.created_by, report.status === "completed" ? "已完成" : report.status === "failed" ? "失敗" : "產生中", `${report.source_count} 個`, dateTime(report.created_at)];
    for (const value of values) row.append(node("td", String(value || "-")));
    const actions = document.createElement("td");
    if (report.status === "completed") {
      const view = node("button", "查看", "row-action"); view.type = "button";
      view.addEventListener("click", () => showReport(report.id));
      const download = node("a", "PDF", "row-action"); download.href = report.download_url;
      actions.append(view, download);
    } else if (report.error_message) {
      actions.append(node("span", report.error_message));
    }
    row.append(actions);
    return row;
  }));
}

async function loadHistory() {
  const data = await request("/api/daily-production-reports?limit=50");
  renderHistory(data.reports || []);
}

async function showReport(id) {
  setBusy(true);
  try { renderReport(await request(`/api/daily-production-reports/${id}`)); }
  catch (error) { $("error").textContent = error.message; $("error").hidden = false; }
  finally { setBusy(false); }
}

async function generate() {
  setBusy(true);
  try {
    const record = await request("/api/daily-production-reports", { method: "POST" });
    renderReport(record);
    await loadHistory();
  } catch (error) {
    $("error").textContent = `報告產生失敗：${error.message}`;
    $("error").hidden = false;
  } finally { setBusy(false); }
}

$("today").textContent = new Intl.DateTimeFormat("zh-TW", { dateStyle: "full" }).format(new Date());
$("generate").addEventListener("click", generate);
$("refresh").addEventListener("click", async () => {
  setBusy(true);
  try { await loadHistory(); }
  catch (error) { $("error").textContent = error.message; $("error").hidden = false; }
  finally { setBusy(false); }
});
loadHistory().catch((error) => { $("error").textContent = error.message; $("error").hidden = false; });
