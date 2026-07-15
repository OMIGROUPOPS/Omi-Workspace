#!/usr/bin/env python3
"""C-FLOW-REST-SEED v1 — OUTCOME REPLAY (per-game, vs the prior slate).
Read-only. For every entry_dossier consultation in tonight's jsonl, recompute
the flow bucket + reach p_fill from the exchange REST trade tape at the
consultation instant, and print: (a) the founding KOAYAZ rows, (b) the
per-cat flip table, (c) the behavior-isolation lane (aims are page-priced;
the gauge feeds the dossier record only — no placement changes by
construction, demonstrated per-line: aim_used == page path aim regardless
of bucket)."""
import json, math, sys, time, urllib.request
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
JSONL = "/root/Omi-Workspace/arb-executor/logs/live_v3_20260715.jsonl"
LAW = json.load(open("/root/Omi-Workspace/.claude/takerreach/LAW.json"))["law"]
THR = {"ITF_M": 6, "ITF_W": 6, "ATP_CHALL": 16, "WTA_CHALL": 16}

consults = []
for line in open(JSONL):
    try:
        j = json.loads(line)
    except Exception:
        continue
    if j.get("event") != "entry_dossier":
        continue
    d = j.get("details", {})
    s = d.get("surfaces", {})
    fs = s.get("flow_state", {})
    rl = s.get("reach_law", {})
    if fs.get("status") != "CONSULTED" and rl.get("status") != "CONSULTED":
        continue
    consults.append({
        "ts": j["ts_epoch"], "et_str": j["ts"], "tk": j.get("ticker", ""),
        "cat": d.get("cat"), "aim": d.get("aim"),
        "decision": d.get("decision"),
        "p30_live": fs.get("prints_30m"), "bucket_live": fs.get("bucket"),
        "pfill_live": rl.get("p_fill_1h"), "X_live": rl.get("depth_X")})

print("consultations found: %d" % len(consults))
tks = sorted({c["tk"] for c in consults if c["tk"]})
print("unique tickers: %d" % len(tks))

def fetch_trades(tk, oldest_needed):
    out, cursor = [], None
    for _page in range(120):
        url = ("https://api.elections.kalshi.com/trade-api/v2/markets/trades"
               "?ticker=%s&limit=500" % tk)
        if cursor:
            url += "&cursor=%s" % cursor
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                d = json.load(r)
        except Exception as e:
            print("  fetch error %s: %s" % (tk, e)); break
        rows = d.get("trades", [])
        for t in rows:
            ts = datetime.fromisoformat(
                t["created_time"].replace("Z", "+00:00")).timestamp()
            px = int(round(float(t["yes_price_dollars"]) * 100))
            out.append((ts, px))
        cursor = d.get("cursor")
        if not cursor or not rows or min(r0[0] for r0 in out) < oldest_needed:
            break
        time.sleep(0.15)
    else:
        # NO SILENT CAPS: a tape deeper than the page budget is NAMED,
        # never counted as zero (the first run counted KOA as 0 this way)
        print("  TRUNCATED %s: page budget hit, oldest fetched %s > needed"
              % (tk, datetime.fromtimestamp(
                  min(r0[0] for r0 in out), ET).strftime("%I:%M:%S %p")))
    if out and min(r0[0] for r0 in out) > oldest_needed:
        print("  WARNING %s: tape does not reach the window (oldest %s)"
              % (tk, datetime.fromtimestamp(
                  min(r0[0] for r0 in out), ET).strftime("%I:%M:%S %p")))
    return out

oldest = min(c["ts"] for c in consults) - 1900
tape = {}
for tk in tks:
    tape[tk] = fetch_trades(tk, oldest)

def bucket_of(n, thr):
    r = n / float(thr)
    return "quiet" if r < 0.25 else ("warm" if r < 1.0 else "open")

flips = defaultdict(lambda: defaultdict(int))
rows_out = []
aim_mismatch = 0
for c in consults:
    thr = THR.get(c["cat"])
    if not thr or not c["tk"]:
        continue
    tp = tape.get(c["tk"], [])
    p30_rest = sum(1 for ts, _ in tp if c["ts"] - 1800 < ts <= c["ts"])
    p30_used = max(p30_rest, c["p30_live"] or 0)
    b_live = c["bucket_live"] or bucket_of(c["p30_live"] or 0, thr)
    b_new = bucket_of(p30_used, thr)
    pxs = sorted(px for ts, px in tp if c["ts"] - 900 < ts <= c["ts"])
    med = pxs[len(pxs) // 2] if pxs else None
    pf_new = None
    if c["aim"] is not None and med is not None:
        X = min(max(int(round(med - c["aim"])), 1), 20)
        rate = LAW.get("%s|%s" % (c["cat"], b_new), {}) \
                  .get("rate_per_hr", {}).get(str(X), 0.0)
        pf_new = round(1 - math.exp(-rate), 3)
    flips[c["cat"]]["%s->%s" % (b_live, b_new)] += 1
    if b_live != b_new:
        rows_out.append((c["et_str"], c["tk"][-18:], c["cat"], c["decision"],
                         c["p30_live"], p30_rest, b_live, b_new,
                         c["pfill_live"], pf_new))

print("\n=== FOUNDING CASE (KOAYAZ) ===")
for c in consults:
    if "KOAYAZ" in c["tk"]:
        tp = tape.get(c["tk"], [])
        p30_rest = sum(1 for ts, _ in tp if c["ts"] - 1800 < ts <= c["ts"])
        print(" %s %s consulted: p30=%s bucket=%s p_fill=%s | REST p30=%d" %
              (c["et_str"], c["tk"][-8:], c["p30_live"], c["bucket_live"],
               c["pfill_live"], p30_rest))

print("\n=== PER-CAT BUCKET TRANSITIONS (live-consulted -> replayed-honest) ===")
for cat in sorted(flips):
    print(" %s: %s" % (cat, dict(flips[cat])))

print("\n=== FLIPPED CONSULTATIONS (%d) ===" % len(rows_out))
print(" %-24s %-18s %-9s %-24s ws rest  bucket        p_fill" % ("ts", "ticker", "cat", "decision"))
for r in rows_out[:40]:
    print(" %-24s %-18s %-9s %-24s %2s %4s  %s->%s  %s->%s" % r)

print("\n=== BEHAVIOR ISOLATION ===")
print("aims are atlas-page-priced upstream of the gauge; the gauge feeds")
print("the dossier record only. Per-line check: every 'placed:path_aim'")
print("dossier's aim equals the trendpath_live_aim path_aim on the same")
print("ticker (bucket-independent).")
aims_by_tk = {}
for line in open(JSONL):
    try:
        j = json.loads(line)
    except Exception:
        continue
    if j.get("event") == "trendpath_live_aim":
        aims_by_tk.setdefault(j.get("ticker", ""), []).append(
            j["details"].get("path_aim"))
n_ok = n_bad = 0
for c in consults:
    if c["decision"] == "placed:path_aim" and c["aim"] is not None:
        if c["aim"] in (aims_by_tk.get(c["tk"]) or []):
            n_ok += 1
        else:
            n_bad += 1
print("placed:path_aim dossiers: aim==page path_aim %d/%d (mismatch %d)"
      % (n_ok, n_ok + n_bad, n_bad))
