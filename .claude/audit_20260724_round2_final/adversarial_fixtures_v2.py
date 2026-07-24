#!/usr/bin/env python3
"""Independent adversarial fixtures against the superseding Round-2
instrument (codex 7667157f). Auditor-authored; none reuse Codex fixtures.
No D=804 event, no scoring, no holdout.

Usage: python adversarial_fixtures_v2.py <worktree> <out-json>
"""

import copy
import json
import sys
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(WT / "arb-executor/analysis"))

import window1_round2_instrument as instr  # noqa: E402

REPO = WT
SURFACES = instr.load_surfaces(REPO)

ANCHOR = 1_000_000.0          # policy_anchor_ts (exchange schedule)
LEFT = ANCHOR - 8 * 3600.0    # policy_left_ts
OBSERVED = LEFT - 600.0       # anchor observed before window

findings = {}


def book(ts, bid, ask, bid_size=200.0, ask_size=100.0, own=None):
    row = {
        "kind": "book", "ts": ts,
        "bids": [[bid - i, bid_size] for i in range(5)],
        "asks": [[ask + i, ask_size] for i in range(5)],
    }
    if own:
        row["own_bid_size_by_price"] = dict(own)
    return row


def pr(ts, price, size=5.0, side="no", tid=None, **overrides):
    row = {
        "kind": "print", "ts": ts, "price": price, "size": size,
        "taker_side": side, "trade_id": tid or f"T{ts}",
        "size_verified": True,
        "source": "normalized_public_true_print",
    }
    row.update(overrides)
    return row


def leg(leg_id, ticker, role, observations, avail=None):
    availability = {
        "causal_role": True, "true_prints": True, "top5": True,
        "own_order_fingerprints": True,
    }
    if avail:
        availability.update(avail)
    return {
        "leg_id": leg_id, "ticker": ticker, "role": role,
        "feature_availability": availability,
        "observations": observations,
    }


def event(legs, date="2026-07-15", category="ATP_MAIN", corridor=0.0,
          extra=None):
    ev = {
        "event_id": "AUDIT-V2-FIX",
        "event_date": date,
        "category": category,
        "policy_anchor_ts": ANCHOR,
        "policy_anchor_observed_at_ts": OBSERVED,
        "policy_anchor_source": "contemporaneous_exchange_schedule",
        "policy_left_ts": LEFT,
        "policy_decision_horizon_ts": ANCHOR + corridor,
        "policy_corridor_seconds_after_anchor": corridor,
        "legs": legs,
    }
    if extra:
        ev.update(extra)
    return ev


def run(ev, candidate, ablations=()):
    return instr.run_event(
        REPO, ev, candidate, ablations=ablations, surfaces=SURFACES
    )


def stream(result, leg_id):
    return result["leg_streams"][leg_id]


# ATP_MAIN anchor 57: recut edge 1, t_deep -144min => eligible ANCHOR-8640
A, B = 57, 44
AE = ANCHOR - 144 * 60
BE = ANCHOR - 252 * 60


def divot_obs(anchor_px, t0):
    return [
        book(t0, anchor_px, anchor_px + 2),
        pr(t0 + 10, anchor_px, tid=f"A{t0}"),
        pr(t0 + 20, anchor_px, tid=f"B{t0}"),
        pr(t0 + 30, anchor_px, tid=f"C{t0}"),
        pr(t0 + 40, anchor_px - 3, tid=f"D{t0}"),
    ]


base_a = [book(LEFT + 60, A, A + 2)] + divot_obs(A, AE + 60)
base_b = [book(LEFT + 60, B, B + 2)] + divot_obs(B, BE + 60)
BASE = event([
    leg("L1", "TKR-A", "favorite", base_a),
    leg("L2", "TKR-B", "underdog", base_b),
])
CAND = "r2_async_pair__park_join__hold"
STEER = "r2_causal_steer__park_join__hold"

# A. forbidden evaluation-truth fields hard-refused --------------------------
refused = {}
for field in sorted(instr.FORBIDDEN_POLICY_CLOCK_FIELDS):
    ev = copy.deepcopy(BASE)
    ev[field] = 123456.0
    try:
        run(ev, CAND)
        refused[field] = "ACCEPTED (VIOLATION)"
    except instr.InstrumentError as err:
        refused[field] = "refused"
findings["A_forbidden_fields_refused"] = {
    "all_refused": all(v == "refused" for v in refused.values()),
    "fields": refused,
}

# B. corridor/anchor declaration integrity ----------------------------------
bad_cases = {}
ev = copy.deepcopy(BASE)
ev["policy_decision_horizon_ts"] = ANCHOR + 60  # corridor says 0
try:
    run(ev, CAND)
    bad_cases["corridor_mismatch"] = "ACCEPTED (VIOLATION)"
except instr.InstrumentError:
    bad_cases["corridor_mismatch"] = "refused"
ev = copy.deepcopy(BASE)
ev["policy_anchor_observed_at_ts"] = ANCHOR + 10  # observed after horizon
try:
    run(ev, CAND)
    bad_cases["anchor_observed_after_horizon"] = "ACCEPTED (VIOLATION)"
except instr.InstrumentError:
    bad_cases["anchor_observed_after_horizon"] = "refused"
findings["B_clock_declarations"] = bad_cases

# C. realized-start invariance + evaluator divergence -----------------------
res1 = run(BASE, CAND)
res2 = run(copy.deepcopy(BASE), CAND)
early = instr.evaluate_order_stream(res1, {
    "start_source_class": "official_exact",
    "evaluation_real_start_ts": LEFT + 1,  # before ANY possible fill
    "start_guard": {"guard_id": "official-point-strict-60s-v1"},
})
late = instr.evaluate_order_stream(res1, {
    "start_source_class": "official_exact",
    "evaluation_real_start_ts": ANCHOR + 3600,
    "start_guard": {"guard_id": "official-point-strict-60s-v1"},
})
findings["C_policy_evaluation_separation"] = {
    "policy_stream_deterministic_identical": (
        res1["stream_sha256"] == res2["stream_sha256"]
    ),
    "policy_result_carries_no_truth": res1["evaluation_truth_present"] is False,
    "early_classification": early["classification"],
    "late_classification": late["classification"],
    "classifications_differ": early["classification"] != late["classification"],
    "same_policy_stream_hash_in_both": (
        early["policy_stream_sha256"] == late["policy_stream_sha256"]
        == res1["stream_sha256"]
    ),
}

# D. schedule-only cannot prove positive ------------------------------------
sched_censored = instr.evaluate_order_stream(res1, {
    "start_source_class": "schedule_only",
    "evaluation_real_start_ts": None,
    "start_guard": None,
})
try:
    instr.evaluate_order_stream(res1, {
        "start_source_class": "schedule_only",
        "evaluation_real_start_ts": ANCHOR,
        "start_guard": {"guard_id": "x"},
    })
    sched_positive = "ACCEPTED (VIOLATION)"
except instr.InstrumentError:
    sched_positive = "refused"
findings["D_schedule_only"] = {
    "classification": sched_censored["classification"],
    "positive_window1_proved": sched_censored["positive_window1_proved"],
    "realized_start_on_schedule_only": sched_positive,
}

# E. evidence admission gate ------------------------------------------------
bad_rows = {
    "size_zero": pr(AE + 100, A - 3, size=0.0, tid="BZ1"),
    "size_none": pr(AE + 100, A - 3, size=None, tid="BZ2"),
    "size_malformed": pr(AE + 100, A - 3, size="x", tid="BZ3"),
    "synthetic_transition": pr(AE + 100, A - 3, tid="BZ4",
                               synthetic_transition=True),
    "unverified_size": pr(AE + 100, A - 3, tid="BZ5", size_verified=False),
    "missing_identity": pr(AE + 100, A - 3, trade_id="", receipt_id=""),
    "unproved_source": pr(AE + 100, A - 3, tid="BZ6",
                          source="mystery_feed"),
}
gate = {}
for name, bad in bad_rows.items():
    obs = [
        book(LEFT + 60, A, A + 2),
        book(AE + 50, A, A + 2),
        pr(AE + 60, A, tid="G1"), pr(AE + 70, A, tid="G2"),
        pr(AE + 80, A, tid="G3"),
        bad,  # would-be divot trigger
    ]
    ev = event([
        leg("L1", "TKR-A", "favorite", obs),
        leg("L2", "TKR-B", "underdog", [book(LEFT + 60, B, B + 2)]),
    ])
    r = run(ev, CAND)
    acts = [a["action"] for a in stream(r, "L1")]
    gate[name] = {
        "print_excluded": "print_excluded" in acts,
        "micro_divot_fired": "micro_divot" in acts,
        "order_placed": "place" in acts,
        "fill_observed": "fill_observed" in acts,
    }
# control: the same trigger with a lawful print MUST fire the divot
ctrl_obs = [
    book(LEFT + 60, A, A + 2),
    book(AE + 50, A, A + 2),
    pr(AE + 60, A, tid="G1"), pr(AE + 70, A, tid="G2"),
    pr(AE + 80, A, tid="G3"),
    pr(AE + 100, A - 3, tid="GOOD"),
]
ctrl = run(event([
    leg("L1", "TKR-A", "favorite", ctrl_obs),
    leg("L2", "TKR-B", "underdog", [book(LEFT + 60, B, B + 2)]),
]), CAND)
findings["E_evidence_admission_gate"] = {
    "control_divot_fires_on_lawful_print": any(
        a["action"] == "micro_divot" for a in stream(ctrl, "L1")
    ),
    "bad_rows": gate,
    "no_bad_row_triggers_anything": all(
        v["print_excluded"] and not v["micro_divot_fired"]
        and not v["order_placed"] and not v["fill_observed"]
        for v in gate.values()
    ),
}

# F. zero-size in walk chain (F2 regression) --------------------------------
def walk_ev(zero_second):
    la = [book(LEFT + 60, A, A + 4)] + divot_obs(A, AE + 60) + [
        book(AE + 150, A, A + 4),
        pr(AE + 200, A - 1, tid="C1"),
        pr(AE + 210, A, tid="C2",
           **({"size": 0.0} if zero_second else {})),
    ]
    return event([
        leg("L1", "TKR-A", "favorite", la),
        leg("L2", "TKR-B", "underdog", [book(LEFT + 60, B, B + 2)]),
    ])


walk_out = {}
for zs, label in ((False, "genuine"), (True, "zero_size_link")):
    r = run(walk_ev(zs), "r2_full_os__walk_park__hold")
    walk_out[label] = [
        (a["ts"] - LEFT, a["price_cents"]) for a in stream(r, "L1")
        if a["reason"] == "verified_nonself_chain_exact_one_cent"
    ]
findings["F_walk_chain_zero_size"] = {
    "genuine_chain_advances": bool(walk_out["genuine"]),
    "zero_size_link_advances": bool(walk_out["zero_size_link"]),
    "defect_fixed": bool(walk_out["genuine"])
    and not bool(walk_out["zero_size_link"]),
}

# G. cohort NO_CALL continues underlying policy on REAL frozen surfaces ------
res_steer = run(BASE, STEER)
l1 = stream(res_steer, "L1")
findings["G_cohort_no_call_continuation"] = {
    "no_call_emitted": any(a["action"] == "cohort_no_call" for a in l1),
    "no_call_flags_continuation": any(
        a["action"] == "cohort_no_call"
        and a.get("underlying_policy_continues") is True for a in l1
    ),
    "feature_censor_absent": not any(
        a["action"] == "feature_censor" for a in l1
    ),
    "order_still_placed": any(a["action"] == "place" for a in l1),
    "terminal": res_steer["event_terminal"],
}

# H. own prints excluded; own book volume subtracted ------------------------
own_obs = base_a + [
    pr(AE + 200, A - 10, size=6.0, tid="OWN1", own_order_fingerprint=True),
]
res_own = run(event([
    leg("L1", "TKR-A", "favorite", own_obs),
    leg("L2", "TKR-B", "underdog", base_b),
]), CAND)
findings["H_own_volume"] = {
    "own_print_logged_excluded": any(
        a["action"] == "contributed_volume_excluded"
        for a in stream(res_own, "L1")
    ),
    "own_print_never_fills": not any(
        a["action"] == "fill_observed" for a in stream(res_own, "L1")
    ),
}

# I. holdout and non-development refusal ------------------------------------
refuse = {}
for date in ("2026-07-24", "2026-07-25", "2026-07-26", "2026-07-23",
             "2026-07-11"):
    try:
        run(event([
            leg("L1", "TKR-A", "favorite", base_a),
            leg("L2", "TKR-B", "underdog", base_b),
        ], date=date), CAND)
        refuse[date] = "ACCEPTED (VIOLATION)"
    except instr.InstrumentError:
        refuse[date] = "refused"
findings["I_holdout_date_fence"] = refuse

# J. eligibility is schedule-anchored (policy clock only) -------------------
elig = [
    a.get("eligible_ts") for a in stream(res1, "L1")
    if a["action"] == "macro_bind"
]
findings["J_eligibility_schedule_anchored"] = {
    "expected_anchor_minus_144m": AE,
    "observed": elig,
    "matches": elig == [AE],
}

OUT.write_text(json.dumps(findings, indent=2, default=str) + "\n",
               encoding="utf-8")
print(json.dumps(findings, indent=2, default=str))
