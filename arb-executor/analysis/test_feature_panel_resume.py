"""Synthetic interrupted-run parity and fail-closed resume integration tests."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import feature_panel_bench as bench
import feature_panel_checkpoint as checkpoint
import feature_panel_run as run
from test_feature_panel_parallel import population_fixture


SOURCE_REGISTRY = {"fixture": "synthetic"}
BINDING = dict(source_registry=SOURCE_REGISTRY,
               code_sha256={"synthetic_execution_fixture": "a"*64},
               protocol={"category": "category", "heldout_months": ["2026-06"]})


class InterruptedForTest(RuntimeError):
    pass


def run_fixture(output, *, workers=1, store=None, progress=None, import_models=None):
    pairs, sampler, baseline, spec = population_fixture()
    return bench.run_category(pairs, sampler, baseline, spec, "category", output,
        heldout_months=["2026-06"], batch_size=2, cache_budget_bytes=1_000_000,
        source_registry=SOURCE_REGISTRY, workers=workers,
        checkpoint_store=store, import_models=import_models, progress=progress or (lambda _: None))


class ResumeTests(unittest.TestCase):
    def interrupt_after(self, output, store, count, *, workers=1):
        seen = []
        def interrupt(row):
            if row["phase"] != "QUERY_COMPLETE":
                return
            seen.append((row["event_id"], row["stream"], row["month"]))
            # A progress report must describe a durable commit, even if the
            # process is interrupted immediately upon reporting completion.
            self.assertEqual(len(store.completed), row["completed_evaluations"])
            self.assertEqual(store.completed[-1], seen[-1])
            if len(seen) == count:
                raise InterruptedForTest("simulated interruption after durable evaluation")
        with self.assertRaisesRegex(InterruptedForTest, "simulated interruption"):
            run_fixture(output, workers=workers, store=store, progress=interrupt)
        self.assertEqual(len(seen), count)
        self.assertEqual(store.completed, tuple(seen))
        return tuple(seen)

    def assert_scientific_artifacts_equal(self, first, second):
        proof = run.compare_runs(first, second)
        self.assertEqual(proof["status"], "DETERMINISTIC")
        self.assertEqual(proof["excluded_only"], {
            "FEATURE_PANEL_RECEIPT.json": ["numerical_execution.elapsed_seconds"]})
        left = {p.relative_to(first): p for p in first.rglob("*") if p.is_file()}
        right = {p.relative_to(second): p for p in second.rglob("*") if p.is_file()}
        self.assertEqual(set(left), set(right))
        for name in left:
            if str(name) != "FEATURE_PANEL_RECEIPT.json":
                self.assertEqual(left[name].read_bytes(), right[name].read_bytes(), str(name))

    def test_interrupt_reopen_change_worker_count_preserves_all_scientific_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            serial = root/"serial"
            run_fixture(serial)
            # First case crosses a month boundary; second resumes partway
            # through June's strict holdout stream. Both scheduling directions
            # must preserve the original receipt addition order.
            for cut, first_workers, resumed_workers in ((2, 1, 2), (7, 2, 1)):
                with self.subTest(cut=cut, workers=(first_workers, resumed_workers)):
                    output, private = root/("resumed-"+str(cut)), root/("checkpoints-"+str(cut))
                    with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                        committed = self.interrupt_after(output, store, cut, workers=first_workers)
                    rows = []
                    with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                        self.assertEqual(store.completed, committed)
                        run_fixture(output, workers=resumed_workers, store=store, progress=rows.append)
                        self.assertEqual(len(store.completed), 9)
                    new_evaluations = [row for row in rows if row["phase"] == "QUERY_COMPLETE"]
                    self.assertEqual(len(new_evaluations), 9-cut)
                    self.assertEqual([row["completed_evaluations"] for row in new_evaluations], list(range(cut+1, 10)))
                    self.assertTrue(all((row["event_id"], row["stream"], row["month"]) not in committed
                                        for row in new_evaluations))
                    self.assert_scientific_artifacts_equal(serial, output)

    def test_completed_resume_does_not_refit_or_evaluate_again(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, private = root/"output", root/"checkpoints"
            with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                run_fixture(output, store=store)
            before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*")
                      if p.is_file() and p.name != "FEATURE_PANEL_RECEIPT.json"}
            with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                with patch.object(bench, "fit_outer_month", side_effect=AssertionError("resume refitted a frozen model")), \
                     patch.object(bench, "evaluate_query", side_effect=AssertionError("resume reevaluated a completed query")):
                    run_fixture(output, store=store, workers=1)
                self.assertEqual(len(store.completed), 9)
            after = {p.relative_to(output): p.read_bytes() for p in output.rglob("*")
                     if p.is_file() and p.name != "FEATURE_PANEL_RECEIPT.json"}
            self.assertEqual(before, after)

    def test_imported_models_avoid_refitting_and_preserve_scientific_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original, imported = root/"original", root/"imported"
            run_fixture(original)
            with patch.object(bench, "fit_outer_month", side_effect=AssertionError("imported model was refitted")):
                run_fixture(imported, import_models=original)
            self.assert_scientific_artifacts_equal(original, imported)

    def test_corrupt_completed_diagnostic_fails_before_further_evaluation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, private = root/"output", root/"checkpoints"
            with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                committed = self.interrupt_after(output, store, 2)
            damaged = output/"receipt_diagnostics"/(committed[0][0]+"__"+committed[0][1]+".npz")
            with damaged.open("ab") as stream:
                stream.write(b"damaged completed diagnostic")
            with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                with patch.object(bench, "evaluate_query", side_effect=AssertionError("evaluated after corrupt diagnostic")):
                    with self.assertRaisesRegex(ValueError, "CHECKPOINT|RESUME|DIAGNOSTIC|HASH_MISMATCH"):
                        run_fixture(output, store=store)
                self.assertEqual(store.completed, committed)

    def test_valid_store_with_mismatched_evaluation_prefix_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root/"output"
            with checkpoint.CheckpointStore(root/"original", BINDING, output_dir=output) as original:
                self.interrupt_after(output, original, 1)
                state = original.load_state()
                models = {key: original.load_model(key) for key in original.model_keys}
            wrong_identity = ("not-in-the-evaluation-plan", "PRIMARY", "2026-04")
            # The store is structurally sound and every hash is valid. The
            # benchmark must additionally bind its completed prefix to the
            # exact original evaluation plan rather than trusting its length.
            with checkpoint.CheckpointStore(root/"mismatched", BINDING, output_dir=output) as store:
                for key, model in models.items():
                    store.save_model(key, model)
                store.commit_state(state, completed=[wrong_identity])
            with checkpoint.CheckpointStore(root/"mismatched", BINDING, output_dir=output) as store:
                with patch.object(bench, "fit_outer_month", side_effect=AssertionError("fitted after invalid prefix")), \
                     patch.object(bench, "evaluate_query", side_effect=AssertionError("evaluated after invalid prefix")):
                    with self.assertRaisesRegex(ValueError, "CHECKPOINT|RESUME|PREFIX|ORDER"):
                        run_fixture(output, store=store)
                self.assertEqual(store.completed, (wrong_identity,))

    def test_saved_model_must_match_published_model_and_scale_files(self):
        for changed in ("model", "scale"):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output, private = root/"output", root/"checkpoints"
                with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                    self.interrupt_after(output, store, 2)
                if changed == "model":
                    path = output/"MODEL_2026-04.json"
                    value = json.loads(path.read_text(encoding="utf-8"))
                    value["method"] += " changed after commit"
                    bench.write_json(path, value)
                else:
                    with (output/"SCALES_2026-04.npz").open("ab") as stream:
                        stream.write(b"changed after commit")
                with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                    with patch.object(bench, "fit_outer_month", side_effect=AssertionError("fitted after model output mismatch")), \
                         patch.object(bench, "evaluate_query", side_effect=AssertionError("evaluated after model output mismatch")):
                        with self.assertRaisesRegex(ValueError, "CHECKPOINT|RECOVER|MODEL|SCALE|HASH"):
                            run_fixture(output, store=store)
                    self.assertEqual(len(store.completed), 2)


if __name__ == "__main__":
    unittest.main()
