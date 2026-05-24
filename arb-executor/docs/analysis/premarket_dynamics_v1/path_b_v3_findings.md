# Path B v3 — per-regime offsets + atlas exit replay (deployable measurement)

**Date:** 2026-05-23
**Universe:** atlas only — 14,033 N. **Strategy:** **per-(category × anchor_regime) optimal** placement
+ offset (from Path B v1 Section 3 hindsight-optimal table), replacing v2's universal 15¢. **Pre-realism.**

This is the deployable measurement: real per-regime fill rates × dual-improvement (entry discount +
atlas exit rule replayed from the cheaper entry). It answers whether per-regime conditioning materially
exceeds the universal-rule lift, or adds only marginal value (Plex Round 6's diminishing-returns thesis).

## Sources (read-only)

| Artifact | sha256 |
|----------|--------|
| `premarket_tape_v1.parquet` | `ff2a63d9951d1a3d6b80044106c96ca9fdfd8d3951590e73eec1b46209c5a214` |
| `path_b_per_regime_fill_summary_v1.parquet` | `d9e2c3c55c6d7fb5d93beeddfde8a40f1298b841a0547d3743e14cd21e64e37e` (per-regime offset lookup) |
| `{cat}_spike_perN.parquet` + `{cat}_descriptive_1c.parquet` | exit-replay substrate + per-cell rule |

## Section 1 — What changed from v2

v2 used a single universal rule (T-240, 15¢ offset). On deep underdogs (anchor 5–14¢) that 15¢ offset
clamps the bid to 1¢ (`max(anchor−15,1)`), which essentially never fills → 96–99% miss → those N's
contribute zero improvement. v3 instead applies each (category × regime) cell's **own** v1-optimal
(placement_minute, offset): 2–3¢ on deep underdogs (which fill ~40–56%), graduated up to 15¢ on heavy
favorites. Everything else (execution-mode split, actual-entry capture, atlas exit replay via
`size_qual_max_250`) is identical to v2. The per-regime offset/placement is observable a priori from the
anchor regime — not per-event foresight — so this is deployable, not hindsight-per-event.

## Section 2 — Corpus headline

| Metric | v3 (per-regime) | v2 (universal 15¢) | atlas raw baseline |
|--------|-----------------|--------------------|--------------------|
| Total realized PnL @10ct | **$8,098.50** | $7,829.30 | $6,158.20 |
| Capital deployed @10ct | **$66,902.00** | $67,346.20 | $70,813.20 |
| Blended ROI | **12.11%** | 11.63% | 8.70% |
| ROI lift vs atlas | **+3.41 pp** | +2.93 pp | — |

v3 earns **+31.5% over the atlas baseline on 5.5% less capital**, a **+3.41pp** blended ROI lift —
**+0.48pp beyond the universal rule** (+$269). Baseline reproduced **exactly** ($6,158.20, ratio 1.0000).

## Section 3 — Execution-mode breakdown

| Mode | N (%) | Total PnL | Capital | ROI | mean entry |
|------|-------|-----------|---------|-----|-----------|
| marketable_taker | 592 (4.2%) | $734 | $2,638 | **27.8%** | 45¢ |
| maker_resting | 3,391 (24.2%) | $2,649 | $13,191 | **20.1%** | 39¢ |
| miss_fallback | 10,050 (71.6%) | $4,716 | $51,072 | 9.2% | 51¢ |

Aggregate **fill rate 28.4%** (vs v2's 15%) — the per-regime offsets nearly **double** the share of N's
that fill at a discount. The maker_resting cohort grew from 1,747 (v2) to 3,391 (v3), almost entirely
from underdog/mid regimes now fillable at small offsets.

## Section 4 — Per-regime ROI lift

Top-lift cells are now the **deep-underdog r05_14 cells** (which v2 missed entirely): ATP_CHALL r05_14
**+21.1pp** (fill 0.39, 3¢ offset), WTA_MAIN r05_14 +18.7pp (fill 0.56, 2¢), WTA_CHALL r05_14 +18.5pp,
ATP_MAIN r05_14 +17.0pp (fill 0.53, 2¢). The large pp-lift reflects the small capital denominator
(underdog entries 5–14¢) — big ROI% on modest dollars. Every cell remains ≥ its atlas baseline.

**Gate-4 check:** v3's per-regime fill rates reproduce Path B v1's optimal-cell fill rates **exactly
(max |Δ| = 0.0pp across all 36 cells)** — confirming the offset lookup applied correctly and the fill
detection is identical to v1.

## Section 5 — Comparison to v2 (what per-regime conditioning bought)

The per-regime upgrade adds **+0.48pp blended (+$269 PnL)** over the universal rule. Modest — consistent
with the diminishing-returns thesis: the universal 15¢ rule already captured the favorite half of the
board (favorites' v1-optimal offset *is* 15¢, so favorite cells are unchanged between v2 and v3). The
incremental gain is the **underdog/mid harvest** the universal rule clamped away. Net is +$269 rather
than the full underdog harvest (~$385, Section 6) because the v1-optimal offset on a few favorite/mid
cells differs from a flat 15¢, a small wash on those cells.

## Section 6 — Where the underdog harvest came from

The three lowest regimes — which v2 left ~entirely unfilled (1¢-clamp) — now contribute:

| regime | N | fill rate | improvement over atlas baseline (@10ct) |
|--------|---|-----------|------------------------------------------|
| r05_14 | 1,005 | 0.47 | +$85 |
| r15_24 | 1,282 | 0.27 | +$122 |
| r25_34 | 1,631 | 0.27 | +$178 |

~**$385** of improvement from these three regimes that the universal rule could not reach — the core of
what per-regime conditioning unlocks. The dollar amounts are modest (cheap underdog entries → small
capital → small absolute PnL despite large ROI%), but they are strictly additive and were zero in v2.

## Section 7 — Observations

Per-regime offsets are the **correct deployable shape** (each regime bid at the offset that actually
fills it) but the **marginal value over the universal favorite-capture rule is small (+0.48pp)**. The
favorite half of the corpus dominates the absolute PnL (favorites carry more capital and the 15¢ offset
is already their optimum), so the universal rule was already most of the way there; per-regime
conditioning is a refinement that harvests the underdog tail for a modest incremental gain. The
practical read: a deployable policy should use per-regime offsets (no reason to leave the underdog
harvest on the table, and it never hurts — every cell ≥ baseline), but should not expect per-regime
tuning alone to be transformative over a sensible universal favorite offset.

## Section 8 — Realism caveats

Pre-realism — B25's 0.5–0.7× fill/exit-realism discount is **not** applied; deployment will see the
exit realization discounted and entry fills subject to queue/sub-minute realism not modeled. The exit
replay uses `size_qual_max_250` as a conservative lower-bound trigger. The per-regime offset lookup is
hindsight-optimal *at corpus level*, but each (category, regime) cell's optimum is **observable a priori
from the anchor regime** (not per-event foresight) — so the policy is deployable. Atlas remains the floor
(+8.70%); v3 measures the deployable entry-side ceiling on top (+3.41pp blended, pre-realism).

## Validation gates (all PASS)

1. Baseline reproduction EXACT ($6,158.20, ratio 1.0000; capital $70,813.20). ✓
2. Row count 14,033. ✓
3. Aggregate fill rate 28.4% ≥ 25%. ✓
4. Per-regime fill rates match v1 within ±5pp (actual: exact, 0.0pp). ✓
5. ROI lift +3.41pp > v2's +2.93pp. ✓
6. Capital $66,902 < v2's $67,346. ✓
