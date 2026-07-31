# Window-1 initial-aim constant audit and replacement specification

Status: descriptive audit and specification only. No replay, scorer, strategy, order, or live code was changed or invoked.

## 1. The seven-cent constant

The controlling row is `ATP_CHALL|underdog|26_50`: `n=1,470`, bottom-depth p25/p50/p75 = `2/4/7` cents, median bottom time `139` minutes. The seven is the third quartile of the deepest pre-onset excursion below the page's **discovery anchor**. In the tour builder, discovery is the median minute-candle price during the first tape hour; bottom is the minimum `price_low` before the fitted flow-step onset; depth is `max(0, discovery - bottom)`. It is neither a Window-1 close delta nor an opening-price delta.

The page was built on 2026-07-15 from G9 tour minute candles before 2026-07-10, with live-era local tape used for ITF hardening. It predates the 2026-07-17 honest-clock migration. Plainly: **the seven-cent fit is pre-migration**.

Sources:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/trendpath/ATLAS_V1.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/arb-executor/analysis/trendpath_build.py

## 2. Predicted p75 dip versus actual ask-side travel

Comparator: the leg's reconstructed ATLAS anchor versus the lowest ask that persisted at least 10 seconds inside guarded Window 1. Bid churn is excluded. Actual travel is `max(0, anchor - ask_10s_low)`. Signed error is `predicted_p75 - actual_travel`: negative means the table was too shallow and would leave the bid too high; positive means it predicted a deeper dip than the ask-side tape supplied.

This is partitioned by tournament category and ATLAS price region. Quantiles are p25/p50/p75/p90; the JSON retains the complete integer-cent histogram and every contributing row ID. Cells with fewer than eight comparable legs are marked THIN rather than aggregated upward.

| Category | Price region | Comparable n | Predicted p75 median | Actual travel p25/p50/p75/p90 | Error p25/p50/p75/p90 | Too shallow / exact / too deep | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| ATP_CHALL | 26_50 | 228 | 7 | 0/1/2/3 | 5/6/7/7 | 6/2/220 | reportable |
| ATP_CHALL | 51_75 | 229 | 6 | 0/1/1/3 | 5/5/6/6 | 5/2/222 | reportable |
| ATP_CHALL | ge75 | 101 | 12 | 0/0/1/3 | 11/12/12/12 | 2/0/99 | reportable |
| ATP_CHALL | le25 | 100 | 5 | 0/1/2/3 | 3/4/5/5 | 1/3/96 | reportable |
| ATP_MAIN | 26_50 | 95 | 9 | 0/1/3/5 | 6/8/9/9 | 0/1/94 | reportable |
| ATP_MAIN | 51_75 | 96 | 15 | 0/1/2/4 | 12/14/15/15 | 1/0/95 | reportable |
| ATP_MAIN | ge75 | 29 | 29 | 0/1/3/6 | 26/28/29/29 | 0/0/29 | reportable |
| ATP_MAIN | le25 | 25 | 5 | 0/0/1/5 | 4/5/5/5 | 1/4/20 | reportable |
| WTA_CHALL | 26_50 | 67 | 6 | 0/0/1/2 | 5/6/6/6 | 0/0/67 | reportable |
| WTA_CHALL | 51_75 | 67 | 8 | 0/0/1/1 | 7/8/8/8 | 0/0/67 | reportable |
| WTA_CHALL | ge75 | 25 | 9 | 0/0/1/1 | 8/9/9/9 | 0/0/25 | reportable |
| WTA_CHALL | le25 | 22 | 4 | 0/0/1/2 | 3/3/4/4 | 0/0/22 | reportable |
| WTA_MAIN | 26_50 | 73 | 8 | 0/1/2/4 | 6/7/8/8 | 2/0/71 | reportable |
| WTA_MAIN | 51_75 | 74 | 10 | 0/0/1/2 | 9/10/10/10 | 1/0/73 | reportable |
| WTA_MAIN | ge75 | 56 | 34 | 0/0/1/3 | 33/34/34/34 | 0/0/56 | reportable |
| WTA_MAIN | le25 | 51 | 5 | 0/0/1/2 | 4/5/5/5 | 0/0/51 | reportable |

Conservation only, not a decision statistic: 1338 comparable legs; 19 negative, 12 exact, 1307 positive. NIK is negative eight: anchor 33, predicted seven, ask-side ten-second low 18, actual travel 15.

Full distributions and identities:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_initial_aim_constant_audit_20260731/ATLAS_P75_CATEGORY_PRICE_DISTRIBUTIONS.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_initial_aim_constant_audit_20260731/ATLAS_P75_ANCHOR_TRAVEL_LEDGER.jsonl

## 3. NIK anchor provenance

| Decision clock, scheduled / bell | Joint observation: NIK bid/ask/last, spread, dwell; VRB bid/ask/last, spread, dwell | Anchor | Side truth | p75 arithmetic |
|---|---|---|---|---|
| T−361.917 / T−366.917 | NIK 23/33/33, 10, 4s; VRB 67/77/∅, 10, 0s | 33 true print | offer-side: `BUY_YES__LIFT_ASK`, receipt `b17542ca-924e-4214-e91f-a96dc81ad7f6` | 33−7=26 |
| T−322.450 / T−327.450 | NIK 29/30/32, 1, 0s; VRB 67/76/∅, 9, 2349s | 30 rounded tight-book midpoint | **not a print**; no trade-side classification exists | 30−7=23 |
| T−278.650 / T−283.650 | NIK 24/27/28, 3, 1s; VRB 72/73/73, 1, 159s | 28 true print | receipt says bid-side: `SELL_YES__HIT_BID`; archived BBO simultaneously places 28 above ask 27, so side is retained from receipt rather than inferred from the book | 28−7=21 |

The three anchors therefore mix an offer-lifting execution, a constructed midpoint, and a bid-hitting execution. Applying one discovery-depth constant to all three is already a reference mismatch before the size of seven is considered.

Source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv

## 4. Downward chase and ask-reachable low

The frozen 804 rescore does not retain the ordered cancel/repost price stream. It retains first target, final legacy fill assignment, and total order count. Consequently, an exact count of downward cancel/repost transitions is **not recoverable** and is reported null. A conservative lower bound is a leg with more than one order and a final assigned fill below its first target. That proves a net-down placement path but cannot count intermediate moves, down-then-up paths, or unfilled chases.

The source also does not retain the capacity identity needed to credit five contracts. Every legacy fill assignment below is therefore `EVIDENCE_ABSENT` for five-contract credit and is diagnostic only.

| Category | Price region | Legacy assignments | Proven net-down lower bound | Ask-low comparable | Fill−ask-low p25/p50/p75/p90 | Above / equal / below ask-only floor |
|---|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | 26_50 | 32 | 6 | 21 | 0/0/4/7 | 10/6/5 |
| ATP_CHALL | 51_75 | 39 | 5 | 26 | -2/-1/1/2 | 9/4/13 |
| ATP_CHALL | ge75 | 5 | 2 | 3 | -1/2/2/2 | 2/0/1 |
| ATP_CHALL | le25 | 17 | 0 | 15 | 0/0/1/2 | 7/5/3 |
| ATP_MAIN | 26_50 | 9 | 0 | 4 | -2/0/1/1 | 2/1/1 |
| ATP_MAIN | 51_75 | 14 | 1 | 8 | -1/0/2/5 | 3/3/2 |
| ATP_MAIN | ge75 | 4 | 1 | 0 | —/—/—/— | 0/0/0 |
| ATP_MAIN | le25 | 5 | 2 | 4 | -1/1/1/1 | 3/0/1 |
| WTA_CHALL | 26_50 | 23 | 5 | 2 | -1/-1/-1/-1 | 0/0/2 |
| WTA_CHALL | 51_75 | 24 | 10 | 5 | -2/-1/0/0 | 1/1/3 |
| WTA_CHALL | ge75 | 11 | 4 | 0 | —/—/—/— | 0/0/0 |
| WTA_CHALL | le25 | 14 | 5 | 3 | -1/-1/-1/-1 | 0/1/2 |
| WTA_MAIN | 26_50 | 9 | 0 | 4 | -1/0/0/0 | 1/2/1 |
| WTA_MAIN | 51_75 | 6 | 1 | 1 | 0/0/0/0 | 0/1/0 |
| WTA_MAIN | ge75 | 3 | 0 | 3 | 1/1/1/1 | 3/0/0 |
| WTA_MAIN | le25 | 2 | 2 | 2 | -2/-2/-2/-2 | 0/0/2 |

Conservation only: 217 legacy fill assignments, 44 proven net-down paths across 41 events. Only 101 assignments retain a ten-second ask-low comparator. Among those, 41 are above, 24 equal, and 36 below the ask-only floor. The comparable sample does not support the population-wide claim that chase *systematically* finishes above the ask floor; NIK is a demonstrated member of the above-floor class. The missing transition stream and capacity evidence remain named measurement defects.

Full partition and identities:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_initial_aim_constant_audit_20260731/CHASE_AND_FILLABLE_LOW_CENSUS.json

## 5. Smallest honest replacement specification

This is a specification, not an implementation or claimed winner.

Lawful inputs before shape exists:

- the same-tick lawful external bid, ask, positive displayed size, spread, and ask-side dwell;
- receipt-qualified last trade, including whether it lifted the ask or hit the bid, as context only—not a universal subtract-from anchor;
- quote cadence and recurrence, separated by side; bid-only cadence has no reach authority for a buy;
- the sibling's same-tick book as a patience/cancel input, never as `100 - our fill` or a synthetic price reference;
- a fresh, independently bound external-book blend only as a sanity envelope. NIKVRB's frozen read was `NO-READ/stale_sources`, so it contributes nothing here;
- top-five depth as a vector/context. It cannot be collapsed to a scalar cell signer.

Smallest rule:

1. On the first lawful positive-size non-crossed BBO, before shape exists, join the live bid: `X0 = min(bid, ask - 1)`. A fresh bound external blend may veto an outlier but may not synthesize or sign X.
2. Re-evaluate on every raw book receipt. A bid change, midpoint change, or last-trade change alone outputs `HOLD(X)`; it cannot lower and repost the order.
3. Only ask-side evidence can change reach state. While `ask > X`, retain X unless an independently bound sibling-patience rule cancels it. If `ask <= X`, first apply capacity-honest fill accounting. If capacity is absent, cancel the now non-maker-safe order and wait; do not chase it downward on the same receipt.
4. A new order after cancellation requires a strictly later ask state that persists for the inherited ten-second ask-dwell comparator. Its maker price is `min(current_bid, current_ask - 1)`. The triggering observation cannot fill the new order.
5. Missing or crossed BBO, missing size, stale/unbound external blend, or ambiguous chronology produces a named `NO_CALL`. Shape, cell, and depth tables have no pre-entry signing authority.

Ten seconds is borrowed from the frozen ask-reachability comparator; it is not newly fitted here. Whether ten seconds is optimal remains unvalidated. No replacement threshold has been invented.

NIK under this rule:

| Clock, scheduled / bell | Joint same-tick observation | Existing p75 branch | Minimal rule |
|---|---|---|---|
| T−361.917 / T−366.917 | NIK 23/33/33, spread 10, ask dwell 4s; VRB 67/77/∅, spread 10, dwell 0s | 33−7=26, PLACE 26 | `min(23,32)=23`, PLACE 23 |
| T−322.450 / T−327.450 | NIK 29/30/32, spread 1, ask dwell 0s; VRB 67/76/∅, spread 9, dwell 2349s | 30−7=23, REPRICE 26→23 | bid/mid change has no reach authority; HOLD 23 |
| T−278.650 / T−283.650 | NIK 24/27/28, spread 3, ask dwell 1s; VRB 72/73/73, spread 1, dwell 159s | 28−7=21, REPRICE 23→21 | bid/last change has no reach authority and ask 27>23; HOLD 23 |

This removes subtract-a-constant and removes bid-led downward chase. It does **not** prove that 23 is the optimal final entry or that the rule reaches 18 across the population. The separately established sibling-patience cancellation remains a later causal input; its recurrence and five-cent release thresholds remain unvalidated single-specimen borrowings.

Machine-readable specification:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_initial_aim_constant_audit_20260731/INITIAL_AIM_REPLACEMENT_SPEC.json
