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

echo "--- [0/3] bank pre-restart book snapshot (C47-ENFORCE: the post-boot audit's diff base)"
(cd "$REPO" && python3 deploy/book_snapshot.py)

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

# [CUTOVER 07-14] path-mode is the law: the bot prices entries from
# ../.claude/trendpath/ATLAS_V1.json (+ ORIENT_V1). The smoke sandbox must
# carry the atlas or every entry is no_path_page_refused and the replay
# exercises nothing (the first cutover gate run FAILED exactly so).
mkdir -p "$SMOKE_ENV/../.claude/trendpath"
cp -f "$REPO/../.claude/trendpath/ATLAS_V1.json" \
      "$SMOKE_ENV/../.claude/trendpath/" 2>/dev/null || true
cp -f "$REPO/../.claude/trendpath/ORIENT_V1.json" \
      "$SMOKE_ENV/../.claude/trendpath/" 2>/dev/null || true

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

# [C50 — THE TWO-FILE CLOSE-OUT LAW, 2026-07-07] a deploy push is a close-out:
# it must carry the knowledge spine with it. Refuse any push (last deployed SHA
# -> HEAD) that does not touch BOTH .claude/BOARD.md (the standing queue) and
# arb-executor/docs/LIVING_VAULT.md (the chronological ledger). Bootstrap: if no
# last-deploy SHA is recorded yet, warn-pass once (deploy_live_v4.sh records it).
echo "--- [4/4] two-file close-out law (C50: BOARD.md + LIVING_VAULT.md in the push)"
LAST_SHA_FILE="$REPO/state/last_deploy_sha"
if [ -f "$LAST_SHA_FILE" ]; then
  LAST_SHA=$(cat "$LAST_SHA_FILE")
  if git -C "$REPO/.." cat-file -e "$LAST_SHA" 2>/dev/null; then
    PUSH_FILES=$(git -C "$REPO/.." diff --name-only "$LAST_SHA"..HEAD)
    MISS=""
    echo "$PUSH_FILES" | grep -q "^\.claude/BOARD\.md$" || MISS="$MISS .claude/BOARD.md"
    echo "$PUSH_FILES" | grep -q "^arb-executor/docs/LIVING_VAULT\.md$" || MISS="$MISS arb-executor/docs/LIVING_VAULT.md"
    # [C-MERGE-AND-LEDGER v1, 07-16] the OPEN LEDGER is gate-checked like the BOARD
    echo "$PUSH_FILES" | grep -q "^truth/OPEN_LEDGER\.md$" || MISS="$MISS truth/OPEN_LEDGER.md"
    if [ -n "$MISS" ]; then
      echo "CLOSE-OUT REFUSED (C50): this push ($LAST_SHA..HEAD) does not touch:$MISS"
      echo "Update the BOARD (queue state) and the LIVING_VAULT (ledger entry) and re-push."
      exit 1
    fi
    echo "two-file law OK: BOARD.md + LIVING_VAULT.md both touched since $LAST_SHA"
    # [C-ONE-TRUTH v1, 07-16] REGISTRATION LAW: a push that ADDS a law
    # (ruling), a fitted surface, or a dated study without registering
    # it (truth/INDEX.json in the same range) is REFUSED. Outside the
    # root = doesn't exist.
    NEW_TRUTH=$(git -C "$REPO/.." diff --name-only --diff-filter=A "$LAST_SHA"..HEAD | \
      grep -E '^\.claude/rulings/.*\.md$|^\.claude/[a-z_]*_20[0-9]{6}/|^\.claude/trendpath/.*\.json$|^\.claude/takerreach/.*\.json$' || true)
    if [ -n "$NEW_TRUTH" ]; then
      if ! echo "$PUSH_FILES" | grep -q "^truth/INDEX\.json$"; then
        echo "CLOSE-OUT REFUSED (C-ONE-TRUTH): this push adds unregistered truth members:"
        echo "$NEW_TRUTH"
        echo "Rebuild truth/INDEX.json (python3 truth/build_index.py) in the same push."
        exit 1
      fi
      echo "one-truth registration OK: new members + INDEX in the same range"
    fi
  else
    echo "C50 WARN: recorded last-deploy SHA $LAST_SHA not in history (branch surgery?) -- warn-pass, re-records at this deploy"
  fi
else
  echo "C50 BOOTSTRAP: no last-deploy SHA recorded yet -- warn-pass; deploy_live_v4.sh records it now"
fi

# [C-CONVICTION-REPLAY 07-10] operator constraints on the gate's grep surface
# alongside §0: the numbered standing orders must exist and keep their heads.
echo "--- [5/5] operator constraints surface (docs/OPERATOR_CONSTRAINTS.md)"
OC="$REPO/docs/OPERATOR_CONSTRAINTS.md"
if [ ! -s "$OC" ]; then
  echo "GATE REFUSED: docs/OPERATOR_CONSTRAINTS.md missing or empty (the operator's numbered standing orders)"
  exit 1
fi
for MUST in "BUILD BEFORE RERUN" "EXITS OUT OF SCOPE" "ONE DISPATCH IN FLIGHT" "NO DECREED CONSTANTS AS GOALS" "CATEGORY LAW" "REPLAY-HARNESS LAW"; do
  grep -q "$MUST" "$OC" || { echo "GATE REFUSED: constraint heading '$MUST' missing from OPERATOR_CONSTRAINTS.md"; exit 1; }
done
echo "operator constraints OK: numbered orders present"

echo "=== DEPLOY GATE: PASS ==="
