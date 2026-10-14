const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const { readFile, mkdir } = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const study = id => ({ id, patient_id: 'demo-p' + id.slice(-3), accession: 'DEMO-XR-' + id.slice(-3),
  date: '2026-10-14', description: '胸部 X 光教學影像', study_uid: '2.25.1234', report_status: id.endsWith('3') ? 'pending' : 'final',
  image_source: { author: 'Mikael Häggström', license: 'CC0 1.0' } });
const report = id => ({ id: 'report-' + id, version: 1, date: '2026-10-14',
  status: id.endsWith('3') ? 'pending' : 'final', text: id.endsWith('3') ? null : '教學報告。公開影像重用於虛構病患，不供臨床診斷。' });
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
    const errors = []; const calls = []; let summaries = 0;
    page.on('pageerror', error => errors.push(error.message));
    await page.route('https://radiology.test/**', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/api/radiology-demo/tools/call') {
        const { name, arguments: args } = route.request().postDataJSON(); calls.push(name);
        let result;
        if (name === 'radiology_search_patients') result = { patients: [1, 3].map(n => ({ id: `demo-p00${n}`, name: `教學病患 ${n}` })) };
        else if (name === 'radiology_search_studies') result = { studies: [study('demo-xr' + args.patient_id.slice(-3))] };
        else if (name === 'radiology_get_study') result = { study: study(args.study_id) };
        else if (name === 'radiology_get_report') result = { report: report(args.study_id) };
        else if (name === 'radiology_open_viewer') result = { preview_url: `/api/radiology-demo/studies/${args.study_id}/image` };
        else throw Error(name);
        return route.fulfill({ json: { tool: name, arguments: args, result } });
      }
      if (url.pathname.endsWith('/image')) {
        // UI fixture, not the public radiograph or an Orthanc integration test.
        return route.fulfill({ contentType: 'image/png', body: await readFile(path.join(root, 'static/icons/icon-192.png')) });
      }
      if (url.pathname.endsWith('/summary')) {
        summaries++;
        const payload = route.request().postDataJSON(); assert.equal(payload.study_id, 'demo-xr001');
        return route.fulfill({ json: { answer: '教學摘要 [R1]', model: 'test', call_id: 7, steps: [], citation_warning: false,
          sources: [{ id: 'R1', title: 'report-demo-xr001', version: 1, url: '/radiology-demo?study=demo-xr001#report' }] } });
      }
      const file = url.pathname === '/radiology-demo' ? 'static/radiology-demo.html' : url.pathname.slice(1);
      const contentType = file.endsWith('.html') ? 'text/html' : file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : 'image/png';
      return route.fulfill({ contentType, body: await readFile(path.join(root, file)) });
    });
    await page.goto('https://radiology.test/radiology-demo');
    await page.waitForFunction(() => !document.getElementById('patient').disabled);
    await page.locator('#patient').selectOption('demo-p001');
    await page.locator('[data-study="demo-xr001"]').click();
    await page.locator('#studyContent').waitFor({state: 'visible'});
    assert.equal(await page.locator('#xray').evaluate(el => el.naturalWidth > 0), true);
    assert.equal(summaries, 0);
    await page.locator('#ask').click();
    await page.waitForFunction(() => document.getElementById('answer').textContent.includes('[R1]'));
    assert.equal(await page.locator('#sources a').count(), 1);
    assert.equal(summaries, 1);
    await page.locator('#patient').selectOption('demo-p003');
    await page.locator('[data-study="demo-xr003"]').click();
    await page.waitForFunction(() => document.getElementById('reportMeta').textContent.includes('待完成'));
    assert.equal(await page.locator('#ask').isDisabled(), true);
    assert.equal(await page.locator('#answer').textContent(), '');
    assert.equal(await page.locator('#sources a').count(), 0);
    await mkdir(path.join(root, 'tmp'), {recursive: true});
    for (const width of [1440, 390]) {
      await page.setViewportSize({width, height: 1050});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.screenshot({path: path.join(root, `tmp/radiology-ui-fixture-${width}.png`), fullPage: true});
    }
    assert.ok(calls.includes('radiology_open_viewer'));
    assert.deepEqual(errors, []);
    console.log('PASS: patient/study/image/report/summary flow, citations, pending report, stale answer clearing, desktop/mobile (fixtures only).');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
