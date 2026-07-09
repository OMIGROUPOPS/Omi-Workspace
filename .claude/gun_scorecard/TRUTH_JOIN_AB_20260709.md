# TRUTH-JOIN A/B — gun_scorecard.py fixed join vs old join (2026-07-09 ~4:40 PM ET, offline on the VPS, same jsonl window, no --nightly side effects)

**Candidate SHA `572d678a`** (analysis-side only; live_v4 / order path / oslayer untouched; the ±3-min FRESH bar UNCHANGED).

## The four named defects → what shipped

1. **Fire-source-independent truth.** Old: only `te_scoreboard` fires got a tape-onset truth; tape_latch / price_divergence / schedule_live fires (46/50 overnight) only graded if a broken observed_starts name-join hit (~never). New: EVERY fire, whatever fired it, grades against its match's certification-grade tape onset (trades CSV, first minute with prints in ≥5 of the trailing 15 one-minute bins), with the observed_starts bank as fallback truth. GRANULARITY LAW held: the 349 training-grade recovered bells are never read (the script never touches shape_corpus).
2. **No silent half-joins.** Old: `truth_src` stamped `tape_onset` before checking the onset existed (ESTAGU/SNIAND/VONZID showed src with empty truth). New: `tape_onset()` returns `(onset, reason)`; a row either grades or prints `UNJOINABLE:no_trades_csv | no_prints_in_window | no_flow_onset`.
3. **The MOCTAN class (day-boundary / lying clocks).** Old: onset searched `[fire−3h, fire+1h]` on the raw fire time. New: the search window centers on the ANCHOR HIERARCHY's honest clock — `clock_liar.te_honest_start` / `pm_clock_shadow.honest_start` (both datemiss-aware) > schedule > fire-time last resort; after-table anchor census: **165 tape@honest, 4 tape@sched, 1 tape@fire**. A truth predating its own FRESH fire by >15 min, or any join >120 min out, is flagged **SUSPECT(reason)** — named per cat, excluded from both the bar and the median, never averaged in. (Suspects cannot eat bar-passers by construction: ≥15 min > ±3 min.)
4. **Miss path verified.** Misses come from observed_starts-joined events with no fire. The matcher was rebuilt (both-leg: each half of the ticker pair-code must match a DIFFERENT player's name-token prefixes; single-leg unique fallback, marked): 8/17 bank rows since day0 now join, all both-leg. All 8 joined events fired tonight, so `misses=[]` is TRUE, not a dead path — proven by synthetic drop-one-fire: removing VONZID's fire yields `NO FIRE` row + `misses=[VONZID]`.

## Before/after — last night's 50 fires (the 6:10 AM committed table, re-graded under the fixed join)

| cat | fires | truth-graded OLD | clean-graded NEW | SUSPECT (named, quarantined) | UNJOINABLE (named) |
|---|---|---|---|---|---|
| ATP_CHALL | 3 | 0 | 0 | 3 | 0 |
| ITF_M | 22 | 3 | 4 | 17 | 1 |
| ITF_W | 19 | 0 | 1 | 18 | 0 |
| WTA_CHALL | 6 | 0 | 2 | 4 | 0 |
| **TOTAL** | **50** | **3** | **7 clean** | **42** | **1** |

Every one of the 50 now has a disposition — graded, SUSPECT with reason, or UNJOINABLE with reason. Zero silent halves.

## Full-day window (same run, 173 fires) — per-cat summary under the fixed join

```
ATP_CHALL n=30 FRESH-within±3min=1/8 med|Δ|=9.3m catchup=0 suspect=[FEALAJ,JOHMAL,BROILA,COPMIC…] unjoinable=0 misses=[]
ITF_M     n=72 FRESH-within±3min=2/9 med|Δ|=8.3m catchup=4 suspect=[DELKUS,HONNAK,JANFUN,JUHKLO…] unjoinable=2 misses=[]
ITF_W     n=50 FRESH-within±3min=4/6 med|Δ|=1.7m catchup=0 suspect=[CHOYAM,DIAPAV,LUENAT,MILMIS…] unjoinable=0 misses=[]
WTA_CHALL n=19 FRESH-within±3min=0/8 med|Δ|=11.8m catchup=0 suspect=[JONJEA,STEZHA,VIDANS,YAMMIN…] unjoinable=0 misses=[]
WTA_MAIN  n=2  FRESH-within±3min=0/0 med|Δ|=--   catchup=0 suspect=[KOSNOS,MUCGAU] unjoinable=0 misses=[]
```

Old same-window summary (for contrast): only 2 of 173 graded (both ITF_M, med|Δ|=168.4m), misses=[] everywhere with the path unverified.

## The named exhibits, before → after

| event | old row | new row |
|---|---|---|
| MOCTAN (26JUL08, day-boundary) | truth 10:31 PM, delta 102.2 **averaged in** | same join, now `102.2 SUSPECT(truth_predates_fresh_fire)` — quarantined |
| ESTAGU | `truth_src=tape_onset, truth EMPTY` (silent half) | truth 9:45 AM `tape@honest`, `−331.7 SUSPECT(join_out_of_bounds)` |
| SNIAND | silent half | truth `tape@honest`, `−326.6 SUSPECT(join_out_of_bounds)` |
| VONZID | silent half | `obs_starts(both-leg)` truth, **delta 0.5 min — graded clean** |

## Honest caveats (named, not hidden)
- The suspect population is large (42/50 overnight). Two causes mix in it: genuinely bad tape joins (premarket churn satisfying the 5-of-15 convention on liquid matches — the onset convention itself is pre-registered and was NOT touched) and genuinely LATE fires (>15 min after real onset). The table names every suspect so manual reads can split them; the 15-min threshold is a tunable the operator can move — it cannot affect the ±3 bar either way.
- ITF_W daytime grades clean (med|Δ| 1.7m, 4/6 within bar) — the machinery works end-to-end where the tape is thin and honest.
