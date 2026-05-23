# Path B — premarket maker-bid fill mechanics (entry-effort study)

**Date:** 2026-05-23
**Universe:** atlas only — 14,033 N's (ATP_MAIN 4,137 / WTA_MAIN 3,683 / ATP_CHALL 5,326 / WTA_CHALL 887).
**Window:** T-4h → T-20m. **Grid:** placement_minute ∈ {240,180,120,90,60,40} × bid_offset ∈ {1,2,3,5,8,10,15c} = 42 cells/N.
**Atlas alignment:** downstream of the locked atlas T42 (`d99c6e9`); addresses **Axis 2 (entry-side maker
improvement)** per **G22**. Doctrine: **A39 / B16 / B25 / G22**. Pure fill mechanics — **no PnL, no exit
logic, no atlas reproduction.** The strategy (per-cell hindsight-optimal exit-or-hold) is locked; this
study answers only *where to place the entry bid*.

## Sources (read-only)

| Artifact | sha256 |
|----------|--------|
| `premarket_tape_v1.parquet` | `ff2a63d9951d1a3d6b80044106c96ca9fdfd8d3951590e73eec1b46209c5a214` |
| `{atp_main,wta_main,atp_chall,wta_chall}_spike_perN.parquet` | atlas membership + `anchor_price` (×100 → cents, banded per Scope A) |

## Section 1 — Methodology

For each atlas N and each strategy cell: `bid_price = anchor_price_cents − bid_offset_cents` (clamped ≥1c).
Walk the N's premarket trajectory forward from `placement_minute` toward T-20m; **fill** at the first
(highest-ttm) minute where `price_close ≤ bid_price` OR `yes_ask_close ≤ bid_price` (last-traded prints
at/below the bid, or the ask comes down to it). If never satisfied by T-20m → **missed**. The metric is
`expected_improvement_cents = fill_rate × bid_offset_cents` — the average entry-side cents recovered,
*additive on top of* whatever exit strategy the locked atlas applies (the atlas measured the exit at
+8.70% blended; entry improvement adds to that). No settlement/PnL is computed here.

## Section 2 — Fill-rate grids (regime × placement_minute) at bid_offset = 3¢

(Representative slice; the full 42-cell grid per regime is in `path_b_per_regime_fill_summary_v1.parquet`.)

**ATP_MAIN** — T-240 / 180 / 120 / 90 / 60 / 40
| regime | 240 | 180 | 120 | 90 | 60 | 40 |
|--------|----|----|----|----|----|----|
| r05_14 | .31 | .30 | .29 | .28 | .27 | .24 |
| r45_54 | .51 | .50 | .47 | .44 | .39 | .32 |
| r85_94 | .64 | .63 | .61 | .60 | .57 | .50 |

**WTA_MAIN**: r05_14 .36→.29, r45_54 .53→.36, r85_94 .70→.56 (240→40).
**ATP_CHALL**: r05_14 .39→.30, r45_54 .58→.40, r85_94 .78→.65.
**WTA_CHALL**: r05_14 .34→.29, r45_54 .55→.38, r85_94 .87→.75.

Two patterns are visible already at 3¢: fill rate **rises with anchor regime** (favorites fill far more
readily than underdogs at the same offset) and **declines gently as placement moves later** (more window
= more chances to be hit). At 8¢ the same shape holds but compressed — favorites r85_94 still ~0.50–0.68,
underdogs r05_14 collapse to ~0.04–0.09.

## Section 3 — Per-regime hindsight-optimal placement (max expected_improvement_cents)

| regime | ATP_MAIN | WTA_MAIN | ATP_CHALL | WTA_CHALL |
|--------|----------|----------|-----------|-----------|
| r05_14 | T240/2c, fill .53, **1.06c** | T240/2c, .56, **1.11c** | T240/3c, .39, **1.16c** | T180/2c, .51, **1.02c** |
| r15_24 | T240/5c, .24, **1.18c** | T240/5c, .27, **1.37c** | T240/5c, .29, **1.46c** | T180/5c, .35, **1.73c** |
| r25_34 | T180/8c, .15, **1.17c** | T180/10c, .15, **1.54c** | T240/3c, .45, **1.34c** | T120/10c, .23, **2.31c** |
| r35_44 | T240/2c, .63, **1.27c** | T180/15c, .14, **2.08c** | T240/8c, .18, **1.42c** | T120/10c, .21, **2.05c** |
| r45_54 | T240/15c, .12, **1.85c** | T180/15c, .22, **3.29c** | T90/15c, .14, **2.05c** | T120/10c, .23, **2.32c** |
| r55_64 | T180/15c, .12, **1.75c** | T240/15c, .16, **2.33c** | T240/3c, .57, **1.72c** | T90/15c, .15, **2.32c** |
| r65_74 | T240/15c, .15, **2.23c** | T180/15c, .22, **3.25c** | T240/15c, .14, **2.13c** | T120/15c, .20, **3.05c** |
| r75_84 | T180/15c, .32, **4.74c** | T180/15c, .29, **4.39c** | T180/15c, .29, **4.40c** | T120/15c, .39, **5.85c** |
| r85_94 | T180/15c, .42, **6.28c** | T240/15c, .43, **6.39c** | T240/15c, .47, **6.98c** | T90/15c, .45, **6.82c** |

(Format: placement/offset, fill_rate, **expected_improvement**. Smallest strata are WTA_CHALL extremes:
r85_94 n=77, r05_14 n=82 — indicative.)

## Section 4 — Corpus-level summary (hindsight ceiling)

Applying the per-regime hindsight-optimal cell to every N, the **n-weighted mean expected entry
improvement is 2.46¢/contract** across the 14,033-N corpus. A single uniform strategy — place a 15¢-below
bid at T-4h for everyone — yields **2.25¢/N** blended (fill 0.150); the regime-conditioning lift over the
uniform rule is modest (~0.2¢/N). Top uniform cells are all the **15¢ offset at the earliest placements**
(T-240 2.25c, T-180 2.24c, T-120 2.21c), with the 10¢ offset close behind (~2.0c at higher fill ~0.20).
These are **hindsight** ceilings — they assume the regime (and that a large offset is the right choice) is
known a priori.

## Section 5 — Observations

The dominant pattern is a clean **favorite/underdog asymmetry driven by the Scope A T4 drift gradient**.
Favorite books drift *up* (~+11¢ at r85_94 over the window), so a bid posted well below the T-20m anchor is
*above* the early mid and gets swept as the market climbs — large 15¢ offsets fill 42–47% on heavy
favorites and capture the full 15¢, giving the corpus's biggest entry edge (~6.3–7.0¢/contract). Underdog
books drift *down toward* the anchor, so a bid *below* the anchor is below where the market lands and only
fills on intraminute overshoot — large offsets barely fill, and the optimal is a small 2–3¢ offset at high
fill, capping underdog entry edge at ~1.0–1.2¢. Expected improvement therefore **rises monotonically with
anchor regime**, and the optimal `bid_offset` rises with it (2–3¢ for deep underdogs → 15¢ for heavy
favorites). Placement timing is a weak second-order lever: **earlier placement (T-4h/T-2h) weakly dominates**
(more window to be hit), and almost every regime's optimum sits at T-240 or T-180; later placement only ever
reduces fill. No regime is "always fills" at meaningful offsets, and no regime is uniformly hard — the grid
is smooth and monotonic (fill_rate decreases in offset in 216/216 strata).

## Section 6 — Disclosure

These are **hindsight-optimal** placements at corpus level — live deployment loses some edge to per-event
uncertainty about which regime/offset to choose without foresight (the 2.46¢/N ceiling vs the 2.25¢/N
single-rule floor brackets that gap). Fill is detected at **minute cadence** (price_close / yes_ask_close at
the minute close), so sub-minute fills/queue position are not modeled, and **fill realism downstream (atlas
Axis 1, B25) is a separate caveat** — a resting maker bid that the trajectory crosses is assumed filled.
Round 5's velocity-conditional cross-fallback is a separate refinement not simulated here. WTA_CHALL (n=887)
extreme-regime cells rest on few legs. This study establishes entry-side fill mechanics only; it does **not**
re-measure realized PnL (atlas T42 owns the exit side).
