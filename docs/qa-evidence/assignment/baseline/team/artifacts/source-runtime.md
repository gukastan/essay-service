Source/runtime owner delivery: docs/qa-evidence/assignment/baseline/source-runtime/README.md
46 included files initially byte-matched; 10,444 excluded files; source reverified unchanged.
Only copied .gitignore modified. Runtime logic unmodified; fresh venv installs original requirements.
API http://127.0.0.1:8100 PID 50640; UI http://127.0.0.1:8600 PID 50794.
Real MCP children 50715 (ops) and 50731 (docs), parent 50640.
Owned exec sessions: backend 20735; frontend 44139. Keep alive until leader instruction.
No .env contents read; no paid LLM; tracing disabled; Python dotenv disabled; env -i.
Evidence index: .omo/evidence/essay18-source-runtime/README.md

FINAL 2026-10-20T05:40:46Z: leader authorized cleanup after browser QA. Sent SIGTERM only to 50794/50640. Both servers and MCP children 50715/50731 absent; 8100/8600 bind probes succeed. Exec sessions ended 143 (SIGTERM). shutdown.json and post-shutdown-source-hashes.json added. All 46 original files unchanged, copied .gitignore sole difference. Runtime stopped.
