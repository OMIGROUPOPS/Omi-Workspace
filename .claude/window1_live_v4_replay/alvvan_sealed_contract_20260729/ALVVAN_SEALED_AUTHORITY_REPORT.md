# ALVVAN — repaired live_v4, complete VPS dossier

**Result: the field repair worked, sealed authority took the pair, and the pair did not complete.** The OS first posted legacy bids at VAN 22 and ALV 74. Once both bands existed, the repaired sweep recognized those orders as its own, canceled them, and reposted the sealed pair at VAN 16 and ALV 70. The tape lows were VAN 22 and ALV 78. Neither sealed bid filled.

Fill model: **RESTING_TOUCH_FILL_V1 — a resting order fills in full when a later true print or opposite BBO touches or passes its limit. No depth proof and no five-contract gate.**

The transaction-consistent VPS `tennis.db` was present, hash-verified, and opened read-only. It was consulted ten times. Its historical quotes were stale at the replay decision times, so the sharp-FV surface honestly returned `NO-READ: stale_sources`; it cast no orientation or price vote.

## The OS thinking in replay-clock order

### 11:00 PM ET — the evaluator opens

The frozen evaluator window ran from 11:00 PM to the guarded 5:00 AM cutoff. Kalshi's scheduled bell was 7:00 AM. The historical `observed_starts.db` was present and queried under the replay clock, but there was no ALVVAN observation visible in time to replace the schedule.

The OS discovered both legs. It waited for a true print before conceiving an entry.

### 12:46:45 AM — VAN wakes at 26

The first VAN true print was 26. The book was 22 bid for 97 and 26 ask for 587, a four-cent spread. The OS fixed 26 as the Window-1 open.

At 12:47:02 AM, 373 minutes before the scheduled bell, its entry layers said:

- Orientation: ALV was the riser, conviction 1.00, from two votes. The 866-row dog cohort voted ALV riser with a 23.6% historical rise rate; the anchor-role vote also chose the incumbent leader ALV.
- Sharp FV: database present, but every source was stale at this replay time. No vote.
- Cohort: `ATP_CHALL|dog|26_50`, 2,053 rows, median dip 4 cents, 3-cent reach 0.61, 4-cent reach 0.534, rise rate 34.0%. VAN was the faller, so cohort steering changed the preliminary target from 23 to 22.
- Entry table: 22, four cents below the 26 anchor. Expected fill rate 0.585; expected net ROI 17.53%; post-only maker; full runway.
- Atlas: `ATP_CHALL|underdog|26_50`, 1,470 rows, bottom depths 2/4/7 cents at p25/p50/p75. Its p50 aim was 22 and its median bottom time was minute 139.
- Contention: `TRADE-AT-PATH`; best fitted completion probability 63.8% at p75. Its deeper contention aim was 19, but that was diagnostic, not the signer.
- Live-aim library: present, but confidence 0.00, so `NO-OPINION`.
- W1 cohort library: shadow page `ATP_CHALL|26_50|lo`, 587 rows, dip frequency 0.656, depth 4/6/10, median time 78 minutes on its explicitly mis-anchored historical clock. Log only.
- Reach law: at four cents deep on the quiet gauge, fitted one-hour fill probability 0.020. Evidence only.
- Missing fits: range-to-entry, gun-axis cash window, volume path, and wall-versus-theater were named gaps and had no authority.
- Pair cap: the live intended pair was within the 97-cent cap.
- Sizing: the shadow proposed 15 contracts; sizing was not armed. Live quantity stayed five.

The current authority was `LEGACY:path_aim`, so the OS rested five VAN at **22**.

At 12:47:46 AM, 44 seconds after posting, drift/band recognition saw open 26, last 26, net 0, dip 0 and called **B4 flat**. The order was already live, but the repaired authority sweep could now see its canonical `order_id` and `price`.

### 1:05:15 AM — ALV wakes at 79

The first ALV true print was 79. The book was 74 bid for 21 and 79 ask for 1,328, a five-cent spread. The OS fixed 79 as the Window-1 open.

At 1:05:21 AM, 355 minutes before the bell:

- Orientation: ALV remained the riser.
- Sharp FV: database present, but historical sources stale; no vote.
- Cohort: `ATP_CHALL|fav|ge76`, 967 rows, median dip 2, 3-cent reach 0.49, rise rate 38.4%. It was visible in the dossier but barred from steering because ALV was the riser.
- Entry table/staircase: preliminary target 73.
- Atlas: `ATP_CHALL|leader|ge75`, 759 rows, bottom depths 2/5/12. Its p50 aim was 74 and median bottom time was minute 384.
- Contention: best probability 2.4%, below the 8% bar, so it said **DROP**.
- Actual priority: DROP was not an enforced veto in the baseline. The PATH governor had a fitted depth and posted anyway.
- Live-aim library: `NO-OPINION`, confidence 0.00.
- W1 cohort library: shadow page `ATP_CHALL|ge75|lo`, 280 rows, dip frequency 0.714, depth 6/14/37, median time 106 minutes on the caveated clock.
- Reach law: five-cent-depth one-hour fill probability 0.012. Evidence only.
- Pair cap: the posted path pair cleared the 97-cent cap.

`LEGACY:path_aim` rested five ALV at **74**.

At 1:06:04 AM, 43 seconds after posting, drift/band recognition saw open 79, last 79, net 0, dip 0 and called **B6 flat**. The pair classifier now had B4 plus B6 and called **flat_flat**.

The sealed policy then became the price authority:

- VAN B4: open 26 minus sealed depth-p90 10 = **16**.
- ALV B6: open 79 minus sealed depth-p90 9 = **70**.

### 1:07:05–1:08:06 AM — repaired authority takes control

At 1:07:05, the sweep found both legacy bids mismatched with their newly selected sealed prices. It waited for its required second consecutive cycle.

At 1:08:06:

- It canceled VAN 22 and reposted VAN 16, signed `SEAL`.
- It canceled ALV 74 and reposted ALV 70, signed `SEAL`.
- The sweep census recorded two touched orders and 50 contract-cents removed: 6 cents × 5 VAN contracts plus 4 cents × 5 ALV contracts.

There were no foreign-order flags. That is the direct proof that the `order_id`/`price` repair restored ownership.

### What the tape did

- VAN's low was 22 at 1:19:15 AM, eleven minutes after the 22 bid had been canceled. Its frozen-window close was also 22. The sealed 16 bid sat six cents below the tape low.
- ALV's low was 78 at 2:04:07 AM. Its close was 78. The sealed 70 bid sat eight cents below the tape low.
- No sealed order filled. There was no first fill, so no headroom carry, sibling re-aim, exit, walk, or park was triggered.
- The tape-proven combined low inside this evaluator window was 100 cents before fees. This game was not a sub-par pair opportunity inside the guarded window.

The final state at 5:00 AM was two untouched resting sealed bids, VAN 16 plus ALV 70, combined 86 with 11 cents of unused cap headroom, zero filled legs, and no completed pair.

## Decision-layer census

| Layer | Source | State in this replay | What it did |
|---|---|---|---|
| Discovery/book/tape | Frozen BBO and true prints | Present: 2,213 BBO ticks, 10 true prints | Opened both entry evaluations |
| Window clock | Schedule + historical `observed_starts.db` | Present; no timely ALVVAN observed-start row | Used 7:00 AM scheduled bell; evaluator continued to 5:00 AM guard |
| Sharp FV | Verified VPS `tennis.snapshot.db` | Present and read-only; quotes stale at decision time | `NO-READ`, no vote |
| Orientation | Cohort, anchor role, ORIENT, sharp FV | Fitted sources present; two votes available | Called ALV riser |
| Cohort aim | `cohort_surface_v1.json` | Present/fitted | Steered VAN preliminary aim to 22; ALV read but barred as riser |
| Entry table | `entry_tables_sealed_v1.json` | Present/fitted | VAN 22; ALV preliminary 73 |
| Atlas/path | VPS `ATLAS_V1.json` | Present/fitted | Final legacy aims VAN 22, ALV 74 |
| Contention | Atlas contention fields | Present/fitted | VAN trade; ALV DROP, but DROP not enforced |
| Live-aim library | VPS library plus confidence gate | Present, confidence 0.00 | No opinion |
| W1 library | VPS `LIBRARY_V1.json` | Present/fitted; timing caveat retained | Logged only |
| Drift | `drift_surfaces_v1.json` + live tape | Present/fitted | B4 on VAN, B6 on ALV |
| Band taxonomy | `band_map_v1.json` | Present/fitted | Called both legs flat |
| Pair class | Two band states | Present | Called `flat_flat` |
| Sealed authority | `pair_policies_sealed_v1.json` | Present/fitted | Chose VAN 16 / ALV 70 |
| Authority ownership | Canonical order fields in `live_v4` | **Repaired** | Recognized, canceled, and re-anchored both own orders |
| Post/hold/walk/park | Live order/book state | Present | Posted 22/74, re-anchored 16/70, then held; no walk/park trigger |
| Fill/headroom | Resting-touch model + pair cap | Present | No fill; headroom path never activated |
| Range-at-entry | Completion-frame mapping | Unfitted | Named gap; no influence |
| Cash-window | Gun-axis lawful-share fit | Unfitted | Named gap; no influence |
| PM reference | PM feed | Absent | No influence |

Raw artifacts:

- `REPLAY_SUMMARY.json`
- `runs/KXATPCHALLENGERMATCH-26JUL12ALVVAN/trace.json`
