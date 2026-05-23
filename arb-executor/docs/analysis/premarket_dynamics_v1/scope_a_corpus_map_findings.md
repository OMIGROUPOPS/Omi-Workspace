# Scope A — corpus-wide premarket dynamics map (atlas-only, 10c anchor bands)

**Date:** 2026-05-23
**Universe:** atlas only — 14,033 N's (ATP_MAIN 4,137 / WTA_MAIN 3,683 / ATP_CHALL 5,326 / WTA_CHALL 887), 7,825 distinct events (6,208 paired + 1,617 singleton).
**Window:** T-4h → T-20m (`time_to_match_start_min` ∈ [20, 240]; 221 per-minute slots).
**Stratification:** category × anchor_regime (9 × 10c bands) × minute.

Descriptive only. No regime classification, no thresholds, no causal claims — Scope B (regime
classification) is the natural follow-on.

## Sources (read-only)

| Artifact | sha256 | role |
|----------|--------|------|
| `premarket_tape_v1.parquet` | `ff2a63d9951d1a3d6b80044106c96ca9fdfd8d3951590e73eec1b46209c5a214` | corpus-wide microstructure base (all 14,033 atlas N) |
| `fv_overlap_join_v1.parquet` | `58cb0d894d83d782f6a793a060b964565e5484c72da4d01b9a35e43f5cf14e1a` | FV layer (≈3.5% of atlas events have any FV) |
| `{atp_main,wta_main,atp_chall,wta_chall}_spike_perN.parquet` | (4 atlas files) | atlas membership + `anchor_price` for banding |

**Methodology.** Atlas universe = inner join on the four spike_perN ticker lists (membership, not
prefix-parse). Each ticker's `anchor_price` (the T-20m taker print, stored in dollars — ×100 →
cents) assigns one of nine 10c `anchor_regime` bands (r05_14 … r85_94; 119 tickers with anchors
outside [5,94]c are dropped from the per-minute stratification). Microstructure stats come from
`premarket_tape_v1` (full corpus); FV stats (`fv_consensus_own`, `fv_delta_at_last_traded`) are
layered from `fv_overlap_join_v1` and exist only for the ~3.5% of atlas events inside the
FV-archive window. All price-like quantities are reported in **cents**.

## Headline tables

### T1 — `spread_close` (cents) by category, median | p90, at three checkpoints

| Category | T-4h (240) | T-2h (120) | T-20m (20) |
|----------|-----------|-----------|-----------|
| ATP_MAIN | 1.0 \| 2.0 | 1.0 \| 3.0 | 2.0 \| 5.0 |
| WTA_MAIN | 1.0 \| 3.0 | 1.0 \| 3.0 | 2.0 \| 7.0 |
| ATP_CHALL | 2.0 \| 4.0 | 2.0 \| 4.0 | 2.0 \| 6.0 |
| WTA_CHALL | 3.0 \| 5.0 | 2.0 \| 4.0 | 2.0 \| 5.0 |

Books are tight throughout (1–2c median) but the **right tail fans out approaching the match** —
p90 spread roughly doubles from T-4h to T-20m on the Main tours (ATP 2→5c, WTA 3→7c). Challenger
starts wider but converges.

### T2 — trade-print availability rate (fraction of minutes with a `price_close`), category × regime

| Category | r05_14 | r15_24 | r25_34 | r35_44 | r45_54 | r55_64 | r65_74 | r75_84 | r85_94 |
|----------|------|------|------|------|------|------|------|------|------|
| ATP_MAIN | 0.459 | 0.350 | 0.343 | 0.335 | 0.406 | 0.457 | 0.463 | 0.402 | 0.404 |
| WTA_MAIN | 0.379 | 0.326 | 0.309 | 0.307 | 0.345 | 0.381 | 0.382 | 0.361 | 0.334 |
| ATP_CHALL | 0.385 | 0.334 | 0.286 | 0.261 | 0.303 | 0.356 | 0.348 | 0.328 | 0.303 |
| WTA_CHALL | 0.434 | 0.309 | 0.277 | 0.288 | 0.279 | 0.311 | 0.318 | 0.314 | 0.327 |

Roughly a quarter to a half of minutes print a trade; ATP_MAIN is the most active (~34–46%).
There's a mild **U/W shape across regimes** — extreme-priced legs (deep underdogs r05_14, mid-fav
r55_74) trade in more minutes than the muddled middle (r25_44).

### T3 — `paired_arb_gap_maker` (cents) by category (paired-event minutes)

| Category | mean | p90 | % minutes \|gap\|>5c | n minutes |
|----------|------|-----|--------------------|-----------|
| ATP_MAIN | 2.59 | 3.0 | 5.15% | 538,404 |
| WTA_MAIN | 3.12 | 4.0 | 7.34% | 442,609 |
| ATP_CHALL | 3.25 | 5.0 | 9.06% | 403,357 |
| WTA_CHALL | 3.46 | 5.0 | 8.43% | 62,368 |

The typical two-sided bid-sum gap is small (~2.6–3.5c), but **large distortions (>5c) are roughly
twice as frequent on Challenger as on ATP_MAIN** (9% vs 5%) — consistent with thinner Challenger
books.

### T4 — mid drift T-4h → T-20m (cents, signed), category × anchor regime

| Category | r05_14 | r15_24 | r25_34 | r35_44 | r45_54 | r55_64 | r65_74 | r75_84 | r85_94 |
|----------|------|------|------|------|------|------|------|------|------|
| ATP_MAIN | -10.56 | -6.62 | -3.84 | -1.99 | -0.36 | 1.62 | 3.09 | 6.50 | 10.81 |
| WTA_MAIN | -10.79 | -7.03 | -4.20 | -1.83 | -0.04 | 1.77 | 2.72 | 6.70 | 10.94 |
| ATP_CHALL | -10.69 | -8.35 | -4.42 | -2.70 | -1.11 | 1.75 | 2.97 | 6.24 | 10.41 |
| WTA_CHALL | -12.60 | -11.97 | -3.91 | -3.05 | -0.16 | 1.35 | 3.27 | 8.87 | 13.08 |

This is the most striking pattern in the map. Mid drift is a **clean, monotonic, near-symmetric
function of anchor regime**: deep underdogs (r05_14) lose ~11c of mid from T-4h to T-20m, heavy
favorites (r85_94) gain ~11c, and the r45_54 coin-flip band sits at ~0. The gradient is essentially
identical across all four categories.

### T5 — FV availability + `fv_delta_at_last_traded` (cents) by category

| Category | FV-available minute rate | fv_delta n | mean | median | p10 | p90 |
|----------|--------------------------|-----------|------|--------|-----|-----|
| ATP_MAIN | 3.03% | 10,752 | 0.85 | 0.90 | -1.0 | 2.7 |
| WTA_MAIN | 2.80% | 5,733 | 0.87 | 1.00 | -1.2 | 2.8 |
| ATP_CHALL | 2.89% | 5,532 | 1.11 | 1.40 | -2.9 | 4.9 |
| WTA_CHALL | 0.00% | 0 | — | — | — | — |

Where FV exists, Kalshi last-traded sits a small amount **above** cross-book consensus (~+0.9c
Main, ~+1.1c Challenger), with wider dispersion on Challenger. WTA_CHALL has zero FV coverage (the
betexplorer scraper carries no women's Challenger tournaments — see fv_overlap_join_v1 notes).

## Observations (descriptive)

The dominant signal is the **anchor-regime mid-drift gradient (T4)**: across the premarket window
the book systematically moves *with* the anchor's lean — favorites strengthen and underdogs weaken
by roughly the same ~10c magnitude at the extremes, monotonically through the bands, crossing zero
at the ~50c coin-flip. This holds with remarkable consistency across ATP/WTA and Main/Challenger.
It is a descriptive characterization of the corpus, not a tradeable claim — the drift is realized
*over* the window, and whether any of it is capturable depends on entry/fill mechanics addressed
elsewhere.

Two liquidity-texture patterns sit alongside it. First, **spreads are tight but their tails widen
into the anchor** (T1) — the median book stays 1–2c but the p90 roughly doubles by T-20m on the
Main tours, i.e. the worst books get worse approaching match time. Second, **distortion frequency
tracks book thinness** (T3): large paired bid-sum gaps (>5c) are about twice as common on
Challenger (~9%) as on ATP_MAIN (~5%), and trade-print activity (T2) is correspondingly lower and
more concentrated in the extreme-priced regimes. The FV layer (T5), available for only ~3% of atlas
minutes, shows Kalshi last-traded printing a small premium over cross-book consensus, slightly
larger on Challenger.

**Small-N / coverage caveats.** WTA_CHALL is the thinnest stratum (887 N / 509 events); its
regime cells and especially its extreme bands (e.g. r15_24 mid-drift −11.97c) rest on few legs and
should be read as indicative. FV cells are uniformly small (~2.8–3% minute coverage; the fv_delta
n's are 5.5k–10.8k minutes corpus-wide, thin once split by minute×regime), and WTA_CHALL FV is
absent entirely. The 119 atlas tickers with anchors outside [5,94]c are excluded from the
per-minute stratification (retained in the per-event fingerprint as `r_oob`).

## Disclosure

Descriptive corpus map, n = full atlas. No causal claims, no regime labels, no policy thresholds.
Outputs: `per_minute_distributions_v1.parquet` (7,956 cells = 221 min × 4 cat × 9 regime, all
populated) and `per_event_fingerprint_v1.parquet` (7,825 events). Regime classification (Scope B),
Plex Round 5 literature synthesis, and the bid-laying policy spec build on top of these.
