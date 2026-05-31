"""
chart_common.py — shared data layer for the ATP_MAIN exit-strategy chart producers.

ONE definition of "cell", ONE reach/fill engine, used by all three producers
(build_chart_sand_overlap.py, build_chart_mirror_outlook.py, build_chart_pyramid.py)
so the geometry, the overlap proof, and the fill numbers are all measured the same way.

================================================================================
INSTRUMENT CONTRACT  (read before changing anything)
================================================================================
Cost-basis cell c
    c = round(100 * yes_bid_close).  This is the bid you LAY and get filled at,
    so it is the cost basis of the position. It is the same anchor the project's
    existing `bounce_*` / excursion columns are measured from
    (verified: max_yes_bid_forward >= yes_bid_close in 99.86% of ATP_MAIN rows).
    yes_bid_close is always populated (0 nulls), so every minute is a candidate
    entry observation — consistent with how the per-minute excursion was computed.
    Used only to LABEL the entry; never used to detect a fill.

Reach / fill  (CORRECTED — this overrides CHART_DEFINITIONS_VERIFIED.md)
    A resting limit sell at c+X is FILLED iff any STRICTLY-FORWARD minute's
    highest TRADED price (price_high) is >= (c+X)/100.
        fill(c, X) := max(price_high over future minutes of this ticker) >= (c+X)/100
    - price_high is the last-traded intraminute high. A limit sell executes at its
      price or better when the market trades THROUGH it, so taking the forward MAX
      is automatically skip/gap-inclusive: a print jumping from below c+X to above
      it is a FILL, not a miss.
    - The ~67% of minutes with NaN price_high are genuine no-trade non-events
      (nothing to fill against) and are simply absent from the forward max — they
      are NOT patched with a quote.

BANNED forward instruments (each has produced a false result on this project):
    yes_bid_high      quoted high bid can be posted & pulled without trading -> false positive
    yes_bid_close     close-of-minute lags the intraminute trade            -> false negative
    price_close       same lag                                              -> false negative
    mid_close         phantom midpoint on no-trade minutes                  -> false positive
The OLD headline ("excursion+10 >= 50% in 85/90 cells") was computed on the
quoted yes_bid_high forward max. compute_forward_max(df, 'yes_bid_high') reproduces
that OLD instrument ONLY so the producers can report corrected-vs-old side by side.
================================================================================
"""

from __future__ import annotations
import glob
import os
import numpy as np
import pandas as pd

# Cell universe (cost-basis cents). 95-99 are the lock/ceiling, not entry cells.
CELL_MIN = 5
CELL_MAX = 94
LOCK = 99  # exits reach up to here

# Cost-basis bands used by the mirror/pyramid producers.
BANDS = [
    ("deep-underdog", 5, 20),
    ("slight-underdog", 21, 40),
    ("even", 41, 60),
    ("slight-fav", 61, 80),
    ("heavy-fav", 81, 94),
]


def resolve_input(input_path: str) -> list[str]:
    """Accept a file, a directory, or a glob. Returns list of parquet files."""
    if os.path.isdir(input_path):
        files = sorted(glob.glob(os.path.join(input_path, "*.parquet")))
    elif any(ch in input_path for ch in "*?["):
        files = sorted(glob.glob(input_path))
    else:
        files = [input_path]
    if not files:
        raise FileNotFoundError(f"no parquet files for input: {input_path}")
    return files


# Default probe input — swap this path (or pass --input) to re-run on the full universe.
DEFAULT_INPUT = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "data", "durable", "per_minute_universe", "probe",
    "per_minute_universe_phase*.parquet",
)


def load_universe(input_path: str = DEFAULT_INPUT, category: str = "ATP_MAIN") -> pd.DataFrame:
    """Load + concat per-minute universe, filter to one category, add the cost-basis cell.

    Returns a frame sorted by (ticker, minute_ts) with:
        cell            int   round(100*yes_bid_close), NaN outside [CELL_MIN, CELL_MAX]
        fwd_max_traded  float max forward price_high (CORRECTED reach instrument)
        fwd_max_bid     float max forward yes_bid_high (OLD/banned, comparison only)
    """
    files = resolve_input(input_path)
    frames = []
    for f in files:
        d = pd.read_parquet(f)
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    if category is not None:
        df = df[df["category"] == category].copy()
    df = df.sort_values(["ticker", "minute_ts"]).reset_index(drop=True)

    # Cost-basis cell. round() to nearest cent; keep only entry-eligible cells.
    cell = np.round(df["yes_bid_close"].to_numpy() * 100.0)
    cell[(cell < CELL_MIN) | (cell > CELL_MAX)] = np.nan
    df["cell"] = cell

    df["fwd_max_traded"] = compute_forward_max(df, "price_high")   # CORRECTED
    df["fwd_max_bid"] = compute_forward_max(df, "yes_bid_high")    # OLD (banned)
    return df


def compute_forward_max(df: pd.DataFrame, col: str) -> np.ndarray:
    """Strictly-forward max of `col` within each ticker (NaN-skipping, gap-inclusive).

    fwd[i] = max(col over rows i+1..end of the same ticker), NaN if none traded after.
    np.fmax.accumulate ignores NaN (fmax(a, nan)=a), so no-trade minutes are skipped
    rather than poisoning the running max.
    """
    out = np.full(len(df), np.nan)
    vals = df[col].to_numpy(dtype=float)
    # group boundaries on the already-sorted frame
    codes = pd.factorize(df["ticker"], sort=False)[0]
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy()
        x = vals[ix]
        rev_incl = np.fmax.accumulate(x[::-1])[::-1]  # rev_incl[i] = max(x[i..end])
        strict = np.empty_like(rev_incl)
        strict[:-1] = rev_incl[1:]                     # max(x[i+1..end])
        strict[-1] = np.nan
        out[ix] = strict
    return out


def reach_table(df: pd.DataFrame, x_max: int = 40) -> pd.DataFrame:
    """Per (cell c, exit offset X) fill rates on both instruments.

    fill_corrected = mean[ fwd_max_traded >= (c+X)/100 ]   (price_high, skip-inclusive)
    fill_old       = mean[ fwd_max_bid    >= (c+X)/100 ]   (yes_bid_high, banned)
    Only X with c+X <= LOCK are emitted (you cannot sell above the 99 ceiling).
    N = entry observations at cell c (rows with a defined cell c).
    """
    rows = []
    sub = df[df["cell"].notna()]
    for c, g in sub.groupby("cell"):
        c = int(c)
        ft = g["fwd_max_traded"].to_numpy()
        fb = g["fwd_max_bid"].to_numpy()
        n = len(g)
        for X in range(1, x_max + 1):
            if c + X > LOCK:
                break
            tgt = (c + X) / 100.0
            fill_c = np.nanmean((ft >= tgt).astype(float)) if n else np.nan
            fill_o = np.nanmean((fb >= tgt).astype(float)) if n else np.nan
            rows.append({
                "c": c, "X": X, "target": c + X, "N": n,
                "fill_corrected": fill_c, "fill_old": fill_o,
                "roi_on_cost": (X / c) * fill_c,
            })
    return pd.DataFrame(rows)


def band_of(c: int) -> str:
    for name, lo, hi in BANDS:
        if lo <= c <= hi:
            return name
    return "out"
