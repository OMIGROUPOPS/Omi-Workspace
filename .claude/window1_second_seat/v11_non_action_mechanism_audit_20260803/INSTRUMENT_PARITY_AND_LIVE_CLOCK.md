# INSTRUMENT PARITY + LIVE CLOCK ERROR [ANALYTICAL_ESTIMATE · MEASUREMENT ONLY]

Analysis seat only. Read-only. **No proposals.** Two measurements. Rows and receipts:
`INSTRUMENT_PARITY_AND_LIVE_CLOCK.json` · `LIVE_CLOCK_ROWS.csv` (804 rows).

Provenance triples (commit · path · sha256, in the JSON). Two of them are cross-checks: the truth table's
`f7bc71d8e615…` and the ripeness artifact's `e2a2162998…` are **byte-identical to the hashes V52p itself
recorded consuming** — the offline seat and the runtime read the same bytes.

---

# PART A — INSTRUMENT PARITY

Corpus: V52p's cohort @ `020b775c` — 60 legs / 30 games, **424,549** runtime role receipts, of which
**339,993** carry both an anchor and a series value. Method: recompute the published role rule @ `e269779b`
offline **at the exact receipt timestamps the runtime evaluated**, then diff.

## The four components, isolated

| component | result |
|---|---|
| **① post-formation-open anchor** | **46 of 52 comparable legs MISMATCH** (6 match, 8 unavailable) |
| ② price series | runtime vs offline true prints: 95.48% (leg floor) · 95.32% (game floor) · **98.20% (no formation floor)** |
| ③ drift computation | **339,993 / 339,993 = 100.000% internally consistent** |
| ④ receipt sampling | identical set by construction — offline evaluated at the runtime timestamps |

## The decisive isolation

| replay | agreement with the runtime's call |
|---|--:|
| offline rule using the **runtime's own anchor** | **329,095 / 339,993 = 96.795%** |
| …the residual 10,898 receipts | **all** `ABSTAIN_BELOW_EFFECTIVE_RIPENESS_GATE` (7,850 offline ROLE_UP + 3,048 offline ROLE_DOWN) |
| **→ ungated reproduction** | **329,095 / 329,095 = 100.000%** |
| offline rule using the **published anchor**, same series | **159,710 / 339,993 = 46.974%** |
| offline full published method | 160,511 / 329,746 = 48.677% |

Swapping **only** the anchor moves agreement from 96.8% to 47.0%. Nothing else moves it.

## The named defect

**`POST_FORMATION_OPEN_ANCHOR_BINDING`.** The runtime binds the anchor to the **first true print at or
after formation end** (identified by hypothesis test: 41 of 52 legs exact; ask-at-formation 9, mid 6, bid 3,
last-print-before-formation 1). The published method binds it to the **spread-settle mid** (@ `3c7bc577` /
`c0056976`) — a book quantity, half-cent capable; the runtime's is a trade price, always an integer.

Anchor delta (runtime − published), cents: **p05 −3 · p25 0 · median +3 · p75 +5 · p95 +46 · max +66**.
**38 of 52 legs (73%) are offset at or beyond the rule's own 2¢ decision threshold**; 37 legs sit above the
mid, 9 below, 6 equal. A first trade crosses at the ask in a wide book, so the anchor is biased high on most
legs, and the bias exceeds the threshold that defines the call.

Resulting disagreement modes: ROLE_DOWN→ABSTAIN **102,137** · ROLE_UP→ABSTAIN **62,084** ·
ABSTAIN→ROLE_UP 3,331 · ROLE_UP→ROLE_DOWN 914 · ABSTAIN→ROLE_DOWN 769.

**VERDICT: the instrument is faithful; the wiring feeds it the wrong anchor.** The rule reproduces exactly
(100%) wherever the gate is not suppressing it. V52p's observed 11/20 = 55% accuracy is fully explained by
the input binding, and impugns the wiring, not the published instrument. Secondary and not decisive: the
runtime's series does not floor at formation end (98.2% match unfloored vs 95.5% floored).

---

# PART B — LIVE CLOCK ERROR

## POST-HOC CERTIFICATION OF THE BELL — **not a live input**

Source: `.claude/window1_start_recovery_round2_20260724/REAL_START_LEDGER_V4.jsonl` (freeze declaration
`WINDOW1_START_TRUTH_ROUND2_FREEZE.md`; ledger sha256 `9d972c17837d…`). Precision classes: **exact 687** ·
live_by_only 52 · clean_interval 31 · schedule_only 20 · contradictory 14. **This is a TennisExplorer
historical *results* start clock — present only after the match completes. It is used here solely to certify
the truth table's bell, never as a live input.**

Verified bell minus honest-clock exact start, by bell source (seconds):

| bell source | n | p25 | med | p75 | reading |
|---|--:|--:|--:|--:|---|
| **MACHINE_RECEIPT** | 192 | **0** | **0** | **0** | **exact agreement at every percentile (min 0, max 0)** |
| TAPE_INFERENCE | 457 | −420 | −180 | +120 | ~3 min early in the median |
| TAPE_INFERENCE_CORROBORATED | 18 | −1,800 | −360 | −60 | |
| OBSERVED_STARTS_UPPER_BOUND | 16 | −115,011 | −15,975 | −10,875 | badly early — **the upper-bound label is confirmed correct** |

Overall (n=683): 66.0% within 5 min, 83.5% within 15 min, 92.4% within 30 min. **The truth table's exact
bells are independently correct, and its weakest class is correctly labelled as weak.**

## Live inputs and coverage

**Live-available:** catalog scheduled start (`joined/events.jsonl scheduled_start_exchange_ts`, **804/804
coverage**; only **2 of 804** revised against the final occurrence field) and Kalshi metadata
(`open_time`, `occurrence_datetime`, `expected_expiration_time`). **`close_time` and `settlement_ts` are
post-hoc and were not used.** Plus the **in-play tape guard** (July law, `REAL_START_LEDGER_V4` live_by
family: ≥5 true prints in a trailing 15 min on **both** legs, evaluated causally).

**Schedule alone vs verified bell** (n=778): p25 −720 · **median +7,020 s** · p75 +10,200 · p95 +11,340.
Within ±15 min **3.1%**, ±30 min **7.1%**; **late by >30 min: 70.3%.** The schedule is a session/order-of-play
anchor, not a match clock, and cannot serve as a span end.

**In-play tape guard latency after the true bell** (n=241): p25 146 · **median 233 s** · p75 375 · p95 1,205.
Fires within 5 min **67.6%**, 15 min **91.7%**, 30 min **95.9%**. It cannot preempt a start — it caps the span
shortly after one.

## THE LIVE-USABLE CLOCK — composite span end = min(scheduled start, in-play guard fire)

| | schedule alone | **composite live clock** |
|---|--:|--:|
| median error vs verified bell | +7,020 s | **−4,020 s** |
| p25 / p75 | −720 / +10,200 | −29,505 / **+27** |
| within ±15 min | 3.1% | **34.8%** |
| within ±30 min | 7.1% | **41.3%** |
| **late by >30 min** | **70.3%** | **1.9%** |

Which bound governs: the **tape guard on 640 games**, the schedule prior on 157. The guard converts a
wildly-late schedule into a mostly-**early** (span-shortening) estimate — errors move from the dangerous
side (span running past a bell that already rang) to the conservative side.

**This retires the "not live-realizable" claim as stated.** A live-computable span end exists; it is not the
verified bell, and its error is now measured rather than asserted.

## V52p bindings: live span vs verified span

- V52p's own recorded scheduled-proxy divergence: **51,384 receipts / 21 legs / 17 games (12.10%)** —
  reproduces its REPORT exactly.
- Recomputed with the **composite live span** and the published gates: **1 leg of 60 changes its binding**
  (1 game). Bound legs 13 → 12. Accuracy on truth-role legs **6/8 = 75.0% verified vs 5/7 = 71.4% live** —
  **only 7–8 bound truth-role legs exist in this cohort; far too small to certify the delta**, and stated as
  such.

## The error bars ripeness gates must tolerate

Span-fraction distortion = verified span ÷ live span (the multiplier applied to any observed f):
**p05 0.84 · p25 0.991 · median 1.017 · p75 1.619 · p95 6.882** (min 0.025, max 536.3); within ±10% of 1.0
on **54.3%** of games, ±25% on 63.2%; the live span is **shorter on 57.2%** (f inflated → gates fire earlier
in real time than the verified clock would license).

**Does span-fraction survive?** At the median, yes — a 1.7% distortion, and 1 binding change in 60 legs.
In the tail, no: a quarter of games carry ≥ ×1.62 distortion and 5% carry ≥ ×6.9, which is many multiples of
the gap between the published gates (0.023 → 0.964). A gate expressed as a fraction of a span inherits the
uncertainty of the span's end, and that uncertainty is not uniform across games. Both facts are measured;
neither is a recommendation.

## Conservation

804 games. Part A: 60 legs, 424,549 receipts, 339,993 with both components, 10,898 gated, 329,095 ungated,
52 legs anchor-comparable (46 mismatch + 6 match; 8 unavailable). Part B: 804 live estimates available, 783
comparable to a known bell, 778 with a formation-end span start, 683 comparable to the honest clock, 21
bells UNKNOWN and excluded throughout. Measurement only — no proposals, no wiring, no mechanism named.
ANALYTICAL_ESTIMATE.
