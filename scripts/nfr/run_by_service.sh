#!/usr/bin/env zsh
set -euo pipefail
# Generate per-service NFR pages and summary under docs/nfrs

# Ensure we run from repo root
REPO_ROOT=${REPO_ROOT:-}
if [[ -z "$REPO_ROOT" ]]; then
  if command -v git >/dev/null 2>&1; then
    REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
  else
    REPO_ROOT=$(pwd)
  fi
fi
cd "$REPO_ROOT"

# Resolve Python interpreter; auto-create venv if missing
PY=${PY:-}
if [[ -z "$PY" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PY=".venv/bin/python"
  else
    if command -v python3 >/dev/null 2>&1; then
      python3 -m venv .venv
      PY=".venv/bin/python"
    elif command -v /opt/homebrew/bin/python3 >/dev/null 2>&1; then
      /opt/homebrew/bin/python3 -m venv .venv
      PY=".venv/bin/python"
    else
      echo "Python 3 not found. Please install python3." >&2
      exit 2
    fi
  fi
fi

# Ensure required Python packages are available in the chosen interpreter
"$PY" -m pip install -q --upgrade pip >/dev/null 2>&1 || true
"$PY" -m pip install -q pyyaml jsonschema >/dev/null 2>&1 || true

"$PY" ./scripts/nfr/build_service_pages.py
