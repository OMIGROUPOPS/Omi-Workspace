#!/usr/bin/env python3
"""[C-JOINT-SHADOW nightly rollup — Plex walk-cap ruling 2026-07-07] Read-only.
For a day's jsonl: every aim_shadow line carrying joint-shadow fields becomes a
decision row; would-fill per counterfactual level = the tape PRINTED <= level in
the 4h after the decision (B3 conservative convention), capped at the event's
latch where one fired. Reports, combined-vs-each-alone: conversion (fills gained/
lost), starvation (levels the tape never reached), and <=97 held on every
constrained pair (joint level + sibling booked basis). Output:
.claude/live_20260705/JOINT_SHADOW_<date>.md (+.json).
Usage (VPS, in arb-executor): python3 analysis/joint_shadow_rollup.py [YYYYMMDD]"""
import gzip, json, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
ET = timezone(timedelta(hours=-4))
HORIZON = 4 * 3600

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


def tape_rows(tk):
    for suf in (".csv", ".csv.gz"):
        f = ROOT / "analysis" / "trades" / (tk + suf)
        if f.exists():
            op = gzip.open if suf.endswith("gz") else open
            out = []
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                for ln in fh:
                    p = ln.split(",")
                    if len(p) < 4:
                        continue
                    t = pts(p[0])
                    if t is None:
                        continue
                    try:
                        out.append((t, int(p[2])))
                    except ValueError:
                        continue
            out.sort()
            return out
    return []


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.now(ET).strftime("%Y%m%d")
    log = ROOT / "logs" / ("live_v3_%s.jsonl" % day)
    rows, fills, latch = [], defaultdict(list), {}
    for line in open(log, encoding="utf-8", errors="replace"):
        if '"aim_shadow"' not in line and '"entry_filled"' not in line and '"match_live_detected"' not in line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        d = e.get("details", {})
        if e["event"] == "aim_shadow" and "joint_level" in d:
            rows.append({"tk": e.get("ticker", ""), "ts": e.get("ts_epoch", 0), **{
                k: d.get(k) for k in ("event", "cat", "site", "actual_bid", "walkcap_level",
                                      "exself_level", "joint_level", "constrained",
                                      "walkcap_anchor_src")}})
        elif e["event"] == "entry_filled":
            fills[e.get("ticker", "")].append((e.get("ts_epoch", 0),
                                               d.get("fill_price")))
        elif e["event"] == "match_live_detected":
            ev = d.get("event")
            if ev and ev not in latch:
                latch[ev] = e.get("ts_epoch", 0)
    # last decision per (tk, minute) to avoid repost spam double-count
    dedup = {}
    for r in rows:
        dedup[(r["tk"], int(r["ts"] // 60))] = r
    rows = sorted(dedup.values(), key=lambda r: r["ts"])
    con = [r for r in rows if r.get("constrained")]
    tapes = {}
    res = []
    for r in con:
        tk = r["tk"]
        if tk not in tapes:
            tapes[tk] = tape_rows(tk)
        end = r["ts"] + HORIZON
        ev = tk.rsplit("-", 1)[0]
        if ev in latch:
            end = min(end, latch[ev])
        win = [px for t, px in tapes[tk] if r["ts"] < t <= end]
        def wf(level):
            return (level is not None and win and min(win) <= level)
        res.append({**r, "wf_actual": wf(r["actual_bid"]), "wf_walkcap": wf(r["walkcap_level"]),
                    "wf_exself": wf(r["exself_level"]), "wf_joint": wf(r["joint_level"]),
                    "tape_prints_in_win": len(win)})
    def rate(key):
        n = sum(1 for x in res if x[key])
        return "%d/%d (%.1f%%)" % (n, len(res), 100 * n / max(1, len(res)))
    # <=97 on constrained pairs: joint level + sibling booked basis same day
    sib_basis = {}
    for tk, fl in fills.items():
        if fl:
            sib_basis[tk] = fl[-1][1]
    pair97 = {"n": 0, "held": 0}
    for x in res:
        ev = x["tk"].rsplit("-", 1)[0]
        sib = next((t for t in sib_basis if t.startswith(ev + "-") and t != x["tk"]), None)
        if sib and x["joint_level"] is not None and sib_basis[sib]:
            pair97["n"] += 1
            if x["joint_level"] + sib_basis[sib] <= 97:
                pair97["held"] += 1
    out = {"day": day, "decisions": len(rows), "constrained": len(con),
           "would_fill": {"actual": rate("wf_actual"), "walkcap_alone": rate("wf_walkcap"),
                          "exself_alone": rate("wf_exself"), "joint": rate("wf_joint")},
           "anchor_src": dict(__import__("collections").Counter(
               r["walkcap_anchor_src"] for r in con)),
           "pair_le97_on_constrained": pair97}
    outdir = ROOT.parent / ".claude" / "live_20260705"
    json.dump({"summary": out, "rows": res[:2000]},
              open(outdir / ("JOINT_SHADOW_%s.json" % day), "w"), indent=1)
    md = ["# JOINT SHADOW rollup — %s (walk-cap x expression, log-only)" % day, "",
          "decisions %d · constrained %d" % (len(rows), len(con)), "",
          "| lane | would-fill (4h/latch-capped, prints<=level) |", "|---|---|",
          "| actual | %s |" % out["would_fill"]["actual"],
          "| walk-cap alone | %s |" % out["would_fill"]["walkcap_alone"],
          "| ex-self alone | %s |" % out["would_fill"]["exself_alone"],
          "| JOINT | %s |" % out["would_fill"]["joint"], "",
          "anchor sources: %s" % out["anchor_src"], "",
          "<=97 held on constrained pairs (joint + sibling basis): %d/%d" % (
              pair97["held"], pair97["n"])]
    (outdir / ("JOINT_SHADOW_%s.md" % day)).write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
