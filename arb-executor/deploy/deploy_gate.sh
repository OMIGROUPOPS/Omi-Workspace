#!/bin/bash
# Deploy gate — LAW (2026-07-04): NO DEPLOY WITHOUT LINT + SMOKE REPLAY.
# LAW (2026-07-05, C46): NOTHING DEPLOYS WITHOUT OUTCOME PROOF — every code change
# must be replayed against the prior slate's full position set and shown to improve
# actual outcomes (grades/dollars) before it arms. Lint proves it parses, smoke
# proves it runs, the outcome replay proves it MATTERS. All three or no deploy.
# Tests-in-isolation are not a deploy gate; this is.
#
# 1. lint_gate.py on the candidate live_v4.py (duplicate-def/redefinition/syntax)
# 2. smoke replay: full LiveV3, real deploy config + paper_mode, recorded slate
#    hour, in an ISOLATED rsync copy so live state is never touched.
# 3. outcome proof: OUTCOME_PROOF=<path> must name the per-game outcome-replay doc
#    (PROOF_PASS pattern, .claude/proof_*/) citing the candidate short SHA.
# Exit 0 = deploy may proceed. Anything else = deploy refused.
set -euo pipefail

REPO="${1:-/root/Omi-Workspace/arb-executor}"
SMOKE_ENV="/root/smoke_env/arb-executor"
TICKS_DIR="$REPO/analysis/premarket_ticks"

echo "=== DEPLOY GATE on $REPO (HEAD $(git -C "$REPO/.." rev-parse --short HEAD)) ==="

echo "--- [1/3] lint gate"
python3 "$REPO/deploy/lint_gate.py" "$REPO/live_v4.py"

echo "--- [2/3] smoke replay (isolated env: $SMOKE_ENV)"
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

echo "--- [3/3] outcome proof (C46: replay vs the prior slate's positions, grades/dollars)"
CAND_SHA=$(git -C "$REPO/.." rev-parse --short HEAD)
if [ -z "${OUTCOME_PROOF:-}" ]; then
  echo "OUTCOME PROOF MISSING: set OUTCOME_PROOF=<path to the per-game outcome-replay doc>"
  echo "(C46: lint proves it parses, smoke proves it runs, the outcome replay proves it MATTERS.)"
  exit 1
fi
if [ ! -f "$OUTCOME_PROOF" ]; then
  echo "OUTCOME PROOF NOT FOUND: $OUTCOME_PROOF"; exit 1
fi
if ! grep -q "$CAND_SHA" "$OUTCOME_PROOF"; then
  echo "OUTCOME PROOF STALE: $OUTCOME_PROOF does not cite candidate SHA $CAND_SHA"; exit 1
fi
echo "outcome proof OK: $OUTCOME_PROOF cites $CAND_SHA"

echo "=== DEPLOY GATE: PASS ==="
