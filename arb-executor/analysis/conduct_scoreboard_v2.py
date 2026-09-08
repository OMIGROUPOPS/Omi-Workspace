#!/usr/bin/env python3
"""Bench-only positive-size, change-point conduct comparison. No engine import/replay.

Historical v1 artifacts remain in conduct_scoreboard/ATP_MAIN. This run writes
conduct_scoreboard_v2/ATP_MAIN. Raw private prints are never written here.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import ExitStack
from datetime import datetime
import gzip
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median
import sys
import time
import numpy as np
import conduct_scoreboard as v1
import tune_bench_v2_survivorship as b

MODES = ("RECEIPT-SIM", "GATE-SIM")


def choose_joint(receipt, legs, fills, memory, active, spec):
    """Empirical joint CDF on observed paired candidates, never marginal products."""
    joint = receipt.get("joint", {})
    result = dict(member_count=joint.get("member_count", 0), ess=joint.get("ess", 0),
                  status="INSUFFICIENT_EVIDENCE", levels={})
    if joint.get("status") != "OK" or len(fills) == len(legs):
        return result
    outcomes = np.asarray(joint["outcomes"], dtype=float)
    levels, mass = outcomes[:, :2], outcomes[:, 2]
    candidates = levels.copy()
    for i, leg in enumerate(legs):
        if leg in fills:
            candidates[:, i] = fills[leg]["cents"]
    candidates = np.unique(candidates, axis=0)
    feasible = np.all(np.isfinite(candidates), axis=1)
    feasible &= np.all(candidates == np.floor(candidates), axis=1)
    feasible &= np.all((candidates >= spec["minimum_cent"]) & (candidates <= spec["maximum_cent"]), axis=1)
    feasible &= candidates.sum(axis=1) <= spec["pair_budget"]
    for i, leg in enumerate(legs):
        if leg in fills:
            continue
        state = receipt["sides"][leg]
        if state["status"] != "OK" or not v1.finite(state["ask"]):
            feasible[:] = False
        else:
            feasible &= candidates[:, i] < state["ask"]
        if state["role"] == "FALLER":
            floor = memory.get(leg)
            if active[leg] is not None:
                floor = max(floor, active[leg]["cents"]) if floor is not None else active[leg]["cents"]
            if floor is not None:
                feasible &= candidates[:, i] >= floor
    candidates = candidates[feasible]
    result["feasible_candidates"] = len(candidates)
    if not len(candidates):
        result["status"] = "NO_FEASIBLE_JOINT_CANDIDATE"
        return result
    # Count both outcomes on the same historical pair, preserving dependence.
    # After one fill its price stays fixed; the same joint outcomes/denominator
    # remain in force (operator-approved), not an invented conditional model.
    reached = np.all(levels[None, :, :] <= candidates[:, None, :], axis=2)
    probabilities = (reached * mass).sum(axis=1) / mass.sum()
    sums = candidates.sum(axis=1)
    objective = probabilities * (spec["par"] - sums)
    winner = np.lexsort((candidates[:, 0], sums, -objective))[0]
    result.update(status="OK", levels=dict(zip(legs, candidates[winner].tolist())),
                  probability_both_reach=float(probabilities[winner]),
                  expected_pair_discount=float(objective[winner]),
                  pair_sum=float(sums[winner]))
    return result


class ReceiptProjector:
    """Batch historical samples, bounded RAM; each row uses only the own prefix."""
    def __init__(self, pairs, contract, batch_size=256):
        self.pairs, self.c, self.batch_size = pairs, contract, batch_size

    def project(self, query, mode):
        c = self.c
        atlas = np.asarray([g for g in c["gates_minutes_to_bell"] if 0 < g <= query.first_mtb])
        observed = query.grid()
        observed = observed[(observed > 0) & (observed <= query.first_mtb)]
        gates = np.sort(np.union1d(observed, atlas))[::-1] if mode == "RECEIPT-SIM" else atlas
        epochs = query.bell - gates * c["minute_seconds"]
        own = query.levels(gates) if len(gates) else np.empty((0, 8))
        members, weights = b.initial_pool(query, self.pairs)
        first_mtb = np.asarray([m.first_mtb for m in members])
        own_roles = np.asarray([query.roles(float(g)) for g in gates])
        own_lows = []
        for leg in query.legs:
            ix = np.searchsorted(leg.epoch, epochs, side="right") - 1
            own_lows.append(np.where(ix >= 0, leg.low[np.maximum(ix, 0)], np.nan))
        binds, previous, flips = [None, None], [None, None], [0, 0]
        observed_cursor = 0
        rows = []
        # The reconstruction flag is conservative: ask changes with unchanged
        # bid/last, no trade-count increment, on the union leg change-point grid.
        obs_epochs = query.bell - observed * c["minute_seconds"]
        obs_states = query.levels(observed) if len(observed) else np.empty((0, 8))
        ask_only = set()
        for j in range(1, len(observed)):
            same = np.equal(obs_states[j], obs_states[j-1]) | (np.isnan(obs_states[j]) & np.isnan(obs_states[j-1]))
            changed = np.flatnonzero(~same[:6])
            if len(changed) and all(col in (2, 5) for col in changed):
                counts_equal = True
                for leg in query.legs:
                    indices = np.searchsorted(leg.count_epoch, np.floor(obs_epochs[j-1:j+1]), side="right")-1
                    vals = [int(leg.print_count_cum[k]) if k >= 0 else 0 for k in indices]
                    counts_equal &= vals[0] == vals[1]
                if counts_equal:
                    ask_only.add(float(observed[j]))
        for start in range(0, len(gates), self.batch_size):
            stop = min(start+self.batch_size, len(gates))
            gs = gates[start:stop]
            n = len(gs)
            mc = np.empty((n, len(members), 8))
            mf = np.empty((n, len(members), 2, 2))
            mr = np.empty((n, len(members), 2), dtype="U12")
            for j, member in enumerate(members):
                mc[:, j] = member.levels(gs)
                for side, leg in enumerate(member.legs):
                    ts = leg.bell - gs*c["minute_seconds"]
                    current = leg.sample(ts)[:, 0]
                    ix = np.searchsorted(leg.epoch, ts, side="right")
                    fi = leg.remaining_floor_index[np.minimum(ix, len(leg.epoch)-1)]
                    future_low = leg.values[fi, 0]
                    use_current = (ix == len(leg.epoch)) | (current <= future_low)
                    mf[:, j, side, 0] = np.where(use_current, current, future_low)
                    mf[:, j, side, 1] = np.where(use_current, gs, (leg.bell-leg.epoch[fi])/c["minute_seconds"])
                    drift = mc[:, j, side*3] - leg.open
                    mr[:, j, side] = np.where(drift >= c["role_drift_cents"], "CLIMBER",
                        np.where(drift <= -c["role_drift_cents"], "FALLER", "NOT_CALLABLE"))
            for local, index in enumerate(range(start, stop)):
                gate, epoch = float(gates[index]), float(epochs[index])
                while observed_cursor < len(observed) and observed[observed_cursor] >= gate:
                    obs_gate = float(observed[observed_cursor])
                    for side, role in enumerate(query.roles(obs_gate)):
                        if role != "NOT_CALLABLE":
                            if binds[side] is None:
                                binds[side] = dict(role=role, minutes_to_bell=obs_gate)
                            if previous[side] is not None and previous[side] != role:
                                flips[side] += 1
                            previous[side] = role
                    observed_cursor += 1
                row = dict(epoch=epoch, source_gate_minutes=gate, sides={},
                           receipt_kind="ATLAS_GATE" if gate in atlas else "LEG_CHANGE_POINT",
                           ask_only_book_tick=mode == "RECEIPT-SIM" and gate not in atlas and gate in ask_only)
                masks = []
                candidate_columns = []
                for side, leg in enumerate(query.legs):
                    role = str(own_roles[index, side])
                    mask = ((mr[local, :, side] == role) | (role == "NOT_CALLABLE"))
                    mask &= np.all(np.isfinite(mc[local, :, side*3:side*3+3]), axis=1)
                    mask &= first_mtb >= gate
                    sw = weights * mask
                    masks.append(mask)
                    ess = float(b.ess(sw) or 0)
                    state = dict(role=role, first_bind=binds[side], flip_count=flips[side],
                        last=float(own[index, side*3]), bid=float(own[index, side*3+1]), ask=float(own[index, side*3+2]),
                        seen_true_trade_low=float(own_lows[side][index]), ess=ess,
                        member_count=int(np.count_nonzero(sw)), status="INSUFFICIENT_EVIDENCE", writer="POOL_FIRST_TICK")
                    delta = mf[local, :, side, 0] - mc[local, :, side*3]
                    candidate_columns.append(own[index, side*3]+delta)
                    if ess >= c["no_call_ess_floor"]:
                        state.update(status="OK", floors={})
                        active = sw > 0
                        for q in c["quantiles"]:
                            if q not in (.25, .5, .75):
                                continue
                            state["floors"][f"q{round(q*100)}"] = dict(
                                level_cents=float(own[index, side*3] + b.inverse_weighted_quantile(delta[active], sw[active], q)),
                                minutes_to_bell=float(b.inverse_weighted_quantile(mf[local, :, side, 1][active], sw[active], q)))
                    row["sides"][leg.leg_id] = state
                joint_weights = weights * masks[0] * masks[1]
                joint_ess = float(b.ess(joint_weights) or 0)
                joint = dict(ess=joint_ess, member_count=int(np.count_nonzero(joint_weights)),
                             status="INSUFFICIENT_EVIDENCE")
                if joint_ess >= c["no_call_ess_floor"]:
                    values = np.column_stack(candidate_columns)
                    positive = (joint_weights > 0) & np.all(np.isfinite(values), axis=1)
                    pairs_unique, inverse = np.unique(values[positive], axis=0, return_inverse=True)
                    mass = np.bincount(inverse, weights=joint_weights[positive])
                    joint.update(status="OK", outcomes=np.column_stack((pairs_unique, mass)).tolist())
                row["joint"] = joint
                rows.append(row)
        return rows


def positive_named_tapes(path, pairs):
    """Retain actual size/source row, discarded by the reference Leg adapter."""
    selected = {p.event_id+"-"+l.leg_id for p in pairs for l in p.legs}
    needles = tuple(p.event_id.encode() for p in pairs)
    tapes, seen = {ticker: [] for ticker in selected}, {}
    census = Counter()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for line_no, line in enumerate(stream, 1):
            digest.update(line)
            if not any(needle in line for needle in needles):
                continue
            r = json.loads(line)
            ticker = r.get("ticker")
            if ticker not in selected:
                continue
            if r.get("true_print") is not True:
                raise ValueError("NAMED_NON_TRUE_PRINT")
            ts = datetime.fromisoformat(r["exchange_ts"].replace("Z", "+00:00")).timestamp()
            price, size = float(r["price_cents"]), float(r["size"])
            identity = r.get("trade_id") or r.get("receipt_id")
            if not identity:
                raise ValueError("NAMED_MISSING_IDENTITY")
            signature = (ticker, ts, price, size)
            if identity in seen:
                if signature != seen[identity]:
                    raise ValueError("NAMED_CONFLICTING_IDENTITY")
                census["deduped"] += 1
                continue
            seen[identity] = signature
            if not all(math.isfinite(x) for x in (ts, price, size)):
                raise ValueError("NAMED_NONFINITE_PRINT")
            if size <= 0:
                census["nonpositive_size_excluded"] += 1
                continue
            tapes[ticker].append([ts, price, size, line_no, "custody_true_trade"])
            census["positive_size_unique_prints"] += 1
    for tape in tapes.values():
        tape.sort(key=lambda p: (p[0], p[3]))
    return tapes, dict(path=str(path), sha256=digest.hexdigest(), census=dict(census))


def summary(rows):
    out = v1.summarize(rows)
    out["one_sided_failed_favourite"] = sum(r["one_sided_failed_orientation"] == "favourite" for r in rows)
    out["one_sided_failed_underdog"] = sum(r["one_sided_failed_orientation"] == "underdog" for r in rows)
    out["neither_filled"] = sum(not r["fills"] for r in rows)
    return out


def matched(rows, base):
    both = [(r, b0) for r, b0 in zip(rows, base) if r["completed"] and b0["completed"]]
    fills = [(r["fills"][leg], b0["fills"][leg]) for r, b0 in zip(rows, base)
             for leg in sorted(r["fills"].keys() & b0["fills"].keys())]
    delta = lambda key: mean(r[key]-b0[key] for r, b0 in zip(rows, base))
    a, z = summary(rows), summary(base)
    return dict(eligible=len(rows), completion_rate_delta=delta("completed"), captured_per_eligible_delta=delta("captured_cents"),
        median_captured_per_eligible_delta=a["median_captured_eligible"]-z["median_captured_eligible"],
        jointly_completed_pairs=len(both), mean_captured_joint_delta=mean(r["captured_cents"]-b0["captured_cents"] for r,b0 in both) if both else None,
        median_captured_joint_delta=median(r["captured_cents"]-b0["captured_cents"] for r,b0 in both) if both else None,
        one_sided_rate_delta=delta("one_sided"), stepped_off_share_delta=delta("stepped_off"),
        jointly_filled_sides=len(fills), mean_fill_minutes_to_bell_delta_joint=mean(f["minutes_to_bell"]-g["minutes_to_bell"] for f,g in fills) if fills else None,
        safety_violation_delta=sum(a["safety_violations"].values())-sum(z["safety_violations"].values()))


def verify_fills(result, tapes):
    """Independent interval audit of every fill AND miss, positive size only."""
    for leg in result["rests_at_bell"]:
        tape = np.asarray([p[:4] for p in tapes[leg]], dtype=float).reshape((-1, 4))
        actions = [a for a in result["actions"] if a["leg"] == leg]
        expected = None
        for i, action in enumerate(actions):
            if action["new_cents"] is None:
                continue
            start = np.searchsorted(tape[:, 0], action["epoch"], side="right")
            stop = np.searchsorted(tape[:, 0], actions[i+1]["epoch"], side="right") if i+1 < len(actions) else len(tape)
            interval = tape[start:stop]
            valid = np.flatnonzero((interval[:, 0] >= result["formation_epoch"]) & (interval[:, 0] < result["bell_epoch"])
                                  & (interval[:, 1] <= action["new_cents"]) & (interval[:, 2] > 0))
            if len(valid):
                p = interval[valid[0]]
                expected = (p[0], action["new_cents"], p[1], p[2], int(p[3]))
                break
        fill = result["fills"].get(leg)
        actual = (fill["epoch"], fill["cents"], fill["print_cents"], fill["size"], fill["print_rowid"]) if fill else None
        if expected != actual:
            raise ValueError("INDEPENDENT_FILL_AUDIT_MISMATCH:" + result["event_id"] + ":" + leg)


def write_json(path, payload):
    path.write_text(json.dumps(v1.clean(payload), indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8", newline="\n")


def run(args):
    root = args.repo_root
    bound = v1.bound_inputs(root)
    helper = v1.verify_reference(b, root)
    contract = bound["receipt"]["organ_contract"]
    spec = dict(bound["conduct"], positive_size_fills=True)
    durable = root / "arb-executor/data/durable"
    library = durable / "RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz"
    counts = durable / "RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz"
    library_sha = v1.sha256(library)
    if library_sha != bound["receipt"]["input_library"]["sha256"]:
        raise ValueError("LIBRARY_NOT_FILED_BASELINE")
    print("LOAD_LIBRARY", flush=True)
    pairs, census, _, count_provenance = b.load_tick_library(library, {}, counts)
    wanted = bound["scoreboard"]["categories"]["ATP_MAIN"]["query_event_ids"]
    queries = [p for p in pairs if p.event_id in set(wanted)]
    if sorted(p.event_id for p in queries) != sorted(wanted):
        raise ValueError("ELIGIBLE_DENOMINATOR_MISMATCH")
    input_receipt_path = args.prints.with_suffix(".receipt.json")
    input_receipt = json.loads(input_receipt_path.read_text())
    input_sha = v1.sha256(args.prints)
    if input_sha != input_receipt["output_sha256"] or library_sha != input_receipt["library_sha256"]:
        raise ValueError("EXTRACT_HASH_MISMATCH")
    tapes = {}
    with gzip.open(args.prints, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["ticker"] in tapes:
                raise ValueError("DUPLICATE_EXTRACT_LEG")
            tapes[row["ticker"]] = row
    print_rows = sum(len(t["prints"]) for t in tapes.values())
    if (len(tapes), print_rows, args.prints.stat().st_size) != (input_receipt["legs"], input_receipt["true_prints"], input_receipt["output_bytes"]):
        raise ValueError("EXTRACT_SIZE_OR_COUNT_MISMATCH")
    projector = ReceiptProjector(pairs, contract, args.batch_size)
    legacy = v1.FirstProjector(b, pairs, contract)
    args.out.mkdir(parents=True, exist_ok=True)
    results = {mode: {rule: [] for rule in v1.RULES_V2} for mode in MODES}
    progress_counts = Counter()
    began = time.monotonic()
    done = 0
    forecasts_path = args.out / "FIRST_FORECASTS.jsonl.gz"
    query_path = args.out / "CONDUCT_QUERIES.jsonl.gz"
    with ExitStack() as stack:
        raw = stack.enter_context(forecasts_path.open("wb"))
        zipped = stack.enter_context(gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0))
        query_raw = stack.enter_context(query_path.open("wb"))
        query_zip = stack.enter_context(gzip.GzipFile(filename="", mode="wb", fileobj=query_raw, mtime=0))
        for query in queries[:args.limit] if args.limit else queries:
            own_tapes = {}
            for leg in query.legs:
                t = tapes[query.event_id+"-"+leg.leg_id]
                if (t["formation_end_epoch"], t["bell_epoch"]) != (leg.formation, leg.bell):
                    raise ValueError("PRINT_SPAN_MISMATCH")
                own_tapes[leg.leg_id] = t["prints"]
            old_forecast = legacy.project(query)
            for mode in MODES:
                forecast = projector.project(query, mode)
                again_forecast = projector.project(query, mode)
                if v1.encode(v1.clean(forecast)) != v1.encode(v1.clean(again_forecast)):
                    raise ValueError("PROJECTION_NONDETERMINISM")
                if mode == "GATE-SIM":
                    compare_forecasts(old_forecast, forecast)
                progress_counts[mode] += len(forecast)
                zipped.write((v1.encode(v1.clean(dict(event_id=query.event_id, mode=mode, receipts=forecast)))+"\n").encode())
                for rule in range(len(v1.RULES_V2)):
                    r = v1.simulate_conduct(query.event_id, [l.leg_id for l in query.legs], forecast, own_tapes, query.formation, query.bell, spec, rule)
                    again = v1.simulate_conduct(query.event_id, [l.leg_id for l in query.legs], forecast, own_tapes, query.formation, query.bell, spec, rule)
                    if v1.encode(v1.clean(r)) != v1.encode(v1.clean(again)):
                        raise ValueError("CONDUCT_NONDETERMINISM")
                    verify_fills(r, own_tapes)
                    query_zip.write((v1.encode(v1.clean(dict(mode=mode, **r)))+"\n").encode())
                    compact = {k:v for k,v in r.items() if k not in ("actions", "joint_decisions", "stepped_off_exposures")}
                    compact.update(action_count=len(r["actions"]), joint_receipt_count=len(r["joint_decisions"]),
                                   full_decision_artifact=query_path.name)
                    results[mode][v1.RULES_V2[rule]].append(compact)
            done += 1
            elapsed = time.monotonic()-began
            print("PROGRESS " + v1.encode(dict(queries_done=done, total=len(queries), elapsed_seconds=elapsed,
                eta_seconds=elapsed/done*(len(queries)-done), receipts=dict(progress_counts))), flush=True)
    if args.limit:
        write_json(args.out/"SMOKE.json", {mode: {rule: summary(rows) for rule,rows in values.items()} for mode,values in results.items()})
        print("SMOKE_COMPLETE", flush=True)
        return
    print("LOAD_NAMED", flush=True)
    named_pairs, named_sources = b.load_named_inputs(root, {}, args.tape_dir, args.named_prints, second_close=True)
    named_tapes, positive_provenance = positive_named_tapes(args.named_prints, named_pairs)
    if positive_provenance["sha256"] != named_sources["sources"]["true_prints"]["sha256"]:
        raise ValueError("NAMED_PRINT_SOURCE_CHANGED")
    named = {}
    for query in named_pairs:
        face_path = root/"window1-watch/data"/(query.event_id+".face.json")
        face = json.loads(face_path.read_text(encoding="utf-8"))
        truth = face.get("rulers", {}).get("effective_truth", face["truth"])
        formation = max(query.formation, truth["span_start_epoch"])
        bell = truth["bell_epoch"]
        own_tapes = {l.leg_id: [p for p in named_tapes[query.event_id+"-"+l.leg_id] if p[0] <= truth["span_end_epoch"]] for l in query.legs}
        for l in query.legs:
            actual = [(p[0],p[1]) for p in own_tapes[l.leg_id] if l.formation <= p[0] < l.bell]
            expected = list(zip(l.trade_epoch, l.trade_price))
            expected = [(float(t),float(p)) for t,p in expected if t <= truth["span_end_epoch"]]
            if actual != expected:
                raise ValueError("NAMED_RAW_ADAPTER_DIFFERS_FROM_REFERENCE:"+l.leg_id)
        record = dict(baseline_bell_epoch=query.bell, corrected_bell_epoch=bell,
            corrected_span_start_epoch=truth["span_start_epoch"], corrected_span_end_epoch=truth["span_end_epoch"],
            corrections_commit=truth.get("corrections_commit"), truth_row_sha256=truth["row_sha256"],
            face_sha256=v1.sha256(face_path), modes={})
        for mode in MODES:
            forecasts = projector.project(query, mode)
            if mode == "GATE-SIM":
                compare_forecasts(legacy.project(query), forecasts)
            rows = {}
            for rule in range(len(v1.RULES_V2)):
                r = v1.simulate_conduct(query.event_id, [l.leg_id for l in query.legs], forecasts, own_tapes, formation, bell, spec, rule)
                again = v1.simulate_conduct(query.event_id, [l.leg_id for l in query.legs], forecasts, own_tapes, formation, bell, spec, rule)
                if v1.encode(v1.clean(r)) != v1.encode(v1.clean(again)):
                    raise ValueError("NAMED_NONDETERMINISM")
                verify_fills(r, own_tapes)
                rows[v1.RULES_V2[rule]] = r
            record["modes"][mode] = dict(receipts=len(forecasts), rules=rows)
        named[query.event_id] = record
    tables = {mode: {rule: summary(rows) for rule,rows in values.items()} for mode,values in results.items()}
    deltas = {mode: {rule: matched(rows,values[v1.RULES_V2[0]]) for rule,rows in values.items()} for mode,values in results.items()}
    write_json(args.out/"CONDUCT_SCOREBOARD.json", dict(summary=tables, matched_deltas=deltas, queries=results))
    write_json(args.out/"CONDUCT_NAMED_CHECKS.json", named)
    receipt = dict(status="BENCH ONLY — REACHABLE, NEVER CERTAIN", baseline=bound["provenance"],
        scripts={str(Path(p).name): v1.sha256(p) for p in (__file__, v1.__file__, b.__file__)},
        no_engine_edit=bound["conduct"], library_sha256=library_sha, count_sidecar=count_provenance,
        reference_check=helper, eligible_query_pairs=len(queries), receipt_counts=dict(progress_counts),
        print_extract=dict(path=str(args.prints), sha256=input_sha, bytes=args.prints.stat().st_size,
            jsonl_leg_rows=len(tapes), accepted_print_rows=print_rows,
            positive_size_prints=sum(p[2]>0 for t in tapes.values() for p in t["prints"]),
            nonpositive_size_prints=sum(p[2]<=0 for t in tapes.values() for p in t["prints"]),
            receipt_sha256=v1.sha256(input_receipt_path), raw_prints_committed=False),
        named_sources=named_sources, positive_named_adapter=positive_provenance,
        determinism="Every query/mode forecast computed twice; every query and named rule simulated twice; canonical bytes identical.",
        validation="Every query gate projection equals the c7825925-equivalent v1 projector; independent positive-size interval audit verifies every fill and miss for both cadences/all seven rules/five named checks.",
        definitions=DEFINITIONS,
        performance=dict(batch_size=args.batch_size, batch_size_is_memory_only=True, elapsed_seconds=time.monotonic()-began))
    lines = report(tables, deltas, named)
    (args.out/"CONDUCT_SUMMARY.md").write_text(lines, encoding="utf-8", newline="\n")
    receipt["outputs"] = {p.name: dict(bytes=p.stat().st_size, sha256=v1.sha256(p)) for p in
        (args.out/"CONDUCT_SCOREBOARD.json", args.out/"CONDUCT_NAMED_CHECKS.json", forecasts_path, query_path, args.out/"CONDUCT_SUMMARY.md")}
    if v1.bound_inputs(root)["conduct"] != bound["conduct"]:
        raise ValueError("ENGINE_CHANGED_DURING_BENCH")
    write_json(args.out/"CONDUCT_RECEIPT.json", receipt)
    print(lines, flush=True)


def compare_forecasts(old, new):
    if len(old) != len(new):
        raise ValueError("GATE_COUNT_MISMATCH")
    for a,z in zip(old,new):
        if a["epoch"] != z["epoch"] or v1.clean(a["sides"]) != v1.clean(z["sides"]):
            raise ValueError("GATE_BASELINE_MISMATCH:"+str(a["source_gate_minutes"]))


DEFINITIONS = dict(
    fill="First later accepted true print with finite size > 0 and price <= standing bid; native ts strictly exceeds latest placement/reprice; formation <= ts < corrected bell and inside verified span. Fill at bid, queue unknown. Zero-size prints remain library observations but never fill or stepped-off witnesses.",
    cadence="RECEIPT-SIM = union of both original library-leg change-point timestamps plus the OS atlas-gate receipts, after the first both-leg observation and before bell. No synthetic pre-first-tick order. GATE-SIM retains only the 15 filed gates that lie inside the span. Own data sampled as-of receipt; historical members aligned by minutes to bell.",
    receipt_limitation="Second-close library cadence is not a byte-for-byte engine replay: individual BOOK/PRINT receipt ids and intra-second book ordering are absent. The ask-only veto is reconstructed when only ask changes with unchanged last/bid and no count increment; coincident atlas gates are unconditional gate receipts. FIRST only as the scoreboard order, not the installed BASE fallback. No claim of exact installed-fill equality.",
    current="R0: FIRST q50 at each receipt where postable, otherwise existing safety hold/pull. Q/X inherit c7825925, including carried-state remaining minima; no future query timestamps used to predict.",
    R1="CLIMBER-ANCHOR: first receipt calling CLIMBER binds stored own seen_true_trade_low forever; faller otherwise R0. No future low lookup.",
    R2="NAMED-LEVEL: faller never steps below its highest actually posted level; may move up. Memory survives safety cancellation; climber otherwise R0.",
    R3="R1 + R2; a bound climber anchor takes priority even through later role flips.",
    R4="R3, except unanchored faller takes FIRST q25 instead of q50 before the same no-downward protection.",
    R5="JOINT: FIRST side-mask intersection, original w0 counted once per pair, existing ESS floor required. Historical remaining minima translated by own current last minus member current last. Candidates are observed paired levels only, not a Cartesian product. Probability is sum w0 of pairs whose BOTH minima <= proposed levels / total joint w0. Maximize probability * (par - pair sum) among valid-cent/postable/pair-cap/R2-feasible candidates. Exact objective ties: lower sum, then lower favourite level. After one fill its price is fixed and only the other level varies; same joint outcomes/denominator. No feasible candidate means hold; safety may still pull. These definitions explicitly approved by operator.",
    R5_limitation="Probability is an empirical remaining-path-minimum model, includes carried state and size-zero observed prices as inherited from FIRST; actual conduct credit separately requires a strictly future size-positive print. Reachable is not certain.",
    R6="R0 plus no-downward protection on BOTH sides regardless of role, unlike faller-only R2. Highest posted-level memory persists through cancellations; post-only and pair cap always override.",
    guards="Unchanged integer-cent validation, locked-book hold, insufficient-authority hold, ask-only veto/rearm, post-only hold/pull, joint budget veto including credited side. A modified rule cannot override any guard. No execution code imported or changed.",
    joint_insufficient="Joint ESS uses the filed no_call_ess_floor, not counts after collapsing equal candidate pairs; below that floor R5 cannot originate/reprice an order.",
    outcomes="Completion needs both prebell fills; incomplete/one-sided pairs get zero captured credit. Failed side is favourite/underdog orientation plus the stored leg id. All 928 eligible pairs remain denominators regardless of calls/fills.",
    stepped_off="Faller down-reprice followed by any strictly later prebell positive-size print with new < print <= old, counted once per pair. Strict while-lower-order-active subset also reported; neither awards fill credit.",
    named_clock="Named Q/X use the baseline query bell/formation at their original absolute times. Conduct bounds use corrected truth spans/bell; no forecast shifted into the past by a bell correction. This retains the v1 baseline rather than silently reforecasting named checks on another clock.",
    constants="No tuned prices or thresholds. Existing budget/par/cent bounds read from unchanged engine text; ESS/role/gates/quantiles from filed c7825925 organ contract. Batch size controls memory only.")


def report(tables, deltas, named):
    f = lambda x: "—" if x is None else f"{x:.3f}"
    lines = ["# Conduct scoreboard v2", "", "Size-positive reachable fills; queue unknown. FIRST-only, all 928 eligible pairs. No engine replay or edit.", "",
             "RECEIPT-SIM uses both-leg change points plus atlas receipts. GATE-SIM is the separately retained 15-gate simulation.", ""]
    for key,value in DEFINITIONS.items():
        if key in ("current","R1","R2","R3","R4","R5","R6","receipt_limitation"):
            lines.append(f"- {key}: {value}")
    for mode in MODES:
        lines += ["", "## "+mode, "", "| Rule | Completed / eligible | Completion | Capture mean / median completed | Capture mean / median eligible | One-sided (fav failed / dog failed) | Stepped off | Mean fill→bell m | Safety |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for rule,r in tables[mode].items():
            lines.append(f"| {rule} | {r['completed']} / {r['eligible']} | {r['completion_rate']:.2%} | {f(r['mean_captured_completed'])} / {f(r['median_captured_completed'])} | {f(r['mean_captured_eligible'])} / {f(r['median_captured_eligible'])} | {r['one_sided']} ({r['one_sided_failed_favourite']} / {r['one_sided_failed_underdog']}) | {r['stepped_off_pairs']} ({r['stepped_off_share']:.2%}) | {f(r['mean_fill_minutes_to_bell'])} | {sum(r['safety_violations'].values())} |")
        lines += ["", "### Matched deltas vs R0", "", "| Rule | Δ completion pp | Δ capture / eligible | Joint completions | Δ capture mean / median joint | Δ one-sided pp | Δ stepped-off pp | Joint filled sides | Δ fill→bell m joint |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for rule,r in deltas[mode].items():
            lines.append(f"| {rule} | {r['completion_rate_delta']*100:.3f} | {f(r['captured_per_eligible_delta'])} | {r['jointly_completed_pairs']} | {f(r['mean_captured_joint_delta'])} / {f(r['median_captured_joint_delta'])} | {r['one_sided_rate_delta']*100:.3f} | {r['stepped_off_share_delta']*100:.3f} | {r['jointly_filled_sides']} | {f(r['mean_fill_minutes_to_bell_delta_joint'])} |")
    lines += ["", "## Five named checks", "", "Fills are resting bid cents; dash = no reachable fill. Every incomplete pair is credited zero.", "", "| Game | Rule | RECEIPT-SIM fills; captured | GATE-SIM fills; captured | Failed legs RECEIPT / GATE |", "|---|---|---|---|---|"]
    for event,record in named.items():
        for rule in v1.RULES_V2:
            texts, failed = [], []
            for mode in MODES:
                r = record["modes"][mode]["rules"][rule]
                texts.append(", ".join(f"{leg} {r['fills'][leg]['cents']:g}" if leg in r["fills"] else f"{leg} —" for leg in r["rests_at_bell"])+f"; {r['captured_cents']:g}¢")
                failed.append(",".join(r["failed_sides"]) or "none")
            lines.append(f"| {event.split('-')[-1]} | {rule} | {texts[0]} | {texts[1]} | {' / '.join(failed)} |")
    return "\n".join(lines)+"\n"


def main():
    if hasattr(sys.stdout,"reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--prints", type=Path, required=True)
    p.add_argument("--tape-dir", type=Path, default=Path(r"C:\Users\omigr\OMI-Window1-private\fit-local\ticks"))
    p.add_argument("--named-prints", type=Path, default=Path(r"C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl"))
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--batch-size", type=int, default=256, help="Memory batching only, never a model parameter")
    p.add_argument("--limit", type=int, help="Smoke only; does not publish a receipt")
    run(p.parse_args())


if __name__ == "__main__":
    main()
