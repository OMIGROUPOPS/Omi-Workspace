#!/usr/bin/env python3
"""Three bench diagnostics on the frozen conduct-v2 receipt archive.

Imports the unchanged simulator, not the engine. Private raw prints are never
written to the output directory. C1 is explicitly noncausal; C2 is unsafe.
"""
from __future__ import annotations
import argparse
from bisect import bisect_left
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import conduct_scoreboard as c
import conduct_scoreboard_v2 as cv2
import tune_bench_v2_survivorship as b

VARIANTS = ("C0 R0", "C1 ORACLE SENTENCE", "C2 BUDGET RELEASED")
SIDES = ("favourite", "underdog")
ARCHIVE_COMMIT = "d2d8f16b"


def write(path, value):
    path.write_text(json.dumps(c.clean(value), indent=2, sort_keys=True, allow_nan=False)+"\n",
                    encoding="utf-8", newline="\n")


def iter_jsonl(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def digest(value):
    return hashlib.sha256(c.encode(c.clean(value)).encode()).hexdigest()


def distribution(values, quantiles):
    supplied = list(values)
    finite = np.asarray([v for v in supplied if c.finite(v)], dtype=float)
    return dict(n=len(finite), missing=len(supplied)-len(finite),
        mean=float(finite.mean()) if len(finite) else None,
        quantiles={str(q): float(b.inverse_weighted_quantile(finite, np.ones(len(finite)), q))
                   if len(finite) else None for q in quantiles},
        negative=int((finite < 0).sum()), zero=int((finite == 0).sum()), positive=int((finite > 0).sum()))


def q50(state):
    return state.get("floors", {}).get("q50", {}).get("level_cents")


def oracle_forecasts(forecasts, tapes, formation, bell):
    """Q only: strictly later size-positive prints; preserve every other field.

    Same-instant prints have already been consumed by the old order when a
    receipt runs. A print at the bell is outside the fill window.
    """
    epochs = np.asarray([r["epoch"] for r in forecasts])
    levels = {}
    counts = Counter()
    for leg, rows in tapes.items():
        tape = np.asarray([[p[0], p[1]] for p in rows
            if formation <= p[0] < bell and c.finite(p[2]) and p[2] > 0], dtype=float).reshape(-1, 2)
        if len(tape) and np.any(np.diff(tape[:, 0]) < 0):
            raise ValueError("UNSORTED_ORACLE_TAPE")
        minima = np.minimum.accumulate(tape[::-1, 1])[::-1] if len(tape) else np.empty(0)
        indices = np.searchsorted(tape[:, 0], epochs, side="right")
        levels[leg] = [float(minima[i]) if i < len(minima) else None for i in indices]
    projected = []
    for i, row in enumerate(forecasts):
        sides = {}
        for leg, state in row["sides"].items():
            level = levels[leg][i]
            counts["side_receipts"] += 1
            counts["oracle_available" if level is not None else "no_later_positive_print"] += 1
            counts["original_status_"+state["status"]] += 1
            floors = dict(state.get("floors", {}))
            floors["q50"] = dict(floors.get("q50", {}), level_cents=level)
            sides[leg] = dict(state, floors=floors)
        projected.append(dict(row, sides=sides))
    return projected, dict(counts)


def commitment_audit(result, legs, budget, par):
    """Nominal-budget audit independent of C2's disabled simulator guard.

    Receipt actions are atomic across the pair: do not count a transient
    intermediate sum while iterating the two actions at one timestamp.
    """
    events = {}
    for action in result["actions"]:
        events.setdefault(action["epoch"], {"actions": [], "fills": []})["actions"].append(action)
    for leg, fill in result["fills"].items():
        events.setdefault(fill["epoch"], {"actions": [], "fills": []})["fills"].append((leg, fill))
    rests, filled = dict.fromkeys(legs), {}
    maximum = 0
    first_above_budget = first_above_par = None
    for epoch, row in sorted(events.items()):
        for leg, fill in row["fills"]:
            filled[leg] = fill["cents"]
            rests[leg] = None
        for action in row["actions"]:
            if action["leg"] in filled:
                raise ValueError("ACTION_AFTER_FILL")
            rests[action["leg"]] = action["new_cents"]
        total = sum(filled.values())+sum(v for v in rests.values() if v is not None)
        maximum = max(maximum, total)
        if total > budget and first_above_budget is None:
            first_above_budget = epoch
        if total > par and first_above_par is None:
            first_above_par = epoch
    return dict(maximum_filled_plus_rest_cents=maximum,
        ever_above_nominal_budget=first_above_budget is not None,
        ever_above_par=first_above_par is not None,
        first_above_nominal_budget_epoch=first_above_budget, first_above_par_epoch=first_above_par,
        completed_above_par=bool(result["completed"] and result["pair_sum"] > par))


def fill_order(result, forecasts, legs, spec, seconds):
    """Baseline only; current Q comes from the last receipt STRICTLY before fill."""
    if not result["fills"]:
        return None
    epochs = [r["epoch"] for r in forecasts]
    earliest = min(f["epoch"] for f in result["fills"].values())
    first = [l for l in legs if l in result["fills"] and result["fills"][l]["epoch"] == earliest]
    index = bisect_left(epochs, earliest)-1
    if index < 0:
        raise ValueError("FILL_WITHOUT_EARLIER_RECEIPT")
    receipt = forecasts[index]
    fav, dog = legs
    fav_fill = result["fills"].get(fav)
    if fav_fill and fav_fill["epoch"] <= earliest:
        commitment, source = fav_fill["cents"], "FILLED"
    else:
        previous = [a for a in result["actions"] if a["leg"] == fav and a["epoch"] < earliest]
        rest = previous[-1]["new_cents"] if previous else None
        commitment, source = (rest, "RESTING") if rest is not None else (0, "NONE")
    dog_q = q50(receipt["sides"][dog])
    allowance = spec["pair_budget"]-commitment
    fills = []
    for leg in legs:
        fill = result["fills"].get(leg)
        if not fill:
            continue
        asof = forecasts[bisect_left(epochs, fill["epoch"])-1]
        current_q = q50(asof["sides"][leg])
        placement = [a for a in result["actions"] if a["leg"] == leg and a["epoch"] == fill["placed_epoch"]]
        if len(placement) != 1 or placement[0]["new_cents"] != fill["cents"]:
            raise ValueError("FILL_PLACEMENT_LINEAGE_MISMATCH")
        placed_q = (placement[0].get("q50") or {}).get("level_cents")
        fills.append(dict(leg=leg, side=SIDES[legs.index(leg)], first=leg in first,
            epoch=fill["epoch"], minutes_to_bell=fill["minutes_to_bell"], cents=fill["cents"],
            current_q_receipt_epoch=asof["epoch"], current_q=current_q,
            current_status=asof["sides"][leg]["status"],
            premium_to_current_q=fill["cents"]-current_q if c.finite(current_q) else None,
            placement_epoch=fill["placed_epoch"], placement_q=placed_q,
            premium_to_placement_q=fill["cents"]-placed_q if c.finite(placed_q) else None,
            price_age_minutes=fill["rest_age_minutes"]))
    return dict(event_id=result["event_id"], outcome="COMPLETED" if result["completed"] else "ONE_SIDED",
        first_side="SAME_TIMESTAMP" if len(first) > 1 else SIDES[legs.index(first[0])],
        first_epoch=earliest, first_minutes_to_bell=(result["bell_epoch"]-earliest)/seconds,
        receipt_epoch=receipt["epoch"], favourite_commitment_cents=commitment,
        favourite_commitment_source=source, nominal_pair_budget=spec["pair_budget"],
        underdog_effective_cap_cents=allowance, underdog_q=dog_q,
        underdog_q_status=receipt["sides"][dog]["status"],
        underdog_cap_headroom_cents=allowance-dog_q if c.finite(dog_q) else None,
        global_cap_minus_underdog_q=spec["pair_budget"]-dog_q if c.finite(dog_q) else None,
        failed_sides=result["failed_sides"], fills=fills)


def summarize_order(rows, quantiles):
    out = {}
    for outcome in ("ALL_FILLED_OR_ONE_SIDED", "COMPLETED", "ONE_SIDED"):
        group = rows if outcome == "ALL_FILLED_OR_ONE_SIDED" else [r for r in rows if r["outcome"] == outcome]
        out[outcome] = {}
        for side in ("ALL", *SIDES, "SAME_TIMESTAMP"):
            selected = group if side == "ALL" else [r for r in group if r["first_side"] == side]
            fills = [f for r in selected for f in r["fills"] if f["first"]]
            out[outcome][side] = dict(pairs=len(selected),
                share_of_outcome=len(selected)/len(group) if group else None,
                first_fill_minutes_to_bell=distribution((r["first_minutes_to_bell"] for r in selected), quantiles),
                first_fill_premium_to_current_q=distribution((f["premium_to_current_q"] for f in fills), quantiles),
                first_fill_premium_to_placement_q=distribution((f["premium_to_placement_q"] for f in fills), quantiles),
                underdog_cap_headroom_cents=distribution((r["underdog_cap_headroom_cents"] for r in selected), quantiles),
                favourite_commitment_sources=dict(Counter(r["favourite_commitment_source"] for r in selected)))
    return out


def summary(rows, audits, baseline, spec):
    result = cv2.summary(rows)
    result["captured_total_cents"] = sum(r["captured_cents"] for r in rows)
    result["matched_vs_R0"] = cv2.matched(rows, baseline)
    for key in ("completed_above_par", "ever_above_par", "ever_above_nominal_budget"):
        count = sum(a[key] for a in audits)
        result[key+"_pairs"] = count
        result[key+"_share_all_eligible"] = count/len(rows)
    result["completed_above_par_share_completed"] = result["completed_above_par_pairs"]/result["completed"] if result["completed"] else None
    result["nominal_pair_budget"] = spec["pair_budget"]
    result["par"] = spec["par"]
    return result


def report(out, scoreboard, orders):
    lines = ["# CEILINGS — ATP_MAIN, RECEIPT-SIM", "", "Bench only. Same 928 eligible pairs; 609,960 archived receipts. Reachable fills, not certain fills. Queue position unknown.", "",
        "| Diagnostic | Completed | One-sided | Neither | Captured / eligible (cents) | Captured / completed (cents) | Completed sum > par | Ever commitment > par |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, s in scoreboard.items():
        lines.append(f"| {name} | {s['completed']} ({s['completion_rate']:.4%}) | {s['one_sided']} ({s['one_sided_rate']:.4%}) | {s['neither_filled']} | {s['mean_captured_eligible']:.6f} | {s['mean_captured_completed']:.6f} | {s['completed_above_par_pairs']} ({s['completed_above_par_share_all_eligible']:.4%} of eligible) | {s['ever_above_par_pairs']} ({s['ever_above_par_share_all_eligible']:.4%}) |")
    lines += ["", "C1 changes only Q to the strictly later positive-size print floor. Original authority status, X, books, cadence and every guard remain. No future print means absent oracle Q. This is a foresight diagnostic under this policy, not a mathematical supremum over all sentences/conduct.", "",
        "C2 disables only the pair-budget guard. UNSAFE DIAGNOSTIC, NEVER CONDUCT. Individual price bounds, authority fence and post-only/book rules remain. Above-par completion produces negative capture; incomplete pairs receive zero credit. Independent nominal-budget exposure audit accompanies simulator safety counters.", "", "## Matched all-eligible deltas versus R0", "", "| Diagnostic | Completion delta (pp) | One-sided delta (pp) | Captured / eligible delta (cents) |", "|---|---:|---:|---:|"]
    for name, s in scoreboard.items():
        d = s["matched_vs_R0"]
        lines.append(f"| {name} | {100*d['completion_rate_delta']:+.4f} | {100*d['one_sided_rate_delta']:+.4f} | {d['captured_per_eligible_delta']:+.6f} |")
    lines += ["", "## C3 — baseline R0 fill order", "", "Current sentence = latest receipt strictly before the fill. Premium = filled bid minus that Q; placement-Q premium is separate. Effective underdog cap = nominal pair budget minus favourite filled/resting commitment at the first-fill timestamp. Headroom = effective cap minus current Q_dog. Simultaneous fills are ties, not an invented order.", "",
        "| Outcome | First side | Pairs | Premium to current Q: q10/q25/q50/q75/q90 | Dog headroom: q10/q25/q50/q75/q90 | Negative / zero / positive headroom |", "|---|---|---:|---|---|---|"]
    for outcome in ("COMPLETED", "ONE_SIDED"):
        for side in (*SIDES, "SAME_TIMESTAMP"):
            s = orders[outcome][side]
            def qs(key):
                return " / ".join("missing" if v is None else f"{v:g}" for v in s[key]["quantiles"].values())
            h = s["underdog_cap_headroom_cents"]
            lines.append(f"| {outcome} | {side} | {s['pairs']} | {qs('first_fill_premium_to_current_q')} | {qs('underdog_cap_headroom_cents')} | {h['negative']} / {h['zero']} / {h['positive']} (missing {h['missing']}) |")
    lines += ["", "Full distributions (including means, missing values, fill minutes-to-bell and placement-Q premiums), pair-level evidence, input hashes and unchanged-engine checks are in the adjacent JSON and receipt. No causal attribution is inferred from C3's observational headroom.", ""]
    (out/"CEILINGS_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run(args):
    root, out = args.root, args.out
    bound = c.bound_inputs(root)
    c.verify_reference(b, root)
    contract = bound["receipt"]["organ_contract"]
    spec = dict(bound["conduct"], positive_size_fills=True)
    archive = root/"arb-executor/analysis/conduct_scoreboard_v2/ATP_MAIN"
    artifacts = {}
    for name in ("FIRST_FORECASTS.jsonl.gz", "CONDUCT_QUERIES.jsonl.gz", "CONDUCT_RECEIPT.json"):
        blob = subprocess.check_output(["git", "rev-parse", ARCHIVE_COMMIT+":"+str((archive/name).relative_to(root)).replace("\\", "/")], cwd=root).decode().strip()
        actual = subprocess.check_output(["git", "hash-object", str(archive/name)], cwd=root).decode().strip()
        if blob != actual:
            raise ValueError("ARCHIVE_NOT_COMMITTED_BASELINE:"+name)
        artifacts[name] = dict(sha256=c.sha256(archive/name), git_blob=blob, bytes=(archive/name).stat().st_size)
    archive_receipt = json.loads((archive/"CONDUCT_RECEIPT.json").read_text(encoding="utf-8"))
    for name, expected in archive_receipt["scripts"].items():
        if c.sha256(root/"arb-executor/analysis"/name) != expected:
            raise ValueError("FROZEN_HELPER_CHANGED:"+name)
    library = root/"arb-executor/data/durable/RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz"
    counts = library.with_name("RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz")
    library_sha = c.sha256(library)
    if library_sha != bound["receipt"]["input_library"]["sha256"]:
        raise ValueError("LIBRARY_NOT_BASELINE")
    print("LOAD_VERIFIED_LIBRARY_AND_PRIVATE_PRINTS", flush=True)
    pairs, _, _, count_source = b.load_tick_library(library, {}, counts)
    wanted = bound["scoreboard"]["categories"]["ATP_MAIN"]["query_event_ids"]
    queries = {p.event_id: p for p in pairs if p.category == "ATP_MAIN" and p.event_id in set(wanted)}
    if sorted(queries) != sorted(wanted):
        raise ValueError("QUERY_DENOMINATOR_MISMATCH")
    extract_path = args.prints.with_suffix(".receipt.json")
    extract = json.loads(extract_path.read_text(encoding="utf-8"))
    print_sha = c.sha256(args.prints)
    if print_sha != extract["output_sha256"] or print_sha != archive_receipt["print_extract"]["sha256"] or extract["library_sha256"] != library_sha:
        raise ValueError("PRINT_EXTRACT_MISMATCH")
    tapes, outer, raw_count, positive_count = {}, 0, 0, 0
    for row in iter_jsonl(args.prints):
        outer += 1
        raw_count += len(row["prints"])
        positive_count += sum(c.finite(p[2]) and p[2] > 0 for p in row["prints"])
        event, leg = row["event_id"], row["leg_id"]
        if event not in queries:
            continue
        obj = next(l for l in queries[event].legs if l.leg_id == leg)
        if (obj.formation, obj.bell) != (row["formation_end_epoch"], row["bell_epoch"]):
            raise ValueError("PRINT_SPAN_MISMATCH")
        if leg in tapes.setdefault(event, {}):
            raise ValueError("DUPLICATE_PRINT_LEG")
        if row["prints"] != sorted(row["prints"], key=lambda p: (p[0], p[3])):
            raise ValueError("UNSORTED_NATIVE_PRINTS")
        tapes[event][leg] = row["prints"]
    if (outer, raw_count, args.prints.stat().st_size) != (extract["legs"], extract["true_prints"], extract["output_bytes"]):
        raise ValueError("EXTRACT_COUNTS_MISMATCH")
    if positive_count != archive_receipt["print_extract"]["positive_size_prints"]:
        raise ValueError("POSITIVE_SIZE_COUNT_MISMATCH")
    baseline = {r["event_id"]: {k:v for k,v in r.items() if k != "mode"}
        for r in iter_jsonl(archive/"CONDUCT_QUERIES.jsonl.gz") if r["mode"] == "RECEIPT-SIM" and r["rule"] == c.RULES[0]}
    if sorted(baseline) != sorted(wanted):
        raise ValueError("ARCHIVED_R0_DENOMINATOR_MISMATCH")
    out.mkdir(parents=True, exist_ok=True)
    results, audits = {v: [] for v in VARIANTS}, {v: [] for v in VARIANTS}
    order_rows, digests, seen, receipt_counts, oracle_counts = [], [], set(), Counter(), Counter()
    began = time.monotonic()
    with (out/"CEILINGS_QUERIES.jsonl.gz").open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
        for archive_row in iter_jsonl(archive/"FIRST_FORECASTS.jsonl.gz"):
            if archive_row["mode"] != "RECEIPT-SIM":
                continue
            event = archive_row["event_id"]
            if event in seen:
                raise ValueError("DUPLICATE_FORECAST_QUERY")
            seen.add(event)
            query = queries[event]
            legs = [l.leg_id for l in query.legs]
            if set(tapes[event]) != set(legs):
                raise ValueError("MISSING_PRINT_LEG")
            forecasts = [{k:v for k,v in r.items() if k != "joint"} for r in archive_row["receipts"]]
            epochs = [r["epoch"] for r in forecasts]
            if epochs != sorted(set(epochs)):
                raise ValueError("NONUNIQUE_RECEIPT_CLOCK")
            receipt_counts.update(r["receipt_kind"] for r in forecasts)
            oracle, oc = oracle_forecasts(forecasts, tapes[event], query.formation, query.bell)
            again_oracle, again_counts = oracle_forecasts(forecasts, tapes[event], query.formation, query.bell)
            if digest(oracle) != digest(again_oracle) or oc != again_counts:
                raise ValueError("ORACLE_NONDETERMINISM")
            oracle_counts.update(oc)
            query_hashes = {"event_id": event, "oracle_sha256": digest(oracle)}
            for variant in VARIANTS:
                projected = oracle if variant == VARIANTS[1] else forecasts
                conduct_spec = dict(spec, pair_budget=math.inf) if variant == VARIANTS[2] else spec
                result = c.simulate_conduct(event, legs, projected, tapes[event], query.formation, query.bell, conduct_spec, 0)
                again = c.simulate_conduct(event, legs, projected, tapes[event], query.formation, query.bell, conduct_spec, 0)
                if digest(result) != digest(again):
                    raise ValueError("SIMULATION_NONDETERMINISM")
                cv2.verify_fills(result, tapes[event])
                if variant == VARIANTS[0] and digest(result) != digest(baseline[event]):
                    raise ValueError("R0_ARCHIVE_MISMATCH:"+event)
                audit = commitment_audit(result, legs, spec["pair_budget"], spec["par"])
                if variant != VARIANTS[2] and audit["ever_above_nominal_budget"]:
                    raise ValueError("NOMINAL_PAIR_BUDGET_VIOLATED")
                if result["safety_violations"]:
                    raise ValueError("RETAINED_GUARD_VIOLATED")
                query_hashes[variant] = digest(result)
                full = dict(diagnostic=variant, **result, nominal_budget_audit=audit)
                gz.write((c.encode(c.clean(full))+"\n").encode())
                results[variant].append({k:v for k,v in result.items() if k not in ("actions", "stepped_off_exposures", "joint_decisions")})
                audits[variant].append(audit)
                if variant == VARIANTS[0]:
                    record = fill_order(result, forecasts, legs, spec, contract["minute_seconds"])
                    if record is not None:
                        order_rows.append(record)
            digests.append(query_hashes)
            if len(seen) % 50 == 0 or len(seen) == len(wanted):
                elapsed = time.monotonic()-began
                print("PROGRESS "+c.encode(dict(queries_done=len(seen), total=len(wanted), receipts=sum(receipt_counts.values()), elapsed_seconds=elapsed, eta_seconds=elapsed/len(seen)*(len(wanted)-len(seen)))), flush=True)
    if sorted(seen) != sorted(wanted):
        raise ValueError("FINAL_QUERY_DENOMINATOR_MISMATCH")
    tables = {v: summary(results[v], audits[v], results[VARIANTS[0]], spec) for v in VARIANTS}
    order_summary = summarize_order(order_rows, contract["quantiles"])
    write(out/"CEILINGS_SCOREBOARD.json", dict(eligible=len(wanted), summary=tables))
    write(out/"C3_FILL_ORDER.json", dict(eligible=len(wanted), with_fill=len(order_rows),
        neither_filled=len(wanted)-len(order_rows), summary=order_summary, rows=order_rows))
    write(out/"DETERMINISM.json", dict(passes=2, query_digests=digests))
    report(out, tables, order_summary)
    if c.bound_inputs(root)["conduct"] != bound["conduct"]:
        raise ValueError("ENGINE_CHANGED_DURING_BENCH")
    receipt = dict(status="BENCH_ONLY_COMPLETE", category="ATP_MAIN", eligible_pairs=len(wanted),
        query_ids_sha256=digest(sorted(wanted)), baseline=bound["provenance"], conduct_archive_commit=ARCHIVE_COMMIT,
        prior_art=["c7825925:arb-executor/analysis/tune_bench_v2_ticks/ATP_MAIN/TUNE_BENCH_RECEIPT.json",
                   "d2d8f16b:arb-executor/analysis/conduct_scoreboard_v2/ATP_MAIN/CONDUCT_RECEIPT.json",
                   "f938d53f:arb-executor/analysis/sentence_experiments/ATP_MAIN/SENTENCE_RECEIPT.json"],
        archives=artifacts, library_sha256=library_sha, count_sidecar=count_source,
        print_extract=dict(path=str(args.prints), sha256=print_sha, receipt_sha256=c.sha256(extract_path),
            bytes=args.prints.stat().st_size, outer_leg_rows=outer, accepted_prints=raw_count,
            positive_size_prints=positive_count, raw_prints_committed=False),
        scripts={Path(p).name:c.sha256(p) for p in (__file__, c.__file__, cv2.__file__, b.__file__, Path(__file__).with_name("test_ceilings.py"))},
        unchanged_engine_and_conduct=bound["conduct"], cadence="RECEIPT-SIM", receipt_counts=dict(receipt_counts),
        total_receipts=sum(receipt_counts.values()), oracle_side_receipt_counts=dict(oracle_counts),
        definitions={
            "C0":"Exact full-result equality to all archived R0 RECEIPT-SIM queries, not merely summary equality.",
            "C1":"Replace only each side's floors.q50.level_cents with min price among accepted prints with size>0, receipt.epoch < native ts < bell, within verified span. Native order is timestamp then rowid. No later print => Q absent. Preserve original ESS/status/authority fence, roles, X, other bands, books, asks, receipt grid, fill law and conduct guards. Existing invalid-Q behavior holds an earlier rest. Only Q is oracle; unchanged writer strings in simulator evidence name the frozen R0 execution path, not causal pool authorship of oracle Q.",
            "C1_limit":"Oracle-level policy diagnostic, not a mathematical global upper bound: exact-floor targeting, missing future prints, postability, fences and rearm can limit it; a different knowingly worse level could still improve completion.",
            "C2":"Current sentence and unchanged R0 simulator with only pair_budget=unbounded in memory. UNSAFE DIAGNOSTIC ONLY, NEVER A CONDUCT. Individual legal-price bounds remain. No engine value or file changed. All other guards and size-positive fill law unchanged. Disabled cap is audited independently at the original nominal budget and par; simulator safety counters cannot certify this unsafe variant.",
            "capture":"Both sides must fill strictly before bell. Credit at resting bid prices, not triggering print prices. Capture=par-pair_sum, including negative capture above par. One-sided/neither receive zero. All-eligible denominator identical for every variant.",
            "above_par":"Completed pair fill sum > par shown per eligible and per completed. Separately show ever filled-plus-resting exposure > par and > original nominal budget; pair actions at one receipt are atomic, not intermediate iteration states.",
            "C3":"Baseline R0 only, completed plus one-sided. First is earliest actual native fill timestamp; equal timestamps are SAME_TIMESTAMP without claiming ordering. Premium=filled bid minus current Q from latest receipt strictly before that fill; placement-Q premium separate. Missing current Q is missing, not zero. Negative premium is possible when a held rest sits below a later sentence.",
            "C3_headroom":"At the first-fill timestamp after any tied fills, favourite commitment=favourite filled cents if filled by then, else its active rest from actions strictly before the timestamp, else zero with NONE source. Effective underdog cap=original pair_budget-favourite commitment. Headroom=effective cap-current Q_dog at latest strictly-earlier receipt. Also store raw pair_budget-Q_dog separately. Dog-first headroom is target slack, not permission to repurchase the already filled side.",
            "distribution":"Unweighted inverse-CDF q10/q25/q50/q75/q90 inherited from bench contract; pair count and missing denominators explicit. Tied first fills contribute both first-side premiums but one pair headroom. Placement-Q premium and fill minutes-to-bell distributions retained.",
            "queue":"Reachable only, not certain. Queue position unknown; zero-size prints, same-instant placement fills and post-bell fills never credited.",
            "scope":"No pool reconstruction, engine edit, face edit, conduct deployment, tuning, or named-game selection. All frozen R0 forecasts from same walk-forward/category/self/same-day-filtered 928 queries."},
        determinism=dict(passes=2, oracle_projection_passes=2, all_query_digests_sha256=digest(digests)),
        verification=dict(archived_R0_full_result_matches=len(wanted), independent_fill_and_miss_audits=len(wanted)*len(VARIANTS),
                          same_query_ids_all_variants=True, original_safety_guards_pass=True, engines_unchanged=True),
        outputs={p.name:dict(sha256=c.sha256(p), bytes=p.stat().st_size) for p in sorted(out.iterdir()) if p.is_file() and p.name != "CEILINGS_RECEIPT.json"})
    write(out/"CEILINGS_RECEIPT.json", receipt)
    print("COMPLETE "+c.encode(dict(eligible=len(wanted), receipts=sum(receipt_counts.values()), out=str(out))), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--prints", type=Path, default=Path(r"C:\tmp\conduct_atp_main_v1\ATP_MAIN_PRINTS.jsonl.gz"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    args.out = args.out or args.root/"arb-executor/analysis/ceilings/ATP_MAIN"
    run(args)
