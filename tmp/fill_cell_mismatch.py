#!/usr/bin/env python3
"""
For each of 130 live fills: bot_cell (FV-derived) vs fill_price_cell (price-derived).
Plus exit target analysis.
"""
import json, csv, os, glob

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"

with open(os.path.join(BASE_DIR, "config/deploy_v4.json")) as f:
    cfg = json.load(f)
active_cells = cfg.get("active_cells", {})

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

# Load fills and exit_posted events
fills = []
exit_posts = {}  # ticker -> exit details

for lf in sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl"))):
    with open(lf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except: continue
            ev = d.get("event","")
            det = d.get("details",{})
            tk = d.get("ticker","")

            if ev == "entry_filled":
                fills.append({
                    "ticker": tk,
                    "fill_price": det.get("fill_price", 0),
                    "posted_price": det.get("posted_price", 0),
                    "bot_cell": det.get("cell", ""),
                    "direction": det.get("direction", ""),
                    "play_type": det.get("play_type", ""),
                    "ts": d.get("ts", ""),
                })
            elif ev == "exit_posted":
                if tk not in exit_posts:  # take first exit_posted per ticker
                    exit_posts[tk] = {
                        "exit_price": det.get("exit_price", 0),
                        "based_on_fill": det.get("based_on_fill", 0),
                        "play_type": det.get("play_type", ""),
                    }

print("Fills: %d, Exit posts: %d" % (len(fills), len(exit_posts)))

# For each fill, compute cell by fill_price and compare
with open(os.path.join(OUT_DIR, "fill_cell_mismatch.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","fill_price","posted_price","bot_cell_fv_derived",
                "fill_price_cell","mismatch","direction_flip",
                "exit_target_absolute","exit_based_on_fill_price",
                "exit_cents_used","cell_exit_cents_config",
                "exit_matches_fill","play_type","ts"])

    mismatch_count = 0
    dir_flip_count = 0
    exit_mismatch_count = 0

    for fl in fills:
        tk = fl["ticker"]
        fp = fl["fill_price"]
        tier = get_tier(tk)
        if not tier: continue

        bot_cell = fl["bot_cell"]
        fill_cell = classify_cell(tier, fp)

        mismatch = bot_cell != fill_cell
        if mismatch: mismatch_count += 1

        # Direction flip?
        bot_dir = "leader" if "leader" in bot_cell else "underdog"
        fill_dir = "leader" if "leader" in fill_cell else "underdog"
        dir_flip = bot_dir != fill_dir
        if dir_flip: dir_flip_count += 1

        # Exit target analysis
        ep = exit_posts.get(tk)
        exit_target = ep["exit_price"] if ep else ""
        exit_based_on = ep["based_on_fill"] if ep else ""

        # What exit_cents does the bot's cell config specify?
        cell_cfg = active_cells.get(bot_cell, {})
        cell_exit_cents = cell_cfg.get("exit_cents", "")

        # Does exit = fill_price + exit_cents?
        if ep and cell_exit_cents:
            expected_exit = min(fp + cell_exit_cents, 98)
            exit_matches = exit_target == expected_exit
            actual_exit_cents = exit_target - fp if exit_target else ""
        else:
            exit_matches = ""
            actual_exit_cents = ""

        if exit_matches == False:
            exit_mismatch_count += 1

        w.writerow([tk, fp, fl["posted_price"], bot_cell, fill_cell,
                     "YES" if mismatch else "NO",
                     "YES" if dir_flip else "NO",
                     exit_target, exit_based_on,
                     actual_exit_cents, cell_exit_cents,
                     "YES" if exit_matches == True else ("NO" if exit_matches == False else ""),
                     fl["play_type"], fl["ts"]])

print("\n=== RESULTS ===")
print("Total fills: %d" % len(fills))
print("Cell mismatches (bot_cell != fill_price_cell): %d (%.0f%%)" % (
    mismatch_count, mismatch_count/len(fills)*100))
print("Direction flips (leader<->underdog): %d (%.0f%%)" % (
    dir_flip_count, dir_flip_count/len(fills)*100))
print("Exit target != fill_price + exit_cents: %d" % exit_mismatch_count)

# Show mismatches
if mismatch_count > 0:
    print("\n=== MISMATCHES ===")
    for fl in fills:
        tk = fl["ticker"]
        fp = fl["fill_price"]
        tier = get_tier(tk)
        if not tier: continue
        bot_cell = fl["bot_cell"]
        fill_cell = classify_cell(tier, fp)
        if bot_cell != fill_cell:
            ep = exit_posts.get(tk)
            exit_t = ep["exit_price"] if ep else "?"
            print("  %s fill=%dc bot_cell=%s fill_cell=%s exit=%s" % (
                tk[-25:], fp, bot_cell, fill_cell, exit_t))
