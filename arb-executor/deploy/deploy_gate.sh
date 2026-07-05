#!/bin/bash
# Deploy gate — LAW (2026-07-04): NO DEPLOY WITHOUT LINT + SMOKE REPLAY.
# LAW (2026-07-05, C46; AMENDED same day): NOTHING DEPLOYS WITHOUT OUTCOME PROOF —
# every code change must be replayed against the prior slate's full position set and
# shown to improve actual outcomes before it arms. Lint proves it parses, smoke
# proves it runs, the outcome replay proves it MATTERS. All three or no deploy.
# OUTCOME = TWO LANES, both required in the proof doc, judged separately:
#   LANE 1 — MECHANISM (primary, luck-free, every game counts): does the fix improve
#     the CONSTRUCTION of trades, replayed deterministically against the tape —
#     grade distribution, <=97 completion rate, delta-aim per leg, pair completion,
#     FV-capture. No settlement involved; this convicts or acquits.
#   LANE 2 — SETTLEMENT P&L (secondary, sanity check): reported alongside, flagged
#     LUCK-POLLUTED below n~30 settlements — never the sole verdict at small n.
#     Lane-1 win + Lane-2 loss at tiny n = "insufficient settlements", not guilty;
#     Lane-2 win without Lane 1 = "lucky sample", not proven.
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

echo "--- [3/3] outcome proof (C46 two-lane: replay vs the prior slate's positions)"
CAND_SHA=$(git -C "$REPO/.." rev-parse --short HEAD)
if [ -z "${OUTCOME_PROOF:-}" ]; then
  echo "OUTCOME PROOF MISSING: set OUTCOME_PROOF=<path to the two-lane per-game outcome-replay doc>"
  echo "(C46: lint proves it parses, smoke proves it runs, the outcome replay proves it MATTERS.)"
  exit 1
fi
if [ ! -f "$OUTCOME_PROOF" ]; then
  echo "OUTCOME PROOF NOT FOUND: $OUTCOME_PROOF"; exit 1
fi
# The proof cites a proven SHA (OUTCOME_PROOF_SHA, default HEAD). The proven SHA must be
# HEAD or an ancestor of HEAD with NO code/config/table delta between them (doc-only /
# monitor-log commits may land after the proof; code may not).
PROOF_SHA="${OUTCOME_PROOF_SHA:-$CAND_SHA}"
if ! grep -q "$PROOF_SHA" "$OUTCOME_PROOF"; then
  echo "OUTCOME PROOF STALE: $OUTCOME_PROOF does not cite proven SHA $PROOF_SHA"; exit 1
fi
if ! git -C "$REPO/.." merge-base --is-ancestor "$PROOF_SHA" HEAD; then
  echo "OUTCOME PROOF INVALID: $PROOF_SHA is not an ancestor of HEAD $CAND_SHA"; exit 1
fi
CODE_DELTA=$(git -C "$REPO/.." diff --name-only "$PROOF_SHA"..HEAD -- '*.py' 'arb-executor/config/' 'arb-executor/docs/policy/' | head -5)
if [ -n "$CODE_DELTA" ]; then
  echo "OUTCOME PROOF STALE: code/config changed after proven SHA $PROOF_SHA:"; echo "$CODE_DELTA"; exit 1
fi
echo "outcome proof OK: $OUTCOME_PROOF cites $PROOF_SHA; no code delta to HEAD $CAND_SHA"

echo "=== DEPLOY GATE: PASS ==="
