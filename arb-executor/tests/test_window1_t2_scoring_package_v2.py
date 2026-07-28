from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_t2_scoring_correction_v2 import (
    CorrectionError,
    headroom_values,
    normalize_authority,
    normalize_d2_sign,
    partition_loss_attribution,
)
from window1_t2_scoring_runner_v2 import (
    CANDIDATE_IDS,
    validation_only,
)


PACKAGE = (
    ROOT
    / ".claude"
    / "window1_t2_scoring_package_v2_prerun_20260728"
)


def read(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


def test_headroom_integer_expressions_agree() -> None:
    receipt = headroom_values(2, 0)
    assert receipt["canonical_b2_max_cents"] == -3
    assert receipt["inherited_floor_expression_b2_max_cents"] == -3
    assert receipt["formulas_equal"] is True
    assert receipt["frozen_fee_raw_json_type"] == "integer"


def test_headroom_fractional_difference_is_explicit() -> None:
    receipt = headroom_values(0.5, 0)
    assert receipt["canonical_b2_max_cents"] == -1
    assert receipt["inherited_floor_expression_b2_max_cents"] == -2
    assert receipt["formulas_equal"] is False


@pytest.mark.parametrize(
    "value",
    [True, False, float("nan"), float("inf"), float("-inf"), "0"],
)
def test_headroom_rejects_nonexact_or_nonfinite_values(value: object) -> None:
    with pytest.raises(CorrectionError):
        headroom_values(value, 0)


def test_authority_families_distinguish_macro_and_divot() -> None:
    assert normalize_authority("NATIVE_MACRO_TARGET") == "NATIVE_MACRO"
    assert (
        normalize_authority("CAUSAL_DIVOT_LATER_RECURRENCE")
        == "CAUSAL_DIVOT"
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [(-1, "NEGATIVE"), (0, "ZERO"), (1, "POSITIVE"), (None, "UNKNOWN")],
)
def test_d2_sign_is_explicit(value: object, expected: str) -> None:
    assert normalize_d2_sign(value) == expected


def test_authority_d2_partition_conserves_target_entries() -> None:
    rows = [
        {
            "primary_loss_stage": "RECOGNIZED_NOT_TARGETED",
            "omitted_lawful_target_provenance": [
                {
                    "raw_target_authority": "NATIVE_MACRO_TARGET",
                    "normalized_authority_family": "NATIVE_MACRO",
                    "omitted_lawful_d2_sign": "NEGATIVE",
                    "target_count": 2,
                },
                {
                    "raw_target_authority":
                        "CAUSAL_DIVOT_LATER_RECURRENCE",
                    "normalized_authority_family": "CAUSAL_DIVOT",
                    "omitted_lawful_d2_sign": "POSITIVE",
                    "target_count": 3,
                },
            ],
        }
    ]
    result = partition_loss_attribution(rows)
    assert result["target_level_source_count"] == 5
    assert result["partition_target_count"] == 5
    assert result["conservation_pass"] is True
    assert result["d2_inferred_from_successful_fill"] is False


def test_partition_rejects_unknown_d2_sign() -> None:
    with pytest.raises(CorrectionError):
        partition_loss_attribution([{
            "primary_loss_stage": "EXPOSED_NOT_CREDITED",
            "omitted_lawful_target_provenance": [{
                "raw_target_authority": "A",
                "normalized_authority_family": "B",
                "omitted_lawful_d2_sign": "FILLED_INFERENCE",
                "target_count": 1,
            }],
        }])


def test_frozen_headroom_receipt_has_no_difference() -> None:
    receipt = read("COMBINED_HEADROOM_ARITHMETIC_RECEIPT.json")
    assert receipt["canonical_expression"] == (
        "ceil(-d1 - frozen_fee) - 1"
    )
    assert receipt["inherited_expression"] == (
        "floor(-d1 - frozen_fee - 1)"
    )
    assert receipt["formula_difference_count"] == 0
    assert receipt["target_change_count"] == 0
    assert receipt["frozen_fee_exact_value_counts"] == {"0": 2_220_400}


def test_target_surface_and_decision_conservation() -> None:
    receipt = read("TARGET_SURFACE_CENSUS_RECONCILIATION.json")
    assert receipt["target_surface_rows"] == 4_576_794
    assert receipt["child_target_entries"] == 9_659_158
    assert receipt["lawful_target_entries"] == 2_996_560
    assert receipt["unlawful_target_entries"] == 6_662_598
    assert receipt["child_conservation_pass"] is True
    assert receipt["terminal_decision_rows"] == 4_576_794
    assert sum(receipt["terminal_decision_counts"].values()) == 4_576_794
    assert receipt["one_terminal_decision_per_surface"] is True
    assert receipt["unexplained_residue_count"] == 0


def test_parent_preservation_grains_are_not_subtracted() -> None:
    receipt = read("TARGET_SURFACE_CENSUS_RECONCILIATION.json")
    parent = receipt["non_displacing_parent_exposure"]
    assert parent["terminal_HOLD_surface_decisions"] == 1_162_210
    assert parent["secondary_rejected_replacement_receipts"] == 10_763
    assert parent["V1_reported_typed_receipt_sum"] == 1_172_973
    assert parent["sum_is_not_a_unique_surface_count"] is True
    assert receipt["reported_count_relationship"]["same_denominator"] is False
    assert (
        receipt["reported_count_relationship"][
            "arithmetic_difference_claimed"
        ]
        is False
    )


def test_blind_audit_protocol_freezes_before_comparison() -> None:
    protocol = read("FUTURE_BLIND_AUDIT_PROTOCOL.json")
    assert [
        row["expected_summaries_may_be_opened"]
        for row in protocol["phase_order"]
    ] == [False, False, True]
    assert protocol["mismatch_default"] == "BLOCK"
    assert protocol["post_hoc_reconciliation_to_expected_value"] == (
        "FORBIDDEN"
    )


def test_v1_package_is_preserved_byte_for_byte() -> None:
    receipt = read("V1_BYTE_IDENTITY_RECEIPT.json")
    assert receipt["V1_preserved_byte_for_byte"] is True
    assert receipt["modified_or_deleted_V1_files"] == 0
    for row in receipt["files"]:
        path = ROOT / row["path"]
        assert path.stat().st_size == row["bytes"]
        import hashlib
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]


def test_score_free_manifest_and_schema_are_null() -> None:
    package = read("SCORING_INPUT_MANIFEST.json")
    schema = read("EXPECTED_OUTPUT_SCHEMA_V2.json")
    for value in (package, schema):
        assert value["C"] is None
        assert value["PC"] is None
        assert value["IC"] is None
        assert value["S"] is None
        assert value["frontier"] is None
        assert value["regret"] is None
        assert value["performance"] is None
        assert value["scored"] is False
    assert all(
        value is None
        for value in package[
            "authority_omitted_d2_loss_attribution"
        ].values()
    )


def test_eight_candidates_and_population_are_unchanged() -> None:
    package = read("SCORING_INPUT_MANIFEST.json")
    assert tuple(package["candidate_ids"]) == CANDIDATE_IDS
    assert package["D"] == 804
    assert package["fit_D"] == 525
    assert package["post_fit_D"] == 279


def test_validation_only_never_invokes_real_population() -> None:
    result = validation_only(
        ROOT, PACKAGE / "SCORING_INPUT_MANIFEST.json"
    )
    assert result["gate_pass"] is True
    assert result["real_population_loaded"] is False
    assert result["fill_adapter_invoked"] is False
    assert result["reference_adapter_invoked"] is False
    assert result["scorer_invoked"] is False


def test_holdout_and_live_surfaces_are_forbidden() -> None:
    receipt = read("FORBIDDEN_ACCESS_RECEIPT.json")
    assert receipt["holdout_dates_2026_07_24_through_26_opened"] is False
    assert receipt["live_or_production_access"] is False
    assert receipt["network_access"] is False
    assert receipt["scorer_invoked"] is False
    assert receipt["authorization_issued"] is False
