"""Resumable eleven-block source recovery, derived private outputs only.

Reads the sealed, cutter-deduplicated two-tour spool and ETag-verified original
objects. It does not open the live store, send orders, mutate source objects,
or import any OS. The original extractor's span/count/volume checks are reused.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import signal
import sqlite3
import time
from types import SimpleNamespace

from feature_panel_taker_recovery import (arithmetic_aggressor, preceding_book,
    unique_identity_matches, authoritative_direction, same_second_quote_change)
from feature_panel_public_trades import PublicTrades


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            digest.update(part)
    return digest.hexdigest()


def atomic_json(path, value):
    partial = path.with_suffix(path.suffix + '.partial.' + str(os.getpid()))
    with partial.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':'), allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    partial.replace(path)


def write_gzip(path, value):
    partial = path.with_suffix('.partial.' + str(os.getpid()))
    with partial.open('xb') as stream:
        with gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=0) as zipped:
            zipped.write(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())
        stream.flush()
        os.fsync(stream.fileno())
    partial.replace(path)
    return dict(name=path.name, sha256=sha(path), bytes=path.stat().st_size)


def load_core(path):
    spec = importlib.util.spec_from_file_location('inventory_bound_source_core', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tune_event(event):
    stamp = re.search(r'-(\d{2}[A-Z]{3}\d{2})', event)
    if stamp is None:
        raise ValueError('UNPARSEABLE_EVENT_NAME_DATE')
    date = datetime.strptime(stamp[1], '%y%b%d')
    return date.month == 7 and 11 <= date.day <= 21


def sealed_rows(connection, ticker, *, joined, before, after, removed):
    """Spool already applied the pinned cutter; never deduplicate it again."""
    yield from connection.execute('SELECT * FROM prints WHERE ticker=? AND ts>=? AND ts<? '
                                  'ORDER BY CAST(ts AS INTEGER),rowid', (ticker, after, before))


@contextmanager
def expanded_sources(core, collected):
    original_book, original_attach = core.book_from_source, core.attach_takers

    def book(raw, ordinal, obj, parsed_epoch=None):
        row = original_book(raw, ordinal, obj, parsed_epoch)
        for plural, singular in (('bids', 'bid'), ('asks', 'ask')):
            row[plural] = [[core.finite(raw.get(f'{singular}_{i}')),
                            core.finite(raw.get(f'{singular}_{i}_sz'))] for i in range(1, 6)]
        return row

    def attach(*args, **kwargs):
        result = original_attach(*args, **kwargs)
        collected.extend(result)
        return result

    core.book_from_source, core.attach_takers = book, attach
    try:
        yield
    finally:
        core.book_from_source, core.attach_takers = original_book, original_attach


def reusable_checkpoint(folder, leg, inputs):
    """Reuse only hash-verified original-book facts; never reuse old flow labels."""
    if folder is None:
        return None
    key = hashlib.sha256(leg['ticker'].encode()).hexdigest()
    marker, target = folder/'parts'/(key+'.ready.json'), folder/'parts'/(key+'.json.gz')
    if not marker.exists():
        return None
    proof = json.loads(marker.read_text())
    if proof.get('ticker') != leg['ticker'] or proof.get('binding', {}).get('inputs') != inputs:
        raise ValueError('REUSED_CHECKPOINT_INPUT_BINDING_MISMATCH')
    if target.name != proof['file']['name'] or sha(target) != proof['file']['sha256']:
        raise ValueError('REUSED_CHECKPOINT_HASH_MISMATCH')
    with gzip.open(target, 'rt') as stream:
        old = json.load(stream)
    if any(old.get(key) != leg[key] for key in ('event_id', 'ticker', 'category', 'leg_id', 'formation_end_epoch', 'bell_epoch')):
        raise ValueError('REUSED_CHECKPOINT_SPAN_MISMATCH')
    old['reused_source_checkpoint'] = dict(file=proof['file'], binding=proof['binding'])
    return old


def recover(core, connection, leg, client, api, reused=None):
    collected = []
    if reused is None:
        with expanded_sources(core, collected):
            panel, witnesses = core.extract_leg(connection, leg,
                SimpleNamespace(accepted_print_rows=sealed_rows, tune_named_event=tune_event), client)
        positive_witness_count = len(witnesses['positive_prints'])
    else:
        collected = [dict(row) for row in sealed_rows(connection, leg['ticker'], joined=False,
            before=leg['bell_epoch'], after=leg['formation_end_epoch'], removed=Counter())]
        if any(row['event'] != leg['event_id'] or row.get('src_role') == 'TUNE_SAMPLE' for row in collected):
            raise ValueError('REUSED_CHECKPOINT_SOURCE_IDENTITY_ERROR')
        checks = core.verify_library(leg, collected)
        previous = {row['rowid']: row for row in reused['takers']}
        positive_ids = {row['rowid'] for row in collected if row['size'] > 0}
        if len(previous) != len(reused['takers']) or positive_ids != set(previous):
            raise ValueError('REUSED_CHECKPOINT_POSITIVE_ROWIDS_MISMATCH')
        for row in collected:
            old = previous.get(row['rowid'], {})
            row.update(taker_side=old.get('observed_side'), trade_id=old.get('trade_id'))
        panel = dict(reused, checks=checks, books=[dict(source_epoch=row[0],bids=row[1],asks=row[2]) for row in reused['books']])
        positive_witness_count = len(positive_ids)
    positives = [dict(row, ticker=leg['ticker']) for row in collected if row['size'] > 0]
    books = panel['books']
    book_epochs = [book['source_epoch'] for book in books]
    counts = Counter(positive_prints=len(positives))
    for row in positives:
        book = preceding_book(books, book_epochs, row['ts'])
        if book is None:
            result = dict(side=None, reason='NO_PRIOR_COMPLETED_BOOK_SECOND')
        else:
            bid, bid_size = book['bids'][0]
            ask, ask_size = book['asks'][0]
            if bid_size is None or ask_size is None or bid_size <= 0 or ask_size <= 0:
                result = dict(side=None, reason='MISSING_POSITIVE_TWO_SIDED_SIZE')
            else:
                result = arithmetic_aggressor(row['price'], bid, ask)
        row['arithmetic_side'], row['arithmetic_reason'] = result['side'], result['reason']
        row.update(same_second_quote_change(books, book_epochs, row['ts']))
        counts['arithmetic:' + result['reason']] += 1
        counts['observed_before'] += row.get('taker_side') in ('yes', 'no')
        counts['arithmetic_resolved'] += result['side'] is not None
        if row.get('taker_side') in ('yes', 'no') and result['side'] is not None:
            counts['arithmetic_vs_original_compared'] += 1
            counts['arithmetic_vs_original_agree'] += result['side'] == row['taker_side']
    # Arithmetic agreement cannot establish authoritative direction or whether
    # a trade was on-book. Fetch every accepted positive print's exact API label.
    api_rows, api_proofs = api.matching(positives)
    matches = unique_identity_matches(positives, api_rows)
    sidecar = []
    for row, match in zip(positives, matches):
        observed, arithmetic = row.get('taker_side'), row['arithmetic_side']
        decision = authoritative_direction(match)
        recovered = decision['side']
        if arithmetic is not None and recovered is not None:
            counts['arithmetic_vs_api_compared'] += 1
            counts['arithmetic_vs_api_agree'] += arithmetic == recovered
        if observed is not None and recovered is not None:
            counts['original_vs_api_compared'] += 1
            counts['original_vs_api_agree'] += observed == recovered
        side, basis = decision['side'], decision['basis']
        counts['after:' + basis] += 1
        counts['resolved_after'] += side is not None
        block = match.get('is_block_trade')
        counts['offbook_excluded'] += block is True
        counts['confirmed_onbook_positive_prints'] += block is False
        counts['unknown_block_status_positive_prints'] += block is None
        coverage = 'API' if decision['direction_authoritative'] else 'arithmetic-only' if arithmetic is not None else 'unresolved'
        if block is not True:
            counts['label_coverage:' + coverage] += 1
        counts['same_second_quote_changed'] += row['top_quote_changed_in_print_second'] is True
        sidecar.append(dict(rowid=row['rowid'], second=math.floor(row['ts']),
            trade_id=match['trade_id'], fetched_at=match.get('fetched_at'),
            observed_side=observed, arithmetic_side=arithmetic,
            arithmetic_reason=row['arithmetic_reason'], arithmetic_status='ESTIMATE_NOT_FLOW_INPUT',
            arithmetic_available_epoch=math.floor(row['ts'])+1,
            **{key:row[key] for key in ('top_quote_changed_in_print_second','top_quote_change_available_epoch','top_quote_change_scope')},
            api_side=match.get('taker_side'), taker_outcome_side=match.get('taker_outcome_side'),
            taker_book_side=match.get('taker_book_side'), is_block_trade=block,
            api_direction_status=match.get('direction_status'),
            api_identity_status=match['status'], **decision))
        row.update(taker_side=side, taker_status=basis, is_block_trade=block)
    if sum(counts['label_coverage:'+kind] for kind in ('API','arithmetic-only','unresolved')) + counts['offbook_excluded'] != counts['positive_prints']:
        raise ValueError('RECOVERY_EXCLUSIVE_COVERAGE_DENOMINATOR_MISMATCH')
    lookup = {r['rowid']: r for r in positives}
    enriched = [lookup.get(r['rowid'], r) for r in collected]
    # Preserve library count/path witnesses; only new flow calculations exclude
    # confirmed off-book trades. Unknown block/direction makes a minute missing.
    minutes = core.minute_features(leg, [row for row in enriched if row.get('is_block_trade') is not True], books)
    # Private derived sidecar; raw API payloads, unrelated trades and raw object
    # CSV/JSON lines are not saved. Source identity and response hashes remain.
    base = {key: leg[key] for key in ('event_id', 'category', 'leg_id', 'ticker', 'formation_end_epoch', 'bell_epoch')}
    output = dict(base, schema='FEATURE_INVENTORY_RECOVERY_V3_AUTHORITATIVE_API', counts=dict(counts), checks=panel['checks'],
        excluded_unverified_objects=panel['excluded_unverified_objects'], source_manifest=panel['source_manifest'],
        book_columns=['second', 'bids', 'asks'],
        books=[[b['source_epoch'], b['bids'], b['asks']] for b in books],
        book_observation_epochs=panel.get('book_observation_epochs'),
        book_observation_status='STORED' if panel.get('book_observation_epochs') is not None else 'REQUIRES_VERIFIED_V1_OBSERVATION_JOIN; legacy recovery omitted unchanged refreshes',
        minute_columns=['available_epoch', 'taker_flow_contracts', 'taker_yes_contracts', 'taker_no_contracts',
                        'known_taker_positive_print_count', 'positive_size_trade_count'],
        minutes=[[r[k] for k in ('available_epoch', 'taker_flow_contracts', 'taker_yes_contracts',
            'taker_no_contracts', 'known_taker_positive_print_count', 'positive_size_trade_count')]
            for r in minutes if r['positive_size_trade_count']],
        takers=sidecar, api_proofs=api_proofs,
        reused_source_checkpoint=panel.get('reused_source_checkpoint'))
    if len(sidecar) != positive_witness_count:
        raise ValueError('RECOVERY_POSITIVE_WITNESS_COUNT_MISMATCH')
    return output


def run(args):
    args.out.mkdir(parents=True, exist_ok=True)
    parts = args.out/'parts'
    parts.mkdir(exist_ok=True)
    source_receipt = json.loads(args.source_receipt.read_text())
    pins = source_receipt['checkpoint_binding']
    actual = dict(extractor_sha256=sha(args.core), library_sha256=sha(args.library),
                  source_spool_sha256=sha(args.spool))
    if actual != pins:
        raise ValueError('SEALED_INPUT_PINS_DO_NOT_MATCH_V1_RECEIPT')
    core = load_core(args.core)
    binding = dict(inputs=actual, source_receipt_sha256=sha(args.source_receipt),
        code={p.name:sha(p) for p in (Path(__file__), Path(__file__).with_name('feature_panel_taker_recovery.py'),
                                    Path(__file__).with_name('feature_panel_public_trades.py'))})
    args_binding = dict(pause_seconds=args.pause_seconds, page_limit=args.page_limit,
        retry_limit=args.retry_limit, timeout=args.timeout, limit_legs=args.limit_legs)
    binding['transport'] = args_binding
    if args.reuse_recovery is not None and args.reuse_recovery.resolve() == args.out.resolve():
        raise ValueError('REUSE_INPUT_MUST_DIFFER_FROM_VERSIONED_OUTPUT')
    binding['reuse_recovery'] = str(args.reuse_recovery) if args.reuse_recovery else None
    connection = sqlite3.connect('file:'+str(args.spool)+'?mode=ro&immutable=1', uri=True)
    connection.row_factory = sqlite3.Row
    client = core.SpacesClient(core.spaces_environment(args.repo))
    api = PublicTrades(args.pause_seconds, args.page_limit, args.retry_limit, args.timeout)
    total = source_receipt['counts']['legs']
    if args.limit_legs is not None:
        total = min(total, args.limit_legs)
    # Re-open stream per sequential read, not full library paths in RAM.
    started, completed, cells = time.monotonic(), [], defaultdict(Counter)
    stop_requested = []
    def checkpoint_stop(signum, frame):
        stop_requested.append(signum)
    previous_signal_handler = signal.signal(signal.SIGTERM, checkpoint_stop)
    def state(status, **extra):
        atomic_json(args.out/'RUN_STATE.json', dict(status=status, pid=os.getpid(),
            completed_legs=len(completed), total_legs=total, elapsed_seconds=time.monotonic()-started,
            requests_this_process=api.requests, binding=binding, **extra))
    state('RUNNING')
    try:
        with gzip.open(args.library, 'rt') as stream:
            for line in stream:
                leg = json.loads(line)
                if leg['category'] not in ('ATP_MAIN', 'ATP_CHALL'):
                    continue
                if len(completed) == total:
                    break
                if tune_event(leg['event_id']):
                    raise ValueError('TUNE_EVENT_IN_LIBRARY')
                key = hashlib.sha256(leg['ticker'].encode()).hexdigest()
                marker, target = parts/(key+'.ready.json'), parts/(key+'.json.gz')
                if marker.exists():
                    proof = json.loads(marker.read_text())
                    if proof['binding'] != binding or sha(target) != proof['file']['sha256']:
                        raise ValueError('RECOVERY_CHECKPOINT_HASH_OR_BINDING_MISMATCH')
                    counts = proof['counts']
                    resumed = True
                else:
                    state('RUNNING', current_ticker=leg['ticker'])
                    reused = reusable_checkpoint(args.reuse_recovery, leg, actual)
                    result = recover(core, connection, leg, client, api, reused=reused)
                    proof = dict(ticker=leg['ticker'], binding=binding, file=write_gzip(target,result), counts=result['counts'])
                    atomic_json(marker, proof)
                    counts, resumed = result['counts'], False
                completed.append(dict(ticker=leg['ticker'], **proof['file']))
                stamp = re.search(r'-(\d{2}[A-Z]{3}\d{2})',leg['event_id'])[1]
                month = datetime.strptime(stamp,'%y%b%d').strftime('%Y-%m')
                cells[(leg['category'],month)].update(counts)
                elapsed = time.monotonic()-started
                print('RECOVERY_PROGRESS '+json.dumps(dict(legs_done=len(completed), legs_total=total,
                    ticker=leg['ticker'], resumed=resumed, elapsed_seconds=elapsed,
                    rate_legs_per_second=len(completed)/elapsed,
                    eta_seconds=(total-len(completed))*elapsed/len(completed),
                    positive_prints=sum(c['positive_prints'] for c in cells.values()))),flush=True)
                if stop_requested or (args.out/'STOP_AFTER_LEG').exists():
                    state('STOPPED_AT_VERIFIED_LEG_CHECKPOINT', stop_signals=stop_requested)
                    return
        if len(completed) != total:
            raise ValueError('INCOMPLETE_RECOVERY_LEG_COUNT')
        receipt = dict(schema='FEATURE_INVENTORY_RECOVERY_RECEIPT_V3_AUTHORITATIVE_API',
            status='SMOKE_ONLY' if args.limit_legs is not None else 'RECOVERY_COMPLETE_NOT_BENCH_RESULT',
            binding=binding, rows=[dict(category=k[0],month=k[1],**dict(v)) for k,v in sorted(cells.items())],
            parts=completed, api_cutoff=api.cutoff, api_cutoff_proof=api.cutoff_proof,
            source_store='NOT_OPENED; sealed cutter-deduplicated spool with original two-hash lock receipt',
            rules=dict(identity='Existing trade_id matched exactly with key consistency; otherwise unique exact ticker, floor(ts), YES cents, size; multiple matches unresolved',
                arithmetic='Last completed book second strictly before print second; separate estimate, never enters authoritative flow. Final-second top-change diagnostic available only next second; intra-second transients invisible.',
                api='Every positive library print queried via ticker/time pages; canonical outcome/book direction, consistent fields, exact identity and is_block_trade=false required. Legacy/original labels telemetry only.',
                offbook='Confirmed block trades excluded from new flow/maker, preserved in unchanged library/witness denominators; unknown block status leaves flow missing.',
                coverage='Exclusive API/arithmetic-only/unresolved among positive prints not confirmed offbook; offbook count and total original positives reported separately.',
                books='All five levels retained; missing/out-of-view is not empty depth',
                span='Exact library formation and bell; tune rows excluded in sealed spool; no rederivation',
                no_raw_upload=True))
        atomic_json(args.out/'RECOVERY_RECEIPT.json',receipt)
        state('RECOVERY_COMPLETE_NOT_BENCH_RESULT')
    except BaseException as error:
        state('FAILED',error_type=type(error).__name__,error=str(error))
        raise
    finally:
        signal.signal(signal.SIGTERM, previous_signal_handler)
        connection.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('library','spool','source-receipt','core','repo','out'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--pause-seconds',type=float,required=True)
    p.add_argument('--page-limit',type=int,required=True)
    p.add_argument('--retry-limit',type=int,required=True)
    p.add_argument('--timeout',type=float,required=True)
    p.add_argument('--limit-legs',type=int)
    p.add_argument('--reuse-recovery',type=Path,help='Prior recovery root; hash-verified books/identities only, all API labels refetched into a distinct output root')
    args = p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    # Linux worker lock is independent of the source store's writer lock: this
    # job reads only the immutable sealed spool, not the current live database.
    import fcntl
    with (args.out/'WORKER.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        code = 1
        try:
            atomic_json(args.out/'RUN_STATE.json',dict(status='VERIFYING_INPUT_HASHES',pid=os.getpid()))
            run(args)
            code = 0
        finally:
            atomic_json(args.out/'RUN.exit',dict(code=code,pid=os.getpid(),
                finished_at=datetime.now(timezone.utc).isoformat()))


if __name__ == '__main__':
    main()
