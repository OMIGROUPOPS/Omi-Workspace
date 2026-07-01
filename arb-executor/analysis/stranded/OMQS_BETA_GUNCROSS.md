# OMQS — β: GUN-CROSS the stranded winner (deterministic replay, 2026-07-01)

**Question (Vault §4E-β):** when a leg fills and its sibling sits stranded approaching the gun, does **crossing the missed leg's ask** to lock the pair recover the −$43.97 forfeit? **Ship if NET recovers ≥ $25.**

**Verdict: DOES NOT SHIP.** Gun-crossing recovers only **≈ +$8.2** of the −$43.97 — a third of the bar. Completing the pair *does* beat riding the loser naked (it caps the loss near par), but by the gun the **stranded winner's ask has already appreciated**, so the completion is priced at/above par.

## Replay (91 stranded events; tape-covered 40; baseline all-91 = −$43.97)
Cross the missed leg's `ask_1` at each offset; combined = kept_entry + crossed_ask; taker fee applied; **good price = combined ≤97** (100 = par).

| offset | completable | lock ≤100 | **lock ≤97** | ask med | **comb med** | thin* | β NET (all 91) | recovery vs base |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| gun-30s | 40/40 | 10/40 (25%) | **6/40 (15%)** | 77¢ | **104¢** | 20 | −$36.03 | **+$7.94** |
| gun-15s | 40/40 | 10/40 | **6/40** | 76¢ | 104¢ | 19 | −$35.76 | +$8.21 |
| gun-5s  | 40/40 | 10/40 | **6/40** | 76¢ | 105¢ | 19 | −$35.74 | +$8.23 |
| gun-time| 40/40 | 10/40 | **6/40** | 76¢ | 105¢ | 22 | −$35.74 | +$8.23 |

*thin = # crosses where `ask_1_sz` < kept_qty (5) → would need to walk up the ask ladder; makes β **optimistic** here.

## Why it fails
- **The winner is expensive by the gun.** Combined median **104-105¢ > par** — crossing locks a small loss vs par, not a good price. Only **15% clear the ≤97 good-price bar**.
- The last 30 seconds barely move (all offsets ≈ identical), so timing the gun-cross finer doesn't help.
- Coverage-robust: even scaling the covered recovery to all 91 (≈ +$18.7) stays under $25, and thin-fill (half the crosses) pushes it lower still.

## Implication
β is a **controlled-loss backstop** (better than naked-loser-ride by ~$8), not a money-maker. The forfeit is not recoverable *at the gun* — the winner's ask has already run up. **This is the case FOR α:** the value, if any, is catching the winner **earlier and cheaper**, at the divot, before the ask appreciates. → `OMQS_ALPHA_DIVOT.md`.

Method: `beta.py` (this dir). gun = `match_live_resting_cancel` ts → else scheduled start → else last tape tick. Source: `analysis/premarket_ticks` (5-deep L1, ask_1+size). Baseline = `stranded_91.json` kept_naked_pnl (−$43.97).
