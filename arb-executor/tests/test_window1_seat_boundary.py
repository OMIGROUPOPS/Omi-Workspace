import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "arb-executor" / "analysis" / "window1_seat_boundary.py"
SPEC = importlib.util.spec_from_file_location("window1_seat_boundary", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class Window1SeatBoundaryTests(unittest.TestCase):
    def test_analysis_allowlist_accepts_owned_namespaces(self):
        paths = [
            "arb-executor/analysis/second_seat/pulse_return.py",
            "arb-executor/tests/analysis_second_seat/test_pulse_return.py",
            "arb-executor/docs/research/window1/second_seat/REPORT.md",
            ".claude/window1_second_seat/RECEIPT.json",
        ]
        self.assertEqual(MODULE.validate_analysis(paths), [])

    def test_analysis_allowlist_rejects_live_and_replay_surfaces(self):
        paths = [
            "arb-executor/live_v4.py",
            "arb-executor/analysis/window1_live_v4_replay.py",
            "arb-executor/config/deploy_v5_live.json",
            "arb-executor/deploy/deploy_live_v4.sh",
        ]
        self.assertEqual(MODULE.validate_analysis(paths), paths)

    def test_similar_prefix_cannot_escape_namespace(self):
        path = "arb-executor/analysis/second_seat_escape.py"
        self.assertEqual(MODULE.validate_analysis([path]), [path])


if __name__ == "__main__":
    unittest.main()
