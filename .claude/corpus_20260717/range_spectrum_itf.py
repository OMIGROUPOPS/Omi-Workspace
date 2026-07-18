#!/usr/bin/env python3
"""PHASE B — ITF pass: extend the range spectrum from premarket_ticks CSVs.

ITF has no snapshot coverage; its tick source is the itf_collector CSVs
(5-level book + last_trade, ~5-min cadence, ET wall clock). Coverage is
RECENT-ERA ONLY (the pre-Jul-11 archive died in the disk-hygiene pruning —
known incident, named; counts posted, never padded). Right edge: official
where cached, else tick-resolution onset (first sustained last_trade
movement at/after sched, clamped >= sched, `onset_ticks_est`), else
sched-only. Appends pair objects (tick_src=premarket_ticks) to
state/range_spectrum_v1.jsonl and rewrites the census as v2.
"""
import csv, glob, gzip, io, json, statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "state/range_spectrum_v1.jsonl"
CENSUS = Path("/tmp/RANGE_SPECTRUM_CENSUS.md")

corpus = {}
for l in open(ROOT / "state/corpus_events_v2.jsonl"):
    r = json.loads(l)
    if r.get("sched_honest"):
        corpus[r["event"]] = r

def ep_et(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %I:%M:%S %p").replace(
            tzinfo=ET).timestamp()
    except ValueError:
        return None

# gather per-event leg files
files = defaultdict(dict)
for f in (glob.glob(str(ROOT / "analysis/premarket_ticks/KXITF*.csv*"))):
    tk = Path(f).name.replace(".csv.gz", "").replace(".csv", "")
    et = tk.rsplit("-", 1)[0]
    files[et][tk] = f
print("ITF events with tick files:", len(files), flush=True)

def read_series(path):
    op = (lambda p: io.TextIOWrapper(gzip.open(p, "rb"),
                                     encoding="utf-8", errors="replace")) \
        if path.endswith(".gz") else (lambda p: open(p, encoding="utf-8",
                                                     errors="replace"))
    out = []
    with op(path) as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            ts = ep_et(row.get("ts_et") or "")
            if ts is None:
                continue
            try:
                b = int(float(row.get("bid_1") or 0)) or None
                a = int(float(row.get("ask_1") or 0)) or None
                lt = int(float(row.get("last_trade") or 0)) or None
            except ValueError:
                continue
            out.append((ts, b, a, lt))
    out.sort(key=lambda x: x[0])   # ts only — None bids must not compare
    return out

def journey(series, t8, redge, anchor):
    traded = [(ts, lc) for ts, b, a, lc in series if lc]
    if not traded or anchor is None:
        return None
    span = max(redge - t8, 1.0)
    lo_px, lo_ts = min((lc, ts) for ts, lc in traded)
    close_px = traded[-1][1]
    net = close_px - traded[0][1]
    lo_frac = (lo_ts - t8) / span
    if lo_px <= anchor - 3 and close_px >= lo_px + 2:
        shape = "dip_recover"
    elif lo_frac >= 0.75 and close_px <= lo_px + 2:
        shape = "late_collapse"
    elif abs(net) >= 3:
        shape = "grind"
    else:
        shape = "flat"
    thirds = [0, 0, 0]
    for ts, _ in traded:
        thirds[min(2, int(3 * (ts - t8) / span))] += 1
    spreads = sorted(a - b for ts, b, a, lc in series if a and b and a > b)
    sp_f = [a - b for ts, b, a, lc in series[:max(1, len(series)//3)]
            if a and b and a > b]
    sp_l = [a - b for ts, b, a, lc in series[-max(1, len(series)//3):]
            if a and b and a > b]
    two = [ts for ts, b, a, lc in series if b and a and (a - b) <= 90]
    return {"anchor": anchor, "close": close_px, "net": net, "low": lo_px,
            "low_tmin_min": round((redge - lo_ts) / 60.0, 1),
            "low_frac": round(lo_frac, 2), "shape": shape,
            "n_traded_polls": len(traded),
            "prints_per_min": round(len(traded) / (span / 60.0), 3),
            "arrival_thirds": thirds,
            "spread_med": statistics.median(spreads) if spreads else None,
            "spread_p90": spreads[int(0.9 * len(spreads))] if spreads else None,
            "spread_close": ((statistics.median(sp_l)
                              - statistics.median(sp_f))
                             if sp_f and sp_l else None),
            "wake_book_tmin_min": (round((redge - two[0]) / 60.0, 1)
                                   if two else None),
            "wake_trade_tmin_min": round((redge - traded[0][0]) / 60.0, 1)}

official = {}
try:
    ob = json.loads((ROOT / "state/daysheet_bells_official.json").read_text())
    for ev, e in ob.items():
        if e.get("start_ep") and e.get("status") not in (None, "not_started"):
            official[ev] = float(e["start_ep"])
except Exception:
    pass

fh = open(OUT, "a")
counts = defaultdict(lambda: defaultdict(int))
for et, legmap in sorted(files.items()):
    r = corpus.get(et)
    if not r or len(legmap) != 2:
        continue
    sched = r["sched_honest"]
    t8 = sched - 8 * 3600
    cat = r["cat"]
    series_by = {tk: read_series(p) for tk, p in legmap.items()}
    # right edge: official > tick onset (>=2 consecutive last_trade
    # CHANGES at/after sched) > sched-only
    off = official.get(et)
    if off:
        redge, esrc = max(off, sched), "official_actual"
    else:
        onset = None
        moves = []
        for tk, s in series_by.items():
            prev = None
            run = 0
            for ts, b, a, lc in s:
                if ts < sched or not lc:
                    continue
                if prev is not None and lc != prev:
                    run += 1
                    if run >= 2:
                        moves.append(ts)
                        break
                prev = lc
        if moves:
            redge, esrc = max(min(moves), sched), "onset_ticks_est"
        else:
            redge, esrc = sched, "sched_only_no_evidence"
    out = {"event": et, "cat": cat, "sched": sched, "right_edge": redge,
           "edge_src": esrc, "tick_src": "premarket_ticks", "legs": {}}
    ok = 0
    for tk, s in series_by.items():
        win = [x for x in s if t8 <= x[0] <= redge]
        pre = [lc for ts, b, a, lc in s if ts <= t8 and lc]
        rule, anchor = "last_before_t8", (pre[-1] if pre else None)
        if anchor is None:
            aft = [(ts, lc) for ts, b, a, lc in win if lc]
            if aft:
                anchor, rule = aft[0][1], "first_after_t8"
            else:
                out["legs"][tk.rsplit("-", 1)[-1]] = {
                    "anchor_rule": "never_traded", "ticks": len(win)}
                continue
        jv = journey(win, t8, redge, anchor)
        if jv:
            jv["anchor_rule"] = rule
            jv["ticks"] = [[round(ts), b, a, lc] for ts, b, a, lc in win]
            out["legs"][tk.rsplit("-", 1)[-1]] = jv
            ok += 1
    if ok == 2:
        (la, lb) = list(out["legs"].values())
        sa = {t[0]: t[3] for t in la["ticks"] if t[3]}
        sb = {t[0]: t[3] for t in lb["ticks"] if t[3]}
        common = sorted(set(sa) & set(sb))
        if len(common) >= 6:
            try:
                out["seesaw_corr"] = round(statistics.correlation(
                    [sa[t] for t in common], [sb[t] for t in common]), 3)
            except Exception:
                pass
    counts[cat]["pairs"] += 1
    counts[cat]["legs_ranged"] += ok
    if ok == 2:
        counts[cat]["pairs_complete"] += 1
    fh.write(json.dumps(out) + "\n")
fh.close()
print("ITF pairs appended:", sum(c["pairs"] for c in counts.values()),
      flush=True)

# census v2 = re-scan the whole spectrum file
tot = defaultdict(lambda: defaultdict(int))
for l in open(OUT):
    r = json.loads(l)
    tot[r["cat"]]["pairs"] += 1
    tot[r["cat"]]["legs"] += sum(1 for v in r["legs"].values()
                                 if v.get("shape"))
    if sum(1 for v in r["legs"].values() if v.get("shape")) == 2:
        tot[r["cat"]]["complete"] += 1
L = ["# PHASE B — THE RANGE SPECTRUM, population census v2 (ITF folded in)",
     "", "pairs are ONE object; per-cat HARD partition; tick_src stamped "
     "per pair (snapshots poll-cadence for mains/CHALL; premarket_ticks "
     "for ITF — RECENT-ERA ONLY, the pre-Jul-11 ITF archive died in the "
     "disk-hygiene pruning, counted never padded).", ""]
grand = 0
for cat, c in sorted(tot.items()):
    grand += c["legs"]
    L.append("- %s: pairs %d · complete-pairs %d · legs ranged %d"
             % (cat, c["pairs"], c["complete"], c["legs"]))
L.append("- **TOTAL legs ranged: %d**" % grand)
CENSUS.write_text("\n".join(L) + "\n")
print(CENSUS.read_text())
