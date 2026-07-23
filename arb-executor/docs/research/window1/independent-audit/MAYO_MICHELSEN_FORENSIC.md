# Mayo / Michelsen Forensic — KXATPCHALLENGERMATCH-26JUL21MICMAY (CC, evidence only)

Reconstructed from byte-pinned engine logs. Order/client identities masked. Times ET (UTC-4).
MICMAY is Jul-21 (outside D=804 Jul12-20); analyzed as the real-start failure exemplar.

| Time (ET) | Time (UTC) | Event | Leg | Detail (ids masked) |
|---|---|---|---|---|
| ~19:00 | ~23:00 | REAL MATCH START | — | P0-established; fill at 19:37 confirms in-play |
| 19:36:19 | 23:36:19Z | order_placed | MAY (Mayo) | resting, oid=«A» coid=«a» |
| 19:36:21 | 23:36:21Z | order_placed | MIC (Michelsen) | resting, oid=«B» coid=«b» |
| 19:36:21 | 23:36:21Z | window_open_set | both | entry window opened (already ~36m post real start) |
| 19:37:30 | 23:37:30Z | entry_filled | MAY | **5 @ 85¢, kalshi_status=adopted — POST-START FILL (~37m after start)** |
| 19:37:31 | 23:37:31Z | order_placed | MAY | re-post, oid=«C» coid=«c» |
| 22:01:12 | Jul22 02:01:12Z | order_cancelled | MIC | `gun_fire_sweep` success=true, then `match_live_cancel` success=false (already gone) — swept at FALSE 22:00 schedule |
| 18:54:16(+1) | Jul22 18:54:16Z | order_cancelled | MAY | re-post oid=«C» `settlement_cleanup` success=false (rested to settlement) |

**Findings**
- Schedule the bot used: **22:00 ET** (from `expected_expiration_time`), ~3h later than the real ~19:00 ET start.
- Detector/live latch: gun latched ~22:01 ET (~3h late); `phantom_bell_void` suppressed the real bell.
- Did an order survive/fill after real start? **Yes** — Mayo filled 37 min post-start; the Mayo re-post rested until settlement.
- Responsible code path: `event_kalshi_occ` derived from `expected_expiration_time` + `phantom_bell_void` real-bell suppression → start-gate anchored on the false 22:00 schedule, permitting post-start entry. Matches the P0 real-start-entry-guard defect (fix candidate `a4996dd0`). Evidence only; no live fix.
