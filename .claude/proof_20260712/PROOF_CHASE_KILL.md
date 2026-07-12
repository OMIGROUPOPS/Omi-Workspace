# PROOF — C-CHASE-KILL v1 (three locks, one gated deploy; the in-play chase ladder dies)

**Candidate SHA: 8a857ecf** (locks in live_v4.py + config knobs armed + monitor violation lines + replay harness).
**Classes cited:** the cap-void lineage (GHASPI 07-10 flag → defined-stamp 07-10 → **the cap rule is DEFINED in this build**, ledger updated with the KILLED bar) · bell coverage (11/day cited; today ran 55 — the cutover file carries the census).

## Prior art (C45)
- C-CYCLE-CAP (07-09 operator ruling, `reentry_cycle_cap`=2): counts COMPLETED buy→cash cycles — a 14-rung ladder is ONE pursuit, zero cycles; the constant is reused as the pursuit cap per constraint #11 (DECREED-by-operator, cycle ruling 07-08 lineage).
- C-FUSED-GUN (07-08): the buy-freeze organ the self-fill bell plugs into — one guard, six sources now.
- C-REALITY-BELL (07-10): sources 1–5 + bell_missing zero-tolerance; self_fill = source six, same `_gun_stamp` contract (confirm/disagreement records work unchanged).
- premarket_walk_cap (armed 07-03) + `walk_cap_honest_anchor` (staged OFF, PLEX_WALK_CAP_SIZES): the cap CORBRU proved void — see Part 4 below.
- Boot lineage rebuilds 1–4 (orders/gun/cycles/trade-ids): this build adds the 5th (pursuit counters + own-activity series + conception registry).

## Part 4 root (code path cited per rung)
All 13 post-initial rungs are `v4_move_repost` (walk-step reposts) chasing `current_price` 60→66 on a LIVE match. **Neither cap engaged:** `premarket_walk_cap` anchors on `_window_open[tk]["cell"]`, which was ABSENT for CORBRU (zero `premarket_walk_capped`/`reach_repost_capped` events on the tape) — the cap-void is the missing ANCHOR, not a wrong constant; the honest-anchor fallback built for exactly this hole sits staged OFF. **−0j escalates from ruling to defect: the ratified table idles while live legs walk 24¢ through the void.** Not cap-void re-entries (zero completed cycles), so the cycle cap never looked.

## Lane 1 — the replay (harness law), `.claude/replay_20260712/replay_chase_kill.py`, run at 8a857ecf on the VPS
CORBRU's 17 recorded buy placements (14 BRU rungs 41→65 + 3 COR) driven through the REAL chokepoint (`place_order` → `_place_order_unlocked`, real `_log`, real `_gun_stamp`; only I/O stubbed, module clock = the tape's own timestamps):
- **FAIL-BEFORE** (locks off = yesterday's config): 17/17 ACCEPTED — reproduces the live tape exactly.
- **PASS-AFTER, cap only:** BRU rungs 1–2 accepted, **rungs 3–14 `chase_cap_refused`** (the dispatch's "fills three through six REFUSED", and everything after them); COR's own 1–2 accepted, 3rd refused — the cap is per leg.
- **PASS-AFTER, both locks:** rung 1 (41) accepted; rung 2 (51) fires `self_fill_bell` (+10¢ inside 30 min) and passes as the evidence; **all 15 subsequent placements refused `gun_fired` (source self_fill) — the event frozen at the 51, the full 3+ hour chase refused including the entire COR side.**
- REPLAY PASS (exit 0).

**Delta named plainly (the spec wins, the tape is what it is):** exchange truth shows NO 51¢ fill — CORBRU has exactly 2 buy fills (65, 32; 4 fill rows total with exits, all maker). The 41→51 rise the operator read as fills was our own bid LADDER. The self-fill bell therefore feeds on the leg's own buy ACTIVITY (accepted placements AND fills — both recorded at the single emitter): on fills alone it could never have frozen CORBRU. The dispatch's replay bar ("freezes at the 51") is met on the placement series.

## Lane 2 — outcome replay vs the prior slate ($ effect, stated without varnish)
Under the locks, today's chase cohort would largely not exist: CORBRU frozen at a resting 51 that the 60+ tape never fills → no BRU 65 fill, no COR 32 completion → **the +115¢ CORBRU pair does not happen; cohort realized today was +415¢ (all six exited maker, hours ago; current exposure ZERO).** The locks refuse trades that WON today. The justification is the doctrine, not the day: chasing a rising in-play tape buys the sucker's anchor (A49; the entry-blend arc killed directional entry as a coin flip), the wins are adverse-selection roulette paid for by the CORBRU that loses 65 straight down, and the operator decreed the kill knowing today's ledger. Guard-rail cost bounded: refusals are per-leg and named; completion placements after leg1 are EXEMPT by construction (`_event_has_fill`) so the cap cannot manufacture starved singles; down/equal re-places pass so a frozen bid can never strand above a falling tape.

## Deploy gate
[1/2] lint PASS (AST core) · [2/3] smoke (gate-run) · [3/3] this file, OUTCOME_PROOF_SHA=8a857ecf · [4/4] C50 push · [5/5] constraints surface. Config knobs armed in the same commit (`chase_pursuit_cap_enabled`, `self_fill_bell_enabled`, `self_fill_rise_cents`=4, `self_fill_window_sec`=1800) — all DECREED, C-CHASE-KILL 07-12, cited in knob_citations.json (census regenerates at deploy).
