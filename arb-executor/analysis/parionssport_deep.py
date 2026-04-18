#!/usr/bin/env python3
"""
Deep verification of parionssport_fr predictive signal on Kalshi tennis.
Zero new API calls — all from cached data.
"""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ANALYSIS = "/root/Omi-Workspace/arb-executor/analysis"
CACHE_PATH = os.path.join(ANALYSIS, "pinnacle_cache.json")
FACTS_PATH = os.path.join(ANALYSIS, "match_facts.csv")
TICKS_DIR = os.path.join(ANALYSIS, "match_ticks_full")
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v3.json"

config = json.load(open(CONFIG_PATH))

# Load cache
with open(CACHE_PATH) as f:
    raw = json.load(f)
cache = {}
for k, v in raw.items():
    cache[tuple(k.split("|"))] = v

# Load facts
facts = {}
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        if r["category"] in ("ATP_MAIN", "WTA_MAIN"):
            facts[r["ticker_id"]] = r

def remove_vig(odds1, odds2):
    p1 = 1.0 / odds1
    p2 = 1.0 / odds2
    total = p1 + p2
    return p1 / total, p2 / total

def name_matches_code(full_name, code):
    for word in full_name.upper().split():
        if word.startswith(code.upper()):
            return True
    return False

def load_ticks(ticker):
    path = os.path.join(TICKS_DIR, "%s.csv" % ticker)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                rows.append((int(row[0]), int(row[1]), int(row[2]), float(row[3])))
    return rows

def percentiles(vals):
    if not vals:
        return 0, 0, 0
    s = sorted(vals)
    n = len(s)
    return s[int(n*0.25)], s[int(n*0.5)], s[int(n*0.75)]

def ci95(successes, n):
    """Wilson score 95% CI."""
    if n == 0:
        return 0, 0, 0
    p = successes / n
    z = 1.96
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    margin = z * math.sqrt((p*(1-p) + z*z/(4*n)) / n) / denom
    return 100*p, 100*max(0, center - margin), 100*min(1, center + margin)

TOP_BOOKS = ["parionssport_fr", "marathonbet", "gtbets", "coolbet", "williamhill"]

def extract_book_signals(book_key):
    """For each fact ticker, find the book's implied prob from the OPEN snapshot."""
    signals = []
    for tk, f in facts.items():
        player_code = tk.split("-")[-1]
        parts = tk.split("-")
        date_part = parts[1][:7]
        try:
            yr = 2000 + int(date_part[:2])
            mon = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
                   "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}[date_part[2:5]]
            day = int(date_part[5:7])
            dt_early = "%04d-%02d-%02dT06:00:00Z" % (yr, mon, day)
            dt_late = "%04d-%02d-%02dT20:00:00Z" % (yr, mon, day)
        except:
            continue

        cat = f["category"]
        sport_keys = ["tennis_atp_miami_open", "tennis_atp_monte_carlo_masters",
                      "tennis_atp_barcelona_open", "tennis_atp_munich",
                      "tennis_atp_indian_wells", "tennis_atp_dubai"] if cat == "ATP_MAIN" else \
                     ["tennis_wta_miami_open", "tennis_wta_charleston_open",
                      "tennis_wta_indian_wells", "tennis_wta_dubai", "tennis_wta_stuttgart_open"]

        book_open = None
        book_close = None
        book_snapshot_ts = None  # timestamp label of the snapshot

        for sk in sport_keys:
            for label, ts_str in [("open", dt_early), ("close", dt_late)]:
                matches = cache.get((ts_str, sk), [])
                for m in matches:
                    for book in m.get("bookmakers", []):
                        if book["key"] != book_key:
                            continue
                        outcomes = book.get("markets", [{}])[0].get("outcomes", [])
                        if len(outcomes) < 2:
                            continue
                        for o in outcomes:
                            if name_matches_code(o["name"], player_code):
                                other = [x for x in outcomes if x != o]
                                if other:
                                    p_fair, _ = remove_vig(o["price"], other[0]["price"])
                                    implied = round(p_fair * 100, 1)
                                    if label == "open":
                                        book_open = implied
                                        book_snapshot_ts = ts_str
                                    else:
                                        book_close = implied
                                break
            if book_open is not None:
                break

        if book_open is None:
            continue

        # Load Kalshi ticks
        ticks = load_ticks(tk)
        if not ticks:
            continue

        kalshi_open_mid = ticks[0][3]
        kalshi_open_bid = ticks[0][1]
        kalshi_open_ask = ticks[0][2]
        kalshi_close_mid = float(f["entry_mid"])
        spread = kalshi_open_ask - kalshi_open_bid
        pregame_ts = int(f["pregame_close_ts"])

        signals.append({
            "ticker": tk,
            "category": cat,
            "side": f["side"],
            "book_open": book_open,
            "book_close": book_close if book_close else book_open,
            "book_snapshot_ts": book_snapshot_ts,
            "kalshi_open_mid": kalshi_open_mid,
            "kalshi_open_bid": kalshi_open_bid,
            "kalshi_open_ask": kalshi_open_ask,
            "kalshi_close_mid": kalshi_close_mid,
            "spread": spread,
            "max_bounce": float(f["max_bounce_from_entry"]),
            "result": f["match_result"],
            "pregame_ts": pregame_ts,
        })

    return signals

# ============================================================
print("=" * 80)
print("STEP 1: TIMING VALIDATION")
print("=" * 80)
print()
print("CRITICAL LIMITATION: Our cached Odds API snapshots are at fixed")
print("timestamps (06:00 UTC = 2:00 AM ET and 20:00 UTC = 4:00 PM ET).")
print("These are Odds API historical snapshot times, NOT the time each")
print("book published its odds. The API returns what odds were live at")
print("the requested timestamp — not when the book first posted them.")
print()
print("Therefore: we CANNOT determine whether parionssport LEADS or")
print("LAGS Kalshi in time. Both snapshots are at the same fixed times.")
print("The historical API does not provide per-book posting timestamps.")
print()
print("CONCLUSION: Step 1 is INDETERMINATE. We cannot prove temporal")
print("precedence from this data. Proceeding with remaining steps")
print("under the assumption that the signal may or may not lead.")
print()

# ============================================================
print("=" * 80)
print("STEP 2: GAP BUCKET ANALYSIS (all 5 books)")
print("=" * 80)

def analyze_book(book_key, signals):
    """Run gap bucket analysis for one book."""
    buckets = {"<2c": [], "2-5c": [], "5-10c": [], ">10c": []}
    for s in signals:
        gap = s["book_open"] - s["kalshi_open_mid"]  # signed
        abs_gap = abs(gap)
        convergence = s["kalshi_close_mid"] - s["kalshi_open_mid"]
        # Did Kalshi converge toward book?
        converged = (gap > 0 and convergence > 0) or (gap < 0 and convergence < 0)
        frac = convergence / gap if abs(gap) > 0.1 else 0

        entry = {
            "gap": gap, "abs_gap": abs_gap, "convergence": convergence,
            "converged": converged, "frac_closed": frac,
            "spread": s["spread"],
            "maker_pnl": s["kalshi_close_mid"] - s["kalshi_open_bid"],
            "taker_pnl": s["kalshi_close_mid"] - s["kalshi_open_ask"],
        }
        if abs_gap < 2: buckets["<2c"].append(entry)
        elif abs_gap < 5: buckets["2-5c"].append(entry)
        elif abs_gap < 10: buckets["5-10c"].append(entry)
        else: buckets[">10c"].append(entry)

    return buckets

for bk in TOP_BOOKS:
    signals = extract_book_signals(bk)
    if not signals:
        continue
    buckets = analyze_book(bk, signals)

    print("\n--- %s (N=%d) ---" % (bk, len(signals)))
    print("%-6s %4s %8s %10s %10s %8s %10s %10s" % (
        "GAP", "N", "CONV%", "MEAN_CONV", "FRAC_CLS", "SPREAD", "MAKER_PL", "TAKER_PL"))

    for bname in ["<2c", "2-5c", "5-10c", ">10c"]:
        entries = buckets[bname]
        n = len(entries)
        if n == 0:
            print("%-6s %4d" % (bname, 0))
            continue
        conv_pct = 100 * sum(1 for e in entries if e["converged"]) / n
        mean_conv = sum(e["convergence"] for e in entries) / n
        mean_frac = sum(e["frac_closed"] for e in entries) / n
        mean_spread = sum(e["spread"] for e in entries) / n
        mean_maker = sum(e["maker_pnl"] for e in entries) / n
        mean_taker = sum(e["taker_pnl"] for e in entries) / n
        print("%-6s %4d %7.0f%% %+9.1fc %9.1f%% %7.1fc %+9.1fc %+9.1fc" % (
            bname, n, conv_pct, mean_conv, 100*mean_frac, mean_spread, mean_maker, mean_taker))

# ============================================================
print("\n" + "=" * 80)
print("STEP 3: EXECUTION COST ANALYSIS (parionssport only)")
print("=" * 80)

ps_signals = extract_book_signals("parionssport_fr")
ps_buckets = analyze_book("parionssport_fr", ps_signals)

print("\n--- Net edge analysis (parionssport_fr) ---")
net_buckets = {"net<2c": [], "net2-5c": [], "net5-10c": [], "net>10c": []}
for s in ps_signals:
    gap = abs(s["book_open"] - s["kalshi_open_mid"])
    net = gap - s["spread"]
    convergence = s["kalshi_close_mid"] - s["kalshi_open_mid"]
    gap_signed = s["book_open"] - s["kalshi_open_mid"]
    converged = (gap_signed > 0 and convergence > 0) or (gap_signed < 0 and convergence < 0)
    entry = {"net": net, "converged": converged, "convergence": convergence,
             "maker_pnl": s["kalshi_close_mid"] - s["kalshi_open_bid"],
             "taker_pnl": s["kalshi_close_mid"] - s["kalshi_open_ask"]}
    if net < 2: net_buckets["net<2c"].append(entry)
    elif net < 5: net_buckets["net2-5c"].append(entry)
    elif net < 10: net_buckets["net5-10c"].append(entry)
    else: net_buckets["net>10c"].append(entry)

print("%-9s %4s %8s %10s %10s" % ("NET_EDGE", "N", "CONV%", "MAKER_PL", "TAKER_PL"))
for bname in ["net<2c", "net2-5c", "net5-10c", "net>10c"]:
    entries = net_buckets[bname]
    n = len(entries)
    if n == 0:
        print("%-9s %4d" % (bname, 0))
        continue
    conv_pct = 100 * sum(1 for e in entries if e["converged"]) / n
    mean_maker = sum(e["maker_pnl"] for e in entries) / n
    mean_taker = sum(e["taker_pnl"] for e in entries) / n
    print("%-9s %4d %7.0f%% %+9.1fc %+9.1fc" % (bname, n, conv_pct, mean_maker, mean_taker))

# ============================================================
print("\n" + "=" * 80)
print("STEP 5: CONSENSUS SIGNAL (parionssport + marathonbet + coolbet)")
print("=" * 80)

# Build per-ticker consensus
ps = {s["ticker"]: s for s in extract_book_signals("parionssport_fr")}
mb = {s["ticker"]: s for s in extract_book_signals("marathonbet")}
cb = {s["ticker"]: s for s in extract_book_signals("coolbet")}

consensus = []
for tk in ps:
    if tk in mb and tk in cb:
        avg_implied = (ps[tk]["book_open"] + mb[tk]["book_open"] + cb[tk]["book_open"]) / 3
        s = ps[tk].copy()
        s["book_open"] = avg_implied
        consensus.append(s)

print("Consensus matches (3-book overlap): %d" % len(consensus))
if consensus:
    cons_buckets = analyze_book("consensus", consensus)
    print("%-6s %4s %8s %10s %10s %8s %10s %10s" % (
        "GAP", "N", "CONV%", "MEAN_CONV", "FRAC_CLS", "SPREAD", "MAKER_PL", "TAKER_PL"))
    for bname in ["<2c", "2-5c", "5-10c", ">10c"]:
        entries = cons_buckets[bname]
        n = len(entries)
        if n == 0:
            print("%-6s %4d" % (bname, 0))
            continue
        conv_pct = 100 * sum(1 for e in entries if e["converged"]) / n
        mean_conv = sum(e["convergence"] for e in entries) / n
        mean_frac = sum(e["frac_closed"] for e in entries) / n
        mean_spread = sum(e["spread"] for e in entries) / n
        mean_maker = sum(e["maker_pnl"] for e in entries) / n
        mean_taker = sum(e["taker_pnl"] for e in entries) / n
        print("%-6s %4d %7.0f%% %+9.1fc %9.1f%% %7.1fc %+9.1fc %+9.1fc" % (
            bname, n, conv_pct, mean_conv, 100*mean_frac, mean_spread, mean_maker, mean_taker))

# ============================================================
print("\n" + "=" * 80)
print("STEP 6: DIRECTION FLIPS - PARIONSSPORT VIEW")
print("=" * 80)

flip_tickers = [
    "KXATPMATCH-26MAR18CAZBAR-CAZ",
    "KXATPMATCH-26MAR18CAZBAR-BAR",
    "KXWTAMATCH-26MAR20OSTYAS-OST",
    "KXWTAMATCH-26MAR20OSTYAS-YAS",
    "KXATPMATCH-26MAR18WALBAE-BAE",
    "KXATPMATCH-26MAR18WALBAE-WAL",
]
for tk in flip_tickers:
    ps_sig = ps.get(tk)
    mb_sig = mb.get(tk)
    f = facts.get(tk, {})
    player = tk.split("-")[-1]
    kalshi_mid = float(f.get("entry_mid", 0))
    result = f.get("match_result", "?")

    print("  %s (%s)" % (tk[:45], player))
    print("    Kalshi mid: %.0fc  Result: %s" % (kalshi_mid, result))
    if ps_sig:
        print("    Parionssport: %.1fc" % ps_sig["book_open"])
    else:
        print("    Parionssport: NO DATA")
    if mb_sig:
        print("    Marathonbet:  %.1fc" % mb_sig["book_open"])
    else:
        print("    Marathonbet:  NO DATA")
    # Pinnacle from prior results
    pin_sig = None
    for bk_key in ["pinnacle"]:
        s = extract_book_signals(bk_key)
        for sig in s:
            if sig["ticker"] == tk:
                pin_sig = sig
                break
    if pin_sig:
        print("    Pinnacle:     %.1fc" % pin_sig["book_open"])
    print()

# ============================================================
print("=" * 80)
print("STEP 7: STATISTICAL SIGNIFICANCE")
print("=" * 80)

print("\n--- Convergence rates with 95% CIs ---")
for bk in TOP_BOOKS:
    signals = extract_book_signals(bk)
    if not signals:
        continue
    buckets = analyze_book(bk, signals)
    print("\n%s (N=%d):" % (bk, len(signals)))
    for bname in ["<2c", "2-5c", "5-10c", ">10c"]:
        entries = buckets[bname]
        n = len(entries)
        if n == 0:
            continue
        successes = sum(1 for e in entries if e["converged"])
        pct, lo, hi = ci95(successes, n)
        sig = "***" if lo > 50 else ("ns" if hi < 50 or lo < 50 else "?")
        print("  %-6s N=%3d  conv=%.0f%%  95%%CI=[%.0f%%, %.0f%%]  %s" % (
            bname, n, pct, lo, hi, sig))

print("\n--- Overall significance test ---")
for bk in TOP_BOOKS:
    signals = extract_book_signals(bk)
    if not signals:
        continue
    total_conv = sum(1 for s in signals
                     if ((s["book_open"] - s["kalshi_open_mid"]) > 0 and
                         (s["kalshi_close_mid"] - s["kalshi_open_mid"]) > 0) or
                        ((s["book_open"] - s["kalshi_open_mid"]) < 0 and
                         (s["kalshi_close_mid"] - s["kalshi_open_mid"]) < 0))
    pct, lo, hi = ci95(total_conv, len(signals))
    sig = "SIG" if lo > 50 else "NOT SIG"
    print("  %-20s  conv=%d/%d=%.0f%%  95%%CI=[%.0f%%, %.0f%%]  %s" % (
        bk, total_conv, len(signals), pct, lo, hi, sig))

# Sample raw data
print("\n" + "=" * 80)
print("SAMPLE: 10 parionssport raw signals")
print("=" * 80)
ps_signals.sort(key=lambda x: -abs(x["book_open"] - x["kalshi_open_mid"]))
print("%-40s %6s %6s %6s %6s %6s %s" % (
    "TICKER", "PS_IMP", "K_OPEN", "K_CLOSE", "GAP", "CONV", "RESULT"))
for s in ps_signals[:10]:
    gap = s["book_open"] - s["kalshi_open_mid"]
    conv = s["kalshi_close_mid"] - s["kalshi_open_mid"]
    print("%-40s %5.1fc %5.1fc %5.1fc %+5.1fc %+5.1fc %s" % (
        s["ticker"][:40], s["book_open"], s["kalshi_open_mid"],
        s["kalshi_close_mid"], gap, conv, s["result"]))

print("\nDONE")
