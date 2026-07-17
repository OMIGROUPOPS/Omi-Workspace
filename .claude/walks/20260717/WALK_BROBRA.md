# THE WALK — BROBRA (20260717) · walk batch 2, FOUNDING CHARGE (operator-flagged; the floor's founding exhibit)
(C-THE-WALK v1 — account auto-rendered from the logs; charge as dispatched)

## ① THE ACCOUNT (external → what it said → action taken)
- 05:14:37 PM schedule_match  {"start_time": "2026-07-17T11:00:00-04:00"}
- 05:16:06 PM clock_liar  {}
- 01:01:47 AM **consultation BRA** → decision `placed:path_aim` aim=60 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:CONS(W2-DEPENDENT) · window_phase:CONS(W1)
- 01:01:52 AM order_placed BRA {"action": "buy", "price": 60, "count": 5} [W1]
- 01:01:57 AM **consultation BRO** → decision `placed:path_aim` aim=18 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:CONS(W2-DEPENDENT) · window_phase:CONS(W1)
- 01:02:07 AM order_placed BRO {"action": "buy", "price": 18, "count": 5} [W1]
- 01:02:07 AM path_mode_hold BRA {"held_price": 60, "proposed": 70} [W1]
- 01:05:18 AM order_cancelled BRA {"label": "v4_move_repost", "success": true} [W1]
- 01:05:20 AM order_placed BRA {"action": "buy", "price": 32, "count": 5} [W1]
- 01:11:46 AM path_mode_hold BRA {"held_price": 32, "proposed": 34} [W1]
- 01:14:29 AM path_mode_hold BRO {"held_price": 18, "proposed": 27} [W1]
- 01:41:23 AM order_cancelled BRA {"label": "v4_cancel_bid_marketable_stale", "success": false} [W1]
- 01:41:24 AM cancel_fill_race BRA {"label": "v4_cancel_bid_marketable_stale", "fill_price": 32}
- 01:41:24 AM entry_filled BRA {"fill_price": 32, "source": "manage_cancel_race"} [W1]
- 01:41:24 AM gun_fired  {"source": "percat_fitted"}
- 01:41:24 AM v4_exit_posted BRA {"exit_price": 39} [W2 gun]
- 01:46:33 AM order_cancelled BRO {"label": "match_live_cancel", "success": true} [W2 gun]

**THE CHARGE (as dispatched, three counts):**
1. **THE FLOOR NEVER SPOKE.** KXITFWMATCH-26JUL17BROBRA carries **66.0 shares of lifetime volume against the 1,500 floor** — and no floor-consult line exists in the account because the conception entered in **W1 phase and the floor's check lived inside `if phase == "CORRIDOR" or stale_date`** (the site-scoped implementation). The receipt the operator asked for is the census: **463 non-corridor ITF conceptions since 07-15, 25 under 1,500 lifetime even now (exact lower bound; all W1-phase), −125¢ realized on the 3 settled so far (MASDUT −155 among them), 22 still open** — BROBRA is the founding exhibit and P3 moves the floor to the conception chokepoint, pair-level, all phases, number untouched.
2. **THE +4-OVER-CELL GAP (named as its own class question):** BRA filled **5×32¢ at 1:41:24 AM** (a lost marketable-stale cancel race, seconds before the gun) — the live conception cell sat at 32 while the shadow brain's fill-estimate aim was **28**. **Why does the live cell sit ABOVE the shadow's number?** Filed as a class question (LIVE-CELL-OVER-SHADOW) — the two brains price the same leg 4¢ apart and the expensive one is live.
3. **BRO: THE RECALIBRATION READ, EXECUTED-NOT-TAKEN (exhibit #8 → decision ⑮):** BRO rested at 18 while the window printed **54–77**; the honest reprice computed to **54, inside its own bound of 65 — and was not taken**; the bid died to the bell sweep at 1:46:33 AM having never been within 36¢ of a print. The window-truth external (⑮) is the consultation that takes that reprice or refuses it BY NAME.

## ② THE AMENDMENT (verbalized by the OS — consultation logic, never a ticker-shaped patch)
**Spoken as consultation, by the OS:** "At conception, 1:01 AM, the volume external says 66 lifetime shares against a 1,500 floor: this book cannot pay either leg — REFUSE THE EVENT, both legs, by name. That consultation now exists at the chokepoint (P3). Had the pair lawfully existed anyway: at 1:14 AM BRO's hold-review, the window-truth external reads prints 54–77 against my 18 and my own reprice math saying 54 ≤ bound 65 — take the reprice or refuse it by name; silence is the defect."

## ③ THE PROOF (replay in window terms)
| path | fate | $ |
|---|---|---|
| ORIGINAL | BRA fills 32 W1 (cancel race lost, gun same second); BRO never within 36¢ of the tape, swept 1:46 AM; pair one-sided on a 66-share book | open (basis risk live) |
| AMENDED (floor at conception) | **EVENT REFUSED at 1:01 AM — below_discovery_floor_refused, both legs, volume 66 logged.** No fill, no one-sided book, no dead-book exit risk (the never-wake probe priced this class: sub-floor ITF = the book that can't pay when you're right) | 0 |

## ④ THE FILING
- **FOUNDING EXHIBIT: P3 FLOOR-AT-CONCEPTION** (deployed this push; the bypass census is the operator's 5th-ask answer).
- **NEW CLASS QUESTION: LIVE-CELL-OVER-SHADOW** — live conception cell 32 vs shadow fill-est 28 on the same leg at the same instant; the divergence audit owes the mechanism.
- **EXHIBIT #8 → decision ⑮ (window-truth):** BRO's computed-but-untaken reprice (54, inside bound 65, vs prints 54–77).
- **SITE-SCOPED LAW instance 3** (the floor's corridor-only site) — class founded this push in CLASS_LEDGER.
