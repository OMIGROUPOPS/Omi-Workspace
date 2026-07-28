"""PHASE-1 BLIND reconstruction for the T2 scoring-package audit.

Sources: ONLY the raw frozen T2 PRE-RUN ledgers at 87ac9382 (independently
audited), the guarded private inputs, and Git objects. No V1/V2 package
artifact, receipt, manifest, schema, contract, or report is opened.
Auditor-authored; no imports from any package builder/correction/freeze/runner.
"""
import gzip
import io
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = r"C:\Users\omigr\OMI-Workspace"
T2PKG = "87ac9382:.claude/window1_t2_causal_divot_prerun_20260727/"
PRIV = Path(r"C:\Users\omigr\OMI-Window1-private")
FIT_DATES = {f"2026-07-{d:02d}" for d in range(12, 18)}


def show_rows(name):
    out = subprocess.run(["git", "-C", REPO, "show", T2PKG + name],
                         stdout=subprocess.PIPE, check=True).stdout
    fh = gzip.open(io.BytesIO(out), "rt", encoding="utf-8")
    for line in fh:
        yield json.loads(line)


R = {"definitions": {
    "fit_slice": "event_date in 2026-07-12..17",
    "postfit_slice": "event_date in 2026-07-18..20",
    "formula_A": "ceil(-d1 - fee) - 1",
    "formula_B": "floor(-d1 - fee - 1)",
    "omitted_lawful_target": ("lawful child (source != CURRENT_TRUE_PRINT_"
                              "REACH_CONTEXT) whose (source, X) differs from "
                              "the decision's selected/held target"),
    "d2_sign_source": "child d2_cents from the surface's own contemporaneous BBO",
    "tape_touch_floor": "min positive-size print price in cache window per leg",
    "five_single_floor": "min price with a single print size >= 5",
    "five_cum_floor": "min P with cumulative print size at prices <= P >= 5",
    "ask5_floor": "min ask level shown with size >= 5 across snapshots",
    "unique_fill": "distinct (event, leg, fill_receipt, X, evidence) tuple",
}}

# event -> date
ev_date = {}
for line in open(PRIV / "joined" / "events.jsonl", encoding="utf-8"):
    row = json.loads(line)
    ev_date[row["event_id"]] = row["event_date"]

# ---------------- overlays: nullity + credited exact-five fills -------------
cred_leg_rows = 0
cred_by_candidate = Counter()
unique_fills = set()
overlay_nonnull = 0
fills_not_five = 0
evidence_types = Counter()
for i in range(1, 17):
    for row in show_rows("UNSCORED_T2_CANDIDATE_EVENT_OVERLAYS_%02d.jsonl.gz" % i):
        if any(row.get(k) is not None for k in ("C", "PC", "IC", "S")) or \
                row.get("metrics") is not None or row.get("performance") is not None:
            overlay_nonnull += 1
        fs = row.get("causal_policy_fill_state_by_leg") or {}
        for leg, st in fs.items():
            if not st:
                continue
            q = st.get("simulated_accounting_quantity")
            if q:
                cred_leg_rows += 1
                cred_by_candidate[row["candidate_id"]] += 1
                if q != 5:
                    fills_not_five += 1
                evidence_types[st.get("simulated_fill_evidence_type")] += 1
                unique_fills.add((row["event_id"], leg,
                                  st.get("simulated_fill_receipt")
                                  or st.get("simulated_fill_book_receipt"),
                                  st.get("simulated_fill_price_cents"),
                                  st.get("simulated_fill_evidence_type")))
R["overlays"] = {
    "rows_with_nonnull_result_fields": overlay_nonnull,
    "credited_leg_fills_all_candidates": cred_leg_rows,
    "credited_by_candidate": dict(sorted(cred_by_candidate.items())),
    "credited_fills_not_exactly_five": fills_not_five,
    "unique_exact_five_fills": len(unique_fills),
    "fill_evidence_types": dict(evidence_types),
}

# ------- surfaces + decisions: headroom, children, rejections, omissions ----
formulaA_match = formulaB_match = both_match = neither = 0
bad_types = Counter()
child_total = child_lawful = child_unlawful = 0
rejection_combos = Counter()
child_vs_surface_denominator_mismatch = 0
distinct_headroom_rows = set()
headroom_diff_examples = []
omit = Counter()   # (candidate, slice, source, d2sign) -> n
omit_norm = Counter()
sel_ledger_equal_dec = True
surfaces_total = 0
decisions_by_key_missing = 0
NORM = {
    "CAUSAL_DIVOT_LATER_RECURRENCE": "causal_divot",
    "LIVEAIM_AIM_DEEP_SOURCE_MAPPING": "liveaim_deep",
    "NATIVE_MACRO_TARGET": "native_macro",
    "CURRENT_EXTERNAL_BID": "external_bid",
    "BID_PLUS_ONE_FALLBACK_NOT_PREFERRED": "bid_plus_one_fallback",
    "ACTIVE_PARENT_EXPOSURE": "active_parent",
    "CURRENT_TRUE_PRINT_REACH_CONTEXT": "context_not_actionable",
}

for shard in range(1, 17):
    dec_by_key = {}
    for row in show_rows(
            "HOLD_WALK_REPRICE_PARK_NOCALL_DECISION_LEDGER_%02d.jsonl.gz" % shard):
        key = (row["candidate_id"], row["event_id"], row["leg_id"],
               row["trigger_receipt"], row["timestamp"])
        dec_by_key[key] = row
    sel_count = 0
    for row in show_rows(
            "TARGET_SELECTION_REJECTED_TARGET_LEDGER_%02d.jsonl.gz" % shard):
        sel_count += 1
        key = (row["candidate_id"], row["event_id"], row["leg_id"],
               row["trigger_receipt"], row["timestamp"])
        if key not in dec_by_key:
            sel_ledger_equal_dec = False
    if sel_count != len(dec_by_key):
        sel_ledger_equal_dec = False
    for row in show_rows("SIBLING_X_OPPORTUNITY_LEDGER_%02d.jsonl.gz" % shard):
        surfaces_total += 1
        key = (row["candidate_id"], row["event_id"], row["leg_id"],
               row["trigger_receipt"], row["timestamp"])
        dec = dec_by_key.get(key)
        if dec is None:
            decisions_by_key_missing += 1
        if row.get("status") != "AVAILABLE":
            continue
        d1 = row["d1_cents"]
        fee = row["fee_cents"]
        b2 = row["b2_max_cents"]
        for label, value in (("d1", d1), ("fee", fee), ("b2_max", b2)):
            if isinstance(value, bool) or not isinstance(value, int):
                bad_types[label + ":" + type(value).__name__] += 1
        fA = math.ceil(-d1 - fee) - 1
        fB = math.floor(-d1 - fee - 1)
        a_ok = (b2 == fA)
        b_ok = (b2 == fB)
        formulaA_match += a_ok
        formulaB_match += b_ok
        both_match += a_ok and b_ok
        if not a_ok and not b_ok:
            neither += 1
            if len(headroom_diff_examples) < 5:
                headroom_diff_examples.append(
                    {"d1": d1, "fee": fee, "b2_max": b2, "A": fA, "B": fB,
                     "event": row["event_id"], "leg": row["leg_id"]})
        distinct_headroom_rows.add((d1, fee, b2))
        selected_key = None
        if dec is not None:
            st = dec.get("selected_target")
            if st:
                selected_key = (st["source"], st["X_cents"])
            elif dec.get("decision") == "HOLD" and dec.get("prior_X_cents") is not None:
                selected_key = ("ACTIVE_PARENT_EXPOSURE", dec["prior_X_cents"])
        sl = "fit" if ev_date.get(row["event_id"]) in FIT_DATES else "postfit"
        for t in row.get("targets") or []:
            child_total += 1
            if t["d1_cents"] != d1 or t["fee_cents"] != fee or \
                    t["b2_max_cents"] != b2:
                child_vs_surface_denominator_mismatch += 1
            if t["lawful"]:
                child_lawful += 1
                if t["source"] == "CURRENT_TRUE_PRINT_REACH_CONTEXT":
                    continue
                tk = (t["source"], t["X_cents"])
                if tk != selected_key:
                    sign = ("NEGATIVE" if t["d2_cents"] < 0
                            else "ZERO" if t["d2_cents"] == 0 else "POSITIVE")
                    omit[(row["candidate_id"], sl, t["source"], sign)] += 1
                    omit_norm[(row["candidate_id"], sl, NORM[t["source"]], sign)] += 1
            else:
                child_unlawful += 1
                failed = tuple(sorted(k for k, v in t["checks"].items() if not v))
                rejection_combos[failed] += 1

R["headroom"] = {
    "available_surfaces_checked": formulaA_match + neither - both_match + (
        formulaB_match - both_match) + both_match + 0,
    "formula_A_matches_b2max": formulaA_match,
    "formula_B_matches_b2max": formulaB_match,
    "both_formulas_match": both_match,
    "neither_formula_matches": neither,
    "examples_neither": headroom_diff_examples,
    "raw_type_violations": dict(bad_types),
    "distinct_d1_fee_b2_rows": len(distinct_headroom_rows),
}
R["surfaces"] = {
    "surfaces_total": surfaces_total,
    "decisions_join_missing": decisions_by_key_missing,
    "selection_ledger_equals_decision_ledger_keys": sel_ledger_equal_dec,
    "child_targets_total": child_total,
    "child_lawful": child_lawful,
    "child_unlawful": child_unlawful,
    "child_vs_surface_fee_d1_b2_mismatch": child_vs_surface_denominator_mismatch,
    "rejection_reason_combinations": {
        "|".join(k): v for k, v in sorted(rejection_combos.items())},
}
R["omitted_attribution_raw"] = {
    "%s|%s|%s|%s" % k: v for k, v in sorted(omit.items())}
R["omitted_attribution_normalized_families"] = sorted(
    {k[2] for k in omit_norm})
R["omitted_totals"] = {
    "total_omitted_lawful_actionable": sum(omit.values()),
    "by_sign": dict(Counter(k[3] for k, v in omit.items()
                            for _ in range(v))),
}

# ---------------- floors from guarded private inputs ------------------------
tape_floor = {}
five_single = {}
five_cum = {}
ask5 = {}
censored_no_print = 0
censored_no_bbo = 0
legs_total = 0
prints_exact_five = 0
for path in sorted((PRIV / "fit-local" / "guarded-cache-v3").glob("*.json.gz")):
    d = json.loads(gzip.open(path, "rt", encoding="utf-8").read())
    for leg in d["legs"]:
        legs_total += 1
        key = (d["event_id"], leg["leg"])
        prints = leg.get("prints") or []
        snaps = leg.get("snapshots") or []
        pos = [p for p in prints if float(p.get("size") or 0) > 0]
        prints_exact_five += sum(1 for p in pos if float(p["size"]) == 5.0)
        if pos:
            tape_floor[key] = min(int(p["price"]) for p in pos)
            singles = [int(p["price"]) for p in pos if float(p["size"]) >= 5.0]
            if singles:
                five_single[key] = min(singles)
            vol_by_price = defaultdict(float)
            for p in pos:
                vol_by_price[int(p["price"])] += float(p["size"])
            run = 0.0
            for price in sorted(vol_by_price):
                run += vol_by_price[price]
                if run >= 5.0:
                    five_cum[key] = price
                    break
        else:
            censored_no_print += 1
        best = None
        has_bbo = False
        for s in snaps:
            if s.get("bids") and s.get("asks"):
                has_bbo = True
            for level, size in s.get("asks") or []:
                if float(size) >= 5.0:
                    best = int(level) if best is None else min(best, int(level))
                    break
        if not has_bbo:
            censored_no_bbo += 1
        if best is not None:
            ask5[key] = best

pairs = defaultdict(dict)
for (event, leg), value in five_cum.items():
    pairs[event][leg] = value
pair_five = {e: sum(v.values()) for e, v in pairs.items() if len(v) == 2}
pairs_t = defaultdict(dict)
for (event, leg), value in tape_floor.items():
    pairs_t[event][leg] = value
pair_tape = {e: sum(v.values()) for e, v in pairs_t.items() if len(v) == 2}
# proven-five floor via ask when no qualifying print
proven5 = {}
for key in set(list(five_cum) + list(ask5)):
    cands = [v for v in (five_cum.get(key), ask5.get(key)) if v is not None]
    proven5[key] = min(cands)
ask_only = sum(1 for k in proven5 if k not in five_cum and k in ask5)
pairs_p = defaultdict(dict)
for (event, leg), value in proven5.items():
    pairs_p[event][leg] = value
pair_proven = {e: sum(v.values()) for e, v in pairs_p.items() if len(v) == 2}


def tiers(mapping):
    return {"le93": sum(1 for v in mapping.values() if v <= 93),
            "le95": sum(1 for v in mapping.values() if v <= 95),
            "le97": sum(1 for v in mapping.values() if v <= 97),
            "lt100": sum(1 for v in mapping.values() if v < 100),
            "events": len(mapping)}


R["floors"] = {
    "legs_total": legs_total,
    "legs_with_tape_touch_floor": len(tape_floor),
    "legs_with_single_print_ge5_floor": len(five_single),
    "legs_with_cumulative_ge5_floor": len(five_cum),
    "legs_with_ask_size_ge5_floor": len(ask5),
    "legs_proven5_by_ask_only_no_qualifying_print": ask_only,
    "evidence_censored_legs_no_positive_print": censored_no_print,
    "legs_without_any_full_BBO_snapshot": censored_no_bbo,
    "prints_of_exactly_five": prints_exact_five,
    "full_tape_pair_floor_tiers_tape_touch": tiers(pair_tape),
    "full_tape_pair_floor_tiers_cumulative5": tiers(pair_five),
    "full_tape_pair_floor_tiers_proven5_incl_ask": tiers(pair_proven),
}

out = Path(r"C:\Users\omigr\AppData\Local\Temp\t2sp_blind_receipt.json")
out.write_text(json.dumps(R, indent=1, sort_keys=True), encoding="utf-8")
print("written", out)
print(json.dumps({k: R[k] for k in ("overlays", "headroom")}, indent=1)[:1500])
