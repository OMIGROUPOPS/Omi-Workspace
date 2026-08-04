# Independent close audit and the joint achievable ceiling

Analysis seat only. Descriptive. Read-only on every input. Independent of the
replay: closes recomputed directly from the raw true-print tape
`OMI-Window1-private/fit-local/prints.jsonl` (4.84M prints), not from any replay
close field. Window edges (`guarded_left_ts`/`guarded_right_ts`) and the replay
close used only for comparison. Per-leg rows in `INDEPENDENT_CLOSE_AUDIT_1608.csv`;
all numbers in `CLOSE_AUDIT_AND_JOINT_CEILING_SUMMARY.json`.

## 1. Independent close audit — all 1,608 legs

Close = last true print inside the guarded window `[left, right]`, with its
timestamp, aggressor (`taker_side`: yes = buyer lifted the ask, no = seller hit
the bid), and distance from the right edge.

### Agreement with the replay closes

| class | legs |
|---|---:|
| **AGREE** (both present, equal) | **1301** |
| DIFFER (both present, differ) | 6 |
| replay close null, audit recovers a real print | 250 |
| no in-window true print at all (close undefined) | 51 |

The independent audit **reproduces the replay close on 1301 of 1307 comparable
legs (99.5%)**. The 6 that differ do so by 1-2¢: LUZTAB-TAB 92/93, VANFAR-FAR
64/65, ROCMAR-ROC 56/58, KABPER-KAB 71/73, CARVON-VON 24/25, FERREN-REN 16/15
(mine/replay). On 250 legs the replay left the close null and the raw tape
carries a genuine in-window print; 51 legs never printed in-window. (My raw
lawful-print count matches the replay's on 1401/1608; the residual is
corridor-censoring and does not move the close value.) **The replay closes are
sound.**

### Closes print early and thin

- **601 of 1557 audited closes (38.6%) print more than 5 minutes before the
  window's right edge** — 228 more than 30 minutes early, **133 more than an hour
  early**, the extreme 7.5 hours. Median distance from the right edge is 164s but
  the p90 is ~49 minutes. The "close" is frequently a stale last-trade, not a
  price struck at the window edge.
- Close aggressor: **1365 buyer-aggressed** (last trade lifted the ask), **192
  seller-aggressed** (hit the bid). The recorded close is a lift, not a hit, ~7:1.

### Close-sum distribution per category (events with both legs audited)

| category | n | min | p25 | median | p75 | max | close-sum < 100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | 357 | 97 | 101 | 101 | 102 | 109 | 11 |
| ATP_MAIN | 141 | 99 | 101 | 101 | 102 | 104 | 2 |
| WTA_MAIN | 141 | 99 | 101 | 101 | 102 | 103 | 3 |
| WTA_CHALL | 134 | 81 | 100 | 101 | 102 | 108 | 7 |

Close sums cluster at **101** (the two sides' closes carry ~1¢ of book vig). Only
**23 events** have a close sum already below 100 on the tape — the market itself
rarely priced the pair under par at the close.

## 2. Joint achievable ceiling — against the audited closes

The completable set the 75% target actually plays against: events where **both**
maker floors sit **strictly below that leg's own audited close** (a real discount
on each side) **and** the two maker floors **sum below 100** (a completed pair
under par). `maker_floor = min(qualifying_ask_floor, seller_aggressed_traded_low)`
per the residency ruling. Computed over the **773** events with both legs audited.

| frontier tier | qualifying events | of ~804 games |
|---|---:|---:|
| ≤ 93 | 59 | 7.3% |
| ≤ 95 | 104 | 12.9% |
| ≤ 97 (par) | **217** | **27.0%** |
| < 100 | **390** | **48.5%** |

**The ceiling caps the achievable completion rate at ~48.5% (<100) and ~27% at
par.** A 75% target is arithmetically unreachable against this denominator — even
if every reachable pair were captured, both legs discounted and summed under par,
the rate tops out near half the book at <100 and near a quarter at par.

### Ceiling by category × region (tier < 100)

| category | le25 | 26_50 | 51_75 | ge76 | total |
|---|---:|---:|---:|---:|---:|
| ATP_CHALL | 31 | 67 | 68 | 18 | 184 |
| ATP_MAIN | 8 | 40 | 34 | 10 | 92 |
| WTA_MAIN | 20 | 24 | 18 | 13 | 75 |
| WTA_CHALL | 7 | 11 | 14 | 7 | 39 |

### Ceiling by tier × category

| tier | ATP_CHALL | ATP_MAIN | WTA_MAIN | WTA_CHALL | total |
|---|---:|---:|---:|---:|---:|
| ≤ 93 | 27 | 16 | 7 | 9 | 59 |
| ≤ 95 | 45 | 34 | 14 | 11 | 104 |
| ≤ 97 | 99 | 68 | 35 | 15 | 217 |
| < 100 | 184 | 92 | 75 | 39 | 390 |

ATP_CHALL carries the ceiling (184 of 390 under-100, 99 of 217 at par); the mid
regions (26_50, 51_75) dominate within each category. The 31 events not counted
here lack a both-legs audited close (one side never printed in-window) and are
undetermined, not excluded on price.

## Artifacts

Under `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/`:
`INDEPENDENT_CLOSE_AUDIT_1608.csv` (per-leg audited close, timestamp, aggressor,
distance-from-edge, divergence class, early flag) and
`CLOSE_AUDIT_AND_JOINT_CEILING_SUMMARY.json` (all tables).
