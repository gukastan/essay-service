# C launch-text-boundary final handoff

Completed only assignment/run.sh, assignment/.env.example, assignment/README.md, assignment/web/foundation.mjs and assigned runtime evidence. No peer product/test edits or commits.

Safe localhost launcher installs frozen dependencies, supports ports0..65535, disables inherited tracing flags, propagates installer failures and SIGINT/SIGTERM, then execs the actual server. No arbitrary port kill, DB deletion, env sourcing, automatic restart, paid call, or root key read. README distinguishes current foundation from future essay API/Vue and documents the separate opt-in migration compatibility probe plus settings restart.

Verification: fresh Python3.12.15 + two independent venv installs; current pinned lock install exit0; corrected actual runtime5 scenarios passed (health/control404, TERM, INT, occupied-port nonzero preserving sentinel, bad port64); installer signal/error3 scenarios passed; 12 JS tests passed; README pytest121 passed/1 explicit paid skip. Existing DB unopened/unchanged. Owned environments and all observed server/MCP PIDs cleaned; normal assignment/.venv preserved.

Evidence index: docs/qa-evidence/assignment/foundation/runtime/README.md. Exact source hashes apply to runtime observation06:36:47Z; A made later type/format edits, so do not relabel these as post-format execution. Parent owns actual Vue browser evidence; B owns in-process MCP close/tracing checks; parent owns live probe invocation/result.

Programming self-review: launcher process ownership and browser boundary responsibilities, 33/57 pure lines, no added dependency/type escape/retry/logging layer. Platform fetch is explicit assignment choice. Tests cover behavior, not just implementation shape.
