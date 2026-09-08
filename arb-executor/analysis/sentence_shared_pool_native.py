#!/usr/bin/env python3
"""E4a receipt-cadence companion: shared FIRST members, unchanged R0 conduct.

Uses archived joint candidate minima and reconstructs joint floor-time marginals
from the same members. Does not assume opposite moves or edit/import the OS.
"""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
import conduct_scoreboard as c
import conduct_scoreboard_v2 as cv2
import tune_bench_v2_survivorship as b
import sentence_experiments as se


def shared_projection(query, rows, pairs, contract, batch_size=256):
    members, w0 = b.initial_pool(query, pairs)
    # Archived joint counts/NO-CALLs are already twice-verified and hash-bound.
    # R0 never reads the large joint-outcome arrays. Do not copy them into the
    # experimental projection, and only rebuild callable joint marginals.
    out = [deepcopy({k:v for k,v in row.items() if k != "joint"}) for row in rows]
    callable_indices = []
    for index, row in enumerate(rows):
        joint = row["joint"]
        if joint["status"] == "OK":
            callable_indices.append(index)
        else:
            assert joint["ess"] < contract["no_call_ess_floor"]
            for state in out[index]["sides"].values():
                state.pop("floors", None)
                state.update(status="INSUFFICIENT_EVIDENCE", ess=joint["ess"], member_count=joint["member_count"])
    first = np.asarray([m.first_mtb for m in members])
    seconds = contract["minute_seconds"]
    for start in range(0, len(callable_indices), batch_size):
        indices = callable_indices[start:start+batch_size]
        batch = [rows[index] for index in indices]
        gates = np.asarray([r["source_gate_minutes"] for r in batch])
        masks = np.ones((len(batch), len(members)), dtype=bool)
        times = np.empty((len(batch), len(members), len(query.legs)))
        deltas = np.empty_like(times)
        for j, member in enumerate(members):
            for side, leg in enumerate(member.legs):
                epochs = member.bell-gates*seconds
                values = leg.sample(epochs)[:, :3]
                drift = values[:, 0]-leg.open
                role = np.where(drift >= contract["role_drift_cents"], "CLIMBER",
                                np.where(drift <= -contract["role_drift_cents"], "FALLER", "NOT_CALLABLE"))
                own = np.asarray([r["sides"][query.legs[side].leg_id]["role"] for r in batch])
                masks[:, j] &= ((role == own) | (own == "NOT_CALLABLE"))
                masks[:, j] &= np.all(np.isfinite(values), axis=1)
                masks[:, j] &= first[j] >= gates
                ix = np.searchsorted(leg.epoch, epochs, side="right")
                fi = leg.remaining_floor_index[np.minimum(ix, len(leg.epoch)-1)]
                use_current = (ix == len(leg.epoch)) | (values[:, 0] <= leg.values[fi, 0])
                times[:, j, side] = np.where(use_current, gates, (member.bell-leg.epoch[fi])/seconds)
                deltas[:, j, side] = np.where(use_current, values[:, 0], leg.values[fi, 0])-values[:, 0]
        for local, old in enumerate(batch):
            row = out[indices[local]]
            weights = w0*masks[local]
            ess = float(b.ess(weights) or 0)
            joint = old["joint"]
            assert ess == joint["ess"] and int(np.count_nonzero(weights)) == joint["member_count"], "SHARED_MASK_DRIFT"
            for side, leg in enumerate(query.legs):
                state = row["sides"][leg.leg_id]
                state.pop("floors", None)
                state.update(status="INSUFFICIENT_EVIDENCE", ess=ess, member_count=joint["member_count"])
                if ess >= contract["no_call_ess_floor"]:
                    assert joint["status"] == "OK"
                    state.update(status="OK", floors={})
                    active = weights > 0
                    for name in ("q25", "q50", "q75"):
                        quantile = float(name[1:])/100
                        state["floors"][name] = dict(
                            level_cents=float(state["last"]+b.inverse_weighted_quantile(deltas[local, active, side], weights[active], quantile)),
                            minutes_to_bell=float(b.inverse_weighted_quantile(times[local, active, side], weights[active], quantile)))
    return out


def run(root, out, prints_path):
    bound = c.bound_inputs(root)
    contract = bound["receipt"]["organ_contract"]
    spec = dict(bound["conduct"], positive_size_fills=True)
    durable = root/"arb-executor/data/durable"
    library = durable/"RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz"
    assert c.sha256(library) == bound["receipt"]["input_library"]["sha256"]
    pairs, _, _, _ = b.load_tick_library(library, {}, durable/"RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz")
    pairs = [p for p in pairs if p.category == "ATP_MAIN"]
    wanted = bound["scoreboard"]["categories"]["ATP_MAIN"]["query_event_ids"]
    queries = {p.event_id: p for p in pairs}
    assert sorted(queries) == sorted(wanted)
    extract = json.loads(prints_path.with_suffix(".receipt.json").read_text())
    assert c.sha256(prints_path) == extract["output_sha256"]
    tapes = {}
    for row in se.iter_jsonl(prints_path):
        if row["event_id"] in queries:
            tapes.setdefault(row["event_id"], {})[row["leg_id"]] = row["prints"]
    archive = root/"arb-executor/analysis/conduct_scoreboard_v2/ATP_MAIN"
    bound_archive = json.loads((out/"SENTENCE_RECEIPT.json").read_text())["archives"]
    for name, sha in bound_archive.items(): assert c.sha256(archive/name) == sha
    baseline = {r["event_id"]: r for r in se.iter_jsonl(archive/"CONDUCT_QUERIES.jsonl.gz")
                if r["mode"] == "RECEIPT-SIM" and r["rule"] == c.RULES[0]}
    results, bases, digests = [], [], []
    started = time.monotonic()
    target = out/"E4_NATIVE_RESULTS.jsonl.gz"
    with target.open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as stream:
        for item in se.iter_jsonl(archive/"FIRST_FORECASTS.jsonl.gz"):
            if item["mode"] != "RECEIPT-SIM": continue
            event = item["event_id"]
            query, rows = queries[event], item["receipts"]
            forecast = shared_projection(query, rows, pairs, contract)
            # Independent batch boundary gives the same mathematical output.
            again = shared_projection(query, rows, pairs, contract, batch_size=128)
            encoded = c.encode(c.clean(forecast))
            assert encoded == c.encode(c.clean(again)), "SHARED_NONDETERMINISM"
            result = c.simulate_conduct(event, [l.leg_id for l in query.legs], forecast, tapes[event], query.formation, query.bell, spec, 0)
            cv2.verify_fills(result, tapes[event])
            fingerprint = hashlib.sha256(encoded.encode()).hexdigest()
            digests.append(fingerprint)
            stream.write((c.encode(c.clean(dict(forecast_sha256=fingerprint, **result)))+"\n").encode())
            results.append(result)
            bases.append(baseline[event])
            if len(results) % 50 == 0 or len(results) == len(queries):
                print("NATIVE_SHARED_PROGRESS "+c.encode(dict(queries=len(results), total=len(queries), elapsed=time.monotonic()-started)), flush=True)
    assert len(results) == len(queries)
    se.write(out/"E4_NATIVE_SUMMARY.json", dict(
        cadence="RECEIPT-SIM: same archived native second-close leg changes and atlas gates as R0",
        baseline=cv2.summary(bases), shared_intersection=cv2.summary(results), matched=cv2.matched(results, bases),
        interpretation="Shared-set-only experiment. Not equal/opposite moves, not pair-sum constraint, not a joint sentence estimator.",
        first_layer_call_safety="Both original side masks intersect, ESS>=filed floor. Insufficient rows hold existing rests under unchanged R0 conduct.",
        baseline_bound=bound["provenance"], library_sha256=c.sha256(library),
        input_archive_sha256=bound_archive, prints_sha256=c.sha256(prints_path), raw_prints_committed=False,
        scripts={Path(p).name:c.sha256(p) for p in (__file__,se.__file__,c.__file__,b.__file__)},
        result_sha256=c.sha256(target), engine_hashes=bound["conduct"],
        determinism="Two projections per query, different computational batch sizes; canonical bytes identical. Independent positive-size order-interval fill audit.",
        forecast_digest_sha256=hashlib.sha256(c.encode(digests).encode()).hexdigest()))
    assert c.bound_inputs(root)["conduct"] == bound["conduct"], "ENGINE_CHANGED"
    print("NATIVE_SHARED_COMPLETE "+c.encode(cv2.matched(results,bases)), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    run(root, root/"arb-executor/analysis/sentence_experiments/ATP_MAIN", Path(r"C:\tmp\conduct_atp_main_v1\ATP_MAIN_PRINTS.jsonl.gz"))
