#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv-traderfactory/bin/python}"
HOURS="${HOURS:-8}"
CACHE_ROOT="${CACHE_ROOT:-$ROOT/.cache/overnight_lab}"

export PYTHONPATH="${PYTHONPATH:-TraderFactory}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$CACHE_ROOT/matplotlib}"
export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-$CACHE_ROOT/pycache}"
mkdir -p "$MPLCONFIGDIR" "$PYTHONPYCACHEPREFIX"

exec "$PYTHON_BIN" TraderFactory/scripts/round1_overnight_lab.py --hours "$HOURS" "$@"
