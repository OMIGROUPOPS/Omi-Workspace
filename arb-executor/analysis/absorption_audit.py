"""Consumed-level absorption audit only: no learner, engine or live store.

The original eleven-block fields are not changed. This versioned measurement
includes the previous best quote and only adds numerator mass at consumed
levels. Source/API custody and conservative second-boundary rules are retained.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import gzip
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import time

from feature_panel_book_recovery import book_invalid_reason, visible_depth
from feature_panel_inventory_gate_extract import checkpoint, digest, encoded
from feature_panel_taker_recovery import decimal


STATES = ('MEASURED', 'UNOBSERVED', 'ZERO_DENOMINATOR')


def prepare_book(book):
    # Execution-only fast path for JSON numeric captures. Convert the two
    # selected tops to Decimal once, not every unchanged level repeatedly.
    # Decimal/string/non-numeric inputs retain the reference implementation.
    numeric = all(v is None or (isinstance(v, (int, float)) and not isinstance(v, bool))
                  for levels in book[1:3] for row in levels for v in row)
    if numeric:
        sides = [[p for p, q in levels if p is not None and q is not None
                  and math.isfinite(p) and math.isfinite(q) and q > 0] for levels in book[1:3]]
        top = {'bid': decimal(max(sides[0])) if sides[0] else None,
               'ask': decimal(min(sides[1])) if sides[1] else None}
        reason = ('NO_TWO_SIDED_VISIBLE_CAPTURE' if not all(sides) else
                  'LOCKED_OR_CROSSED_CAPTURE' if top['bid'] >= top['ask'] else None)
        return dict(raw=book, reason=reason, top=top)
    return dict(raw=book, reason=book_invalid_reason(book), top={side:
        (max if side == 'bid' else min)([decimal(p) for p, q in book[i]
            if decimal(p) is not None and decimal(q) is not None and decimal(q) > 0], default=None)
        for i, side in ((1, 'bid'), (2, 'ask'))})


def audit_interval(previous, current, start, end, prints, *, formation, bell):
    """Every book-side interval gets exactly one state; no partial aggregate.

    Captures are final observed states per second, not exchange-sequenced
    snapshots. End-second data is known only at end+1; that availability must
    precede bell. Boundary-second executions remain unallocated. No changed
    state is substituted for an actual observation.
    """
    if end <= start:
        raise ValueError('NONINCREASING_OBSERVATION_INTERVAL')
    cutoff = math.floor(end) + 1
    global_reason = ('CROSSES_FORMATION' if start < formation else
                     'NOT_AVAILABLE_BEFORE_BELL' if cutoff >= bell else
                     previous['reason'] or current['reason'])
    executions = defaultdict(Decimal)
    unknown = defaultdict(set)
    accepted, excluded = Counter(), Counter()
    for row in prints:
        if not (math.floor(start) <= math.floor(row['ts']) <= math.floor(end)):
            continue
        if row['ts'] >= cutoff:
            raise ValueError('FUTURE_PRINT_IN_INTERVAL')
        p, size = decimal(row['price']), decimal(row['size'])
        if size is None or size <= 0:
            continue
        if row.get('is_block_trade') is True:
            excluded['OFF_BOOK'] += 1
            continue
        valid = (row.get('direction_authoritative') is True and
                 row.get('is_block_trade') is False)
        side = {'yes': 'ask', 'no': 'bid'}.get(row.get('side')) if valid else None
        reason = ('UNRESOLVED_DIRECTION_OR_BLOCK_STATUS' if side is None else
                  'BOUNDARY_SECOND_ORDER_UNKNOWN' if math.floor(row['ts']) in
                  (math.floor(start), math.floor(end)) else
                  'INTERVAL_ORDER_UNKNOWN' if row.get('interval_ordering_unresolved') else None)
        if p is None:
            reason = 'MISSING_EXECUTION_PRICE'
        if reason:
            for target in (side,) if side else ('bid', 'ask'):
                unknown[target].add(reason)
            continue
        executions[(side, p)] += size
        accepted[side] += 1
    outputs = []
    for i, side in ((1, 'bid'), (2, 'ask')):
        reasons = set(unknown[side])
        if global_reason:
            reasons.add(global_reason)
        levels = []
        for (s, price), executed in sorted(executions.items()):
            if s != side:
                continue
            before = visible_depth(previous['raw'][i], price, side)
            after = visible_depth(current['raw'][i], price, side)
            if before is None or after is None:
                reasons.add('CONSUMED_LEVEL_NOT_VISIBLE_AT_BOTH_SNAPSHOTS')
                levels.append(dict(side=side, level=float(price), executed=float(executed),
                                   status='UNOBSERVED', was_best=price == previous['top'][side]))
                continue
            net = after - before + executed
            # Accounting identity, not independent evidence of gross adds or
            # cancellations. Source/API hash/identity checks are separate.
            residual_error = after - (before - executed + net)
            if residual_error:
                raise ValueError('UNEXPLAINED_ACCOUNTING_RESIDUAL')
            levels.append(dict(side=side, level=float(price), executed=float(executed),
                               start_size=float(before), end_size=float(after),
                               net_add=float(max(Decimal(0), net)),
                               net_pull=float(max(Decimal(0), -net)),
                               status='MEASURED', was_best=price == previous['top'][side],
                               reconciliation_error=float(residual_error)))
        denom = sum(v['executed'] for v in levels)
        status = 'UNOBSERVED' if reasons else 'MEASURED' if denom > 0 else 'ZERO_DENOMINATOR'
        numerator = sum(v.get('net_add', 0) for v in levels)
        ratio = numerator / denom if status == 'MEASURED' else None
        outputs.append(dict(side=side, start=start, end=end, available_epoch=cutoff,
                            status=status, reasons=sorted(reasons), refill_ratio=ratio,
                            net_add=numerator if status == 'MEASURED' else None,
                            net_pull=sum(v.get('net_pull', 0) for v in levels)
                            if status == 'MEASURED' else None,
                            executed=denom if status != 'UNOBSERVED' else None,
                            accepted_prints=accepted[side], levels=levels))
    return outputs


def atomic_json(path, value):
    temp = path.with_suffix(path.suffix + '.partial')
    temp.write_bytes(encoded(value) + b'\n')
    temp.replace(path)


def leg_audit(leg, recovery, legacy, conn, target):
    observations = recovery.get('book_observation_epochs')
    if observations is None:
        observations = legacy['book_observation_epochs']
    if observations != sorted(set(observations)):
        raise ValueError('OBSERVATIONS_NOT_STRICTLY_ORDERED')
    books = recovery['books']
    epochs = [b[0] for b in books]
    if epochs != sorted(set(epochs)):
        raise ValueError('BOOK_STATES_NOT_STRICTLY_ORDERED')
    accepted = [dict(r) for r in conn.execute(
        'SELECT * FROM prints WHERE ticker=? AND ts>=? AND ts<? ORDER BY ts,rowid',
        (leg['ticker'], leg['formation_end_epoch'], leg['bell_epoch']))]
    if any(r['event'] != leg['event_id'] or r.get('src_role') == 'TUNE_SAMPLE' for r in accepted):
        raise ValueError('SPAN_OR_COHORT_MISMATCH')
    labels = {r['rowid']: r for r in recovery['takers']}
    positive = [r for r in accepted if r['size'] > 0]
    if len(labels) != len(recovery['takers']) or {r['rowid'] for r in positive} != set(labels):
        raise ValueError('POSITIVE_SOURCE_API_IDENTITY_SET_MISMATCH')
    for r in positive:
        r.update(labels[r['rowid']])
    times = [r['ts'] for r in positive]
    counts, reasons, examples = Counter(), Counter(), {}
    prepared = {}
    prior = None
    temp = target.with_suffix('.partial')
    with temp.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as out:
        for end in observations:
            if end < leg['formation_end_epoch']:
                prior = end
                continue
            if end >= leg['bell_epoch']:
                break
            if prior is None:
                counts['NO_PRIOR_SNAPSHOT_OBSERVATIONS'] += 1
                prior = end
                continue
            start, prior = prior, end
            a, b = bisect_right(epochs, start)-1, bisect_right(epochs, end)-1
            if min(a, b) < 0:
                raise ValueError('OBSERVATION_WITHOUT_CAUSAL_BOOK_STATE')
            for index in (a, b):
                if index not in prepared:
                    prepared[index] = prepare_book(books[index])
            sample = positive[bisect_left(times, math.floor(start)):
                              bisect_left(times, math.floor(end)+1)]
            items = audit_interval(prepared[a], prepared[b], start, end, sample,
                                   formation=leg['formation_end_epoch'], bell=leg['bell_epoch'])
            for item in items:
                counts['side_intervals'] += 1
                counts[item['status']] += 1
                counts[item['side']+':'+item['status']] += 1
                reasons.update(item['reasons'])
                if item['status'] == 'MEASURED':
                    counts['measured_consumed_levels'] += len(item['levels'])
                    counts['best_quote_consumed_levels'] += sum(x['was_best'] for x in item['levels'])
                    counts['accounting_identities_checked'] += len(item['levels'])
                    counts['positive_refill_intervals'] += item['refill_ratio'] > 0
                    counts['zero_refill_measured_intervals'] += item['refill_ratio'] == 0
                for reason in item['reasons'] or [item['status']]:
                    examples.setdefault(reason, dict(event=leg['event_id'], ticker=leg['ticker'], **item))
                # Private derived intervals; no raw trade IDs or source records.
                out.write(encoded(item) + b'\n')
    if sum(counts[s] for s in STATES) != counts['side_intervals']:
        raise ValueError('INTERVAL_PARTITION_MISMATCH')
    temp.replace(target)
    return dict(ticker=leg['ticker'], event_id=leg['event_id'], category=leg['category'],
                formation=leg['formation_end_epoch'], bell=leg['bell_epoch'],
                counts=dict(counts), reasons=dict(reasons), examples=examples,
                input_positive_prints=len(positive), no_intervals=not counts['side_intervals'],
                interval_output=dict(name=target.name, bytes=target.stat().st_size, sha256=digest(target)))


def run(args):
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'parts').mkdir(exist_ok=True)
    receipt = json.loads(args.recovery_receipt.read_text())
    inputs = receipt['binding']['inputs']
    if receipt['status'] != 'RECOVERY_COMPLETE_NOT_BENCH_RESULT':
        raise ValueError('COMPLETE_AMENDED_RECOVERY_REQUIRED')
    for path, pin in ((args.library, inputs['library_sha256']), (args.spool, inputs['source_spool_sha256'])):
        if digest(path) != pin:
            raise ValueError('AUDIT_INPUT_HASH_MISMATCH')
    code = {Path(p).name: digest(p) for p in (__file__,
            Path(__file__).with_name('feature_panel_book_recovery.py'),
            Path(__file__).with_name('feature_panel_taker_recovery.py'),
            Path(__file__).with_name('feature_panel_inventory_gate_extract.py'))}
    binding = dict(library_sha256=inputs['library_sha256'], spool_sha256=inputs['source_spool_sha256'],
                   recovery_receipt_sha256=digest(args.recovery_receipt), code=code,
                   minimum_measured_games=args.minimum_measured_games)
    groups, all_games, measured_games = defaultdict(Counter), defaultdict(set), defaultdict(set)
    reasons, examples, completed = Counter(), {}, []
    conn = sqlite3.connect('file:'+str(args.spool)+'?mode=ro&immutable=1', uri=True)
    conn.row_factory = sqlite3.Row
    started = time.monotonic()
    with gzip.open(args.library, 'rt') as stream:
        for line in stream:
            leg = json.loads(line)
            if leg['category'] not in args.categories:
                continue
            key = hashlib.sha256(leg['ticker'].encode()).hexdigest()
            marker, target = args.out/'parts'/(key+'.json'), args.out/'parts'/(key+'.jsonl.gz')
            recovered, proof = checkpoint(args.recovery_parts, leg['ticker'])
            if proof['binding'] != receipt['binding']:
                raise ValueError('RECOVERY_BINDING_MISMATCH')
            old, oldproof = checkpoint(args.legacy_source_parts, leg['ticker'], legacy=True)
            if oldproof['binding'] != inputs:
                raise ValueError('LEGACY_BINDING_MISMATCH')
            for source in (recovered, old):
                for name in ('event_id', 'ticker', 'category', 'formation_end_epoch', 'bell_epoch'):
                    if source[name] != leg[name]:
                        raise ValueError('SOURCE_LIBRARY_SPAN_MISMATCH')
            if marker.exists():
                item = json.loads(marker.read_text())
                if item['binding'] != binding or digest(target) != item['interval_output']['sha256']:
                    raise ValueError('AUDIT_CHECKPOINT_MISMATCH')
            else:
                item = leg_audit(leg, recovered, old, conn, target)
                item['binding'] = binding
                atomic_json(marker, item)
            month = datetime.strptime(leg['event_id'].split('-')[-1][:7], '%y%b%d').strftime('%Y-%m')
            cell = (leg['category'], month)
            groups[cell].update(item['counts'])
            groups[cell]['legs'] += 1
            groups[cell]['legs_without_intervals'] += item['no_intervals']
            all_games[cell].add(leg['event_id'])
            if item['counts'].get('MEASURED', 0):
                measured_games[cell].add(leg['event_id'])
            reasons.update(item['reasons'])
            for reason, sample in item['examples'].items():
                examples.setdefault(reason, sample)
            completed.append(dict(ticker=leg['ticker'], marker_sha256=digest(marker),
                                  intervals_sha256=item['interval_output']['sha256']))
            elapsed = time.monotonic()-started
            state = dict(status='AUDITING', legs_done=len(completed), legs_total=len(receipt['parts']),
                         elapsed_seconds=elapsed, rate_legs_per_second=len(completed)/elapsed,
                         eta_seconds=(len(receipt['parts'])-len(completed))*elapsed/len(completed),
                         ticker=leg['ticker'])
            atomic_json(args.out/'RUN_STATE.json', state)
            print('AUDIT_PROGRESS '+json.dumps(state), flush=True)
            if args.limit_legs and len(completed) >= args.limit_legs:
                break
    conn.close()
    if not args.limit_legs and len(completed) != len(receipt['parts']):
        raise ValueError('INCOMPLETE_AUDIT_POPULATION')
    coverage = [dict(category=k[0], month=k[1], **dict(v),
                     independent_games=len(all_games[k]), games_with_measured_refill=len(measured_games[k]))
                for k, v in sorted(groups.items())]
    bars = {cat: dict(measured_independent_games=len(set().union(
        *(values for (tour, _), values in measured_games.items() if tour == cat))),
        minimum=args.minimum_measured_games) for cat in args.categories}
    for bar in bars.values():
        bar['pass'] = bar['measured_independent_games'] >= bar['minimum']
    result = dict(schema='CONSUMED_LEVEL_ABSORPTION_AUDIT_V1',
        status='SMOKE_ONLY' if args.limit_legs else 'AUDIT_COMPLETE', binding=binding,
        coverage=coverage, bars=bars, unexplained_reconciliation_failures=[],
        unobserved_reasons=dict(reasons), examples=examples, parts=completed,
        source_store='NOT_OPENED; read-only immutable sealed spool and hash-verified recovered captures',
        rules=dict(refill='sum(max(0, end_size-start_size+on_book_execution)) / sum(on_book_execution), at consumed levels only, including prior best; per book side',
            status='MEASURED only if every consumed/potentially-consumed level on that side resolves; measured zero is a value; no known execution denominator is ZERO_DENOMINATOR, never zero refill; otherwise UNOBSERVED',
            interval='Every consecutive actual captured observation in exact library span; no sparse-state substitution. Availability is end second + 1; preformation or not-before-bell intervals unobserved.',
            attribution='Exact API-authoritative, positive-size, explicitly non-block; no arithmetic substitution. Boundary-second order unknown; no interpolation.',
            units='Existing capture-normalized YES cents, no second NO-side inversion',
            visibility='Top-five off-screen is unknown, not zero',
            reconciliation='Exact arithmetic identity + independently hash-checked source/API row identity. Identity alone does not independently verify true gross maker flow.',
            limitation='Net displayed refill only: same-interval additions and cancellations may offset; no individual queue attribution; WS remains deferred',
            month='Event-name month, consistent with preceding coverage report',
            privacy='Only aggregate coverage/receipt published; detailed derived intervals stay private',
            fitting='NONE; audit only'))
    atomic_json(args.out/'ABSORPTION_AUDIT_RECEIPT.json', result)
    atomic_json(args.out/'RUN_STATE.json', dict(status=result['status'], legs_done=len(completed),
                                             elapsed_seconds=time.monotonic()-started, bars=bars))
    print('AUDIT_COMPLETE '+json.dumps(dict(legs=len(completed), coverage=coverage, bars=bars)), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('library', 'spool', 'recovery-receipt', 'recovery-parts', 'legacy-source-parts', 'out'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--categories', nargs='+', choices=('ATP_MAIN', 'ATP_CHALL'), required=True)
    p.add_argument('--minimum-measured-games', type=int, required=True)
    p.add_argument('--limit-legs', type=int)
    args = p.parse_args()
    import fcntl
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out/'WORKER.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        exit_code = 1
        try:
            run(args)
            exit_code = 0
        except BaseException as exc:
            atomic_json(args.out/'RUN_STATE.json', dict(status='FAILED', error=repr(exc)))
            raise
        finally:
            atomic_json(args.out/'RUN.exit', dict(code=exit_code, finished_at=datetime.now(timezone.utc).isoformat()))


if __name__ == '__main__':
    main()
