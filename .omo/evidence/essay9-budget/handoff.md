# ESSAY-9 execution budget handoff

Member B; 2026-10-19. Owned product files: `src/server/workflow/budget.ts`, `src/server/workflow/budget.test.ts` only.

## Interface

`new ExecutionBudget({signal?, now?})` creates one request-local budget. `deadline` is epoch milliseconds (default Date.now +180000). `snapshot()` returns readonly modelCalls/searches/pageReads/deadline. Never put the mutable runtime object in graph state.

`run(kind, callback({signal, timeoutMs}), scope?)` reserves synchronously and invokes callback once. Kinds model/search/page have caps6/2/3. Failure and cancellation after dispatch consume the attempt. There are no retries. Model calls are at most30000ms; every call respects the same request deadline. Search/page automatically start/use the shared45000ms research window. Research model must pass third argument `"research"`; other model roles use default `"request"` so concurrent analysis retains its own applicable deadline. This API was coordinated with provider member C.

`runResearch(callback)` wraps all research work, including parsing/gaps between providers; `runRequest(callback)` wraps entire orchestration including gaps between nodes. Both callbacks receive signal/timeoutMs and bound caller completion even for promises that ignore AbortSignal. `startResearch()` starts the stage window explicitly and never resets it. `cancel()`/`dispose()` abort active work and prohibit new work. Future graph integration should use runRequest + finally dispose, and runResearch around the research branch. No graph/roles/endpoint was implemented.

Timeout stops the shared budget and aborts siblings. Plain provider rejection propagates; future orchestrator must cancel siblings when selecting an error/needs_input terminal outcome. Ignored-signal transport work itself cannot be forcibly terminated in JavaScript, but the waiting caller always settles; late rejection is observed by Promise.race. Event-loop-blocking synchronous code cannot be preempted; a late completion is rejected by an explicit post-completion deadline check.

## Reproducible evidence

All paths below are rooted at `/Users/jay/Projects/essay-service/`.

Invocation for all behavioral scenarios: `pnpm exec vitest run src/server/workflow/budget.test.ts --reporter=verbose`.
Artifact: `.omo/evidence/essay9-budget/tests.log` (17 tests pass).

| Criterion/scenario | Binary observable |
| --- | --- |
| Parallel model/search/page contention | Exactly6/2/3 callbacks dispatch;4 excess attempts reject per kind |
| Failed model attempts/no retries | Exactly6 rejected provider invocations; seventh rejects LIMIT_EXCEEDED |
| Model transport ignores signal | Caller and sibling search reject at30000ms; both signals aborted;0 timers |
| Shared research model remainder | Search begins window; model starting at40000ms receives5000ms and rejects at45000ms |
| Research between provider calls | Hanging runResearch callback rejects at45000ms;0 timers |
| Shared request model remainder | Model starting at179000ms receives1000ms and rejects at180000ms |
| Expired request/research before dispatch | Typed deadline rejection;0 provider invocations;0 model attempts |
| External abort during dispatch | Active caller rejects CANCELLED; signal aborted; consumed attempt stays1; next call rejects |
| Already-aborted external signal |0 provider invocations |
| Successful cleanup | External abort listener removed;0 timers; original result returned |
| Explicit disposal | Pending caller rejects CANCELLED;0 timers |
| Request between provider calls | Hanging runRequest rejects at180000ms;0 timers |
| Synchronous late completion | Result rejected at30000ms despite timer not firing |
| Request isolation | Two concurrent budgets each permit6 model calls |

Static invocations:
- `pnpm exec tsc --noEmit --incremental false` → exit0, `.omo/evidence/essay9-budget/typecheck.log`.
- `pnpm exec biome check src/server/workflow/budget.ts src/server/workflow/budget.test.ts` →2 checked, no fixes, `.omo/evidence/essay9-budget/lint.log`.

Initial test launch hit sandbox cache writes; permission granted and full scenario suite rerun. Initial whole-repository typecheck saw contracts member's in-progress import; member fixed it and final whole typecheck exited0. No existing v1 files edited. These are deterministic real-budget tests with fake clocks, not live-provider or browser validation.

## Programming review

Pure LOC: budget.ts117; budget.test.ts196. Single responsibility: request execution budgeting / behavioral budget tests. No untrusted external data boundary introduced. No assertions escaping types, any, non-null assertions, broad catches, logging, new dependencies, or >3-parameter functions. Mutable counters/controllers are intentionally local runtime state. Primitive operation kind selects map counters and time policy; no tagged-object variant is discarded. Tests exercise caps, shared deadlines, observable dispatch, rejection, abort and cleanup; no prompt prose pinned.

## Approved native-tool contract extension

The user approved replacing native internal query/page accounting with a hosted tool-call cap. Added `runNativeResearch(callback)` and readonly `NativeResearchContext` (signal, timeoutMs, maxToolCalls literal2). It atomically checks both budgets, then reserves1 model attempt plus2 hosted-tool calls before dispatch. Successful calls that use fewer tools, failures, and cancellations never refund reserved capacity. The provider must send `max_tool_calls: context.maxToolCalls`; this module cannot count unobservable internal queries/page reads. The unchanged explicit server search2/page3 counters remain separate.

`snapshot().nativeToolCallsReserved` is now a distinct field, coordinated with contracts/state member A and provider member C. Second native research dispatch is blocked without consuming another model attempt. Model exhaustion blocks native dispatch without reserving tools. Model cap remains6 shared with ordinary model calls. Research45s/model30s/request180s minimum still applies.

Leader approved adding `src/server/workflow/budget-native.test.ts` to keep focused tests below the skill size limit; existing budget.test.ts unchanged. Current pure LOC budget.ts137, budget.test.ts196, budget-native.test.ts120. Same architectural review conclusions as above; additional file owns native reservation regression tests.

Native verification invocation: `pnpm exec vitest run src/server/workflow/budget.test.ts src/server/workflow/budget-native.test.ts --reporter=verbose` →27 pass. Artifact `.omo/evidence/essay9-budget/native-tests.log`.

| Native criterion/scenario | Binary observable |
| --- | --- |
| Four simultaneous native attempts | Exactly1 callback, capacity2;3 reject; modelCalls1/nativeToolCallsReserved2; server counters0 |
| Six ordinary models before native | Native callback0; tools reserved0; modelCalls6 |
| Native/ordinary race with one model slot left | Native fulfills; ordinary rejects; modelCalls6/tools2 |
| Successful native call using zero actual tools | Next native blocked; modelCalls1/tools2 retained |
| Native provider failure | Next native blocked; modelCalls1/tools2 retained |
| External cancellation | Signal aborted; caller rejects; modelCalls1/tools2 retained;0 timers |
| Native call at t0, research t40s, request t179s | Supplied timeout30000/5000/1000ms respectively; timeout rejection;0 timers |
| Native call after research expiry | Callback0; modelCalls0/tools0 |

`pnpm exec biome check src/server/workflow/budget.ts src/server/workflow/budget.test.ts src/server/workflow/budget-native.test.ts` →3 checked clean; artifact `.omo/evidence/essay9-budget/native-lint.log`.

Whole-repository `pnpm exec tsc --noEmit --incremental false` during provider editing currently exits2 only for native-provider.ts:60 SDK `max_tool_calls` type error; artifact `.omo/evidence/essay9-budget/native-typecheck.log`. Provider member informed. This does not represent a passing final integrated typecheck; leader/provider must rerun after adapter fix.
