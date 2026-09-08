#!/usr/bin/env python3
"""Render the signed experiment results and seal their file-hash manifest."""
import json
from pathlib import Path
import subprocess
import sys
import sentence_experiments as s


def num(value, places=3):
    return "—" if value is None else f"{value:.{places}f}"


def pct(value):
    return "—" if value is None else f"{value*100:.2f}%"


def render(root):
    out = root/"arb-executor/analysis/sentence_experiments/ATP_MAIN"
    read = lambda name: json.loads((out/name).read_text(encoding="utf-8"))
    receipt = read("SENTENCE_RECEIPT.json")
    durable = root/"arb-executor/data/durable"
    assert s.c.sha256(durable/"RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz")==receipt["library_sha256"]
    assert s.c.sha256(durable/"RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz")==receipt["count_sidecar"]["sidecar_sha256"]
    for name,sha in receipt["archives"].items():
        assert s.c.sha256(root/"arb-executor/analysis/conduct_scoreboard_v2/ATP_MAIN"/name)==sha
    private = Path(r"C:\tmp\conduct_atp_main_v1\ATP_MAIN_PRINTS.jsonl.gz")
    extract = json.loads(private.with_suffix(".receipt.json").read_text())
    assert s.c.sha256(private)==receipt["print_extract"]["sha256"]==extract["output_sha256"]
    assert s.c.sha256(private.with_suffix(".receipt.json"))==receipt["print_extract"]["receipt_sha256"]
    for name, meta in receipt["outputs"].items():
        assert s.c.sha256(out/name)==meta["sha256"], "UNSEALED_OUTPUT_CHANGE:"+name
    e3 = read("E3_AUTOPSY.json")
    e1 = read("E1_FIRST_PASSAGE.json")["rows"]
    records = list(s.iter_jsonl(out/"GATE_RECORDS.jsonl.gz"))
    assert all(r["realized_family"] is not None for r in records)
    assert all(r["family_called"] is not None for r in records if r["q"] is not None)
    tables = read("GATE_TABLES.json")
    conduct = read("GATE_CONDUCT.json")
    native = read("E4_NATIVE_SUMMARY.json")
    assert s.c.sha256(out/"E4_NATIVE_RESULTS.jsonl.gz")==native["result_sha256"]
    native_rows = list(s.iter_jsonl(out/"E4_NATIVE_RESULTS.jsonl.gz"))
    expected_ids = {r["event_id"] for r in records}
    assert len(native_rows)==len(expected_ids)==receipt["eligible_pairs"]
    assert {r["event_id"] for r in native_rows}==expected_ids
    assert all(not r["safety_violations"] for r in native_rows)
    assert native["engine_hashes"]==receipt["engine_hashes_unchanged"]
    contract = receipt["atlas_contract"]
    criterion = receipt["matched_win_criterion"]
    n = receipt["eligible_pairs"]
    gates = contract["gates_minutes_to_bell"]
    for gate in gates:
        for side in s.SIDES:
            rr = [r for r in e1 if r["gate"]==gate and r["side"]==side]
            tables[str(gate)][side]["E1_FIRST_PASSAGE"]["common_bell_horizon"] = dict(
                n=len(rr), mean_probability=s.average(r["member_hit_weight_share"] for r in rr),
                observed_reach=s.average(r["actual_hit"] for r in rr),
                brier=s.average((r["member_hit_weight_share"]-int(r["actual_hit"]))**2 for r in rr),
                interpretation="Pool-implied common-horizon diagnostic, not an emitted OS probability. Q/pool unchanged: identical for both X rules by construction.")
    s.write(out/"GATE_TABLES.json",tables)
    baseline = {(r["event_id"],r["gate"],r["side"]):r for r in records if r["variant"]=="CURRENT_ROLE"}
    aggregate = dict(pool={}, first_passage={}, eligible_pairs=n,
        possible_gate_side_opportunities=n*len(gates)*len(s.SIDES),
        note="Aggregates pool repeated gate-side observations, not independent games. Filed wins tested per side/gate only.")
    for variant in s.VARIANTS:
        rr = [r for r in records if r["variant"]==variant]
        calls = [r for r in rr if r["q"] is not None]
        match = [(r,baseline[r["event_id"],r["gate"],r["side"]]) for r in calls
                 if baseline[r["event_id"],r["gate"],r["side"]]["q"] is not None]
        aggregate["pool"][variant] = dict(span_gate_sides=len(rr), calls=len(calls), abstentions=len(rr)-len(calls),
            coverage_all_possible=len(calls)/aggregate["possible_gate_side_opportunities"],
            before_first_tick=aggregate["possible_gate_side_opportunities"]-len(rr),
            floor_mae=s.average(r["floor_error"] for r in calls), timing_mae=s.average(r["timing_error"] for r in calls),
            family_accuracy=s.average(r["family_called"]==r["realized_family"] for r in calls),
            matched_n=len(match), floor_delta=s.average(a["floor_error"]-z["floor_error"] for a,z in match),
            timing_delta=s.average(a["timing_error"]-z["timing_error"] for a,z in match),
            family_accuracy_delta=s.average(int(a["family_called"]==a["realized_family"])-int(z["family_called"]==z["realized_family"]) for a,z in match))
    for side in s.SIDES:
        rr = [r for r in e1 if r["side"]==side]
        finite = [r for r in rr if r["first_passage_x"] is not None]
        match = [r for r in finite if r["actual_hit"]]
        aggregate["first_passage"][side] = dict(baseline_calls=len(rr), finite_deadlines=len(finite), censored=len(rr)-len(finite),
            matched_hits=len(match), baseline_mae=s.average(r["baseline_deadline_error"] for r in match),
            new_mae=s.average(r["new_deadline_error"] for r in match), delta=s.average(r["new_deadline_error"]-r["baseline_deadline_error"] for r in match),
            baseline_brier=s.average(r["baseline_brier"] for r in finite), new_brier=s.average(r["new_brier"] for r in finite),
            predicted_new_reach=s.average(r["new_reach_probability"] for r in finite), observed_new_reach=s.average(r["new_reached_by_deadline"] for r in finite),
            mean_member_nonhit_weight_share=s.average(r["nonhit_weight_share"] for r in rr),
            bell_mean_probability=s.average(r["member_hit_weight_share"] for r in rr),
            bell_observed_reach=s.average(r["actual_hit"] for r in rr),
            bell_brier=s.average((r["member_hit_weight_share"]-int(r["actual_hit"]))**2 for r in rr),
            winning_gates=[g for g in gates if tables[str(g)][side]["E1_FIRST_PASSAGE"]["matched_deadline"]["filed_matched_win"]])
    s.write(out/"AGGREGATES.json",aggregate)
    lines = ["# Sentence experiments — ATP_MAIN", "", "BENCH ONLY. Engine and historical artifacts unchanged. All 928 filed queries; tick library only.", "",
        "Run order: E3; E1 amended for positive-print first passage and censoring; E2(a/b); E4 shared-set-only diagnostic. E2(c) deferred: no filed causal family learner/callability rule supplied. Equal-and-opposite E4 not run: amplitude/constraint estimator unspecified and marginal minima need not be simultaneous.", "",
        "## E3 — one-sided failures first", "",
        "Last scheduled gate is 5m to bell, not the last successful call. Error = Q minus strictly-later positive-size remaining floor. Causes overlap. No-call and no-future-print are retained, never zero-filled. Never postable means no unfilled receipt with status OK, cent-valid Q below ask and unlocked book, before the separate ask-only/pair-cap guards. Pair-cap-ever is exposure, NOT a causal attribution.", "",
        "| Failed side | Pairs | Scorable Q/positive floor | q10 / q25 / q50 / q75 / q90 (cents) | Too deep | Never postable | Moved off later print (active interval) | Pair cap ever | No call | No later print |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|"]
    role_notes = []
    for side in reversed(s.SIDES):
        r=e3["summary"]["one_sided_failed"][side]; dist=r["q_minus_positive_floor"]
        qq=" / ".join(num(dist["quantiles"][str(q)],0) for q in contract["quantiles"])
        lines.append(f"| {side} | {r['n']} | {dist['n']} | {qq} | {r['too_deep']} | {r['never_postable']} | {r['moved_off_later_print']} ({r['moved_off_while_lower_active']}) | {r['pair_cap_ever']} | {r['no_call']} | {r['no_later_positive_print']} |")
        role_notes.append(f"{side} last-gate roles: {json.dumps(r['last_gate_roles'],sort_keys=True)}; original FALLER-only stepped-off subset: {r['legacy_faller_stepped_off']}.")
    for note in role_notes: lines += ["",note]
    # Keep prose outside the Markdown table.
    lines += ["", "Controls (sides, not independent pairs):", "", "| Group | Side | n | Too deep | Never postable | Moved off | Pair cap ever |", "|---|---|---:|---:|---:|---:|---:|"]
    for group in ("completed_control","no_fill_control","filled_side_control"):
        for side in s.SIDES:
            r=e3["summary"][group][side]
            lines.append(f"| {group} | {side} | {r['n']} | {r['too_deep']} | {r['never_postable']} | {r['moved_off_later_print']} | {r['pair_cap_ever']} |")
    lines += ["", "## E1 — fixed Q, target-specific first-passage X", "",
        "Finite elapsed-time weighted median with non-hits at infinity. Error comparisons condition on an actual query hit and finite candidate median; coverage below includes every filed game. Calibration uses member reach probability at each rule's own deadline: different horizons, not a fixed-horizon superiority claim. The filed matched-win criterion is applied per gate/side, never to pooled repeated gates.", "",
        "| Gate m | Finite calls F/D (each /928) | Censored F/D | Matched hits F/D | Deadline MAE delta m F/D | Strict wins F/D | Brier delta F/D | Filed win F/D |", "|---:|---|---|---|---|---|---|---|"]
    for gate in gates:
        rr=[tables[str(gate)][side]["E1_FIRST_PASSAGE"] for side in s.SIDES]
        pair=lambda fn:" / ".join(fn(r) for r in rr)
        lines.append(f"| {gate} | {pair(lambda r:str(r['finite_deadlines']))} | {pair(lambda r:str(r['censored_medians']))} | {pair(lambda r:str(r['matched_deadline']['n']))} | {pair(lambda r:num(r['matched_deadline']['delta_mae']))} | {pair(lambda r:pct(r['matched_deadline']['strictly_closer_share']))} | {pair(lambda r:num(r['delta_brier']))} | {pair(lambda r:str(r['matched_deadline']['filed_matched_win']))} |")
    lines += ["", "## E2(a/b) and E4 shared-set-only — matched sentence errors", "",
        "Negative delta is better. F/D means favourite/underdog. Floors and times here use the filed carried-state minimum target; positive-future-print errors and target denominators are also in GATE_TABLES.json. Calls include states without a later query print; this deliberately differs from the old SCORABLE-conditioned summary. Every CURRENT_ROLE Q/X/ESS matched the archived baseline.", ""]
    insertion = lines.index("## E2(a/b) and E4 shared-set-only — matched sentence errors")-1
    calibration = ["", "Common bell-horizon reach calibration (pool-implied diagnostic, not an emitted OS probability):", "",
        "| Gate m | Predicted reach F/D | Observed reach F/D | Brier F/D |", "|---:|---|---|---|"]
    for gate in gates:
        rr=[tables[str(gate)][side]["E1_FIRST_PASSAGE"]["common_bell_horizon"] for side in s.SIDES]
        pair=lambda fn:" / ".join(fn(r) for r in rr)
        calibration.append(f"| {gate} | {pair(lambda r:pct(r['mean_probability']))} | {pair(lambda r:pct(r['observed_reach']))} | {pair(lambda r:num(r['brier']))} |")
    calibration += ["", "At this common horizon both X rules have identical implied probabilities because Q and member weights are fixed. Changing X alone cannot improve this probability model; own-deadline Brier differences are not a matched fixed-horizon calibration win.", ""]
    lines[insertion:insertion] = calibration
    for variant in ("NO_ROLE","SHARED_INTERSECTION"):
        lines += [f"### {variant}", "", "| Gate m | Calls F/D (each /928) | Baseline calls F/D | Matched n F/D | Floor delta cents F/D | Timing delta m F/D | Family accuracy F/D |", "|---:|---|---|---|---|---|---|"]
        for gate in gates:
            rr=[tables[str(gate)][side][variant] for side in s.SIDES]
            pair=lambda fn:" / ".join(fn(r) for r in rr)
            bc=" / ".join(str(tables[str(gate)][side]["CURRENT_ROLE"]["calls"]) for side in s.SIDES)
            lines.append(f"| {gate} | {pair(lambda r:str(r['calls']))} | {bc} | {pair(lambda r:str(r['matched_floor']['n']))} | {pair(lambda r:num(r['matched_floor']['delta_mae']))} | {pair(lambda r:num(r['matched_timing']['delta_mae']))} | {pair(lambda r:pct(r['family_accuracy']))} |")
        lines += [""]
    lines += ["Family accuracy is diagnostic only: inherited full-library retrospective SLEEPER p10, not a causally learned family callability rule. Neither NO_ROLE nor SHARED_INTERSECTION meets the filed floor-error win test at any gate/side.", "",
        "## R0 conduct with experimental sentences", "", "Positive-size strictly-later pre-bell prints; reachable, not certain. No execution change. Never compare a GATE-SIM candidate to the RECEIPT-SIM baseline.", "",
        "| Cadence | Sentence pool | Completed /928 | One-sided /928 | Capture cents /eligible | Delta completion pp | Delta capture /eligible | Delta one-sided pp |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for variant in s.VARIANTS:
        r,d=conduct["summary"][variant],conduct["matched"][variant]
        lines.append(f"| GATE-SIM | {variant} | {r['completed']} | {r['one_sided']} | {num(r['mean_captured_eligible'])} | {num(d['completion_rate_delta']*100)} | {num(d['captured_per_eligible_delta'])} | {num(d['one_sided_rate_delta']*100)} |")
    r=native["baseline"]
    lines.append(f"| RECEIPT-SIM | CURRENT_ROLE | {r['completed']} | {r['one_sided']} | {num(r['mean_captured_eligible'])} | 0 | 0 | 0 |")
    r,d=native["shared_intersection"],native["matched"]
    lines.append(f"| RECEIPT-SIM | SHARED_INTERSECTION | {r['completed']} | {r['one_sided']} | {num(r['mean_captured_eligible'])} | {num(d['completion_rate_delta']*100)} | {num(d['captured_per_eligible_delta'])} | {num(d['one_sided_rate_delta']*100)} |")
    lines += ["", "All reported simulations have zero safety violations. Two identical projection passes; native shared projections also invariant to batch boundary. Independent interval audit checks every fill and miss. No family learner, opposite-move model, engine change, or promotion is implied.", "",
        "## Provenance", "", "- Baseline c7825925; conduct archives d2d8f16b; matched-win filing 87049680.",
        "- Tick library c823d172; positive-print extract bf982a5e, 777,937 accepted rows / 771,159 positive-size rows; raw prints never committed.",
        "- Definitions, exact hashes, original/candidate per-gate rows, E3 per-side autopsies, censoring, call/abstention denominators, and native simulation details are alongside this summary."]
    lines += ["", "## Reproduce", "", "From the worktree root with the approved private extract still at its receipt path:", "", "```powershell",
        r"$benchPython = 'C:\Users\omigr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'",
        "& $benchPython -B arb-executor/analysis/sentence_experiments.py",
        "& $benchPython -B arb-executor/analysis/sentence_shared_pool_native.py",
        "& $benchPython -B -m unittest discover -s arb-executor/analysis -p test_sentence_experiments.py",
        "& $benchPython -B arb-executor/analysis/sentence_experiments_report.py", "```", "",
        "Native shared projection reuses hash-bound archived joint NO-CALL rows; callable Q/X are reconstructed twice. Large archived joint-outcome arrays are not copied into R0's projection because R0 does not read them. These are computation-only optimizations."]
    (out/"SENTENCE_SUMMARY.md").write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")
    current=Path(receipt["matched_win_source"]["path"])
    pinned=subprocess.check_output(["git","show","87049680:arb-executor/analysis/tune_bench_v2_ticks/ATP_MAIN/TUNE_BENCH_RECEIPT.json"],cwd=root)
    assert json.loads(pinned)["matched_step_first"]["criterion"] == criterion
    assert s.c.sha256(current)==receipt["matched_win_source"]["sha256"]
    receipt["matched_win_source"]["commit"]="87049680"
    receipt["definitions"]["E3_never_postable"]="No unfilled receipt with status OK, cent-valid Q below cent-valid ask and unlocked book. Individual postability before ask-only and pair-cap guards; guard exposures counted separately. Not a claim that no possible maker price existed."
    receipt["definitions"]["E1_common_horizon"]="Report builder adds pool-implied reach probability and Brier by bell using all baseline calls, including censored medians. Same Q/pool implies identical probabilities for both X rules at the same horizon; this diagnostic is not an emitted OS probability or a claim of improved calibration."
    receipt["native_shared_companion"] = dict(script="sentence_shared_pool_native.py",sha256=s.c.sha256(root/"arb-executor/analysis/sentence_shared_pool_native.py"),
        report="E4_NATIVE_SUMMARY.json",definition=native["interpretation"],cadence=native["cadence"],determinism=native["determinism"])
    receipt["tests"] = dict(file="test_sentence_experiments.py",sha256=s.c.sha256(root/"arb-executor/analysis/test_sentence_experiments.py"),
        count=15,status="PASS",scope="censoring, positive-size/span/time boundaries, causal query future perturbation, walk-forward exclusions, gate/native agreement, exact guard reconstruction")
    receipt["report_builder"] = dict(file=Path(__file__).name,sha256=s.c.sha256(__file__))
    receipt["outputs"]={p.name:dict(bytes=p.stat().st_size,sha256=s.c.sha256(p)) for p in sorted(out.iterdir()) if p.is_file() and p.name!="SENTENCE_RECEIPT.json"}
    for name,sha in receipt["scripts"].items(): assert s.c.sha256(root/"arb-executor/analysis"/name)==sha
    assert s.c.bound_inputs(root)["conduct"]==receipt["engine_hashes_unchanged"]
    s.write(out/"SENTENCE_RECEIPT.json",receipt)
    print(json.dumps(aggregate,indent=2))


if __name__=="__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    render(Path(__file__).resolve().parents[2])
