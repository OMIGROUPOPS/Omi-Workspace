#!/usr/bin/env python3
"""RANGE LAYER BUILDER — Part 2b (REVISED): the composer's historical anchor.
C45 LINEAGE (this layer invents NOTHING; it is the June framework era-stamped):
  OMQS_WINDOW_MAP_3WAY_JUN26PLUS.md  — THE axes: fill_minus_runmid buckets
    (deep_disc<=-5 / disc -5..-1 / at-mid -1..+1 / over +1..+5 / deep_over>=+5)
    x price cells (<=25 / 26-50 / 51-75 / >=75) x windows (W1 fill->scheduled,
    CORRIDOR scheduled->gun, W2 gun->settle); reach = print >= fill+band;
    outcomes n / W1% / COR% / W2% / win% / loser-true-knife%.
  OMQS_WINDOW_MAP_JUN26PLUS.md, OMQS_THREEPRICE_FAVORITES_JUN26PLUS.md,
  OMQS_MIDPOINT_FAVORITES_JUN24PLUS.md — the range/fill-quality lineage.
  Fill-grid two-regime verdict: fill-quality matters <=50c; GEOMETRY dominates
    >=75c favorites (W1/COR floor-zero at every fill quality).
  CENSUS 07-10 granularity law: ITF = live-era only; CHALL archive +/-30min
    COARSE RANGES ONLY (never timing) -> the archive contributes a separate
    coarse geometry table, no window decomposition, CHALL jump-slice only.
EXTENSION (the operator's standing framework, not alongside it): same axes,
population widened June-settled-set -> full era-admissible book (Jun 26 ->
today, our settled filled legs), PER CATEGORY, PER SIDE (leader/underdog).
runmid = trailing 30-min traded mean at the fill instant (observable; never
retrospective fv_burst). Read-only; no exit/cut change (§0A)."""
import glob, gzip, json, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ET = timezone(timedelta(hours=-4))
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
def cat_of(tk):
    for k, v in CAT.items():
        if tk.startswith(k):
            return v
def bucket(frm):
    if frm <= -5: return "deep_disc"
    if frm < -1: return "disc"
    if frm <= 1: return "at_mid"
    if frm < 5: return "over"
    return "deep_over"
def cell(px):
    if px <= 25: return "le25"
    if px <= 50: return "26_50"
    if px <= 75: return "51_75"
    return "ge75"


def leg_prints(tk):
    out = []
    for f in glob.glob(str(ROOT / "analysis/trades" / (tk + ".csv*"))):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt", encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            for ln in fh:
                p = ln.split(",")
                try:
                    ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
                    out.append((ts, float(p[2])))
                except Exception:
                    continue
    out.sort()
    return out


def main():
    legs = {}          # tk -> leg record (first completed fill per cycle kept simple: first fill)
    sched, gun = {}, {}
    logs = sorted(glob.glob(str(ROOT / "logs/live_v3_202606*.jsonl*")) +
                  glob.glob(str(ROOT / "logs/live_v3_202607*.jsonl*")))
    logs = [l for l in logs if "20260626" <= Path(l).name[8:16]]
    for lp in logs:
        op = gzip.open if lp.endswith(".gz") else open
        with op(lp, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not any(k in line for k in ('"entry_filled"', '"v4_exit_posted"',
                                               '"settled"', '"schedule_match"',
                                               '"gun_fired"', '"match_live_detected"',
                                               '"exit_filled"')):
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                e, det, tk = d["event"], d.get("details") or {}, d.get("ticker", "")
                ev = det.get("event", "") or (tk.rsplit("-", 1)[0] if tk else "")
                if e == "schedule_match":
                    try:
                        sched[ev] = datetime.fromisoformat(det.get("start_time", "")).timestamp()
                    except Exception:
                        pass
                elif e in ("gun_fired", "match_live_detected"):
                    if ev and ev not in gun:
                        gun[ev] = d.get("ts_epoch", 0)
                elif e == "entry_filled" and tk and tk not in legs:
                    legs[tk] = {"fill": det.get("fill_price"), "ts": d.get("ts_epoch", 0),
                                "side": det.get("direction", "?"), "band": None,
                                "outcome": None, "reach": {}}
                elif e == "v4_exit_posted" and tk in legs and legs[tk]["band"] is None:
                    try:
                        legs[tk]["band"] = int(det.get("exit_price", 0)) - int(det.get("entry_price", 0))
                    except Exception:
                        pass
                elif e == "settled" and tk in legs and legs[tk]["outcome"] is None:
                    legs[tk]["outcome"] = "WIN" if det.get("settle") == "WIN" else "LOSS"
                elif e == "exit_filled" and tk in legs and legs[tk]["outcome"] is None:
                    if det.get("complete"):
                        legs[tk]["outcome"] = "CASHED"
    # per-leg tape pass
    agg = defaultdict(lambda: {"n": 0, "w1": 0, "cor": 0, "w2": 0, "win": 0,
                               "loss": 0, "knife": 0, "cashed": 0})
    done = 0
    for tk, L in legs.items():
        if not L["fill"] or not L["ts"] or L["outcome"] is None or not L["band"] or L["band"] <= 0:
            continue
        ev = tk.rsplit("-", 1)[0]
        c = cat_of(tk)
        if not c:
            continue
        pr = leg_prints(tk)
        if not pr:
            continue
        rm = [px for ts, px in pr if L["ts"] - 1800 <= ts <= L["ts"]]
        if not rm:
            continue
        runmid = sum(rm) / len(rm)
        b = bucket(L["fill"] - runmid)
        pc = cell(L["fill"])
        st = sched.get(ev)
        g = gun.get(ev)
        tgt = L["fill"] + L["band"]
        def reach(t0, t1):
            return any(px >= tgt for ts, px in pr if t0 <= ts <= (t1 or 9e12))
        key = (c, L["side"], b, pc)
        a = agg[key]
        a["n"] += 1
        if st:
            a["w1"] += int(reach(L["ts"], st))
            if g and g > st:
                a["cor"] += int(reach(st, g))
                a["w2"] += int(reach(g, None))
            else:
                a["w2"] += int(reach(st, None))
        else:
            a["w2"] += int(reach(L["ts"], None))
        if L["outcome"] == "WIN":
            a["win"] += 1
        elif L["outcome"] == "CASHED":
            a["cashed"] += 1
        else:
            a["loss"] += 1
            if not reach(L["ts"], None):
                a["knife"] += 1
        done += 1
        if done % 200 == 0:
            print("...", done, flush=True)
    out = {"generated": datetime.now(ET).strftime("%Y-%m-%d %I:%M %p ET"),
           "lineage": "WINDOW_MAP_3WAY axes verbatim; era-admissible live book Jun26->today; runmid=trailing-30min traded mean at fill; census law: ITF live-era only (this table IS live-era); archive CHALL coarse addendum separate",
           "n_legs": done,
           "cells": {"|".join(k): v for k, v in agg.items()}}
    op_ = ROOT.parent / ".claude/range_layer/RANGE_LAYER_3WAY.json"
    op_.parent.mkdir(parents=True, exist_ok=True)
    op_.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("WROTE", op_, "legs:", done, "cells:", len(agg))


if __name__ == "__main__":
    main()
