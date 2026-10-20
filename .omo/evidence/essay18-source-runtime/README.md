# ESSAY-18 source/runtime evidence index

Authoritative report and scenario artifacts: `/Users/jay/Projects/essay-service/docs/qa-evidence/assignment/baseline/source-runtime/README.md`.

# ESSAY-18 source and original runtime evidence

Captured on 2026-10-20. Source: `/Users/jay/Downloads/all_total_vue_student`; working copy: `/Users/jay/Projects/essay-service/assignment`.

46 supplied source/documentation/asset files were copied with equal SHA-256 hashes. Original screenshots under `assignment/doc/` are inherited source-package documentation, not evidence from this run. 10,444 files were excluded (mostly the supplied `.venv`). `source-provenance.json` records every included hash and excluded filename, size and reason. Excluded file contents, including `.env`, were not read or copied. Reverification found every included original unchanged. The only copy change is stronger `assignment/.gitignore` rules; all runnable source remains byte-identical. No domain migration or ESSAY-19 implementation occurred.

A fresh CPython 3.11.15 virtual environment was created at `.omo/runtime/essay18/venv`, without system site packages. Original lower-bound requirements resolved to 95 compatible installed packages. `installed-requirements.txt` captures exact versions as run evidence, not a modified application dependency contract. Platform/interpreter details are in `environment.json`; installation and compatibility results are in `venv-create.txt`, `install.txt`, and `package-check.txt`.

## Launch discrepancy and safe equivalent

The supplied package has no root `run.sh` and no `sh/run.sh`, although documentation/scripts refer to them. Existing launch files include `sh/run_agent_openai.sh`, `sh/run_agent_ollma.sh`, and `sh/run_frontend.sh`. The original agent scripts source `.env`, terminate arbitrary port listeners with `kill -9`, and delete `session.db`. They were read but never run. Exact executed installation and direct Uvicorn commands are in `commands.txt`. Both services bind only `127.0.0.1`; no reload is used.

Backend started as PID 50640, UI as PID 50794. The original lifespan spawned real MCP stdio children PID 50715 (`mcp_server.py`) and PID 50731 (`mcp_server_docs.py`) under the backend. `process-tree.txt` records this direct parent-child relationship. API `/health`, proxied UI `/health`, and UI `/` returned HTTP 200. Health reports `v2`, `fake`, one agent-bundle creation, and fake model names. The first incident request was reserved for the flow QA owner so the one-shot educational retry could be observed.

Each service was launched with `env -i`, no API credentials, `PYTHON_DOTENV_DISABLED=1`, `PYTHONDONTWRITEBYTECODE=1`, and LangChain/LangSmith tracing disabled. SQLite is hardcoded by the original implementation to `assignment/session.db`; this is a newly generated, ignored DB, isolated from the untouched Downloads DB. Runtime logs and virtual environment are ignored under `.omo/runtime/essay18/`. Original application prompt/debug semantics are retained, but full prompt output is not placed in these evidence artifacts.

## Evidence ledger

| Success criterion / scenario | Invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Source copy provenance | pathlib/shutil copy, SHA-256 of every included source and destination | 46/46 initial hashes equal; 10,444 exclusions inventoried | `source-provenance.json` |
| Original preservation and copy delta | SHA-256 reverification after launch | All included source hashes unchanged; only copied `.gitignore` differs | `source-reverification.json` |
| Isolated Mac install | `uv venv`, `uv pip install -r assignment/requirements.txt`, `uv pip check` | Fresh CPython 3.11.15 environment; install exit 0; all 95 packages compatible | `venv-create.txt`, `environment.json`, `install.txt`, `installed-requirements.txt`, `package-check.txt` |
| Fake v2 API startup | `curl -fsS -D ... http://127.0.0.1:8100/health` | HTTP 200; status ok; fake; v2; creation_count 1 | `backend-health.headers`, `backend-health.json` |
| Original UI and proxy startup | `curl -fsS -D ... http://127.0.0.1:8600/` and `/health` | Both HTTP 200; served HTML equals supplied UI | `frontend-ui.headers`, `frontend-ui.html`, `frontend-health.headers`, `frontend-health.json`, `runtime-checks.json` |
| Real MCP child processes | `ps -p 50640,50715,50731,50794 -o pid,ppid,command` | Two MCP scripts with backend parent PID 50640 | `process-tree.txt` |
| Localhost binding | `lsof -nP -iTCP:8100 -iTCP:8600 -sTCP:LISTEN` | API/UI only listen on 127.0.0.1 | `listeners.txt` |
| Runtime and secret exclusion rules | `git check-ignore -v` representative DB/env/venv/cache/log paths | All probe paths ignored | `ignored-paths.txt` |
| Provided script discrepancy | File inventory plus read-only script inspection | Root/sh run.sh absent, three named launch scripts present; unsafe cleanup not executed | `source-provenance.json`, `runtime-checks.json`, `commands.txt` |

Actual model/search calls were not attempted. Fake inference and JSON monitoring are educational fixtures. MCP protocol flow, API/SSE results and observed loops are peer-owned evidence under `../flow/`; actual browser QA is leader-owned under `../browser/`. Readiness does not independently certify those scenarios.

## Cleanup after team QA

At 2026-10-20T05:40:46Z, after the leader authorized shutdown, verified process identities and sent SIGTERM only to owned frontend PID 50794 and backend PID 50640. No arbitrary port-based kill was used. Both owned execution sessions subsequently completed with status 143 (SIGTERM). The backend and frontend, plus both MCP children 50715/50731, were absent in the process probe. Exclusive bind checks succeeded on localhost ports 8100 and 8600, proving release. `shutdown.json` captures commands, process output, target PIDs and port observations.

Final post-shutdown SHA-256 checks again verified all 46 original source/documentation files unchanged; copied `.gitignore` remains the sole intentional difference. `post-shutdown-source-hashes.json` contains every final hash. No runtime source fix was required. Runtime venv/logs and the newly generated fake SQLite DB remain local ignored artifacts; the servers are stopped.

| Success criterion / scenario | Invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Owned runtime cleanup | `kill -TERM 50794 50640`; `ps -p 50640,50715,50731,50794 -o pid,ppid,command`; socket bind to 127.0.0.1 ports 8100/8600 | All four owned PIDs absent; both port binds succeed | `shutdown.json` |
| Final source preservation | SHA-256 every included original/copy after shutdown | 46 originals unchanged; only copied `.gitignore` differs | `post-shutdown-source-hashes.json` |
