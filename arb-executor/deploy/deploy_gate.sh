#!/bin/bash
# Deploy gate — LAW (2026-07-04): NO DEPLOY WITHOUT LINT + SMOKE REPLAY.
# Tests-in-isolation are not a deploy gate; this is.
#
# 1. lint_gate.py on the candidate live_v4.py (duplicate-def/redefinition/syntax)
# 2. smoke replay: full LiveV3, real deploy config + paper_mode, recorded slate
#    hour, in an ISOLATED rsync copy so live state is never touched.
# Exit 0 = deploy may proceed. Anything else = deploy refused.
set -euo pipefail

REPO="${1:-/root/Omi-Workspace/arb-executor}"
SMOKE_ENV="/root/smoke_env/arb-executor"
TICKS_DIR="$REPO/analysis/premarket_ticks"

echo "=== DEPLOY GATE on $REPO (HEAD $(git -C "$REPO/.." rev-parse --short HEAD)) ==="

echo "--- [1/2] lint gate"
python3 "$REPO/deploy/lint_gate.py" "$REPO/live_v4.py"

echo "--- [2/2] smoke replay (isolated env: $SMOKE_ENV)"
mkdir -p "$SMOKE_ENV"
rsync -a --delete \
  --include='*.py' \
  --include='kalshi.pem' \
  --include='.env' \
  --include='config/***' \
  --include='docs/' --include='docs/policy/***' \
  --include='data/' --include='data/durable/' \
  --include='data/durable/exit_surface_gated_optima/***' \
  --include='data/durable/spike_volatility_map/***' \
  --include='deploy/***' \
  --exclude='*' \
  "$REPO/" "$SMOKE_ENV/"

cd "$SMOKE_ENV"
python3 deploy/smoke_replay.py --ticks-dir "$TICKS_DIR"

echo "=== DEPLOY GATE: PASS ==="
