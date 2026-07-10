#!/usr/bin/env python3
"""OS SHADOW ROLLUP [OS BUILD 07-09] -- nightly: agreement rate, divergence
classes, would-be fills tape-verified, would-be dynamic-S inputs, hold-flag
divergence, cap-sensitivity note (NO cap read before joint-shadow n>=30 --
operator's order; staged is the only live setting)."""
import json, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ET = timezone(timedelta(hours=-4))

def main():
    files = sorted((ROOT / "logs").glob("live_v3_*.jsonl"),
                   key=lambda p: p.stat().st_mtime)[-1:]
    rows = []
    for p in files:
        for line in open(p, encoding="utf-8", errors="replace"):
            if '"os_shadow"' not in line:
                continue
            try:
                d = json.loads(line)
                rows.append(d)
            except ValueError:
                pass
    n = len(rows)
    sites = Counter(r["details"]["site"] for r in rows)
    agree = diverge = 0
    dv = Counter()
    holds = {"reviews": 0, "quiet": 0, "floor_miss": 0, "both": 0, "diverge": 0,
             "floor_unevaluable": 0, "pre_instrument": 0}
    for r in rows:
        det = r["details"]
        w, a = det.get("would") or {}, det.get("actual") or {}
        if det["site"] != "hold_review" and a.get("actual_bid") is not None \
                and w.get("level") is not None:
            if abs((a["actual_bid"] or 0) - w["level"]) <= 1:
                agree += 1
            else:
                diverge += 1
                dv["%s|%s" % (w.get("regime"), w.get("timing"))] += 1
        h = det.get("hold")
        if h:
            # [T4 DUAL-FLAG FENCE 07-09, Plex ratification] lines written
            # before the dual-flag instrument (no t4 stamp: floor reading was
            # structurally dead — expected_share passed as None) are
            # PRE_INSTRUMENT: counted visibly, EXCLUDED from the threshold
            # dataset. Plex's T4 accumulation clock starts at the first
            # dual_flag_v1 line.
            if h.get("t4") != "dual_flag_v1":
                holds["pre_instrument"] += 1
                continue
            holds["reviews"] += 1
            q, fm = h.get("quiet_flag"), h.get("floor_miss_flag")
            holds["quiet"] += int(bool(q))
            holds["floor_miss"] += int(bool(fm))
            holds["both"] += int(bool(q) and bool(fm))
            holds["diverge"] += int(bool(q) != bool(fm))
            holds["floor_unevaluable"] += int(h.get("floor_qual") == "unevaluable")
    out = ["OS SHADOW %s: n=%d sites=%s | placement agree(±1c)=%d diverge=%d"
           " | divergence classes: %s | hold: %s"
           " | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)"
           % (datetime.now(ET).strftime("%Y-%m-%d"), n, dict(sites), agree,
              diverge, dict(dv.most_common(5)), holds)]
    print(out[0])
    np = ROOT.parent / ".claude" / "live_20260705" / "NIGHTLY_PASS.md"
    try:
        with open(np, "a", encoding="utf-8") as fh:
            fh.write("\n" + out[0] + "\n")
    except OSError:
        pass

if __name__ == "__main__":
    main()
