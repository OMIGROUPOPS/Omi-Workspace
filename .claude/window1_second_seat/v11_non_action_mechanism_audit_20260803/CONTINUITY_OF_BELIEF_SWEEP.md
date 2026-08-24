# REDUNDANCY SWEEP — CONTINUITY OF BELIEF ACROSS RECEIPTS

License: LAW_INDEX @ 3e3d3548 lineage, sha256 41784e6a… · L8 L11 L18 L20 L22 · welds.
Seat: CC verification. Method: six-lane fan-out over policy code, build receipts, shape organs, historical organs, ledger/rulings, and a repo-wide mechanical grep, each adversarially verified; every load-bearing claim below re-checked by me at rows.

## Answer in one line

**Continuity of BELIEF is HALF-WIRED and effectively dead: the mechanism exists, one genuinely consuming branch was added on 2026-08-24, and it fired 0 times in 2,767 placement rows. Shape elimination was fully WIRED a year-era ago and is retired with nothing replacing it.** Two other continuities — of evidence and of standing — are wired and are routinely mistaken for this one.

## 0 — A newer policy tip exists than anything I have counter-graded

`codex/window1-v54-touch-subordinated-20260824` tip **f5fb8e8f** ("window1: subordinate touch to live beliefs", 2026-08-24 09:44), one commit past 35555882. It cites F-VS-129/130 as its provenance and banks `v54_touch_subordinated_inside_spread_reach_20260824/`. Not yet counter-graded. All code lines below are at f5fb8e8f.

## 1 — Three different continuities, kept apart

| kind | verdict | receipt |
|---|---|---|
| **Evidence** (running lows/highs/volume) | WIRED, but category (c) | `window1_v54_functionable_os.js` `createTapeState` — per-leg `running_low_cents`, `running_true_trade_low_cents`, `running_high_cents`, `volume_contracts`. Monotone prefix aggregates ≡ recomputation from the causal prefix; they never resist contradiction |
| **Standing** (the rest on the book) | WIRED | `state.positions[leg].standing_target_cents`, written per receipt at `build_window1_v54_functionable_v6.js:608`. Dedicated organ: **V51 continuity-of-standing @69754968** — its own report says it "never creates the rest, never changes P"; measured, never ratified, gate-era retired |
| **Belief** (conviction / eliminations) | **HALF-WIRED, dead in execution** | §2 |

## 2 — The belief-continuity surface

Mechanism exists: `state` is created once per event (`v6.js:588`) and mutated per receipt; `state.dual_belief` is created on the first stage and never destroyed:

```
dual_belief_os.js:355  if (!state.dual_belief) state.dual_belief = { first_coherence: null, current_envelopes: null,
                         coherence_history: [], envelope_history: [], first_lawful_coherence_by_leg: {}, rearm_by_leg: {} };
```
Per-event only — nothing crosses games.

| field | persists? | consumed by a later decision? | verdict |
|---|---|---|---|
| `current_envelopes` | yes — written **only** under `if (coherentNow)` (L419/L428), the sole assignment, **never reset to null** → `beliefMode` (L432) is a one-way latch | **new at f5fb8e8f**: L528–548 `PRIOR_BELIEF_ENVELOPE_SUBORDINATES_TOUCH_HOLD_PENDING_CURRENT_RESOLUTION` — `targets = active`, `may_originate_rest: false`, `touch_lane_subordinated: true`. At 35555882 the same branch took the live bid with `may_originate_rest: true` | **HALF-WIRED** — see §3 |
| `rearm_by_leg` | yes — `armed_at_epoch/receipt` carried, `attempts` accumulates (L617, 664–696) | a carried **obligation to act**, not a belief; verifier: it only sets the `reason` string, and `actionForTarget` ignores `reason` | HALF-WIRED |
| `first_coherence` | yes — deep-frozen belief snapshot at first coherence (L429) | never read into a decision | HALF-WIRED (telemetry) |
| `first_lawful_coherence_by_leg` | yes — write-once latch | latency odometer only | HALF-WIRED (telemetry) |
| `coherence_history` / `envelope_history` | yes, accumulating | self-dedup / `.length` reported | HALF-WIRED (telemetry) |
| shape / family | **no** | `interimFamily` (L195–202) is a stateless sign test on current drift → three families | **ABSENT** |

## 3 — Why the one real wire is dead

In f5fb8e8f's own four-game run, `ENVELOPE_PLACEMENT_RECEIPT.json` has **2,767 placement rows**:
- 2,620 `CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE`
- 147 `DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT`
- **0** `PRIOR_BELIEF_ENVELOPE_SUBORDINATES_TOUCH…` · **0** `CONSUME_OWN_EVIDENCED_LIVE_TOUCH_WHILE_ENVELOPE_NULL`

Every receipt was either coherent or DISAGREES, so the subordination branch never executed. And in the 2,620 coherent rows the envelope read at L441 was **overwritten at L428 on that same receipt** — the value is a fresh recomputation, not a carried conviction; the 147 DISAGREES rows hold `active`, which is order standing. **No decision in the executed bed consumed a belief formed at an earlier receipt.**

## 4 — Shape elimination: WIRED once, retired

`build_window1_quote_shape_elimination_replay_v1.js` @**189eaa20** (output dir `quote_shape_elimination_20260731`) is a real eliminator: `leg.survivor_shapes = [...leg.all_shape_ids]` (L268) seeds the full candidate set, `const priorShapes = [...leg.survivor_shapes]` (L278) carries it across ticks, narrowing modules `window1_interim_elimination_v13.js`, `window1_pair_interim_elimination_v18.js` (`mutuallyNarrowPairAndLegs`), `window1_pair_couple_elimination_v19.js` (`narrowBySignableCouples`) shrink it, and survivorship is consumed in the placement decision (L178 `leg.survivor_shapes.includes(...)` → `leg.order`). Elimination/survivor/persistence-floor files: **9 at 189eaa20, 0 at f5fb8e8f.** Retired; nothing in the V54 lineage replaced it.

Measured consequence of its absence: in the @35555882 bed the current "shape" flips **51 times** and every one of the 8 legs visits all three families (DAN 11 flips, PAL 11, BAR 6, GIU 6, LAJ 5, PRA 5, SVA 4, URS 3). Nothing is ever ruled out.

## 5 — The law posture (this is not a gap nobody noticed)

Two standing findings push against belief persistence, and a third files it as a defect:
- **F-VS-102** named STALE-PRIOR-OVER-FRESH a defect; the prior-carrying path was deleted (`stale_prior_path_used` is now hardcoded false and gate-checked).
- **F-VS-118** requires current-receipt coherence to originate a placement — "stale coherence never originates a placement."
- **F-VS-106** filed a persisting belief price as FAULT B.

So continuity of belief is closer to **legislated against** than merely missing. Wiring it would need a ruling that distinguishes a *carried conviction* from a *stale prior* — the vault currently has no such distinction.

## Verdict

WIRED: continuity of evidence (as prefix aggregates) · continuity of standing.
HALF-WIRED: `current_envelopes` latch (code-live at f5fb8e8f, 0 executions), `rearm_by_leg` obligation, four telemetry fields.
ABSENT: retained shape/hypothesis eliminations anywhere in the current lineage — last WIRED at 189eaa20, retired.
