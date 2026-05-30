#!/usr/bin/env python3
"""
Per-cent weighted exit surface (own-N + eff-N pyramid).

WHAT THIS SOLVES (operator, 2026-05-29):
  The 56-band v3 floor collapses 5 cents into ONE shared exit offset X. But
  "every cent is its own cent" -- each cent should get its OWN exit X, computed
  from a WEIGHTED BALANCE of its own tapes (own-N) and its neighbors (eff-N).
  Where own-N is fat, the cent trusts itself; where own-N is thin, neighbors
  fill in (the pyramid). One continuous dial, not a binary band/own switch.

THE BLEND (per cent c, per exit offset X):
    f_blend(c, X) = sum_k  g(k - c) * pnl_own(k, X)
  where g is a Gaussian weight over the band's own tapes within +-w of c,
  bandwidth sigma per category (v3 CV: atp_main 5, atp_chall 3, wta_main 4,
  wta_chall 6). The cent's exit X* = argmax_X f_blend(c, X).

TWO GATE BASES (operator: "whatever is more profitable"):
  A. STRICT  -- a cent trades only if its OWN-N realized EV > 0. eff-N sets the
                exit X but can never flip an own-negative cent into a trade.
  B. BLENDED -- a cent trades if the eff-N blended EV > 0.
  We measure BOTH against each cent's OWN tapes (own-N realized PnL is ALWAYS
  the judge -- the tape always wins), then report which is more profitable
  per category so the operator's "more profitable" rule decides.

OUTPUT: data/durable/spike_volatility_map/{cat}_percent_exits_v3.json
  per cent: own_x/own_ev/own_n, blend_x/blend_ev, gate decisions A & B,
  realized own-tape EV under each gate's chosen exit.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import exit_chain_core as ec  # noqa: E402

HERE = Path(__file__).resolve().parent
ARB = HERE.parent
SVM = ARB / "data" / "durable" / "spike_volatility_map"

CATS = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]
# v3 CV-selected per-category sigma (already validated; thin cats pool wider).
SIGMA = {"ATP_MAIN": 5, "ATP_CHALL": 3, "WTA_MAIN": 4, "WTA_CHALL": 6}

# Tradeable cent range matches the live bot's tiers: leader 55-89, dog 10-44.
LEADER_CENTS = list(range(55, 90))
DOG_CENTS = list(range(10, 45))
X_RANGE = range(1, 95)


def load_df(cat):
    return ec.load_corpus(str(SVM / f"{cat.lower()}_spike_perN.parquet"))


def cent_arrays(df, c):
    sub = df[df.c == c]
    if len(sub) == 0:
        return None
    return (sub["peak"].to_numpy().astype(float),
            sub["c"].to_numpy().astype(float),
            sub["win"].to_numpy().astype(float))


def pnl_at_X(pk, cc, wn, X):
    """Realized per-N PnL vector if we exit at own-anchor + X (else settle)."""
    T = cc + X
    return np.where(pk >= T, T - cc,
                    np.where(wn == 1, ec.SETTLE_WIN - cc, -cc)).astype(float)


def own_best(pk, cc, wn):
    """Pure own-tape argmax X + its realized EV/hit (oranges -- binding judge)."""
    best = None
    for X in X_RANGE:
        ev = float(pnl_at_X(pk, cc, wn, X).mean())
        if best is None or ev > best[1]:
            best = (X, ev, float((pk >= (cc + X)).mean()))
    hold = float(np.where(wn == 1, ec.SETTLE_WIN - cc, -cc).mean())
    return {"X": best[0], "ev": best[1], "hit": best[2], "hold_ev": hold}


def build_cat(cat):
    df = load_df(cat)
    sigma = SIGMA[cat]
    # cache each cent's raw tapes + own-best
    cents = sorted(int(x) for x in df["c"].unique())
    cache = {}
    for c in cents:
        a = cent_arrays(df, c)
        if a is None:
            continue
        pk, cc, wn = a
        cache[c] = {"pk": pk, "cc": cc, "wn": wn, "n": len(pk),
                    "own": own_best(pk, cc, wn)}

    def tradeable(c, direction):
        return c in (LEADER_CENTS if direction == "leader" else DOG_CENTS)

    out = {}
    for direction in ("leader", "underdog"):
        cent_list = LEADER_CENTS if direction == "leader" else DOG_CENTS
        for c in cent_list:
            if c not in cache:
                continue
            own = cache[c]["own"]
            own_n = cache[c]["n"]

            # --- BLENDED surface: Gaussian-weighted EV across neighbor cents ---
            # For each X, ev_blend(X) = sum_k w_k * ev_own(k, X), w_k ~ N(0,sigma)
            # restricted to neighbors within the SAME direction's tradeable range
            # (don't pool a favorite into an underdog).
            neigh = [k for k in cache
                     if abs(k - c) <= 3 * sigma and tradeable(k, direction)]
            w = {k: float(np.exp(-0.5 * ((k - c) / sigma) ** 2)) for k in neigh}
            wsum = sum(w.values())
            blend_best = None
            for X in X_RANGE:
                ev = sum(w[k] * float(pnl_at_X(cache[k]["pk"], cache[k]["cc"],
                                               cache[k]["wn"], X).mean())
                         for k in neigh) / wsum
                if blend_best is None or ev > blend_best[1]:
                    blend_best = (X, ev)
            blend_x, blend_ev = blend_best

            # eff_n: sum of neighbor weights * their N (interpretable pyramid N)
            eff_n = sum(w[k] * cache[k]["n"] for k in neigh) / max(w[c], 1e-9)

            # --- Realized OWN-TAPE EV under each gate's chosen exit X ---
            pk, cc, wn = cache[c]["pk"], cache[c]["cc"], cache[c]["wn"]
            realized_own_x = own["ev"]                       # gate A exit = own X
            realized_blend_x = float(pnl_at_X(pk, cc, wn, blend_x).mean())  # gate B exit = blend X, judged on OWN tape

            # GATE A (strict own-N): trade iff own EV>0; exit at own X
            gateA_trade = own["ev"] > 0
            gateA_realized = realized_own_x if gateA_trade else 0.0
            # GATE B (blended eff-N): trade iff blend EV>0; exit at blend X,
            # but realized PnL still measured on OWN tape (tape wins).
            gateB_trade = blend_ev > 0
            gateB_realized = realized_blend_x if gateB_trade else 0.0

            out[f"{direction}:{c}"] = {
                "cent": c, "direction": direction,
                "own_n": own_n, "eff_n": round(eff_n, 1),
                "own_x": own["X"], "own_ev": round(own["ev"], 3),
                "own_hit": round(own["hit"], 4), "own_hold_ev": round(own["hold_ev"], 3),
                "blend_x": blend_x, "blend_ev": round(blend_ev, 3),
                "realized_own_at_own_x": round(realized_own_x, 3),
                "realized_own_at_blend_x": round(realized_blend_x, 3),
                "gateA_strict_trade": gateA_trade,
                "gateA_realized_own_ev": round(gateA_realized, 3),
                "gateB_blended_trade": gateB_trade,
                "gateB_realized_own_ev": round(gateB_realized, 3),
            }
    return out


def main():
    summary = {}
    for cat in CATS:
        res = build_cat(cat)
        json.dump(res, open(SVM / f"{cat.lower()}_percent_exits_v3.json", "w"), indent=2)
        # aggregate realized own-tape EV*N under each gate (total $ proxy)
        def agg(gate_real_key, gate_trade_key):
            tot = 0.0; ncells = 0; ntr = 0
            for v in res.values():
                ncells += 1
                if v[gate_trade_key]:
                    ntr += 1
                    tot += v[gate_real_key] * v["own_n"]  # EV/N * N = total realized $
            return tot, ntr, ncells
        a_tot, a_tr, ncells = agg("gateA_realized_own_ev", "gateA_strict_trade")
        b_tot, b_tr, _ = agg("gateB_realized_own_ev", "gateB_blended_trade")
        summary[cat] = {
            "cells": ncells,
            "gateA_strict": {"total_realized_own": round(a_tot, 1), "trades": a_tr},
            "gateB_blended": {"total_realized_own": round(b_tot, 1), "trades": b_tr},
            "more_profitable": "A_strict" if a_tot >= b_tot else "B_blended",
        }
    json.dump(summary, open(SVM / "percent_exits_v3_summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
