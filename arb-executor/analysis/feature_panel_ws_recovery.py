"""Stream original WS depth into a resumable, library-only derived sidecar.

One object transaction is committed only after its gzip CRC, size, compressed
SHA and response MD5 ETag verify. Sequence custody crosses hourly objects; the
checkpoint includes the complete live decoder state. No raw archives saved.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import gzip
import io
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import time
import zlib

from feature_panel_book_recovery import DepthDecoder
from feature_panel_inventory_extract import atomic_json, load_core, sha, tune_event


APPROVED_OBJECT_EXCLUSIONS = {
    'ws_20260623_08.jsonl.gz': 'TRUNCATED_GZIP; operator-approved exclusion after EOF before end-of-stream marker',
}


def archive_exclusion(item):
    reason=APPROVED_OBJECT_EXCLUSIONS.get(item['name'])
    if reason is None:
        return None
    # Recorder writer() names archives by UTC clock hour, not event-name day.
    start=datetime.strptime(item['name'][3:14],'%Y%m%d_%H').replace(tzinfo=timezone.utc)
    return dict(name=item['name'],bytes=item['bytes'],status='EXCLUDED',reason=reason,
        hour_start_epoch=start.timestamp(),hour_end_epoch=(start+timedelta(hours=1)).timestamp(),
        action='invalidate capture chain; no state carried across excluded object until fresh snapshot')


def encode(value):
    return zlib.compress(json.dumps(value,separators=(',',':'),sort_keys=True,allow_nan=False).encode())


def decoder_snapshot(decoder):
    return dict(started=decoder.started,sequence=decoder.sequence,counters=dict(decoder.counters),
        no_price_convention=decoder.no_price_convention,
        capture_no_price_convention=decoder.capture_no_price_convention,
        books={ticker:dict(sid=book['sid'],
            bid=[[str(p),str(q)] for p,q in book['bid'].items()],
            ask=[[str(p),str(q)] for p,q in book['ask'].items()]) for ticker,book in decoder.books.items()})


def restore_decoder(decoder,saved):
    decoder.started=saved['started']
    decoder.sequence={int(k):v for k,v in saved['sequence'].items()}
    decoder.counters.update(saved['counters'])
    decoder.no_price_convention=saved['no_price_convention']
    decoder.capture_no_price_convention=saved['capture_no_price_convention']
    decoder.books={ticker:dict(sid=book['sid'],
        bid={Decimal(p):Decimal(q) for p,q in book['bid']},
        ask={Decimal(p):Decimal(q) for p,q in book['ask']}) for ticker,book in saved['books'].items()}


def manifest(path,first,last):
    rows=[]
    for line in path.read_text().splitlines():
        parts=line.split(';')
        if len(parts)!=3:
            continue
        name=parts[2]
        if re.fullmatch(r'ws_\d{8}_\d{2}(?:_[A-Za-z0-9_]+)?\.jsonl\.gz',name) is None:
            continue
        if first<=name[3:11]<=last:
            rows.append(dict(name=name,bytes=int(parts[1])))
    if len({r['name'] for r in rows})!=len(rows):
        raise ValueError('DUPLICATE_WS_MANIFEST_NAME')
    return sorted(rows,key=lambda r:r['name'])


def run(args):
    core=load_core(args.core)
    receipt=json.loads(args.source_receipt.read_text())
    if sha(args.library)!=receipt['library_sha256'] or sha(args.core)!=receipt['extractor_sha256']:
        raise ValueError('WS_RECOVERY_INPUT_BINDING_MISMATCH')
    required={}
    with gzip.open(args.library,'rt') as stream:
        for line in stream:
            leg=json.loads(line)
            if leg['category'] in ('ATP_MAIN','ATP_CHALL'):
                if tune_event(leg['event_id']):
                    raise ValueError('TUNE_EVENT_REFUSED')
                required[leg['ticker']]={k:leg[k] for k in ('formation_end_epoch','bell_epoch','event_id','category')}
    first=datetime.fromtimestamp(min(r['formation_end_epoch'] for r in required.values()),timezone.utc).strftime('%Y%m%d')
    last=datetime.fromtimestamp(max(r['bell_epoch'] for r in required.values()),timezone.utc).strftime('%Y%m%d')
    objects=manifest(args.inventory,first,last)
    if args.limit_objects is not None:
        objects=objects[:args.limit_objects]
    binding=dict(library_sha256=receipt['library_sha256'],core_sha256=receipt['extractor_sha256'],
        inventory_sha256=sha(args.inventory),objects=objects,
        code={p.name:sha(p) for p in (Path(__file__),Path(__file__).with_name('feature_panel_book_recovery.py'),
            Path(__file__).with_name('feature_panel_inventory_extract.py'),
            Path(__file__).with_name('feature_panel_taker_recovery.py'))})
    args.out.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(args.out/'WS_DERIVED.sqlite')
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('CREATE TABLE IF NOT EXISTS states (ticker TEXT,second INTEGER,available_epoch REAL,payload BLOB,PRIMARY KEY(ticker,second)) WITHOUT ROWID')
    db.execute('CREATE TABLE IF NOT EXISTS objects (ordinal INTEGER PRIMARY KEY,name TEXT,proof TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS checkpoint (id INTEGER PRIMARY KEY,binding TEXT,state BLOB)')
    existing=db.execute('SELECT binding,state FROM checkpoint WHERE id=1').fetchone()
    decoders={}
    if existing:
        if json.loads(existing[0])!=binding:
            raise ValueError('WS_CHECKPOINT_BINDING_MISMATCH')
        saved=json.loads(zlib.decompress(existing[1]))
        for session,state in saved.items():
            decoders[session]=DepthDecoder(required)
            restore_decoder(decoders[session],state)
    completed=db.execute('SELECT ordinal,name FROM objects ORDER BY ordinal').fetchall()
    if completed!=[(i,r['name']) for i,r in enumerate(objects[:len(completed)])]:
        raise ValueError('WS_CHECKPOINT_NOT_MANIFEST_PREFIX')
    db.commit()
    client=core.SpacesClient(core.spaces_environment(args.repo))
    started=time.monotonic()
    processed_bytes=0
    for ordinal,item in enumerate(objects):
        if ordinal<len(completed):
            continue
        atomic_json(args.out/'RUN_STATE.json',dict(status='RUNNING',pid=os.getpid(),
            objects_done=ordinal,objects_total=len(objects),current_object=item['name']))
        # New recorder suffix identifies its session across hours. Legacy
        # archives have one common chain; recorder_start frames reset it.
        components=item['name'].removesuffix('.jsonl.gz').split('_')
        session='_'.join(components[3:]) if len(components)>3 else 'legacy'
        decoder=decoders.setdefault(session,DepthDecoder(required))
        exclusion=archive_exclusion(item)
        if exclusion is not None:
            # Skip is transactionally recorded, and kills the previous ladder.
            # It is not a successful decode or an hour of unchanged books.
            db.execute('BEGIN IMMEDIATE')
            try:
                invalidated=decoder.invalidate_archive()
                epoch=exclusion['hour_start_epoch']
                for ticker in invalidated:
                    bounds=required[ticker]
                    if bounds['formation_end_epoch']<=epoch<bounds['bell_epoch']:
                        payload=dict(ticker=ticker,available_epoch=epoch,sid=None,seq=None,
                            valid=False,reason='EXCLUDED_TRUNCATED_ARCHIVE',object=item['name'])
                        db.execute('INSERT OR REPLACE INTO states VALUES (?,?,?,?)',
                            (ticker,math.floor(epoch),epoch,encode(payload)))
                exclusion['invalidated_library_ladders']=len(invalidated)
                db.execute('INSERT INTO objects VALUES (?,?,?)',
                    (ordinal,item['name'],json.dumps(exclusion,sort_keys=True)))
                db.execute('INSERT OR REPLACE INTO checkpoint VALUES (1,?,?)',
                    (json.dumps(binding,sort_keys=True),encode({k:decoder_snapshot(v) for k,v in decoders.items()})))
                db.commit()
            except BaseException:
                db.rollback()
                raise
            print('WS_OBJECT_EXCLUDED '+json.dumps(exclusion,sort_keys=True),flush=True)
            continue
        response=client.open('ws_depth/'+item['name'])
        etag=(response.getheader('ETag') or '').strip('"').lower()
        hashed=core.HashReader(response)
        physical,selected,written=0,0,0
        pending={}
        pending_second=None
        def flush_second():
            nonlocal written
            for ticker,last in pending.items():
                state=(last if last.get('valid') is False else decoder.state(**last))
                bounds=required[ticker]
                epoch=state['available_epoch']
                if bounds['formation_end_epoch']<=epoch<bounds['bell_epoch']:
                    db.execute('INSERT INTO states VALUES (?,?,?,?) ON CONFLICT(ticker,second) DO UPDATE '
                        'SET available_epoch=excluded.available_epoch,payload=excluded.payload '
                        'WHERE excluded.available_epoch>=states.available_epoch',
                        (ticker,math.floor(epoch),epoch,encode(state)))
                    written+=1
            pending.clear()
        # Objects are immutable input; only library spans are persisted. Foreign
        # ticker sequence frames are parsed solely to verify stream continuity.
        try:
            db.execute('BEGIN IMMEDIATE')
            with io.BufferedReader(hashed) as buffered,gzip.GzipFile(fileobj=buffered) as zipped:
                for line in zipped:
                    physical+=1
                    row=json.loads(line)
                    clock=row.get('t')
                    if not isinstance(clock,(int,float)) or not math.isfinite(clock):
                        raise ValueError('WS_LOCAL_RECEIPT_CLOCK_MISSING')
                    second=math.floor(clock)
                    if pending_second is not None and second<pending_second:
                        raise ValueError('WS_RECEIPT_SECOND_REGRESSION')
                    if second!=pending_second:
                        flush_second()
                        pending_second=second
                    state=decoder.consume(row,materialize=False)
                    for ticker in decoder.invalidated:
                        pending[ticker]=dict(ticker=ticker,available_epoch=clock,sid=None,seq=None,
                            valid=False,reason='DEPTH_CUSTODY_INVALIDATED')
                    if state is None:
                        continue
                    selected+=1
                    pending[state['ticker']]=state
            flush_second()
            if hashed.bytes!=item['bytes'] or hashed.md5.hexdigest()!=etag:
                raise ValueError('WS_OBJECT_SIZE_OR_MD5_ETAG_MISMATCH:'+item['name'])
            proof=dict(name=item['name'],bytes=hashed.bytes,compressed_sha256=hashed.digest.hexdigest(),
                compressed_md5=hashed.md5.hexdigest(),observed_etag=etag,physical_rows=physical,
                selected_library_updates=selected,library_state_or_invalidation_seconds=written,session=session)
            db.execute('INSERT INTO objects VALUES (?,?,?)',(ordinal,item['name'],json.dumps(proof,sort_keys=True)))
            db.execute('INSERT OR REPLACE INTO checkpoint VALUES (1,?,?)',
                (json.dumps(binding,sort_keys=True),encode({k:decoder_snapshot(v) for k,v in decoders.items()})))
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            response.close()
        processed_bytes+=item['bytes']
        elapsed=time.monotonic()-started
        remaining=sum(r['bytes'] for r in objects[ordinal+1:])
        print('WS_PROGRESS '+json.dumps(dict(objects_done=ordinal+1,objects_total=len(objects),
            bytes_this_process=processed_bytes,elapsed_seconds=elapsed,bytes_per_second=processed_bytes/elapsed,
            eta_seconds=remaining*elapsed/processed_bytes,library_updates_this_object=selected)),flush=True)
    stats=Counter()
    for decoder in decoders.values():
        stats.update(decoder.counters)
    objects_proof=[json.loads(r[0]) for r in db.execute('SELECT proof FROM objects ORDER BY ordinal')]
    counts={r[0]:r[1] for r in db.execute('SELECT ticker,count(*) FROM states GROUP BY ticker')}
    rows=[]
    cells=Counter()
    for ticker,n in counts.items():
        row=required[ticker]
        stamp=re.search(r'-(\d{2}[A-Z]{3}\d{2})',row['event_id'])[1]
        cells[(row['category'],datetime.strptime(stamp,'%y%b%d').strftime('%Y-%m'))]+=n
    db.close()
    result=dict(status='SMOKE_ONLY' if args.limit_objects is not None else 'WS_RECOVERY_COMPLETE_NOT_BENCH_RESULT',
        binding=binding,objects=objects_proof,counters=dict(stats),library_legs_with_states=len(counts),
        excluded_objects=[p for p in objects_proof if p.get('status')=='EXCLUDED'],
        per_ticker_rows=counts,rows=[dict(category=k[0],month=k[1],seconds=v) for k,v in sorted(cells.items())],
        output=dict(name='WS_DERIVED.sqlite',sha256=sha(args.out/'WS_DERIVED.sqlite'),bytes=(args.out/'WS_DERIVED.sqlite').stat().st_size),
        rules=dict(clock='actual local recorder receipt timestamp; no exchange timestamp relabeled as receipt time',
            convention='historical capture default NO-leg price inverted to YES cents; explicit recorder use_yes_price metadata overrides per capture; fixed-point fields explicit',
            eligibility='recorder-started, snapshot-seeded and SID gap-free causal prefix; gaps emit invalidation rows until fresh snapshot, never carry old depth across a gap',
            source_binding='inventory bytes plus full compressed SHA and GET-response MD5 ETag; no previously filed WS hash claimed',
            output='last observed full ladder in each local receipt second, with its exact availability epoch; raw archives never saved'))
    atomic_json(args.out/'WS_RECOVERY_RECEIPT.json',result)
    atomic_json(args.out/'RUN_STATE.json',dict(status=result['status'],objects_done=len(objects),objects_total=len(objects),
        rows_written=sum(counts.values()),pid=os.getpid()))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('library','source-receipt','core','repo','inventory','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--limit-objects',type=int)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    import fcntl
    with (args.out/'WORKER.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        code=1
        try:
            atomic_json(args.out/'RUN_STATE.json',dict(status='VERIFYING_INPUTS',pid=os.getpid()))
            run(args)
            code=0
        finally:
            atomic_json(args.out/'RUN.exit',dict(code=code,pid=os.getpid(),finished_at=datetime.now(timezone.utc).isoformat()))


if __name__=='__main__':
    main()
