import json, glob, sys
sys.path.insert(0, '/root/Omi-Workspace/arb-executor')

# Load deployed config
with open('/root/Omi-Workspace/arb-executor/config/deploy_v4.json') as f:
    config = json.load(f)

active_cells = config.get('active_cells', {})
disabled_cells = config.get('disabled_cells', [])

print("Active cell count: %d" % len(active_cells))
print("Disabled cell count: %d" % len(disabled_cells))

def cell_lookup(category, direction, entry_mid):
    bucket = int(entry_mid // 5) * 5
    cell_name = "%s_%s_%d-%d" % (category, direction, bucket, bucket + 4)
    if cell_name in disabled_cells:
        return cell_name, None
    if cell_name in active_cells:
        return cell_name, active_cells[cell_name]
    return cell_name, None

# ═══════════════════════════════════════════════════════════════
# TEST 1: Synthetic logic verification
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("TEST 1: Synthetic logic verification")
print("=" * 70)

# Scenario A: same cell at fill (no drift)
print()
print("--- Scenario A: Anchor at 42 (underdog_40-44), fill at 41 ---")
old_cell, old_cfg = cell_lookup("ATP_CHALL", "underdog", 42)
new_cell, new_cfg = cell_lookup("ATP_CHALL", "underdog", 41)
print("  Anchor cell: %s  exit_cents: %s" % (old_cell, old_cfg.get("exit_cents") if old_cfg else "N/A"))
print("  Fill cell:   %s  exit_cents: %s" % (new_cell, new_cfg.get("exit_cents") if new_cfg else "N/A"))
assert old_cell == new_cell, "FAIL: expected same cell"
print("  Result: PASS — no drift, no re-lookup needed")

# Scenario B: drift across 5c boundary, both cells active
print()
print("--- Scenario B: Anchor at 42 (underdog_40-44), fill at 38 (underdog_35-39) ---")
old_cell, old_cfg = cell_lookup("ATP_CHALL", "underdog", 42)
new_cell, new_cfg = cell_lookup("ATP_CHALL", "underdog", 38)
print("  Anchor cell: %s  exit_cents: %s" % (old_cell, old_cfg.get("exit_cents") if old_cfg else "N/A"))
print("  Fill cell:   %s  exit_cents: %s" % (new_cell, new_cfg.get("exit_cents") if new_cfg else "N/A"))
if old_cell != new_cell:
    if new_cfg is not None:
        print("  Result: PASS — cell_reclassified would fire")
        print("    old_exit_cents=%s -> new_exit_cents=%s" % (
            old_cfg.get("exit_cents") if old_cfg else "N/A",
            new_cfg.get("exit_cents")))
    else:
        print("  Result: cell_drift_to_inactive would fire (new cell not active)")
else:
    print("  Result: no drift (unexpected)")

# Scenario C: drift to inactive cell
print()
print("--- Scenario C: Find active->inactive drift example in current config ---")
found_inactive = False
for cell_name, cfg in sorted(active_cells.items()):
    parts = cell_name.split("_")
    if len(parts) < 4:
        continue
    cat = "_".join(parts[:2])
    direction = parts[2]
    band = parts[3]
    lo = int(band.split("-")[0])
    # Try the band below
    test_price = lo - 1
    if test_price < 0:
        continue
    neighbor_cell, neighbor_cfg = cell_lookup(cat, direction, test_price)
    if neighbor_cfg is None and neighbor_cell != cell_name:
        print("  Active: %s (exit_cents=%s)" % (cell_name, cfg.get("exit_cents")))
        print("  If fill drifts to price=%d -> cell=%s (NOT in active set)" % (test_price, neighbor_cell))
        print("  Result: PASS — cell_drift_to_inactive would fire, default exit_cents=15")
        found_inactive = True
        break
if not found_inactive:
    print("  No active->inactive boundary found in current config")

# Scenario D: drift across leader/underdog boundary
print()
print("--- Scenario D: Anchor at 52 (leader_50-54), fill at 48 (underdog_45-49) ---")
old_cell, old_cfg = cell_lookup("ATP_CHALL", "leader", 52)
new_cell, new_cfg = cell_lookup("ATP_CHALL", "leader", 48)
print("  Anchor cell: %s  cfg: %s" % (old_cell, old_cfg.get("exit_cents") if old_cfg else "N/A"))
# Note: cell_lookup uses the SAME direction param, so leader stays leader even at 48
# The direction is passed from pos.direction, not derived from price
# This is correct — the bot bought the leader side, the price just moved
new_cell2, new_cfg2 = cell_lookup("ATP_CHALL", "leader", 48)
print("  Fill cell (direction=leader): %s  cfg: %s" % (new_cell2, new_cfg2.get("exit_cents") if new_cfg2 else "N/A"))
print("  Note: direction is preserved from routing — leader side stays leader")

# ═══════════════════════════════════════════════════════════════
# TEST 2: Historical replay across all fills
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("TEST 2: Historical replay — all entry_filled events from JSONL logs")
print("=" * 70)

no_drift = 0
reclassified = 0
drift_to_inactive = 0
drift_examples = []
exit_cents_changes = []

for path in sorted(glob.glob("logs/live_v3_*.jsonl")):
    with open(path) as f:
        for line in f:
            try:
                ev = json.loads(line)
            except:
                continue
            if ev.get("event") != "entry_filled":
                continue
            details = ev.get("details", ev)
            ticker = ev.get("ticker", "")
            fill_price = details.get("fill_price")
            posted_price = details.get("posted_price")
            cell = details.get("cell")
            direction = details.get("direction")
            if not all([ticker, fill_price is not None, cell, direction]):
                continue

            # Extract category from cell name
            parts = cell.split("_")
            if len(parts) < 4:
                continue
            category = "_".join(parts[:2])

            new_cell, new_cfg = cell_lookup(category, direction, fill_price)

            if new_cell == cell:
                no_drift += 1
            elif new_cfg is not None:
                reclassified += 1
                old_cfg_lookup = active_cells.get(cell, {})
                old_ec = old_cfg_lookup.get("exit_cents", "?")
                new_ec = new_cfg.get("exit_cents", "?")
                drift_examples.append({
                    "ticker": ticker[-35:], "old_cell": cell, "new_cell": new_cell,
                    "posted": posted_price, "fill": fill_price,
                    "old_exit_cents": old_ec, "new_exit_cents": new_ec,
                    "type": "reclassified",
                })
                if old_ec != new_ec:
                    exit_cents_changes.append((cell, new_cell, old_ec, new_ec, posted_price, fill_price))
            else:
                drift_to_inactive += 1
                old_cfg_lookup = active_cells.get(cell, {})
                old_ec = old_cfg_lookup.get("exit_cents", "?")
                drift_examples.append({
                    "ticker": ticker[-35:], "old_cell": cell, "new_cell": new_cell,
                    "posted": posted_price, "fill": fill_price,
                    "old_exit_cents": old_ec, "new_exit_cents": 15,
                    "type": "drift_to_inactive",
                })

total = no_drift + reclassified + drift_to_inactive
print()
print("Total entry_filled events: %d" % total)
print()
print("Cell drift breakdown:")
print("  No drift (fill in same cell):            %d (%5.1f%%)" % (no_drift, no_drift/total*100 if total else 0))
print("  Reclassified (different active cell):     %d (%5.1f%%)" % (reclassified, reclassified/total*100 if total else 0))
print("  Drift to inactive cell:                  %d (%5.1f%%)" % (drift_to_inactive, drift_to_inactive/total*100 if total else 0))

if drift_examples:
    print()
    print("All drift examples:")
    for ex in drift_examples:
        print("  [%-18s] %-35s posted=%s fill=%s" % (
            ex["type"], ex["ticker"], ex["posted"], ex["fill"]))
        print("    %s (exit=%s) -> %s (exit=%s)" % (
            ex["old_cell"], ex["old_exit_cents"], ex["new_cell"], ex["new_exit_cents"]))

if exit_cents_changes:
    print()
    print("Cases where exit_cents would have changed:")
    for old_c, new_c, old_ec, new_ec, posted, fill in exit_cents_changes:
        print("  %s (%sc) -> %s (%sc)  posted=%s fill=%s  delta=%sc" % (
            old_c, old_ec, new_c, new_ec, posted, fill, int(fill) - int(posted) if posted else "?"))
