"""Deterministic compact reports from completed, hash-bound feature bench runs.

Only derived diagnostics arrays are read, one game at a time, to distinguish
observed zero from missing/unknown. Arrays, raw captures and witnesses are not
copied. PRIMARY alone supplies coverage; strict June remains a separate table.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np


CATEGORIES = ("ATP_MAIN", "ATP_CHALL")
ARTIFACTS = tuple("FEATURE_PANEL_"+name+".json" for name in
                  ("SCOREBOARD", "DIAGNOSTICS", "QUERIES", "NAMED_CHECKS"))
RECEIPT = "FEATURE_PANEL_RECEIPT.json"
TARGETS = ("carried", "reachable")
SECTIONS = ("all_receipts", "gates", "filed_scorable_gates")


def required_variants(receipt):
    """Reconstruct the complete six-block experiment from its filed fields."""
    fields = receipt.get("fields", [])
    names = [field["name"] for field in fields]
    if not names or len(set(names)) != len(names):
        raise ValueError("INVALID_OR_MISSING_FIELD_REGISTRY")
    blocks = list(dict.fromkeys(field["block"] for field in fields if field.get("block") is not None))
    if len(blocks) != 6 or any(not isinstance(block, str) or not block for block in blocks):
        raise ValueError("REQUIRE_SIX_REGISTERED_FEATURE_BLOCKS")
    expected = [dict(name="FIRST", blocks=[])]
    expected += [dict(name=f"CUMULATIVE_{i}", blocks=blocks[:i]) for i in range(1, len(blocks)+1)]
    expected += [dict(name="LEAVE_OUT_"+block, blocks=[other for other in blocks if other != block])
                 for block in blocks]
    if receipt.get("variants") != expected:
        raise ValueError("INCOMPLETE_OR_INCORRECT_VARIANT_REGISTRY")
    return expected


def checked_contract(board, receipt):
    contract = board["all_receipts"].get("contract")
    if not contract or any(board[section].get("contract") != contract for section in SECTIONS):
        raise ValueError("MISSING_OR_INCONSISTENT_BASELINE_SCORE_CONTRACT")
    quantiles = contract.get("quantiles", [])
    minimum = contract.get("minimum_matched_queries")
    share = contract.get("minimum_strictly_closer_share")
    ess = contract.get("no_call_ess_floor")
    if (not quantiles or .5 not in quantiles or len(set(quantiles)) != len(quantiles)
            or any(not isinstance(q, (int, float)) or not math.isfinite(q) or not 0 <= q <= 1 for q in quantiles)
            or not isinstance(minimum, int) or minimum <= 0
            or not isinstance(share, (int, float)) or not 0 <= share <= 1
            or not isinstance(ess, (int, float)) or not math.isfinite(ess) or ess <= 0
            or contract.get("engine_authorship_enabled") is not False):
        raise ValueError("INVALID_BASELINE_SCORE_CONTRACT")
    baseline_sha = receipt.get("baseline_receipt_sha256", "")
    if len(baseline_sha) != 64 or any(c not in "0123456789abcdef" for c in baseline_sha):
        raise ValueError("MISSING_BASELINE_RECEIPT_BINDING")
    return contract


def required_metrics(contract):
    """Required core output schema, including explicit unavailable entries."""
    names = {"floor_crps_cents", "floor_signed_error_cents", "floor_absolute_error_cents",
             "floor_timing_signed_error_minutes", "floor_timing_absolute_error_minutes",
             "timing_candidate_ess", "family_accuracy", "family_brier"}
    quantiles = contract["quantiles"]
    qname = lambda q: "q"+format(q*100, ".12g")
    names.update("quantiles."+qname(q)+".signed_error_cents" for q in quantiles)
    for lo in quantiles:
        for hi in quantiles:
            if lo < .5 < hi and math.isclose(lo+hi, 1):
                names.update("floor_band."+qname(lo)+"_"+qname(hi)+"."+part
                             for part in ("coverage", "nominal_calibration_gap"))
    names.update("reach.support."+part for part in
                 ("level_count", "mean_probability", "observed_rate", "calibration_gap", "brier"))
    names.update("reach.q50."+part for part in ("probability", "outcome", "calibration_gap", "brier"))
    return names


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024*1024), b""):
            result.update(block)
    return result.hexdigest()


def contained(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("UNSAFE_MANIFEST_PATH:"+str(relative))
    path = (root/relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("MANIFEST_PATH_ESCAPES_RUN")
    return path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_file(root, name, sha, size=None):
    path = contained(root, name)
    if not path.is_file():
        raise ValueError("MISSING_COMPLETED_ARTIFACT:"+str(path))
    if size is not None and path.stat().st_size != size:
        raise ValueError("ARTIFACT_SIZE_MISMATCH:"+name)
    if digest(path) != sha:
        raise ValueError("ARTIFACT_HASH_MISMATCH:"+name)
    return path


def validate_cell(cell, variants):
    if set(cell.get("all_eligible", {})) != set(variants) or set(cell.get("matched_to_first", {})) != set(variants[1:]):
        raise ValueError("INCOMPLETE_CELL_VARIANTS")
    for variant, own in cell["all_eligible"].items():
        n, called = own["eligible_receipts"], own["called_receipts"]
        target_n = own["target_available_receipts"]
        statuses = own.get("statuses", {})
        if (not 0 <= called <= n or own["abstained_receipts"] != n-called
                or not 0 <= target_n <= n or own["target_missing_receipts"] != n-target_n
                or any(not isinstance(value, int) or value < 0 for value in statuses.values())
                or sum(statuses.values()) != n):
            raise ValueError("INVALID_CELL_DENOMINATORS_OR_STATUSES")
        if any(not 0 <= metric["n"] <= called for metric in own["metrics"].values()):
            raise ValueError("INVALID_METRIC_DENOMINATOR")
        if variant != "FIRST":
            match = cell["matched_to_first"][variant]
            if (match["eligible_receipts"] != n or not 0 <= match["n"] <= match["both_called_receipts"] <= called
                    or match["both_called_receipts"] > cell["all_eligible"]["FIRST"]["called_receipts"]
                    or not 0 <= match["strictly_closer"]+match["tied"] <= match["n"]):
                raise ValueError("INVALID_MATCHED_DENOMINATOR")
            for metric in match["metrics"].values():
                counts = {metric[part]["n"] for part in ("variant", "baseline", "delta")}
                if len(counts) != 1 or not 0 <= next(iter(counts)) <= match["both_called_receipts"]:
                    raise ValueError("INVALID_MATCHED_METRIC_DENOMINATOR")


def read_run(directory):
    root = Path(directory).resolve()
    receipt_path = root/RECEIPT
    if not receipt_path.is_file():
        raise ValueError("INCOMPLETE_RUN_NO_FINAL_RECEIPT:"+str(root))
    receipt = load_json(receipt_path)
    if receipt.get("status") != "BENCH_ONLY_NO_ENGINE_CHANGE" or receipt.get("category") not in CATEGORIES:
        raise ValueError("NOT_A_COMPLETED_FEATURE_RUN")
    outputs = receipt.get("outputs", {})
    if not receipt.get("source_registry") or not set(ARTIFACTS).issubset(outputs):
        raise ValueError("INCOMPLETE_OUTPUT_OR_SOURCE_MANIFEST")
    for name, info in sorted(outputs.items()):
        verify_file(root, name, info["sha256"], info["bytes"])
    payloads = {name: load_json(root/name) for name in ARTIFACTS}
    diagnostics = payloads[ARTIFACTS[1]]
    queries = payloads[ARTIFACTS[2]]
    category = receipt["category"]
    seen, primary, strict = set(), set(), set()
    for row in diagnostics:
        if row.get("category") != category or row.get("stream") not in ("PRIMARY", "STRICT_HOLDOUT"):
            raise ValueError("DIAGNOSTIC_CATEGORY_OR_STREAM_MISMATCH")
        key = (row["event_id"], row["stream"])
        if key in seen:
            raise ValueError("DUPLICATE_DIAGNOSTIC_GAME_STREAM")
        seen.add(key)
        (primary if row["stream"] == "PRIMARY" else strict).add(row["event_id"])
        verify_file(root, row["path"], row["sha256"])
        scale = outputs.get(row["scale_file"])
        if not scale or scale["sha256"] != row["scale_sha256"]:
            raise ValueError("UNBOUND_DIAGNOSTIC_SCALE")
    if len(primary) != receipt.get("eligible_games") or len(seen) != receipt.get("evaluated_stream_games"):
        raise ValueError("INCOMPLETE_DIAGNOSTIC_POPULATION")
    query_keys = [(row["event_id"], row["stream"]) for row in queries]
    if len(query_keys) != len(set(query_keys)) or set(query_keys) != seen:
        raise ValueError("QUERY_DIAGNOSTIC_COHORT_MISMATCH")
    heldout = set(receipt.get("heldout_months", []))
    expected_strict = {row["event_id"] for row in diagnostics
                       if row["stream"] == "PRIMARY" and row["month"] in heldout}
    if strict != expected_strict:
        raise ValueError("INCOMPLETE_STRICT_HOLDOUT_POPULATION")
    board = payloads[ARTIFACTS[0]]
    if not {"all_receipts", "gates", "filed_scorable_gates"}.issubset(board):
        raise ValueError("MISSING_SCOREBOARD_COHORT")
    registry = required_variants(receipt)
    variants = [row["name"] for row in registry]
    contract = checked_contract(board, receipt)
    for section, scorer in board.items():
        if section not in ("all_receipts", "gates", "filed_scorable_gates"):
            continue
        if scorer.get("variants") != variants:
            raise ValueError("SCOREBOARD_VARIANT_MISMATCH")
        group_keys = set()
        for cell in scorer["groups"]:
            group = cell["group"]
            key = canonical(group)
            if key in group_keys:
                raise ValueError("DUPLICATE_SCOREBOARD_GROUP")
            group_keys.add(key)
            if group.get("category") != category:
                raise ValueError("SCOREBOARD_CATEGORY_MISMATCH")
            if set(cell["targets"]) != set(TARGETS):
                raise ValueError("INCOMPLETE_TARGET_KINDS")
            filed = section == "filed_scorable_gates" and group.get("stream", "").endswith("_FILED_SCORABLE_GATES")
            for target in cell["targets"].values():
                validate_cell(target, variants)
                for match in target["matched_to_first"].values():
                    if not filed and (match.get("qualifies") is not None or match.get("filed_side_gate_scope")):
                        raise ValueError("UNFILED_QUALIFICATION_PUBLISHED")
                    if filed:
                        scope = (group.get("side") is not None and group.get("gate") is not None
                                 and match["n"] == match["distinct_matched_games"])
                        qualifies = (match["n"] >= contract["minimum_matched_queries"] and
                                     match["strictly_closer"] >= contract["minimum_strictly_closer_share"]*match["n"])
                        if match.get("filed_side_gate_scope") != scope or match.get("qualifies") != (qualifies if scope else None):
                            raise ValueError("FILED_QUALIFICATION_CONTRACT_MISMATCH")
    expected_receipts = defaultdict(int)
    for row in diagnostics:
        expected_receipts[row["stream"]+"_ALL_RECEIPTS"] += row["receipts"]*len(row["coverage"])
    aggregate_groups = {row["group"]["stream"]:row for row in board["all_receipts"]["groups"]
                        if set(row["group"]) == {"category", "stream"}}
    if set(aggregate_groups) != set(expected_receipts):
        raise ValueError("MISSING_ALL_RECEIPT_COHORT_SUMMARY")
    for stream, expected in expected_receipts.items():
        for target in ("carried", "reachable"):
            cell = aggregate_groups[stream]["targets"][target]
            if any(cell["all_eligible"][variant]["eligible_receipts"] != expected for variant in variants):
                raise ValueError("SCOREBOARD_DIAGNOSTIC_DENOMINATOR_MISMATCH")
    expected_months, expected_gates, expected_events = defaultdict(int), defaultdict(int), Counter()
    for row in diagnostics:
        sides = len(row["coverage"])
        expected_months[(row["stream"]+"_ALL_RECEIPTS", row["month"])] += row["receipts"]*sides
        expected_events[row["stream"]] += 1
        with np.load(contained(root, row["path"]), allow_pickle=False) as data:
            if "is_gate" not in data or data["is_gate"].shape != (row["receipts"],):
                raise ValueError("MISSING_DIAGNOSTIC_GATE_MEMBERSHIP")
            flags = np.asarray(data["is_gate"])
            if not np.all((flags == 0) | (flags == 1)):
                raise ValueError("INVALID_DIAGNOSTIC_GATE_MEMBERSHIP")
            expected_gates[row["stream"]+"_GATES"] += int(np.count_nonzero(flags))*sides
    monthly = {(row["group"]["stream"], row["group"]["month"]): row
               for row in board["all_receipts"]["groups"]
               if set(row["group"]) == {"category", "stream", "month"}}
    if set(monthly) != set(expected_months):
        raise ValueError("MISSING_MONTHLY_RECEIPT_COHORT")
    for key, expected in expected_months.items():
        if any(monthly[key]["targets"][target]["all_eligible"][variant]["eligible_receipts"] != expected
               for target in TARGETS for variant in variants):
            raise ValueError("MONTHLY_DIAGNOSTIC_DENOMINATOR_MISMATCH")
    gates = {}
    for row in board["gates"]["groups"]:
        group = row["group"]
        if set(group) != {"category", "stream", "side", "gate"} or group["stream"] not in expected_gates:
            raise ValueError("INVALID_GATE_GROUP")
        gates[(group["stream"], group["side"], group["gate"])] = row
    for stream, expected in expected_gates.items():
        for target in TARGETS:
            for variant in variants:
                observed = sum(row["targets"][target]["all_eligible"][variant]["eligible_receipts"]
                               for key, row in gates.items() if key[0] == stream)
                if observed != expected:
                    raise ValueError("GATE_DIAGNOSTIC_DENOMINATOR_MISMATCH")
    for row in board["filed_scorable_gates"]["groups"]:
        group = row["group"]
        key = (group["stream"].replace("_FILED_SCORABLE_GATES", "_GATES"), group["side"], group["gate"])
        if key not in gates:
            raise ValueError("FILED_CELL_WITHOUT_ELIGIBLE_GATE")
        for target in TARGETS:
            for variant in variants:
                n = row["targets"][target]["all_eligible"][variant]["eligible_receipts"]
                if n > gates[key]["targets"][target]["all_eligible"][variant]["eligible_receipts"]:
                    raise ValueError("FILED_DENOMINATOR_EXCEEDS_ELIGIBLE_GATE")
    conduct = {row["group"]["stream"]: row for row in board["all_receipts"].get("r0_conduct", [])
               if set(row["group"]) == {"category", "stream"}}
    if set(conduct) != set(expected_events):
        raise ValueError("MISSING_R0_CONDUCT_COHORT")
    for stream, expected in expected_events.items():
        if set(conduct[stream]["variants"]) != set(variants):
            raise ValueError("INCOMPLETE_R0_VARIANTS")
        for row in conduct[stream]["variants"].values():
            n = row["evaluated_events"]
            if row["eligible_events"] != expected or not 0 <= n <= expected or row["missing_events"] != expected-n:
                raise ValueError("R0_EVENT_DENOMINATOR_MISMATCH")
            if any(row["metrics"].get(key, {}).get("n", 0) != n for key in ("completed", "one_sided", "captured_cents")):
                raise ValueError("R0_METRIC_DENOMINATOR_MISMATCH")
    return dict(root=root, receipt=receipt, diagnostics=diagnostics, board=board, variants=variants, contract=contract,
                provenance=dict(category=category, run_directory=str(root),
                    receipt_sha256=digest(receipt_path), baseline_receipt_sha256=receipt.get("baseline_receipt_sha256"),
                    source_registry=receipt["source_registry"],
                    diagnostics_manifest_sha256=outputs[ARTIFACTS[1]]["sha256"],
                    outputs={name: info for name, info in sorted(outputs.items())},
                    diagnostic_array_manifest_sha256=hashlib.sha256(canonical([
                        {key: row[key] for key in ("event_id", "stream", "path", "sha256", "scale_file", "scale_sha256")}
                        for row in sorted(diagnostics, key=lambda r:(r["event_id"], r["stream"]))]).encode()).hexdigest()))


def coverage_rows(run):
    """Use PRIMARY once; a finite numeric zero is an available observation."""
    totals = defaultdict(lambda: dict(eligible_receipts=0, available_receipts=0,
        missing_receipts=0, unknown_receipts=0, observed_zero_values=0, zero_count_unknown_receipts=0,
        class_counts=Counter()))
    primary = [row for row in run["diagnostics"] if row["stream"] == "PRIMARY"]
    registry = {field["name"]: field for field in run["receipt"]["fields"]}
    fields = sorted(set(registry) | {name for row in primary for side in row["coverage"].values() for name in side["fields"]})
    for row in primary:
        path = contained(run["root"], row["path"])
        with np.load(path, allow_pickle=False) as data:
            names = [str(name) for name in data["feature_names"]]
            raw = np.asarray(data["raw_value"], dtype=float)
            diagnostic_sides = row.get("diagnostics", [])
            if raw.ndim != 3 or raw.shape[0] != row["receipts"] or raw.shape[2] != len(names):
                raise ValueError("DIAGNOSTIC_ARRAY_SHAPE_MISMATCH")
            if "empirical_rank" not in data or data["empirical_rank"].shape != raw.shape:
                raise ValueError("MISSING_PER_RECEIPT_EMPIRICAL_RANKS")
            if len(diagnostic_sides) != raw.shape[1]:
                raise ValueError("MISSING_DIAGNOSTIC_SIDE_ORDER")
            for side, diagnostic in enumerate(diagnostic_sides):
                prefix = row["event_id"]+"-"
                ticker = diagnostic.get("ticker", "")
                if not ticker.startswith(prefix):
                    raise ValueError("DIAGNOSTIC_TICKER_MISMATCH")
                leg = ticker[len(prefix):]
                coverage = row["coverage"][leg]
                n = coverage["receipts"]
                if n != row["receipts"]:
                    raise ValueError("COVERAGE_RECEIPT_COUNT_MISMATCH")
                for field in fields:
                    total = totals[(row["category"], row["month"], field)]
                    total["eligible_receipts"] += n
                    count = coverage["fields"].get(field)
                    if count is None:
                        total["unknown_receipts"] += n
                        total["zero_count_unknown_receipts"] += n
                        continue
                    if not isinstance(count, int) or not 0 <= count <= n:
                        raise ValueError("INVALID_FIELD_COVERAGE_COUNT")
                    total["available_receipts"] += count
                    total["missing_receipts"] += n-count
                    if field in names:
                        values = raw[:, side, names.index(field)]
                    elif leg+"__"+field in data:
                        values = np.asarray(data[leg+"__"+field], dtype=float)
                    elif field == "cadence_class" and "cadence_rank_interval" in data:
                        values = np.asarray(data["cadence_rank_interval"], dtype=float)[:, side]
                    else:
                        total["zero_count_unknown_receipts"] += n
                        continue
                    finite = np.isfinite(values)
                    # Availability fields count true source availability in
                    # the manifest, not the number of known boolean statuses.
                    availability_flag = field in ("odds_available", "ws_depth_available")
                    observed_count = int(np.count_nonzero(finite & (values == 1))) if availability_flag else int(finite.sum())
                    if values.shape != (n,) or observed_count != count:
                        raise ValueError("COVERAGE_ARRAY_COUNT_MISMATCH:"+field)
                    total["observed_zero_values"] += int(np.count_nonzero(finite & (values == 0)))
                    if registry.get(field, {}).get("kind") == "categorical":
                        codes, counts = np.unique(values[finite], return_counts=True)
                        for code, count in zip(codes, counts):
                            label = "code:"+format(float(code), ".12g")
                            if field == "spread_band":
                                labels = diagnostic.get("spread_band_labels", [])
                                if code == int(code) and 0 <= int(code) < len(labels):
                                    label = str(labels[int(code)])
                            elif field == "cadence_class":
                                label = "filed_quantile_interval:"+format(float(code), ".12g")
                            total["class_counts"][label] += int(count)
    return [dict(category=category, month=month, field=field, **value,
                 available_share=value["available_receipts"]/value["eligible_receipts"] if value["eligible_receipts"] else None)
            for (category, month, field), value in sorted(totals.items())]


def merge_metric(rows):
    n = sum(row.get("n", 0) for row in rows)
    if any(row.get("n", 0) and (not isinstance(row.get("mean"), (float, int))
                               or not math.isfinite(row["mean"])) for row in rows):
        raise ValueError("INVALID_METRIC_SUMMARY")
    return dict(n=n, mean=math.fsum(row["n"]*row["mean"] for row in rows if row.get("n", 0))/n if n else None,
                availability="OBSERVED" if n else "NO_FINITE_SCORED_OBSERVATIONS")


def aggregate_cells(cells, variant, contract):
    own = [cell["all_eligible"][variant] for cell in cells]
    names = sorted(required_metrics(contract) | {name for row in own for name in row["metrics"]})
    eligible = sum(row["eligible_receipts"] for row in own)
    called = sum(row["called_receipts"] for row in own)
    result = dict(eligible_receipts=eligible, called_receipts=called, abstained_receipts=eligible-called,
        call_coverage=called/eligible if eligible else None,
        target_available_receipts=sum(row["target_available_receipts"] for row in own),
        target_missing_receipts=sum(row["target_missing_receipts"] for row in own),
        statuses=dict(sorted(sum((Counter(row["statuses"]) for row in own), Counter()).items())),
        metric_missing_reason="NO_FINITE_SCORED_OBSERVATIONS means no valid prediction/target pair; status and target-missing counts are separate, and finer causes are not retained by the scorer",
        ess=merge_metric([row["ess"] for row in own]),
        candidate_floor_available_weight_share=merge_metric([row["candidate_floor_available_weight_share"] for row in own]),
        metrics={name:merge_metric([row["metrics"].get(name, {}) for row in own]) for name in names})
    if variant != "FIRST":
        matched = [cell["matched_to_first"][variant] for cell in cells]
        mn = sum(row["n"] for row in matched)
        wins = sum(row["strictly_closer"] for row in matched)
        metrics = sorted(required_metrics(contract) | {name for row in matched for name in row["metrics"]})
        result["matched_to_first"] = dict(n=mn, strictly_closer=wins,
            strictly_closer_share=wins/mn if mn else None, tied=sum(row["tied"] for row in matched),
            both_called_receipts=sum(row["both_called_receipts"] for row in matched),
            matched_floor_coverage=mn/eligible if eligible else None,
            metrics={name:{part: merge_metric([row["metrics"].get(name, {}).get(part, {}) for row in matched])
                           for part in ("variant", "baseline", "delta")} for name in metrics})
    return result


def forecast_rows(run):
    rows, qualifications = [], []
    for section in SECTIONS:
        grouped = defaultdict(list)
        for row in run["board"][section]["groups"]:
            group = row["group"]
            # ALL already contains aggregate, month and month/side rollups.
            # GATE groups are disjoint side/gate cells and may be summed.
            if section == "all_receipts" and set(group) not in ({"category", "stream"}, {"category", "stream", "month"}):
                continue
            for target, cell in row["targets"].items():
                grouped[(group["stream"], group.get("month", ""), target)].append(cell)
                if section == "filed_scorable_gates":
                    for variant, matched in cell["matched_to_first"].items():
                        qualifications.append(dict(category=group["category"], stream=group["stream"],
                            side=group.get("side"), gate=group.get("gate"), target=target, variant=variant,
                            n=matched["n"], strictly_closer=matched["strictly_closer"], tied=matched["tied"],
                            eligible_receipts=matched["eligible_receipts"], both_called_receipts=matched["both_called_receipts"],
                            distinct_matched_games=matched["distinct_matched_games"], filed_side_gate_scope=matched["filed_side_gate_scope"],
                            qualifies=matched.get("qualifies"), engine_authorship_enabled=False))
        for (stream, month, target), cells in sorted(grouped.items()):
            for variant in run["variants"]:
                rows.append(dict(category=run["receipt"]["category"], cohort=section, stream=stream,
                                 month=month or None, target=target, variant=variant,
                                 **aggregate_cells(cells, variant, run["contract"])))
    return rows, qualifications


def build_report(run_directories):
    runs = [read_run(path) for path in run_directories]
    categories = [run["receipt"]["category"] for run in runs]
    if set(categories) != set(CATEGORIES) or len(categories) != len(CATEGORIES):
        raise ValueError("REQUIRE_ONE_COMPLETED_MAIN_AND_CHALL_RUN")
    runs.sort(key=lambda run:CATEGORIES.index(run["receipt"]["category"]))
    if any(run["variants"] != runs[0]["variants"] for run in runs):
        raise ValueError("CROSS_TOUR_VARIANT_MISMATCH")
    forecasts, qualifications, coverage, conduct, diagnostic_index, contracts, cohort_status = [], [], [], [], [], [], []
    for run in runs:
        coverage.extend(coverage_rows(run))
        rows, filed = forecast_rows(run)
        forecasts.extend(rows)
        qualifications.extend(filed)
        contracts.append(dict(category=run["receipt"]["category"],
            baseline_receipt_sha256=run["receipt"]["baseline_receipt_sha256"], **run["contract"]))
        for row in sorted(run["diagnostics"], key=lambda r:(r["event_id"], r["stream"])):
            diagnostic_index.append(dict(
                **{key: row[key] for key in ("category", "event_id", "month", "stream", "receipts", "path", "sha256",
                                             "scale_file", "scale_sha256", "scale_cutoff")},
                run_directory=str(run["root"]),
                side_order=[side["ticker"] for side in row["diagnostics"]],
                source_diagnostics=row["diagnostics"],
                cadence_interval_boundaries=row.get("cadence_interval_boundaries"),
                reader="NPZ epoch/gate/is_gate index receipts; raw_value and empirical_rank are receipt x side x feature_names; categorical codes are not ordinal ranks"))
        for stream in sorted({row["stream"] for row in run["diagnostics"]}):
            for section in SECTIONS:
                name = stream+"_"+section.upper()
                count = sum(row["group"].get("stream") == name for row in run["board"][section]["groups"])
                cohort_status.append(dict(category=run["receipt"]["category"], stream=name, cohort=section,
                    recorded_cells=count, status="RECORDED" if count else "NO_CELLS_RECORDED",
                    independent_filed_denominator="Not reconstructible from derived diagnostics; recorded cells checked as subsets of eligible gates" if section == "filed_scorable_gates" else None))
        for row in run["board"]["all_receipts"].get("r0_conduct", []):
            if set(row["group"]) == {"category", "stream"}:
                conduct.append(row)
    return dict(status="VERIFIED_COMPACT_FEATURE_PANEL_REPORT", categories=list(CATEGORIES),
        variants=runs[0]["variants"], variant_registry=runs[0]["receipt"]["variants"],
        field_registries=[dict(category=run["receipt"]["category"], fields=run["receipt"]["fields"]) for run in runs],
        score_contracts=contracts, diagnostic_index=diagnostic_index, cohort_status=cohort_status,
        heldout_months=sorted({month for run in runs for month in run["receipt"]["heldout_months"]}),
        provenance=[run["provenance"] for run in runs],
        coverage=coverage, forecasts=forecasts, r0_conduct=conduct, filed_qualifications=qualifications,
        definitions=dict(coverage="PRIMARY once per game, side and receipt; strict holdout does not double-count coverage",
            zero="Numeric/code zero counts as observed, never imputed. For odds/ws availability flags, zero means known source-unavailable, one means available; unknown stays separate.",
            errors="Each metric retains its finite denominator; NO-CALL is not zero prediction error",
            unavailable_metrics="Required metrics have n=0, mean=null, and explicit availability status when no finite score exists; a missing score is never a measured zero",
            receipt_reader="diagnostic_index resolves each hash-checked private NPZ and its frozen scale; arrays are referenced, not copied. PRIMARY class_counts use observed categorical codes/labels; cadence intervals use the filed quantiles, not new thresholds",
            gate_overview="Disjoint side/gate cells summed for compact overview; no pooled authorization claim",
            qualification="Only FILED_SCORABLE_GATES individual side/gate cells may qualify; engine authorship remains disabled",
            holdout="June: new-experiment holdout—not historically unseen; STRICT_HOLDOUT kept separate from PRIMARY",
            files="Derived arrays checked and read in place; no raw/witness/array copied into report"))


def format_number(value, digits=3):
    return "—" if value is None else format(value, "."+str(digits)+"f")


def metric(row, name):
    return row["metrics"].get(name, {}).get("mean")


def metric_with_n(row, name):
    value = row["metrics"].get(name, {})
    return format_number(value.get("mean"))+" / "+str(value.get("n", 0))


def render_markdown(report):
    lines = ["# Feature-panel benchmark", "",
        "June is a **new-experiment holdout—not historically unseen**. PRIMARY and STRICT_HOLDOUT remain separate. "
        "All predictions are bench results; engine authorship is disabled.", "",
        "Every listed run, diagnostics array and empirical-scale binding was hash checked. "
        "The companion JSON retains all signed quantile errors, matched metric denominators, ESS, family metrics, "
        "coverage by month/field, PRIMARY month tables, ALL/GATES/FILED overviews, and individual filed side/gate qualification results. "
        "Its diagnostic_index locates the private per-receipt values, empirical ranks, source diagnostics and frozen scales. "
        "This Markdown is a selected overview, not the full gate table. A dash / 0 means no finite score, not a measured zero."]
    for category in report["categories"]:
        views = [("PRIMARY_ALL_RECEIPTS", None)]
        views += [("PRIMARY_ALL_RECEIPTS", month) for month in report["heldout_months"]]
        views += [("STRICT_HOLDOUT_ALL_RECEIPTS", None)]
        for stream, month in views:
            rows = [row for row in report["forecasts"] if row["category"] == category
                    and row["stream"] == stream and row["month"] == month and row["cohort"] == "all_receipts"]
            if not rows:
                continue
            lines += ["", "## "+category+" · "+stream+(" · "+month if month else ""), ""]
            for target in ("carried", "reachable"):
                lines += ["", "### "+target, "",
                    "| Variant | Called / eligible | CRPS ¢ / n | Signed Q50 ¢ / n | Timing MAE min / n | Q25–75 coverage / n | Reach Brier / n | ΔCRPS matched / n |",
                    "|---|---:|---:|---:|---:|---:|---:|---:|"]
                for row in rows:
                    if row["target"] != target:
                        continue
                    paired = row.get("matched_to_first", {}).get("metrics", {}).get("floor_crps_cents", {}).get("delta", {})
                    comparison = "—" if not paired else format_number(paired["mean"])+" / "+str(paired["n"])
                    lines.append("| "+" | ".join((row["variant"], f'{row["called_receipts"]} / {row["eligible_receipts"]}',
                        metric_with_n(row,"floor_crps_cents"), metric_with_n(row,"floor_signed_error_cents"),
                        metric_with_n(row,"floor_timing_absolute_error_minutes"),
                        metric_with_n(row,"floor_band.q25_q75.coverage"),
                        metric_with_n(row,"reach.support.brier"), comparison))+" |")
            family_rows = [row for row in rows if row["target"] == "carried"]
            lines += ["", "| Variant | Mean ESS / n | Abstained | Family accuracy / n | Strictly closer / matched floor n |",
                      "|---|---:|---:|---:|---:|"]
            for row in family_rows:
                family = row["metrics"].get("family_accuracy", {})
                match = row.get("matched_to_first", {})
                lines.append("| "+" | ".join((row["variant"], format_number(row["ess"]["mean"])+" / "+str(row["ess"]["n"]),
                    str(row["abstained_receipts"]), format_number(family.get("mean"))+" / "+str(family.get("n",0)),
                    f'{match.get("strictly_closer", "—")} / {match.get("n", "—")}'))+" |")
    lines += ["", "## R0 conduct", "", "Reachable witnesses do not establish queue fills.", "",
              "| Tour / stream | Variant | Evaluated / eligible games | Completion | One-sided | Capture ¢ / eligible evaluated game |",
              "|---|---|---:|---:|---:|---:|"]
    for group in report["r0_conduct"]:
        for variant in report["variants"]:
            row = group["variants"][variant]
            metrics = row["metrics"]
            lines.append("| "+" | ".join((group["group"]["category"]+" / "+group["group"]["stream"], variant,
                f'{row["evaluated_events"]} / {row["eligible_events"]}',
                format_number(metrics.get("completed",{}).get("mean")),
                format_number(metrics.get("one_sided",{}).get("mean")),
                format_number(metrics.get("captured_cents",{}).get("mean"))))+" |")
    qualified = [row for row in report["filed_qualifications"] if row["qualifies"]]
    for contract in report["score_contracts"]:
        lines += ["", contract["category"]+": baseline-bound filed criterion is n >= "+str(contract["minimum_matched_queries"])
                  +" and strictly closer >= "+format(contract["minimum_strictly_closer_share"], ".12g")
                  +" × n; ties remain in n and are not wins. NO-CALL ESS floor: "+format(contract["no_call_ess_floor"], ".12g")+"."]
    lines += ["", f"Filed criterion: {len(qualified)} qualifying variant/target/side/gate cells. "
              "Only FILED_SCORABLE_GATES cells are tested; pooled overview rows do not authorize changes.", "",
              "Feature coverage is in FEATURE_PANEL_COMPACT_REPORT.json. Available values, observed zero values, "
              "missing receipts, and unknown receipts are separate counts. PRIMARY supplies coverage once; June is not counted twice.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.run)
    outputs = {"FEATURE_PANEL_COMPACT_REPORT.json": canonical(report)+"\n",
               "FEATURE_PANEL_SUMMARY.md": render_markdown(report)}
    args.out.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        path = args.out/name
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise ValueError("REFUSE_DIFFERENT_EXISTING_REPORT:"+str(path))
    for name, content in outputs.items():
        (args.out/name).write_text(content, encoding="utf-8", newline="\n")
    print(canonical(dict(status=report["status"], output=str(args.out.resolve()),
                         categories=report["categories"], raw_files_copied=0)))


if __name__ == "__main__":
    main()
