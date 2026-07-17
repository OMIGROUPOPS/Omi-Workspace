#!/usr/bin/env python3
"""ENTRY-MECHANICS retro census (P1 + P3), 07-17. Read-only over the engine
logs. Three sections:
  A. fitted-hour vs discovery placement (queue/cents bill)  [P1]
  B. orientation column: how often the leader-rises role-prior called the
     realized riser wrong                                    [P1]
  C. flow-window re-grade: today's join_queue reads recomputed from the
     trade's BIRTH (first placement) vs the last-post clock  [P3]
Run on the VPS from arb-executor/.  Output: /tmp/ENTRYMECH_CENSUS.md
"""
import json, glob, sys
from collections import defaultdict
import statistics

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ENTRYMECH_CENSUS.md"
LOGS = sorted(glob.glob("logs/live_v3_2026071[5-7].jsonl"))

first_seen = {}
placed = []
joinq = []            # (tk, ts, outcome, fill_latency_sec, reposts)
first_post = {}       # tk -> first order_placed(buy) ts
wopen = {}            # tk -> window_open price
lastpx = {}           # tk -> last aim_shadow tape_last / book mid
fills_ts = {}         # tk -> first entry fill ts

for path in LOGS:
    for line in open(path, encoding="utf-8", errors="replace"):
        if '"event"' not in line:
            continue
        try:
            j = json.loads(line)
        except ValueError:
            continue
        ev = j.get("event"); tk = j.get("ticker") or ""
        d = j.get("details") or {}
        et = d.get("event") or (tk.rsplit("-", 1)[0] if "-" in tk else "")
        ts = j.get("ts_epoch")
        if et and ts and et not in first_seen:
            first_seen[et] = ts
        if ev == "order_placed" and d.get("action") == "buy" and tk not in first_post:
            first_post[tk] = ts
        elif ev == "v4_place":
            placed.append((et, tk, ts))
        elif ev == "join_queue":
            joinq.append((tk, ts, d.get("outcome"),
                          d.get("fill_latency_sec"), d.get("reposts")))
        elif ev == "window_open_set":
            wopen.setdefault(tk, d.get("price"))
        elif ev == "aim_shadow":
            if d.get("tape_last"):
                lastpx[tk] = d["tape_last"]
            elif d.get("book_bid"):
                lastpx[tk] = d.get("book_bid")
        elif ev == "entry_filled" and tk not in fills_ts:
            fills_ts[tk] = ts

L = ["# ENTRY-MECHANICS RETRO CENSUS — 07-17 (P1 queue bill · P1 "
     "orientation column · P3 flow re-grade)", ""]

# A — the fitted-hour bill
lags = [(tk, (ts - first_seen[et]) / 3600.0) for et, tk, ts in placed
        if et in first_seen and ts]
lh = sorted(l for _, l in lags)
L.append("## A. THE FITTED-HOUR BILL (Jul 15-17 logs, %d placements)" % len(lags))
if lh:
    L.append("- discovery -> placement lag: median %.2fh · p25 %.2fh · "
             "p75 %.2fh · max %.1fh" % (statistics.median(lh),
                                        lh[len(lh)//4], lh[3*len(lh)//4],
                                        lh[-1]))
    L.append("- placements waiting >4h after the event was on the tape: "
             "**%d of %d (%.0f%%)**"
             % (sum(1 for l in lh if l > 4), len(lh),
                100.0 * sum(1 for l in lh if l > 4) / len(lh)))
L.append("- queue forfeited at the fitted-hour join (join_queue "
         "depth_at_post, earlier pull): median 300 shares, p75 2,176 — "
         "the queue a discovery-time park would have owned.")
L.append("")

# B — orientation column: leader-rises prior vs realized
pairs = defaultdict(dict)
for tk, p in wopen.items():
    if p:
        pairs[tk.rsplit("-", 1)[0]][tk] = p
right = wrong = und = 0
for et, legs in pairs.items():
    if len(legs) != 2:
        continue
    (tka, pa), (tkb, pb) = sorted(legs.items(), key=lambda x: -x[1])
    la, lb = lastpx.get(tka), lastpx.get(tkb)
    if la is None or lb is None or pa == pb:
        und += 1
        continue
    leader_rose = (la - pa) > (lb - pb)   # relative: who gained
    if abs((la - pa) - (lb - pb)) < 3:
        und += 1
        continue
    if leader_rose:
        right += 1
    else:
        wrong += 1
n_call = right + wrong
L.append("## B. ORIENTATION COLUMN — the leader-rises role-prior vs the "
         "realized riser")
L.append("- basis: window-open price vs last observed print/bid per leg "
         "(shadow-series resolution); relative-gain winner = realized "
         "riser; moves <3c apart = undetermined.")
L.append("- **prior called the riser RIGHT %d / WRONG %d (%.0f%% wrong) · "
         "undetermined %d** of %d two-leg events observed"
         % (right, wrong, (100.0 * wrong / n_call) if n_call else 0.0,
            und, len(pairs)))
L.append("")

# C — P3 flow re-grade: join_queue latency from birth vs last post
regraded = []
for tk, ts, outcome, lat, reposts in joinq:
    fp = first_post.get(tk)
    if fp and ts and lat is not None and lat >= 0:
        true_lat = ts - fp
        regraded.append((tk, outcome, lat, true_lat, reposts or 0))
if regraded:
    short = [r for r in regraded if r[4] and r[3] > 2 * max(r[2], 1)]
    L.append("## C. P3 RE-GRADE — today's join_queue reads, birth-clock vs "
             "last-post clock (%d reads)" % len(regraded))
    L.append("- reads whose birth-latency is >2x the order-age latency the "
             "meter reported (the churn-blinded class): **%d of %d "
             "(%.0f%%)**" % (len(short), len(regraded),
                             100.0 * len(short) / len(regraded)))
    _meds = statistics.median([r[2] for r in regraded])
    _medt = statistics.median([r[3] for r in regraded])
    L.append("- median reported latency %.0fs vs median TRUE (birth) "
             "latency %.0fs — the meter under-read the wait by %.1fx"
             % (_meds, _medt, _medt / max(_meds, 1)))
    worst = sorted(regraded, key=lambda r: -(r[3] - r[2]))[:5]
    for tk, oc, lat, tl, rp in worst:
        L.append("    - %s %s: reported %.0fs, true %.0fs, %d reposts"
                 % (tk.split("-")[-2][-8:] + "-" + tk.split("-")[-1],
                    oc, lat, tl, rp))
else:
    L.append("## C. P3 RE-GRADE — no join_queue reads in range")
L.append("")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote %s (%d lines)" % (OUT, len(L)))
