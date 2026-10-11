#!/usr/bin/env bash
# Run LabLens. Default port 5091 (5000 is taken by another local service).
set -u
cd "$(dirname "$0")"
# Prefer a local venv (has opencv for photo cleanup); fall back to system python.
if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi
export PORT="${PORT:-5091}"
export LLM_BASE_URL="${LLM_BASE_URL:-http://127.0.0.1:8790/v1/chat/completions}"
export LLM_MODEL="${LLM_MODEL:-gemini-2.5-flash}"
echo "LabLens on http://127.0.0.1:$PORT  (python: $PY, model: $LLM_MODEL)"
exec "$PY" app.py
