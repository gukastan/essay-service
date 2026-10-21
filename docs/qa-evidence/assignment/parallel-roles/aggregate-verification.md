# ESSAY-11·12·13·15 aggregate verification

2026-10-21, repository `/Users/jay/Projects/essay-service`, Python 3.12.15. Four members implemented separate role files and retained evidence in the linked role reports. This leader run verifies the combined checkout after two review fixes: F now checks every occurrence of repeated factual text, and the Vue proxy defaults to the backend's documented port 8001.

From `assignment/` the final commands and observed results were:

| Command | Observed result |
| --- | --- |
| `.venv/bin/pytest -q` | 460 passed, 2 skipped (both explicit paid opt-in), 20.70s; run with local loopback fixture socket permission |
| `.venv/bin/ruff check .` | All checks passed |
| `.venv/bin/ruff format --check .` | 90 files already formatted |
| `.venv/bin/basedpyright` | 0 errors, 0 warnings, 0 notes |
| `node --test tests/test_foundation.mjs tests/test_web_contract.mjs` | 13 passed, 0 failed |
| `git diff --check` | Exit 0 |

The first sandboxed Python run reported 439 passed, 20 failed, 2 skipped solely because existing MCP/HTTP tests could not bind `127.0.0.1` (`PermissionError: [Errno 1] Operation not permitted`). The same full suite passed when local fixture sockets were allowed; no test was removed or weakened. After subsequent F and proxy corrections the complete suite was rerun to the final 460-pass result.

The role reports provide exact inputs/outputs, failure-before-fix artifacts, mocked SDK boundaries and browser screenshots: [analysis](../analysis/verification.md), [writing](../writing/verification.md), [evaluation](../evaluation/verification.md), [Vue](../vue/verification.md). The Vue worker exercised 48 synthetic-response Chrome scenarios and the leader independently inspected 24 responsive light/dark screenshots. No paid model call or full role/API graph execution occurred in this run. ESSAY-14, 16 and 17 remain separate integration, regression and live factuality milestones.
