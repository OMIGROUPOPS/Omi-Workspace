# OMQS LIVE FORENSIC — KXITFMATCH-26JUN30SHINIS (Shiraishi H. vs Nishiwaki K., ITF-M), Nishiwaki leg

Read-only, Kalshi REST + tick tape + order-event log, ET. Scheduled start 11:00 PM ET (Jul-01 03:00 UTC). We FILLED Shiraishi (favorite) buy-yes @85 x5 (maker, REST-confirmed, position 5). We did NOT fill Nishiwaki (0 fills, position 0). Correction to the brief: Nishiwaki traded **16–21¢ premarket** (not ~44¢); it collapsed to 5–8¢ only IN-PLAY.

## COMPLETE EVENT LOG — Nishiwaki (-NIS) leg
| ts (ET) | event | price/qty | reason / book |
|---|---|---|---|
| 21:58:31 | window_open_set | 16¢ | ttm 61.5min (window opens T-61 to sched 11:00 PM); Nishiwaki cell 16 (underdog) |
| 22:20:17 | order_placed | **buy yes @15 x5** | first maker bid (r15_24), at/below the 16 market |
| 22:40:37 | order_cancelled | — | label **v4_t20m_fallback** (T-19m) |
| 22:40:37 | order_placed → clamp | **@12 x5** | clamp ask1=12 best_ask=15, tts 19.4 |
| 22:42:37 | cancel → repost | @12 | v4_move_repost (cur 14, ask 15) |
| 22:44:38 | cancel → repost | **@12 x5** | v4_t20m_fallback → final resting bid @12 (order 99bd38ac), tts 15.4 |
| 23:10:50 | *(sibling)* entry_filled SHI | @85 | Shiraishi FILLED @85 (maker) → Nishiwaki now the naked resting leg |
| 23:12:39 | fv_burst_anchor | — | **legs_filled=1, solo** (Nishiwaki unfilled) |
| 23:16:05 | match_live_detected | — | volume_burst=12/60s, **tts_min −16.1** (real gun fired 16 min AFTER scheduled start) |
| 23:16:06 | order_cancelled | — | label **match_live_cancel** (the @12 bid) |
| 23:16:06 | **match_live_resting_cancel** | — | fires on the Nishiwaki bid, **1 s after the gun, INSTANT (grace OFF in current bisect config), sibling Shiraishi HELD** |
| 23:16:06 | **complete_cross_skip** | ask 13, **ask_sz 1** | completion-cross to buy Nishiwaki@13 SKIPPED — only **1 lot** at the ask, needed 5 (basis 85+13=98 ≤ cap 102 would have qualified) |
| 02:51–03:57 AM | *(tape, in-play)* | 16→**8→5** | 631 trades; **562 prints at/below 13¢** — the collapse traded THROUGH our old 12¢ bid, but ~3.5 h AFTER it was cancelled |

## (1) Where did our bid rest?
At **15¢ then 12¢** (repriced down by the fallback-maker clamp), reposted 4× over 22:20–22:44. **12¢ sat BELOW the 16–21¢ premarket market** (best_ask 15). We deliberately posted under the touch (r15_24 offset), not at it.

## (2) Did the market trade through our bid?
**While our bid was alive (22:20–23:16), NO** — the premarket market was 16–21¢ and never dipped to our 12¢ (our bid was below the premarket range; depth ahead of us also grew 58→2454→5124). **The 562 trades at/below 13¢ all occurred 02:51–03:57 AM — IN-PLAY, ~3.5 h AFTER our bid was cancelled.** So there was no premarket fill opportunity (market above us), and the in-play trade-through happened post-cancel. Not a gap — the price simply never came down to our low bid until after we were out.

## (3) The cancel
**match_live_resting_cancel fired on the Nishiwaki bid at 23:16:06 — 1 second after match_live_detected (tts −16 min).** It was the **match_live_cancel** (the volume-burst gun latch), NOT the T-20 fallback (which had earlier fired only as repost triggers at 22:40/22:44). It was **INSTANT, not graced** — the current bisect config has `match_live_grace_kill=FALSE`, so no grace was applied even though the sibling (Shiraishi) was HELD → cancelling left Shiraishi naked. Separately, the **completion-cross was blocked** the same second by a 1-lot ask (`ask_sz 1` < qty 5).

## (4) THE SEQUENCE → outcome
post @15→@12 (below the 16–21 premarket market) → **market never dipped to our bid premarket** (no fill opportunity) → Shiraishi fills @85, Nishiwaki goes solo/naked → at the gun (11:16 PM, 16 min late) **match_live_cancel removes the @12 bid instantly (grace OFF)** AND **the completion-cross is skipped (ask_sz 1<5)** → Shiraishi left **naked @85** → in-play Nishiwaki collapses 16→8→5, trading through our old 12¢ level 562× (~3.5 h later) → bid already gone, **no fill**. Position now: Shiraishi 5 @85 naked; Nishiwaki 0.

## VERDICT — which scenario?
**Closest to (c) — a cancel that removed a bid that WOULD have become the completing fill — with an (a) caveat.**
- It is NOT (b): the price did not gap past us. Premarket it stayed ABOVE our low bid (never dipped to 12); in-play it traded through us, but only after the cancel.
- The premarket no-fill was a **pricing miss, not queue-starvation per se**: our bid at 12 was below the 16–21 market, so no premarket dip reached it (we posted under the touch by design).
- Had we HELD the @12 bid, the in-play collapse (16→8) would have filled it, **completing the pair** Shiraishi@85 + Nishiwaki@12 = combined **97 → a LOCKED +3** (one side always pays 100). That completing fill is the fill we wanted — and TWO mechanisms blocked it: (i) the **match_live_cancel** pulled the resting bid at the gun (grace OFF), and (ii) the **completion-cross** that would have locked it @98 was blocked by a **1-lot ask**.
- The (a) caveat: viewed standalone (ignoring the pair), that fill would be buying the losing underdog @12→0 = −12; so the cancel did "avoid a knife" in isolation. But the correct frame is the PAIR — we forfeited a locked +3 and are instead riding **Shiraishi naked @85** (currently ~92% to win → ~+15 expected, but the −85 tail = the FUCKUP-3 naked-favorite pattern).

**Bottom line:** not-filling Nishiwaki was NOT the stale buffer correctly killing a naked bid — the stale buffer only repriced it. It was the **gun-cancel (instant, grace OFF) plus a thin-ask completion-cross skip** that together forfeited the pair-completion the resting bid would have caught on the in-play collapse. The lever: (i) grace-hold the resting sibling bid at the gun when the other leg is held (the disarmed grace-kill), and (ii) a completion path that tolerates a thin ask (size-up or ride to the collapse) instead of skipping on ask_sz=1.
