# RISER_POST REVISION — the evidenced proposal (2026-07-04, read-only replay; PLEX-GATED)

**Method:** every leg with window-open ≥50c across the last two logs (N=69 riser legs with
tape), replayed at demand-depths {0,1,2,3,4}¢ below window-open against the recorded trade
tape, premarket window = open→latch. Fill proxies: *certain* = print strictly below the
level (dip-through, queue-independent); *at-touch* = print ≤ level. FV verdict on the
subset with a recorded burst-FV (18 legs; thin — named caveat). Script:
`riser_depth_replay.py`, per-leg detail `riser_depth_legs.json`.

## The table (certain-fill retention / below-FV share of fills)

| depth | ALL fill (certain) | ATP_CHALL | ATP_MAIN | ITF_M | ITF_W | WTA_MAIN | below-FV of filled |
|---|---|---|---|---|---|---|---|
| 0 (today) | 91% | 100% | 88% | 83% | 95% | 100% | 44% |
| 1 | 84% | 100% | **38%** | 83% | 95% | 88% | 44% |
| 2 | 77% | 90% | **25%** | 83% | 79% | 88% | 47% |
| 3 | 70% | 90% | 12% | 75% | 79% | 62% | 43% |
| 4 | 62% | 90% | 12% | 62% | 68% | 62% | 38% |

## The two findings

1. **Fills do NOT vanish with depth — except on the main tours.** Challenger/ITF books dip
   through 2–4¢ of riser depth at 62–90% retention (ATP_CHALL barely notices: 90% at 4¢).
   ATP_MAIN collapses immediately (88→38% at just 1¢): liquid main-tour riser books do not
   dip; demand-depth there means non-participation.

2. **Depth does NOT kill the adverse selection — the answer to the question is NO.**
   Below-FV share of fills is flat across depth: 44% → 44% → 47% → 43% → 38%. The dumpers
   DO still hit us 2–3¢ lower: a fading riser leg blows through 4¢ of depth all the same.
   The seesaw's negative selection is structural (the June kept-leg mechanism: the filled
   leg loses 65%, was the worse-priced side 70% of the time), not a price-level artifact
   inside the 4¢ band. **What depth buys is CENTS, not selection**: at ATP_CHALL depth-3,
   90% retention × +3¢ better basis ≈ +2.7¢/riser-leg expected price improvement vs today,
   with the same proportion of those fills still being fades.

## Proposed aim-table riser_post revision (Plex-gated — touches entry doctrine, DO NOT ship without the gate)

| cat | riser_post today | proposed | rationale |
|---|---|---|---|
| ATP_CHALL | 0 | **3** | 90% retention at 3-4¢; the cheapest cents on the board |
| WTA_CHALL | 0 | **3** | structural sibling (no direct N tonight; CHALL class) |
| ITF_M | 0 | **3** | 75% retention at 3¢ |
| ITF_W | 0 | **2** | 79% retention at 2-3¢; steeper decay than ITF_M |
| ATP_MAIN | 0 | **0–1 (hold)** | 1¢ costs 50pts of fill-rate; the concession is the price of participating in liquid books — accept it KNOWINGLY, annotated |
| WTA_MAIN | 0 | **1–2** | 88% at 2¢, decays after |

**Honest framing for the gate:** this revision is a price-improvement trade (+2–3¢/leg on
~60–90% of Challenger/ITF riser fills), NOT an adverse-selection fix. The selection cost
is structural to being the resting side of a seesaw; the only structural mitigations
remain faller-side (where EARNED lives), pair-completion math (the bounds), and exits.
FV-subset is thin (18 legs) — the gate should demand a week of fv_observe accumulation
before treating the flat-selection curve as final.
