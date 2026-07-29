from pathlib import Path
import sys
import unittest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_evaluator_boundary import full_lawful_right


class EvaluatorBoundaryTests(unittest.TestCase):
    def test_late_actual_start_extends_evaluator_but_not_policy(self) -> None:
        self.assertEqual(full_lawful_right(
            policy_right_ts=1000.0,
            guarded_cutoff_ts=1600.0,
            positive_window1_provable=True,
        ), 1600.0)

    def test_early_actual_start_still_controls_evaluator(self) -> None:
        self.assertEqual(full_lawful_right(
            policy_right_ts=1000.0,
            guarded_cutoff_ts=800.0,
            positive_window1_provable=True,
        ), 800.0)

    def test_unresolved_is_not_replaced_with_policy_horizon(self) -> None:
        self.assertIsNone(full_lawful_right(
            policy_right_ts=1000.0,
            guarded_cutoff_ts=None,
            positive_window1_provable=False,
        ))

    def test_positive_boundary_requires_guarded_cutoff(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "positive boundary lacks guarded actual-start cutoff",
        ):
            full_lawful_right(
                policy_right_ts=1000.0,
                guarded_cutoff_ts=None,
                positive_window1_provable=True,
            )


if __name__ == "__main__":
    unittest.main()
