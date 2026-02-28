import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# Load current trades
with open("trades.json") as f:
    current = json.load(f)

# Load archive
with open("trades_archive_feb8-21.json") as f:
    archive = json.load(f)

all_trades = archive + current
print("Total trades: {} (archive={}, current={})".format(len(all_trades), len(archive), len(current)))

def parse_ts(t):
    ts = t.get("timestamp","")
    try:
        return datetime.fromisoformat(ts.replace("Z","+00:00"))
    except:
        return None

trades_with_ts = [(t, parse_ts(t)) for t in all_trades]
trades_with_ts = [(t, dt) for t, dt in trades_with_ts if dt is not None]
trades_with_ts.sort(key=lambda x: x[1])

print("Date range: {} to {}".format(trades_with_ts[0][1].strftime("%Y-%m-%d"), trades_with_ts[-1][1].strftime("%Y-%m-%d")))
print()

now = trades_with_ts[-1][1]
week_ago = now - timedelta(days=7)
three_days_ago = now - timedelta(days=3)

week_trades = [(t, dt) for t, dt in trades_with_ts if dt >= week_ago]
three_day_trades = [(t, dt) for t, dt in trades_with_ts if dt >= three_days_ago]

for label, subset in [("LAST 3 DAYS", three_day_trades), ("LAST 7 DAYS", week_trades), ("ALL TIME", trades_with_ts)]:
    print("=" * 60)
    print(label)
    print("=" * 60)
    total = len(subset)
    statuses = Counter(t.get("status","?") for t, _ in subset)
    print("Total attempts: {}".format(total))
    print("Status breakdown:")
    for s, c in statuses.most_common():
        pct = c / total * 100 if total else 0
        print("  {}: {} ({:.1f}%)".format(s, c, pct))
    
    successes = sum(1 for t, _ in subset if t.get("status") == "SUCCESS")
    fill_rate = successes / total * 100 if total else 0
    print("Fill rate: {:.1f}%".format(fill_rate))
    
    no_fills = sum(1 for t, _ in subset if t.get("status") == "PM_NO_FILL")
    no_fill_rate = no_fills / total * 100 if total else 0
    print("No-fill rate: {:.1f}%".format(no_fill_rate))
    
    success_profits = [t.get("profit_dollars", 0) or 0 for t, _ in subset if t.get("status") == "SUCCESS"]
    total_profit = sum(success_profits)
    print("Gross profit from fills: ${:.2f}".format(total_profit))
    
    success_spreads = [t.get("spread_cents", 0) or 0 for t, _ in subset if t.get("status") == "SUCCESS"]
    avg_spread = sum(success_spreads) / len(success_spreads) if success_spreads else 0
    print("Avg spread on fills: {:.1f}c".format(avg_spread))
    
    nofill_spreads = [t.get("spread_cents", 0) or 0 for t, _ in subset if t.get("status") == "PM_NO_FILL"]
    avg_nf_spread = sum(nofill_spreads) / len(nofill_spreads) if nofill_spreads else 0
    print("Avg spread on no-fills: {:.1f}c".format(avg_nf_spread))
    
    exited = [(t, dt) for t, dt in subset if t.get("status") == "EXITED"]
    exit_losses = sum(abs(t.get("unwind_loss_cents", 0) or 0) for t, _ in exited)
    print("Exited trades: {} (unwind cost: {:.0f}c = ${:.2f})".format(len(exited), exit_losses, exit_losses/100))
    
    t3 = [(t, dt) for t, dt in subset if t.get("status") == "TIER3_OPPOSITE_HEDGE"]
    t3_losses = sum(abs(t.get("unwind_loss_cents", 0) or 0) for t, _ in t3)
    print("Tier3 hedges: {} (cost: {:.0f}c = ${:.2f})".format(len(t3), t3_losses, t3_losses/100))
    
    net = total_profit - exit_losses/100 - t3_losses/100
    print("Estimated net P&L: ${:.2f}".format(net))
    
    missed_profits = [t.get("profit_dollars", 0) or 0 for t, _ in subset if t.get("status") == "PM_NO_FILL"]
    total_missed = sum(missed_profits)
    print("Missed opportunity (no-fills): ${:.2f}".format(total_missed))
    
    print()
    print("By direction:")
    for direction in ["BUY_PM_SELL_K", "BUY_K_SELL_PM"]:
        dir_trades = [(t, dt) for t, dt in subset if t.get("direction") == direction]
        dir_total = len(dir_trades)
        dir_success = sum(1 for t, _ in dir_trades if t.get("status") == "SUCCESS")
        dir_nofill = sum(1 for t, _ in dir_trades if t.get("status") == "PM_NO_FILL")
        dir_exit = sum(1 for t, _ in dir_trades if t.get("status") == "EXITED")
        if dir_total:
            print("  {}: {} total, {} fills ({:.1f}%), {} no-fills, {} exits".format(
                direction, dir_total, dir_success, dir_success/dir_total*100, dir_nofill, dir_exit))
    
    # Daily breakdown for this window
    print()
    print("Daily breakdown:")
    daily = defaultdict(lambda: {"total": 0, "success": 0, "no_fill": 0, "exited": 0, "profit": 0.0, "loss": 0.0})
    for t, dt in subset:
        day = dt.strftime("%Y-%m-%d")
        daily[day]["total"] += 1
        s = t.get("status","")
        if s == "SUCCESS":
            daily[day]["success"] += 1
            daily[day]["profit"] += (t.get("profit_dollars", 0) or 0)
        elif s == "PM_NO_FILL":
            daily[day]["no_fill"] += 1
        elif s == "EXITED":
            daily[day]["exited"] += 1
            daily[day]["loss"] += abs(t.get("unwind_loss_cents", 0) or 0) / 100
    
    for day in sorted(daily.keys()):
        d = daily[day]
        fr = d["success"] / d["total"] * 100 if d["total"] else 0
        net_d = d["profit"] - d["loss"]
        print("  {} | {:>3} attempts | {:>2} fills ({:>5.1f}%) | {:>2} no-fills | {:>1} exits | net ${:>6.2f}".format(
            day, d["total"], d["success"], fr, d["no_fill"], d["exited"], net_d))
    print()
