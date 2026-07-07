# C-AIM-SHADOW — C46 no-order-path-delta proof (candidate SHA 8aac278a)

**The change is a LOGGER.** Diff anatomy at 8aac278a: (1) flag init `aim_shadow` +
lazy table handle; (2) helper `_aim_shadow_log` — reads the operational table +
sibling book, emits ONE `aim_shadow` log line, entire body inside try/except-pass;
(3) two call sites (after the v4_place log; before the v4_move_repost log) that
CALL the helper and change nothing else; (4) one marker key inside an existing
log dict; (5) config `aim_shadow: true`; (6) analysis/aim_shadow_rollup.py (offline).

**No-order-path-delta, grep-proofed:** the added code contains no `place_order`,
no assignment to `target_bid`/`new_target`/`entry_price`/any `pos.` attribute, no
cancel, no await on the order API. A helper exception cannot propagate (swallowed).
LANE 1: mechanism unchanged by construction — the order path is byte-equivalent
with the flag on or off. LANE 2: n/a (no trading delta to measure).
Lint PASS · zero new test failures vs baseline (43 pre-existing).

---
## AMENDMENT (C-SPREAD-EXPRESSION, candidate SHA be0880d9)
Adds book-state fields (bid/ask/spread) + posture classification for the actual bid
AND the shadow targets to the same `aim_shadow` line — all inside the same
try/except-swallowed helper. Same proof shape: no `place_order`, no target/pos
mutation, no cancels, no order-API awaits in the added code. Order path
byte-equivalent flag-on/flag-off. Lint PASS, zero new test failures.

Proven-state carrier: 1e98fc46 (delta from be0880d9 = analysis census scripts + docs only; zero bot-code change beyond the proven amendment).
