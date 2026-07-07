#!/usr/bin/env python3
"""PAIR-STORY 2026-07-07 (re-dispatch; the 07-06 run died with no artifact).
READ-ONLY corpus study. Honest axis: corpus bells (LATCH-CAL, 25m residual gate,
as banked by the shape-corpus accumulator); observed_starts preferred where a
suffix+day match exists (13 rows at dispatch, coverage reported). Book =
premarket_ticks 5-level gz CSVs; prints = analysis/trades tape (conservative
fill convention: a level is fillable only where the tape PRINTED at/below it).

Per detected-bell pair, T-8h -> bell:
 1 joint buyability (best jointly-fillable combined, T, dwell; floors per cat/bucket)
 2 divot sequence (fav-first %, inter-divot lag, P(leg2 within 15/30/60m))
 3 seesaw mechanics (1-min mid-delta cross-corr, lag structure)
 4 canonical shapes (median+envelope per cat/bucket, RAMP split, gap number)
Conventions (stated): fillable(t) = min print in trailing 15min (a resting bid
at that level, posted before, fills within 15min); divot moment = minute whose
min print <= window_low + 2c; fav = higher first joint mid; bucket = fav
first-mid 20c band 0-4; mid used ONLY as mechanics measurement (0A: analysis
anchors on printed/bid/ask — the joint-buyability deliverable is prints-only).
Resume: per-pair records append to results.jsonl keyed by event; restart skips
done events. Heartbeat: /root/pair_story_progress.json every 25 pairs.
Usage: python3 pair_story_20260707.py [--aggregate-only]"""
import csv, gzip, io, json, math, os, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
TICKS = ROOT / "analysis" / "premarket_ticks"
TRADES = ROOT / "analysis" / "trades"
OUT = Path("/root/pair_story_20260707")
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "results.jsonl"
HEART = Path("/root/pair_story_progress.json")
ET = timezone(timedelta(hours=-4))
W8H = 8 * 3600
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}


def cat_of(ev):
    for k, v in CAT.items():
        if ev.startswith(k):
            return v
    return None


_dc = {}
def pts(s):
    try:
        d, t, ap = s.split(" ")
        if d not in _dc:
            y, mo, dy = d.split("-")
            _dc[d] = datetime(int(y), int(mo), int(dy), tzinfo=ET).timestamp()
        hh, mm, ss = t.split(":")
        return _dc[d] + (int(hh) % 12 + (12 if ap == "PM" else 0)) * 3600 + int(mm) * 60 + int(ss)
    except Exception:
        return None


def open_any(base):
    for suf in (".csv", ".csv.gz"):
        f = base.parent / (base.name + suf)
        if f.exists():
            return (gzip.open if suf.endswith("gz") else open)(f, "rt", encoding="utf-8", errors="replace")
    return None


def load_ticks_minute(tk, t0, t1):
    """1-min grid dicts: bid, ask, mid (last obs per minute) within [t0,t1]."""
    fh = open_any(TICKS / tk)
    if fh is None:
        return None
    bid, ask, mid = {}, {}, {}
    with fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 27:
                continue
            t = pts(p[0])
            if t is None or t < t0 or t > t1:
                continue
            m = int(t // 60) * 60
            try:
                b = int(p[2]) if p[2] else None
                a = int(p[12]) if p[12] else None
            except ValueError:
                continue
            if b:
                bid[m] = b
            if a:
                ask[m] = a
            if b and a:
                mid[m] = (b + a) / 2.0
    return {"bid": bid, "ask": ask, "mid": mid}


def load_prints_minute(tk, t0, t1):
    """per-minute (min_price, n_prints) within [t0,t1]."""
    fh = open_any(TRADES / tk)
    if fh is None:
        return {}
    out = {}
    with fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 4:
                continue
            t = pts(p[0])
            if t is None or t < t0 or t > t1:
                continue
            try:
                px = int(p[2]); ct = float(p[3])
            except ValueError:
                continue
            m = int(t // 60) * 60
            cur = out.get(m)
            out[m] = (px if cur is None else min(cur[0], px),
                      (0 if cur is None else cur[1]) + ct)
    return out


def fillable_series(prints, minutes, trail=15):
    """fillable(t) = min print in trailing `trail` minutes; None if no print."""
    out = {}
    win = []
    for m in minutes:
        pm = prints.get(m)
        win.append((m, pm[0] if pm else None))
        cutoff = m - trail * 60
        win = [(t, v) for t, v in win if t >= cutoff]
        vals = [v for _, v in win if v is not None]
        out[m] = min(vals) if vals else None
    return out


def corr(xs, ys):
    n = len(xs)
    if n < 10:
        return None
    mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def build_universe():
    bells = {}
    for f in sorted((ROOT / "data" / "shape_corpus").glob("samples_*.jsonl")):
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            tk = d.get("tk", ""); b = d.get("bell")
            if tk and b:
                bells[tk.rsplit("-", 1)[0]] = int(b)
    obs_used = 0
    try:
        con = sqlite3.connect(str(ROOT / "tennis.db"))
        rows = con.execute("SELECT kalshi_ticker, first_inplay_at FROM observed_starts").fetchall()
        for suf, ts in rows:
            try:
                obs_ep = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            except Exception:
                continue
            hits = [ev for ev in bells if ev.endswith(suf) and abs(bells[ev] - obs_ep) < 6 * 3600]
            if len(hits) == 1:
                bells[hits[0]] = int(obs_ep); obs_used += 1
        con.close()
    except Exception:
        pass
    legs = defaultdict(list)
    for f in TICKS.glob("*.csv*"):
        tk = f.name.replace(".csv.gz", "").replace(".csv", "")
        legs[tk.rsplit("-", 1)[0]].append(tk)
    pairs = [(ev, sorted(tks)) for ev, tks in legs.items()
             if len(tks) == 2 and ev in bells and cat_of(ev)]
    return sorted(pairs), bells, obs_used, len(legs)


def per_pair(ev, tks, bell):
    t1 = bell; t0 = bell - W8H
    minutes = list(range(int(t0 // 60) * 60, int(t1 // 60) * 60 + 60, 60))
    A = load_ticks_minute(tks[0], t0, t1)
    B = load_ticks_minute(tks[1], t0, t1)
    if not A or not B or len(A["mid"]) < 30 or len(B["mid"]) < 30:
        return {"ev": ev, "skip": "thin_ticks"}
    first_m = next((m for m in minutes if m in A["mid"] and m in B["mid"]), None)
    if first_m is None:
        return {"ev": ev, "skip": "no_joint_minute"}
    fav_i = 0 if A["mid"][first_m] >= B["mid"][first_m] else 1
    fav, dog = (tks[fav_i], tks[1 - fav_i])
    F, D = (A, B) if fav_i == 0 else (B, A)
    fav_open = (F["mid"][first_m])
    bucket = min(4, int(fav_open // 20))
    pf = load_prints_minute(fav, t0, t1)
    pd = load_prints_minute(dog, t0, t1)
    ff = fillable_series(pf, minutes)
    fd = fillable_series(pd, minutes)

    # --- 1 joint buyability ---
    joint = {m: ff[m] + fd[m] for m in minutes if ff[m] is not None and fd[m] is not None}
    if not joint:
        return {"ev": ev, "skip": "no_joint_fillable", "cat": cat_of(ev), "bucket": bucket}
    best = min(joint.values())
    bestT = min(m for m, v in joint.items() if v == best)
    dwell97 = sum(1 for v in joint.values() if v <= 97)
    dwell_best2 = sum(1 for v in joint.values() if v <= best + 2)

    # --- 2 divots ---
    def lows(prints, fill):
        vals = [v for v in fill.values() if v is not None]
        if not vals:
            return None, []
        lo = min(vals)
        mins = [m for m in minutes if prints.get(m) and prints[m][0] <= lo + 2]
        return lo, mins
    lof, divf = lows(pf, ff)
    lod, divd = lows(pd, fd)
    div = None
    if divf and divd:
        fav_first = divf[0] <= divd[0]
        lag = (divd[0] - divf[0]) / 60.0
        first_leg, other = (divf, divd) if fav_first else (divd, divf)
        t_first = first_leg[0]
        within = {w: any(abs(m - t_first) <= w * 60 for m in other) for w in (15, 30, 60)}
        div = {"fav_first": fav_first, "lag_min": lag, "within": within,
               "n_divot_min_fav": len(divf), "n_divot_min_dog": len(divd)}

    # --- 3 seesaw ---
    common = [m for m in minutes if m in F["mid"] and m in D["mid"]]
    see = None
    if len(common) > 60:
        dm_f = [F["mid"][b] - F["mid"][a] for a, b in zip(common, common[1:]) if b - a == 60]
        dm_d = [D["mid"][b] - D["mid"][a] for a, b in zip(common, common[1:]) if b - a == 60]
        n = min(len(dm_f), len(dm_d))
        dm_f, dm_d = dm_f[:n], dm_d[:n]
        lag_corr = {}
        for L in (-5, -1, 0, 1, 5):
            if L >= 0:
                c = corr(dm_f[:n - L or None], dm_d[L:])
            else:
                c = corr(dm_f[-L:], dm_d[:n + L])
            lag_corr[str(L)] = round(c, 3) if c is not None else None
        see = {"corr": lag_corr, "n_min": n}

    # --- 4 shapes + ramp ---
    rate = {m: (pf.get(m, (0, 0))[1] + pd.get(m, (0, 0))[1]) for m in minutes}
    base = sorted(rate[m] for m in minutes[:240])
    base_med = base[len(base) // 2] if base else 0
    ramp = None
    thr = max(3 * base_med, 2)
    run = 0
    for m in minutes[240:]:
        run = run + 1 if rate[m] >= thr else 0
        if run >= 15:
            ramp = m - 14 * 60
            break
    def seg_stats(mm):
        sp = [ (F["ask"].get(m,0)-F["bid"].get(m,0)) for m in mm if F["ask"].get(m) and F["bid"].get(m)]
        pr = [rate[m] for m in mm]
        jj = [joint[m] for m in mm if m in joint]
        slope = None
        if len(jj) > 30:
            k = len(jj)
            xs = list(range(k)); mx = (k - 1) / 2; my = sum(jj) / k
            den = sum((x - mx) ** 2 for x in xs)
            slope = round(sum((x - mx) * (y - my) for x, y in zip(xs, jj)) / den * 60, 3) if den else None
        return {"spread_med": (sorted(sp)[len(sp)//2] if sp else None),
                "prints_per_min": round(sum(pr)/max(1,len(mm)), 2),
                "joint_slope_c_per_hr": slope}
    ramp_rel = ((ramp - bell) / 60.0) if ramp else None
    pre = seg_stats([m for m in minutes if ramp and m < ramp] or minutes)
    post = seg_stats([m for m in minutes if ramp and m >= ramp]) if ramp else None
    # shape path: 10-min grid T-8h..bell, 49 pts, fav/dog mid
    grid = []
    for i in range(49):
        m = int((t0 + i * 600) // 60) * 60
        grid.append([F["mid"].get(m), D["mid"].get(m)])
    mids = [ (F["mid"][m]+D["mid"][m]) for m in common ]
    med_comb_mid = sorted(mids)[len(mids)//2] if mids else None
    gap = round(med_comb_mid - best, 1) if med_comb_mid is not None else None

    return {"ev": ev, "cat": cat_of(ev), "bucket": bucket, "fav": fav.rsplit("-", 1)[-1],
            "fav_open": round(fav_open, 1), "bell": bell,
            "best_joint": best, "bestT_min_to_bell": round((bestT - bell) / 60.0, 1),
            "dwell97_min": dwell97, "dwell_best2_min": dwell_best2,
            "le97": best <= 97, "le95": best <= 95, "le93": best <= 93, "le90": best <= 90,
            "low_fav": lof, "low_dog": lod, "div": div, "see": see,
            "ramp_min_to_bell": (round(ramp_rel, 1) if ramp_rel is not None else None),
            "pre": pre, "post": post, "gap_midless_best": gap, "shape": grid}


def heartbeat(stage, done, total):
    json.dump({"ts": time.time(), "stage": stage, "done": done, "total": total},
              open(HEART, "w"))


def main():
    pairs, bells, obs_used, n_events_ticks = build_universe()
    done = set()
    if RESULTS.exists():
        for line in open(RESULTS, encoding="utf-8", errors="replace"):
            try:
                done.add(json.loads(line)["ev"])
            except Exception:
                pass
    total = len(pairs)
    meta = {"universe_pairs": total, "tick_events": n_events_ticks,
            "bell_events": len(bells), "observed_starts_used": obs_used,
            "resumed_done": len(done)}
    json.dump(meta, open(OUT / "meta.json", "w"), indent=1)
    print("UNIVERSE", json.dumps(meta), flush=True)
    if "--aggregate-only" not in sys.argv:
        with open(RESULTS, "a", encoding="utf-8") as out:
            for i, (ev, tks) in enumerate(pairs):
                if ev in done:
                    continue
                try:
                    rec = per_pair(ev, tks, bells[ev])
                except Exception as e:
                    rec = {"ev": ev, "skip": "error:" + str(e)[:120]}
                out.write(json.dumps(rec) + "\n")
                out.flush()
                if i % 25 == 0:
                    heartbeat("pairs", i, total)
        heartbeat("aggregate", total, total)
    # ---- aggregate ----
    recs = [json.loads(l) for l in open(RESULTS, encoding="utf-8", errors="replace")]
    ok = [r for r in recs if not r.get("skip")]
    json.dump({"n_records": len(recs), "n_ok": len(ok),
               "skips": dict(sorted(
                   __import__("collections").Counter(r["skip"].split(":")[0] for r in recs if r.get("skip")).items()))},
              open(OUT / "agg_counts.json", "w"), indent=1)

    def pct(v, p):
        v = sorted(v)
        return v[min(len(v) - 1, int(len(v) * p))] if v else None
    floors = {}
    for key in sorted(set((r["cat"], r["bucket"]) for r in ok)) + sorted(set((r["cat"], "ALL") for r in ok)):
        rows = [r for r in ok if r["cat"] == key[0] and (key[1] == "ALL" or r["bucket"] == key[1])]
        bj = [r["best_joint"] for r in rows]
        floors["%s|%s" % key] = {
            "n": len(rows), "p10": pct(bj, .10), "p25": pct(bj, .25),
            "med": pct(bj, .50), "p75": pct(bj, .75),
            "pct_le97": round(100 * sum(r["le97"] for r in rows) / len(rows), 1),
            "pct_le95": round(100 * sum(r["le95"] for r in rows) / len(rows), 1),
            "pct_le93": round(100 * sum(r["le93"] for r in rows) / len(rows), 1),
            "pct_le90": round(100 * sum(r["le90"] for r in rows) / len(rows), 1),
            "bestT_med_min": pct([r["bestT_min_to_bell"] for r in rows], .5),
            "dwell97_med": pct([r["dwell97_min"] for r in rows], .5),
            "gap_med": pct([r["gap_midless_best"] for r in rows if r["gap_midless_best"] is not None], .5),
        } if rows else {}
    divs = {}
    for cat in sorted(set(r["cat"] for r in ok)):
        rows = [r["div"] for r in ok if r["cat"] == cat and r.get("div")]
        if not rows:
            continue
        lags = [abs(d["lag_min"]) for d in rows]
        divs[cat] = {"n": len(rows),
                     "fav_first_pct": round(100 * sum(d["fav_first"] for d in rows) / len(rows), 1),
                     "lag_med_min": pct(lags, .5), "lag_p75": pct(lags, .75),
                     "p_within15": round(100 * sum(d["within"]["15"] if isinstance(list(d["within"].keys())[0],str) else d["within"][15] for d in rows) / len(rows), 1) if rows else None,
                     "p_within30": round(100 * sum((d["within"].get("30") if "30" in d["within"] else d["within"].get(30)) for d in rows) / len(rows), 1),
                     "p_within60": round(100 * sum((d["within"].get("60") if "60" in d["within"] else d["within"].get(60)) for d in rows) / len(rows), 1)}
    sees = {}
    for cat in sorted(set(r["cat"] for r in ok)):
        rows = [r["see"] for r in ok if r["cat"] == cat and r.get("see")]
        if not rows:
            continue
        c0 = [s["corr"].get("0") for s in rows if s["corr"].get("0") is not None]
        sees[cat] = {"n": len(rows), "corr_lag0_med": pct(c0, .5),
                     "corr_lag0_p25": pct(c0, .25), "corr_lag0_p75": pct(c0, .75),
                     "pct_strong_inverse": round(100 * sum(1 for c in c0 if c <= -0.3) / max(1, len(c0)), 1)}
    ramps = {}
    for cat in sorted(set(r["cat"] for r in ok)):
        rows = [r for r in ok if r["cat"] == cat]
        rr = [r["ramp_min_to_bell"] for r in rows if r["ramp_min_to_bell"] is not None]
        pre_s = [r["pre"]["joint_slope_c_per_hr"] for r in rows if r["pre"]["joint_slope_c_per_hr"] is not None]
        post_s = [r["post"]["joint_slope_c_per_hr"] for r in rows if r.get("post") and r["post"]["joint_slope_c_per_hr"] is not None]
        best_after_ramp = [1 for r in rows if r["ramp_min_to_bell"] is not None and r["bestT_min_to_bell"] > r["ramp_min_to_bell"]]
        ramps[cat] = {"n": len(rows), "ramp_detected_pct": round(100 * len(rr) / len(rows), 1),
                      "ramp_med_min_to_bell": pct(rr, .5),
                      "pre_slope_med": pct(pre_s, .5), "post_slope_med": pct(post_s, .5),
                      "best_after_ramp_pct": round(100 * len(best_after_ramp) / max(1, len(rr)), 1)}
    agg = {"floors": floors, "divots": divs, "seesaw": sees, "ramp": ramps, "meta": meta}
    json.dump(agg, open(OUT / "aggregate.json", "w"), indent=1)
    print("AGGREGATE WRITTEN", flush=True)

    # plots
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        cats = sorted(set(r["cat"] for r in ok))
        fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharex=True)
        for ax, cat in zip(axes.flat, cats):
            rows = [r for r in ok if r["cat"] == cat]
            xs = [(-8 * 60 + i * 10) for i in range(49)]
            for li, lab, col in ((0, "fav", "tab:blue"), (1, "dog", "tab:orange")):
                series = []
                for i in range(49):
                    vals = [r["shape"][i][li] for r in rows if r["shape"][i][li] is not None]
                    vals.sort()
                    series.append((vals[len(vals)//2], vals[len(vals)//4], vals[(3*len(vals))//4]) if vals else (None,)*3)
                med = [s[0] for s in series]
                ax.plot(xs, med, color=col, label=lab)
                ax.fill_between(xs, [s[1] for s in series], [s[2] for s in series],
                                color=col, alpha=0.15)
            rr = [r["ramp_min_to_bell"] for r in rows if r["ramp_min_to_bell"] is not None]
            if rr:
                rr.sort(); ax.axvline(rr[len(rr)//2], color="red", ls="--", lw=1, label="ramp med")
            ax.set_title("%s (n=%d)" % (cat, len(rows))); ax.legend(fontsize=7)
        fig.suptitle("Canonical pair shapes, T-8h to bell (median + IQR, honest axis)")
        fig.savefig(OUT / "shapes.png", dpi=110, bbox_inches="tight")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        data = [[r["best_joint"] for r in ok if r["cat"] == c] for c in cats]
        ax2.boxplot(data, tick_labels=cats, showfliers=False)
        ax2.axhline(97, color="red", ls="--", lw=1, label="97 ceiling")
        ax2.set_ylabel("best jointly-fillable combined (c)")
        ax2.set_title("Achievable floor per category (prints-only convention)")
        ax2.legend()
        fig2.savefig(OUT / "floors.png", dpi=110, bbox_inches="tight")
        print("PLOTS WRITTEN", flush=True)
    except Exception as e:
        print("PLOT SKIP:", e, flush=True)
    (OUT / "DONE").write_text(datetime.now(ET).isoformat())
    heartbeat("done", total, total)


if __name__ == "__main__":
    main()
