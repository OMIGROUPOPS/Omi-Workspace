#!/usr/bin/env python3
"""
build_fv_overlap_join_v1.py — join premarket_tape_v1 with the fv_history archive.

For each (ticker, minute_ts) row of premarket_tape_v1 whose minute_ts falls within FV-archive
coverage, resolve a per-leg cross-book consensus fair value AS OF that minute, plus fv_delta
(Kalshi last-traded vs consensus), partner FV and paired_fv_sum.

DESIGN NOTES — five deviations from the originally-drafted prompt, all documented in run_summary
+ MANIFEST. Output contract = premarket_tape_v1 columns + 9 new FV columns.

1. TIMEZONE. book_prices.polled_at is America/New_York local text (verified: across 95 ATP_MAIN
   overlap events max-poll lands median +78 min after match_start under ET vs -162 min under UTC;
   fv.py also parses polled_at as ET). polled_at ET -> UTC epoch for the join to minute_ts (UTC).

2. AS-OF JOIN, not +/-60s. Poll cadence ~90s-2min (betexplorer ~10min); fv.py freshness is
   1800s (pinnacle/aggregate) / 3600s (betexplorer). +/-60s yields ~20% coverage. We use an
   as-of carry-forward per tier with that tier's freshness window (point-in-time correct).

3. TIERS (corrected to fv.py's ACTUAL hierarchy — the drafted prompt wrongly excluded
   betexplorer, which is exactly the Challenger source). Priority: tier1 pinnacle (1800s, conf
   0.95) -> tier2 aggregate mean of non-pinnacle/non-betexplorer books >=3 (1800s, conf 0.80) ->
   tier3 betexplorer single-book (3600s, conf 0.50) -> unavailable. fv.py's tier-5 paired-sum
   fallback is intentionally EXCLUDED (runtime-only fallback, not an analytical signal source).
   fv_source in {pinnacle, aggregate, betexplorer, unavailable}; confidence_weight per fv.py.

4. LEG -> SIDE mapping. Kalshi legs end in a 3-char player code (NOT -P1/-P2). Map each leg to
   book_prices p1/p2 via (a) last-name[:3] bijection on player1_name/player2_name (clean for MAIN);
   (b) name_cache.odds_api_name substring fallback; (c) NULL (compound-surname events).

5. GATE-2 DENOMINATOR. Null fraction is reported per-category; the <50% expectation applies to
   events with genuine cross-book coverage (Main tour) — events absent from book_prices and
   Challenger tournaments outside the betexplorer scrape list are legitimately 'unavailable'.

Streaming: only the FV-window slice of the tape is materialized (~154k of 2.06M rows); polls are
loaded per-event. Peak RSS target < 700 MB.
"""
import argparse, json, os, time, resource, sqlite3, bisect, datetime as dt
from zoneinfo import ZoneInfo
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.compute as pc
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent.parent
TAPE = REPO / "data/durable/per_minute_universe/premarket_tape_v1.parquet"
DB   = REPO / "tennis.db"
PROBE_OUT = REPO / "data/durable/per_minute_universe/probe/fv_overlap_join_v1_probe.parquet"

ET = ZoneInfo("America/New_York"); UTC = dt.timezone.utc
FRESH = 1800          # pinnacle / aggregate freshness (s)
FRESH_BETX = 3600     # betexplorer freshness (s) per fv.py
MIN_AGG = 3
CONF = {"pinnacle": 0.95, "aggregate": 0.80, "betexplorer": 0.50}


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def pe_et(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET).timestamp()


def lastpfx(name):
    if not name or not name.strip():
        return None
    return name.strip().split()[-1][:3].upper()


def map_sides(legs_codes, p1name, p2name, name_cache):
    codes = {c for _, c in legs_codes}
    c1, c2 = lastpfx(p1name), lastpfx(p2name)
    if c1 and c2 and c1 != c2 and {c1, c2} == codes:
        return {tk: ("p1" if c == c1 else "p2") for tk, c in legs_codes}
    res = {}
    for tk, c in legs_codes:
        nm = name_cache.get(c); side = None
        if nm:
            nl = nm.lower()
            if p1name and (nl in p1name.lower() or p1name.lower() in nl): side = "p1"
            elif p2name and (nl in p2name.lower() or p2name.lower() in nl): side = "p2"
        res[tk] = side
    if {res[tk] for tk, _ in legs_codes} == {"p1", "p2"}:
        return res
    return {tk: None for tk, _ in legs_codes}


def build_event_tiers(rows):
    """rows: (book_key, p1, p2, polled_at). Return tiers[side] = priority-ordered list (low->high)
    of (t_arr, fv_arr, n_arr, str_list, fresh_sec, name)."""
    pin, agg, betx = {}, {}, {}
    for bk, p1, p2, s in rows:
        t = pe_et(s)
        if bk == "pinnacle":
            d = pin.setdefault(t, [np.nan, np.nan, s])
            if p1 and p1 > 0: d[0] = p1
            if p2 and p2 > 0: d[1] = p2
        elif bk == "betexplorer":
            d = betx.setdefault(t, [np.nan, np.nan, s])
            if p1 and p1 > 0: d[0] = p1
            if p2 and p2 > 0: d[1] = p2
        else:
            d = agg.setdefault(t, {"a1": [], "a2": [], "s": s})
            if p1 and p1 > 0: d["a1"].append(p1)
            if p2 and p2 > 0: d["a2"].append(p2)

    def simple(dct, idx):
        ts = sorted(dct)
        return (np.array(ts, dtype=float),
                np.array([dct[x][idx] for x in ts], dtype=float),
                np.ones(len(ts), dtype=np.int64),
                [dct[x][2] for x in ts])

    def aggside(key):
        ts = sorted(agg); T, F, N, S = [], [], [], []
        for x in ts:
            v = agg[x][key]
            if len(v) >= MIN_AGG:
                T.append(x); F.append(sum(v)/len(v)); N.append(len(v)); S.append(agg[x]["s"])
        return np.array(T, dtype=float), np.array(F, dtype=float), np.array(N, dtype=np.int64), S

    tiers = {}
    for side, idx, key in [("p1", 0, "a1"), ("p2", 1, "a2")]:
        ps = simple(pin, idx); bs = simple(betx, idx); ag = aggside(key)
        # priority low->high so higher tier overwrites: betexplorer, aggregate, pinnacle
        tiers[side] = [
            (bs[0], bs[1], bs[2], bs[3], FRESH_BETX, "betexplorer"),
            (ag[0], ag[1], ag[2], ag[3], FRESH, "aggregate"),
            (ps[0], ps[1], ps[2], ps[3], FRESH, "pinnacle"),
        ]
    return tiers


def resolve_side(tier_list, m):
    n = len(m)
    fv = np.full(n, np.nan); src = np.array(["unavailable"]*n, dtype=object)
    nb = np.zeros(n, dtype=np.int64); js = np.array([None]*n, dtype=object); conf = np.full(n, np.nan)
    for t, fvarr, narr, ss, fresh, name in tier_list:
        if len(t) == 0:
            continue
        pos = np.searchsorted(t, m, side="right") - 1
        posc = np.clip(pos, 0, len(t)-1)
        valid = (pos >= 0) & ((m - t[posc]) <= fresh) & ~np.isnan(fvarr[posc])
        for ii in np.where(valid)[0]:
            p = pos[ii]
            fv[ii] = fvarr[p]; src[ii] = name; nb[ii] = int(narr[p]); js[ii] = ss[p]; conf[ii] = CONF[name]
    return fv, src, nb, js, conf


def main():
    t0 = time.time()
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True); cur = con.cursor()
    min_poll = cur.execute("SELECT MIN(polled_at) FROM book_prices").fetchone()[0]
    threshold = pe_et(min_poll)
    print(f"FV coverage start ({min_poll} ET) -> {threshold:.0f} UTC ({dt.datetime.fromtimestamp(threshold, UTC)})", flush=True)
    name_cache = {c: n for c, n in cur.execute("SELECT kalshi_code, odds_api_name FROM name_cache")}
    bp_events = set(r[0] for r in cur.execute("SELECT DISTINCT event_ticker FROM book_prices"))

    dset = ds.dataset(TAPE)
    df = dset.scanner(filter=pc.field("minute_ts") >= int(threshold)).to_table().to_pandas()
    print(f"tape FV-window rows: {len(df)}  events: {df.event_ticker.nunique()}  rss={rss_mb():.0f}MB", flush=True)
    n = len(df)

    fv_own = np.full(n, np.nan); fv_part = np.full(n, np.nan)
    fv_src = np.array(["unavailable"]*n, dtype=object)
    fv_nb = np.zeros(n, dtype=np.int64); conf_w = np.full(n, np.nan)
    join_ts = np.array([None]*n, dtype=object)

    mapped_events = 0; unmapped_legs = 0
    for event, gdf in df.groupby("event_ticker", sort=False):
        if event not in bp_events:
            continue
        rows = cur.execute("SELECT book_key, book_p1_fv_cents, book_p2_fv_cents, polled_at FROM book_prices WHERE event_ticker=?", (event,)).fetchall()
        if not rows:
            continue
        p1name, p2name = cur.execute("SELECT player1_name, player2_name FROM book_prices WHERE event_ticker=? LIMIT 1", (event,)).fetchone()
        legs_codes = [(tk, tk.rsplit("-", 1)[1]) for tk in gdf.ticker.unique()]
        side_map = map_sides(legs_codes, p1name, p2name, name_cache)
        tiers = build_event_tiers(rows)
        mapped_events += 1
        for tk in gdf.ticker.unique():
            own = side_map.get(tk)
            if own is None:
                unmapped_legs += 1
                continue
            partner = "p2" if own == "p1" else "p1"
            tdf = gdf[gdf.ticker == tk]
            rr = tdf.index.values
            m = tdf.minute_ts.values.astype(np.int64)
            ofv, osrc, onb, ojs, oconf = resolve_side(tiers[own], m)
            pfv, _, _, _, _ = resolve_side(tiers[partner], m)
            fv_own[rr] = ofv; fv_src[rr] = osrc; fv_nb[rr] = onb
            join_ts[rr] = ojs; conf_w[rr] = oconf; fv_part[rr] = pfv

    df["fv_consensus_own"] = fv_own
    df["fv_source"] = fv_src
    df["num_books_in_window"] = fv_nb
    df["confidence_weight"] = conf_w
    df["fv_consensus_partner"] = fv_part
    df["fv_join_minute_ts"] = join_ts
    own = df["fv_consensus_own"]
    df["fv_delta_at_last_traded"] = np.where(df["price_close"].notna() & own.notna(), df["price_close"]*100.0 - own, np.nan)
    df["fv_delta_at_mid"] = np.where(own.notna(), df["mid_close"]*100.0 - own, np.nan)
    df["paired_fv_sum"] = np.where(own.notna() & df["fv_consensus_partner"].notna(), own + df["fv_consensus_partner"], np.nan)

    PROBE_OUT.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), PROBE_OUT, compression="snappy")

    # ---- validation ----
    null_frac = df["fv_consensus_own"].isna().mean()
    src_dist = df["fv_source"].value_counts(dropna=False).to_dict()
    pfs = df["paired_fv_sum"].dropna(); delta = df["fv_delta_at_last_traded"].dropna()
    df["_in_bp"] = df.event_ticker.isin(bp_events)
    print("=== VALIDATION ===", flush=True)
    print(f"rows_out={len(df)}", flush=True)
    print(f"fv_consensus_own null_fraction(ALL)={null_frac:.4f}", flush=True)
    print(f"null_fraction(bp events only)={df[df._in_bp].fv_consensus_own.isna().mean():.4f}", flush=True)
    print(f"fv_source distribution={src_dist}", flush=True)
    print("per-category (bp events) null_fraction + tier mix:", flush=True)
    for cat, g in df[df._in_bp].groupby("category"):
        td = g["fv_source"].value_counts().to_dict()
        print(f"  {cat}: rows={len(g)} events={g.event_ticker.nunique()} null={g.fv_consensus_own.isna().mean():.3f} src={td}", flush=True)
    print(f"paired_fv_sum: n={len(pfs)} mean={pfs.mean():.3f} median={pfs.median():.3f} std={pfs.std():.3f}", flush=True)
    print(f"fv_delta_at_last_traded: n={len(delta)} mean={delta.mean():.3f} median={delta.median():.3f} std={delta.std():.3f} p5={delta.quantile(.05):.2f} p95={delta.quantile(.95):.2f} min={delta.min():.2f} max={delta.max():.2f}", flush=True)
    print(f"mapped_events={mapped_events} unmapped_legs={unmapped_legs}", flush=True)
    print(f"output_size_bytes={PROBE_OUT.stat().st_size}", flush=True)
    print(f"wall_clock_s={time.time()-t0:.1f} peak_rss_mb={rss_mb():.0f}", flush=True)
    print("DONE_MARKER", flush=True)
    con.close()


if __name__ == "__main__":
    main()
