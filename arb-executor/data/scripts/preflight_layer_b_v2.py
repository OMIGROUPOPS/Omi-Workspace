#!/usr/bin/env python3
"""Pre-launch validation probe for Layer B v2 Phase 3.

Authored Session 11 post-cell-20-crash diagnostic per user's Option-2 instruction:
"fix + comprehensive pre-launch validation" before re-launching Phase 3.

Probes:
  a. created_time format variants in g9_trades; verify pd.to_datetime(format="ISO8601")
     parses cleanly on every observed variant.
  b. settlement_ts format variants in g9_metadata; verify datetime.fromisoformat (with
     Z normalization) parses cleanly.
  c. Schema invariants: every ticker in any cell's manifest has at least one row in
     g9_trades; every (cell, ticker) tuple resolves to non-empty trade tape; taker_side
     is non-null on >99% of trade rows in a stratified sample.
  d. Cell manifest sanity: all 235 cells in build_corpus_cell_list() produce at least
     one valid ticker tuple.
  e. Resume-state coherence: number of JSONL lines == number of cell_summary_cell_NNN
     parquet files in the phase3 output dir == max(cell_idx in JSONL) + 1 (contiguous
     from cell 0). If mismatch, surface for inspection before relaunch.

Exit codes:
  0  → all checks pass; safe to relaunch Phase 3
  1  → at least one check failed; do NOT relaunch
"""

import json
import os
import re
import sys
import random
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).parent))
from cell_key_helpers import (
    ENTRY_BANDS, SPREAD_BANDS, VOLUME_BANDS, REGIMES, CATEGORIES,
    categorize, entry_band_idx, spread_band_name,
    detect_match_start, regime_for_moment, volume_intensity_for_market,
)

DUR_DIR = "/root/Omi-Workspace/arb-executor/data/durable"
LAYER_B_PARQUET = os.path.join(DUR_DIR, "layer_b_v1", "exit_policy_per_cell.parquet")
SAMPLE_MANIFEST = os.path.join(DUR_DIR, "layer_a_v1", "sample_manifest.json")
TRADES_PARQUET = os.path.join(DUR_DIR, "g9_trades.parquet")
META_PARQUET = os.path.join(DUR_DIR, "g9_metadata.parquet")
PHASE3_DIR = os.path.join(DUR_DIR, "layer_b_v2", "phase3")

FAILURES = []
WARNINGS = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}{(': ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append((name, detail))


def warn(name, detail):
    print(f"  [WARN] {name}: {detail}")
    WARNINGS.append((name, detail))


# ----------------------------------------------------------------
# (a) g9_trades.created_time format variant scan
# ----------------------------------------------------------------

def probe_created_time_variants():
    print("\n=== (a) g9_trades.created_time format variants ===")
    # Memory-efficient sampling: enumerate the manifest's ticker universe (the only
    # tickers Phase 3 actually touches) instead of reading the full ticker column from
    # g9_trades (33M rows × string objects OOMs the 1.9 GiB VPS). Sample 100 tickers
    # stratified across the manifest entries to catch cross-cell format heterogeneity.
    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)
    manifest_tickers = set()
    for mkey, entry in manifest.items():
        for t in entry.get("tickers", []):
            manifest_tickers.add(t)
    all_tickers = sorted(manifest_tickers)
    print(f"  unique manifest tickers (Phase 3 universe): {len(all_tickers):,}")
    random.seed(42)
    sample_tickers = random.sample(all_tickers, min(100, len(all_tickers)))
    print(f"  sampled tickers: {len(sample_tickers)}")

    variant_patterns = {}  # regex_label → count
    sample_values = {}     # regex_label → example string
    sample_values_lim = 5

    def classify(s):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", s):
            return "microsec_Z"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", s):
            return "second_Z"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:?\d{2}", s):
            return "microsec_offset"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:?\d{2}", s):
            return "second_offset"
        return "OTHER"

    total_rows = 0
    parse_failures = []
    for ticker in sample_tickers:
        ts = pq.read_table(TRADES_PARQUET, columns=["created_time"],
                           filters=[("ticker", "=", ticker)]).to_pandas()
        for v in ts["created_time"].values:
            if v is None:
                continue
            cls = classify(str(v))
            variant_patterns[cls] = variant_patterns.get(cls, 0) + 1
            if cls not in sample_values:
                sample_values[cls] = []
            if len(sample_values[cls]) < sample_values_lim:
                sample_values[cls].append(str(v))
        total_rows += len(ts)
        # Test ISO8601 parser on the full set (catches per-ticker outliers)
        try:
            pd.to_datetime(ts["created_time"], format="ISO8601")
        except Exception as e:
            parse_failures.append((ticker, str(e)))

    print(f"  rows sampled: {total_rows:,}")
    print(f"  variant distribution:")
    for k, v in sorted(variant_patterns.items(), key=lambda x: -x[1]):
        print(f"    {k:18s} {v:>10,}  example: {sample_values.get(k, ['?'])[0]!r}")

    check("ISO8601 parser handles all variants (no per-ticker failures)",
          len(parse_failures) == 0,
          f"{len(parse_failures)} ticker(s) failed" if parse_failures else "")
    if parse_failures:
        for ticker, err in parse_failures[:3]:
            print(f"    {ticker}: {err[:100]}")

    check("no OTHER format variants",
          variant_patterns.get("OTHER", 0) == 0,
          f"{variant_patterns.get('OTHER', 0)} unclassified" if variant_patterns.get("OTHER") else "")
    if variant_patterns.get("OTHER", 0) > 0:
        for v in sample_values.get("OTHER", [])[:5]:
            print(f"    OTHER example: {v!r}")

    return variant_patterns


# ----------------------------------------------------------------
# (b) g9_metadata.settlement_ts format variant scan
# ----------------------------------------------------------------

def probe_settlement_ts_variants():
    print("\n=== (b) g9_metadata.settlement_ts format variants ===")
    t = pq.read_table(META_PARQUET, columns=["ticker", "result", "settlement_ts"]).to_pandas()
    print(f"  total metadata rows: {len(t):,}")
    binary = t[t["result"].isin(["yes", "no"])]
    print(f"  binary-outcome rows (used by producer): {len(binary):,}")

    parse_failures = []
    variants = {}
    for s in binary["settlement_ts"].values:
        if s is None or s == "":
            variants["null_or_empty"] = variants.get("null_or_empty", 0) + 1
            continue
        try:
            datetime.fromisoformat(str(s).replace("Z", "+00:00"))
            # Classify
            if str(s).endswith("Z"):
                variants["ends_Z"] = variants.get("ends_Z", 0) + 1
            elif re.search(r"[+-]\d{2}:?\d{2}$", str(s)):
                variants["has_offset"] = variants.get("has_offset", 0) + 1
            else:
                variants["naive"] = variants.get("naive", 0) + 1
        except Exception as e:
            parse_failures.append((s, str(e)))
            variants["parse_fail"] = variants.get("parse_fail", 0) + 1

    print(f"  variant distribution (after Z normalization):")
    for k, v in sorted(variants.items(), key=lambda x: -x[1]):
        print(f"    {k:18s} {v:>10,}")

    check("fromisoformat handles all settlement_ts (Z-normalized)",
          len(parse_failures) == 0,
          f"{len(parse_failures)} parse failures" if parse_failures else "")
    if parse_failures:
        for s, err in parse_failures[:3]:
            print(f"    {s!r}: {err[:80]}")

    null_count = variants.get("null_or_empty", 0)
    if null_count > 0:
        warn("settlement_ts has nulls in binary-outcome rows",
             f"{null_count} rows; producer handles via meta=None path")


# ----------------------------------------------------------------
# (c) Schema invariants: ticker presence + taker_side non-null
# ----------------------------------------------------------------

def probe_schema_invariants():
    print("\n=== (c) Schema invariants ===")
    # Stratified-by-ticker sample to avoid OOM on full taker_side column read.
    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)
    all_tickers = sorted({t for e in manifest.values() for t in e.get("tickers", [])})
    random.seed(43)
    sample_tickers = random.sample(all_tickers, min(50, len(all_tickers)))

    n_total = 0
    n_null = 0
    n_other = 0
    n_rows_per_ticker = []
    empty_tickers = []
    for ticker in sample_tickers:
        t = pq.read_table(TRADES_PARQUET, columns=["taker_side"],
                          filters=[("ticker", "=", ticker)]).to_pandas()
        if len(t) == 0:
            empty_tickers.append(ticker)
            continue
        n_rows_per_ticker.append(len(t))
        n_total += len(t)
        n_null += int(t["taker_side"].isna().sum())
        n_other += int((~t["taker_side"].isin(["yes", "no"]) & t["taker_side"].notna()).sum())

    pct_null = n_null / max(1, n_total)
    pct_other = n_other / max(1, n_total)
    print(f"  sampled tickers: {len(sample_tickers)}; rows scanned: {n_total:,}")
    print(f"  empty tickers (no g9_trades rows): {len(empty_tickers)}")
    print(f"  taker_side null: {n_null:,} ({pct_null:.4%})")
    print(f"  taker_side neither 'yes' nor 'no' nor null: {n_other:,} ({pct_other:.4%})")
    check("every sampled ticker has at least one g9_trades row",
          len(empty_tickers) == 0,
          f"{len(empty_tickers)} empty tickers: {empty_tickers[:3]}" if empty_tickers else "")
    check("taker_side null rate < 1%", pct_null < 0.01, f"{pct_null:.4%}")
    check("taker_side anomaly rate < 0.1%", pct_other < 0.001, f"{pct_other:.4%}")


# ----------------------------------------------------------------
# (d) Cell manifest sanity
# ----------------------------------------------------------------

def probe_cell_manifest_sanity():
    print("\n=== (d) Cell manifest sanity ===")
    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)
    print(f"  manifest entries: {len(manifest):,}")

    layer_b = pq.read_table(LAYER_B_PARQUET).to_pandas()
    pre = layer_b[layer_b["channel"] == "premarket"].copy()

    def _is_settle(s):
        try:
            return json.loads(s).get("horizon_min") == "settle"
        except Exception:
            return False

    pre["_is_settle"] = pre["policy_params"].apply(_is_settle)
    non_settle = pre[~pre["_is_settle"]].copy()
    cell_cols = ["category", "entry_band_lo", "entry_band_hi", "spread_band", "volume_intensity"]
    cells = (non_settle.sort_values(cell_cols + ["policy_type", "policy_params"])
                       .drop_duplicates(subset=cell_cols, keep="first")
                       .sort_values(cell_cols)
                       .reset_index(drop=True))
    print(f"  non-settle premarket cells (build_corpus_cell_list): {len(cells):,}")

    empty_cells = []
    missing_keys = []
    for cell_idx, c in cells.iterrows():
        idx = int(c["entry_band_lo"] // 10)
        mkey = f"premarket__{idx}__{c['spread_band']}__{c['volume_intensity']}__{c['category']}"
        if mkey not in manifest:
            missing_keys.append((cell_idx, mkey))
            continue
        tickers = manifest[mkey].get("tickers", [])
        if not tickers:
            empty_cells.append((cell_idx, mkey))

    check("every cell has manifest entry",
          len(missing_keys) == 0,
          f"{len(missing_keys)} cells missing" if missing_keys else "")
    if missing_keys:
        for ci, mk in missing_keys[:3]:
            print(f"    cell_idx={ci} mkey={mk}")
    check("every cell has at least one ticker in manifest",
          len(empty_cells) == 0,
          f"{len(empty_cells)} empty cells" if empty_cells else "")
    if empty_cells:
        for ci, mk in empty_cells[:3]:
            print(f"    cell_idx={ci} mkey={mk}")


# ----------------------------------------------------------------
# (e) Resume-state coherence (phase3 output dir)
# ----------------------------------------------------------------

def probe_resume_state():
    print("\n=== (e) Phase 3 resume-state coherence ===")
    progress_path = os.path.join(PHASE3_DIR, "_progress_summary.jsonl")
    if not os.path.exists(progress_path):
        print(f"  no JSONL at {progress_path} → fresh run (no resume state)")
        return

    with open(progress_path) as f:
        jsonl_lines = [json.loads(line) for line in f if line.strip()]
    print(f"  JSONL lines: {len(jsonl_lines)}")
    jsonl_idxs = sorted({entry["cell_idx"] for entry in jsonl_lines})
    print(f"  unique cell_idx values: {len(jsonl_idxs)}")
    print(f"  max cell_idx in JSONL: {max(jsonl_idxs) if jsonl_idxs else 'n/a'}")

    import glob
    per_cell_files = sorted(glob.glob(os.path.join(PHASE3_DIR, "cell_summary_cell_*.parquet")))
    print(f"  per-cell parquets: {len(per_cell_files)}")
    parquet_idxs = sorted(
        int(re.search(r"cell_summary_cell_(\d+)\.parquet", p).group(1))
        for p in per_cell_files
    )

    check("JSONL line count == per-cell parquet count",
          len(jsonl_lines) == len(per_cell_files),
          f"JSONL={len(jsonl_lines)} parquets={len(per_cell_files)}")
    check("JSONL cell_idx set == parquet cell_idx set",
          set(jsonl_idxs) == set(parquet_idxs),
          f"JSONL∖parquet={set(jsonl_idxs) - set(parquet_idxs)} parquet∖JSONL={set(parquet_idxs) - set(jsonl_idxs)}")
    check("JSONL cell_idx values are contiguous from 0",
          jsonl_idxs == list(range(max(jsonl_idxs) + 1)) if jsonl_idxs else True,
          f"non-contiguous; missing {set(range(max(jsonl_idxs)+1)) - set(jsonl_idxs)}" if jsonl_idxs and jsonl_idxs != list(range(max(jsonl_idxs)+1)) else "")

    # Sanity check: do the JSONL values look right? (n_filled, fill_rate)
    bad_jsonl_rows = []
    for entry in jsonl_lines:
        n_moments = entry.get("n_moments", 0)
        n_filled = entry.get("n_filled", 0)
        fill_rate = entry.get("replay_fill_rate")
        if n_filled is not None and n_filled > n_moments and n_moments > 0:
            bad_jsonl_rows.append((entry["cell_idx"], "n_filled > n_moments",
                                    f"n_filled={n_filled} n_moments={n_moments}"))
        if fill_rate is not None and (fill_rate < 0 or fill_rate > 1):
            bad_jsonl_rows.append((entry["cell_idx"], "fill_rate out of [0,1]",
                                    f"fill_rate={fill_rate}"))
    check("JSONL n_filled/fill_rate values plausible",
          len(bad_jsonl_rows) == 0,
          f"{len(bad_jsonl_rows)} bad rows" if bad_jsonl_rows else "")
    if bad_jsonl_rows:
        for ci, name, det in bad_jsonl_rows[:5]:
            print(f"    cell_idx={ci}: {name} ({det})")


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------

def main():
    print(f"Preflight check for Layer B v2 Phase 3 — {datetime.now().isoformat(timespec='seconds')}")
    print(f"DUR_DIR={DUR_DIR}")
    print(f"PHASE3_DIR={PHASE3_DIR}")

    probe_created_time_variants()
    probe_settlement_ts_variants()
    probe_schema_invariants()
    probe_cell_manifest_sanity()
    probe_resume_state()

    print()
    print("=" * 60)
    print(f"FAILURES: {len(FAILURES)}")
    for name, det in FAILURES:
        print(f"  ✗ {name}: {det}")
    print(f"WARNINGS: {len(WARNINGS)}")
    for name, det in WARNINGS:
        print(f"  ! {name}: {det}")
    print("=" * 60)

    if FAILURES:
        print("VERDICT: FAIL — do NOT relaunch Phase 3")
        sys.exit(1)
    print("VERDICT: PASS — safe to relaunch Phase 3 (resume mode)")
    sys.exit(0)


if __name__ == "__main__":
    main()
