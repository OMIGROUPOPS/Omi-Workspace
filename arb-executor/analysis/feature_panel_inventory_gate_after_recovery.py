"""Detached dependent stage: wait on the recovery worker lock, then export.

This is a single batch dependency, not a polling/relaunch loop. Incomplete or
failed recovery is rejected; the approved task follow-up handles that failure.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import sys

import feature_panel_inventory_gate_extract as gate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('library','spool','recovery-receipt','recovery-parts','legacy-source-parts',
                 'baseline-receipt','out','recovery-worker-lock'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--categories',nargs='+',choices=('ATP_MAIN','ATP_CHALL'),required=True)
    args=parser.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    def state(status,**extra):
        payload=dict(status=status,pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**extra)
        tmp=args.out.parent/('GATE_RUN_STATE.partial.'+str(os.getpid()))
        tmp.write_text(json.dumps(payload,sort_keys=True)+'\n')
        tmp.replace(args.out.parent/'GATE_RUN_STATE.json')
        print(json.dumps(payload),flush=True)
    code=1
    try:
        with (args.out.parent/'GATE_WORKER.lock').open('a') as own:
            fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB)
            state('WAITING_FOR_RECOVERY_WORKER_LOCK')
            with args.recovery_worker_lock.open('a') as dependency:
                fcntl.flock(dependency,fcntl.LOCK_EX)
                # gate.run requires complete amended receipt and rehashes inputs.
                state('VERIFYING_RECOVERY_THEN_EXPORTING')
                gate.run(args)
            state('GATE_INPUTS_VERIFIED')
            code=0
    except BaseException as error:
        state('FAILED',error_type=type(error).__name__,error=str(error))
        raise
    finally:
        (args.out.parent/'GATE_RUN.exit').write_text(json.dumps(dict(code=code,pid=os.getpid()))+'\n')


if __name__=='__main__':
    main()
