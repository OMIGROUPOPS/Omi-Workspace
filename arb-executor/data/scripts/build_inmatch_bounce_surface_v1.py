#!/usr/bin/env python3
"""
build_inmatch_bounce_surface_v1.py — Band-Free In-Match Bounce Surface producer.

Implements docs/inmatch_bounce_surface_v1_spec.md (committed 11dce1c).
Layer-A-equivalent per B16: descriptive market property, no exit/fees/fills.

Every structural choice is spec-mandated and probe-resolved (C38):
  axis = band-free price-level |mid_close - 0.50| (probe-1)
  pooled + category as level-covariate (probe-2)
  A39 dual-metric (cents AND ROI) — both emitted every row (structural, not cosmetic)
  A38 firewall — operational bounce uses ONLY finite-horizon labels;
    to-settlement is diagnostic-only (gate G3)
  in-match only, regime=="in_match" (B14/G17)

C37 discipline: write .new, reload from disk, gate-validate, os.replace on all-pass.
Bounded memory: per-ticker pushdown + explicit del + gc-every-200 (the n_profile OOM lesson).
Quarantine-don't-delete on any pre-existing output.

Usage:
  python3 build_inmatch_bounce_surface_v1.py [--phase {1,2}] [--input-base PATH] [--output-dir PATH]
  Phase 1 = 1000-ticker stratified sanity (<30min). Phase 2 = full cohort + all gates.
"""

import argparse
import gc
import hashlib
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


def _install_pandas3_pyarrow_compat_patch():
    try:
        import pyarrow.pandas_compat as _papc
        from pandas.core.dtypes.dtypes import DatetimeTZDtype as _DTZD
        def _patched_make_datetimetz(unit, tz):
            return _DTZD(unit=unit, tz=tz)
        _papc.make_datetimetz = _patched_make_datetimetz
    except Exception:
        pass

_install_pandas3_pyarrow_compat_patch()

ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

DEFAULT_INPUT_BASE = Path("data/durable")
DEFAULT_OUTPUT_DIR = Path("data/durable/inmatch_bounce_surface_v1")
DEFAULT_OUTPUT_FILE = "surface.parquet"
DEFAULT_REPORT_FILE = "validation_report.md"
DEFAULT_META_FILE = "surface.meta.json"

FINITE_HORIZONS = ["5min", "15min", "30min", "60min"]
HEADLINE_HORIZON = "30min"
DIAG_LABEL = "max_yes_bid_forward_to_settlement"

N_PRICE_BINS = 40
MIN_BIN_SUPPORT = 200
ENTRY_PRICE_LO = 0.01
ENTRY_PRICE_HI = 0.99

PMF_PUSHDOWN_COLS = [
    "ticker", "minute_ts", "category", "regime",
    "yes_bid_close", "yes_ask_close", "mid_close",
    "time_to_match_start_min",
    "max_yes_bid_forward_5min", "max_yes_bid_forward_15min",
    "max_yes_bid_forward_30min", "max_yes_bid_forward_60min",
    "max_yes_bid_forward_to_settlement",
]

CATEGORIES = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bounce_surface_v1")


@dataclass
class GateResult:
    name: str
    passed: bool
    n_violations: int
    detail: str


@dataclass
class ProducerResult:
    rows_emitted: int
    cohort_n: int
    in_match_minutes: int
    gate_results: list
    output_sha256: str
    output_bytes: int
    run_started_at_et: str
    run_completed_at_et: str
    inputs_sha256: dict = field(default_factory=dict)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _producer_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def read_pmf_for_ticker(pmf_path: Path, ticker: str) -> pd.DataFrame:
    tbl = pq.read_table(
        str(pmf_path),
        columns=PMF_PUSHDOWN_COLS,
        filters=[("ticker", "=", ticker)],
    )
    if tbl.num_rows == 0:
        return pd.DataFrame()
    return tbl.to_pandas()


def select_cohort(n_profile_path: Path) -> pd.DataFrame:
    npf = pd.read_parquet(n_profile_path)
    cohort = npf[
        npf["match_start_method"].isin(
            ["both_sides_price_discovery", "both_sides_trade_density"]
        )
        & (npf["tier"] == "live")
        & (npf["total_volume_in_match"] > 0)
    ][["ticker", "category", "match_start_method", "tier",
       "total_volume_in_match"]].copy()
    return cohort


def per_ticker_in_match_minutes(pmf_path: Path, ticker: str) -> pd.DataFrame:
    d = read_pmf_for_ticker(pmf_path, ticker)
    if len(d) == 0:
        return pd.DataFrame()
    d = d[d["regime"] == "in_match"]
    if len(d) == 0:
        return pd.DataFrame()
    d = d.dropna(subset=["yes_bid_close", "yes_ask_close", "mid_close"]).copy()
    if len(d) == 0:
        return pd.DataFrame()
    d["entry_price"] = d["yes_ask_close"]
    d = d[(d["entry_price"] > ENTRY_PRICE_LO) & (d["entry_price"] < ENTRY_PRICE_HI)]
    if len(d) == 0:
        return pd.DataFrame()
    d["price_level_dislocation"] = (d["mid_close"] - 0.50).abs()
    for h in FINITE_HORIZONS:
        col = f"max_yes_bid_forward_{h}"
        if col in d.columns:
            d[f"bounce_c_{h}"] = d[col] - d["entry_price"]
            d[f"bounce_roi_{h}"] = (d[col] - d["entry_price"]) / d["entry_price"]
        else:
            d[f"bounce_c_{h}"] = np.nan
            d[f"bounce_roi_{h}"] = np.nan
    if DIAG_LABEL in d.columns:
        d["bounce_c_to_settlement"] = d[DIAG_LABEL] - d["entry_price"]
    else:
        d["bounce_c_to_settlement"] = np.nan
    keep = (["ticker", "minute_ts", "category", "regime",
             "entry_price", "price_level_dislocation",
             "time_to_match_start_min", "bounce_c_to_settlement"]
            + [f"bounce_c_{h}" for h in FINITE_HORIZONS]
            + [f"bounce_roi_{h}" for h in FINITE_HORIZONS])
    return d[[c for c in keep if c in d.columns]]


def _agg_block(df: pd.DataFrame, cat_label: str, bin_edges: np.ndarray) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame()
    df = df.copy()
    df["pl_bin"] = pd.cut(df["price_level_dislocation"], bins=bin_edges,
                          include_lowest=True, duplicates="drop")
    rows = []
    for h in FINITE_HORIZONS:
        cc, rc = f"bounce_c_{h}", f"bounce_roi_{h}"
        for binv, g in df.groupby("pl_bin", observed=True):
            gc_ = g.dropna(subset=[cc])
            if len(gc_) == 0:
                continue
            gr_ = g.dropna(subset=[rc])
            n = len(gc_)
            low_support = (cat_label == "ALL" and n < MIN_BIN_SUPPORT) or \
                          (cat_label != "ALL" and n < MIN_BIN_SUPPORT)
            rows.append({
                "category": cat_label,
                "horizon": h,
                "price_level_bin_lo": float(binv.left),
                "price_level_bin_hi": float(binv.right),
                "price_level_bin_mid": float((binv.left + binv.right) / 2.0),
                "bounce_c_mean": float(gc_[cc].mean()),
                "bounce_c_median": float(gc_[cc].median()),
                "bounce_c_p25": float(gc_[cc].quantile(0.25)),
                "bounce_c_p75": float(gc_[cc].quantile(0.75)),
                "bounce_c_p90": float(gc_[cc].quantile(0.90)),
                "bounce_c_frac_positive": float((gc_[cc] > 0).mean()),
                "bounce_roi_mean": float(gr_[rc].mean()) if len(gr_) else np.nan,
                "bounce_roi_median": float(gr_[rc].median()) if len(gr_) else np.nan,
                "bounce_roi_p25": float(gr_[rc].quantile(0.25)) if len(gr_) else np.nan,
                "bounce_roi_p75": float(gr_[rc].quantile(0.75)) if len(gr_) else np.nan,
                "bounce_roi_p90": float(gr_[rc].quantile(0.90)) if len(gr_) else np.nan,
                "bounce_c_to_settlement_mean": float(
                    g["bounce_c_to_settlement"].mean())
                    if g["bounce_c_to_settlement"].notna().any() else np.nan,
                "bounce_c_to_settlement_median": float(
                    g["bounce_c_to_settlement"].median())
                    if g["bounce_c_to_settlement"].notna().any() else np.nan,
                "n_minutes": int(n),
                "n_tickers": int(gc_["ticker"].nunique()),
                "low_support": bool(low_support),
                "time_to_match_start_min_median": float(
                    g["time_to_match_start_min"].median()),
                "time_to_match_start_min_p25": float(
                    g["time_to_match_start_min"].quantile(0.25)),
                "time_to_match_start_min_p75": float(
                    g["time_to_match_start_min"].quantile(0.75)),
            })
    return pd.DataFrame(rows)


def build_surface(im: pd.DataFrame) -> pd.DataFrame:
    qs = np.linspace(0, 1, N_PRICE_BINS + 1)
    bin_edges = np.unique(im["price_level_dislocation"].quantile(qs).values)
    blocks = [_agg_block(im, "ALL", bin_edges)]
    for c in CATEGORIES:
        sub = im[im["category"] == c]
        if len(sub):
            blocks.append(_agg_block(sub, c, bin_edges))
    out = pd.concat([b for b in blocks if len(b)], ignore_index=True)
    return out


def gate1_cohort_parity(attempted_n, contributing_tickers, dropouts):
    # Phase-aware: parity against the ticker set ATTEMPTED this run (Phase-1
    # subsamples; Phase-2 = full cohort). Probe-confirmed defect: v0.1
    # hardcoded full cohort_n and false-failed every subsample.
    ok = (contributing_tickers + dropouts == attempted_n)
    return GateResult("G1_cohort_parity", ok,
                      0 if ok else abs(attempted_n - contributing_tickers - dropouts),
                      f"attempted={attempted_n} contributing={contributing_tickers} "
                      f"dropouts={dropouts}")


def gate2_in_match_purity(im):
    # Regime-purity ONLY. The v0.1 ttms<0 clause was a spec over-specification
    # inconsistent with the foundation's INCLUSIVE in_match boundary
    # (in_match := minute_ts >= match_start_ts; boundary minute is
    # regime==in_match ttms==0 by foundation design — probe /tmp/g2_probe.log:
    # 0 rows ttms>0). regime purity was already perfect (non_in_match=0).
    bad_regime = int((im["regime"] != "in_match").sum())
    return GateResult("G2_in_match_purity", bad_regime == 0, bad_regime,
                      f"non_in_match={bad_regime} "
                      f"(regime-purity only; ttms-boundary inclusive per foundation)")


def gate3_a38_firewall(surface):
    h = surface[(surface["category"] == "ALL") &
                (surface["horizon"] == HEADLINE_HORIZON)]
    fin = h["bounce_c_mean"].mean()
    diag = h["bounce_c_to_settlement_mean"].mean()
    ratio = (diag / fin) if (fin and fin > 0) else float("nan")
    ok = bool(np.isfinite(ratio) and ratio >= 1.3)
    return GateResult("G3_a38_firewall", ok, 0 if ok else 1,
                      f"finite30_mean={fin:.5f} diag_mean={diag:.5f} "
                      f"ratio={ratio:.3f} (must be >=1.3 — A38 saturation visible)")


def gate4_a39_dual_completeness(surface):
    cents_null = surface["bounce_c_mean"].isna()
    roi_null = surface["bounce_roi_mean"].isna()
    xor = int((cents_null ^ roi_null).sum())
    return GateResult("G4_a39_dual_completeness", xor == 0, xor,
                      f"rows_with_one_metric_missing={xor}")


def gate5_dislocation_domain(im):
    bad = int(((im["price_level_dislocation"] < 0) |
               (im["price_level_dislocation"] > 0.49)).sum())
    return GateResult("G5_dislocation_domain", bad == 0, bad,
                      f"out_of_[0,0.49]={bad}")


def gate6_bin_support(surface):
    all_rows = surface[surface["category"] == "ALL"]
    thin = int((all_rows["n_minutes"] < MIN_BIN_SUPPORT).sum())
    return GateResult("G6_bin_support", thin == 0, thin,
                      f"pooled_ALL_bins_below_{MIN_BIN_SUPPORT}={thin}")


def gate7_memory_bound(peak_rss_mb):
    ok = peak_rss_mb < 1700.0
    return GateResult("G7_memory_bound", ok, 0 if ok else 1,
                      f"peak_rss_mb={peak_rss_mb:.0f} (envelope 1700)")


def run_all_gates(on_disk_path, attempted_n, contributing, dropouts,
                  im_for_gates, peak_rss_mb):
    surface = pd.read_parquet(on_disk_path)
    return [
        gate1_cohort_parity(attempted_n, contributing, dropouts),
        gate2_in_match_purity(im_for_gates),
        gate3_a38_firewall(surface),
        gate4_a39_dual_completeness(surface),
        gate5_dislocation_domain(im_for_gates),
        gate6_bin_support(surface),
        gate7_memory_bound(peak_rss_mb),
    ]


def _peak_rss_mb() -> float:
    try:
        with open(f"/proc/{os.getpid()}/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0


def write_meta_sidecar(meta_path, result):
    meta = {
        "artifact": "inmatch_bounce_surface_v1/surface.parquet",
        "producer_commit": _producer_commit(),
        "spec": "docs/inmatch_bounce_surface_v1_spec.md",
        "rows_emitted": result.rows_emitted,
        "cohort_n": result.cohort_n,
        "in_match_minutes": result.in_match_minutes,
        "inputs_sha256": result.inputs_sha256,
        "output_sha256": result.output_sha256,
        "output_bytes": result.output_bytes,
        "gates_passed": all(g.passed for g in result.gate_results),
        "gate_detail": {g.name: {"passed": g.passed,
                                 "n_violations": g.n_violations,
                                 "detail": g.detail}
                        for g in result.gate_results},
        "run_started_at_et": result.run_started_at_et,
        "run_completed_at_et": result.run_completed_at_et,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")


def write_validation_report(report_path, surface, result):
    L = []
    L.append("# In-Match Bounce Surface v1 — Validation Report")
    L.append("")
    L.append(f"**Producer commit:** {_producer_commit()}")
    L.append(f"**Spec:** docs/inmatch_bounce_surface_v1_spec.md")
    L.append(f"**Run:** {result.run_started_at_et} -> {result.run_completed_at_et} ET")
    L.append(f"**Cohort N:** {result.cohort_n}  |  **In-match minutes:** "
             f"{result.in_match_minutes}  |  **Surface rows:** {result.rows_emitted}")
    L.append("")
    L.append("## Gate results")
    for g in result.gate_results:
        L.append(f"- **{g.name}**: {'PASS' if g.passed else 'FAIL'} "
                 f"(n_violations={g.n_violations}) — {g.detail}")
    L.append("")
    h = surface[(surface["category"] == "ALL") &
                (surface["horizon"] == HEADLINE_HORIZON)].sort_values(
                    "price_level_bin_mid")
    L.append("## Pooled headline curve (category=ALL, horizon=30min)")
    L.append("")
    L.append("| pl_mid | n_min | cents_mean | cents_med | roi_mean | roi_med "
             "| frac_pos | diag_to_settle_mean |")
    L.append("|--------|-------|------------|-----------|----------|---------"
             "|----------|---------------------|")
    for _, r in h.iterrows():
        L.append(f"| {r['price_level_bin_mid']:.4f} | {int(r['n_minutes'])} "
                 f"| {r['bounce_c_mean']:+.5f} | {r['bounce_c_median']:+.5f} "
                 f"| {r['bounce_roi_mean']:+.5f} | {r['bounce_roi_median']:+.5f} "
                 f"| {r['bounce_c_frac_positive']:.3f} "
                 f"| {r['bounce_c_to_settlement_mean']:+.5f} |")
    L.append("")
    if len(h) >= 4:
        cm = h["bounce_c_mean"].values
        rm = h["bounce_roi_mean"].values
        # v0.3: Spearman rank-correlation sign IS the monotone-direction
        # measure (the v0.2 rigid argmin/argmax<=1 positional heuristic
        # false-negatived whenever the characterized mid-axis trough/peak
        # was not in the first two bins -- same brittle pattern flagged on
        # the probe-2 classifier, C38/B20: read the curve, not the position).
        _bins = np.arange(len(cm))
        try:
            from scipy.stats import spearmanr
            _rho_c = float(spearmanr(_bins, cm).correlation)
            _rho_r = float(spearmanr(_bins, rm).correlation)
        except Exception:
            # numpy rank-correlation fallback (mirrors the probe-2 substitution)
            def _rankcorr(a, b):
                ra = pd.Series(a).rank().values
                rb = pd.Series(b).rank().values
                return float(np.corrcoef(ra, rb)[0, 1])
            _rho_c = _rankcorr(_bins, cm)
            _rho_r = _rankcorr(_bins, rm)
        _MONO = 0.5  # |rho| >= 0.5 => directional monotone trend
        c_dir = ("MONOTONE-DOWN" if _rho_c <= -_MONO
                 else "MONOTONE-UP" if _rho_c >= _MONO
                 else f"NON-MONOTONE(rho={_rho_c:+.3f})")
        r_dir = ("MONOTONE-UP" if _rho_r >= _MONO
                 else "MONOTONE-DOWN" if _rho_r <= -_MONO
                 else f"NON-MONOTONE(rho={_rho_r:+.3f})")
        # Inversion = cents and roi trend OPPOSITE signs (the load-bearing
        # A39 structure), judged by rho sign, not string-match.
        inverted = bool((_rho_c < 0 and _rho_r > 0) or
                        (_rho_c > 0 and _rho_r < 0))
        L.append(f"**Shape (measured, B20):** cents-curve {c_dir}; "
                 f"roi-curve {r_dir}; inversion present: {inverted}. "
                 f"(probe-1+2 expectation: cents-DOWN, roi-UP, inverted=True — "
                 f"MEASURED, not assumed.)")
        L.append("")
        roi_argmin = int(np.argmin(rm))
        L.append(f"**Second-order ROI shape (B20):** ROI minimum at bin index "
                 f"{roi_argmin}/{len(rm)-1}. Characterized, not baked in.")
        L.append("")
    L.append("## Per-category level shift (probe-2: covariate, NOT shape split)")
    for c in CATEGORIES:
        cr = surface[(surface["category"] == c) &
                     (surface["horizon"] == HEADLINE_HORIZON)]
        if len(cr):
            L.append(f"- {c}: cents_mean={cr['bounce_c_mean'].mean():+.5f} "
                     f"roi_mean={cr['bounce_roi_mean'].mean():+.5f} "
                     f"(n_bins={len(cr)}, low_support_bins="
                     f"{int(cr['low_support'].sum())})")
    L.append("")
    L.append("## SCALP-window sensitivity (5/15/30/60min, pooled ALL)")
    for hz in FINITE_HORIZONS:
        hh = surface[(surface["category"] == "ALL") &
                     (surface["horizon"] == hz)]
        if len(hh):
            L.append(f"- {hz}: cents_mean={hh['bounce_c_mean'].mean():+.5f} "
                     f"roi_mean={hh['bounce_roi_mean'].mean():+.5f} "
                     f"frac_pos={hh['bounce_c_frac_positive'].mean():.3f}")
    L.append("")
    L.append("_A38 note: bounce_c_to_settlement_* are DIAGNOSTIC-ONLY "
             "(gate G3 confirms saturation). Operational bounce uses ONLY "
             "the finite-horizon families._")
    report_path.write_text("\n".join(L) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="inmatch_bounce_surface_v1 producer")
    parser.add_argument("--phase", type=int, default=2, choices=[1, 2])
    parser.add_argument("--input-base", type=Path, default=DEFAULT_INPUT_BASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    started_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")
    n_profile_path = args.input_base / "n_profile_v1" / "n_profile.parquet"
    pmf_path = args.input_base / "per_minute_universe" / "per_minute_features.parquet"

    for p in (n_profile_path, pmf_path):
        if not p.exists():
            log.error(f"Missing required input: {p}")
            return 1

    inputs_sha = {
        "n_profile.parquet": sha256_of_file(n_profile_path),
        "per_minute_features.parquet": sha256_of_file(pmf_path),
    }
    log.info(f"Inputs: n_profile sha={inputs_sha['n_profile.parquet'][:12]} "
             f"pmf sha={inputs_sha['per_minute_features.parquet'][:12]}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    final_path = args.output_dir / DEFAULT_OUTPUT_FILE
    if final_path.exists():
        qdir = (args.input_base / "_quarantine" /
                f"pre_bounce_surface_{datetime.now(ET).strftime('%Y%m%dT%H%M%S')}")
        qdir.mkdir(parents=True, exist_ok=True)
        for f in args.output_dir.iterdir():
            if f.is_file():
                f.rename(qdir / f.name)
        log.info(f"Quarantined prior output -> {qdir}")

    log.info("Cohort screen from n_profile_v1 ...")
    cohort = select_cohort(n_profile_path)
    cohort_n = len(cohort)
    log.info(f"F35-reliable tier-1/2 live-era cohort: {cohort_n} N")
    log.info(f"cohort by category:\n{cohort['category'].value_counts()}")

    tickers = sorted(cohort["ticker"].unique())
    if args.phase == 1:
        per_cat = max(1, 1000 // len(CATEGORIES))
        samp = []
        cset = set(cohort["ticker"])
        for c in CATEGORIES:
            ct = sorted(cohort[cohort["category"] == c]["ticker"].unique())
            samp.extend(ct[:per_cat])
        tickers = [t for t in samp if t in cset][:1000]
        log.info(f"PHASE 1 stratified sanity: {len(tickers)} tickers")

    frames = []
    contributing = 0
    dropouts = 0
    for i, t in enumerate(tickers):
        if i > 0 and i % 1000 == 0:
            log.info(f"  pushdown {i}/{len(tickers)}  "
                     f"contributing={contributing} dropouts={dropouts}")
        if i > 0 and i % 200 == 0:
            gc.collect()
        d = per_ticker_in_match_minutes(pmf_path, t)
        if len(d) == 0:
            dropouts += 1
            continue
        contributing += 1
        frames.append(d)
        del d
    log.info(f"pushdown complete: contributing={contributing} "
             f"dropouts={dropouts} (cohort={cohort_n})")

    if not frames:
        log.error("No in-match minutes collected — STOP")
        return 1

    im = pd.concat(frames, ignore_index=True)
    del frames
    gc.collect()
    in_match_minutes = len(im)
    log.info(f"in-match minutes: {in_match_minutes} across "
             f"{im['ticker'].nunique()} tickers")

    log.info("Building band-free surface (pooled ALL + per-category covariate)...")
    surface = build_surface(im)
    log.info(f"surface rows: {len(surface)}")

    new_path = args.output_dir / (DEFAULT_OUTPUT_FILE + ".new")
    surface.to_parquet(new_path, index=False)
    peak_rss = _peak_rss_mb()
    log.info(f"wrote {new_path} (peak RSS {peak_rss:.0f} MB) — "
             f"reloading from disk for gate validation (C37)")

    gate_results = run_all_gates(new_path, len(tickers), contributing, dropouts,
                                 im, peak_rss)
    for g in gate_results:
        log.info(f"  {g.name}: {'PASS' if g.passed else 'FAIL'} "
                 f"n_violations={g.n_violations} {g.detail}")

    if not all(g.passed for g in gate_results):
        halt_path = args.output_dir / (
            f"halted_{datetime.now(ET).strftime('%Y%m%dT%H%M%S')}.log")
        try:
            lines = ["GATE FAILURE — surface NOT promoted (C37; .new retained)"]
            for g in gate_results:
                lines.append(f"  {g.name}: {'PASS' if g.passed else 'FAIL'} "
                             f"n_violations={g.n_violations} {g.detail}")
            halt_path.write_text("\n".join(lines) + "\n")
            log.error(f"Halt log written: {halt_path}")
        except Exception as e:
            log.error(f"Failed to write halt log: {type(e).__name__}: {e}")
        return 1

    log.info(f"All gates PASS — os.replace({new_path} -> {final_path})")
    os.replace(new_path, final_path)

    output_sha = sha256_of_file(final_path)
    output_bytes = final_path.stat().st_size
    completed_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")

    result = ProducerResult(
        rows_emitted=len(surface),
        cohort_n=cohort_n,
        in_match_minutes=in_match_minutes,
        gate_results=gate_results,
        output_sha256=output_sha,
        output_bytes=output_bytes,
        run_started_at_et=started_at,
        run_completed_at_et=completed_at,
        inputs_sha256=inputs_sha,
    )
    write_meta_sidecar(args.output_dir / DEFAULT_META_FILE, result)
    write_validation_report(args.output_dir / DEFAULT_REPORT_FILE,
                            pd.read_parquet(final_path), result)
    log.info(f"DONE. surface.parquet sha={output_sha} bytes={output_bytes} "
             f"rows={len(surface)} — all 7 gates PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
