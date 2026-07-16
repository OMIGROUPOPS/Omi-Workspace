# THE WALK — FEISAM (20260716) · Samson/Feistel (WTA CHALL)
(C-THE-WALK v1 — the OS answers for itself; account auto-rendered from the logs)

## ① THE ACCOUNT (external → what it said → action taken)
- 06:23:45 PM schedule_match  {"start_time": "2026-07-16T09:10:00-04:00"}
- 06:23:50 PM clock_liar  {}
- 02:31:22 AM **consultation SAM** → decision `placed:path_aim` aim=64 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:GAP(no fitted gun-axis lawful_share for this) · window_phase:CONS(W1)
- 02:31:23 AM order_placed SAM {"action": "buy", "price": 64, "count": 5} [W1]
- 02:31:24 AM **consultation FEI** → decision `placed:path_aim` aim=30 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:GAP(no fitted gun-axis lawful_share for this) · window_phase:CONS(W1)
- 02:31:24 AM order_placed FEI {"action": "buy", "price": 30, "count": 5} [W1]
- 02:33:20 AM path_mode_hold FEI {"held_price": 30, "proposed": 33} [W1]
- 06:25:44 AM path_mode_hold SAM {"held_price": 64, "proposed": 65} [W1]
- 06:26:05 AM order_cancelled SAM {"label": "v4_cancel_bid_marketable_stale", "success": false} [W1]
- 06:26:05 AM cancel_fill_race SAM {"label": "v4_cancel_bid_marketable_stale", "fill_price": 64}
- 06:26:05 AM entry_filled SAM {"fill_price": 64, "source": "manage_cancel_race"} [W1]
- 06:26:06 AM order_placed SAM {"action": "sell", "price": 79, "count": 5} [W1]
- 06:26:06 AM v4_exit_posted SAM {"exit_price": 79} [W1]
- 06:26:06 AM order_cancelled FEI {"label": "completion_reprice", "success": true} [W1]
- 06:27:39 AM gun_fired  {"source": "fallback_bell"}  (honest bell 06:29:57 AM)
- 08:12:37 AM settled SAM {"pnl_cents": -320.0, "settle": "LOSS"}
- 08:12:40 AM order_cancelled SAM {"label": "settlement_cleanup", "success": false} [W2 gun]

**THE CHARGE:** we bought the leg the window PROVED uncashable and killed our bid on the leg the window proved cashable, one second apart. SAM: our fill 64¢ @6:26:05 AM (a LOST marketable-stale cancel race) against a window whose best print was 50¢ @6:29:22 AM — and worse than the price: **REFUSE-AT-EVERY-PRICE — of 56 W1 prints, no entry at ANY price ever saw entry+band print after it (size-aware); the leg was uncashable at all entries**; the exit posted at 79 was a wish; settled NO −320¢. FEI: 16 of 16 window prints cashable, best 31¢ @6:25:27 AM with band to 38¢ printing after and 4,719 shares of size at ≤best — our 30 bid sat one cent below the printed floor (the 2:33 AM hold refused the proposed 33 that would have owned it), and at 6:26:06 AM — one second after SAM's fill — `completion_reprice` CANCELLED it and nothing ever re-placed it. What we failed to consult: **cashability** — the cash_window stamp said GAP by its own admission and both placements proceeded anyway; window-truth at the 6:25:44 hold-review (a whole session of tape saying SAM had no cashable structure); and sibling cashability at completion-reprice, which consults sibling ACCOUNTING and never asks which side the tape says can cash.

## ② THE AMENDMENT (verbalized by the OS — consultation logic, never a ticker-shaped patch)
**Spoken as consultation, by the OS:** "At 6:25:44 AM, holding SAM at 64 against a proposed 65, the WINDOW-TRUTH external reads the session's whole tape: 56 prints and not one entry — at any price — ever printed its band after it. This leg is refuse-at-every-price; the lawful verdict is PULL, not hold. The same external on FEI reads the mirror: every print cashable, floor 31 with band to 38 and four thousand shares of size — the pair's cashable side is FEI. Work FEI at the printed floor (the 33 the hold refused at 2:33 AM is already the right number), and when SAM's fill triggers completion-reprice, the CASHABILITY consult refuses the cancel: never take down the side the tape says can cash to fund completion on the side it says cannot."

**THE MISSING EXTERNALS:** (a) window-truth cashability per leg — cash_window is a fitted PRIOR and stamped itself GAP here; nothing reads the realized tape's cashable structure at placement or hold-review (the FOMLIM class, at a second decision site). (b) **sibling cashability at completion-reprice — NO existing external supplies it**: completion prices from the sibling's accounting (basis/ceiling arithmetic) and is structurally blind to which leg the window can cash. The missing external is the finding.

## ③ THE PROOF (the game's recorded tape re-run under the amended logic)
| path | fate | grade | $ |
|---|---|---|---|
| ORIGINAL | SAM fills 64¢ W1 (cancel race lost by 21s); exit 79 never printable (refuse-at-every-price); settled NO. FEI's cashable bid cancelled by completion_reprice one second after SAM's fill; never re-placed; the cashable side dies unworked | SAM **F(uncashable-entry)** · FEI unworked | **−320¢** |
| AMENDED (window-truth cashability) | SAM: PULL at the 6:25:44 hold-review — 21s ahead of the fatal marketable window (if the race still loses, the fallback consult exits at the printed band, never a 79 wish) → **REFUSE, no trade, −320¢ avoided**. FEI: re-aim 33 (the refused propose) under the cashable-floor reading → tape prints 31 @6:25:27 AM at size → fills ≤33 → band to 38 printed after (size-aware, 16/16) → **exit printable inside W1** | SAM **lawful pass** · FEI **W1 fill + W1 cash** | **+25¢** (conservative, 33 basis → 38 band) |

Verdict in window terms: **the pair inverts — REFUSE the uncashable side, fill-and-cash the cashable side inside W1.** Batch swing on this game: +345¢.

## ④ THE FILING
- **NEW-CLASS #2 (this walk): CASHABILITY INVERSION** — filed in CLASS_LEDGER: the machinery bought the refuse-at-every-price side and cancelled the 16/16-cashable side's bid on that fill (completion_reprice consults sibling accounting, never sibling cashability). SHADOW-FIRST: the cashability consult ships as would-have-said lines at placement + completion-reprice; **the operator's word gates any live arming.**
- **Instance under WINDOW-TRUTH BLINDNESS (FOMLIM class):** the 6:25:44 SAM hold-review had a full session of tape proving no cashable structure and held anyway.
- **Instance under the cancel-made one-sided-pair census (KOAYAZ intake, 07-15):** FEI = a pair made one-sided by our own cancel, invisible to the pair-law stamp.
- **Cancel-race note to decision ③:** the marketable-stale cancel lost by seconds again (the FOMLIM sweep-gap family's sibling shape).
