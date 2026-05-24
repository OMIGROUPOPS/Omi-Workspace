# Path B v2 — marketable-vs-resting split + atlas exit replay (dual-improvement measurement)

**Date:** 2026-05-23
**Universe:** atlas only — 14,033 N. **Strategy:** single universal rule — place bid at T-4h (T-240),
offset 15¢ below the T-20m anchor (`bid = anchor − 15`, clamped ≥1¢). **Pre-realism** (B25 0.5–0.7×
discount NOT applied).

This is the load-bearing measurement: the actual deployable ROI that maker placement adds over the
locked atlas's +8.70% T-20m-taker baseline, with execution mode (marketable taker vs resting maker vs
miss) split out and the locked atlas cell exit-rule replayed from the *actual* entry price.

## Sources (read-only)

| Artifact | sha256 |
|----------|--------|
| `premarket_tape_v1.parquet` | `ff2a63d9951d1a3d6b80044106c96ca9fdfd8d3951590e73eec1b46209c5a214` |
| `{cat}_spike_perN.parquet` | anchor_price, size_qual_max_250, settlement_value (exit-replay substrate) |
| `{cat}_descriptive_1c.parquet` | per-cell `best_exit_X` + `rule` |

## Section 1 — Methodology

For each atlas N: `bid = max(anchor−15, 1)`. At the T-240 placement, if `yes_ask_close ≤ bid` →
**marketable_taker** (entry = ask, executes immediately as taker). Else post a **resting maker** bid;
walk T-240→T-20m, fill at the first minute `price_close ≤ bid OR yes_ask_close ≤ bid` (entry = bid).
If never filled → **miss_fallback** (entry = T-20m anchor, identical to the atlas baseline).

**Atlas exit replay (substrate-resolved).** The cell's rule (`best_exit_X` / "hold to settlement")
is replayed from the actual entry: "exit at +X" triggers iff `entry+X ≤ size_qual_max_250` (the
≥250ct depth-qualified post-anchor max from spike_perN); realized = X if triggered, else hold
(winner 99−entry, loser −(entry−1)). Because maker/marketable entries are ≤ anchor, the target
`entry+X` is ≤ `anchor+X`, so this is a **conservative lower bound** (the pre-T-20m window, where a
climbing favorite can also hit the target, is not added). No g9_trades / post-T-20m walk needed;
`size_qual_max_250` was itself baked from g9_trades by `build_spike_perN.py`. `exit_minute` is NULL
throughout (the proxy yields the trigger boolean, not the minute).

## Section 2 — Corpus headline

| Metric | Maker placement (this) | Atlas baseline (T-20m taker) | Δ |
|--------|------------------------|------------------------------|---|
| Total realized PnL @10ct | **$7,829.30** | $6,158.20 | **+$1,671.10 (+27.1%)** |
| Capital deployed @10ct | **$67,346.20** | $70,813.20 | −$3,467.00 |
| Blended ROI | **11.63%** | 8.70% | **+2.93 pp** |

Maker placement earns **27% more on 5% less capital** → a 2.93-point ROI lift, **pre-realism**. The
atlas baseline was reproduced **exactly** ($6,158.20, ratio 1.0000) — the methodology gate.

## Section 3 — Execution-mode breakdown

| Mode | N (%) | Total PnL | Capital | ROI | mean entry |
|------|-------|-----------|---------|-----|-----------|
| marketable_taker | 358 (2.6%) | $466 | $1,755 | **26.6%** | 49¢ |
| maker_resting | 1,747 (12.4%) | $1,844 | $8,607 | **21.4%** | 49¢ |
| miss_fallback | 11,928 (85.0%) | $5,519 | $56,984 | 9.7% | 48¢ |

The entire +$1,671 lift comes from the **~15% of N's (2,105) that filled at a discount** — they earn
21–27% ROI. The 85% that missed get baseline-equivalent (entered at anchor, improvement = 0). So
**maker placement is a "capture the 15% that fill cheap, everything else falls back to atlas"**
strategy under the universal 15¢ rule.

## Section 4 — Per-regime ROI lift (all 36 cells positive)

ROI lift is **positive in every category × regime cell** (+1.3 to +5.9 pp). Representative ATP_MAIN:

| regime | %mkt | %rest | %miss | ROI | atlas ROI | lift |
|--------|-----|------|------|-----|-----------|------|
| r05_14 | 0% | 3% | 97% | 77.1% | 73.1% | +4.01 |
| r45_54 | 2% | 10% | 88% | 11.5% | 8.5% | +2.95 |
| r85_94 | 14% | 28% | 58% | 7.6% | 4.1% | +3.57 |

Top lifts corpus-wide: WTA_MAIN r45_54 **+5.93pp**, WTA_MAIN r25_34 +5.75pp, WTA_CHALL r75_84 +4.88pp,
ATP_MAIN r05_14 +4.01pp.

## Section 5 — Where the gains came from

The **fill rate rises monotonically with anchor regime** (favorites fill far more): ATP_MAIN
marketable+resting goes from 3% (r05_14) → 42% (r85_94). Favorite legs are routinely cheap at T-4h
relative to their anchor, so the 15¢-below bid is either already marketable (14% of heavy favorites)
or fills as the book firms up (28% resting). The lift on these favorite cells is both absolute (cheaper
entry → better hold outcomes) and capital-efficient (lower entry → higher ROI on the same +X exit).
Underdog cells show small-N lift driven by a handful of near-free fills (see caveat below).

## Section 6 — Observations

The dominant structural fact is the **universal-15¢-offset asymmetry**: a 15¢ offset is a large,
well-targeted discount for favorites (anchor 85–94¢ → bid 70–79¢, frequently reached) but **clamps to
a 1¢ bid for deep underdogs** (anchor 10¢ → bid −5¢ → clamp 1¢), which essentially never fills — so
underdog regimes are 96–99% miss_fallback and contribute almost no lift beyond a few near-free 1¢
fills. **The single universal rule is therefore a favorite-capture rule**; the underdog side is left
on the table. Path B v1's per-regime optima (2–3¢ offsets for underdogs) would be required to harvest
the underdog side — this v2 single-rule run deliberately measures the simplest deployable policy, and
its +2.93pp lift is achieved almost entirely on the favorite half of the board. Every regime cell
still shows positive lift, so the universal rule never *hurts* relative to baseline (misses fall back
to the exact atlas outcome).

## Section 7 — Realism caveats

These are **pre-realism** numbers. B25's 0.5–0.7× fill-realism discount (minute-cadence simulators
overcount achievable fills/exits) is **not applied** — deployment will see the exit-side realization
discounted, and the maker-entry fills themselves carry queue/sub-minute realism not modeled here. The
exit replay uses `size_qual_max_250` as a conservative lower-bound trigger (pre-T-20m target-hits not
added). The 15% of N's whose lift is small-N (underdog 1¢ fills) rest on few legs. The atlas remains
the strategy floor (+8.70%); this measures the entry-side ceiling maker placement adds on top
(+2.93pp blended, pre-realism), driven by the favorite half of the corpus.

## Validation gates (all PASS)

1. **Baseline reproduction:** $6,158.20 vs atlas $6,158.20 (ratio 1.0000, within ±2%) — capital exact $70,813.20. ✓
2. Row count 14,033. ✓
3. Execution-mode sanity: marketable not near-zero (r85_94 14%); favorite fill > underdog fill. ✓
4. Mean realized 5.58¢ > baseline 4.39¢. ✓
5. Maker capital $67,346 < atlas $70,813. ✓
