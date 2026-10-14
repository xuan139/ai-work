const $ = id => document.getElementById(id);
const state = { busy: false, study: null, report: null, steps: [], imageURL: null };
function controls() {
  document.querySelectorAll('button, select, textarea, input').forEach(el => { el.disabled = state.busy; });
  $('ask').disabled = state.busy || state.report?.status !== 'final';
  document.querySelector('main').setAttribute('aria-busy', String(state.busy));
}
async function request(url, payload) {
  const response = await fetch(url, { credentials: 'same-origin', ...(payload ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) } : {}) });
  if (response.status === 401) throw Error('請先返回工作區登入。');
  if (!response.ok) {
    const data = await response.json(); throw Error(typeof data.detail === 'string' ? data.detail : '讀取失敗');
  }
  return response;
}
async function work(message, action) {
  if (state.busy) return;
  state.busy = true; $('busy').textContent = message; $('busy').hidden = false; $('error').hidden = true; controls();
  try { await action(); }
  catch (error) { $('error').textContent = error.message; $('error').hidden = false; }
  finally { state.busy = false; $('busy').hidden = true; controls(); }
}
function trace() { $('traceSection').hidden = !state.steps.length; $('trace').textContent = JSON.stringify(state.steps, null, 2); }
async function tool(name, args = {}) {
  const step = await (await request('/api/radiology-demo/tools/call', { name, arguments: args })).json();
  state.steps.push(step); trace(); return step.result;
}
function clearStudy() {
  state.study = null; state.report = null; state.steps = []; trace();
  $('studyContent').hidden = true; $('studyTitle').textContent = '請選擇檢查'; $('metadata').textContent = '';
  $('answer').textContent = ''; $('sources').replaceChildren(); $('summaryStatus').textContent = '';
  $('xray').removeAttribute('src');
  if (state.imageURL) URL.revokeObjectURL(state.imageURL);
  state.imageURL = null;
}
async function studies() {
  clearStudy(); $('studies').replaceChildren();
  if (!$('patient').value) return;
  const result = await tool('radiology_search_studies', { patient_id: $('patient').value });
  for (const study of result.studies) {
    const button = document.createElement('button'); button.type = 'button'; button.dataset.study = study.id;
    button.textContent = `${study.accession} · ${study.date} · ${study.report_status === 'final' ? '報告已完成' : '報告待完成'}`;
    button.addEventListener('click', () => work('讀取 Orthanc 影像與報告…', () => openStudy(study.id)));
    $('studies').append(button);
  }
  if (!result.studies.length) $('studies').textContent = '沒有檢查資料。';
}
async function openStudy(id) {
  clearStudy();
  const study = (await tool('radiology_get_study', { study_id: id })).study;
  const report = (await tool('radiology_get_report', { study_id: id })).report;
  const viewer = await tool('radiology_open_viewer', { study_id: id });
  const expected = '/api/radiology-demo/studies/' + encodeURIComponent(id) + '/image';
  if (viewer.preview_url !== expected) throw Error('影像來源不符合唯讀範圍。');
  const blob = await (await request(expected)).blob();
  state.imageURL = URL.createObjectURL(blob); $('xray').src = state.imageURL;
  await $('xray').decode();
  state.study = study; state.report = report;
  $('studyTitle').textContent = study.description;
  $('metadata').textContent = `${study.accession} · ${study.patient_id} · ${study.date} · Study UID: ${study.study_uid}`;
  $('reportMeta').textContent = `${report.id} · v${report.version} · ${report.date} · ${report.status === 'final' ? '教學稿已完成' : '待完成'}`;
  $('reportText').textContent = report.text || '尚無報告內容，不會呼叫模型產生推測性摘要。';
  $('credit').replaceChildren(document.createTextNode(`${study.image_source.author} · ${study.image_source.license} · `));
  const link = document.createElement('a'); link.textContent = '原圖與授權';
  link.href = 'https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg';
  link.target = '_blank'; link.rel = 'noopener noreferrer'; $('credit').append(link);
  $('zoom').value = '100'; $('contrast').value = '100'; adjustImage();
  $('studyContent').hidden = false;
  document.querySelectorAll('[data-study]').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.study === id)));
  history.replaceState(null, '', '/radiology-demo?study=' + encodeURIComponent(id));
}
async function load() {
  await work('透過 MCP 讀取教學病患…', async () => {
    clearStudy(); $('studies').replaceChildren(); $('patient').replaceChildren(new Option('請選擇病患', ''));
    const result = await tool('radiology_search_patients');
    result.patients.forEach(p => $('patient').append(new Option(`${p.name} · ${p.id}`, p.id)));
    const selected = new URLSearchParams(location.search).get('study');
    if (/^demo-xr00[1-3]$/.test(selected || '')) {
      $('patient').value = 'demo-p' + selected.slice(-3); await studies(); await openStudy(selected);
    }
  });
}
$('patient').addEventListener('change', () => work('查詢 Orthanc 檢查清單…', studies));
$('refresh').addEventListener('click', load);
$('example').addEventListener('change', () => { $('prompt').value = $('example').value; });
function adjustImage() { $('xray').style.width = $('zoom').value + '%'; $('xray').style.filter = `contrast(${$('contrast').value}%)`; }
$('zoom').addEventListener('input', adjustImage); $('contrast').addEventListener('input', adjustImage);
$('summaryForm').addEventListener('submit', event => {
  event.preventDefault(); if (!state.study || state.report?.status !== 'final') return;
  work('MCP 重新取得來源，LLM 正在摘要報告…', async () => {
    $('answer').textContent = ''; $('sources').replaceChildren(); $('summaryStatus').textContent = '';
    const data = await (await request('/api/radiology-demo/summary', { study_id: state.study.id, prompt: $('prompt').value })).json();
    $('answer').textContent = data.answer; state.steps.push(...data.steps); trace();
    $('summaryStatus').textContent = data.citation_warning ? '注意：模型未附必要引用，以下僅列出本次使用來源；請核對答案。' : `模型：${data.model} · 呼叫記錄：${data.call_id}`;
    for (const source of data.sources) {
      const item = document.createElement('li'); const link = document.createElement('a');
      const expected = '/radiology-demo?study=' + encodeURIComponent(state.study.id);
      link.href = source.url === expected + '#report' ? expected + '#report' : expected;
      link.textContent = `[${source.id}] ${source.title}${source.version ? ' · v' + source.version : ''}`;
      item.append(link); $('sources').append(item);
    }
  });
});
load();
