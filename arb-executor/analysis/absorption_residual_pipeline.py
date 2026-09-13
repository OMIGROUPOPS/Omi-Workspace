"""Finish the already-authorized audit/test sequence, without data transfer.

The SSH response allowlist is aggregate coverage/rules/counts/hashes only.
No audit intervals, source rows, example values or per-leg data are returned.
No scheduler, engine execution, automatic Git action or live-store access.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from absorption_residual_run import atomic, now
from feature_panel_inventory_gate_extract import digest


REMOTE_CHECK = r'''
import hashlib,json,pathlib
base=pathlib.Path('/mnt/omi-trading-data-nyc3/library/absorption_audit_20260913')
out=base/'production'
request=REQUEST_BINDING
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
exitfile=out/'RUN.exit'
if not exitfile.exists():
 state=json.loads((out/'RUN_STATE.json').read_text())
 print(json.dumps({'state':{k:state.get(k) for k in ('status','legs_done','legs_total','elapsed_seconds','rate_legs_per_second','eta_seconds')}}))
 raise SystemExit
code=json.loads(exitfile.read_text())
if code['code']!=0:
 print(json.dumps({'failure':'REMOTE_AUDIT_EXIT_NONZERO','exit':code}))
 raise SystemExit
path=out/'ABSORPTION_AUDIT_RECEIPT.json'
r=json.loads(path.read_text())
if r['status']!='AUDIT_COMPLETE':raise ValueError('AUDIT_NOT_COMPLETE')
for name,expected in request['code'].items():
 if sha(base/'code'/name)!=expected:raise ValueError('AUDIT_CODE_PIN_MISMATCH:'+name)
parts=out/'parts'
seen=set()
for item in r['parts']:
 key=hashlib.sha256(item['ticker'].encode()).hexdigest()
 marker=parts/(key+'.json')
 if key in seen or sha(marker)!=item['marker_sha256']:raise ValueError('PART_IDENTITY_OR_MARKER_SHA')
 seen.add(key)
 m=json.loads(marker.read_text())
 if m['binding']!=r['binding']:raise ValueError('PART_BINDING_DRIFT')
 p=parts/m['interval_output']['name']
 if p.parent.resolve()!=parts.resolve():raise ValueError('PART_PATH_ESCAPE')
 interval_sha=sha(p)
 if interval_sha!=item['intervals_sha256'] or interval_sha!=m['interval_output']['sha256']:raise ValueError('PART_INTERVAL_SHA')
keep={k:r[k] for k in ('schema','status','binding','coverage','bars','unexplained_reconciliation_failures','unobserved_reasons','rules','source_store')}
keep.update(remote_receipt_sha256=sha(path),verified_parts=len(seen),all_part_hashes_verified=True,
            transferred='AGGREGATE_REPORT_ONLY; no intervals, private examples, per-leg data, snapshots or prints',
            code_transfer_sha256s=request['code'],exit=code)
print(json.dumps({'audit':keep}))
'''


def remote_status(host, code):
    script=REMOTE_CHECK.replace('REQUEST_BINDING',repr(dict(code=code)))
    result=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',host,'python3','-'],
        input=script,text=True,capture_output=True,check=True)
    return json.loads(result.stdout)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--host',required=True)
    p.add_argument('--poll-seconds',type=float,default=30,help='Transport cadence only; not a bench parameter')
    args=p.parse_args()
    analysis=args.root/'arb-executor/analysis'
    names=('absorption_audit.py','feature_panel_book_recovery.py','feature_panel_taker_recovery.py',
           'feature_panel_inventory_gate_extract.py','feature_panel_inventory_features.py')
    code={n:digest(analysis/n) for n in names}
    args.out.mkdir(parents=True,exist_ok=True)
    audit_path=args.out/'AUDIT_AGGREGATE.json'
    while True:
        result=remote_status(args.host,code)
        if result.get('failure'):
            atomic(args.out/'PIPELINE_STATE.json',dict(status='STOPPED',**result,at=now()))
            print(json.dumps(result),flush=True)
            return
        if 'audit' in result:
            audit=result['audit']
            atomic(audit_path,audit)
            if audit['unexplained_reconciliation_failures'] or not all(v['pass'] for v in audit['bars'].values()):
                atomic(args.out/'PIPELINE_STATE.json',dict(status='AUDIT_BAR_FAILED_NO_FIT',bars=audit['bars'],at=now()))
                print('AUDIT_BAR_FAILED '+json.dumps(audit['bars']),flush=True)
                return
            print('AUDIT_VERIFIED '+json.dumps(dict(bars=audit['bars'],receipt_sha256=audit['remote_receipt_sha256'])),flush=True)
            break
        atomic(args.out/'PIPELINE_STATE.json',dict(status='WAITING_FOR_REMOTE_AUDIT',**result,at=now()))
        print('WAITING '+json.dumps(result['state']),flush=True)
        time.sleep(args.poll_seconds)
    common=[sys.executable,'-B',str(analysis/'absorption_residual_run.py'),
        '--root',str(args.root),'--out',str(args.out/'models'),'--audit',str(audit_path),
        '--gates',r'C:\tmp\feature_panel_inventory_v2\INVENTORY_GATE_INPUTS.jsonl.gz',
        '--gate-receipt',r'C:\tmp\feature_panel_inventory_v2\INVENTORY_GATE_INPUTS.jsonl.receipt.json',
        '--witnesses',r'C:\tmp\feature_panel_v1\POSITIVE_PRINT_WITNESSES.jsonl.gz',
        '--source-receipt',r'C:\tmp\feature_panel_v1\FEATURE_EXTRACT_RECEIPT.json']
    for phase in ('development','confirmation'):
        result_file=args.out/'models'/(phase.upper()+'_RESULTS.json')
        if result_file.exists():
            raise ValueError('PIPELINE_PHASE_ALREADY_FINISHED; inspect before resuming '+phase)
        atomic(args.out/'PIPELINE_STATE.json',dict(status='RUNNING_'+phase.upper(),at=now()))
        subprocess.run(common+['--phase',phase],check=True,cwd=analysis)
    atomic(args.out/'PIPELINE_STATE.json',dict(status='RESULTS_READY_FOR_REVIEW_NOT_COMMITTED',at=now()))
    print('RESULTS_READY_FOR_REVIEW_NOT_COMMITTED',flush=True)


if __name__=='__main__':
    main()
