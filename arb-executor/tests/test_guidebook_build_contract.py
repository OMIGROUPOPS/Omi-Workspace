import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "guidebook_build.py"


def _module():
    spec = importlib.util.spec_from_file_location("guidebook_build_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_close_keyed_recut_is_rejected_before_output(tmp_path):
    module = _module()
    module.RECUT = (
        ROOT.parent / ".claude" / "seqfloor_20260708" / "recut_cells.json"
    )
    module.OUT = tmp_path / "GUIDEBOOK_V1.json"

    with pytest.raises(RuntimeError, match="INVALID_AIM_KEY_BRIDGE"):
        module.build()

    assert not module.OUT.exists()


def test_exact_forward_contract_is_the_only_accepted_shape():
    module = _module()
    cells = {"ATP_MAIN": {"50": {"n": 20, "edge_p50": 3}}}
    source = {
        "meta": {
            "surface_role": "forward_entry_aim",
            "fit_key": {
                "price_source": "fresh_last_trade",
                "timestamp_semantics": "exact_consultation_time",
                "timestamp_retained": True,
            },
            "target": {
                "direction": "subsequent_attainable_depth",
                "horizon": "lawful_window_1",
            },
        },
        "cells": cells,
    }

    assert module._forward_cells(source) is cells


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("fit_key", "price_source", "window1_close"),
        ("fit_key", "timestamp_semantics", "window_left_edge"),
        ("fit_key", "timestamp_retained", False),
        ("target", "direction", "retrospective_depth"),
        ("target", "horizon", "policy_horizon"),
    ],
)
def test_near_miss_contracts_fail_closed(section, field, value):
    module = _module()
    source = {
        "meta": {
            "surface_role": "forward_entry_aim",
            "fit_key": {
                "price_source": "fresh_last_trade",
                "timestamp_semantics": "exact_consultation_time",
                "timestamp_retained": True,
            },
            "target": {
                "direction": "subsequent_attainable_depth",
                "horizon": "lawful_window_1",
            },
        },
        "cells": {},
    }
    source["meta"][section][field] = value

    with pytest.raises(RuntimeError, match="INVALID_AIM_KEY_BRIDGE"):
        module._forward_cells(source)
