"""Private-input launcher/public-summary exporter for the full atlas screen.

No raw source, witness, diagnostic array or fitted sample is published by this
module. The full receipt-cadence runner is not edited or invoked in screen mode.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import feature_panel_atlas as atlas
import feature_panel_bench as bench
import feature_panel_run as launcher
import feature_panel_report as report
import feature_panel_scoring as scoring

ATLAS_FILES = ('feature_panel_atlas.py', 'feature_panel_atlas_optimizer.py',
               'feature_panel_atlas_run.py')


class SelectionTee:
    def __init__(self, original, selection):
        self.original, self.selection = original, selection

    def add_receipt(self, identity, targets, forecasts, **kwargs):
        self.original.add_receipt(identity, targets, forecasts, **kwargs)
        self.selection.add_receipt(dict(identity, stream='NON_JUNE_SELECTION_FILED_SCORABLE_GATES'),
                                   targets, forecasts, **kwargs)


def summaries(output):
    output = Path(output)
    receipt = launcher.json_file(output/'FEATURE_PANEL_RECEIPT.json')
    board = launcher.json_file(output/'FEATURE_PANEL_SCOREBOARD.json')
    variants = [v['name'] for v in report.required_variants(receipt)]
    data = dict(board=board, receipt=receipt, variants=variants,
                contract=report.checked_contract(board, receipt))
    rows, filed = report.forecast_rows(data)
    selection_board = dict(board, filed_scorable_gates=board['selection_filed_scorable_gates'])
    _, selection = report.forecast_rows(dict(data, board=selection_board))
    selection = [x for x in selection if x['stream']=='NON_JUNE_SELECTION_FILED_SCORABLE_GATES']
    qualifications = [x for x in selection if x['qualifies']]
    chosen = sorted({x['variant'] for x in qualifications})
    optimizers = []
    for path in sorted(output.glob('MODEL_*.json')):
        optimizers.extend(atlas.optimizer_rows(launcher.json_file(path)))
    # Only summaries, not per-game arrays or original tape fields.
    result = dict(schema='FEATURE_PANEL_ATLAS_SCREEN_V1', category=receipt['category'],
        status='SCREEN_ONLY_NOT_FULL_CADENCE_PROOF', receipt_sha256=launcher.digest(output/'FEATURE_PANEL_RECEIPT.json'),
        cadence='GATE-SIM', full_universe=receipt['eligible_games'],
        rows=[x for x in rows if x['month'] is None],
        filed_primary_and_holdout=filed, selection_cells=selection,
        advancement=dict(variants=chosen, evidence=qualifications,
            rule='Filed n/strict-win criterion, per side/gate/target; selection excludes June completely',
            june_may_select=False, full_receipt_two_pass_proof_required=True),
        conduct_gate_sim=board['all_receipts'].get('conduct'),
        optimizer_outcomes=optimizers)
    bench.write_json(output/'ATLAS_SCREEN_RESULTS.json', result)
    bench.write_json(output/'OPTIMIZER_OUTCOMES.json', optimizers)
    return result


def run(args):
    if args.workers != 1:
        raise ValueError('ATLAS_SCREEN_SINGLE_COORDINATOR_REQUIRED; the gate cache is shared in one process')
    source_scope = hashlib.sha256(json.dumps({
        key: launcher.digest(getattr(args,key)) for key in ('source_receipt','supplemental_receipt')},
        sort_keys=True).encode()).hexdigest()
    original_verify, original_run, original_evaluate = launcher.verify_inputs, bench.run_category, bench.evaluate_query
    selection_holder = {}

    def verify(*params, **kwargs):
        paths, registry, source, supplemental = original_verify(*params, **kwargs)
        registry['atlas_screen'] = dict(cadence='GATE-SIM', all_queries=True,
            gate_source='bound organ_contract.gates_minutes_to_bell; no observed-grid additions',
            june='frozen weights/scales/library; no June outcomes in selection',
            source_scope=source_scope, exact_state_cache=True,
            optimizer='original fit plus numerical Newton polish when stalled; unchanged CRPS and gradient tolerance',
            code={name:launcher.digest(args.root/'arb-executor/analysis'/name) for name in ATLAS_FILES})
        return paths, registry, source, supplemental

    def evaluate(query, *params, **kwargs):
        if kwargs.get('stream')=='PRIMARY' and query.date[:7] not in launcher.HELDOUT_MONTHS:
            kwargs['filed_gate_scorer'] = SelectionTee(kwargs['filed_gate_scorer'], selection_holder['scorer'])
        return original_evaluate(query, *params, **kwargs)

    def category(pairs, sampler, baseline, conduct, category, output, **kwargs):
        variants = [v.name for v in bench.variant_registry(bench.panel.BLOCKS)]
        selection_holder['scorer'] = scoring.FeaturePanelScorer(baseline,variants,
            groupings=(('category','stream','side','gate'),), identity_mode='contiguous_event',
            common_variant_metrics=False, metric_profile='core',
            authorization_streams=('NON_JUNE_SELECTION_FILED_SCORABLE_GATES',))
        # The separate selection accumulator must not be silently lost on a
        # partial resume. Models can be imported, but screen scores restart.
        if kwargs.get('checkpoint_store') is not None:
            raise ValueError('SCREEN_SCORE_RESUME_NOT_SUPPORTED; restart cheap atlas evaluation')
        receipt, board = original_run(pairs,sampler,baseline,conduct,category,output,**kwargs)
        board['selection_filed_scorable_gates'] = selection_holder['scorer'].finish()
        bench.write_json(Path(output)/'FEATURE_PANEL_SCOREBOARD.json',board)
        receipt['outputs']['FEATURE_PANEL_SCOREBOARD.json'] = dict(
            sha256=launcher.digest(Path(output)/'FEATURE_PANEL_SCOREBOARD.json'),
            bytes=(Path(output)/'FEATURE_PANEL_SCOREBOARD.json').stat().st_size)
        receipt.update(evaluation_cadence='GATE-SIM', screen_only=True,
            advancement_selection='PRIMARY excluding June; June holdout is reporting-only',
            member_feature_cache=sampler.state_cache.receipt())
        bench.write_json(Path(output)/'FEATURE_PANEL_RECEIPT.json',receipt)
        return receipt,board

    with atlas.adapter(source_scope,args.state_cache_mib*1024*1024), \
         patch.object(launcher,'verify_inputs',verify), \
         patch.object(bench,'run_category',category), patch.object(bench,'evaluate_query',evaluate):
        launcher.run(args)
    result = summaries(args.out)
    print('SCREEN_COMPLETE '+json.dumps(dict(category=result['category'],games=result['full_universe'],
        advancing=result['advancement']['variants'],output=str(args.out))),flush=True)
    return result


def main():
    parser = launcher.parser()
    parser.description = __doc__
    parser.add_argument('--state-cache-mib', type=int, required=True, help='Execution-only exact feature-state cache budget')
    args = parser.parse_args()
    if args.checkpoint_dir or args.resume or args.import_models:
        parser.error('Atlas screen fits repaired models afresh; do not mix full-run checkpoints/models')
    run(args)


if __name__=='__main__':
    main()
