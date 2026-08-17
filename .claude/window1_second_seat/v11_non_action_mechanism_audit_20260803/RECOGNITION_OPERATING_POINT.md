# RECOGNITION OPERATING-POINT RECONCILIATION [ANALYTICAL_ESTIMATE · MEASUREMENT ONLY]

Analysis seat only. Read-only. **No proposals.** Corpus: the verified pre-match spans of
`W1_GROUND_TRUTH_TABLE` @ `c0056976` (776 clean-span games); role legs = both legs of the 298 mirrored
pairs on those spans = **596 legs**. Rule under test: the benchmark role-rule @ `e269779b` — drift = last
in-span true print at or before the receipt, minus post-formation open; **≥+2¢ CLIMBER, ≤−2¢ FALLER, else
not callable**. Clock: f = fraction of the verified span (0 = formation end, 1 = bell). Truth = the leg's
eventual verified-span role. Rows: `RECOGNITION_OPERATING_POINT_SLICES.csv` + `.json`.

## ① When the signal arrives — f\* (first |drift| ≥ 2¢), by journey class and category

| class | legs | p10 | p25 | **med** | p75 | p90 | never reaches 2¢ |
|---|--:|--:|--:|--:|--:|--:|--:|
| ALL | 596 | 0.005 | 0.023 | **0.097** | 0.322 | 0.687 | 4 |
| UP_SHAPES | 289 | 0.004 | 0.019 | **0.058** | 0.235 | 0.549 | 0 |
| DOWN_SHAPES | 188 | 0.007 | 0.028 | **0.113** | 0.293 | 0.736 | 0 |
| STILL_SHAPES | 119 | 0.011 | 0.066 | **0.234** | 0.520 | 0.926 | 4 |
| ATP_CHALL | 276 | 0.009 | 0.036 | **0.179** | 0.487 | 0.775 | 2 |
| ATP_MAIN | 132 | 0.003 | 0.014 | **0.037** | 0.113 | 0.249 | 0 |
| WTA_CHALL | 54 | 0.004 | 0.091 | **0.277** | 0.859 | 0.982 | 1 |
| WTA_MAIN | 134 | 0.005 | 0.017 | **0.048** | 0.147 | 0.311 | 1 |

The signal *arrives* early — half of all role legs have moved 2¢ by f = 0.10. Arrival is not correctness;
② and ③ separate them.

## ②③ Callable coverage and accuracy-if-called, by clock slice

| class | f=0.05 | f=0.10 | f=0.25 | f=0.50 | f=0.75 | f=1.00 |
|---|---|---|---|---|---|---|
| **ALL** cov / acc | 36.2% / **81.0%** | 46.5% / **82.3%** | 62.4% / 92.2% | 76.3% / 96.5% | 85.9% / 98.2% | 96.5% / 100% |
| UP_SHAPES | 45.3% / **96.9%** | 56.4% / 96.9% | 72.3% / 98.6% | 84.4% / 99.2% | 93.1% / 99.3% | 100% / 100% |
| DOWN_SHAPES | 34.0% / **62.5%** | 44.7% / 69.0% | 62.8% / 89.8% | 77.7% / 95.9% | 85.6% / 96.9% | 100% / 100% |
| STILL_SHAPES | 17.6% / **38.1%** | 25.2% / 40.0% | 37.8% / 68.9% | 54.6% / 87.7% | 68.9% / 97.6% | 82.4% / 100% |
| ATP_CHALL | 26.4% / 76.7% | 34.8% / 79.2% | 50.7% / 90.0% | 69.9% / 93.3% | 83.7% / 96.5% | 95.3% / 100% |
| ATP_MAIN | 50.8% / 79.1% | 64.4% / 81.2% | 75.8% / 92.0% | 85.6% / 100% | 90.9% / 100% | 96.2% / 100% |
| WTA_CHALL | 20.4% / 81.8% | 29.6% / 81.2% | 46.3% / 92.0% | 48.1% / 96.2% | 61.1% / 97.0% | 96.3% / 100% |
| WTA_MAIN | 48.5% / 87.7% | 59.7% / 87.5% | 79.9% / 95.3% | 91.8% / 98.4% | 95.5% / 100% | 99.3% / 100% |

**Early calls are not the same instrument as late calls.** At f = 0.05 the rule is already 96.9% right on
up-shapes and only **62.5% right on down-shapes** and **38.1% on still-shapes** — early down-drift reverses.

Pair grain (298 pairs): both-callable / both-right-of-callable / full-inversion —
f=0.05: 17.4% / 73.1% / 1.9% · f=0.10: 25.2% / 77.3% / 4.0% · f=0.25: 45.0% / 91.0% / 0.7% ·
f=0.50: 63.8% / 95.3% / 1.1% · f=0.75: 77.5% / 97.4% / 0.9% · f=1.00: 93.0% / 100% / 0%.

## ④ The two operating points, side by side (exact receipt evaluation)

| operating point | legs | f (p25 / **med** / p75) | callable | **coverage** | acc-if-called | pairs both-callable / both-right |
|---|--:|---|--:|--:|--:|---|
| **A — old POSTING receipts** @ `336f42bf` | 483 | 0.209 / **0.543** / 0.893 | 405 | **83.9%** | **95.1%** | 75.4% / 96.1% |
| **C — canonical ONSET receipts** (dev-804 `onset_sel`) | 582 | 0.001 / **0.103** / 0.450 | 283 | **48.6%** | 90.1% | 36.1% / 89.4% |
| **B — V52l CAUSAL-ONSET receipts** @ `6678fd0c` | **24** | −0.065 / **+0.001** / +0.007 | 2 | **8.3%** | 50.0% (n=2) | 0.0% / — |
| A restricted to B's legs | 24 | 0.384 / 0.642 / 0.882 | 18 | 75.0% | 88.9% | — |
| C restricted to B's legs | 22 | 0.001 / 0.157 / 0.373 | 12 | 54.5% | 91.7% | — |

**The reconciliation is a clock, not a rule change.** A and B run the identical classifier on the identical
corpus; the only difference is *when it is asked*. The posting clock sits at median f = 0.543; the V52l
causal-onset clock sits at median f = **+0.001** — the instant the book finishes forming. Coverage is a
monotone function of that position:

| coverage | 8.3% | 20% | **27.0%** | 40% | 48.6% | 60% | 70% | **83.9%** | 90% |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| first reached at f = | 0.004 | 0.019 | **0.027** | 0.074 | 0.115 | 0.218 | 0.376 | **0.720** | 0.900 |

So **84% is the coverage of a clock at f ≈ 0.72, and 27% is the coverage of a clock at f = 0.027** — the
same instrument, 26 percentage points of window apart.

**On the 27% figure specifically, stated honestly: no quantity equal to 27% exists as a rate in the pinned
artifacts.** The only 27 in the V52l package is `offer_denominator_under_par: 27` — a game *count*, not a
percentage. The candidates that land near it, measured: corpus coverage is exactly **27.0% at f = 0.027**;
pair both-callable is 25.2% at f = 0.10 (the canonical-onset median). The V52l causal-onset receipts
themselves measure **8.3% coverage (2 of 24 role legs)** — *below* the 27% level, because those receipts sit
earlier (p75 = +0.007) than the f = 0.027 crossing. **n = 24 is thin and is stated as thin**: V52l ran a
30-game cohort, of which 28 are on verified spans and only 12 games / 24 legs are mirrored role legs. It is
not enough to certify a causal-onset coverage figure; it is enough to locate the clock (median f = +0.001,
with 5 of 24 receipts firing *before* the formation end, f < 0).

## ⑤ Conclusion — when recognition is ripe

Ripeness = the earliest f from which accuracy-if-called **stays at or above the benchmarked bar of 95.1%**
(the taxonomy's published called-leg accuracy @ `e269779b`), with ≥10 legs called. This is the number the
wiring must respect.

| class | **ripe at f** | callable there | coverage | acc from there on |
|---|--:|--:|--:|--:|
| UP_SHAPES | **0.023** | 83 | 28.7% | 95.2% |
| WTA_MAIN | **0.206** | 103 | 76.9% | 95.1% |
| ATP_MAIN | **0.351** | 103 | 78.0% | 95.1% |
| **ALL** | **0.384** | 421 | 70.6% | 95.2% |
| DOWN_SHAPES | **0.448** | 139 | 73.9% | 95.7% |
| STILL_SHAPES | **0.650** | 77 | 64.7% | 96.1% |
| ATP_CHALL | **0.703** | 227 | 82.2% | 95.2% |
| WTA_CHALL | **0.964** | 41 | 75.9% | 97.6% |

Read as measurement: **the instrument does not have one ripeness — it has five.** Up-shapes are ripe almost
immediately (f = 0.023, and they are the majority of role legs at 289/596); down-shapes need nearly half the
window (0.448); still-shapes two thirds (0.650); ATP_CHALL is the slowest main category (0.703) and
WTA_CHALL effectively never ripens before the bell (0.964). The posting clock (median f = 0.543) sat past
ripeness for up-shapes, ATP_MAIN and WTA_MAIN, and short of it for down-shapes' full quality, ATP_CHALL and
WTA_CHALL. The causal-onset clock (median f = +0.001) sits before every class's ripeness without exception.

## Conservation

804 games = 776 verified corpus + 28 excluded @ `c0056976`. 298 mirrored pairs → 596 role legs (592 with a
measurable f\*, 4 never reaching 2¢). Operating-point denominators: A 483 legs / 236 pairs (113 role legs
carry no posting receipt), C 582 legs / 288 pairs (14 lack a canonical onset), B 24 legs / 12 pairs (V52l
cohort intersection, thin and stated). Slice table 8 classes × 6 slices = 48 rows; every accuracy cell is
over its own callable denominator, printed beside it. Measurement only — no proposals, no wiring, no
mechanism named. ANALYTICAL_ESTIMATE.
