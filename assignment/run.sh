#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if ! command -v uv >/dev/null 2>&1; then
  printf '%s\n' 'uv is required. Follow the installation steps in assignment/README.md.' >&2
  exit 127
fi
port="${ESSAY_PORT:-8001}"
if [[ ! "$port" =~ ^[0-9]{1,5}$ ]] || (( 10#$port > 65535 )); then
  printf '%s\n' 'ESSAY_PORT must be an integer from 0 to 65535 (0 selects a free port).' >&2
  exit 64
fi
export LANGCHAIN_TRACING=false
export LANGCHAIN_TRACING_V2=false
export LANGSMITH_TRACING=false
stop_install() {
  kill -TERM "$install_pid" 2>/dev/null || true
  wait "$install_pid" 2>/dev/null || true
  exit "$1"
}
uv sync --frozen &
install_pid=$!
trap 'stop_install 130' INT
trap 'stop_install 143' TERM
if wait "$install_pid"; then
  trap - INT TERM
else
  install_status=$?
  trap - INT TERM
  exit "$install_status"
fi
venv_path="${UV_PROJECT_ENVIRONMENT:-.venv}"
exec "$venv_path/bin/python" -m uvicorn server:app \
  --host 127.0.0.1 --port "$port" --no-access-log
