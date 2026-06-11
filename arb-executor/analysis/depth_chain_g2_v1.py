"""
G2 DEPTH-CHAIN STUDY v1 (ROADMAP G2, operator-driven). READ-ONLY.

Data: analysis/premarket_ticks/*.csv[.gz] -- 5-level book with per-level sizes
at tick cadence (ts_et, bid_1..bid_5+sz, ask_1..ask_5+sz, mid, bid_depth_5,
ask_depth_5, depth_ratio=bid_share, last_trade).

PRE-REGISTERED QUESTIONS (answers only; no strategy design):
 Q1 P(fill | depth-ahead): simulated join at best_bid at T-240/180/120/60
    snapshots, depth_ahead = bid_1_sz (back of queue). Forward to T-15:
    CERTAIN fill = strict traded-through (last_trade < L) or book crossed past
    (ask_1 < L); TOUCHED = certain OR print/ask AT L. Emit by depth quartile x
    category x price band.
 Q2 Walls vs our placements: wall = bid level with size >= K x median of the
    other 4 levels (K in {3,5,10}). Placement P = last_trade - offset (per-
    regime argmax LUT, replay parity), classified at-wall / BURIED (wall
    between P and mid) / in-front / no-wall; realized touch rate per class.
    Exhibits: 26JUN11CORCOL (Collarini), 26JUN10MANRIN (Mannarino),
    26JUN11SWEHAR (Billy Harris).
 Q3 Imbalance as drift: depth_ratio at t vs mid drift over +15/30/60 min.
    Pearson r + ratio-bin mean drift, by category x tts bucket.
 Q4 Realism calibration for joins: P(certain | touched, depth quartile) vs the
    0.5x/0.7x engagement-replay bracket.
Null is a valid answer and will be stated plainly.
"""
import csv, gzip, glob, os, math, json, hashlib, statistics, collections
from datetime import datetime
from zoneinfo import ZoneInfo
import pyarrow as pa, pyarrow.parquet as pq

ROOT = "/root/Omi-Workspace/arb-executor"
TICKS = ROOT + "/analysis/premarket_ticks"
TAPE = ROOT + "/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1 = ROOT + "/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
OUTDIR = ROOT + "/data/durable/depth_chain"; os.makedirs(OUTDIR, exist_ok=True)
ET = ZoneInfo("America/New_York")
SNAPS = (240.0, 180.0, 120.0, 60.0)
KS = (3, 5, 10)
EXHIBITS = ("KXATPCHALLENGERMATCH-26JUN11CORCOL", "KXATPMATCH-26JUN10MANRIN",
            "KXATPCHALLENGERMATCH-26JUN11SWEHAR")
BANDS = [(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
         (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"
def cat_of(tk):
    if tk.startswith("KXATPCHALLENGERMATCH"): return "ATP_CHALL"
    if tk.startswith("KXWTACHALLENGERMATCH"): return "WTA_CHALL"
    if tk.startswith("KXATPMATCH"): return "ATP_MAIN"
    if tk.startswith("KXWTAMATCH"): return "WTA_MAIN"
    return None

# ---- start map: tape parquet + jsonl schedule_match fallback (recent days) ----
starts = {}
t = pq.ParquetFile(TAPE).read(columns=["ticker","match_start_ts","match_start_method"])
for tk, ms, mm in zip(t.column(0).to_pylist(), t.column(1).to_pylist(), t.column(2).to_pylist()):
    if mm != "unknown" and ms: starts[tk] = ms
ev_start = {}
for jf in sorted(glob.glob(ROOT + "/logs/live_v3_2026*.jsonl")):
    for line in open(jf, errors="ignore"):
        if '"schedule_match"' not in line: continue
        try: e = json.loads(line)
        except: continue
        d = e.get("details", {})
        st = d.get("start_time", "")
        try:
            ts = datetime.fromisoformat(st.replace("Z", "+00:00")).timestamp()
            ev_start[d["event"]] = ts   # last write wins (latest schedule)
        except: continue
print("starts: tape=%d  jsonl events=%d" % (len(starts), len(ev_start)), flush=True)

# ---- offset LUT (replay parity: per-regime argmax expected_improvement) ----
lut = {}
pb = pq.read_table(PBV1).to_pandas()
for r in pb.loc[pb.groupby(["category","anchor_regime"]).expected_improvement_cents.idxmax()].itertuples():
    lut[(r.category, r.anchor_regime)] = int(r.bid_offset_cents)

def start_for(tk):
    if tk in starts: return starts[tk]
    et_ = tk.rsplit("-", 1)[0]
    return ev_start.get(et_)

# ---- accumulators ----
joins = []          # (cat, bandL, S, depth_ahead, touched, certain)
wallrows = collections.defaultdict(lambda: [0, 0])   # (K, cls) -> [n, touched]
q3 = collections.defaultdict(lambda: [0,0.0,0.0,0.0,0.0,0.0])  # (cat,bucket,dt)->n,Sx,Sy,Sxy,Sxx,Syy
q3bins = collections.defaultdict(lambda: [0, 0.0])   # (cat,bucket,dt,bin)->n,sum_drift
exhibit_out = []
n_files = n_used = n_nostart = n_rows = 0

def parse_file(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", errors="ignore") as f:
        rd = csv.reader(f)
        head = next(rd, None)
        if not head or head[0] != "ts_et": return None
        rows = []
        for r in rd:
            try:
                ts = datetime.strptime(r[0], "%Y-%m-%d %I:%M:%S %p")
                b1, b1s = float(r[2] or 0), float(r[3] or 0)
                bl = [(float(r[2+2*i] or 0), float(r[3+2*i] or 0)) for i in range(5)]
                a1 = float(r[12] or 0)
                mid = float(r[22] or 0)
                bd, ad = float(r[23] or 0), float(r[24] or 0)
                lt = float(r[26] or 0)
                rows.append((ts, b1, b1s, bl, a1, mid, bd, ad, lt))
            except (ValueError, IndexError):
                continue
        return rows

for path in sorted(glob.glob(TICKS + "/*.csv") + glob.glob(TICKS + "/*.csv.gz")):
    n_files += 1
    tk = os.path.basename(path).replace(".csv.gz", "").replace(".csv", "")
    cat = cat_of(tk)
    if cat is None: continue
    ms = start_for(tk)
    if not ms:
        n_nostart += 1; continue
    msdt = datetime.fromtimestamp(ms, ET).replace(tzinfo=None)
    rows = parse_file(path)
    if not rows: continue
    rows.sort(key=lambda r: r[0])
    # tts in minutes for each row
    seq = [((msdt - r[0]).total_seconds()/60.0,) + r for r in rows]
    seq = [s for s in seq if 14.0 <= s[0] <= 246.0]
    if len(seq) < 10: continue
    n_used += 1; n_rows += len(seq)
    is_exhibit = tk.rsplit("-",1)[0] in EXHIBITS
    # ---------- Q1/Q4 joins + Q2 walls at snapshots ----------
    for S in SNAPS:
        snap = next((s for s in seq if s[0] <= S), None)
        if snap is None or snap[0] < S - 30: continue
        tts0, ts0, b1, b1s, bl, a1, mid0, bd, ad, lt0 = snap
        if not (1 <= b1 < a1 <= 99): continue
        L = int(round(b1)); depth = b1s
        fwd = [s for s in seq if s[0] < tts0 and s[0] >= 15.0]
        certain = touched = False
        for s in fwd:
            _, _, fb1, _, _, fa1, _, _, _, flt = s
            if (flt > 0 and flt < L) or (0 < fa1 < L): certain = True; touched = True; break
            if flt == L or fa1 == L: touched = True
        joins.append((cat, band(L), int(S), depth, touched, certain))
        # Q2: placement vs walls (needs a print for the anchor)
        if lt0 > 0:
            anchor = max(1, min(99, int(round(lt0))))
            off = lut.get((cat, band(anchor)), 1)
            P = max(1, anchor - off)
            sizes = [sz for (_, sz) in bl]
            prices = [p for (p, _) in bl]
            for K in KS:
                cls = "no_wall"; wall_lvls = []
                for i in range(5):
                    if prices[i] <= 0: continue
                    others = [sizes[j] for j in range(5) if j != i and prices[j] > 0]
                    medo = statistics.median(others) if others else 0
                    if medo > 0 and sizes[i] >= K * medo: wall_lvls.append(prices[i])
                if wall_lvls:
                    if any(abs(w - P) < 0.5 for w in wall_lvls): cls = "at_wall"
                    elif any(w > P for w in wall_lvls): cls = "buried_behind_wall"
                    else: cls = "in_front_of_wall"
                ptouch = any((s[9] > 0 and s[9] <= P) or (0 < s[5] <= P)
                             for s in fwd)
                w = wallrows[(K, cls)]; w[0] += 1; w[1] += int(ptouch)
            if is_exhibit and S in (180.0, 120.0):
                exhibit_out.append((tk, S, dict(bid_levels=bl, ask1=a1, lt=lt0,
                    bd5=bd, ad5=ad, P=P, depth_at_b1=b1s)))
    # ---------- Q3 imbalance -> drift ----------
    last_t = None
    mids = [(s[1], s[0], s[6], s[7], s[8]) for s in seq]   # (ts, tts, mid, bd, ad)
    for idx, (ts_, tts_, mid_, bd_, ad_) in enumerate(mids):
        if mid_ <= 0 or bd_ + ad_ <= 0: continue
        if last_t is not None and (ts_ - last_t).total_seconds() < 60: continue
        last_t = ts_
        ratio = bd_ / (bd_ + ad_)
        bucket = "T240_T60" if tts_ > 60 else "T60_T15"
        for dt in (15, 30, 60):
            tgt = tts_ - dt
            if tgt < 14: continue
            fm = next((m for (t2, tt2, m, _, _) in mids[idx:] if tt2 <= tgt), None)
            if fm is None or fm <= 0: continue
            drift = fm - mid_
            k = (cat, bucket, dt); a = q3[k]
            a[0] += 1; a[1] += ratio; a[2] += drift; a[3] += ratio*drift
            a[4] += ratio*ratio; a[5] += drift*drift
            bi = min(4, int(ratio * 5))
            qb = q3bins[(cat, bucket, dt, bi)]; qb[0] += 1; qb[1] += drift
    if n_used % 500 == 0:
        print("...%d files used, %d rows" % (n_used, n_rows), flush=True)

print("files=%d used=%d nostart=%d rows=%d joins=%d" % (n_files, n_used, n_nostart, n_rows, len(joins)), flush=True)

# ================= aggregate + output =================
out = []
depths = sorted(j[3] for j in joins)
qs = [depths[int(len(depths)*q)] for q in (0.25, 0.5, 0.75)] if depths else [0,0,0]
def dq(d):
    return "Q1_thin" if d <= qs[0] else ("Q2" if d <= qs[1] else ("Q3" if d <= qs[2] else "Q4_wall"))
agg = collections.defaultdict(lambda: [0,0,0])
for cat, bd_, S, d, t_, c_ in joins:
    for key in ((cat, bd_, S, dq(d)), (cat, "ALL", 0, dq(d))):
        a = agg[key]; a[0] += 1; a[1] += int(t_); a[2] += int(c_)
for (cat, bd_, S, q), (n, t_, c_) in sorted(agg.items()):
    out.append(dict(q="Q1", category=cat, band=bd_, snap=S, depth_quartile=q,
        n_joins=n, p_touched=round(t_/n,4), p_fill_certain=round(c_/n,4),
        p_fill_given_touched=round(c_/t_,4) if t_ else None))
for (K, cls), (n, t_) in sorted(wallrows.items()):
    out.append(dict(q="Q2", K=K, wall_class=cls, n=n, touch_rate=round(t_/n,4) if n else None))
for (cat, bucket, dt), (n, sx, sy, sxy, sxx, syy) in sorted(q3.items()):
    if n < 50: continue
    cov = sxy/n - (sx/n)*(sy/n)
    vx = sxx/n - (sx/n)**2; vy = syy/n - (sy/n)**2
    r = cov/math.sqrt(vx*vy) if vx > 0 and vy > 0 else 0.0
    row = dict(q="Q3", category=cat, tts_bucket=bucket, horizon_min=dt, n=n,
               pearson_r=round(r,4))
    for bi in range(5):
        qb = q3bins.get((cat, bucket, dt, bi))
        row["bin%d_mean_drift_c" % bi] = round(qb[1]/qb[0], 3) if qb and qb[0] else None
    out.append(row)
tbl = pa.Table.from_pylist(out)
OUTP = OUTDIR + "/depth_chain_g2_v1.parquet"
pq.write_table(tbl, OUTP)
sha = hashlib.sha256(open(OUTP, "rb").read()).hexdigest()

print("\n=== Q1: P(fill) by depth quartile (pooled bands, quartile bounds %s) ===" % qs)
for (cat, bd_, S, q), (n, t_, c_) in sorted(agg.items()):
    if bd_ == "ALL":
        print("  %-9s %-8s N=%5d touched=%.3f certain=%.3f cert|touch=%s" % (
            cat, q, n, t_/n, c_/n, ("%.3f" % (c_/t_)) if t_ else "-"))
print("=== Q2: wall classes (touch rate of our placement level) ===")
for (K, cls), (n, t_) in sorted(wallrows.items()):
    print("  K=%-2d %-20s n=%5d touch=%.3f" % (K, cls, n, t_/n if n else 0))
print("=== Q3: imbalance->drift (pearson r; bins 0-0.2..0.8-1.0 mean drift cents) ===")
for row in out:
    if row.get("q") == "Q3":
        print("  %-9s %-8s +%2dm n=%6d r=%+.3f bins=%s" % (row["category"], row["tts_bucket"],
            row["horizon_min"], row["n"], row["pearson_r"],
            [row.get("bin%d_mean_drift_c" % b) for b in range(5)]))
print("=== EXHIBITS ===")
for tk, S, d in exhibit_out:
    print("  %s @T-%d: bid_levels=%s ask1=%s lt=%s bd5/ad5=%s/%s P=%s depth@b1=%s" % (
        tk, int(S), d["bid_levels"], d["ask1"], d["lt"], d["bd5"], d["ad5"], d["P"], d["depth_at_b1"]))
print("\nparquet", OUTP); print("sha256", sha)
json.dump(dict(sha256=sha, rows=len(out), files=n_files, used=n_used,
    nostart=n_nostart, tick_rows=n_rows, n_joins=len(joins),
    depth_quartile_bounds=qs), open(OUTDIR + "/_g2_meta.json", "w"), indent=1)
print("DONE.")
