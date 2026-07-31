# NIK-VRB decision autopsy

Event: `KXATPCHALLENGERMATCH-26JUL19NIKVRB`<br>
Category: `ATP_CHALL`<br>
Scheduled start: 2026-07-19 12:30:00 ET<br>
Observed bell: 2026-07-19 12:35:00 ET
Code bound for this autopsy: `arb-executor/live_v4.py`, Git blob
`01534495161a9f8f53477794a9e30d4483ebe39f`, SHA-256
`f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760`.

## Finding

The OS recognized VRB as the riser at every priced consultation, but the
orientation organ did not sign the price. The deployed `ATLAS` p50 path aim
signed instead. It placed VRB at 67 and then 65 while the only lawful VRB low
was 70. Once 65 existed, a separate hold law made the silence executable:
six own-book callbacks returned at the 60-second cadence gate and the next 868
returned at the `staircase_hold` quiet-volatility gate. The rolling 60-second
true-print count was never more than two; the configured trail threshold was
five.

NIK followed a different failure mode. Its three placements, 29 -> 26 -> 24,
were fresh re-conceptions after the prior order became marketable-stale, not a
single order walking down. The 24 filled at 10:39:57.500480 ET. Booking that
fill set `phase="active"`. From then to the actual bell, 5,534 NIK BBO
callbacks occurred, 5,387 with ask at or below 24, but the entry manager was
called zero times. The router's lawful-presence return and the
`phase == "entry_resting"` guard excluded all fourth-move logic. The later
18-cent tape was not evaluated and rejected by a target organ; it never
reached one.

That distinction is the reference law for future fixes:

- VRB before the first fill: repeated affirmative `HOLD` decisions.
- NIK after its fill: repeated entry-subsystem ineligibility, not `HOLD`.
- VRB after the NIK fill: active move/repost behavior, but only after the
  earlier 70-cent opportunity had passed.

## Evidence boundary

The five initial consultations, fill, first sibling re-aim, aggregate repost
counts, tape, and clocks are committed evidence. The earlier report binds a
full replay trace by SHA-256
`5dd923fb3636926165e651668954f6b778e9d4c8811b2254f3102a9aa05302cc`, but
the referenced local file is no longer present and was never committed.
Accordingly, this autopsy does **not** fabricate exact timestamps for each of
the nine later VRB move/repost cycles. It reports the committed facts: first
re-aim at 10:40:14, nine move/reposts, five `window_truth_reaim` decisions,
and no fill. Loose `C:\tmp` replay variants are not promoted to controlling
evidence because their fill state differs from the frozen replay.

The complete receipt-resolvable silence is preserved separately in
`NIKVRB_NON_DECISION_LEDGER.csv`: one row for every VRB own-book callback from
the 65 placement to the NIK fill, and one row for every NIK own-book callback
strictly after the fill through the actual bell.

## Clock convention

`T-minus scheduled` counts back from 12:30:00 ET. `T-minus bell` counts back
from the observed 12:35:00 ET. The five-minute difference is deliberate, not
rounding. The frozen evaluator right edge was 12:34:00 ET; the dual-book clock
continues to the observed bell for the decision autopsy.

## Chronology of committed decisions

| ET | T-minus scheduled | T-minus bell | Leg | Decision | Signer / return | What was overwritten or not reached |
|---|---:|---:|---|---|---|---|
| 04:30:00 | T-480.000 | T-485.000 | pair | Window admitted, but retained BBO and print history absent | admission only | No lawful price organ could run. |
| 06:14:33 | T-375.450 | T-380.450 | VRB | Enter durable `skip_no_trade` | `_v4_entry_anchor` returns `None` | All pricing organs below the last-trade gate were unreachable; 349 observations accumulated before the state ended. |
| 06:28:05 | T-361.917 | T-366.917 | NIK | Place 29 | `ATLAS` p50 path aim | Cohort/preliminary also arrived at 29; orientation named VRB riser but did not sign; all external voices were absent or diagnostic. |
| 07:07:33 | T-322.450 | T-327.450 | NIK | Cancel 29, then place 26 | marketable-stale cancellation; fresh `ATLAS` conception | 29 >= ask 30 - buffer 1 caused the cancellation. Tight-mid 30 replaced the out-of-book print 32; p50 depth 4 signed 26. |
| 07:13:56.179481 | T-316.064 | T-321.064 | VRB | True print 70, the eventual W1 low | market evidence, not an order decision | No already-resting VRB order existed at 70. |
| 07:13:58 | T-316.033 | T-321.033 | VRB | Place 67 | `ATLAS` p50 path aim | Orientation/preliminary target 69 was overwritten; contention `DROP` was not enforced. |
| 07:15:22 | T-314.633 | T-319.633 | VRB | Cancel 67 as marketable-stale | `_resting_cancel_reason` | 67 >= ask 68 - buffer 1. This is a real response during the second 68-ask visit. |
| 07:15:43 | T-314.283 | T-319.283 | VRB | Freshly conceive 65 | `ATLAS` p50 path aim | Orientation/preliminary target 67 was overwritten; sealed fish 60 was dossier-only; contention `DROP` remained unenforced. |
| 07:51:20.380398 | T-278.660 | T-283.660 | NIK | Print 28 against 24/27; 26 order becomes marketable-stale | cancel path | 26 >= ask 27 - buffer 1; old position is untombstoned for a fresh route. |
| 07:51:21 | T-278.650 | T-283.650 | NIK | Freshly conceive 24 | `ATLAS` p50 path aim | Sealed fish 23 was dossier-only; orientation still named VRB riser. |
| 10:39:57.500480 | T-110.042 | T-115.042 | NIK | Print 24 credits the resting five-lot | fill booking | `entry_qty=5`, `entry_filled_ts=now`, and `phase="active"`; all later NIK entry repricing becomes ineligible. |
| 10:40:14 | T-109.767 | T-114.767 | VRB | Reprice 65 -> 73 | print-backed `window_truth_reaim` through regular move/repost | The arrival helper itself returned because 65 was already <= 97-24. The following BBO manager formed 73, and combined headroom bounded it. |
| 10:40-11:09 | T-109.8 to T-80.8 | T-114.8 to T-85.8 | VRB | Toggle 72/73 | nine move/reposts, including five `window_truth_reaim` decisions | No later true print or opposite BBO reached the exposed level. Exact per-cycle timestamps are unavailable under the evidence boundary above. |
| 11:09:33 | T-80.450 | T-85.450 | VRB | Band changes flat/B4 -> faller/B2 | band cascade, descriptive | It did not originate the earlier 65 hold or recover the missed 70. |
| 11:38:49.709443 | T-51.172 | T-56.172 | NIK | True print 18 | market evidence only | NIK remained `active`; no entry target or fourth move was computed. |
| 12:30:12 | T+0.200 | T-4.800 | pair | Price-divergence gun fires | gun state | New entry walks are frozen. |
| 12:30:33 | T+0.550 | T-4.450 | VRB | Cancel remaining entry | match-live/gun cancellation | No second fill. |

## The signing chain at each priced consultation

All five consultations followed the same control sequence:

1. `_route_event` admits the side and calls `_v4_entry_anchor`
   (`live_v4.py:11391-11468`).
2. `_v4_entry_anchor` selects last trade or tight mid, looks up the native
   cell/regime, consults orientation, cohort, and the preliminary target
   (`live_v4.py:4739-5009`).
3. `_selector_verdict` computes the ATLAS path and contention return
   (`live_v4.py:2960-3004`).
4. `_pair_verdict` computes a synthetic `100-current_price` sibling rather
   than reading the actual sibling book (`live_v4.py:3014-3055`). The separate
   live seesaw is only a refusal ceiling (`live_v4.py:3057-3098`).
5. `_initial_entry_aim` returns `current_price - depth_p50`
   (`live_v4.py:5057-5080`).
6. Because `orientation_live=false`, the branch that could restore a
   riser-near-now price is skipped (`live_v4.py:12095-12110`).
7. The assignment `entry_price = target_bid = _pa9` makes ATLAS the actual
   signer (`live_v4.py:12142-12164`).

### Organ returns

| Time / leg | Instant inputs | Anchor | Orientation | Preliminary/cohort | ATLAS + contention | Pair | Other organs | Signed price |
|---|---|---|---|---|---|---|---|---:|
| 06:28:05 NIK | book 23/33, last 33 | last trade 33 | VRB riser, conviction 1.0, cohort + anchor-role voices | dog 26-50, n=2,053, dip p50 4; preliminary 30 -> 29 | underdog 26-50, n=1,470, p50 4 -> 29; `TRADE-AT-PATH` 26.1% | `PAIR-COMPOSED` 93, sibling estimate 67 | flow quiet/1 print; FV `NO-READ`; PM `NO-FEED`; library `NO-OPINION` | 29 |
| 07:07:33 NIK | book 29/30, last 32 outside tight book | tight mid 30 | VRB riser, 1.0 | same cohort, target 26 | p50 4 -> 26; `TRADE-AT-PATH` 39.4% | composed 93, sibling estimate 70 | flow quiet/1; external voices absent | 26 |
| 07:13:58 VRB | book 69/70, last 70 | last trade 70 | VRB riser, 1.0 | fav 51-75, n=2,008, p50 4, riser steering barred; preliminary 69 | leader 51-75, n=1,614, p50 3 -> 67; `DROP` -6.5% | composed 93, sibling estimate 30 | flow quiet/1; external voices absent | 67 |
| 07:15:43 VRB | book 67/68, last 70 outside tight book | tight mid 68 | VRB riser, 1.0 | preliminary 67; sealed pair dossier fish 60 | p50 3 -> 65; `DROP` -4.2% | composed 93, sibling estimate 32 | flow quiet/1; external voices absent | 65 |
| 07:51:21 NIK | book 24/27, last 28 | last trade 28 | VRB riser, 1.0 | dog cohort target 24; sealed dossier fish 23 | p50 4 -> 24; `TRADE-AT-PATH` 50.5% | composed 93, sibling estimate 72 | flow quiet/2; external voices absent | 24 |

The overwrite map is exact:

- Orientation affected the preliminary role in `_v4_entry_anchor`, but
  `orientation_live=false` prevented it from changing the final ATLAS price.
- Cohort could set the preliminary target, but `_initial_entry_aim` then
  installed ATLAS. Where both happened to agree, the number survived but the
  signing authority still changed.
- The sealed pair target was logged in the dossier but
  `pair_class_steer_enabled=false`; it never entered the target assignment.
- `DROP` was computed twice, but `contention_drop_enforced=false`; both orders
  posted.
- Flow, FV, Polymarket, and library values were recorded, not controlling.

## VRB's nine 68-ask visits

The quote-state series contains exactly nine 67/68 intervals totaling 641
seconds. The claim “the OS never moved off 65 on all nine” needs two
corrections: visit 1 predates any VRB order, and visit 2 is precisely when the
OS cancelled 67 and re-conceived 65.

| Visit | Interval ET | T-minus scheduled / bell at start | Seconds | VRB BBO receipts during state | Decision and code path |
|---:|---|---|---:|---:|---|
| 1 | 07:12:11-07:12:23 | T-317.817 / T-322.817 | 12 | 5 | No VRB order; no fresh VRB print, so `_v4_entry_anchor` returned `None` (`4775-4808`, `11464-11472`). |
| 2 | 07:15:22-07:16:21 | T-314.633 / T-319.633 | 59 | 2 | First receipt cancelled 67 as marketable-stale; fresh route signed 65 at 07:15:43; the remaining callback was inside the 60-second cadence return (`13242-13247`). |
| 3 | 07:21:12-07:21:20 | T-308.800 / T-313.800 | 8 | 7 | `staircase_hold` quiet-volatility return (`13248-13263`). |
| 4 | 07:22:12-07:22:20 | T-307.800 / T-312.800 | 8 | 3 | Same quiet FIFO hold. |
| 5 | 07:23:15-07:23:20 | T-306.750 / T-311.750 | 5 | 10 | Same quiet FIFO hold. |
| 6 | 07:24:13-07:24:20 | T-305.783 / T-310.783 | 7 | 8 | Same quiet FIFO hold. |
| 7 | 07:28:10-07:28:20 | T-301.833 / T-306.833 | 10 | 7 | Same quiet FIFO hold. |
| 8 | 07:29:11-07:29:20 | T-300.817 / T-305.817 | 9 | 8 | Same quiet FIFO hold. |
| 9 | 07:30:17-07:39:00 | T-299.717 / T-304.717 | 523 | 18 | Same quiet FIFO hold throughout. |

The quote-state builder and raw merged rows have different grains. Sixty-eight
VRB BBO receipt timestamps lie inside the nine state intervals; 49 underlying
merged rows are themselves stamped ask 68. This is retained, not coerced. The
visit fact is the quote-state interval; the raw-row count is a separate
provenance fact.

## Why 65 remained 65

From 07:15:43 through the NIK fill, VRB received 874 own-book callbacks.
Every callback first encountered two paths:

- `_route_event` saw the ticker in `self.positions` and returned lawful
  presence (`live_v4.py:11401-11402`).
- Because the position was still `entry_resting`, `on_bbo_update` did call the
  resting manager (`live_v4.py:12394-12399`).

The manager then signed exactly these returns:

| Return | Count | Input that decided it | Consequence |
|---|---:|---|---|
| `HOLD_CADENCE` | 6 | less than 60 seconds since the 65 post | Return at `13246-13247`; no target organ ran. |
| `HOLD_STAIRCASE_QUIET_FIFO` | 868 | rolling event true-print count below five | Return at `13251-13263`; best-bid mismatch, regime target, window-truth, cohort, and cancel/repost never ran. |
| Volatility trail | 0 | maximum rolling count was two | No callback reached the trail path. |

The exact rolling-count distribution was 772 callbacks with zero prints, 57
with one, and 45 with two. This is the operative answer to “why did it not
respond when the ask came back?” The repost condition was not evaluated. The
`staircase_hold` gate returned first.

## Why NIK had no fourth move

The first three NIK orders came from this sequence:

```text
fresh conception 33 - ATLAS depth 4 = 29
29 becomes marketable-stale at ask 30 -> cancel -> fresh conception 30 - 4 = 26
26 becomes marketable-stale at ask 27 -> cancel -> fresh conception 28 - 4 = 24
24 fills
```

The cancellation rule is `target_bid >= best_ask - 1`
(`live_v4.py:9058-9070`, applied at `13004-13062`). A clean cancellation
untombstones the unfilled position, so the next route is a new conception. It
is not a downward `v4_move_repost` chain.

Fill booking then executes, without an await between check and state write:

```text
pos.entry_qty = filled
pos.entry_filled_ts = time.time()
pos.phase = "active"
```

at `live_v4.py:9777-9787`. After that, each BBO callback follows:

```text
_route_event: ticker is in self.positions -> continue
on_bbo_update: phase != "entry_resting" -> do not call _v4_manage_resting
```

at `live_v4.py:11401-11402` and `12394-12399`.

From the 24 fill through the actual bell:

- 5,534 NIK own-BBO callbacks followed that path;
- 5,387 showed ask <= 24;
- the ask set new lows 27, 26, 24, 23, 19, and 18;
- zero callbacks invoked the entry manager;
- no code computed 23, 19, or 18 as another entry price.

There is therefore no hidden “hold 24 instead of buying 18” authority. The OS
considered the entry complete and moved the leg to exit management. Any fix
that introduces a fourth buy is a re-entry/DCA policy change, not a correction
to the existing entry repricer.

## Post-fill sibling reaction

NIK's fill handler called three sibling organs in order
(`live_v4.py:9832-9840`): exit application, paired-cap/completion handling, and
arrival re-aim. The exact arrival helper is lower-only. It computed
`goal_level = 97 - 24 = 73`, saw the existing VRB 65 was already inside that
ceiling, and returned at `live_v4.py:7290-7293`. It did **not** raise 65.

At the next VRB BBO decision, the book was 73/77, last 76. The normal resting
manager formed a higher supported target, the combined cap allowed at most 73,
and the print-backed `window_truth_reaim` branch signed 73
(`live_v4.py:13501-13600`). The distinction matters:

- pair headroom made 73 lawful;
- the regular BBO manager and print-backed window-truth path made it an action;
- the first-fill arrival helper did not.

The action was causally late. VRB's only 70 print was 206.3 minutes earlier;
after the re-aim, its minimum was 74.

## Fix-regression questions

Every future positioning change should answer these against the frozen rows:

1. At 07:13:58, does VRB-riser information now reach the signer, or is it
   still overwritten by symmetric p50 depth?
2. At each of visits 3-9, does the same receipt still return before inspecting
   recurrence/support? If not, which named evidence authorizes the change?
3. Does any response preserve strict chronology, so the receipt recognizing a
   retouch cannot fill the action it creates?
4. Does a change to VRB positioning leave NIK's filled-leg state law alone?
5. If a proposal changes NIK after 10:39:57, is it honestly named as re-entry
   or DCA rather than disguised as a fourth move?
6. Does the post-fill sibling action distinguish “lawful headroom” from
   “current evidence supports this price”?
7. Does the new trace retain both clocks and name which organ signed and which
   returns were bypassed?

## Machine-readable artifacts

- `.claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_NON_DECISION_LEDGER.csv`
  contains all 6,408 receipt-resolvable non-decisions described here.
- `.claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_VRB_ASK68_VISITS.csv`
  contains the nine visit rows.
- `.claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_SILENCE_CENSUS.json`
  contains conservation counts and source/output hashes.
- `arb-executor/analysis/build_nikvrb_decision_autopsy.js` deterministically
  regenerates those artifacts from the already-frozen dual-book inputs.
