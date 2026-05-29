#!/usr/bin/env python3
"""
Generate the v3 DEPLOYMENT blueprint from the CORRECTED pooled best-X surfaces.

WHY: every prior blueprint (version_b_blueprint.py) was built on the broken
foundation (size_qual contamination, own-N false negatives, breakeven formula
overriding tape). Measured: 40/41 cells had the wrong exit_target, 12 cells
told the bot to HOLD when it should EXIT early, 12 profitable cells were
wrongly SKIPPED. This regenerates the blueprint cell-by-cell from v3 ground
truth.

SCOPE = CONSERVATIVE EXIT FLOOR:
  - exit_target  : volume-weighted pooled best-X across each band's cents
                   (the proven exit). Band EV<=0 => SKIP (entry_size 0).
  - maker_bid_offset = 0  : TAKER entry at the anchor. No discount yet. This is
                   the floor; Part 2 (entry discount) only loosens exit
                   requirements and lifts EV on top of this.
  - sizing / dca : carried from the existing band sizing where active (these
                   are capital/entry knobs, NOT the foundation bug). Cells v3
                   RE-OPENS default to standard 40/20. dca_drop carried as-is
                   (entry-side mechanic, revisited in Part 2).

Keeps the SAME band structure as the live bot (leader 55-89, underdog 10-44 per
category) so it is drop-in: CC does not need to touch LEADER_TIERS_V5 /
UNDERDOG_TIERS_V5. Only the DEPLOYMENT dict body changes.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import exit_chain_core as ec  # noqa: E402
from version_b_blueprint import DEPLOYMENT as OLD  # noqa: E402

HERE = Path(__file__).resolve().parent
ARB = HERE.parent
ATL = ARB / "data" / "durable" / "exit_atlas_v1"
SVM = ARB / "data" / "durable" / "spike_volatility_map"
CATS = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]

# Same band structure the live bot uses.
LEADER_TIERS = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
UNDERDOG_TIERS = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]

STD_ENTRY, STD_DCA = 40, 20  # default sizing for cells v3 re-opens


def load_surface(cat):
    S = json.load(open(ATL / f"{cat.lower()}_pooled_surface_v3.json"))
    rows = {r["c"]: (r.get("achievable") or {}) for r in S["rows"]}
    return rows


def load_counts(cat):
    df = ec.load_corpus(str(SVM / f"{cat.lower()}_spike_perN.parquet"))
    return df["c"].value_counts().to_dict()


def load_df(cat):
    return ec.load_corpus(str(SVM / f"{cat.lower()}_spike_perN.parquet"))


def own_tape_best(df, lo, hi):
    """The TRUE floor: sweep every exit X over the band's OWN tapes (each N at
    its own cent, T = own_c + X) and return the X that maximizes realized EV/N,
    plus that EV and the hit rate. This is what actually happens if deployed --
    no pooling, no smoothing. Pooling may ENRICH the map but can never flip an
    own-tape-negative band into a live trade."""
    import numpy as np
    sub = df[(df.c >= lo) & (df.c <= hi)]
    if len(sub) == 0:
        return None
    pk = sub["peak"].to_numpy(); cc = sub["c"].to_numpy(); wn = sub["win"].to_numpy()
    best = None
    for X in range(1, 95):
        T = cc + X
        pnl = np.where(pk >= T, T - cc,
                       np.where(wn == 1, ec.SETTLE_WIN - cc, -cc)).astype(float)
        ev = float(pnl.mean())
        hit = float((pk >= T).mean())
        if best is None or ev > best[1]:
            best = (X, ev, hit)
    # also hold-to-settle as a candidate (X = None)
    hold = float(np.where(wn == 1, ec.SETTLE_WIN - cc, -cc).astype(float).mean())
    return {"X": best[0], "ev": best[1], "hit": best[2], "hold_ev": hold, "n": int(len(sub))}


def band_stats(rows, counts, lo, hi):
    """Volume-weighted pooled best-X + aggregate EV/hit across cents in band."""
    num_x = num_w = 0.0      # weighted exit
    ev_sum = n_sum = 0.0
    hit_w = 0.0
    pos_cents = []
    for c in range(lo, hi + 1):
        a = rows.get(c)
        if not isinstance(a, dict) or a.get("bestX") is None:
            continue
        n = counts.get(c, 0)
        ev = a.get("ev")
        if ev is None:
            continue
        ev_sum += ev * n
        n_sum += n
        if ev > 0:
            pos_cents.append(c)
            num_x += a["bestX"] * n
            num_w += n
            hit_w += (a.get("hit") or 0) * n
    if n_sum == 0:
        return None
    band_ev = ev_sum / n_sum                       # vol-weighted EV/N over band
    exit_x = round(num_x / num_w) if num_w > 0 else None
    hit = (hit_w / num_w / 100.0) if num_w > 0 else None
    return {
        "exit_x": exit_x,
        "band_ev": band_ev,
        "n": int(n_sum),
        "hit": hit,
        "pos_cents": pos_cents,
        "n_pos": int(num_w),
    }


def build():
    out = {}
    reopened = []
    closed = []
    for cat in CATS:
        rows = load_surface(cat)
        counts = load_counts(cat)
        df = load_df(cat)
        for dirn, tiers in (("leader", LEADER_TIERS), ("underdog", UNDERDOG_TIERS)):
            for lo, hi in tiers:
                key = (cat, dirn, lo, hi)
                st = band_stats(rows, counts, lo, hi)          # pooled (enrichment)
                ot = own_tape_best(df, lo, hi)                  # OWN-TAPE FLOOR (binding)
                old = OLD.get(key) if isinstance(OLD.get(key), dict) else None
                # VIABILITY GATE = own-tape realized EV must be positive. Pooling
                # only enriches the map; it can NEVER flip an own-tape-negative
                # band into a live trade. The exit_target is the own-tape argmax.
                viable = ot is not None and ot["ev"] > 0 and ot["X"] is not None
                # carry sizing/dca/entry-range from old where present, else defaults
                if old:
                    entry_lo = old.get("entry_lo", lo)
                    entry_hi = old.get("entry_hi", hi)
                    dca_drop = old.get("dca_drop")
                    dca_size = old.get("dca_size", 0)
                    base_entry = old.get("entry_size", STD_ENTRY) or STD_ENTRY
                    old_was_skip = old.get("entry_size", 0) == 0
                else:
                    entry_lo, entry_hi = lo, hi
                    dca_drop, dca_size = None, 0
                    base_entry = STD_ENTRY
                    old_was_skip = True
                if viable:
                    entry_size = base_entry
                    dsize = dca_size if dca_drop is not None else 0
                    if old_was_skip:
                        entry_size = STD_ENTRY
                        dsize = 0
                        reopened.append((key, round(ot["ev"], 2), ot["X"], ot["n"]))
                else:
                    entry_size, dsize = 0, 0
                    if old and not old_was_skip:
                        closed.append((key, round(ot["ev"], 2) if ot else None))
                # exit_target = OWN-TAPE argmax (binding floor). If holding to
                # settle beats every early exit, exit_target=None (hold).
                exit_target = None
                if viable:
                    exit_target = ot["X"] if ot["ev"] >= ot["hold_ev"] else None
                out[key] = {
                    "entry_lo": entry_lo, "entry_hi": entry_hi,
                    "dca_drop": dca_drop,
                    "exit_target": exit_target,
                    "entry_size": entry_size, "dca_size": dsize,
                    "mode": dirn,
                    "maker_bid_offset": 0,            # TAKER FLOOR — no discount yet
                    # BINDING own-tape floor (what actually happens if deployed):
                    "own_ev": (round(ot["ev"], 3) if ot else None),
                    "own_hit": (round(ot["hit"], 4) if ot else None),
                    "own_n": (ot["n"] if ot else 0),
                    # Pooled surface (enrichment / cross-cent context only):
                    "pooled_band_ev": (round(st["band_ev"], 3) if st else None),
                    "pooled_hit": (round(st["hit"], 4) if st and st["hit"] else None),
                    "source": "v3_own_tape_floor_2026-05-29",
                }
    return out, reopened, closed


def fmt(out):
    """Emit a clean python module string for version_c_blueprint_v3.py."""
    lines = ['"""VERSION C Deployment Blueprint — v3 OWN-TAPE EXIT FLOOR (CORRECTED FOUNDATION)',
             "=" * 72,
             "Generated: 2026-05-29 from the corrected Foundation tapes.",
             "",
             "REPLACES version_b_blueprint.py, which was built on the BROKEN foundation",
             "(size_qual contamination + own-N false negatives + breakeven formula over",
             "tape). vs v3 truth the old blueprint was wrong on 40/41 exit_targets, held",
             "12 cells that should exit early, and skipped 12 profitable cells.",
             "",
             "SCOPE: conservative EXIT FLOOR for LIVE capital.",
             "  - VIABILITY GATE = OWN-TAPE realized EV>0. The pooled surface is for",
             "    MAPPING/understanding; for live money the binding floor is what each",
             "    band's own tapes actually did. Pooling can enrich but NEVER flips an",
             "    own-tape-negative band into a trade (caught 15 such cells).",
             "  - exit_target = OWN-TAPE argmax X (or None = hold to settle if holding",
             "    beats every early exit).",
             "  - maker_bid_offset = 0 (TAKER entry at the anchor). Part 2 entry discount",
             "    layers on top and only LOOSENS exit requirements / lifts EV.",
             "",
             "Each cell carries own_ev/own_hit/own_n (binding) + pooled_band_ev/pooled_hit",
             "(context). Drop-in: same band structure as LEADER_TIERS_V5/UNDERDOG_TIERS_V5.",
             '"""',
             "",
             "DEPLOYMENT = {"]
    last_cat = None
    for key in sorted(out, key=lambda k: (CATS.index(k[0]), 0 if k[1] == "leader" else 1, k[2])):
        cat = key[0]
        if cat != last_cat:
            lines.append(f"\n    # {'=' * 56}\n    # {cat}\n    # {'=' * 56}")
            last_cat = cat
        c = out[key]
        viab = "TRADE" if c["entry_size"] > 0 else "SKIP "
        lines.append(f"    {key!r}: {{  # {viab} own_ev={c['own_ev']} own_n={c['own_n']} own_hit={c['own_hit']}")
        lines.append(f"        'entry_lo': {c['entry_lo']}, 'entry_hi': {c['entry_hi']},")
        lines.append(f"        'dca_drop': {c['dca_drop']}, 'exit_target': {c['exit_target']},")
        lines.append(f"        'entry_size': {c['entry_size']}, 'dca_size': {c['dca_size']},")
        lines.append(f"        'mode': {c['mode']!r}, 'maker_bid_offset': {c['maker_bid_offset']},")
        lines.append(f"        'own_ev': {c['own_ev']}, 'own_hit': {c['own_hit']}, 'own_n': {c['own_n']},")
        # in_sample_daily_pnl: dual-mode primary-side tiebreaker in tennis_v5.py.
        # Mapped to own_ev (per-N realized EV) = the binding live floor metric,
        # so the stronger side wins primary by its true own-tape edge.
        lines.append(f"        'in_sample_daily_pnl': {c['own_ev']},")
        lines.append(f"        'pooled_band_ev': {c['pooled_band_ev']}, 'pooled_hit': {c['pooled_hit']},")
        lines.append(f"        'source': {c['source']!r},")
        lines.append("    },")
    lines.append("}")

    # ---- drop-in helpers (parity with version_b_blueprint API) ----
    lines.append('''

LEADER_TIERS_V5 = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
UNDERDOG_TIERS_V5 = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]

def get_strategy(category, side, entry_price):
    """Lookup the strategy cell for (category, side, entry_price).

    Returns the cell dict if a viable cell matches and entry_price is within
    its [entry_lo, entry_hi] sub-range, else None. SKIP cells (entry_size==0)
    are returned as-is; caller checks entry_size. Drop-in for version_b API.
    """
    tiers = LEADER_TIERS_V5 if side == 'leader' else UNDERDOG_TIERS_V5
    for lo, hi in tiers:
        if lo <= entry_price <= hi:
            cell = DEPLOYMENT.get((category, side, lo, hi))
            if cell is None:
                return None
            if cell['entry_lo'] <= entry_price <= cell['entry_hi']:
                return cell
            return None
    return None


def use_blended_target(category, direction, tier_lo, tier_hi):
    """Conservative FLOOR: always first-fill target (False).

    The blended-average auto-sell optimization is an ENTRY-side (Part 2)
    enhancement; the exit floor never assumes it. Defaults False for all cells.
    """
    return False
''')

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    out, reopened, closed = build()
    txt = fmt(out)
    dst = ARB / "version_c_blueprint_v3.py"
    dst.write_text(txt, encoding="utf-8")
    trade = sum(1 for c in out.values() if c["entry_size"] > 0)
    skip = sum(1 for c in out.values() if c["entry_size"] == 0)
    print(f"wrote {dst}")
    print(f"cells: {len(out)}  TRADE={trade}  SKIP={skip}")
    print(f"re-opened (v3 profitable, old skipped): {len(reopened)}")
    for k, ev, x, n in reopened:
        print(f"   {k}  v3_ev={ev}  exit=+{x}  n={n}")
    print(f"closed (old traded, v3 negative): {len(closed)}")
    for k, ev in closed:
        print(f"   {k}  v3_ev={ev}")
