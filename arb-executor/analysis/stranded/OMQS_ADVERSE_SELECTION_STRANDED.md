# OMQS — ADVERSE-SELECTION on STRANDED SINGLES (log-truth reconstruction, 2026-07-01)

**What this is.** The stranded-single set behind §4E of the June Vault, *persisted at last*. The original `OMQS_ADVERSE_SELECTION_STRANDED.md` was never saved to disk; this is a faithful **log-truth reconstruction** built from the Jun24-30 order-event logs (`live_v3_2026062x.jsonl`), matched to the operator's own producer definitions (`phaseA.py`). Companion data: [`stranded_91.json`](stranded_91.json).

**Honest provenance / gate status (operator-ratified, Option 1).** This reproduces the funnel to **91 of 93 stranded singles** and a **−$43.97** baseline vs the funnel's **−$50.65**. The residual is diagnosed and bounded:
- The funnel counted fills by **Kalshi REST truth**; ~9 completed pairs it saw via a live REST-fills pull have **no `entry_filled` in the logs** and that pull is **not cached anywhere on the box** (`kalshi_fills_cache.json` is stale Jan–Mar, 0 Jun tennis fills).
- The **−$50.65 was a Jun-30 snapshot** the funnel itself flagged as *"newest legs still settling"* — realized totals have drifted since.
- Ratified as **β-decision-safe**: the ±2 events / ±$6.68 residual is small relative to β's ship threshold (recover ≥ $25), so it cannot flip the β conclusion.

## The gate table (reconstruction vs funnel)
| | pairable | completed | (a) queue-starve | (b) missed-both | (c) gun-cancel | forfeit $ | stranded (a+c) |
|---|--:|--:|--:|--:|--:|--:|--:|
| **log-truth recon** | 403 | 285 | 53 | 27 | 38 | **−$43.97** | **91** |
| funnel (REST-truth, Jun30 snap) | 406 | 294 | 57 | 19 | 36 | −$50.65 | 93 |

Definitions (from `phaseA.py`): `filled` = entry qty > 0 (`entry_filled`/`completion_fill`; settled/exited legs already imply a fill); **pairable** = both legs posted a buy-yes bid; **completed** = both filled; **stranded single** = exactly one leg filled — split into **(a) queue-starve** (sibling never filled, no gun-cancel) vs **(c) gun-cancel** (sibling's resting bid cancelled by `match_live_resting_cancel` before it filled). Forfeit $ = kept-leg realized (settle+exit cents).

## The mechanism (this reconstruction)
- **91 stranded singles**: 53 queue-starve + 38 gun-cancel. By cat: ATP_CHALL 42, WTA_MAIN 28, ATP_MAIN 21.
- **We keep the loser, strand the winner.** Among the 45 events with a known settlement, the **missed (stranded) leg WON in 41 = 91%** — i.e. the leg we failed to fill was overwhelmingly the eventual winner; the leg we kept was the loser. (46 events have no settlement recorded in the logs; the known subset is even starker than §4E's 65% headline but small-N.)
- Kept-leg settle where known: 40 LOSS / 3 WIN. Kept-leg naked realized totals **−$43.97** — the money forfeited by riding one naked leg instead of completing the pair.

## "Good price" definition (operator, 2026-07-01)
**A good price is pair combined ≤ 97¢. 100 = par. The goal is 97-and-under.** Downstream β lock-rate reports BOTH the ≤100 bucket and the ≤97 bucket; **the ≤97 rate is the one that matters.**

## `stranded_91.json` schema (per event)
`event`, `cat`, `mode` (queue_starve|gun_cancel), `kept` / `missed` (leg tickers), `kept_entry_cents`, `kept_qty`, `kept_settle` / `missed_settle` (WIN|LOSS|null), `winner` (kept|missed|null), `kept_naked_pnl_usd` (the baseline realized, sums to −$43.97), `gun_cancel_ts` (epoch, present for gun-cancel legs).

## Downstream
- **β** (deterministic): replay these 91 — cross the missed leg's ask at gun-30s/15s/5s/gun-time, report per-offset completable / ask+size / combined / lock-rate (≤100 and ≤97) / NET vs −$43.97. Ship if NET recovers ≥ $25. → `OMQS_BETA_GUNCROSS.md`.
- **α** (divot predictability): best_bid-drops-without-trade on the 91 missed winners from the L1 tape + L2 `ws_depth_recorder`; leading-signal AUC + duration vs fill latency. Buildable if AUC>0.65 AND duration>latency. → `OMQS_ALPHA_DIVOT.md`.
