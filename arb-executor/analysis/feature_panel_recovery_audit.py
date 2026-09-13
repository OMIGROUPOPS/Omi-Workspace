"""Read-only attribution feasibility audit of the pinned v1 private extract.

Writes aggregate counts only, not a recovered feature set or a bench result.
This measures arithmetic attribution independently of API identity recovery.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
from itertools import zip_longest
import json
import math
from pathlib import Path
import re
import time

from feature_panel_taker_recovery import arithmetic_aggressor


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def audit(directory, receipt_path):
    started = time.monotonic()
    receipt = json.loads(receipt_path.read_text())
    bindings = {}
    for name in ('FEATURE_SOURCES.jsonl.gz', 'POSITIVE_PRINT_WITNESSES.jsonl.gz'):
        expected = receipt['outputs'][name]
        path = directory/name
        digest = sha(path)
        if path.stat().st_size != expected['bytes'] or digest != expected['sha256']:
            raise ValueError('PRIVATE_SOURCE_BINDING_MISMATCH:'+name)
        bindings[name] = dict(sha256=digest, bytes=path.stat().st_size)
    cells = defaultdict(Counter)
    total = Counter()
    with gzip.open(directory/'FEATURE_SOURCES.jsonl.gz', 'rt') as features, \
         gzip.open(directory/'POSITIVE_PRINT_WITNESSES.jsonl.gz', 'rt') as witnesses:
        for feature_line, witness_line in zip_longest(features, witnesses):
            if feature_line is None or witness_line is None:
                raise ValueError('SOURCE_WITNESS_LENGTH_MISMATCH')
            source, witness = json.loads(feature_line), json.loads(witness_line)
            for key in ('ticker', 'event_id', 'formation_end_epoch', 'bell_epoch'):
                if source[key] != witness[key]:
                    raise ValueError('SOURCE_WITNESS_IDENTITY_MISMATCH:'+key)
            match = re.search(r'-(\d{2}[A-Z]{3}\d{2})', source['event_id'])
            date = datetime.strptime(match[1], '%y%b%d')
            if date.month == 7 and 11 <= date.day <= 21:
                raise ValueError('TUNE_EVENT_FORBIDDEN')
            cell = cells[(source['category'], date.strftime('%Y-%m'))]
            cell['legs'] += 1
            rows = witness['positive_prints']
            cell['positive_prints'] += len(rows)
            cell['v1_completed_minute_known_aggressors'] += sum(
                row['known_taker_positive_print_count'] for row in source['minute_features'])
            cell['v1_completed_minute_positive_prints'] += sum(
                row['positive_size_trade_count'] for row in source['minute_features'])
            books = source['books']
            if any(a['source_epoch'] > b['source_epoch'] for a,b in zip(books,books[1:])):
                raise ValueError('UNSORTED_BOOK_STATES')
            book_index = -1
            for epoch, price, size, rowid, origin in rows:
                if not source['formation_end_epoch'] <= epoch < source['bell_epoch'] or size <= 0:
                    raise ValueError('INVALID_POSITIVE_PRINT_SPAN_OR_SIZE')
                second = math.floor(epoch)
                while book_index+1 < len(books) and books[book_index+1]['source_epoch'] < second:
                    book_index += 1
                cell['source:'+origin] += 1
                if book_index < 0:
                    result = dict(side=None, reason='NO_PRIOR_COMPLETED_BOOK_SECOND')
                else:
                    book = books[book_index]
                    bid, bid_size = book['bids'][0]
                    ask, ask_size = book['asks'][0]
                    if bid_size is None or ask_size is None or bid_size <= 0 or ask_size <= 0:
                        result = dict(side=None, reason='MISSING_POSITIVE_TWO_SIDED_SIZE')
                    else:
                        result = arithmetic_aggressor(price, bid, ask)
                cell['arithmetic:'+result['reason']] += 1
                if result['side'] is not None:
                    cell['arithmetic_resolved'] += 1
                    cell['arithmetic_resolved:'+origin] += 1
                else:
                    cell['arithmetic_ambiguous'] += 1
                    cell['arithmetic_ambiguous:'+origin] += 1
            total['legs'] += 1
            total['positive_prints'] += len(rows)
            if total['legs'] % 250 == 0:
                print('AUDIT_PROGRESS '+json.dumps(dict(total, elapsed_seconds=time.monotonic()-started)), flush=True)
    return dict(schema='TAKER_RECOVERY_FEASIBILITY_V1', status='AUDIT_ONLY_NOT_RECOVERED_FEATURES',
        inputs=bindings, source_receipt_sha256=sha(receipt_path),
        rule='Last book state strictly before the print second; same-second final book never used. Positive-size prints only. No API request or inferred identity in this audit.',
        before_denominator='v1 completed-minute known count / completed-minute positive count; full print count reported separately so incomplete final minutes are visible',
        arithmetic_label='ESTIMATED, not observed aggressor; cannot infer complete API recovery from this table',
        rows=[dict(category=key[0], month=key[1], **dict(value)) for key,value in sorted(cells.items())],
        totals=dict(total), elapsed_seconds=time.monotonic()-started)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():
        raise ValueError('REFUSE_EXISTING_AUDIT')
    result=audit(a.directory,a.receipt)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(result,f,indent=2,sort_keys=True)
        f.write('\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
