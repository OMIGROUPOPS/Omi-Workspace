#!/usr/bin/env python3
"""Per-entry verification of ATP_CHALL_underdog_20-24 at +65c optimal exit."""
import sqlite3, json, csv, os
from collections import defaultdict

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()
cur.execute("""SELECT event_ticker, category, winner, loser,
    first_price_winner, min_price_winner, max_price_winner, last_price_winner,
    first_price_loser, total_trades, first_ts, last_ts,
    min_price_loser, max_price_loser
    FROM historical_events
    WHERE first_ts > '2026-03-20' AND first_ts < '2026-04-18'
    AND total_trades >= 10
    AND category = 'ATP_CHALL'""")
events = cur.fetchall()
conn.close()

TARGET_CELL = "ATP_CHALL_underdog_20-24"
EXIT_C = 65
QTY = 10

with open(os.path.join(OUT_DIR, "verify_underdog_2024_at_65c.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["row","event_ticker","side_code","entry_price","target_absolute",
                "max_price_this_side","scalp_fired","max_minus_target",
                "settlement_side","settle_price",
                "max_within_3c_of_99","max_at_99",
                "pnl_cents_if_scalp","pnl_cents_if_settle",
                "pnl_cents_actual","first_ts","last_ts"])

    row_num = 0
    for ev in events:
        evt = ev[0]
        fp_w, min_w, max_w, last_w = ev[4], ev[5], ev[6], ev[7]
        fp_l, min_l, max_l = ev[8], ev[12], ev[13]

        # Check winner side
        if fp_w and 0 < fp_w < 100:
            c = classify_cell("ATP_CHALL", fp_w)
            if c == TARGET_CELL:
                row_num += 1
                target = min(99, fp_w + EXIT_C)
                scalped = max_w is not None and max_w >= target
                within_3 = max_w is not None and max_w >= 97
                at_99 = max_w is not None and max_w >= 99
                pnl_scalp = EXIT_C * QTY if scalped else 0
                pnl_settle = (99 - fp_w) * QTY  # winner settles at 99
                pnl_actual = pnl_scalp if scalped else pnl_settle
                w.writerow([row_num, evt, ev[2], fp_w, target,
                            max_w, "YES" if scalped else "NO",
                            "%.0f" % (max_w - target) if max_w else "",
                            "winner", 99,
                            "YES" if within_3 else "NO",
                            "YES" if at_99 else "NO",
                            pnl_scalp, pnl_settle, pnl_actual,
                            ev[10], ev[11]])

        # Check loser side
        if fp_l and 0 < fp_l < 100:
            c = classify_cell("ATP_CHALL", fp_l)
            if c == TARGET_CELL:
                row_num += 1
                target = min(99, fp_l + EXIT_C)
                scalped = max_l is not None and max_l >= target
                within_3 = max_l is not None and max_l >= 97
                at_99 = max_l is not None and max_l >= 99
                pnl_scalp = EXIT_C * QTY if scalped else 0
                pnl_settle = -(fp_l - 1) * QTY  # loser settles at 1
                pnl_actual = pnl_scalp if scalped else pnl_settle
                w.writerow([row_num, evt, ev[3], fp_l, target,
                            max_l, "YES" if scalped else "NO",
                            "%.0f" % (max_l - target) if max_l else "",
                            "loser", 1,
                            "YES" if within_3 else "NO",
                            "YES" if at_99 else "NO",
                            pnl_scalp, pnl_settle, pnl_actual,
                            ev[10], ev[11]])

print("Rows written: %d" % row_num)

# Summary stats
scalps_winner = 0
scalps_loser = 0
scalps_winner_at99 = 0
scalps_loser_at99 = 0
total_winner = 0
total_loser = 0

with open(os.path.join(OUT_DIR, "verify_underdog_2024_at_65c.csv")) as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r["settlement_side"] == "winner":
            total_winner += 1
            if r["scalp_fired"] == "YES":
                scalps_winner += 1
                if r["max_at_99"] == "YES":
                    scalps_winner_at99 += 1
        else:
            total_loser += 1
            if r["scalp_fired"] == "YES":
                scalps_loser += 1
                if r["max_at_99"] == "YES":
                    scalps_loser_at99 += 1

print("\nSummary:")
print("  Total entries: %d (winner=%d, loser=%d)" % (total_winner+total_loser, total_winner, total_loser))
print("  Winner scalps at +65c: %d/%d (all at 99c: %d)" % (scalps_winner, total_winner, scalps_winner_at99))
print("  Loser scalps at +65c: %d/%d (all at 99c: %d)" % (scalps_loser, total_loser, scalps_loser_at99))
