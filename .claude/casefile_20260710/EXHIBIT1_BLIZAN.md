# CASE FILE — EXHIBIT 1: KXWTACHALLENGERMATCH-26JUL10BLIZAN, both legs (2026-07-10; CC extract, Plex renders)
Artifacts: `EXHIBIT1_BLI.json` · `EXHIBIT1_ZAN.json` (self-describing: decision points + full input vectors + rule citations + tape slice 7:55–8:50 AM ET + prints w/ taker side + render-spec) · `FV_SWEEP.json` (Part 2b). Era stamp: live-era clocks only (census 07-10: WTA_CHALL archive slice ±30m coarse; this exhibit is gun/TE-clocked).

## The four answers

### (1) The 8:15:24 "dual-FV disagreement" — the input that lied was the CLOCK, not a price feed
At the 8:15:24 tick ZAN's book read **23/26→27, last 27, mid 24.5** (tape_slice rows in the JSON) — every price-derived FV the machinery owns (book-mid 24.5, last-traded 27, pair-complement 100−BLI≈26.5) agreed within ~2¢. What disagreed was reality: the match had been LIVE since **8:00:00 AM ET on the honest TE clock** (`clock_liar` 4:00:43 AM: `kalshi_start` = 10:20 AM, `te_honest_start` = 8:00 AM, **disagreement 140 min**), and Zanevska's true probability was already climbing toward the ~50 the burst latch later measured (`fv_burst_anchor` 9:50:40: fv_mid 50.5, fv_bid 50, fv_ask 51, fv_last 51 — all four agree; BLI's mirror: 48.5). The tape-gated abandon was meanwhile logging `schedule_abandon_deferred: tape_not_live` every few seconds (8:10–8:16, `time_to_start_sec` negative and growing) — the book was 15+ minutes behind the match because nothing that reprices it had woken. **Verdict: no FV derivation lied about the book; the Kalshi schedule lied about time, and every book-derived FV inherited it.** LATE-CLOCK class.

### (2) The 8:18:19→8:28 exit at 28 vs burst-FV ~50 — the exit never consults FV, by design
The exit was posted at **8:15:25**, the same second as the fill: `v4_exit_posted {exit_price: 28, band_x: 5, cell_id: 23, entry_price: 23, depth_ok: FALSE (60 < floor 250)}`, and filled 8:18:28 (+$0.25). Its cited rule: **`exit_rule_for` (live_v4.py ~:3060) — "v4 exit lookup: returns (band_x|None, rule) for the 1¢ cell of the entry price"** — the lookup's inputs are (category, entry-price cell). **There is no FV parameter anywhere in the exit path**; the 28 is 23+5 from the WTA_CHALL cell-23 exit table. This is FV-blindness BY DESIGN (the aim-table ruling made FV a yardstick, not a target, on the ENTRY side; the exit side never had an FV input at all). **Per the dispatch's own framing: that is an operator ruling to make, not a bug** — the sweep below gives the live numbers to rule on. The counterfactual on this leg: hold-to-settle paid +$3.85 vs the band's +$0.25 — the exit-harvest class (FUCKUP-3 lineage) at its boundary: the $0.36-counterfactual doctrine was measured on *reachable-band* legs; this leg's band was reachable and paid, but 22¢ under the live-market truth the machinery never looked at.

### (3) Pair integrity 8:18→8:28 — BLI was pair-naked ~10 min; the rebuy was the completion machinery; cycle-2 was intended and stamped
From **8:18:28 (ZAN cycle-1 cashed)** to **~8:28:05 (ZAN cycle-2 fill)**, the held **BLI 5 @74** was the pair's only leg — one-sided for ~10 minutes with its 92¢ exit resting above a falling book (not order-naked: the exit rested; pair-naked in the completion sense). The 8:18:38 rebuy was placed by **`sibling_repost_placed {leg1: BLI, leg1_basis: 74, aim: 22, goal_level: 23}`** — the sibling-completion machinery re-bidding the dog because leg-1 was held and the combined goal (97−74=23) had a live dog bid available; move_repost lifted it 22→23 at 8:18:47. **Cycle-2 was intended by design and stamped** (`cycle: 2` under C-CYCLE-CAP, cap 2 — legal). Its fill raced the match-live cancel: gun fired 8:22:51 (`price_divergence`, honest tts **−7.9 min**), grace armed 8:22:59, and at 8:28:05 the cancel returned `success: false` with `entry_cancel_partial {filled_qty: 5, kept_position: true}` — the order filled during the cancel (the −0c cancel-race class, here on the benign side: the "accident" bought the winner at 23 against a burst-FV of 50.5, the deep_neg_fv watch line −27.5).

### (4) Final accounting (settlement vocabulary, per leg, per cycle)
| leg | cycle | entry | cashed-via-exit | rode-to-settlement | net |
|---|---|---|---|---|---|
| BLI | 1 | 5 sh @74 (8:07:31) | — (92 never printed) | **LOSS −$3.70** (settled 10:28:56, F-bucket) | −$3.70 |
| ZAN | 1 | 5 sh @23 (8:15:25) | **+$0.25** (28¢, 8:18:28) | — | +$0.25 |
| ZAN | 2 | 5 sh @23 (~8:28:05, cancel-raced fill) | — | **WIN +$3.85** (settled; API shows flat) | +$3.85 |
| **pair** | | combined c1 = 97 = goal | +$0.25 | −3.70 +3.85 | **+$0.40** |
Fee-blind jsonl convention; cents-exact reconciliation awaits −1a000. The pair achieved the 97 goal and net-positive — but only because the cycle-2 "accident" recaptured what the FV-blind 28¢ exit gave away.

## Part 2b — LIVE SWEEP (`FV_SWEEP.json`, run 1:0x PM ET)
21 open positions + 36 resting buys swept against each leg's latest `fv_burst_anchor` fv_mid. **Flags >10¢: 2, both KXITFMATCH-26JUL10ALFLOO** — held LOO ≈78¢ basis vs burst-FV 12.5 (÷65.5¢: holding the dying side, exit band above a collapsed book — the BLI pattern live right now) and resting ALF buy 18 vs burst-FV 86.5 (−68.5¢: the completion dog-bid far under a running winner). Most legs have no burst yet (n_with_burst_fv in the JSON) — the sweep measures what's measurable and names it. **The exit machinery consults FV nowhere** (citation above, one line). **Ruling framing, said plainly: FV-blind exits are the design, not a defect** — the divergence numbers (−27.5 ZAN, ±65 ALFLOO live) are the evidence base if the operator wants an FV-aware exit clause; boarded as an operator-decision item, not a bug.

## Failure-taxonomy verdicts (also embedded in each JSON)
- **BLI: RODE-LOSER-TO-ZERO (F-bucket)** on a +140-min lying clock — the 4:00 AM 74¢ staircase bid was legitimate premarket by the honest clock (start 8:00), but the fill at 8:07 was 7 minutes IN-PLAY and the 92¢ cell-band exit chased a book that never came back.
- **ZAN: EXIT-BAND-MYOPIA + LATE-CLOCK** — fill and exit both in-play on a book 15 min behind the match; the band paid +$0.25 where the live truth held +$3.85; cycle-2 (by design) recaptured it.

## Render-spec (in each JSON)
G9-style panels: price (bid/ask/mid/last from tape_slice) · prints (scatter sized by count, colored by taker_side) · decision markers (every decision_point with rule_cited label) · annotation lines at honest start 8:00:00 AM and gun 8:22:51 AM · verdict banner from failure_taxonomy_verdict.

## Follow-on exhibits queued
PAPJER both legs · PAWHRU · one early-unlock cohort member · one stale-anchor cohort member.
