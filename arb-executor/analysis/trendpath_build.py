#!/usr/bin/env python3
"""[C-TREND-PATH v1, 07-14] THE WINDOW-1 DRIFT ATLAS — where markets like
this one usually travel. AIM/TIMING MISSES fifth closing design; the axis
none of the four prior attempts carried: the fitted PRICE PATH across
window 1, per class.

OPERATOR RULING (recorded verbatim in the vault, binding here): option A
rejected — no completion fills mid-game; window-1 value is the thesis;
flatten-kept remains the only post-bell action. The atlas exists so BOTH
legs are placed along the path at discovery and the pair completes INSIDE
the window.

PAGES: category x discovery-price cell x side. Each page:
  path[slice]   p25/p50/p75 of (last - discovery) cents at each
                minutes-before-onset slice
  bottom        p25/p50/p75 of the deepest W1 excursion below discovery,
                and the median minutes-before-onset it occurs
SOURCES: G9 minute-candles (< Jul 10, era-admissible tour, walk-forward) ·
live-era local tape for ITF (BRANDED live_era, hardening daily).
Honest clock: onset = the -0k flow-step rule on per-minute volume.
Discovery = median price of the first tape hour (the v2 convention)."""
import json, gzip, sys, bisect
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parent.parent
WS = ROOT.parent
OUT = WS / ".claude/trendpath/ATLAS_V1.json"
SLICES = [480, 360, 240, 180, 120, 90, 60, 45, 30, 20, 10, 5]
CATS = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
        "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
        "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}

def pcell(px):
    return ("le25" if px <= 25 else "26_50" if px <= 50 else
            "51_75" if px <= 75 else "ge75")

def onset_of(vol_minutes):
    keys = sorted(vol_minutes)
    if not keys:
        return None
    base60 = sum(vol_minutes[m] for m in keys if m < keys[0] + 3600)
    need = max(8, 3.0 * base60 / 4.0)
    for m in keys:
        t15 = sum(vol_minutes.get(k, 0) for k in range(m - 14 * 60, m + 60, 60))
        act = sum(1 for k in range(m - 14 * 60, m + 60, 60) if k in vol_minutes)
        fwd = sum(vol_minutes.get(k, 0) for k in range(m + 60, m + 31 * 60, 60))
        if act >= 5 and t15 >= need and fwd >= need:
            return m
    return None

def add_leg(pages, cat, series, vol_minutes):
    """series: sorted [(minute_ts, last, low)] ; vol_minutes: {minute: prints}"""
    if len(series) < 10:
        return
    on = onset_of(vol_minutes)
    if on is None:
        return
    t0 = series[0][0]
    if on <= t0 + 3600:
        return
    first_hr = sorted(x[1] for x in series if x[0] < t0 + 3600)
    if not first_hr:
        return
    disc = first_hr[len(first_hr) // 2]
    side = "leader" if disc >= 50 else "underdog"
    key = "%s|%s|%s" % (cat, side, pcell(int(disc)))
    P = pages[key]
    P["n"] += 1
    ts_ = [x[0] for x in series]
    for sl in SLICES:
        t = on - sl * 60
        if t < t0:
            continue
        j = bisect.bisect_right(ts_, t) - 1
        if j >= 0:
            P["path"][sl].append(series[j][1] - disc)
    pre = [(x[0], x[2]) for x in series if x[0] < on]
    if pre:
        bm, bp = min(pre, key=lambda x: x[1])
        P["bottom_depth"].append(max(0.0, disc - bp))
        P["bottom_t"].append((on - bm) / 60.0)

def build_tour(pages):
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(ROOT / "data/durable/g9_candles.parquet")
    per_tk = defaultdict(list)
    for rg in range(pf.num_row_groups):
        t = pf.read_row_group(rg, columns=["ticker", "end_period_ts",
                                           "price_close", "price_low",
                                           "volume_fp"]).to_pydict()
        for tk, ts, pc, plo, v in zip(t["ticker"], t["end_period_ts"],
                                      t["price_close"], t["price_low"],
                                      t["volume_fp"]):
            if not tk or "MATCH-" not in tk:
                continue
            cat = CATS.get(tk.split("-")[0])
            if cat in (None, "ITF_M", "ITF_W"):
                continue
            try:
                tts = ts.timestamp() if hasattr(ts, "timestamp") else float(ts)
            except Exception:
                continue
            if datetime.fromtimestamp(tts, tz=timezone.utc
                                      ).strftime("%Y-%m-%d") >= "2026-07-10":
                continue
            try:
                per_tk[tk].append((int(tts // 60) * 60, float(pc), float(plo),
                                   float(v or 0)))
            except Exception:
                continue
    for tk, rows in per_tk.items():
        rows.sort()
        cat = CATS.get(tk.split("-")[0])
        # candle prices may be dollars (<=1) or cents; normalize to cents
        series = [(m, c if c > 1 else c * 100, l if l > 1 else l * 100)
                  for m, c, l, _ in rows]
        vol = {m: max(1, int(v)) for m, _, _, v in rows if v}
        add_leg(pages, cat, series, vol)

def build_itf(pages):
    TR = ROOT / "analysis/trades"
    per_tk = defaultdict(list)
    for f in TR.glob("KXITF*"):
        tk = f.name.split(".csv")[0]
        op = gzip.open if f.name.endswith(".gz") else open
        try:
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                for ln in fh:
                    p = ln.split(",")
                    if len(p) < 3:
                        continue
                    try:
                        d, t, ap = p[0].split(" ")
                        y, mo, dy = d.split("-")
                        hh, mm = t.split(":")[:2]
                        ts = datetime(int(y), int(mo), int(dy),
                                      int(hh) % 12 + (12 if ap == "PM" else 0),
                                      int(mm), tzinfo=ET).timestamp()
                        per_tk[tk].append((int(ts // 60) * 60, float(p[2])))
                    except Exception:
                        continue
        except OSError:
            continue
    for tk, rows in per_tk.items():
        rows.sort()
        cat = CATS.get(tk.split("-")[0])
        mins = defaultdict(list)
        for m, px in rows:
            mins[m].append(px)
        series = [(m, v[-1], min(v)) for m, v in sorted(mins.items())]
        vol = {m: len(v) for m, v in mins.items()}
        add_leg(pages, cat, series, vol)

def q(xs, p):
    xs = sorted(xs)
    return round(xs[int(len(xs) * p)], 1) if xs else None

pages = defaultdict(lambda: {"n": 0, "path": defaultdict(list),
                             "bottom_depth": [], "bottom_t": []})
print("atlas: tour from g9_candles ...", flush=True)
build_tour(pages)
print("atlas: ITF from live-era tape (BRANDED) ...", flush=True)
build_itf(pages)

atlas = {"meta": {"built": "2026-07-14",
                  "lineage": ["AIM/TIMING MISSES attempt 5 — the path axis",
                              "G9 minute-candles < 2026-07-10 (tour, walk-forward)",
                              "live-era local tape (ITF, BRANDED, hardening)",
                              "-0k flow-step onset; discovery = first-hour median"],
                  "slices_min_before_onset": SLICES,
                  "operator_ruling": "option A rejected — no completion fills "
                                     "mid-game; window-1 value is the thesis; "
                                     "flatten-kept remains the only post-bell action"},
         "pages": {}}
for key, P in pages.items():
    if P["n"] < 8:
        atlas["pages"][key] = {"n": P["n"], "verdict": "REFUSE_THIN"}
        continue
    atlas["pages"][key] = {
        "n": P["n"], "verdict": "PATH",
        "branded": ("live_era" if key.startswith("ITF") else "g9_train"),
        "path": {str(sl): {"p25": q(v, 0.25), "p50": q(v, 0.50),
                           "p75": q(v, 0.75), "n": len(v)}
                 for sl, v in P["path"].items() if len(v) >= 8},
        "bottom": {"depth_p25": q(P["bottom_depth"], 0.25),
                   "depth_p50": q(P["bottom_depth"], 0.50),
                   "depth_p75": q(P["bottom_depth"], 0.75),
                   "t_med_min": q(P["bottom_t"], 0.50)}}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(atlas, indent=1), encoding="utf-8")
n_path = sum(1 for p in atlas["pages"].values() if p.get("verdict") == "PATH")
print("ATLAS_V1: %d pages (%d PATH) -> %s" % (len(atlas["pages"]), n_path, OUT))
sh = atlas["pages"].get("ITF_W|underdog|le25")
print("SHIMIC page (ITF_W|underdog|le25):", json.dumps(sh)[:400] if sh else "MISSING")
