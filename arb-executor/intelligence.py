#!/usr/bin/env python3
"""
intelligence.py — Read-only analysis functions for tennis trading intelligence.

Five standalone queries that assess tradability of an event/ticker pair.
No writes, no execution, no modification of existing tables or scrapers.
"""

import sqlite3, json, os
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")
CONFIG_PATH = str(Path(__file__).resolve().parent / "config" / "deploy_v4.json")


def _conn():
    return sqlite3.connect(DB_PATH, timeout=10)


def _age_sec(polled_at_str, now):
    try:
        dt = datetime.strptime(polled_at_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET)
        return (now - dt).total_seconds()
    except Exception:
        return None


# ── 1. FV Stability ──────────────────────────────────────────────────────────

def fv_stability(event_ticker, hours=4):
    """Assess FV consensus and stability over a window.

    Returns: {fv_now, fv_min, fv_max, range_c, range_pct, samples,
              sources: [{book, fv, age_sec}], stable: bool, grade: str}
    """
    conn = _conn()
    cur = conn.cursor()
    now = datetime.now(ET)
    cutoff = (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        SELECT book_key, book_p1_fv_cents, book_p2_fv_cents, polled_at
        FROM book_prices
        WHERE event_ticker = ? AND polled_at > ?
        ORDER BY polled_at DESC
    """, (event_ticker, cutoff))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return {"event_ticker": event_ticker, "samples": 0, "stable": False,
                "grade": "NO_DATA", "sources": [], "num_books": 0,
                "fv_now": 0, "fv_min": 0, "fv_max": 0,
                "range_c": 0, "range_pct": 0, "mean_fv": 0}

    latest_by_book = {}
    all_p1 = []
    all_p2 = []
    for book, p1, p2, polled in rows:
        if p1 and p1 > 0:
            all_p1.append(p1)
        if p2 and p2 > 0:
            all_p2.append(p2)
        if book not in latest_by_book:
            age = _age_sec(polled, now)
            latest_by_book[book] = {"book": book, "p1_fv": p1, "p2_fv": p2,
                                    "age_sec": int(age) if age else None}

    side = "p1"
    fvs = all_p1 if all_p1 else all_p2
    if not all_p1 and all_p2:
        side = "p2"
    if not fvs:
        return {"event_ticker": event_ticker, "samples": 0, "stable": False,
                "grade": "NO_DATA", "sources": list(latest_by_book.values()),
                "num_books": len(latest_by_book), "fv_now": 0, "fv_min": 0,
                "fv_max": 0, "range_c": 0, "range_pct": 0, "mean_fv": 0}

    fv_now = fvs[0]
    fv_min = min(fvs)
    fv_max = max(fvs)
    range_c = fv_max - fv_min
    mean_fv = sum(fvs) / len(fvs)
    range_pct = (range_c / mean_fv * 100) if mean_fv > 0 else 0

    if range_pct > 20:
        grade = "VOLATILE"
        stable = False
    elif range_pct > 10:
        grade = "MODERATE"
        stable = True
    else:
        grade = "STABLE"
        stable = True

    return {
        "event_ticker": event_ticker,
        "side_analyzed": side,
        "fv_now": round(fv_now, 1),
        "fv_min": round(fv_min, 1),
        "fv_max": round(fv_max, 1),
        "range_c": round(range_c, 1),
        "range_pct": round(range_pct, 1),
        "mean_fv": round(mean_fv, 1),
        "samples": len(fvs),
        "num_books": len(latest_by_book),
        "sources": list(latest_by_book.values()),
        "stable": stable,
        "grade": grade,
    }


# ── 2. Kalshi Tracking FV ────────────────────────────────────────────────────

def kalshi_tracking_fv(event_ticker, ticker, hours=4):
    """Assess how well Kalshi price tracks FV over time.

    Returns: {snapshots, avg_spread_c, max_spread_c, kalshi_above_pct,
              kalshi_below_pct, tracking_grade, current_spread_c, pairs: [...]}
    """
    conn = _conn()
    cur = conn.cursor()
    now = datetime.now(ET)
    cutoff = (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        SELECT polled_at, bid_cents, ask_cents, last_cents
        FROM kalshi_price_snapshots
        WHERE ticker = ? AND polled_at > ?
        ORDER BY polled_at ASC
    """, (ticker, cutoff))
    kalshi_rows = cur.fetchall()

    cur.execute("""
        SELECT bp.polled_at, bp.book_p1_fv_cents, bp.book_p2_fv_cents, bp.book_key
        FROM book_prices bp
        INNER JOIN (
            SELECT event_ticker, book_key, MAX(polled_at) as mp
            FROM book_prices
            WHERE event_ticker = ? AND polled_at > ?
            GROUP BY event_ticker, book_key, substr(polled_at, 1, 16)
        ) latest ON bp.event_ticker = latest.event_ticker
                AND bp.book_key = latest.book_key
                AND bp.polled_at = latest.mp
        WHERE bp.event_ticker = ?
        ORDER BY bp.polled_at ASC
    """, (event_ticker, cutoff, event_ticker))
    fv_rows = cur.fetchall()
    conn.close()

    if not kalshi_rows:
        return {"event_ticker": event_ticker, "ticker": ticker,
                "snapshots": 0, "tracking_grade": "NO_KALSHI_DATA"}
    if not fv_rows:
        return {"event_ticker": event_ticker, "ticker": ticker,
                "snapshots": len(kalshi_rows), "tracking_grade": "NO_FV_DATA"}

    is_p1 = "-" in ticker and ticker.split("-")[-1][:3].upper() == ticker.split("-")[-1][:3].upper()

    fv_timeline = []
    for polled, p1, p2, book in fv_rows:
        if book == "pinnacle":
            fv_timeline.append((polled, p1, p2))
        elif not fv_timeline or fv_timeline[-1][0] != polled:
            fv_timeline.append((polled, p1, p2))

    pairs = []
    spreads = []
    above = 0
    below = 0

    for k_polled, bid, ask, last in kalshi_rows:
        kalshi_mid = (bid + ask) / 2 if bid and ask else (last or 0)
        if kalshi_mid <= 0:
            continue

        best_fv = None
        best_dist = float("inf")
        for f_polled, p1, p2 in fv_timeline:
            dist = abs(_time_diff_sec(k_polled, f_polled))
            if dist < best_dist:
                best_dist = dist
                best_fv = (f_polled, p1, p2)

        if not best_fv or best_dist > 900:
            continue

        fv_p1 = best_fv[1] or 0
        fv_p2 = best_fv[2] or 0
        fv_use = fv_p1 if fv_p1 > 0 else fv_p2
        if fv_use <= 0:
            continue

        spread_c = kalshi_mid - fv_use
        spreads.append(spread_c)
        if spread_c > 0:
            above += 1
        elif spread_c < 0:
            below += 1
        pairs.append({"time": k_polled, "kalshi_mid": round(kalshi_mid, 1),
                       "fv": round(fv_use, 1), "spread_c": round(spread_c, 1)})

    if not spreads:
        return {"event_ticker": event_ticker, "ticker": ticker,
                "snapshots": len(kalshi_rows), "tracking_grade": "NO_OVERLAP"}

    avg_spread = sum(spreads) / len(spreads)
    max_spread = max(abs(s) for s in spreads)
    total = above + below + (len(spreads) - above - below)

    if max_spread <= 3:
        tracking_grade = "TIGHT"
    elif max_spread <= 8:
        tracking_grade = "NORMAL"
    else:
        tracking_grade = "WIDE"

    return {
        "event_ticker": event_ticker,
        "ticker": ticker,
        "snapshots": len(pairs),
        "avg_spread_c": round(avg_spread, 1),
        "max_spread_c": round(max_spread, 1),
        "kalshi_above_pct": round(above / total * 100, 1) if total else 0,
        "kalshi_below_pct": round(below / total * 100, 1) if total else 0,
        "current_spread_c": round(spreads[-1], 1) if spreads else None,
        "tracking_grade": tracking_grade,
        "pairs": pairs[-5:],
    }


def _time_diff_sec(t1_str, t2_str):
    try:
        t1 = datetime.strptime(t1_str, "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(t2_str, "%Y-%m-%d %H:%M:%S")
        return (t1 - t2).total_seconds()
    except Exception:
        return 99999


# ── 3. FV Trajectory ─────────────────────────────────────────────────────────

def fv_trajectory(event_ticker, hours=12):
    """Compute FV drift rate via linear regression.

    Returns: {slope_c_per_hr, direction, r_squared, fv_start, fv_end, samples}
    """
    conn = _conn()
    cur = conn.cursor()
    now = datetime.now(ET)
    cutoff = (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        SELECT book_p1_fv_cents, book_p2_fv_cents, polled_at
        FROM book_prices
        WHERE event_ticker = ? AND book_key = 'pinnacle' AND polled_at > ?
        ORDER BY polled_at ASC
    """, (event_ticker, cutoff))
    rows = cur.fetchall()

    if len(rows) < 2:
        cur.execute("""
            SELECT book_p1_fv_cents, book_p2_fv_cents, polled_at
            FROM book_prices
            WHERE event_ticker = ? AND book_key = 'betexplorer' AND polled_at > ?
            ORDER BY polled_at ASC
        """, (event_ticker, cutoff))
        rows = cur.fetchall()
    conn.close()

    if len(rows) < 2:
        return {"event_ticker": event_ticker, "samples": len(rows),
                "direction": "INSUFFICIENT_DATA"}

    points = []
    t0 = None
    for p1, p2, polled in rows:
        fv = p1 if p1 and p1 > 0 else (p2 if p2 and p2 > 0 else None)
        if fv is None:
            continue
        try:
            t = datetime.strptime(polled, "%Y-%m-%d %H:%M:%S")
            if t0 is None:
                t0 = t
            hours_elapsed = (t - t0).total_seconds() / 3600
            points.append((hours_elapsed, fv))
        except Exception:
            continue

    if len(points) < 2:
        return {"event_ticker": event_ticker, "samples": len(points),
                "direction": "INSUFFICIENT_DATA"}

    n = len(points)
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    sxx = sum(p[0] ** 2 for p in points)
    sxy = sum(p[0] * p[1] for p in points)

    denom = n * sxx - sx * sx
    if abs(denom) < 1e-10:
        slope = 0
    else:
        slope = (n * sxy - sx * sy) / denom

    y_mean = sy / n
    ss_tot = sum((p[1] - y_mean) ** 2 for p in points)
    intercept = (sy - slope * sx) / n
    ss_res = sum((p[1] - (intercept + slope * p[0])) ** 2 for p in points)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    if abs(slope) < 0.5:
        direction = "FLAT"
    elif slope > 0:
        direction = "RISING"
    else:
        direction = "FALLING"

    return {
        "event_ticker": event_ticker,
        "slope_c_per_hr": round(slope, 2),
        "direction": direction,
        "r_squared": round(max(0, r_squared), 3),
        "fv_start": round(points[0][1], 1),
        "fv_end": round(points[-1][1], 1),
        "span_hours": round(points[-1][0], 1),
        "samples": n,
    }


# ── 4. Cell Assignment ───────────────────────────────────────────────────────

def cell_assignment(event_ticker, ticker, config=None):
    """Show which cell this event/ticker maps to and its configuration.

    Returns: {category, direction, fv_cents, kalshi_mid, cell_name, cell_cfg,
              play_type, enabled}
    """
    if config is None:
        with open(CONFIG_PATH) as f:
            config = json.load(f)

    conn = _conn()
    cur = conn.cursor()
    now = datetime.now(ET)

    from fv import get_consensus_fv
    fv_p1 = get_consensus_fv(event_ticker, "p1", conn=conn)
    fv_p2 = get_consensus_fv(event_ticker, "p2", conn=conn)

    cur.execute("""
        SELECT bid_cents, ask_cents, last_cents
        FROM kalshi_price_snapshots
        WHERE ticker = ?
        ORDER BY polled_at DESC LIMIT 1
    """, (ticker,))
    k_row = cur.fetchone()
    conn.close()

    kalshi_mid = None
    if k_row:
        bid, ask, last = k_row
        kalshi_mid = (bid + ask) / 2 if bid and ask else last

    suffix = ticker.split("-")[-1] if "-" in ticker else ""
    is_challenger = "CHALLENGER" in event_ticker.upper()
    series = event_ticker.split("-")[0] if "-" in event_ticker else ""

    if "KXATPCHALLENGERMATCH" in series or "KXWTACHALLENGERMATCH" in series:
        tour = "ATP_CHALL" if "KXATP" in series else "WTA_CHALL"
    elif "KXATPMATCH" in series or "KXWTAMATCH" in series:
        tour = "ATP_MAIN" if "KXATP" in series else "WTA_MAIN"
    else:
        tour = "UNKNOWN"

    result = {"event_ticker": event_ticker, "ticker": ticker, "tour": tour}

    for side_label, fv_result in [("p1", fv_p1), ("p2", fv_p2)]:
        if not fv_result or fv_result.get("fv_cents") is None:
            continue
        fv_c = fv_result["fv_cents"]
        direction = "underdog" if fv_c < 50 else "leader"
        bucket = int(fv_c / 5) * 5
        cell_name = "%s_%s_%d-%d" % (tour, direction, bucket, bucket + 4)

        enabled = cell_name in config.get("active_cells", {})
        disabled = cell_name in config.get("disabled_cells", [])
        cell_cfg = config.get("active_cells", {}).get(cell_name)

        play_type = None
        if kalshi_mid is not None and fv_c > 0:
            if kalshi_mid < fv_c:
                play_type = "B_convergence"
            else:
                fv_bucket = int(fv_c / 5) * 5
                kalshi_bucket = int(kalshi_mid / 5) * 5
                if fv_bucket == kalshi_bucket:
                    play_type = "A_tight"
                else:
                    play_type = "A_patient"

        result[side_label] = {
            "fv_cents": round(fv_c, 1),
            "fv_source": fv_result.get("source"),
            "fv_tier": fv_result.get("tier"),
            "direction": direction,
            "cell_name": cell_name,
            "cell_cfg": cell_cfg,
            "enabled": enabled,
            "disabled": disabled,
            "play_type": play_type,
        }

    if kalshi_mid is not None:
        result["kalshi_mid"] = round(kalshi_mid, 1)

    return result


# ── 5. Confidence Score ──────────────────────────────────────────────────────

def confidence_score(event_ticker, ticker):
    """Compute overall 0-100 tradability score combining all signals.

    Two scoring paths:
      FV-anchored: fv_quality(30) + stability(20) + tracking(20) + trajectory(15) + cell_fit(15)
      Kalshi-anchored: kalshi_history(20) + kalshi_stability(20) + kalshi_oscillation(15) + cell_fit_kalshi(15)
        (activates when FV components score 0 AND Kalshi has 3+ snapshots)

    Returns: {score, grade, anchor_mode, components, flags}
    """
    components = {}
    flags = []

    stab = fv_stability(event_ticker, hours=4)
    track = kalshi_tracking_fv(event_ticker, ticker, hours=4)
    traj = fv_trajectory(event_ticker, hours=12)
    cell = cell_assignment(event_ticker, ticker)

    # ── FV-anchored scoring ──
    fv_score = 0
    if stab["samples"] > 0:
        if stab["num_books"] >= 5:
            fv_score += 15
        elif stab["num_books"] >= 3:
            fv_score += 10
        elif stab["num_books"] >= 1:
            fv_score += 5

        if stab["grade"] == "STABLE":
            fv_score += 15
        elif stab["grade"] == "MODERATE":
            fv_score += 8
        else:
            flags.append("FV_VOLATILE")
    else:
        flags.append("NO_FV_DATA")
    components["fv_quality"] = min(fv_score, 30)

    stab_score = 0
    if stab["stable"]:
        stab_score = 20
    elif stab["range_pct"] <= 15:
        stab_score = 12
    elif stab["samples"] > 0:
        stab_score = 5
        flags.append("HIGH_FV_RANGE")
    components["stability"] = stab_score

    track_score = 0
    if track.get("tracking_grade") == "TIGHT":
        track_score = 20
    elif track.get("tracking_grade") == "NORMAL":
        track_score = 14
    elif track.get("tracking_grade") == "WIDE":
        track_score = 6
        flags.append("WIDE_KALSHI_SPREAD")
    elif track.get("tracking_grade") in ("NO_KALSHI_DATA", "NO_FV_DATA", "NO_OVERLAP"):
        flags.append("NO_TRACKING_DATA")
    components["tracking"] = track_score

    traj_score = 0
    if traj["direction"] == "FLAT":
        traj_score = 15
    elif traj["direction"] in ("RISING", "FALLING"):
        if traj.get("r_squared", 0) > 0.7:
            traj_score = 10
        else:
            traj_score = 12
        if abs(traj.get("slope_c_per_hr", 0)) > 3:
            flags.append("FAST_FV_DRIFT")
    elif traj["direction"] == "INSUFFICIENT_DATA":
        traj_score = 7
    components["trajectory"] = traj_score

    cell_score = 0
    for side in ("p1", "p2"):
        s = cell.get(side, {})
        if s.get("enabled"):
            cell_score = max(cell_score, 15)
        elif s.get("disabled"):
            cell_score = max(cell_score, 3)
            if cell_score <= 3:
                flags.append("CELL_DISABLED_%s" % s.get("cell_name", ""))
        elif s.get("cell_name"):
            cell_score = max(cell_score, 8)
    components["cell_fit"] = cell_score

    fv_total = sum(components.values())

    # ── Kalshi-anchored fallback ──
    # Activates when FV components contribute nothing meaningful
    has_fv = components["fv_quality"] > 0 or components["tracking"] > 0
    kpa = kalshi_price_anchor(event_ticker, ticker, hours=4)
    kalshi_snaps = kpa.get("n_snapshots", 0)

    if not has_fv and kalshi_snaps >= 3:
        flags.append("KALSHI_ANCHORED")
        k_components = {}

        # Kalshi history quality (0-20): snapshot depth
        if kalshi_snaps >= 30:
            k_components["kalshi_history"] = 20
        elif kalshi_snaps >= 15:
            k_components["kalshi_history"] = 14
        elif kalshi_snaps >= 6:
            k_components["kalshi_history"] = 8
        else:
            k_components["kalshi_history"] = 4

        # Kalshi price stability (0-20): low stddev = predictable
        std = kpa.get("std_dev_cents", 99)
        if std <= 1.0:
            k_components["kalshi_stability"] = 20
        elif std <= 2.0:
            k_components["kalshi_stability"] = 15
        elif std <= 4.0:
            k_components["kalshi_stability"] = 10
        else:
            k_components["kalshi_stability"] = 4
            flags.append("KALSHI_HIGH_VOLATILITY")

        # Kalshi oscillation (0-15): mean reversion signal
        if kpa.get("is_oscillating"):
            k_components["kalshi_oscillation"] = 15
            flags.append("KALSHI_OSCILLATING")
        elif kpa.get("range_cents", 0) >= 3:
            k_components["kalshi_oscillation"] = 8
        else:
            k_components["kalshi_oscillation"] = 3

        # Cell fit from Kalshi mid (0-15)
        kalshi_mid = cell.get("kalshi_mid")
        k_cell_score = 0
        if kalshi_mid:
            tour = cell.get("tour", "")
            direction = "underdog" if kalshi_mid < 50 else "leader"
            bucket = int(kalshi_mid / 5) * 5
            k_cell_name = "%s_%s_%d-%d" % (tour, direction, bucket, bucket + 4)
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            if k_cell_name in cfg.get("active_cells", {}):
                k_cell_score = 15
            elif k_cell_name in cfg.get("disabled_cells", []):
                k_cell_score = 3
            else:
                k_cell_score = 8
        k_components["cell_fit_kalshi"] = k_cell_score

        k_total = sum(k_components.values())

        if k_total > fv_total:
            components = k_components
            total = k_total
            anchor_mode = "kalshi"
        else:
            total = fv_total
            anchor_mode = "fv"
    else:
        total = fv_total
        anchor_mode = "fv"

    if total >= 80:
        grade = "HIGH"
    elif total >= 50:
        grade = "MEDIUM"
    elif total >= 30:
        grade = "LOW"
    else:
        grade = "SKIP"

    return {
        "event_ticker": event_ticker,
        "ticker": ticker,
        "score": total,
        "grade": grade,
        "anchor_mode": anchor_mode,
        "components": components,
        "flags": flags,
    }


# ── 6. Kalshi Price Anchor ────────────────────────────────────────────────────

def kalshi_price_anchor(event_ticker, ticker, hours=1):
    """For events with weak FV, use Kalshi's own price history as anchor.

    Returns: {median_price_cents, std_dev_cents, n_snapshots, range_cents,
              is_oscillating, is_stable, current_price, deviation_from_median}
    """
    conn = _conn()
    cur = conn.cursor()
    now = datetime.now(ET)
    cutoff = (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        SELECT bid_cents, ask_cents, last_cents, polled_at
        FROM kalshi_price_snapshots
        WHERE ticker = ? AND polled_at > ?
        ORDER BY polled_at ASC
    """, (ticker, cutoff))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return {"event_ticker": event_ticker, "ticker": ticker,
                "n_snapshots": 0, "median_price_cents": None}

    mids = []
    for bid, ask, last, polled in rows:
        mid = (bid + ask) / 2 if bid and ask and bid > 0 and ask > 0 else last
        if mid and mid > 0:
            mids.append(mid)

    if not mids:
        return {"event_ticker": event_ticker, "ticker": ticker,
                "n_snapshots": 0, "median_price_cents": None}

    sorted_mids = sorted(mids)
    n = len(sorted_mids)
    median = sorted_mids[n // 2] if n % 2 == 1 else (sorted_mids[n // 2 - 1] + sorted_mids[n // 2]) / 2
    mean = sum(mids) / n
    variance = sum((m - mean) ** 2 for m in mids) / n if n > 1 else 0
    std_dev = variance ** 0.5
    range_c = sorted_mids[-1] - sorted_mids[0]
    current = mids[-1]

    return {
        "event_ticker": event_ticker,
        "ticker": ticker,
        "median_price_cents": round(median, 1),
        "std_dev_cents": round(std_dev, 1),
        "n_snapshots": n,
        "range_cents": round(range_c, 1),
        "is_oscillating": std_dev > 2 and range_c > 5,
        "is_stable": range_c < 3,
        "current_price": round(current, 1),
        "deviation_from_median": round(current - median, 1),
    }


# ── 7. Recommended Window ────────────────────────────────────────────────────

def recommended_window_seconds(event_ticker, ticker):
    """Data-driven entry window based on confidence and data quality.

    HIGH (80+):  4h, fv_consensus, 10ct
    MEDIUM (50-79): 2h, fv_consensus if FV else kalshi_price, 10ct if FV else 5ct
    LOW (30-49): 1h, kalshi_price, 5ct
    SKIP (<30):  0

    Returns: {window_seconds, anchor_source, rationale, recommended_size, ...}
    """
    cs = confidence_score(event_ticker, ticker)
    score = cs["score"]
    grade = cs["grade"]
    is_kalshi_anchored = cs.get("anchor_mode") == "kalshi"

    base = {"event_ticker": event_ticker, "ticker": ticker,
            "confidence_score": score, "confidence_grade": grade,
            "anchor_mode": cs.get("anchor_mode", "fv")}

    if score >= 80:
        base.update({
            "window_seconds": 14400,
            "anchor_source": "fv_consensus",
            "rationale": "HIGH confidence (%d/100) — full FV coverage, %d-book consensus" % (
                score, fv_stability(event_ticker).get("num_books", 0)),
            "recommended_size": 10,
        })
        return base

    if score >= 50:
        if is_kalshi_anchored:
            kpa = kalshi_price_anchor(event_ticker, ticker, hours=1)
            base.update({
                "window_seconds": 7200,
                "anchor_source": "kalshi_price",
                "rationale": "MEDIUM confidence (%d/100, Kalshi-anchored) — no FV, Kalshi price anchor (median %.1fc, %d snaps)" % (
                    score, kpa.get("median_price_cents", 0), kpa.get("n_snapshots", 0)),
                "recommended_size": 5,
                "kalshi_anchor": kpa,
            })
        else:
            base.update({
                "window_seconds": 7200,
                "anchor_source": "fv_consensus",
                "rationale": "MEDIUM confidence (%d/100) — FV available but limited coverage or moderate volatility" % score,
                "recommended_size": 10,
            })
        return base

    if score >= 30:
        kpa = kalshi_price_anchor(event_ticker, ticker, hours=1)
        if kpa.get("n_snapshots", 0) >= 2 and kpa.get("median_price_cents") is not None:
            rationale = "LOW confidence (%d/100) — Kalshi price anchor (median %.1fc, %d snaps, range %.1fc)" % (
                score, kpa["median_price_cents"], kpa["n_snapshots"], kpa.get("range_cents", 0))
            if kpa.get("is_oscillating"):
                rationale += " — price oscillating (mean reversion opportunity)"
            base.update({
                "window_seconds": 3600,
                "anchor_source": "kalshi_price",
                "rationale": rationale,
                "recommended_size": 5,
                "kalshi_anchor": kpa,
            })
        else:
            base.update({
                "window_seconds": 0,
                "anchor_source": "skip",
                "rationale": "LOW confidence (%d/100) AND no Kalshi price history — no reliable anchor" % score,
                "recommended_size": 0,
            })
        return base

    base.update({
        "window_seconds": 0,
        "anchor_source": "skip",
        "rationale": "SKIP (%d/100) — insufficient data quality to trade" % score,
        "recommended_size": 0,
    })
    return base


# ── Self-test ─────────────────────────────────────────────────────────────────

def self_test():
    """Run all 7 functions against real events — 4 test cases."""
    conn = _conn()
    cur = conn.cursor()
    now_et = datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p ET")

    # Case A: Main tour with full FV
    cur.execute("""
        SELECT DISTINCT kps.event_ticker, kps.ticker
        FROM kalshi_price_snapshots kps
        JOIN book_prices bp ON kps.event_ticker = bp.event_ticker
        WHERE kps.event_ticker NOT LIKE '%CHALLENGER%'
        ORDER BY kps.polled_at DESC LIMIT 1
    """)
    case_a = cur.fetchone()

    # Case B: Challenger with BetExplorer FV + Kalshi price
    cur.execute("""
        SELECT DISTINCT kps.event_ticker, kps.ticker
        FROM kalshi_price_snapshots kps
        JOIN book_prices bp ON kps.event_ticker = bp.event_ticker
            AND bp.book_key = 'betexplorer'
        WHERE kps.event_ticker LIKE '%CHALLENGER%'
        ORDER BY kps.polled_at DESC LIMIT 1
    """)
    case_b = cur.fetchone()

    # Case C: Challenger with Kalshi price but NO FV at all
    cur.execute("""
        SELECT DISTINCT kps.event_ticker, kps.ticker
        FROM kalshi_price_snapshots kps
        LEFT JOIN book_prices bp ON kps.event_ticker = bp.event_ticker
        WHERE kps.event_ticker LIKE '%CHALLENGER%'
            AND bp.event_ticker IS NULL
        ORDER BY kps.polled_at DESC LIMIT 1
    """)
    case_c = cur.fetchone()
    if not case_c:
        cur.execute("""
            SELECT DISTINCT kps.event_ticker, kps.ticker
            FROM kalshi_price_snapshots kps
            WHERE kps.event_ticker LIKE '%CHALLENGER%'
                AND kps.event_ticker NOT IN (SELECT DISTINCT event_ticker FROM book_prices)
            ORDER BY kps.polled_at DESC LIMIT 1
        """)
        case_c = cur.fetchone()

    # Case D: Fabricated ticker with no data at all
    case_d = ("KXWTACHALLENGERMATCH-26APR21FAKXYZ", "KXWTACHALLENGERMATCH-26APR21FAKXYZ-FAK")

    conn.close()

    def run_case(label, event_ticker, ticker):
        print("\n" + "=" * 70)
        print("CASE %s @ %s" % (label, now_et))
        print("Event: %s" % event_ticker)
        print("Ticker: %s" % ticker)
        print("=" * 70)

        print("\n── 1. FV Stability ──")
        s = fv_stability(event_ticker)
        print("  Grade: %s | Stable: %s | Range: %.1fc (%.1f%%)" % (
            s["grade"], s["stable"], s["range_c"], s["range_pct"]))
        print("  FV now: %.1fc | Min: %.1fc | Max: %.1fc | Samples: %d | Books: %d" % (
            s.get("fv_now", 0), s.get("fv_min", 0), s.get("fv_max", 0),
            s["samples"], s.get("num_books", 0)))

        print("\n── 2. Kalshi Tracking FV ──")
        t = kalshi_tracking_fv(event_ticker, ticker)
        print("  Grade: %s | Snapshots: %d" % (t.get("tracking_grade", "?"), t.get("snapshots", 0)))
        if t.get("avg_spread_c") is not None:
            print("  Avg spread: %.1fc | Max: %.1fc | Current: %sc" % (
                t["avg_spread_c"], t["max_spread_c"],
                "%.1f" % t["current_spread_c"] if t["current_spread_c"] is not None else "?"))

        print("\n── 3. FV Trajectory ──")
        tr = fv_trajectory(event_ticker)
        print("  Direction: %s | Samples: %d" % (tr["direction"], tr["samples"]))
        if tr.get("slope_c_per_hr") is not None:
            print("  Slope: %+.2f c/hr | R²: %.3f" % (tr["slope_c_per_hr"], tr.get("r_squared", 0)))

        print("\n── 4. Cell Assignment ──")
        c = cell_assignment(event_ticker, ticker)
        print("  Tour: %s" % c.get("tour", "?"))
        if c.get("kalshi_mid"):
            print("  Kalshi mid: %.1fc" % c["kalshi_mid"])
        for side in ("p1", "p2"):
            si = c.get(side, {})
            if si:
                print("  %s: FV=%.1fc (%s T%s) → %s [%s] %s" % (
                    side, si.get("fv_cents", 0), si.get("fv_source", "?"), si.get("fv_tier", "?"),
                    si.get("cell_name", "?"),
                    "ENABLED" if si.get("enabled") else ("DISABLED" if si.get("disabled") else "UNCONFIGURED"),
                    si.get("play_type", "")))

        print("\n── 5. Confidence Score ──")
        cs = confidence_score(event_ticker, ticker)
        print("  Score: %d/100 | Grade: %s | Anchor mode: %s" % (
            cs["score"], cs["grade"], cs.get("anchor_mode", "fv")))
        print("  Components: %s" % json.dumps(cs["components"]))
        if cs["flags"]:
            print("  Flags: %s" % ", ".join(cs["flags"]))

        print("\n── 6. Kalshi Price Anchor ──")
        kpa = kalshi_price_anchor(event_ticker, ticker, hours=4)
        if kpa.get("median_price_cents") is not None:
            print("  Median: %.1fc | StdDev: %.1fc | Range: %.1fc | Snapshots: %d" % (
                kpa["median_price_cents"], kpa["std_dev_cents"], kpa["range_cents"], kpa["n_snapshots"]))
            print("  Current: %.1fc | Dev from median: %+.1fc | Stable: %s | Oscillating: %s" % (
                kpa["current_price"], kpa["deviation_from_median"], kpa["is_stable"], kpa["is_oscillating"]))
        else:
            print("  No Kalshi price data")

        print("\n── 7. Recommended Window ──")
        rw = recommended_window_seconds(event_ticker, ticker)
        print("  Window: %ds (%s) | Anchor: %s | Size: %dct" % (
            rw["window_seconds"],
            "%dh" % (rw["window_seconds"] // 3600) if rw["window_seconds"] >= 3600 else
            ("%dm" % (rw["window_seconds"] // 60) if rw["window_seconds"] > 0 else "SKIP"),
            rw["anchor_source"], rw["recommended_size"]))
        print("  Rationale: %s" % rw["rationale"])

    if case_a:
        run_case("A — Main tour with full FV", case_a[0], case_a[1])
    else:
        print("\nCASE A: No Main tour event with Kalshi+FV overlap found")

    if case_b:
        run_case("B — Challenger with weak BetExplorer FV + Kalshi", case_b[0], case_b[1])
    else:
        print("\nCASE B: No Challenger with BetExplorer FV found")

    if case_c:
        run_case("C — Challenger with Kalshi price, NO FV", case_c[0], case_c[1])
    else:
        print("\nCASE C: No Challenger without FV found (all have book_prices)")

    run_case("D — No data (fabricated)", case_d[0], case_d[1])

    print("\n" + "=" * 70)
    print("All 4 test cases complete.")


if __name__ == "__main__":
    self_test()
