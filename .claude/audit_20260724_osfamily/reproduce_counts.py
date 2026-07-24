#!/usr/bin/env python3
"""Independent reproduction of the Codex Window-1 OS-family result.

Reads ONLY the committed artifacts at results commit f7cd4209 (via a
detached read-only worktree) and recomputes every headline number from the
per-event selected ledger. No Codex code is imported; classification and
metric laws are re-implemented from the written contract:

  C  = both legs filled exactly five contracts inside lawful Window 1
  PC = C and combined Window-1-close delta strictly negative
  S  = C and combined entry cost strictly below 100 cents
  IC = C and both individual leg deltas strictly negative
"""

import datetime as dt
import json
import sys
from collections import Counter, defaultdict

LEDGER = sys.argv[1]
RESULTS = sys.argv[2]

rows = [json.loads(line) for line in open(LEDGER, encoding="utf-8") if line.strip()]
D = len(rows)

ids = [r["event_id"] for r in rows]
assert len(set(ids)) == D, "duplicate event ids"

cls = Counter(r["classification"] for r in rows)

# --- independent re-derivation of C / PC / S / IC from leg-level fields ---
LOT = 5.0
my = Counter()
pc_violations = []
ic_violations = []
s_violations = []
c_flag_mismatch = []
guard_missing = []
schedule_positive = []
holdout_dates = set()
window_left_nonfills = 0
nonfill_status = Counter()
censored_status = Counter()
by_date = defaultdict(Counter)
by_class = defaultdict(Counter)
by_source = defaultdict(Counter)
opt = 0

for r in rows:
    legs = r["legs"]
    qty_ok = len(legs) == 2 and all(abs(l["quantity"] - LOT) < 1e-9 for l in legs)
    cutoff = r["strict_positive_cutoff_utc"]
    # in-window check: completion ts must lie in [T-8h, cutoff]
    in_window = True
    if qty_ok and cutoff:
        cut = dt.datetime.fromisoformat(cutoff).timestamp()
        for l in legs:
            ts = l["completion_exchange_ts"]
            if ts is None or float(ts) > cut:
                in_window = False
    else:
        in_window = qty_ok and cutoff is not None
    my_C = qty_ok and in_window and cutoff is not None
    if my_C != bool(r["C"]):
        c_flag_mismatch.append(r["event_id"])

    deltas = [l["window1_close_delta_cents"] for l in legs] if legs else []
    have_deltas = legs and all(d is not None for d in deltas)
    my_PC = bool(my_C and have_deltas and sum(deltas) < 0)
    costs = [l["vwap_cents"] * l["quantity"] for l in legs] if my_C else []
    my_S = bool(my_C and r["combined_entry_cost_cents"] is not None
                and r["combined_entry_cost_cents"] < 100)
    my_IC = bool(my_C and have_deltas and all(d < 0 for d in deltas))

    if bool(r["PC"]) != my_PC:
        pc_violations.append(r["event_id"])
    if bool(r["S"]) != my_S:
        s_violations.append(r["event_id"])
    if bool(r["IC"]) != my_IC:
        ic_violations.append(r["event_id"])

    my["C"] += my_C
    my["PC"] += my_PC
    my["S"] += my_S
    my["IC"] += my_IC
    opt += bool(r["optimistic_queue_complete"])

    # guard stated beside every verdict?
    if r.get("start_guard") in (None, "", {}) and r["classification"] not in (
        "contradictory",
    ):
        guard_missing.append(r["event_id"])
    # schedule-only start source must never produce a positive C
    if r["start_source_class"] in ("schedule_only", "live_by_only") and (
        r["C"] or r["strict_positive_cutoff_utc"] is not None
    ):
        schedule_positive.append(r["event_id"])
    if r["event_date"] >= "2026-07-24":
        holdout_dates.add(r["event_date"])

    if r["classification"] == "nonfill":
        for l in legs:
            nonfill_status[l["status"]] += 1
        if r["feature_coverage_class"] == "window_left_after_guarded_start":
            window_left_nonfills += 1
    if r["classification"] == "censored":
        key = (r["feature_coverage_class"],
               tuple(sorted({l["status"] for l in legs})) if legs else ())
        censored_status[key] += 1

    by_date[r["event_date"]]["D"] += 1
    by_date[r["event_date"]]["C"] += my_C
    by_date[r["event_date"]]["PC"] += my_PC
    by_class[r["tournament_class"]]["D"] += 1
    by_class[r["tournament_class"]]["C"] += my_C
    by_class[r["tournament_class"]]["PC"] += my_PC
    by_source[r["start_source_class"]]["D"] += 1
    by_source[r["start_source_class"]]["C"] += my_C
    by_source[r["start_source_class"]]["PC"] += my_PC

res = json.load(open(RESULTS, encoding="utf-8"))
sel = res["selected"]["raw"]

report = {
    "D_ledger": D,
    "classification_counts": dict(cls),
    "conservation_sum": sum(cls.values()),
    "reproduced": dict(my),
    "codex_selected_raw": {k: sel[k] for k in ("C", "PC", "S", "IC",
        "exact_five", "partial", "other_quantity", "nonfill",
        "contradictory", "censored")},
    "flag_mismatches": {
        "C": c_flag_mismatch, "PC": pc_violations,
        "S": s_violations, "IC": ic_violations,
    },
    "optimistic_queue_complete_reproduced": opt,
    "guard_missing_events": guard_missing[:20],
    "guard_missing_count": len(guard_missing),
    "schedule_or_liveby_positives": schedule_positive,
    "holdout_dates_in_ledger": sorted(holdout_dates),
    "window_left_events_classified_nonfill": window_left_nonfills,
    "nonfill_leg_statuses": dict(nonfill_status),
    "censored_breakdown": {str(k): v for k, v in sorted(censored_status.items())},
    "ratios": {
        "C_over_D": my["C"] / D, "PC_over_D": my["PC"] / D,
        "PC_over_C": my["PC"] / my["C"] if my["C"] else None,
        "S_over_C": my["S"] / my["C"] if my["C"] else None,
        "IC_over_D": my["IC"] / D,
    },
    "by_date": {k: dict(v) for k, v in sorted(by_date.items())},
    "by_tournament_class": {k: dict(v) for k, v in sorted(by_class.items())},
    "by_start_source_class": {k: dict(v) for k, v in sorted(by_source.items())},
}
print(json.dumps(report, indent=2))
