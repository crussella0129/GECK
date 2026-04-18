#!/usr/bin/env bash
# Cross-tool parity check for GECK v1.3.
#
# Runs the Python generator and the Rust `geck` binary against identical
# inputs, then asserts that the two implementations agree on every piece
# of content that should be deterministic (file tree, stable text,
# log_index.jsonl invariants, task IDs).
#
# Non-deterministic content (human-readable timestamps, runtime versions,
# OS/shell detection) is normalized before comparison.
#
# Usage: scripts/check_parity.sh
#
# Requirements:
#   * cargo on PATH (builds `geck` on first run)
#   * PYTHON pointing at a Python interpreter with `jinja2` installed
#     (default: /home/charles/.local/geck-venv/bin/python)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-/home/charles/.local/geck-venv/bin/python}"
CARGO_BIN="${CARGO_BIN:-$HOME/.cargo/bin/cargo}"

if [ ! -x "$PYTHON" ]; then
    echo "error: python interpreter not found at $PYTHON" >&2
    echo "set PYTHON=/path/to/python (must have jinja2 installed)" >&2
    exit 2
fi

WORK="$(mktemp -d -t geck-parity-XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

PY_ROOT="$WORK/py"
RS_ROOT="$WORK/rs"
mkdir -p "$PY_ROOT" "$RS_ROOT"

PROJECT_NAME="ParityDemo"
GOAL="Ship the Rust port"
PROFILE="cli_tool"

echo "==> building geck (release)"
(cd "$ROOT" && "$CARGO_BIN" build --quiet --release --bin geck)
GECK_BIN="$ROOT/target/x86_64-unknown-linux-musl/release/geck"
if [ ! -x "$GECK_BIN" ]; then
    # Fallback to default target triple if not using musl config.
    GECK_BIN="$ROOT/target/release/geck"
fi

echo "==> python generator scaffolds $PY_ROOT/GECK"
PYTHONPATH="$ROOT" "$PYTHON" - <<PYEOF
from geck_generator.core.generator import GECKGenerator
gen = GECKGenerator()
gen.init_geck_folder("$PY_ROOT", {
    "project_name": "$PROJECT_NAME",
    "goal": "$GOAL",
    "profile": "$PROFILE",
})
PYEOF

echo "==> rust binary scaffolds $RS_ROOT/GECK"
"$GECK_BIN" init "$RS_ROOT" \
    --project-name "$PROJECT_NAME" \
    --goal "$GOAL" \
    --profile "$PROFILE" >/dev/null

# ---- Assertions ----------------------------------------------------------

fail=0
check() {
    local label="$1"; shift
    if "$@"; then
        printf '  PASS  %s\n' "$label"
    else
        printf '  FAIL  %s\n' "$label" >&2
        fail=1
    fi
}

echo "==> comparing directory trees"
# Both roots should have the same relative layout.
diff <(cd "$PY_ROOT/GECK" && find . -type d -o -type f | sort) \
     <(cd "$RS_ROOT/GECK" && find . -type d -o -type f | sort)
check "identical file tree" true

echo "==> invariants on log_index.jsonl"
# Count non-empty lines (both impls may or may not emit a trailing newline).
count_records() { grep -c . "$1" || true; }
check "py log_index.jsonl has exactly one record" \
    test "$(count_records "$PY_ROOT/GECK/log_index.jsonl")" -eq 1
check "rs log_index.jsonl has exactly one record" \
    test "$(count_records "$RS_ROOT/GECK/log_index.jsonl")" -eq 1

# Normalize volatile fields (ts) to compare structurally.
strip_ts() {
    "$PYTHON" -c '
import json, sys
for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    obj = json.loads(line)
    obj["ts"] = "STRIPPED"
    print(json.dumps(obj, sort_keys=True))
' "$1"
}
py_idx="$(strip_ts "$PY_ROOT/GECK/log_index.jsonl")"
rs_idx="$(strip_ts "$RS_ROOT/GECK/log_index.jsonl")"
check "log_index.jsonl records are structurally identical" \
    test "$py_idx" = "$rs_idx"

echo "==> invariants on GECK_Inst.md"
# Jinja2 omits a trailing newline, Tera keeps one. Normalize before comparing.
normalize_trailing_nl() {
    awk 'BEGIN { ORS="" } { print sep $0; sep="\n" }' "$1"
}
check "GECK_Inst.md matches modulo trailing newline" \
    test "$(normalize_trailing_nl "$PY_ROOT/GECK/GECK_Inst.md")" = \
         "$(normalize_trailing_nl "$RS_ROOT/GECK/GECK_Inst.md")"

echo "==> invariants on tasks.md"
extract_task_lines() {
    grep -E '^- \[' "$1/GECK/tasks.md" | sort
}
check "task lines match" \
    test "$(extract_task_lines "$PY_ROOT")" = "$(extract_task_lines "$RS_ROOT")"

echo "==> invariants on LLM_init.md"
# Strip the volatile 'Created' line and normalize trailing newline.
normalize_llm_init() {
    sed '/^\*\*Created:\*\*/d' "$1" | awk 'BEGIN { ORS="" } { print sep $0; sep="\n" }'
}
check "LLM_init.md matches modulo Created date" \
    test "$(normalize_llm_init "$PY_ROOT/GECK/LLM_init.md")" = \
         "$(normalize_llm_init "$RS_ROOT/GECK/LLM_init.md")"

echo "==> invariants on decisions.md / learnings.md"
check "decisions.md matches modulo trailing newline" \
    test "$(normalize_trailing_nl "$PY_ROOT/GECK/decisions.md")" = \
         "$(normalize_trailing_nl "$RS_ROOT/GECK/decisions.md")"
check "learnings.md matches modulo trailing newline" \
    test "$(normalize_trailing_nl "$PY_ROOT/GECK/learnings.md")" = \
         "$(normalize_trailing_nl "$RS_ROOT/GECK/learnings.md")"

echo
if [ "$fail" -eq 0 ]; then
    echo "parity OK"
else
    echo "parity FAILED" >&2
fi
exit "$fail"
