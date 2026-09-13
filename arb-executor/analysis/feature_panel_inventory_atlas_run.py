"""Amended eleven-block atlas launcher; no engine change or raw publication."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import feature_panel_atlas_run as screen
import feature_panel_inventory_atlas as inventory
import feature_panel_run as launcher


CODE_FILES = ('feature_panel_inventory_atlas.py', 'feature_panel_inventory_atlas_run.py',
              'feature_panel_inventory_features.py', 'feature_panel_book_recovery.py')


def run(args):
    args.root = args.root.resolve(strict=True)
    baseline, _, _ = launcher.bind_baseline(args.root, args.category)
    inputs = inventory.GateInputs.read(args.inventory_gates, args.inventory_receipt,
        baseline['organ_contract'], baseline['input_library']['sha256'])
    if args.category not in inputs.receipt['categories']:
        raise ValueError('INVENTORY_CATEGORY_NOT_VERIFIED')
    source_scope = launcher.digest(args.inventory_receipt)
    original_verify = launcher.verify_inputs

    def verify(*params, **kwargs):
        paths, registry, source, supplemental = original_verify(*params, **kwargs)
        registry['amended_inventory'] = dict(
            schema='FEATURE_PANEL_INVENTORY_ATLAS_V2',
            inputs=launcher.check_file(args.inventory_gates, inputs.receipt['output'], 'inventory gates'),
            receipt_sha256=source_scope, receipt=inputs.receipt,
            blocks=list(inventory.BLOCKS), arithmetic_is_diagnostic_only=True,
            reference_queue='unchanged FIRST Q for each query/member, same active library freeze; no candidate-model Q',
            queue_cache_key=['source receipt sha', 'member library event/span sha', 'event', 'exact float64 gate', 'span sha'],
            fit_and_criterion='Inherited atlas nested walk-forward, repaired optimizer, filed matched criterion unchanged',
            code={name: launcher.digest(args.root/'arb-executor/analysis'/name) for name in CODE_FILES})
        return paths, registry, source, supplemental

    with inventory.adapter(inputs, source_scope), patch.object(launcher, 'verify_inputs', verify):
        return launcher.run(args) if args.verify_only else screen.run(args)


def main():
    parser = launcher.parser()
    parser.description = __doc__
    parser.add_argument('--state-cache-mib', type=int, required=True)
    parser.add_argument('--inventory-gates', type=Path, required=True)
    parser.add_argument('--inventory-receipt', type=Path, required=True)
    args = parser.parse_args()
    if args.checkpoint_dir or args.resume or args.import_models:
        parser.error('Eleven-block screen does not import old six-block models/scores')
    run(args)


if __name__ == '__main__':
    main()
