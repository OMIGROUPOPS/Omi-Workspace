#!/usr/bin/env python3
"""Focused Stage-C shadow-safety and frozen-policy parity tests."""

import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EXECUTOR = REPO / "arb-executor"
sys.path.insert(0, str(EXECUTOR))

from v36_shadow_brain import POLICY_COMMIT, V36ShadowBrain, v36_decide  # noqa: E402


POLICY_FILES = {
    "window1_v29r3_standing_floor_release_policy.js": "12c223e7e62bd22888aee6cec31d7a44ed4dcc644bd1e432e9604f6ba0864663",
    "window1_v32_no_chase_state_machine.js": "414b1079a03ad1938a2b2dcc80f230e72a928662176582a68af788c997d0631a",
    "window1_v34_dual_side_residency_machine.js": "e26802f5bcfeab74b77d2b3201386fb527e1d543967c71d05679c2b1d44bc81a",
    "window1_v35_living_rest_evidence_gate.js": "14d237ccfcda4c716a43c6c455ad0f4a8c8994835f770bd3ff18ce4d7d79a54f",
    "window1_v36_state_directional_rest_mature_floor.js": "5db3922d5749e11548bca0c301abec19da5e2dfb993ffc17a44ec90989e34f73",
}


def test_frozen_policy_files_are_byte_identical():
    for name, expected_sha256 in POLICY_FILES.items():
        rel = f"arb-executor/analysis/{name}"
        local = (REPO / rel).read_bytes()
        assert hashlib.sha256(local).hexdigest() == expected_sha256


def _decision_cases():
    cases = []
    for state, bid, active, cap, floor, flicker, mature in itertools.product(
        ("FALLING", "RISING", "SETTLED"),
        (1, 40, 55, 98),
        (None, 1, 39, 60),
        (None, 35, 70),
        (None, 38, 55),
        (False, True),
        (False, True),
    ):
        ask = min(99, bid + 1)
        book = {
            "bid": bid,
            "ask": ask,
            "spread": ask - bid,
            "ask_dwell_seconds": 10,
            "top_ask_size": 5,
        }
        cases.append({
            "state": state, "book": book, "activeTarget": active,
            "pairCap": cap, "activeEvidenceFloor": floor,
            "floorFirstFlickerLive": flicker, "floorMature": mature,
        })
    return cases


def test_python_decision_seam_matches_frozen_javascript_exhaustively():
    cases = _decision_cases()
    script = r'''const fs=require("fs");
const p=require("./arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js");
const rows=JSON.parse(fs.readFileSync(0,"utf8"));
process.stdout.write(JSON.stringify(rows.map((x)=>p.decide(x))));'''
    expected = json.loads(subprocess.check_output(
        ["node", "-e", script], cwd=REPO,
        input=json.dumps(cases).encode("utf-8"),
    ))
    actual = [v36_decide(
        row["state"], row["book"], row["activeTarget"], row["pairCap"],
        row["activeEvidenceFloor"], row["floorFirstFlickerLive"],
        row["floorMature"],
    ) for row in cases]
    assert actual == expected


def test_shadow_brain_is_receipt_driven_and_has_no_order_surface():
    rows = []
    brain = V36ShadowBrain(lambda event, details, ticker: rows.append(
        {"event": event, "details": details, "ticker": ticker}))
    assert not hasattr(brain, "place_order")
    assert not hasattr(brain, "cancel_order")
    first = brain.on_book("EV-A", "EV", 1000.0, [(50, 100)], [(51, 100)], "b:1")
    assert first["action"] == "PLACE_REST"
    assert first["target_cents"] == 49
    # A rising book may re-anchor the hypothetical rest upward.
    rising = brain.on_book("EV-A", "EV", 1001.0, [(52, 100)], [(53, 100)], "b:2")
    assert rising["state"] == "RISING"
    assert rising["action"] == "REPRICE_REST"
    assert rising["target_cents"] == 51
    # A later fall walks down; it never chases up while FALLING.
    falling = brain.on_book("EV-A", "EV", 1002.0, [(48, 100)], [(49, 100)], "b:3")
    assert falling["state"] == "FALLING"
    assert falling["target_cents"] == 47
    # Same-receipt or undersized prints cannot credit a maker fill.
    brain.on_trade("EV-A", "EV", 1002.0, 47, 5, "no", "t:same")
    assert not [r for r in rows if r["event"] == "v36_shadow_fill"]
    brain.on_trade("EV-A", "EV", 1003.0, 47, 4, "no", "t:small")
    assert not [r for r in rows if r["event"] == "v36_shadow_fill"]
    brain.on_trade("EV-A", "EV", 1004.0, 47, 5, "no", "t:fill")
    fills = [r for r in rows if r["event"] == "v36_shadow_fill"]
    assert len(fills) == 1
    assert fills[0]["details"]["fill_class"].startswith("PROVEN_MAKER")


def test_live_v4_shadow_hook_cannot_control_exchange_paths():
    source = (EXECUTOR / "live_v4.py").read_text(encoding="utf-8")
    assert "self._v36_shadow = V36ShadowBrain(self._log)" in source
    assert "await self._v36_shadow" not in source
    assert "v36_shadow_decision" not in source.replace(
        "every decision is a v36_shadow_* receipt", "")
    shadow = (EXECUTOR / "v36_shadow_brain.py").read_text(encoding="utf-8")
    for forbidden in ("api_post", "api_delete", "place_order", "cancel_order"):
        assert forbidden not in shadow


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} Stage-C V36 shadow tests")
