#!/usr/bin/env python3
"""
Generate the PER-CENT v3 DEPLOYMENT blueprint from the LOCKED ground-truth v3
pooled surfaces -- the perfect blend.

THE CORRECTION (operator, 2026-05-29):
  The 56-band blueprint collapsed 5 cents into one shared exit X. But "every
  cent is its own cent." AND strict own-N is NOT enough -- argmax-X on a thin
  cent is unstable (overfits a handful of tapes -> false positives live).

  The reconciliation already exists and is LOCKED: the ground-truth v3 pooled
  surface (build_pooled_surface_v3.py, CV-selected sigma per category) decides
  PER CENT whether to trust own-N or fall back to the pooled neighborhood --
  the `achievable.basis` field is "own-N" where the cent is credible (low
  cvErr) and "pooled" where own-N is thin. This is the perfect blend; this
  generator just READS it. No new formula, no re-validation.

PER-CENT EXIT:
  exit_target(cent) = surface.row[cent].achievable.bestX     (the blend's X)
  VIABILITY GATE    = surface.row[cent].achievable.ev > 0
  hold-to-settle    = bestX None OR ev < holdEv -> exit_target None

ARCHITECTURE (drop-in, zero executor tier rewrite):
  Keep the SAME 56 band keys (cat, dir, lo, hi) as the lookup ENVELOPE. Inside
  each band cell, embed `percent_exits`: {cent -> {exit_target, ev, hit, basis,
  ownN, effN}}. The executor resolves the band, then picks the SPECIFIC entry
  cent's exit from percent_exits. A band is SKIP only if EVERY cent in it is
  non-viable; otherwise it trades the viable cents and skips the rest.

OUTPUT: version_c_blueprint_v3.py  (per-cent, replaces the 56-band-only one)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from version_b_blueprint import DEPLOYMENT as OLD  # noqa: E402

HERE = Path(__file__).resolve().parent
ARB = HERE.parent
ATL = ARB / "data" / "durable" / "exit_atlas_v1"
CATS = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]

LEADER_TIERS = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
UNDERDOG_TIERS = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]
STD_ENTRY, STD_DCA = 40, 20


def load_surface(cat):
    S = json.load(open(ATL / f"{cat.lower()}_pooled_surface_v3.json"))
    return {r["c"]: r for r in S["rows"]}


def percent_cell(row):
    """Per-cent deployable exit from the locked surface's achievable (the blend).
    Returns (exit_target, viable, meta) where exit_target=None means hold."""
    a = row.get("achievable") or {}
    bx = a.get("bestX")
    ev = a.get("ev")
    if bx is None or ev is None or ev <= 0:
        return None, False, {
            "exit_target": None, "ev": (round(ev, 3) if ev is not None else None),
            "hit": None, "basis": a.get("basis"),
            "ownN": row.get("ownN"), "effN": round(row.get("effN", 0), 1),
            "cvErr": (round(a.get("cvErr"), 1) if a.get("cvErr") is not None else None),
        }
    # hold-to-settle wins if holding beats the best early exit
    hold = a.get("holdEv")
    exit_t = bx if (hold is None or ev >= hold) else None
    return exit_t, True, {
        "exit_target": exit_t, "ev": round(ev, 3),
        "hit": (round(a.get("hit"), 2) if a.get("hit") is not None else None),
        "basis": a.get("basis"),
        "ownN": row.get("ownN"), "effN": round(row.get("effN", 0), 1),
        "cvErr": (round(a.get("cvErr"), 1) if a.get("cvErr") is not None else None),
    }


def build():
    out = {}
    stats = {"trade_cents": 0, "skip_cents": 0, "hold_cents": 0,
             "own_basis": 0, "pooled_basis": 0, "skip_bands": 0, "trade_bands": 0}
    for cat in CATS:
        surf = load_surface(cat)
        for dirn, tiers in (("leader", LEADER_TIERS), ("underdog", UNDERDOG_TIERS)):
            for lo, hi in tiers:
                key = (cat, dirn, lo, hi)
                old = OLD.get(key) if isinstance(OLD.get(key), dict) else None
                # sizing/dca carried from old where active else defaults
                if old:
                    dca_drop = old.get("dca_drop")
                    dca_size = old.get("dca_size", 0)
                    base_entry = old.get("entry_size", STD_ENTRY) or STD_ENTRY
                else:
                    dca_drop, dca_size, base_entry = None, 0, STD_ENTRY

                pe = {}
                any_viable = False
                for c in range(lo, hi + 1):
                    row = surf.get(c)
                    if row is None:
                        continue
                    exit_t, viable, meta = percent_cell(row)
                    pe[c] = meta
                    if viable:
                        any_viable = True
                        stats["trade_cents"] += 1
                        if exit_t is None:
                            stats["hold_cents"] += 1
                        if meta["basis"] == "own-N":
                            stats["own_basis"] += 1
                        elif meta["basis"] == "pooled":
                            stats["pooled_basis"] += 1
                    else:
                        stats["skip_cents"] += 1

                # band-level entry_size: 0 only if NO cent viable
                entry_size = base_entry if any_viable else 0
                dsize = dca_size if (any_viable and dca_drop is not None) else 0
                if any_viable:
                    stats["trade_bands"] += 1
                else:
                    stats["skip_bands"] += 1

                # band-level exit_target = volume(ownN)-weighted mean of viable
                # cents' exits (a fallback for any code path that reads the band
                # value; the per-cent map is the source of truth).
                vex = [(pe[c]["exit_target"], pe[c]["ownN"] or 1)
                       for c in pe if pe[c]["exit_target"] is not None]
                if vex:
                    band_exit = round(sum(x * n for x, n in vex) / sum(n for _, n in vex))
                else:
                    band_exit = None

                out[key] = {
                    "entry_lo": lo, "entry_hi": hi,
                    "dca_drop": dca_drop,
                    "exit_target": band_exit,            # band fallback only
                    "entry_size": entry_size, "dca_size": dsize,
                    "mode": dirn,
                    "maker_bid_offset": 0,
                    "percent_exits": pe,                 # SOURCE OF TRUTH (per cent)
                    "source": "v3_pooled_blend_percent_2026-05-29",
                }
    return out, stats


def fmt(out):
    L = ['"""VERSION C Deployment Blueprint - v3 PER-CENT EXIT FLOOR (perfect blend)',
         "=" * 72,
         "Generated 2026-05-29 from the LOCKED ground-truth v3 pooled surfaces.",
         "",
         "Every cent is its own cent. exit_target per cent = the v3 pooled-surface",
         "achievable.bestX -- the PERFECT BLEND: per-cent CV decides own-N (where the",
         "cent is credible) vs pooled neighborhood (where own-N is thin/unstable).",
         "Strict own-N alone overfits thin cents; this is the validated balance.",
         "",
         "LOOKUP: band keys (cat,dir,lo,hi) are the ENVELOPE; each cell's",
         "percent_exits[cent] holds that cent's own exit_target/ev/hit/basis. The",
         "executor resolves the band then reads the specific entry cent. A band is",
         "SKIP only if EVERY cent in it is non-viable.",
         "",
         "maker_bid_offset=0 (taker floor). Part 2 entry discount layers on top.",
         '"""',
         "",
         "DEPLOYMENT = {"]
    last = None
    for key in sorted(out, key=lambda k: (CATS.index(k[0]), 0 if k[1] == "leader" else 1, k[2])):
        if key[0] != last:
            L.append(f"\n    # {'=' * 56}\n    # {key[0]}\n    # {'=' * 56}")
            last = key[0]
        c = out[key]
        viab = "TRADE" if c["entry_size"] > 0 else "SKIP "
        L.append(f"    {key!r}: {{  # {viab} band_exit={c['exit_target']}")
        L.append(f"        'entry_lo': {c['entry_lo']}, 'entry_hi': {c['entry_hi']},")
        L.append(f"        'dca_drop': {c['dca_drop']}, 'exit_target': {c['exit_target']},")
        L.append(f"        'entry_size': {c['entry_size']}, 'dca_size': {c['dca_size']},")
        L.append(f"        'mode': {c['mode']!r}, 'maker_bid_offset': {c['maker_bid_offset']},")
        L.append("        'percent_exits': {")
        for cent in sorted(c["percent_exits"]):
            m = c["percent_exits"][cent]
            L.append(f"            {cent}: {{'exit_target': {m['exit_target']}, "
                     f"'ev': {m['ev']}, 'hit': {m['hit']}, 'basis': {m['basis']!r}, "
                     f"'ownN': {m['ownN']}, 'effN': {m['effN']}, 'cvErr': {m['cvErr']}}},")
        L.append("        },")
        L.append(f"        'source': {c['source']!r},")
        L.append("    },")
    L.append("}")

    # drop-in helpers (parity with version_b_blueprint API) + per-cent resolver
    L.append('''

LEADER_TIERS_V5 = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
UNDERDOG_TIERS_V5 = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]


def get_strategy(category, side, entry_price):
    """Resolve the band, then specialize to the ENTRY CENT's own exit.

    Returns a cell dict whose exit_target is the per-cent value for entry_price
    (every cent is its own cent). Returns None if the band is absent, the band
    is a full SKIP, or this specific cent is non-viable (percent_exits[cent]
    has exit_target None AND ev<=0). Drop-in for the version_b API.
    """
    tiers = LEADER_TIERS_V5 if side == 'leader' else UNDERDOG_TIERS_V5
    for lo, hi in tiers:
        if lo <= entry_price <= hi:
            cell = DEPLOYMENT.get((category, side, lo, hi))
            if cell is None or cell.get('entry_size', 0) == 0:
                return None
            pe = cell.get('percent_exits', {}).get(entry_price)
            if pe is None:
                return None
            # this cent is viable iff it has a positive-EV achievable read
            if (pe.get('ev') or 0) <= 0:
                return None  # cent-level SKIP even though the band trades
            out = dict(cell)
            out['exit_target'] = pe['exit_target']   # per-cent exit (None=hold)
            out['cent_ev'] = pe['ev']
            out['cent_hit'] = pe['hit']
            out['cent_basis'] = pe['basis']
            out['cent_ownN'] = pe['ownN']
            out['cent_effN'] = pe['effN']
            # in_sample_daily_pnl: dual-mode primary-side tiebreaker -> per-cent ev
            out['in_sample_daily_pnl'] = pe['ev']
            return out
    return None


def use_blended_target(category, direction, tier_lo, tier_hi):
    """Conservative FLOOR: always first-fill target (False). Blended-average
    auto-sell is a Part-2 entry-side enhancement; the floor never assumes it."""
    return False
''')
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    out, stats = build()
    txt = fmt(out)
    (ARB / "version_c_blueprint_v3.py").write_text(txt, encoding="utf-8")
    print("wrote version_c_blueprint_v3.py")
    print(f"bands: {len(out)}  TRADE_bands={stats['trade_bands']}  SKIP_bands={stats['skip_bands']}")
    print(f"per-cent: TRADE_cents={stats['trade_cents']}  SKIP_cents={stats['skip_cents']}  "
          f"HOLD_cents={stats['hold_cents']}")
    print(f"basis: own-N={stats['own_basis']}  pooled={stats['pooled_basis']} "
          f"(pooled = thin cents the blend rescues with neighbors)")
