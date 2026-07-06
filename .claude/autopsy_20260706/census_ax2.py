#!/usr/bin/env python3
"""[READ-ONLY] AXIS-2 AMENDMENT — pair-coherent timing regrade.
The per-leg vs-own-cheapest gauge is STRUCK (operator, 07-06): the pair's leg minimums
are mutually exclusive under the inverse relationship; filling the riser early is
doctrine, not a miss. Replacement: per-leg fill vs its ROLE's typical bell-anchored
path for the game's bucket, built from THIS census's own tapes (the shapes).
  bell   = true tape onset where unambiguous, else honest start (P3a convention)
  bucket = first-post price quintile (0-19/20-39/40-59/60-79/80-99)
  role   = monitor riser/faller stamp (live_validation fills); fallback: >=50 first-post = riser
  path   = median traded price per (cat, role, bucket) on a 10-min T-minus grid, W1+corridor
  edge   = fill_px - path(bin at fill T-minus): negative = beat the role path (GOOD for both
           roles; the riser beats it by being early, the faller by being late)
Also: riser-early share (fill >=60min pre-bell) and faller into-decline share
(path 60m before the fill sat HIGHER than the fill => the decline was realized).
Run from arb-executor root. Writes /tmp/census_ax2.json. NO writes to bot state."""
import json, sys, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
D = json.load(open("/tmp/census_dump.json"))
VALID = "/root/Omi-Workspace/.claude/live_20260705/live_validation.jsonl"
BIN = 600  # 10-min bins
GRID_MAX = 36  # bins: up to 6h pre-bell

def parse_hm(s):
    if not s: return None
    try:
        return datetime.strptime("2026-" + s, "%Y-%m-%d %H:%M").replace(tzinfo=ET).timestamp()
    except Exception:
        return None

# role stamps from the monitor stream
side_of = {}
if Path(VALID).exists():
    for line in open(VALID, encoding="utf-8", errors="replace"):
        try: o = json.loads(line)
        except Exception: continue
        if o.get("type") in ("fill", "fill_regrade") and o.get("ticker") and o.get("side"):
            side_of[o["ticker"].replace("KX","")] = o["side"]

_dc = {}
def pts(s):
    try:
        d, t, ap = s.split(" ")
        if d not in _dc:
            y, mo, dy = d.split("-")
            _dc[d] = datetime(int(y), int(mo), int(dy), tzinfo=ET).timestamp()
        hh, mm, ss = t.split(":")
        h = int(hh) % 12 + (12 if ap == "PM" else 0)
        return _dc[d] + h*3600 + int(mm)*60 + int(ss)
    except Exception:
        return None

def read_tape(tk):
    f = Path("analysis/trades") / (tk + ".csv")
    rows = []
    if not f.exists(): return rows
    with open(f, encoding="utf-8", errors="replace") as fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 5: continue
            t = pts(p[0])
            if t is None: continue
            try: rows.append((t, int(p[2])))
            except Exception: continue
    rows.sort()
    return rows

def bucket(px):
    if px is None: return None
    return min(4, max(0, int(px) // 20))

BUKLAB = ["0-19", "20-39", "40-59", "60-79", "80-99"]

conc = [g for g in D["games"] if g["concluded"]]
# ---- pass 1: build role paths ----
# samples[(cat, role, bucket)][bin] -> list of prices (last print per leg per bin)
samples = defaultdict(lambda: defaultdict(list))
leg_ctx = []  # (game, leg, bell, role, buk, tape)
for g in conc:
    bell = None
    if g.get("gun") and not g.get("onset_amb"):
        bell = parse_hm(g.get("onset_t"))
    if bell is None:
        bell = parse_hm(g.get("hstart_t")) or parse_hm(g.get("sstart_t"))
    if bell is None: continue
    for l in g["legs"]:
        buk = bucket(l.get("post_px"))
        if buk is None: continue
        tk = "KX" + l["tk"] if not l["tk"].startswith("KX") else l["tk"]
        role = side_of.get(l["tk"].replace("KX",""))
        if role not in ("riser", "faller"):
            role = "riser" if (l.get("post_px") or 0) >= 50 else "faller"
        rows = read_tape(tk)
        leg_ctx.append((g, l, bell, role, buk, rows))
        binlast = {}
        for t, px in rows:
            tm = bell - t
            if tm < 0 or tm > GRID_MAX * BIN: continue
            b = int(tm // BIN)
            binlast[b] = px if b not in binlast or t > binlast[b][1] else binlast[b]
            # keep (px, t) of the LAST print in the bin
            cur = binlast.get(b)
            if not isinstance(cur, tuple) or t >= cur[1]:
                binlast[b] = (px, t)
        for b, v in binlast.items():
            samples[(g["cat"], role, buk)][b].append(v[0] if isinstance(v, tuple) else v)

def med(v):
    v = sorted(v)
    return v[len(v)//2] if v else None

path = {}
for key, bins in samples.items():
    path[key] = {b: med(v) for b, v in bins.items() if len(v) >= 2}

def path_at(cat, role, buk, tbin):
    p = path.get((cat, role, buk), {})
    for d in range(0, 4):
        for b in (tbin - d, tbin + d):
            if b in p: return p[b], b
    return None, None

# ---- pass 2: per-fill edges ----
out_legs = []
for g, l, bell, role, buk, rows in leg_ctx:
    if l.get("fill_px") is None or not l.get("fill_ts"): continue
    ft = float(l["fill_ts"])
    tmin = (bell - ft) / 60.0
    tbin = int(max(0, min(GRID_MAX, (bell - ft) // BIN)))
    ppx, pb = path_at(g["cat"], role, buk, tbin)
    edge = round(l["fill_px"] - ppx, 1) if ppx is not None else None
    # faller into-decline: path ~60m before the fill sat higher than the fill
    into_dec = None
    if role == "faller":
        prev, _ = path_at(g["cat"], role, buk, tbin + 6)
        if prev is not None: into_dec = bool(l["fill_px"] <= prev)
    out_legs.append({"ev": g["ev"], "cat": g["cat"], "suf": l["suf"], "role": role,
                     "bucket": BUKLAB[buk], "fill_px": l["fill_px"],
                     "T_bell_min": round(tmin, 1), "path_px": ppx, "path_bin_used": pb,
                     "edge_c": edge, "riser_early": (tmin >= 60) if role == "riser" else None,
                     "faller_into_decline": into_dec})

json.dump({"legs": out_legs,
           "paths": {f"{k[0]}|{k[1]}|{BUKLAB[k[2]]}": v for k, v in path.items()}},
          open("/tmp/census_ax2.json", "w"))
print(f"AX2 regrade: {len(out_legs)} filled legs graded, {len(path)} role-paths built", file=sys.stderr)
