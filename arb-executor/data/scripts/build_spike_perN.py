#!/usr/bin/env python3
"""Build per-N spike volatility parquet for a given category.

Reproducible canonical producer for data/durable/spike_volatility_map/<category>_spike_perN.parquet.
Replaces the inline-heredoc producer from chat session 2025-05-19; reproduces ATP_MAIN and WTA_MAIN
parquets (committed in 9912660) byte-identical.

Usage:
  python3 data/scripts/build_spike_perN.py --category ATP_MAIN --output /tmp/atp_main_spike_perN.parquet

Convention:
  - Anchor: real T-20m taker trade (t20m_trade_ts/t20m_trade_price from cell_economics)
  - Window: [anchor_ts, settlement_ts]
  - size_qual_max_250: highest price P where cumulative count_fp at-that-price-or-higher >= 250
  - spike_cents = (size_qual_max_250 - anchor_price) * 100
  - All time-window comparisons in microseconds (trade created_time parses to datetime64[us, UTC],
    so .astype('int64') is microseconds; bounds from Timestamp.value are nanoseconds and MUST be
    converted via .value // 1000)
"""

import argparse
import time
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyarrow.dataset as ds

CELL_ECON = "data/durable/rung0_cell_economics/cell_economics.parquet"
G9_TRADES = "data/durable/g9_trades.parquet"
VALID_CATEGORIES = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]

OUTPUT_COLS = [
    "ticker", "event_ticker", "partner_ticker",
    "anchor_price", "anchor_ts", "settlement_ts", "settlement_value",
    "old_metric_cents", "raw_max", "raw_max_ts", "size_qual_max_250",
    "spike_cents", "spike_pct", "truncation_delta_cents",
    "time_to_max_min", "drop_reason",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True, choices=VALID_CATEGORIES)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    t0 = time.time()

    cols = ["ticker", "category", "event_ticker", "paired_event_partner_ticker",
            "t20m_trade_ts", "t20m_trade_price", "settlement_ts",
            "settlement_value_dollars", "peak_bid_bounce_pre_resolution"]
    c = pq.read_table(CELL_ECON, columns=cols).to_pandas(timestamp_as_object=True)
    am = c[c.category == args.category].copy().reset_index(drop=True)
    N_total = len(am)
    print(f"{args.category} N={N_total}", flush=True)

    meta = {}
    a_us = {}
    s_us = {}
    for _, r in am.iterrows():
        tk = r.ticker
        ats = r.t20m_trade_ts
        sts = r.settlement_ts
        ap_v = r.t20m_trade_price
        valid = pd.notna(ats) and pd.notna(sts) and pd.notna(ap_v)
        meta[tk] = dict(
            event_ticker=r.event_ticker,
            partner_ticker=r.paired_event_partner_ticker,
            anchor_price=(float(ap_v) if pd.notna(ap_v) else None),
            anchor_ts=(pd.Timestamp(ats).tz_convert("UTC").isoformat() if pd.notna(ats) else None),
            settlement_ts=(pd.Timestamp(sts).tz_convert("UTC").isoformat() if pd.notna(sts) else None),
            settlement_value=(float(r.settlement_value_dollars) if pd.notna(r.settlement_value_dollars) else None),
            old_metric_cents=(round(float(r.peak_bid_bounce_pre_resolution) * 100, 4)
                              if pd.notna(r.peak_bid_bounce_pre_resolution) else None),
            valid=valid,
        )
        if valid:
            # CRITICAL: bounds in microseconds (trade timestamps parse to datetime64[us])
            a_us[tk] = pd.Timestamp(ats).value // 1000
            s_us[tk] = pd.Timestamp(sts).value // 1000

    scan = list(a_us.keys())
    print(f"valid={len(scan)}", flush=True)

    pmap = {tk: {} for tk in scan}
    dset = ds.dataset(G9_TRADES, format="parquet")
    sc = dset.scanner(
        columns=["ticker", "created_time", "yes_price_dollars", "count_fp"],
        filter=ds.field("ticker").isin(scan),
        batch_size=300000,
    )
    nb = 0
    kept_tot = 0
    for b in sc.to_batches():
        if b.num_rows == 0:
            continue
        d = b.to_pandas()
        # tsus = microseconds since epoch (datetime64[us, UTC] -> int64 = us)
        tsus = pd.to_datetime(d["created_time"], utc=True, format="ISO8601").astype("int64").to_numpy()
        lo = d["ticker"].map(a_us).to_numpy()
        hi = d["ticker"].map(s_us).to_numpy()
        mask = (~pd.isna(lo)) & (tsus >= lo) & (tsus <= hi)
        k = d[mask]
        ksus = tsus[mask]
        for tk, price, cf, ts in zip(k.ticker.values, k.yes_price_dollars.values,
                                     k.count_fp.values, ksus):
            m = pmap[tk]
            e = m.get(price)
            if e is None:
                m[price] = [int(cf), int(ts)]
            else:
                e[0] += int(cf)
                if ts < e[1]:
                    e[1] = int(ts)
        kept_tot += len(k)
        nb += 1
    print(f"streamed {nb} batches kept_rows={kept_tot} elapsed={time.time()-t0:.1f}s", flush=True)

    recs = []
    for tk in am.ticker:
        mt = meta[tk]
        rec = dict(
            ticker=tk,
            event_ticker=mt["event_ticker"],
            partner_ticker=mt["partner_ticker"],
            anchor_price=mt["anchor_price"],
            anchor_ts=mt["anchor_ts"],
            settlement_ts=mt["settlement_ts"],
            settlement_value=mt["settlement_value"],
            old_metric_cents=mt["old_metric_cents"],
            raw_max=None,
            raw_max_ts=None,
            size_qual_max_250=None,
            spike_cents=None,
            spike_pct=None,
            truncation_delta_cents=None,
            time_to_max_min=None,
            drop_reason=None,
        )
        if not mt["valid"]:
            rec["drop_reason"] = "no_anchor_or_settle"
            recs.append(rec)
            continue
        m = pmap.get(tk)
        if not m:
            rec["drop_reason"] = "no_trades_in_window"
            recs.append(rec)
            continue
        ap_v = mt["anchor_price"]
        au = a_us[tk]
        prices = sorted(m.keys(), reverse=True)
        raw = prices[0]
        rec["raw_max"] = float(raw)
        rec["raw_max_ts"] = pd.Timestamp(m[raw][1], unit="us", tz="UTC").isoformat()
        cum = 0
        P = None
        for p in prices:
            cum += m[p][0]
            if cum >= 250:
                P = p
                break
        if P is None:
            P = prices[-1]
            rec["drop_reason"] = "lt250ct_total"
        rec["size_qual_max_250"] = float(P)
        rec["spike_cents"] = round((P - ap_v) * 100, 4)
        rec["spike_pct"] = round((P - ap_v) / ap_v * 100, 4) if ap_v else None
        if mt["old_metric_cents"] is not None:
            rec["truncation_delta_cents"] = round(rec["spike_cents"] - mt["old_metric_cents"], 4)
        rec["time_to_max_min"] = round((m[P][1] - au) / 1e6 / 60.0, 3)
        recs.append(rec)

    df = pd.DataFrame(recs)
    df = df[OUTPUT_COLS]   # explicit column ordering for schema stability
    df.to_parquet(args.output, index=False)
    ok = df[df.drop_reason.isna() | (df.drop_reason == "lt250ct_total")]
    print(f"WROTE {args.output} rows={len(df)} computed={len(ok)} coverage={len(ok)/N_total*100:.2f}% elapsed={time.time()-t0:.1f}s", flush=True)
    print("DROP_COUNTS " + repr(df.drop_reason.value_counts(dropna=False).to_dict()), flush=True)
    print("DONE_MARKER", flush=True)


if __name__ == "__main__":
    main()
