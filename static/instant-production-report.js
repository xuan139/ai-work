const $ = (id) => document.getElementById(id);
let activeReport = null;

const defaultRules = {
  plan_attainment_min: 90,
  first_pass_yield_min: 95,
  oee_min: 75,
  predicted_on_time_min: 95,
  late_orders_max: 0,
  shortage_items_max: 0,
  downtime_minutes_max: 60,
};

function dateTime(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("zh-TW", { dateStyle: "medium", timeStyle: "medium", hour12: false }).format(new Date(value));
}

async function request(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
  if (response.status === 401) {
    location.href = "/";
    throw new Error("登入已失效");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
  return data;
}

function node(tag, text = "", className = "") {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  return element;
}

function setBusy(busy, message = "正在處理，請稍候…") {
  $("busy").textContent = message;
  $("busy").hidden = !busy;
  for (const id of ["generate", "refresh", "push", "email", "ask"]) $(id).disabled = busy;
  if (busy) $("error").hidden = true;
}

function showNotice(message) {
  $("notice").textContent = message;
  $("notice").hidden = false;
}

function showError(message) {
  $("error").textContent = message;
  $("error").hidden = false;
}

function rulesFromForm() {
  return {
    plan_attainment_min: Number($("planAttainmentMin").value),
    first_pass_yield_min: Number($("firstPassYieldMin").value),
    oee_min: Number($("oeeMin").value),
    predicted_on_time_min: Number($("predictedOnTimeMin").value),
    late_orders_max: Number($("lateOrdersMax").value),
    shortage_items_max: Number($("shortageItemsMax").value),
    downtime_minutes_max: Number($("downtimeMinutesMax").value),
  };
}

function applyRules(rules = defaultRules) {
  $("planAttainmentMin").value = rules.plan_attainment_min;
  $("firstPassYieldMin").value = rules.first_pass_yield_min;
  $("oeeMin").value = rules.oee_min;
  $("predictedOnTimeMin").value = rules.predicted_on_time_min;
  $("lateOrdersMax").value = rules.late_orders_max;
  $("shortageItemsMax").value = rules.shortage_items_max;
  $("downtimeMinutesMax").value = rules.downtime_minutes_max;
}

function plainRows(items) {
  if (!items.length) return [node("p", "目前沒有需要關注的項目。", "empty")];
  return items.map(({ title, detail }) => {
    const row = node("div", "", "plain-row");
    row.append(node("strong", title), node("span", detail));
    return row;
  });
}

function renderQuestions(questions = []) {
  $("questionHistory").replaceChildren(...questions.map((item) => {
    const row = node("article", "", "question-item");
    row.append(
      node("strong", item.question),
      node("p", item.answer),
      node("small", `${item.asked_by || "管理者"} · ${item.model_id} · ${dateTime(item.created_at)}`),
    );
    return row;
  }));
}

function renderReport(record) {
  if (!record.report) return;
  activeReport = record;
  const report = record.report;
  $("current").hidden = false;
  $("download").href = record.download_url;
  $("reportStatus").textContent = report.alerts.length ? `觸發 ${report.alerts.length} 項告警` : "正常";
  $("reportStatus").className = `badge ${report.alerts.length ? "attention" : "normal"}`;
  $("reportMeta").textContent = `#${record.id} · ${report.plant} · ${dateTime(report.generated_at)} · 截止 ${dateTime(report.snapshot_at)} · ${record.source_count} 個來源`;
  applyRules(report.alert_rules || defaultRules);

  $("kpis").replaceChildren(...Object.values(report.kpis).map((metric) => {
    const card = node("article", "", `kpi ${metric.status}`);
    card.append(node("strong", metric.label), node("span", metric.display, "kpi-value"), node("small", `${metric.formula} · ${metric.sources.join("、")}`));
    card.title = metric.note || metric.formula;
    return card;
  }));

  $("alerts").replaceChildren(...(report.alerts.length
    ? report.alerts.map((item) => {
      const row = node("div", "", "alert-row");
      row.append(node("strong", `${item.label} · ${item.severity === "critical" ? "嚴重" : "警告"}`), node("span", `${item.message} 來源：${item.sources.join("、")}`));
      return row;
    })
    : [node("p", "本次 KPI 未觸發設定門檻。", "empty")]));

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
  $("pushState").textContent = record.push_status === "completed"
    ? `已推送至 ${record.push_target} · ${dateTime(record.pushed_at)}`
    : record.push_status === "failed" ? `推送失敗：${record.push_error || "未知錯誤"}` : "尚未推送";
  const emailDelivery = (record.deliveries || []).find((item) => item.channel === "gmail");
  $("emailState").textContent = !emailDelivery ? "尚未寄送"
    : emailDelivery.status === "completed"
      ? `已由 ${emailDelivery.sender} 寄送至 ${emailDelivery.recipients.join("、")} · ${dateTime(emailDelivery.completed_at)}`
      : emailDelivery.status === "failed"
        ? `寄送失敗：${emailDelivery.error_message || "未知錯誤"}`
        : emailDelivery.status === "skipped" ? "未觸發告警，已略過寄送" : "寄送中";
  renderQuestions(record.questions || []);
  history.replaceState(null, "", `/instant-production-report?report=${record.id}`);
  $("current").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderHistory(reports) {
  $("empty").hidden = reports.length > 0;
  $("historyBody").replaceChildren(...reports.map((report) => {
    const row = document.createElement("tr");
    const alertCount = Array.isArray(report.alerts) ? report.alerts.length : 0;
    const values = [`#${report.id}`, dateTime(report.created_at), report.plant, `${alertCount} 項`, report.push_status, `${report.source_count} 個`];
    for (const value of values) row.append(node("td", String(value || "-")));
    const actions = document.createElement("td");
    if (report.status === "completed") {
      const view = node("button", "查看", "row-action");
      view.type = "button";
      view.addEventListener("click", () => showReport(report.id));
      const download = node("a", "PDF", "row-action");
      download.href = report.download_url;
      actions.append(view, download);
    } else {
      actions.append(node("span", report.error_message || "產生中"));
    }
    row.append(actions);
    return row;
  }));
}

async function loadHistory() {
  const data = await request("/api/instant-production-reports?limit=50");
  renderHistory(data.reports || []);
}

async function showReport(id) {
  setBusy(true, "正在讀取 NAS 中的報告快照…");
  try { renderReport(await request(`/api/instant-production-reports/${id}`)); }
  catch (error) { showError(error.message); }
  finally { setBusy(false); }
}

async function generate() {
  const autoPush = $("autoPush").checked;
  const autoPushGroup = $("generationLineGroup").value;
  if (autoPush && !autoPushGroup) {
    showError("請先選擇告警自動推送群組。");
    return;
  }
  setBusy(true, "正在透過唯讀 MCP 取得資料、計算 KPI 並產生 PDF，請稍候…");
  $("notice").hidden = true;
  try {
    const record = await request("/api/instant-production-reports", {
      method: "POST", body: JSON.stringify({ alert_rules: rulesFromForm() }),
    });
    renderReport(record);
    await loadHistory();
    if (autoPush) {
      try {
        const pushed = await request(`/api/instant-production-reports/${record.id}/push`, {
          method: "POST", body: JSON.stringify({ group_id: autoPushGroup, alert_only: true }),
        });
        showNotice(pushed.status === "skipped"
          ? `即時報告 #${record.id} 已保存到 NAS；本次未觸發告警，因此未推送。`
          : `即時報告 #${record.id} 已保存到 NAS，並已推送至 ${pushed.group}。`);
        renderReport(await request(`/api/instant-production-reports/${record.id}`));
        await loadHistory();
      } catch (pushError) {
        showNotice(`即時報告 #${record.id} 已保存到 NAS。`);
        showError(`自動推送失敗：${pushError.message}`);
      }
    } else {
      showNotice(`即時報告 #${record.id} 已保存到 NAS。`);
    }
  } catch (error) { showError(`報告產生失敗：${error.message}`); }
  finally { setBusy(false); }
}

async function loadLineGroups() {
  try {
    const data = await request("/api/line/groups");
    const groups = data.groups || [];
    $("lineGroup").replaceChildren(
      new Option("請選擇已核准 LINE 群組", ""),
      ...groups.map((group) => new Option(group.name || group.id, group.id)),
    );
    $("generationLineGroup").replaceChildren(
      new Option("不自動推送", ""),
      ...groups.map((group) => new Option(group.name || group.id, group.id)),
    );
  } catch (error) {
    $("lineGroup").replaceChildren(new Option(`LINE 群組無法載入：${error.message}`, ""));
    $("generationLineGroup").replaceChildren(new Option(`LINE 群組無法載入：${error.message}`, ""));
  }
}

async function loadGmailAccounts() {
  try {
    const data = await request("/api/gmail-sender-accounts");
    const accounts = data.accounts || [];
    const options = [new Option("請選擇 Gmail 寄件帳號", "")];
    for (const account of accounts) {
      const unavailable = account.status === "reauthorization_required" ? " · 需重新授權 gmail.send" : " · 未設定";
      const option = new Option(`${account.label} · ${account.email}${account.configured ? "" : unavailable}`, account.id);
      option.disabled = !account.configured;
      option.dataset.email = account.email;
      option.title = account.recipient_policy;
      options.push(option);
    }
    if (!accounts.length) options[0].textContent = "尚未設定 Gmail 寄件帳號";
    $("gmailAccount").replaceChildren(...options);
  } catch (error) {
    $("gmailAccount").replaceChildren(new Option(`Gmail 帳號無法載入：${error.message}`, ""));
  }
}

async function pushReport() {
  if (!activeReport) return showError("請先產生或選擇一份即時報告。"), undefined;
  const groupId = $("lineGroup").value;
  if (!groupId) return showError("請選擇已核准的 LINE 群組。"), undefined;
  setBusy(true, "正在推送報告告警…");
  try {
    const result = await request(`/api/instant-production-reports/${activeReport.id}/push`, {
      method: "POST", body: JSON.stringify({ group_id: groupId, alert_only: $("alertOnly").checked }),
    });
    if (result.status === "skipped") showNotice(result.message);
    else showNotice(`報告已推送至 ${result.group}。`);
    await showReport(activeReport.id);
    await loadHistory();
  } catch (error) { showError(`推送失敗：${error.message}`); }
  finally { setBusy(false); }
}

async function emailReport() {
  if (!activeReport) return showError("請先產生或選擇一份即時報告。"), undefined;
  const accountId = $("gmailAccount").value;
  const recipients = $("gmailRecipients").value.trim();
  if (!accountId) return showError("請選擇 Gmail 寄件帳號。"), undefined;
  if (!recipients) return showError("請輸入收件人 Email。"), undefined;
  setBusy(true, "正在透過 Gmail API 寄送報告 PDF…");
  try {
    const result = await request(`/api/instant-production-reports/${activeReport.id}/email`, {
      method: "POST",
      body: JSON.stringify({ account_id: accountId, recipients, alert_only: $("emailAlertOnly").checked }),
    });
    showNotice(result.status === "skipped" ? result.message : `報告已由 ${result.account} 寄送至 ${result.recipients.join("、")}。`);
    await showReport(activeReport.id);
  } catch (error) { showError(`Gmail 寄送失敗：${error.message}`); }
  finally { setBusy(false); }
}

async function askReport() {
  if (!activeReport) return showError("請先產生或選擇一份即時報告。"), undefined;
  const question = $("question").value.trim();
  if (!question) return showError("請輸入管理層問題。"), undefined;
  setBusy(true, "正在依據目前報告快照產生可追溯回答…");
  try {
    const result = await request(`/api/instant-production-reports/${activeReport.id}/ask`, {
      method: "POST", body: JSON.stringify({ question }),
    });
    $("answer").textContent = result.answer;
    $("answer").hidden = false;
    await showReport(activeReport.id);
  } catch (error) { showError(`追問失敗：${error.message}`); }
  finally { setBusy(false); }
}

$("resetRules").addEventListener("click", () => applyRules());
$("generate").addEventListener("click", generate);
$("refresh").addEventListener("click", async () => {
  setBusy(true, "正在重新載入報告歷史…");
  try { await loadHistory(); } catch (error) { showError(error.message); } finally { setBusy(false); }
});
$("push").addEventListener("click", pushReport);
$("email").addEventListener("click", emailReport);
$("gmailAccount").addEventListener("change", (event) => {
  const option = event.target.selectedOptions[0];
  if (option?.dataset.email && !$("gmailRecipients").value.trim()) $("gmailRecipients").value = option.dataset.email;
});
$("ask").addEventListener("click", askReport);
$("sampleQuestion").addEventListener("change", (event) => { if (event.target.value) $("question").value = event.target.value; });

Promise.all([loadHistory(), loadLineGroups(), loadGmailAccounts()]).then(async () => {
  const reportId = Number(new URLSearchParams(location.search).get("report"));
  if (reportId > 0) await showReport(reportId);
}).catch((error) => showError(error.message));
