# RULING RUN — TICK LIBRARY — CANDIDATE POOL SCOREBOARD

No engine change or automatic rule selection. Book reach is diagnostic only, not execution proof.

Error means are conditional on called sides. Utility shows both called-pair and all-eligible-query denominators; NO-CALL contributes zero only to reach/discount utility. These are not matched-cohort comparisons.

## ATP_MAIN

### MACRO — favorite / underdog last-path MAE

| Rule | 2880 | 2160 | 1440 | 1080 | 720 | 480 | 360 | 240 | 180 | 120 | 90 | 60 | 30 | 15 | 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOFT | 1.468 ; 1.733 | 2.165 ; 1.959 | 2.177 ; 2.481 | 2.291 ; 2.327 | 1.573 ; 1.603 | 1.362 ; 1.261 | 1.163 ; 1.079 | 0.973 ; 1.060 | 0.854 ; 0.867 | 0.780 ; 0.852 | 0.663 ; 1.193 | 0.673 ; 0.683 | 0.488 ; 0.956 | 0.470 ; 0.380 | 0.741 ; 3.552 |
| HARD | 1.468 ; 1.733 | 2.095 ; 1.924 | 2.125 ; 2.321 | 2.159 ; 2.083 | 1.566 ; 1.591 | 1.360 ; 1.249 | 1.127 ; 0.997 | 0.973 ; 1.060 | 0.854 ; 0.867 | 0.780 ; 0.852 | 0.663 ; 1.193 | 0.673 ; 0.683 | 0.488 ; 0.956 | 0.470 ; 0.380 | 0.741 ; 0.453 |
| STEP-FORECAST | 1.771 ; 1.697 | 2.122 ; 2.095 | 1.776 ; 1.832 | 1.793 ; 1.709 | 1.527 ; 1.475 | 1.401 ; 1.392 | 1.345 ; 1.363 | 1.150 ; 1.217 | 0.936 ; 0.950 | 1.012 ; 1.190 | 0.711 ; 0.834 | 1.047 ; 0.899 | 0.664 ; 0.733 | 0.609 ; 0.474 | 0.782 ; 1.141 |
| FIRST-TICK-ONLY | 2.049 ; 1.985 | 2.069 ; 2.000 | 1.804 ; 1.803 | 1.760 ; 1.629 | 1.502 ; 1.452 | 1.369 ; 1.356 | 1.248 ; 1.260 | 1.143 ; 1.168 | 1.093 ; 1.091 | 1.025 ; 1.046 | 0.930 ; 0.979 | 0.899 ; 0.916 | 0.770 ; 0.787 | 0.577 ; 0.615 | 0.542 ; 0.596 |
| BASE | 1.816 ; 2.020 | 2.017 ; 1.997 | 1.887 ; 1.894 | 1.744 ; 1.663 | 1.468 ; 1.460 | 1.386 ; 1.363 | 1.278 ; 1.276 | 1.169 ; 1.186 | 1.118 ; 1.106 | 1.046 ; 1.063 | 0.967 ; 1.002 | 0.920 ; 0.917 | 0.785 ; 0.789 | 0.593 ; 0.615 | 0.544 ; 0.612 |
| TAXONOMY-NULL | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — | — ; — |

### MICRO — floor MAE / median absolute error, favorite then underdog

| Rule | 2880 | 2160 | 1440 | 1080 | 720 | 480 | 360 | 240 | 180 | 120 | 90 | 60 | 30 | 15 | 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOFT | 1.000/1.000 ; 1.286/1.000 | 1.889/1.000 ; 2.635/1.000 | 2.146/1.000 ; 3.250/2.000 | 3.122/1.000 ; 2.126/1.000 | 2.073/1.000 ; 1.620/1.000 | 1.817/1.000 ; 1.423/1.000 | 1.580/1.000 ; 1.421/1.000 | 1.341/1.000 ; 1.348/1.000 | 1.354/1.000 ; 1.118/1.000 | 1.120/1.000 ; 0.917/1.000 | 1.667/1.000 ; 2.200/1.500 | 1.684/1.000 ; 1.625/1.000 | 0.737/1.000 ; 2.625/1.000 | 0.833/0.000 ; 0.500/0.000 | 1.444/0.000 ; 4.833/0.500 |
| HARD | 1.000/1.000 ; 1.286/1.000 | 1.817/1.000 ; 2.549/1.000 | 2.152/1.000 ; 3.152/2.000 | 2.679/2.000 ; 2.024/1.000 | 2.074/1.000 ; 1.603/1.000 | 1.817/1.000 ; 1.420/1.000 | 1.514/1.000 ; 1.275/1.000 | 1.333/1.000 ; 1.348/1.000 | 1.354/1.000 ; 1.118/1.000 | 1.120/1.000 ; 0.917/1.000 | 1.667/1.000 ; 2.200/1.500 | 1.684/1.000 ; 1.625/1.000 | 0.737/1.000 ; 2.625/1.000 | 0.833/0.000 ; 0.500/0.000 | 1.444/0.000 ; 0.600/0.000 |
| STEP-FORECAST | 2.156/1.000 ; 2.159/1.000 | 2.403/1.000 ; 2.701/2.000 | 2.192/1.000 ; 2.476/2.000 | 2.371/1.000 ; 2.120/1.000 | 2.154/1.000 ; 1.709/1.000 | 2.087/1.000 ; 1.787/1.000 | 2.007/1.000 ; 1.678/1.000 | 1.659/1.000 ; 1.675/1.000 | 1.435/1.000 ; 1.339/1.000 | 1.523/1.000 ; 1.515/1.000 | 1.554/1.000 ; 1.250/1.000 | 2.159/1.000 ; 1.438/1.000 | 1.033/1.000 ; 1.500/1.000 | 1.241/1.000 ; 0.593/0.000 | 1.222/0.500 ; 1.667/0.000 |
| FIRST-TICK-ONLY | 3.023/1.000 ; 2.137/1.000 | 2.450/2.000 ; 2.516/2.000 | 2.285/2.000 ; 2.287/2.000 | 2.332/1.000 ; 2.130/1.000 | 2.160/1.000 ; 1.868/1.000 | 2.188/1.000 ; 1.947/1.000 | 2.040/1.000 ; 1.922/1.000 | 1.929/1.000 ; 1.769/1.000 | 1.900/1.000 ; 1.692/1.000 | 1.821/1.000 ; 1.580/1.000 | 1.691/1.000 ; 1.551/1.000 | 1.562/1.000 ; 1.435/1.000 | 1.389/1.000 ; 1.229/1.000 | 1.170/1.000 ; 0.967/1.000 | 0.898/0.000 ; 0.799/0.000 |
| BASE | 2.439/1.000 ; 2.031/1.000 | 2.576/2.000 ; 2.662/2.000 | 2.356/2.000 ; 2.334/2.000 | 2.310/1.000 ; 2.165/1.500 | 2.135/1.000 ; 1.938/1.000 | 2.250/1.000 ; 2.083/1.000 | 2.129/1.000 ; 2.071/2.000 | 1.989/1.000 ; 1.818/1.000 | 1.939/1.000 ; 1.680/1.000 | 1.859/1.000 ; 1.609/1.000 | 1.737/1.000 ; 1.571/1.000 | 1.596/1.000 ; 1.455/1.000 | 1.418/1.000 ; 1.234/1.000 | 1.185/1.000 ; 0.967/1.000 | 0.897/0.000 ; 0.798/0.000 |
| TAXONOMY-NULL | 2.978/2.500 ; 3.595/3.000 | 4.449/3.000 ; 5.490/2.500 | 4.113/2.500 ; 4.724/2.000 | 3.935/2.000 ; 4.749/2.000 | 3.927/2.000 ; 5.069/2.000 | 3.788/2.000 ; 4.583/2.000 | 3.905/3.000 ; 4.447/2.000 | 3.982/3.000 ; 4.376/2.000 | 4.051/3.000 ; 4.344/2.000 | 4.198/3.000 ; 4.317/2.000 | 4.148/3.000 ; 4.205/2.000 | 4.214/3.000 ; 4.266/2.000 | 4.319/3.000 ; 4.395/2.500 | 4.278/3.000 ; 4.337/2.500 | 4.320/3.000 ; 4.607/2.500 |

### MICRO-MICRO — q50 pair reach × discount, per called pair / per eligible query

| Rule | 2880 | 2160 | 1440 | 1080 | 720 | 480 | 360 | 240 | 180 | 120 | 90 | 60 | 30 | 15 | 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOFT | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| HARD | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| STEP-FORECAST | 0.174 / 0.024 | 0.048 / 0.021 | 0.014 / 0.007 | 0.007 / 0.003 | 0.022 / 0.018 | 0.011 / 0.007 | 0.016 / 0.006 | 0.021 / 0.005 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| FIRST-TICK-ONLY | 0.121 / 0.024 | 0.041 / 0.021 | 0.024 / 0.015 | 0.016 / 0.012 | 0.010 / 0.009 | 0.008 / 0.007 | 0.003 / 0.002 | -0.001 / -0.001 | 0.000 / 0.000 | 0.004 / 0.003 | -0.003 / -0.002 | 0.000 / 0.000 | -0.005 / -0.005 | 0.003 / 0.003 | 0.003 / 0.003 |
| BASE | 0.000 / 0.000 | 0.015 / 0.009 | 0.011 / 0.009 | 0.000 / 0.000 | 0.018 / 0.016 | 0.000 / 0.000 | 0.004 / 0.003 | -0.002 / -0.002 | 0.004 / 0.003 | 0.005 / 0.005 | -0.002 / -0.002 | 0.000 / 0.000 | -0.005 / -0.005 | 0.010 / 0.009 | 0.002 / 0.002 |
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
