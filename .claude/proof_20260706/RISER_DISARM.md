# RISER DISARM — pre-registered rule executed (C46 outcome doc, 2026-07-06)

**Candidate SHA: `e5de4f45`** (config-only: `riser_post_revision: true → false`; the code
delta vs the proven morning state b8a73a55 is the gated-OFF z-score shadow + staged
analysis scripts — byte-identical-off, lint PASS, zero new test failures at commit time).

## The rule, verbatim (SCOREBOARD_20260706.md, pre-registered 07-05 BEFORE the data)
"if (a) does not move — median shift < 1¢ on CHALL/ITF riser fills — the fix MISSED and
comes out (disarm `riser_post_revision`, one config flip through the gate)."

## LANE 1 — the bars, both samples
| bar | 07-06 overnight box (n=130 CHALL/ITF riser fills) | LIVE session 12:15→15:16 ET | pre-registered pass |
|---|---|---|---|
| (a) fill-discount vs best-bid-at-post | **median −1¢** (non-eroded subset +1¢, eroded −4¢) | n=1: **−8¢** (BERMEL-BER, posted 76 → filled 84) | ≥ +2¢; **disarm < 1¢ → FIRED** |
| (b) retention | 83–90% class baseline held | 1/2 posted risers filled | ≥60% (not the breach) |
| (e) erosion | **60% of riser fills walked above first post** (med +6¢, max +57¢) | 1/1 eroded | <25% — FAIL; names the CAUSE (walks eat the conception-site revision) |

## LANE 2 — secondary
Overnight settled P&L attribution not separable at n; flagged. The disarm's Lane-2 exposure
is nil: OFF = the pre-revision baseline (riser posts at the bid), the configuration that ran
every night before 07-05 22:46.

## Why the population caveat no longer parks it
Yesterday's deferral cited the flip-night population change. Today's live tape (the honest
regime itself) produced n=1, consistent with breach, and cannot rescue the rule at any
horizon inside today. The operator's standing order: a failed fix does not trade the rest
of today in ambiguity — the letter executes. The EROSION mechanism (the walks) is the
follow-up build (walk-cap honest anchor, staged this session), which per the
pre-registration is where bar-(e) routes — the revision's idea survives in the aim-layer
lineage (AIM_V2_SPEC); the flag comes out.

## Post-action live verification (to be appended after restart)
Config echo from the running process + first riser placements post-boot at the bid
(riser_post no longer subtracted), timestamped.
