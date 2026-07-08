#!/usr/bin/env python3
"""EARLY-CANVAS STUDY 2026-07-08 (CONCEPTION HORIZON Part 2). READ-ONLY corpus.

Extends FLOOR-BY-HOUR beyond T-8h: window T-24h -> bell, hour bins -24..-1.
COVERAGE FIRST per (cat, hour-bin) -- the study says exactly how thin the early
tape is before it says anything else. Same universe/conventions as
pair_story_20260707.py (corpus bells LATCH-CAL via shape-corpus accumulator,
observed_starts preferred on suffix+day match; prints convention: fillable(t) =
min print in trailing 15min; quote-touch convention: ask+ask cross floor).

Per (cat, bin): quote lattice vs prints (spread, prints/min); joint fillability
BOTH conventions; drift information (across-pair corr of fav mid@bin vs
mid@bell + median |move to bell|); anti-selection on early sell-flow prints
(taker_side==no -- the our-resting-bid-fill proxy: outcome = bell mid - print).

FLOW-STATE (operator doctrine 2026-07-08: early quiet is VOLUME-conditional,
not time-conditional): per GAME, flow_onset = first minute with prints in >=5
of the trailing 15 minutes (the observable "this game's window is opening"
transition); floor_open = first minute joint prints-fillable <= 97 (and <= cat
S-line). Study population = pairs whose floor opened EARLY (before T-2h).
DISTRIBUTIONS (p10/25/50/75/90), never medians alone -- medians locate mass,
never fences.

Resume: results.jsonl keyed by event. Heartbeat /root/early_canvas_progress.json.
Usage: python3 early_canvas_20260708.py [--aggregate-only]"""
import gzip, json, math, sqlite3, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
TICKS = ROOT / "analysis" / "premarket_ticks"
TRADES = ROOT / "analysis" / "trades"
OUT = Path("/root/early_canvas_20260708")
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "results.jsonl"
HEART = Path("/root/early_canvas_progress.json")
ET = timezone(timedelta(hours=-4))
W24H = 24 * 3600
S_LINE = {"ITF_M": 84, "ITF_W": 84, "ATP_CHALL": 93, "WTA_CHALL": 90,
          "ATP_MAIN": 93, "WTA_MAIN": 93}
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


def load_prints(tk, t0, t1):
    """per-minute: (min_price, n_prints, [(price,count,taker_side), ...capped])"""
    fh = open_any(TRADES / tk)
    if fh is None:
        return {}
    out = {}
    with fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 5:
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
            if cur is None:
                out[m] = [px, 1, [(px, ct, p[4])]]
            else:
                cur[0] = min(cur[0], px)
                cur[1] += 1
                if len(cur[2]) < 30:
                    cur[2].append((px, ct, p[4]))
    return out


def fillable_series(prints, minutes, trail=15):
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


def pct(v, p):
    v = sorted(x for x in v if x is not None)
    return v[min(len(v) - 1, int(len(v) * p))] if v else None


def dist(v):
    return {"n": len([x for x in v if x is not None]),
            "p10": pct(v, .10), "p25": pct(v, .25), "p50": pct(v, .50),
            "p75": pct(v, .75), "p90": pct(v, .90)}


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
    t0 = bell - W24H; t1 = bell
    minutes = list(range(int(t0 // 60) * 60, int(t1 // 60) * 60 + 60, 60))
    A = load_ticks_minute(tks[0], t0, t1)
    B = load_ticks_minute(tks[1], t0, t1)
    if not A or not B:
        return {"ev": ev, "skip": "no_ticks"}
    joint_minutes = [m for m in minutes if m in A["mid"] and m in B["mid"]]
    if len(joint_minutes) < 30:
        return {"ev": ev, "skip": "thin_ticks", "cat": cat_of(ev),
                "joint_min": len(joint_minutes)}
    first_m = joint_minutes[0]
    fav_i = 0 if A["mid"][first_m] >= B["mid"][first_m] else 1
    fav, dog = (tks[fav_i], tks[1 - fav_i])
    F, D = (A, B) if fav_i == 0 else (B, A)
    pf = load_prints(fav, t0, t1)
    pd = load_prints(dog, t0, t1)
    ff = fillable_series(pf, minutes)
    fd = fillable_series(pd, minutes)
    # bell reference = last joint mid at/before bell
    bell_mid_f = F["mid"][joint_minutes[-1]]
    bell_mid_d = D["mid"][joint_minutes[-1]]

    # ---- per hour bin (-24..-1) ----
    bins = {}
    for h in range(-24, 0):
        b0 = bell + h * 3600; b1 = b0 + 3600
        mm = [m for m in minutes if b0 <= m < b1]
        jm = [m for m in mm if m in F["mid"] and m in D["mid"]]
        n_pr = sum((pf.get(m, [0, 0, []])[1] + pd.get(m, [0, 0, []])[1]) for m in mm)
        sp = [F["ask"][m] - F["bid"][m] for m in mm if m in F["ask"] and m in F["bid"]]
        jp = [ff[m] + fd[m] for m in mm if ff[m] is not None and fd[m] is not None]
        ja = [F["ask"][m] + D["ask"][m] for m in jm if m in F["ask"] and m in D["ask"]]
        # anti-selection: sell-flow prints (taker_side==no), outcome vs own bell mid
        sf = []
        for m in mm:
            for leg, prm, bm in ((fav, pf, bell_mid_f), (dog, pd, bell_mid_d)):
                for (px, ct, side) in prm.get(m, [0, 0, []])[2]:
                    if side == "no":
                        sf.append(round(bm - px, 1))
        bins[str(h)] = {
            "quoted_min": len(jm),
            "prints": n_pr,
            "spread_med_fav": pct(sp, .5),
            "joint_print_min": (min(jp) if jp else None),
            "joint_ask_min": (min(ja) if ja else None),
            "fav_mid_last": (F["mid"][jm[-1]] if jm else None),
            "sf_outcomes": sf[:50],
        }

    # ---- flow-state / floor-open ----
    def flow_onset():
        hist = []
        for m in minutes:
            has = 1 if (pf.get(m) or pd.get(m)) else 0
            hist.append((m, has))
            hist = [(t, v) for t, v in hist if t >= m - 15 * 60]
            if sum(v for _, v in hist) >= 5:
                return m
        return None
    onset = flow_onset()
    joint_fill = {m: ff[m] + fd[m] for m in minutes
                  if ff[m] is not None and fd[m] is not None}
    sline = S_LINE.get(cat_of(ev), 97)

    def first_le(level):
        for m in minutes:
            if joint_fill.get(m) is not None and joint_fill[m] <= level:
                return m
        return None
    fo97 = first_le(97)
    foS = first_le(sline)

    def flow_at(m):
        if m is None:
            return None
        w0 = m - 30 * 60
        npr = sum((pf.get(x, [0, 0, []])[1] + pd.get(x, [0, 0, []])[1])
                  for x in minutes if w0 <= x <= m)
        sp = [F["ask"][x] - F["bid"][x] for x in minutes
              if w0 <= x <= m and x in F["ask"] and x in F["bid"]]
        return {"rate30": round(npr / 30.0, 3), "spread_med": pct(sp, .5)}

    return {"ev": ev, "cat": cat_of(ev), "bell": bell,
            "fav": fav.rsplit("-", 1)[-1],
            "bell_mid_f": round(bell_mid_f, 1), "bell_mid_d": round(bell_mid_d, 1),
            "bins": bins,
            "flow_onset_min_to_bell": (round((onset - bell) / 60.0) if onset else None),
            "floor97_min_to_bell": (round((fo97 - bell) / 60.0) if fo97 else None),
            "floorS_min_to_bell": (round((foS - bell) / 60.0) if foS else None),
            "flow_at_floor97": flow_at(fo97),
            "flow_at_floorS": flow_at(foS),
            "flow_at_onset": flow_at(onset),
            "onset_to_floor97_min": (round((fo97 - onset) / 60.0)
                                     if (fo97 and onset) else None)}


def heartbeat(stage, done, total):
    json.dump({"ts": time.time(), "stage": stage, "done": done, "total": total},
              open(HEART, "w"))


def aggregate():
    recs = [json.loads(l) for l in open(RESULTS, encoding="utf-8", errors="replace")]
    ok = [r for r in recs if not r.get("skip")]
    counts = {"n_records": len(recs), "n_ok": len(ok),
              "skips": dict(Counter(r["skip"].split(":")[0] for r in recs if r.get("skip")))}
    cats = sorted(set(r["cat"] for r in ok))
    per_bin = {}
    for cat in cats:
        rows = [r for r in ok if r["cat"] == cat]
        for h in range(-24, 0):
            key = "%s|T%d" % (cat, h)
            bb = [r["bins"].get(str(h)) for r in rows]
            bb = [b for b in bb if b]
            quoted = [b["quoted_min"] for b in bb]
            with_q = [b for b in bb if b["quoted_min"] > 0]
            prints = [b["prints"] for b in bb]
            jp = [b["joint_print_min"] for b in bb if b["joint_print_min"] is not None]
            ja = [b["joint_ask_min"] for b in bb if b["joint_ask_min"] is not None]
            sf_all = [o for b in bb for o in b.get("sf_outcomes", [])]
            # drift info: fav mid at this bin vs at bell, across pairs
            xy = [(b["fav_mid_last"], r["bell_mid_f"]) for b, r in
                  zip([rr["bins"].get(str(h)) for rr in rows], rows)
                  if b and b.get("fav_mid_last") is not None]
            per_bin[key] = {
                "n_pairs": len(rows), "n_with_ticks_in_bin": len(bb),
                "n_with_quotes": len(with_q),
                "coverage_pct": round(100 * len(with_q) / max(1, len(rows)), 1),
                "quoted_min_dist": dist(quoted),
                "prints_per_min_p50": (round(pct(prints, .5) / 60.0, 4)
                                       if pct(prints, .5) is not None else None),
                "prints_per_min_p90": (round(pct(prints, .9) / 60.0, 4)
                                       if pct(prints, .9) is not None else None),
                "pct_bins_zero_prints": round(100 * sum(1 for p in prints if p == 0)
                                              / max(1, len(prints)), 1),
                "spread_med_fav_dist": dist([b["spread_med_fav"] for b in bb]),
                "jf_print_pct": round(100 * len(jp) / max(1, len(rows)), 1),
                "jf_print_le97_pct": round(100 * sum(1 for v in jp if v <= 97)
                                           / max(1, len(rows)), 1),
                "joint_print_min_dist": dist(jp),
                "joint_ask_min_dist": dist(ja),
                "drift_corr_mid_vs_bell": (round(corr([x for x, _ in xy], [y for _, y in xy]), 3)
                                           if len(xy) >= 10 else None),
                "drift_absmove_med": pct([abs(y - x) for x, y in xy], .5),
                "antisel": {"n_sf_prints": len(sf_all),
                            "outcome_dist": dist(sf_all),
                            "underwater_at_bell_pct": (round(100 * sum(1 for o in sf_all if o < 0)
                                                             / len(sf_all), 1) if sf_all else None)},
            }
    # flow-state populations
    flow = {}
    for cat in cats:
        rows = [r for r in ok if r["cat"] == cat]
        early97 = [r for r in rows if r["floor97_min_to_bell"] is not None
                   and r["floor97_min_to_bell"] < -120]
        late97 = [r for r in rows if r["floor97_min_to_bell"] is not None
                  and r["floor97_min_to_bell"] >= -120]
        never = [r for r in rows if r["floor97_min_to_bell"] is None]
        def flowdist(pop, k):
            return {"rate30": dist([(r.get(k) or {}).get("rate30") for r in pop if r.get(k)]),
                    "spread_med": dist([(r.get(k) or {}).get("spread_med") for r in pop if r.get(k)])}
        flow[cat] = {
            "n": len(rows),
            "floor97_early_n": len(early97), "floor97_late_n": len(late97),
            "floor97_never_n": len(never),
            "floor97_early_pct": round(100 * len(early97) / max(1, len(rows)), 1),
            "floor97_ttb_dist_min": dist([r["floor97_min_to_bell"] for r in rows]),
            "floorS_ttb_dist_min": dist([r["floorS_min_to_bell"] for r in rows]),
            "flow_onset_ttb_dist_min": dist([r["flow_onset_min_to_bell"] for r in rows]),
            "onset_to_floor97_dist_min": dist([r["onset_to_floor97_min"] for r in rows]),
            "onset_to_floor97_EARLY_dist_min": dist([r["onset_to_floor97_min"] for r in early97]),
            "flow_at_floor97_EARLY": flowdist(early97, "flow_at_floor97"),
            "flow_at_floor97_LATE": flowdist(late97, "flow_at_floor97"),
            "flow_at_onset_ALL": flowdist(rows, "flow_at_onset"),
        }
    agg = {"counts": counts, "per_bin": per_bin, "flow": flow}
    json.dump(agg, open(OUT / "aggregate.json", "w"), indent=1)
    print("AGGREGATE WRITTEN", flush=True)


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
            "resumed_done": len(done), "window_h": 24}
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
    aggregate()
    (OUT / "DONE").write_text(datetime.now(ET).isoformat())
    heartbeat("done", total, total)


if __name__ == "__main__":
    main()
