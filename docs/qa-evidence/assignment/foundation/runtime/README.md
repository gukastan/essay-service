# ESSAY-19 launcher and text-boundary verification

Executed 2026-10-20 on macOS arm64 with uv 0.13.1 and isolated uv-managed CPython 3.12.15. These are foundation observations, not completed essay generation or paid model QA. Existing session.db was only hashed, never deleted. No key or source .env file was read by this worker.

## Reproducible scenarios and binary observations

| Scenario | Invocation / environment | Required observation | Captured artifact |
| --- | --- | --- | --- |
| Fresh Python installation | `uv python install 3.12`, isolated `UV_PYTHON_INSTALL_DIR`, `UV_CACHE_DIR`, `UV_PYTHON_BIN_DIR` | exit 0; CPython 3.12.15 installed | `python-install.log` |
| Initial frozen installation | `uv sync --frozen --project assignment`, fresh isolated venv/cache | exit 0 | `uv-sync.log`, `initial-temp-root.txt` |
| Final pinned dependency installation | `uv sync --frozen --project assignment`, second fresh venv with the first run's isolated interpreter/cache | exit 0; lock hash `fa98a81e5c782279308596f58d303a01b717a2c3d85456fcd8cc4e91324f0904` | `uv-sync-final.log`, `install-hashes.txt`, `installed-packages.txt`, `temp-root.txt` |
| Honest foundation startup and control input | `node docs/qa-evidence/assignment/foundation/runtime/check-runtime.mjs` runs `ESSAY_PORT=0 bash run.sh` from assignment | health status ok, modelConfigured false, mcpConnected true, pipelineAvailable false; repeated instanceId identical, creationCount 1; drafts/chat/stream 404 | `runtime-result.json`, `runtime-final.log`, `sigterm.log` |
| Owned server/MCP cleanup | Same harness sends SIGTERM and SIGINT only to the recorded launcher/server PID | server lifespan shutdown completes; captured parent/MCP PIDs absent | `runtime-result.json`, `sigterm.log`, `sigint.log` |
| Occupied local port | Harness owns sentinel listener, then starts `ESSAY_PORT=<sentinel-port> bash run.sh` | nonzero exit (observed 3); sentinel still listening; collision server/MCP children absent | `runtime-result.json`, `collision.log` |
| Persistence/log boundary | Harness captures owned-process open files and compares pre/post copied DB hash | no session.db open handle, unchanged hash, control-input marker absent from logs/responses | `runtime-result.json`, `open-files.txt` |
| Installer interruption and errors | `node docs/qa-evidence/assignment/foundation/runtime/check-install-signals.mjs`, temporary uv stub | SIGINT exit130, SIGTERM exit143, own installer gone; installer exit37 propagated | `install-signals.json` |
| Launcher configuration edges | `bash -n run.sh`, missing-uv PATH, `ESSAY_PORT=65536 bash run.sh` | syntax exit0; missing uv127; invalid port64; .env.example values blank | `static-result.json` |
| Browser text/request contract | `node --test tests/test_foundation.mjs` from assignment | 12 passed: LF/Unicode fixtures, invalid offsets, timed body cancellation, preabort, single HTTP failure, cleanup | `static-result.json` |
| README Python checks in fresh environment | `uv run --frozen pytest` from assignment | exit0; 121 passed; 1 explicitly opt-in paid test skipped | `readme-pytest.log` |
| End-of-task owned cleanup | PID probes followed by removal of only recorded temporary roots | all observed owned PIDs absent; own environments/cache/interpreter/stub removed; assignment/.venv untouched | `cleanup.json` |

The initial uv installer binary already existed; the README's optional uv bootstrap download/install command was not executed. Actual Python installation and lock installation were executed. The Python test run had one sandbox-only pytest-cache write warning; no test failed. The paid opt-in test is **not** counted as passed by this report.

## Scope and history

`runtime-result.json` records exact source hashes at the passing 06:36:47Z runtime observation. A subsequently made formatting/type changes; these hashes are not relabeled as a check of later bytes. `owned-file-hashes.txt` captures this worker's final launcher/config/README/helper bytes. The dependency lock remained unchanged between final install and runtime execution.

Attempt 1 was blocked by sandbox process-list access and shut its owned server down. Attempt 2 checked process absence immediately and hit transient OS reaping. Attempt 3 assumed an old uvicorn occupied-port exit1 while the installed version returned3. Those logs remain in `runtime-attempt-{1,2,3}.log`. The final criterion is nonzero, with actual numeric exit recorded. An interim passing run was archived in `interim-before-lifecycle-fix/`; it is not the final same-process MCP ownership proof. A then implemented explicit transport close, and the final runtime was rerun successfully. B owns the stronger in-process transport cleanup regression.

Launcher injects tracing=false before startup; this harness began with tracing=true sentinel flags and recorded no secret values. Explicit app/child tracing flag proofs belong to B's lifecycle/stdio checks, not to an environment dump. Real Vue UI fixture verification belongs to the leader's `../browser/` artifacts. The helper itself was unchanged after those browser checks.

The source module uses the platform fetch API as assigned, adds no framework/dependency, and performs no retries. The timeout includes JSON body completion and listener/timer cleanup is unconditional. Future Vue integration must parse the returned JSON against its feature contract. No existing Vue page, original Downloads file, root Next.js file, Jira state, or commit was changed by this worker.

## Implementation self-review

Launcher responsibility: process entrypoint ownership. Browser module responsibility: text/HTTP boundary contract. Both remain below 200 pure lines (launcher33, helper57 in static-result.json). Public JS values use JSDoc types and unknown response JSON; no type assertions, mutable exports, swallowed unknown exceptions, tagged-union shortcuts, extra retry layer, or payload logging were added. Cancellation and error behavior have failing-sensitive tests. Source helpers are reusable by future Vue features and exercised independently in Node/browser checks. Shell cleanup targets only its own installer PID; server cleanup belongs to lifespan through direct exec.
