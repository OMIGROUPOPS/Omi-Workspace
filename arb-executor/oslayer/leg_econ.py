"""OS LAYER — PER-LEG ECONOMICS (C-COMPLETION-POLICY v1; RULING_PAIR_ECONOMICS
as code). PURE module: no live_v4/network imports (gate-asserted boundary).

THE FRAME, the operator's words as math: each leg is an independent scalp —
  EV_hold = P(exit fills before collapse) x band  -  P(ride to zero) x basis
priced per tick from the FITTED surfaces (the range layer, M15: the June
WINDOW_MAP_3WAY framework era-stamped — cash/win/loss/knife per cell).
Leg one enters on conviction that entry < achievable exit. The sibling
completes ONLY on its own passing math, or as explicitly priced insurance.
pair-97 is CONSULTED NOWHERE in this module (constraint #11).

Win-ride residual (legs that ride to a WIN, paying 100-basis) is EXCLUDED
from EV_hold — conservative slack, named, per the operator's two-term frame.

Verdicts for a one-sided pair (the strand-forming state):
  hold           EV_hold(kept) >= 0
  flatten_kept   EV_hold(kept) < 0 and sibling cannot pass its own math ->
                 never hold the kept leg naked; price = current bid
  taker_complete EV_cross(sibling at ask) > 0 and > EV of flattening ->
                 cross the spread on the winning sibling (GATED:
                 operator_taker_word — computes and logs, cannot act)
NO-OPINION when the range cell is empty/thin (never a guess)."""


def _bucket(delta):
    if delta <= -5:
        return "deep_disc"
    if delta < -1:
        return "disc"
    if delta <= 1:
        return "at_mid"
    if delta < 5:
        return "over"
    return "deep_over"


def _cell(px):
    if px <= 25:
        return "le25"
    if px <= 50:
        return "26_50"
    if px <= 75:
        return "51_75"
    return "ge75"


def leg_ev(range_cells, cat, side, basis, band, runmid_now):
    """EV of HOLDING a leg priced from its live range position:
    (cat, side, bucket(basis - runmid_now), cell(basis)). Returns dict."""
    if runmid_now is None or not basis or not band or band <= 0:
        return {"opinion": "NO-OPINION",
                "missing": "no observable runmid / basis / band"}
    key = "|".join((cat or "?", side or "?", _bucket(basis - runmid_now), _cell(basis)))
    v = (range_cells or {}).get(key)
    if not v or v.get("n", 0) < 5:
        return {"opinion": "NO-OPINION", "cell": key,
                "missing": "range cell empty/thin (n=%s)" % (v.get("n", 0) if v else 0)}
    n = float(v["n"])
    p_exit = v.get("cashed", 0) / n
    p_zero = v.get("loss", 0) / n
    ev = p_exit * band - p_zero * basis
    return {"opinion": "EV", "cell": key, "n": v["n"],
            "p_exit_fill": round(p_exit, 3), "p_ride_zero": round(p_zero, 3),
            "ev_cents": round(ev, 2), "band": band, "basis": basis,
            "win_ride_residual_excluded": round(v.get("win", 0) / n, 3),
            "citation": "M15 RANGE_LAYER_3WAY (WINDOW_MAP_3WAY axes)"}


def completion_verdict(range_cells, cat, kept_side, kept_basis, kept_band,
                       kept_bid_now, sib_side, sib_ask, sib_band, runmid_kept,
                       runmid_sib):
    """The one-sided-pair policy, both branches, shadow verdicts only."""
    kept = leg_ev(range_cells, cat, kept_side, kept_basis, kept_band, runmid_kept)
    # branch (b): the cross priced as a fresh taker entry at the ask,
    # basis = ask, minus nothing hidden -- the ask IS the cost
    cross = leg_ev(range_cells, cat, sib_side, sib_ask, sib_band, runmid_sib) \
        if sib_ask else {"opinion": "NO-OPINION", "missing": "no sibling ask"}
    if kept.get("opinion") != "EV":
        return {"verdict": "NO-OPINION", "kept": kept, "cross": cross}
    if kept["ev_cents"] >= 0:
        v = "hold"
    elif cross.get("opinion") == "EV" and cross["ev_cents"] > 0 and \
            cross["ev_cents"] > kept["ev_cents"]:
        v = "taker_complete"      # gated: operator_taker_word
    else:
        v = "flatten_kept"
    return {"verdict": v, "kept": kept, "cross": cross,
            "flatten_price_now": kept_bid_now,
            "pair97_consulted": False}
