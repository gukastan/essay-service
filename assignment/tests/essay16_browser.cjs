const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/Users/jay/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const port = Number(process.argv[2]);
const apiPort = Number(process.argv[3]);
const output = path.resolve(__dirname, '../../docs/qa-evidence/assignment/automated');

(async () => {
  assert.ok(Number.isInteger(port) && port > 0);
  assert.ok(Number.isInteger(apiPort) && apiPort > 0);
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, permissions: ['clipboard-read', 'clipboard-write'] });
    const page = await context.newPage();
    const errors = [];
    const requests = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {
      if (request.url().endsWith('/api/drafts')) requests.push(request);
    });
    await page.goto(`http://127.0.0.1:${port}/`);
    for (const [id, value] of Object.entries({
      company: '회사',
      role: '개발',
      question: '경험을 설명하세요.',
      experience: '😀 점검했다.\n직접 수정했다.',
      jobPostingText: '협업을 요구한다.',
    })) await page.locator(`#${id}`).fill(value);
    await page.getByRole('button', { name: '초안 만들기', exact: true }).click();
    await page.locator('#draft').waitFor({ state: 'visible', timeout: 20000 });
    assert.equal(requests.length, 1);
    assert.equal(requests[0].method(), 'POST');
    assert.equal(new URL(requests[0].url()).search, '');
    assert.equal([...await page.locator('#draft').inputValue()].length, 900);
    assert.ok(await page.getByText('생성 당시 검토 통과', { exact: false }).count());
    assert.ok(await page.getByText('협업을 요구한다.', { exact: false }).count());
    await page.screenshot({ path: path.join(output, 'essay16-real-chain-ready.png'), fullPage: true });
    await page.locator('#draft').fill('😀\n편집');
    await page.getByRole('button', { name: '현재 내용 복사' }).click();
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), '😀\n편집');
    assert.ok(await page.getByText('편집한 내용 · 수정본 미검토', { exact: true }).isVisible());
    await page.screenshot({ path: path.join(output, 'essay16-real-chain-edited.png'), fullPage: true });
    const choose = async mode => {
      const response = await fetch(`http://127.0.0.1:${apiPort}/__fixture/${mode}`, { method: 'POST' });
      assert.equal(response.status, 200);
    };
    await choose('missing');
    await page.getByRole('button', { name: '초안 만들기', exact: true }).click();
    await page.getByText('추가 정보가 필요합니다', { exact: true }).waitFor();
    assert.equal(await page.locator('#draft').inputValue(), '😀\n편집');
    await page.screenshot({ path: path.join(output, 'essay16-real-chain-needs.png'), fullPage: true });
    await choose('quality');
    await page.getByRole('button', { name: '초안 만들기', exact: true }).click();
    await page.getByText('이번 생성에서 기준을 충족하지 못했습니다', { exact: true }).waitFor();
    assert.equal(await page.locator('#draft').inputValue(), '😀\n편집');
    await page.screenshot({ path: path.join(output, 'essay16-real-chain-quality.png'), fullPage: true });
    assert.equal(requests.length, 3);
    assert.deepEqual(errors, []);
    process.stdout.write(JSON.stringify({ mode: 'real Chrome → Vue proxy → FastAPI → LangGraph with controlled model/research', requests: requests.length, draftCharacters: 900, editedCopy: true, needsPreservesPrevious: true, qualityPreservesPrevious: true, pageErrors: errors }) + '\n');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
