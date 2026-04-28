#!/usr/bin/env python3
"""
Greeks-style decomposition from kalshi_price_snapshots (5-min BBO, Apr 21-28).
Uses commence_time for lifecycle normalization.
"""
import sqlite3, json, csv, os, math
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"
ET = timezone(timedelta(hours=-4))

with open(os.path.join(BASE_DIR, "config/deploy_v4.json")) as f:
    cfg = json.load(f)
active_cells = cfg.get("active_cells", {})
ALL_CELLS = {}
for cell, params in active_cells.items():
    ALL_CELLS[cell] = params.get("exit_cents", 0)
DISABLED_EXITS = {
    "ATP_MAIN_underdog_40-44": 9, "ATP_CHALL_underdog_30-34": 15,
    "ATP_MAIN_leader_75-79": 14, "ATP_CHALL_underdog_25-29": 21,
    "ATP_MAIN_underdog_35-39": 12, "ATP_CHALL_leader_60-64": 6,
    "ATP_MAIN_leader_60-64": 15, "ATP_MAIN_underdog_25-29": 22,
    "ATP_CHALL_underdog_15-19": 31, "WTA_MAIN_leader_55-59": 10,
    "WTA_MAIN_underdog_40-44": 5, "WTA_MAIN_underdog_30-34": 16,
    "WTA_MAIN_underdog_35-39": 11, "ATP_MAIN_leader_55-59": 13,
    "ATP_MAIN_underdog_20-24": 25, "WTA_MAIN_leader_60-64": 8,
    "WTA_MAIN_underdog_15-19": 31, "WTA_MAIN_underdog_20-24": 22,
}
for cell, exit_c in DISABLED_EXITS.items():
    ALL_CELLS[cell] = exit_c

OPTIMAL_EXITS = {
    "ATP_CHALL_leader_50-54": 7, "ATP_CHALL_leader_55-59": 17,
    "ATP_CHALL_leader_60-64": 26, "ATP_CHALL_leader_65-69": 17,
    "ATP_CHALL_leader_70-74": 19, "ATP_CHALL_leader_75-79": 7,
    "ATP_CHALL_leader_80-84": 12, "ATP_CHALL_leader_85-89": 6,
    "ATP_CHALL_underdog_10-14": 35, "ATP_CHALL_underdog_15-19": 42,
    "ATP_CHALL_underdog_20-24": 65, "ATP_CHALL_underdog_25-29": 18,
    "ATP_CHALL_underdog_30-34": 7, "ATP_CHALL_underdog_35-39": 33,
    "ATP_CHALL_underdog_40-44": 27, "ATP_CHALL_underdog_45-49": 48,
    "ATP_MAIN_leader_50-54": 40, "ATP_MAIN_leader_55-59": 37,
    "ATP_MAIN_leader_60-64": 26, "ATP_MAIN_leader_70-74": 16,
    "ATP_MAIN_underdog_30-34": 8, "ATP_MAIN_underdog_35-39": 46,
    "ATP_MAIN_underdog_40-44": 4, "ATP_MAIN_underdog_45-49": 10,
    "WTA_MAIN_leader_50-54": 16, "WTA_MAIN_leader_60-64": 18,
    "WTA_MAIN_leader_65-69": 27, "WTA_MAIN_leader_70-74": 23,
    "WTA_MAIN_underdog_25-29": 17, "WTA_MAIN_underdog_35-39": 19,
    "WTA_MAIN_underdog_45-49": 15,
}

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

def get_tier(tk):
    if "KXATPMATCH" in tk and "CHALL" not in tk: return "ATP_MAIN"
    if "KXWTAMATCH" in tk and "CHALL" not in tk: return "WTA_MAIN"
    if "KXATPCHALL" in tk: return "ATP_CHALL"
    if "KXWTACHALL" in tk: return "WTA_CHALL"
    return None

conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()

# Pull all snapshots grouped by ticker, with commence_time
cur.execute("""SELECT ticker, polled_at, bid_cents, ask_cents, commence_time
    FROM kalshi_price_snapshots
    WHERE (ticker LIKE 'KXATP%' OR ticker LIKE 'KXWTA%')
    AND bid_cents > 0 AND ask_cents > 0 AND ask_cents < 100
    ORDER BY ticker, polled_at""")

# Build per-ticker price paths
ticker_paths = defaultdict(list)
ticker_commence = {}
for tk, polled, bid, ask, commence in cur.fetchall():
    mid = (bid + ask) / 2.0
    ticker_paths[tk].append((polled, mid, bid, ask))
    if commence and tk not in ticker_commence:
        ticker_commence[tk] = commence

conn.close()
print("Loaded %d tickers with price paths" % len(ticker_paths))

# For each ticker: classify into cell, extract lifecycle metrics
cell_matches = defaultdict(list)  # cell -> list of match dicts

for tk, path in ticker_paths.items():
    if len(path) < 10:
        continue
    tier = get_tier(tk)
    if not tier:
        continue

    # Entry = first snapshot
    entry_mid = path[0][1]
    entry_bid = path[0][2]
    entry_ts = path[0][0]

    cell = classify_cell(tier, entry_mid)
    if cell not in ALL_CELLS:
        continue

    # Commence time
    commence_str = ticker_commence.get(tk)
    if not commence_str:
        continue
    try:
        commence_dt = datetime.fromisoformat(commence_str.replace("Z", "+00:00"))
        commence_epoch = commence_dt.timestamp()
    except:
        continue

    # Parse entry timestamp
    try:
        entry_dt = datetime.strptime(entry_ts, "%Y-%m-%d %H:%M:%S")
        entry_dt = entry_dt.replace(tzinfo=ET)
        entry_epoch = entry_dt.timestamp()
    except:
        continue

    # Settlement = last snapshot
    last_mid = path[-1][1]
    last_ts = path[-1][0]
    try:
        last_dt = datetime.strptime(last_ts, "%Y-%m-%d %H:%M:%S")
        last_dt = last_dt.replace(tzinfo=ET)
        last_epoch = last_dt.timestamp()
    except:
        continue

    # Winner side if last price >= 90, loser if <= 10
    if last_mid >= 90:
        side = "winner"
    elif last_mid <= 10:
        side = "loser"
    else:
        side = "unsettled"
        continue  # skip unsettled

    total_duration_sec = last_epoch - entry_epoch
    if total_duration_sec < 600:  # skip < 10 min
        continue

    # Extract lifecycle samples
    all_mids = [m for _, m, _, _ in path]
    all_epochs = []
    for ts_str, _, _, _ in path:
        try:
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(tzinfo=ET)
            all_epochs.append(dt.timestamp())
        except:
            all_epochs.append(0)

    # Pregame = entry to commence
    # In-play = commence to settlement
    pregame_mids = [m for ep, m in zip(all_epochs, all_mids) if ep < commence_epoch and ep > 0]
    early_match_mids = [m for ep, m in zip(all_epochs, all_mids) if commence_epoch <= ep < commence_epoch + 1800]
    mid_match_mids = [m for ep, m in zip(all_epochs, all_mids) if commence_epoch + 1800 <= ep < commence_epoch + 3600]
    late_match_mids = [m for ep, m in zip(all_epochs, all_mids) if ep >= commence_epoch + 3600 and ep > 0]

    # Theta: price drift per minute
    pregame_duration_min = (commence_epoch - entry_epoch) / 60
    if pregame_duration_min > 5 and len(pregame_mids) >= 2:
        theta_pregame = (pregame_mids[-1] - pregame_mids[0]) / pregame_duration_min
    else:
        theta_pregame = None

    if len(early_match_mids) >= 2:
        early_dur_min = 30  # fixed 30-min window
        theta_early = (early_match_mids[-1] - early_match_mids[0]) / early_dur_min
    else:
        theta_early = None

    # Gamma: max excursion during match
    match_mids = [m for ep, m in zip(all_epochs, all_mids) if ep >= commence_epoch and ep > 0]
    if match_mids:
        gamma_excursion = (max(match_mids) - min(match_mids)) / entry_mid * 100
    else:
        gamma_excursion = None

    # Realized vega: stddev of price across all samples
    if len(all_mids) >= 5:
        mean_m = sum(all_mids) / len(all_mids)
        vega = (sum((m - mean_m) ** 2 for m in all_mids) / len(all_mids)) ** 0.5
    else:
        vega = None

    # Scalp timing: when did price first cross exit target?
    exit_c = OPTIMAL_EXITS.get(cell, ALL_CELLS[cell])
    target = min(99, entry_bid + exit_c)
    scalp_epoch = None
    for ep, m in zip(all_epochs, all_mids):
        if ep > 0 and m >= target:
            scalp_epoch = ep
            break

    scalp_phase = None
    if scalp_epoch:
        if scalp_epoch < commence_epoch:
            scalp_phase = "pregame"
        elif scalp_epoch < commence_epoch + 1800:
            scalp_phase = "early_match"  # 0-30 min
        elif scalp_epoch < commence_epoch + (last_epoch - commence_epoch) * 0.75:
            scalp_phase = "mid_match"
        else:
            # Check if within 5 min of settlement
            if last_epoch - scalp_epoch < 300:
                scalp_phase = "settlement"
            else:
                scalp_phase = "late_match"

    cell_matches[cell].append({
        "ticker": tk, "entry_mid": entry_mid, "entry_bid": entry_bid,
        "side": side, "last_mid": last_mid,
        "theta_pregame": theta_pregame, "theta_early": theta_early,
        "gamma_excursion": gamma_excursion, "vega": vega,
        "scalp_phase": scalp_phase, "exit_c": exit_c,
        "pregame_duration_min": pregame_duration_min,
        "total_duration_min": total_duration_sec / 60,
        "n_snapshots": len(path),
    })

# Output CSV
with open(os.path.join(OUT_DIR, "greeks_decomposition.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell", "N", "avg_entry", "exit_c",
                "theta_pregame_per_min", "theta_early_match_per_min",
                "gamma_avg_excursion_pct", "realized_vega",
                "pct_scalps_pregame", "pct_scalps_early_match",
                "pct_scalps_mid_match", "pct_scalps_late_match",
                "pct_scalps_at_settlement", "pct_no_scalp",
                "N_winner", "N_loser",
                "avg_pregame_duration_min", "avg_total_duration_min",
                "data_source"])

    for cell in sorted(ALL_CELLS.keys()):
        matches = cell_matches.get(cell, [])
        if len(matches) < 5:
            continue

        n = len(matches)
        avg_e = sum(m["entry_mid"] for m in matches) / n
        exit_c = matches[0]["exit_c"]

        # Theta
        thetas_pre = [m["theta_pregame"] for m in matches if m["theta_pregame"] is not None]
        thetas_early = [m["theta_early"] for m in matches if m["theta_early"] is not None]
        avg_theta_pre = sum(thetas_pre) / len(thetas_pre) if thetas_pre else 0
        avg_theta_early = sum(thetas_early) / len(thetas_early) if thetas_early else 0

        # Gamma
        gammas = [m["gamma_excursion"] for m in matches if m["gamma_excursion"] is not None]
        avg_gamma = sum(gammas) / len(gammas) if gammas else 0

        # Vega
        vegas = [m["vega"] for m in matches if m["vega"] is not None]
        avg_vega = sum(vegas) / len(vegas) if vegas else 0

        # Scalp timing distribution
        phases = [m["scalp_phase"] for m in matches]
        n_pregame = sum(1 for p in phases if p == "pregame")
        n_early = sum(1 for p in phases if p == "early_match")
        n_mid = sum(1 for p in phases if p == "mid_match")
        n_late = sum(1 for p in phases if p == "late_match")
        n_settle = sum(1 for p in phases if p == "settlement")
        n_no = sum(1 for p in phases if p is None)

        n_winner = sum(1 for m in matches if m["side"] == "winner")
        n_loser = sum(1 for m in matches if m["side"] == "loser")

        avg_pre_dur = sum(m["pregame_duration_min"] for m in matches) / n
        avg_total_dur = sum(m["total_duration_min"] for m in matches) / n

        w.writerow([cell, n, "%.1f" % avg_e, exit_c,
                     "%.4f" % avg_theta_pre, "%.4f" % avg_theta_early,
                     "%.1f" % avg_gamma, "%.1f" % avg_vega,
                     "%.1f" % (n_pregame / n * 100),
                     "%.1f" % (n_early / n * 100),
                     "%.1f" % (n_mid / n * 100),
                     "%.1f" % (n_late / n * 100),
                     "%.1f" % (n_settle / n * 100),
                     "%.1f" % (n_no / n * 100),
                     n_winner, n_loser,
                     "%.0f" % avg_pre_dur, "%.0f" % avg_total_dur,
                     "kalshi_price_snapshots Apr21-28 (5min intervals)"])

print("Written: greeks_decomposition.csv")
print("Cells with data: %d" % len([c for c in cell_matches if len(cell_matches[c]) >= 5]))

# Also output per-match detail for audit
with open(os.path.join(OUT_DIR, "greeks_per_match.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell", "ticker", "entry_mid", "entry_bid", "side", "last_mid",
                "exit_c", "target", "scalp_phase",
                "theta_pregame", "theta_early", "gamma_excursion_pct", "vega",
                "pregame_min", "total_min", "n_snapshots"])
    for cell in sorted(cell_matches.keys()):
        for m in cell_matches[cell]:
            target = min(99, m["entry_bid"] + m["exit_c"])
            w.writerow([cell, m["ticker"], "%.1f" % m["entry_mid"], m["entry_bid"],
                         m["side"], "%.1f" % m["last_mid"], m["exit_c"], "%.0f" % target,
                         m["scalp_phase"] or "none",
                         "%.4f" % m["theta_pregame"] if m["theta_pregame"] is not None else "",
                         "%.4f" % m["theta_early"] if m["theta_early"] is not None else "",
                         "%.1f" % m["gamma_excursion"] if m["gamma_excursion"] is not None else "",
                         "%.1f" % m["vega"] if m["vega"] is not None else "",
                         "%.0f" % m["pregame_duration_min"], "%.0f" % m["total_duration_min"],
                         m["n_snapshots"]])

print("Written: greeks_per_match.csv")
for fn in ["greeks_decomposition.csv", "greeks_per_match.csv"]:
    print("  %s: %.1f KB" % (fn, os.path.getsize(os.path.join(OUT_DIR, fn)) / 1024))
