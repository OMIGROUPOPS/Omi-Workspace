# THE WALK — VIISAC (20260716) · Viiala/Sach (ITF W)
(C-THE-WALK v1 — the OS answers for itself; account auto-rendered from the logs)

## ① THE ACCOUNT (external → what it said → action taken)
- 08:13:33 AM schedule_match  {"start_time": "2026-07-16T02:00:00-04:00"}
- 03:56:07 PM clock_liar  {}   ← Kalshi's clock lay 6 hours from the honest start
- 04:00:20 PM **consultation SAC** → decision `placed:path_aim` aim=54 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:?() · window_phase:CONS(W1)
- 04:00:24 PM order_placed SAC {"action": "buy", "price": 54, "count": 5} [W1]
- 04:00:24 PM **consultation VII** → decision `placed:path_aim` aim=16 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:?() · window_phase:CONS(W1)
- 04:00:25 PM order_placed VII {"action": "buy", "price": 16, "count": 5} [W1]
- 04:00:25 PM path_mode_hold VII {"held_price": 16, "proposed": 29} [W1]   ← the refused re-aim = the window's exact best
- 04:00:47 PM path_mode_hold SAC {"held_price": 54, "proposed": 65} [W1]
- 06:28:18 PM gun_fired  {"source": "percat_fitted"}  (honest bell 08:00:00 PM)
- 08:24:08 PM w2_fill_violation VII {"fill_price": 16}   ← 24 min past the bell
- 08:24:08 PM entry_filled VII {"fill_price": 16} [W2 gun]
- 08:24:09 PM v4_exit_posted VII {"exit_price": 21} [W2 gun]
- 08:54:29 PM exit_filled VII {"exit_price": 21, "pnl_cents": 25.0} [W2 gun]
- 09:46:23 PM w2_fill_violation SAC {"fill_price": 54}   ← 106 min past the bell, booked via reconcile_adoption
- 09:46:23 PM entry_filled SAC {"fill_price": 54, "source": "reconcile_adoption"} [W2 gun]
- 09:46:23 PM v4_exit_posted SAC {"exit_price": 69} [W2 gun]
- 10:14:10 PM settled SAC {"pnl_cents": -270.0, "settle": "LOSS"}
- 10:14:11 PM order_cancelled SAC {"label": "settlement_cleanup", "success": false} [W2 gun]

**THE CHARGE:** both legs filled W2 on FULLY CASHABLE windows. VII: 5 of 5 window prints cashable, best **29¢ @6:40:59 PM (92.2 sh, band to 35¢ printing after)** — and the 4:00:25 PM hold refused a proposed re-aim of **exactly 29**; the held 16 never traded in W1, survived the bell, and filled 24 minutes into W2 (+25¢ of luck). SAC: 4 of 4 prints cashable, best **68¢ @12:35 PM** — our held 54 (proposed 65 refused) was below anything the window ever printed; the bid survived the bell by **106 minutes**, was booked by `reconcile_adoption` (the fill wasn't even seen live), and settled NO −270¢. What we failed to consult: **window-truth at hold-review on both legs** (the realized floors — 29 and 68 — against held aims of 16 and 54), and the bell sweep left both stale bids alive deep into W2 (the 106-minute SAC survival is the family's worst row in this batch).

## ② THE AMENDMENT (verbalized by the OS — consultation logic, never a ticker-shaped patch)
**Spoken as consultation, by the OS:** "On VII my own path machinery proposed 29 at 4:00:25 PM and my hold refused it; two and a half hours later the tape printed its floor at exactly 29 with ninety shares of size and a cashable band to 35. The window-truth external at hold-review says: the printed reality IS the propose — yield. On SAC the same external says the opposite: the floor is 68, printed once at 12:35 PM with 7 shares; my 54 — and even the proposed 65 — is below anything this window has ever traded; the verdict is not a re-aim, it is 'this bid will never fill lawfully: let the sweep own it at the bell.' And at 8:00 PM the bell external says both remaining bids are OVER — a bid the tape never touched must die before W2 can touch it."

**NO NEW CLASS — two instances of WINDOW-TRUTH BLINDNESS (FOMLIM class) at the hold-review site, one on each leg — with opposite lawful verdicts (re-aim VII / stand-and-sweep SAC), which is the class's own point: the external reads the tape, not a direction.** The 106-minute post-bell survival + reconcile_adoption booking files to **decision ③** (sweep family) with the booking source named per the standard.

## ③ THE PROOF (the game's recorded tape re-run under the amended logic)
| path | fate | grade | $ |
|---|---|---|---|
| ORIGINAL | VII: 16 fills 8:24 PM W2 (violation), exit 21 → +25¢ luck. SAC: 54 fills 9:46 PM W2 via reconcile_adoption (violation), settles NO 28 min later → −270¢ | VII **F(W2-entry)** · SAC **F(W2-entry)** | **−245¢** |
| AMENDED (window-truth at hold-review) | VII: hold yields to the propose (29) → **fills 29¢ @6:40:59 PM inside W1 (92.2 sh)** → band to 35 printed after (5/5 cashable) → **exit ≤35 printable inside W1** → +30¢ lawful. SAC: floor 68 never reaches 54/65 → **REFUSE — lawful pass, never traded that low**; the bell sweep pulls the untouched bid → −270¢ avoided | VII **W1 fill + W1 cash** · SAC **lawful pass** | **+30¢** |
| W2 eliminated on both legs: one converts to a lawful W1 fill-and-cash, one converts to a lawful pass. | | | |

Verdict in window terms: **VII — new fill 29¢ @6:40:59 PM → exit printable inside W1. SAC — REFUSE.** Batch swing on this game: +275¢.

## ④ THE FILING
- **Two instances under WINDOW-TRUTH BLINDNESS (FOMLIM class), hold-review site** — VII (refused propose = the window's exact best) and SAC (held aim below the window's entire printed range).
- **W2-violation rows → decision ③**, SAC's with the booking source named (`reconcile_adoption`, 106 min post-bell — the sweep never owned the bid, the reconciler met the fill after the fact).
- No arming, no patch: SHADOW-FIRST per the class filing; **the operator's word gates any live arming.**
