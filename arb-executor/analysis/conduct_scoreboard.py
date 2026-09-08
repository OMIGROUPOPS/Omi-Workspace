#!/usr/bin/env python3
"""Bench-only conduct comparison. Never imports, edits, or replays the OS.

The extraction subcommand runs on droplet A, read-only under the cutter lock.
The scoring subcommand runs on the desktop against the filed FIRST baseline.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import closing
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import sys
import time
import re
import subprocess
from statistics import mean, median
sys.dont_write_bytecode = True


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def extract(args):
    spec = importlib.util.spec_from_file_location("bound_cutter", args.cutter)
    cutter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cutter)
    source = json.loads(args.library_receipt.read_text())
    if sha256(args.cutter) != source["builder"]["sha256"]:
        raise ValueError("CUTTER_HASH_MISMATCH")
    if sha256(args.library) != source["output"]["sha256"]:
        raise ValueError("LIBRARY_HASH_MISMATCH")
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise ValueError("EXTRACT_REQUIRES_NICE_10")
    allowed = Path("/mnt/omi-trading-data-nyc3/library").resolve()
    if not args.out.resolve().is_relative_to(allowed):
        raise ValueError("REMOTE_WRITES_MUST_STAY_IN_LIBRARY")
    receipt_path = args.out.with_suffix(".receipt.json")
    partial = args.out.with_suffix(args.out.suffix + ".partial")
    if any(p.exists() for p in (args.out, partial, receipt_path)):
        raise ValueError("REFUSE_TO_OVERWRITE_CONDUCT_INPUT")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.expected_sha256 = source["source_snapshot"]["sha256"]
    with cutter.store_cut_lock(args) as (lock, record):
        stat = args.db.stat()
        signature = (stat.st_size, stat.st_mtime_ns)
        record(status="HASHING_START")
        start_sha = sha256(args.db)
        print("SOURCE_SHA256_START=" + start_sha, flush=True)
        if start_sha != args.expected_sha256:
            raise ValueError("STORE_NOT_LIBRARY_SNAPSHOT")
        record(status="EXTRACTING", store_sha256_start=start_sha, store_sha256=start_sha)
        removed = Counter()
        legs = total = zeros = 0
        started = time.monotonic()
        with closing(cutter.open_snapshot(args.db, consolidated=True)) as db:
            with partial.open("xb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as output:
                with gzip.open(args.library, "rt") as library:
                    for line in library:
                        leg = json.loads(line)
                        if leg["category"] != args.category:
                            continue
                        if cutter.tune_named_event(leg["event_id"]):
                            raise ValueError("EXAM_EVENT_IN_LIBRARY")
                        prints = []
                        for r in cutter.accepted_print_rows(db, leg["ticker"], joined=leg.get("include_other_roles", False),
                                                           before=leg["bell_epoch"], removed=removed):
                            if r["ts"] < leg["formation_end_epoch"]:
                                continue
                            if r["event"] != leg["event_id"] or r["src_role"] == "TUNE_SAMPLE":
                                raise ValueError("PRINT_IDENTITY_OR_EXAM_ERROR")
                            prints.append([r["ts"], r["price"], r["size"], r["rowid"], r["src"]])
                        prints.sort(key=lambda r: (r[0], r[3]))
                        if len(prints) != leg["true_print_count_in_span"]:
                            raise ValueError("FINAL_PRINT_COUNT_MISMATCH:" + leg["ticker"])
                        # Reproduce cutter rowid ordering inside each second for exact volume verification.
                        running = 0
                        volume_seconds = []
                        for second, group in itertools.groupby(prints, key=lambda r: math.floor(r[0])):
                            for r in sorted(group, key=lambda r: r[3]):
                                running += r[2]
                            volume_seconds.append((second, running))
                        cursor, volume = 0, 0
                        for point in leg["path"]:
                            while cursor < len(volume_seconds) and volume_seconds[cursor][0] <= math.floor(point["ts"]):
                                volume = volume_seconds[cursor][1]
                                cursor += 1
                            if volume != point["volume_cum"]:
                                raise ValueError("LIBRARY_POINT_VOLUME_MISMATCH:" + leg["ticker"])
                        output.write((encode(dict(event_id=leg["event_id"], ticker=leg["ticker"], leg_id=leg["leg_id"],
                            formation_end_epoch=leg["formation_end_epoch"], bell_epoch=leg["bell_epoch"],
                            columns=["ts", "price", "size", "rowid", "src"], prints=prints)) + "\n").encode())
                        legs += 1
                        total += len(prints)
                        zeros += sum(p[2] == 0 for p in prints)
                        if legs % 100 == 0:
                            print("PROGRESS " + encode(dict(legs=legs, prints=total, elapsed_seconds=time.monotonic()-started)), flush=True)
        record(status="HASHING_END")
        end_sha = sha256(args.db)
        print("SOURCE_SHA256_END=" + end_sha, flush=True)
        after = args.db.stat()
        if start_sha != end_sha or signature != (after.st_size, after.st_mtime_ns):
            raise ValueError("SOURCE_CHANGED")
        receipt = dict(status="VERIFIED", category=args.category,
            library_sha256=source["output"]["sha256"], library_receipt_sha256=sha256(args.library_receipt),
            cutter_sha256=sha256(args.cutter), extractor_sha256=sha256(__file__),
            source_sha256_start=start_sha, source_sha256_end=end_sha, store_lock=dict(lock),
            legs=legs, true_prints=total, zero_size_accepted_prints=zeros, final_count_matches=legs,
            volume_check="Exact cumulative size at every original library change-point second",
            dedupe=cutter.DEDUPE_POLICY, removed_before_bell={str(k): v for k, v in sorted(removed.items())},
            span="Exact library formation <= accepted native timestamp < bell; no bounds rederived",
            ordering="Fill search uses native timestamp then rowid; library Q/book grid retains cutter second-close ordering",
            output_sha256=sha256(partial), output_bytes=partial.stat().st_size)
        partial.replace(args.out)
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        record(status="VERIFIED", store_sha256_end=end_sha)
        print("EXTRACT_COMPLETE " + encode(receipt), flush=True)


RULES = ("R0 CURRENT", "R1 CLIMBER-ANCHOR", "R2 NAMED-LEVEL", "R3 ANCHOR+NAMED", "R4 ANCHOR+Q25-NAMED")
RULES_V2 = RULES + ("R5 JOINT", "R6 ALL-SIDE-SAFETY")
BASELINE = "c7825925"


def bound_inputs(root):
    """Read the filed baseline, not a mutable scoreboard or invented thresholds."""
    folder = "arb-executor/analysis/tune_bench_v2_ticks/ATP_MAIN/"
    out, provenance = {}, {}
    for key, name in (("receipt", "TUNE_BENCH_RECEIPT.json"),
                      ("scoreboard", "TUNE_BENCH_SCOREBOARD.json"),
                      ("named", "TUNE_BENCH_NAMED_CHECKS.json")):
        raw = subprocess.check_output(["git", "show", f"{BASELINE}:{folder}{name}"], cwd=root)
        out[key] = json.loads(raw)
        provenance[key] = dict(commit=BASELINE, path=folder+name, sha256=hashlib.sha256(raw).hexdigest())
    out["provenance"] = provenance
    engine = root / "arb-executor/analysis/window1_v54_dual_belief_os.js"
    functionable = engine.with_name("window1_v54_functionable_os.js")
    source = engine.read_text(encoding="utf-8")
    budget = int(re.search(r"const PAR_BUDGET_CENTS = (\d+);", functionable.read_text(encoding="utf-8"))[1])
    par = int(re.search(r"const CONTRACT_SUM_CENTS = (\d+);", source)[1])
    bounds = re.search(r"function cent\(value\).*?value >= (\d+) && value <= (\d+)", source)
    out["conduct"] = dict(pair_budget=budget, par=par, minimum_cent=int(bounds[1]), maximum_cent=int(bounds[2]),
                           engine_sha256=sha256(engine), functionable_sha256=sha256(functionable))
    return out


def verify_reference(reference, root):
    import ast
    relative = "arb-executor/analysis/tune_bench_v2_survivorship.py"
    before = ast.parse(subprocess.check_output(["git", "show", f"{BASELINE}:{relative}"], cwd=root).decode())
    after = ast.parse(Path(reference.__file__).read_text(encoding="utf-8"))
    verified = []
    for name in ("load_tick_library", "load_named_inputs", "initial_pool", "remaining_floor", "Pair", "Leg", "role", "date_key"):
        a = next(n for n in before.body if getattr(n, "name", None) == name)
        b = next(n for n in after.body if getattr(n, "name", None) == name)
        if ast.dump(a) != ast.dump(b): raise ValueError("REFERENCE_DRIFT:" + name)
        verified.append(name)
    return dict(commit=BASELINE, structural_equivalence=verified)


class FirstProjector:
    """FIRST-only projection, same helpers/formula; no query-future evaluation."""
    def __init__(self, reference, pairs, contract):
        self.b, self.pairs, self.c = reference, pairs, contract
        self.cache = {}

    def category_gate(self, category, gate):
        import numpy as np
        key = (category, gate)
        if key not in self.cache:
            pool = [m for m in self.pairs if m.category == category]
            current = np.array([m.levels([gate])[0] for m in pool])
            opens = np.array([[leg.open for leg in m.legs] for m in pool])
            drift = current[:, [0, 3]] - opens
            boundary = self.c["role_drift_cents"]
            roles = np.where(drift >= boundary, "CLIMBER", np.where(drift <= -boundary, "FALLER", "NOT_CALLABLE"))
            floors = np.array([[self.b.remaining_floor(leg, gate) for leg in m.legs] for m in pool])
            self.cache[key] = (pool, current, roles, floors, {m.event_id: i for i, m in enumerate(pool)})
        return self.cache[key]

    def project(self, query):
        import numpy as np
        members, weights = self.b.initial_pool(query, self.pairs)
        rows = []
        binds, previous, flips = [None, None], [None, None], [0, 0]
        # Recognition sees every observed prefix tick, not a retrospective role scan.
        observed = query.grid()
        cursor = 0
        for gate in self.c["gates_minutes_to_bell"]:
            if gate > query.first_mtb:
                continue
            while cursor < len(observed) and observed[cursor] >= gate:
                obs_gate = float(observed[cursor])
                for i, role in enumerate(query.roles(obs_gate)):
                    if role != "NOT_CALLABLE":
                        if binds[i] is None: binds[i] = dict(role=role, minutes_to_bell=obs_gate)
                        if previous[i] is not None and role != previous[i]: flips[i] += 1
                        previous[i] = role
                cursor += 1
            epoch = query.bell - gate * self.c["minute_seconds"]
            current = query.levels([gate])[0]
            roles = query.roles(gate)
            row = dict(source_gate_minutes=gate, epoch=epoch, sides={})
            if members:
                pool, mc, mr, mf, indices = self.category_gate(query.category, gate)
                ix = np.array([indices[m.event_id] for m in members])
            for i, leg in enumerate(query.legs):
                own_index = int(np.searchsorted(leg.epoch, epoch, side="right")) - 1
                state = dict(role=roles[i], first_bind=binds[i], flip_count=flips[i],
                    last=float(current[i*3]), bid=float(current[i*3+1]), ask=float(current[i*3+2]),
                    seen_true_trade_low=float(leg.low[own_index]) if own_index >= 0 else None,
                    ess=0.0, member_count=0, status="INSUFFICIENT_EVIDENCE", writer="POOL_FIRST_TICK")
                if members:
                    mask = ((mr[ix, i] == roles[i]) | (roles[i] == "NOT_CALLABLE"))
                    mask &= np.all(np.isfinite(mc[ix, i*3:i*3+3]), axis=1)
                    mask &= np.array([m.first_mtb for m in members]) >= gate
                    sw = weights * mask
                    state.update(ess=float(self.b.ess(sw) or 0), member_count=int(np.count_nonzero(sw)))
                    if state["ess"] >= self.c["no_call_ess_floor"]:
                        active = sw > 0
                        delta = mf[ix, i, 0] - mc[ix, i*3]
                        state.update(status="OK", floors={})
                        for q in self.c["quantiles"]:
                            if q not in (.25, .5, .75): continue
                            state["floors"][f"q{round(q*100)}"] = dict(
                                level_cents=float(current[i*3] + self.b.inverse_weighted_quantile(delta[active], sw[active], q)),
                                minutes_to_bell=float(self.b.inverse_weighted_quantile(mf[ix, i, 1][active], sw[active], q)))
                row["sides"][leg.leg_id] = state
            rows.append(row)
        return rows


def finite(value):
    return isinstance(value, (float, int)) and math.isfinite(value)


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value): return None
    return value


def simulate_conduct(event, leg_ids, forecasts, tapes, formation, bell, spec, rule):
    """Deterministic event loop: old orders see prints at a gate before its decision.

    New orders require ts > placement; there is no same-timestamp fill credit.
    """
    active = {leg: None for leg in leg_ids}
    fills, anchors, named_levels, actions, exposures = {}, {}, {}, [], []
    safety = Counter()
    postability = {}
    joint_decisions = []
    positive_only = spec.get("positive_size_fills", False)
    all_prints = sorted((p[0], leg, p[3], p[1], p[2]) for leg in leg_ids for p in tapes[leg]
                        if formation <= p[0] < bell and (not positive_only or finite(p[2]) and p[2] > 0))
    cursor = 0

    def consume(end):
        nonlocal cursor
        while cursor < len(all_prints) and all_prints[cursor][0] <= end:
            ts, leg, rowid, price, size = all_prints[cursor]
            cursor += 1
            order = active[leg]
            if order is None or leg in fills or ts <= order["placed_epoch"]: continue
            for exposure in exposures:
                if exposure["leg"] == leg and not exposure.get("closed") and ts > exposure["epoch"]:
                    if exposure["new_cents"] < price <= exposure["old_cents"]:
                        exposure.setdefault("witness", dict(epoch=ts, price=price, rowid=rowid))
            if price <= order["cents"]:
                fills[leg] = dict(cents=order["cents"], epoch=ts, print_cents=price, size=size, print_rowid=rowid,
                    minutes_to_bell=(bell-ts)/60, rest_age_minutes=(ts-order["placed_epoch"])/60,
                    placed_epoch=order["placed_epoch"], writer=order["writer"], reachability="REACHABLE — queue position unknown")
                active[leg] = None
                for exposure in exposures:
                    if exposure["leg"] == leg: exposure["closed"] = True

    def valid_cent(value):
        return finite(value) and value == int(value) and spec["minimum_cent"] <= value <= spec["maximum_cent"]

    for receipt in forecasts:
        ts = receipt["epoch"]
        if ts < formation or ts >= bell: continue
        consume(ts)
        proposals, reasons = {}, {}
        if rule == 5:
            from conduct_scoreboard_v2 import choose_joint
            joint = choose_joint(receipt, leg_ids, fills, named_levels, active, spec)
            joint_decisions.append(dict(epoch=ts, **joint))
        for leg in leg_ids:
            state, order = receipt["sides"][leg], active[leg]
            old = order["cents"] if order else None
            if leg in fills:
                proposals[leg], reasons[leg] = None, "ALREADY_FILLED"
                continue
            role = state["role"]
            protected = rule == 6 or rule in (2, 3, 4, 5) and role == "FALLER"
            if protected and old is not None:
                named_levels[leg] = max(old, named_levels.get(leg, old))
            if rule in (1, 3, 4) and role == "CLIMBER" and leg not in anchors:
                low = state["seen_true_trade_low"]
                if valid_cent(low): anchors[leg] = dict(cents=low, epoch=ts)
            q = state.get("floors", {}).get("q25" if rule == 4 and role == "FALLER" else "q50", {}).get("level_cents")
            if rule == 5:
                q = joint.get("levels", {}).get(leg)
            bid, ask = state["bid"], state["ask"]
            prior = postability.get(leg, {})
            postable = valid_cent(q) and valid_cent(ask) and q < ask
            became_postable = postable and prior.get("target") == q and prior.get("postable") is False
            postability[leg] = dict(target=q, postable=postable)
            if finite(bid) and finite(ask) and bid >= ask:
                proposals[leg], reasons[leg] = old, "LOCKED_BOOK_HOLD"
                continue
            if state["status"] != "OK" or not valid_cent(q):
                proposals[leg], reasons[leg] = old, "INSUFFICIENT_AUTHORITY_HOLD"
                continue
            if receipt.get("ask_only_book_tick", False) and not became_postable:
                proposals[leg], reasons[leg] = old, "ASK_ONLY_BOOK_HOLD"
                continue
            if rule in (1, 3, 4) and leg in anchors:
                q = anchors[leg]["cents"]
            elif protected and leg in named_levels:
                q = max(named_levels[leg], q)
            if not valid_cent(ask) or q >= ask:
                proposals[leg] = old if old is not None and valid_cent(ask) and old <= ask else None
                reasons[leg] = "POST_ONLY_HOLD_OR_PULL"
            else:
                proposals[leg], reasons[leg] = q, "RULE_TARGET_POSTABLE"
        total = sum(fills[leg]["cents"] if leg in fills else (proposals[leg] or 0) for leg in leg_ids)
        if total > spec["pair_budget"]:
            for leg in leg_ids:
                proposals[leg] = active[leg]["cents"] if active[leg] else None
                reasons[leg] = "PAIR_CAP_HOLD"
        for leg in leg_ids:
            old = active[leg]["cents"] if active[leg] else None
            new = proposals[leg]
            if old == new: continue
            for exposure in exposures:
                if exposure["leg"] == leg: exposure["closed"] = True
            state = receipt["sides"][leg]
            if old is not None and new is not None and new < old and state["role"] == "FALLER":
                exposures.append(dict(leg=leg, epoch=ts, old_cents=old, new_cents=new))
            if new is not None:
                if ts < formation: safety["pre_formation"] += 1
                if not finite(state["ask"]) or new >= state["ask"]: safety["post_only"] += 1
                if state["status"] != "OK": safety["insufficient_evidence_placement"] += 1
            writer = "JOINT_EXPECTED_DISCOUNT" if rule == 5 else "CLIMBER_ANCHOR" if rule in (1, 3, 4) and leg in anchors else "FIRST_Q25" if rule == 4 and state["role"] == "FALLER" else "FIRST_Q50"
            active[leg] = None if new is None else dict(cents=new, placed_epoch=ts, writer=writer)
            if (rule == 6 or rule in (2, 3, 4, 5) and state["role"] == "FALLER") and new is not None:
                named_levels[leg] = max(new, named_levels.get(leg, new))
            actions.append(dict(leg=leg, epoch=ts, minutes_to_bell=(bell-ts)/60,
                source_gate_minutes=receipt["source_gate_minutes"], old_cents=old, new_cents=new,
                action="PULL" if new is None else "PLACE" if old is None else "REPRICE",
                role=state["role"], writer=writer, reason=reasons[leg], q50=state.get("floors", {}).get("q50")))
        held = sum(fills[l]["cents"] if l in fills else active[l]["cents"] if active[l] else 0 for l in leg_ids)
        if held > spec["pair_budget"]: safety["pair_cap"] += 1
    consume(bell)
    completed = len(fills) == len(leg_ids)
    pair_sum = sum(f["cents"] for f in fills.values()) if completed else None
    for fill in fills.values():
        if fill["epoch"] >= bell: safety["after_bell"] += 1
        if fill["epoch"] <= fill["placed_epoch"]: safety["not_strictly_later"] += 1
        if fill["print_cents"] > fill["cents"]: safety["print_above_bid"] += 1
        if positive_only and not (finite(fill["size"]) and fill["size"] > 0): safety["nonpositive_size_witness"] += 1
    # Also report the broad literal "any later print" count separately, not as proof
    # the abandoned level remained available after another order change.
    for ex in exposures:
        ex["any_later_print"] = any(ex["epoch"] < p[0] < bell and ex["new_cents"] < p[1] <= ex["old_cents"]
            and (not positive_only or finite(p[2]) and p[2] > 0) for p in tapes[ex["leg"]])
    return dict(event_id=event, rule=RULES_V2[rule], eligible=True, formation_epoch=formation, bell_epoch=bell,
        completed=completed, one_sided=len(fills)==1, fills=fills, pair_sum=pair_sum,
        captured_cents=spec["par"]-pair_sum if completed else 0, captured_credit="BOTH SIDES ONLY",
        rests_at_bell=active, climber_bindings=anchors, named_level_memory=named_levels, actions=actions,
        stepped_off=any(e["any_later_print"] for e in exposures),
        stepped_off_while_lower_rest_active=any("witness" in e for e in exposures),
        stepped_off_any_later=any(e["any_later_print"] for e in exposures), stepped_off_exposures=exposures,
        safety_violations=dict(safety), queue_position="UNKNOWN — reachable is not certain",
        failed_sides=[leg for leg in leg_ids if leg not in fills],
        one_sided_failed_orientation=("favourite" if leg_ids[0] not in fills else "underdog") if len(fills)==1 else None,
        joint_decisions=joint_decisions)


def summarize(results):
    done = [r for r in results if r["completed"]]
    completed_c = [r["captured_cents"] for r in done]
    eligible_c = [r["captured_cents"] for r in results]
    times = [f["minutes_to_bell"] for r in results for f in r["fills"].values()]
    violations = Counter()
    for row in results: violations.update(row["safety_violations"])
    n = len(results)
    return dict(eligible=n, completed=len(done), completion_rate=len(done)/n,
        mean_captured_completed=mean(completed_c) if done else None, median_captured_completed=median(completed_c) if done else None,
        mean_captured_eligible=mean(eligible_c), median_captured_eligible=median(eligible_c),
        one_sided=sum(r["one_sided"] for r in results), one_sided_rate=sum(r["one_sided"] for r in results)/n,
        stepped_off_pairs=sum(r["stepped_off"] for r in results), stepped_off_share=sum(r["stepped_off"] for r in results)/n,
        stepped_off_any_later_pairs=sum(r["stepped_off_any_later"] for r in results),
        stepped_off_while_lower_rest_active_pairs=sum(r["stepped_off_while_lower_rest_active"] for r in results),
        mean_fill_minutes_to_bell=mean(times) if times else None, fill_denominator=len(times),
        zero_size_accepted_print_fills=sum(f.get("size") == 0 for r in results for f in r["fills"].values()),
        safety_violations=dict(violations))


def score(args):
    import numpy as np
    import tune_bench_v2_survivorship as b
    root = args.repo_root
    bound = bound_inputs(root)
    helper_check = verify_reference(b, root)
    c = bound["receipt"]["organ_contract"]
    durable = root / "arb-executor/data/durable"
    library = args.library or durable / "RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz"
    counts = durable / "RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz"
    if sha256(library) != bound["receipt"]["input_library"]["sha256"]:
        raise ValueError("LIBRARY_NOT_FILED_BASELINE")
    print("LOAD_LIBRARY", flush=True)
    pairs, census, _, count_provenance = b.load_tick_library(library, {}, counts)
    wanted = bound["scoreboard"]["categories"][args.category]["query_event_ids"]
    queries = [p for p in pairs if p.event_id in set(wanted)]
    if sorted(p.event_id for p in queries) != sorted(wanted): raise ValueError("ELIGIBLE_DENOMINATOR_MISMATCH")
    projector = FirstProjector(b, pairs, c)
    if args.prepare_only:
        args.out.mkdir(parents=True, exist_ok=True)
        forecasts = {}
        began = time.monotonic()
        for i, query in enumerate(queries):
            forecasts[query.event_id] = projector.project(query)
            if (i+1) % 50 == 0: print("FORECAST_PROGRESS " + encode(dict(queries_done=i+1, total=len(queries), elapsed_seconds=time.monotonic()-began)), flush=True)
        with (args.out/"FIRST_PREPARED.json.gz").open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            zipped.write(encode(clean(dict(script_sha256=sha256(__file__), library_sha256=sha256(library), predictions=forecasts))).encode())
        print("FIRST_PREPARED_COMPLETE", flush=True)
        return
    input_receipt = json.loads(args.prints.with_suffix(".receipt.json").read_text())
    if sha256(args.prints) != input_receipt["output_sha256"] or sha256(library) != input_receipt["library_sha256"]:
        raise ValueError("CONDUCT_PRINT_INPUT_HASH_MISMATCH")
    raw_tapes = {}
    print_rows = 0
    with gzip.open(args.prints, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["ticker"] in raw_tapes: raise ValueError("DUPLICATE_EXTRACT_LEG")
            raw_tapes[row["ticker"]] = row
            print_rows += len(row["prints"])
    if (len(raw_tapes) != input_receipt["legs"] or print_rows != input_receipt["true_prints"]
            or args.prints.stat().st_size != input_receipt["output_bytes"]):
        raise ValueError("EXTRACT_LOCAL_ROW_COUNT_OR_SIZE_MISMATCH")
    extract_local = dict(path=str(args.prints.resolve()), sha256=sha256(args.prints), bytes=args.prints.stat().st_size,
        jsonl_leg_rows=len(raw_tapes), accepted_print_rows=print_rows,
        row_definition="One outer JSONL row per library leg; its prints array contains the accepted native print rows",
        matches_extractor_receipt=True, raw_prints_committed=False)
    results = {r: [] for r in RULES}
    predictions = {}
    prepared_path = args.out / "FIRST_PREPARED.json.gz"
    prepared = None
    if prepared_path.exists():
        with gzip.open(prepared_path, "rt") as stream: prepared = json.load(stream)
        if prepared["library_sha256"] != sha256(library): raise ValueError("PREPARED_LIBRARY_MISMATCH")
    began = time.monotonic()
    for i, query in enumerate(queries):
        forecast = projector.project(query)
        if prepared is not None and clean(forecast) != prepared["predictions"][query.event_id]:
            raise ValueError("FIRST_FORECAST_NONDETERMINISM:" + query.event_id)
        predictions[query.event_id] = forecast
        tapes = {}
        for leg in query.legs:
            raw = raw_tapes[query.event_id+"-"+leg.leg_id]
            if raw["formation_end_epoch"] != leg.formation or raw["bell_epoch"] != leg.bell: raise ValueError("PRINT_SPAN_MISMATCH")
            tapes[leg.leg_id] = raw["prints"]
        for rule in range(len(RULES)):
            result = simulate_conduct(query.event_id, [l.leg_id for l in query.legs], forecast, tapes,
                                      query.formation, query.bell, bound["conduct"], rule)
            again = simulate_conduct(query.event_id, [l.leg_id for l in query.legs], forecast, tapes,
                                      query.formation, query.bell, bound["conduct"], rule)
            if encode(clean(result)) != encode(clean(again)): raise ValueError("CONDUCT_NONDETERMINISM")
            results[RULES[rule]].append(result)
        if (i+1) % 50 == 0: print("PROGRESS " + encode(dict(queries_done=i+1, total=len(queries), elapsed_seconds=time.monotonic()-began)), flush=True)
    print("LOAD_NAMED_TRUE_PRINTS", flush=True)
    named_pairs, named_sources = b.load_named_inputs(root, {}, args.tape_dir, args.named_prints, second_close=True)
    named_results, comparison = {}, []
    for query in named_pairs:
        forecast = projector.project(query)
        original = next(v for v in bound["named"]["events"].values() if v["event_id"] == query.event_id)
        for row in forecast:
            expected = original["gates"][str(row["source_gate_minutes"])]
            for side, leg in zip(b.SIDES, query.legs):
                ref = expected.get("rules", {}).get("FIRST-TICK-ONLY", {}).get("sides", {}).get(side)
                got = row["sides"][leg.leg_id]
                if not ref: continue
                if ref.get("status") == "OK":
                    for quantile in ("q25", "q50", "q75"):
                        for key in ("level_cents", "minutes_to_bell"):
                            if not np.isclose(ref["floors"][quantile][key], got["floors"][quantile][key], rtol=0, atol=np.finfo(float).eps*max(1, abs(ref["floors"][quantile][key]))*len(pairs)):
                                raise ValueError(f"FIRST_BASELINE_MISMATCH:{query.event_id}:{row['source_gate_minutes']}:{leg.leg_id}:{key}")
                elif got["status"] == "OK": raise ValueError("BASELINE_NO_CALL_MISMATCH")
                comparison.append(dict(event=query.event_id, gate=row["source_gate_minutes"], leg=leg.leg_id, status="MATCH"))
        face_path = root / "window1-watch/data" / (query.event_id+".face.json")
        face = json.loads(face_path.read_text(encoding="utf-8"))
        truth = face.get("rulers", {}).get("effective_truth", face["truth"])
        formation = max(query.formation, truth["span_start_epoch"])
        # The verified tape's last observed instant is not a fabricated bell.
        bell = truth["bell_epoch"]
        if bell > query.bell and truth["span_end_epoch"] > query.bell:
            raise ValueError("NAMED_TAPE_REQUIRES_PRINTS_BEYOND_BASELINE_BELL")
        tapes = {l.leg_id: [[float(t), float(price), None, j, "custody_true_trade"]
                           for j, (t, price) in enumerate(zip(l.trade_epoch, l.trade_price))
                           if t <= truth["span_end_epoch"]] for l in query.legs}
        named_results[query.event_id] = dict(baseline_bell_epoch=query.bell, corrected_bell_epoch=bell,
            truth_commit=truth["table_commit"], corrections_commit=truth.get("corrections_commit"),
            truth_row_sha256=truth["row_sha256"], face_sha256=sha256(face_path),
            corrected_span_start_epoch=truth["span_start_epoch"], corrected_span_end_epoch=truth["span_end_epoch"],
            forecasts=forecast, rules={RULES[r]: simulate_conduct(query.event_id, [l.leg_id for l in query.legs],
                forecast, tapes, formation, bell, bound["conduct"], r) for r in range(len(RULES))})
    summary = {rule: summarize(rows) for rule, rows in results.items()}
    deltas = {}
    baseline = results[RULES[0]]
    for rule, rows in results.items():
        both = [(r, base) for r, base in zip(rows, baseline) if r["completed"] and base["completed"]]
        joint_fills = [(r["fills"][leg], base["fills"][leg]) for r, base in zip(rows, baseline)
                       for leg in sorted(r["fills"].keys() & base["fills"].keys())]
        deltas[rule] = dict(all_eligible_pairs=len(rows), completion_rate_delta=summary[rule]["completion_rate"]-summary[RULES[0]]["completion_rate"],
            captured_per_eligible_delta=summary[rule]["mean_captured_eligible"]-summary[RULES[0]]["mean_captured_eligible"],
            median_captured_per_eligible_delta=summary[rule]["median_captured_eligible"]-summary[RULES[0]]["median_captured_eligible"],
            one_sided_rate_delta=summary[rule]["one_sided_rate"]-summary[RULES[0]]["one_sided_rate"],
            stepped_off_share_delta=summary[rule]["stepped_off_share"]-summary[RULES[0]]["stepped_off_share"],
            safety_violation_delta=sum(summary[rule]["safety_violations"].values())-sum(summary[RULES[0]]["safety_violations"].values()),
            jointly_filled_sides=len(joint_fills),
            mean_fill_minutes_to_bell_delta_joint=mean(f["minutes_to_bell"]-base["minutes_to_bell"] for f, base in joint_fills) if joint_fills else None,
            jointly_completed_pairs=len(both), mean_captured_joint_delta=mean(r["captured_cents"]-base["captured_cents"] for r, base in both) if both else None,
            median_captured_joint_delta=median(r["captured_cents"]-base["captured_cents"] for r, base in both) if both else None)
    receipt = dict(status="BENCH ONLY — REACHABLE FILLS, NOT CERTAIN", baseline=bound["provenance"],
        script_sha256=sha256(__file__), reference_script_sha256=sha256(Path(b.__file__)), conduct_guard_source=bound["conduct"],
        library_sha256=sha256(library), print_extract=input_receipt, print_extract_local_verification=extract_local,
        print_extract_receipt_sha256=sha256(args.prints.with_suffix(".receipt.json")),
        count_sidecar=count_provenance, named_inputs=named_sources, query_count=len(queries), baseline_named_comparisons=comparison,
        cohort=dict(category=args.category, eligible_query_pairs=len(queries), eligible_query_legs=sum(len(q.legs) for q in queries),
                    filed_category_census={k: v for k, v in census.items() if k.startswith(args.category+":")}),
        inherited_helper_check=helper_check,
        determinism=dict(conduct="Each query/rule event loop evaluated twice; canonical bytes equal",
                         first_forecasts="Independent prepared pass equals scoring pass on all queries" if prepared is not None else "NOT_CHECKED", prepared_sha256=sha256(prepared_path) if prepared else None),
        definitions=dict(eligible="Exact 928 oriented ATP_MAIN query ids filed at c7825925; no future-SCORABLE filter; all are denominators, including no-call/no-gate queries",
          fill="First accepted native print strictly after placement/reprice, price <= bid, formation <= print < bell. Fill at resting bid, not print price. Queue unknown. Zero-size library prints retain cutter acceptance, separately reported.",
          current="R0 is FIRST-only at fixed atlas-gate receipts as ordered, not a replay of installed FIRST/BASE or its between-gate conduct. No pre-first-gate synthetic placement.",
          guards="Existing integer-cent validation, locked-book hold, insufficient-authority hold, post-only hold/pull, joint pair-budget veto; existing credited entry included. Atlas receipts are not ask-only book ticks.",
          roles="Reference receipt-time current role; first bind and flips update causally across observed prefix points, not via terminal-label scanning.",
          anchor="First atlas receipt calling CLIMBER binds the stored own running low; freezes through later role flips. Author ESS/guards still required; no invented price after safety cancellation.",
          named_level="Protect actually posted faller levels from downward movement, not an unposted forecast. Remember the posted high-water level through a safety cancellation. May rise; current non-FALLER uses R0 unless a climber binding already froze it.",
          q25="R4 replaces faller q50 with q25 then applies the same standing-level protection. Existing climber binding takes priority.",
          stepped_off="As ordered: a downward faller reprice has any strictly later pre-bell accepted print with new < price <= old. Count a pair once. Also report the stricter subset whose witness arrives while that lower order is still active; neither counter awards fill credit.",
          matching="All rules score identical eligible ids. Conditional capture delta uses pairs completed under BOTH rules, denominator explicit.",
          named_clock="Named Q/X/roles reproduce c7825925 FIRST at their original absolute receipt timestamps; accepted fills and order bounds use corrected ruler. Original gate and corrected minutes-to-bell both written. No old forecast moved backwards to a corrected gate.",
          future_access="Query future prints used only in consume/fill/outcome/stepped-off evaluation; projector samples own prefix only. Member remaining floors are already historical (bell < query formation)."))
    args.out.mkdir(parents=True, exist_ok=True)
    payloads = {"CONDUCT_SCOREBOARD.json": dict(summary=summary, matched_deltas=deltas, queries=results),
                "CONDUCT_NAMED_CHECKS.json": named_results, "CONDUCT_RECEIPT.json": receipt}
    for name, payload in payloads.items():
        (args.out/name).write_text(json.dumps(clean(payload), indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    with (args.out/"FIRST_FORECASTS.jsonl.gz").open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
        for event, forecasts in predictions.items(): zipped.write((encode(clean(dict(event_id=event, receipts=forecasts)))+"\n").encode())
    lines = ["# Conduct scoreboard — reachable, not certain", "", "FIRST-only atlas-gate comparison; all eligible pairs; no engine replay.", "",
        "| Rule | Complete / eligible | Rate | Captured mean / median completed | Captured mean / median eligible | One-sided | Stepped off | Fill → bell mean m | Safety |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    fmt = lambda v: "—" if v is None else f"{v:.3f}"
    for rule, r in summary.items():
        lines.append(f"| {rule} | {r['completed']} / {r['eligible']} | {r['completion_rate']:.2%} | {fmt(r['mean_captured_completed'])} / {fmt(r['median_captured_completed'])} | {fmt(r['mean_captured_eligible'])} / {fmt(r['median_captured_eligible'])} | {r['one_sided']} ({r['one_sided_rate']:.2%}) | {r['stepped_off_pairs']} ({r['stepped_off_share']:.2%}) | {fmt(r['mean_fill_minutes_to_bell'])} | {sum(r['safety_violations'].values())} |")
    lines += ["", "## Matched deltas vs R0", "", "| Rule | Δ completion | Δ captured / eligible | Joint completions | Δ capture mean / median, joint |", "|---|---:|---:|---:|---:|"]
    for rule, r in deltas.items(): lines.append(f"| {rule} | {r['completion_rate_delta']:.2%} | {fmt(r['captured_per_eligible_delta'])} | {r['jointly_completed_pairs']} | {fmt(r['mean_captured_joint_delta'])} / {fmt(r['median_captured_joint_delta'])} |")
    lines += ["", "| Rule | Δ one-sided | Δ stepped-off | Joint filled sides | Δ mean fill → bell m, joint |", "|---|---:|---:|---:|---:|"]
    for rule, r in deltas.items(): lines.append(f"| {rule} | {r['one_sided_rate_delta']:.2%} | {r['stepped_off_share_delta']:.2%} | {r['jointly_filled_sides']} | {fmt(r['mean_fill_minutes_to_bell_delta_joint'])} |")
    lines += ["", "## Named checks", "", "Original baseline receipt epochs; fills censored by corrected ruler. A dash is no reachable fill. Incomplete pairs receive zero credit.", "", "| Game | Rule | Fills (bid cents) | Captured cents |", "|---|---|---|---:|"]
    for event, named in named_results.items():
        for rule, r in named["rules"].items():
            fills = ", ".join(f"{leg} {r['fills'][leg]['cents']}" if leg in r['fills'] else f"{leg} —" for leg in r['rests_at_bell'])
            lines.append(f"| {event.split('-')[-1]} | {rule} | {fills} | {r['captured_cents']} |")
    (args.out/"CONDUCT_SUMMARY.md").write_text("\n".join(lines)+"\n", encoding="utf-8", newline="\n")
    receipt["outputs"] = {name: dict(sha256=sha256(args.out/name), bytes=(args.out/name).stat().st_size)
        for name in ("CONDUCT_SCOREBOARD.json", "CONDUCT_NAMED_CHECKS.json", "FIRST_FORECASTS.jsonl.gz", "CONDUCT_SUMMARY.md")}
    (args.out/"CONDUCT_RECEIPT.json").write_text(json.dumps(clean(receipt), indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    print("\n".join(lines), flush=True)


def main():
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract-prints", action="store_true")
    parser.add_argument("--prepare-only", action="store_true", help="Build auditable FIRST forecasts while accepted-print extraction runs; not a scoreboard")
    parser.add_argument("--category", default="ATP_MAIN")
    parser.add_argument("--db", type=Path)
    parser.add_argument("--cutter", type=Path)
    parser.add_argument("--store-lock")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--library", type=Path)
    parser.add_argument("--library-receipt", type=Path)
    parser.add_argument("--prints", type=Path)
    parser.add_argument("--tape-dir", type=Path, default=Path(r"C:\Users\omigr\OMI-Window1-private\fit-local\ticks"))
    parser.add_argument("--named-prints", type=Path, default=Path(r"C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.extract_prints:
        extract(args)
    else:
        score(args)


if __name__ == "__main__":
    main()
