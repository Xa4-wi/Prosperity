#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "${SCRIPT_DIR}/../../.." && pwd)"
BT_DIR="${SCRIPT_DIR}"

usage() {
    cat <<'EOF'
Usage:
  run_repo_backtester.sh [TRADER] [DATASET] [EXTRA_ARGS...]

Defaults:
  TRADER   newest Bots/Round3/*.py file
  DATASET  round3

Dataset aliases:
  tutorial | tut
  round1   | r1
  round2   | r2
  round3   | r3
  round4   | r4

Examples:
  Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh
  Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py
  Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py round3 --day 2
  Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py round3 --products full --persist
  Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py /absolute/path/to/submission.log
EOF
}

pick_latest_trader() {
    find "${REPO_ROOT}/Bots/Round3" -maxdepth 1 -type f -name '*.py' \
        ! -name '*_module.py' \
        ! -name 'r3_bs_fair_module.py' \
        -print0 | xargs -0 ls -t 2>/dev/null | head -n 1
}

resolve_trader() {
    input="$1"
    if [ -z "$input" ]; then
        latest="$(pick_latest_trader)"
        if [ -z "${latest}" ]; then
            printf 'No trader file found under %s\n' "${REPO_ROOT}/Bots/Round3" >&2
            exit 1
        fi
        printf '%s\n' "$latest"
        return
    fi
    case "$input" in
        /*) path="$input" ;;
        *) path="${REPO_ROOT}/${input}" ;;
    esac
    if [ ! -f "$path" ]; then
        printf 'Trader not found: %s\n' "$path" >&2
        exit 1
    fi
    printf '%s\n' "$path"
}

resolve_dataset() {
    input="${1:-round3}"
    case "$input" in
        tutorial|tut) printf '%s\n' "${REPO_ROOT}/Data/Tutorial" ;;
        round1|r1) printf '%s\n' "${REPO_ROOT}/Data/ROUND_1" ;;
        round2|r2) printf '%s\n' "${REPO_ROOT}/Data/ROUND_2" ;;
        round3|r3) printf '%s\n' "${REPO_ROOT}/Data/ROUND_3" ;;
        round4|r4) printf '%s\n' "${REPO_ROOT}/Data/ROUND_4" ;;
        /*) printf '%s\n' "$input" ;;
        *)
            if [ -e "${REPO_ROOT}/${input}" ]; then
                printf '%s\n' "${REPO_ROOT}/${input}"
            else
                printf '%s\n' "$input"
            fi
            ;;
    esac
}

if [ "${1-}" = "-h" ] || [ "${1-}" = "--help" ]; then
    usage
    exit 0
fi

if [ -f "${HOME}/.cargo/env" ]; then
    # shellcheck disable=SC1090
    . "${HOME}/.cargo/env"
fi

if ! command -v cargo >/dev/null 2>&1; then
    printf 'cargo was not found. Install Rust first, then retry.\n' >&2
    printf 'See: %s\n' "${BT_DIR}/README_PROSPERITY.md" >&2
    exit 1
fi

TRADER_ARG=""
DATASET_ARG="round3"

if [ "${1-}" != "" ] && [ "${1#-}" = "$1" ]; then
    TRADER_ARG="$1"
    shift
fi

if [ "${1-}" != "" ] && [ "${1#-}" = "$1" ]; then
    DATASET_ARG="$1"
    shift
fi

TRADER_PATH="$(resolve_trader "$TRADER_ARG")"
DATASET_PATH="$(resolve_dataset "$DATASET_ARG")"

if [ ! -e "$DATASET_PATH" ]; then
    printf 'Dataset path not found: %s\n' "$DATASET_PATH" >&2
    exit 1
fi

cd "$BT_DIR"

if [ -z "${CARGO_TARGET_DIR-}" ]; then
    CARGO_TARGET_DIR="${BT_DIR}/.target"
fi
export CARGO_TARGET_DIR

printf 'trader: %s\n' "$TRADER_PATH"
printf 'dataset: %s\n' "$DATASET_PATH"

exec ./scripts/cargo_local.sh run --release -- \
    --trader "$TRADER_PATH" \
    --dataset "$DATASET_PATH" \
    "$@"
