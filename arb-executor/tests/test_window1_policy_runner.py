import json
import sys
import unittest
from pathlib import Path


ANALYSIS_DIR = Path(__file__).resolve().parents[1] / 'analysis'
sys.path.insert(0, str(ANALYSIS_DIR))

import window1_policy_runner as runner
from window1_benchmark import canonical_true_prints


def book(ticker, timestamp, sequence, bid_quantity=3):
    return {
        'receipt_id': f'book-{ticker}-{timestamp}',
        'ticker': ticker,
        'exchange_ts': timestamp,
        'source': 'ws_depth',
        'capture_depth': 'full',
        'epoch_id': f'epoch-{ticker}',
        'sequence': sequence,
        'sequence_valid': True,
        'gap_before': False,
        'reconnect': False,
        'corrupt': False,
        'bids': [[40, bid_quantity], [39, 10], [38, 15], [37, 20],
                 [36, 25], [35, 30]],
        'asks': [[41, 10], [42, 10]],
    }


def true_print(identity, ticker, timestamp, size=8):
    return {
        'receipt_id': identity,
        'ticker': ticker,
        'exchange_ts': timestamp,
        'price_cents': 40,
        'size': size,
        'source': 'public_tape',
        'true_print': True,
    }


@unittest.skip(
    "deprecated proxy runner; superseded by window1_fit_benchmark.py"
)
class CandidateGridTests(unittest.TestCase):
    def test_grid_has_16_boundaries_and_every_declared_policy(self):
        path = (Path(__file__).resolve().parents[1] / 'docs' / 'research'
                / 'window1' / 'WINDOW1_CANDIDATES.json')
        spec = json.loads(path.read_text(encoding='utf-8'))
        candidates = runner.candidate_definitions(spec)
        boundaries = [row for row in candidates
                      if row['experiment_kind'] == 'boundary']
        policies = [row for row in candidates
                    if row['experiment_kind'] == 'policy']
        self.assertEqual(len(boundaries), 16)
        self.assertEqual(len(policies), 16 * len(spec['policies']))
        self.assertFalse(spec['dca'])
        self.assertFalse(spec['window2_or_exit_inputs'])

    def test_ablation_grid_removes_one_named_family_at_a_time(self):
        path = (Path(__file__).resolve().parents[1] / 'docs' / 'research'
                / 'window1' / 'WINDOW1_CANDIDATES.json')
        spec = json.loads(path.read_text(encoding='utf-8'))
        policy = spec['policies'][0]
        freeze = {
            'selected_candidate_id': 'P1',
            'selected_window_definition': {
                'boundary_id': 'b1',
                'left_edge_hours_before_schedule': 8,
                'schedule_only_corridor_minutes': 30,
            },
            'selected_policy_definition': policy,
        }
        candidates = runner.ablation_definitions(spec, freeze)
        self.assertEqual(len(candidates), len(spec['feature_ablations']))
        self.assertEqual(
            {row['feature_removed'] for row in candidates},
            set(spec['feature_ablations']))
        self.assertTrue(all(row['experiment_kind'] == 'ablation'
                            for row in candidates))


@unittest.skip(
    "deprecated proxy runner; superseded by window1_fit_benchmark.py"
)
class RunnerCausalityTests(unittest.TestCase):
    def test_gap_inside_candidate_window_is_corrupt(self):
        rows = [book('T-A', 100, 1), book('T-A', 110, 2)]
        rows[1]['gap_before'] = True
        valid, defect = runner.full_books_for('T-A', rows, 90, 120)
        self.assertEqual(valid, [])
        self.assertIn('gap', defect)

    def test_full_ladder_features_include_below_top_five_and_extreme_class(self):
        row = book('T-A', 100, 1)
        row['asks'] = [[41, 500], [42, 500]]
        receipt = runner.feature_receipt(
            {'category': 'ATP_MAIN', 'schedule_source': 'official'},
            {'ticker': 'T-A', 'role': 'favorite', 'shape_class': 'flat'},
            row, [], 100, 200)
        micro = receipt['microstructure']
        self.assertGreater(micro['bid_depth_below_top5'], 0)
        self.assertTrue(micro['extreme_ask_over_bid_sanity_class'])

    def test_two_leg_static_policy_produces_causal_dual_fill_outcome(self):
        event = {
            'event_id': 'E1',
            'category': 'ATP_MAIN',
            'event_date': '2026-07-12',
            'scheduled_start_exchange_ts': 100,
            'schedule_source': 'official',
            'actual_start_exchange_ts': 200,
            'actual_start_source': 'sportradar_milestone',
            'actual_start_verified': True,
            'legs': [
                {'ticker': 'T-A', 'leg': 'A', 'role': 'favorite',
                 'shape_class': 'flat'},
                {'ticker': 'T-B', 'leg': 'B', 'role': 'underdog',
                 'shape_class': 'flat'},
            ],
        }
        candidate = {
            'candidate_id': 'P1',
            'experiment_kind': 'policy',
            'boundary_id': 'b1',
            'policy_id': 'park',
            'window_definition': {
                'boundary_id': 'b1',
                'left_edge_hours_before_schedule': 0,
                'schedule_only_corridor_minutes': 30,
            },
            'policy_definition': {
                'policy_id': 'park',
                'placement_rule': 'touch',
                'sequence_rule': 'simultaneous',
                'first_fill_response': 'hold',
            },
        }
        books = [book('T-A', 100, 1), book('T-B', 100, 1)]
        prints, errors = canonical_true_prints([
            true_print('r1', 'T-A', 120),
            true_print('r2', 'T-B', 121),
        ])
        self.assertEqual(errors, [])
        result = runner.simulate_event(event, candidate, books, prints, 'fit')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual([leg['status'] for leg in result['legs']],
                         ['filled', 'filled'])
        self.assertEqual([leg['fill_vwap_cents'] for leg in result['legs']],
                         [40, 40])


if __name__ == '__main__':
    unittest.main()
