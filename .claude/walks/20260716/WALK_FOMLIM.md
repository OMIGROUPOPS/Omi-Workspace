# THE WALK — FOMLIM (20260716)
(C-THE-WALK v1 — the OS answers for itself; account auto-rendered from the logs)

## ① THE ACCOUNT (external → what it said → action taken)
- 09:44:39 PM schedule_match  {"start_time": "2026-07-16T05:00:00-04:00"}
- 10:54:21 PM **consultation LIM** → decision `refused:below_leg_floor` aim=None | atlas_page:CONS · reach_law:NOT-(law page absent for ITF_M|quiet) · flow_state:CONS(quiet) · cash_window:CONS(W2-DEPENDENT) · window_phase:CONS(W1)
- 11:21:50 PM **consultation LIM** → decision `placed:path_aim` aim=39 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(warm) · cash_window:CONS(W2-DEPENDENT) · window_phase:CONS(W1)
- 11:21:51 PM order_placed LIM {"action": "buy", "price": 39, "count": 5} [W1]
- 11:21:52 PM **consultation FOM** → decision `placed:path_aim` aim=58 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:CONS(W2-DEPENDENT) · window_phase:CONS(W1)
- 11:21:52 PM order_placed FOM {"action": "buy", "price": 58, "count": 5} [W1]
- 11:22:21 PM path_mode_hold FOM {"held_price": 58, "proposed": 64} [W1]
- 11:23:13 PM gun_fired  {"source": "percat_fitted"}
- 11:24:14 PM clock_liar  {}
- 11:30:33 PM order_cancelled FOM {"label": "match_live_cancel", "success": true} [W2 gun]
- 11:30:43 PM **consultation FOM** → decision `placed:path_aim` aim=78 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(warm) · cash_window:CONS(W2-DEPENDENT) · window_phase:CONS(W2)
- 11:34:26 PM path_mode_hold LIM {"held_price": 39, "proposed": 44} [W2 gun]
- 11:40:36 PM order_cancelled LIM {"label": "v4_cancel_bid_marketable_stale", "success": false} [W2 gun]
- 11:40:39 PM cancel_fill_race LIM {"label": "v4_cancel_bid_marketable_stale", "fill_price": 39}
- 11:40:39 PM w2_fill_violation LIM {"fill_price": 39}
- 11:40:39 PM entry_filled LIM {"fill_price": 39, "source": "manage_cancel_race"} [W2 gun]
- 11:40:42 PM order_placed LIM {"action": "sell", "price": 47, "count": 5} [W2 gun]
- 11:40:42 PM v4_exit_posted LIM {"exit_price": 47} [W2 gun]
- 11:45:45 PM exit_filled LIM {"exit_price": 47, "pnl_cents": 40.0} [W2 gun]

## ② THE AMENDMENT (verbalized by the OS — consultation logic, never a ticker-shaped patch)
**Spoken as consultation, by the OS:** "At 10:54 PM the tape's W1 low was 7¢ (printed 10:54:04, five thin prints in the whole window) and my machinery was refusing LIM outright — 27 consecutive below-floor refusals from 10:54 to 11:20, because the page's fitted depth priced my aim under the nickel, while the reach law answered NOT-APPLICABLE (no page exists for ITF_M|quiet). A **WINDOW-TRUTH external** — the tape's realized W1 low, the SIZE at that low, and my distance from it, consulted at every placement, hold-review, and cancel decision — would have said at 10:54: 'the printed reality is 7 on five thin prints; there is no size there; the lawful verdict is HOLD THE CAST, not chase the page's 39 after the rise.' And at 11:34 PM, with the gun eleven minutes fired and my 39 bid still resting, the same external at fill-decision time would have said: 'the window is OVER — pull now,' six minutes before the marketable-stale race lost."

**NO EXISTING EXTERNAL SUPPLIES EITHER READING — THE MISSING EXTERNAL IS THE FINDING:** the atlas prices from discovery (not the printed low); the reach law had no page for the bucket; nothing consults the tape's realized window low or its size at hold-review; and the post-gun pull decision consulted no window-truth at all (LIM's cancel came via marketable-stale at 11:40, not match_live — a 17-minute sweep gap on the sibling leg, second observable filed).

## ③ THE PROOF (the game's recorded tape re-run under the amended logic)
Tape re-run (exchange truth, size-aware fill law):
| path | fate | grade | $ |
|---|---|---|---|
| ORIGINAL | 39¢ bid rested through the gun; W2 fill 11:40:39 PM (17 min post-bell, cancel-fill race lost); exit 47¢ 11:45 PM; **LIM settled NO after the cash** | **F(W2-entry)** | +40¢ (double luck: unlawful fill AND pre-collapse exit on a leg that died) |
| AMENDED (window-truth) | aim ≤12 from the 10:54 consultation: **NEVER FILLS — the 7¢ was five thin prints, cumulative size at ≤12 after the consult never reached 5 shares** ("never traded that low at size"); the 39 bid pulls at gun+grace 11:28 → no W2 fill | **lawful pass (no trade)** | 0¢ — forgoes the +40¢ luck; the CLASS the amendment kills ran −333¢ pooled across 92 W2 fills (three-day replay) |

The corrected fate is NO TRADE, and that is the right answer: the amendment does not manufacture the 7¢ fill (the tape never offered size there); it prevents the unlawful one. The instance paid; the class bleeds; the class is the verdict.

## ④ THE FILING
- **NEW-CLASS #1 (this walk): WINDOW-TRUTH BLINDNESS** — filed in CLASS_LEDGER: no consultation reads the tape's realized window low + size at decision time (placement, hold-review, cancel). SHADOW-FIRST: the external ships as a dossier surface + logs would-have-said lines before it ever moves an aim; **the operator's word gates any live arming.**
- **Instance filed under the sweep family: the 17-minute sibling sweep gap** (gun 11:23 → FOM cancelled 11:30 → LIM's first cancel attempt 11:40 via marketable-stale, lost to the fill race) — evidence to decision ③ (the dial-walk clock question), not patched here.
- OPEN_LEDGER updated same push; this walk is the protocol's founding exhibit.
