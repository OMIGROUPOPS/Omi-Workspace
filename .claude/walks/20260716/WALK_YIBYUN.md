# THE WALK — YIBYUN (20260716) · Wu/Bu (ATP CHALL) — OPEN GAME, provisional
(C-THE-WALK v1 — the OS answers for itself; account auto-rendered from the logs)

## ① THE ACCOUNT (external → what it said → action taken)
- 12:19:25 AM schedule_match  {"start_time": "2026-07-15T14:00:00-04:00"}
- 08:32:18 AM **consultation YIB (Wu)** → decision `placed:path_aim` aim=53 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:?() · window_phase:CONS(W1)
- 08:32:21 AM order_placed YIB {"action": "buy", "price": 53, "count": 5} [W1]
- 10:01:36 AM **consultation YUN (Bu)** → decision `placed:path_aim` aim=42 | atlas_page:CONS · reach_law:CONS · flow_state:CONS(quiet) · cash_window:?() · window_phase:CONS(W1)
- 10:01:37 AM order_placed YUN {"action": "buy", "price": 42, "count": 5} [W1]
- 02:11:10 PM bell_missing  {"min_past_start": 11.2}   ← the match did NOT start on schedule
- 02:53:25 PM entry_filled YUN {"fill_price": 42} [CORRIDOR]
- 02:53:25 PM v4_exit_posted YUN {"exit_price": 51} [CORRIDOR]
- 04:33:45 PM gun_fired  {"source": "fallback_bell"}   ← fired 2.5h past a start the tape never confirmed
- 04:40:48 PM order_cancelled YIB {"label": "match_live_cancel", "success": true} [W2 gun]   ← Wu's bid dies here
- 12:12:25 AM (07-16) completion_action YUN {"verdict": "taker_complete"} [W2 gun]
- 12:58:12 PM (07-16) order_placed YIB {"action": "buy", "price": 55, "count": 5} [UNKNOWN]   ← completion machinery, not presence
- 01:33:49 PM (07-16) order_cancelled YIB {"label": "completion_live_resolve", "success": true} [CORRIDOR]
- 01:33:49 PM (07-16) completion_action YUN {"verdict": "taker_complete"} [CORRIDOR]

**THE CHARGE (presence class — the operator's flag):** a one-sided pair made and KEPT one-sided by our own machinery on a match that never started. The fallback bell fired 4:33:45 PM off a lying schedule (bell_missing had already said, at 2:11 PM, that no start was observed); match_live_cancel killed Wu's bid at 4:40:48 PM and **no presence machinery ever re-placed it** — the only YIB order since (55¢ @12:58 PM 07-16) came from completion logic and was cancelled by its own resolver 35 minutes later. Bu meanwhile holds 5@42 from a CORRIDOR fill **27¢ above the window's proven best (15¢ @1:16 AM, 71 W1 prints, cashable band to 19¢)** — and 42 was never a cashable entry by the window's own tape (only 4 of 19 prints cashable, all in the ≤19 band zone). What we failed to consult: presence-after-unlatch (is the match actually live? ESPN/te said no; the tape said quiet) and the reschedule-aware clock — this is the REACH VERDICT's exact shape (07-14: "the aims were right and the bids were gone"), live on today's flag panel.

## ② THE AMENDMENT (verbalized by the OS — consultation logic, never a ticker-shaped patch)
**Spoken as consultation, by the OS:** "At 4:40:48 PM, the unlatch consult reads three externals before letting the cancel stand: the tape (quiet — no live flow ever printed), the status feed (no live match), and my own bell_missing stamp from 2:11 PM (the start never happened). All three say the same thing: this bell is a schedule artifact, not a match. The presence verdict is RE-PLACE Wu's bid and re-anchor the clock to the reschedule; Wu stays worked into the true T−8h horizon. And at Bu's 2:53 PM corridor fill, the window-truth external says: the printed floor is 15 with band to 19 — a 42 fill is 27¢ above the window's proven best and outside its cashable structure."

**NO NEW CLASS — this is priced evidence to DECISION ⑦ (presence: re-place-on-unlatch + ESPN-status gate for match_live_cancel), awaiting the operator's word since 07-14.** The reschedule variant adds a third input to the priced build: bell_missing's own stamp should veto a fallback-bell latch (the OS already KNEW the start hadn't happened when it let the cancel fire).

## ③ THE PROOF — PROVISIONAL (the game is OPEN; this row is the LIVING DOCKET's founding exhibit)
| path | fate | grade | $ |
|---|---|---|---|
| ORIGINAL (as it stands) | Bu: held 5@42, corridor fill above the window's cashable structure, exit 51 resting — **ungraded until settle**. Wu: unworked since 4:40 PM 07-15 (20h+ and counting); completion churned one bid and resolved it away | **PROVISIONAL** — one-sided pair, wrong-side basis risk open | held −0¢ realized; exposure 210¢ |
| AMENDED (presence held) | Wu's bid survives the false latch (three-consult veto) and re-anchors to the reschedule → worked at T−8h on the true clock; the pair is two-sided going into tonight; Bu's basis unchanged (the corridor fill predates the latch — its own charge files under window-truth, evidence only, the fill stands) | **PROVISIONAL** | verdict lands at settle |

**The replay verdict here is a WATCH, not a number: if Wu is not worked inside tonight's T−8h horizon, the latch-blocks-replacement class CONVICTS (the standing OPEN_LEDGER watch, now carrying this walk as its evidence).** Final grades post-settle via the living docket.

## ④ THE FILING
- **Instance to DECISION ⑦ (presence)** — third priced exhibit (REACH VERDICT slate-scale 07-14, FERCER 06-19, YIBYUN live): re-place-on-unlatch + status gate + **NEW input: bell_missing veto on fallback-bell latches** (the OS's own stamp contradicted the bell it obeyed).
- **Instance under WINDOW-TRUTH BLINDNESS (FOMLIM class):** Bu's 42 corridor fill vs the 15¢ printed floor with cashable band to 19 — evidence row only (fill stands, game open).
- **LIVING-DOCKET WIRE (operator-proven missing, filed this walk):** the docket grades settled legs only; open positions (Bu 5@42) and resting/unworked orders (Wu) have NO provisional grade anywhere the operator reads. The build — provisional grading of open positions + resting orders rendered beside the panel — is priced; **the build word is pending.**
