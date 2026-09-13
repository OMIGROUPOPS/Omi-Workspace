"""Stream amended private recovery into exact atlas-only feature states.

Reads one pair at a time; raw prints/depth never leave the droplet. Queue Q is
deliberately not chosen here: the screen computes unchanged FIRST in its own
primary/training/frozen-June universe. No OS import and no source-store write.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import sqlite3

from feature_panel_inventory_features import NEW_FIELDS, previous_receipt, asof_book, receipt_features
from feature_panel_book_recovery import book_invalid_reason


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def checkpoint(folder, ticker, *, legacy=False):
    key = hashlib.sha256(ticker.encode()).hexdigest()
    marker = folder/(key+'.ready.json')
    proof = json.loads(marker.read_text())
    if proof.get('ticker', ticker) != ticker:
        raise ValueError('CHECKPOINT_TICKER_MISMATCH')
    if legacy:
        # V1 completion markers bind feature and witness files separately.
        files = proof.get('files', {})
        target = folder/(key+'.feature.json.gz')
        candidates = list(files.values()) if isinstance(files, dict) else files
        binding = next((v for v in candidates if isinstance(v, dict) and
                        (v.get('name') == target.name or v.get('path', '').endswith(target.name))), None)
        if binding is None:
            raise ValueError('LEGACY_FEATURE_HASH_BINDING_NOT_FOUND')
    else:
        binding = proof['file']
        target = folder/binding['name']
    if target.parent.resolve() != folder.resolve() or digest(target) != binding['sha256']:
        raise ValueError('RECOVERY_CHECKPOINT_HASH_MISMATCH')
    with gzip.open(target, 'rt') as stream:
        data = json.load(stream)
    if data['ticker'] != ticker:
        raise ValueError('RECOVERY_BODY_TICKER_MISMATCH')
    return data, proof


def epochs_for(leg):
    return [float(p['ts']) for p in leg['path']]


def last_at(leg, epoch):
    if epoch is None:
        return None
    i = bisect_right(leg['_epochs'], epoch)-1
    return leg['path'][i] if i >= 0 else None


def pair_identity(rows, first_seconds):
    if len(rows) != 2 or rows[0]['bell_epoch'] != rows[1]['bell_epoch']:
        return None, 'NOT_TWO_LEGS_COMMON_BELL'
    for row in rows:
        row['_epochs'] = epochs_for(row)
        eligible = [p for p in row['_epochs'] if math.floor(p) >= first_seconds[row['ticker']]]
        if not eligible:
            return None, 'NO_NATIVE_STATE_AFTER_FIRST_PRINT'
        row['_first'] = eligible[0]
    first = max(r['_first'] for r in rows)
    values = [last_at(row, first)['last_cents'] for row in rows]
    if any(v is None or not math.isfinite(float(v)) for v in values):
        return None, 'NO_FIRST_TRUE_TRADE'
    if values[0] == values[1]:
        return None, 'FIRST_TICK_TIE_STORE_SILENT'
    ordered = sorted(rows, key=lambda row: -last_at(row, first)['last_cents'])
    span = dict(event=ordered[0]['event_id'], category=ordered[0]['category'], legs=[dict(
        leg=r['leg_id'], formation=float(r['formation_end_epoch']).hex(),
        bell=float(r['bell_epoch']).hex()) for r in ordered])
    return dict(event_id=span['event'], category=span['category'],
        span_sha256=hashlib.sha256(encoded(span)).hexdigest(), first_epoch=first,
        bell=float(ordered[0]['bell_epoch']), rows=ordered), None


def observation_book(books, book_epochs, observation_epoch):
    state = asof_book(books, book_epochs, observation_epoch)
    return [observation_epoch, state[1], state[2]] if state is not None else None


def side_state(leg, recovery, prints, epoch, previous, seconds):
    """Every feature is at the same exact receipt; no as-of gate rounding."""
    books = recovery['books']
    book_epochs = [r[0] for r in books]
    observations = recovery.get('book_observation_epochs')
    if observations is None:
        raise ValueError('ACTUAL_BOOK_OBSERVATION_EPOCHS_REQUIRED')
    j = bisect_right(observations, epoch)
    current = observation_book(books, book_epochs, observations[j-1]) if j else None
    prior = observation_book(books, book_epochs, observations[j-2]) if j > 1 else None
    if prior is not None and prior[0] < leg['formation_end_epoch']:
        prior = None  # Accepted execution custody starts at formation.
    now, before = last_at(leg, epoch), last_at(leg, previous)
    def val(row, key):
        return row.get(key) if row is not None else None
    # Keep library price grid intact. Only new empirical features exclude
    # confirmed off-book executions; unknown direction remains missing in flow.
    positive = [[r['ts'], r['price'], r['size']] for r in prints if r.get('is_block_trade') is not True]
    values, proof = receipt_features(epoch=epoch, previous_epoch=previous,
        seconds_per_minute=seconds, formation=leg['formation_end_epoch'], books=books,
        book_epochs=book_epochs, first_q=None, bid=val(now,'bid_cents'), ask=val(now,'ask_cents'),
        previous_bid=val(before,'bid_cents'), previous_ask=val(before,'ask_cents'),
        last=val(now,'last_cents'), prints=positive, maker_previous=prior, maker_current=current,
        attributed_prints=prints)
    for name in ('displayed_depth_at_first_q', 'queue_decay_per_minute'):
        values.pop(name)
    end = math.floor(epoch/seconds)*seconds
    start = max(end-seconds, leg['formation_end_epoch'])
    minute = [r for r in prints if start <= r['ts'] < end and r.get('is_block_trade') is not True]
    complete = start < end and all(r.get('direction_authoritative') is True and
        r.get('is_block_trade') is False and r.get('side') in ('yes','no') for r in minute)
    yes = sum(r['size'] for r in minute if r.get('side')=='yes') if complete else None
    no = sum(r['size'] for r in minute if r.get('side')=='no') if complete else None
    values.update(taker_yes_contracts=yes, taker_no_contracts=no,
                  taker_flow=yes-no if complete else None)
    return dict(epoch=epoch, previous_receipt_epoch=previous, features=values,
        book_current=asof_book(books, book_epochs, epoch),
        book_previous=asof_book(books, book_epochs, previous),
        current_book_invalid_reason=proof['current_book_invalid_reason'],
        previous_book_invalid_reason=proof['previous_book_invalid_reason'],
        maker=proof['maker'], flow_interval=[start,end], flow_complete=complete,
        arithmetic_used_in_model_flow=False)


def build_states(identity, recoveries, prints, gates, seconds):
    rows, first, bell = identity['rows'], identity['first_epoch'], identity['bell']
    native = sorted({p for row in rows for p in row['_epochs'] if p >= first})
    atlas = sorted(bell-float(g)*seconds for g in gates if bell-float(g)*seconds >= first)
    states=[]
    required = [name for name,_,_ in NEW_FIELDS if name not in
                ('displayed_depth_at_first_q','queue_decay_per_minute')]
    required += ['taker_flow','taker_yes_contracts','taker_no_contracts']
    for g in gates:
        epoch = bell-float(g)*seconds
        previous = previous_receipt(native, atlas, epoch, first)
        sides={}
        for row in rows:
            if epoch < first:
                item=dict(epoch=epoch,previous_receipt_epoch=None,
                    features={k:None for k in required}, book_current=None,book_previous=None,
                    reason='BEFORE_FIRST_PAIR_OBSERVATION',maker=None)
            else:
                item=side_state(row,recoveries[row['ticker']],prints[row['ticker']],epoch,previous,seconds)
            sides[row['leg_id']]=item
        states.append(dict(minutes_to_bell=float(g),sides=sides))
    return dict(event_id=identity['event_id'],category=identity['category'],
        span_sha256=identity['span_sha256'],first_epoch=first,bell_epoch=bell,states=states)


def run(args):
    receipt=json.loads(args.recovery_receipt.read_text())
    if receipt.get('status')!='RECOVERY_COMPLETE_NOT_BENCH_RESULT':
        raise ValueError('COMPLETE_AMENDED_RECOVERY_REQUIRED')
    binding=receipt['binding']
    library_sha=digest(args.library)
    if library_sha!=binding['inputs']['library_sha256'] or digest(args.spool)!=binding['inputs']['source_spool_sha256']:
        raise ValueError('GATE_INPUT_PIN_MISMATCH')
    baseline=json.loads(args.baseline_receipt.read_text())
    contract=baseline['organ_contract']
    gates,seconds=contract['gates_minutes_to_bell'],contract['minute_seconds']
    counts=Counter();coverage=defaultdict(Counter);seen=set();source_parts=[]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.out.exists() or args.out.with_suffix('.receipt.json').exists():
        raise ValueError('REFUSE_EXISTING_GATE_OUTPUT')
    partial=args.out.with_suffix(args.out.suffix+'.partial')
    conn=sqlite3.connect('file:'+str(args.spool)+'?mode=ro&immutable=1',uri=True)
    conn.row_factory=sqlite3.Row
    with gzip.open(args.library,'rt') as source,partial.open('xb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as out:
        records=(json.loads(line) for line in source)
        for event,group in itertools.groupby(records,key=lambda r:r['event_id']):
            rows=list(group)
            if rows[0]['category'] not in args.categories:
                continue
            if event in seen:
                raise ValueError('LIBRARY_PAIR_ROWS_NOT_CONTIGUOUS')
            seen.add(event)
            first_seconds={};recoveries={};prints={}
            for leg in rows:
                ticker=leg['ticker']
                recovered,proof=checkpoint(args.recovery_parts,ticker)
                if proof['binding']!=binding or recovered.get('schema')=='FEATURE_INVENTORY_RECOVERY_V2':
                    raise ValueError('UNAMENDED_RECOVERY_REFUSED')
                for k in ('event_id','category','formation_end_epoch','bell_epoch'):
                    if recovered[k]!=leg[k]:
                        raise ValueError('RECOVERY_LEG_SPAN_MISMATCH')
                if recovered.get('book_observation_epochs') is None:
                    old,oldproof=checkpoint(args.legacy_source_parts,ticker,legacy=True)
                    if oldproof['binding']!=binding['inputs']:
                        raise ValueError('LEGACY_OBSERVATION_INPUT_BINDING_MISMATCH')
                    for k in ('event_id','formation_end_epoch','bell_epoch'):
                        if old[k]!=leg[k]:
                            raise ValueError('LEGACY_OBSERVATION_SPAN_MISMATCH')
                    recovered['book_observation_epochs']=old['book_observation_epochs']
                    source_parts.append(dict(ticker=ticker,legacy_observations=oldproof))
                accepted=[dict(r) for r in conn.execute('SELECT * FROM prints WHERE ticker=? AND ts>=? AND ts<? ORDER BY ts,rowid',
                    (ticker,leg['formation_end_epoch'],leg['bell_epoch']))]
                if not accepted:
                    raise ValueError('LIBRARY_WITHOUT_ACCEPTED_PRINTS')
                first_seconds[ticker]=min(math.floor(r['ts']) for r in accepted)
                labels={r['rowid']:r for r in recovered['takers']}
                positive=[r for r in accepted if r['size']>0]
                if {r['rowid'] for r in positive}!=set(labels):
                    raise ValueError('RECOVERY_POSITIVE_PRINT_IDENTITY_MISMATCH')
                for r in positive:
                    r.update(labels[r['rowid']])
                recoveries[ticker]=recovered;prints[ticker]=positive
                source_parts.append(dict(ticker=ticker,sha256=proof['file']['sha256']))
            identity,reason=pair_identity(rows,first_seconds)
            if reason:
                counts['excluded:'+reason]+=1
                continue
            data=build_states(identity,recoveries,prints,gates,seconds)
            out.write(encoded(data)+b'\n')
            counts['pairs']+=1;counts[identity['category']]+=1
            month=datetime.strptime(event.split('-')[-1][:7],'%y%b%d').strftime('%Y-%m')
            for stage in data['states']:
                if identity['bell']-stage['minutes_to_bell']*seconds < identity['first_epoch']:
                    continue
                for leg,item in stage['sides'].items():
                    cell=coverage[(identity['category'],month)]
                    cell['side_gate_receipts']+=1
                    if item.get('current_book_invalid_reason'):
                        cell['current_book_invalid:'+item['current_book_invalid_reason']]+=1
                    if item.get('maker', {}).get('reason'):
                        cell['maker_invalid:'+item['maker']['reason']]+=1
                    for name,value in item['features'].items():
                        cell[name+':available']+=value is not None
            print('GATE_INPUT_PROGRESS '+json.dumps(dict(pairs=counts['pairs'],event=event)),flush=True)
    conn.close()
    summary=dict(schema='FEATURE_INVENTORY_GATE_INPUTS_V2',status='VERIFIED',complete=True,
        library_sha256=library_sha,gates_minutes_to_bell=gates,categories=args.categories,
        output=dict(sha256=digest(partial),bytes=partial.stat().st_size,rows=counts['pairs']),
        counts=dict(counts),coverage=[dict(category=k[0],month=k[1],**dict(v)) for k,v in sorted(coverage.items())],
        label_coverage_by_month_tour=receipt['rows'],
        recovery_binding=binding,recovery_receipt_sha256=digest(args.recovery_receipt),
        baseline_receipt_sha256=digest(args.baseline_receipt),source_parts_sha256=hashlib.sha256(encoded(source_parts)).hexdigest(),
        code={p.name:digest(p) for p in (Path(__file__),Path(__file__).with_name('feature_panel_inventory_features.py'),
            Path(__file__).with_name('feature_panel_book_recovery.py'),Path(__file__).with_name('feature_panel_taker_recovery.py'))},
        rules=dict(queue='UNCHANGED_FIRST_Q_COMPUTED_LOCALLY_PER_FROZEN_UNIVERSE',
            gate_clock='exact filed minutes-to-bell, no rounding; original receipt predecessor',
            maker='last two actual observed snapshots, not last two changed states; end-start+on-book executions; already-known prints in either snapshot boundary second make affected attribution unresolved; prints beyond the receipt are never consulted',
            csv_price_convention='Already YES cents per recorder writer contract; no second NO-price inversion; exact April deployed revision unfiled',
            invalid_book='New maker/imbalance/queue missing on locked/crossed or absent two-sided captures; baseline B1-B6 unchanged',
            direction='API-authoritative non-block only; estimates never flow substitutions',
            ws_depth='DEFERRED_NOT_CHEAP; ws_20260623_08 excluded for truncated gzip; no WS feature claims',
            privacy='Derived exact-gate data only; raw prints/trade ids never exported'))
    partial.replace(args.out)
    args.out.with_suffix('.receipt.json').write_bytes(encoded(summary)+b'\n')
    print('GATE_INPUTS_VERIFIED '+json.dumps(summary),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('library','spool','recovery-receipt','recovery-parts','legacy-source-parts','baseline-receipt','out'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--categories',nargs='+',choices=('ATP_MAIN','ATP_CHALL'),required=True)
    run(p.parse_args())


if __name__=='__main__':
    main()
