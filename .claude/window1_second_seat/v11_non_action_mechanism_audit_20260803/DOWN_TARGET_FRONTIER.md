# DOWN-TARGET FRONTIER — the last measurement before V52r [ANALYTICAL_ESTIMATE · MEASUREMENT ONLY]

Analysis seat only. **No selection — the operator picks.** Same simulator lineage @ `71de534a` (corrected
anchor per `a059264d`), **TRD5 binding fixed**; DOWN-bound legs on verified spans @ `c0056976`: **251
verified / 196 live-clock**. Sibling model stated: the UP sibling fills at its TRD5 bind price (the V52p/q
immediate-up policy); targets clamp ≥1¢; session low = running post-onset true-print low. Full grid both
clocks: `DOWN_TARGET_FRONTIER.{csv,json}` (12 rules × 2 clocks, per-category blocks in the JSON).

Library percentiles used (pooled category down-depth below anchor, from the corpus): ATP_CHALL 7/8/8 ·
ATP_MAIN 7/7/8 · WTA_CHALL 7/7/7 · WTA_MAIN 6.5/8/8 (p25/p40/p50).

## The table (verified | live)

| rule | kiss % | fill−floor med | completes | banked ¢ | lost dn-unkissed / up-missing | LIVE: kiss % · completes · banked ¢ |
|---|--:|--:|--:|--:|---|---|
| P25 | 53.8 | 2 | 76 | 229 | 111 / 4 | 35.7 · 33 · 86 |
| P40 | 42.2 | 2 | 66 | 222 | 140 / 4 | 27.0 · 28 · 77 |
| P50 | 38.2 | 2 | 62 | 210 | 149 / 3 | 24.5 · 25 · 73 |
| **LOW-0** | **88.4** | 2 | 66 | 142 | **26** / 6 | **78.1 · 45 · 87** |
| **LOW-1** | 74.1 | 2 | 111 | 233 | 59 / 3 | 57.1 · 62 · **128** |
| LOW-2 | 54.2 | 2 | 101 | **266** | 108 / 2 | 31.6 · 40 · 87 |
| MAX25L1 | 80.5 | 2 | 101 | 189 | 44 / 4 | 63.8 · 59 · 109 |
| **MAX40L1** | 78.5 | 2 | 108 | 210 | 49 / 4 | 62.2 · 63 · 119 |
| MAX50L1 | 78.5 | 2 | 110 | 213 | 49 / 4 | 62.2 · 64 · 121 |
| TRAIL1 | ≡ LOW-1 | ≡ | ≡ | ≡ | ≡ | ≡ LOW-1 |
| TRAIL2 | 29.5 | 2 | 49 | 144 | 168 / 0 | 20.9 · 24 · 57 |
| TRAIL3 | 11.2 | 1 | 19 | 59 | 214 / 0 | 7.7 · 10 · 27 |

## Three structural findings, before the frontier

1. **TRAIL1 is IDENTICAL to LOW-1 — every scored column, both clocks.** With integer prices, a new session
   low cannot print without first kissing a stand at low−1: **at Δ=1, trailing is impossible by
   construction.** At Δ=2/3 trailing chases the low away (29.5% / 11.2% kiss, the worst banked on the
   board). The trailing family adds nothing that LOW-1 doesn't already carry.
2. **Depth-of-fill is rule-insensitive: fill−floor median is 2¢ on essentially every rule and both
   clocks.** The rules never differ in how deep a fill lands — only in **whether** you fill and **how many
   pairs you strand** unkissed. The frontier's real axes are kissability and pairs, not cents-per-fill.
3. **Every static library-percentile rule is dominated, both clocks.** P25/P40/P50 kiss 38–54%, strand
   111–149 pairs, and bank no more than LOW-1 — **the running session low beats every static shape
   aggregate.** This is the averages-can't-aim-depth proof at its final grain: even percentile-tuned
   library depths lose to a one-line reference the tape itself supplies.

## The kissability-vs-banked frontier

**Non-dominated, verified:** LOW-0 (88.4 / 142¢) → MAX25L1 (80.5 / 189¢) → MAX50L1 (78.5 / 213¢) → LOW-1
(74.1 / 233¢) → LOW-2 (54.2 / 266¢). **Non-dominated, live:** LOW-0 (78.1 / 87¢) → MAX25L1 (63.8 / 109¢) →
MAX50L1 (62.2 / 121¢) → LOW-1 (57.1 / **128¢**) — **LOW-2 falls off the live frontier entirely**: its
verified-best 266¢ collapses to 87¢, dominated by LOW-0 at equal banked and 2.5× the kissability.
**The live clock reverses the verified ranking** — deeper static targets need time the live span does not
grant. Dominated set, named: P25 · P40 · P50 · TRAIL2 · TRAIL3 · LOW-2 (live) · MAX40L1 (sits 1 fill
inside MAX50L1 on both clocks).

Per-category blocks are in the JSON; the pattern holds in every category (WTA_CHALL thinnest at n=19
library legs — its percentile values carry that width honestly).

## Three cleanest candidates — receipts only, no selection

1. **LOW-0** (stand at the session low): kiss **88.4 / 78.1%**, fewest stranded pairs (26 / 45), the
   live-robust end; banks least on verified (142¢). The kissability pole.
2. **LOW-1** (session low − 1): **best banked under the live clock (128¢)**, second verified (233¢), 74.1 /
   57.1% kiss; carries the TRAIL1 identity — it *is* the Δ=1 trailing rule. The banked pole that survives
   the live clock.
3. **MAX50L1** (shape-median backstopped by low−1): 78.5 / 62.2% kiss, 213 / 121¢ — the non-dominated
   interior point where the library depth serves only as a backstop to the session-low reference, both
   clocks (MAX40L1 sits one fill inside it and is dominated).

## Conservation

DOWN binds 251 verified / 196 live (UP siblings 287 / 241); every rule scores the identical bind
population per clock; per-rule pair accounting carried in the JSON: down_binds = completes +
lost-down-unkissed + lost-up-missing + residual (unfilled with no UP sibling, or filled pair ≥100¢);
12 rules × 2 clocks = 24 scored cells, all in the CSV; TRAIL1≡LOW-1 verified equal on every column;
provenance triples on the three inputs. Measurement only — no proposal, no selection, no wiring; V52r's
design is the operator's. ANALYTICAL_ESTIMATE.
