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
Discovery = median price of the first tape hour (the v2 convention).

[C-CONTENTION-LAW v1, 07-15] every page gains one number: CONTENTION =
the achievable swing at the path entry -- the validated exit band (8c, the
live band, a fitted anchor per section 0A) reachable from the page's
path-aim, against the ride-loss at that entry weighted by the page's win
partition OF ENTERED LEGS (legs whose path actually dipped to the aim --
adverse selection kept, never averaged away). Exit reach = band-touch
before onset (the week-regrade convention); win = terminal-tape proxy;
entry fill probability annotated from the reach law (LAW.json) at the
page's median flow/residency. FITTED AND CITED, NEVER DECREED (#11);
NO-OPINION on thin tiers (n_entry < 8). Recomputed as pages harden daily
(the 12:05a cron); operator understanding recorded verbatim in the vault:
reaching exits in window 1 is the thesis; favorites with higher swings
entered at the path are in great contention; high-priced favorites get
dropped where the path shows no promise."""
import json, gzip, sys, bisect, math
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
BAND = 8  # the live validated exit band -- a fitted anchor, cited, not tuned here
_LAWP = WS / ".claude/takerreach/LAW.json"
LAW = (json.loads(_LAWP.read_text(encoding="utf-8"))["law"]
       if _LAWP.exists() else {})
THR9 = {"ITF_M": 6, "ITF_W": 6, "ATP_CHALL": 16, "WTA_CHALL": 16}

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

def add_leg(pages, cat, series, vol_minutes, tk=None):
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
    pre3 = [x for x in series if x[0] < on]
    if pre3:
        bi = min(range(len(pre3)), key=lambda i: pre3[i][2])
        bm, bp = pre3[bi][0], pre3[bi][2]
        P["bottom_depth"].append(max(0.0, disc - bp))
        P["bottom_t"].append((on - bm) / 60.0)
        # [C-CONTENTION-LAW] per-leg primitives: for each integer entry
        # depth d (1..30 below THIS leg's discovery), did the path dip to
        # the aim (entry), and after the FIRST touch did the pre-onset tape
        # rebound to aim+BAND (exit reach, band-touch convention)? Plus the
        # terminal-tape win proxy and the flow/residency the reach law needs.
        win = 1 if series[-1][1] >= 50 else 0
        suff = [0.0] * len(pre3)
        mx = -1e9
        for i in range(len(pre3) - 1, -1, -1):
            mx = max(mx, pre3[i][1])
            suff[i] = mx
        reb, runmin, dseen = set(), 1e9, 0
        for i, (_, _, lo_) in enumerate(pre3):
            if lo_ < runmin:
                runmin = lo_
                dh = int(disc - runmin)
                while dseen < min(30, dh):
                    dseen += 1
                    if suff[i] >= disc - dseen + BAND:
                        reb.add(dseen)
        p30 = sum(vol_minutes.get(k, 0)
                  for k in range(int(bm) - 29 * 60, int(bm) + 60, 60))
        P["disc"].append(disc)
        P["res_h"].append((on - t0) / 3600.0)
        P["p30"].append(p30)
        P["legs"].append((disc, win, dseen, reb))
        # [C-TAPE-GATE Part 2, operator word 07-14 — THE TIMING RECUT]
        # bottom ABSOLUTE minute + ticker kept so the emit phase can join
        # the evidence-gun clock (dual stamps, live era)
        P["bottoms_abs"].append((tk, bm))
        # [C-W1-LIBRARY Part 2] the cohort record: category x price band x
        # realized-volume trajectory -> the W1 story
        hour_p = sum(v for m, v in vol_minutes.items() if m < t0 + 3600)
        LIB.append((cat, disc, hour_p, max(0.0, disc - bp),
                    (on - bm) / 60.0, sum(vol_minutes.values()), tk, bm))

ORIENT = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # cat -> bucket -> [n, dog_rise]
LIB = []   # [C-W1-LIBRARY] per-leg cohort records: (cat, disc, hour_prints,
           # bottom_depth, bottom_t_min, total_prints)

def orient_fit(per_series, vol_of):
    """[C-PAIR-LAW AMENDMENT, 07-15 — the seesaw is the thesis] fit the
    directional read per event pair, walk-forward: which side is the
    riser, from the fitted tells on the DISCOVERY (first-tape-hour) tape:
      f_drift  sign of (hour-end last − first-hour-median) on the dog
      f_range  the dog's hour-end position in the hour's [low, high]
      f_flow   the dog's share of the pair's first-hour prints
    (spread asymmetry: SILENT in this corpus — candles carry no book;
    named, not faked.) Truth = the side whose pre-onset drift from its
    discovery is positive by ≥2¢ (no clear riser → the event doesn't
    grade). Buckets with n<10 are NO-CALL downstream."""
    by_ev = defaultdict(dict)
    for tk, series in per_series.items():
        by_ev[tk.rsplit("-", 1)[0]][tk] = series
    for ev, legs in by_ev.items():
        if len(legs) != 2:
            continue
        cat = CATS.get(ev.split("-")[0])
        if not cat:
            continue
        stats = {}
        ok = True
        for tk, series in legs.items():
            if len(series) < 10:
                ok = False
                break
            t0 = series[0][0]
            hour = [x for x in series if x[0] < t0 + 3600]
            if len(hour) < 3:
                ok = False
                break
            med = sorted(x[1] for x in hour)[len(hour) // 2]
            vol = vol_of.get(tk, {})
            on = onset_of(vol)
            if on is None or on <= t0 + 3600:
                ok = False
                break
            pre = [x for x in series if x[0] < on]
            stats[tk] = {"disc": med, "hour_last": hour[-1][1],
                         "hour_lo": min(x[2] for x in hour),
                         "hour_hi": max(x[1] for x in hour),
                         "hour_prints": sum(vol.get(m, 0) for m in
                                            range(int(t0), int(t0) + 3600,
                                                  60)),
                         "pre_last": pre[-1][1] if pre else None}
        if not ok or len(stats) != 2:
            continue
        tks = sorted(stats, key=lambda t: stats[t]["disc"])
        dog, ldr = tks[0], tks[1]
        if stats[dog]["disc"] >= 50 or stats[ldr]["disc"] < 50:
            continue
        dd = stats[dog]
        drift_d = (dd["pre_last"] or dd["disc"]) - dd["disc"]
        drift_l = (stats[ldr]["pre_last"] or stats[ldr]["disc"]) \
            - stats[ldr]["disc"]
        if abs(drift_d) < 2 and abs(drift_l) < 2:
            continue
        dog_rise = 1 if drift_d >= 2 or drift_l <= -2 else 0
        f1 = (1 if dd["hour_last"] - dd["disc"] >= 1 else
              -1 if dd["hour_last"] - dd["disc"] <= -1 else 0)
        span = max(1.0, dd["hour_hi"] - dd["hour_lo"])
        rp = (dd["hour_last"] - dd["hour_lo"]) / span
        f2 = "lo" if rp < 0.33 else ("mid" if rp < 0.67 else "hi")
        tot = dd["hour_prints"] + stats[ldr]["hour_prints"]
        fs = dd["hour_prints"] / float(tot) if tot else 0.5
        f3 = "lo" if fs < 0.4 else ("mid" if fs < 0.6 else "hi")
        b = ORIENT[cat]["%s|%s|%s" % (f1, f2, f3)]
        b[0] += 1
        b[1] += dog_rise

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
    per_series, vol_of = {}, {}
    for tk, rows in per_tk.items():
        rows.sort()
        cat = CATS.get(tk.split("-")[0])
        # candle prices may be dollars (<=1) or cents; normalize to cents
        series = [(m, c if c > 1 else c * 100, l if l > 1 else l * 100)
                  for m, c, l, _ in rows]
        vol = {m: max(1, int(v)) for m, _, _, v in rows if v}
        per_series[tk], vol_of[tk] = series, vol
        add_leg(pages, cat, series, vol, tk=tk)
    orient_fit(per_series, vol_of)

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
    per_series, vol_of = {}, {}
    for tk, rows in per_tk.items():
        rows.sort()
        cat = CATS.get(tk.split("-")[0])
        mins = defaultdict(list)
        for m, px in rows:
            mins[m].append(px)
        series = [(m, v[-1], min(v)) for m, v in sorted(mins.items())]
        vol = {m: len(v) for m, v in mins.items()}
        per_series[tk], vol_of[tk] = series, vol
        add_leg(pages, cat, series, vol, tk=tk)
    orient_fit(per_series, vol_of)

def q(xs, p):
    xs = sorted(xs)
    return round(xs[int(len(xs) * p)], 1) if xs else None

def contention_of(P, cat):
    """[C-CONTENTION-LAW v1] the page's one number, fitted: at each bottom
    quantile depth d, among legs whose path ENTERED (dipped >= d):
    p_exit = band-touch rate, p_win = win partition of those entered legs;
    E/share at the page-median discovery = p_exit*BAND +
    (1-p_exit)*(p_win*(100-aim) - (1-p_win)*aim); yield% = 100*E/aim.
    Tiers with n_entry < 8 are omitted (NO-OPINION downstream). The live
    selector recomputes yield at the leg's ACTUAL discovery from these
    primitives; the reach law prices the entry fill as an annotation."""
    legs = P.get("legs") or []
    if len(legs) < 8:
        return None
    discs = sorted(x[0] for x in legs)
    disc_med = discs[len(discs) // 2]
    res_s = sorted(P.get("res_h") or [4.0])
    res_med = res_s[len(res_s) // 2]
    p30s = sorted(P.get("p30") or [])
    p30_med = p30s[len(p30s) // 2] if p30s else None
    thr = THR9.get(cat)
    fb = None
    if thr and p30_med is not None:
        r = p30_med / float(thr)
        fb = "quiet" if r < 0.25 else ("warm" if r < 1.0 else "open")
    tiers = {}
    for tq, pp in (("p25", 0.25), ("p50", 0.50), ("p75", 0.75)):
        dq = q(P["bottom_depth"], pp)
        if not dq or dq < 1:
            continue
        d = int(round(dq))
        ent = [x for x in legs if x[2] >= d]
        if len(ent) < 8:
            continue
        p_exit = sum(1 for x in ent if d in x[3]) / float(len(ent))
        p_win = sum(1 for x in ent if x[1]) / float(len(ent))
        aim = max(1, int(round(disc_med - d)))
        ev = p_exit * BAND + (1 - p_exit) * (p_win * (100 - aim)
                                             - (1 - p_win) * aim)
        t = {"d": d, "n_entry": len(ent), "p_exit": round(p_exit, 3),
             "p_win_entry": round(p_win, 3),
             "yield_at_med_pct": round(100.0 * ev / aim, 1)}
        if fb and LAW:
            Lw = LAW.get("%s|%s" % (cat, fb))
            if Lw:
                rt = Lw["rate_per_hr"].get(str(min(max(d, 1), 20)), 0.0)
                t["entry_fill_p"] = round(1 - math.exp(-rt * res_med), 3)
                t["flow_med"] = fb
        tiers[tq] = t
    if not tiers:
        return None
    return {"band": BAND, "disc_med": disc_med,
            "tiers": tiers,
            "best_yield_at_med_pct": max(v["yield_at_med_pct"]
                                         for v in tiers.values()),
            "cited": ("exit=band-touch pre-onset (week-regrade convention); "
                      "win=terminal-tape proxy; ride-loss weighted by the "
                      "win partition of ENTERED legs (adverse selection "
                      "kept); entry fill = reach law LAW.json")}

pages = defaultdict(lambda: {"n": 0, "path": defaultdict(list),
                             "bottom_depth": [], "bottom_t": [],
                             "disc": [], "res_h": [], "p30": [],
                             "legs": [], "bottoms_abs": []})
print("atlas: tour from g9_candles ...", flush=True)
build_tour(pages)
print("atlas: ITF from live-era tape (BRANDED) ...", flush=True)
build_itf(pages)

atlas = {"meta": {"built": "2026-07-15",
                  "lineage": ["AIM/TIMING MISSES attempt 5 — the path axis",
                              "G9 minute-candles < 2026-07-10 (tour, walk-forward)",
                              "live-era local tape (ITF, BRANDED, hardening)",
                              "-0k flow-step onset; discovery = first-hour median",
                              "C-CONTENTION-LAW v1: contention fitted per page "
                              "(band-touch exit; entered-legs win partition; "
                              "reach-law entry fill) — never decreed"],
                  "operator_understanding": "reaching exits in window 1 is the "
                      "thesis; favorites with higher swings entered at the path "
                      "are in great contention; high-priced favorites get "
                      "dropped where the path shows no promise",
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
                   "t_med_min": q(P["bottom_t"], 0.50)},
        "contention": contention_of(P, key.split("|")[0]),
        "timing_gun": gun_columns(P)}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(atlas, indent=1), encoding="utf-8")
n_path = sum(1 for p in atlas["pages"].values() if p.get("verdict") == "PATH")
print("ATLAS_V1: %d pages (%d PATH) -> %s" % (len(atlas["pages"]), n_path, OUT))
sh = atlas["pages"].get("ITF_W|underdog|le25")
print("SHIMIC page (ITF_W|underdog|le25):", json.dumps(sh)[:400] if sh else "MISSING")
n_con = sum(1 for p in atlas["pages"].values()
            if p.get("verdict") == "PATH" and p.get("contention"))
print("CONTENTION: %d/%d PATH pages carry the fitted number" % (n_con, n_path))
# [C-PAIR-LAW AMENDMENT] the orientation table: fitted tells -> riser call.
# v1 operating point (NAMED, its own n>=300 clock before money): bucket
# n>=10, rate >=0.65 -> dog riser / <=0.35 -> leader riser, else NO-CALL.
orient = {"meta": {"built": atlas["meta"]["built"],
                   "tells": ["f_drift (hour-end last vs first-hour median)",
                             "f_range (hour-end pos in hour range)",
                             "f_flow (dog share of pair first-hour prints)",
                             "spread asymmetry: SILENT in this corpus (no "
                             "book in candles) — named, not faked"],
                   "truth": "pre-onset drift >= 2c on either side",
                   "operating_point": {"min_n": 10, "call_hi": 0.65,
                                       "call_lo": 0.35},
                   "clock": "orientation accuracy accrues its own n>=300 "
                            "before it ever touches money"},
          "cats": {}}
for cat9, bk in ORIENT.items():
    orient["cats"][cat9] = {
        b: {"n": v[0], "dog_rise_rate": round(v[1] / float(v[0]), 3)}
        for b, v in bk.items() if v[0] >= 10}
(WS / ".claude/trendpath/ORIENT_V1.json").write_text(
    json.dumps(orient, indent=1), encoding="utf-8")
n_ob = sum(len(v) for v in orient["cats"].values())
print("ORIENT_V1: %d callable buckets across %d cats"
      % (n_ob, len(orient["cats"])))
# [C-W1-LIBRARY v1 Part 2, 07-14 — the operator directive, verbatim in the
# vault: "we aren't working with nothing — this is all waiting for us"]
# THE W1-COHORT LIBRARY: cat x price band x realized-volume trajectory ->
# the cohort's W1 story (dip frequency, depth percentiles, dip timing,
# never-wake probability). AXIS HONESTY: timing rides the -0k onset clock
# (the CLOCK X-CAL adjudication found gun-vs-onset skew up to hours on
# ITF — the timing axis is MIS-ANCHORED for live use until the recut);
# the minutes-to-scheduled axis is 'na' for the tour corpus (no archive
# schedule joins) — GAP named, live-era enrichment queued.
vol_cuts = {}
by_cat = defaultdict(list)
for rec9 in LIB:
    by_cat[rec9[0]].append(rec9[2])
for cat9, xs in by_cat.items():
    xs = sorted(xs)
    vol_cuts[cat9] = [xs[len(xs) // 3], xs[2 * len(xs) // 3]]
lib_cells = defaultdict(lambda: {"n": 0, "dips": 0, "depths": [],
                                 "timings": [], "sleep": 0})
for cat9, disc9, hp9, bd9, bt9, tp9, tk9, bm9 in LIB:
    c1, c2 = vol_cuts.get(cat9, [5, 20])
    vb9 = "lo" if hp9 <= c1 else ("mid" if hp9 <= c2 else "hi")
    key9 = "%s|%s|%s" % (cat9, pcell(int(disc9)), vb9)
    cell9 = lib_cells[key9]
    cell9["n"] += 1
    if bd9 >= 3:
        cell9["dips"] += 1
        cell9["depths"].append(bd9)
        cell9["timings"].append(bt9)
    if tp9 < 10:
        cell9["sleep"] += 1
    g9 = GUNS.get((tk9 or "").rsplit("-", 1)[0]) if tk9 else None
    if g9 is not None:
        ga9 = cell9.setdefault("gun", {"n": 0, "lawful": 0, "pre": []})
        ga9["n"] += 1
        if bm9 < g9:
            ga9["lawful"] += 1
            ga9["pre"].append((g9 - bm9) / 60.0)
library = {"meta": {"built": atlas["meta"]["built"],
                    "axes": "cat|pcell|vol_band (first-hour prints, fitted "
                            "terciles per cat)",
                    "vol_cuts": vol_cuts,
                    "dip_def": "bottom >= 3c below discovery",
                    "never_wake_def": "total prints < 10 (v1, named)",
                    "timing_axis": "-0k onset clock — MIS-ANCHORED for "
                                   "live use per CLOCK-XCAL; recut queued",
                    "tts_axis": "na for tour corpus — GAP, live-era "
                                "enrichment queued"},
           "cells": {}}
for key9, c9 in lib_cells.items():
    g9x = c9.get("gun")
    c9["gun_axis"] = ({"n_dual": g9x["n"],
                       "lawful_share": round(g9x["lawful"] / float(g9x["n"]), 3),
                       "pre_gun_med_min": q(g9x["pre"], 0.50)}
                      if g9x and g9x["n"] >= 8 else None)
    if c9["n"] < 8:
        continue
    library["cells"][key9] = {
        "n": c9["n"],
        "dip_freq": round(c9["dips"] / float(c9["n"]), 3),
        "depth_p25_50_75": [q(c9["depths"], 0.25), q(c9["depths"], 0.50),
                            q(c9["depths"], 0.75)],
        "dip_t_med_min_before_0k": q(c9["timings"], 0.50),
        "gun_axis": c9.get("gun_axis"),
        "never_wake_p": round(c9["sleep"] / float(c9["n"]), 3)}

# [C-TAPE-GATE Part 2] evidence guns from every day-log on disk (the gun
# clock; live era only -- tour has no gun archive, its pages keep the -0k
# axis with the caveat)
import glob as _g
GUNS = {}
_BURST = ("tape_latch", "price_divergence")
for _lp in sorted(_g.glob(str(ROOT / "logs/live_v3_*.jsonl"))):
    try:
        for _ln in open(_lp, encoding="utf-8", errors="replace"):
            if '"gun_fired"' not in _ln:
                continue
            try:
                _o = json.loads(_ln)
            except ValueError:
                continue
            _d = _o.get("details") or {}
            _ev = _d.get("event", "")
            if _ev and _d.get("source") not in _BURST and _ev not in GUNS:
                GUNS[_ev] = _o["ts_epoch"]
    except OSError:
        continue

def gun_columns(P):
    """gun-axis timing per page: dual-stamp legs only; lawful_share =
    fraction whose bottom lands PRE-gun."""
    ts9 = []
    n_dual = 0
    lawful = 0
    for tk9, bm9 in P.get("bottoms_abs", []):
        if not tk9:
            continue
        g9 = GUNS.get(tk9.rsplit("-", 1)[0])
        if g9 is None:
            continue
        n_dual += 1
        if bm9 < g9:
            lawful += 1
            ts9.append((g9 - bm9) / 60.0)
    if n_dual < 8:
        return None
    return {"n_dual": n_dual,
            "lawful_share": round(lawful / float(n_dual), 3),
            "bottom_pre_gun_min_p25_50_75": [q(ts9, 0.25), q(ts9, 0.50),
                                             q(ts9, 0.75)],
            "axis": "evidence_gun (C-TAPE-GATE recut 07-14)"}

(WS / ".claude/trendpath/LIBRARY_V1.json").write_text(
    json.dumps(library, indent=1), encoding="utf-8")
print("LIBRARY_V1: %d cohort cells (n>=8) from %d legs"
      % (len(library["cells"]), len(LIB)))
for k9 in ("ITF_W|leader|ge75", "ITF_W|underdog|le25"):
    c9 = (atlas["pages"].get(k9) or {}).get("contention")
    print("  %s -> %s" % (k9, json.dumps(c9)[:360] if c9 else "NO-OPINION"))

# [C-TAPE-GATE Part 2] THE LAWFUL HARVEST MAP: where the dips live before
# the gun, per category -- the fitted "when" every aim consults forward.
hm = defaultdict(lambda: {"n": 0, "lawful": 0, "pre": []})
for cat9, disc9, hp9, bd9, bt9, tp9, tk9, bm9 in LIB:
    g9 = GUNS.get((tk9 or "").rsplit("-", 1)[0]) if tk9 else None
    if g9 is None:
        continue
    hm[cat9]["n"] += 1
    if bm9 < g9:
        hm[cat9]["lawful"] += 1
        hm[cat9]["pre"].append((g9 - bm9) / 60.0)
HM = ["THE LAWFUL HARVEST MAP (gun clock; dual-stamp legs; recut 07-14)",
      ""]
for cat9 in sorted(hm):
    h9 = hm[cat9]
    HM.append("%-10s n_dual=%d | lawful_share=%.0f%% | pre-gun bottom "
              "p25/50/75 = %s / %s / %s min"
              % (cat9, h9["n"], 100.0 * h9["lawful"] / h9["n"],
                 q(h9["pre"], 0.25), q(h9["pre"], 0.50), q(h9["pre"], 0.75)))
(WS / ".claude/trendpath/LAWFUL_HARVEST_MAP.txt").write_text(
    "\n".join(HM), encoding="utf-8")
print("\n".join(HM))
