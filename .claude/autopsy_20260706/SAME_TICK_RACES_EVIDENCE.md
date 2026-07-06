# SAME-TICK RACE EVIDENCE — the 6 pre-basis races + the KEYNOS grace orphan (raw rows)

Read-only evidence pull (2026-07-06 17:47 ET). Sources: bot session log (order/cancel/fill rows with oids), exchange /fills (created_time per fill), the 07-06 deep-cut joins. Every row below is a log or exchange line, not prose.

## ITFWMATCH-26JUL06DZJMCK — over-goal by +2¢ (bound 20)
- leg-1 JMCK-DZJ 77c @03:38:19 · leg-2 JMCK-MCK 22c @03:38:20 · **gap 0.9s** · leg-2 resting at leg-1 fill: 22¢
  - EXCHANGE: UL06DZJMCK-DZJ buy 77¢ ×5.00 @ 07:38:03.259Z order 454d9173 taker=False
  - EXCHANGE: UL06DZJMCK-MCK buy 22¢ ×5.00 @ 07:38:07.498Z order 7b0f5e2a taker=False
  - LOG 03:38:20 order_placed UL06DZJMCK-DZJ: {"price": 96, "action": "sell", "order_id": "45e77e60-11bd-4430-ae8d-981f3d10dfbe"}
  - LOG 03:38:20 v4_exit_posted UL06DZJMCK-DZJ: {"order_id": "45e77e60-11bd-4430-ae8d-981f3d10dfbe", "qty": 5}
  - LOG 03:38:20 completion_no_attempt UL06DZJMCK-DZJ: {}
  - LOG 03:38:20 order_cancelled UL06DZJMCK-MCK: {"order_id": "7b0f5e2a-a1a5-44e0-af4d-4c2e769f2a81", "success": false, "label": "reaim_sibling_lower"}
  - LOG 03:38:20 entry_filled UL06DZJMCK-MCK: {"fill_price": 22, "qty": 5}
  - LOG 03:38:20 join_queue UL06DZJMCK-MCK: {}
  - LOG 03:38:20 order_placed UL06DZJMCK-MCK: {"price": 28, "action": "sell", "order_id": "35e2f544-7aa0-4f48-85ab-55237b1776b4"}
  - LOG 03:38:20 v4_exit_posted UL06DZJMCK-MCK: {"order_id": "35e2f544-7aa0-4f48-85ab-55237b1776b4", "qty": 5}
  - between-fills: 03:38:20 order_cancelled

## WTACHALLENGERMATCH-26JUL06HERNGU — over-goal by +1¢ (bound 57)
- leg-1 RNGU-HER 40c @05:09:22 · leg-2 RNGU-NGU 58c @05:09:22 · **gap 0.4s** · leg-2 resting at leg-1 fill: 58¢
  - EXCHANGE: UL06HERNGU-NGU buy 58¢ ×5.00 @ 09:08:55.507Z order 6caf44f2 taker=False
  - EXCHANGE: UL06HERNGU-HER buy 41¢ ×5.00 @ 09:09:14.712Z order cd8927ce taker=False
  - LOG 05:13:12 v4_repost_hold_same_price UL06HERNGU-HER: {}
  - LOG 05:13:28 leg2_reshuffle_reaim UL06HERNGU-HER: {}
  - LOG 05:13:36 leg2_reshuffle_reaim UL06HERNGU-HER: {}
  - LOG 05:13:36 leg2_reshuffle_reaim UL06HERNGU-HER: {}
  - LOG 05:13:43 leg2_reshuffle_reaim UL06HERNGU-HER: {}
  - LOG 05:13:43 leg2_reshuffle_reaim UL06HERNGU-HER: {}
  - LOG 05:13:43 leg2_reshuffle_reaim UL06HERNGU-HER: {}
  - LOG 05:14:12 leg2_reshuffle_reaim UL06HERNGU-HER: {}
  - between-fills: 05:09:22 order_cancelled

## ATPCHALLENGERMATCH-26JUL06ERHSIN — over-goal by +3¢ (bound 1)
- leg-1 HSIN-ERH 96c @06:40:20 · leg-2 HSIN-SIN 4c @06:40:21 · **gap 0.8s** · leg-2 resting at leg-1 fill: 4¢
  - EXCHANGE: UL06ERHSIN-SIN buy 4¢ ×5.00 @ 10:37:57.298Z order 33904aaf taker=False
  - EXCHANGE: UL06ERHSIN-ERH buy 96¢ ×5.00 @ 10:39:25.471Z order 9c994c48 taker=False
  - LOG 06:41:37 exit_filled UL06ERHSIN-ERH: {"qty": 5}
  - LOG 06:41:37 scalp_filled UL06ERHSIN-ERH: {}
  - LOG 06:42:29 order_placed UL06ERHSIN-ERH: {"price": 91, "action": "buy", "order_id": "53ef1fb0-2c12-44c2-9d49-44f3c3050ca7"}
  - LOG 06:42:29 sibling_repost_placed UL06ERHSIN-ERH: {}
  - LOG 06:42:41 leg2_reshuffle_reaim UL06ERHSIN-ERH: {}
  - LOG 06:42:41 order_cancelled UL06ERHSIN-ERH: {"order_id": "53ef1fb0-2c12-44c2-9d49-44f3c3050ca7", "success": true, "label": "v4_move_repost"}
  - LOG 06:42:42 order_placed UL06ERHSIN-ERH: {"price": 93, "action": "buy", "order_id": "6876d2bb-a312-4b12-b34c-594cdcb510d2"}
  - LOG 06:42:42 v4_move_repost UL06ERHSIN-ERH: {}
  - between-fills: 06:40:21 order_cancelled

## WTACHALLENGERMATCH-26JUL06HESPAL — over-goal by +5¢ (bound 64)
- leg-1 SPAL-HES 33c @06:55:42 · leg-2 SPAL-PAL 69c @06:55:43 · **gap 0.8s** · leg-2 resting at leg-1 fill: 69¢
  - EXCHANGE: UL06HESPAL-PAL buy 69¢ ×5.00 @ 10:55:02.494Z order 2a4d9a2b taker=False
  - EXCHANGE: UL06HESPAL-HES buy 33¢ ×5.00 @ 10:55:24.544Z order 73248a39 taker=False
  - LOG 06:55:42 order_placed UL06HESPAL-HES: {"price": 40, "action": "sell", "order_id": "6eb8a053-a48f-4a4d-8540-38c5c5ba74a2"}
  - LOG 06:55:42 v4_exit_posted UL06HESPAL-HES: {"order_id": "6eb8a053-a48f-4a4d-8540-38c5c5ba74a2", "qty": 5}
  - LOG 06:55:42 order_cancelled UL06HESPAL-PAL: {"order_id": "2a4d9a2b-0d04-4c9b-9a87-8a77e474a5ec", "success": false, "label": "reaim_sibling_lower"}
  - LOG 06:55:43 entry_filled UL06HESPAL-PAL: {"fill_price": 69, "qty": 5}
  - LOG 06:55:43 order_placed UL06HESPAL-PAL: {"price": 87, "action": "sell", "order_id": "41c498b2-d86a-494a-8dd8-3ab0bde56d8f"}
  - LOG 06:55:43 v4_exit_posted UL06HESPAL-PAL: {"order_id": "41c498b2-d86a-494a-8dd8-3ab0bde56d8f", "qty": 5}
  - LOG 06:57:28 exit_filled UL06HESPAL-HES: {"qty": 5}
  - LOG 06:57:28 scalp_filled UL06HESPAL-HES: {}
  - between-fills: 06:55:42 order_cancelled

## ITFMATCH-26JUL06DUHCAR — over-goal by +3¢ (bound 9)
- leg-1 HCAR-DUH 88c @07:06:48 · leg-2 HCAR-CAR 12c @07:06:49 · **gap 0.9s** · leg-2 resting at leg-1 fill: 12¢
  - EXCHANGE: UL06DUHCAR-CAR buy 12¢ ×5.00 @ 11:06:16.006Z order 21321951 taker=False
  - EXCHANGE: UL06DUHCAR-DUH buy 88¢ ×5.00 @ 11:06:25.965Z order cd72d9ce taker=False
  - LOG 07:06:49 order_placed UL06DUHCAR-DUH: {"price": 98, "action": "sell", "order_id": "7d6f074a-132d-463c-8e87-d10773615a56"}
  - LOG 07:06:49 v4_exit_posted UL06DUHCAR-DUH: {"order_id": "7d6f074a-132d-463c-8e87-d10773615a56", "qty": 5}
  - LOG 07:06:49 completion_no_attempt UL06DUHCAR-DUH: {}
  - LOG 07:06:49 order_cancelled UL06DUHCAR-CAR: {"order_id": "21321951-381c-4664-abbd-8046c322b80f", "success": false, "label": "reaim_sibling_lower"}
  - LOG 07:06:49 entry_filled UL06DUHCAR-CAR: {"fill_price": 12, "qty": 5}
  - LOG 07:06:49 join_queue UL06DUHCAR-CAR: {}
  - LOG 07:06:49 order_placed UL06DUHCAR-CAR: {"price": 16, "action": "sell", "order_id": "7df5fb63-d22a-44e9-900e-ad1f22c26b9a"}
  - LOG 07:06:49 v4_exit_posted UL06DUHCAR-CAR: {"order_id": "7df5fb63-d22a-44e9-900e-ad1f22c26b9a", "qty": 5}
  - between-fills: 07:06:49 order_cancelled

## WTACHALLENGERMATCH-26JUL06BASBAD — over-goal by +2¢ (bound 72)
- leg-1 SBAD-BAS 25c @09:50:54 · leg-2 SBAD-BAD 74c @09:50:55 · **gap 0.7s** · leg-2 resting at leg-1 fill: 74¢
  - EXCHANGE: UL06BASBAD-BAS buy 25¢ ×5.00 @ 13:48:24.249Z order cd9ccfd8 taker=False
  - EXCHANGE: UL06BASBAD-BAD buy 74¢ ×5.00 @ 13:48:52.610Z order 318cf267 taker=False
  - LOG 09:50:54 completion_booking_adoption UL06BASBAD-BAS: {"qty": 5}
  - LOG 09:50:54 entry_filled UL06BASBAD-BAS: {"fill_price": 25, "qty": 5}
  - LOG 09:50:55 order_placed UL06BASBAD-BAS: {"price": 31, "action": "sell", "order_id": "f1630bb2-8b90-4f4f-95ec-1cb66accec90"}
  - LOG 09:50:55 v4_exit_posted UL06BASBAD-BAS: {"order_id": "f1630bb2-8b90-4f4f-95ec-1cb66accec90", "qty": 5}
  - LOG 09:50:55 order_cancelled UL06BASBAD-BAD: {"order_id": "318cf267-95c4-4496-ab21-f61630b31a71", "success": false, "label": "reaim_sibling_lower"}
  - LOG 09:50:55 entry_filled UL06BASBAD-BAD: {"fill_price": 74, "qty": 5}
  - LOG 09:50:55 order_placed UL06BASBAD-BAD: {"price": 92, "action": "sell", "order_id": "6bce58d0-b616-4763-89e9-fe1523bf0d12"}
  - LOG 09:50:55 v4_exit_posted UL06BASBAD-BAD: {"order_id": "6bce58d0-b616-4763-89e9-fe1523bf0d12", "qty": 5}
  - between-fills: 09:50:55 order_cancelled

## KXWTAMATCH-26JUL06KEYNOS — the grace orphan (duplicate-writer family, NOT a same-tick race)
- LOG 08:12:28 order_cancelled 5b01cd6e success=true label=reaim_sibling_lower
- LOG 08:12:34 order_placed KEY buy 54¢ order **e71a32af** (placed by reaim_sibling_arrival; pos re-keyed)
- LOG 08:12:49 order_placed KEY buy 54¢ order **98afdab4** (sibling_repost_placed off the PASS-START ord_map snapshot — the duplicate; entry_order_id overwritten → e71a32af ORPHANED)
- LOG 10:50:26 match_live_detected · 10:50:27 grace armed 300s · 10:56:01 order_cancelled **98afdab4** success=true label=match_live_cancel (the TRACKED twin)
- EXCHANGE 15:12:42Z (11:12:42 ET): KEYNOS-KEY buy 54¢ ×5 order **e71a32af** — the orphan filled 22.3min past latch. Pair completed 43+54=97; grace machinery itself clean.

## LOOP-CHECK — which previous failure is each closer secretly? (the graves, named)

| candidate closer for the 6 pre-basis races | the grave it secretly is | verdict |
|---|---|---|
| pre-fill combined veto on resting pairs | **June-12 paired_cap** (naked-single manufacture; residue struck 3×; BANNED lineage) — and now also the 2¢-ruling's banned per-leg-conditional class | DEAD-IN-DRAFT |
| a second watcher that pulls one leg when the other's fill is detected faster | **pair_governor** (06-29 SUMTAK: a second writer racing the loop; serialization one-post-per-leg-per-tick NEVER built) | DEAD-IN-DRAFT without the serialization it never had |
| joint model: both bids priced from ONE read (pair as one state) | not a grave — the 2¢-ruling's own dissolution path | the sanctioned closer; BLOCKED-ON-DATA (coverage trigger) |

KEYNOS family: the reaim×sibling-repost duplicate is P4-GUARDED since 12:15 (in-memory in-flight check; 0 occurrences post-guard); the residual reaim×walk PLACE-AWAIT micro-window is P2b-logged (`move_repost_ownership_abort`), 0 firings — the full serialization design stays parked behind the §4H no-cancel-rework lock (pair_governor grave precondition, unbuilt by order).

Bounded exposure restated from the ledger: the 6 races cost +1..+5¢ cushion each on 5-lots (≈$1.10 total basis-over-goal); KEYNOS pair completed at 97 and sits in the open book.