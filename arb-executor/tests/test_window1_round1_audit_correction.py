from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round1_audit_correction as correction  # noqa: E402


def test_round1_correction_reproduces_controlling_audit(tmp_path):
    correction.run(ROOT, tmp_path)
    receipt = json.loads(
        (tmp_path / "ROUND1_CORRECTION_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )
    assert receipt["selected_metrics"] == {
        "D": 804, "C": 10, "PC": 9, "S": 9, "IC": 4
    }
    assert receipt["failure_decomposition"]["corrected"] == {
        "genuine_zero_fill": 582,
        "naked_single_leg_fill": 84,
        "zero_length_window1_opportunity": 12,
    }
    assert receipt["failure_decomposition"]["censored"] == {
        "start_boundary": 85,
        "missing_feature_or_birth_book": 11,
        "queue_ambiguous": 6,
    }
    assert receipt["optimistic_completion_bound"]["market_ceiling"] is False
    assert len(
        receipt["lookahead_correction"]["ineligible_candidate_ids"]
    ) == 4
    assert (
        receipt["lookahead_correction"]["selected_candidate_affected"]
        is False
    )


def test_round1_family_claims_are_no_longer_all_effective(tmp_path):
    correction.run(ROOT, tmp_path)
    receipt = json.loads(
        (tmp_path / "ROUND1_CORRECTION_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )
    os_rows = {
        row["family_id"]: row
        for row in receipt["os_family_capability_matrix"]
    }
    assert os_rows["pair_divot_core"]["available"] is False
    assert os_rows["mirror_deceleration"]["decision_changing"] is False
    assert os_rows["drift_cohort_orientation"]["actually_selected"] is True
    feature_rows = {
        row["family_id"]: row
        for row in receipt["feature_family_capability_matrix"]
    }
    for inert in (
        "drift_recognition",
        "cohort_steering",
        "orientation_prior",
        "reach",
        "own_order_fingerprints",
    ):
        assert feature_rows[inert]["decision_changing"] is False
