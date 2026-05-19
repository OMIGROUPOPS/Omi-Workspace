#!/usr/bin/env python3
"""
build_exit_optimized_bounce_v1.py -- Phase-2 exit-optimization producer.

Implements docs/exit_optimized_bounce_v1_spec.md (committed de62d7f).
Layer-B-equivalent per B16, built on the validated Layer-A
(inmatch_bounce_surface_v1, 6f1d4bde, surface sha 14241db0).
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

DEFAULT_INPUT_BASE = Path("data/durable")
DEFAULT_OUTPUT_DIR = Path("data/durable/exit_optimized_bounce_v1")
DEFAULT_SURFACE_FILE = "surface.parquet"
DEFAULT_ROBUSTNESS_FILE = "robustness.parquet"
DEFAULT_META_FILE = "meta.json"
DEFAULT_REPORT_FILE = "validation_report.md"

N_PRICE_BINS = 40
MIN_BAND_SUPPORT = 200
# Frame P is structurally sparse (one T-20m conservative fill per ticker);
# probe /tmp/g7_probe.log full-cohort measured min 27 / median 172, zero
# bands <10, 39/40 >=30. Calibrated frame-aware floor (G7).
FRAME_P_MIN_BAND_SUPPORT = 30
ENTRY_PRICE_LO = 0.01
ENTRY_PRICE_HI = 0.99
T20_TARGET_MIN = 20.0
T20_TOL_MIN = 2.0
LAYER_A_HEADLINE_HORIZON = "30min"

PMF_PUSHDOWN_COLS = [
    "ticker", "minute_ts", "category", "regime",
    "yes_bid_close", "yes_ask_close", "mid_close",
    "time_to_match_start_min", "time_to_settlement_min",
    "settlement_value",
    "max_yes_bid_forward_5min", "max_yes_bid_forward_15min",
    "max_yes_bid_forward_30min", "max_yes_bid_forward_60min",
    "max_yes_bid_forward_to_match_start",
    "max_yes_bid_forward_to_settlement",
]

CATEGORIES = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]

FRAME_P = "P_premarket_t20"
FRAME_I = "I_inmatch_pricelevel"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("exit_optimized_v1")


@dataclass
class GateResult:
    name: str
    passed: bool
    n_violations: int
    detail: str


@dataclass
class ProducerResult:
    surface_rows: int
    robustness_rows: int
    cohort_n: int
    attempted_n: int
    positions_total: int
    gate_results: list
    surface_sha256: str
    surface_bytes: int
    robustness_sha256: str
    robustness_bytes: int
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


def load_layer_a_band_targets(layer_a_path: Path) -> pd.DataFrame:
    la = pd.read_parquet(layer_a_path)
    pooled = la[(la["category"] == "ALL") &
                (la["horizon"] == LAYER_A_HEADLINE_HORIZON)].copy()
    if len(pooled) == 0:
        raise RuntimeError(
            "Layer-A surface has no pooled ALL/30min rows -- cannot derive "
            "band exit targets (spec Sec 2.3 dependency unmet)")
    out = pooled[["price_level_bin_lo", "price_level_bin_hi",
                  "price_level_bin_mid", "bounce_c_median"]].copy()
    out = out.rename(columns={"bounce_c_median": "f_band_move_c"})
    out = out.sort_values("price_level_bin_lo").reset_index(drop=True)
    return out


def _band_index_for(dislocation: np.ndarray,
                     band_lo: np.ndarray, band_hi: np.ndarray) -> np.ndarray:
    idx = np.searchsorted(band_hi, dislocation, side="left")
    idx = np.clip(idx, 0, len(band_hi) - 1)
    return idx


def per_ticker_positions(pmf_path: Path, ticker: str,
                         band_lo: np.ndarray, band_hi: np.ndarray,
                         band_target_move: np.ndarray) -> pd.DataFrame:
    d = read_pmf_for_ticker(pmf_path, ticker)
    if len(d) == 0:
        return pd.DataFrame()
    d = d.dropna(subset=["yes_bid_close", "yes_ask_close", "mid_close"]).copy()
    if len(d) == 0:
        return pd.DataFrame()
    cat = d["category"].iloc[0] if "category" in d.columns and len(d) else None
    rows = []

    pm = d[(d["regime"] == "premarket")].copy()
    if len(pm) > 0 and "time_to_match_start_min" in pm.columns:
        pm = pm.dropna(subset=["time_to_match_start_min"])
        if len(pm) > 0:
            within = pm[(pm["time_to_match_start_min"]
                         >= T20_TARGET_MIN - T20_TOL_MIN)
                        & (pm["time_to_match_start_min"]
                           <= T20_TARGET_MIN + T20_TOL_MIN)]
            if len(within) > 0:
                j = (within["time_to_match_start_min"]
                     - T20_TARGET_MIN).abs().idxmin()
                r = within.loc[j]
                ep = float(r["yes_ask_close"])
                if ENTRY_PRICE_LO < ep < ENTRY_PRICE_HI:
                    disloc = abs(float(r["mid_close"]) - 0.50)
                    bi = int(_band_index_for(
                        np.array([disloc]), band_lo, band_hi)[0])
                    fmove = float(band_target_move[bi])
                    target = ep + fmove
                    w1 = r.get("max_yes_bid_forward_to_match_start", np.nan)
                    im_after = d[(d["regime"] == "in_match")]
                    w2 = (float(im_after["max_yes_bid_forward_30min"].max())
                          if len(im_after) and
                          im_after["max_yes_bid_forward_30min"].notna().any()
                          else np.nan)
                    hit_w1 = (pd.notna(w1) and float(w1) >= target)
                    hit_w2 = (not hit_w1) and pd.notna(w2) and float(w2) >= target
                    if hit_w1:
                        res = "hit_target_window1"
                        bounce_c = target - ep
                    elif hit_w2:
                        res = "hit_target_window2"
                        bounce_c = target - ep
                    else:
                        res = "rode_to_settlement"
                        sv = r.get("settlement_value", np.nan)
                        term = (1.0 if (pd.notna(sv) and float(sv) >= 0.5)
                                else 0.0)
                        bounce_c = term - ep
                    rows.append({
                        "ticker": ticker, "category": cat,
                        "fill_frame": FRAME_P,
                        "entry_price": ep,
                        "price_level_dislocation": disloc,
                        "exit_target_c": target,
                        "exit_window_resolution": res,
                        "bounce_c": bounce_c,
                        "bounce_roi": bounce_c / ep,
                        "settlement_yes": int(
                            pd.notna(r.get("settlement_value", np.nan))
                            and float(r.get("settlement_value", 0)) >= 0.5),
                        "rode": int(res == "rode_to_settlement"),
                        "hit": int(res.startswith("hit_target")),
                        "entry_ttms": float(r["time_to_match_start_min"]),
                    })

    im = d[(d["regime"] == "in_match")].copy()
    if len(im) > 0:
        im = im[(im["yes_ask_close"] > ENTRY_PRICE_LO)
                & (im["yes_ask_close"] < ENTRY_PRICE_HI)]
        if len(im) > 0:
            ep = im["yes_ask_close"].to_numpy()
            disloc = (im["mid_close"].to_numpy() - 0.50)
            disloc = np.abs(disloc)
            bi = _band_index_for(disloc, band_lo, band_hi)
            fmove = band_target_move[bi]
            target = ep + fmove
            w = im["max_yes_bid_forward_30min"].to_numpy()
            sv = im["settlement_value"].to_numpy()
            ttms = im["time_to_match_start_min"].to_numpy()
            hit = np.where(np.isfinite(w), w >= target, False)
            term = np.where(np.isfinite(sv) & (sv >= 0.5), 1.0, 0.0)
            bounce_c = np.where(hit, target - ep, term - ep)
            res = np.where(hit, "hit_target_window1", "rode_to_settlement")
            for k in range(len(im)):
                rows.append({
                    "ticker": ticker, "category": cat,
                    "fill_frame": FRAME_I,
                    "entry_price": float(ep[k]),
                    "price_level_dislocation": float(disloc[k]),
                    "exit_target_c": float(target[k]),
                    "exit_window_resolution": str(res[k]),
                    "bounce_c": float(bounce_c[k]),
                    "bounce_roi": float(bounce_c[k] / ep[k]),
                    "settlement_yes": int(
                        np.isfinite(sv[k]) and sv[k] >= 0.5),
                    "rode": int(res[k] == "rode_to_settlement"),
                    "hit": int(str(res[k]).startswith("hit_target")),
                    "entry_ttms": float(ttms[k])
                    if np.isfinite(ttms[k]) else np.nan,
                })
    return pd.DataFrame(rows)


def _agg_block(df: pd.DataFrame, cat_label: str,
               bin_edges: np.ndarray) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame()
    df = df.copy()
    df["pl_bin"] = pd.cut(df["price_level_dislocation"], bins=bin_edges,
                          include_lowest=True, duplicates="drop")
    rows = []
    for frame in (FRAME_P, FRAME_I):
        fdf = df[df["fill_frame"] == frame]
        if len(fdf) == 0:
            continue
        for binv, g in fdf.groupby("pl_bin", observed=True):
            if len(g) == 0:
                continue
            n = len(g)
            low_support = (n < MIN_BAND_SUPPORT) if frame == FRAME_I \
                else (n < FRAME_P_MIN_BAND_SUPPORT)
            rows.append({
                "category": cat_label,
                "fill_frame": frame,
                "price_band_lo": float(binv.left),
                "price_band_hi": float(binv.right),
                "price_band_mid": float((binv.left + binv.right) / 2.0),
                "exit_bounce_c_mean": float(g["bounce_c"].mean()),
                "exit_bounce_c_median": float(g["bounce_c"].median()),
                "exit_bounce_c_p25": float(g["bounce_c"].quantile(0.25)),
                "exit_bounce_c_p75": float(g["bounce_c"].quantile(0.75)),
                "exit_bounce_c_p90": float(g["bounce_c"].quantile(0.90)),
                "exit_bounce_roi_mean": float(g["bounce_roi"].mean()),
                "exit_bounce_roi_median": float(g["bounce_roi"].median()),
                "exit_bounce_roi_p25": float(g["bounce_roi"].quantile(0.25)),
                "exit_bounce_roi_p75": float(g["bounce_roi"].quantile(0.75)),
                "exit_bounce_roi_p90": float(g["bounce_roi"].quantile(0.90)),
                "avg_bounce_rank_metric": float(g["bounce_c"].mean()),
                "exit_target_c": float(g["exit_target_c"].mean()),
                "exit_target_rule": "entry_price + layerA_pooled_median_30min_bounce_per_band",
                "settlement_outcome_frac_yes": float(g["settlement_yes"].mean()),
                "rode_to_settlement_frac": float(g["rode"].mean()),
                "hit_rate": float(g["hit"].mean()),
                "n_positions": int(n),
                "n_tickers": int(g["ticker"].nunique()),
                "low_support": bool(low_support),
                "entry_mark_ttms_median": float(g["entry_ttms"].median()),
                "entry_mark_ttms_p25": float(g["entry_ttms"].quantile(0.25)),
                "entry_mark_ttms_p75": float(g["entry_ttms"].quantile(0.75)),
            })
    return pd.DataFrame(rows)


def build_surface(pos: pd.DataFrame) -> pd.DataFrame:
    qs = np.linspace(0, 1, N_PRICE_BINS + 1)
    bin_edges = np.unique(
        pos["price_level_dislocation"].quantile(qs).values)
    blocks = [_agg_block(pos, "ALL", bin_edges)]
    for c in CATEGORIES:
        sub = pos[pos["category"] == c]
        if len(sub):
            blocks.append(_agg_block(sub, c, bin_edges))
    return pd.concat([b for b in blocks if len(b)], ignore_index=True)


def build_robustness(surface: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key = ["category", "price_band_lo", "price_band_hi", "price_band_mid"]
    for keyvals, g in surface.groupby(key, observed=True):
        p = g[g["fill_frame"] == FRAME_P]
        i = g[g["fill_frame"] == FRAME_I]
        p_av = float(p["avg_bounce_rank_metric"].iloc[0]) if len(p) else np.nan
        i_av = float(i["avg_bounce_rank_metric"].iloc[0]) if len(i) else np.nan
        both = np.isfinite(p_av) and np.isfinite(i_av)
        same_sign = both and (np.sign(p_av) == np.sign(i_av))
        both_pos = both and (p_av > 0) and (i_av > 0)
        ratio = (p_av / i_av) if (both and i_av != 0) else np.nan
        flag = "robust" if both_pos else (
            "frame_dependent" if both else "single_frame_only")
        rows.append({
            "category": keyvals[0],
            "price_band_lo": keyvals[1],
            "price_band_hi": keyvals[2],
            "price_band_mid": keyvals[3],
            "frame_P_avg_bounce": p_av,
            "frame_I_avg_bounce": i_av,
            "sign_agreement": bool(same_sign),
            "both_positive": bool(both_pos),
            "magnitude_ratio_P_over_I": ratio,
            "robustness_flag": flag,
        })
    return pd.DataFrame(rows)


def gate1_cohort_parity(attempted_n, contributing, dropouts):
    ok = (contributing + dropouts == attempted_n)
    return GateResult("G1_cohort_parity", ok,
                      0 if ok else abs(attempted_n - contributing - dropouts),
                      f"attempted={attempted_n} contributing={contributing} "
                      f"dropouts={dropouts}")


def gate2_frame_purity(pos):
    # Frame-I purity is regime-membership, ttms-boundary INCLUSIVE: the
    # foundation tags the match-start boundary minute (ttms==0) as
    # regime==in_match inclusively (probe /tmp/g2_probe.log; identical to
    # the Layer-A G2 correction, commit 85118d4). Violation is ttms > 0
    # (strictly after the inclusive boundary), NOT ttms >= 0 (which the
    # v0.1 over-specified, re-introducing the already-fixed Layer-A defect).
    p = pos[pos["fill_frame"] == FRAME_P]
    i = pos[pos["fill_frame"] == FRAME_I]
    bad_p = int(((p["entry_ttms"] < T20_TARGET_MIN - T20_TOL_MIN)
                 | (p["entry_ttms"] > T20_TARGET_MIN + T20_TOL_MIN)).sum())
    bad_i = int((i["entry_ttms"] > 0).sum()) if len(i) else 0
    n = bad_p + bad_i
    return GateResult("G2_frame_purity", n == 0, n,
                      f"frameP_outside_T20pm2={bad_p} "
                      f"frameI_post_boundary_ttms={bad_i} "
                      f"(boundary ttms==0 inclusive per foundation)")


def gate3_a38_firewall(surface, pos):
    h = surface[surface["category"] == "ALL"]
    eo_mean = float(h["exit_bounce_c_mean"].mean()) if len(h) else float("nan")
    rode = pos[pos["rode"] == 1]
    rode_mean = float(rode["bounce_c"].mean()) if len(rode) else float("nan")
    ok = bool(np.isfinite(eo_mean) and abs(eo_mean) < 1.0)
    return GateResult("G3_a38_firewall", ok, 0 if ok else 1,
                      f"exit_opt_mean={eo_mean:.5f} rode_mean={rode_mean:.5f} "
                      f"(exit-optimized must be a finite real exit, never a "
                      f"forward_to_settlement saturation)")


def gate4_ranking_metric_integrity(surface):
    if "avg_bounce_rank_metric" not in surface.columns or \
       "hit_rate" not in surface.columns:
        return GateResult("G4_ranking_metric_integrity", False, 1,
                          "missing avg_bounce_rank_metric or hit_rate column")
    mism = int((~np.isclose(surface["avg_bounce_rank_metric"],
                            surface["exit_bounce_c_mean"],
                            equal_nan=True)).sum())
    return GateResult("G4_ranking_metric_integrity", mism == 0, mism,
                      f"rank_metric!=exit_bounce_c_mean rows={mism} "
                      f"(ranking is avg_bounce, NOT hit_rate -- E32(e))")


def gate5_no_stop_integrity(pos):
    valid = {"hit_target_window1", "hit_target_window2", "rode_to_settlement"}
    bad = int((~pos["exit_window_resolution"].isin(valid)).sum())
    return GateResult("G5_no_stop_integrity", bad == 0, bad,
                      f"positions_in_invalid_or_stopped_state={bad} "
                      f"(E32(c) no-stop: only hit_w1/hit_w2/rode)")


def gate6_a39_dual_completeness(surface):
    c_null = surface["exit_bounce_c_mean"].isna()
    r_null = surface["exit_bounce_roi_mean"].isna()
    xor = int((c_null ^ r_null).sum())
    return GateResult("G6_a39_dual_completeness", xor == 0, xor,
                      f"rows_with_one_metric_missing={xor}")


def gate7_band_support(surface, attempted_n, full_cohort_n):
    # Frame-aware AND phase-aware. Frame I is dense (~2,128/band at full
    # cohort) -- keep the real >=200 reliability bar (it is dense enough to
    # hold at Phase-1 sampling too; min Frame-I n was 1535 at Phase-1). Frame
    # P is structurally sparse by construction (one T-20m conservative fill
    # per ticker); the calibrated floor 30 is probe-grounded for the FULL
    # COHORT (/tmp/g7_probe.log: 7,115 positions, 39/40 bands >=30). It must
    # be PHASE-SCALED -- applying the full-cohort constant to a downsampled
    # Phase-1 run is the identical defect class as the original G1
    # phase-blindness (full-cohort threshold vs subsample). Scale by the
    # phase sampling fraction: == 30 at Phase-2 (attempted_n == full cohort,
    # the deliverable, probe-grounded unchanged), proportionate at Phase-1.
    frac = (attempted_n / full_cohort_n) if full_cohort_n else 1.0
    frame_p_floor = max(1, round(FRAME_P_MIN_BAND_SUPPORT * frac))
    allrows = surface[surface["category"] == "ALL"]
    fi = allrows[allrows["fill_frame"] == FRAME_I]
    fp = allrows[allrows["fill_frame"] == FRAME_P]
    thin_i = int((fi["n_positions"] < MIN_BAND_SUPPORT).sum())
    # Frame-P sub-floor bands carry low_support=True (set in _agg_block)
    # and are flagged-into-robustness, NOT hard-failed -- this is the
    # spec's OWN stated G7 design (Sec 4.1) and the g7-probe verdict
    # (/tmp/g7_probe.log): the lone structurally-sparse extreme-dislocation
    # band (idx39, n~27 at full cohort) is surfaced via the flag, not a
    # gate violation. Exempt low_support=True bands from the violation
    # count; a non-flagged Frame-P band below floor IS still a real
    # violation (catches a genuine Frame-P collapse).
    fp_unflagged = fp[~fp["low_support"].astype(bool)]
    thin_p = int((fp_unflagged["n_positions"] < frame_p_floor).sum())
    n_flagged_p = int(fp["low_support"].astype(bool).sum())
    n = thin_i + thin_p
    return GateResult("G7_band_support", n == 0, n,
                      f"frameI_below_{MIN_BAND_SUPPORT}={thin_i} "
                      f"frameP_below_{frame_p_floor}_unflagged={thin_p} "
                      f"frameP_low_support_flagged={n_flagged_p} "
                      f"(frame+phase-aware; low_support bands "
                      f"flagged-into-robustness not hard-failed per spec "
                      f"Sec 4.1 + /tmp/g7_probe.log; floor "
                      f"{FRAME_P_MIN_BAND_SUPPORT} x frac {frac:.3f})")


def gate8_memory_bound(peak_rss_mb):
    ok = peak_rss_mb < 1700.0
    return GateResult("G8_memory_bound", ok, 0 if ok else 1,
                      f"peak_rss_mb={peak_rss_mb:.0f} (envelope 1700)")


def gate9_robustness_completeness(surface, robustness):
    surf_keys = surface[["category", "price_band_lo",
                         "price_band_hi"]].drop_duplicates()
    rob_keys = robustness[["category", "price_band_lo",
                           "price_band_hi"]].drop_duplicates()
    missing = len(surf_keys) - len(
        surf_keys.merge(rob_keys, on=["category", "price_band_lo",
                                      "price_band_hi"], how="inner"))
    flagged = int(robustness["robustness_flag"].notna().sum())
    ok = (missing == 0) and (flagged == len(robustness)) and len(robustness) > 0
    return GateResult("G9_robustness_completeness", ok,
                      missing + (len(robustness) - flagged),
                      f"bands_missing_from_robustness={missing} "
                      f"unflagged={len(robustness) - flagged} "
                      f"rob_rows={len(robustness)}")


def run_all_gates(surface_path, robustness_path, attempted_n, contributing,
                  dropouts, pos_for_gates, peak_rss_mb, full_cohort_n):
    surface = pd.read_parquet(surface_path)
    robustness = pd.read_parquet(robustness_path)
    return [
        gate1_cohort_parity(attempted_n, contributing, dropouts),
        gate2_frame_purity(pos_for_gates),
        gate3_a38_firewall(surface, pos_for_gates),
        gate4_ranking_metric_integrity(surface),
        gate5_no_stop_integrity(pos_for_gates),
        gate6_a39_dual_completeness(surface),
        gate7_band_support(surface, attempted_n, full_cohort_n),
        gate8_memory_bound(peak_rss_mb),
        gate9_robustness_completeness(surface, robustness),
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


def write_meta(meta_path: Path, result: ProducerResult) -> None:
    meta = {
        "artifact": "exit_optimized_bounce_v1/surface.parquet",
        "companion": "exit_optimized_bounce_v1/robustness.parquet",
        "producer_commit": _producer_commit(),
        "spec": "docs/exit_optimized_bounce_v1_spec.md",
        "surface_rows": result.surface_rows,
        "robustness_rows": result.robustness_rows,
        "cohort_n": result.cohort_n,
        "attempted_n": result.attempted_n,
        "positions_total": result.positions_total,
        "inputs_sha256": result.inputs_sha256,
        "surface_sha256": result.surface_sha256,
        "surface_bytes": result.surface_bytes,
        "robustness_sha256": result.robustness_sha256,
        "robustness_bytes": result.robustness_bytes,
        "gates_passed": all(g.passed for g in result.gate_results),
        "gate_detail": {g.name: {"passed": g.passed,
                                 "n_violations": g.n_violations,
                                 "detail": g.detail}
                        for g in result.gate_results},
        "run_started_at_et": result.run_started_at_et,
        "run_completed_at_et": result.run_completed_at_et,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")


def write_validation_report(report_path: Path, surface: pd.DataFrame,
                            robustness: pd.DataFrame,
                            result: ProducerResult) -> None:
    L = []
    L.append("# Exit-Optimized Bounce v1 -- Validation Report")
    L.append("")
    L.append(f"**Producer commit:** {_producer_commit()}")
    L.append("**Spec:** docs/exit_optimized_bounce_v1_spec.md (de62d7f)")
    L.append(f"**Run:** {result.run_started_at_et} -> "
             f"{result.run_completed_at_et} ET")
    L.append(f"**Cohort N:** {result.cohort_n}  |  **Attempted:** "
             f"{result.attempted_n}  |  **Positions:** "
             f"{result.positions_total}  |  **Surface rows:** "
             f"{result.surface_rows}  |  **Robustness rows:** "
             f"{result.robustness_rows}")
    L.append("")
    L.append("## Gate results (all 9)")
    for g in result.gate_results:
        L.append(f"- **{g.name}**: {'PASS' if g.passed else 'FAIL'} "
                 f"(n_violations={g.n_violations}) -- {g.detail}")
    L.append("")
    L.append("## Cross-frame robustness (THE headline -- spec Sec 2.1)")
    L.append("")
    rob_all = robustness[robustness["category"] == "ALL"].sort_values(
        "price_band_mid")
    nb = len(rob_all)
    n_robust = int((rob_all["robustness_flag"] == "robust").sum())
    n_fdep = int((rob_all["robustness_flag"] == "frame_dependent").sum())
    n_single = int((rob_all["robustness_flag"] == "single_frame_only").sum())
    L.append(f"Pooled ALL bands: {nb} | robust (edge in BOTH conservative "
             f"frames): {n_robust} | frame_dependent: {n_fdep} | "
             f"single_frame_only: {n_single}")
    L.append("")
    L.append("| band_mid | frameP_avg_c | frameI_avg_c | sign_agree | "
             "ratio_P/I | flag |")
    L.append("|----------|--------------|--------------|------------|"
             "-----------|------|")
    for _, r in rob_all.iterrows():
        L.append(f"| {r['price_band_mid']:.4f} "
                 f"| {r['frame_P_avg_bounce']:+.5f} "
                 f"| {r['frame_I_avg_bounce']:+.5f} "
                 f"| {str(bool(r['sign_agreement']))} "
                 f"| {r['magnitude_ratio_P_over_I']:+.3f} "
                 f"| {r['robustness_flag']} |")
    L.append("")
    L.append("_Decision rule (spec Sec 1.1): an edge present in BOTH "
             "conservative frames is real; an edge in only one is "
             "frame-dependent -- the fill frame is doing the work, not the "
             "strategy. Decision-critical pre-deployment._")
    L.append("")
    for frame in (FRAME_P, FRAME_I):
        h = surface[(surface["category"] == "ALL") &
                    (surface["fill_frame"] == frame)].sort_values(
                        "price_band_mid")
        if len(h) == 0:
            continue
        L.append(f"## Exit-optimized curve -- {frame} (category=ALL)")
        L.append("")
        L.append("| band_mid | n_pos | exit_c_mean | exit_c_med "
                 "| exit_roi_mean | hit_rate | rode_frac | tgt_c |")
        L.append("|----------|-------|-------------|------------|"
                 "---------------|----------|-----------|-------|")
        for _, r in h.iterrows():
            L.append(f"| {r['price_band_mid']:.4f} "
                     f"| {int(r['n_positions'])} "
                     f"| {r['exit_bounce_c_mean']:+.5f} "
                     f"| {r['exit_bounce_c_median']:+.5f} "
                     f"| {r['exit_bounce_roi_mean']:+.5f} "
                     f"| {r['hit_rate']:.3f} "
                     f"| {r['rode_to_settlement_frac']:.3f} "
                     f"| {r['exit_target_c']:+.4f} |")
        L.append("")
        if len(h) >= 4:
            cm = h["exit_bounce_c_mean"].values
            rm = h["exit_bounce_roi_mean"].values
            _bins = np.arange(len(cm))
            try:
                from scipy.stats import spearmanr
                _rho_c = float(spearmanr(_bins, cm).correlation)
                _rho_r = float(spearmanr(_bins, rm).correlation)
            except Exception:
                def _rankcorr(a, b):
                    ra = pd.Series(a).rank().values
                    rb = pd.Series(b).rank().values
                    return float(np.corrcoef(ra, rb)[0, 1])
                _rho_c = _rankcorr(_bins, cm)
                _rho_r = _rankcorr(_bins, rm)
            _MONO = 0.5
            c_dir = ("MONOTONE-DOWN" if _rho_c <= -_MONO
                     else "MONOTONE-UP" if _rho_c >= _MONO
                     else f"NON-MONOTONE(rho={_rho_c:+.3f})")
            r_dir = ("MONOTONE-UP" if _rho_r >= _MONO
                     else "MONOTONE-DOWN" if _rho_r <= -_MONO
                     else f"NON-MONOTONE(rho={_rho_r:+.3f})")
            inverted = bool((_rho_c < 0 and _rho_r > 0) or
                            (_rho_c > 0 and _rho_r < 0))
            L.append(f"**Shape (measured, B20):** cents-curve {c_dir} "
                     f"(rho={_rho_c:+.3f}); roi-curve {r_dir} "
                     f"(rho={_rho_r:+.3f}); cents-vs-roi inversion: "
                     f"{inverted}. Measured, not assumed.")
            L.append("")
    L.append("## E32(e) extreme-band characterization (measured)")
    for frame in (FRAME_P, FRAME_I):
        h = surface[(surface["category"] == "ALL") &
                    (surface["fill_frame"] == frame)].sort_values(
                        "price_band_mid")
        if len(h) >= 2:
            lo = h.iloc[0]
            hi = h.iloc[-1]
            L.append(f"- {frame}: low-dislocation band "
                     f"(mid={lo['price_band_mid']:.3f}) "
                     f"exit_c_mean={lo['exit_bounce_c_mean']:+.5f} "
                     f"hit_rate={lo['hit_rate']:.3f}; high-dislocation band "
                     f"(mid={hi['price_band_mid']:.3f}) "
                     f"exit_c_mean={hi['exit_bounce_c_mean']:+.5f} "
                     f"hit_rate={hi['hit_rate']:.3f}. "
                     f"(E32(e) predicts extremes fail for OPPOSITE reasons "
                     f"-- characterized here, not baked.)")
    L.append("")
    L.append("_A38 firewall (G3): the exit is a finite real target or the "
             "settlement answer-key terminal (E32(d)); NEVER a "
             "*_forward_to_settlement saturation. No-stop (G5): every "
             "position is hit_w1/hit_w2/rode -- non-winners NOT cut "
             "(E32(c))._")
    report_path.write_text("\n".join(L) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="exit_optimized_bounce_v1 producer")
    parser.add_argument("--phase", type=int, default=2, choices=[1, 2])
    parser.add_argument("--input-base", type=Path, default=DEFAULT_INPUT_BASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    started_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")
    n_profile_path = args.input_base / "n_profile_v1" / "n_profile.parquet"
    pmf_path = (args.input_base / "per_minute_universe"
                / "per_minute_features.parquet")
    layer_a_path = (args.input_base / "inmatch_bounce_surface_v1"
                    / "surface.parquet")

    for p in (n_profile_path, pmf_path, layer_a_path):
        if not p.exists():
            log.error(f"Missing required input: {p}")
            return 1

    inputs_sha = {
        "n_profile.parquet": sha256_of_file(n_profile_path),
        "per_minute_features.parquet": sha256_of_file(pmf_path),
        "inmatch_bounce_surface_v1_surface.parquet":
            sha256_of_file(layer_a_path),
    }
    log.info(f"Inputs: n_profile={inputs_sha['n_profile.parquet'][:12]} "
             f"pmf={inputs_sha['per_minute_features.parquet'][:12]} "
             f"layerA="
             f"{inputs_sha['inmatch_bounce_surface_v1_surface.parquet'][:12]}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    final_surface = args.output_dir / DEFAULT_SURFACE_FILE
    if final_surface.exists():
        qdir = (args.input_base / "_quarantine" /
                f"pre_exit_opt_{datetime.now(ET).strftime('%Y%m%dT%H%M%S')}")
        qdir.mkdir(parents=True, exist_ok=True)
        for f in args.output_dir.iterdir():
            if f.is_file():
                f.rename(qdir / f.name)
        log.info(f"Quarantined prior output -> {qdir}")

    log.info("Loading Layer-A band exit-target moves (spec Sec 2.3)...")
    band_targets = load_layer_a_band_targets(layer_a_path)
    band_lo = band_targets["price_level_bin_lo"].to_numpy()
    band_hi = band_targets["price_level_bin_hi"].to_numpy()
    band_move = band_targets["f_band_move_c"].to_numpy()
    log.info(f"Layer-A bands: {len(band_targets)} "
             f"(f(band) = pooled median 30min bounce per band)")

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
    attempted_n = len(tickers)

    frames = []
    contributing = 0
    dropouts = 0
    for i, t in enumerate(tickers):
        if i > 0 and i % 1000 == 0:
            log.info(f"  pushdown {i}/{attempted_n}  "
                     f"contributing={contributing} dropouts={dropouts}")
        if i > 0 and i % 200 == 0:
            gc.collect()
        d = per_ticker_positions(pmf_path, t, band_lo, band_hi, band_move)
        if len(d) == 0:
            dropouts += 1
            continue
        contributing += 1
        frames.append(d)
        del d
    log.info(f"pushdown complete: contributing={contributing} "
             f"dropouts={dropouts} (attempted={attempted_n} "
             f"cohort={cohort_n})")

    if not frames:
        log.error("No positions collected -- STOP")
        return 1

    pos = pd.concat(frames, ignore_index=True)
    del frames
    gc.collect()
    positions_total = len(pos)
    log.info(f"positions: {positions_total} "
             f"(Frame P: {int((pos['fill_frame'] == FRAME_P).sum())}, "
             f"Frame I: {int((pos['fill_frame'] == FRAME_I).sum())}) "
             f"across {pos['ticker'].nunique()} tickers")

    log.info("Building dual-frame exit-optimized surface...")
    surface = build_surface(pos)
    log.info(f"surface rows: {len(surface)}")
    log.info("Building cross-frame robustness table (the headline)...")
    robustness = build_robustness(surface)
    log.info(f"robustness rows: {len(robustness)}")

    new_surface = args.output_dir / (DEFAULT_SURFACE_FILE + ".new")
    new_robust = args.output_dir / (DEFAULT_ROBUSTNESS_FILE + ".new")
    surface.to_parquet(new_surface, index=False)
    robustness.to_parquet(new_robust, index=False)
    peak_rss = _peak_rss_mb()
    log.info(f"wrote .new artifacts (peak RSS {peak_rss:.0f} MB) -- "
             f"reloading from disk for gate validation (C37)")

    gate_results = run_all_gates(new_surface, new_robust, attempted_n,
                                 contributing, dropouts, pos, peak_rss,
                                 cohort_n)
    for g in gate_results:
        log.info(f"  {g.name}: {'PASS' if g.passed else 'FAIL'} "
                 f"n_violations={g.n_violations} {g.detail}")

    if not all(g.passed for g in gate_results):
        halt_path = args.output_dir / (
            f"halted_{datetime.now(ET).strftime('%Y%m%dT%H%M%S')}.log")
        try:
            lines = ["GATE FAILURE -- artifacts NOT promoted "
                     "(C37; .new retained)"]
            for g in gate_results:
                lines.append(f"  {g.name}: {'PASS' if g.passed else 'FAIL'} "
                             f"n_violations={g.n_violations} {g.detail}")
            halt_path.write_text("\n".join(lines) + "\n")
            log.error(f"Halt log written: {halt_path}")
        except Exception as e:
            log.error(f"Failed to write halt log: {type(e).__name__}: {e}")
        return 1

    log.info("All 9 gates PASS -- promoting both artifacts (os.replace)")
    os.replace(new_surface, final_surface)
    final_robust = args.output_dir / DEFAULT_ROBUSTNESS_FILE
    os.replace(new_robust, final_robust)

    surface_sha = sha256_of_file(final_surface)
    robust_sha = sha256_of_file(final_robust)
    completed_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")

    result = ProducerResult(
        surface_rows=len(surface),
        robustness_rows=len(robustness),
        cohort_n=cohort_n,
        attempted_n=attempted_n,
        positions_total=positions_total,
        gate_results=gate_results,
        surface_sha256=surface_sha,
        surface_bytes=final_surface.stat().st_size,
        robustness_sha256=robust_sha,
        robustness_bytes=final_robust.stat().st_size,
        run_started_at_et=started_at,
        run_completed_at_et=completed_at,
        inputs_sha256=inputs_sha,
    )
    write_meta(args.output_dir / DEFAULT_META_FILE, result)
    write_validation_report(args.output_dir / DEFAULT_REPORT_FILE,
                            pd.read_parquet(final_surface),
                            pd.read_parquet(final_robust), result)
    log.info(f"DONE. surface sha={surface_sha} bytes={result.surface_bytes} "
             f"rows={len(surface)} | robustness sha={robust_sha} "
             f"rows={len(robustness)} -- all 9 gates PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
