#!/usr/bin/env python3
"""
Rebuild artifacts vs current paper config — comprehensive diff report.
Output: /tmp/rebuild_vs_paper_diff.md

Reads:
  /tmp/rebuilt_scorecard.csv
  /tmp/exit_sweep_curves.csv
  /tmp/per_cell_verification/entry_price_bias_by_cell.csv
  /tmp/rebuilt_scorecard_script.py
  /root/Omi-Workspace/arb-executor/config/deploy_v4_paper.json
"""

import csv, json, os, sys, hashlib, datetime, time
from collections import defaultdict

OUT_PATH = "/tmp/rebuild_vs_paper_diff.md"

SCORECARD = "/tmp/rebuilt_scorecard.csv"
SWEEP = "/tmp/exit_sweep_curves.csv"
BIAS = "/tmp/per_cell_verification/entry_price_bias_by_cell.csv"
METHOD_SCRIPT = "/tmp/rebuilt_scorecard_script.py"
PAPER_CFG = "/root/Omi-Workspace/arb-executor/config/deploy_v4_paper.json"

LINES = []
def w(s=""):
    LINES.append(s)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def fmt_ts(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

# === Load all data ===
def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))

scorecard = read_csv(SCORECARD)
sweep = read_csv(SWEEP)
bias = read_csv(BIAS)
with open(PAPER_CFG) as f:
    paper_cfg = json.load(f)
with open(METHOD_SCRIPT) as f:
    method_src = f.read()

# Index helpers
score_by_cell = {r["cell"]: r for r in scorecard}
sweep_by_cell = {r["cell"]: r for r in sweep}
bias_by_cell = {r["cell"]: r for r in bias}

active_cells = paper_cfg.get("active_cells", {})
disabled_cells = paper_cfg.get("disabled_cells", [])
active_cells_set = set(active_cells.keys())
disabled_cells_set = set(disabled_cells)

# Mechanism distribution
mech_counts = defaultdict(int)
for r in scorecard:
    mech_counts[r["mechanism"]] += 1

# Compute optimal exit_cents per sweep row
def optimal_exit(row):
    """Return (optimal_exit_cents, max_value)."""
    best_n, best_v = 1, -1e9
    for n in range(1, 50):
        col = "exit_%d" % n
        if col in row and row[col] != "":
            try:
                v = float(row[col])
                if v > best_v:
                    best_v = v
                    best_n = n
            except ValueError:
                continue
    return best_n, best_v

sweep_optimal = {r["cell"]: optimal_exit(r) for r in sweep}

# Map sweep cell (10c band) <-> scorecard cell (5c band)
# sweep cells like "ATP_CHALL_underdog_0-9" cover scorecard cells "0-4" and "5-9"
def sweep_cell_for_scorecard(scorecard_cell):
    """Given a 5c-band scorecard cell, return the 10c-band sweep cell name."""
    parts = scorecard_cell.rsplit("_", 1)
    if len(parts) != 2:
        return None
    base, band = parts
    try:
        lo, hi = band.split("-")
        lo, hi = int(lo), int(hi)
    except:
        return None
    sweep_lo = (lo // 10) * 10
    sweep_hi = sweep_lo + 9
    return "%s_%d-%d" % (base, sweep_lo, sweep_hi)

# === Section 1: Artifact Integrity ===
w("# Rebuild vs Paper Config — Diff Report")
w()
w("**Generated**: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ET"))
w("**Paper config**: `config/deploy_v4_paper.json`")
w()
w("---")
w()
w("## 1. Artifact Integrity")
w()

w("| Artifact | Path | mtime | sha256 | rows (incl header) | data rows |")
w("|---|---|---|---|---|---|")
for path, label in [(SCORECARD, "scorecard"), (SWEEP, "exit_sweep"), (BIAS, "bias_corrections")]:
    st = os.stat(path)
    sha = sha256_file(path)[:16] + "…"
    with open(path) as f:
        n_lines = sum(1 for _ in f)
    w("| %s | `%s` | %s | `%s` | %d | %d |" % (label, path, fmt_ts(st.st_mtime), sha, n_lines, n_lines - 1))

w()
w("### 1.1 Schemas")
w()
w("**rebuilt_scorecard.csv columns** (%d):" % len(scorecard[0].keys()))
w("```")
w(", ".join(scorecard[0].keys()))
w("```")
w()
w("**exit_sweep_curves.csv columns** (%d):" % len(sweep[0].keys()))
w("```")
w(", ".join(list(sweep[0].keys())[:5]) + ", ... exit_1 through exit_49 (49 columns)")
w("```")
w()
w("**entry_price_bias_by_cell.csv columns** (%d):" % len(bias[0].keys()))
w("```")
w(", ".join(bias[0].keys()))
w("```")
w()

w("### 1.2 Sample rows")
w()
w("**scorecard first row**: `" + ", ".join("%s=%s" % (k, scorecard[0][k]) for k in list(scorecard[0].keys())[:8]) + "...`")
w()
w("**sweep first row**: `cell=%s, band_width=%s, N=%s, exit_1=%s, ..., exit_49=%s`" %
  (sweep[0]["cell"], sweep[0]["band_width"], sweep[0]["N"], sweep[0]["exit_1"], sweep[0]["exit_49"]))
w()
w("**bias first row**: `" + ", ".join("%s=%s" % (k, bias[0][k]) for k in bias[0].keys()) + "`")
w()

w("### 1.3 ⚠ Discrepancy: counts vs operator's mental model")
w()
w("Operator's prompt described the scorecard as: **11 SCALPER_EDGE + 4 bleed + 30 UNCALIBRATED = 45 cells**.")
w()
w("Actual file at the path provided contains **%d data rows** with **%d distinct mechanism classes**:" %
  (len(scorecard), len(mech_counts)))
w()
w("| Mechanism | Count | Operator's framing |")
w("|---|---|---|")
for mech, n in sorted(mech_counts.items(), key=lambda x: -x[1]):
    framing = ""
    if mech == "SCALPER_EDGE":
        framing = "operator said 11; actual %d" % n
    elif mech == "UNCALIBRATED":
        framing = "operator said 30; actual %d ✓" % n
    elif mech in ("SCALPER_NEGATIVE", "MIXED_BREAK_EVEN", "SETTLEMENT_RIDE_CONTAMINATED", "SCALPER_BREAK_EVEN"):
        framing = "candidate for 'bleed' bucket — not specified individually in prompt"
    w("| %s | %d | %s |" % (mech, n, framing))
w()
w("**STOP-trigger evaluation**: operator specified \"if fewer than 45 cells, STOP.\" Actual = 67 cells. Trigger does not fire (67 > 45). Proceeding with file's actual classifications. The operator's 11/4/30 framing may be from an earlier version of the analysis or a sub-bucketing of the 6-class output. **The diff sections below use the actual 6-class scheme**; if operator wants to remap to 11/4/30, they can advise.")
w()
w("---")
w()

# === Section 2: Methodology ===
w("## 2. Rebuild Methodology Recap")
w()
w("**Source script**: `/tmp/rebuilt_scorecard_script.py`")
w()

# Extract docstring/header (top ~20 lines and key sections)
method_lines = method_src.split("\n")
w("### 2.1 Script header (first 30 lines, verbatim)")
w("```python")
for ln in method_lines[:30]:
    w(ln)
w("```")
w()

# Identify methodology details from the script
w("### 2.2 Methodology details extracted from the script")
w()
w("- **Data source**: `tennis.db.historical_events` (rows with `total_trades >= 10`, `first_price_winner` and `first_price_loser` both ∈ (0, 100))")
w("- **Time window**: `first_ts > '2026-01-01' AND first_ts < '2026-04-30'` (Jan-Apr 2026)")
w("- **Exit target (fixed for scorecard)**: 15c above entry (`EXIT_C = 15`)")
w("- **Quantity**: 10 contracts per trade (`QTY = 10`)")
w("- **Cell band**: 5c (`bs = int(price // 5) * 5` → cell = `tier_side_lo-hi` where hi = lo+4)")
w("- **Bias correction**: from `entry_price_bias_by_cell.csv`, only cells with `N_late >= 10` (so smaller cells inherit no correction)")
w("- **Min sample size for inclusion**: `n_total < 20` filtered out (sum of winner_N + loser_N)")
w()
w("### 2.3 Mechanism classifications (extracted by grep over the script)")
w("```")
classification_lines = []
for ln in method_lines:
    if "SCALPER_EDGE" in ln or "SCALPER_NEGATIVE" in ln or "BREAK_EVEN" in ln or "UNCALIBRATED" in ln or "SETTLEMENT_RIDE" in ln:
        if "import" not in ln and "csv" not in ln.lower()[:20]:
            classification_lines.append(ln)
for ln in classification_lines[:25]:
    w(ln)
w("```")
w()

w("### 2.4 What is NOT reconstructable from the script alone")
w()
w("- The exact CI computation method (looks like normal-approximation but the formula isn't explicit in the head)")
w("- Whether the underdog three-regime split (deep/mid/near-50c) was data-driven or operator-defined — not present in this script")
w("- Whether other scripts contributed to the scorecard (e.g., a separate post-processing step)")
w("- The precise threshold separating SCALPER_EDGE from SCALPER_BREAK_EVEN (CI excludes zero? Mean ROI > X%? Need to read the full classify() block, which is lower in the file)")
w()
w("---")
w()

# === Section 3: Scorecard Contents — Full ===
w("## 3. Scorecard Contents — Full")
w()
w("**Total cells**: %d (operator framing: 45; actual: %d)" % (len(scorecard), len(scorecard)))
w()

# Group by mechanism
by_mech = defaultdict(list)
for r in scorecard:
    by_mech[r["mechanism"]].append(r)

# Show all mechanisms in priority order
mech_order = ["SCALPER_EDGE", "SCALPER_BREAK_EVEN", "SCALPER_NEGATIVE",
              "MIXED_BREAK_EVEN", "SETTLEMENT_RIDE_CONTAMINATED", "UNCALIBRATED"]

for mech in mech_order:
    rows = by_mech.get(mech, [])
    if not rows:
        continue
    w("### 3.%d %s (%d cells)" % (mech_order.index(mech)+1, mech, len(rows)))
    w()
    w("| Cell | N | N_w | N_l | avg_entry | bias_corr | TWP | Sw | Sl | ROI%% | CI_low | CI_high | uncalibrated |")
    w("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:-:|")
    for r in sorted(rows, key=lambda x: x["cell"]):
        try:
            roi_pct = float(r["decomposed_ROI"])
            ci_lo = float(r["ci_low"])
            ci_hi = float(r["ci_high"])
            roi_str = "%.1f" % roi_pct
            ci_lo_str = "%.2f" % ci_lo
            ci_hi_str = "%.2f" % ci_hi
        except:
            roi_str = r["decomposed_ROI"]
            ci_lo_str = r["ci_low"]
            ci_hi_str = r["ci_high"]
        w("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["cell"], r["N"], r["N_winner"], r["N_loser"],
            r["avg_entry"], r["bias_correction"],
            r["TWP"], r["Sw"], r["Sl"],
            roi_str, ci_lo_str, ci_hi_str,
            r["uncalibrated"]))
    w()

w("---")
w()

# === Section 4: Exit Sweep — Underdog Regimes ===
w("## 4. Exit Sweep — Underdog Cells (10c bands)")
w()
w("**Methodology note**: optimal_exit_cents = argmax of exit_1..exit_49 columns. Curve values appear to be expected per-contract payout in cents. Higher exit_N often indicates more profit captured; argmax may saturate near the upper end depending on cell base rate.")
w()

# Filter sweep cells: underdogs
underdog_sweeps = [r for r in sweep if "underdog" in r["cell"]]
leader_sweeps = [r for r in sweep if "leader" in r["cell"]]

# Group underdogs by regime
def regime_for_cell(cell):
    parts = cell.rsplit("_", 1)
    if len(parts) != 2:
        return "unknown"
    band = parts[1]
    try:
        lo = int(band.split("-")[0])
    except:
        return "unknown"
    if lo < 20:
        return "deep (0-19c)"
    elif lo < 35:
        return "mid (20-34c)"
    else:
        return "near-50c (35-49c)"

regime_groups = defaultdict(list)
for r in underdog_sweeps:
    regime_groups[regime_for_cell(r["cell"])].append(r)

for regime in ["deep (0-19c)", "mid (20-34c)", "near-50c (35-49c)", "unknown"]:
    rows = regime_groups.get(regime, [])
    if not rows:
        continue
    w("### 4.%d Underdog regime: %s (%d cells)" % (
        ["deep (0-19c)", "mid (20-34c)", "near-50c (35-49c)", "unknown"].index(regime)+1, regime, len(rows)))
    w()
    w("| Cell | band | N | optimal_exit_cents | curve_max_value | exit@15c value |")
    w("|---|---|--:|--:|--:|--:|")
    for r in sorted(rows, key=lambda x: x["cell"]):
        opt_n, opt_v = sweep_optimal[r["cell"]]
        e15 = r.get("exit_15", "")
        try:
            e15_str = "%.2f" % float(e15)
        except:
            e15_str = e15
        w("| %s | %s | %s | %d | %.2f | %s |" % (
            r["cell"], r["band_width"], r["N"], opt_n, opt_v, e15_str))
    w()

w("### 4.4 Cells where optimal differs from current deployed by >5c")
w()
w("(Comparing each sweep cell against any matching active scorecard-style cell in paper config)")
w()
w("| Sweep cell | optimal | matched paper config cells | deployed exit_cents | delta |")
w("|---|--:|---|--:|--:|")
divergence_count = 0
for r in underdog_sweeps:
    opt_n, opt_v = sweep_optimal[r["cell"]]
    sweep_cell = r["cell"]
    # Find matching scorecard cells (5c bands)
    parts = sweep_cell.rsplit("_", 1)
    if len(parts) != 2:
        continue
    base, band = parts
    try:
        lo, hi = band.split("-")
        lo = int(lo)
    except:
        continue
    sub_lo = lo
    sub_hi = sub_lo + 4
    sub_lo_2 = sub_lo + 5
    sub_hi_2 = sub_lo_2 + 4
    candidates = ["%s_%d-%d" % (base, sub_lo, sub_hi), "%s_%d-%d" % (base, sub_lo_2, sub_hi_2)]
    deployed_str = []
    for c in candidates:
        if c in active_cells:
            ec = active_cells[c].get("exit_cents", "?")
            deployed_str.append("%s=%s" % (c, ec))
            try:
                ec_int = int(ec)
                delta = opt_n - ec_int
                if abs(delta) > 5:
                    divergence_count += 1
                    w("| %s | %d | %s | %d | %+d |" % (sweep_cell, opt_n, c, ec_int, delta))
            except:
                pass
w()
w("Total cells with optimal-vs-deployed delta >5c (underdog): **%d**" % divergence_count)
w()
w("---")
w()

# === Section 5: Exit Sweep — Leader Cells ===
w("## 5. Exit Sweep — Leader Cells (10c bands)")
w()
def leader_regime(cell):
    parts = cell.rsplit("_", 1)
    if len(parts) != 2:
        return "unknown"
    try:
        lo = int(parts[1].split("-")[0])
    except:
        return "unknown"
    if lo < 60:
        return "near-50c (50-59c)"
    elif lo < 80:
        return "mid (60-79c)"
    else:
        return "deep (80-99c)"

leader_groups = defaultdict(list)
for r in leader_sweeps:
    leader_groups[leader_regime(r["cell"])].append(r)

for regime in ["near-50c (50-59c)", "mid (60-79c)", "deep (80-99c)", "unknown"]:
    rows = leader_groups.get(regime, [])
    if not rows:
        continue
    w("### 5.%d Leader regime: %s (%d cells)" % (
        ["near-50c (50-59c)", "mid (60-79c)", "deep (80-99c)", "unknown"].index(regime)+1, regime, len(rows)))
    w()
    w("| Cell | band | N | optimal_exit_cents | curve_max_value | exit@15c value |")
    w("|---|---|--:|--:|--:|--:|")
    for r in sorted(rows, key=lambda x: x["cell"]):
        opt_n, opt_v = sweep_optimal[r["cell"]]
        e15 = r.get("exit_15", "")
        try:
            e15_str = "%.2f" % float(e15)
        except:
            e15_str = e15
        w("| %s | %s | %s | %d | %.2f | %s |" % (
            r["cell"], r["band_width"], r["N"], opt_n, opt_v, e15_str))
    w()

w("### 5.4 Leader cells where optimal differs from current deployed by >5c")
w()
w("| Sweep cell | optimal | matched paper config cells | deployed exit_cents | delta |")
w("|---|--:|---|--:|--:|")
leader_divergence_count = 0
for r in leader_sweeps:
    opt_n, opt_v = sweep_optimal[r["cell"]]
    sweep_cell = r["cell"]
    parts = sweep_cell.rsplit("_", 1)
    if len(parts) != 2:
        continue
    base, band = parts
    try:
        lo, hi = band.split("-")
        lo = int(lo)
    except:
        continue
    sub_lo = lo
    sub_hi = sub_lo + 4
    sub_lo_2 = sub_lo + 5
    sub_hi_2 = sub_lo_2 + 4
    candidates = ["%s_%d-%d" % (base, sub_lo, sub_hi), "%s_%d-%d" % (base, sub_lo_2, sub_hi_2)]
    for c in candidates:
        if c in active_cells:
            ec = active_cells[c].get("exit_cents", "?")
            try:
                ec_int = int(ec)
                delta = opt_n - ec_int
                if abs(delta) > 5:
                    leader_divergence_count += 1
                    w("| %s | %d | %s | %d | %+d |" % (sweep_cell, opt_n, c, ec_int, delta))
            except:
                pass
w()
w("Total leader cells with optimal-vs-deployed delta >5c: **%d**" % leader_divergence_count)
w()
w("---")
w()

# === Section 6: Bias Correction ===
w("## 6. Bias Correction Contents")
w()
w("Per-cell `mean_bias_first_vs_late_mid` from `entry_price_bias_by_cell.csv`. Bias is in cents — first_price minus late-game mid; positive bias means first_price was systematically HIGHER than the eventual fair late-game mid (entry was overpriced).")
w()

# Sort by absolute bias
def bias_val(r):
    try:
        return float(r["mean_bias_first_vs_late_mid"])
    except:
        return 0.0

sorted_bias = sorted(bias, key=lambda r: abs(bias_val(r)), reverse=True)

w("### 6.1 All %d cells with bias data, sorted by absolute bias" % len(bias))
w()
w("| Cell | N_late | mean_bias | stddev | median | within_3c | within_5c |")
w("|---|--:|--:|--:|--:|--:|--:|")
for r in sorted_bias:
    w("| %s | %s | %s | %s | %s | %s%% | %s%% |" % (
        r["cell"], r["N_late"], r["mean_bias_first_vs_late_mid"],
        r["stddev"], r["median"], r["pct_within_3c"], r["pct_within_5c"]))
w()

w("### 6.2 Cells with bias > 5c (material)")
w()
material_bias = [r for r in bias if abs(bias_val(r)) > 5]
w("**%d cells** have |bias| > 5c:" % len(material_bias))
w()
w("| Cell | bias |")
w("|---|--:|")
for r in sorted(material_bias, key=lambda r: -abs(bias_val(r))):
    w("| %s | %+.1f |" % (r["cell"], bias_val(r)))
w()

w("### 6.3 Cells with bias > 20c (analyzing different markets entirely)")
w()
huge_bias = [r for r in bias if abs(bias_val(r)) > 20]
if huge_bias:
    w("**%d cells** have |bias| > 20c. Yesterday's findings called out ATP_CHALL underdogs 25-49 (+21-37c) and ATP_MAIN leaders 50-64 (+13-15c). Reproducing:" % len(huge_bias))
    w()
    w("| Cell | bias |")
    w("|---|--:|")
    for r in sorted(huge_bias, key=lambda r: -abs(bias_val(r))):
        w("| %s | %+.1f |" % (r["cell"], bias_val(r)))
else:
    w("**No cells** have |bias| > 20c in this version of the bias file. **Operator's prior framing of \"+21-37c bias on ATP_CHALL underdogs 25-49\" does NOT reproduce in this artifact.** Possible explanations: this is a different (later) version of the bias analysis with smoother corrections; OR a different bias-window methodology was used for the prior framing. Flag for review.")
w()
w("---")
w()

# === Section 7: Current Paper Config ===
w("## 7. Current Paper Config Snapshot")
w()
w("**File**: `config/deploy_v4_paper.json`")
w()
w("### 7.1 Top-level config")
w()
for k, v in paper_cfg.items():
    if k in ("active_cells", "disabled_cells"):
        continue
    w("- `%s`: `%s`" % (k, json.dumps(v)))
w()

w("### 7.2 Active cells (%d)" % len(active_cells))
w()
w("| Cell | strategy | exit_cents | dca_trigger_cents | other |")
w("|---|---|--:|--:|---|")
for cell, cfg in sorted(active_cells.items()):
    strategy = cfg.get("strategy", "")
    exit_c = cfg.get("exit_cents", "")
    dca = cfg.get("dca_trigger_cents", "")
    other_keys = [k for k in cfg.keys() if k not in ("strategy", "exit_cents", "dca_trigger_cents")]
    other = ", ".join("%s=%s" % (k, cfg[k]) for k in other_keys)
    w("| %s | %s | %s | %s | %s |" % (cell, strategy, exit_c, dca, other))
w()

w("### 7.3 Disabled cells (%d)" % len(disabled_cells))
w()
for c in sorted(disabled_cells):
    w("- `%s`" % c)
w()
w("---")
w()

# === Section 8: Active Status Disagreements ===
w("## 8. Diff: Active Status Disagreements")
w()

scorecard_cells = set(score_by_cell.keys())
all_paper_cells = active_cells_set | disabled_cells_set

# SCALPER_EDGE in scorecard, disabled in paper
edge_disabled = [c for c, r in score_by_cell.items()
                 if r["mechanism"] == "SCALPER_EDGE" and c in disabled_cells_set]
edge_absent = [c for c, r in score_by_cell.items()
               if r["mechanism"] == "SCALPER_EDGE" and c not in all_paper_cells]
edge_active = [c for c, r in score_by_cell.items()
               if r["mechanism"] == "SCALPER_EDGE" and c in active_cells_set]

# Bleed-like in scorecard, active in paper
bleed_classes = ("SCALPER_NEGATIVE", "MIXED_BREAK_EVEN", "SETTLEMENT_RIDE_CONTAMINATED", "SCALPER_BREAK_EVEN")
bleed_active = [c for c, r in score_by_cell.items()
                if r["mechanism"] in bleed_classes and c in active_cells_set]

# UNCALIBRATED in scorecard
uncal_active = [c for c, r in score_by_cell.items()
                if r["mechanism"] == "UNCALIBRATED" and c in active_cells_set]
uncal_disabled = [c for c, r in score_by_cell.items()
                  if r["mechanism"] == "UNCALIBRATED" and c in disabled_cells_set]
uncal_absent = [c for c, r in score_by_cell.items()
                if r["mechanism"] == "UNCALIBRATED" and c not in all_paper_cells]

w("### 8.1 Counts at a glance")
w()
w("| Disagreement | Count |")
w("|---|--:|")
w("| SCALPER_EDGE in rebuild, **disabled** in paper config (should consider enabling) | %d |" % len(edge_disabled))
w("| SCALPER_EDGE in rebuild, **absent** from paper config (not deployed at all) | %d |" % len(edge_absent))
w("| SCALPER_EDGE in rebuild, **active** in paper config (aligned ✓) | %d |" % len(edge_active))
w("| Bleed-like (NEGATIVE/MIXED/SETTLEMENT_RIDE/BREAK_EVEN), **active** in paper (consider disabling) | %d |" % len(bleed_active))
w("| UNCALIBRATED, **active** in paper (risk: no data backing) | %d |" % len(uncal_active))
w("| UNCALIBRATED, **disabled** in paper (no data, will not generate any) | %d |" % len(uncal_disabled))
w("| UNCALIBRATED, **absent** from paper config | %d |" % len(uncal_absent))
w()

w("### 8.2 SCALPER_EDGE cells DISABLED in paper (consider enabling)")
w()
if edge_disabled:
    w("| Cell | N | ROI%% | CI |")
    w("|---|--:|--:|---|")
    for c in sorted(edge_disabled):
        r = score_by_cell[c]
        w("| %s | %s | %s | [%s, %s] |" % (c, r["N"], r["decomposed_ROI"], r["ci_low"], r["ci_high"]))
else:
    w("(none)")
w()

w("### 8.3 SCALPER_EDGE cells ABSENT from paper (not deployed at all)")
w()
if edge_absent:
    w("| Cell | N | ROI%% | CI |")
    w("|---|--:|--:|---|")
    for c in sorted(edge_absent):
        r = score_by_cell[c]
        w("| %s | %s | %s | [%s, %s] |" % (c, r["N"], r["decomposed_ROI"], r["ci_low"], r["ci_high"]))
else:
    w("(none)")
w()

w("### 8.4 Bleed-like cells ACTIVE in paper (consider disabling)")
w()
if bleed_active:
    w("| Cell | mechanism | N | ROI%% | CI |")
    w("|---|---|--:|--:|---|")
    for c in sorted(bleed_active):
        r = score_by_cell[c]
        w("| %s | %s | %s | %s | [%s, %s] |" % (c, r["mechanism"], r["N"], r["decomposed_ROI"], r["ci_low"], r["ci_high"]))
else:
    w("(none)")
w()

w("### 8.5 UNCALIBRATED cells ACTIVE in paper (no data backing)")
w()
if uncal_active:
    w("| Cell | N | ROI%% (low confidence) |")
    w("|---|--:|--:|")
    for c in sorted(uncal_active):
        r = score_by_cell[c]
        w("| %s | %s | %s |" % (c, r["N"], r["decomposed_ROI"]))
else:
    w("(none)")
w()

w("### 8.6 UNCALIBRATED cells DISABLED in paper (will not generate data)")
w()
if uncal_disabled:
    w("| Cell |")
    w("|---|")
    for c in sorted(uncal_disabled):
        w("| %s |" % c)
else:
    w("(none)")
w()

w("---")
w()

# === Section 9: Exit_cents Disagreements ===
w("## 9. Diff: exit_cents disagreements (active cells only)")
w()

deltas = []  # (cell, deployed, optimal, delta)
no_match = []
for cell, cfg in active_cells.items():
    deployed = cfg.get("exit_cents")
    if deployed is None:
        continue
    sweep_cell = sweep_cell_for_scorecard(cell)
    if sweep_cell is None or sweep_cell not in sweep_optimal:
        no_match.append((cell, deployed))
        continue
    opt_n, opt_v = sweep_optimal[sweep_cell]
    try:
        deployed_int = int(deployed)
    except:
        no_match.append((cell, deployed))
        continue
    delta = opt_n - deployed_int
    deltas.append((cell, sweep_cell, deployed_int, opt_n, delta))

material = [d for d in deltas if abs(d[4]) > 5]
minor = [d for d in deltas if 1 <= abs(d[4]) <= 5]
matched = [d for d in deltas if d[4] == 0]

w("### 9.1 Counts")
w()
w("| Bucket | Count |")
w("|---|--:|")
w("| Active cells with sweep coverage | %d |" % len(deltas))
w("| Active cells with NO sweep match | %d |" % len(no_match))
w("| delta > 5c (material disagreement) | %d |" % len(material))
w("| delta 1-5c (minor) | %d |" % len(minor))
w("| delta = 0 (exact match) | %d |" % len(matched))
w()

w("### 9.2 Material disagreements (|delta| > 5c)")
w()
if material:
    w("| Active cell | matched sweep cell (10c band) | deployed exit_cents | optimal exit_cents | delta |")
    w("|---|---|--:|--:|--:|")
    for c, sc, d, o, dt in sorted(material, key=lambda x: -abs(x[4])):
        w("| %s | %s | %d | %d | %+d |" % (c, sc, d, o, dt))
else:
    w("(none)")
w()

w("### 9.3 Minor disagreements (|delta| 1-5c)")
w()
if minor:
    w("| Active cell | matched sweep cell | deployed | optimal | delta |")
    w("|---|---|--:|--:|--:|")
    for c, sc, d, o, dt in sorted(minor, key=lambda x: -abs(x[4])):
        w("| %s | %s | %d | %d | %+d |" % (c, sc, d, o, dt))
else:
    w("(none)")
w()

w("### 9.4 Exact matches (delta = 0)")
w()
if matched:
    w("| Active cell | sweep cell | exit_cents |")
    w("|---|---|--:|")
    for c, sc, d, o, dt in sorted(matched):
        w("| %s | %s | %d |" % (c, sc, d))
else:
    w("(none)")
w()

w("### 9.5 Active cells with NO sweep coverage")
w()
if no_match:
    w("| Active cell | deployed exit_cents |")
    w("|---|--:|")
    for c, d in sorted(no_match):
        w("| %s | %s |" % (c, d))
else:
    w("(none)")
w()

w("---")
w()

# === Section 10: Paper-only cells ===
w("## 10. Cells in Paper Config NOT in Rebuild Scorecard")
w()
paper_only_active = [c for c in active_cells_set if c not in scorecard_cells]
paper_only_disabled = [c for c in disabled_cells_set if c not in scorecard_cells]

w("### 10.1 Active in paper, no rebuild data (deployed without backing)")
w()
if paper_only_active:
    w("| Cell | exit_cents | strategy |")
    w("|---|--:|---|")
    for c in sorted(paper_only_active):
        cfg = active_cells[c]
        w("| %s | %s | %s |" % (c, cfg.get("exit_cents", ""), cfg.get("strategy", "")))
else:
    w("(none)")
w()

w("### 10.2 Disabled in paper, no rebuild data")
w()
if paper_only_disabled:
    for c in sorted(paper_only_disabled):
        w("- `%s`" % c)
else:
    w("(none)")
w()

w("---")
w()

# === Section 11: Rebuild-only cells ===
w("## 11. Cells in Rebuild Scorecard NOT in Paper Config")
w()
rebuild_only = [c for c in scorecard_cells if c not in all_paper_cells]
w("### 11.1 Cells in scorecard but absent from paper config (any list)")
w()
if rebuild_only:
    by_mech_only = defaultdict(list)
    for c in rebuild_only:
        by_mech_only[score_by_cell[c]["mechanism"]].append(c)
    for mech, cells in sorted(by_mech_only.items()):
        w("**%s** (%d):" % (mech, len(cells)))
        for c in sorted(cells):
            r = score_by_cell[c]
            w("- `%s` (N=%s, ROI=%s)" % (c, r["N"], r["decomposed_ROI"]))
        w()
else:
    w("(none)")
w()

w("---")
w()

# === Section 12: Summary table ===
w("## 12. Summary Table")
w()

edge_total = mech_counts.get("SCALPER_EDGE", 0)
brk_total = mech_counts.get("SCALPER_BREAK_EVEN", 0)
neg_total = mech_counts.get("SCALPER_NEGATIVE", 0)
mix_total = mech_counts.get("MIXED_BREAK_EVEN", 0)
sett_total = mech_counts.get("SETTLEMENT_RIDE_CONTAMINATED", 0)
uncal_total = mech_counts.get("UNCALIBRATED", 0)

# Disabled by mechanism
edge_disabled_n = sum(1 for c, r in score_by_cell.items()
                       if r["mechanism"] == "SCALPER_EDGE" and c in disabled_cells_set)
edge_active_n = len(edge_active)
edge_absent_n = edge_total - edge_disabled_n - edge_active_n

bleed_active_n = len(bleed_active)
bleed_disabled_n = sum(1 for c, r in score_by_cell.items()
                        if r["mechanism"] in bleed_classes and c in disabled_cells_set)
bleed_total = neg_total + mix_total + sett_total + brk_total
bleed_absent_n = bleed_total - bleed_active_n - bleed_disabled_n

uncal_active_n = len(uncal_active)
uncal_disabled_n = len(uncal_disabled)
uncal_absent_n = uncal_total - uncal_active_n - uncal_disabled_n

w("| Metric | Value |")
w("|---|--:|")
w("| Total cells in paper config | %d |" % (len(active_cells) + len(disabled_cells)))
w("| Paper config: active | %d |" % len(active_cells))
w("| Paper config: disabled | %d |" % len(disabled_cells))
w("| Total cells in rebuild scorecard | %d |" % len(scorecard))
w("| SCALPER_EDGE total in rebuild | %d |" % edge_total)
w("| SCALPER_EDGE active in paper | %d |" % edge_active_n)
w("| SCALPER_EDGE disabled in paper | %d |" % edge_disabled_n)
w("| SCALPER_EDGE absent from paper | %d |" % edge_absent_n)
w("| Bleed-like total in rebuild (NEG+MIX+SETTLE+BRK) | %d |" % bleed_total)
w("| Bleed-like active in paper | %d |" % bleed_active_n)
w("| Bleed-like disabled in paper | %d |" % bleed_disabled_n)
w("| Bleed-like absent from paper | %d |" % bleed_absent_n)
w("| UNCALIBRATED total in rebuild | %d |" % uncal_total)
w("| UNCALIBRATED active in paper | %d |" % uncal_active_n)
w("| UNCALIBRATED disabled in paper | %d |" % uncal_disabled_n)
w("| UNCALIBRATED absent from paper | %d |" % uncal_absent_n)
w("| Paper-only active (no rebuild data) | %d |" % len(paper_only_active))
w("| Paper-only disabled (no rebuild data) | %d |" % len(paper_only_disabled))
w("| Rebuild-only (not in any paper list) | %d |" % len(rebuild_only))
w()

w("---")
w()

# === Section 13: Recommended changes ===
w("## 13. Recommended Changes (suggestions only — no config changes made)")
w()
w("These are derived directly from §8 and §9. Frame: \"rebuild suggests X\". Operator decides whether/when to deploy.")
w()

w("### 13.1 Cells the rebuild suggests ENABLING (currently disabled or absent)")
w()
recos = []
for c in sorted(edge_disabled):
    r = score_by_cell[c]
    recos.append("- **Enable** `%s` — currently disabled. Rebuild: SCALPER_EDGE, N=%s, ROI=%s, CI [%s, %s]" %
                 (c, r["N"], r["decomposed_ROI"], r["ci_low"], r["ci_high"]))
for c in sorted(edge_absent):
    r = score_by_cell[c]
    recos.append("- **Add (enable)** `%s` — not in paper config at all. Rebuild: SCALPER_EDGE, N=%s, ROI=%s, CI [%s, %s]" %
                 (c, r["N"], r["decomposed_ROI"], r["ci_low"], r["ci_high"]))
if recos:
    for r in recos:
        w(r)
else:
    w("(none — all SCALPER_EDGE cells already active)")
w()

w("### 13.2 Cells the rebuild suggests DISABLING (active in paper, bleed-like or worse)")
w()
recos = []
for c in sorted(bleed_active):
    r = score_by_cell[c]
    recos.append("- **Disable** `%s` — currently active. Rebuild: %s, ROI=%s, CI [%s, %s]" %
                 (c, r["mechanism"], r["decomposed_ROI"], r["ci_low"], r["ci_high"]))
if recos:
    for r in recos:
        w(r)
else:
    w("(none)")
w()

w("### 13.3 Cells with material exit_cents disagreement (>5c)")
w()
if material:
    for c, sc, d, o, dt in sorted(material, key=lambda x: -abs(x[4])):
        w("- **Adjust** `%s` exit_cents from %d to %d (delta %+d, sweep cell %s)" % (c, d, o, dt, sc))
else:
    w("(none)")
w()

w("### 13.4 Risk-review queue")
w()
if uncal_active:
    w("**UNCALIBRATED cells currently active** — risk that the bot trades these without backing data. Operator decides whether the burn-in itself counts as data-gathering, or whether they should be disabled until classified:")
    w()
    for c in sorted(uncal_active):
        r = score_by_cell[c]
        w("- `%s` (N=%s in scorecard, but mechanism=UNCALIBRATED → low confidence)" % (c, r["N"]))
else:
    w("(no UNCALIBRATED cells active)")
w()

w("---")
w()

# === Section 14: Methodology concerns ===
w("## 14. Methodology Concerns")
w()
w("### 14.1 Sample size")
w()
small_n_edge = [c for c, r in score_by_cell.items()
                 if r["mechanism"] == "SCALPER_EDGE" and int(r["N"]) < 50]
if small_n_edge:
    w("**SCALPER_EDGE cells with N < 50** (smaller-sample edges should be treated cautiously):")
    w()
    for c in sorted(small_n_edge):
        r = score_by_cell[c]
        w("- `%s`: N=%s" % (c, r["N"]))
else:
    w("All SCALPER_EDGE cells have N >= 50.")
w()

w("### 14.2 Classification thresholds — opaque from script header")
w()
w("- The exact CI computation (formula, bootstrap vs normal-approx) isn't shown in the head of the script. Need to read further.")
w("- The threshold separating SCALPER_EDGE from SCALPER_BREAK_EVEN — explicit threshold (CI excludes zero? Mean ROI > X%?) — not shown.")
w("- Whether all 6 mechanism classes were defined in this script or in a separate post-processing step is not visible from the header.")
w()

w("### 14.3 Bias correction coverage")
w()
w("- Bias map only loads cells with `N_late >= 10` (per script line: `if n_late >= 10: bias_map[r['cell']] = ...`). Cells with N_late < 10 inherit zero correction. This means:")
w()
zero_bias = [r for r in bias if int(r["N_late"]) < 10]
w("  - %d of %d cells in the bias file have N_late < 10 → they get NO bias correction in the scorecard." % (len(zero_bias), len(bias)))
w()
w("### 14.4 Underdog three-regime split")
w()
w("- Regimes (`deep`, `mid`, `near-50c`) are presented in §4 with operator-defined boundaries (0-19c / 20-34c / 35-49c). The rebuild scripts at `/tmp/` do not appear to bake these boundaries in — they emerge from the analysis narrative, not the data. **Operator-defined**, not data-driven.")
w()

w("### 14.5 Bias artifact discrepancy")
w()
w("- Operator's prompt referenced \"+21-37c bias on ATP_CHALL underdogs 25-49\" and \"+13-15c on ATP_MAIN leaders 50-64\" — these magnitudes do NOT appear in the current `entry_price_bias_by_cell.csv` (max |bias| in current file is much smaller, see §6.3). Possible explanations: different bias-window methodology in the prior framing, OR an earlier version of the bias file at a different path. Worth checking `/tmp/per_cell_verification/entry_price_bias.run1.csv` and `/tmp/per_cell_verification/entry_price_bias_by_cell.run1.csv` (both exist on disk).")
w()

w("---")
w()

# === Section 15: What the diff doesn't tell us ===
w("## 15. What the Diff Report Does NOT Tell Us (open questions from yesterday)")
w()
w("- **Inversion-pair analysis** — queued yesterday, not run. Whether the rebuild correctly handles inverted ticker pairs (e.g., A vs B and B vs A) hasn't been validated.")
w("- **30 UNCALIBRATED cells split by price-regime priors** — not attempted. UNCALIBRATED cells are still a flat \"insufficient data\" bucket.")
w("- **Cell band geometry** — 5c uniform vs alternative bands (e.g., wider near 50c, narrower in extremes) — open question. Current scorecard uses 5c bands; current sweep uses 10c bands. Inconsistent.")
w("- **Multi-axis edge dimensions** — time-to-start, spread, FV gap, depth, volume, trajectory, tournament tier, surface — none of these are in the scorecard. Cell name encodes only `tier_side_priceband`.")
w("- **Greeks framing** — not operationalized. The rebuild expresses ROI%% but not delta/gamma/vega-style exposure decomposition.")
w("- **First-vs-late bias methodology** — the file used here may be a smoothed/late version of the bias analysis. The +21-37c values in the operator's prior framing don't appear in this file (see §14.5).")
w("- **Sample-size confidence threshold for SCALPER_EDGE classification** — not explicit in the script header.")
w("- **Whether SCALPER_BREAK_EVEN cells should be active or disabled** — they're profitable in expectation but not statistically distinguishable from zero. Trading them is a judgment call the rebuild doesn't resolve.")
w()
w("All open questions from yesterday's investigation remain open.")
w()

# === Write the report ===
with open(OUT_PATH, "w") as f:
    f.write("\n".join(LINES))

print("WROTE:", OUT_PATH)
print("Lines:", len(LINES))
