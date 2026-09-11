"""Fail-closed planning/validation for a NOT ENABLED public Actions proof.

This module never downloads, uploads, fits, or scores. Approval must separately
authorize a private input release and an execution adapter. Public artifacts
are allowlisted summaries, not arbitrary files beneath a run directory.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

PUBLIC_ARTIFACTS = frozenset(('ATLAS_SCREEN_RESULTS.json','OPTIMIZER_OUTCOMES.json',
    'ATLAS_SCREEN_RECEIPT.json','SUMMARY.md',
    'PROOF_SUMMARY.json','PROOF_RECEIPT.json','DETERMINISM.json','SHARD_COUNTS.json'))
INPUT_NAMES = frozenset(('RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz',
    'RANGE_OVERLAP_LIBRARY_TICKS_RECEIPT.json','RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz',
    'RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS_RECEIPT.json','FEATURE_SOURCES.jsonl.gz',
    'POSITIVE_PRINT_WITNESSES.jsonl.gz','SUPPLEMENTAL_AVAILABILITY.jsonl.gz',
    'FEATURE_EXTRACT_RECEIPT.json','SUPPLEMENTAL_AVAILABILITY_RECEIPT.json','ODDS_COVERAGE_RECEIPT.json'))
TOURS = ('ATP_MAIN','ATP_CHALL')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def forbidden_event(event):
    return re.search(r'-26JUL(?:1[1-9]|2[01])(?:[^0-9]|$)',event) is not None


def reject_tune(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ('event_id','event','ticker') and isinstance(item,str) and forbidden_event(item):
                raise ValueError('TUNE_EVENT_FORBIDDEN')
            reject_tune(item)
    elif isinstance(value,(list,tuple)):
        for item in value:reject_tune(item)
    elif isinstance(value,str) and value.upper()=='TUNE_SAMPLE':
        raise ValueError('TUNE_TAG_FORBIDDEN')


def validate_manifest(manifest):
    if manifest.get('schema')!='FEATURE_PANEL_ACTIONS_RELEASE_V1':
        raise ValueError('UNKNOWN_RELEASE_SCHEMA')
    files=manifest.get('files',[])
    if {x['name'] for x in files} != INPUT_NAMES or len(files)!=len(INPUT_NAMES):
        raise ValueError('EXACT_INPUT_ALLOWLIST_REQUIRED')
    for item in files:
        if (Path(item['name']).name!=item['name'] or not re.fullmatch('[0-9a-f]{64}',item['sha256'])
                or not isinstance(item['bytes'],int) or item['bytes']<=0):
            raise ValueError('INVALID_INPUT_BINDING')
    if manifest.get('tune_sample_allowed') is not False:
        raise ValueError('TUNE_POLICY_MISSING')
    if set(manifest.get('public_artifacts',[])) != PUBLIC_ARTIFACTS:
        raise ValueError('PUBLIC_ARTIFACT_ALLOWLIST_REQUIRED')
    return manifest


def validate_bundle(directory,manifest):
    validate_manifest(manifest)
    root=Path(directory).resolve(strict=True)
    if {p.name for p in root.iterdir()} != INPUT_NAMES:
        raise ValueError('UNALLOWLISTED_RELEASE_FILE')
    for item in manifest['files']:
        p=root/item['name']
        if p.is_symlink() or p.resolve().parent!=root or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:
            raise ValueError('INPUT_HASH_SIZE_OR_PATH_MISMATCH:'+item['name'])
    library_events=set();library_legs={}
    with gzip.open(root/'RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz','rt') as f:
        for line in f:
            row=json.loads(line);reject_tune(row);library_events.add(row['event_id'])
            ticker=row['ticker']
            if ticker in library_legs:raise ValueError('DUPLICATE_LIBRARY_LEG')
            library_legs[ticker]={key:row.get(key) for key in
                ('event_id','formation_end_epoch','bell_epoch')}
    # Receipt bytes are hash-bound above. Their exclusion-policy prose may
    # legitimately name TUNE_SAMPLE; reject that role in data, not policy text.
    # No named-check file is admitted, including under an innocuous filename.
    for item in manifest['files']:
        p=root/item['name']
        if item['name'].endswith('.jsonl.gz') and not item['name'].startswith('RANGE_OVERLAP_LIBRARY_TICKS.'):
            with gzip.open(p,'rt') as f:
                for line in f:
                    row=json.loads(line);reject_tune(row)
                    event=row.get('event_id') or str(row.get('ticker','')).rsplit('-',1)[0]
                    if event not in library_events or row.get('ticker') not in library_legs:
                        raise ValueError('NON_LIBRARY_INPUT_ROW')
                    leg=library_legs[row['ticker']]
                    if event!=leg['event_id']:raise ValueError('INPUT_EVENT_TICKER_MISMATCH')
                    for field in ('formation_end_epoch','bell_epoch'):
                        if field in row and row[field]!=leg.get(field):
                            raise ValueError('INPUT_SPAN_MISMATCH')
    return dict(status='VALIDATED_LIBRARY_ONLY',library_events=len(library_events))


def shard_queries(queries,count):
    if count<=0:raise ValueError('POSITIVE_SHARD_COUNT_REQUIRED')
    keys=[(q['event_id'],q['stream'],q['month']) for q in queries]
    if len(keys)!=len(set(keys)):raise ValueError('DUPLICATE_QUERY')
    bins=[[] for _ in range(count)];cost=[0]*count
    for q in sorted(queries,key=lambda q:(-q['receipt_cost'],q['event_id'],q['stream'],q['month'])):
        target=min(range(count),key=lambda i:(cost[i],i))
        bins[target].append(q);cost[target]+=q['receipt_cost']
    # Full query remains atomic. Reducer order is the original global order,
    # never this scheduling order and never unordered floating-point sums.
    return [dict(shard=i,estimated_receipts=cost[i],queries=sorted(bucket,
        key=lambda q:(q['month'],q['stream']!='PRIMARY',q['event_id']))) for i,bucket in enumerate(bins)]


def matrix(results,shards):
    jobs=[]
    for category in TOURS:
        result=results[category]
        chosen=result['advancement']['variants']
        if result['advancement']['june_may_select'] is not False:
            raise ValueError('HOLDOUT_SELECTED_FINALISTS')
        if chosen:
            for repeat in ('pass1','pass2'):
                for shard in range(shards):
                    jobs.append(dict(category=category,repeat=repeat,shard=shard,shards=shards,variants=chosen))
    return dict(include=jobs)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results-root',type=Path,required=True)
    p.add_argument('--shards',type=int,required=True)
    a=p.parse_args()
    results={c:json.loads((a.results_root/c/'ATLAS_SCREEN_RESULTS.json').read_text()) for c in TOURS}
    print(json.dumps(matrix(results,a.shards),sort_keys=True))


if __name__=='__main__':main()
