"""Saved-model import proofs; no population run or untrusted pickle."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

import feature_panel_bench as bench
import feature_panel_model as model
import feature_panel_recovery as recovery


class ModelRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.contract = dict(quantiles=[.1, .25, .5, .75, .9], gates_minutes_to_bell=[3, 1])
        train = SimpleNamespace(event_id="prior", category="ATP_MAIN", date="2026-05-01",
                                bell=50, first_mtb=5)
        self.plan = dict(category="ATP_MAIN", month="2026-06", cutoff=100., queries=[object()],
                         training=[train], inner=[], strict_holdout=True)
        fields = tuple(f for f in bench.panel.FIELDS if f.block is not None)
        blocks = tuple(bench.panel.BLOCKS)
        scales = {f.name: model.EmpiricalRankScale(np.asarray([0., .25, 3.]))
                  for f in fields if f.kind == "numeric"}
        registry = bench.variant_registry(blocks)
        self.receipt = dict(plan=bench.plan_receipt(self.plan),
            scales=dict(training_games=1, sampled_atlas_receipts=2,
                features={k: dict(n=3, sha256=hashlib.sha256(v.sorted_values.tobytes()).hexdigest())
                          for k, v in scales.items()}), inner_folds=[],
            model_class_choices={v.name: dict(selected="FIRST_ZERO") for v in registry if v.name != "FIRST"},
            refits={}, refit_cache=None, heldout_months=["2026-06"], training_normalizers={},
            coefficients={v.name: {block: 0. for block in blocks} for v in registry})
        self.frozen = bench.FrozenMonthModel("ATP_MAIN", "2026-06", 100.,
            bench.RankedBlockKernel(fields, blocks, scales),
            {v.name: np.zeros(len(blocks)) for v in registry}, self.receipt)
        coefficient = float(np.nextafter(.1, 1.))
        self.receipt["coefficients"]["CUMULATIVE_1"][blocks[0]] = coefficient
        self.receipt["model_class_choices"]["CUMULATIVE_1"]["selected"] = "CONTINUOUS"
        self.frozen.coefficients["CUMULATIVE_1"][0] = coefficient
        self.proof = bench.write_scale_diagnostics(self.directory, self.frozen, self.contract)
        self.receipt["empirical_distributions"] = self.proof
        self.write_receipt()

    def write_receipt(self):
        bench.write_json(self.directory / "MODEL_2026-06.json", self.receipt)

    def load(self):
        return recovery.load_recovered_model(self.directory, "ATP_MAIN", "2026-06", self.plan, self.contract)

    def test_exact_roundtrip_without_fitting_and_missing_source_evidence(self):
        frozen, proof = self.load()
        self.assertEqual(frozen.receipt, self.receipt)
        self.assertEqual(proof, self.proof)
        for name, scale in frozen.kernel.scales.items():
            self.assertEqual(scale.sorted_values.tobytes(), self.frozen.kernel.scales[name].sorted_values.tobytes())
        for name, value in frozen.coefficients.items():
            self.assertEqual(value.tobytes(), self.frozen.coefficients[name].tobytes())
        with tempfile.TemporaryDirectory() as rewritten:
            bench.write_scale_diagnostics(rewritten, frozen, self.contract)
            self.assertEqual((Path(rewritten) / self.proof["path"]).read_bytes(),
                             (self.directory / self.proof["path"]).read_bytes())
        evidence = recovery.recovered_model_evidence(self.directory, "2026-06")
        self.assertEqual(evidence["source_registry_status"], "UNAVAILABLE_LEGACY_PARTIAL_RUN")
        self.assertEqual(len(evidence["files"]), 2)

    def test_plan_identity_cutoff_and_scope_fail_closed(self):
        original = copy.deepcopy(self.receipt)
        for key, value in (("category", "ATP_CHALL"), ("month", "2026-07"), ("cutoff", 101.),
                           ("training_event_ids", ["different"]), ("strict_holdout", False)):
            with self.subTest(key=key):
                self.receipt = copy.deepcopy(original)
                self.receipt["plan"][key] = value
                self.write_receipt()
                with self.assertRaisesRegex(ValueError, "PLAN_MISMATCH"):
                    self.load()

    def test_coefficients_reject_nonfinite_negative_inactive_and_registry_drift(self):
        original = copy.deepcopy(self.receipt)
        block = next(iter(bench.panel.BLOCKS))
        changes = [("FIRST", block, .1), ("CUMULATIVE_1", block, -1.),
                   ("CUMULATIVE_1", block, float("inf")), ("CUMULATIVE_1", block, True)]
        for variant, field, value in changes:
            with self.subTest(value=value, variant=variant):
                self.receipt = copy.deepcopy(original)
                self.receipt["coefficients"][variant][field] = value
                (self.directory / "MODEL_2026-06.json").write_text(json.dumps(self.receipt), encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.load()
        self.receipt = copy.deepcopy(original)
        self.receipt["coefficients"]["UNREGISTERED"] = self.receipt["coefficients"]["FIRST"]
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, "VARIANT_REGISTRY"):
            self.load()

    def test_scale_file_and_internal_proofs_are_checked(self):
        original = copy.deepcopy(self.receipt)
        name = next(iter(self.proof["fields"]))
        for section, key, value in (("empirical_distributions", "cutoff", 101.),
                                    ("empirical_distributions", "path", "../other.npz"),
                                    ("empirical_distributions", "sha256", "0" * 64)):
            with self.subTest(key=key):
                self.receipt = copy.deepcopy(original)
                self.receipt[section][key] = value
                self.write_receipt()
                with self.assertRaises(ValueError):
                    self.load()
        self.receipt = copy.deepcopy(original)
        self.receipt["scales"]["features"][name]["sha256"] = "0" * 64
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, "SCALE_FIELD_HASH"):
            self.load()
        self.receipt = copy.deepcopy(original)
        self.receipt["empirical_distributions"]["fields"][name]["quantiles"]["0.5"] = 9
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, "SCALE_FIELD_QUANTILES"):
            self.load()

    def test_contract_and_field_registry_mismatches_rejected(self):
        self.contract["quantiles"] = [.5]
        with self.assertRaisesRegex(ValueError, "CONTRACT_QUANTILES"):
            self.load()
        self.contract["quantiles"] = [.1, .25, .5, .75, .9]
        self.receipt["scales"]["features"]["new_field"] = dict(n=0, sha256="0" * 64)
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, "NUMERIC_FIELD_REGISTRY"):
            self.load()

    def test_duplicate_json_keys_and_unsafe_month_rejected(self):
        path = self.directory / "MODEL_2026-06.json"
        raw = path.read_text(encoding="utf-8")
        path.write_text('{"plan":{},' + raw[1:], encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            self.load()
        with self.assertRaisesRegex(ValueError, "MONTH"):
            recovery.load_recovered_model(self.directory, "ATP_MAIN", "../2026-06", self.plan, self.contract)


if __name__ == "__main__":
    unittest.main()
