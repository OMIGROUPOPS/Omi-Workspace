#!/usr/bin/env python3
"""Plot per_minute_universe_phase1 output against g9_trades for visual chart-reproduction.

PASS criterion: visual inspection by Druid + chat-side, comparing against the chart
Druid uploaded yesterday (Jun 18 2025 Rune match, full lifecycle).
"""

import os
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pyarrow.parquet as pq

DUR_DIR = "/root/Omi-Workspace/arb-executor/data/durable"
PROBE = os.path.join(DUR_DIR, "per_minute_universe", "probe", "per_minute_universe_phase1.parquet")
TRADES = os.path.join(DUR_DIR, "g9_trades.parquet")
OUT_PNG = os.path.join(DUR_DIR, "per_minute_universe", "probe", "phase1_rune_chart.png")

# UTC offset for ET display (Jun 18 is EDT, UTC-4)
ET_OFFSET_HRS = -4


def main():
    df = pd.read_parquet(PROBE)
    ticker = df["ticker"].iloc[0]
    partner_ticker = df["partner_ticker"].iloc[0] if "partner_ticker" in df.columns and pd.notna(df["partner_ticker"].iloc[0]) else None
    df["dt_et"] = pd.to_datetime(df["minute_ts"] + ET_OFFSET_HRS * 3600, unit="s")

    trades = pq.read_table(
        TRADES,
        columns=["ticker", "created_time", "taker_side", "yes_price_dollars", "count_fp"],
        filters=[("ticker", "=", ticker)],
    ).to_pandas()
    trades["dt_et"] = pd.to_datetime(trades["created_time"], format="ISO8601") + pd.Timedelta(hours=ET_OFFSET_HRS)

    partner_trades = None
    if partner_ticker is not None:
        partner_trades = pq.read_table(
            TRADES,
            columns=["ticker", "created_time", "taker_side", "yes_price_dollars", "count_fp"],
            filters=[("ticker", "=", partner_ticker)],
        ).to_pandas()
        if len(partner_trades) > 0:
            partner_trades["dt_et"] = pd.to_datetime(partner_trades["created_time"], format="ISO8601") + pd.Timedelta(hours=ET_OFFSET_HRS)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True,
                                    gridspec_kw={"height_ratios": [3, 1]})

    # --- Top panel: bid/ask + trade scatter (own + partner overlay) ---
    ax1.fill_between(df["dt_et"], df["yes_bid_close"], df["yes_ask_close"],
                     alpha=0.15, color="grey", label=f"Own spread ({ticker.split('-')[-1]})")
    ax1.plot(df["dt_et"], df["yes_bid_close"], color="tab:blue", linewidth=1.6,
             label=f"own yes_bid_close ({ticker.split('-')[-1]})")
    ax1.plot(df["dt_et"], df["yes_ask_close"], color="tab:red", linewidth=1.6,
             label=f"own yes_ask_close ({ticker.split('-')[-1]})")

    # Partner overlay (dashed, lighter)
    if partner_ticker is not None and "partner_yes_bid_close" in df.columns:
        pt_short = partner_ticker.split('-')[-1]
        ax1.plot(df["dt_et"], df["partner_yes_bid_close"], color="tab:green", linewidth=1.2,
                 linestyle="--", alpha=0.85, label=f"partner yes_bid_close ({pt_short})")
        ax1.plot(df["dt_et"], df["partner_yes_ask_close"], color="tab:orange", linewidth=1.2,
                 linestyle="--", alpha=0.85, label=f"partner yes_ask_close ({pt_short})")

    yes_trades = trades[trades["taker_side"] == "yes"]
    no_trades = trades[trades["taker_side"] == "no"]
    if len(yes_trades) > 0:
        ax1.scatter(yes_trades["dt_et"], yes_trades["yes_price_dollars"],
                    s=30, color="tab:red", marker="^", alpha=0.85, zorder=5,
                    label=f"own taker=yes ({len(yes_trades)})")
    if len(no_trades) > 0:
        ax1.scatter(no_trades["dt_et"], no_trades["yes_price_dollars"],
                    s=30, color="tab:blue", marker="v", alpha=0.85, zorder=5,
                    label=f"own taker=no ({len(no_trades)})")

    # Partner trades at half opacity
    if partner_trades is not None and len(partner_trades) > 0:
        pt_yes = partner_trades[partner_trades["taker_side"] == "yes"]
        pt_no = partner_trades[partner_trades["taker_side"] == "no"]
        if len(pt_yes) > 0:
            ax1.scatter(pt_yes["dt_et"], pt_yes["yes_price_dollars"],
                        s=22, color="tab:orange", marker="^", alpha=0.45, zorder=4,
                        label=f"partner taker=yes ({len(pt_yes)})")
        if len(pt_no) > 0:
            ax1.scatter(pt_no["dt_et"], pt_no["yes_price_dollars"],
                        s=22, color="tab:green", marker="v", alpha=0.45, zorder=4,
                        label=f"partner taker=no ({len(pt_no)})")

    # Vertical lines: open, match_start (fallback), settlement
    open_ts = int(df["open_time_ts"].iloc[0])
    settle_ts = int(df["settlement_ts"].iloc[0])
    match_start_ts = int(df["match_start_ts"].iloc[0])
    match_start_method = df["match_start_method"].iloc[0]
    expected_exp_ts = int(df["expected_expiration_ts"].iloc[0])

    open_dt = pd.to_datetime(open_ts + ET_OFFSET_HRS * 3600, unit="s")
    settle_dt = pd.to_datetime(settle_ts + ET_OFFSET_HRS * 3600, unit="s")
    ms_dt = pd.to_datetime(match_start_ts + ET_OFFSET_HRS * 3600, unit="s")
    first_trade_dt = trades["dt_et"].min() if len(trades) > 0 else None
    exp_exp_dt = pd.to_datetime(expected_exp_ts + ET_OFFSET_HRS * 3600, unit="s")

    ax1.axvline(open_dt, color="green", linestyle="--", alpha=0.6,
                label=f"open_time ({open_dt.strftime('%H:%M')} ET)")
    ax1.axvline(ms_dt, color="orange", linestyle=":", alpha=0.8,
                label=f"match_start [{match_start_method}] ({ms_dt.strftime('%H:%M')} ET)")
    if first_trade_dt is not None:
        ax1.axvline(first_trade_dt, color="purple", linestyle="-.", alpha=0.7,
                    label=f"first_trade ({first_trade_dt.strftime('%H:%M:%S')} ET)")
    ax1.axvline(settle_dt, color="black", linestyle="--", alpha=0.6,
                label=f"settlement ({settle_dt.strftime('%H:%M')} ET)")

    # Premarket-phase shading
    formation_mask = df["premarket_phase"] == "formation"
    if formation_mask.any():
        f_start = df.loc[formation_mask, "dt_et"].min()
        f_end = df.loc[formation_mask, "dt_et"].max()
        ax1.axvspan(f_start, f_end, color="yellow", alpha=0.08, label="premarket_phase=formation")

    ax1.set_ylim(0, 1.0)
    ax1.set_ylabel("Price ($)", fontsize=11)
    title = (f"Per-Minute Universe Phase 1 — {ticker}\n"
             f"{df['result'].iloc[0]}=settled ${df['settlement_value'].iloc[0]:.2f}  |  "
             f"210 candle minutes, {len(trades)} trade events  |  "
             f"premarket: {(df['regime']=='premarket').sum()} min, "
             f"in_match: {(df['regime']=='in_match').sum()} min")
    ax1.set_title(title, fontsize=11)
    ax1.legend(loc="center left", fontsize=8, framealpha=0.85)
    ax1.grid(True, alpha=0.3)

    # --- Bottom panel: per-minute trade volume + taker_flow ---
    bar_width_min = 1
    ax2.bar(df["dt_et"], df["taker_yes_count_in_minute"],
            width=pd.Timedelta(minutes=bar_width_min), color="tab:red", alpha=0.6,
            label="taker_yes count")
    ax2.bar(df["dt_et"], -df["taker_no_count_in_minute"],
            width=pd.Timedelta(minutes=bar_width_min), color="tab:blue", alpha=0.6,
            label="taker_no count")
    ax2.axhline(0, color="black", linewidth=0.5)
    ax2.set_ylabel("Per-minute taker count", fontsize=10)
    ax2.set_xlabel("Time (ET, June 18 2025)", fontsize=11)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.setp(ax2.get_xticklabels(), rotation=0)

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=110)
    print(f"Wrote {OUT_PNG}: {os.path.getsize(OUT_PNG):,} bytes")


if __name__ == "__main__":
    main()
