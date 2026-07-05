#!/usr/bin/env python3
"""[READ-ONLY] THE LEAK DECOMPOSITION — the week's central question:
why aren't more pairs completing at <=97 when the faller mechanism demonstrably
manufactures discounts?

Population per run: every pair that completed >97, and every half-pair whose bound
(goal - leg1_basis) never got met. Per event, the excess-over-97 (or the unmet
bound) decomposes into cents:

  riser_concession   leg-1's fill vs what the per-cat proposed riser depth would
                     have paid, VALIDATED against the tape (did a print reach
                     W1 - depth before the actual fill? if not -> 0, depth was
                     unattainable in time, flagged)
  faller_shortfall   the faller's resting level vs the dip the tape actually
                     delivered while the bid rested (unmet half-pairs); for
                     completed >97 pairs: fill2 - (97 - achievable_riser)
  completion_timing  did the fader's dip to <= bound happen only BEFORE leg-1
                     filled (bound didn't exist yet) -- the timing leak class

Appends per-event rows to week_leak.jsonl (date-stamped, cumulative across the
week) and prints per-cat aggregates. Usage:
  python3 leak_decomposition.py LOG [LOG2...]   (from arb-executor root)"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
GOAL = 97
CAT_MAP = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
           "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
           "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
# proposed riser depths (RISER_REVISION_PROPOSAL.md) -- the counterfactual riser post
RISER_DEPTH = {"ATP_CHALL": 3, "WTA_CHALL": 3, "ITF_M": 3, "ITF_W": 2,
               "WTA_MAIN": 2, "ATP_MAIN": 1}
OUT = Path("/root/Omi-Workspace/.claude/live_20260705/week_leak.jsonl")

def cat_of(tk):
    return next((v for k, v in CAT_MAP.items() if tk.startswith(k)), "?")

logs = sys.argv[1:] or ["logs/live_v3_20260704.jsonl"]
wopen, fills, latch = {}, {}, {}
bids = defaultdict(list)     # tk -> [(ts, price)] resting buy posts
for lp in logs:
    if not Path(lp).exists():
        continue
    for line in open(lp, encoding="utf-8", errors="replace"):
        if '"event"' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        e, tk, d = o.get("event"), o.get("ticker") or "", o.get("details", {})
        ts = o.get("ts_epoch", 0)
        if e == "window_open_set" and tk and tk not in wopen:
            wopen[tk] = (ts, d.get("price"))
        elif e == "entry_filled" and tk and tk not in fills:
            fills[tk] = (ts, d.get("fill_price"), d.get("direction"), d.get("play_type"))
        elif e == "order_placed" and d.get("action") == "buy" and tk and d.get("price"):
            bids[tk].append((ts, d["price"]))
        elif e == "match_live_detected" and d.get("event"):
            latch.setdefault(d["event"], ts)

def tape(tk, t0, t1):
    f = Path("analysis/trades") / (tk + ".csv")
    out = []
    if not f.exists():
        return out
    for ln in f.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        p = ln.split(",")
        if len(p) < 5:
            continue
        try:
            t = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
        except Exception:
            continue
        if t0 <= t <= t1:
            out.append((t, int(p[2])))
    return out

ev_fills = defaultdict(list)
for tk, f in fills.items():
    if f[3] in ("reconcile_adoption",):
        continue
    ev_fills[tk.rsplit("-", 1)[0]].append((tk, f))

rows = []
for ev, legs in ev_fills.items():
    cat = cat_of(ev + "-")
    end = latch.get(ev, max(f[0] for _, f in legs) + 3600)
    legs.sort(key=lambda x: x[1][0])
    if len(legs) >= 2:
        (tk1, f1), (tk2, f2) = legs[0], legs[1]
        combined = (f1[1] or 0) + (f2[1] or 0)
        if combined <= GOAL:
            continue
        excess = combined - GOAL
        # riser concession: leg-1's counterfactual deeper post, tape-validated
        W1 = (wopen.get(tk1) or (None, None))[1]
        depth = RISER_DEPTH.get(cat, 2)
        rc, rc_attainable = 0, False
        if W1 is not None:
            r_star = W1 - depth
            tp1 = tape(tk1, wopen[tk1][0], f1[0])
            rc_attainable = any(pr < r_star for _, pr in tp1)
            rc = max(0, (f1[1] or 0) - r_star) if rc_attainable else 0
        # faller component: what leg-2 paid beyond the bound the achievable riser sets
        r_star_eff = (W1 - depth) if (W1 is not None and rc_attainable) else (f1[1] or 0)
        f_star = GOAL - r_star_eff
        fc = max(0, (f2[1] or 0) - f_star)
        rows.append({"date": datetime.now(ET).strftime("%Y-%m-%d"), "ev": ev, "cat": cat,
                     "kind": "pair_over_97", "combined": combined, "excess": excess,
                     "riser_concession": rc, "riser_depth_attainable": rc_attainable,
                     "faller_component": fc, "timing_component": 0,
                     "legs": {tk1[-8:]: f1[1], tk2[-8:]: f2[1]}})
    elif len(legs) == 1:
        tk1, f1 = legs[0]
        basis = f1[1] or 0
        bound = GOAL - basis
        sib = None
        for otk in list(wopen) + list(bids):
            if otk.rsplit("-", 1)[0] == ev and otk != tk1:
                sib = otk
                break
        if not sib or bound <= 2:
            continue
        t_open = (wopen.get(sib) or (f1[0] - 4 * 3600, None))[0]
        tp = tape(sib, t_open, end)
        if not tp:
            rows.append({"date": datetime.now(ET).strftime("%Y-%m-%d"), "ev": ev, "cat": cat,
                         "kind": "half_no_tape", "basis": basis, "bound": bound,
                         "riser_concession": 0, "faller_component": 0, "timing_component": 0})
            continue
        pre = [pr for t, pr in tp if t < f1[0]]
        post = [pr for t, pr in tp if t >= f1[0]]
        dip_pre = min(pre) if pre else None
        dip_post = min(post) if post else None
        # our faller resting level while the bound existed
        lvl = None
        for t, p in sorted(bids.get(sib, [])):
            if t <= end:
                lvl = p
        if dip_post is not None and dip_post <= bound:
            # the dip DID reach the bound after leg-1 filled -> we missed it:
            # level too deep (shortfall) or queue
            kind = "half_dip_missed"
            fc = max(0, dip_post - (lvl or 0)) if (lvl is not None and lvl < dip_post) else 0
            tc = 0
        elif dip_pre is not None and dip_pre <= bound:
            kind = "half_timing"          # dip existed only BEFORE the bound did
            fc = 0
            tc = min(bound - dip_pre + 1, bound)   # cents the early dip offered
        else:
            kind = "half_no_dip"          # tape never reached the bound: true structural
            fc = 0
            tc = 0
        rows.append({"date": datetime.now(ET).strftime("%Y-%m-%d"), "ev": ev, "cat": cat,
                     "kind": kind, "basis": basis, "bound": bound,
                     "faller_level": lvl, "dip_pre_leg1": dip_pre, "dip_post_leg1": dip_post,
                     "riser_concession": 0, "faller_component": fc, "timing_component": tc})

# append cumulative (dedup by (date, ev))
seen = set()
if OUT.exists():
    for ln in OUT.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            j = json.loads(ln)
            seen.add((j.get("date"), j.get("ev")))
        except Exception:
            pass
new = [r for r in rows if (r["date"], r["ev"]) not in seen]
with open(OUT, "a", encoding="utf-8") as fh:
    for r in new:
        fh.write(json.dumps(r) + "\n")

print(f"LEAK DECOMPOSITION: {len(rows)} events this run ({len(new)} new to week file)")
agg = defaultdict(lambda: defaultdict(float))
kinds = defaultdict(int)
for r in rows:
    kinds[r["kind"]] += 1
    agg[r["cat"]]["riser_concession"] += r["riser_concession"]
    agg[r["cat"]]["faller_component"] += r["faller_component"]
    agg[r["cat"]]["timing_component"] += r["timing_component"]
print("kinds:", dict(kinds))
print(f"{'cat':10s} {'riser_concession':>16} {'faller_component':>16} {'timing':>8}")
for c in sorted(agg):
    a = agg[c]
    print(f"{c:10s} {a['riser_concession']:>14.0f}c {a['faller_component']:>14.0f}c {a['timing_component']:>6.0f}c")
print("\nper-event detail:")
for r in sorted(rows, key=lambda x: -(x['riser_concession'] + x['faller_component'] + x['timing_component'])):
    print(" ", json.dumps(r)[:200])
