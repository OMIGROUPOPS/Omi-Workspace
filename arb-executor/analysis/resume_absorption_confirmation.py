"""Execution-only continuation after an empty-atlas input stopped confirmation.

No fitting, model choice, or replay. Already scored games are not opened again.
The sole permitted runner change is `if not rows: return []` in scored_rows;
AST equality after removing that guard is mandatory. Old bindings stay intact.
"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import pickle
import time
import absorption_residual_run as run
from absorption_residual_data import load_selected_pairs, prepare_rows
from feature_panel_inventory_gate_extract import digest


def verify_empty_guard(before, after):
    old, new = ast.parse(before), ast.parse(after)
    function = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == 'scored_rows')
    guard = ast.parse('if not rows:\n    return []').body[0]
    if ast.dump(function.body[0]) != ast.dump(guard):
        raise ValueError('EXPECTED_EMPTY_ONLY_GUARD')
    function.body.pop(0)
    if ast.dump(old) != ast.dump(new):
        raise ValueError('NON_EXECUTION_CHANGE_FORBIDDEN')


def resume(args):
    contract, reservation, current, library, counts = run.bind(args)
    old = json.loads((args.out/'INPUT_BINDING.json').read_text())
    runner = Path(run.__file__)
    if digest(args.before_runner) != old['code'][runner.name]:
        raise ValueError('ORIGINAL_RUNNER_HASH_MISMATCH')
    verify_empty_guard(args.before_runner.read_text(), runner.read_text())
    normalized = json.loads(json.dumps(current))
    normalized['code'][runner.name] = old['code'][runner.name]
    if normalized != old:
        raise ValueError('ONLY_RUNNER_EMPTY_GUARD_MAY_CHANGE')
    if (args.out/'CONFIRMATION_RESULTS.json').exists():
        raise ValueError('CONFIRMATION_ALREADY_FINISHED')
    development = json.loads((args.out/'DEVELOPMENT_RESULTS.json').read_text())
    if development['binding'] != old:
        raise ValueError('DEVELOPMENT_BINDING_DRIFT')
    receipt_path = args.out/'EXECUTION_RESUME.json'
    receipt = dict(schema='EMPTY_ATLAS_EXECUTION_RESUME_V1',
        reason='Empty atlas game caused NumPy empty float mask IndexError; no prediction existed to change',
        started_at=run.now(), original_binding=old, current_binding=current,
        runner_ast_identical_after_removing_empty_guard=True,
        resume_code_sha256=digest(Path(__file__)), categories=[],
        fitting='NONE; original frozen models and original completed checkpoints reused',
        confirmation='Continuation of the single final phase, not a second test or retune')
    if receipt_path.exists():
        saved = json.loads(receipt_path.read_text())
        for key in ('original_binding','current_binding','resume_code_sha256'):
            if saved[key] != receipt[key]:
                raise ValueError('RESUME_BINDING_DRIFT')
        receipt = saved
    run.atomic(receipt_path, receipt)
    started = time.monotonic()
    combined = []
    for category in run.CATEGORIES:
        spec = reservation['categories'][category]
        private = args.out/'confirmation'/category
        saved = args.out/'development'/category
        freeze = json.loads((saved/'MODEL_FREEZE.json').read_text())
        model_path = saved/'CONFIRMATION_MODELS.pkl'
        if freeze['binding'] != old or digest(model_path) != freeze['model_sha256']:
            raise ValueError('FROZEN_MODEL_DRIFT')
        selected = {r['event_id']: r for r in spec['reserved']}
        completed = {}
        for event in selected:
            path = private/(event+'.json')
            if path.exists():
                part = json.loads(path.read_text())
                if part['binding'] not in (old, current) or any(r['event'] != event for r in part['scores']):
                    raise ValueError('CHECKPOINT_DRIFT')
                completed[event] = part['scores']
        pending = {e:r for e,r in selected.items() if e not in completed}
        summary = dict(category=category,reserved_games=len(selected),
            reused_completed_games=len(completed),pending_games=len(pending),
            frozen_model_sha256=freeze['model_sha256'])
        print('RESUME '+json.dumps(summary),flush=True)
        if pending:
            metadata = {r['event_id']:dict(r,event_date=run.reference.date_key(r['event_id'])) for r in spec['development']}
            pairs, _ = load_selected_pairs(library,counts,metadata)
            queries, leg_meta = load_selected_pairs(library,counts,pending)
            members = [p for p in pairs if p.bell < spec['confirmation_cutoff']]
            c, _, par = run.numerical_contract(args.root,category)
            frozen = pickle.loads(model_path.read_bytes())
            for event, rows in prepare_rows(queries,members,args.gates,args.witnesses,leg_meta,c,par):
                scores = []
                for side in (0,1):
                    scores.extend(run.scored_rows([r for r in rows if r['side']==side],frozen[side],par))
                scores = run.clean(scores)
                run.atomic(private/(event+'.json'),dict(binding=current,scores=scores,
                    execution_resume='EXECUTION_RESUME.json; frozen model/checkpoint provenance preserved'))
                completed[event] = scores
                print('CONFIRMATION_SCORED '+event,flush=True)
        if set(completed) != set(selected):
            raise ValueError('RESERVED_SET_INCOMPLETE')
        ordered = sorted(selected,key=lambda e:(selected[e]['formation_epoch'],e))
        rows = [r for e in ordered for r in completed[e]]
        summary.update(completed_games=len(completed),zero_atlas_games=sum(not v for v in completed.values()))
        receipt['categories'].append(summary)
        run.atomic(receipt_path,receipt)
        run.atomic(private/'SCORES.json',rows)
        combined.extend(rows)
    result = run.reports(combined,contract,current,'confirmation',reservation)
    if run.bind(args)[2] != current:
        raise ValueError('BINDING_CHANGED_DURING_RESUME')
    receipt.update(completed_at=run.now(),elapsed_seconds=time.monotonic()-started,status='COMPLETE')
    run.atomic(receipt_path,receipt)
    result['execution_resume_sha256'] = digest(receipt_path)
    run.atomic(args.out/'CONFIRMATION_RESULTS.json',result)
    run.atomic(args.out/'RUN_STATE.json',dict(status='CONFIRMATION_COMPLETE',completed_at=run.now(),
        execution_resume_sha256=digest(receipt_path),elapsed_seconds=time.monotonic()-started))
    run.atomic(args.out.parent/'PIPELINE_STATE.json',dict(status='RESULTS_READY_FOR_REVIEW_NOT_COMMITTED',at=run.now()))
    print('CONFIRMATION_COMPLETE '+json.dumps(receipt['categories']),flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('root','out','audit','gates','gate-receipt','witnesses','source-receipt','before-runner'):
        p.add_argument('--'+name,type=Path,required=True)
    resume(p.parse_args())
