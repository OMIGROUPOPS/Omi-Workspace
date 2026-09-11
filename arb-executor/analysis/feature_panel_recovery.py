"""Import explicitly approved local model artifacts without fitting or pickle.

This validates the evidence actually stored in a partial run. Legacy model
files do not bind the complete input registry or every contract constant, so
the caller must opt in to the saved directory and independently verify/bind
the current immutable inputs. The import never claims missing provenance.
"""
from __future__ import annotations

from io import BytesIO
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np

import feature_panel_bench as bench
import feature_panel as panel
import feature_panel_model as model


def _require(condition, label):
    if not condition:
        raise ValueError("RECOVERED_MODEL_" + label)


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _require(key not in result, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("RECOVERED_MODEL_NONFINITE_JSON:" + value)

    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique, parse_constant=invalid)


def _paths(model_dir, month):
    _require(isinstance(month, str) and re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month), "MONTH")
    directory = Path(model_dir).resolve(strict=True)
    paths = [directory / (prefix + month + suffix)
             for prefix, suffix in (("MODEL_", ".json"), ("SCALES_", ".npz"))]
    for path in paths:
        _require(path.resolve(strict=True).parent == directory, "ARTIFACT_OUTSIDE_DIRECTORY")
    return paths


def recovered_model_evidence(model_dir, month):
    """Report local file bindings; a missing old run receipt is explicit."""
    paths = _paths(model_dir, month)
    evidence = dict(files={p.name: dict(bytes=p.stat().st_size, sha256=panel.sha256(p)) for p in paths},
        authorization="CALLER_EXPLICITLY_APPROVED_SAVED_MODEL_DIRECTORY",
        validation_scope="stored plan, coefficient registry, numeric fields, scales and filed quantiles",
        requires_current_inputs_verified=True)
    receipt_path = Path(model_dir) / "FEATURE_PANEL_RECEIPT.json"
    if receipt_path.is_file():
        receipt = _json(receipt_path.read_bytes())
        evidence.update(source_registry_status="AVAILABLE_REQUIRES_CALLER_COMPARISON",
            source_registry=receipt.get("source_registry"),
            run_receipt_sha256=panel.sha256(receipt_path))
    else:
        evidence["source_registry_status"] = "UNAVAILABLE_LEGACY_PARTIAL_RUN"
    return evidence


def load_recovered_model(model_dir, category, month, expected_plan, contract):
    """Return the exact frozen model and original empirical-scale proof.

``expected_plan`` is the freshly computed ``outer_month_plan`` (or its
``plan_receipt``). This does not resume an old scoreboard. No input pickle is
read, no fitting runs, and no scientific receipt content is rewritten.
"""
    model_path, scale_path = _paths(model_dir, month)
    receipt = _json(model_path.read_bytes())
    _require(isinstance(receipt, dict), "RECEIPT")
    required = {"plan", "scales", "inner_folds", "model_class_choices", "refits", "refit_cache",
                "coefficients", "heldout_months", "training_normalizers", "empirical_distributions"}
    _require(required <= receipt.keys(), "INCOMPLETE_RECEIPT")
    full_plan = "queries" in expected_plan and "training" in expected_plan
    expected = bench.plan_receipt(expected_plan) if full_plan else expected_plan
    _require(expected.get("category") == category and expected.get("month") == month, "EXPECTED_IDENTITY")
    _require(_number(expected.get("cutoff")), "CUTOFF")
    _require(receipt["plan"] == expected, "PLAN_MISMATCH")
    cutoff = expected["cutoff"]
    heldout = receipt["heldout_months"]
    _require(isinstance(heldout, list) and all(isinstance(m, str) and
        re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", m) for m in heldout)
        and len(heldout) == len(set(heldout)), "HELDOUT_MONTHS")
    _require((month in heldout) == expected["strict_holdout"], "HELDOUT_SCOPE")
    if "heldout_months" in expected_plan:
        _require(heldout == list(expected_plan["heldout_months"]), "HELDOUT_MONTHS_MISMATCH")
    if full_plan:
        _require(all(p.category == category and p.date[:7] not in heldout and
                     p.date[:7] < month and p.bell < cutoff for p in expected_plan["training"]), "TRAINING_SCOPE")
    inner = receipt["inner_folds"]
    _require(isinstance(inner, list) and len(inner) == len(expected["inner"]), "INNER_FOLD_COUNT")
    for saved, wanted in zip(inner, expected["inner"]):
        _require(isinstance(saved, dict) and all(saved.get(k) == v for k, v in wanted.items()), "INNER_FOLD_PLAN")

    fields = tuple(f for f in panel.FIELDS if f.block is not None)
    numeric_names = tuple(f.name for f in fields if f.kind == "numeric")
    numeric = set(numeric_names)
    blocks = tuple(panel.BLOCKS)
    registry = bench.variant_registry(blocks)
    coefficients, saved_coefficients = {}, receipt["coefficients"]
    _require(isinstance(saved_coefficients, dict) and set(saved_coefficients) ==
             {v.name for v in registry}, "VARIANT_REGISTRY")
    choices = receipt["model_class_choices"]
    _require(isinstance(choices, dict) and set(choices) == {v.name for v in registry if v.name != "FIRST"},
             "CHOICE_REGISTRY")
    for variant in registry:
        saved = saved_coefficients[variant.name]
        _require(isinstance(saved, dict) and set(saved) == set(blocks), "BLOCK_REGISTRY")
        _require(all(_number(value) and value >= 0 for value in saved.values()), "COEFFICIENT_VALUE")
        _require(all(saved[name] == 0 for name in blocks if name not in variant.blocks), "INACTIVE_COEFFICIENT")
        if variant.name != "FIRST":
            _require(isinstance(choices[variant.name], dict), "MODEL_CLASS_CHOICE")
            choice = choices[variant.name].get("selected")
            _require(choice in {"FIRST_ZERO", "CONTINUOUS"}, "MODEL_CLASS_CHOICE")
            _require(choice != "FIRST_ZERO" or not any(saved.values()), "ZERO_CHOICE_COEFFICIENT")
        coefficients[variant.name] = np.asarray([saved[name] for name in blocks], dtype=float)

    proof, scale_receipt = receipt["empirical_distributions"], receipt["scales"]
    _require(isinstance(proof, dict) and isinstance(scale_receipt, dict), "SCALE_PROOF")
    _require(proof.get("category") == category and proof.get("month") == month and
             _number(proof.get("cutoff")) and proof["cutoff"] == cutoff, "SCALE_IDENTITY")
    _require(proof.get("path") == scale_path.name, "SCALE_PATH")
    quantiles = contract["quantiles"]
    _require(all(_number(q) and 0 <= q <= 1 for q in quantiles) and
             proof.get("quantiles_from_filed_contract") == list(quantiles), "CONTRACT_QUANTILES")
    _require(scale_receipt.get("training_games") == expected["training_games"], "SCALE_TRAINING_COUNT")
    if full_plan:
        atlas_count = sum(sum(0 < g <= p.first_mtb for g in contract["gates_minutes_to_bell"])
                          for p in expected_plan["training"])
        _require(scale_receipt.get("sampled_atlas_receipts") == atlas_count, "SCALE_ATLAS_COUNT")
    _require(isinstance(scale_receipt.get("features"), dict) and set(scale_receipt["features"]) == numeric
             and isinstance(proof.get("fields"), dict) and set(proof["fields"]) == numeric, "NUMERIC_FIELD_REGISTRY")
    raw = scale_path.read_bytes()
    _require(hashlib.sha256(raw).hexdigest() == proof.get("sha256"), "SCALE_FILE_HASH")
    scales = {}
    with np.load(BytesIO(raw), allow_pickle=False) as saved:
        # Original fitting and NPZ writing use feature-registry insertion order.
        # Preserving it also preserves the rewritten archive's scientific bytes.
        _require(tuple(saved.files) == numeric_names, "SCALE_ARRAY_REGISTRY")
        for name in numeric_names:
            values = saved[name]
            _require(values.dtype == np.dtype(float) and values.ndim == 1 and np.isfinite(values).all()
                     and np.all(values[:-1] <= values[1:]), "SCALE_ARRAY_VALUES")
            filed, detail = scale_receipt["features"][name], proof["fields"][name]
            _require(isinstance(filed, dict) and isinstance(detail, dict), "SCALE_FIELD_PROOF")
            _require(filed.get("n") == len(values) and detail.get("n") == len(values), "SCALE_FIELD_COUNT")
            _require(filed.get("sha256") == hashlib.sha256(values.tobytes()).hexdigest(), "SCALE_FIELD_HASH")
            actual = {str(q): bench.b.inverse_weighted_quantile(values, np.ones(len(values)), q)
                      if len(values) else None for q in quantiles}
            _require(detail.get("quantiles") == actual, "SCALE_FIELD_QUANTILES")
            scales[name] = model.EmpiricalRankScale(values)
    frozen = bench.FrozenMonthModel(category, month, cutoff,
        bench.RankedBlockKernel(fields, blocks, scales), coefficients, receipt)
    return frozen, proof
