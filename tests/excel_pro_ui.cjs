const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const http = require('node:http');
const { readFile, mkdir } = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const files = {
  '/excel-pro': ['excel-pro.html', 'text/html'],
  '/static/excel-pro.js': ['excel-pro.js', 'text/javascript'],
  '/static/excel-pro.css': ['excel-pro.css', 'text/css'],
  '/static/icons/icon-192.png': ['icons/icon-192.png', 'image/png'],
};
const sources = [
  {asset_id:41,title:'銷售明細',filename:'sales.xlsx',uploader:'sales',visibility:'group',file_size:18200},
  {asset_id:52,title:'庫存',filename:'inventory.csv',uploader:'warehouse',visibility:'company',file_size:8300},
];
const tables = [
  {...sources[0],sheet_name:'銷售明細',table_name:'asset_41__銷售明細',columns:['產品','數量','銷售額'],row_count:849,range:'銷售明細!A2:C850'},
  {...sources[1],sheet_name:'data',table_name:'asset_52__data',columns:['產品','可用庫存'],row_count:20,range:'data!A2:B21'},
];
let jobs = [];let exportPosts=0;let askPayload=null;
const server = http.createServer(async (req,res) => {
  const url = new URL(req.url,'http://localhost'); const file = files[url.pathname];
  if(file){try{const content=await readFile(path.join(root,'static',file[0]));res.writeHead(200,{'Content-Type':file[1]});res.end(content)}catch{res.writeHead(500);res.end()}return;}
  const send=(body,status=200)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(body))};
  if(url.pathname==='/api/excel-pro/sources'&&req.method==='GET')return send({count:2,sources});
  if(url.pathname==='/api/excel-pro/ask'&&req.method==='POST'){let raw='';for await(const chunk of req)raw+=chunk;askPayload=JSON.parse(raw);return send({answer:'NAS B 的可用庫存低於銷售數量，存在缺貨風險。',model:'Qwen3 4B',selected_sources:sources,generated_sql:'SELECT * FROM "asset_41__銷售明細"',sql_explanation:'聯查銷售與庫存',result:{engine:'DuckDB 1.5.6',columns:['產品','銷售數量','可用庫存'],rows:[['NAS B',20,12]],row_count:1,truncated:false},citations:tables,trace:[{step:1,kind:'llm',label:'理解問題與資料範圍',status:'completed',duration_ms:20},{step:2,kind:'mcp',label:'excel_pro_list_sources',status:'completed',duration_ms:10}],export_created:false})}
  if(url.pathname==='/api/excel-pro/sources/describe')return send({source_count:2,table_count:2,tables});
  if(url.pathname==='/api/excel-pro/query')return send({engine:'DuckDB 1.5.6',columns:['產品','銷售數量','可用庫存'],rows:[['NAS A',40,100],['NAS B',20,12]],row_count:2,truncated:false,citations:tables});
  if(url.pathname==='/api/excel-pro/jobs'&&req.method==='POST'){exportPosts++;jobs=[{id:7,status:'running',progress:55,stage:'running_query',created_at:'2026-10-21 10:00'}];return send(jobs[0])}
  if(url.pathname==='/api/excel-pro/jobs'&&req.method==='GET')return send({jobs});
  res.writeHead(404);res.end();
});
(async()=>{let browser;try{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  browser=await chromium.launch({headless:true,channel:'chrome'});
  const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/excel-pro`);
  await page.waitForFunction(()=>document.querySelectorAll('.source-item').length===2);
  assert.equal(await page.locator('#advancedSql').getAttribute('open'),null);
  assert.match(await page.locator('#scopeSelection').textContent(),/自動選擇/);
  await page.locator('#scopeFiles').click();assert.equal(await page.locator('#sourceDialog').getAttribute('open'),'');
  await page.locator('.dialog-source-item input').nth(0).check();await page.locator('.dialog-source-item input').nth(1).check();
  assert.match(await page.locator('#dialogSelectionCount').textContent(),/2 份/);await page.locator('#confirmSourceSelection').click();
  assert.equal(await page.locator('#sourceDialog').getAttribute('open'),null);assert.match(await page.locator('#scopeSelection').textContent(),/sales.xlsx/);
  await page.locator('#questionSample').selectOption({label:'綜合銷售與庫存，找出可能缺貨的產品並說明原因。'});
  await page.locator('#askExcel').click();await page.waitForFunction(()=>!document.getElementById('agentAnswer').hidden);
  assert.deepEqual(askPayload.selected_asset_ids,[41,52]);
  assert.match(await page.locator('#answerText').textContent(),/NAS B/);assert.match(await page.locator('#agentCitations').textContent(),/銷售明細!A2:C850/);
  assert.match(await page.locator('#agentTrace').textContent(),/excel_pro_list_sources/);assert.equal(exportPosts,0);
  await page.waitForFunction(()=>document.querySelectorAll('.table-definition').length===2);
  assert.match(await page.locator('#tableMap').textContent(),/銷售明細!A2:C850/);
  await page.locator('#advancedSql > summary').click();
  await page.locator('#sqlEditor').fill('SELECT * FROM "asset_41__銷售明細"');await page.locator('#runQuery').click();
  await page.waitForFunction(()=>document.querySelectorAll('#resultBody tr').length===2);
  assert.equal(await page.locator('#resultBody tr').count(),2);assert.match(await page.locator('#citations').textContent(),/上傳者 sales/);
  await page.locator('.export-panel > summary').click();await page.locator('#pivotRows').fill('產品');await page.locator('#pivotValue').fill('銷售數量');await page.locator('#startExport').click();
  await page.waitForFunction(()=>document.querySelectorAll('.job').length===1);assert.match(await page.locator('.job').textContent(),/處理中/);
  await mkdir(path.join(root,'tmp'),{recursive:true});await page.screenshot({path:path.join(root,'tmp/excel-pro-1440.png'),fullPage:true});
  for(const width of [1440,390]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)}
  assert.equal(exportPosts,1);assert.deepEqual(errors,[]);console.log('PASS: natural-language chain, folded SQL, citations, explicit export, progress, responsive layout.');
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve))}})().catch(error=>{console.error(error);process.exitCode=1});
