const state={sources:[],tables:[],selected:new Set(),agentMode:"auto",poll:null};
const $=id=>document.getElementById(id);
const esc=value=>String(value??"");

async function api(url,options={}){
  const response=await fetch(url,{credentials:"same-origin",headers:{"Content-Type":"application/json",...(options.headers||{})},...options});
  if(response.status===401){location.href="/";throw new Error("請重新登入");}
  let body={};try{body=await response.json();}catch{}
  if(!response.ok)throw new Error(body.detail||`HTTP ${response.status}`);
  return body;
}

function loading(button,busy,label){if(!button)return;button.disabled=busy;if(!button.dataset.label)button.dataset.label=button.textContent;button.textContent=busy?label:button.dataset.label;}
function selectedSources(){return [...state.selected].map(asset_id=>({asset_id}));}

async function loadSources(){
  loading($("reloadSources"),true,"…");
  try{const q=$("sourceSearch").value.trim();const data=await api(`/api/excel-pro/sources?q=${encodeURIComponent(q)}&limit=100`);state.sources=data.sources||[];renderSources();renderDialogSources();updateAgentScope();}
  catch(error){$("sourceList").innerHTML="";const p=document.createElement("p");p.className="error";p.textContent=error.message;$("sourceList").append(p);}
  finally{loading($("reloadSources"),false,"");}
}

async function askExcel(){
  const prompt=$("agentPrompt").value.trim();
  if(!prompt)return setStatus("agentStatus","請先輸入問題",true);
  if(state.agentMode==="files"&&!state.selected.size)return setStatus("agentStatus","請先選擇至少一份要詢問的檔案",true);
  loading($("askExcel"),true,"分析中…");$("agentAnswer").hidden=true;
  setStatus("agentStatus","LLM 正在理解問題，接著將透過 MCP 與 DuckDB 查詢…");
  try{
    const selected_asset_ids=state.agentMode==="files"?[...state.selected]:[];
    const data=await api("/api/excel-pro/ask",{method:"POST",body:JSON.stringify({prompt,selected_asset_ids})});
    renderAgentAnswer(data);if(data.model)$("agentModel").textContent=data.model;
    setStatus("agentStatus",`${data.result?.engine||"DuckDB"} · 已完成 · 未建立匯出檔`);
  }catch(error){setStatus("agentStatus",error.message,true)}
  finally{loading($("askExcel"),false,"")}
}

function renderAgentAnswer(data){
  $("agentAnswer").hidden=false;$("answerText").textContent=data.answer||"沒有可顯示的答案。";
  $("agentSql").textContent=data.generated_sql||"";$("agentSqlNote").textContent=data.sql_explanation||"";
  const sources=$("agentSources");sources.innerHTML="";(data.selected_sources||[]).forEach(item=>{const span=document.createElement("span");span.textContent=item.filename||item.title||`Asset ${item.asset_id}`;sources.append(span)});
  const citations=$("agentCitations");citations.innerHTML="";(data.citations||[]).forEach(item=>{const div=document.createElement("div");div.className="citation";div.textContent=`${item.filename} · ${item.range} · 上傳者 ${item.uploader||"未知"}`;citations.append(div)});
  const trace=$("agentTrace");trace.innerHTML="";(data.trace||[]).forEach(item=>{const li=document.createElement("li");const strong=document.createElement("strong");strong.textContent=`${item.step}. ${item.label}`;const meta=document.createElement("span");meta.textContent=`${item.kind.toUpperCase()} · ${item.status} · ${item.duration_ms} ms`;li.append(strong,meta);trace.append(li)});
  if(data.result?.columns)renderResult({...data.result,citations:data.citations||[]});
  $("agentAnswer").scrollIntoView({behavior:"smooth",block:"nearest"});
}

function renderSources(){
  const root=$("sourceList");root.innerHTML="";
  if(!state.sources.length){const p=document.createElement("p");p.className="empty";p.textContent="沒有可讀取的試算表。請先從 NAS 上傳 XLSX、CSV 或 TSV。";root.append(p);return;}
  state.sources.forEach(source=>{
    const label=document.createElement("label");label.className="source-item";
    const input=document.createElement("input");input.type="checkbox";input.checked=state.selected.has(source.asset_id);input.addEventListener("change",()=>{if(!setSourceSelected(source.asset_id,input.checked)){input.checked=false;return}setAgentMode("files");describe();renderDialogSources();});
    const info=document.createElement("span");const strong=document.createElement("strong");strong.textContent=source.filename;const meta=document.createElement("small");meta.textContent=`${source.uploader||"未知"} · ${source.visibility} · ${formatBytes(source.file_size)}`;info.append(strong,meta);label.append(input,info);root.append(label);
  });
}

function updateAgentScope(){
  const root=$("scopeSelection");root.innerHTML="";
  if(state.agentMode==="auto"){
    const span=document.createElement("span");span.textContent="目前：自動選擇相關檔案";root.append(span);
    setStatus("agentStatus","系統會從您可讀取的資料中自動選擇相關檔案。");return;
  }
  if(!state.selected.size){const span=document.createElement("span");span.className="scope-empty";span.textContent="尚未選擇檔案";root.append(span);setStatus("agentStatus","請點擊「選擇檔案」指定查詢範圍。");return}
  state.sources.filter(item=>state.selected.has(item.asset_id)).forEach(item=>{const span=document.createElement("span");span.className="scope-chip";span.textContent=item.filename;root.append(span)});
  setStatus("agentStatus",`本次問答限定使用已選取的 ${state.selected.size} 份資料。`);
}

function setSourceSelected(assetId,checked){
  if(checked&&state.selected.size>=6&&!state.selected.has(assetId)){setStatus("agentStatus","最多可選擇 6 份檔案",true);return false}
  checked?state.selected.add(assetId):state.selected.delete(assetId);return true;
}

function setAgentMode(mode){
  state.agentMode=mode;const files=mode==="files";
  $("scopeAuto").classList.toggle("active",!files);$("scopeAuto").setAttribute("aria-checked",String(!files));
  $("scopeFiles").classList.toggle("active",files);$("scopeFiles").setAttribute("aria-checked",String(files));
  $("openSourceDialog").hidden=!files;updateAgentScope();
  if(files&&!state.selected.size)openSourceDialog();
}

function renderDialogSources(){
  const root=$("dialogSourceList");if(!root)return;root.innerHTML="";
  const query=$("dialogSourceSearch").value.trim().toLowerCase();
  const visible=state.sources.filter(item=>!query||`${item.filename} ${item.title||""} ${item.uploader||""}`.toLowerCase().includes(query));
  if(!visible.length){const p=document.createElement("p");p.className="empty";p.textContent="沒有符合條件的可讀取檔案。";root.append(p)}
  visible.forEach(source=>{const label=document.createElement("label");label.className="dialog-source-item";const input=document.createElement("input");input.type="checkbox";input.checked=state.selected.has(source.asset_id);input.addEventListener("change",()=>{if(!setSourceSelected(source.asset_id,input.checked)){input.checked=false;return}renderSources();updateDialogCount();updateAgentScope()});const info=document.createElement("span");const strong=document.createElement("strong");strong.textContent=source.filename;const small=document.createElement("small");small.textContent=`${source.uploader||"未知"} · ${source.visibility} · ${formatBytes(source.file_size)}`;info.append(strong,small);label.append(input,info);root.append(label)});
  updateDialogCount();
}

function updateDialogCount(){$("dialogSelectionCount").textContent=`已選 ${state.selected.size} 份`}
function openSourceDialog(){renderDialogSources();$("sourceDialog").showModal()}
function closeSourceDialog(){$("sourceDialog").close();describe();renderSources();updateAgentScope()}

async function describe(){
  if(!state.selected.size){state.tables=[];renderTables();return;}
  try{const data=await api("/api/excel-pro/sources/describe",{method:"POST",body:JSON.stringify({sources:selectedSources()})});state.tables=data.tables||[];renderTables();if(!$("sqlEditor").value.trim()&&state.tables[0])$("sqlEditor").value=`SELECT *\nFROM "${state.tables[0].table_name}"\nLIMIT 100`;}
  catch(error){state.tables=[];renderTables(error.message);}
}

function renderTables(error=""){
  const root=$("tableMap");root.innerHTML="";
  if(error||!state.tables.length){const p=document.createElement("p");p.className=error?"error":"empty";p.textContent=error||"選擇檔案後顯示工作表、欄位、資料範圍與 SQL 表名。";root.append(p);return;}
  state.tables.forEach(table=>{const div=document.createElement("div");div.className="table-definition";const code=document.createElement("code");code.textContent=`"${table.table_name}"`;const meta=document.createElement("small");meta.textContent=`${table.filename} · ${table.range} · ${table.row_count} 筆`;const cols=document.createElement("small");cols.textContent=`欄位：${(table.columns||[]).join(", ")}`;div.append(code,meta,cols);root.append(div);});
}

async function runQuery(){
  if(!state.selected.size)return setStatus("queryStatus","請先選擇資料來源",true);
  loading($("runQuery"),true,"查詢中…");setStatus("queryStatus","DuckDB 正在載入並執行唯讀 SQL");
  try{const data=await api("/api/excel-pro/query",{method:"POST",body:JSON.stringify({sources:selectedSources(),sql:$("sqlEditor").value,max_rows:200})});renderResult(data);setStatus("queryStatus",`${data.engine} · 完成`);}
  catch(error){setStatus("queryStatus",error.message,true);}
  finally{loading($("runQuery"),false,"");}
}

function renderResult(data){
  $("resultPanel").hidden=false;$("engineBadge").textContent=data.engine;$("resultCount").textContent=`${data.row_count} 筆${data.truncated?"（已截斷）":""}`;
  const head=$("resultHead"),body=$("resultBody");head.innerHTML="";body.innerHTML="";const tr=document.createElement("tr");(data.columns||[]).forEach(value=>{const th=document.createElement("th");th.textContent=esc(value);tr.append(th)});head.append(tr);
  (data.rows||[]).forEach(row=>{const line=document.createElement("tr");row.forEach(value=>{const td=document.createElement("td");td.textContent=esc(value);line.append(td)});body.append(line)});
  const citations=$("citations");citations.innerHTML="";(data.citations||[]).forEach(item=>{const div=document.createElement("div");div.className="citation";div.textContent=`${item.filename} · ${item.range} · 上傳者 ${item.uploader||"未知"}`;citations.append(div)});
}

function exportPayload(){
  const pivotRows=split($("pivotRows").value),pivotValue=$("pivotValue").value.trim(),chartType=$("chartType").value;
  const payload={sources:selectedSources(),sql:$("sqlEditor").value,output_name:$("outputName").value};
  if(pivotRows.length&&pivotValue)payload.pivot={rows:pivotRows,values:[{column:pivotValue,aggregate:$("pivotAggregate").value}]};
  if(chartType)payload.chart={type:chartType,sheet:$("chartSheet").value,category_column:$("chartCategory").value.trim(),value_columns:split($("chartValues").value),title:"NAS Excel Pro 分析"};
  return payload;
}

async function startExport(){
  if(!state.selected.size)return setStatus("exportStatus","請先選擇資料來源",true);
  loading($("startExport"),true,"加入佇列中…");
  try{const job=await api("/api/excel-pro/jobs",{method:"POST",body:JSON.stringify(exportPayload())});setStatus("exportStatus",`工作 #${job.id} 已建立，原始檔不會被修改。`);await loadJobs();startPolling();}
  catch(error){setStatus("exportStatus",error.message,true);}
  finally{loading($("startExport"),false,"");}
}

async function loadJobs(){
  try{const data=await api("/api/excel-pro/jobs?limit=30");renderJobs(data.jobs||[]);if((data.jobs||[]).some(job=>["queued","running"].includes(job.status)))startPolling();else stopPolling();}
  catch(error){$("jobList").textContent=error.message;}
}

function renderJobs(jobs){
  const root=$("jobList");root.innerHTML="";if(!jobs.length){const p=document.createElement("p");p.className="empty";p.textContent="尚無匯出工作。";root.append(p);return;}
  jobs.forEach(job=>{const item=document.createElement("article");item.className="job";const info=document.createElement("div");const title=document.createElement("strong");title.textContent=`工作 #${job.id} · ${statusLabel(job.status)}`;const meta=document.createElement("small");meta.textContent=`${job.stage||"queued"} · ${job.created_at||""}`;info.append(title,meta);if(job.error_message){const err=document.createElement("small");err.className="error";err.textContent=job.error_message;info.append(err)}const progress=document.createElement("div");progress.className="progress";const bar=document.createElement("span");bar.style.width=`${job.progress}%`;progress.append(bar);const actions=document.createElement("div");actions.className="job-actions";if(job.download_url){const link=document.createElement("a");link.href=job.download_url;link.textContent="下載 XLSX";actions.append(link)}if(["queued","running"].includes(job.status)){const cancel=document.createElement("button");cancel.className="secondary";cancel.textContent="取消";cancel.addEventListener("click",()=>cancelJob(job.id));actions.append(cancel)}item.append(info,progress,actions);root.append(item)});
}

async function cancelJob(id){try{await api(`/api/excel-pro/jobs/${id}/cancel`,{method:"POST",body:"{}"});await loadJobs()}catch(error){setStatus("exportStatus",error.message,true)}}
function startPolling(){if(!state.poll)state.poll=setInterval(loadJobs,2000)}function stopPolling(){if(state.poll){clearInterval(state.poll);state.poll=null}}
function setStatus(id,text,error=false){const el=$(id);el.textContent=text;el.classList.toggle("error",error)}
function split(value){return value.split(",").map(item=>item.trim()).filter(Boolean)}
function formatBytes(value){const n=Number(value||0);if(n<1024)return `${n} B`;if(n<1048576)return `${(n/1024).toFixed(1)} KB`;return `${(n/1048576).toFixed(1)} MB`}
function statusLabel(value){return({queued:"等待中",running:"處理中",completed:"已完成",failed:"失敗",cancelled:"已取消"})[value]||value}

$("reloadSources").addEventListener("click",loadSources);$("sourceSearch").addEventListener("input",()=>{clearTimeout(state.searchTimer);state.searchTimer=setTimeout(loadSources,300)});$("scopeAuto").addEventListener("click",()=>setAgentMode("auto"));$("scopeFiles").addEventListener("click",()=>setAgentMode("files"));$("openSourceDialog").addEventListener("click",openSourceDialog);$("closeSourceDialog").addEventListener("click",closeSourceDialog);$("confirmSourceSelection").addEventListener("click",closeSourceDialog);$("clearSourceSelection").addEventListener("click",()=>{state.selected.clear();renderDialogSources();renderSources();updateAgentScope()});$("dialogSourceSearch").addEventListener("input",renderDialogSources);$("questionSample").addEventListener("change",event=>{if(event.target.value)$("agentPrompt").value=event.target.value});$("askExcel").addEventListener("click",askExcel);$("agentPrompt").addEventListener("keydown",event=>{if((event.metaKey||event.ctrlKey)&&event.key==="Enter")askExcel()});$("runQuery").addEventListener("click",runQuery);$("startExport").addEventListener("click",startExport);$("reloadJobs").addEventListener("click",loadJobs);window.addEventListener("beforeunload",stopPolling);loadSources();loadJobs();
