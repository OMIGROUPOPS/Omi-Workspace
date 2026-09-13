"""Freeze formation-metadata-only reservation; never read forecast targets or fit.

The latest 15% is historically inspected, not fresh. Existing published
per-query hash manifests define the unchanged 928/2287 query universes.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def freeze(root, out):
    library = root/'arb-executor/data/durable/RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz'
    prior = root/'arb-executor/analysis/feature_panel_inventory_v2'
    universes, pins = {}, {}
    for category in ('ATP_MAIN', 'ATP_CHALL'):
        path = prior/category/'ATLAS_SCREEN_RECEIPT.json'
        receipt = json.loads(path.read_text(encoding='utf-8'))
        files = receipt['population_determinism']['canonical_sha256s']
        universes[category] = {name.split('/')[-1].removesuffix('__PRIMARY.npz')
            for name in files if name.startswith('receipt_diagnostics/') and name.endswith('__PRIMARY.npz')}
        if receipt['population_determinism']['status'] != 'DETERMINISTIC':
            raise ValueError('UNVERIFIED_POPULATION')
        pins[category] = dict(path=str(path.relative_to(root)), sha256=sha(path))
    metadata = defaultdict(dict)
    with gzip.open(library, 'rt') as stream:
        for line in stream:
            # The input file contains paths; only identity and span metadata
            # are used here. No path values, target or score is inspected.
            leg = json.loads(line)
            category, event = leg['category'], leg['event_id']
            if category not in universes or event not in universes[category]:
                continue
            row = metadata[category].setdefault(event, dict(event_id=event, category=category,
                formation_epoch=leg['formation_end_epoch'], bell_epoch=leg['bell_epoch']))
            row['formation_epoch'] = max(row['formation_epoch'], leg['formation_end_epoch'])
            if row['bell_epoch'] != leg['bell_epoch']:
                raise ValueError('PAIR_BELL_MISMATCH')
    result = dict(schema='ABSORPTION_RESIDUAL_RESERVATION_V1',
        frozen_at=datetime.now(timezone.utc).isoformat(), label='historically inspected — not fresh',
        selection='Latest ceil(15% * query games) by pair formation_epoch, event_id ascending tie break, separately per tour; metadata only',
        previous_exposure='All reserved games already scored in the verified full-universe eleven-block screen',
        fresh_confirmation='DEFERRED to LIVE_PAPER cohort after DESK activation; no fresh-confirmation claim from this reserve',
        library_sha256=sha(library), previous_receipts=pins, categories={})
    for category, rows in metadata.items():
        ordered = sorted(rows.values(), key=lambda r: (r['formation_epoch'], r['event_id']))
        if len(ordered) != len(universes[category]):
            raise ValueError('RESERVATION_UNIVERSE_MISMATCH')
        n = math.ceil(len(ordered)*.15)
        development, reserved = ordered[:-n], ordered[-n:]
        result['categories'][category] = dict(eligible_games=len(ordered), development_games=len(development),
            reserved_games=n, confirmation_cutoff=reserved[0]['formation_epoch'],
            development=development, reserved=reserved,
            member_freeze='Confirmation FIRST and both corrections use only non-reserved member events resolved before confirmation_cutoff; no reserved outcome authors another reserved prediction')
    if out.exists():
        raise ValueError('REFUSE_TO_REPLACE_FROZEN_RESERVATION')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(dict(path=str(out), sha256=sha(out), categories={cat:
        {k: v for k, v in row.items() if k not in ('development', 'reserved')}
        for cat, row in result['categories'].items()}), ensure_ascii=False))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    freeze(args.root, args.out)
