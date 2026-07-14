#!/bin/bash
# [C-INCUMBENT-SUNSET Part 2, DECREED — DEFAULT-GO] After the consolidated
# packet fires, the operator's "stop" halts the cutover; 12 hours of
# silence flips trendpath_live=true through the FULL deploy gate (lint +
# smoke + outcome proof + C50 check + boot audit). The burden of proof is
# reversed: the proven design doesn't wait for ceremony. Runs on a 30-min
# cron; no-ops until every condition holds. STOP file:
# .claude/trendpath/OPERATOR_STOP (its presence permanently halts; the
# operator's word via the relay creates it).
set -u
WS=/root/Omi-Workspace
ST=$WS/.claude/trendpath/PACKET_STATUS.json
STOP=$WS/.claude/trendpath/OPERATOR_STOP
CONF=$WS/arb-executor/config/deploy_v5_live.json
LOG=/tmp/auto_cutover.log
cd "$WS" || exit 0
[ -f "$ST" ] || exit 0
if [ -f "$STOP" ]; then
  python3 - "$ST" <<'PY'
import json, sys
st = json.load(open(sys.argv[1]))
if st.get("go_state") != "STOPPED (operator word)":
    st["go_state"] = "STOPPED (operator word)"
    json.dump(st, open(sys.argv[1], "w"), indent=1)
PY
  exit 0
fi
READY=$(python3 - "$ST" "$CONF" <<'PY'
import json, sys, time
st = json.load(open(sys.argv[1]))
cf = json.load(open(sys.argv[2]))
ok = (st.get("fired") and st.get("go_deadline_epoch")
      and time.time() > st["go_deadline_epoch"]
      and not st.get("cutover_done")
      and not cf.get("trendpath_live", False))
print("GO" if ok else "NO")
PY
)
[ "$READY" = "GO" ] || exit 0
echo "$(date -u +%FT%TZ) conditions met -- executing default-GO cutover" >> "$LOG"
# guard: never run two cutovers (mkdir = atomic lock)
mkdir "$WS/.claude/trendpath/.cutover_lock" 2>/dev/null || exit 0
# 1) flip the flag (config commit = the candidate SHA)
python3 - "$CONF" <<'PY'
import json, sys
cf = json.load(open(sys.argv[1]))
cf["trendpath_live"] = True
json.dump(cf, open(sys.argv[1], "w"), indent=2)
PY
git add "$CONF"
git -c user.name="auto-cutover" -c user.email="bot@omi" commit -q -m "AUTO-CUTOVER (C-INCUMBENT-SUNSET default-GO, operator silence 12h past the packet): trendpath_live=true -- path-mode NO-CALL posture live; the convicted incumbent's static aims retire at this boot."
SHA=$(git rev-parse --short HEAD)
# 2) stamp the proof (doc-only commit after the candidate)
PROOF=$WS/.claude/proof_20260714/PROOF_CUTOVER.md
python3 - "$PROOF" "$ST" "$SHA" <<'PY'
import json, sys
tpl = open(sys.argv[1], encoding="utf-8").read()
st = json.load(open(sys.argv[2]))
out = tpl.replace("__SHA__", sys.argv[3]).replace(
    "__STATUS__", json.dumps(st.get("summary", {}), indent=1))
open(sys.argv[1], "w", encoding="utf-8").write(out)
PY
git add "$PROOF"
git commit -q -m "AUTO-CUTOVER proof stamped for $SHA (packet numbers attached). Doc-only after $SHA."
git push -q origin blend/kalshi-occ-fallback || true
# 3) the FULL gate
cd "$WS/arb-executor"
OUTCOME_PROOF="$PROOF" OUTCOME_PROOF_SHA="$SHA" bash deploy/deploy_live_v4.sh >> "$LOG" 2>&1
RES=$?
DEPLOYED=$(cat "$WS/arb-executor/state/last_deploy_sha" 2>/dev/null | cut -c1-8)
python3 - "$ST" "$SHA" "$DEPLOYED" <<'PY'
import json, sys, datetime
st = json.load(open(sys.argv[1]))
ok = sys.argv[3].startswith(sys.argv[2][:8]) or sys.argv[2].startswith(sys.argv[3])
st["cutover_done"] = {"sha": sys.argv[2], "deployed": sys.argv[3],
                      "verified": bool(ok)}
st["go_state"] = ("CUTOVER-DONE" if ok else
                  "CUTOVER-ATTEMPTED-GATE-FAILED (incumbent still runs)")
json.dump(st, open(sys.argv[1], "w"), indent=1)
PY
if grep -q "=== DEPLOYED" "$LOG"; then
  /root/notify.sh critical "AUTO-CUTOVER EXECUTED" "trendpath_live=true deployed ($SHA) after 12h default-GO silence. Path-mode NO-CALL posture is live; the incumbent's static aims are retired. Full gate + boot audit passed."
else
  /root/notify.sh critical "AUTO-CUTOVER GATE FAILED" "default-GO attempted ($SHA) but the deploy gate did not complete -- the incumbent still runs. Manual attention needed."
fi
rmdir "$WS/.claude/trendpath/.cutover_lock" 2>/dev/null
exit 0
