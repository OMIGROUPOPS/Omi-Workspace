#!/usr/bin/env python3
"""Signed sentence experiments; imports bench helpers, never the engine.

Raw prints stay outside git. Reuses the hash-bound conduct v2 archives. All
changes are experimental projections; no OS, face, or historical output edits.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
import conduct_scoreboard as c
import conduct_scoreboard_v2 as cv2
import tune_bench_v2_survivorship as b

VARIANTS = ("CURRENT_ROLE", "NO_ROLE", "SHARED_INTERSECTION")
SIDES = ("favourite", "underdog")


def write(path, value):
    path.write_text(json.dumps(c.clean(value), indent=2, sort_keys=True, allow_nan=False)+"\n",
                    encoding="utf-8", newline="\n")


def average(values):
    values = [float(v) for v in values if v is not None and math.isfinite(v)]
    return sum(values)/len(values) if values else None


def distribution(values, quantiles):
    values = np.asarray([v for v in values if v is not None and math.isfinite(v)], dtype=float)
    return dict(n=len(values), mean=average(values), quantiles={str(q):
        float(b.inverse_weighted_quantile(values, np.ones(len(values)), q)) if len(values) else None
        for q in quantiles})


def iter_jsonl(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def positive_tape(rows, formation, bell):
    return np.asarray([[p[0], p[1]] for p in rows
                       if formation <= p[0] < bell and c.finite(p[2]) and p[2] > 0], dtype=float).reshape(-1, 2)


def future_floor(tape, epoch, bell, seconds):
    valid = tape[(tape[:, 0] > epoch) & (tape[:, 0] < bell)]
    if not len(valid):
        return None, None
    i = int(np.argmin(valid[:, 1]))
    return float(valid[i, 1]), float((bell-valid[i, 0])/seconds)


def first_passage(tape, epoch, bell, level, seconds):
    """Strictly later size-positive accepted native prints; bid/downward target."""
    valid = np.flatnonzero((tape[:, 0] > epoch) & (tape[:, 0] < bell) & (tape[:, 1] <= level))
    return float((bell-tape[valid[0], 0])/seconds) if len(valid) else None


def censored_median(hit_mtb, weights, gate, quantile):
    """Invert elapsed-time CDF with non-hits at +infinity, never drop their mass."""
    hit = np.isfinite(hit_mtb)
    total = weights.sum()
    if total <= 0:
        return None
    elapsed = np.where(hit, gate-hit_mtb, np.inf)
    order = np.argsort(elapsed, kind="stable")
    i = int(np.searchsorted(np.cumsum(weights[order]), quantile*total, side="left"))
    value = elapsed[order[min(i, len(order)-1)]]
    return float(gate-value) if np.isfinite(value) else None


def win_record(new_errors, old_errors, criterion):
    pairs = [(a, z) for a, z in zip(new_errors, old_errors) if a is not None and z is not None]
    n = len(pairs)
    wins = sum(a < z for a, z in pairs)
    return dict(n=n, new_mae=average(a for a, z in pairs), baseline_mae=average(z for a, z in pairs),
                delta_mae=average(a-z for a, z in pairs), strictly_closer=wins,
                ties=sum(a == z for a, z in pairs), strictly_closer_share=wins/n if n else None,
                filed_matched_win=bool(n >= criterion["minimum_matched_queries"] and
                    wins >= criterion["minimum_step_strictly_closer_share"]*n))


def guard_diagnostics(forecasts, result, spec):
    """Reconstruct R0 holds from archived state/actions; assert every action agrees.

    Earlier fills are observations, not forecast inputs. No new conduct rule.
    This exposes omitted HOLD reasons without modifying the frozen simulator.
    """
    legs = list(forecasts[0]["sides"]) if forecasts else list(result["rests_at_bell"])
    active = {l: None for l in legs}
    prior = {}
    counts = {l: Counter() for l in legs}
    ready = Counter()
    changes = defaultdict(dict)
    for a in result["actions"]:
        changes[a["epoch"]][a["leg"]] = a["new_cents"]
    def cent(v):
        return c.finite(v) and v == int(v) and spec["minimum_cent"] <= v <= spec["maximum_cent"]
    for row in forecasts:
        ts = row["epoch"]
        fills = {l: f for l, f in result["fills"].items() if f["epoch"] <= ts}
        proposals, why = {}, {}
        for l in legs:
            if l in fills:
                active[l] = None
                proposals[l], why[l] = None, "ALREADY_FILLED"
                continue
            s = row["sides"][l]
            q = s.get("floors", {}).get("q50", {}).get("level_cents")
            ask, bid, old = s["ask"], s["bid"], active[l]
            postable = cent(q) and cent(ask) and q < ask
            if s["status"] == "OK" and postable and not (c.finite(bid) and bid >= ask):
                ready[l] += 1
            before = prior.get(l, {})
            became = postable and before.get("target") == q and before.get("postable") is False
            prior[l] = dict(target=q, postable=postable)
            if c.finite(bid) and c.finite(ask) and bid >= ask:
                proposals[l], why[l] = old, "LOCKED_BOOK_HOLD"
            elif s["status"] != "OK" or not cent(q):
                proposals[l], why[l] = old, "INSUFFICIENT_AUTHORITY_HOLD"
            elif row.get("ask_only_book_tick", False) and not became:
                proposals[l], why[l] = old, "ASK_ONLY_BOOK_HOLD"
            elif not cent(ask) or q >= ask:
                proposals[l] = old if old is not None and cent(ask) and old <= ask else None
                why[l] = "POST_ONLY_HOLD_OR_PULL"
            else:
                proposals[l], why[l] = q, "RULE_TARGET_POSTABLE"
        total = sum(fills[l]["cents"] if l in fills else (proposals[l] or 0) for l in legs)
        if total > spec["pair_budget"]:
            for l in legs:
                proposals[l], why[l] = active[l], "PAIR_CAP_HOLD"
        for l in legs:
            expected = changes.get(ts, {}).get(l, active[l])
            if expected != proposals[l]:
                raise ValueError("GUARD_RECONSTRUCTION_DIFFERS_FROM_R0:"+result["event_id"]+":"+l)
            active[l] = expected
            counts[l][why[l]] += 1
    return {l: dict(reasons=dict(counts[l]), postable_receipts=ready[l]) for l in legs}


def autopsy(query, result, forecasts, positive, contract, spec):
    gates = [r for r in forecasts if r["receipt_kind"] == "ATLAS_GATE"]
    last = gates[-1] if gates else None
    guards = guard_diagnostics(forecasts, result, spec)
    out = []
    for i, leg in enumerate(query.legs):
        state = last["sides"][leg.leg_id] if last else {}
        q = state.get("floors", {}).get("q50", {}).get("level_cents")
        carried = b.remaining_floor(leg, last["source_gate_minutes"]) if last else (None, None)
        floor, floor_time = future_floor(positive[leg.leg_id], last["epoch"], query.bell,
                                        contract["minute_seconds"]) if last else (None, None)
        actions = [a for a in result["actions"] if a["leg"] == leg.leg_id]
        moved, moved_active = [], []
        for j, a in enumerate(actions):
            old, new = a["old_cents"], a["new_cents"]
            if old is None or new is None or new >= old:
                continue
            tape = positive[leg.leg_id]
            hits = tape[(tape[:, 0] > a["epoch"]) & (tape[:, 1] > new) & (tape[:, 1] <= old)]
            if len(hits):
                moved.append(dict(epoch=a["epoch"], old=old, new=new, role=a["role"],
                                  witness_epoch=float(hits[0, 0]), witness_price=float(hits[0, 1])))
                end = actions[j+1]["epoch"] if j+1 < len(actions) else query.bell
                fill = result["fills"].get(leg.leg_id)
                if fill: end = min(end, fill["epoch"])
                if hits[0, 0] <= end:
                    moved_active.append(moved[-1])
        group = ("completed_control" if result["completed"] else "no_fill_control" if not result["fills"]
                 else "filled_side_control" if leg.leg_id in result["fills"] else "one_sided_failed")
        out.append(dict(event_id=query.event_id, side=SIDES[i], leg=leg.leg_id, group=group,
            last_gate=last["source_gate_minutes"] if last else None, last_gate_status=state.get("status"),
            last_gate_role=state.get("role"), q=q, carried_remaining_floor=carried[0],
            positive_future_floor=floor, positive_floor_mtb=floor_time,
            q_minus_carried_floor=q-carried[0] if q is not None else None,
            q_minus_positive_floor=q-floor if q is not None and floor is not None else None,
            never_postable=guards[leg.leg_id]["postable_receipts"] == 0,
            guards=guards[leg.leg_id], placements=len(actions), moved_off_later_print=moved,
            moved_off_while_lower_active=moved_active,
            legacy_faller_stepped_off=any(e["leg"] == leg.leg_id and e["any_later_print"]
                                         for e in result["stepped_off_exposures"])))
    return out


def autopsy_summary(rows, contract):
    out = {}
    for group in sorted(set(r["group"] for r in rows)):
        out[group] = {}
        for side in SIDES:
            part = [r for r in rows if r["group"] == group and r["side"] == side]
            out[group][side] = dict(n=len(part),
                last_gate_roles=dict(Counter(r["last_gate_role"] for r in part)),
                q_minus_positive_floor=distribution([r["q_minus_positive_floor"] for r in part], contract["quantiles"]),
                q_minus_carried_floor=distribution([r["q_minus_carried_floor"] for r in part], contract["quantiles"]),
                no_call=sum(r["q"] is None for r in part),
                no_later_positive_print=sum(r["positive_future_floor"] is None for r in part),
                too_deep=sum(r["q_minus_positive_floor"] is not None and r["q_minus_positive_floor"] < 0 for r in part),
                never_postable=sum(r["never_postable"] for r in part),
                moved_off_later_print=sum(bool(r["moved_off_later_print"]) for r in part),
                moved_off_while_lower_active=sum(bool(r["moved_off_while_lower_active"]) for r in part),
                legacy_faller_stepped_off=sum(r["legacy_faller_stepped_off"] for r in part),
                pair_cap_ever=sum(r["guards"]["reasons"].get("PAIR_CAP_HOLD", 0) > 0 for r in part),
                guards_receipt_counts=dict(sum((Counter(r["guards"]["reasons"]) for r in part), Counter())))
    return out


class GateExperiments:
    def __init__(self, pairs, contract, tapes):
        self.pairs, self.c, self.tapes = pairs, contract, tapes
        self.projector = c.FirstProjector(b, pairs, contract)
        self.passages = {}

    def hits(self, member, gate, side, delta, current):
        key = (member.event_id, gate, side, float(delta))
        if key not in self.passages:
            leg = member.legs[side]
            self.passages[key] = first_passage(self.tapes[member.event_id][leg.leg_id],
                member.bell-gate*self.c["minute_seconds"], member.bell, current+delta,
                self.c["minute_seconds"])
        value = self.passages[key]
        return np.nan if value is None else value

    def project(self, query, baseline):
        members, w0 = b.initial_pool(query, self.pairs)
        output, e1 = [], []
        variants = {v: [] for v in VARIANTS}
        for receipt in baseline:
            gate, epoch = receipt["source_gate_minutes"], receipt["epoch"]
            pool, current, roles, floors, lookup = self.projector.category_gate(query.category, gate)
            ix = np.asarray([lookup[m.event_id] for m in members], dtype=int)
            available, filtered = [], []
            for side, leg in enumerate(query.legs):
                mask = np.all(np.isfinite(current[ix, side*3:side*3+3]), axis=1)
                mask &= np.asarray([m.first_mtb >= gate for m in members], dtype=bool)
                own_role = receipt["sides"][leg.leg_id]["role"]
                available.append(mask)
                filtered.append(mask & ((roles[ix, side] == own_role) | (own_role == "NOT_CALLABLE")))
            both = filtered[0] & filtered[1]
            for variant in VARIANTS:
                row = deepcopy(receipt)
                row.pop("joint", None)
                for side, leg in enumerate(query.legs):
                    state = row["sides"][leg.leg_id]
                    mask = available[side] if variant == "NO_ROLE" else both if variant == "SHARED_INTERSECTION" else filtered[side]
                    weights = w0*mask
                    ess = float(b.ess(weights) or 0)
                    state.pop("floors", None)
                    state.update(ess=ess, member_count=int(np.count_nonzero(weights)), status="INSUFFICIENT_EVIDENCE")
                    family = None
                    if ess >= self.c["no_call_ess_floor"]:
                        active = weights > 0
                        delta = floors[ix, side, 0]-current[ix, side*3]
                        state.update(status="OK", floors={})
                        for quantile in ("q25", "q50", "q75"):
                            fraction = float(quantile[1:])/100
                            state["floors"][quantile] = dict(level_cents=float(state["last"]+
                                b.inverse_weighted_quantile(delta[active], weights[active], fraction)),
                                minutes_to_bell=float(b.inverse_weighted_quantile(floors[ix, side, 1][active], weights[active], fraction)))
                        mass = Counter()
                        for member, weight in zip(members, weights):
                            if weight > 0: mass[member.legs[side].family] += float(weight)
                        family = min(mass, key=lambda name: (-mass[name], name))
                    original = receipt["sides"][leg.leg_id]
                    if variant == "CURRENT_ROLE":
                        for key in ("status", "ess", "member_count", "floors"):
                            if state.get(key) != original.get(key):
                                raise ValueError("BASELINE_GATE_MISMATCH:"+query.event_id+":"+str(gate)+":"+key)
                    truth = b.remaining_floor(leg, gate)
                    pos_floor, pos_time = future_floor(self.tapes[query.event_id][leg.leg_id], epoch,
                                                       query.bell, self.c["minute_seconds"])
                    qx = state.get("floors", {}).get("q50", {})
                    q, x = qx.get("level_cents"), qx.get("minutes_to_bell")
                    record = dict(event_id=query.event_id, gate=gate, side=SIDES[side], variant=variant,
                        ess=ess, member_count=state["member_count"], status=state["status"], q=q, x=x,
                        role=state["role"], family_called=family, realized_family=leg.family,
                        carried_floor=truth[0], carried_floor_mtb=truth[1], positive_floor=pos_floor, positive_floor_mtb=pos_time,
                        floor_error=abs(q-truth[0]) if q is not None else None,
                        timing_error=abs(x-truth[1]) if x is not None else None,
                        positive_floor_error=abs(q-pos_floor) if q is not None and pos_floor is not None else None,
                        positive_timing_error=abs(x-pos_time) if x is not None and pos_time is not None else None)
                    output.append(record)
                    if variant == "CURRENT_ROLE" and q is not None:
                        active = weights > 0
                        hit = np.asarray([self.hits(m, gate, side, q-state["last"], current[k, side*3])
                                          for m, k, enabled in zip(members, ix, active) if enabled])
                        ws = weights[active]
                        xp = censored_median(hit, ws, gate, .5)
                        actual = first_passage(self.tapes[query.event_id][leg.leg_id], epoch,
                                               query.bell, q, self.c["minute_seconds"])
                        rec = dict(event_id=query.event_id, gate=gate, side=SIDES[side], q=q, x=x, first_passage_x=xp,
                            member_count=len(ws), ess=ess, member_hit_weight_share=float(ws[np.isfinite(hit)].sum()/ws.sum()),
                            nonhit_weight_share=float(ws[~np.isfinite(hit)].sum()/ws.sum()),
                            actual_first_passage_mtb=actual, actual_hit=actual is not None,
                            baseline_deadline_error=abs(x-actual) if actual is not None else None,
                            new_deadline_error=abs(xp-actual) if xp is not None and actual is not None else None)
                        for name, deadline in (("baseline", x), ("new", xp)):
                            p = float(ws[np.isfinite(hit) & (hit >= deadline)].sum()/ws.sum()) if deadline is not None else None
                            y = int(actual is not None and actual >= deadline) if deadline is not None else None
                            rec[name+"_reach_probability"] = p
                            rec[name+"_reached_by_deadline"] = y
                            rec[name+"_brier"] = (p-y)**2 if p is not None else None
                        e1.append(rec)
                variants[variant].append(row)
        return output, e1, variants


def summarize_gates(records, e1, n_queries, contract, criterion):
    out = {}
    for gate in contract["gates_minutes_to_bell"]:
        out[str(gate)] = {}
        for side in SIDES:
            scope = [r for r in records if r["gate"] == gate and r["side"] == side]
            base = {r["event_id"]: r for r in scope if r["variant"] == "CURRENT_ROLE"}
            layers = {}
            for variant in VARIANTS:
                rows = [r for r in scope if r["variant"] == variant]
                calls = [r for r in rows if r["q"] is not None]
                matched = [r for r in calls if base[r["event_id"]]["q"] is not None]
                layers[variant] = dict(all_eligible=n_queries, span_eligible=len(rows), calls=len(calls),
                    coverage_all_eligible=len(calls)/n_queries, abstained=len(rows)-len(calls),
                    before_first_tick=n_queries-len(rows), floor_mae=average(r["floor_error"] for r in calls),
                    timing_mae_minutes=average(r["timing_error"] for r in calls),
                    positive_future_floor_mae=average(r["positive_floor_error"] for r in calls),
                    positive_future_timing_mae=average(r["positive_timing_error"] for r in calls),
                    positive_future_target_n=sum(r["positive_floor"] is not None for r in calls),
                    family_accuracy=average(r["family_called"] == r["realized_family"] for r in calls),
                    matched_floor=win_record([r["floor_error"] for r in matched], [base[r["event_id"]]["floor_error"] for r in matched], criterion),
                    matched_timing=win_record([r["timing_error"] for r in matched], [base[r["event_id"]]["timing_error"] for r in matched], criterion))
            erows = [r for r in e1 if r["gate"] == gate and r["side"] == side]
            finite = [r for r in erows if r["first_passage_x"] is not None]
            layers["E1_FIRST_PASSAGE"] = dict(all_eligible=n_queries, span_eligible=len(base), baseline_calls=len(erows),
                finite_deadlines=len(finite), censored_medians=len(erows)-len(finite),
                coverage_all_eligible=len(finite)/n_queries, query_hits=sum(r["actual_hit"] for r in erows),
                mean_member_nonhit_weight_share=average(r["nonhit_weight_share"] for r in erows),
                matched_deadline=win_record([r["new_deadline_error"] for r in erows], [r["baseline_deadline_error"] for r in erows], criterion),
                baseline_mean_probability=average(r["baseline_reach_probability"] for r in finite),
                baseline_observed_reach=average(r["baseline_reached_by_deadline"] for r in finite),
                new_mean_probability=average(r["new_reach_probability"] for r in finite),
                new_observed_reach=average(r["new_reached_by_deadline"] for r in finite),
                baseline_brier_matched=average(r["baseline_brier"] for r in finite),
                new_brier=average(r["new_brier"] for r in finite),
                delta_brier=average(r["new_brier"]-r["baseline_brier"] for r in finite))
            out[str(gate)][side] = layers
    return out


def run(args):
    root, out = args.root, args.out
    out.mkdir(parents=True, exist_ok=True)
    bound = c.bound_inputs(root)
    c.verify_reference(b, root)
    contract = bound["receipt"]["organ_contract"]
    criterion_path = root/"arb-executor/analysis/tune_bench_v2_ticks/ATP_MAIN/TUNE_BENCH_RECEIPT.json"
    criterion = json.loads(criterion_path.read_text())["matched_step_first"]["criterion"]
    spec = dict(bound["conduct"], positive_size_fills=True)
    durable = root/"arb-executor/data/durable"
    library = durable/"RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz"
    counts = durable/"RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz"
    if c.sha256(library) != bound["receipt"]["input_library"]["sha256"]:
        raise ValueError("LIBRARY_NOT_BASELINE")
    print("LOAD_LIBRARY_AND_PRIVATE_PRINT_EXTRACT", flush=True)
    pairs, census, thresholds, count_source = b.load_tick_library(library, {}, counts)
    pairs = [p for p in pairs if p.category == "ATP_MAIN"]
    wanted = bound["scoreboard"]["categories"]["ATP_MAIN"]["query_event_ids"]
    queries = {p.event_id: p for p in pairs if p.event_id in set(wanted)}
    assert sorted(queries) == sorted(wanted)
    extract = json.loads(args.prints.with_suffix(".receipt.json").read_text())
    assert c.sha256(args.prints) == extract["output_sha256"]
    assert extract["library_sha256"] == c.sha256(library)
    tapes, positive = {}, {}
    raw_count = 0
    outer_count = 0
    for row in iter_jsonl(args.prints):
        raw_count += len(row["prints"])
        outer_count += 1
        event, leg = row["event_id"], row["leg_id"]
        if event not in queries: continue
        obj = next(l for l in queries[event].legs if l.leg_id == leg)
        assert (obj.formation, obj.bell) == (row["formation_end_epoch"], row["bell_epoch"])
        tapes.setdefault(event, {})[leg] = row["prints"]
        positive.setdefault(event, {})[leg] = positive_tape(row["prints"], obj.formation, obj.bell)
    assert (raw_count, outer_count, args.prints.stat().st_size) == (extract["true_prints"], extract["legs"], extract["output_bytes"])
    for pair in pairs:
        for leg in pair.legs:
            leg.family = b.classify_leg(leg, thresholds[pair.category])["family"]
    archive = root/"arb-executor/analysis/conduct_scoreboard_v2/ATP_MAIN"
    archive_receipt = json.loads((archive/"CONDUCT_RECEIPT.json").read_text())
    for name, expected in archive_receipt["scripts"].items():
        assert c.sha256(root/"arb-executor/analysis"/name) == expected
    assert c.sha256(args.prints) == archive_receipt["print_extract"]["sha256"]
    artifacts = {name: c.sha256(archive/name) for name in ("FIRST_FORECASTS.jsonl.gz", "CONDUCT_QUERIES.jsonl.gz", "CONDUCT_RECEIPT.json")}
    # Exact committed archives, not a mutable local run.
    import subprocess
    for name in artifacts:
        blob = subprocess.check_output(["git", "rev-parse", "d2d8f16b:arb-executor/analysis/conduct_scoreboard_v2/ATP_MAIN/"+name], cwd=root).decode().strip()
        actual = subprocess.check_output(["git", "hash-object", str(archive/name)], cwd=root).decode().strip()
        assert actual == blob, name
    results = {(r["event_id"], r["mode"]): r for r in iter_jsonl(archive/"CONDUCT_QUERIES.jsonl.gz") if r["rule"] == c.RULES[0]}
    e3, baselines = [], {}
    began = time.monotonic()
    for row in iter_jsonl(archive/"FIRST_FORECASTS.jsonl.gz"):
        event, mode = row["event_id"], row["mode"]
        if mode == "GATE-SIM":
            baselines[event] = row["receipts"]
        else:
            e3.extend(autopsy(queries[event], results[event, mode], row["receipts"], positive[event], contract, spec))
    e3_summary = autopsy_summary(e3, contract)
    write(out/"E3_AUTOPSY.json", dict(summary=e3_summary, rows=e3))
    print("E3_COMPLETE "+c.encode(e3_summary["one_sided_failed"]), flush=True)
    if args.autopsy_only: return
    projector = GateExperiments(pairs, contract, positive)
    records, e1, conduct = [], [], {v: [] for v in VARIANTS}
    query_digests = []
    for done, event in enumerate(sorted(queries), 1):
        query = queries[event]
        first = projector.project(query, baselines[event])
        second = projector.project(query, baselines[event])
        encoded = c.encode(c.clean(first))
        assert encoded == c.encode(c.clean(second)), "NONDETERMINISTIC_GATE_EXPERIMENT"
        query_digests.append(hashlib.sha256(encoded.encode()).hexdigest())
        rr, ee, projections = first
        records.extend(rr)
        e1.extend(ee)
        for variant, forecast in projections.items():
            simulation = c.simulate_conduct(event, [l.leg_id for l in query.legs], forecast, tapes[event], query.formation, query.bell, spec, 0)
            cv2.verify_fills(simulation, tapes[event])
            if variant == "CURRENT_ROLE":
                assert c.encode(c.clean(simulation)) == c.encode({k:v for k,v in results[event,"GATE-SIM"].items() if k != "mode"}), "R0_GATE_MISMATCH"
            conduct[variant].append({k:v for k,v in simulation.items() if k not in ("actions", "joint_decisions", "stepped_off_exposures")})
        if done % 50 == 0 or done == len(queries):
            print("PROGRESS "+c.encode(dict(queries=done, total=len(queries), elapsed=time.monotonic()-began)), flush=True)
    table = summarize_gates(records, e1, len(queries), contract, criterion)
    write(out/"GATE_TABLES.json", table)
    write(out/"E1_FIRST_PASSAGE.json", dict(rows=e1))
    with (out/"GATE_RECORDS.jsonl.gz").open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
        for r in records: gz.write((c.encode(c.clean(r))+"\n").encode())
    write(out/"GATE_CONDUCT.json", dict(cadence="GATE-SIM, not RECEIPT-SIM; same cadence for baseline and candidates",
        summary={v: cv2.summary(rr) for v,rr in conduct.items()},
        matched={v: cv2.matched(rr, conduct["CURRENT_ROLE"]) for v,rr in conduct.items()}, queries=conduct))
    receipt = dict(status="BENCH_ONLY_SIGNED_AMENDMENTS", baseline=bound["provenance"], conduct_commit="d2d8f16b",
        scripts={Path(p).name: c.sha256(p) for p in (__file__, c.__file__, cv2.__file__, b.__file__)},
        engine_hashes_unchanged=bound["conduct"], archives=artifacts, library_sha256=c.sha256(library),
        count_sidecar=count_source, print_extract=dict(sha256=c.sha256(args.prints), receipt_sha256=c.sha256(args.prints.with_suffix(".receipt.json")),
            outer_rows=outer_count, accepted_print_rows=raw_count, positive_size_prints=archive_receipt["print_extract"]["positive_size_prints"], raw_prints_committed=False),
        eligible_pairs=len(queries), atlas_contract=contract, matched_win_criterion=criterion,
        matched_win_source=dict(path=str(criterion_path), sha256=c.sha256(criterion_path)),
        order=["E3", "E1", "E2a_NO_ROLE_vs_E2b_CURRENT_ROLE", "E4a_SHARED_INTERSECTION"],
        deferred={"E2c":"No filed causal family learner/weighting or callability criterion supplied. Not implemented or scored.",
                  "E4_equal_opposite":"Not run: joint minima need not be simultaneous; amplitude and constraint-selection estimator unspecified."},
        definitions={
            "E3":"Last scheduled atlas gate, no last-call selection. Q minus carried remaining floor AND strictly-later positive-size future-print floor. No-call/no-print retained. Causes overlap. Moved-off reported all roles and original FALLER-only subset, plus active-order interval subset. R0 guards reconstructed from archived actions and every proposal asserted identical.",
            "E1":"Original CURRENT_ROLE Q, weights, member mask fixed. For each member target=its gate last+(query Q-query gate last). First later accepted positive-size print <=target before member bell. Non-hits retained at infinite elapsed time. Median elapsed uses all weights; if infinite, deadline censored. Same bell-relative minute clock. Actual query first passage is scoring-only. Current and new X errors target the same first passage; MAE conditional on query hit and finite new median. Censor and all-eligible denominators explicit.",
            "E1_calibration":"For each deadline use empirical weighted share of member first passages before that deadline, versus query binary reach; report Brier and mean predicted/observed reach on matched finite-X cohort. Different horizons: not a pure fixed-horizon calibration superiority test. No calibration promotion threshold invented.",
            "E2":"Availability/finite books, w0, walk-forward, self/same-day/category exclusions and ESS floor unchanged; only receipt-time role mask removed in NO_ROLE.",
            "E4a":"Both original side masks intersect; original w0 used once per shared member for both marginal Q/X. No equal/opposite restriction, no synthetic pair-sum target or conduct rule. Gate-only R0 replay reported against identical GATE-SIM baseline, not the superior receipt-cadence baseline.",
            "floor_timing":"Carried-state+future-last minima and their earliest time match filed baseline. Positive future-print minima/time supplied separately. No future-print target means missing, not zero error.",
            "family":"Weighted mode of filed realized family labels, alphabetic tie break as reference. Diagnostic only: same full-library retrospective SLEEPER p10 as baseline. No family-conditioning claim.",
            "coverage":"Each gate-side has all 928 queries, span-eligible, calls, abstention, before-first-tick and target-available denominators. Pooled gate counts are repeated games, never independent matched-win trials.",
            "matched_win":"File's >=100 matched, >=half strictly closer, ties included not wins; applied separately per side/gate. Report-only, no organ promotion.",
            "queue":"Positive native prints show reachable, not certain; same-second and post-bell prints cannot fill. Existing conduct guards unchanged."},
        determinism=dict(gate_projection_passes=2, query_digests_sha256=hashlib.sha256(c.encode(query_digests).encode()).hexdigest()),
        prior_art=["c7825925:arb-executor/analysis/tune_bench_v2_ticks/ATP_MAIN/TUNE_BENCH_RECEIPT.json",
            "d2d8f16b:arb-executor/analysis/conduct_scoreboard_v2/ATP_MAIN/CONDUCT_RECEIPT.json",
            "artifacts/review_mirror/GATE_1_OBJECT.md", "e269779b:SHAPE_TAXONOMY_BUILD1", "41c1f724:RECOGNITION_OPERATING_POINT"])
    now = c.bound_inputs(root)
    assert now["conduct"] == bound["conduct"], "ENGINE_CHANGED_DURING_BENCH"
    receipt["outputs"] = {p.name: dict(sha256=c.sha256(p), bytes=p.stat().st_size) for p in sorted(out.iterdir()) if p.is_file() and p.name != "SENTENCE_RECEIPT.json"}
    write(out/"SENTENCE_RECEIPT.json", receipt)
    print("COMPLETE "+str(out), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--prints", type=Path, default=Path(r"C:\tmp\conduct_atp_main_v1\ATP_MAIN_PRINTS.jsonl.gz"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--autopsy-only", action="store_true")
    args = parser.parse_args()
    args.out = args.out or args.root/"arb-executor/analysis/sentence_experiments/ATP_MAIN"
    run(args)
