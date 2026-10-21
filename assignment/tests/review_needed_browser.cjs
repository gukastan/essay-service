const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/Users/jay/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const proxyPort = Number(process.argv[2]);
const apiPort = Number(process.argv[3]);
const output = path.resolve(__dirname, '../../docs/qa-evidence/assignment/browser');

(async () => {
  assert.ok(Number.isInteger(proxyPort) && proxyPort > 0);
  assert.ok(Number.isInteger(apiPort) && apiPort > 0);
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const results = [];
  try {
    for (const [width, theme] of [[390, 'light'], [1280, 'light'], [390, 'dark'], [1280, 'dark']]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const choose = async mode => {
        const response = await fetch(`http://127.0.0.1:${apiPort}/__fixture/${mode}`, { method: 'POST' });
        assert.equal(response.status, 200);
      };
      await choose('pass');
      await page.goto(`http://127.0.0.1:${proxyPort}/`);
      for (const [id, value] of Object.entries({
        company: '회사',
        role: '개발',
        question: '경험을 설명하세요.',
        experience: '😀 점검했다.\n직접 수정했다.',
        jobPostingText: '협업을 요구한다.',
      })) await page.locator(`#${id}`).fill(value);
      await page.getByRole('button', { name: '초안 만들기', exact: true }).click();
      await page.getByText('생성 당시 검토 통과', { exact: true }).waitFor();
      await page.locator('#draft').fill('이전 편집 내용');

      await choose('quality');
      await page.getByRole('button', { name: '초안 만들기', exact: true }).click();
      await page.getByText('이번 초안은 검토가 필요합니다', { exact: true }).waitFor();
      assert.equal([...await page.locator('#draft').inputValue()].length, 900);
      assert.ok(await page.getByText('생성 당시 기준 미충족 · 직접 검토 필요', { exact: true }).isVisible());
      assert.ok(await page.getByText('문항 충족:', { exact: false }).count());
      assert.equal(await page.getByText('아래는 이전에 생성한 결과입니다.').count(), 0);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      await page.screenshot({ path: path.join(output, `review-needed-${width}-${theme}.png`), fullPage: true });

      await choose('missing');
      await page.getByRole('button', { name: '초안 만들기', exact: true }).click();
      await page.getByText('필요한 정보: 나의 경험', { exact: false }).waitFor();
      assert.equal([...await page.locator('#draft').inputValue()].length, 900);
      assert.deepEqual(errors, []);
      results.push({ width, theme, reviewNeededHasCurrentDraft: true, postDraftMissingHasDraft: true, pageErrors: errors });
      await context.close();
    }
    process.stdout.write(JSON.stringify(results) + '\n');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
