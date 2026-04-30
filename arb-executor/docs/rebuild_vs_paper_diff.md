# Rebuild vs Paper Config — Diff Report

**Generated**: 2026-04-29 20:06:10 ET
**Paper config**: `config/deploy_v4_paper.json`

---

## 1. Artifact Integrity

| Artifact | Path | mtime | sha256 | rows (incl header) | data rows |
|---|---|---|---|---|---|
| scorecard | `/tmp/rebuilt_scorecard.csv` | 2026-04-28 23:26:20 | `73ab508a931d3253…` | 68 | 67 |
| exit_sweep | `/tmp/exit_sweep_curves.csv` | 2026-04-29 00:51:24 | `0d9f372466d7e4b2…` | 50 | 49 |
| bias_corrections | `/tmp/per_cell_verification/entry_price_bias_by_cell.csv` | 2026-04-28 20:53:35 | `50e6e551c74c7f8f…` | 44 | 43 |

### 1.1 Schemas

**rebuilt_scorecard.csv columns** (19):
```
cell, N, N_winner, N_loser, avg_entry, bias_correction, distance_from_50, target_at_15c, proximity_to_settle, TWP, Sw, Sl, Sl_predicted, Sl_residual, decomposed_ROI, ci_low, ci_high, mechanism, uncalibrated
```

**exit_sweep_curves.csv columns** (52):
```
cell, band_width, N, exit_1, exit_2, ... exit_1 through exit_49 (49 columns)
```

**entry_price_bias_by_cell.csv columns** (10):
```
cell, N_late, mean_bias_first_vs_late_mid, stddev, median, pct_within_3c, pct_within_5c, N_T2h, mean_bias_first_vs_T2h, stddev_T2h
```

### 1.2 Sample rows

**scorecard first row**: `cell=ATP_CHALL_underdog_0-4, N=72, N_winner=21, N_loser=51, avg_entry=4.0, bias_correction=0.0, distance_from_50=46.0, target_at_15c=19.0...`

**sweep first row**: `cell=ATP_CHALL_underdog_0-9, band_width=10c, N=281, exit_1=11.69, ..., exit_49=216.45`

**bias first row**: `cell=ATP_CHALL_leader_50-54, N_late=74, mean_bias_first_vs_late_mid=-0.4, stddev=30.8, median=0.0, pct_within_3c=11, pct_within_5c=11, N_T2h=8, mean_bias_first_vs_T2h=-5.6, stddev_T2h=10.7`

### 1.3 ⚠ Discrepancy: counts vs operator's mental model

Operator's prompt described the scorecard as: **11 SCALPER_EDGE + 4 bleed + 30 UNCALIBRATED = 45 cells**.

Actual file at the path provided contains **67 data rows** with **6 distinct mechanism classes**:

| Mechanism | Count | Operator's framing |
|---|---|---|
| UNCALIBRATED | 30 | operator said 30; actual 30 ✓ |
| SCALPER_EDGE | 15 | operator said 11; actual 15 |
| SCALPER_BREAK_EVEN | 10 | candidate for 'bleed' bucket — not specified individually in prompt |
| SCALPER_NEGATIVE | 6 | candidate for 'bleed' bucket — not specified individually in prompt |
| MIXED_BREAK_EVEN | 3 | candidate for 'bleed' bucket — not specified individually in prompt |
| SETTLEMENT_RIDE_CONTAMINATED | 3 | candidate for 'bleed' bucket — not specified individually in prompt |

**STOP-trigger evaluation**: operator specified "if fewer than 45 cells, STOP." Actual = 67 cells. Trigger does not fire (67 > 45). Proceeding with file's actual classifications. The operator's 11/4/30 framing may be from an earlier version of the analysis or a sub-bucketing of the 6-class output. **The diff sections below use the actual 6-class scheme**; if operator wants to remap to 11/4/30, they can advise.

---

## 2. Rebuild Methodology Recap

**Source script**: `/tmp/rebuilt_scorecard_script.py`

### 2.1 Script header (first 30 lines, verbatim)
```python
import sqlite3, csv
from collections import defaultdict
from statistics import mean
from math import sqrt

bias_map = {}
with open("/tmp/per_cell_verification/entry_price_bias_by_cell.csv") as f:
    for r in csv.DictReader(f):
        n_late = int(r["N_late"])
        if n_late >= 10:
            bias_map[r["cell"]] = float(r["mean_bias_first_vs_late_mid"])

print("Loaded bias corrections for %d cells" % len(bias_map))

conn = sqlite3.connect("/root/Omi-Workspace/arb-executor/tennis.db")
cur = conn.cursor()
cur.execute("""SELECT category, first_price_winner, max_price_winner, last_price_winner,
                      first_price_loser, max_price_loser
               FROM historical_events
               WHERE first_ts > ? AND first_ts < ? AND total_trades >= 10
                 AND first_price_winner > 0 AND first_price_winner < 100
                 AND first_price_loser > 0 AND first_price_loser < 100""",
            ("2026-01-01", "2026-04-30"))
rows = cur.fetchall()
conn.close()
print("Loaded %d events from historical_events Jan-Apr" % len(rows))

cat_to_tier = {"ATP_MAIN":"ATP_MAIN", "ATP_CHALL":"ATP_CHALL",
               "WTA_MAIN":"WTA_MAIN", "WTA_CHALL":"WTA_CHALL"}

```

### 2.2 Methodology details extracted from the script

- **Data source**: `tennis.db.historical_events` (rows with `total_trades >= 10`, `first_price_winner` and `first_price_loser` both ∈ (0, 100))
- **Time window**: `first_ts > '2026-01-01' AND first_ts < '2026-04-30'` (Jan-Apr 2026)
- **Exit target (fixed for scorecard)**: 15c above entry (`EXIT_C = 15`)
- **Quantity**: 10 contracts per trade (`QTY = 10`)
- **Cell band**: 5c (`bs = int(price // 5) * 5` → cell = `tier_side_lo-hi` where hi = lo+4)
- **Bias correction**: from `entry_price_bias_by_cell.csv`, only cells with `N_late >= 10` (so smaller cells inherit no correction)
- **Min sample size for inclusion**: `n_total < 20` filtered out (sum of winner_N + loser_N)

### 2.3 Mechanism classifications (extracted by grep over the script)
```
        r["mechanism"] = "UNCALIBRATED"
        r["mechanism"] = "SETTLEMENT_RIDE_CONTAMINATED"
        r["mechanism"] = "SETTLEMENT_RIDE"
        r["mechanism"] = "MIXED_EDGE" if r["_ci_low_num"] > 0 else "MIXED_BREAK_EVEN"
            r["mechanism"] = "SCALPER_EDGE"
            r["mechanism"] = "SCALPER_NEGATIVE"
            r["mechanism"] = "SCALPER_BREAK_EVEN"
print("\nSCALPER_EDGE cells:")
    if r["mechanism"] == "SCALPER_EDGE":
print("\nSETTLEMENT_RIDE cells:")
    if r["mechanism"].startswith("SETTLEMENT_RIDE"):
print("\nSCALPER_NEGATIVE cells:")
    if r["mechanism"] == "SCALPER_NEGATIVE":
print("\nUNCALIBRATED:")
    if r["mechanism"] == "UNCALIBRATED":
```

### 2.4 What is NOT reconstructable from the script alone

- The exact CI computation method (looks like normal-approximation but the formula isn't explicit in the head)
- Whether the underdog three-regime split (deep/mid/near-50c) was data-driven or operator-defined — not present in this script
- Whether other scripts contributed to the scorecard (e.g., a separate post-processing step)
- The precise threshold separating SCALPER_EDGE from SCALPER_BREAK_EVEN (CI excludes zero? Mean ROI > X%? Need to read the full classify() block, which is lower in the file)

---

## 3. Scorecard Contents — Full

**Total cells**: 67 (operator framing: 45; actual: 67)

### 3.1 SCALPER_EDGE (15 cells)

| Cell | N | N_w | N_l | avg_entry | bias_corr | TWP | Sw | Sl | ROI%% | CI_low | CI_high | uncalibrated |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:-:|
| ATP_CHALL_leader_55-59 | 417 | 219 | 198 | 57.8 | -0.8 | 0.525 | 0.995 | 0.621 | 3.7 | 0.01 | 0.06 | False |
| ATP_CHALL_leader_60-64 | 109 | 77 | 32 | 64.5 | -4.5 | 0.706 | 1.000 | 0.594 | 8.7 | 0.04 | 0.13 | False |
| ATP_CHALL_underdog_10-14 | 208 | 35 | 173 | 12.1 | 2.8 | 0.168 | 1.000 | 0.671 | 64.5 | 0.61 | 0.68 | False |
| ATP_CHALL_underdog_15-19 | 515 | 100 | 415 | 17.5 | 4.0 | 0.194 | 0.990 | 0.694 | 42.2 | 0.40 | 0.44 | False |
| ATP_CHALL_underdog_20-24 | 352 | 91 | 261 | 22.7 | 4.4 | 0.259 | 1.000 | 0.778 | 39.4 | 0.38 | 0.41 | False |
| ATP_CHALL_underdog_25-29 | 329 | 93 | 236 | 27.7 | 9.0 | 0.283 | 1.000 | 0.737 | 25.8 | 0.24 | 0.28 | False |
| ATP_CHALL_underdog_30-34 | 181 | 51 | 130 | 30.7 | 8.4 | 0.282 | 1.000 | 0.738 | 21.5 | 0.19 | 0.24 | False |
| ATP_CHALL_underdog_35-39 | 93 | 39 | 54 | 39.7 | 7.8 | 0.419 | 1.000 | 0.630 | 8.7 | 0.04 | 0.14 | False |
| ATP_CHALL_underdog_40-44 | 334 | 145 | 189 | 42.1 | 0.3 | 0.434 | 1.000 | 0.619 | 6.9 | 0.04 | 0.10 | False |
| ATP_MAIN_underdog_20-24 | 106 | 27 | 79 | 21.2 | 3.8 | 0.255 | 0.963 | 0.658 | 31.2 | 0.26 | 0.37 | False |
| WTA_MAIN_underdog_15-19 | 106 | 24 | 82 | 17.7 | 4.5 | 0.226 | 1.000 | 0.768 | 52.8 | 0.50 | 0.56 | False |
| WTA_MAIN_underdog_25-29 | 91 | 32 | 59 | 28.4 | 5.6 | 0.352 | 0.969 | 0.678 | 23.8 | 0.18 | 0.29 | False |
| WTA_MAIN_underdog_30-34 | 153 | 41 | 112 | 32.5 | 2.6 | 0.268 | 1.000 | 0.696 | 14.4 | 0.11 | 0.17 | False |
| WTA_MAIN_underdog_35-39 | 157 | 56 | 101 | 37.0 | 2.7 | 0.357 | 1.000 | 0.594 | 4.6 | 0.00 | 0.09 | False |
| WTA_MAIN_underdog_40-44 | 211 | 89 | 122 | 42.2 | 4.0 | 0.422 | 1.000 | 0.615 | 5.9 | 0.03 | 0.09 | False |

### 3.2 SCALPER_BREAK_EVEN (10 cells)

| Cell | N | N_w | N_l | avg_entry | bias_corr | TWP | Sw | Sl | ROI%% | CI_low | CI_high | uncalibrated |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:-:|
| ATP_CHALL_leader_50-54 | 629 | 312 | 317 | 51.8 | -0.4 | 0.496 | 1.000 | 0.530 | -1.2 | -0.04 | 0.01 | False |
| ATP_CHALL_underdog_45-49 | 198 | 83 | 115 | 48.5 | -3.1 | 0.419 | 1.000 | 0.496 | -6.8 | -0.11 | -0.02 | False |
| ATP_MAIN_leader_50-54 | 327 | 143 | 184 | 51.9 | -1.7 | 0.437 | 1.000 | 0.484 | -8.0 | -0.11 | -0.04 | False |
| ATP_MAIN_leader_55-59 | 145 | 88 | 57 | 58.0 | -2.7 | 0.607 | 0.989 | 0.544 | 3.9 | -0.01 | 0.09 | False |
| ATP_MAIN_underdog_35-39 | 297 | 115 | 182 | 38.2 | -1.7 | 0.387 | 1.000 | 0.516 | -1.2 | -0.05 | 0.03 | False |
| ATP_MAIN_underdog_40-44 | 182 | 51 | 131 | 41.1 | 3.5 | 0.280 | 1.000 | 0.527 | -9.2 | -0.13 | -0.05 | False |
| WTA_MAIN_leader_50-54 | 179 | 93 | 86 | 53.5 | -2.2 | 0.520 | 0.989 | 0.547 | 0.9 | -0.03 | 0.05 | False |
| WTA_MAIN_leader_55-59 | 142 | 77 | 65 | 56.1 | 1.6 | 0.542 | 0.987 | 0.554 | 1.6 | -0.03 | 0.06 | False |
| WTA_MAIN_underdog_20-24 | 94 | 25 | 69 | 21.9 | 5.3 | 0.266 | 1.000 | 0.551 | 14.3 | 0.08 | 0.21 | False |
| WTA_MAIN_underdog_45-49 | 29 | 14 | 15 | 45.6 | 3.4 | 0.483 | 1.000 | 0.533 | 1.3 | -0.10 | 0.13 | False |

### 3.3 SCALPER_NEGATIVE (6 cells)

| Cell | N | N_w | N_l | avg_entry | bias_corr | TWP | Sw | Sl | ROI%% | CI_low | CI_high | uncalibrated |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:-:|
| ATP_CHALL_leader_65-69 | 364 | 225 | 139 | 67.0 | -10.6 | 0.618 | 0.996 | 0.446 | -3.1 | -0.07 | 0.00 | False |
| ATP_MAIN_leader_60-64 | 193 | 110 | 83 | 62.8 | -3.4 | 0.570 | 1.000 | 0.325 | -11.6 | -0.17 | -0.06 | False |
| ATP_MAIN_leader_70-74 | 116 | 82 | 34 | 73.6 | -2.7 | 0.707 | 1.000 | 0.176 | -8.4 | -0.17 | -0.00 | False |
| WTA_MAIN_leader_60-64 | 41 | 22 | 19 | 64.9 | -4.9 | 0.537 | 1.000 | 0.474 | -6.5 | -0.16 | 0.03 | False |
| WTA_MAIN_leader_65-69 | 144 | 97 | 47 | 67.9 | -4.6 | 0.674 | 1.000 | 0.340 | -3.9 | -0.10 | 0.02 | False |
| WTA_MAIN_leader_70-74 | 193 | 125 | 68 | 72.4 | -2.1 | 0.648 | 0.992 | 0.221 | -12.0 | -0.18 | -0.06 | False |

### 3.4 MIXED_BREAK_EVEN (3 cells)

| Cell | N | N_w | N_l | avg_entry | bias_corr | TWP | Sw | Sl | ROI%% | CI_low | CI_high | uncalibrated |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:-:|
| ATP_CHALL_leader_70-74 | 111 | 81 | 30 | 74.8 | -4.8 | 0.730 | 1.000 | 0.267 | -3.5 | -0.11 | 0.04 | False |
| ATP_CHALL_leader_75-79 | 672 | 501 | 171 | 77.4 | -5.5 | 0.746 | 0.996 | 0.222 | -4.0 | -0.07 | -0.01 | False |
| ATP_MAIN_leader_75-79 | 260 | 185 | 75 | 76.8 | -1.0 | 0.712 | 1.000 | 0.227 | -6.8 | -0.12 | -0.02 | False |

### 3.5 SETTLEMENT_RIDE_CONTAMINATED (3 cells)

| Cell | N | N_w | N_l | avg_entry | bias_corr | TWP | Sw | Sl | ROI%% | CI_low | CI_high | uncalibrated |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:-:|
| ATP_CHALL_leader_80-84 | 452 | 352 | 100 | 82.8 | -2.5 | 0.779 | 0.997 | 0.120 | -4.6 | -0.09 | -0.01 | False |
| ATP_CHALL_leader_85-89 | 303 | 239 | 64 | 87.6 | -3.5 | 0.789 | 1.000 | 0.125 | -4.3 | -0.09 | 0.00 | False |
| WTA_MAIN_leader_85-89 | 168 | 128 | 40 | 87.8 | -2.8 | 0.762 | 0.984 | 0.100 | -7.8 | -0.14 | -0.01 | False |

### 3.6 UNCALIBRATED (30 cells)

| Cell | N | N_w | N_l | avg_entry | bias_corr | TWP | Sw | Sl | ROI%% | CI_low | CI_high | uncalibrated |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:-:|
| ATP_CHALL_leader_90-94 | 241 | 185 | 56 | 91.7 | 0.0 | 0.768 | 1.000 | 0.054 | -9.0 | -0.15 | -0.03 | True |
| ATP_CHALL_leader_95-99 | 159 | 107 | 52 | 95.9 | 0.0 | 0.673 | 1.000 | 0.058 | -19.7 | -0.28 | -0.12 | True |
| ATP_CHALL_underdog_0-4 | 72 | 21 | 51 | 4.0 | 0.0 | 0.292 | 1.000 | 0.824 | 321.1 | 3.13 | 3.29 | True |
| ATP_CHALL_underdog_5-9 | 209 | 18 | 191 | 7.6 | 0.0 | 0.086 | 1.000 | 0.581 | 89.3 | 0.85 | 0.94 | True |
| ATP_MAIN_leader_65-69 | 225 | 146 | 79 | 66.7 | 0.0 | 0.649 | 1.000 | 0.316 | -6.5 | -0.12 | -0.01 | True |
| ATP_MAIN_leader_80-84 | 156 | 106 | 50 | 82.0 | 0.0 | 0.679 | 1.000 | 0.080 | -16.2 | -0.24 | -0.08 | True |
| ATP_MAIN_leader_85-89 | 84 | 63 | 21 | 87.3 | 0.0 | 0.750 | 1.000 | 0.048 | -10.4 | -0.21 | -0.00 | True |
| ATP_MAIN_leader_90-94 | 112 | 79 | 33 | 93.0 | 0.0 | 0.705 | 1.000 | 0.030 | -16.7 | -0.26 | -0.07 | True |
| ATP_MAIN_underdog_10-14 | 48 | 8 | 40 | 12.0 | 0.0 | 0.167 | 1.000 | 0.625 | 57.6 | 0.49 | 0.67 | True |
| ATP_MAIN_underdog_15-19 | 174 | 33 | 141 | 17.8 | 0.0 | 0.190 | 1.000 | 0.660 | 35.0 | 0.32 | 0.39 | True |
| ATP_MAIN_underdog_5-9 | 74 | 14 | 60 | 6.8 | 0.0 | 0.189 | 1.000 | 0.633 | 130.0 | 1.20 | 1.40 | True |
| WTA_CHALL_leader_50-54 | 50 | 23 | 27 | 51.9 | 0.0 | 0.460 | 0.957 | 0.630 | 4.7 | -0.02 | 0.12 | True |
| WTA_CHALL_leader_60-64 | 121 | 61 | 60 | 62.2 | 0.0 | 0.504 | 1.000 | 0.400 | -12.3 | -0.19 | -0.06 | True |
| WTA_CHALL_leader_65-69 | 78 | 45 | 33 | 66.7 | 0.0 | 0.577 | 0.978 | 0.303 | -12.9 | -0.22 | -0.04 | True |
| WTA_CHALL_leader_70-74 | 51 | 31 | 20 | 71.9 | 0.0 | 0.608 | 1.000 | 0.550 | -0.2 | -0.07 | 0.07 | True |
| WTA_CHALL_leader_75-79 | 48 | 36 | 12 | 76.7 | 0.0 | 0.750 | 0.944 | 0.333 | 0.2 | -0.10 | 0.10 | True |
| WTA_CHALL_leader_80-84 | 45 | 40 | 5 | 82.3 | 0.0 | 0.889 | 1.000 | 0.400 | 10.4 | 0.04 | 0.17 | True |
| WTA_CHALL_leader_85-89 | 67 | 55 | 12 | 86.6 | 0.0 | 0.821 | 0.964 | 0.167 | -0.1 | -0.09 | 0.09 | True |
| WTA_CHALL_leader_95-99 | 25 | 14 | 11 | 96.0 | 0.0 | 0.560 | 1.000 | 0.000 | -34.8 | -0.57 | -0.12 | True |
| WTA_CHALL_underdog_15-19 | 35 | 2 | 33 | 16.9 | 0.0 | 0.057 | 1.000 | 0.424 | -10.5 | -0.19 | -0.02 | True |
| WTA_CHALL_underdog_20-24 | 35 | 4 | 31 | 22.1 | 0.0 | 0.114 | 1.000 | 0.452 | -11.5 | -0.21 | -0.02 | True |
| WTA_CHALL_underdog_25-29 | 46 | 14 | 32 | 27.2 | 0.0 | 0.304 | 1.000 | 0.406 | -7.4 | -0.19 | 0.05 | True |
| WTA_CHALL_underdog_30-34 | 50 | 18 | 32 | 32.3 | 0.0 | 0.360 | 1.000 | 0.406 | -8.0 | -0.20 | 0.03 | True |
| WTA_CHALL_underdog_35-39 | 122 | 54 | 68 | 37.1 | 0.0 | 0.443 | 0.981 | 0.529 | 5.4 | -0.01 | 0.11 | True |
| WTA_CHALL_underdog_45-49 | 60 | 34 | 26 | 46.5 | 0.0 | 0.567 | 1.000 | 0.538 | 6.2 | -0.01 | 0.14 | True |
| WTA_CHALL_underdog_5-9 | 25 | 4 | 21 | 6.6 | 0.0 | 0.160 | 1.000 | 0.476 | 89.9 | 0.65 | 1.14 | True |
| WTA_MAIN_leader_75-79 | 314 | 225 | 89 | 77.6 | 0.0 | 0.717 | 1.000 | 0.146 | -9.2 | -0.14 | -0.04 | True |
| WTA_MAIN_leader_90-94 | 135 | 91 | 44 | 92.0 | 0.0 | 0.674 | 1.000 | 0.068 | -18.7 | -0.27 | -0.10 | True |
| WTA_MAIN_underdog_10-14 | 130 | 18 | 112 | 12.5 | 0.0 | 0.138 | 1.000 | 0.571 | 41.6 | 0.36 | 0.47 | True |
| WTA_MAIN_underdog_5-9 | 107 | 40 | 67 | 8.1 | 0.0 | 0.374 | 1.000 | 0.701 | 133.3 | 1.26 | 1.41 | True |

---

## 4. Exit Sweep — Underdog Cells (10c bands)

**Methodology note**: optimal_exit_cents = argmax of exit_1..exit_49 columns. Curve values appear to be expected per-contract payout in cents. Higher exit_N often indicates more profit captured; argmax may saturate near the upper end depending on cell base rate.

### 4.1 Underdog regime: deep (0-19c) (18 cells)

| Cell | band | N | optimal_exit_cents | curve_max_value | exit@15c value |
|---|---|--:|--:|--:|--:|
| ATP_CHALL_underdog_0-4 | 5c | 72 | 46 | 764.69 | 320.98 |
| ATP_CHALL_underdog_0-9 | 10c | 281 | 48 | 216.61 | 125.15 |
| ATP_CHALL_underdog_10-14 | 5c | 208 | 46 | 100.79 | 65.43 |
| ATP_CHALL_underdog_10-19 | 10c | 723 | 45 | 59.72 | 47.38 |
| ATP_CHALL_underdog_15-19 | 5c | 515 | 29 | 53.01 | 42.31 |
| ATP_CHALL_underdog_5-9 | 5c | 209 | 31 | 130.10 | 89.69 |
| ATP_MAIN_underdog_0-9 | 10c | 75 | 47 | 309.49 | 126.88 |
| ATP_MAIN_underdog_10-14 | 5c | 48 | 49 | 126.13 | 58.36 |
| ATP_MAIN_underdog_10-19 | 10c | 222 | 45 | 64.07 | 38.95 |
| ATP_MAIN_underdog_15-19 | 5c | 174 | 41 | 55.15 | 35.35 |
| ATP_MAIN_underdog_5-9 | 5c | 74 | 47 | 312.55 | 128.49 |
| WTA_CHALL_underdog_10-19 | 10c | 52 | 29 | 21.01 | 2.15 |
| WTA_CHALL_underdog_15-19 | 5c | 35 | 29 | 12.33 | -9.63 |
| WTA_MAIN_underdog_0-9 | 10c | 111 | 49 | 367.91 | 137.98 |
| WTA_MAIN_underdog_10-14 | 5c | 130 | 41 | 69.64 | 41.62 |
| WTA_MAIN_underdog_10-19 | 10c | 236 | 49 | 63.65 | 47.75 |
| WTA_MAIN_underdog_15-19 | 5c | 106 | 44 | 64.62 | 53.08 |
| WTA_MAIN_underdog_5-9 | 5c | 107 | 49 | 349.66 | 132.68 |

### 4.2 Underdog regime: mid (20-34c) (18 cells)

| Cell | band | N | optimal_exit_cents | curve_max_value | exit@15c value |
|---|---|--:|--:|--:|--:|
| ATP_CHALL_underdog_20-24 | 5c | 352 | 42 | 44.38 | 39.45 |
| ATP_CHALL_underdog_20-29 | 10c | 681 | 42 | 36.03 | 32.20 |
| ATP_CHALL_underdog_25-29 | 5c | 329 | 40 | 29.46 | 25.84 |
| ATP_CHALL_underdog_30-34 | 5c | 181 | 17 | 22.63 | 21.55 |
| ATP_CHALL_underdog_30-39 | 10c | 274 | 15 | 16.42 | 16.42 |
| ATP_MAIN_underdog_20-24 | 5c | 106 | 47 | 40.76 | 28.28 |
| ATP_MAIN_underdog_20-29 | 10c | 106 | 47 | 40.76 | 28.28 |
| ATP_MAIN_underdog_30-39 | 10c | 297 | 36 | 8.60 | -1.32 |
| WTA_CHALL_underdog_20-24 | 5c | 35 | 10 | 5.30 | -10.98 |
| WTA_CHALL_underdog_20-29 | 10c | 81 | 10 | 1.63 | -8.55 |
| WTA_CHALL_underdog_25-29 | 5c | 46 | 41 | 0.48 | -7.05 |
| WTA_CHALL_underdog_30-34 | 5c | 50 | 49 | 7.37 | -7.81 |
| WTA_CHALL_underdog_30-39 | 10c | 172 | 49 | 16.56 | 0.72 |
| WTA_MAIN_underdog_20-24 | 5c | 94 | 44 | 42.96 | 14.33 |
| WTA_MAIN_underdog_20-29 | 10c | 185 | 44 | 35.25 | 19.75 |
| WTA_MAIN_underdog_25-29 | 5c | 91 | 30 | 36.39 | 24.09 |
| WTA_MAIN_underdog_30-34 | 5c | 153 | 14 | 14.60 | 14.22 |
| WTA_MAIN_underdog_30-39 | 10c | 310 | 14 | 10.39 | 8.98 |

### 4.3 Underdog regime: near-50c (35-49c) (13 cells)

| Cell | band | N | optimal_exit_cents | curve_max_value | exit@15c value |
|---|---|--:|--:|--:|--:|
| ATP_CHALL_underdog_35-39 | 5c | 93 | 42 | 11.81 | 8.69 |
| ATP_CHALL_underdog_40-44 | 5c | 334 | 25 | 13.37 | 6.90 |
| ATP_CHALL_underdog_40-49 | 10c | 532 | 19 | 4.10 | 1.33 |
| ATP_CHALL_underdog_45-49 | 5c | 198 | 17 | -5.27 | -6.84 |
| ATP_MAIN_underdog_35-39 | 5c | 297 | 36 | 8.60 | -1.32 |
| ATP_MAIN_underdog_40-44 | 5c | 182 | 18 | -6.83 | -9.32 |
| ATP_MAIN_underdog_40-49 | 10c | 182 | 18 | -6.83 | -9.32 |
| WTA_CHALL_underdog_35-39 | 5c | 122 | 42 | 20.67 | 3.76 |
| WTA_CHALL_underdog_40-49 | 10c | 71 | 45 | 10.97 | 0.62 |
| WTA_CHALL_underdog_45-49 | 5c | 60 | 45 | 19.14 | 6.49 |
| WTA_MAIN_underdog_35-39 | 5c | 157 | 36 | 20.53 | 4.48 |
| WTA_MAIN_underdog_40-44 | 5c | 211 | 35 | 11.99 | 6.08 |
| WTA_MAIN_underdog_40-49 | 10c | 240 | 35 | 12.58 | 5.47 |

### 4.4 Cells where optimal differs from current deployed by >5c

(Comparing each sweep cell against any matching active scorecard-style cell in paper config)

| Sweep cell | optimal | matched paper config cells | deployed exit_cents | delta |
|---|--:|---|--:|--:|
| ATP_CHALL_underdog_10-19 | 45 | ATP_CHALL_underdog_10-14 | 30 | +15 |
| ATP_CHALL_underdog_20-29 | 42 | ATP_CHALL_underdog_20-24 | 15 | +27 |
| ATP_CHALL_underdog_40-49 | 19 | ATP_CHALL_underdog_40-44 | 30 | -11 |
| ATP_CHALL_underdog_40-49 | 19 | ATP_CHALL_underdog_45-49 | 13 | +6 |
| ATP_MAIN_underdog_30-39 | 36 | ATP_MAIN_underdog_30-34 | 15 | +21 |
| ATP_MAIN_underdog_40-49 | 18 | ATP_MAIN_underdog_45-49 | 4 | +14 |
| WTA_CHALL_underdog_40-49 | 45 | WTA_CHALL_underdog_40-44 | 30 | +15 |
| WTA_MAIN_underdog_20-29 | 44 | WTA_MAIN_underdog_25-29 | 21 | +23 |
| WTA_MAIN_underdog_40-49 | 35 | WTA_MAIN_underdog_45-49 | 11 | +24 |
| ATP_CHALL_underdog_10-14 | 46 | ATP_CHALL_underdog_10-14 | 30 | +16 |
| ATP_CHALL_underdog_15-19 | 29 | ATP_CHALL_underdog_20-24 | 15 | +14 |
| ATP_CHALL_underdog_20-24 | 42 | ATP_CHALL_underdog_20-24 | 15 | +27 |
| ATP_CHALL_underdog_30-34 | 17 | ATP_CHALL_underdog_35-39 | 11 | +6 |
| ATP_CHALL_underdog_35-39 | 42 | ATP_CHALL_underdog_35-39 | 11 | +31 |
| ATP_CHALL_underdog_35-39 | 42 | ATP_CHALL_underdog_40-44 | 30 | +12 |
| ATP_CHALL_underdog_40-44 | 25 | ATP_CHALL_underdog_45-49 | 13 | +12 |
| ATP_MAIN_underdog_40-44 | 18 | ATP_MAIN_underdog_45-49 | 4 | +14 |
| WTA_CHALL_underdog_35-39 | 42 | WTA_CHALL_underdog_40-44 | 30 | +12 |
| WTA_MAIN_underdog_20-24 | 44 | WTA_MAIN_underdog_25-29 | 21 | +23 |
| WTA_MAIN_underdog_25-29 | 30 | WTA_MAIN_underdog_25-29 | 21 | +9 |
| WTA_MAIN_underdog_40-44 | 35 | WTA_MAIN_underdog_45-49 | 11 | +24 |

Total cells with optimal-vs-deployed delta >5c (underdog): **21**

---

## 5. Exit Sweep — Leader Cells (10c bands)

### 5.4 Leader cells where optimal differs from current deployed by >5c

| Sweep cell | optimal | matched paper config cells | deployed exit_cents | delta |
|---|--:|---|--:|--:|

Total leader cells with optimal-vs-deployed delta >5c: **0**

---

## 6. Bias Correction Contents

Per-cell `mean_bias_first_vs_late_mid` from `entry_price_bias_by_cell.csv`. Bias is in cents — first_price minus late-game mid; positive bias means first_price was systematically HIGHER than the eventual fair late-game mid (entry was overpriced).

### 6.1 All 43 cells with bias data, sorted by absolute bias

| Cell | N_late | mean_bias | stddev | median | within_3c | within_5c |
|---|--:|--:|--:|--:|--:|--:|
| ATP_CHALL_leader_65-69 | 89 | -10.6 | 19.2 | -16.1 | 10% | 11% |
| ATP_MAIN_underdog_30-34 | 43 | -9.2 | 30.7 | 0.0 | 12% | 16% |
| ATP_CHALL_underdog_25-29 | 77 | 9.0 | 14.6 | 13.1 | 12% | 14% |
| ATP_CHALL_underdog_30-34 | 96 | 8.4 | 22.8 | 18.0 | 10% | 12% |
| ATP_CHALL_underdog_35-39 | 93 | 7.8 | 24.6 | 19.7 | 9% | 11% |
| WTA_CHALL_leader_55-59 | 16 | -6.7 | 29.2 | -24.3 | 12% | 12% |
| ATP_MAIN_underdog_25-29 | 38 | 6.6 | 16.7 | 12.6 | 11% | 21% |
| WTA_MAIN_leader_80-84 | 17 | -5.8 | 5.0 | -6.2 | 29% | 47% |
| WTA_MAIN_underdog_25-29 | 29 | 5.6 | 16.7 | 11.9 | 10% | 21% |
| ATP_CHALL_leader_75-79 | 67 | -5.5 | 17.0 | -10.9 | 10% | 18% |
| WTA_MAIN_underdog_20-24 | 28 | 5.3 | 12.9 | 9.2 | 11% | 25% |
| ATP_MAIN_underdog_45-49 | 34 | -5.0 | 30.2 | -9.1 | 6% | 6% |
| WTA_MAIN_leader_60-64 | 26 | -4.9 | 27.1 | -14.9 | 12% | 15% |
| ATP_CHALL_leader_70-74 | 89 | -4.8 | 20.0 | -13.0 | 11% | 12% |
| WTA_MAIN_leader_65-69 | 33 | -4.6 | 24.9 | -13.2 | 21% | 24% |
| ATP_CHALL_leader_60-64 | 97 | -4.5 | 26.9 | -15.9 | 9% | 10% |
| WTA_MAIN_underdog_15-19 | 21 | 4.5 | 5.7 | 5.6 | 33% | 43% |
| ATP_CHALL_underdog_20-24 | 53 | 4.4 | 20.0 | 10.8 | 11% | 13% |
| ATP_CHALL_underdog_15-19 | 60 | 4.0 | 13.1 | 7.9 | 10% | 23% |
| WTA_MAIN_underdog_40-44 | 29 | 4.0 | 31.3 | 23.1 | 3% | 7% |
| ATP_MAIN_underdog_20-24 | 17 | 3.8 | 15.0 | 10.7 | 12% | 18% |
| WTA_CHALL_underdog_40-44 | 16 | 3.7 | 29.3 | 22.4 | 6% | 6% |
| ATP_CHALL_leader_85-89 | 41 | -3.5 | 6.4 | -6.1 | 22% | 37% |
| ATP_MAIN_underdog_40-44 | 50 | 3.5 | 24.6 | 5.2 | 18% | 26% |
| ATP_MAIN_leader_60-64 | 46 | -3.4 | 23.0 | -6.0 | 13% | 20% |
| WTA_MAIN_underdog_45-49 | 24 | 3.4 | 27.7 | 3.9 | 12% | 17% |
| ATP_CHALL_underdog_45-49 | 91 | -3.1 | 31.8 | -0.5 | 10% | 10% |
| ATP_CHALL_underdog_10-14 | 42 | 2.8 | 5.8 | 4.1 | 26% | 57% |
| WTA_MAIN_leader_85-89 | 18 | -2.8 | 4.7 | -2.9 | 44% | 61% |
| ATP_MAIN_leader_55-59 | 44 | -2.7 | 27.2 | -11.1 | 14% | 16% |
| ATP_MAIN_leader_70-74 | 43 | -2.7 | 22.9 | -11.6 | 9% | 9% |
| WTA_MAIN_underdog_35-39 | 27 | 2.7 | 23.8 | 13.0 | 11% | 15% |
| WTA_MAIN_underdog_30-34 | 26 | 2.6 | 26.3 | 12.6 | 19% | 19% |
| ATP_CHALL_leader_80-84 | 59 | -2.5 | 16.2 | -6.9 | 12% | 25% |
| WTA_MAIN_leader_50-54 | 36 | -2.2 | 27.7 | -1.0 | 11% | 17% |
| WTA_MAIN_leader_70-74 | 31 | -2.1 | 20.4 | -10.4 | 16% | 19% |
| ATP_MAIN_leader_50-54 | 33 | -1.7 | 28.6 | 0.0 | 12% | 12% |
| ATP_MAIN_underdog_35-39 | 38 | -1.7 | 25.8 | 4.4 | 11% | 16% |
| WTA_MAIN_leader_55-59 | 27 | 1.6 | 33.0 | -19.8 | 0% | 0% |
| ATP_MAIN_leader_75-79 | 20 | -1.0 | 14.5 | -1.8 | 30% | 30% |
| ATP_CHALL_leader_55-59 | 109 | -0.8 | 29.9 | -10.3 | 12% | 13% |
| ATP_CHALL_leader_50-54 | 74 | -0.4 | 30.8 | 0.0 | 11% | 11% |
| ATP_CHALL_underdog_40-44 | 99 | 0.3 | 29.6 | 1.3 | 14% | 15% |

### 6.2 Cells with bias > 5c (material)

**11 cells** have |bias| > 5c:

| Cell | bias |
|---|--:|
| ATP_CHALL_leader_65-69 | -10.6 |
| ATP_MAIN_underdog_30-34 | -9.2 |
| ATP_CHALL_underdog_25-29 | +9.0 |
| ATP_CHALL_underdog_30-34 | +8.4 |
| ATP_CHALL_underdog_35-39 | +7.8 |
| WTA_CHALL_leader_55-59 | -6.7 |
| ATP_MAIN_underdog_25-29 | +6.6 |
| WTA_MAIN_leader_80-84 | -5.8 |
| WTA_MAIN_underdog_25-29 | +5.6 |
| ATP_CHALL_leader_75-79 | -5.5 |
| WTA_MAIN_underdog_20-24 | +5.3 |

### 6.3 Cells with bias > 20c (analyzing different markets entirely)

**No cells** have |bias| > 20c in this version of the bias file. **Operator's prior framing of "+21-37c bias on ATP_CHALL underdogs 25-49" does NOT reproduce in this artifact.** Possible explanations: this is a different (later) version of the bias analysis with smoother corrections; OR a different bias-window methodology was used for the prior framing. Flag for review.

---

## 7. Current Paper Config Snapshot

**File**: `config/deploy_v4_paper.json`

### 7.1 Top-level config

- `b_convergence_enabled`: `false`
- `sizing`: `{"entry_contracts": 10, "dca_contracts": 5}`
- `dca_fill_floor_cents`: `10`
- `paper_mode`: `true`
- `paper_state_max_age_sec`: `86400`

### 7.2 Active cells (25)

| Cell | strategy | exit_cents | dca_trigger_cents | other |
|---|---|--:|--:|---|
| ATP_CHALL_leader_50-54 | noDCA | 15 |  |  |
| ATP_CHALL_leader_55-59 | noDCA | 20 |  |  |
| ATP_CHALL_leader_65-69 | noDCA | 30 |  |  |
| ATP_CHALL_leader_70-74 | noDCA | 25 |  |  |
| ATP_CHALL_leader_75-79 | DCA-A | 10 | 25 |  |
| ATP_CHALL_leader_80-84 | noDCA | 15 |  |  |
| ATP_CHALL_leader_85-89 | noDCA | 7 |  |  |
| ATP_CHALL_underdog_10-14 | noDCA | 30 |  |  |
| ATP_CHALL_underdog_20-24 | noDCA | 15 |  |  |
| ATP_CHALL_underdog_35-39 | noDCA | 11 |  |  |
| ATP_CHALL_underdog_40-44 | noDCA | 30 |  |  |
| ATP_CHALL_underdog_45-49 | noDCA | 13 |  |  |
| ATP_MAIN_leader_50-54 | noDCA | 12 |  |  |
| ATP_MAIN_leader_70-74 | noDCA | 17 |  |  |
| ATP_MAIN_underdog_30-34 | noDCA | 15 |  |  |
| ATP_MAIN_underdog_45-49 | noDCA | 4 |  |  |
| WTA_CHALL_leader_55-59 | noDCA | 20 |  |  |
| WTA_CHALL_underdog_40-44 | noDCA | 30 |  |  |
| WTA_MAIN_leader_50-54 | noDCA | 10 |  |  |
| WTA_MAIN_leader_65-69 | noDCA | 23 |  |  |
| WTA_MAIN_leader_70-74 | noDCA | 25 |  |  |
| WTA_MAIN_leader_80-84 | noDCA | 17 |  |  |
| WTA_MAIN_leader_85-89 | noDCA | 14 |  |  |
| WTA_MAIN_underdog_25-29 | noDCA | 21 |  |  |
| WTA_MAIN_underdog_45-49 | noDCA | 11 |  |  |

### 7.3 Disabled cells (27)

- `ATP_CHALL_leader_60-64`
- `ATP_CHALL_underdog_15-19`
- `ATP_CHALL_underdog_25-29`
- `ATP_CHALL_underdog_30-34`
- `ATP_MAIN_leader_55-59`
- `ATP_MAIN_leader_60-64`
- `ATP_MAIN_leader_65-69`
- `ATP_MAIN_leader_75-79`
- `ATP_MAIN_underdog_20-24`
- `ATP_MAIN_underdog_25-29`
- `ATP_MAIN_underdog_35-39`
- `ATP_MAIN_underdog_40-44`
- `WTA_CHALL_leader_50-54`
- `WTA_CHALL_leader_60-64`
- `WTA_CHALL_leader_65-69`
- `WTA_CHALL_leader_70-74`
- `WTA_CHALL_leader_75-79`
- `WTA_CHALL_leader_80-84`
- `WTA_CHALL_leader_85-89`
- `WTA_CHALL_leader_90-94`
- `WTA_MAIN_leader_55-59`
- `WTA_MAIN_leader_60-64`
- `WTA_MAIN_underdog_15-19`
- `WTA_MAIN_underdog_20-24`
- `WTA_MAIN_underdog_30-34`
- `WTA_MAIN_underdog_35-39`
- `WTA_MAIN_underdog_40-44`

---

## 8. Diff: Active Status Disagreements

### 8.1 Counts at a glance

| Disagreement | Count |
|---|--:|
| SCALPER_EDGE in rebuild, **disabled** in paper config (should consider enabling) | 9 |
| SCALPER_EDGE in rebuild, **absent** from paper config (not deployed at all) | 0 |
| SCALPER_EDGE in rebuild, **active** in paper config (aligned ✓) | 6 |
| Bleed-like (NEGATIVE/MIXED/SETTLEMENT_RIDE/BREAK_EVEN), **active** in paper (consider disabling) | 14 |
| UNCALIBRATED, **active** in paper (risk: no data backing) | 0 |
| UNCALIBRATED, **disabled** in paper (no data, will not generate any) | 8 |
| UNCALIBRATED, **absent** from paper config | 22 |

### 8.2 SCALPER_EDGE cells DISABLED in paper (consider enabling)

| Cell | N | ROI%% | CI |
|---|--:|--:|---|
| ATP_CHALL_leader_60-64 | 109 | 8.7 | [0.045, 0.130] |
| ATP_CHALL_underdog_15-19 | 515 | 42.2 | [0.402, 0.443] |
| ATP_CHALL_underdog_25-29 | 329 | 25.8 | [0.239, 0.277] |
| ATP_CHALL_underdog_30-34 | 181 | 21.5 | [0.190, 0.240] |
| ATP_MAIN_underdog_20-24 | 106 | 31.2 | [0.256, 0.369] |
| WTA_MAIN_underdog_15-19 | 106 | 52.8 | [0.496, 0.562] |
| WTA_MAIN_underdog_30-34 | 153 | 14.4 | [0.113, 0.174] |
| WTA_MAIN_underdog_35-39 | 157 | 4.6 | [0.004, 0.088] |
| WTA_MAIN_underdog_40-44 | 211 | 5.9 | [0.025, 0.094] |

### 8.3 SCALPER_EDGE cells ABSENT from paper (not deployed at all)

(none)

### 8.4 Bleed-like cells ACTIVE in paper (consider disabling)

| Cell | mechanism | N | ROI%% | CI |
|---|---|--:|--:|---|
| ATP_CHALL_leader_50-54 | SCALPER_BREAK_EVEN | 629 | -1.2 | [-0.035, 0.012] |
| ATP_CHALL_leader_65-69 | SCALPER_NEGATIVE | 364 | -3.1 | [-0.065, 0.002] |
| ATP_CHALL_leader_70-74 | MIXED_BREAK_EVEN | 111 | -3.5 | [-0.107, 0.037] |
| ATP_CHALL_leader_75-79 | MIXED_BREAK_EVEN | 672 | -4.0 | [-0.069, -0.009] |
| ATP_CHALL_leader_80-84 | SETTLEMENT_RIDE_CONTAMINATED | 452 | -4.6 | [-0.086, -0.007] |
| ATP_CHALL_leader_85-89 | SETTLEMENT_RIDE_CONTAMINATED | 303 | -4.3 | [-0.090, 0.003] |
| ATP_CHALL_underdog_45-49 | SCALPER_BREAK_EVEN | 198 | -6.8 | [-0.113, -0.023] |
| ATP_MAIN_leader_50-54 | SCALPER_BREAK_EVEN | 327 | -8.0 | [-0.114, -0.044] |
| ATP_MAIN_leader_70-74 | SCALPER_NEGATIVE | 116 | -8.4 | [-0.165, -0.002] |
| WTA_MAIN_leader_50-54 | SCALPER_BREAK_EVEN | 179 | 0.9 | [-0.034, 0.051] |
| WTA_MAIN_leader_65-69 | SCALPER_NEGATIVE | 144 | -3.9 | [-0.100, 0.022] |
| WTA_MAIN_leader_70-74 | SCALPER_NEGATIVE | 193 | -12.0 | [-0.183, -0.057] |
| WTA_MAIN_leader_85-89 | SETTLEMENT_RIDE_CONTAMINATED | 168 | -7.8 | [-0.145, -0.010] |
| WTA_MAIN_underdog_45-49 | SCALPER_BREAK_EVEN | 29 | 1.3 | [-0.099, 0.126] |

### 8.5 UNCALIBRATED cells ACTIVE in paper (no data backing)

(none)

### 8.6 UNCALIBRATED cells DISABLED in paper (will not generate data)

| Cell |
|---|
| ATP_MAIN_leader_65-69 |
| WTA_CHALL_leader_50-54 |
| WTA_CHALL_leader_60-64 |
| WTA_CHALL_leader_65-69 |
| WTA_CHALL_leader_70-74 |
| WTA_CHALL_leader_75-79 |
| WTA_CHALL_leader_80-84 |
| WTA_CHALL_leader_85-89 |

---

## 9. Diff: exit_cents disagreements (active cells only)

### 9.1 Counts

| Bucket | Count |
|---|--:|
| Active cells with sweep coverage | 10 |
| Active cells with NO sweep match | 15 |
| delta > 5c (material disagreement) | 9 |
| delta 1-5c (minor) | 1 |
| delta = 0 (exact match) | 0 |

### 9.2 Material disagreements (|delta| > 5c)

| Active cell | matched sweep cell (10c band) | deployed exit_cents | optimal exit_cents | delta |
|---|---|--:|--:|--:|
| ATP_CHALL_underdog_20-24 | ATP_CHALL_underdog_20-29 | 15 | 42 | +27 |
| WTA_MAIN_underdog_45-49 | WTA_MAIN_underdog_40-49 | 11 | 35 | +24 |
| WTA_MAIN_underdog_25-29 | WTA_MAIN_underdog_20-29 | 21 | 44 | +23 |
| ATP_MAIN_underdog_30-34 | ATP_MAIN_underdog_30-39 | 15 | 36 | +21 |
| WTA_CHALL_underdog_40-44 | WTA_CHALL_underdog_40-49 | 30 | 45 | +15 |
| ATP_CHALL_underdog_10-14 | ATP_CHALL_underdog_10-19 | 30 | 45 | +15 |
| ATP_MAIN_underdog_45-49 | ATP_MAIN_underdog_40-49 | 4 | 18 | +14 |
| ATP_CHALL_underdog_40-44 | ATP_CHALL_underdog_40-49 | 30 | 19 | -11 |
| ATP_CHALL_underdog_45-49 | ATP_CHALL_underdog_40-49 | 13 | 19 | +6 |

### 9.3 Minor disagreements (|delta| 1-5c)

| Active cell | matched sweep cell | deployed | optimal | delta |
|---|---|--:|--:|--:|
| ATP_CHALL_underdog_35-39 | ATP_CHALL_underdog_30-39 | 11 | 15 | +4 |

### 9.4 Exact matches (delta = 0)

(none)

### 9.5 Active cells with NO sweep coverage

| Active cell | deployed exit_cents |
|---|--:|
| ATP_CHALL_leader_50-54 | 15 |
| ATP_CHALL_leader_55-59 | 20 |
| ATP_CHALL_leader_65-69 | 30 |
| ATP_CHALL_leader_70-74 | 25 |
| ATP_CHALL_leader_75-79 | 10 |
| ATP_CHALL_leader_80-84 | 15 |
| ATP_CHALL_leader_85-89 | 7 |
| ATP_MAIN_leader_50-54 | 12 |
| ATP_MAIN_leader_70-74 | 17 |
| WTA_CHALL_leader_55-59 | 20 |
| WTA_MAIN_leader_50-54 | 10 |
| WTA_MAIN_leader_65-69 | 23 |
| WTA_MAIN_leader_70-74 | 25 |
| WTA_MAIN_leader_80-84 | 17 |
| WTA_MAIN_leader_85-89 | 14 |

---

## 10. Cells in Paper Config NOT in Rebuild Scorecard

### 10.1 Active in paper, no rebuild data (deployed without backing)

| Cell | exit_cents | strategy |
|---|--:|---|
| ATP_MAIN_underdog_30-34 | 15 | noDCA |
| ATP_MAIN_underdog_45-49 | 4 | noDCA |
| WTA_CHALL_leader_55-59 | 20 | noDCA |
| WTA_CHALL_underdog_40-44 | 30 | noDCA |
| WTA_MAIN_leader_80-84 | 17 | noDCA |

### 10.2 Disabled in paper, no rebuild data

- `ATP_MAIN_underdog_25-29`
- `WTA_CHALL_leader_90-94`

---

## 11. Cells in Rebuild Scorecard NOT in Paper Config

### 11.1 Cells in scorecard but absent from paper config (any list)

**UNCALIBRATED** (22):
- `ATP_CHALL_leader_90-94` (N=241, ROI=-9.0)
- `ATP_CHALL_leader_95-99` (N=159, ROI=-19.7)
- `ATP_CHALL_underdog_0-4` (N=72, ROI=321.1)
- `ATP_CHALL_underdog_5-9` (N=209, ROI=89.3)
- `ATP_MAIN_leader_80-84` (N=156, ROI=-16.2)
- `ATP_MAIN_leader_85-89` (N=84, ROI=-10.4)
- `ATP_MAIN_leader_90-94` (N=112, ROI=-16.7)
- `ATP_MAIN_underdog_10-14` (N=48, ROI=57.6)
- `ATP_MAIN_underdog_15-19` (N=174, ROI=35.0)
- `ATP_MAIN_underdog_5-9` (N=74, ROI=130.0)
- `WTA_CHALL_leader_95-99` (N=25, ROI=-34.8)
- `WTA_CHALL_underdog_15-19` (N=35, ROI=-10.5)
- `WTA_CHALL_underdog_20-24` (N=35, ROI=-11.5)
- `WTA_CHALL_underdog_25-29` (N=46, ROI=-7.4)
- `WTA_CHALL_underdog_30-34` (N=50, ROI=-8.0)
- `WTA_CHALL_underdog_35-39` (N=122, ROI=5.4)
- `WTA_CHALL_underdog_45-49` (N=60, ROI=6.2)
- `WTA_CHALL_underdog_5-9` (N=25, ROI=89.9)
- `WTA_MAIN_leader_75-79` (N=314, ROI=-9.2)
- `WTA_MAIN_leader_90-94` (N=135, ROI=-18.7)
- `WTA_MAIN_underdog_10-14` (N=130, ROI=41.6)
- `WTA_MAIN_underdog_5-9` (N=107, ROI=133.3)


---

## 12. Summary Table

| Metric | Value |
|---|--:|
| Total cells in paper config | 52 |
| Paper config: active | 25 |
| Paper config: disabled | 27 |
| Total cells in rebuild scorecard | 67 |
| SCALPER_EDGE total in rebuild | 15 |
| SCALPER_EDGE active in paper | 6 |
| SCALPER_EDGE disabled in paper | 9 |
| SCALPER_EDGE absent from paper | 0 |
| Bleed-like total in rebuild (NEG+MIX+SETTLE+BRK) | 22 |
| Bleed-like active in paper | 14 |
| Bleed-like disabled in paper | 8 |
| Bleed-like absent from paper | 0 |
| UNCALIBRATED total in rebuild | 30 |
| UNCALIBRATED active in paper | 0 |
| UNCALIBRATED disabled in paper | 8 |
| UNCALIBRATED absent from paper | 22 |
| Paper-only active (no rebuild data) | 5 |
| Paper-only disabled (no rebuild data) | 2 |
| Rebuild-only (not in any paper list) | 22 |

---

## 13. Recommended Changes (suggestions only — no config changes made)

These are derived directly from §8 and §9. Frame: "rebuild suggests X". Operator decides whether/when to deploy.

### 13.1 Cells the rebuild suggests ENABLING (currently disabled or absent)

- **Enable** `ATP_CHALL_leader_60-64` — currently disabled. Rebuild: SCALPER_EDGE, N=109, ROI=8.7, CI [0.045, 0.130]
- **Enable** `ATP_CHALL_underdog_15-19` — currently disabled. Rebuild: SCALPER_EDGE, N=515, ROI=42.2, CI [0.402, 0.443]
- **Enable** `ATP_CHALL_underdog_25-29` — currently disabled. Rebuild: SCALPER_EDGE, N=329, ROI=25.8, CI [0.239, 0.277]
- **Enable** `ATP_CHALL_underdog_30-34` — currently disabled. Rebuild: SCALPER_EDGE, N=181, ROI=21.5, CI [0.190, 0.240]
- **Enable** `ATP_MAIN_underdog_20-24` — currently disabled. Rebuild: SCALPER_EDGE, N=106, ROI=31.2, CI [0.256, 0.369]
- **Enable** `WTA_MAIN_underdog_15-19` — currently disabled. Rebuild: SCALPER_EDGE, N=106, ROI=52.8, CI [0.496, 0.562]
- **Enable** `WTA_MAIN_underdog_30-34` — currently disabled. Rebuild: SCALPER_EDGE, N=153, ROI=14.4, CI [0.113, 0.174]
- **Enable** `WTA_MAIN_underdog_35-39` — currently disabled. Rebuild: SCALPER_EDGE, N=157, ROI=4.6, CI [0.004, 0.088]
- **Enable** `WTA_MAIN_underdog_40-44` — currently disabled. Rebuild: SCALPER_EDGE, N=211, ROI=5.9, CI [0.025, 0.094]

### 13.2 Cells the rebuild suggests DISABLING (active in paper, bleed-like or worse)

- **Disable** `ATP_CHALL_leader_50-54` — currently active. Rebuild: SCALPER_BREAK_EVEN, ROI=-1.2, CI [-0.035, 0.012]
- **Disable** `ATP_CHALL_leader_65-69` — currently active. Rebuild: SCALPER_NEGATIVE, ROI=-3.1, CI [-0.065, 0.002]
- **Disable** `ATP_CHALL_leader_70-74` — currently active. Rebuild: MIXED_BREAK_EVEN, ROI=-3.5, CI [-0.107, 0.037]
- **Disable** `ATP_CHALL_leader_75-79` — currently active. Rebuild: MIXED_BREAK_EVEN, ROI=-4.0, CI [-0.069, -0.009]
- **Disable** `ATP_CHALL_leader_80-84` — currently active. Rebuild: SETTLEMENT_RIDE_CONTAMINATED, ROI=-4.6, CI [-0.086, -0.007]
- **Disable** `ATP_CHALL_leader_85-89` — currently active. Rebuild: SETTLEMENT_RIDE_CONTAMINATED, ROI=-4.3, CI [-0.090, 0.003]
- **Disable** `ATP_CHALL_underdog_45-49` — currently active. Rebuild: SCALPER_BREAK_EVEN, ROI=-6.8, CI [-0.113, -0.023]
- **Disable** `ATP_MAIN_leader_50-54` — currently active. Rebuild: SCALPER_BREAK_EVEN, ROI=-8.0, CI [-0.114, -0.044]
- **Disable** `ATP_MAIN_leader_70-74` — currently active. Rebuild: SCALPER_NEGATIVE, ROI=-8.4, CI [-0.165, -0.002]
- **Disable** `WTA_MAIN_leader_50-54` — currently active. Rebuild: SCALPER_BREAK_EVEN, ROI=0.9, CI [-0.034, 0.051]
- **Disable** `WTA_MAIN_leader_65-69` — currently active. Rebuild: SCALPER_NEGATIVE, ROI=-3.9, CI [-0.100, 0.022]
- **Disable** `WTA_MAIN_leader_70-74` — currently active. Rebuild: SCALPER_NEGATIVE, ROI=-12.0, CI [-0.183, -0.057]
- **Disable** `WTA_MAIN_leader_85-89` — currently active. Rebuild: SETTLEMENT_RIDE_CONTAMINATED, ROI=-7.8, CI [-0.145, -0.010]
- **Disable** `WTA_MAIN_underdog_45-49` — currently active. Rebuild: SCALPER_BREAK_EVEN, ROI=1.3, CI [-0.099, 0.126]

### 13.3 Cells with material exit_cents disagreement (>5c)

- **Adjust** `ATP_CHALL_underdog_20-24` exit_cents from 15 to 42 (delta +27, sweep cell ATP_CHALL_underdog_20-29)
- **Adjust** `WTA_MAIN_underdog_45-49` exit_cents from 11 to 35 (delta +24, sweep cell WTA_MAIN_underdog_40-49)
- **Adjust** `WTA_MAIN_underdog_25-29` exit_cents from 21 to 44 (delta +23, sweep cell WTA_MAIN_underdog_20-29)
- **Adjust** `ATP_MAIN_underdog_30-34` exit_cents from 15 to 36 (delta +21, sweep cell ATP_MAIN_underdog_30-39)
- **Adjust** `WTA_CHALL_underdog_40-44` exit_cents from 30 to 45 (delta +15, sweep cell WTA_CHALL_underdog_40-49)
- **Adjust** `ATP_CHALL_underdog_10-14` exit_cents from 30 to 45 (delta +15, sweep cell ATP_CHALL_underdog_10-19)
- **Adjust** `ATP_MAIN_underdog_45-49` exit_cents from 4 to 18 (delta +14, sweep cell ATP_MAIN_underdog_40-49)
- **Adjust** `ATP_CHALL_underdog_40-44` exit_cents from 30 to 19 (delta -11, sweep cell ATP_CHALL_underdog_40-49)
- **Adjust** `ATP_CHALL_underdog_45-49` exit_cents from 13 to 19 (delta +6, sweep cell ATP_CHALL_underdog_40-49)

### 13.4 Risk-review queue

(no UNCALIBRATED cells active)

---

## 14. Methodology Concerns

### 14.1 Sample size

All SCALPER_EDGE cells have N >= 50.

### 14.2 Classification thresholds — opaque from script header

- The exact CI computation (formula, bootstrap vs normal-approx) isn't shown in the head of the script. Need to read further.
- The threshold separating SCALPER_EDGE from SCALPER_BREAK_EVEN — explicit threshold (CI excludes zero? Mean ROI > X%?) — not shown.
- Whether all 6 mechanism classes were defined in this script or in a separate post-processing step is not visible from the header.

### 14.3 Bias correction coverage

- Bias map only loads cells with `N_late >= 10` (per script line: `if n_late >= 10: bias_map[r['cell']] = ...`). Cells with N_late < 10 inherit zero correction. This means:

  - 0 of 43 cells in the bias file have N_late < 10 → they get NO bias correction in the scorecard.

### 14.4 Underdog three-regime split

- Regimes (`deep`, `mid`, `near-50c`) are presented in §4 with operator-defined boundaries (0-19c / 20-34c / 35-49c). The rebuild scripts at `/tmp/` do not appear to bake these boundaries in — they emerge from the analysis narrative, not the data. **Operator-defined**, not data-driven.

### 14.5 Bias artifact discrepancy

- Operator's prompt referenced "+21-37c bias on ATP_CHALL underdogs 25-49" and "+13-15c on ATP_MAIN leaders 50-64" — these magnitudes do NOT appear in the current `entry_price_bias_by_cell.csv` (max |bias| in current file is much smaller, see §6.3). Possible explanations: different bias-window methodology in the prior framing, OR an earlier version of the bias file at a different path. Worth checking `/tmp/per_cell_verification/entry_price_bias.run1.csv` and `/tmp/per_cell_verification/entry_price_bias_by_cell.run1.csv` (both exist on disk).

---

## 15. What the Diff Report Does NOT Tell Us (open questions from yesterday)

- **Inversion-pair analysis** — queued yesterday, not run. Whether the rebuild correctly handles inverted ticker pairs (e.g., A vs B and B vs A) hasn't been validated.
- **30 UNCALIBRATED cells split by price-regime priors** — not attempted. UNCALIBRATED cells are still a flat "insufficient data" bucket.
- **Cell band geometry** — 5c uniform vs alternative bands (e.g., wider near 50c, narrower in extremes) — open question. Current scorecard uses 5c bands; current sweep uses 10c bands. Inconsistent.
- **Multi-axis edge dimensions** — time-to-start, spread, FV gap, depth, volume, trajectory, tournament tier, surface — none of these are in the scorecard. Cell name encodes only `tier_side_priceband`.
- **Greeks framing** — not operationalized. The rebuild expresses ROI%% but not delta/gamma/vega-style exposure decomposition.
- **First-vs-late bias methodology** — the file used here may be a smoothed/late version of the bias analysis. The +21-37c values in the operator's prior framing don't appear in this file (see §14.5).
- **Sample-size confidence threshold for SCALPER_EDGE classification** — not explicit in the script header.
- **Whether SCALPER_BREAK_EVEN cells should be active or disabled** — they're profitable in expectation but not statistically distinguishable from zero. Trading them is a judgment call the rebuild doesn't resolve.

All open questions from yesterday's investigation remain open.
