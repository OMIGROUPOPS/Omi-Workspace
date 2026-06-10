"""[C-DETECTOR-EVAL] Score the LIVE liveness detector against the foundation's
labeled match starts. READ-ONLY; consumes match_start_ts/match_start_method (tuned
corpus labels) -- no re-derivation of what a start looks like.

Tier mapping (explicit): tier-1 = both_sides_trade_density, tier-2 =
both_sides_price_discovery (trade-signal-labeled cohort); tier-3/floor =
expected_expiration_fallback (+ tickers absent from the foundation). Tournament
names do not exist in corpus data (verified: market_metadata carries no title) --
sub-class tail axis = category x ISO week, disclosed in the summary.

Detector replay: >= K prints summed across both legs within T seconds, LATCHED
(first crossing ever). Sweep K in {5,10,15,20} x T in {30,60,120}.
Output: /tmp/detector_eval_v1.parquet (long format) + /tmp/detector_eval_summary.txt
"""
import csv
import glob
import json
import sys
import collections
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path("/root/Omi-Workspace/arb-executor")
HIST = ROOT / "data" / "historical_pull" / "trades"
TAPE = ROOT / "data/durable/per_minute_universe/premarket_tape_v1.parquet"
KS = [5, 10, 15, 20]
TS = [30, 60, 120]
TIER12 = {"both_sides_trade_density": 1, "both_sides_price_discovery": 2}

# ---- foundation labels ----
pf = pq.ParquetFile(TAPE)
lab = {}
for i in range(pf.metadata.num_row_groups):
    rg = pf.read_row_group(i, columns=["ticker", "category", "match_start_ts", "match_start_method"])
    for t, c, s, m in zip(rg.column("ticker").to_pylist(), rg.column("category").to_pylist(),
                          rg.column("match_start_ts").to_pylist(), rg.column("match_start_method").to_pylist()):
        if t in lab or s is None:
            continue
        try:
            ts = s.timestamp() if hasattr(s, "timestamp") else float(s)
        except Exception:
            continue
        lab[t] = (ts, m, (c or "?").upper())
floor = collections.Counter()
events = {}
for t, (ts, m, c) in lab.items():
    et = t.rsplit("-", 1)[0]
    tier = TIER12.get(m)
    if tier is None:
        floor[c] += 1
        continue
    cur = events.get(et)
    if cur is None or ts < cur[0]:
        events[et] = (ts, tier, c)
print("foundation tickers=%d tier12_events=%d floor_tickers(tier3)=%s"
      % (len(lab), len(events), dict(floor)), file=sys.stderr)

def latches(prints):
    """one pass -> {(K,T): first_latch_ts or None}"""
    prints.sort()
    out = {}
    for T in TS:
        j = 0
        first = {K: None for K in KS}
        need = set(KS)
        for i, ts in enumerate(prints):
            while prints[j] < ts - T:
                j += 1
            n = i - j + 1
            for K in list(need):
                if n >= K:
                    first[K] = ts
                    need.discard(K)
            if not need:
                break
        for K in KS:
            out[(K, T)] = first[K]
    return out

rows = []
n_cov = n_nofile = 0
for et, (start, tier, cat) in sorted(events.items()):
    files = list(HIST.glob(et + "-*"))
    prints = []
    for p in files:
        try:
            for row in csv.DictReader(open(p)):
                try:
                    prints.append(datetime.fromisoformat(
                        row["created_time"].replace("Z", "+00:00")).timestamp())
                except Exception:
                    continue
        except Exception:
            continue
    if not prints:
        n_nofile += 1
        continue
    n_cov += 1
    week = datetime.fromtimestamp(start, timezone.utc).strftime("%G-W%V")
    lt = latches(prints)
    for (K, T), l in lt.items():
        lat = (l - start) if l is not None else None
        if l is None:
            verdict = "never"
        elif lat < -1800:
            verdict = "false_fire_ge30m"
        elif lat < -60:
            verdict = "false_fire_1_30m"
        elif lat <= 0:
            verdict = "early_le60s"
        else:
            verdict = "latched_after_start"
        rows.append({"event": et, "category": cat, "tier": tier, "week": week,
                     "n_prints": len(prints), "K": K, "T": T,
                     "start_ts": start, "latch_ts": l,
                     "latency_sec": round(lat, 1) if lat is not None else None,
                     "verdict": verdict})
print("events covered=%d no_trade_files=%d" % (n_cov, n_nofile), file=sys.stderr)
pq.write_table(pa.Table.from_pylist(rows), "/tmp/detector_eval_v1.parquet")

# ---- measured cancel latency (live jsonl; detect -> cancel-ack pairs) ----
pairs = []
inter = []
for lf in sorted(glob.glob(str(ROOT / "logs" / "live_v3_2026*.jsonl"))):
    det = []
    cancels = []
    for l in open(lf, errors="replace"):
        if '"match_live_detected"' in l or '"order_cancelled"' in l:
            try:
                e = json.loads(l)
            except Exception:
                continue
            if e["event"] == "match_live_detected":
                det.append((e["ts_epoch"], e["details"].get("event", "")))
            else:
                cancels.append((e["ts_epoch"], e.get("ticker", ""),
                                e["details"].get("label", "")))
    for dts, ev in det:
        for cts, tk, lbl in cancels:
            if 0 <= cts - dts <= 30 and ev and ev in tk:
                pairs.append(cts - dts)
                break
    cancels.sort()
    for a, b in zip(cancels, cancels[1:]):
        d = b[0] - a[0]
        if 0 < d <= 2.0:
            inter.append(d)

# ---- summary ----
S = []
A = S.append
df = collections.defaultdict(list)
agg = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    key = (r["K"], r["T"])
    agg[key][r["verdict"]] += 1
    if r["verdict"] == "latched_after_start":
        df[key].append(r["latency_sec"])
A("[C-DETECTOR-EVAL] live detector vs foundation labels (tier-1/2 trade-signal starts)")
A("cohort: %d tier-1/2 events with trade files (no-file: %d); tier-3 floor below" % (n_cov, n_nofile))
A("")
A("K/T sweep -- %% of events: latched-after-start / early<=60s / false 1-30m / false >=30m / never ; latency p50/p90/p99 (s)")
for K in KS:
    for T in TS:
        key = (K, T)
        c = agg[key]
        tot = sum(c.values())
        ds = sorted(df[key])
        def q(p):
            return ds[min(len(ds) - 1, int(len(ds) * p))] if ds else float("nan")
        mark = "  <== DEPLOYED" if (K, T) == (10, 60) else ""
        A("K=%2d T=%3ds | %5.1f%% / %4.1f%% / %4.1f%% / %4.1f%% / %4.1f%% | p50=%5.0f p90=%5.0f p99=%6.0f%s" % (
            K, T, 100*c["latched_after_start"]/tot, 100*c["early_le60s"]/tot,
            100*c["false_fire_1_30m"]/tot, 100*c["false_fire_ge30m"]/tot,
            100*c["never"]/tot, q(.5), q(.9), q(.99), mark))
A("")
A("DEPLOYED (10/60) per category: latency p50/p90/p99 ; never%% ; false>=30m%%")
cat_lat = collections.defaultdict(list)
cat_v = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    if (r["K"], r["T"]) != (10, 60):
        continue
    cat_v[r["category"]][r["verdict"]] += 1
    if r["verdict"] == "latched_after_start":
        cat_lat[r["category"]].append(r["latency_sec"])
for c in sorted(cat_v):
    ds = sorted(cat_lat[c])
    tot = sum(cat_v[c].values())
    def q2(p):
        return ds[min(len(ds) - 1, int(len(ds) * p))] if ds else float("nan")
    A("  %-10s p50=%5.0f p90=%5.0f p99=%6.0f | never %4.1f%% | false>=30m %4.1f%%" % (
        c, q2(.5), q2(.9), q2(.99), 100*cat_v[c]["never"]/tot, 100*cat_v[c]["false_fire_ge30m"]/tot))
A("")
A("sub-class tail (10/60, category x ISO-week; tournament names absent from corpus -- disclosed):")
wk = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    if (r["K"], r["T"]) == (10, 60):
        wk[(r["category"], r["week"])][r["verdict"]] += 1
worst = sorted(wk.items(), key=lambda kv: -(kv[1]["never"] + kv[1]["false_fire_ge30m"]))[:5]
for (c, w), v in worst:
    tot = sum(v.values())
    A("  %-10s %s: never %d + false>=30m %d of %d" % (c, w, v["never"], v["false_fire_ge30m"], tot))
A("")
A("structural floor (tier-3 expected_expiration_fallback tickers; detector blind by construction):")
A("  %s" % dict(floor))
A("")
if pairs:
    pairs.sort()
    A("measured detect->cancel-ack latency (live jsonl, %d pairs): p50=%.1fs max=%.1fs" % (
        len(pairs), pairs[len(pairs)//2], pairs[-1]))
else:
    A("measured detect->cancel-ack: NO live match_live_detected->cancel pairs in June jsonls;")
    inter.sort()
    if inter:
        A("  fallback inter-cancel ack spacing (n=%d): p50=%.2fs p90=%.2fs (API roundtrip+rate-limit proxy)" % (
            len(inter), inter[len(inter)//2], inter[int(len(inter)*0.9)]))
A("danger window = latency above + cancel latency; dominated by latency term.")
open("/tmp/detector_eval_summary.txt", "w").write("\n".join(S) + "\n")
print("\n".join(S))
