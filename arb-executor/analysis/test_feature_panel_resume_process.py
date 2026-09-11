"""Real abrupt process exit and exact resume across independent hash seeds."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import feature_panel_checkpoint as checkpoint
import feature_panel_run as run
from test_feature_panel_resume import BINDING


_CHILD = r'''
import os
from pathlib import Path
import sys
import feature_panel_checkpoint as checkpoint
from test_feature_panel_resume import BINDING, run_fixture

mode, output, private = sys.argv[1:]
output, private = Path(output), Path(private)
if mode == "reference":
    run_fixture(output)
else:
    with checkpoint.CheckpointStore(private, BINDING, output_dir=output) as store:
        def progress(row):
            if mode == "crash" and row["phase"] == "QUERY_COMPLETE" and row["completed_evaluations"] == 7:
                assert len(store.completed) == 7
                print("DURABLE_PREFIX=7", flush=True)
                os._exit(73)
        run_fixture(output, store=store, workers=2 if mode == "resume" else 1, progress=progress)
        assert len(store.completed) == 9
'''


class ProcessResumeTests(unittest.TestCase):
    def test_abrupt_exit_and_different_hash_seed_resume_are_byte_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference, resumed, private = root/"reference", root/"resumed", root/"checkpoint"
            for mode, seed, output, expected_status in (
                    ("reference", "101", reference, 0),
                    ("crash", "202", resumed, 73),
                    ("resume", "303", resumed, 0)):
                env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONDONTWRITEBYTECODE="1")
                process = subprocess.run([sys.executable, "-B", "-c", _CHILD,
                    mode, str(output), str(private)], cwd=Path(__file__).resolve().parent,
                    env=env, capture_output=True, text=True, timeout=90)
                self.assertEqual(process.returncode, expected_status,
                    mode+" subprocess failed:\n"+process.stdout+"\n"+process.stderr)
                if mode == "crash":
                    self.assertIn("DURABLE_PREFIX=7", process.stdout)
                    # No normal context-manager cleanup occurred. Acquiring
                    # this store verifies the OS released the crashed writer.
                    with checkpoint.CheckpointStore(private, BINDING, output_dir=resumed) as store:
                        self.assertEqual(len(store.completed), 7)
                        self.assertIsNotNone(store.load_state())
            with checkpoint.CheckpointStore(private, BINDING, output_dir=resumed) as store:
                self.assertEqual(len(store.completed), 9)
            self.assertEqual(run.compare_runs(reference, resumed)["status"], "DETERMINISTIC")
            left = {p.relative_to(reference): p for p in reference.rglob("*") if p.is_file()}
            right = {p.relative_to(resumed): p for p in resumed.rglob("*") if p.is_file()}
            self.assertEqual(set(left), set(right))
            for name in left:
                if name.as_posix() != "FEATURE_PANEL_RECEIPT.json":
                    self.assertEqual(left[name].read_bytes(), right[name].read_bytes(), name.as_posix())


if __name__ == "__main__":
    unittest.main()
