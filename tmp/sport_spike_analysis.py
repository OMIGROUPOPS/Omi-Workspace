#!/usr/bin/env python3
"""Sport-specific spike analysis from 214 reclassified trades (Mar 11-15).
Break down by sport: spike WR, spike losses, loss patterns.
Output sport-specific spike gate recommendations.
"""
import csv
from collections import defaultdict

CSV = "/tmp/v3_enriched_trades.csv"

with open(CSV) as f:
    reader = csv.DictReader(f)
    trades = list(reader)

print(f"Loaded {len(trades)} trades from {CSV}")
print()

# ─── Recover first_seen_price and classify ───
for t in trades:
    entry = int(float(t.get("entry_price", 0) or 0))
    pnl = int(float(t.get("pnl_cents", 0) or 0))
    sport = t.get("sport", "unknown")

    # Recover first_seen from pre10m or default
    pre10m = t.get("pre_entry_price_10m", "") or ""
    if pre10m and pre10m not in ("", "nan", "None"):
        try:
            fsp = int(float(pre10m))
        except (ValueError, TypeError):
            fsp = 50
    else:
        # Sport-specific defaults
        fsp = 50

    spike = entry - fsp
    is_maker = entry >= 88

    t["_fsp"] = fsp
    t["_spike"] = spike
    t["_is_maker"] = is_maker
    t["_cls"] = "SPIKE" if spike > 2 else ("DIP" if spike < -2 else "FLAT")
    t["_entry"] = entry
    t["_pnl"] = pnl
    t["_sport"] = sport
    # W/L: use pnl
    if pnl > 0:
        t["_wl"] = "W"
    elif pnl < 0:
        t["_wl"] = "L"
    else:
        t["_wl"] = "P"  # pending/breakeven

# ─── SECTION 1: Sport breakdown ───
print("=" * 80)
print("SECTION 1: SPORT-LEVEL SPIKE BREAKDOWN")
print("=" * 80)

sports = sorted(set(t["_sport"] for t in trades))
for sport in sports:
    st = [t for t in trades if t["_sport"] == sport]
    spikes = [t for t in st if t["_cls"] == "SPIKE"]
    spike_w = [t for t in spikes if t["_wl"] == "W"]
    spike_l = [t for t in spikes if t["_wl"] == "L"]
    spike_p = [t for t in spikes if t["_wl"] == "P"]
    spike_pnl = sum(t["_pnl"] for t in spikes)

    settled = [t for t in spikes if t["_wl"] in ("W", "L")]
    wr = len(spike_w) / len(settled) * 100 if settled else 0

    print(f"\n  {sport.upper()}")
    print(f"    Total trades: {len(st)}")
    print(f"    Spikes: {len(spikes)} ({len(spikes)/len(st)*100:.0f}%)")
    print(f"    Spike WR: {wr:.1f}% ({len(spike_w)}W / {len(spike_l)}L / {len(spike_p)}P)")
    print(f"    Spike PnL: {spike_pnl:+d}c (${spike_pnl/100:.2f})")
    print(f"    Spike $/day: ${spike_pnl/100/5:.2f}")

    if spike_l:
        print(f"    LOSSES:")
        for t in spike_l:
            side = t.get("ticker", "?").rsplit("-", 1)[-1] if "ticker" in t else t.get("side", "?")
            print(f"      {side}: entry={t['_entry']}c fsp={t['_fsp']}c spike={t['_spike']:+d}c "
                  f"maker={'YES' if t['_is_maker'] else 'no'} pnl={t['_pnl']:+d}c")

# ─── SECTION 2: STB vs Maker by sport ───
print()
print("=" * 80)
print("SECTION 2: STB vs MAKER BY SPORT")
print("=" * 80)

for sport in sports:
    st = [t for t in trades if t["_sport"] == sport]
    stb = [t for t in st if not t["_is_maker"]]
    maker = [t for t in st if t["_is_maker"]]

    stb_spikes = [t for t in stb if t["_cls"] == "SPIKE"]
    maker_spikes = [t for t in maker if t["_cls"] == "SPIKE"]

    stb_spike_l = [t for t in stb_spikes if t["_wl"] == "L"]
    maker_spike_l = [t for t in maker_spikes if t["_wl"] == "L"]

    stb_pnl = sum(t["_pnl"] for t in stb_spikes)
    maker_pnl = sum(t["_pnl"] for t in maker_spikes)

    stb_settled = [t for t in stb_spikes if t["_wl"] in ("W", "L")]
    maker_settled = [t for t in maker_spikes if t["_wl"] in ("W", "L")]

    stb_wr = len([t for t in stb_settled if t["_wl"] == "W"]) / len(stb_settled) * 100 if stb_settled else 0
    maker_wr = len([t for t in maker_settled if t["_wl"] == "W"]) / len(maker_settled) * 100 if maker_settled else 0

    print(f"\n  {sport.upper()}")
    print(f"    STB spikes:   {len(stb_spikes):>3d} trades | WR={stb_wr:.0f}% | "
          f"losses={len(stb_spike_l)} | PnL={stb_pnl:+d}c (${stb_pnl/100:.2f})")
    print(f"    Maker spikes: {len(maker_spikes):>3d} trades | WR={maker_wr:.0f}% | "
          f"losses={len(maker_spike_l)} | PnL={maker_pnl:+d}c (${maker_pnl/100:.2f})")

    if stb_spike_l:
        print(f"    STB SPIKE LOSSES:")
        for t in stb_spike_l:
            side = t.get("ticker", "?").rsplit("-", 1)[-1] if "ticker" in t else t.get("side", "?")
            print(f"      {side}: entry={t['_entry']}c spike={t['_spike']:+d}c pnl={t['_pnl']:+d}c")
    if maker_spike_l:
        print(f"    MAKER SPIKE LOSSES:")
        for t in maker_spike_l:
            side = t.get("ticker", "?").rsplit("-", 1)[-1] if "ticker" in t else t.get("side", "?")
            print(f"      {side}: entry={t['_entry']}c spike={t['_spike']:+d}c pnl={t['_pnl']:+d}c")

# ─── SECTION 3: Loss deep-dive ───
print()
print("=" * 80)
print("SECTION 3: ALL LOSSES — SPIKE PROFILE")
print("=" * 80)

all_losses = [t for t in trades if t["_wl"] == "L"]
print(f"\n  Total losses: {len(all_losses)}")

for t in all_losses:
    side = t.get("ticker", "?").rsplit("-", 1)[-1] if "ticker" in t else t.get("side", "?")
    print(f"    {t['_sport']:<8s} {side:<6s} entry={t['_entry']}c fsp={t['_fsp']}c "
          f"spike={t['_spike']:+d}c cls={t['_cls']:<5s} maker={'YES' if t['_is_maker'] else 'no '} "
          f"pnl={t['_pnl']:+d}c")

# ─── SECTION 4: Spike magnitude by sport ───
print()
print("=" * 80)
print("SECTION 4: SPIKE MAGNITUDE DISTRIBUTION BY SPORT")
print("=" * 80)

buckets = [
    ("0-5c", 0, 5),
    ("6-10c", 6, 10),
    ("11-20c", 11, 20),
    ("21-30c", 21, 30),
    ("31+c", 31, 999),
]

for sport in sports:
    spikes = [t for t in trades if t["_sport"] == sport and t["_cls"] == "SPIKE"]
    if not spikes:
        continue
    print(f"\n  {sport.upper()}")
    for bname, lo, hi in buckets:
        b = [t for t in spikes if lo <= t["_spike"] <= hi]
        if not b:
            continue
        bpnl = sum(t["_pnl"] for t in b)
        bl = len([t for t in b if t["_wl"] == "L"])
        bw = len([t for t in b if t["_wl"] == "W"])
        bp = len([t for t in b if t["_wl"] == "P"])
        print(f"    spike {bname:>6s}: {len(b):>3d} trades | {bw}W {bl}L {bp}P | "
              f"PnL={bpnl:+d}c (${bpnl/100:.2f})")

# ─── SECTION 5: Navone and Yuzuki investigation ───
print()
print("=" * 80)
print("SECTION 5: NAVONE + YUZUKI INVESTIGATION")
print("=" * 80)

for name_search in ["NAV", "YUZ"]:
    matches = [t for t in trades if name_search in t.get("ticker", "") or
               name_search in t.get("side", "")]
    print(f"\n  {name_search} trades ({len(matches)}):")
    for t in matches:
        side = t.get("ticker", "?").rsplit("-", 1)[-1] if "ticker" in t else t.get("side", "?")
        print(f"    {side}: entry={t['_entry']}c fsp={t['_fsp']}c spike={t['_spike']:+d}c "
              f"cls={t['_cls']} maker={'YES' if t['_is_maker'] else 'no'} "
              f"pnl={t['_pnl']:+d}c wl={t['_wl']}")

# ─── SECTION 6: Recommendations ───
print()
print("=" * 80)
print("SECTION 6: SPORT-SPECIFIC SPIKE GATE RECOMMENDATIONS")
print("=" * 80)

print("""
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ ANALYSIS FRAMEWORK                                                         │
  │                                                                             │
  │ For each sport × entry_type (STB vs Maker):                                │
  │   - How many spike losses?                                                  │
  │   - What spike magnitude were the losses?                                   │
  │   - Would a gate at spike>X have blocked them?                              │
  │   - How many winners would that same gate block?                            │
  │   - Net impact: savings from blocked losses - cost of blocked winners       │
  └─────────────────────────────────────────────────────────────────────────────┘
""")

for sport in sports:
    st = [t for t in trades if t["_sport"] == sport]
    stb = [t for t in st if not t["_is_maker"]]
    maker = [t for t in st if t["_is_maker"]]

    stb_spikes = [t for t in stb if t["_cls"] == "SPIKE"]
    maker_spikes = [t for t in maker if t["_cls"] == "SPIKE"]

    stb_spike_losses = [t for t in stb_spikes if t["_wl"] == "L"]
    maker_spike_losses = [t for t in maker_spikes if t["_wl"] == "L"]

    print(f"\n  {'='*60}")
    print(f"  {sport.upper()}")
    print(f"  {'='*60}")

    # Maker analysis
    if maker_spike_losses:
        loss_spikes = [t["_spike"] for t in maker_spike_losses]
        min_spike = min(loss_spikes)
        max_spike = max(loss_spikes)
        total_loss = sum(t["_pnl"] for t in maker_spike_losses)

        # Simulate gate at various thresholds
        for threshold in [5, 10, 15, 20]:
            blocked_l = [t for t in maker_spike_losses if t["_spike"] > threshold]
            blocked_w = [t for t in maker_spikes if t["_spike"] > threshold and t["_wl"] == "W"]
            blocked_p = [t for t in maker_spikes if t["_spike"] > threshold and t["_wl"] == "P"]
            saved = abs(sum(t["_pnl"] for t in blocked_l))
            lost = sum(t["_pnl"] for t in blocked_w) + sum(t["_pnl"] for t in blocked_p)
            net = saved - lost
            print(f"    MAKER gate spike>{threshold}c: block {len(blocked_l)}L + "
                  f"{len(blocked_w)}W + {len(blocked_p)}P | "
                  f"save {saved}c - lose {lost}c = net {net:+d}c")

        print(f"    MAKER losses: {len(maker_spike_losses)} at spikes {loss_spikes}")
        print(f"    MAKER loss total: {total_loss:+d}c")
    else:
        print(f"    MAKER: zero spike losses ✓")
        maker_spike_pnl = sum(t["_pnl"] for t in maker_spikes)
        print(f"    MAKER spike trades: {len(maker_spikes)} | PnL={maker_spike_pnl:+d}c")

    # STB analysis
    if stb_spike_losses:
        loss_spikes = [t["_spike"] for t in stb_spike_losses]
        total_loss = sum(t["_pnl"] for t in stb_spike_losses)

        for threshold in [5, 10, 15, 20]:
            blocked_l = [t for t in stb_spike_losses if t["_spike"] > threshold]
            blocked_w = [t for t in stb_spikes if t["_spike"] > threshold and t["_wl"] == "W"]
            blocked_p = [t for t in stb_spikes if t["_spike"] > threshold and t["_wl"] == "P"]
            saved = abs(sum(t["_pnl"] for t in blocked_l))
            lost = sum(t["_pnl"] for t in blocked_w) + sum(t["_pnl"] for t in blocked_p)
            net = saved - lost
            print(f"    STB gate spike>{threshold}c: block {len(blocked_l)}L + "
                  f"{len(blocked_w)}W + {len(blocked_p)}P | "
                  f"save {saved}c - lose {lost}c = net {net:+d}c")

        print(f"    STB losses: {len(stb_spike_losses)} at spikes {loss_spikes}")
        print(f"    STB loss total: {total_loss:+d}c")
    else:
        print(f"    STB: zero spike losses ✓")
        stb_spike_pnl = sum(t["_pnl"] for t in stb_spikes)
        print(f"    STB spike trades: {len(stb_spikes)} | PnL={stb_spike_pnl:+d}c")

# ─── FINAL VERDICT ───
print()
print("=" * 80)
print("FINAL VERDICT: SPORT-SPECIFIC SPIKE GATE CONFIG")
print("=" * 80)

# Count losses per sport×type
summary = {}
for sport in sports:
    st = [t for t in trades if t["_sport"] == sport]
    for entry_type in ["STB", "MAKER"]:
        subset = [t for t in st if (entry_type == "MAKER") == t["_is_maker"]]
        spikes = [t for t in subset if t["_cls"] == "SPIKE"]
        losses = [t for t in spikes if t["_wl"] == "L"]
        winners = [t for t in spikes if t["_wl"] in ("W", "P") and t["_pnl"] > 0]
        summary[(sport, entry_type)] = {
            "trades": len(spikes),
            "losses": len(losses),
            "loss_pnl": sum(t["_pnl"] for t in losses),
            "win_pnl": sum(t["_pnl"] for t in winners),
        }

print()
for sport in sports:
    s_stb = summary.get((sport, "STB"), {})
    s_maker = summary.get((sport, "MAKER"), {})

    stb_rec = "NO GATE" if s_stb.get("losses", 0) == 0 else "NEEDS GATE"
    maker_rec = "NO GATE" if s_maker.get("losses", 0) == 0 else "NEEDS GATE"

    print(f"  {sport.upper():>8s} STB:   {s_stb.get('trades',0):>3d} spike trades | "
          f"{s_stb.get('losses',0)} losses | {stb_rec}")
    print(f"  {sport.upper():>8s} MAKER: {s_maker.get('trades',0):>3d} spike trades | "
          f"{s_maker.get('losses',0)} losses | {maker_rec}")

# Write to file
with open("/tmp/sport_spike_analysis.txt", "w") as f:
    import io, sys
    # Re-run with stdout redirected
    pass

print()
print("=" * 80)
print("Written analysis to stdout. Save manually if needed.")
print("=" * 80)
