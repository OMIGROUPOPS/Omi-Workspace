# RULING RUN — TICK LIBRARY — CANDIDATE POOL SCOREBOARD

No engine change or automatic rule selection. Book reach is diagnostic only, not execution proof.

Error means are conditional on called sides. Utility shows both called-pair and all-eligible-query denominators; NO-CALL contributes zero only to reach/discount utility. These are not matched-cohort comparisons.

## ATP_MAIN

### MACRO — favorite / underdog last-path MAE

| Rule | 2880 | 2160 | 1440 | 1080 | 720 | 480 | 360 | 240 | 180 | 120 | 90 | 60 | 30 | 15 | 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOFT | 1.421 ; 1.779 | 2.451 ; 2.046 | 2.319 ; 2.523 | 2.437 ; 2.404 | 1.782 ; 1.821 | 1.513 ; 1.392 | 1.316 ; 1.190 | 1.063 ; 1.152 | 0.919 ; 0.908 | 0.848 ; 0.850 | 0.762 ; 1.600 | 0.684 ; 0.833 | 0.579 ; 1.250 | 0.611 ; 0.417 | — ; — |
| HARD | 1.421 ; 1.779 | 2.381 ; 2.023 | 2.288 ; 2.396 | 2.400 ; 2.285 | 1.766 ; 1.807 | 1.512 ; 1.391 | 1.300 ; 1.122 | 1.065 ; 1.152 | 0.919 ; 0.908 | 0.848 ; 0.850 | 0.762 ; 1.600 | 0.684 ; 0.833 | 0.579 ; 1.250 | 0.611 ; 0.417 | — ; — |
| STEP-FORECAST | 1.792 ; 1.797 | 2.278 ; 2.220 | 1.904 ; 1.953 | 1.973 ; 1.919 | 1.691 ; 1.645 | 1.464 ; 1.441 | 1.396 ; 1.377 | 1.175 ; 1.234 | 0.978 ; 0.980 | 1.108 ; 1.212 | 0.844 ; 0.933 | 0.902 ; 0.909 | 0.700 ; 0.792 | 0.724 ; 0.444 | — ; — |
| FIRST-TICK-ONLY | 2.026 ; 2.048 | 2.198 ; 2.131 | 1.923 ; 1.906 | 1.962 ; 1.845 | 1.671 ; 1.629 | 1.431 ; 1.423 | 1.292 ; 1.309 | 1.120 ; 1.151 | 1.063 ; 1.062 | 0.988 ; 1.008 | 0.942 ; 1.006 | 0.976 ; 0.994 | 0.796 ; 0.805 | 0.613 ; 0.613 | — ; — |
| BASE | 1.854 ; 2.033 | 2.138 ; 2.145 | 2.003 ; 2.005 | 1.918 ; 1.865 | 1.630 ; 1.643 | 1.442 ; 1.422 | 1.313 ; 1.313 | 1.128 ; 1.158 | 1.073 ; 1.074 | 1.003 ; 1.019 | 0.985 ; 1.027 | 0.992 ; 1.006 | 0.806 ; 0.809 | 0.625 ; 0.612 | — ; — |
| TAXONOMY-NULL | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — |

### MICRO — floor MAE / median absolute error, favorite then underdog

| Rule | 2880 | 2160 | 1440 | 1080 | 720 | 480 | 360 | 240 | 180 | 120 | 90 | 60 | 30 | 15 | 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOFT | 1.444/2.000 ; 1.667/1.000 | 1.730/1.000 ; 2.288/2.000 | 1.604/1.000 ; 2.667/2.000 | 2.659/1.000 ; 2.172/2.000 | 1.691/1.000 ; 1.810/2.000 | 1.497/1.000 ; 1.545/1.000 | 1.460/1.000 ; 1.850/2.000 | 1.163/1.000 ; 1.464/1.000 | 1.172/1.000 ; 1.658/2.000 | 1.160/1.000 ; 1.333/1.000 | 1.619/1.000 ; 1.800/1.500 | 1.684/1.000 ; 2.000/1.500 | 1.263/1.000 ; 3.375/2.000 | 1.444/1.000 ; 0.833/1.000 | 1.444/0.000 ; 4.667/0.000 |
| HARD | 1.444/2.000 ; 1.667/1.000 | 1.700/1.000 ; 2.314/2.000 | 1.630/1.000 ; 2.576/1.000 | 2.247/1.000 ; 2.036/2.000 | 1.697/1.000 ; 1.793/2.000 | 1.491/1.000 ; 1.529/1.000 | 1.419/1.000 ; 1.718/2.000 | 1.170/1.000 ; 1.464/1.000 | 1.172/1.000 ; 1.658/2.000 | 1.160/1.000 ; 1.333/1.000 | 1.619/1.000 ; 1.800/1.500 | 1.684/1.000 ; 2.000/1.500 | 1.263/1.000 ; 3.375/2.000 | 1.444/1.000 ; 0.833/1.000 | 1.444/0.000 ; 0.400/0.000 |
| STEP-FORECAST | 1.844/1.000 ; 2.000/1.000 | 2.043/1.000 ; 2.213/2.000 | 1.663/1.000 ; 1.856/1.000 | 1.796/1.000 ; 1.916/1.000 | 1.606/1.000 ; 1.806/1.000 | 1.728/1.000 ; 1.621/1.000 | 1.745/1.000 ; 1.814/1.000 | 1.382/1.000 ; 1.705/1.000 | 1.163/1.000 ; 1.468/1.000 | 1.400/1.000 ; 1.470/1.000 | 1.446/1.000 ; 1.288/1.000 | 2.091/1.000 ; 1.452/1.000 | 1.167/1.000 ; 1.750/1.000 | 1.379/1.000 ; 0.630/1.000 | 1.111/1.000 ; 1.625/0.000 |
| FIRST-TICK-ONLY | 2.432/1.000 ; 1.922/1.000 | 1.991/1.000 ; 2.149/2.000 | 1.694/1.000 ; 1.761/1.000 | 1.759/1.000 ; 1.767/1.000 | 1.591/1.000 ; 1.684/1.000 | 1.586/1.000 ; 1.571/1.000 | 1.465/1.000 ; 1.478/1.000 | 1.425/1.000 ; 1.404/1.000 | 1.359/1.000 ; 1.354/1.000 | 1.362/1.000 ; 1.280/1.000 | 1.343/1.000 ; 1.237/1.000 | 1.279/1.000 ; 1.150/1.000 | 1.199/1.000 ; 1.057/1.000 | 1.106/1.000 ; 0.968/1.000 | 0.891/0.000 ; 0.748/0.000 |
| BASE | 1.780/1.000 ; 1.877/1.000 | 1.860/1.000 ; 2.180/2.000 | 1.776/1.000 ; 1.866/1.000 | 1.758/1.000 ; 1.736/1.000 | 1.576/1.000 ; 1.691/1.000 | 1.672/1.000 ; 1.552/1.000 | 1.592/1.000 ; 1.483/1.000 | 1.440/1.000 ; 1.403/1.000 | 1.418/1.000 ; 1.304/1.000 | 1.399/1.000 ; 1.215/1.000 | 1.367/1.000 ; 1.212/1.000 | 1.294/1.000 ; 1.146/1.000 | 1.232/1.000 ; 1.049/1.000 | 1.157/1.000 ; 0.942/1.000 | 0.892/0.000 ; 0.746/0.000 |
| TAXONOMY-NULL | 2.978/2.500 ; 3.595/3.000 | 4.440/3.000 ; 5.490/2.500 | 4.100/2.500 ; 4.724/2.000 | 3.935/2.000 ; 4.749/2.000 | 3.920/2.000 ; 5.058/2.000 | 3.781/2.000 ; 4.581/2.000 | 3.895/3.000 ; 4.445/2.000 | 3.972/3.000 ; 4.375/2.000 | 4.047/3.000 ; 4.338/2.000 | 4.192/3.000 ; 4.310/2.000 | 4.143/3.000 ; 4.203/2.000 | 4.206/3.000 ; 4.255/2.000 | 4.306/3.000 ; 4.380/2.000 | 4.250/3.000 ; 4.328/2.500 | 4.294/3.000 ; 4.578/2.500 |

### MICRO-MICRO — q50 pair reach × discount, per called pair / per eligible query

| Rule | 2880 | 2160 | 1440 | 1080 | 720 | 480 | 360 | 240 | 180 | 120 | 90 | 60 | 30 | 15 | 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOFT | 0.000 / 0.000 | 0.150 / 0.018 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| HARD | 0.000 / 0.000 | 0.103 / 0.012 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| STEP-FORECAST | 0.478 / 0.065 | 1.117 / 0.481 | 0.826 / 0.389 | 0.564 / 0.293 | 0.670 / 0.540 | 0.791 / 0.491 | 0.485 / 0.173 | 0.319 / 0.068 | 0.097 / 0.010 | 0.280 / 0.008 | 0.000 / 0.000 | 0.150 / 0.004 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| FIRST-TICK-ONLY | 0.727 / 0.143 | 0.890 / 0.454 | 1.000 / 0.636 | 0.598 / 0.449 | 0.652 / 0.578 | 0.732 / 0.661 | 0.703 / 0.632 | 0.429 / 0.389 | 0.310 / 0.281 | 0.178 / 0.163 | 0.182 / 0.167 | 0.123 / 0.113 | 0.076 / 0.070 | 0.062 / 0.057 | 0.014 / 0.013 |
| BASE | 0.574 / 0.208 | 1.020 / 0.620 | 0.955 / 0.792 | 0.610 / 0.541 | 0.541 / 0.496 | 0.786 / 0.721 | 0.642 / 0.594 | 0.322 / 0.299 | 0.220 / 0.205 | 0.160 / 0.149 | 0.159 / 0.148 | 0.109 / 0.101 | 0.061 / 0.056 | 0.071 / 0.066 | 0.003 / 0.003 |
| TAXONOMY-NULL | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — | — / — |

### Call coverage / initial-pool ESS

| Gate (minutes to bell) | Eligible | Initial ESS median | BASE pair calls |
|---:|---:|---:|---:|
| 2880 | 168 | 166.773 | 61 |
| 2160 | 337 | 166.773 | 205 |
| 1440 | 453 | 166.773 | 376 |
| 1080 | 590 | 166.773 | 523 |
| 720 | 796 | 166.773 | 730 |
| 480 | 849 | 166.773 | 779 |
| 360 | 867 | 166.773 | 802 |
| 240 | 877 | 166.773 | 813 |
| 180 | 876 | 166.773 | 817 |
| 120 | 867 | 166.773 | 804 |
| 90 | 864 | 166.773 | 804 |
| 60 | 853 | 166.773 | 791 |
| 30 | 817 | 166.773 | 756 |
| 15 | 774 | 166.773 | 716 |
| 5 | 634 | 166.773 | 577 |

### Same-player members — mean count / mean weight share (reporting only)

| Gate | SOFT | HARD | STEP-FORECAST | FIRST-TICK-ONLY | BASE | TAXONOMY-NULL |
|---:|---|---|---|---|---|---|
| 2880 | 10.974 / 0.026 | 10.576 / 0.026 | 11.026 / 0.026 | 11.026 / 0.026 | 10.230 / 0.024 | 0.000 / — |
| 2160 | 12.028 / 0.026 | 10.578 / 0.026 | 12.067 / 0.027 | 12.067 / 0.028 | 10.936 / 0.025 | 0.000 / — |
| 1440 | 10.925 / 0.023 | 7.681 / 0.024 | 11.191 / 0.026 | 11.191 / 0.028 | 10.099 / 0.025 | 0.000 / — |
| 1080 | 10.612 / 0.023 | 6.408 / 0.024 | 11.103 / 0.026 | 11.103 / 0.028 | 10.046 / 0.025 | 0.000 / — |
| 720 | 9.341 / 0.025 | 4.712 / 0.026 | 10.251 / 0.026 | 10.251 / 0.028 | 9.322 / 0.025 | 0.000 / — |
| 480 | 8.462 / 0.027 | 4.029 / 0.029 | 9.989 / 0.028 | 9.989 / 0.028 | 9.102 / 0.024 | — / — |
| 360 | 7.823 / 0.024 | 3.785 / 0.031 | 9.858 / 0.029 | 9.858 / 0.027 | 8.989 / 0.024 | — / — |
| 240 | 7.310 / 0.026 | 3.583 / 0.030 | 9.792 / 0.028 | 9.792 / 0.027 | 8.923 / 0.024 | — / — |
| 180 | 7.037 / 0.023 | 3.528 / 0.026 | 9.781 / 0.026 | 9.781 / 0.027 | 8.894 / 0.024 | — / — |
| 120 | 6.787 / 0.025 | 3.418 / 0.024 | 9.748 / 0.025 | 9.748 / 0.027 | 8.866 / 0.024 | — / — |
| 90 | 6.639 / 0.029 | 3.364 / 0.026 | 9.754 / 0.027 | 9.754 / 0.027 | 8.856 / 0.024 | — / — |
| 60 | 6.435 / 0.032 | 3.323 / 0.029 | 9.747 / 0.029 | 9.747 / 0.027 | 8.850 / 0.024 | — / — |
| 30 | 6.116 / 0.031 | 3.312 / 0.029 | 9.742 / 0.030 | 9.742 / 0.027 | 8.846 / 0.024 | — / — |
| 15 | 5.957 / 0.030 | 3.308 / 0.030 | 9.742 / 0.032 | 9.742 / 0.027 | 8.846 / 0.024 | — / — |
| 5 | 5.810 / 0.036 | 3.305 / 0.032 | 9.739 / 0.034 | 9.739 / 0.027 | 8.845 / 0.024 | — / — |

### Per-side call denominators — favorite / underdog

| Gate | Eligible pairs | SOFT | HARD | STEP-FORECAST | FIRST-TICK-ONLY | BASE | TAXONOMY-NULL |
|---:|---:|---|---|---|---|---|---|
| 2880 | 168 | 9 / 21 | 9 / 21 | 32 / 44 | 44 / 51 | 82 / 65 | 46 / 42 |
| 2160 | 337 | 63 / 52 | 60 / 51 | 186 / 174 | 211 / 188 | 229 / 222 | 108 / 99 |
| 1440 | 453 | 48 / 36 | 46 / 33 | 276 / 250 | 337 / 314 | 407 / 380 | 221 / 185 |
| 1080 | 590 | 82 / 87 | 81 / 84 | 383 / 393 | 494 / 484 | 529 / 534 | 299 / 243 |
| 720 | 796 | 191 / 179 | 188 / 179 | 690 / 674 | 729 / 725 | 733 / 738 | 477 / 385 |
| 480 | 849 | 169 / 156 | 169 / 157 | 622 / 610 | 789 / 778 | 783 / 793 | 582 / 490 |
| 360 | 867 | 150 / 133 | 148 / 131 | 439 / 463 | 804 / 795 | 807 / 813 | 634 / 541 |
| 240 | 877 | 135 / 112 | 135 / 112 | 343 / 302 | 819 / 804 | 820 / 818 | 684 / 586 |
| 180 | 876 | 99 / 76 | 99 / 76 | 184 / 186 | 817 / 804 | 820 / 823 | 706 / 607 |
| 120 | 867 | 25 / 12 | 25 / 12 | 65 / 66 | 809 / 804 | 808 / 813 | 695 / 611 |
| 90 | 864 | 21 / 10 | 21 / 10 | 56 / 52 | 808 / 799 | 807 / 812 | 694 / 625 |
| 60 | 853 | 19 / 16 | 19 / 16 | 44 / 73 | 800 / 788 | 800 / 797 | 705 / 624 |
| 30 | 817 | 19 / 8 | 19 / 8 | 30 / 24 | 764 / 760 | 763 / 762 | 692 / 617 |
| 15 | 774 | 18 / 12 | 18 / 12 | 29 / 27 | 724 / 718 | 720 / 721 | 651 / 591 |
| 5 | 634 | 9 / 6 | 9 / 5 | 18 / 24 | 588 / 583 | 581 / 583 | 529 / 485 |

## Declared limits

- RULING RUN — tick library only, effective April 18 through July 10 event-name dates; UTC bell can be July 11. No June minute-library members. Candidate pool comparison only; no engine edit.
- Prior trendpath used first-hour-median discovery and flow onset; the operator explicitly replaces both with first true-traded pair discovery and bell slices, and replaces count thresholds with ESS < 10.
- The two taxonomy bench choices are operator-authorized: SLEEPER below category p10 actual trade counts; absolute net after first quarter <=2c for flat-after. Category p10 is retrospective full-library scale, not walk-forward calibration.
- Fixed July family/depth medians are the requested retrospective null and include named games; not an out-of-sample fitted baseline. Gate-family calls use causal prefixes only. ITF categories have no filed numerical-null rows: STORE_SILENT, no ALL borrowing.
- SLEEPER category p10 uses true_print_count_in_span from tick-library rows, checked against the exact per-second sidecar. Gate counts use that sidecar; never volume or change-point counts. Canonical onsets absent from the library stay STORE_SILENT.
- First_tick means the first causal state at which both legs have traded since formation, not a requirement for simultaneous trades. Orientation is by the two first_tick prices; equal prices are excluded.
- Role-open is separate from pool discovery: library postformation_open_cents when supplied, otherwise its filed anchor_cents; named checks use the filed truth-table postformation open. Neither is replaced by a later first-trade price.
- Member missing observations cause no weight update, not a fabricated tick or death; the member stays in the original pool and can forecast only when its clock is observed. Reported availability counts distinguish this.
- Seven price coordinates stay in cents. Volume is a separate log1p likelihood on pair contract-volume increments over each gate interval; no contracts enter the cents distance.
- SOFT updates the seven-price likelihood at every stored tick; volume is multiplied once per completed gate interval. HARD keeps its median-price kill rule (binary price factor) and applies the separate volume factor once per gate; no extra soft-price rule is added to HARD.
- The role-only null has filed depth but no unique numeric early/late timing scalar. Such timing stays silent; family-null rows use their exact published medians, even if that predicted floor lies before the query gate.
- Literal tau-to-minutes replacement retains ORDER4's 0.10 tolerance as 0.10 minutes; absolute timing errors in minutes are primary.
- ORDER4 reach still uses the running low after placement (possibly retaining a past dip). The separate future_print_reached diagnostic uses second-close last prices; same-second non-closing prints can be omitted. Neither metric certifies a maker fill; the tick-library receipt licenses MACRO/MICRO, not execution proof.
- No full-worktree OS, builder, shape-organ or face edits are made; this tool reads only explicit library and named-check inputs.
- Named custody files have no SQLite rowid or consolidated cross-source join: deterministic within-second source row order substitutes only for ordering, with trade_id dedupe unchanged. Native exchange true prints and recorded books, no minute closes; second extrema retained.
- SUPERSEDES ATP_MAIN @0c8850b7: its Q was the minimum of a pointwise-quantile path and its X used future query timestamps. Those tables are not the causal organ acceptance baseline. Other category runs with that definition are not comparable to this corrected run.
- Q quantiles are current query last plus weighted quantiles of each historical member's remaining minimum minus its current last. Remaining paths include the carried gate state and native member changes after the gate; earliest minimum wins, and no further dip has floor time at the gate. X is the independent weighted median of member floor minutes-to-bell, mapped by query bell minus X*60; q25/q75 times are independent marginal quantiles, not paired trajectories.
- Forecast curves and path scoring use only subsequent fixed atlas gates. Q/X use complete historical member remainders, never future query timestamps. At the final atlas gate Q/X remain available, but no subsequent atlas path error is claimed.
- Roles, first-bind and flips use only receipts observed from first pair bind through this receipt. Final-truth accuracy lives in a separately labelled retrospective evaluation block. Gate SCORABLE is an evaluation denominator only, never a prediction gate.
- VALIDITY retains the raw share for audit and is labelled INVALID: ESS < 10 below the atlas evidence floor; never an accepted call below ten.
