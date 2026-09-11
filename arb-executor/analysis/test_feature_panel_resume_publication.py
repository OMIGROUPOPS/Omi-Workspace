"""Durable artifact reuse when a finished checkpoint only needs finalization."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import feature_panel_bench as bench
import feature_panel_checkpoint as checkpoint
from test_feature_panel_resume import BINDING, run_fixture


class ResumePublicationTests(unittest.TestCase):
    def test_resume_never_overwrites_checkpoint_bound_models_or_scales(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, private = root/"output", root/"checkpoint"
            with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                run_fixture(output, store=store)
            original = {p.name: p.read_bytes() for p in output.iterdir()
                        if p.name.startswith(("MODEL_", "SCALES_"))}
            write_json = bench.write_json
            def publish(path, value):
                if Path(path).name.startswith("MODEL_"):
                    self.fail("resume overwrote a checkpoint-bound model")
                return write_json(path, value)
            with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
                with patch.object(bench, "write_scale_diagnostics", side_effect=AssertionError(
                        "resume overwrote checkpoint-bound scales")), \
                     patch.object(bench, "write_json", side_effect=publish):
                    run_fixture(output, store=store)
                self.assertEqual(len(store.completed), 9)
            self.assertEqual(original, {name: (output/name).read_bytes() for name in original})


if __name__ == "__main__":
    unittest.main()
