"""Durability/exactness tests; synthetic execution data, no model calibration."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import feature_panel_checkpoint as checkpoint
import feature_panel_parallel as parallel
from test_feature_panel_scoring import baseline, forecast, identity, targets


BINDING = dict(source_registry={"fixture": {"sha256": "a"*64}},
               code_sha256={"fixture.py": "b"*64}, protocol={"category": "ATP_MAIN"})


def evaluation(number):
    return ("event-"+str(number), "PRIMARY", "2026-06")


def add_evaluation(channels, number):
    # This sequence exposes loss from changing receipt/partial-sum order.
    for offset, level in enumerate((1e16, 1.0, 1.0, 1.0)):
        for name, scorer in channels.items():
            ident = identity("event-"+str(number), receipt=str(offset), stream=name)
            distributions = dict(FIRST=forecast(level), FEATURE=forecast(level+2.0))
            scorer.apply_prepared_receipt(scorer.prepare_receipt(ident, targets(), distributions))
    channels["all"].add_conduct_event(identity("event-"+str(number), stream="PRIMARY"), dict(
        FIRST=dict(completed=1, one_sided=0, captured_cents=number+.1),
        FEATURE=dict(completed=1, one_sided=0, captured_cents=number+.2)))


class CheckpointTests(unittest.TestCase):
    def test_exact_accumulators_resume_and_continue_original_order(self):
        original = parallel.scorer_channels(baseline(), ["FIRST", "FEATURE"])
        resumed = parallel.scorer_channels(baseline(), ["FIRST", "FEATURE"])
        with tempfile.TemporaryDirectory() as directory:
            for number in range(5):
                add_evaluation(original, number)
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                for number in range(2):
                    add_evaluation(resumed, number)
                    state = dict(channels=resumed, results=[{"event_id": evaluation(i)[0]} for i in range(number+1)],
                        diagnostics=[{"sha256": str(i)} for i in range(number+1)], receipts=(number+1)*4)
                    store.commit_state(state, completed=[evaluation(i) for i in range(number+1)])
                self.assertEqual(len(list(Path(directory).glob("state-*.pickle.gz"))), 1)
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                restored = store.load_state()
                self.assertEqual(restored["results"], state["results"])
                self.assertEqual(restored["diagnostics"], state["diagnostics"])
                self.assertEqual(restored["receipts"], 8)
                resumed = restored["channels"]
                for number in range(2, 5):
                    add_evaluation(resumed, number)
                    store.commit_state(dict(channels=resumed), completed=[*store.completed, evaluation(number)])
                for name in original:
                    self.assertEqual(json.dumps(original[name].finish(), sort_keys=True),
                                     json.dumps(resumed[name].finish(), sort_keys=True))
                    # Check stored sums directly, independent of report rounding.
                    for group, entries in original[name].groups.items():
                        for target, cells in entries.items():
                            for variant, cell in cells["variants"].items():
                                actual = resumed[name].groups[group][target]["variants"][variant]
                                for metric, moments in cell.metrics.items():
                                    self.assertEqual(moments.total.hex(), actual.metrics[metric].total.hex())
                with self.assertRaisesRegex(ValueError, "DUPLICATE_RECEIPT_IDENTITY"):
                    resumed["all"].add_receipt(identity("event-4", receipt="0", stream="all"),
                        targets(), dict(FIRST=forecast(), FEATURE=forecast()))

    def test_restored_default_factories_create_new_metrics_exactly(self):
        channels = parallel.scorer_channels(baseline(), ["FIRST", "FEATURE"])
        add_evaluation(channels, 0)
        with tempfile.TemporaryDirectory() as directory:
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                store.commit_state(channels, completed=[evaluation(0)])
                restored = store.load_state()
                matched = next(iter(restored["all"].groups.values()))["carried"]["matched"]["FEATURE"]
                triple = matched.metrics["new_test_metric"]
                self.assertEqual(len(triple), 3)
                self.assertTrue(all(isinstance(value, checkpoint.scoring._Moments) for value in triple))
                triple[0].add(.1)
                self.assertEqual(triple[0].total.hex(), (.1).hex())

    def test_model_roundtrip_aliases_array_layout_and_immutable_key(self):
        values = np.asfortranarray(np.arange(12.).reshape(3, 4))
        model = dict(month="2026-06", values=values, alias=values, proof={"cutoff": 123.0})
        with tempfile.TemporaryDirectory() as directory:
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                self.assertIsNone(store.load_model("2026-06"))
                store.save_model("2026-06", model)
                with self.assertRaisesRegex(ValueError, "MODEL_ALREADY_EXISTS"):
                    store.save_model("2026-06", model)
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                actual = store.load_model("2026-06")
                np.testing.assert_array_equal(actual["values"], values)
                self.assertEqual(actual["values"].strides, values.strides)
                self.assertIs(actual["values"], actual["alias"])
                self.assertEqual(actual["proof"], model["proof"])
                self.assertEqual(store.model_keys, ("2026-06",))

    def test_source_code_protocol_and_output_changes_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/"checkpoints"
            output = Path(directory)/"artifacts"
            with checkpoint.CheckpointStore(root, BINDING, output_dir=output) as store:
                store.commit_state({"value": 1}, completed=[evaluation(0)])
            for key in BINDING:
                changed = copy.deepcopy(BINDING)
                changed[key]["changed"] = True
                with self.assertRaisesRegex(ValueError, "BINDING_MISMATCH"):
                    checkpoint.CheckpointStore(root, changed, output_dir=output)
            with self.assertRaisesRegex(ValueError, "BINDING_MISMATCH"):
                checkpoint.CheckpointStore(root, BINDING, output_dir=Path(directory)/"other")
            with checkpoint.CheckpointStore(root, BINDING, output_dir=output) as store:
                self.assertEqual(store.load_state(), {"value": 1})

    def test_manifest_corruption_and_blob_corruption_fail_closed(self):
        for corruption in ("manifest", "state", "model"):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as directory:
                with checkpoint.CheckpointStore(directory, BINDING) as store:
                    store.save_model("2026-06", {"weights": [1., 2.]})
                    store.commit_state({"value": 1}, completed=[evaluation(0)])
                if corruption == "manifest":
                    path = Path(directory)/"manifest.json"
                else:
                    path = next(Path(directory).glob(corruption+"-*.pickle.gz"))
                with path.open("ab") as stream:
                    stream.write(b"corruption")
                with self.assertRaisesRegex(ValueError, "CORRUPT|HASH_MISMATCH"):
                    checkpoint.CheckpointStore(directory, BINDING)

    def test_failed_manifest_commit_preserves_last_completed_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                store.commit_state({"value": "first"}, completed=[evaluation(0)])
                first_manifest = (Path(directory)/"manifest.json").read_bytes()
                replace = checkpoint._atomic_replace
                def fail_manifest(source, target):
                    if Path(target).name == "manifest.json":
                        raise OSError("injected manifest publication failure")
                    return replace(source, target)
                with patch.object(checkpoint, "_atomic_replace", side_effect=fail_manifest):
                    with self.assertRaisesRegex(OSError, "injected"):
                        store.commit_state({"value": "second"}, completed=[evaluation(0), evaluation(1)])
                self.assertEqual((Path(directory)/"manifest.json").read_bytes(), first_manifest)
                self.assertEqual(store.completed, (evaluation(0),))
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                self.assertEqual(store.load_state(), {"value": "first"})
                self.assertEqual(len(list(Path(directory).glob("state-*.pickle.gz"))), 1)
                self.assertFalse(list(Path(directory).glob("*.partial")))

    def test_missing_manifest_never_silently_resets_saved_state(self):
        with tempfile.TemporaryDirectory() as directory:
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                store.commit_state({"value": 1}, completed=[evaluation(0)])
            (Path(directory)/"manifest.json").unlink()
            with self.assertRaisesRegex(ValueError, "MANIFEST_MISSING"):
                checkpoint.CheckpointStore(directory, BINDING)
            self.assertEqual(len(list(Path(directory).glob("state-*.pickle.gz"))), 1)

    def test_budget_exhaustion_preserves_previous_state_and_removes_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                store.commit_state({"value": "first"}, completed=[evaluation(0)])
                used = sum(p.stat().st_size for p in Path(directory).iterdir())
                store.max_bytes = used+128
                with self.assertRaisesRegex(OSError, "DISK_BUDGET_EXCEEDED"):
                    store.commit_state({"payload": os.urandom(8192)}, completed=[evaluation(0), evaluation(1)])
                self.assertEqual(store.load_state(), {"value": "first"})
                self.assertFalse(list(Path(directory).glob("*.partial")))

    def test_prefix_must_append_exactly_one_unique_evaluation(self):
        with tempfile.TemporaryDirectory() as directory:
            with checkpoint.CheckpointStore(directory, BINDING) as store:
                store.commit_state({}, completed=[evaluation(0)])
                for prefix in ([], [evaluation(0)], [evaluation(1), evaluation(0)],
                               [evaluation(0), evaluation(1), evaluation(2)]):
                    with self.assertRaisesRegex(ValueError, "NONCONTIGUOUS_PREFIX"):
                        store.commit_state({}, completed=prefix)
                with self.assertRaisesRegex(ValueError, "DUPLICATE_EVALUATION"):
                    store.commit_state({}, completed=[evaluation(0), evaluation(0)])
                with self.assertRaisesRegex(ValueError, "INVALID_COMPLETED_PREFIX"):
                    store.commit_state({}, completed=[evaluation(0), ("bad",)])

    def test_exclusive_lock_and_outside_artifact_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "OUTSIDE_ARTIFACT"):
                checkpoint.CheckpointStore(root/"output"/"checkpoint", BINDING, output_dir=root/"output")
            with checkpoint.CheckpointStore(root/"checkpoint", BINDING) as store:
                with self.assertRaisesRegex(ValueError, "ALREADY_OPEN"):
                    checkpoint.CheckpointStore(root/"checkpoint", BINDING)
                self.assertIsNone(store.load_state())
            with checkpoint.CheckpointStore(root/"checkpoint", BINDING) as store:
                self.assertEqual(store.completed, ())
            with self.assertRaisesRegex(ValueError, "CLOSED"):
                store.load_state()

    def test_fsync_precedes_each_atomic_publication(self):
        events = []
        fsync, replace = checkpoint.os.fsync, checkpoint._atomic_replace
        def sync(descriptor):
            events.append("fsync")
            return fsync(descriptor)
        def publish(source, target):
            self.assertEqual(events[-1], "fsync")
            events.append("replace")
            return replace(source, target)
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(checkpoint.os, "fsync", side_effect=sync), patch.object(checkpoint, "_atomic_replace", side_effect=publish):
                with checkpoint.CheckpointStore(directory, BINDING) as store:
                    store.save_model("2026-06", {})
                    store.commit_state({}, completed=[evaluation(0)])
        self.assertEqual(events.count("replace"), 5)


if __name__ == "__main__":
    unittest.main()
