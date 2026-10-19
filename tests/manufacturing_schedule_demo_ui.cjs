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
    wms_snapshot:{notice:'WMS 教學模擬資料。',material_profiles:[{family:'A',item:'PCB-A',available_units:520,location:'WH-A-01',lot_ids:['LOT-PCB-A-2609'],ready_at:'2026-10-19T08:00',status:'available'},{family:'B',item:'MCU-B',available_units:210,location:'WH-B-03',lot_ids:['LOT-MCU-B-2610'],ready_at:'2026-10-19T08:00',status:'available'},{family:'C',item:'MCU-C',available_units:40,location:'WH-C-02',lot_ids:['LOT-MCU-C-2610'],ready_at:'2026-10-21T08:00',status:'inbound'}],serial_genealogy:[{serial:'SN-DEMO-C-0001',order:'MES-DEMO-1003',consumed_lots:['LOT-MCU-C-2610']}]},
    plm_snapshot:{notice:'PLM 教學模擬資料。',revisions:[{family:'A',bom:'BOM-A-004',revision:'A.04',status:'released',extra_setup_minutes:0,extra_operation_minutes:0},{family:'B',bom:'BOM-B-007',revision:'B.07',status:'released',extra_setup_minutes:5,extra_operation_minutes:0},{family:'C',bom:'BOM-C-012',revision:'C.12',status:'controlled_release',extra_setup_minutes:10,extra_operation_minutes:20}],open_ecos:[{eco_id:'ECO-2026-014',status:'verification',risk:'high',summary:'BGA 焊墊設計調整'}]},
    spc_snapshot:{notice:'SPC 教學模擬資料。',profiles:[{family:'A',center_id:'SMT-01',metric:'paste',cp:1.82,cpk:1.67,status:'stable',extra_inspection_minutes_per_100:0},{family:'B',center_id:'ASSY-01',metric:'alignment',cp:1.36,cpk:1.21,status:'watch',extra_inspection_minutes_per_100:12},{family:'C',center_id:'TEST-01',metric:'resistance',cp:1.08,cpk:.91,status:'alert',extra_inspection_minutes_per_100:35}],out_of_control_points:[{point_id:'SPC-OOC-027',center_id:'TEST-01',rule:'Rule 2',observed_at:'2026-10-18T14:20'}]},
    integration_warnings:['教學模擬資料；由 MES MCP 提供。','QMS 教學模擬資料。','CMMS 教學模擬資料。','WMS 教學模擬資料。','PLM 教學模擬資料。','SPC 教學模擬資料。','Odoo MCP 提供 3 筆訂單；另由 MES MCP 補入 2 筆教學訂單。'],
    inventory:[{item:'MCU-C',on_hand:40,required:160,status:'短缺 120',source_id:'stock.quant/MCU-C'}],orders,operations,
    summary:{order_count:orderCount,late_count:1,on_time_count:orderCount-1,high_risk_count:1,setup_count:6,latest_completion_at:'2026-10-24T15:00'},
    sources:[{id:'odoo',name:'Goldsys Odoo / search_read',detail:'3 筆訂單'},{id:'stock',name:'Goldsys Odoo / search_read',detail:'stock.quant'},
      {id:'mes',name:'FactorySemantics MES / mes_electronics_schedule_snapshot',detail:'3 個模擬工作中心'},
      {id:'qms',name:'Electronics QMS Demo / qms_quality_snapshot',detail:'3 個產品家族'},
      {id:'cmms',name:'Electronics CMMS Demo / cmms_maintenance_snapshot',detail:'3 台設備'},
      {id:'wms',name:'Electronics WMS Demo / wms_inventory_snapshot',detail:'3 個家族'},
      {id:'plm',name:'Electronics PLM Demo / plm_engineering_snapshot',detail:'3 個 BOM'},
      {id:'spc',name:'Electronics SPC Demo / spc_process_snapshot',detail:'3 個製程剖面'},
      {id:'scheduler',name:'本地排程引擎',detail:'finite-capacity-mcp-v4'}],
    trace:[{kind:'mcp',tool:'search_read',arguments:{model:'sale.order'},result:`${orderCount} orders`},{kind:'mcp',tool:'mes_electronics_schedule_snapshot',arguments:{},result:'snapshot'},{kind:'mcp',tool:'qms_quality_snapshot',arguments:{},result:'snapshot'},{kind:'mcp',tool:'cmms_maintenance_snapshot',arguments:{},result:'snapshot'},{kind:'mcp',tool:'wms_inventory_snapshot',arguments:{},result:'snapshot'},{kind:'mcp',tool:'plm_engineering_snapshot',arguments:{},result:'snapshot'},{kind:'mcp',tool:'spc_process_snapshot',arguments:{},result:'snapshot'},{kind:'local',tool:'schedule.run_finite_capacity',arguments:{},result:`${operations.length} operations`}],};
}
function comparedFixture(orderCount = 5) {
  const rule = fixture(orderCount); const optimized = structuredClone(rule);
  rule.optimization_metrics={late_minutes:60,weighted_late_minutes:240,changeover_minutes:180,setup_minutes:180,makespan_minutes:7200};
  optimized.engine={name:'Google OR-Tools CP-SAT',version:'ortools-cp-sat-v1',solver_status:'OPTIMAL',solve_time_ms:42};
  optimized.optimization_metrics={late_minutes:0,weighted_late_minutes:0,changeover_minutes:120,setup_minutes:120,makespan_minutes:6900};
  optimized.trace=[...optimized.trace.slice(0,-1),{kind:'local',tool:'schedule.solve_cp_sat',arguments:{},result:`${optimized.operations.length} operations`}];
  const result=structuredClone(rule);
  result.engine_comparison={default_engine:'finite-capacity-mcp-v4',active_engine:'finite-capacity-mcp-v4',fallback_used:false,ortools_available:true,ortools_error:null,
    rule,ortools:optimized,metrics:{rule:rule.optimization_metrics,ortools:optimized.optimization_metrics},delay_improved:true,changeover_improved:true,validated_better:true,
    delta:{weighted_late_minutes_reduced:240,changeover_minutes_reduced:60,makespan_minutes_reduced:300},verdict:'ortools_validated_better'};
  result.engine_setting={current:{id:'finite-capacity-mcp-v4',name:'確定性有限產能規則排程'},can_manage:true,options:[
    {id:'finite-capacity-mcp-v4',name:'確定性有限產能規則排程'},{id:'ortools-cp-sat-v1',name:'Google OR-Tools CP-SAT'}]};
  return result;
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
    await page.route('**/api/manufacturing-schedule-demo/schedule', async route => { scheduleCalls.push(route.request().postDataJSON()); await route.fulfill({json:comparedFixture(scheduleCalls.at(-1).scenario.rush_order ? 6 : 5)}); });
    await page.route('**/api/admin/manufacturing-schedule-engine', async route => route.fulfill({json:{id:route.request().postDataJSON().engine_id,name:'Google OR-Tools CP-SAT'}}));
    await page.route('**/api/manufacturing-schedule-demo/ask', async route => {
      const request = route.request().postDataJSON(); askCalls.push(request);
      if (request.prompt === 'FAIL') { await route.fulfill({status:502,json:{detail:'Prompt has too many tokens'}}); return; }
      const data=comparedFixture(6); await new Promise(resolve => setTimeout(resolve, 50));
      await route.fulfill({json:{answer:'SO-1003 因 MCU-C 缺料而延期。',model:'Qwen3 4B',schedule:data,sources:data.sources,steps:[...data.trace,{tool:'llm.explain_schedule'}]}});
    });
    await page.goto(`http://127.0.0.1:${server.address().port}/manufacturing-schedule-demo`);
    await page.waitForFunction(() => document.querySelectorAll('#ordersBody tr').length === 5);
    assert.equal(await page.locator('#sampleQuestion option').count(),19);
    assert.match(await page.locator('#sampleQuestion option').nth(10).textContent(),/有限產能排程引擎/);
    assert.equal(scheduleCalls.length,1); assert.equal(await page.locator('#gantt .gantt-row').count(),3); assert.equal(await page.locator('#gantt .gantt-bar').count(),15); assert.equal(await page.locator('.source').count(),9);
    assert.equal(await page.locator('#engineComparison').isVisible(),true); assert.match(await page.locator('#comparisonVerdict').textContent(),/比較通過/);
    assert.equal(await page.locator('#ruleGantt .gantt-row').count(),3); assert.equal(await page.locator('#ortoolsGantt .gantt-row').count(),3);
    assert.equal(await page.locator('#defaultEngine option').count(),2); assert.equal(await page.locator('#defaultEngine option').nth(1).isDisabled(),false);
    assert.equal(await page.locator('#integrationWarnings').isVisible(),true); assert.match(await page.locator('#mesStatus').textContent(),/ELECTRONICS-DEMO-01/);
    assert.match(await page.locator('#quality').textContent(),/BGA/); assert.match(await page.locator('#maintenance').textContent(),/MWO-2026-018/);
    assert.match(await page.locator('#wms').textContent(),/LOT-MCU-C-2610/); assert.match(await page.locator('#plm').textContent(),/ECO-2026-014/); assert.match(await page.locator('#spc').textContent(),/Cpk 0.91/);
    assert.match(await page.locator('.badge').textContent(),/MCP/); assert.match(await page.locator('#trace').textContent(),/qms_quality_snapshot/); assert.match(await page.locator('#trace').textContent(),/cmms_maintenance_snapshot/);
    assert.match(await page.locator('#trace').textContent(),/wms_inventory_snapshot/); assert.match(await page.locator('#trace').textContent(),/plm_engineering_snapshot/); assert.match(await page.locator('#trace').textContent(),/spc_process_snapshot/);
    await page.locator('#rushOrder').check(); await page.locator('#downtimeHours').selectOption('2'); await page.locator('#materialDelay').selectOption('2');
    assert.match(await page.locator('#scenarioState').textContent(), /變更/); assert.equal(scheduleCalls.length,1);
    await page.locator('#runSchedule').click(); await page.waitForFunction(() => document.querySelectorAll('#ordersBody tr').length === 6);
    assert.deepEqual(scheduleCalls.at(-1).scenario,{rush_order:true,smt_downtime_hours:2,material_delay_days:2});
    await page.locator('#sampleQuestion').selectOption('1'); assert.match(await page.locator('#prompt').inputValue(),/S00003/); assert.equal(askCalls.length,0);
    await page.locator('#sampleQuestion').selectOption('2'); assert.equal(await page.locator('#downtimeHours').inputValue(),'2'); assert.equal(askCalls.length,0);
    await page.locator('#sampleQuestion').selectOption('1');
    await page.locator('#ask').click(); await page.waitForFunction(() => !document.getElementById('answerPanel').hidden);
    assert.match(await page.locator('#answer').textContent(),/正在|explaining/i);
    await page.waitForFunction(() => document.getElementById('answer').textContent.includes('MCU-C'));
    assert.equal(askCalls.length,1); assert.match(await page.locator('#answer').textContent(),/MCU-C/); assert.match(await page.locator('#trace').textContent(),/llm.explain_schedule/);
    await page.locator('#prompt').fill('FAIL'); await page.locator('#ask').click();
    await page.waitForFunction(() => document.getElementById('answer').textContent.includes('too many tokens'));
    assert.equal(await page.locator('#answerPanel').isVisible(),true); assert.equal(await page.locator('#error').isVisible(),true);
    await mkdir(path.join(root,'tmp'),{recursive:true});
    for (const width of [1440,390]) { await page.setViewportSize({width,height:1100}); assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),true); await page.screenshot({path:path.join(root,`tmp/manufacturing-schedule-${width}.png`),fullPage:true}); }
    assert.deepEqual(errors,[]); console.log('PASS: baseline, three what-if controls, Gantt, LLM samples, sources/trace, desktop/mobile layout.');
  } finally { if (browser) await browser.close(); await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); process.exitCode=1; });
