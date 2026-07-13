#!/usr/bin/env python3
"""[C-GUIDEBOOK-V2 v1, 07-13] THE TIMING-CONDITIONED RECUT — the discount as
a moment: depth x dip-window x three-price shape.

LINEAGE (C45): third closing attempt for AIM/TIMING MISSES (refusals on
record: 07-11 aim refit; guidebook v1 static depth). Both refusals convicted
the same missing axis: WHEN. This recut conditions on it.

CORPUS: the G9 trade tape (data/durable/g9_trades.parquet, 33.7M rows,
era-admissible tour+ITF actual prints) + this week's local trades CSVs.
Self-contained truth per ticker, no external clock:
  onset  = the -0k flow-step rule on minute bins (tape ignition)
  ref    = median traded price of the ticker's first 60 tape minutes
  result = terminal print >=97 WIN / <=3 LOSS / else excluded
  dip    = deepest pre-onset print; t_dip = minutes before onset
AXES per page: category x shape(ref vs runmid30 at window entry: disc/at/over)
x price-cell(ref). PAGE: dip-window [p25,p75] of t_dip for the cat (the
fitted anatomy), depth-below-ref reached inside the window at 50/70/90
percent frequency, and the WIN/LOSS partition of legs whose tape touched the
page depth inside vs outside the window (the adverse-selection check v1
failed). TRAIN = strictly before HELD_OUT_FROM; the week stays held out."""
import json, gzip, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parent.parent
WS = ROOT.parent
G9 = ROOT / "data/durable/g9_trades.parquet"
TRADES = ROOT / "analysis/trades"
OUT = WS / ".claude/guidebook/GUIDEBOOK_V2.json"
HELD_OUT_FROM = "2026-07-10"   # the week is the test set, per the Plex frame

CATS = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
        "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
        "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
ONSET_K, ONSET_FLOOR = 3.0, 8


def pcell(px):
    return ("le25" if px <= 25 else "26_50" if px <= 50 else
            "51_75" if px <= 75 else "ge75")


def shape_of(px, rm):
    d = px - rm
    return "disc" if d < -1 else ("over" if d > 1 else "at_mid")


def onset_of(minutes):
    keys = sorted(minutes)
    if not keys:
        return None
    base60 = sum(minutes[m][1] for m in keys if m < keys[0] + 3600)
    need = max(ONSET_FLOOR, ONSET_K * base60 / 4.0)
    for m in keys:
        t15 = sum(minutes.get(k, (0, 0))[1] for k in range(m - 14 * 60, m + 60, 60))
        act = sum(1 for k in range(m - 14 * 60, m + 60, 60) if k in minutes)
        fwd = sum(minutes.get(k, (0, 0))[1] for k in range(m + 60, m + 31 * 60, 60))
        if act >= 5 and t15 >= need and fwd >= need:
            return m
    return None


def collect_g9():
    """(ticker, minute) -> (min_px_cents, n_prints, sum_px) via chunked row groups."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(G9)
    agg = {}
    cutoff = datetime.fromisoformat(HELD_OUT_FROM).replace(tzinfo=timezone.utc).timestamp()
    for rg in range(pf.num_row_groups):
        t = pf.read_row_group(rg, columns=["ticker", "created_time",
                                           "yes_price_dollars"]).to_pydict()
        for tk, ct, yp in zip(t["ticker"], t["created_time"], t["yes_price_dollars"]):
            if not tk or not tk.startswith("KX") or "MATCH-" not in tk:
                continue
            # created_time is an ISO string ('2026-04-03T04:31:29.900853Z');
            # string date-prefix gate first (cheap), full parse second
            try:
                if isinstance(ct, str):
                    if ct[:10] >= HELD_OUT_FROM:
                        continue    # train era only
                    ts = datetime.fromisoformat(ct.replace("Z", "+00:00")).timestamp()
                else:
                    ts = ct.timestamp()
                    if ts >= cutoff:
                        continue
            except Exception:
                continue
            px = round(float(yp) * 100)
            m = int(ts // 60) * 60
            cur = agg.get((tk, m))
            if cur is None:
                agg[(tk, m)] = [px, 1, px]
            else:
                if px < cur[0]:
                    cur[0] = px
                cur[1] += 1
                cur[2] += px
    return agg


def build():
    agg = collect_g9()
    print("g9 (ticker,minute) rows (train era):", len(agg))
    per_tk = defaultdict(dict)
    for (tk, m), v in agg.items():
        per_tk[tk][m] = (v[0], v[1], v[2])
    del agg
    print("tickers:", len(per_tk))
    dip_times = defaultdict(list)
    legs = []
    for tk, minutes in per_tk.items():
        cat = CATS.get(tk.split("-")[0])
        if not cat or len(minutes) < 10:
            continue
        keys = sorted(minutes)
        last_px = minutes[keys[-1]][2] / minutes[keys[-1]][1]
        result = "win" if last_px >= 97 else ("loss" if last_px <= 3 else None)
        if result is None:
            continue
        on = onset_of(minutes)
        if on is None or on <= keys[0] + 3600:
            continue
        first_hr = [minutes[m][2] / minutes[m][1] for m in keys if m < keys[0] + 3600]
        ref = sorted(first_hr)[len(first_hr) // 2]
        pre = [(m, minutes[m][0]) for m in keys if m < on]
        if not pre:
            continue
        dip_m, dip_px = min(pre, key=lambda x: x[1])
        t_dip = (on - dip_m) / 60.0
        dip_times[cat].append(t_dip)
        legs.append((tk, cat, ref, on, pre, result))
    windows = {}
    for cat, ts in dip_times.items():
        ts.sort()
        n = len(ts)
        windows[cat] = [round(ts[n // 4], 1), round(ts[(3 * n) // 4], 1)]
    print("dip windows [p25,p75] min-before-onset:", windows)
    pages = defaultdict(lambda: {"n": 0, "depths": [], "in_win": [0, 0],
                                 "out_win": [0, 0]})
    for tk, cat, ref, on, pre, result in legs:
        w = windows.get(cat)
        if not w:
            continue
        w_lo, w_hi = on - w[1] * 60, on - w[0] * 60
        rm_pts = [minutes_px for m, minutes_px in pre if w_lo - 1800 <= m < w_lo]
        rm = (sum(rm_pts) / len(rm_pts)) if rm_pts else ref
        key = "%s|%s|%s" % (cat, shape_of(ref, rm), pcell(int(ref)))
        P = pages[key]
        P["n"] += 1
        in_min = min((px for m, px in pre if w_lo <= m <= w_hi), default=None)
        out_min = min((px for m, px in pre if m < w_lo or m > w_hi), default=None)
        if in_min is not None:
            P["depths"].append(max(0, int(ref) - in_min))
        # adverse-selection partition at a FIXED probe depth (5c) in/out:
        probe = 5
        if in_min is not None and int(ref) - in_min >= probe:
            P["in_win"][0 if result == "win" else 1] += 1
        if out_min is not None and int(ref) - out_min >= probe:
            P["out_win"][0 if result == "win" else 1] += 1
    gb = {"meta": {"built": "2026-07-13", "corpus": "g9_trades.parquet (train era < %s)" % HELD_OUT_FROM,
                   "onset": "-0k flow-step rule", "ref": "median of first tape hour",
                   "windows_p25_p75_min_before_onset": windows,
                   "probe_depth_for_partition_cents": 5,
                   "lineage": ["AIM/TIMING MISSES attempt 3",
                               "axes = cat x shape x price-cell x DIP WINDOW"]},
          "pages": {}}
    for key, P in pages.items():
        if P["n"] < 8:
            gb["pages"][key] = {"n": P["n"], "verdict": "REFUSE_THIN"}
            continue
        d = sorted(P["depths"])
        nd = len(d)
        gb["pages"][key] = {
            "n": P["n"], "verdict": "AIM",
            "depth_in_window": {
                "p50": d[nd // 2] if nd else 0,
                "p70": d[int(nd * 0.3)] if nd else 0,   # reached by 70%
                "p90": d[int(nd * 0.1)] if nd else 0},  # reached by 90%
            "win_loss_at_probe": {"inside": P["in_win"], "outside": P["out_win"]}}
    OUT.write_text(json.dumps(gb, indent=1), encoding="utf-8")
    aims = sum(1 for p in gb["pages"].values() if p.get("verdict") == "AIM")
    print("GUIDEBOOK_V2: %d pages (%d AIM) -> %s" % (len(gb["pages"]), aims, OUT))


if __name__ == "__main__":
    build()
