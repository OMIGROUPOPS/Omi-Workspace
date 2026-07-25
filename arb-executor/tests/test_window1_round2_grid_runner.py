from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_grid_runner as grid  # noqa: E402


def candidate_receipts() -> dict[str, dict[str, str]]:
    stream_sha = grid.canonical_sha256([])
    return {
        candidate_id: {
            f"E{index:03d}": stream_sha
            for index in range(804)
        }
        for candidate_id in grid.FROZEN_CANDIDATES
    }


def identities() -> list[dict]:
    return [
        {
            "event_id": f"E{index:03d}",
            "event_date": grid.DEV_DATES[index % len(grid.DEV_DATES)],
            "leg_id": leg,
            "ticker": f"E{index:03d}-{leg}",
        }
        for index in range(804)
        for leg in ("A", "B")
    ]


def events() -> list[dict]:
    return [
        {
            "event_id": f"E{index:03d}",
            "event_date": grid.DEV_DATES[index % len(grid.DEV_DATES)],
            "category": "ATP_MAIN",
            "legs": [
                {"leg": "A", "ticker": f"E{index:03d}-A"},
                {"leg": "B", "ticker": f"E{index:03d}-B"},
            ],
        }
        for index in range(804)
    ]


def package_fixture() -> tuple[dict, dict]:
    receipts = candidate_receipts()
    legs = identities()
    stream_rows = []
    stream_inputs = []
    container_oid = "1" * 40
    container_sha = "2" * 64
    for event_id in receipts[grid.FROZEN_CANDIDATES[0]]:
        for candidate_id in grid.FROZEN_CANDIDATES:
            ordinal = len(stream_rows) + 1
            stream = {
                "candidate_id": candidate_id,
                "event_id": event_id,
                "evaluation_truth_present": False,
                "leg_streams": {"A": [], "B": []},
                "order_stream": [],
                "scored": False,
                "metrics": None,
                "holdout_queried": False,
                "stream_sha256": receipts[candidate_id][event_id],
            }
            row = {
                "candidate_id": candidate_id,
                "event_id": event_id,
                "stream": stream,
            }
            line = (grid.compact(row) + "\n").encode()
            stream_rows.append(row)
            stream_inputs.append({
                "ordinal": ordinal,
                "candidate_id": candidate_id,
                "event_id": event_id,
                "path": f"{grid.STREAM_BUNDLE_PATH}#L{ordinal}",
                "role": "frozen_candidate_event_order_stream",
                "bytes": len(line),
                "git_blob_oid": container_oid,
                "sha256": grid.sha256_bytes(line),
                "container_sha256": container_sha,
                "stream_sha256": receipts[candidate_id][event_id],
            })
    contract = {
        "candidate_ids": list(grid.FROZEN_CANDIDATES),
        "candidate_stream_receipts": receipts,
        "frozen_event_leg_identities": legs,
    }
    package = {
        "schema_version": grid.PACKAGE_SCHEMA,
        "execution_id": grid.EXECUTION_ID,
        "authorized_parent": grid.AUTHORIZED_PARENT,
        "authorization_audit": grid.AUTHORIZED_AUDIT,
        "exact_execution_command": grid.EXACT_EXECUTION_COMMAND,
        "exact_validation_command": grid.EXACT_VALIDATION_COMMAND,
        "result_directory": grid.RESULT_DIRECTORY,
        "D": 804,
        "target_PC": 603,
        "development_dates": grid.DEV_DATES,
        "sealed_holdout_dates": grid.HOLDOUT_DATES,
        "candidate_ids": list(grid.FROZEN_CANDIDATES),
        "git_inputs": [
            {
                "path": path,
                "role": (
                    "frozen_candidate_event_stream_bundle"
                    if path == grid.STREAM_BUNDLE_PATH
                    else "fixture"
                ),
                "bytes": 1,
                "git_blob_oid": container_oid,
                "sha256": container_sha,
            }
            for path in grid.FROZEN_GIT_INPUT_PATHS
        ],
        "external_inputs": [
            {
                "path": path,
                "availability": "available",
                "holdout_dates_present": 0,
                "bytes": 1,
                "sha256": "0" * 64,
            }
            for path in grid.FROZEN_EXTERNAL_INPUT_PATHS
        ],
        "market_cache_files": [
            {
                "path": f"cache/E{index:03d}.json.gz",
                "event_id": f"E{index:03d}",
                "event_date": grid.DEV_DATES[
                    index % len(grid.DEV_DATES)
                ],
                "availability": "available",
                "holdout_dates_present": 0,
                "bytes": 1,
                "sha256": "0" * 64,
            }
            for index in range(804)
        ],
        "roles": {
            "scorer_contract": "contract.json",
            "event_ledger": "events.jsonl",
            "candidate_event_streams": grid.STREAM_BUNDLE_PATH,
        },
        "candidate_event_stream_inputs": stream_inputs,
        "candidate_event_stream_receipts": copy.deepcopy(receipts),
        "candidate_event_stream_receipts_sha256": (
            grid.canonical_sha256(receipts)
        ),
        "frozen_event_leg_identities": copy.deepcopy(legs),
        "frozen_event_leg_identities_sha256": (
            grid.canonical_sha256(legs)
        ),
    }
    package["_fixture_stream_rows"] = stream_rows
    package["input_bundle_sha256"] = grid.canonical_sha256(package)
    return package, contract


def install_validation_mocks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    package: dict,
    contract: dict,
) -> Path:
    package_path = tmp_path / "package.json"
    stream_rows = package.pop("_fixture_stream_rows")
    material = dict(package)
    material.pop("input_bundle_sha256", None)
    package["input_bundle_sha256"] = grid.canonical_sha256(material)

    def fake_read_json(path: Path) -> dict:
        return package if path == package_path else contract

    def fake_git(repo: Path, *args: str) -> bytes:
        command = tuple(args)
        if command == ("branch", "--show-current"):
            return b"codex/window1-definition\n"
        if command == ("rev-parse", "HEAD"):
            return (grid.AUTHORIZED_PARENT + "\n").encode()
        if command == ("diff", "--name-only"):
            return b""
        raise AssertionError(command)

    monkeypatch.setattr(grid, "read_json", fake_read_json)
    monkeypatch.setattr(
        grid,
        "read_jsonl",
        lambda path: (
            stream_rows
            if str(path).endswith(
                "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
            )
            else events()
        ),
    )
    monkeypatch.setattr(grid, "git", fake_git)
    monkeypatch.setattr(
        grid, "_verify_git_input", lambda repo, row, git_ref: None
    )
    monkeypatch.setattr(
        grid, "_verify_external_input", lambda repo, row: None
    )
    return package_path


def test_execution_identity_and_commands_are_fully_fixed():
    assert grid.EXECUTION_ID
    assert grid.EXACT_EXECUTION_COMMAND == (
        "python -B arb-executor/analysis/"
        "window1_round2_grid_runner.py --repo . --package "
        ".claude/window1_round2_execution_package_20260724/"
        "SCORING_INPUT_BUNDLE.json --mode execute"
    )
    assert "*" not in grid.EXACT_EXECUTION_COMMAND
    assert "$" not in grid.EXACT_EXECUTION_COMMAND
    assert grid.FROZEN_CANDIDATES == [
        pair_member
        for pair in grid.FROZEN_PAIRS
        for pair_member in pair
    ]


@pytest.mark.parametrize(
    "candidate_ids,match",
    [
        (grid.FROZEN_CANDIDATES[:-1], "missing or additional"),
        (grid.FROZEN_CANDIDATES + ["extra"], "missing or additional"),
        (
            grid.FROZEN_CANDIDATES[:-1]
            + [grid.FROZEN_CANDIDATES[0]],
            "duplicated",
        ),
        (list(reversed(grid.FROZEN_CANDIDATES)), "reordered"),
    ],
)
def test_missing_additional_duplicated_or_reordered_grid_refused(
    candidate_ids, match,
):
    with pytest.raises(grid.GridExecutionError, match=match):
        grid.assert_exact_candidate_order(candidate_ids)


@pytest.mark.parametrize(
    "paths,match",
    [
        (grid.FROZEN_GIT_INPUT_PATHS[:-1], "missing or additional"),
        (grid.FROZEN_GIT_INPUT_PATHS + ["extra"], "missing or additional"),
        (
            grid.FROZEN_GIT_INPUT_PATHS[:-1]
            + [grid.FROZEN_GIT_INPUT_PATHS[0]],
            "duplicated",
        ),
        (list(reversed(grid.FROZEN_GIT_INPUT_PATHS)), "reordered"),
    ],
)
def test_missing_additional_duplicated_or_reordered_inputs_refused(
    paths, match,
):
    with pytest.raises(grid.GridExecutionError, match=match):
        grid.assert_exact_input_paths(
            paths, grid.FROZEN_GIT_INPUT_PATHS, "Git"
        )


def test_denominator_holdout_and_non_development_dates_refused():
    rows = events()
    grid.validate_dates(rows)
    with pytest.raises(grid.GridExecutionError, match="D=804"):
        grid.validate_dates(rows[:-1])
    holdout = copy.deepcopy(rows)
    holdout[0]["event_date"] = "2026-07-24"
    with pytest.raises(grid.GridExecutionError, match="holdout"):
        grid.validate_dates(holdout)
    outside = copy.deepcopy(rows)
    outside[0]["event_date"] = "2026-07-23"
    with pytest.raises(grid.GridExecutionError, match="non-development"):
        grid.validate_dates(outside)


def test_existing_execution_id_refuses_overwrite_or_resume(tmp_path):
    package = {"result_directory": grid.RESULT_DIRECTORY}
    result = tmp_path / grid.RESULT_DIRECTORY
    result.mkdir(parents=True)
    with pytest.raises(
        grid.GridExecutionError, match="overwrite/resume"
    ):
        grid.validate_result_directory_absent(tmp_path, package)


def test_changed_or_missing_git_input_receipt_hard_fails(
    monkeypatch, tmp_path,
):
    row = {
        "path": "bound.json",
        "bytes": 4,
        "git_blob_oid": "a" * 40,
        "sha256": grid.sha256_bytes(b"data"),
    }

    def changed_git(repo, *args):
        if args[0] == "rev-parse":
            return ("a" * 40 + "\n").encode()
        if args[0] == "cat-file":
            return b"changed"
        raise AssertionError(args)

    monkeypatch.setattr(grid, "git", changed_git)
    with pytest.raises(grid.GridExecutionError, match="receipt mismatch"):
        grid._verify_git_input(tmp_path, row, git_ref="INDEX")

    def missing_git(repo, *args):
        raise grid.GridExecutionError("git input missing")

    monkeypatch.setattr(grid, "git", missing_git)
    with pytest.raises(grid.GridExecutionError, match="missing"):
        grid._verify_git_input(tmp_path, row, git_ref="INDEX")


def test_changed_or_missing_external_input_receipt_hard_fails(tmp_path):
    path = tmp_path / "external.bin"
    row = {
        "path": "external.bin",
        "bytes": 4,
        "sha256": grid.sha256_bytes(b"data"),
    }
    with pytest.raises(grid.GridExecutionError, match="missing"):
        grid._verify_external_input(tmp_path, row)
    path.write_bytes(b"changed")
    with pytest.raises(grid.GridExecutionError, match="receipt mismatch"):
        grid._verify_external_input(tmp_path, row)


def test_changed_input_bundle_hash_hard_fails(monkeypatch, tmp_path):
    package, contract = package_fixture()
    package_path = install_validation_mocks(
        monkeypatch, tmp_path, package, contract
    )
    package["target_PC"] = 602
    with pytest.raises(grid.GridExecutionError, match="bundle hash"):
        grid.validate_package(
            tmp_path, package_path, mode="validate-only"
        )


def test_holdout_market_cache_receipt_hard_fails(monkeypatch, tmp_path):
    package, contract = package_fixture()
    package["market_cache_files"][0]["event_date"] = "2026-07-24"
    package_path = install_validation_mocks(
        monkeypatch, tmp_path, package, contract
    )
    with pytest.raises(grid.GridExecutionError, match="market cache"):
        grid.validate_package(
            tmp_path, package_path, mode="validate-only"
        )


def test_changed_stream_receipt_hard_fails(monkeypatch, tmp_path):
    package, contract = package_fixture()
    package_path = install_validation_mocks(
        monkeypatch, tmp_path, package, contract
    )
    candidate_id = grid.FROZEN_CANDIDATES[0]
    contract["candidate_stream_receipts"][candidate_id]["E000"] = "f" * 64
    with pytest.raises(grid.GridExecutionError, match="6,432"):
        grid.validate_package(
            tmp_path, package_path, mode="validate-only"
        )


def test_changed_leg_identity_hard_fails(monkeypatch, tmp_path):
    package, contract = package_fixture()
    package_path = install_validation_mocks(
        monkeypatch, tmp_path, package, contract
    )
    contract["frozen_event_leg_identities"][0]["ticker"] = "CHANGED"
    with pytest.raises(grid.GridExecutionError, match="1,608"):
        grid.validate_package(
            tmp_path, package_path, mode="validate-only"
        )


def test_validation_only_dispatches_zero_candidates_or_scorers(
    monkeypatch, tmp_path,
):
    package, contract = package_fixture()
    package_path = install_validation_mocks(
        monkeypatch, tmp_path, package, contract
    )
    monkeypatch.setattr(
        grid.capability,
        "normalize_event",
        lambda *args, **kwargs: pytest.fail("normalizer invoked"),
    )
    monkeypatch.setattr(
        grid.scorer,
        "score_population",
        lambda *args, **kwargs: pytest.fail("scorer invoked"),
    )
    first = grid.validation_only(tmp_path, package_path)
    second = grid.validation_only(tmp_path, package_path)
    assert first == second
    assert first["candidate_dispatch_order"] == grid.FROZEN_CANDIDATES
    assert first["candidate_instrument_invocations"] == 0
    assert first["scorer_invocations"] == 0
    assert first["candidate_event_streams_loaded"] == 6432
    assert first["performance_results_produced"] is False


def test_changed_or_reordered_materialized_stream_refused(
    monkeypatch, tmp_path,
):
    package, contract = package_fixture()
    rows = package["_fixture_stream_rows"]
    rows[0], rows[1] = rows[1], rows[0]
    package_path = install_validation_mocks(
        monkeypatch, tmp_path, package, contract
    )
    with pytest.raises(grid.GridExecutionError, match="reordered"):
        grid.validate_package(
            tmp_path, package_path, mode="validate-only"
        )


def test_dispatcher_invokes_each_frozen_candidate_once_in_order():
    calls = []

    def fake_score(bundle, contract):
        calls.append(bundle["candidate_id"])
        return {"candidate_id": bundle["candidate_id"]}

    dispatcher = grid.FrozenScorerDispatcher(fake_score)
    for candidate_id in grid.FROZEN_CANDIDATES:
        result = dispatcher.invoke(
            candidate_id, {"candidate_id": candidate_id}, {}
        )
        assert result["candidate_id"] == candidate_id
    dispatcher.assert_complete()
    assert calls == grid.FROZEN_CANDIDATES
    assert dispatcher.counts == {
        candidate_id: 1 for candidate_id in grid.FROZEN_CANDIDATES
    }
    with pytest.raises(
        grid.GridExecutionError, match="additional scorer"
    ):
        dispatcher.invoke(
            grid.FROZEN_CANDIDATES[0],
            {"candidate_id": grid.FROZEN_CANDIDATES[0]},
            {},
        )


def test_dispatcher_refuses_reordered_or_incomplete_invocations():
    dispatcher = grid.FrozenScorerDispatcher(
        lambda bundle, contract: {}
    )
    with pytest.raises(grid.GridExecutionError, match="reordered"):
        dispatcher.invoke(
            grid.FROZEN_CANDIDATES[1],
            {"candidate_id": grid.FROZEN_CANDIDATES[1]},
            {},
        )
    dispatcher.invoke(
        grid.FROZEN_CANDIDATES[0],
        {"candidate_id": grid.FROZEN_CANDIDATES[0]},
        {},
    )
    with pytest.raises(grid.GridExecutionError, match="missing"):
        dispatcher.assert_complete()


def result_fixture() -> tuple[dict, dict]:
    event_rows = [
        {
            "event_id": f"E{index:03d}",
            "event_date": grid.DEV_DATES[index % len(grid.DEV_DATES)],
            "classification": "genuine_nonfill",
            "C": False,
            "PC": False,
            "S": False,
            "IC": False,
            "combined_entry_cost_cents": None,
            "combined_window1_close_delta_cents": None,
            "individual_leg_window1_close_delta_cents": None,
        }
        for index in range(804)
    ]
    raw = {
        "D": 804, "C": 0, "PC": 0, "S": 0, "IC": 0,
        **{key: 0 for key in grid.PRIMARY_CENSUS},
        "genuine_zero_fill": 804,
        "cohort_NO_CALL": 0,
        "reaim_NO_CALL": 0,
        "feature_unavailable": 0,
    }
    raw["genuine_nonfill"] = 804
    result = {
        "candidate_id": grid.FROZEN_CANDIDATES[0],
        "event_results": event_rows,
        "raw_integer_metrics_before_percentages": raw,
        "rates_after_raw_integers": {
            "C_over_D": 0, "PC_over_D": 0, "PC_over_C": None,
            "S_over_C": None, "IC_over_D": 0, "IC_over_C": None,
        },
        "result_sha256": "a" * 64,
    }
    meta = {
        f"E{index:03d}": {
            "category": "ATP_MAIN",
            "start_source_class": "official_exact",
            "policy_boundary_class": "positive",
        }
        for index in range(804)
    }
    return result, meta


def test_deterministic_candidate_output_schema_and_conservation():
    result, meta = result_fixture()
    first = grid._candidate_summary(result, meta)
    second = grid._candidate_summary(copy.deepcopy(result), meta)
    assert json.dumps(first, sort_keys=True) == json.dumps(
        second, sort_keys=True
    )
    raw = first["raw_integers_before_percentages"]
    assert raw["D"] == 804
    assert raw["target_PC"] == 603
    assert raw["distance_from_603"] == 603
    assert sum(raw[key] for key in grid.PRIMARY_CENSUS) == 804
    assert set(first["breakdowns"]) == {
        "utc_date",
        "tournament_class",
        "start_source_class",
        "policy_boundary_class",
    }


def test_no_frozen_selection_rule_means_unranked_output():
    source = (
        ROOT
        / "arb-executor"
        / "analysis"
        / "window1_round2_grid_runner.py"
    ).read_text(encoding="utf-8")
    assert "UNRANKED_FROZEN_SELECTION_RULE_ABSENT" in source
    assert "selected_candidate_receipt_emitted" in source
    assert "\"ranking_or_selection_applied\": False" in source


def test_runner_has_no_network_or_live_exchange_interface():
    source = (
        ROOT
        / "arb-executor"
        / "analysis"
        / "window1_round2_grid_runner.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "requests.",
        "httpx.",
        "api.kalshi",
        "process_settlement",
        "place_order",
        "cancel_order",
    ):
        assert forbidden not in source
