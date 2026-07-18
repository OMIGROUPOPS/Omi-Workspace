#!/usr/bin/env python3
"""PHASE B — THE RANGE SPECTRUM (Dispatch 2, operator's design; 07-17).

For every leg in the corpus: range = traded price at T−8h → traded price at
the official start (right edge from Phase A's corrected table, evidence
grade carried). Ranges kept as PAIRS — the seesaw signature is one object,
never two orphans. Full tick series retained inside each range (best bid /
best ask / traded per poll, through the corridor). HARD per-category
partition — populations never pool across cats.

Stale-anchor rules, NAMED (never silently guessed):
  anchor_t8   = last traded print at/before T−8h; if none, the FIRST traded
                print after T−8h carries `anchor_rule=first_after_t8` with
                its lag; if the leg never traded before the right edge,
                `anchor_rule=never_traded` and the leg enters the spectrum
                as a NO-RANGE row (counted, never fitted).
  close_px    = last traded print at/before the right edge (grade carried
                from Phase A: official_actual / onset_snapshot_est /
                sched_only_no_evidence).

Journey vector per leg:
  path_shape   — grind / dip_recover / late_collapse / flat (low + its
                 timing vs the window; decreed shape rules v1, named in
                 the row: dip_recover = low <= anchor−3c recovering >=2c;
                 late_collapse = low in the last 25% of the window ending
                 within 2c of it; grind = monotone-ish drift |net| >= 3c
                 with low near an endpoint; flat = |net| < 3c)
  volume_tex   — prints/min mean + arrival thirds (early/mid/late shares)
  spread_reg   — median + p90 spread, closure (first-third median vs
                 last-third median)
  wake         — first poll with a two-sided book <= 90c wide + first
                 traded print (both as T-minus minutes)
  sibling      — the mirror lives at the PAIR level (both legs' series in
                 one object; seesaw corr on overlapping polls)

Tick source: kalshi_price_snapshots (poll-cadence bid/ask/last, Apr-21 →
now — mains+CHALL; ITF carried where premarket_ticks CSVs exist, source
stamped per pair). Output: state/range_spectrum_v1.jsonl (one JSON object
per EVENT = the pair) + per-cat population counts to stdout/census.
"""
import glob, json, sqlite3, statistics, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "state/range_spectrum_v1.jsonl"
CENSUS = Path("/tmp/RANGE_SPECTRUM_CENSUS.md")

def iso_ep(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None

corpus = {}
for l in open(ROOT / "state/corpus_events_v2.jsonl"):
    r = json.loads(l)
    if r.get("sched_honest") and r.get("right_edge"):
        corpus[r["event"]] = r
print("corpus events with edges:", len(corpus), flush=True)

con = sqlite3.connect("file:%s?mode=ro" % (ROOT / "tennis.db"), uri=True,
                      timeout=5)

def journey(series, t8, redge, anchor):
    """series = [(ts, bid, ask, last)] inside [t8, redge]; anchor = int."""
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
    sp_first = [a - b for ts, b, a, lc in series[:max(1, len(series)//3)]
                if a and b and a > b]
    sp_last = [a - b for ts, b, a, lc in series[-max(1, len(series)//3):]
               if a and b and a > b]
    two_sided = [ts for ts, b, a, lc in series if b and a and (a - b) <= 90]
    return {
        "anchor": anchor, "close": close_px, "net": net,
        "low": lo_px, "low_tmin_min": round((redge - lo_ts) / 60.0, 1),
        "low_frac": round(lo_frac, 2), "shape": shape,
        "n_traded_polls": len(traded),
        "prints_per_min": round(len(traded) / (span / 60.0), 3),
        "arrival_thirds": thirds,
        "spread_med": (statistics.median(spreads) if spreads else None),
        "spread_p90": (spreads[int(0.9 * len(spreads))] if spreads else None),
        "spread_close": ((statistics.median(sp_last)
                          - statistics.median(sp_first))
                         if sp_first and sp_last else None),
        "wake_book_tmin_min": (round((redge - two_sided[0]) / 60.0, 1)
                               if two_sided else None),
        "wake_trade_tmin_min": (round((redge - traded[0][0]) / 60.0, 1)
                                if traded else None),
    }

# stream snapshots grouped by event
print("streaming snapshots ...", flush=True)
rows = con.execute(
    "SELECT event_ticker, ticker, polled_at, bid_cents, ask_cents, "
    "last_cents FROM kalshi_price_snapshots ORDER BY event_ticker, polled_at")
n_pairs = 0
counts = defaultdict(lambda: defaultdict(int))
fh = open(OUT, "w")

def emit(et, legs):
    global n_pairs
    r = corpus.get(et)
    if not r or len(legs) != 2:
        return
    t8 = r["sched_honest"] - 8 * 3600
    redge = r["right_edge"]
    cat = r["cat"]
    out = {"event": et, "cat": cat, "sched": r["sched_honest"],
           "right_edge": redge, "edge_src": r["right_edge_src"],
           "tick_src": "kalshi_price_snapshots", "legs": {}}
    ok = 0
    for tk, series in legs.items():
        win = [x for x in series if t8 <= x[0] <= redge]
        pre = [lc for ts, b, a, lc in series if ts <= t8 and lc]
        rule = "last_before_t8"
        anchor = pre[-1] if pre else None
        if anchor is None:
            aft = [(ts, lc) for ts, b, a, lc in win if lc]
            if aft:
                anchor = aft[0][1]
                rule = "first_after_t8"
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
    # sibling mirror: seesaw corr on overlapping traded polls
    if ok == 2:
        (la, lb) = list(out["legs"].values())
        sa = {t[0]: t[3] for t in la["ticks"] if t[3]}
        sb = {t[0]: t[3] for t in lb["ticks"] if t[3]}
        common = sorted(set(sa) & set(sb))
        if len(common) >= 6:
            xa = [sa[t] for t in common]
            xb = [sb[t] for t in common]
            try:
                out["seesaw_corr"] = round(
                    statistics.correlation(xa, xb), 3)
            except Exception:
                pass
    counts[cat]["pairs"] += 1
    counts[cat]["legs_ranged"] += ok
    if ok == 2:
        counts[cat]["pairs_complete"] += 1
    fh.write(json.dumps(out) + "\n")
    n_pairs += 1

prev_et, legs = None, defaultdict(list)
for et, tk, pa, b, a, lc in rows:
    if et != prev_et:
        if prev_et:
            emit(prev_et, legs)
        prev_et, legs = et, defaultdict(list)
    ts = iso_ep(pa)
    if ts:
        legs[tk].append((ts, b, a, lc))
if prev_et:
    emit(prev_et, legs)
fh.close()
print("pairs written:", n_pairs, flush=True)

L = ["# PHASE B — THE RANGE SPECTRUM, population census v1", "",
     "source: kalshi_price_snapshots (poll-cadence; Apr-21→now); right "
     "edges from the Phase A corrected table, evidence grade carried; "
     "pairs are ONE object; per-cat HARD partition.", ""]
tot_legs = 0
for cat, c in sorted(counts.items()):
    tot_legs += c["legs_ranged"]
    L.append("- %s: pairs %d · complete-pairs %d · legs ranged %d"
             % (cat, c["pairs"], c["pairs_complete"], c["legs_ranged"]))
L.append("- TOTAL legs ranged: %d" % tot_legs)
L.append("")
L.append("(ITF: snapshots carry no ITF — ITF legs enter from the "
         "premarket_ticks CSV source in the follow-up pass, stamped "
         "tick_src=premarket_ticks; counted zero here, never guessed.)")
CENSUS.write_text("\n".join(L) + "\n")
print(CENSUS.read_text())
