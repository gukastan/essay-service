import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const loader = process.env.OMOWRIGHT_LOADER;
assert.ok(loader, "Set OMOWRIGHT_LOADER to the installed browser skill scripts/omowright.mjs");
const { loadOmowright } = await import(pathToFileURL(loader).href);
const { omowright } = await loadOmowright();
const output = resolve(process.env.QA_OUTPUT_DIR || "docs/qa-evidence/browser");
await mkdir(output, { recursive: true });
const profile = await mkdtemp(join(tmpdir(), "essay-browser-qa-"));
const browser = await omowright.connectPipe({
  browserPath:
    process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  browserArgs: ["--headless", "--no-first-run", `--user-data-dir=${profile}`],
  storageRoot: profile,
});
const results = [];
let trace;
let routes;
try {
  const page = await browser.newTab(process.env.QA_BASE_URL || "http://127.0.0.1:3000");
  await page.cdp.send(
    "Emulation.setDeviceMetricsOverride",
    { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false },
    await page.resolveSessionId(),
  );
  await page.locator("#company").waitFor({ state: "visible", timeout: 15_000 });
  trace = omowright.createTrace(page, { dir: output });
  const snapshot = async () =>
    trace.mark("accessibility", omowright.compactSnapshot(await page.snapshot()));
  const fill = async (selector, value) => {
    await snapshot();
    await page.locator(selector).fill(value);
  };
  const click = async (selector) => {
    await snapshot();
    await page.locator(selector).click();
  };
  const value = (selector) => page.evaluate((s) => document.querySelector(s)?.value, selector);
  const text = (selector) => page.evaluate((s) => document.querySelector(s)?.textContent, selector);
  const run = async (id, operation) => {
    console.log(`RUN ${id}: real Chrome browser; node tests/browser-qa.mjs; see trace.step`);
    await trace.step(id, operation);
    results.push({ id, verdict: "PASS" });
  };
  const samples = JSON.parse(
    await readFile(new URL("./fixtures/live-samples.json", import.meta.url), "utf8"),
  );
  const { id: _id, category: _category, ...input } = samples[0];
  await run("B01-empty-required-fields", async () => {
    await click('button[type="submit"]');
    await page.locator("#company-error").waitFor();
    assert.equal(await page.evaluate(() => document.activeElement?.id), "company");
    for (const field of Object.keys(input)) assert.ok(await text(`#${field}-error`));
  });
  await run("B02-real-backend-missing-key-inputs-preserved", async () => {
    for (const [field, content] of Object.entries(input)) await fill(`#${field}`, content);
    await click('button[type="submit"]');
    await page
      .locator('.notice:has-text("모델 설정이 필요합니다.")')
      .waitFor({ state: "attached", timeout: 10_000 });
    for (const [field, content] of Object.entries(input))
      assert.equal(await value(`#${field}`), content);
    assert.equal(await page.locator('button[type="submit"]').isDisabled(), false);
  });
  routes = omowright.createRoutes(page);
  const intercepted = [];
  let reply = {
    status: 200,
    body: { status: "ready", draft: "가".repeat(801), characterCount: 801, generationCalls: 1 },
  };
  let gate = Promise.withResolvers();
  let observed = Promise.withResolvers();
  let holding = true;
  await routes.route(/\/api\/drafts$/, async (route) => {
    intercepted.push(JSON.parse(route.request.postData));
    observed.resolve();
    if (holding) await gate.promise;
    if (reply.abort) await route.abort();
    else
      await route.fulfill({
        status: reply.status,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reply.body),
      });
  });
  await run("B03-route-mock-pending-lock-and-ready-snapshot", async () => {
    await click('button[type="submit"]');
    await observed.promise;
    await page.locator('form[aria-busy="true"]').waitFor();
    for (const field of Object.keys(input))
      assert.equal(await page.locator(`#${field}`).isDisabled(), true);
    assert.equal(await page.locator('button[type="submit"]').isDisabled(), true);
    await page.evaluate(() => document.querySelector('button[type="submit"]').click());
    assert.equal(intercepted.length, 1);
    assert.deepEqual(intercepted[0], input);
    await writeFile(join(output, "pending.png"), await page.screenshot());
    gate.resolve();
    holding = false;
    await page.locator("#draft").waitFor({ state: "attached" });
    assert.equal(await value("#draft"), "가".repeat(801));
    assert.equal(await text(".original-experience"), input.experience);
    await fill("#experience", "다음 요청에 사용할 수정한 경험입니다.");
    assert.equal(await text(".original-experience"), input.experience);
  });
  await run("B04-route-mock-edit-count-boundaries-and-unicode", async () => {
    for (const count of [800, 801, 1000, 1001]) {
      await fill("#draft", "가".repeat(count));
      assert.equal(await text(".count"), `${count.toLocaleString("ko-KR")} / 1,000자`);
      assert.equal(
        await page.evaluate(() => document.querySelector(".count").classList.contains("valid")),
        count >= 801 && count <= 1000,
      );
      assert.equal(await page.locator('button:has-text("초안 복사")').isDisabled(), false);
    }
    const mixed = "가\r\n나\r다\n 😀 👨‍👩‍👧‍👦";
    const normalized = mixed.replace(/\r\n?/g, "\n");
    await fill("#draft", normalized);
    assert.equal(await value("#draft"), normalized);
    assert.equal(await text(".count"), `${Array.from(normalized).length} / 1,000자`);
    assert.equal(intercepted.length, 1);
  });
  await run("B05-route-mock-real-clipboard-current-edit-paste", async () => {
    const edited = "직접 수정한 현재 초안 😀\n공백 포함 내용";
    await fill("#draft", edited);
    await page.cdp.send("Browser.grantPermissions", {
      origin: new URL(page.url()).origin,
      permissions: ["clipboardReadWrite", "clipboardSanitizedWrite"],
    });
    await click('button:has-text("초안 복사")');
    await page
      .locator('.copy-feedback:has-text("현재 초안을 복사했어요.")')
      .waitFor({ state: "attached" });
    await fill("#question", "");
    await click("#question");
    await page.keyboard.press("Meta+V");
    assert.equal(await value("#question"), edited);
    trace.mark("clipboard-paste", {
      expected: edited,
      actual: await value("#question"),
      count: Array.from(edited).length,
    });
    await fill("#question", input.question);
  });
  await run("B06-route-mock-injected-clipboard-rejection", async () => {
    await page.evaluate(() => {
      Object.defineProperty(navigator.clipboard, "writeText", {
        configurable: true,
        value: async () => {
          throw new DOMException("QA denied", "NotAllowedError");
        },
      });
    });
    await click('button:has-text("초안 복사")');
    await page
      .locator('.copy-feedback:has-text("복사하지 못했어요.")')
      .waitFor({ state: "attached" });
    assert.equal(await page.locator('button:has-text("초안 복사")').isDisabled(), false);
    assert.equal(await value("#draft"), "직접 수정한 현재 초안 😀\n공백 포함 내용");
  });
  await run("B07-route-mock-needs-input-then-retry", async () => {
    reply = {
      status: 200,
      body: { status: "needs_input", message: "당시 맡은 역할을 알려 주세요.", generationCalls: 1 },
    };
    await click('button[type="submit"]');
    await page
      .locator('.notice:has-text("당시 맡은 역할을 알려 주세요.")')
      .waitFor({ state: "attached" });
    assert.equal(await value("#experience"), "다음 요청에 사용할 수정한 경험입니다.");
    assert.equal(await text(".original-experience"), input.experience);
    reply = {
      status: 200,
      body: { status: "ready", draft: "나".repeat(1000), characterCount: 1000, generationCalls: 2 },
    };
    await click('button[type="submit"]');
    await page.locator('.notice:has-text("초안이 준비됐어요.")').waitFor({ state: "attached" });
    assert.equal(await value("#draft"), "나".repeat(1000));
    assert.equal(await text(".original-experience"), "다음 요청에 사용할 수정한 경험입니다.");
  });
  await run("B08-route-mock-all-errors-preserve-input-and-result", async () => {
    for (const [status, code] of [
      [400, "INVALID_INPUT"],
      [422, "LENGTH_RETRY_EXHAUSTED"],
      [502, "MODEL_ERROR"],
      [504, "MODEL_TIMEOUT"],
      [500, "CONFIG_ERROR"],
    ]) {
      const before = intercepted.length;
      reply = {
        status,
        body: {
          status: "error",
          code,
          message: `QA 오류 ${code}`,
          ...(status === 400 ? { fieldErrors: { company: "QA 기업 오류" } } : {}),
        },
      };
      await click('button[type="submit"]');
      await page.locator(`.notice:has-text("QA 오류 ${code}")`).waitFor({ state: "attached" });
      assert.equal(intercepted.length, before + 1);
      assert.equal(await value("#experience"), "다음 요청에 사용할 수정한 경험입니다.");
      assert.equal(await value("#draft"), "나".repeat(1000));
      assert.equal(await page.locator('button[type="submit"]').isDisabled(), false);
    }
  });
  await run("B09-route-mock-network-and-shape-failures", async () => {
    reply = { status: 200, body: { unexpected: true } };
    await click('button[type="submit"]');
    await page
      .locator('.notice:has-text("초안을 불러오지 못했어요.")')
      .waitFor({ state: "attached" });
    reply = { abort: true };
    await click('button[type="submit"]');
    await page
      .locator('.notice:has-text("연결에 문제가 생겼어요.")')
      .waitFor({ state: "attached" });
    assert.equal(await value("#experience"), "다음 요청에 사용할 수정한 경험입니다.");
  });
  await run("B10-mobile-390-layout", async () => {
    await page.cdp.send(
      "Emulation.setDeviceMetricsOverride",
      { width: 390, height: 844, deviceScaleFactor: 1, mobile: true },
      await page.resolveSessionId(),
    );
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      true,
    );
    await writeFile(join(output, "mobile.png"), await page.screenshot({ fullPage: true }));
  });
  trace.mark("intercepted-requests", intercepted);
} finally {
  await routes?.dispose();
  await trace?.stop();
  await browser.close();
  await rm(profile, { recursive: true, force: true });
  await writeFile(
    join(output, "results.json"),
    `${JSON.stringify({ results, cleanup: "Owned browser closed and temporary profile removed", completedAt: new Date().toISOString() }, null, 2)}\n`,
  );
}
console.log(JSON.stringify(results));
