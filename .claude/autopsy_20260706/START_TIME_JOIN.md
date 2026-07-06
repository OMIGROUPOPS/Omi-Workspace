# CORPUS START-TIME JOIN — one question, answered (2026-07-06 19:48:58 ET)

**Question: do the honest-clock sources (TE/ESPN via state/schedule.json) or anything on disk hold ACTUAL start times for the corpus events? Answer: NO source on disk holds actual starts at corpus scale; the only joinable source holds SCHEDULED times at 18% coverage, and those miss the certified latch by med 63m — 5× worse than the 12.2m LATCH-CAL grid-fit. The tape remains the only start-time source for the corpus.** Findings only; no rule changes; nothing touched.

## (a) What exists on disk (surveyed: schedule.json, tennis.db 16.8GB — matches/players/live_scores/bookmaker_odds/historical_events/betexplorer_staging/book_prices 39.7M rows, name_cache)
- **state/schedule.json**: 2,454 entries, 06-22→07-08, TE/ESPN, key = 6-char player-code. Thin exactly where the corpus lives: 32–68 entries/day for 07-01..05 vs ~600 corpus matches/day (the pre-flip producer tracked the card-era subset). Holds SCHEDULED times, not actuals.
- **tennis.db `live_scores`** (19,264 rows, TE, back to April): the natural observed-start source — **but the collector retains only {'finished','scheduled'} statuses; every in-play transition row is overwritten. Zero observed starts exist.** (Named data-retention gap: the collector sees starts live and discards them; retention going forward would build the real archive — that is a proposal-shaped observation and stops here.)
- **`historical_events`** (5,889): has first_ts/last_ts — **TRADE-derived (the tape itself); circular** for this purpose, not used.
- **`bookmaker_odds` (118k) / `betexplorer_staging` (139k)**: pre-match scrape timestamps = weak upper/lower BOUNDS on start, never the start; joinable only via player-name prefixes.

## (b) Join rate — true denominator stated
Corpus: **7442 tickers → 3805 matches** (leg samples are per-player; one lookup serves both legs). Join: **schedule.json 702/3805 = 18%** (espn_midnight rows: 0) · live_scores observed starts: **0** · either: 702 · none: 3103.

## (c) Overlap-53: looked-up start vs certified latch
- live_scores: **n=0** (no in-play rows exist — see (a)).
- schedule.json scheduled-start vs latch: n=46, **med -61.5m [p25 -83.3, p75 -33.1], med|err| 63.2m** — scheduled times run ~an hour early vs the certified latch (the late-start physics again, now against the latch).
- **Verdict, plainly: it does NOT beat the 12.2m grid-fit — med|err| 63.2m vs 12.2m, worse by ~5×.**

## (d) Exclusion recount under lookup (moot given (c), reported anyway)
- BAR no-bell matches: 261 excluded → **29 have any lookup (11%)**
- LATCH-CAL no-bell: 1248 → **154 (12%)**
Even the comebacks would import the −61m-biased scheduled axis — a worse clock than the bar they failed. No recount is claimed.

**Bottom line for the amendment: the tape is the only corpus-scale start source; the LATCH-CAL bar (12.2m) stands as the best available axis; the accumulator/coverage path is unaffected. The one new fact worth the record: the TE live_scores collector discards the exact rows that would have answered this question — 19,264 rows kept, zero of them starts.**