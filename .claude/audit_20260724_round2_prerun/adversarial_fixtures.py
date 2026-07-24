#!/usr/bin/env python3
"""Independent adversarial fixture campaign against the frozen Round-2
Window-1 instrument at codex commit 6eecbd1d.

Every fixture here was authored by the independent auditor; none reuses the
Codex-supplied capability fixtures. The instrument module is imported
read-only from a detached worktree pinned at the PRE-RUN commit. No event of
the D=804 population is loaded and no scoring is performed.

Usage: python adversarial_fixtures.py <detached-worktree-path> <output-json>
"""

import copy
import json
import sys
from pathlib import Path

WORKTREE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(WORKTREE / "arb-executor/analysis"))

import window1_round2_instrument as instr  # noqa: E402

REPO = WORKTREE
SURFACES = instr.load_surfaces(REPO)
SPEC = instr.load_candidate_spec(REPO)

GUARD = {
    "guard_id": "te-calibration-central-93pct-asymmetric-v1",
    "positive_guard_seconds": 900.0,
    "negative_guard_seconds": 600.0,
}
LEFT = 1_000_000.0
CUTOFF = LEFT + 8 * 3600.0  # 8h window


def book(ts, bid, ask, bid_size=200.0, ask_size=100.0, own=None, levels=5):
    bids = [[bid - i, bid_size] for i in range(levels)]
    asks_ = [[ask + i, ask_size] for i in range(levels)]
    row = {"kind": "book", "ts": ts, "bids": bids, "asks": asks_}
    if own:
        row["own_bid_size_by_price"] = dict(own)
    return row


def pr(ts, price, size=5.0, side="no", trade_id=None, own=False):
    row = {
        "kind": "print", "ts": ts, "price": price, "size": size,
        "taker_side": side, "trade_id": trade_id or f"T{ts}",
    }
    if own:
        row["own_order_fingerprint"] = True
    return row


def leg(leg_id, ticker, role, observations, avail=None):
    availability = {
        "true_prints": True, "top5": True, "own_order_fingerprints": True,
    }
    if avail:
        availability.update(avail)
    return {
        "leg_id": leg_id, "ticker": ticker, "role": role,
        "feature_availability": availability,
        "observations": observations,
    }


def event(legs, date="2026-07-15", source="quantized_late_detection_proxy",
          cutoff=CUTOFF, guard=GUARD, category="ATP_MAIN"):
    return {
        "event_id": "AUDIT-FIX",
        "event_date": date,
        "category": category,
        "left_ts": LEFT,
        "strict_positive_cutoff_ts": cutoff,
        "start_source_class": source,
        "start_guard": guard,
        "legs": legs,
    }


def run(ev, candidate, ablations=()):
    return instr.run_event(
        REPO, ev, candidate, ablations=ablations, surfaces=SURFACES
    )


def stream(result, leg_id):
    return result["leg_streams"][leg_id]


def sig(rows, drop=("queue_ahead",)):
    out = []
    for r in rows:
        r = {k: v for k, v in r.items() if k not in drop}
        out.append(json.dumps(r, sort_keys=True))
    return out


findings = {}


# ---------------------------------------------------------------- fixtures
# Divot trigger helper: 3 prior prints near median M, then a print >=2c
# below M while best ask holds within 1c of M.
def divot_obs(anchor, t0, prices_extra=()):
    rows = [
        book(t0, anchor, anchor + 1),
        pr(t0 + 10, anchor, trade_id=f"A{t0}"),
        pr(t0 + 20, anchor, trade_id=f"B{t0}"),
        pr(t0 + 30, anchor, trade_id=f"C{t0}"),
        pr(t0 + 40, anchor - 3, trade_id=f"D{t0}"),  # divot print
    ]
    rows += list(prices_extra)
    return rows


# Anchor 57 in ATP_MAIN: edge_p50=1, t_deep_p50=-144min
# Anchor 44 in ATP_MAIN: edge_p50=2, t_deep_p50=-252min
A_ANCHOR, B_ANCHOR = 57, 44
A_ELIG = CUTOFF - 144 * 60
B_ELIG = CUTOFF - 252 * 60

base_a = [book(LEFT + 60, A_ANCHOR, A_ANCHOR + 2)] + divot_obs(
    A_ANCHOR, A_ELIG + 60
)
base_b = [book(LEFT + 60, B_ANCHOR, B_ANCHOR + 2)] + divot_obs(
    B_ANCHOR, B_ELIG + 60
)
BASE = event([
    leg("L1", "TKR-A", "favorite", base_a),
    leg("L2", "TKR-B", "underdog", base_b),
])

CAND = "r2_async_pair__park_join__hold"

# 1+2. per-leg timing asymmetry and cross-leg invariance -------------------
res_base = run(BASE, CAND)
va = copy.deepcopy(BASE)
va["legs"][0]["observations"][0] = book(LEFT + 60, 68, 70)  # A: t_deep -480
res_va = run(va, CAND)
vb = copy.deepcopy(BASE)
vb["legs"][1]["observations"][0] = book(LEFT + 60, 68, 70)
res_vb = run(vb, CAND)

elig = lambda r, lid: [  # noqa: E731
    a["eligible_ts"] for a in stream(r, lid) if a["action"] == "macro_bind"
]
findings["1_legA_timing_independent"] = {
    "base_eligible_A": elig(res_base, "L1"),
    "variant_eligible_A": elig(res_va, "L1"),
    "A_changed": sig(stream(res_base, "L1")) != sig(stream(res_va, "L1")),
    "B_invariant": sig(stream(res_base, "L2")) == sig(stream(res_va, "L2")),
}
findings["2_legB_timing_independent"] = {
    "B_changed": sig(stream(res_base, "L2")) != sig(stream(res_vb, "L2")),
    "A_invariant": sig(stream(res_base, "L1")) == sig(stream(res_vb, "L1")),
}
findings["1b_eligibility_is_cutoff_anchored"] = {
    "expected_A": A_ELIG, "observed_A": elig(res_base, "L1"),
    "note": "eligible_ts = cutoff + t_deep_p50*60 (realized-start anchored)",
}

# 3. posture independence --------------------------------------------------
res_tp = run(BASE, "r2_async_pair__touch_park__hold")
pa = [a for a in stream(res_base, "L1") if a["action"] in ("place", "reprice")]
pt = [a for a in stream(res_tp, "L1") if a["action"] in ("place", "reprice")]
findings["3_posture_changes_decision"] = {
    "park_join_L1_orders": [(a["price_cents"], a["posture"]) for a in pa],
    "touch_park_L1_orders": [(a["price_cents"], a["posture"]) for a in pt],
    "decision_differs": sig(pa) != sig(pt),
}

# 4. first-fill sibling response ------------------------------------------
# Leg A gets divot + fill prints below its resting price; sibling must react
# only via a timestamped bias, on its own book.
fill_a = base_a + [
    pr(A_ELIG + 200, A_ANCHOR - 10, size=6.0, trade_id="FILL1"),
]
FILLEV = event([
    leg("L1", "TKR-A", "favorite", fill_a),
    leg("L2", "TKR-B", "underdog", base_b),
])
res_hold = run(FILLEV, "r2_async_pair__park_join__hold")
res_reaim = run(FILLEV, "r2_async_pair__park_join__reaim")


def all_acts(r):
    return [a for lid in ("L1", "L2") for a in stream(r, lid)]


# NOTE: in this fixture leg L2 (earlier eligibility) fills FIRST, so the
# sibling response lands on L1. The decision is timestamped at the fill,
# but its execution defers to L1's OWN eligibility clock and divot trigger.
sib_hold = [a for a in all_acts(res_hold) if a["action"] == "sibling_hold"]
sib_re = [a for a in all_acts(res_reaim)
          if a["action"] == "sibling_reaim_decision"]
orders = lambda r, lid: [  # noqa: E731
    (a["ts"], a.get("price_cents")) for a in stream(r, lid)
    if a["action"] in ("place", "reprice")
]
findings["4_sibling_response"] = {
    "first_fill_observed": any(
        a["action"] == "fill_observed" and a.get("complete")
        for a in all_acts(res_hold)
    ),
    "hold_emits_sibling_hold": bool(sib_hold),
    "reaim_emits_decision": bool(sib_re),
    "reaim_bias_cents": [a.get("reaim_cents") for a in sib_re],
    "sibling_L1_orders_hold": orders(res_hold, "L1"),
    "sibling_L1_orders_reaim": orders(res_reaim, "L1"),
    "reaim_changed_sibling_price_by_1c_on_own_clock": (
        orders(res_hold, "L1") != orders(res_reaim, "L1")
        and all(
            h[0] == r_[0] and r_[1] - h[1] == 1
            for h, r_ in zip(
                orders(res_hold, "L1"), orders(res_reaim, "L1")
            )
        )
    ),
}

# 5. missing feature -> censor --------------------------------------------
miss = copy.deepcopy(BASE)
miss["legs"][0]["feature_availability"]["true_prints"] = False
res_miss = run(miss, CAND)
findings["5_missing_feature_censored"] = {
    "event_terminal": res_miss["event_terminal"],
    "L1_terminal": stream(res_miss, "L1")[-1]["reason"],
    "L1_placed_any_order": any(
        a["action"] == "place" for a in stream(res_miss, "L1")
    ),
    "censor_action_named": any(
        a["action"] == "feature_censor" for a in stream(res_miss, "L1")
    ),
}

# 6. schedule-only cannot be positive -------------------------------------
sched_ok = event(
    [leg("L1", "TKR-A", "favorite", base_a),
     leg("L2", "TKR-B", "underdog", base_b)],
    source="schedule_only", cutoff=None, guard=None,
)
res_sched = run(sched_ok, CAND)
try:
    bad = event(
        [leg("L1", "TKR-A", "favorite", base_a),
         leg("L2", "TKR-B", "underdog", base_b)],
        source="schedule_only", cutoff=CUTOFF, guard=GUARD,
    )
    run(bad, CAND)
    sched_refused = False
except instr.InstrumentError:
    sched_refused = True
findings["6_schedule_only"] = {
    "no_orders_without_cutoff": not any(
        a["action"] == "place"
        for lid in ("L1", "L2") for a in stream(res_sched, lid)
    ),
    "terminal": res_sched["event_terminal"],
    "positive_cutoff_refused": sched_refused,
}

# 7. T8/T6 recognition isolation (own fixture, causal_steer profile) ------
rec_ev = event([
    leg("L1", "TKR-A", "favorite",
        [book(LEFT + 60, 84, 86)] + divot_obs(84, LEFT + 3000)
        + divot_obs(84, CUTOFF - 3600)),
    leg("L2", "TKR-B", "underdog",
        [book(LEFT + 60, 44, 46)] + divot_obs(44, LEFT + 3200)
        + divot_obs(44, CUTOFF - 3600)),
])
CS = "r2_causal_steer__park_join__hold"
res_r1 = run(rec_ev, CS)
mutated = copy.deepcopy(SURFACES.drift)
rec_map = mutated.setdefault("recognition", {})
for cat_key in list(rec_map) or ["ATP_MAIN|h6"]:
    pass
rec_map.setdefault("ATP_MAIN|h6", {})
for bucket in ("a95|flat|d0", "a50|flat|d0", "a95|flat|d3", "a50|flat|d3"):
    rec_map["ATP_MAIN|h6"][bucket] = {"top": "AM_B1", "purity": 0.99}
S2 = instr.SurfaceBundle(
    band_map=SURFACES.band_map, divot=SURFACES.divot, drift=mutated,
    recut=SURFACES.recut, orientation=SURFACES.orientation,
    cohort=SURFACES.cohort,
)
policy = instr.candidate_policy(SPEC, CS)
res_r2 = instr.CausalInstrument(S2, policy).run(rec_ev)
T6 = LEFT + 7200


def split_actions(r):
    pre, post = [], []
    for lid in ("L1", "L2"):
        for a in stream(r, lid):
            (pre if float(a["ts"]) < T6 else post).append(a)
    return sig(pre), sig(post)


pre1, post1 = split_actions(res_r1)
pre2, post2 = split_actions(res_r2)
findings["7_t8_t6_isolation_own_fixture"] = {
    "pre_T6_identical": pre1 == pre2,
    "post_T6_differ": post1 != post2,
}

# 8. flow hygiene: zero-size and own prints -------------------------------
# 8a. zero-size prints must not confirm flow: ATP_CHALL needs 16 prints/30m.
zs_obs = [book(LEFT + 60, 44, 46)]
t0 = CUTOFF - 3600
zs_obs.append(book(t0, 44, 46))
for i in range(16):
    zs_obs.append(pr(t0 + 10 + i, 44, size=0.0, trade_id=f"Z{i}"))
zs_ev = event(
    [leg("L1", "TKR-A", "favorite", zs_obs),
     leg("L2", "TKR-B", "underdog",
         [book(LEFT + 60, 44, 46)] + divot_obs(44, t0))],
    category="ATP_CHALL",
)
res_zs = run(zs_ev, "r2_async_pair__touch_park__hold")  # L1 touch: flow-gated
findings["8a_zero_size_flow"] = {
    "L1_placed_on_zero_size_flow": any(
        a["action"] == "place" for a in stream(res_zs, "L1")
    ),
}
# 8b. own fingerprint print at fillable price: no fill, no flow credit.
own_obs = base_a + [
    pr(A_ELIG + 200, A_ANCHOR - 10, size=6.0, trade_id="OWN1", own=True),
]
own_ev = event([
    leg("L1", "TKR-A", "favorite", own_obs),
    leg("L2", "TKR-B", "underdog", base_b),
])
res_own = run(own_ev, CAND)
findings["8b_own_print_never_fills"] = {
    "excluded_action_present": any(
        a["action"] == "contributed_volume_excluded"
        for a in stream(res_own, "L1")
    ),
    "no_fill_from_own_print": not any(
        a["action"] == "fill_observed" for a in stream(res_own, "L1")
    ),
}
# 8c. ADVERSARIAL: walk chain, genuine vs zero-size second link.
# r2_full_os includes cohort_steering, which censors every development
# category under the frozen cohort surface (see finding 14); the
# predeclared without_cohort_steering ablation lawfully isolates the walk.
def walk_ev_make(zero_second):
    la = [book(LEFT + 60, A_ANCHOR, A_ANCHOR + 4)] + divot_obs(
        A_ANCHOR, A_ELIG + 60
    ) + [
        book(A_ELIG + 150, A_ANCHOR, A_ANCHOR + 4),
        pr(A_ELIG + 200, A_ANCHOR - 1, size=5.0, trade_id="C1"),
        pr(A_ELIG + 210, A_ANCHOR,
           size=(0.0 if zero_second else 5.0), trade_id="C2"),
    ]
    return event([
        leg("L1", "TKR-A", "favorite", la),
        leg("L2", "TKR-B", "underdog", [book(LEFT + 60, 44, 46)]),
    ])


walk_results = {}
for zs_flag, label in ((False, "genuine_chain"), (True, "zero_size_link")):
    res_w = run(walk_ev_make(zs_flag), "r2_full_os__walk_park__hold",
                ablations=("without_cohort_steering",))
    moves = [
        a for a in stream(res_w, "L1")
        if a["reason"] == "verified_nonself_chain_exact_one_cent"
    ]
    walk_results[label] = [(a["ts"] - LEFT, a["price_cents"]) for a in moves]
findings["8c_walk_chain"] = {
    "genuine_chain_advances_exactly_1c": walk_results["genuine_chain"],
    "zero_size_link_also_advances_DEFECT": walk_results["zero_size_link"],
    "spec_violated": bool(walk_results["zero_size_link"]),
}
# 8d. ADVERSARIAL: zero-size print as the divot print itself.
zd_obs = [book(LEFT + 60, 44, 46)]
zt = B_ELIG + 60
zd_obs += [
    book(zt, 44, 46),
    pr(zt + 10, 44, trade_id="P1"), pr(zt + 20, 44, trade_id="P2"),
    pr(zt + 30, 44, trade_id="P3"),
    pr(zt + 40, 41, size=0.0, trade_id="ZDIV"),  # zero-size divot print
]
zd_ev = event([
    leg("L1", "TKR-A", "favorite", zd_obs),
    leg("L2", "TKR-B", "underdog", base_b),
])
res_zd = run(zd_ev, CAND)
findings["8d_zero_size_divot_signal"] = {
    "micro_divot_emitted_from_zero_size": any(
        a["action"] == "micro_divot" and a["print_price_cents"] == 41
        for a in stream(res_zd, "L1")
    ),
}

# 9. top-five pressure: causal and coverage-gated -------------------------
# (cohort ablated for the same structural reason as fixture 8c)
def p_ev_make(ask_size):
    la = [book(LEFT + 60, A_ANCHOR, A_ANCHOR + 2)] + [
        book(A_ELIG + 60, A_ANCHOR, A_ANCHOR + 2,
             bid_size=10.0, ask_size=ask_size),
        pr(A_ELIG + 70, A_ANCHOR, trade_id="Q1"),
        pr(A_ELIG + 80, A_ANCHOR, trade_id="Q2"),
        pr(A_ELIG + 90, A_ANCHOR, trade_id="Q3"),
        pr(A_ELIG + 100, A_ANCHOR - 3, trade_id="Q4"),
    ]
    return event([
        leg("L1", "TKR-A", "favorite", la),
        leg("L2", "TKR-B", "underdog", [book(LEFT + 60, 44, 46)]),
    ])


res_p = run(p_ev_make(30.0), "r2_causal_steer__park_join__hold",
            ablations=("without_cohort_steering",))
res_pf = run(p_ev_make(5.0), "r2_causal_steer__park_join__hold",
             ablations=("without_cohort_steering",))
d1 = [(a.get("price_cents"), a.get("effective_depth_cents"))
      for a in stream(res_p, "L1") if a["action"] in ("place", "reprice")]
d2 = [(a.get("price_cents"), a.get("effective_depth_cents"))
      for a in stream(res_pf, "L1") if a["action"] in ("place", "reprice")]
p_miss = p_ev_make(30.0)
p_miss["legs"][0]["feature_availability"]["top5"] = False
res_pm = run(p_miss, "r2_causal_steer__park_join__hold",
             ablations=("without_cohort_steering",))
findings["9_top5_pressure"] = {
    "ask_heavy_orders_price_depth": d1,
    "balanced_orders_price_depth": d2,
    "pressure_added_exactly_1c_depth": d1 != d2,
    "missing_top5_censored": res_pm["event_terminal"] == "censored_feature",
}

# 11. per-leg recut on causal book-cell change ----------------------------
rc_obs = [book(LEFT + 60, A_ANCHOR, A_ANCHOR + 2)] + divot_obs(
    A_ANCHOR, A_ELIG + 60
) + [book(A_ELIG + 300, 44, 46)]
rc_ev = event([
    leg("L1", "TKR-A", "favorite", rc_obs),
    leg("L2", "TKR-B", "underdog", [book(LEFT + 60, 44, 46)]),
])
res_rc = run(rc_ev, CAND)
findings["11_per_leg_recut"] = {
    "L1_actions": [
        (a["ts"] - LEFT, a["action"], a.get("price_cents"),
         a.get("recut_depth_cents"))
        for a in stream(res_rc, "L1")
        if a["action"] in ("pair_recut", "place", "reprice", "cancel")
    ],
    "L2_untouched": [a["action"] for a in stream(res_rc, "L2")]
    == ["leg_open", "macro_bind", "terminal"],
}

# 14. STRUCTURAL: frozen cohort surface vs development categories ----------
from collections import Counter  # noqa: E402

cohort_rows = SURFACES.cohort.get("rows") or []
zone_counts: dict = {}
for cat in ("ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"):
    counts = Counter(
        int(float(r.get("px") or 0) // 25)
        for r in cohort_rows
        if r.get("cat") == cat and r.get("cell_edge") is not None
    )
    zone_counts[cat] = dict(counts)
min_n = int(SPEC["common_parameters"]["cohort_minimum_n"])
findings["14_cohort_structurally_dead"] = {
    "cohort_rows_with_cell_edge_by_dev_category_zone": zone_counts,
    "frozen_cohort_minimum_n": min_n,
    "any_dev_zone_reaches_min_n": any(
        v >= min_n for cat in zone_counts for v in zone_counts[cat].values()
    ),
    "consequence": (
        "every leg of every D=804 event is feature-censored at birth for "
        "the six cohort_steering candidates (r2_causal_steer x2, "
        "r2_full_os x4); capability gate passed only on synthetic surfaces"
    ),
}

# 10. unavailable machinery is absent from code ---------------------------
src = (WORKTREE / "arb-executor/analysis/window1_round2_instrument.py").read_text(
    encoding="utf-8"
)
findings["10_exclusions_absent_from_code"] = {
    name: (name not in src.lower())
    for name in ("pinnacle", "aim_v2", "shape_aim", "full_depth",
                 "pair_policies_sealed", "riser")
}

# 12. holdout + non-development refusal -----------------------------------
refusals = {}
for date in ("2026-07-24", "2026-07-25", "2026-07-26", "2026-07-22",
             "2026-07-11"):
    try:
        run(event(
            [leg("L1", "TKR-A", "favorite", base_a),
             leg("L2", "TKR-B", "underdog", base_b)], date=date,
        ), CAND)
        refusals[date] = "ACCEPTED (VIOLATION)"
    except instr.InstrumentError as err:
        refusals[date] = f"refused: {err}"
findings["12_holdout_and_date_fence"] = refusals

# 13. complete two-leg streams --------------------------------------------
findings["13_complete_streams"] = {
    "both_legs_open_and_terminal": all(
        stream(res_base, lid)[0]["action"] == "leg_open"
        and stream(res_base, lid)[-1]["action"] == "terminal"
        for lid in ("L1", "L2")
    ),
    "orders_generated_not_replayed": any(
        a["action"] == "place" for lid in ("L1", "L2")
        for a in stream(res_base, lid)
    ),
    "scored_flag": res_base["scored"],
    "metrics_field": res_base["metrics"],
}

# zero-length window --------------------------------------------------------
zl = event(
    [leg("L1", "TKR-A", "favorite", base_a),
     leg("L2", "TKR-B", "underdog", base_b)],
    cutoff=LEFT - 60,
)
res_zl = run(zl, CAND)
findings["extra_zero_length_class"] = {
    "terminal": res_zl["event_terminal"],
}

OUT.write_text(json.dumps(findings, indent=2, default=str) + "\n",
               encoding="utf-8")
print(json.dumps(findings, indent=2, default=str))
