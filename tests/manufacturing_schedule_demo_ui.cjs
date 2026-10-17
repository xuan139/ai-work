const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const http = require('node:http');
const { readFile, mkdir } = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const files = {
  '/manufacturing-schedule-demo': ['manufacturing-schedule-demo.html', 'text/html'],
  '/static/manufacturing-schedule-demo.js': ['manufacturing-schedule-demo.js', 'text/javascript'],
  '/static/manufacturing-schedule-demo.css': ['manufacturing-schedule-demo.css', 'text/css'],
  '/static/icons/icon-192.png': ['icons/icon-192.png', 'image/png'],
};
const baseOrder = (id, family, index) => ({ order: id, product: `Product ${family}`, family, quantity: 100,
  customer: index < 3 ? 'Goldsys Customer' : 'MES 教學客戶', source_kind: index < 3 ? 'odoo_mcp' : 'mes_mcp_demo',
  priority: index === 2 ? 'normal' : 'high', due_at: `2026-10-2${index}T16:00`, material: index === 2 ? 'MCU-C 缺 120 件' : '齊套',
  material_ready_at: '2026-10-19T08:00', predicted_completion_at: `2026-10-2${index}T15:00`, late_minutes: index === 2 ? 60 : 0,
  risk_probability: index === 2 ? 80 : 12, risk_level: index === 2 ? 'high' : 'low', reasons: [index === 2 ? '缺料' : '可滿足交期'] });
function fixture(orderCount = 5) {
  const orders = Array.from({ length: orderCount }, (_, i) => baseOrder(`SO-${1001 + i}`, ['A','B','C'][i % 3], Math.min(i + 1, 4)));
  const centers = [{id:'SMT-01',name:'SMT',shift:'08:00–17:00',units_per_hour:70,setup_minutes:30},{id:'ASSY-01',name:'組裝',shift:'08:00–17:00',units_per_hour:45,setup_minutes:20},{id:'TEST-01',name:'測試',shift:'08:00–17:00',units_per_hour:55,setup_minutes:15}];
  const operations = orders.flatMap((order, oi) => centers.map((center, ci) => ({order:order.order,product:order.product,family:order.family,center_id:center.id,center:center.name,
    start_at:`2026-10-${19 + oi}T${String(8 + ci).padStart(2,'0')}:00`,end_at:`2026-10-${19 + oi}T${String(10 + ci).padStart(2,'0')}:00`,setup_minutes:ci ? 15 : 0,duration_minutes:120})));
  return {demo:true,read_only:true,data_mode:'live_mcp',snapshot_at:'2026-10-19T08:00',scenario:{},engine:{name:'確定性有限產能規則排程',note:'Demo'},
    work_centers:centers,downtimes:[{center_id:'TEST-01',start:'2026-10-20T13:00',end:'2026-10-20T14:30',reason:'預防保養'}],
    mes_snapshot:{plant:'ELECTRONICS-DEMO-01',dataset_type:'synthetic_electronics_schedule',notice:'教學模擬資料；由 MES MCP 提供。'},
    qms_snapshot:{notice:'QMS 教學模擬資料。',profiles:[{family:'A',first_pass_yield_pct:98.2,top_defect:'少錫',expected_rework_minutes_per_100:18,quality_level:'stable'},{family:'B',first_pass_yield_pct:95.8,top_defect:'連接器偏位',expected_rework_minutes_per_100:42,quality_level:'watch'},{family:'C',first_pass_yield_pct:91.2,top_defect:'BGA 焊點異常',expected_rework_minutes_per_100:95,quality_level:'alert'}]},
    cmms_snapshot:{notice:'CMMS 教學模擬資料。',assets:[{center_id:'SMT-01',health:'watch',open_work_order:'MWO-2026-018',reason:'吸嘴真空值趨勢偏低'},{center_id:'ASSY-01',health:'normal',open_work_order:null,reason:'無未結維護工單'},{center_id:'TEST-01',health:'planned',open_work_order:'MWO-2026-021',reason:'週期校驗'}]},
    integration_warnings:['教學模擬資料；由 MES MCP 提供。','QMS 教學模擬資料。','CMMS 教學模擬資料。','Odoo MCP 提供 3 筆訂單；另由 MES MCP 補入 2 筆教學訂單。'],
    inventory:[{item:'MCU-C',on_hand:40,required:160,status:'短缺 120',source_id:'stock.quant/MCU-C'}],orders,operations,
    summary:{order_count:orderCount,late_count:1,on_time_count:orderCount-1,high_risk_count:1,setup_count:6,latest_completion_at:'2026-10-24T15:00'},
    sources:[{id:'odoo',name:'Goldsys Odoo / search_read',detail:'3 筆訂單'},{id:'stock',name:'Goldsys Odoo / search_read',detail:'stock.quant'},
      {id:'mes',name:'FactorySemantics MES / mes_electronics_schedule_snapshot',detail:'3 個模擬工作中心'},
      {id:'qms',name:'Electronics QMS Demo / qms_quality_snapshot',detail:'3 個產品家族'},
      {id:'cmms',name:'Electronics CMMS Demo / cmms_maintenance_snapshot',detail:'3 台設備'},
      {id:'scheduler',name:'本地排程引擎',detail:'finite-capacity-mcp-v3'}],
    trace:[{kind:'mcp',tool:'search_read',arguments:{model:'sale.order'},result:`${orderCount} orders`},{kind:'mcp',tool:'mes_electronics_schedule_snapshot',arguments:{},result:'snapshot'},{kind:'mcp',tool:'qms_quality_snapshot',arguments:{},result:'snapshot'},{kind:'mcp',tool:'cmms_maintenance_snapshot',arguments:{},result:'snapshot'},{kind:'local',tool:'schedule.run_finite_capacity',arguments:{},result:`${operations.length} operations`}],};
}
const server = http.createServer(async (req, res) => {
  const file = files[new URL(req.url, 'http://localhost').pathname];
  if (!file) { res.writeHead(404); res.end(); return; }
  try { const content = await readFile(path.join(root, 'static', file[0])); res.writeHead(200, {'Content-Type':file[1]}); res.end(content); }
  catch { res.writeHead(500); res.end(); }
});
(async () => {
  let browser;
  try {
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    browser = await chromium.launch({headless:true,channel:'chrome'});
    const page = await browser.newPage({viewport:{width:1440,height:1100}}); const errors=[]; const scheduleCalls=[]; const askCalls=[];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/api/manufacturing-schedule-demo/schedule', async route => { scheduleCalls.push(route.request().postDataJSON()); await route.fulfill({json:fixture(scheduleCalls.at(-1).scenario.rush_order ? 6 : 5)}); });
    await page.route('**/api/manufacturing-schedule-demo/ask', async route => { askCalls.push(route.request().postDataJSON()); const data=fixture(6); await route.fulfill({json:{answer:'SO-1003 因 MCU-C 缺料而延期。',model:'Qwen3 4B',schedule:data,sources:data.sources,steps:[...data.trace,{tool:'llm.explain_schedule'}]}}); });
    await page.goto(`http://127.0.0.1:${server.address().port}/manufacturing-schedule-demo`);
    await page.waitForFunction(() => document.querySelectorAll('#ordersBody tr').length === 5);
    assert.equal(scheduleCalls.length,1); assert.equal(await page.locator('.gantt-row').count(),3); assert.equal(await page.locator('.gantt-bar').count(),15); assert.equal(await page.locator('.source').count(),6);
    assert.equal(await page.locator('#integrationWarnings').isVisible(),true); assert.match(await page.locator('#mesStatus').textContent(),/ELECTRONICS-DEMO-01/);
    assert.match(await page.locator('#quality').textContent(),/BGA/); assert.match(await page.locator('#maintenance').textContent(),/MWO-2026-018/);
    assert.match(await page.locator('.badge').textContent(),/MCP/); assert.match(await page.locator('#trace').textContent(),/qms_quality_snapshot/); assert.match(await page.locator('#trace').textContent(),/cmms_maintenance_snapshot/);
    await page.locator('#rushOrder').check(); await page.locator('#downtimeHours').selectOption('2'); await page.locator('#materialDelay').selectOption('2');
    assert.match(await page.locator('#scenarioState').textContent(), /變更/); assert.equal(scheduleCalls.length,1);
    await page.locator('#runSchedule').click(); await page.waitForFunction(() => document.querySelectorAll('#ordersBody tr').length === 6);
    assert.deepEqual(scheduleCalls.at(-1).scenario,{rush_order:true,smt_downtime_hours:2,material_delay_days:2});
    await page.locator('#sampleQuestion').selectOption('1'); assert.match(await page.locator('#prompt').inputValue(),/S00003/); assert.equal(askCalls.length,0);
    await page.locator('#sampleQuestion').selectOption('2'); assert.equal(await page.locator('#downtimeHours').inputValue(),'2'); assert.equal(askCalls.length,0);
    await page.locator('#sampleQuestion').selectOption('1');
    await page.locator('#ask').click(); await page.waitForFunction(() => !document.getElementById('answerPanel').hidden);
    assert.equal(askCalls.length,1); assert.match(await page.locator('#answer').textContent(),/MCU-C/); assert.match(await page.locator('#trace').textContent(),/llm.explain_schedule/);
    await mkdir(path.join(root,'tmp'),{recursive:true});
    for (const width of [1440,390]) { await page.setViewportSize({width,height:1100}); assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),true); await page.screenshot({path:path.join(root,`tmp/manufacturing-schedule-${width}.png`),fullPage:true}); }
    assert.deepEqual(errors,[]); console.log('PASS: baseline, three what-if controls, Gantt, LLM samples, sources/trace, desktop/mobile layout.');
  } finally { if (browser) await browser.close(); await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); process.exitCode=1; });
