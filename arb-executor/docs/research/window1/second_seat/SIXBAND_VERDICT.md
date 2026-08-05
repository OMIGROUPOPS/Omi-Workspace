# Six-band verdict on the coin flip — the ARNROM method on my own Tier B2 result

Analysis seat only. Read-only; exchange re-pull is the unauthenticated public
`/markets/trades`. Charts + machine verdict:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SIXBAND_VERDICT.json`
and `…/sixband_charts/*.png` (12).

## Setup

12 events sampled from c28fdd28 — **4 flat-book TIES, 4 MISCALLED, 4 CORRECT**, one
category per bucket-cell. For each, the standing autopsy chart (exchange re-pulled
prints + WS-delta rails, both legs, one clock, marks at `call_moment` and the patient
floor). Then, per game, the **full** WS-delta tape between book formation and the
patient floor was scanned on six depth bands — `CROSSED_BID_SIZE`, `LOCK_EPISODES`,
`BID_DEPTH_DOM`, `ASK_DEPTH_DOM`, `ASK_STAIRCASE_DOWN`, `BID_STAIRCASE_UP` — that the
±180 s snapshot counter never saw.

## Per-game verdict

| bucket | game | cat | verdict | bands carrying | first-visible (ET) | lead before floor |
|---|---|---|---|---|---|---:|
| TIE | ARNROM | ATP_CHALL | **VISIBLE·COUNTER_BLIND** | ask-staircase, crossed-bid, locks | 07-13 04:17:42 | 89 min |
| TIE | CARSAN | ATP_MAIN | **VISIBLE·COUNTER_BLIND** | ask-depth-dom, crossed-bid, locks | 07-11 23:01:07 | 345 min |
| TIE | AKSVAL | WTA_CHALL | **VISIBLE·COUNTER_BLIND** | 5 bands (ask+bid staircase, cross, locks, ask-dom) | 07-14 02:12:41 | 476 min |
| TIE | HODYAS | WTA_MAIN | ABSENT (strong·inverted) | chased 90% ask-dom | — | — |
| MISCALL | BARVIS | ATP_CHALL | **VISIBLE·COUNTER_BLIND** | ask-depth-dom | 07-13 17:01:26 | 895 min |
| MISCALL | BUDPEL | ATP_MAIN | ABSENT (strong·inverted) | patient 170 crossed-with-size | — | — |
| MISCALL | BOSKOV | WTA_CHALL | ABSENT (strong·inverted) | both legs 79–100% depth-dom | — | — |
| MISCALL | BLISAS | WTA_MAIN | **VISIBLE·COUNTER_BLIND** | 5 bands | 07-13 15:08:11 | 1332 min |
| CORRECT | FANBIG | ATP_CHALL | VISIBLE | ask+bid staircase, both depth-dom | 07-12 06:19:04 | 282 min |
| CORRECT | MULSHE | ATP_MAIN | VISIBLE | 6 bands | 07-11 23:01:22 | 2901 min |
| CORRECT | SHEVAN | WTA_CHALL | VISIBLE | 6 bands | 07-12 05:20:11 | 398 min |
| CORRECT | KOZIBR | WTA_MAIN | VISIBLE | ask-dom, bid-staircase, cross, locks | 07-11 22:15:31 | 97 min |

## The finding

**Zero of the 8 failures (ties + miscalls) are genuinely flat.** Every one carries a
visible book signature the ±180 s counter at `call_moment` could not see:

- **5 / 8 — SIGNATURE_VISIBLE_COUNTER_BLIND.** A *role-consistent* signature (chased
  side crossing/locking/depth-stacking, patient side ask-staircase/ask-depth) appears
  in the full window, and **every one precedes the patient floor** — leads 89, 345,
  476, 895, 1332 min — so a full-window reader would have called the role in time
  (race-won). ARNROM is the emblem: flat at the 04:07 snapshot, but its
  ask-staircase-down + crossed-bid + lock episodes begin at 04:17, 89 min before ROM's
  floor. The signature is *macro-minutes*, not ±180 s.
- **3 / 8 — SIGNATURE_ABSENT but NOT flat.** HODYAS (chased 90 % ask-depth-dominance),
  BUDPEL (patient 170 crossed-with-size rows), BOSKOV (both legs 79–100 %
  depth-dominant) carry *strong* asymmetries that point *against* my rigid
  band→role map. That indicts the **mapping**, not the book — the structure is loud;
  my label for it was wrong.
- **4 / 4 CORRECT** show rich multi-band signatures (sanity), confirming the bands
  separate roles when read over the full window.

## Rollup decision

> **SIGNAL_DEFINITION_IS_THE_CORPSE — the architecture re-opens.**

The Tier B2 death (54.3 % tie-neutral, "game-row role architecture dead") was a
property of the **reader**, not the data. The role *is* written in the book — on the
crossed-bid, depth-dominance and ask-staircase bands — but a ±180 s snapshot with a
rigid chased/patient mapping is blind to it. 8/8 failures have visible structure; 0 are
flat; the 5 role-consistent ones are all actionable before the floor. The corpse is the
**signal definition** (snapshot window + simplistic mapping). A path-integrated,
full-window, correctly-mapped reader re-opens V30 — and the ceiling above the current
tie-neutral 20 is the prize to re-measure with it.

Same receipts ARNROM first gave us: the book was never silent — the counter was.

## Caveat

12-event sample (4/4/4), not the full corpus; the decision is a direction, not a
recount. The band→role mapping used here is deliberately simple and is itself one of
the things the re-opened architecture must re-specify (the 3 inverted cases are the
evidence it needs work). Charts are supporting; the band scan is the driver.
