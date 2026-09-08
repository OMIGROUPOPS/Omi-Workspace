# Sentence experiments — ATP_MAIN

BENCH ONLY. Engine and historical artifacts unchanged. All 928 filed queries; tick library only.

Run order: E3; E1 amended for positive-print first passage and censoring; E2(a/b); E4 shared-set-only diagnostic. E2(c) deferred: no filed causal family learner/callability rule supplied. Equal-and-opposite E4 not run: amplitude/constraint estimator unspecified and marginal minima need not be simultaneous.

## E3 — one-sided failures first

Last scheduled gate is 5m to bell, not the last successful call. Error = Q minus strictly-later positive-size remaining floor. Causes overlap. No-call and no-future-print are retained, never zero-filled. Never postable means no unfilled receipt with status OK, cent-valid Q below ask and unlocked book, before the separate ask-only/pair-cap guards. Pair-cap-ever is exposure, NOT a causal attribution.

| Failed side | Pairs | Scorable Q/positive floor | q10 / q25 / q50 / q75 / q90 (cents) | Too deep | Never postable | Moved off later print (active interval) | Pair cap ever | No call | No later print |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| underdog | 155 | 112 | -1 / 0 / 0 / 0 / 2 | 12 | 3 | 37 (26) | 112 | 10 | 34 |
| favourite | 113 | 80 | -1 / 0 / 0 / 1 / 2 | 12 | 6 | 25 (23) | 81 | 7 | 28 |

underdog last-gate roles: {"CLIMBER": 73, "FALLER": 35, "NOT_CALLABLE": 47}; original FALLER-only stepped-off subset: 16.

favourite last-gate roles: {"CLIMBER": 82, "FALLER": 17, "NOT_CALLABLE": 14}; original FALLER-only stepped-off subset: 8.

Controls (sides, not independent pairs):

| Group | Side | n | Too deep | Never postable | Moved off | Pair cap ever |
|---|---|---:|---:|---:|---:|---:|
| completed_control | favourite | 375 | 32 | 0 | 241 | 118 |
| completed_control | underdog | 375 | 28 | 0 | 302 | 118 |
| no_fill_control | favourite | 285 | 32 | 234 | 8 | 17 |
| no_fill_control | underdog | 285 | 17 | 233 | 13 | 17 |
| filled_side_control | favourite | 155 | 15 | 0 | 75 | 112 |
| filled_side_control | underdog | 113 | 9 | 0 | 61 | 81 |

## E1 — fixed Q, target-specific first-passage X

Finite elapsed-time weighted median with non-hits at infinity. Error comparisons condition on an actual query hit and finite candidate median; coverage below includes every filed game. Calibration uses member reach probability at each rule's own deadline: different horizons, not a fixed-horizon superiority claim. The filed matched-win criterion is applied per gate/side, never to pooled repeated gates.

| Gate m | Finite calls F/D (each /928) | Censored F/D | Matched hits F/D | Deadline MAE delta m F/D | Strict wins F/D | Brier delta F/D | Filed win F/D |
|---:|---|---|---|---|---|---|---|
| 2880 | 44 / 51 | 0 / 0 | 27 / 30 | 503.189 / 319.470 | 22.22% / 20.00% | 0.043 / 0.020 | False / False |
| 2160 | 211 / 188 | 0 / 0 | 115 / 102 | 138.419 / 109.381 | 38.26% / 34.31% | 0.036 / 0.033 | False / False |
| 1440 | 338 / 315 | 0 / 0 | 195 / 212 | 130.441 / 99.678 | 36.92% / 36.79% | 0.031 / 0.025 | False / False |
| 1080 | 500 / 490 | 0 / 0 | 317 / 294 | 92.231 / 94.648 | 42.90% / 29.59% | 0.043 / 0.028 | False / False |
| 720 | 746 / 741 | 0 / 0 | 459 / 372 | 102.036 / 60.837 | 33.77% / 32.53% | 0.055 / 0.045 | False / False |
| 480 | 814 / 804 | 0 / 0 | 481 / 411 | 49.926 / 54.281 | 38.25% / 34.79% | 0.045 / 0.053 | False / False |
| 360 | 833 / 823 | 1 / 0 | 468 / 440 | 25.337 / 30.181 | 42.95% / 40.23% | 0.070 / 0.065 | False / False |
| 240 | 851 / 835 | 0 / 0 | 506 / 486 | 19.807 / 13.024 | 41.70% / 40.53% | 0.069 / 0.043 | False / False |
| 180 | 854 / 839 | 0 / 0 | 557 / 467 | 12.564 / 9.637 | 38.78% / 38.97% | 0.048 / 0.055 | False / False |
| 120 | 863 / 855 | 0 / 0 | 567 / 479 | 7.019 / 2.735 | 38.62% / 43.22% | 0.046 / 0.057 | False / False |
| 90 | 866 / 854 | 0 / 0 | 524 / 502 | 4.728 / 2.775 | 42.94% / 44.22% | 0.069 / 0.063 | False / False |
| 60 | 869 / 854 | 0 / 0 | 506 / 510 | 6.696 / 3.621 | 35.77% / 40.20% | 0.072 / 0.071 | False / False |
| 30 | 868 / 861 | 0 / 0 | 477 / 478 | 2.852 / 2.565 | 41.72% / 44.77% | 0.128 / 0.130 | False / False |
| 15 | 869 / 861 | 1 / 0 | 505 / 488 | 1.131 / 0.575 | 47.72% / 46.93% | 0.180 / 0.184 | False / False |
| 5 | 845 / 847 | 22 / 15 | 582 / 567 | -0.106 / -0.064 | 55.50% / 51.50% | 0.245 / 0.248 | True / True |

Common bell-horizon reach calibration (pool-implied diagnostic, not an emitted OS probability):

| Gate m | Predicted reach F/D | Observed reach F/D | Brier F/D |
|---:|---|---|---|
| 2880 | 64.03% / 65.79% | 61.36% / 58.82% | 0.215 / 0.257 |
| 2160 | 66.62% / 60.48% | 54.50% / 54.26% | 0.257 / 0.245 |
| 1440 | 64.38% / 64.29% | 57.69% / 67.30% | 0.238 / 0.225 |
| 1080 | 68.33% / 60.64% | 63.40% / 60.00% | 0.217 / 0.227 |
| 720 | 64.03% / 60.00% | 61.53% / 50.20% | 0.229 / 0.255 |
| 480 | 63.08% / 60.45% | 59.09% / 51.12% | 0.236 / 0.251 |
| 360 | 63.50% / 60.36% | 56.24% / 53.46% | 0.243 / 0.245 |
| 240 | 64.85% / 67.31% | 59.46% / 58.20% | 0.234 / 0.228 |
| 180 | 67.00% / 64.50% | 65.22% / 55.66% | 0.219 / 0.240 |
| 120 | 66.60% / 65.92% | 65.70% / 56.02% | 0.219 / 0.243 |
| 90 | 64.78% / 65.60% | 60.51% / 58.78% | 0.240 / 0.237 |
| 60 | 64.33% / 65.34% | 58.23% / 59.72% | 0.247 / 0.242 |
| 30 | 62.40% / 62.02% | 54.95% / 55.52% | 0.253 / 0.246 |
| 15 | 62.80% / 65.59% | 58.05% / 56.68% | 0.229 / 0.234 |
| 5 | 70.09% / 67.14% | 68.40% / 66.82% | 0.207 / 0.225 |

At this common horizon both X rules have identical implied probabilities because Q and member weights are fixed. Changing X alone cannot improve this probability model; own-deadline Brier differences are not a matched fixed-horizon calibration win.


## E2(a/b) and E4 shared-set-only — matched sentence errors

Negative delta is better. F/D means favourite/underdog. Floors and times here use the filed carried-state minimum target; positive-future-print errors and target denominators are also in GATE_TABLES.json. Calls include states without a later query print; this deliberately differs from the old SCORABLE-conditioned summary. Every CURRENT_ROLE Q/X/ESS matched the archived baseline.

### NO_ROLE

| Gate m | Calls F/D (each /928) | Baseline calls F/D | Matched n F/D | Floor delta cents F/D | Timing delta m F/D | Family accuracy F/D |
|---:|---|---|---|---|---|---|
| 2880 | 91 / 91 | 44 / 51 | 44 / 51 | 0.000 / 0.000 | 11.059 / -40.847 | 45.05% / 29.67% |
| 2160 | 285 / 285 | 211 / 188 | 211 / 188 | -0.009 / 0.016 | -17.323 / -17.209 | 35.09% / 30.88% |
| 1440 | 423 / 423 | 338 / 315 | 338 / 315 | -0.012 / 0.019 | -12.869 / -15.461 | 33.81% / 31.91% |
| 1080 | 565 / 565 | 500 / 490 | 500 / 490 | -0.016 / -0.022 | -8.160 / -25.837 | 32.39% / 29.20% |
| 720 | 787 / 787 | 746 / 741 | 746 / 741 | -0.021 / 0.000 | -1.801 / -7.896 | 30.88% / 27.57% |
| 480 | 847 / 847 | 814 / 804 | 814 / 804 | -0.012 / -0.083 | -3.041 / -3.830 | 29.87% / 27.39% |
| 360 | 869 / 869 | 834 / 823 | 834 / 823 | 0.004 / -0.057 | -0.211 / -2.741 | 30.26% / 27.62% |
| 240 | 881 / 881 | 851 / 835 | 851 / 835 | 0.000 / -0.054 | -2.518 / -1.353 | 29.40% / 27.13% |
| 180 | 885 / 885 | 854 / 839 | 854 / 839 | 0.025 / -0.055 | -1.276 / -1.358 | 29.27% / 27.01% |
| 120 | 895 / 895 | 863 / 855 | 863 / 855 | -0.029 / -0.023 | -0.297 / -1.334 | 29.27% / 26.82% |
| 90 | 896 / 896 | 866 / 854 | 866 / 854 | -0.044 / -0.028 | -0.126 / -0.749 | 29.24% / 26.79% |
| 60 | 897 / 897 | 869 / 854 | 868 / 854 | -0.038 / -0.019 | -0.251 / -0.681 | 29.21% / 26.87% |
| 30 | 898 / 898 | 868 / 861 | 868 / 861 | -0.025 / -0.022 | -0.272 / -0.035 | 29.18% / 26.84% |
| 15 | 898 / 898 | 870 / 861 | 870 / 861 | -0.026 / -0.017 | -0.251 / -0.161 | 29.18% / 26.84% |
| 5 | 900 / 900 | 867 / 862 | 867 / 862 | -0.037 / -0.005 | -0.040 / -0.009 | 29.11% / 26.89% |

### SHARED_INTERSECTION

| Gate m | Calls F/D (each /928) | Baseline calls F/D | Matched n F/D | Floor delta cents F/D | Timing delta m F/D | Family accuracy F/D |
|---:|---|---|---|---|---|---|
| 2880 | 27 / 27 | 44 / 51 | 27 / 27 | -0.148 / -0.037 | 31.512 / 2.804 | 40.74% / 29.63% |
| 2160 | 148 / 148 | 211 / 188 | 148 / 147 | 0.020 / -0.068 | -5.911 / -1.613 | 38.51% / 38.51% |
| 1440 | 257 / 257 | 338 / 315 | 257 / 256 | 0.078 / 0.035 | 9.678 / 12.215 | 37.35% / 33.85% |
| 1080 | 400 / 400 | 500 / 490 | 400 / 399 | 0.040 / 0.033 | 9.029 / 10.484 | 39.50% / 32.00% |
| 720 | 654 / 654 | 746 / 741 | 651 / 650 | 0.049 / 0.114 | 7.362 / 9.504 | 32.11% / 27.68% |
| 480 | 736 / 736 | 814 / 804 | 733 / 732 | 0.018 / 0.072 | 3.869 / 6.352 | 33.02% / 28.12% |
| 360 | 757 / 757 | 834 / 823 | 756 / 753 | 0.028 / 0.076 | 1.213 / 2.576 | 32.76% / 28.14% |
| 240 | 765 / 765 | 851 / 835 | 763 / 763 | 0.012 / 0.069 | 0.511 / 2.319 | 30.59% / 27.19% |
| 180 | 775 / 775 | 854 / 839 | 773 / 771 | 0.054 / 0.047 | 1.401 / 2.296 | 31.61% / 26.45% |
| 120 | 788 / 788 | 863 / 855 | 786 / 784 | 0.014 / 0.033 | 1.039 / 0.626 | 29.70% / 26.90% |
| 90 | 795 / 795 | 866 / 854 | 793 / 791 | 0.040 / 0.056 | 0.761 / 0.939 | 28.55% / 26.92% |
| 60 | 791 / 791 | 869 / 854 | 789 / 786 | 0.056 / 0.060 | 0.403 / 0.756 | 28.19% / 26.80% |
| 30 | 797 / 797 | 868 / 861 | 795 / 795 | 0.035 / 0.035 | 0.122 / 0.578 | 29.36% / 26.98% |
| 15 | 807 / 807 | 870 / 861 | 805 / 803 | 0.017 / 0.039 | 0.150 / 0.156 | 29.24% / 25.77% |
| 5 | 804 / 804 | 867 / 862 | 802 / 802 | 0.031 / 0.031 | 0.021 / 0.018 | 29.60% / 26.99% |

Family accuracy is diagnostic only: inherited full-library retrospective SLEEPER p10, not a causally learned family callability rule. Neither NO_ROLE nor SHARED_INTERSECTION meets the filed floor-error win test at any gate/side.

## R0 conduct with experimental sentences

Positive-size strictly-later pre-bell prints; reachable, not certain. No execution change. Never compare a GATE-SIM candidate to the RECEIPT-SIM baseline.

| Cadence | Sentence pool | Completed /928 | One-sided /928 | Capture cents /eligible | Delta completion pp | Delta capture /eligible | Delta one-sided pp |
|---|---|---:|---:|---:|---:|---:|---:|
| GATE-SIM | CURRENT_ROLE | 316 | 295 | 0.589 | 0.000 | 0.000 | 0.000 |
| GATE-SIM | NO_ROLE | 329 | 299 | 0.602 | 1.401 | 0.013 | 0.431 |
| GATE-SIM | SHARED_INTERSECTION | 297 | 298 | 0.531 | -2.047 | -0.058 | 0.323 |
| RECEIPT-SIM | CURRENT_ROLE | 375 | 268 | 0.730 | 0 | 0 | 0 |
| RECEIPT-SIM | SHARED_INTERSECTION | 354 | 275 | 0.700 | -2.263 | -0.029 | 0.754 |

All reported simulations have zero safety violations. Two identical projection passes; native shared projections also invariant to batch boundary. Independent interval audit checks every fill and miss. No family learner, opposite-move model, engine change, or promotion is implied.

## Provenance

- Baseline c7825925; conduct archives d2d8f16b; matched-win filing 87049680.
- Tick library c823d172; positive-print extract bf982a5e, 777,937 accepted rows / 771,159 positive-size rows; raw prints never committed.
- Definitions, exact hashes, original/candidate per-gate rows, E3 per-side autopsies, censoring, call/abstention denominators, and native simulation details are alongside this summary.

## Reproduce

From the worktree root with the approved private extract still at its receipt path:

```powershell
$benchPython = 'C:\Users\omigr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $benchPython -B arb-executor/analysis/sentence_experiments.py
& $benchPython -B arb-executor/analysis/sentence_shared_pool_native.py
& $benchPython -B -m unittest discover -s arb-executor/analysis -p test_sentence_experiments.py
& $benchPython -B arb-executor/analysis/sentence_experiments_report.py
```

Native shared projection reuses hash-bound archived joint NO-CALL rows; callable Q/X are reconstructed twice. Large archived joint-outcome arrays are not copied into R0's projection because R0 does not read them. These are computation-only optimizations.
