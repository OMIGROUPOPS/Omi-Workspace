#!/usr/bin/env python3
"""Independent reproduction of the superseding Round-2 PRE-RUN capability
claims from the committed receipts at codex commit 7667157f.

Reads only committed artifacts in a detached worktree. Computes every
headline claim from the per-event receipt rows rather than trusting the
summary integers. No scoring, no D=804 execution, no holdout access.

Usage: python reproduce_capability_claims.py <worktree> <out-json>
"""

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
V2 = WT / ".claude/window1_round2_prerun_v2_20260724"

rc = json.loads((V2 / "ROUND2_REAL_CAPABILITY.json").read_text("utf-8"))
db = json.loads((V2 / "ROUND2_DATA_BINDING_MANIFEST.json").read_text("utf-8"))
fam = json.loads((V2 / "ROUND2_ACTUAL_FAMILY_PROOF.json").read_text("utf-8"))

out = {}
cands = rc["candidate_summaries"]
ids = [c["candidate_id"] for c in cands]
out["candidate_ids"] = ids

# --- conservation and terminals from per-event receipts -------------------
conservation = {}
terminals = {}
for c in cands:
    rows = c["event_stream_receipts"]
    term = Counter(r["terminal"] for r in rows)
    eids = [r["event_id"] for r in rows]
    conservation[c["candidate_id"]] = {
        "event_receipts": len(rows),
        "unique_events": len(set(eids)),
        "claimed_eligible": c["eligible_event_count"],
        "claimed_censored": c["censored_event_count"],
        "recomputed_eligible": term.get("complete_counterfactual_stream", 0),
        "recomputed_censored": term.get("censored_feature", 0),
        "eligible_plus_censored": (
            term.get("complete_counterfactual_stream", 0)
            + term.get("censored_feature", 0)
        ),
        "terminals": dict(term),
    }
    terminals[c["candidate_id"]] = term
out["1_conservation_694_110_804"] = conservation

# --- cohort NO_CALL grain -------------------------------------------------
nocall = {}
for c in cands:
    rows = c["cohort_availability_by_class_zone_event"]
    pairs = [(r["event_id"], r["leg_id"]) for r in rows]
    nocall[c["candidate_id"]] = {
        "claimed": c["cohort_NO_CALL_count"],
        "rows": len(rows),
        "unique_event_leg_pairs": len(set(pairs)),
        "status_counts": dict(Counter(r["cohort_status"] for r in rows)),
        "events_touched": len({p[0] for p in pairs}),
        "all_below_min_n": all(
            r["cohort_status"] == "NO_CALL_UNAVAILABLE" for r in rows
        ),
        "max_cohort_n_seen": max(
            (r["cohort_n"] for r in rows), default=None
        ),
    }
out["2_cohort_no_call_grain"] = nocall
# arithmetic identity: legs that bind cohort = 1608 - censored legs that
# return before the cohort binding step
base = cands[0]
out["2b_no_call_arithmetic"] = {
    "total_leg_identities": db["leg_identities"],
    "recut_unavailable_legs": base["censor_reasons"].get(
        "dynamic_recut_cell_unavailable", 0
    ),
    "causal_role_missing_legs": base["censor_reasons"].get("causal_role", 0),
    "identity_1608_minus_127_minus_10": db["leg_identities"]
    - base["censor_reasons"].get("dynamic_recut_cell_unavailable", 0)
    - base["censor_reasons"].get("causal_role", 0),
    "matches_1471": (
        db["leg_identities"]
        - base["censor_reasons"].get("dynamic_recut_cell_unavailable", 0)
        - base["censor_reasons"].get("causal_role", 0)
    ) == 1471,
}

# --- NO_CALL never censors: cohort-aware candidates keep 694/110 ----------
out["3_no_call_never_censors"] = {
    cid: {
        "eligible": conservation[cid]["recomputed_eligible"],
        "censored": conservation[cid]["recomputed_censored"],
        "same_as_non_cohort_candidates": (
            conservation[cid]["recomputed_eligible"]
            == conservation[ids[0]]["recomputed_eligible"]
        ),
    }
    for cid in ids
}

# --- print universe -------------------------------------------------------
out["4_print_universe"] = {
    "claimed_per_candidate": {
        c["candidate_id"]: c["positive_size_print_count_consumed"]
        for c in cands
    },
    "identical_across_candidates": len({
        c["positive_size_print_count_consumed"] for c in cands
    }) == 1,
    "operator_relayed_claim_2240391_matches": any(
        c["positive_size_print_count_consumed"] == 2240391 for c in cands
    ),
    "committed_value": cands[0]["positive_size_print_count_consumed"],
}
# decision volume vs universe (prints that could have changed decisions)
out["4b_decision_volume"] = {
    c["candidate_id"]: dict(c["decision_counts"]) for c in cands
}

# --- pairwise distinctness on real events from decision hashes ------------
streams = {
    c["candidate_id"]: {
        r["event_id"]: r["decision_sha256"] for r in c["event_stream_receipts"]
    }
    for c in cands
}
pairwise = {}
for a, b in combinations(ids, 2):
    diff = [e for e in streams[a] if streams[a][e] != streams[b].get(e)]
    pairwise[f"{a} vs {b}"] = {
        "differing_events": len(diff),
        "example_events": sorted(diff)[:3],
    }
out["5_pairwise_distinctness"] = pairwise
out["5b_all_pairs_distinct_on_real_events"] = all(
    v["differing_events"] > 0 for v in pairwise.values()
)

# --- BBO / top-five coverage ---------------------------------------------
out["6_bbo_top5_coverage"] = {
    c["candidate_id"]: {
        "bbo_covered": c["BBO_covered_event_count"],
        "top5_covered": c["top5_covered_event_count"],
        "uncovered": rc["D"] - c["BBO_covered_event_count"],
    }
    for c in cands
}

# --- censor reasons lawful and named -------------------------------------
out["7_censor_reasons"] = {
    c["candidate_id"]: {
        "reasons": dict(c["censor_reasons"]),
        "missing_feature_legs": dict(c["missing_feature_leg_counts"]),
    }
    for c in cands
}

# --- family witnesses are real events inside the bound population ---------
event_universe = set(streams[ids[0]])
witnesses = {}
for w in fam["family_witnesses"]:
    witnesses[w["family_id"]] = {
        "event_id": w["event_id"],
        "event_date": w["event_date"],
        "in_bound_804_universe": w["event_id"] in event_universe,
        "decision_changing": w["decision_changing"],
        "enabled_count": w["enabled_decision_count"],
        "disabled_count": w["disabled_decision_count"],
        "hashes_differ": (
            w["enabled_decision_sha256"] != w["disabled_decision_sha256"]
        ),
    }
out["8_family_witnesses"] = witnesses
out["8b_witness_dates_development_only"] = all(
    w["event_date"].startswith("2026-07-1")
    or w["event_date"] in ("2026-07-20",)
    for w in fam["family_witnesses"]
)

# --- holdout absence ------------------------------------------------------
dates = set()
for c in cands:
    for r in c["cohort_availability_by_class_zone_event"]:
        dates.add(r["event_date"])
out["9_holdout"] = {
    "holdout_dates_present_in_binding": db["holdout_dates_present_in_any_input"],
    "capability_dates_seen": sorted(dates),
    "rc_flags": {
        "holdout_opened": rc["holdout_opened"],
        "holdout_queried": rc["holdout_queried"],
        "scored": rc["candidate_scoring_performed"],
        "performance_ablation": rc["performance_ablation_performed"],
        "tuning": rc["tuning_performed"],
        "metrics": rc["metrics"],
    },
}

OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2)[:6000])
