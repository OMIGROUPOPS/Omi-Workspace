"""Exact two-pass atlas verification with validated runtime-hash dependencies.

No scientific fields are dropped. The existing elapsed-runtime exclusion also
changes the raw receipt SHA in the atlas summary; verify that link first, then
replace it with the canonical receipt SHA. Source files are never rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import feature_panel_run as launcher


RECEIPT = 'FEATURE_PANEL_RECEIPT.json'
SUMMARY = 'ATLAS_SCREEN_RESULTS.json'


def canonical_files(directory):
    directory = Path(directory)
    files = {p.relative_to(directory).as_posix(): p
             for p in directory.rglob('*') if p.is_file()}
    if not {RECEIPT, SUMMARY}.issubset(files):
        raise ValueError('COMPLETE_ATLAS_RECEIPT_AND_SUMMARY_REQUIRED')
    receipt = launcher.json_file(files[RECEIPT])
    if receipt.get('evaluation_cadence') != 'GATE-SIM' or receipt.get('screen_only') is not True:
        raise ValueError('NOT_AN_ATLAS_SCREEN')
    canonical_receipt = launcher.canonical_report(receipt, RECEIPT)
    canonical_receipt_sha = hashlib.sha256(canonical_receipt).hexdigest()
    raw_receipt_sha = launcher.digest(files[RECEIPT])
    result = {}
    raw = {}
    for name, path in sorted(files.items()):
        raw[name] = launcher.digest(path)
        if path.suffix == '.json':
            value = launcher.json_file(path)
            if name == SUMMARY:
                if value.get('receipt_sha256') != raw_receipt_sha:
                    raise ValueError('ATLAS_RECEIPT_HASH_LINK_MISMATCH')
                value['receipt_sha256'] = canonical_receipt_sha
            data = launcher.canonical_report(value, Path(name).name)
            result[name] = hashlib.sha256(data).hexdigest()
        else:
            # Large private arrays remain binary exact, with no normalization.
            result[name] = raw[name]
    return result, raw


def compare(first, second):
    left, raw_left = canonical_files(first)
    right, raw_right = canonical_files(second)
    if set(left) != set(right):
        raise ValueError('DETERMINISM_FILE_SET_MISMATCH')
    for name in left:
        if left[name] != right[name]:
            raise ValueError('DETERMINISM_CONTENT_MISMATCH:' + name)
    return dict(schema='FEATURE_INVENTORY_ATLAS_DETERMINISM_V1', status='DETERMINISTIC',
        files=len(left), canonical_sha256s=left,
        pass1_raw_sha256s=raw_left, pass2_raw_sha256s=raw_right,
        excluded_only={name: ['.'.join(p) for p in paths]
                       for name, paths in launcher.WALL_CLOCK_PATHS.items()},
        validated_hash_dependencies={SUMMARY + ':receipt_sha256':
            'Raw receipt SHA validated per pass, then replaced by canonical receipt SHA'},
        scientific_fields='All clocks, prices, weights, inputs, model outcomes and scores retained exactly')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first', type=Path, required=True)
    parser.add_argument('--second', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compare(args.first, args.second), sort_keys=True))


if __name__ == '__main__':
    main()
