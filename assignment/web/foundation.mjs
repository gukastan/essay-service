// @ts-check

export const REQUEST_TIMEOUT_MS = 180_000;
export const CLIENT_TIMEOUT_MS = 195_000;

/** @param {string} text */
export function normalizeLf(text) {
  return text.replace(/\r\n?/g, "\n");
}

/** @param {string} text */
export function codePointLength(text) {
  return Array.from(normalizeLf(text)).length;
}

/**
 * @param {string} text
 * @param {number} start
 * @param {number} end
 */
export function codePointSlice(text, start, end) {
  const points = Array.from(normalizeLf(text));
  if (!Number.isInteger(start) || !Number.isInteger(end)
    || start < 0 || end < start || end > points.length) {
    throw new RangeError("Evidence offsets must be ordered code point positions within the text.");
  }
  return points.slice(start, end).join("");
}

/**
 * @param {string} text
 * @param {{ readonly quote: string, readonly start: number, readonly end: number }} evidence
 */
export function evidenceMatches(text, evidence) {
  try {
    return evidence.end > evidence.start
      && codePointSlice(text, evidence.start, evidence.end) === evidence.quote;
  } catch (error) {
    if (error instanceof RangeError) return false;
    throw error;
  }
}

export class RequestError extends Error {
  /** @param {number} status */
  constructor(status) {
    super("The server returned an unsuccessful response.");
    this.name = "RequestError";
    this.status = status;
  }
}

/**
 * Read one JSON response within the client deadline, including its body.
 * The caller validates the returned JSON against its feature's response contract.
 * @param {string | URL} url
 * @param {RequestInit} [init]
 * @returns {Promise<unknown>}
 */
export async function requestJson(url, init = {}) {
  const controller = new AbortController();
  const externalSignal = init.signal;
  const forwardAbort = () => controller.abort(externalSignal?.reason);
  const deadline = performance.now() + CLIENT_TIMEOUT_MS;
  const timeoutReason = new DOMException("The request exceeded the client deadline.", "TimeoutError");
  const timer = setTimeout(() => controller.abort(timeoutReason), CLIENT_TIMEOUT_MS);
  externalSignal?.addEventListener("abort", forwardAbort, { once: true });
  if (externalSignal?.aborted) forwardAbort();
  try {
    controller.signal.throwIfAborted();
    const response = await fetch(url, { ...init, signal: controller.signal });
    if (!response.ok) {
      await response.body?.cancel();
      throw new RequestError(response.status);
    }
    const body = await response.json();
    controller.signal.throwIfAborted();
    if (performance.now() >= deadline) throw timeoutReason;
    return body;
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", forwardAbort);
  }
}
