#!/usr/bin/env python3
"""C-CONVICTION-REPLAY Part 3 — the conviction composer (offline, recorded tape only).

Constraints bound (docs/OPERATOR_CONSTRAINTS.md):
  #1 build-before-rerun (the 3a tests in conviction_replay.py gate the replay)
  #4 no decreed constant is a goal or anchor (pair-97 graded as contamination)
  #5 directional conviction at discovery; EVERY tick alters the confidence
  NO-OPINION discipline: no admissible anchor -> NO-OPINION with the missing
  model NAMED (MODEL_REGISTRY.md gaps G1..G5). Never a guess, never a constant
  filling the vacuum.

Era law (census 07-10): ITF = live-era anchors only; CHALL archive ±30m coarse;
mains CONVICTED -> no admissible discovery prior (gap G1).

Honesty about what we own: the registry holds NO fitted match-winner model —
the direction PRIOR is the market-implied probability at discovery (the three
observable prices), CITED as such; the fitted models speak to W1 SHAPE
(M2 dip anatomy), EDGE (M1 cell edge_p50) and WAKE RISK (M3 volume floor).
The tick posterior then lets the tape overrule the prior print by print."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE_ERA_OK = {"ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL"}   # M1-M4 fits (live tape)
MAINS = {"ATP_MAIN", "WTA_MAIN"}
K_PRIOR = 8.0    # prints needed for the tape to outweigh the prior 50/50


class Composer:
    def __init__(self):
        self.m1 = self._load(ROOT.parent / ".claude/seqfloor_20260708/recut_cells.json")
        _a = self._load(ROOT / "docs/policy/aim_table.json")
        self.m2 = (_a or {}).get("aim")
        self.m3 = self._load(ROOT.parent / ".claude/volume_20260709/recut_cells_volume.json")

    @staticmethod
    def _load(p):
        try:
            return json.loads(Path(p).read_text(encoding="utf-8"))
        except OSError:
            return None

    # ---- (a) discovery prior, per leg ----
    def discovery_prior(self, cat, price, sibling_price=None, lifetime_vol=None,
                        offered_anchor_era=None):
        """Returns dict {opinion: 'PRIOR'|'NO-OPINION', ...}. offered_anchor_era
        lets a caller TRY to hand us an archive anchor -- the era law refuses it
        for ITF (the 3a era test)."""
        if offered_anchor_era == "archive" and cat in ("ITF_M", "ITF_W"):
            return {"opinion": "NO-OPINION", "cat": cat,
                    "missing": "M9 has no ITF rows and archive anchors are "
                               "INADMISSIBLE for ITF (census 07-10, gap G4) -- "
                               "offered archive anchor REFUSED"}
        if cat in MAINS:
            return {"opinion": "NO-OPINION", "cat": cat,
                    "missing": "G1: no admissible discovery-time direction model "
                               "for mains (clocks convicted, gauge fits exclude mains)"}
        if cat not in LIVE_ERA_OK or price is None or not (0 < price < 100):
            return {"opinion": "NO-OPINION", "cat": cat,
                    "missing": "no admissible category anchor / no observable price"}
        citations = ["market-implied prior (three observable prices law)"]
        direction = "climb_side" if price >= 50 else "decay_side"
        conf = price / 100.0
        # W1 shape from the fitted surfaces (never a decreed constant):
        dip = None
        if self.m2:
            try:
                bucket = self.m2.get(cat) or {}
                for b, row in bucket.items():
                    lo, hi = (int(x) for x in b.split("-"))
                    if lo <= price <= hi:
                        dip = row.get("dip_med", row.get("faller_depth"))
                        break
                if dip is not None:
                    citations.append("M2 aim_table dip anatomy (%s bucket %s)" % (cat, b))
            except Exception:
                dip = None
        edge = None
        if self.m1:
            try:
                edge = ((self.m1.get(cat) or {}).get(str(int(price))) or {}).get("edge_p50")
                if edge is not None:
                    citations.append("M1 seqfloor recut edge_p50 (cell %d)" % int(price))
            except Exception:
                edge = None
        wake_risk = None
        if lifetime_vol is not None:
            wake_risk = "below_floor" if lifetime_vol < 2500 else "qualified"
            citations.append("M3 volume ledger (floor 2,500, EXECUTED as early-unlock)")
        if dip is None and edge is None:
            return {"opinion": "NO-OPINION", "cat": cat,
                    "missing": "G2: no fitted W1 volatility/edge anchor resolved for "
                               "this cell (M1/M2 rows absent)"}
        return {"opinion": "PRIOR", "cat": cat, "direction": direction,
                "confidence": round(conf, 3),
                "w1_shape": {"expected_dip_cents": dip, "cell_edge_p50": edge,
                             "wake_risk": wake_risk},
                "citations": citations}

    # ---- (b) tick posterior: EVERY print/book update alters the confidence ----
    def tick_posterior(self, prior, observations):
        """observations: sorted [(ts, kind, px)] with kind in ('print','mid').
        Returns full time series [(ts, confidence, n_eff)]. Prints weigh 1.0,
        tight-book mids 0.25 (prints are primary — observable-prices law)."""
        if prior.get("opinion") != "PRIOR":
            return []
        p0 = prior["confidence"]
        n_eff = 0.0
        series = []
        for ts, kind, px in observations:
            n_eff += 1.0 if kind == "print" else 0.25
            w = n_eff / (n_eff + K_PRIOR)
            conf = w * (px / 100.0) + (1 - w) * p0
            series.append((ts, round(conf, 4), round(n_eff, 2)))
        return series
