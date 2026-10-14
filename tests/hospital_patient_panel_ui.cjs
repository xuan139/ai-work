const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const { readFile, mkdir } = require('node:fs/promises');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const profiles = JSON.parse(execFileSync(path.join(root, '.venv/bin/python'), ['-c',
  'import json; from app.hospital_demo_profiles import PROFILES; print(json.dumps(PROFILES))'], { cwd: root }));
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
    let connected = true, failed = false, empty = false, mismatch = false, release;
    let pause = false, llm = 0;
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const patients = [1, 2, 3].map(n => ({ id: `demo-p00${n}`, name: [{ text: `教學病患 ${n}` }] }));
    await page.route('https://hospital.test/**', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/api/mcp/available') return route.fulfill({ json: { servers: [
        { id: 77, slug: 'hospital-demo', tools: [] }, ...(connected ? [{ id: 78, slug: 'orthanc-radiology', tools: [] }] : [])] } });
      if (url.pathname === '/api/llm/run') { llm++; return route.fulfill({ json: { answer: '' } }); }
      if (url.pathname === '/api/hospital-demo/tools/call') {
        const { name, arguments: args } = route.request().postDataJSON();
        if (pause && name === 'his_patient_overview') { pause = false; await new Promise(resolve => { release = resolve; }); }
        const content = name === 'his_search_patients' ? { records: patients } : { records: [], teaching_profile: profiles[args.patient_id] };
        return route.fulfill({ json: { tool: name, result: { structuredContent: content } } });
      }
      if (url.pathname === '/api/radiology-demo/tools/call') {
        if (failed) return route.fulfill({ status: 502, json: { detail: 'Orthanc unavailable' } });
        const { name, arguments: args } = route.request().postDataJSON();
        const id = args.study_id || 'demo-xr' + args.patient_id.slice(-3);
        const study = { id, patient_id: mismatch ? 'demo-p999' : 'demo-p' + id.slice(-3), accession: id, date: '2026-10-14', study_uid: '2.25.1234', image_source: { author: 'CC0 fixture', license: 'CC0' } };
        let result;
        if (name === 'radiology_search_studies') result = { studies: empty ? [] : [study] };
        else if (name === 'radiology_get_study') result = { study };
        else if (name === 'radiology_get_report') result = { report: { id: 'report-' + id, version: 1, date: '2026-10-14', status: id.endsWith('3') ? 'pending' : 'final', text: id.endsWith('3') ? null : 'Teaching report ' + id } };
        else if (name === 'radiology_open_viewer') result = { preview_url: `/api/radiology-demo/studies/${id}/image` };
        else throw Error(name);
        return route.fulfill({ json: { tool: name, arguments: args, result } });
      }
      if (url.pathname.endsWith('/image')) return route.fulfill({ contentType: 'image/png', body: await readFile(path.join(root, 'static/icons/icon-192.png')) });
      const file = url.pathname === '/hospital-demo' ? 'static/hospital-demo.html' : url.pathname.slice(1);
      return route.fulfill({ contentType: file.endsWith('.html') ? 'text/html' : file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : 'image/png', body: await readFile(path.join(root, file)) });
    });
    const ready = () => page.waitForFunction(() => !document.getElementById('imagePatient').disabled);
    await page.goto('https://hospital.test/hospital-demo'); await ready();
    assert.equal(await page.locator('#patientXray').evaluate(el => el.naturalWidth > 0 && !el.hidden), true);
    assert.match(await page.locator('#profileDiet').textContent(), /花生/);
    assert.match(await page.locator('#imagingReport').textContent(), /demo-xr001/);
    assert.equal(await page.locator('#imagingLink').getAttribute('href'), '/radiology-demo?study=demo-xr001');
    pause = true;
    await page.locator('#imagePatient').selectOption('demo-p002');
    await page.waitForFunction(() => document.getElementById('imagePatient').disabled);
    assert.equal(await page.locator('#imagingContent').isVisible(), false);
    assert.equal(await page.locator('#patientProfile').isVisible(), false);
    while (!release) await new Promise(resolve => setTimeout(resolve, 10));
    release(); await ready();
    assert.match(await page.locator('#profileDiet').textContent(), /蛋奶素/);
    assert.doesNotMatch(await page.locator('#profileDiet').textContent(), /花生/);
    await page.locator('#imagePatient').selectOption('demo-p003'); await ready();
    assert.match(await page.locator('#profileAdmissions').textContent(), /不代表從未住院/);
    assert.match(await page.locator('#imagingReportMeta').textContent(), /待完成/);
    assert.doesNotMatch(await page.locator('#imagingReport').textContent(), /demo-xr002/);
    await page.locator('#language').click();
    assert.equal(await page.locator('#imagingTitle').textContent(), 'Patient images and reports');
    assert.match(await page.locator('#imagingReportMeta').textContent(), /pending/);
    await page.locator('#language').click();
    await page.locator('#imagePatient').selectOption('demo-p001'); await ready();
    await mkdir(path.join(root, 'tmp'), { recursive: true });
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1050 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.screenshot({ path: path.join(root, `tmp/hospital-patient-${width}.png`), fullPage: true });
    }
    failed = true;
    await page.locator('#imagePatient').selectOption('demo-p002'); await ready();
    assert.equal(await page.locator('#imagingContent').isVisible(), false);
    assert.equal(await page.locator('#patientProfile').isVisible(), true);
    assert.match(await page.locator('#imagingMessage').textContent(), /Orthanc unavailable/);
    failed = false; empty = true;
    await page.locator('#imagePatient').selectOption('demo-p003'); await ready();
    assert.match(await page.locator('#imagingMessage').textContent(), /沒有符合/);
    assert.equal(await page.locator('#imageStudy').isDisabled(), true);
    empty = false; mismatch = true;
    await page.locator('#imagePatient').selectOption('demo-p001'); await ready();
    assert.equal(await page.locator('#imagingContent').isVisible(), false);
    assert.match(await page.locator('#imagingMessage').textContent(), /不符合/);
    mismatch = false; connected = false;
    await page.locator('#imageRefresh').click(); await ready();
    assert.match(await page.locator('#imagingMessage').textContent(), /尚未連線/);
    assert.equal(await page.locator('#patientProfile').isVisible(), true);
    assert.equal(llm, 0);
    assert.deepEqual(errors, []);
    console.log('PASS hospital patient panel: images/reports, profiles, switching, pending/empty/error/disconnected, source links, no automatic LLM, bilingual desktop/mobile (fixtures).');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
