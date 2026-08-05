# Window-1 V32 no-chase state machine — executable disposition

Date: 2026-08-05

V32 makes the model-free no-chase discipline at `6f2c3f822b85cb4e4a22001cdfe14ef2af8384fc` executable on the frozen 804-event development population. One state per leg is recomputed at every book receipt from a trailing-300-second quote path plus the July-6 top-five depth-pressure read. Quote path is primary; opposite pressure is logged. FALLING rests one cent below best bid and can only walk down. RISING waits. SETTLED may take a standing ask only with spread at most one cent, dwell at least ten seconds, displayed size at least five, and the pair cap. A first credited fill arms the sibling at `99 - fill`. The 300-second value is evidence recency, not an elapsed-time action trigger; orders carry to the guarded right edge.

The executable fill correction is controlling: maker credit requires a strictly later seller-aggressed true print of at least five contracts at or below the active resting limit. Residency alone is not a fill. Taker credit is explicit displayed opposing size on the submission receipt.

Result: D=804; 1,564 acted legs; 957 credited legs, comprising 116 proven-maker and 841 proven-taker; 202 completed pairs; 202 under par; 41 both-below-close JOINT; 41 carried; 74 execution-floor pair passes. V32 therefore regresses the operative V29-R3 JOINT floor from 68 to 41 and is rejected as an operative replacement. V29-R3 remains operative. The earlier 201 result remains labelled `MODEL_FREE_CEILING`; the executable gap is 160 pairs and is the execution price of the conservative fill law, not market absence.

ARNROM executes at 61+38=99. Both sides are explicit taker credits; both are strictly below their audited own closes, so ARNROM is JOINT in V32. This differs from the model-free 56+38 exemplar and is reported without substitution.

Two clean builds reproduced 18 core artifacts byte-for-byte, including the exact 8,256,742-row decision trace. The 139,525,074-byte gzip trace was then deterministically split into two Git-safe binary parts; two split runs matched and exact reassembly returns SHA-256 `07db47509b949d41bc82662ddd20bf02a2c0c06e58da3ded5f51bd4e56518f4e`. Package tests, chronology tests, conservation tests, and hash checks pass. Forbidden-access counts are zero.

Frozen package commit: `a3429cad6719f96a25a900812e0f360b71a5607e`.

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a3429cad6719f96a25a900812e0f360b71a5607e/.claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805/SCORECARD.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a3429cad6719f96a25a900812e0f360b71a5607e/.claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805/FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a3429cad6719f96a25a900812e0f360b71a5607e/.claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805/REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a3429cad6719f96a25a900812e0f360b71a5607e/.claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805/WAITED_AND_LOST_COST.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a3429cad6719f96a25a900812e0f360b71a5607e/.claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805/ARNROM_REGRESSION_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a3429cad6719f96a25a900812e0f360b71a5607e/.claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805/DETERMINISM_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a3429cad6719f96a25a900812e0f360b71a5607e/.claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805/TRACE_PACKAGING_RECEIPT.json
