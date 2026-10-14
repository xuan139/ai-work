const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const http = require('node:http');
const { readFile, mkdir } = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const files = {
  '/hospital-demo': ['hospital-demo.html', 'text/html'],
  '/static/hospital-demo.js': ['hospital-demo.js', 'text/javascript'],
  '/static/hospital-demo.css': ['hospital-demo.css', 'text/css'],
  '/static/notion-demo.css': ['notion-demo.css', 'text/css'],
  '/static/icons/icon-192.png': ['icons/icon-192.png', 'image/png'],
};
const server = http.createServer(async (req, res) => {
  const file = files[new URL(req.url, 'http://localhost').pathname];
  if (!file) { res.writeHead(404); res.end(); return; }
  try {
    const content = await readFile(path.join(root, 'static', file[0]));
    res.writeHead(200, { 'Content-Type': file[1] }); res.end(content);
  } catch { res.writeHead(500); res.end(); }
});

(async () => {
  let browser;
  try {
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    browser = await chromium.launch({ headless: true, channel: 'chrome' });
    const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
    const errors = []; const requests = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/api/mcp/available', route => route.fulfill({ json: { servers: [{ id: 77, slug: 'hospital-demo', tools: [] }] } }));
    let release;
    await page.route('**/api/llm/run', async route => {
      requests.push(route.request().postDataJSON());
      await new Promise(resolve => { release = resolve; });
      await route.fulfill({ json: { answer: 'Demo answer', mcp: { used: false } } });
    });
    await page.goto(`http://127.0.0.1:${server.address().port}/hospital-demo`);
    await page.waitForFunction(() => !document.getElementById('ask').disabled);
    assert.equal(await page.locator('#sample option').count(), 6);
    assert.equal(await page.locator('#prompt').inputValue(), '');
    for (const [index, expected] of ['所有示範病患', 'demo-p001', '2026-10-15', 'Observation', 'Encounter/demo-e001'].entries()) {
      await page.locator('#sample').selectOption(String(index));
      assert.ok((await page.locator('#prompt').inputValue()).includes(expected));
      assert.equal(await page.locator('#prompt').evaluate(el => el === document.activeElement), true);
    }
    assert.equal(requests.length, 0, 'Choosing a sample must not call the LLM');
    await page.locator('#prompt').fill('我的自訂問題 demo-p002');
    assert.equal(await page.locator('#sample').inputValue(), '');
    await page.locator('#language').click();
    assert.equal(await page.locator('#sample option').first().textContent(), 'Choose a sample question');
    assert.equal(await page.locator('#prompt').inputValue(), '我的自訂問題 demo-p002');
    for (let index = 0; index < 5; index++) {
      await page.locator('#sample').selectOption(String(index));
      assert.ok((await page.locator('#prompt').inputValue()).startsWith('Use Hospital HIS / FHIR Demo MCP'));
    }
    const draft = await page.locator('#prompt').inputValue();
    await page.locator('#sample').selectOption('');
    assert.equal(await page.locator('#prompt').inputValue(), draft);
    await page.locator('#language').click();
    await page.locator('#sample').selectOption('1');
    const prompt = await page.locator('#prompt').inputValue();
    await page.locator('#ask').click();
    await page.waitForFunction(() => document.getElementById('sample').disabled);
    assert.equal(await page.locator('#prompt').isDisabled(), true);
    while (!release) await new Promise(resolve => setTimeout(resolve, 10));
    assert.equal(requests.length, 1);
    assert.equal(requests[0].prompt, prompt);
    assert.equal(requests[0].use_mcp, true);
    assert.equal(requests[0].mcp_server_id, 77);
    release();
    await page.waitForFunction(() => !document.getElementById('sample').disabled);
    await mkdir(path.join(root, 'tmp'), { recursive: true });
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1050 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.locator('#askForm').scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(root, `tmp/hospital-presets-${width}.png`) });
    }
    assert.deepEqual(errors, []);
    console.log('PASS: 5 bilingual presets, editable drafts, explicit submission, busy state, desktop/mobile layout (API fixtures).');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
