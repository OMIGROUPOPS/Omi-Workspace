# ATP_MAIN pair-aware exit cell reanalysis (counterpart-conditioned) — 2026-05-27 11:49 PM ET

**Single concern. Read-only. In-sample. No commit. Stage only if all G gates pass.**

## Methodology
- 1,881 real paired matches (both contracts each); legA = higher-priced contract, legB = lower; `legA_settle+legB_settle=1.0` (real outcome).
- peak_trade per leg = `legX_peak_trade_inmatch_cents` (raw `price_high`, **no depth filter**); cost basis = `anchor − clip(drift_low_vs_anchor,0,5)` (per-ticker, conservative 5c cap).
- target hit = `peak_trade ≥ anchor + target`; capture = exit at `anchor+target`; else ride to `legX_realized_at_settlement_cents`. per-match net = legA + legB PnL. ROI = net / (costA+costB).
- **Two objectives tested per matchup-group:** `aggregate` net (separable → equals per-leg-independent) and `median` per-match net (non-separable → the genuinely counterpart-aware one). Both gated on bootstrap CI-lower(mean net) > 0, with v6 per-leg fallback.

## A. Inputs verified
primitive 1,881 (sha 564c1938) · drift_envelope 4,137 (fb61d47e) · v6 bands 31 (a9aee4ec). legA≥legB and one-winner confirmed on all 1,881.

## B. v6 baseline — the floor
- aggregate **$1384.80 @10ct** / **$692.40 @5ct**; EV/match **$0.7362**
- per-match net (cents): {'mean': 7.362, 'p10': -38.0, 'p25': -14.0, 'median': 12.0, 'p75': 31.0, 'p90': 46.0}
- ROI on traded capital: {'mean': 0.079, 'p10': -0.383, 'p25': -0.143, 'median': 0.122, 'p75': 0.323, 'p90': 0.484}
- match hit rates: ≥1 leg captures **0.983**, both **0.510**, neither **0.017**

## C. Cells by match density (quantile-adaptive per axis)
- Method: per-axis quantile edges (octiles) so cells are finer where matches are dense. high(legA) edges `[51, 56, 61, 65, 69, 74, 79, 86, 99]`, low(legB) edges `[6, 17, 24, 29, 34, 39, 42, 46, 77]`.
- Matches cluster on the anti-diagonal (anchorA+anchorB ≈ 102±2c), so populated (hi×lo) groups are few and large.
- Coverage by MIN_MATCHES (fraction of 1,881 matches in optimizable groups):

| MIN_MATCHES | optimizable groups | coverage |
|---|---|---|
| 30 | 10 | 84.7% |
| 50 | 10 | 84.7% |
| 75 | 9 | 82.0% |

Chosen **MIN_MATCHES = 50** (conviction/coverage balance). Thin groups + CI-fails → v6 fallback.

## D/F — objective = `agg` (separable = per-leg independent)
Per-group selected targets:

| hi cell | lo cell | N | tgt_hi | tgt_lo | opt? | net med | ROI med | $@10ct | v6 net med (same) | CI-lo |
|---|---|---|---|---|---|---|---|---|---|---|
| 86-98 | 6-16 | 204 | HOLD | 59 | fallback | 12.0 | 0.1237 | 189.6 | 12.0 | 5.16 |
| 79-85 | 17-23 | 193 | 14 | 56 | Y | 0.0 | 0.0 | 281.7 | 1.0 | 9.92 |
| 65-68 | 34-38 | 187 | HOLD | 39 | Y | 3.0 | 0.0309 | 198.7 | 15.0 | 5.86 |
| 56-60 | 42-45 | 186 | 30 | 34 | Y | -8.0 | -0.0825 | 209.8 | 24.0 | 6.05 |
| 51-55 | 46-76 | 181 | 6 | 13 | Y | 24.0 | 0.2474 | 170.9 | 19.0 | 5.73 |
| 69-73 | 29-33 | 180 | 26 | 30 | Y | 2.0 | 0.0208 | 229.6 | 32.0 | 7.62 |
| 74-78 | 24-28 | 176 | 14 | 71 | Y | -4.0 | -0.0417 | 175.5 | 12.0 | 5.1 |
| 61-64 | 39-41 | 156 | 35 | 58 | Y | 2.0 | 0.0211 | 180.0 | 14.5 | 7.18 |
| 56-60 | 46-76 | 79 | 11 | 10 | Y | 26.0 | 0.268 | 60.4 | -9.0 | 1.53 |
| 61-64 | 34-38 | 51 | 34 | 4 | Y | 41.0 | 0.4184 | 71.1 | 14.0 | 3.09 |

**Corpus (agg):** aggregate **$1841.2 @10ct** (v6 $1384.8, Δ +456.4) · EV/match $0.9788
- per-match net: {'mean': 9.788, 'p10': -28.0, 'p25': -8.0, 'median': 2.0, 'p75': 26.0, 'p90': 66.0}
- ROI: {'mean': 0.104, 'p10': -0.278, 'p25': -0.083, 'median': 0.021, 'p75': 0.271, 'p90': 0.704}
- match hits: ≥1 0.936, both 0.324, neither 0.064
- Δ vs v6: median net **-10.0c**, median ROI **-0.1016**, p10 net +10.0c, improved 791 / degraded 562
- negative-median groups (N≥10): **8** — [((56, 60), (39, 41), 16, -11.0), ((56, 60), (42, 45), 186, -8.0), ((61, 64), (42, 45), 21, -12.0), ((69, 73), (34, 38), 25, -8.0), ((74, 78), (24, 28), 176, -4.0), ((74, 78), (29, 33), 22, -11.0), ((79, 85), (24, 28), 18, -0.5), ((86, 98), (17, 23), 28, -1.0)]
- optimized groups: 9 of 10

## D/F — objective = `median` (counterpart-aware, non-separable)
Per-group selected targets:

| hi cell | lo cell | N | tgt_hi | tgt_lo | opt? | net med | ROI med | $@10ct | v6 net med (same) | CI-lo |
|---|---|---|---|---|---|---|---|---|---|---|
| 86-98 | 6-16 | 204 | HOLD | 7 | Y | 20.0 | 0.2031 | 140.8 | 12.0 | 2.64 |
| 79-85 | 17-23 | 193 | 14 | 16 | Y | 32.0 | 0.3232 | 175.0 | 1.0 | 4.1 |
| 65-68 | 34-38 | 187 | HOLD | 3 | fallback | 15.0 | 0.1613 | 97.4 | 15.0 | -2.92 |
| 56-60 | 42-45 | 186 | 2 | 41 | Y | 45.5 | 0.4596 | 169.7 | 24.0 | 3.29 |
| 51-55 | 46-76 | 181 | 23 | 13 | Y | 38.0 | 0.38 | 125.4 | 19.0 | 1.57 |
| 69-73 | 29-33 | 180 | HOLD | 10 | Y | 41.5 | 0.4214 | 186.7 | 32.0 | 4.86 |
| 74-78 | 24-28 | 176 | HOLD | 5 | fallback | 12.0 | 0.125 | 68.1 | 12.0 | -7.48 |
| 61-64 | 39-41 | 156 | 35 | 5 | Y | 43.0 | 0.4388 | 132.0 | 14.5 | 1.46 |
| 56-60 | 46-76 | 79 | 38 | 2 | fallback | -9.0 | -0.0918 | 46.5 | -9.0 | -4.43 |
| 61-64 | 34-38 | 51 | 34 | 8 | Y | 44.0 | 0.4444 | 65.5 | 14.0 | 1.84 |

**Corpus (median):** aggregate **$1281.0 @10ct** (v6 $1384.8, Δ -103.8) · EV/match $0.6810
- per-match net: {'mean': 6.81, 'p10': -51.0, 'p25': -22.0, 'median': 10.0, 'p75': 41.0, 'p90': 47.0}
- ROI: {'mean': 0.073, 'p10': -0.526, 'p25': -0.228, 'median': 0.102, 'p75': 0.426, 'p90': 0.495}
- match hits: ≥1 0.934, both 0.388, neither 0.066
- Δ vs v6: median net **-2.0c**, median ROI **-0.0204**, p10 net -13.0c, improved 709 / degraded 415
- negative-median groups (N≥10): **7** — [((56, 60), (39, 41), 16, -11.0), ((56, 60), (46, 76), 79, -9.0), ((61, 64), (42, 45), 21, -12.0), ((69, 73), (34, 38), 25, -8.0), ((74, 78), (29, 33), 22, -11.0), ((79, 85), (24, 28), 18, -0.5), ((86, 98), (17, 23), 28, -1.0)]
- optimized groups: 7 of 10

## E. Assembled directional config + fallback
- Optimizable coverage at MIN=50: 84.7% of matches; remainder → v6 per-leg fallback.
- Singletons: 323 single-leg events (one side in cohort) + 375 unpaired N. ≈ **14.5%** of events are single-leg in-sample → counterpart-aware config cannot apply; they fall back to single-leg v6. Live, the bot lays both legs, so most live matches are paired, but unfilled/skipped legs reproduce this singleton rate.

## G. Staging gates

| gate | aggregate obj | median obj |
|---|---|---|
| roi_med | False | False |
| tot10 | True | False |
| no_neg | False | False |
| p10 | True | False |
| PASS_ALL | False | False |

**DECISION: DO NOT STAGE.** Neither objective passes all gates.

### Gap (precise)
- **Aggregate objective** beats v6 on aggregate \$ (+$456, +33%), EV, and p10 tail — but **fails the median floor** (net 2c vs v6 12c) and leaves 8 negative-median groups. It is separable (= per-leg independent), so it reproduces the 65c44e1 mean-vs-median tradeoff: it fattens the right tail (p90 66c vs v6 46c) at the median's expense.
- **Median objective** (genuinely counterpart-aware) **still cannot beat v6's median** (net 10c vs 12c), and loses on aggregate (−$104) and tail (p10 -51c vs −38c). v6's zone-aware R is already near the in-sample median optimum.
- **Structural floor:** negative-median groups (e.g. 56-60×42-45 N=186, 74-78×24-28 N=176) are **vig-driven** — paid ~102c for ~100c of combined settlement value; no exit target removes the ~2c median vig when the spike does not hit. This is not fixable by cell-target reoptimization.

## Caveats
- **In-sample.** Targets fit on the same 1,881 matches measured; the aggregate +$456 is in-sample curve-fit to the realized right tail. Out-of-sample validation required before any deploy.
- **Raw-peak realism (no depth filter):** hit assumes a resting sell fills on any print ≥ target; thin prints may not fill 10ct. Inflates absolute $ uniformly (cancels in v6-vs-candidate deltas).
- **Drift-discount cost basis** `anchor − clip(dip,0,5)`: 5c-capped conservative bound; identical for v6 and candidate.
- **Bootstrap CI overlaps:** many group target picks have wide CI; single-cent targets are statistically soft.
- **Singleton fallback:** ~14.5% of events single-leg → v6 fallback (counterpart-aware inapplicable).
- **Deployability:** directional cells require the exit lookup to know BOTH legs' anchors. Current `_v4_apply_exit` calls `exit_rule_for(category, fill_price)` — a 1D lookup on the leg's own fill only. The bot lays both legs (counterpart anchor is knowable) but the exit path would need code changes to use it. Moot here (not staged).

---

# REOPENED — corrected gate (daily aggregate ROI) — 2026-05-27 11:57 PM ET

**The prior median-net floor was wrong.** Operator objective = daily ROI = Σnet / Σcapital (aggregate, not median of per-match ROI). Median floor removed. The aggregate-objective config ($1,841.2 @10ct, +$456.4 / +33% vs v6 $1,384.80) is a higher daily ROI and is interrogated below.

## A. Capture vs settlement decomposition (the decisive number)
Per leg: **Source 1 (capture)** = legs that hit target in-match `(anchor+target)−cost` (repeatable, who-won-independent). **Source 2 (settlement)** = ride legs at realized 0/100 `settle−cost` (curve-fit to who won). **Generalizable floor** marks rides at fair=anchor (removes who-won luck).

| component ($@10ct) | config | v6 | delta |
|---|---|---|---|
| TOTAL (realized) | 1841.2 | 1384.8 | **+456.4** |
| Source 1 — capture (repeatable) | 5882.8 | 4666.8 | **+1216.0** |
| Source 2 — settlement (curve-fit) | -4041.6 | -3282.0 | **-759.6** |
| GENERALIZABLE (rides@fair=anchor) | 6335.0 | 4980.6 | **+1354.4** |

**Verdict:** the +$456 total is **+$1216 repeatable capture MINUS $760 settlement drag** — i.e. settlement *hurts* the config; 100% of the gain (and more) is in-match capture. The capture-only / generalizable floor (+$1354) **beats v6 decisively**. The +$456 is real in-match capture edge, NOT settlement curve-fit.

## B. Corrected vig analysis (prior 'structural vig' claim was wrong)
Negative-median groups split by capture participation. They are NOT a neither-capture vig tail — nearly all have ≥1 capture:

| hi cell | lo cell | N | frac ≥1 cap | frac neither | net med (all) | net med (≥1 cap) | net med (neither) |
|---|---|---|---|---|---|---|---|
| 56-60 | 39-41 | 16 | 1.0 | 0.0 | -11.0 | -11.0 | nan |
| 56-60 | 42-45 | 186 | 1.0 | 0.0 | -8.0 | -8.0 | nan |
| 61-64 | 42-45 | 21 | 1.0 | 0.0 | -12.0 | -12.0 | nan |
| 69-73 | 34-38 | 25 | 1.0 | 0.0 | -8.0 | -8.0 | nan |
| 74-78 | 24-28 | 176 | 1.0 | 0.0 | -4.0 | -4.0 | nan |
| 74-78 | 29-33 | 22 | 1.0 | 0.0 | -11.0 | -11.0 | nan |
| 79-85 | 24-28 | 18 | 1.0 | 0.0 | -0.5 | -0.5 | nan |
| 86-98 | 17-23 | 28 | 0.893 | 0.107 | -1.0 | -1.0 | -1.0 |

**Corrected:** negative medians have frac≥1cap ≈ 1.0 (not the ~6% neither tail). The negative median is the deep target on one leg forcing a ride-to-loss the captured leg doesn't fully offset in the typical match — a median/aggregate tradeoff, accepted under the daily-ROI objective. Not structural vig.

## C. Corrected gate (daily aggregate ROI; median floor dropped)

| gate | value | pass |
|---|---|---|
| aggregate $ @10ct beats v6 | $1841.2 vs $1384.8 | True |
| aggregate ROI (Σnet/Σcapital) beats v6 | 0.1015 vs 0.0763 | True |
| EV per match beats v6 | $0.9788 vs $0.7362 | True |
| p10 per-match net not worse >10c | -28c vs -38c (BETTER) | True |
| **capture-only beats v6 (D — decisive)** | +$1354 | **True** |
| hit ≥1-leg not worse than v6 | config 0.9362 vs v6 0.9830 | **False** |

**CORRECTION:** the prompt cited 'v6's 0.936' — that figure is actually the **config's** ≥1-capture rate. **v6's true ≥1-capture rate is 0.9830** (1849/1881). So the config **regresses −4.7pp** on capture breadth (1761 vs 1849 matches with ≥1 capture) — the expected flip side of deeper targets (fewer but larger captures). 93.6% is still high, but this is a real regression vs v6, flagged for the call.

## E. Cell-by-cell config vs v6 (where the capture gain concentrates)

| hi cell | lo cell | N | cfg tgt_hi | v6 R hi(mid) | cfg tgt_lo | v6 R lo(mid) | cap\$ cfg | cap\$ v6 | cap\$ Δ |
|---|---|---|---|---|---|---|---|---|---|
| 61-64 | 39-41 | 156 | 35 | 8 | 58 | 1 | 757.1 | 327.4 | **+430** |
| 74-78 | 24-28 | 176 | 14 | 8 | 71 | 3 | 663.1 | 332.7 | **+330** |
| 69-73 | 29-33 | 180 | 26 | 17 | 30 | 12 | 722.2 | 495.4 | **+227** |
| 56-60 | 42-45 | 186 | 30 | 18 | 34 | 3 | 831.6 | 619.7 | **+212** |
| 79-85 | 17-23 | 193 | 14 | 1 | 56 | 52 | 721.4 | 572.7 | **+149** |
| 61-64 | 34-38 | 51 | 34 | 8 | 4 | 3 | 168.3 | 70.3 | **+98** |
| 86-98 | 6-16 | 204 | v6 | 2 | v6 | 6 | 326.8 | 326.8 | **+0** |
| 51-55 | 46-76 | 181 | 6 | 11 | 13 | 24 | 396.1 | 442.1 | **-46** |
| 65-68 | 34-38 | 187 | HOLD | 33 | 39 | 3 | 414.6 | 474.8 | **-60** |
| 56-60 | 46-76 | 79 | 11 | 18 | 10 | 24 | 185.5 | 308.8 | **-123** |

**Capture gain concentrates in 5 mid-favorite cells** (61-64×39-41 +\$430, 74-78×24-28 +\$330, 69-73×29-33 +\$227, 56-60×42-45 +\$212, 79-85×17-23 +\$149) where the config sets **much deeper targets** (e.g. 61-64 high: 35 vs v6 8; low: 58 vs v6 1). A few cells go shallower/HOLD with small negative capture delta (56-60×46-76 −\$123, 65-68×34-38 −\$60).

## CORRECTED STAGING DECISION
- Operator's decisive rule (D): **capture-only aggregate beats v6** → **True** (+$1354 generalizable, +$1216 realized capture).
- **DECISION: STAGED** `atp_main_exit_cells_v7_paired_candidate.parquet` (directional cell targets + fallback row).
- **Caveat for operator call (does NOT block per D, but material):** config ≥1-capture rate 0.936 vs v6 0.983 (−4.7pp). Deeper targets capture bigger but in fewer matches.

## Caveats (reopened)
- **In-sample:** capture target levels are fit to the realized in-sample peak_trade distribution. Capture is generalizable in KIND (price spikes recur, who-won-independent) but the SPECIFIC target cents are in-sample — out-of-sample validation still required before deploy.
- **The honest generalizable improvement is the capture-only / fair-marked floor (+$1354), not the realized total (+$456)** — the realized total happens to be LOWER because settlement luck ran against the config this corpus (−$760).
- Raw-peak no-depth realism; 5c-capped drift cost basis; bootstrap-CI overlaps (single-cent targets soft); ~14.5% singleton fallback; directional cells need 2D exit lookup (current `exit_rule_for(category, fill_price)` is 1D — code change required to deploy).

---

# PART 1-4 — pairing proof, settlement equivalence, clean reframe, frequency floor — 2026-05-28 12:17 AM ET

## PART 1 — Pairing is real player-A-vs-player-B (PROVEN)
Sample (10 events) all share the full event prefix, differ only in the player code, anchors sum ~100-105c, exactly one winner. Examples: `KXATPMATCH-25AUG01COBMAR` → MAR(53c) vs COB(50c) sum 103; `KXATPMATCH-25AUG01NAKSHE` → SHE(72c) vs NAK(32c) sum 104.

Across all 1,881:
- legA & legB share event prefix AND differ only in player code: **1,881 / 1,881**
- legA_settle + legB_settle == 1.0 (exactly one player wins): **1,881 / 1,881**
- anchorsum ∈ [98,106]: **1,754 / 1,881**; distribution min 99 / p50 102 / p99 128 / max 158 (the 127 high-sum events are genuine pairs with wide premarket asks, not pairing errors)
- **anomalies (legs not the two players of one match, or settle≠1): 0**

**Verdict: every paired event is genuinely the two sides of one real binary match. Pair analysis is valid.**

## PART 2 — 'settlement' and the 99-ceiling / 1-floor are the SAME thing
peak_trade distribution split by realized outcome:

| leg outcome | n | peak min | p10 | p25 | p50 | p75 | p90 | max | mean |
|---|---|---|---|---|---|---|---|---|---|
| WINNERS (settle=1) | 1,880 | 73 | 99 | 99 | 99 | 99 | 99 | 99 | 98.8 |
| LOSERS (settle=0) | 1,880 | 4 | 24 | 39 | 61 | 78 | 91 | 99 | 58.5 |

Winners reach 99c (98.4% ≥95c) → a winner fills ANY target up to 99. Losers' peak is their in-match high → only low targets fill, otherwise the contract rides to ~1. **So sweeping exit targets up to 99 with peak_trade as the fill signal automatically encodes settlement — no separate payout mechanism needed (Option X). 'Settlement' = peak reached the 99 ceiling (winner) or rode to the 1 floor (loser).**

## PART 3 — clean peak-only reframe (exit price E; net = E−cost if peak≥E, else settle−cost)
Re-confirmed under the clean framing (no settlement-source split):

| config | aggregate $ @10ct | ROI on traded capital |
|---|---|---|
| v6 baseline | $1384.80 | 0.0763 |
| staged candidate (v7_paired) | $1841.20 | 0.1015 |

Numbers are identical to prior (the 'settlement source' split was just a reframing of the same exit math). Staged candidate beats v6 on aggregate $ and ROI.

## PART 4 — capture frequency + frequency-floored config
- match-level ≥1-leg capture: v6 **0.9830** vs staged candidate **0.9362** (Δ -0.0468).
- Per-cell ≥1-capture regression (where the candidate's deeper targets lose frequency):

| hi cell | lo cell | N | ≥1 v6 | ≥1 cand | Δ |
|---|---|---|---|---|---|
| 65-68 | 34-38 | 187 | 1.0 | 0.529 | -0.471 |
| 61-64 | 39-41 | 156 | 1.0 | 0.942 | -0.058 |
| 69-73 | 29-33 | 180 | 1.0 | 0.994 | -0.006 |
| 51-55 | 46-76 | 181 | 1.0 | 1.0 | +0.000 |
| 61-64 | 34-38 | 51 | 1.0 | 1.0 | +0.000 |
| 56-60 | 46-76 | 79 | 1.0 | 1.0 | +0.000 |
| 56-60 | 42-45 | 186 | 1.0 | 1.0 | +0.000 |
| 74-78 | 24-28 | 176 | 1.0 | 1.0 | +0.000 |
| 86-98 | 6-16 | 204 | 0.936 | 0.936 | +0.000 |
| 79-85 | 17-23 | 193 | 0.948 | 1.0 | +0.052 |

**The regression is concentrated in ONE cell: 65-68×34-38 (N=187), 1.000→0.529 (−0.47)** — the candidate set HOLD on its high leg, so that leg never captures. One cell improves (79-85×17-23 +0.05).

### Frequency-floored re-optimization (constraint: per-cell ≥1-rate ≥ v6's; maximize aggregate)

| config | aggregate $ @10ct | Δ vs v6 | ROI | ≥1-capture |
|---|---|---|---|---|
| v6 baseline | $1384.80 | — | 0.0763 | 0.9830 |
| v7_paired (unconstrained) | $1841.20 | +$456 | 0.1015 | 0.9362 |
| **v7_freqfloor** | **$1789.70** | **+$405** | 0.0986 | **0.9942** |

**The frequency-floored config keeps ≥1-capture at 0.994 (≥ v6's 0.983) AND still beats v6 by +$405 (+29%) on aggregate.** Enforcing the floor costs only ~$52 of the unconstrained +$456 gain while removing the capture-breadth regression. **Staged** as `atp_main_exit_cells_v7_freqfloor_candidate.parquet`.

### Staging summary (two candidates for operator review)
- `atp_main_exit_cells_v7_paired_candidate.parquet`: +$456 aggregate, but ≥1-capture 0.936 < v6 0.983.
- `atp_main_exit_cells_v7_freqfloor_candidate.parquet`: +$405 aggregate, ≥1-capture 0.994 ≥ v6 — **no frequency regression** (recommended for OOS validation).

### Caveats (unchanged)
- **In-sample** target cents fit to this corpus; capture generalizes in kind (price spikes recur, who-won-independent) but specific targets need OOS validation before deploy.
- Raw-peak no-depth realism; 5c-capped drift cost basis; bootstrap-CI overlaps; ~14.5% singleton fallback; directional cells require a 2D exit lookup (current `exit_rule_for(category, fill_price)` is 1D — code change to deploy).

---

# COST = ANCHOR (honest foundation, NO drift discount) — 2026-05-28 12:29 AM ET

**Correction to all prior sections.** Cost basis = `anchor_cents` exactly (the T-20m cell price you pay). The earlier `anchor − clip(drift_low_vs_anchor,0,5)` discount was an unfounded assumption that baked premarket drift into the entry. Here you pay the cell price, period; premarket drift is **separate upside, to be quantified later — not baked in.**

Model: enter at anchor; target T captures T cents iff `peak_trade ≥ anchor + T`, else resolve at final (99 winner / 1 loser, already in peak per Part 2). Sweep T=1..(99−anchor). ROI denominator = anchorA + anchorB.

## Impact of removing the drift discount
- **v6 baseline collapses from $1,384.80 → $137.20 @10ct** (ROI 0.71%). The ~$1,247 difference was the drift discount, NOT exit edge — i.e. ~90% of the prior apparent P&L was the (now-removed) drift assumption.
- At honest cost, v6 is only marginally profitable; the real exit-target edge over it is correspondingly smaller in absolute terms.

## A–D. Results (cost=anchor)

| config | agg \$@10ct | \$@5ct | ROI (Σnet/Σanchor) | EV/match | ≥1-capture | both | median net |
|---|---|---|---|---|---|---|---|
| **v6 baseline** | $137.2 | $68.6 | 0.71% | $0.073 | 0.983 | 0.510 | 6c |
| agg (unconstrained, CI-gated) | $268.8 | $134.4 | 1.39% | $0.143 | 0.983 | 0.427 | -4c |
| **freqfloor (CI-gated, ≥1≥v6)** | **$183.5** | $91.8 | **0.95%** | $0.098 | **0.988** | 0.479 | -1c |

**Deltas vs v6:** agg +$131.6 (ROI +0.68pp); freqfloor **+$46.3** (ROI +0.24pp), ≥1-capture 0.988 ≥ v6 0.983 (no regression).

Net-percentile detail:
- v6: {'mean': 0.73, 'p10': -45.0, 'p25': -20.0, 'median': 6.0, 'p75': 26.0, 'p90': 36.0}
- agg: {'mean': 1.43, 'p10': -42.0, 'p25': -17.0, 'median': -4.0, 'p75': 22.0, 'p90': 47.0}
- freqfloor: {'mean': 0.98, 'p10': -43.0, 'p25': -18.0, 'median': -1.0, 'p75': 22.0, 'p90': 44.0}

## E. Staging (cost=anchor)
- freqfloor beats v6 on aggregate ROI (0.95% > 0.71%) with no ≥1-capture regression (0.988 ≥ 0.983) → **STAGED** `atp_main_exit_cells_v7_anchor_freqfloor.parquet`.
- Only **2 matchup groups** clear both the frequency floor AND the CI-lower>0 gate at honest cost (the rest fall back to v6):

| hi cell | lo cell | N | tgt_hi (v6) | tgt_lo (v6) | capture\$ Δ vs v6 | group ROI |
|---|---|---|---|---|---|---|
| 69-73 | 29-33 | 180 | 25 (17) | 30 (12) | +$235 | 5.6% |
| 79-85 | 17-23 | 193 | 14 (1) | 56 (52) | +$148 | 8.1% |

## F. Map data exported
- `data/durable/spike_volatility_map/atp_main_exit_map.json` — per matchup-group (10 populated, MIN=50): cell ranges, N, chosen vs v6 targets, group \$/ROI/≥1/both, capture-\$ delta; cell axis edges; corpus totals (v6, freqfloor, agg).

## Honest read
- At true cost (anchor), the exit-target edge over v6 is **modest: +$46 (freqfloor) / +$132 (agg)** on 1,881 matches — a far cry from the drift-inflated +$405/+$456. Most of the previously-reported gain was the drift discount in the cost basis.
- **Premarket drift is real but SEPARATE upside** — to be measured on its own (how much below anchor the bot actually fills), not assumed into the exit cost basis.
- Still **in-sample**; OOS validation required. Directional cells still need a 2D exit lookup to deploy.

---

# DAILY ROI (correct denominator) + FULL SPECTRUM AT OPTIMAL TARGETS — 2026-05-28 12:40 AM ET

**Correcting the denominator.** Prior 'ROI 0.71%/0.95%' was Σnet/Σcapital blended across all 1,881 matches (~10 months) — meaningless for daily consistency. Below: per-day ROI = (day net)/(day capital wagered), distribution across actual ET trading days. cost=anchor, 10ct.

## PART 1 — Daily ROI
- **251 distinct ET trading days.** matches/day: min 1, median 7, max 32. Median capital wagered/day @10ct: $71.

### All days (n=251) — daily ROI distribution
| config | median ROI | mean ROI | p10 | p25 | p75 | p90 | frac days green | med daily $ | worst day $ | best day $ |
|---|---|---|---|---|---|---|---|---|---|---|
| v6 | 0.96% | 1.89% | -15.5% | -6.9% | 10.4% | 18.9% | 51.4% | $0.6 | $-26.5 | $30.8 |
| freqfloor | 1.26% | 1.56% | -15.0% | -7.4% | 10.4% | 18.9% | 55.4% | $0.8 | $-32.1 | $35.1 |
| agg | 1.47% | 1.88% | -15.7% | -7.0% | 10.6% | 18.9% | 55.4% | $0.8 | $-32.1 | $32.8 |

### Days with ≥10 matches (n=77, statistically meaningful) — the number that matters
| config | median ROI | mean ROI | p10 | p75 | frac days green | med daily $ | med daily capital |
|---|---|---|---|---|---|---|---|
| v6 | -0.30% | 0.54% | -11.5% | 7.0% | 46.8% | $-0.5 | $132.3 |
| freqfloor | 1.24% | 1.14% | -11.5% | 7.0% | 57.1% | $1.4 | $132.3 |
| agg | 1.79% | 1.79% | -9.4% | 7.7% | 61.0% | $2.2 | $132.3 |

### D. Honest read (daily consistency)
- **v6 is NOT consistently profitable day-to-day at honest cost.** On the 77 meaningful (≥10-match) days, v6's **median daily ROI is -0.30% (negative)** and only **47% of days are green** (median daily net −$0.5). The blended-positive aggregate hid a coin-flip-to-losing typical day.
- **freqfloor improves daily consistency:** median day +1.24% ROI, **57% green** (median day +$1.4) — turns v6's negative median day positive.
- **agg is best on daily consistency:** median day +1.79%, **61% green** (median day +$2.2).
- BUT downside days are real and fat-tailed: p10 day ≈ −9% to −12% ROI; worst day −$26 to −$32. The edge is modest and variance is high. This improves daily *consistency* (more green days, positive median) over v6, not just the long-run aggregate.

## PART 2 — FULL SPECTRUM AT OPTIMAL (max-average) TARGETS, hit rate shown
**The ungated peak.** T* = the target maximizing AVERAGE net per N (highest point of the curve), NOT the CI-gated conservative pick. These show the *ceiling* of each cell/matchup and the hit rate it implies — they are more aggressive and more in-sample than the deployable freqfloor config. Both views matter: optimal = ceiling; freqfloor = conservative deployable.

### E. Per single-cell optimal (anchor 5–94, all 4,137 N; full 90 rows in spectrum JSON). Representative:
| cell | N | T* | hit% @T* | avg net @T* | $ @T* (10ct) | avg@T3 | avg@T10 | avg@T20 |
|---|---|---|---|---|---|---|---|---|
| 5.0 | 21.0 | 65.0 | 14% | 5.0 | 10.5 | 1.86 | 1.43 | 0.95 |
| 10.0 | 31.0 | 7.0 | 55% | -0.68 | -2.1 | -2.03 | -1.61 | -3.23 |
| 15.0 | 24.0 | 60.0 | 29% | 6.88 | 16.5 | 0.0 | 0.62 | -1.88 |
| 20.0 | 35.0 | 66.0 | 34% | 9.49 | 33.2 | 0.37 | -0.29 | 0.57 |
| 25.0 | 49.0 | 16.0 | 69% | 3.45 | 16.9 | -0.43 | 2.14 | -0.2 |
| 30.0 | 59.0 | 34.0 | 54% | 6.41 | 37.8 | -3.15 | 0.85 | 4.75 |
| 35.0 | 69.0 | 29.0 | 62% | 4.88 | 33.7 | -2.51 | -0.43 | 1.67 |
| 40.0 | 63.0 | 9.0 | 79% | -1.11 | -7.0 | -3.83 | -1.9 | -4.76 |
| 45.0 | 61.0 | 50.0 | 56% | 9.59 | 58.5 | -1.72 | -0.82 | 1.89 |
| 50.0 | 53.0 | 49.0 | 57% | 11.7 | 62.0 | -3.0 | -0.19 | 5.47 |
| 55.0 | 48.0 | 28.0 | 75% | 7.25 | 34.8 | 0.58 | -0.83 | 1.25 |
| 60.0 | 57.0 | 38.0 | 60% | 0.21 | 1.2 | -4.74 | -5.96 | -1.05 |
| 65.0 | 79.0 | 11.0 | 84% | -1.51 | -11.9 | -5.61 | -2.34 | -4.56 |
| 70.0 | 48.0 | 20.0 | 81% | 3.12 | 15.0 | -3.08 | 0.0 | 3.12 |
| 75.0 | 52.0 | 22.0 | 75% | -0.33 | -1.7 | -4.5 | -3.08 | -1.92 |
| 80.0 | 47.0 | 5.0 | 94% | -0.43 | -2.0 | -0.53 | -5.32 | nan |
| 85.0 | 32.0 | 14.0 | 88% | 7.88 | 25.2 | 3.0 | 4.06 | nan |
| 90.0 | 19.0 | 9.0 | 95% | 3.79 | 7.2 | -1.89 | nan | nan |

Pattern: underdog cells (5–20) have large T* (their occasional big spike is the whole edge); the **mid-favorite zone (60–75) is structurally hard — negative average net even at the optimal target** (cell 65 avg −1.5, cell 75 avg −0.3); clear favorites (80–90) and near-even (40–55) are positive. Curves are peaked (avg@T3/T10/T20 vary sign).

### F. Paired-group optimal (max average per-match net, ungated) — full spectrum hi→lo
| hi cell | lo cell | N | opt tgt_hi | opt tgt_lo | hit_hi | hit_lo | both | ≥1 | avg net | $@10ct | ROI | v6 $@10ct | v6 ROI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 86-98 | 6-16 | 204 | 1 | 59 | 97% | 20% | 17% | 100% | 0.42 | 8.5 | 0.4% | 53.7 | 2.6% |
| 79-85 | 17-23 | 193 | 14 | 56 | 84% | 38% | 23% | 100% | 8.26 | 159.5 | 8.1% | 120.2 | 6.1% |
| 74-78 | 24-28 | 176 | 14 | 71 | 83% | 31% | 14% | 100% | 3.58 | 63.0 | 3.5% | -44.4 | -2.5% |
| 69-73 | 29-33 | 180 | 26 | 30 | 75% | 55% | 31% | 99% | 6.49 | 116.9 | 6.4% | 95.7 | 5.2% |
| 65-68 | 34-38 | 187 | 31 | 39 | 66% | 53% | 19% | 100% | 4.17 | 77.9 | 4.1% | -21.4 | -1.1% |
| 61-64 | 34-38 | 51 | 34 | 4 | 74% | 84% | 59% | 100% | 8.55 | 43.6 | 8.5% | -5.5 | -1.1% |
| 61-64 | 39-41 | 156 | 35 | 58 | 65% | 38% | 9% | 94% | 4.91 | 76.6 | 4.8% | 5.5 | 0.4% |
| 56-60 | 42-45 | 186 | 30 | 34 | 66% | 62% | 28% | 100% | 5.13 | 95.5 | 5.0% | 69.1 | 3.6% |
| 56-60 | 46-76 | 79 | 11 | 10 | 87% | 78% | 66% | 100% | 0.19 | 1.5 | 0.2% | -12.4 | -1.5% |
| 51-55 | 46-76 | 181 | 6 | 13 | 89% | 84% | 74% | 100% | 2.92 | 52.8 | 2.9% | 26.1 | 1.4% |

**Ungated optimal beats v6 in 9 of 10 groups** (often turning v6-negative groups positive: 74-78×24-28 v6 −2.5%→opt +3.5%; 65-68×34-38 v6 −1.1%→+4.1%; 61-64×34-38 v6 −1.1%→+8.5%). The one exception is the **heavy-favorite group 86-98×6-16, where v6 (ROI 2.6%) beats the ungated optimal (0.4%)** — there the max-average pick sets a deep dog target that rarely fills. These optima are in-sample ceilings, not the conservative deployable.

### G. Spectrum map exported
- `data/durable/spike_volatility_map/atp_main_spectrum_map.json` — per-cell (90: cell, N, T*, hit@*, avg net, $), paired-groups (opt targets, hit rates, both/≥1, avg net, $, ROI, v6 comparison), daily-ROI summary per config, cell axis edges.

### Caveats
- Daily ROI: median day modestly positive for candidates, ~55–61% green on meaningful days, but high variance (p10 day ≈ −10%, worst ≈ −$30). Not a steady printer; a modest edge with real daily downside.
- Optimal (max-average) targets are the UNGATED in-sample peak — they overfit the realized peaks more than the CI-gated freqfloor. OOS validation required; deploy the conservative freqfloor, read the optimal as the ceiling.