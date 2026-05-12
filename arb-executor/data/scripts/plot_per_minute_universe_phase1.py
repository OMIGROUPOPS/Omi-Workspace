#!/usr/bin/env python3
"""Plot per_minute_universe_phase1 output as a three-panel chart for visual review.

Per spec Section 2.9 + Section 2.10 + v3 amendment:
- Top panel: own ticker universe (BBO + own trades + lifecycle markers)
- Middle panel: partner ticker universe (BBO + partner trades + lifecycle markers)
- Bottom panel: paired derived signals (paired_mid_sum, paired_arb_gap_maker, partner_volume_ratio)

PASS criterion: visual inspection by Druid + chat-side.
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
CANDLES = os.path.join(DUR_DIR, "g9_candles.parquet")
TRADES = os.path.join(DUR_DIR, "g9_trades.parquet")
OUT_PNG = os.path.join(DUR_DIR, "per_minute_universe", "probe", "phase1_rune_chart.png")

# UTC offset for ET display (Jun 18 is EDT, UTC-4)
ET_OFFSET_HRS = -4


def _to_et(ts_unix):
    return pd.to_datetime(ts_unix + ET_OFFSET_HRS * 3600, unit="s")


def _load_trades(ticker):
    t = pq.read_table(
        TRADES,
        columns=["ticker", "created_time", "taker_side", "yes_price_dollars", "count_fp"],
        filters=[("ticker", "=", ticker)],
    ).to_pandas()
    if len(t) == 0:
        return t
    t["dt_et"] = pd.to_datetime(t["created_time"], format="ISO8601") + pd.Timedelta(hours=ET_OFFSET_HRS)
    return t


def _load_candles_partner(ticker):
    """Load partner candles directly from g9_candles for the middle panel BBO."""
    t = pq.read_table(
        CANDLES,
        columns=["ticker", "end_period_ts", "yes_bid_close", "yes_ask_close"],
        filters=[("ticker", "=", ticker)],
    ).to_pandas().sort_values("end_period_ts").reset_index(drop=True)
    if len(t) == 0:
        return t
    t["dt_et"] = pd.to_datetime(t["end_period_ts"] + ET_OFFSET_HRS * 3600, unit="s")
    return t


def _draw_lifecycle_markers(ax, df, label_match_start=False):
    """Vertical lines for open_time, match_start, first_trade, settlement on a given axis."""
    open_ts = int(df["open_time_ts"].iloc[0])
    settle_ts = int(df["settlement_ts"].iloc[0])
    match_start_ts = int(df["match_start_ts"].iloc[0]) if pd.notna(df["match_start_ts"].iloc[0]) else None
    match_start_method = df["match_start_method"].iloc[0]

    ax.axvline(_to_et(open_ts), color="green", linestyle="--", alpha=0.5,
               label=f"open_time ({_to_et(open_ts).strftime('%H:%M')} ET)" if label_match_start else None)
    if match_start_ts is not None:
        ax.axvline(_to_et(match_start_ts), color="orange", linestyle=":", alpha=0.85, linewidth=1.6,
                   label=f"match_start [{match_start_method}] ({_to_et(match_start_ts).strftime('%H:%M')} ET)"
                         if label_match_start else None)
    ax.axvline(_to_et(settle_ts), color="black", linestyle="--", alpha=0.5,
               label=f"settlement ({_to_et(settle_ts).strftime('%H:%M')} ET)" if label_match_start else None)


def main():
    df = pd.read_parquet(PROBE)
    own_ticker = df["ticker"].iloc[0]
    partner_ticker = df["partner_ticker"].iloc[0] if pd.notna(df["partner_ticker"].iloc[0]) else None
    df["dt_et"] = pd.to_datetime(df["minute_ts"] + ET_OFFSET_HRS * 3600, unit="s")

    own_trades = _load_trades(own_ticker)
    partner_trades = _load_trades(partner_ticker) if partner_ticker else pd.DataFrame()
    partner_candles = _load_candles_partner(partner_ticker) if partner_ticker else pd.DataFrame()

    fig, (ax_own, ax_partner, ax_paired) = plt.subplots(
        3, 1, figsize=(15, 13), sharex=True,
        gridspec_kw={"height_ratios": [3, 3, 2]}
    )

    # ============================================================
    # Top panel — own ticker (RUN)
    # ============================================================
    own_short = own_ticker.split("-")[-1]
    ax_own.fill_between(df["dt_et"], df["yes_bid_close"], df["yes_ask_close"],
                        alpha=0.15, color="grey", label=f"{own_short} spread")
    ax_own.plot(df["dt_et"], df["yes_bid_close"], color="tab:blue", linewidth=1.6,
                label=f"{own_short} yes_bid_close")
    ax_own.plot(df["dt_et"], df["yes_ask_close"], color="tab:red", linewidth=1.6,
                label=f"{own_short} yes_ask_close")

    own_yes = own_trades[own_trades["taker_side"] == "yes"] if len(own_trades) else own_trades
    own_no = own_trades[own_trades["taker_side"] == "no"] if len(own_trades) else own_trades
    if len(own_yes) > 0:
        ax_own.scatter(own_yes["dt_et"], own_yes["yes_price_dollars"],
                       s=28, color="tab:red", marker="^", alpha=0.85, zorder=5,
                       label=f"{own_short} taker=yes ({len(own_yes)})")
    if len(own_no) > 0:
        ax_own.scatter(own_no["dt_et"], own_no["yes_price_dollars"],
                       s=28, color="tab:blue", marker="v", alpha=0.85, zorder=5,
                       label=f"{own_short} taker=no ({len(own_no)})")

    _draw_lifecycle_markers(ax_own, df, label_match_start=True)
    first_trade_dt = own_trades["dt_et"].min() if len(own_trades) > 0 else None
    if first_trade_dt is not None:
        ax_own.axvline(first_trade_dt, color="purple", linestyle="-.", alpha=0.7,
                       label=f"first_trade ({first_trade_dt.strftime('%H:%M:%S')} ET)")
    formation_mask = df["premarket_phase"] == "formation"
    if formation_mask.any():
        f_start = df.loc[formation_mask, "dt_et"].min()
        f_end = df.loc[formation_mask, "dt_et"].max()
        ax_own.axvspan(f_start, f_end, color="yellow", alpha=0.08, label="formation phase")

    ax_own.set_ylim(0, 1.0)
    ax_own.set_ylabel("Price ($)", fontsize=11)
    title = (f"Per-Minute Universe Phase 1 v3 — {own_ticker}  +  {partner_ticker or '(no partner)'}\n"
             f"own: settled ${df['settlement_value'].iloc[0]:.2f} ({df['result'].iloc[0]}) | "
             f"210 candle minutes, {len(own_trades)} own trades, {len(partner_trades)} partner trades | "
             f"premarket: {(df['regime']=='premarket').sum()} min, in_match: {(df['regime']=='in_match').sum()} min")
    ax_own.set_title(title, fontsize=10)
    ax_own.legend(loc="center left", fontsize=8, framealpha=0.85, ncol=2)
    ax_own.grid(True, alpha=0.3)

    # ============================================================
    # Middle panel — partner ticker (MCD)
    # ============================================================
    if partner_ticker and len(partner_candles) > 0:
        pt_short = partner_ticker.split("-")[-1]
        ax_partner.fill_between(partner_candles["dt_et"], partner_candles["yes_bid_close"],
                                partner_candles["yes_ask_close"],
                                alpha=0.15, color="grey", label=f"{pt_short} spread")
        ax_partner.plot(partner_candles["dt_et"], partner_candles["yes_bid_close"],
                        color="tab:green", linewidth=1.6, linestyle="-",
                        label=f"{pt_short} yes_bid_close")
        ax_partner.plot(partner_candles["dt_et"], partner_candles["yes_ask_close"],
                        color="tab:orange", linewidth=1.6, linestyle="-",
                        label=f"{pt_short} yes_ask_close")

        pt_yes = partner_trades[partner_trades["taker_side"] == "yes"] if len(partner_trades) else partner_trades
        pt_no = partner_trades[partner_trades["taker_side"] == "no"] if len(partner_trades) else partner_trades
        if len(pt_yes) > 0:
            ax_partner.scatter(pt_yes["dt_et"], pt_yes["yes_price_dollars"],
                               s=28, color="tab:orange", marker="^", alpha=0.85, zorder=5,
                               label=f"{pt_short} taker=yes ({len(pt_yes)})")
        if len(pt_no) > 0:
            ax_partner.scatter(pt_no["dt_et"], pt_no["yes_price_dollars"],
                               s=28, color="tab:green", marker="v", alpha=0.85, zorder=5,
                               label=f"{pt_short} taker=no ({len(pt_no)})")

        _draw_lifecycle_markers(ax_partner, df, label_match_start=False)
        if formation_mask.any():
            ax_partner.axvspan(f_start, f_end, color="yellow", alpha=0.08)

    ax_partner.set_ylim(0, 1.0)
    ax_partner.set_ylabel("Price ($)", fontsize=11)
    ax_partner.set_title(f"Partner: {partner_ticker or 'none'} (inverse-side structure expected)",
                         fontsize=10)
    ax_partner.legend(loc="center left", fontsize=8, framealpha=0.85, ncol=2)
    ax_partner.grid(True, alpha=0.3)

    # ============================================================
    # Bottom panel — paired derived signals
    # ============================================================
    ax_paired.plot(df["dt_et"], df["paired_mid_sum"], color="tab:purple", linewidth=1.4,
                   label="paired_mid_sum (should ≈ $1)")
    ax_paired.axhline(1.0, color="tab:purple", linestyle=":", alpha=0.5)
    ax_paired.plot(df["dt_et"], df["paired_arb_gap_maker"], color="tab:brown", linewidth=1.4,
                   alpha=0.8, label="paired_arb_gap_maker ($1 − paired_yes_bid_sum)")
    if "partner_volume_ratio" in df.columns and df["partner_volume_ratio"].notna().any():
        ax_paired.plot(df["dt_et"], df["partner_volume_ratio"], color="tab:gray", linewidth=1.4,
                       alpha=0.8, label="partner_volume_ratio (own / (own+partner))")
    else:
        ax_paired.text(0.02, 0.5, "partner_volume_ratio: all null (historical-tier g9_candles.volume_fp)",
                       transform=ax_paired.transAxes, fontsize=9, color="gray", alpha=0.7)

    _draw_lifecycle_markers(ax_paired, df, label_match_start=False)
    ax_paired.set_ylim(0, 1.5)
    ax_paired.set_ylabel("Paired signal value", fontsize=11)
    ax_paired.set_xlabel("Time (ET, June 18 2025)", fontsize=11)
    ax_paired.legend(loc="upper left", fontsize=9, framealpha=0.85)
    ax_paired.grid(True, alpha=0.3)

    ax_paired.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax_paired.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.setp(ax_paired.get_xticklabels(), rotation=0)

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=110)
    print(f"Wrote {OUT_PNG}: {os.path.getsize(OUT_PNG):,} bytes")


if __name__ == "__main__":
    main()
