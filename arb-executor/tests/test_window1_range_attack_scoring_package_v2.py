from __future__ import annotations

import copy
import gzip
import json
import subprocess
import sys
from pathlib import Path

import pytest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_range_attack_guarded_fill_adapter_v2 import (  # noqa: E402
    GuardedFillError,
    adapt_unique_fill_row,
    adapt_unique_fill_rows,
)
from window1_range_attack_reference_adapter_v2 import (  # noqa: E402
    AMBIGUOUS_REASON,
    derive_window1_close_reference,
)
from window1_range_attack_scoring_package_builder_v2 import (  # noqa: E402
    CANDIDATES,
    _unique_fill_ledger,
    canonical_text_bytes,
    source_row,
)
from window1_range_attack_scoring_runner_v2 import (  # noqa: E402
    COMMAND_TEMPLATE,
    RunnerError,
    load_and_verify_authorization_report,
    verify_authorization_report_text,
)


CANDIDATE = CANDIDATES[0]
EVENT = {
    "event_id": "KXTEST-26JUL12AB",
    "event_date": "2026-07-12",
    "category": "ATP_MAIN",
    "scheduled_start_exchange_ts": 20_000.0,
    "legs": [
        {"leg": "A", "ticker": "KXTEST-26JUL12AB-A"},
        {"leg": "B", "ticker": "KXTEST-26JUL12AB-B"},
    ],
}


def boundary() -> dict:
    return {
        "schema_version": "window1-real-start-ledger-v5-guarded",
        "event_id": EVENT["event_id"],
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "guard_censor_reason": None,
        "exact_start_utc": 20_000.0,
        "guard_band": {
            "guard_id": "official-point-strict-60s-v1",
            "positive_guard_seconds": 60,
        },
    }


def unique_row(
    *,
    evidence_type: str = "PRICE_REACHED",
    target: object = 40,
    fill_price: object = 40,
    quantity: object = 5,
) -> dict:
    print_evidence = evidence_type == "PRICE_REACHED"
    evidence = (
        {
            "receipt": "print-A",
            "ts": 19_000.0,
            "price": 40,
            "size": 0.25,
        }
        if print_evidence
        else {
            "receipt": "book-A",
            "ts": 19_000.0,
            "target_price_cents": 40,
            "external_ask_price_cents": 39,
        }
    )
    return {
        "schema_version": "window1-range-attack-unique-guarded-fill-v2",
        "candidate_id": CANDIDATE,
        "event_id": EVENT["event_id"],
        "event_date": EVENT["event_date"],
        "category": EVENT["category"],
        "leg_id": "A",
        "ticker": "KXTEST-26JUL12AB-A",
        "order_interval_id": f"{CANDIDATE}|fixture|A|0001",
        "opened_ts": 18_000.0,
        "evaluated_right_ts": 19_940.0,
        "target_price_cents": target,
        "boundary": {
            "event_id": EVENT["event_id"],
            "start_source_class": "official_exact",
            "positive_window1_provable": True,
            "schedule_can_prove_positive": False,
            "guarded_cutoff_ts": 19_940.0,
            "guard_id": "official-point-strict-60s-v1",
            "guard_seconds": 60,
        },
        "FILLABLE_AT_X": True,
        "FILLABLE_AT_X_evidence_type": evidence_type,
        "FILLABLE_AT_X_evidence": evidence,
        "PRICE_REACHED": print_evidence,
        "STRICT_ASK_CERTAIN_FILL": not print_evidence,
        "primary_price_fillability_assigns_five": True,
        "accounting_quantity_if_later_scored": quantity,
        "accounting_fill_price_if_later_scored": fill_price,
        "unique_selection_receipt": {
            "selection_basis": "SINGLETON_GUARDED_RECEIPT",
            "selector_receipt_sha256": "a" * 64,
        },
        "metrics": None,
        "scored": False,
    }


def expected_legs() -> dict:
    return {
        (EVENT["event_id"], "A"): "KXTEST-26JUL12AB-A",
        (EVENT["event_id"], "B"): "KXTEST-26JUL12AB-B",
    }


def adapt(row: dict):
    return adapt_unique_fill_row(
        row,
        expected_candidates=frozenset({CANDIDATE}),
        expected_legs=expected_legs(),
    )


def test_exact_integer_control_and_fractional_print_size_pass() -> None:
    value = adapt(unique_row())
    assert value.accounting_quantity == 5
    assert value.accounting_fill_price_cents == 40


@pytest.mark.parametrize(
    ("case", "mutator"),
    [
        ("quantity_5.9", lambda row: row.update(
            accounting_quantity_if_later_scored=5.9
        )),
        ("quantity_5.0001", lambda row: row.update(
            accounting_quantity_if_later_scored=5.0001
        )),
        ("target_and_fill_40.9", lambda row: row.update(
            target_price_cents=40.9,
            accounting_fill_price_if_later_scored=40.9,
        )),
        ("fill_40.9_only", lambda row: row.update(
            accounting_fill_price_if_later_scored=40.9
        )),
        ("fractional_print_price_39.7", lambda row: row[
            "FILLABLE_AT_X_evidence"
        ].update(price=39.7)),
        ("strict_fractional_target_40.9", lambda row: row[
            "FILLABLE_AT_X_evidence"
        ].update(target_price_cents=40.9)),
        ("strict_fractional_ask_39.9", lambda row: row[
            "FILLABLE_AT_X_evidence"
        ].update(external_ask_price_cents=39.9)),
        ("boolean_quantity", lambda row: row.update(
            accounting_quantity_if_later_scored=True
        )),
    ],
)
def test_all_eight_adversarial_numeric_cases_rejected(
    case: str,
    mutator,
) -> None:
    evidence_type = (
        "STRICT_ASK_CERTAIN_FILL" if case.startswith("strict_")
        else "PRICE_REACHED"
    )
    row = unique_row(evidence_type=evidence_type)
    mutator(row)
    with pytest.raises(GuardedFillError):
        adapt(row)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("accounting_quantity_if_later_scored", float("nan")),
        ("accounting_quantity_if_later_scored", float("inf")),
        ("target_price_cents", 0),
        ("target_price_cents", 100),
        ("target_price_cents", True),
    ],
)
def test_nonfinite_out_of_range_and_bool_rejected(
    field: str,
    value: object,
) -> None:
    row = unique_row()
    row[field] = value
    with pytest.raises(GuardedFillError):
        adapt(row)


def test_runtime_unique_ledger_rejects_duplicate_leg() -> None:
    row = unique_row()
    duplicate = copy.deepcopy(row)
    duplicate["order_interval_id"] += "-duplicate"
    duplicate["FILLABLE_AT_X_evidence"]["receipt"] = "print-other"
    with pytest.raises(GuardedFillError, match="multiple unique-ledger"):
        adapt_unique_fill_rows(
            [row, duplicate],
            expected_candidates=frozenset({CANDIDATE}),
            expected_legs=expected_legs(),
        )


def test_real_unique_ledger_census_and_known_resolutions() -> None:
    repo = Path(__file__).resolve().parents[2]
    rows, receipt = _unique_fill_ledger(repo)
    assert len(rows) == 991
    assert receipt["candidate_counts"] == {
        CANDIDATES[0]: 501,
        CANDIDATES[1]: 490,
    }
    assert receipt["evidence_type_counts"] == {
        "PRICE_REACHED": 965,
        "STRICT_ASK_CERTAIN_FILL": 26,
    }
    observed = {
        (row["candidate_id"], row["event_id"], row["leg_id"]):
        (row["order_interval_id"].rsplit("|", 1)[-1],
         row["target_price_cents"])
        for row in rows
    }
    assert observed[(
        CANDIDATES[0], "KXWTACHALLENGERMATCH-26JUL20LANRAD", "RAD"
    )] == ("0005", 80)
    assert observed[(
        CANDIDATES[1], "KXWTACHALLENGERMATCH-26JUL20LANRAD", "RAD"
    )] == ("0005", 80)
    assert observed[(
        CANDIDATES[1], "KXATPCHALLENGERMATCH-26JUL19BOHBOU", "BOH"
    )] == ("0007", 3)


def reference_print(receipt: str, price: int) -> dict:
    return {
        "ticker": "KXTEST-26JUL12AB-A",
        "trade_id": receipt,
        "ts": 19_900.0,
        "price": price,
        "size": 0.25,
    }


def test_same_latest_timestamp_same_price_retains_all_receipts() -> None:
    value = derive_window1_close_reference(
        event=EVENT,
        leg=EVENT["legs"][0],
        boundary=boundary(),
        true_prints=[
            reference_print("uuid-z", 55),
            reference_print("uuid-a", 55),
        ],
    )
    assert value.available is True
    assert value.window1_close_cents == 55
    assert value.reference_receipt is None
    assert value.reference_supporting_receipts == ("uuid-a", "uuid-z")


def test_differing_price_latest_tie_is_unavailable_without_sequence() -> None:
    value = derive_window1_close_reference(
        event=EVENT,
        leg=EVENT["legs"][0],
        boundary=boundary(),
        true_prints=[
            reference_print("uuid-z", 55),
            reference_print("uuid-a", 54),
        ],
    )
    assert value.available is False
    assert value.reason == AMBIGUOUS_REASON
    assert value.window1_close_cents is None
    assert value.reference_supporting_receipts == ("uuid-a", "uuid-z")


def test_report_text_has_finite_non_self_referential_bindings() -> None:
    report = "\n".join([
        "PASS",
        "1" * 40,
        "execution-1",
        "2" * 64,
        COMMAND_TEMPLATE,
    ])
    verify_authorization_report_text(
        report,
        package_commit="1" * 40,
        execution_id="execution-1",
        bundle_sha256="2" * 64,
        command_template=COMMAND_TEMPLATE,
    )
    for replacement in (
        {"package_commit": "3" * 40},
        {"execution_id": "wrong"},
        {"bundle_sha256": "4" * 64},
    ):
        values = {
            "package_commit": "1" * 40,
            "execution_id": "execution-1",
            "bundle_sha256": "2" * 64,
            "command_template": COMMAND_TEMPLATE,
            **replacement,
        }
        with pytest.raises(RunnerError):
            verify_authorization_report_text(report, **values)


def _git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args], cwd=repo, check=True,
        capture_output=True, text=True,
    )
    return process.stdout.strip()


def test_commit_report_then_authorize_workflow_is_satisfiable(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "fixture@example.test")
    _git(repo, "config", "user.name", "Fixture")
    (repo / "package.txt").write_text("frozen\n", encoding="utf-8")
    _git(repo, "add", "package.txt")
    _git(repo, "commit", "-m", "package")
    package_commit = _git(repo, "rev-parse", "HEAD")
    execution_id = "fixture-execution"
    bundle = "b" * 64
    report_path = "audit/AUDIT_REPORT.md"
    (repo / "audit").mkdir()
    (repo / report_path).write_text(
        "\n".join([
            "PASS", package_commit, execution_id, bundle,
            COMMAND_TEMPLATE, "",
        ]),
        encoding="utf-8",
    )
    _git(repo, "add", report_path)
    _git(repo, "commit", "-m", "independent authorization")
    audit_commit = _git(repo, "rev-parse", "HEAD")
    _git(
        repo, "update-ref",
        "refs/remotes/origin/audit/window1-independent", audit_commit,
    )
    report = load_and_verify_authorization_report(
        repo,
        audit_commit=audit_commit,
        audit_report_path=report_path,
        audit_ref="refs/remotes/origin/audit/window1-independent",
        package_commit=package_commit,
        execution_id=execution_id,
        bundle_sha256=bundle,
        command_template=COMMAND_TEMPLATE,
    )
    assert "PASS" in report
    with pytest.raises(RunnerError):
        load_and_verify_authorization_report(
            repo,
            audit_commit="0" * 40,
            audit_report_path=report_path,
            audit_ref="refs/remotes/origin/audit/window1-independent",
            package_commit=package_commit,
            execution_id=execution_id,
            bundle_sha256=bundle,
            command_template=COMMAND_TEMPLATE,
        )
    with pytest.raises(RunnerError):
        load_and_verify_authorization_report(
            repo,
            audit_commit=audit_commit,
            audit_report_path="audit/MISSING.md",
            audit_ref="refs/remotes/origin/audit/window1-independent",
            package_commit=package_commit,
            execution_id=execution_id,
            bundle_sha256=bundle,
            command_template=COMMAND_TEMPLATE,
        )


def test_lf_crlf_source_identities_are_equal(tmp_path: Path) -> None:
    repo = tmp_path
    path = repo / "fixture.py"
    path.write_bytes(b"a=1\nb=2\n")
    left = source_row(repo, "fixture.py", newline_probe="lf")
    right = source_row(repo, "fixture.py", newline_probe="crlf")
    assert left == right
    assert canonical_text_bytes(b"a\r\nb\r\n") == b"a\nb\n"
