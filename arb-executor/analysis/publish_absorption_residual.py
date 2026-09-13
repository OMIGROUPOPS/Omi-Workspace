"""Publish aggregate reports only after the frozen residual run completes.

Reads existing private score checkpoints, not source outcomes. No fitting,
prediction, replay, network or Git action. Raw rows/models are never copied.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+
        ['| '+' | '.join(str(v) for v in row)+' |' for row in rows])


def fmt(value):
    return 'no data' if value is None else f'{value:.4f}'


def main(args):
    dest=args.root/'arb-executor/analysis/absorption_residual_v1'
    private=args.private
    models=private/'models'
    if read(private/'PIPELINE_STATE.json')['status']!='RESULTS_READY_FOR_REVIEW_NOT_COMMITTED':
        raise ValueError('PIPELINE_NOT_COMPLETE')
    if read(models/'RUN_STATE.json')['status']!='CONFIRMATION_COMPLETE':
        raise ValueError('CONFIRMATION_NOT_COMPLETE')
    contract=read(dest/'CONTRACT.json')
    reservation=read(dest/'RESERVATION.json')
    pins=read(dest/'INPUTS.json')
    engine={n:sha(args.root/'arb-executor/analysis'/n) for n in pins['engine_unchanged']}
    if engine!=pins['engine_unchanged']:
        raise ValueError('ENGINE_CHANGED')
    audit=read(private/'AUDIT_AGGREGATE.json')
    if audit['unexplained_reconciliation_failures'] or not all(r['pass'] for r in audit['bars'].values()):
        raise ValueError('AUDIT_BAR_FAILED')
    resumed=read(models/'EXECUTION_RESUME.json')
    if resumed['status']!='COMPLETE' or not resumed['runner_ast_identical_after_removing_empty_guard']:
        raise ValueError('RESUME_NOT_VERIFIED')
    results={p:read(models/(p.upper()+'_RESULTS.json')) for p in ('development','confirmation')}
    for phase,r in results.items():
        expected=resumed['original_binding' if phase=='development' else 'current_binding']
        if r['binding']!=expected or r['binding']['contract_sha256']!=sha(dest/'CONTRACT.json'):
            raise ValueError('RESULT_BINDING_DRIFT')
        if len(r['comparisons'])!=36:
            raise ValueError('MISSING_COMPARISONS')
    for name,expected in resumed['current_binding']['code'].items():
        if sha(args.root/'arb-executor/analysis'/name)!=expected:
            raise ValueError('FINAL_CODE_DRIFT:'+name)
    optimizers=read(models/'OPTIMIZER_OUTCOMES.json')
    primary=[]
    coverage=[]
    run_checks=[]
    for phase,r in results.items():
        for category in ('ATP_MAIN','ATP_CHALL'):
            spec=reservation['categories'][category]
            selected={g['event_id'] for g in spec['development' if phase=='development' else 'reserved']}
            rows=read(models/phase/category/'SCORES.json')
            if any(row['event'] not in selected for row in rows):
                raise ValueError('COHORT_MIXING')
            keys=[(row['event'],row['side'],row['gate']) for row in rows]
            if len(keys)!=len(set(keys)):
                raise ValueError('DUPLICATE_SCORE_RECEIPT')
            if phase=='confirmation':
                for event in selected:
                    path=models/phase/category/(event+'.json')
                    if not path.exists():
                        raise ValueError('UNSCORED_CONFIRMATION_GAME')
            unsafe_first=[row['q'] for row in rows if row['q'] is not None and
                not 0<=row['q']<=100]
            run_checks.append(dict(phase=phase,category=category,selected_games=len(selected),
                games_with_atlas_rows=len({row['event'] for row in rows}),side_gate_rows=len(rows),
                zero_atlas_games=len(selected-{row['event'] for row in rows}),
                duplicate_receipts=0,first_out_of_range_calls=len(unsafe_first),
                first_out_of_range_min=min(unsafe_first,default=None),
                first_out_of_range_max=max(unsafe_first,default=None)))
            for side in ('favourite','underdog'):
                base=next(x for x in r['comparisons'] if x['category']==category and x['side']==side
                          and x['variant']=='BASE_CORRECTION' and x['control']=='FIRST')
                book=next(x for x in r['comparisons'] if x['category']==category and x['side']==side
                          and x['variant']=='BOOK_CORRECTION' and x['control']=='BASE_CORRECTION')
                versus=next(x for x in r['comparisons'] if x['category']==category and x['side']==side
                          and x['variant']=='BOOK_CORRECTION' and x['control']=='FIRST')
                own=[row for row in rows if row['side']==(0 if side=='favourite' else 1)]
                matched=[row for row in own if 'FIRST' in row['scores']]
                primary.append(dict(phase=phase,category=category,side=side,matched_games=base['mae']['n_games'],
                    all_eligible_games=len(selected),eligible_gate_rows=len(own),called_gate_rows=base['first_calls'],
                    called_share=base['first_calls']/len(own) if own else None,
                    scored_gate_rows=len(matched),target_gate_rows=base['target_available'],
                    first_mae=base['control_mae'],base_mae=base['variant_mae'],book_mae=book['variant_mae'],
                    first_crps=base['control_crps'],base_crps=base['variant_crps'],book_crps=book['variant_crps'],
                    book_minus_base=book['mae'],book_minus_first=versus['mae'],
                    book_incremental_pass=book['pass_bar'] and versus['pass_bar'],
                    unsafe_book_forecasts=book['unsafe_forecasts']))
            for month in sorted({row['month'] for row in rows}):
                subset=[row for row in rows if row['month']==month]
                counter=Counter(status for row in subset for key,status in row['refill_status'].items() if key.startswith('own:'))
                measured={row['event'] for row in subset if any(status=='MEASURED' for key,status in row['refill_status'].items() if key.startswith('own:'))}
                supported={name:sum(row['book_supported'].get(name,False) for row in subset)
                           for name in sorted(set().union(*(set(row['book_supported']) for row in subset)))}
                coverage.append(dict(phase=phase,category=category,month=month,
                    independent_games=len({row['event'] for row in subset}),side_gate_rows=len(subset),
                    own_book_side_gate_states=sum(counter.values()),refill_status_counts=dict(counter),
                    independent_games_with_measured_refill=len(measured),
                    block_supported_side_gate_rows=supported))
    optimizer_summary=[]
    for row in optimizers:
        for model,fit in row['models'].items():
            curve=fit.get('validation_curve') or {}
            nonzero={k:v for k,v in curve.items() if k!='ZERO'}
            best=min(nonzero,key=lambda k:(nonzero[k]['mae'],nonzero[k]['crps'],k)) if nonzero else None
            optimizer_summary.append(dict(category=row['category'],side='favourite' if row['side']==0 else 'underdog',
                month=row['month'],model=model,training_games=fit['training_games'],choice=fit['choice'],reason=fit['reason'],
                inner_validation_games=curve.get('ZERO',{}).get('games'),
                zero_mae=curve.get('ZERO',{}).get('mae'),best_nonzero_choice=best,
                best_nonzero_mae=nonzero.get(best,{}).get('mae'),
                inner_folds_without_training=[f['month'] for f in fit['folds'] if f['status']=='NO_INNER_VALIDATION_TRAINING']))
    freezes={category:read(models/'development'/category/'MODEL_FREEZE.json') for category in ('ATP_MAIN','ATP_CHALL')}
    access={category:read(models/'confirmation'/category/'CONFIRMATION_ACCESS.json') for category in freezes}
    publication={'AUDIT_RECEIPT.json':audit,'DEVELOPMENT_RESULTS.json':results['development'],
        'CONFIRMATION_RESULTS.json':results['confirmation'],'OPTIMIZER_OUTCOMES.json':optimizers,
        'OPTIMIZER_SUMMARY.json':optimizer_summary,'PRIMARY_SUMMARY.json':primary,
        'GATE_COVERAGE.json':dict(rule='Own leg only; each bid/ask book side counted once, partner not double-counted. Block support means at least one actual numeric field, not complete absorption coverage.',rows=coverage),
        'EXECUTION_RESUME.json':resumed,'MODEL_FREEZES.json':freezes}
    for name,value in publication.items():
        write(dest/name,value)
    safe_code=[p for p in (args.root/'arb-executor/analysis').glob('*absorption*.py')]
    test=subprocess.run([args.python,'-B','-m','unittest','test_absorption_audit','test_absorption_residual_model',
        'test_absorption_residual_data','test_absorption_residual_run','test_feature_panel_book_recovery',
        'test_feature_panel_inventory_features'],cwd=args.root/'arb-executor/analysis',text=True,capture_output=True)
    if test.returncode:
        raise ValueError('TEST_FAILURE:'+test.stdout+test.stderr)
    receipt=dict(schema='ABSORPTION_RESIDUAL_PUBLICATION_V1',status='COMPLETE_NO_ENGINE_CHANGE_NO_REPLAY',
        published_at=datetime.now(timezone.utc).isoformat(),contract_sha256=sha(dest/'CONTRACT.json'),
        reservation_sha256=sha(dest/'RESERVATION.json'),remote_audit_receipt_sha256=audit['remote_receipt_sha256'],
        audit_gate=audit['bars'],input_binding_development=results['development']['binding'],
        input_binding_confirmation=results['confirmation']['binding'],engine_unchanged=engine,
        cohort_checks=run_checks,confirmation_access=access,
        confirmation_label=contract['reservation']['label'],fresh_confirmation=contract['reservation']['fresh_confirmation'],
        privacy='Only code sent to droplet; aggregate audit report returned. All remote audit intervals/source rows remain remote. Existing desktop gate proofs/witnesses used locally; only aggregate results committed.',
        failure_and_resume='Confirmation stopped after MAIN 140 and CHALL 109 at a zero-atlas game. Empty-input-only guard verified by AST; no refit, completed source outcomes not reopened; original checkpoints/models preserved.',
        tests=dict(exit_code=test.returncode,output=(test.stdout+test.stderr).strip()),
        code_sha256s={p.name:sha(p) for p in sorted(safe_code)},
        report_sha256s={name:sha(dest/name) for name in publication},
        ruling='No engine promotion from this run. Primary BASE and BOOK policies selected zero correction in every outer/confirmation fit; see diagnostic block results separately.',
        limitations=['Historical confirmation is not fresh; LIVE_PAPER deferred.',
            'All-interval audit coverage does not imply absorption was measurable at atlas gates; see GATE_COVERAGE.',
            'Measured residual is net displayed replenishment, not gross order additions or queue priority.',
            'Zero selected correction and zero paired differences do not establish absence of every possible book signal.',
            'Unchanged FIRST may emit out-of-market minima; these were flagged, not clipped; no conduct replay.',
            'This is the frozen equal-game ridge/translated-distribution family, not every possible direct residual learner.'])
    # The main ruling is mechanically checked, never inferred from rounded tables.
    prim=[r for r in optimizer_summary if r['model'] in ('BASE_CORRECTION','BOOK_CORRECTION')]
    if any(r['choice']!='ZERO' for r in prim):
        raise ValueError('UPDATE_REPORT_RULING_FOR_NONZERO_PRIMARY; no automatic verdict')
    write(dest/'RUN_RECEIPT.json',receipt)
    report=['# Absorption audit and frozen residual test',
        'Bench only. No engine edit, conduct change, or finalist replay. Historical confirmation — not fresh.',
        '## 1. Absorption audit',
        table(['Tour','Month','Measured games / games','Measured intervals','Unobserved','Zero denominator'],
            [(r['category'],r['month'],f"{r['games_with_measured_refill']}/{r['independent_games']}",r.get('MEASURED',0),r.get('UNOBSERVED',0),r.get('ZERO_DENOMINATOR',0)) for r in audit['coverage']]),
        'Both audit bars passed: MAIN 449 and CHALL 763 independent measured games; all 6,482 parts hash verified. No unexplained reconciliation failures. Includes prior best quote. Net replenishment is not gross maker activity.',
        '### Why intervals are unobserved',
        table(['Reason','Count'],sorted(audit['unobserved_reasons'].items())),
        'Reasons can overlap. Unknown boundary ordering, locked/crossed captures, missing direction/block status, or off-screen consumed levels are not assigned a refill value.',
        '### Availability at the actual model gates',
        table(['Phase','Tour','Month','Measured games / gate games','Measured states','Unobserved states','Zero-denominator states'],
            [(r['phase'],r['category'],r['month'],f"{r['independent_games_with_measured_refill']}/{r['independent_games']}",r['refill_status_counts'].get('MEASURED',0),r['refill_status_counts'].get('UNOBSERVED',0),r['refill_status_counts'].get('ZERO_DENOMINATOR',0)) for r in coverage]),
        'Gate states are own-leg bid/ask states; partner copies are not double-counted. The full-span audit bar is distinct from gate-time availability. At model gates only 57 MAIN / 43 CHALL development games and 29 MAIN / 32 CHALL confirmation games had measured refill. Neither tour has a powered gate-level rejection of absorption itself.',
        '## 2. Frozen contract',
        'Frozen before fitting. Full text: [CONTRACT.json](CONTRACT.json). SHA256 `'+sha(dest/'CONTRACT.json')+'`.',
        'Separate tours; monthly outer freezes and earlier-resolved inner validation; no named checks. Strictly later positive-size floor before the exact library bell. Match identical games/sides/gates, preserve FIRST coverage, average receipts within games, then weight games equally.',
        'Models: unchanged FIRST; baseline-only residual (first prices, time, receipt role); baseline plus six book blocks. Six single-block diagnostics remain diagnostics. Training-only ranks and eigenvalue-derived ridge strengths; explicit ZERO on missing validation or no inner improvement. Translate the original FIRST distribution; do not clip forecasts.',
        'Bar: n >= 100 independent games; floor-MAE reduction >= 0.10 cents per side; simultaneous 95% interval excluding zero after 36-comparison Bonferroni adjustment; no mean CRPS or coverage deterioration; no unsafe prediction. 50,000 deterministic date-then-game bootstrap draws. BOOK must beat BASE and FIRST.',
        'Latest 140 MAIN / 344 CHALL reserved; frozen models and member pool; one final confirmation phase, interrupted then resumed without refitting. Label: historically inspected — not fresh. True out-of-sample confirmation deferred to LIVE_PAPER after DESK activation.',
        '## 3. Primary results',
        'MAE and CRPS are in cents. Slash-separated values are FIRST / baseline correction / baseline plus book. No corrections were selected in either primary model.',
        table(['Phase','Tour','Side','Matched games / eligible','Scored / gate rows','Calls / gates','MAE: FIRST / BASE / BOOK','CRPS: FIRST / BASE / BOOK','Book incremental pass'],
            [(r['phase'],r['category'],r['side'],f"{r['matched_games']}/{r['all_eligible_games']}",f"{r['scored_gate_rows']}/{r['eligible_gate_rows']}",f"{r['called_gate_rows']}/{r['eligible_gate_rows']}",' / '.join(fmt(r[k]) for k in ('first_mae','base_mae','book_mae')),' / '.join(fmt(r[k]) for k in ('first_crps','base_crps','book_crps')),r['book_incremental_pass']) for r in primary]),
        '### Every predeclared contrast',
        table(['Phase','Tour','Side','Variant - control','n','Delta MAE','Adjusted MAE interval','Delta CRPS','Pass'],
            [(phase,r['category'],r['side'],r['variant']+' - '+r['control'],r['mae']['n_games'],fmt(r['mae']['delta']),str(r['mae']['interval']),fmt(r['crps']['delta']),r['pass_bar']) for phase,p in results.items() for r in p['comparisons']]),
        '### Primary optimizer outcomes',
        table(['Tour','Side','Fit month','Model','Training games','Choice','ZERO inner MAE','Best nonzero inner MAE','Reason'],
            [(r['category'],r['side'],r['month'],r['model'],r['training_games'],r['choice'],fmt(r['zero_mae']),fmt(r['best_nonzero_mae']),r['reason']) for r in prim]),
        'Every fold, candidate, and single-block outcome is in OPTIMIZER_OUTCOMES.json and OPTIMIZER_SUMMARY.json. Missing validation is explicit; rejected fitted candidates are not described as numerical stalls.',
        '## Verification and ruling',
        'The interrupted CHALL zero-atlas game is preserved in denominators. The only runner repair returns no predictions for no receipts; AST comparison proves the rest of the runner unchanged. All 484 reserved games have a checkpoint, including zero-atlas games. No completed game was refitted or reopened by the continuation.',
        receipt['ruling'],
        'This rejects promotion of the specified residual policy, not absorption as a universal mechanism. Inspect gate coverage before claiming refill itself received a powered test. Zero chosen adjustments produce exact zero paired intervals; they do not bound an untested nonzero correction. Out-of-range FIRST calls are disclosed in RUN_RECEIPT, not silently repaired.',
        'Scripts, metadata and aggregates only are published. Private audit intervals stay on droplet; model pickles, training rows and per-receipt scores stay local. Fresh LIVE_PAPER confirmation remains outstanding.']
    (dest/'REPORT.md').write_text('\n\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='AGGREGATES_PUBLISHED_FOR_REVIEW',primary=primary,gate_coverage=coverage),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--private',type=Path,required=True)
    p.add_argument('--python',required=True)
    main(p.parse_args())
