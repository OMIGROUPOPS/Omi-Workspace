# Pairing diagnostic — four-category spike volatility map atlas

Empirical bilateral-capable rate across all four committed categories. Pure derivation from `*_spike_perN.parquet` files in this directory; no tape walk. Relevant to B23 (bilateral capture mechanism) upstream feasibility funnel — how often does the corpus actually offer both legs of a paired event with valid T-20m anchors? This artifact answers that at corpus scale.

Convention: each match = one event. Each event has two N's (YES on each player). `event_ticker = ticker.rsplit('-', 1)[0]`. An event is "paired" if BOTH N's exist in this category's spike per-N parquet (i.e., both sides had valid T-20m anchors AND made it through the spike producer's filters).

## Per-category pairing table

| Category | n_N | n_events | n_paired_ev | n_unpaired_ev | paired% |
|----------|-----|----------|-------------|---------------|---------|
| ATP_MAIN | 4,137 | 2,230 | **1,907** | 323 | **85.52%** |
| WTA_MAIN | 3,683 | 2,033 | **1,650** | 383 | **81.16%** |
| ATP_CHALL | 5,326 | 3,053 | **2,273** | 780 | **74.45%** |
| WTA_CHALL | 887 | 509 | **378** | 131 | **74.26%** |

All sanity checks pass: `2 × n_paired + n_unpaired == n_N` for every category. Derived `event_ticker = ticker.rsplit('-',1)[0]` matches the stored `event_ticker` column for every row across all four categories.

## Corpus totals

- total_N = **14,033** (matches expected ✓)
- total_distinct_events = **7,825**
- total_paired_events = **6,208**
- total_unpaired_events = **1,617**
- **corpus_paired_rate = 79.34%**
- sanity: 2 × 6,208 + 1,617 = 14,033 == total_N ✓

## Pairing-rate gradient

The pairing rate sorts cleanly Main > Challenger and ATP_MAIN > WTA_MAIN > ATP_CHALL ≈ WTA_CHALL:

- ATP_MAIN: **85.52%** (highest)
- WTA_MAIN: 81.16%
- ATP_CHALL: 74.45%
- WTA_CHALL: 74.26% (lowest, within 0.2 pp of ATP_CHALL)

The Main↔Challenger gap is ~7 pp (Mains both > 80%, Challengers both ~74%). The ATP↔WTA gap within each tier is ~4 pp at Main, ~0.2 pp at Challenger.

## Per-N realized ROI under locked rule — paired vs unpaired, per category

| Category | Slice | N | Capital | Earn | ROI |
|----------|-------|---|---------|------|-----|
| ATP_MAIN | paired | 3,814 | $19,441.20 | +$1,593.20 | **+8.20%** |
| ATP_MAIN | unpaired | 323 | $1,562.20 | +$65.60 | +4.20% |
| WTA_MAIN | paired | 3,300 | $16,818.70 | +$1,658.60 | **+9.86%** |
| WTA_MAIN | unpaired | 383 | $1,727.20 | +$166.30 | +9.63% |
| ATP_CHALL | paired | 4,546 | $23,138.80 | +$1,713.10 | **+7.40%** |
| ATP_CHALL | unpaired | 780 | $3,680.90 | +$316.10 | +8.59% |
| WTA_CHALL | paired | 756 | $3,844.30 | +$597.00 | **+15.53%** |
| WTA_CHALL | unpaired | 131 | $599.90 | +$48.30 | +8.05% |

## Aggregate paired vs unpaired (all four combined)

| Slice | N | % corpus | Capital | Earn | ROI |
|-------|---|----------|---------|------|-----|
| paired | 12,416 | **88.48%** | $63,243.00 | +$5,561.90 | **+8.79%** |
| unpaired | 1,617 | **11.52%** | $7,570.20 | +$596.30 | **+7.88%** |

Paired N's are 88.5% of corpus and produce 90.3% of earnings ($5,561.90 / $6,158.20). Unpaired N's deliver +7.88% ROI — slightly below the paired +8.79% but still positive and trade-worthy on their own.

## Aggregate regime split — paired vs unpaired

| Regime | Slice | N | Capital | Earn | ROI |
|--------|-------|---|---------|------|-----|
| cheap (5–30c) | paired | 2,723 | $5,381.80 | +$2,096.40 | **+38.95%** |
| cheap (5–30c) | unpaired | 484 | $662.70 | +$301.80 | **+45.54%** |
| mid (31–65c) | paired | 5,961 | $28,676.90 | +$2,447.20 | +8.53% |
| mid (31–65c) | unpaired | 691 | $3,615.90 | +$175.00 | +4.84% |
| high (66–94c) | paired | 3,732 | $29,184.30 | +$1,018.30 | +3.49% |
| high (66–94c) | unpaired | 442 | $3,291.60 | +$119.50 | +3.63% |

## Structural patterns visible

1. **Cheap unpaired N's outperform cheap paired N's on ROI** (+45.54% vs +38.95% aggregate; pattern holds per-category: ATP_MAIN +45.67% vs +35.53%, WTA_MAIN +73.28% vs +39.42%, WTA_CHALL +73.27% vs +54.91%). When a low-priced underdog's anchor exists but its overdog partner's anchor doesn't, the underdog's spike data is included and tends to settle YES disproportionately often (or capture a big bounce) — the asymmetric-information pattern flagged in the chat-side ROY/MAR forensic probe, surfacing here at corpus scale.

2. **Mid-regime unpaired N's underperform mid paired N's** (+4.84% vs +8.53% aggregate). The middle of the spread is where the matching anchor most likely also existed; when it doesn't, the surviving N tends to be the loser side of a sloppily-traded event.

3. **High regime is essentially flat** across paired vs unpaired (+3.49% vs +3.63%) — the favorite-side trades carry minimal information about pairing.

4. **Challenger tours have ~11 pp lower pairing rates than Main tours** (74% vs 85%). Likely interpretation candidates (not asserted): less liquid markets, partial-event coverage, T-20m anchor more frequently missing on one side. The codebase's earlier ROY/MAR probe established that "anchor exists" is a non-trivial filter; this diagnostic shows it operates at ~25% of Challenger events vs ~17% of Main events.

5. **WTA tours show smaller paired-vs-unpaired ROI gap** at Main level (WTA_MAIN: 9.86% vs 9.63%, only 0.23 pp) **than ATP tours** (ATP_MAIN: 8.20% vs 4.20%, 4.0 pp gap). The unpaired ATP_MAIN N's are the worst-ROI cohort in the entire diagnostic (still positive, but notably lower). WTA_CHALL shows the opposite pattern from ATP — paired vastly outperforms unpaired (+15.53% vs +8.05%, 7.5 pp), consistent with WTA_CHALL's higher cheap-unpaired ROI being a small-N outlier within the smallest category.

## Implications for B23 bilateral capture (descriptive only)

The 79.34% corpus paired rate is the upper-bound feasibility for any B23 bilateral-capture mechanism: at most ~79% of events offer a matched anchor on both sides at T-20m. The remaining ~21% of events are unilaterally-anchored — bilateral strategies cannot operate on them at the T-20m anchor point. The 11.52% unpaired N's are still individually tradeable (positive ROI), but only as single-leg trades.

Whether realized B23 capture matches the 79% feasibility ceiling depends on downstream factors (depth, fill, sizing, simultaneity-of-fills) addressed elsewhere. This diagnostic establishes only the anchor-existence upper bound.

## Cross-references

- LESSONS **B23** (bilateral mechanism)
- B23 amendment **2026-05-06** (funnel-layer disambiguation)
- LESSONS **E18** (70.7% double-cash anchor)
- LESSONS **E21** (per-cell bilateral rate)
- **U4 Phase 2** (76.4% high-volume conditional rate)

Read-only artifact. No new computation beyond joining on `event_ticker`. All numbers derived from the four committed `*_spike_perN.parquet` files in this directory.
