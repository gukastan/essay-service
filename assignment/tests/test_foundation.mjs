import assert from 'node:assert/strict';
import test from 'node:test';
import { normalizeLf, codePointLength, codePointSlice, evidenceMatches, requestJson, RequestError } from '../web/foundation.mjs';

const fixtures = [
  ['한글 문장', '한글 문장', 5, 3, 5, '문장'],
  ['가😀\r\n나', '가😀\n나', 4, 1, 3, '😀\n'],
  ['가é🧑‍💻\r끝', '가é🧑‍💻\n끝', 8, 3, 6, '🧑‍💻'],
];
for (const [source, normalized, count, start, end, quote] of fixtures) {
  test(`code-point fixture ${JSON.stringify(source)}`, () => {
    // Given / When / Then
    assert.equal(normalizeLf(source), normalized);
    assert.equal(codePointLength(source), count);
    assert.equal(codePointSlice(source, start, end), quote);
    assert.equal(evidenceMatches(source, {start, end, quote}), true);
    assert.equal(evidenceMatches(source, {start, end, quote: '변조'}), false);
  });
}
for (const [start, end] of [[-1, 1], [0.5, 2], [0, 9], [2, 1], [0, NaN]]) {
  test(`invalid offset ${start}:${end}`, () => {
    // Given / When / Then
    assert.throws(() => codePointSlice('가😀나', start, end), RangeError);
    assert.equal(evidenceMatches('가😀나', {start, end, quote: '가'}), false);
  });
}

test('deadline aborts after 195 seconds while reading body without retry', async (t) => {
  // Given
  let advance;
  let delay;
  let calls = 0;
  let cleared = 0;
  let bodyEntered;
  const entered = new Promise(resolve => { bodyEntered = resolve; });
  t.mock.method(globalThis, 'setTimeout', (callback, milliseconds) => {
    advance = callback; delay = milliseconds; return 1;
  });
  t.mock.method(globalThis, 'clearTimeout', () => { cleared += 1; });
  t.mock.method(globalThis, 'fetch', async (_url, init) => {
    calls += 1;
    return { ok: true, json: () => new Promise((_resolve, reject) => {
      bodyEntered();
      init.signal.addEventListener('abort', () => reject(init.signal.reason), { once: true });
    }) };
  });
  // When
  const result = requestJson('https://example.invalid');
  const rejected = assert.rejects(result, {name: 'TimeoutError'});
  await entered;
  advance();
  await rejected;
  // Then
  assert.equal(delay, 195000);
  assert.equal(calls, 1);
  assert.equal(cleared, 1);
});

test('pre-aborted request never transmits', async (t) => {
  // Given
  let calls = 0;
  t.mock.method(globalThis, 'fetch', async () => { calls += 1; return new Response('{}'); });
  const controller = new AbortController();
  controller.abort();
  // When / Then
  await assert.rejects(requestJson('https://example.invalid', {signal: controller.signal}), {name: 'AbortError'});
  assert.equal(calls, 0);
});

test('HTTP failure exposes status without provider body or retry', async (t) => {
  // Given
  let calls = 0;
  t.mock.method(globalThis, 'fetch', async () => {
    calls += 1;
    return new Response('secret-provider-body', {status: 502});
  });
  // When / Then
  await assert.rejects(requestJson('https://example.invalid'), error => {
    assert.ok(error instanceof RequestError);
    assert.equal(error.status, 502);
    assert.equal(error.message.includes('secret-provider-body'), false);
    return true;
  });
  assert.equal(calls, 1);
});

test('successful JSON cleans timer and abort listener', async (t) => {
  // Given
  const controller = new AbortController();
  const remove = t.mock.method(controller.signal, 'removeEventListener');
  const clear = t.mock.method(globalThis, 'clearTimeout');
  t.mock.method(globalThis, 'fetch', async () => Response.json({status: 'ok'}));
  // When
  const body = await requestJson('https://example.invalid', {signal: controller.signal});
  // Then
  assert.deepEqual(body, {status: 'ok'});
  assert.equal(clear.mock.callCount(), 1);
  assert.equal(remove.mock.callCount(), 1);
});
