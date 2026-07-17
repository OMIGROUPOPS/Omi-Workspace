# OUTCOME PROOF — P3 FLOOR-AT-CONCEPTION (pair-level, all phases)
Proven SHA: **SHAPLACE**
Operator word (07-17, verbatim): "The discovery floor moves to the single conception chokepoint every entry passes: every ITF event consults lifetime volume at conception; below floor = the EVENT is refused — both legs, one pair-level refusal, below_discovery_floor_refused with the volume seen — regardless of phase. Corridor and fallback checks remain as second doors. The number stays 1,500 — the operator's floor, untouched."
Prior art (C45): C-DISCOVERY-FLOOR v1 07-15 (the number + the corridor site; ALHVUX exhibit) · SITE-SCOPED LAW class (founded this push: the corridor-only site is instance 3) · never-wake probe (sub-floor ITF = −$76.66/wk, the dollars behind the law).

## Lane 1 — per-game replay (the bypass census IS the replay)
Census since 07-15 (`.claude/floor_20260717/FLOOR_BYPASS_CENSUS.txt`, method in floor_census.py): **463 non-corridor ITF conceptions; 31 on books under 1,500 lifetime EVEN NOW** (exact lower bound — books grown past the floor since conception are uncounted; the count rose 25→31 during this dispatch's own hour). Realized on the settled subset: **−125¢ across 3** (MASDUT −155 / SAKFER −65 / CHACHA2 +95); 28 open including BROBRA (66.0 shares — the founding exhibit, walked in WALK_BROBRA.md: the floor-consult line is ABSENT from its account because W1 phase never reached the corridor-scoped check). Under this deploy every one of the 31 conceptions is refused at the chokepoint with the volume logged: `below_discovery_floor_refused site=conception_chokepoint pair_level=true`.

## Lane 2 — behavior isolation
- Rides the EXISTING flag + number: `discovery_floor_enabled` (already true) and `discovery_floor_shares` (1,500, untouched). Flag off = byte-identical.
- Scope: ITF_M/ITF_W buys on UNFILLED events only — completion of a held leg is never blocked (never-hold-naked); corridor + fallback second doors untouched; non-ITF untouched.
- `event_lifetime_vol` is rebuilt atomically every discovery pass for all tracked events (the early-unlock organ) — an event conceivable at the chokepoint always has a reading; unmeasured reads refuse (the corridor site's own precedent).
- One pair-level log per event per boot (dedup set), the refusal returns the same `_error` shape as the sibling gates.

## Gate
lint + smoke via deploy/deploy_gate.sh (this file is OUTCOME_PROOF; OUTCOME_PROOF_SHA=SHAPLACE).
