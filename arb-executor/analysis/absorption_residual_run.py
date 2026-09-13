"""Audit-gated, frozen-contract residual test. Bench only; no OS/replay calls.

Development and confirmation are separate commands. Private rows/models stay
under --out, outside the repository. Confirmation refuses an existing final
receipt and only resumes identically bound per-game score checkpoints.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import pickle
import re
import time
import numpy as np

from absorption_residual_data import (BLOCKS, BASE_FIELDS, load_selected_pairs,
    prepare_rows, span_hash)
from absorption_residual_model import (RidgeFamily, translated_scores, game_weights,
    paired_game_losses, clustered_interval, promotion_bar)
from feature_panel_inventory_gate_extract import digest, encoded
from feature_panel_run import git_json, BASELINES
from conduct_scoreboard import verify_reference
import tune_bench_v2_survivorship as reference


MODELS = ('BASE_CORRECTION', 'BOOK_CORRECTION')+tuple('BASE_PLUS_'+b for b in BLOCKS)
CATEGORIES = ('ATP_MAIN', 'ATP_CHALL')


def numerical_contract(root,category):
    relative='arb-executor/analysis/tune_bench_v2_ticks/'+category+'/TUNE_BENCH_RECEIPT.json'
    receipt,source=git_json(root,BASELINES[category],relative)
    c=receipt['organ_contract']
    engine=(root/'arb-executor/analysis/window1_v54_dual_belief_os.js').read_text(encoding='utf-8')
    par=int(re.search(r'const CONTRACT_SUM_CENTS = (\d+);',engine)[1])
    if c['gates_minutes_to_bell']!=list(reference.GATES) or c['quantiles']!=list(reference.QUANTILES):
        raise ValueError('REFERENCE_ATLAS_CONTRACT_DRIFT')
    return c,dict(receipt=source,reference=verify_reference(reference,root),
                  no_named_checks_or_population_scoreboards_opened=True),par


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp=path.with_suffix(path.suffix+'.partial')
    temp.write_bytes(encoded(value)+b'\n')
    temp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def clean(value):
    if isinstance(value, dict):
        return {k:clean(v) for k,v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def columns(model):
    if model=='BASE_CORRECTION':
        return ()
    return BLOCKS if model=='BOOK_CORRECTION' else (model.removeprefix('BASE_PLUS_'),)


def features(row, model):
    result=dict(row['base_features'])
    for block in columns(model):
        result.update({block+':'+k:v for k,v in row['blocks'][block].items()})
    return result


def supported(row, model):
    return any(v is not None and math.isfinite(v) for block in columns(model)
               for v in row['blocks'][block].values())


def matrix(rows, names, model):
    dictionaries=[features(r,model) for r in rows]
    return np.asarray([[r.get(n) for n in names] for r in dictionaries],dtype=float).reshape((len(rows),len(names)))


def predict(fitted, rows):
    if fitted['family'] is None:
        return np.zeros(len(rows))
    return fitted['family'].predict(matrix(rows,fitted['names'],fitted['model']),fitted['choice'])


class Learner:
    """Expanding inner months with recursive earlier-only baseline fallback."""
    def __init__(self, metadata, quantiles):
        self.metadata,self.quantiles,self.cache=metadata,quantiles,{}
        self.month_cutoffs={month:min(r['formation_epoch'] for r in metadata.values()
            if r['event_date'][:7]==month) for month in sorted({r['event_date'][:7] for r in metadata.values()})}

    def learn(self, training, model):
        events=tuple(sorted({r['event'] for r in training}))
        side=training[0]['side'] if training else None
        key=(events,side,model)
        if key in self.cache:
            return self.cache[key]
        base=dict(model=model, family=None, choice='ZERO', names=list(BASE_FIELDS),
                  reason='NO_EARLIER_TRAINING', folds=[], training_games=len(events))
        if not training:
            self.cache[key]=base
            return base
        names=tuple(BASE_FIELDS)+tuple(sorted(set().union(*(set(features(r,model))-set(BASE_FIELDS) for r in training))))
        candidates=defaultdict(list)
        strengths=defaultdict(list)
        for month in sorted({r['month'] for r in training}):
            cutoff=self.month_cutoffs[month]
            inner=[r for r in training if r['month']<month and r['bell']<cutoff]
            validation=[r for r in training if r['month']==month]
            fold=dict(month=month,cutoff=cutoff,training_games=len({r['event'] for r in inner}),
                      validation_games=len({r['event'] for r in validation}))
            if not inner or not validation:
                fold['status']='NO_INNER_VALIDATION_TRAINING'
                base['folds'].append(fold)
                continue
            inner_names=tuple(BASE_FIELDS)+tuple(sorted(set().union(*(set(features(r,model))-set(BASE_FIELDS) for r in inner))))
            family=RidgeFamily.fit(matrix(inner,inner_names,model),[r['target']-r['q'] for r in inner],
                [r['event'] for r in inner],inner_names,self.quantiles)
            fallback=self.learn(inner,'BASE_CORRECTION') if model!='BASE_CORRECTION' else None
            fallback_prediction=predict(fallback,validation) if fallback else None
            missing=np.asarray([not supported(r,model) for r in validation]) if fallback else None
            x=matrix(validation,inner_names,model)
            fold['status']='VALIDATED'
            fold['candidate_scores']={}
            for choice in ('ZERO',*family.strengths):
                correction=family.predict(x,choice)
                if fallback is not None:
                    correction[missing]=fallback_prediction[missing]
                losses=[]
                for row,shift in zip(validation,correction):
                    score=translated_scores(row,float(shift))
                    record=dict(event=row['event'],mae=score['mae'],crps=score['crps'])
                    losses.append(record)
                candidates[choice].extend(losses)
                strength=family.strengths.get(choice,0)
                strengths[choice].append(strength)
                w=game_weights([r['event'] for r in losses])
                fold['candidate_scores'][choice]=dict(mae=float(w@np.asarray([r['mae'] for r in losses])),
                    crps=float(w@np.asarray([r['crps'] for r in losses])),ridge_strength=strength)
            base['folds'].append(fold)
        if not candidates:
            base['reason']='NO_INNER_VALIDATION; ZERO_CORRECTION'
            self.cache[key]=base
            return base
        curves={}
        for choice,rows in candidates.items():
            w=game_weights([r['event'] for r in rows])
            curves[choice]=dict(mae=float(w@np.asarray([r['mae'] for r in rows])),
                crps=float(w@np.asarray([r['crps'] for r in rows])),
                strength_tiebreak=float(np.median(strengths[choice])),games=len(set(r['event'] for r in rows)))
        best=min(curves,key=lambda k:(curves[k]['mae'],curves[k]['crps'],-curves[k]['strength_tiebreak'],k))
        base['validation_curve']=curves
        if curves[best]['mae']>=curves['ZERO']['mae']:
            base['reason']='ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT'
            self.cache[key]=base
            return base
        family=RidgeFamily.fit(matrix(training,names,model),[r['target']-r['q'] for r in training],
            [r['event'] for r in training],names,self.quantiles)
        base.update(family=family,choice=best,names=names,reason='SELECTED_BY_EARLIER_INNER_VALIDATION',
                    fit=family.receipt(best))
        self.cache[key]=base
        return base


def scored_rows(rows, fitted, par):
    if not rows:
        return []
    result=[]
    base=predict(fitted['BASE_CORRECTION'],rows)
    changes={m:predict(fitted[m],rows) for m in MODELS}
    for m in MODELS:
        if m!='BASE_CORRECTION':
            missing=np.asarray([not supported(r,m) for r in rows])
            changes[m][missing]=base[missing]
    for index,row in enumerate(rows):
        item={k:row[k] for k in ('event','date','month','category','side','leg','gate','q','target','ess','member_count')}
        item.update(scores={},fallback={},unsafe={})
        if row['q'] is not None:
            item['forecasts']={'FIRST':row['q'],**{m:row['q']+float(changes[m][index]) for m in MODELS}}
            if row['target'] is not None:
                item['scores']['FIRST']=row['first_scores']
                for m in MODELS:
                    item['scores'][m]=translated_scores(row,float(changes[m][index]))
            for m in MODELS:
                item['fallback'][m]=m!='BASE_CORRECTION' and not supported(row,m)
                q=item['forecasts'][m]
                item['unsafe'][m]=not math.isfinite(q) or not 0<=q<=par
        item['book_supported']={m:supported(row,m) for m in MODELS if m!='BASE_CORRECTION'}
        item['refill_status']={k:v['status'] for k,v in row['refill_status'].items()}
        result.append(item)
    return result


def fit_receipt(fitted):
    return {name:{k:v for k,v in value.items() if k!='family'} for name,value in fitted.items()}


def reports(rows, contract, binding, phase, reservation):
    outcomes=[]
    contrasts=[('BASE_CORRECTION','FIRST'),('BOOK_CORRECTION','FIRST'),('BOOK_CORRECTION','BASE_CORRECTION')]
    contrasts += [('BASE_PLUS_'+b,'BASE_CORRECTION') for b in BLOCKS]
    comparisons=len(contrasts)*2*len(CATEGORIES)
    bar=contract['inference']['bar']
    for category in CATEGORIES:
        for side in (0,1):
            selected=[r for r in rows if r['category']==category and r['side']==side]
            for variant,control in contrasts:
                key='|'.join((phase,category,str(side),variant,control))
                mae=clustered_interval(paired_game_losses(selected,variant,control,'mae'),
                    seed_material=binding['contract_sha256']+'|'+key+'|MAE',draws=contract['inference']['bootstrap_draws'],comparisons=comparisons)
                crps=clustered_interval(paired_game_losses(selected,variant,control,'crps'),
                    seed_material=binding['contract_sha256']+'|'+key+'|CRPS',draws=contract['inference']['bootstrap_draws'],comparisons=comparisons)
                paired=paired_game_losses(selected,variant,control,'mae')
                paired_crps=paired_game_losses(selected,variant,control,'crps')
                called=sum(r.get('q') is not None for r in selected)
                variant_calls=sum(variant in r.get('forecasts',{}) for r in selected)
                control_calls=sum(control in r.get('forecasts',{}) for r in selected)
                coverage_preserved=all((variant in r.get('forecasts',{})) == (control in r.get('forecasts',{})) for r in selected)
                unsafe=sum(r['unsafe'].get(variant,False) for r in selected)
                decision=promotion_bar(mae,crps,minimum_games=bar['minimum_independent_matched_games'],
                    minimum_effect=bar['minimum_floor_mae_improvement_cents'],coverage_preserved=coverage_preserved,unsafe=unsafe)
                outcomes.append(dict(category=category,side='favourite' if side==0 else 'underdog',variant=variant,control=control,
                    mae=mae,crps=crps,variant_mae=math.fsum(x['variant'] for x in paired)/len(paired) if paired else None,
                    control_mae=math.fsum(x['control'] for x in paired)/len(paired) if paired else None,
                    variant_crps=math.fsum(x['variant'] for x in paired_crps)/len(paired_crps) if paired_crps else None,
                    control_crps=math.fsum(x['control'] for x in paired_crps)/len(paired_crps) if paired_crps else None,
                    eligible_universe_games=reservation['categories'][category]['development_games' if phase=='development' else 'reserved_games'],
                    games_with_atlas_opportunities=len({r['event'] for r in selected}),eligible_gate_opportunities=len(selected),
                    first_calls=called,variant_calls=variant_calls,control_calls=control_calls,
                    target_available=sum(r['target'] is not None for r in selected),
                    book_supported=sum(r['book_supported'].get(variant,False) for r in selected),
                    base_fallback=sum(r['fallback'].get(variant,False) for r in selected),unsafe_forecasts=unsafe,**decision))
    return dict(schema='ABSORPTION_RESIDUAL_RESULTS_V1',phase=phase,binding=binding,comparisons=outcomes,
        confirmation_label=contract['reservation']['label'] if phase=='confirmation' else None,
        fresh_confirmation=contract['reservation']['fresh_confirmation'])


def bind(args):
    contract_path=args.root/'arb-executor/analysis/absorption_residual_v1/CONTRACT.json'
    reservation_path=contract_path.with_name('RESERVATION.json')
    contract=json.loads(contract_path.read_text(encoding='utf-8'))
    reservation=json.loads(reservation_path.read_text(encoding='utf-8'))
    pins=json.loads(contract_path.with_name('INPUTS.json').read_text(encoding='utf-8'))
    for path,key in ((contract_path,'contract_sha256'),(reservation_path,'reservation_sha256'),
        (args.gates,'gate_inputs_sha256'),(args.gate_receipt,'gate_receipt_sha256'),
        (args.witnesses,'witness_sha256'),(args.source_receipt,'source_receipt_sha256')):
        if digest(path)!=pins[key]:
            raise ValueError('PRE_FIT_PIN_MISMATCH:'+key)
    for name,sha in pins['engine_unchanged'].items():
        if digest(args.root/'arb-executor/analysis'/name)!=sha:
            raise ValueError('ENGINE_HASH_CHANGED:'+name)
    if digest(reservation_path)!=contract['reservation']['sha256']:
        raise ValueError('FROZEN_RESERVATION_HASH_DRIFT')
    audit=json.loads(args.audit.read_text(encoding='utf-8'))
    if (audit['status']!='AUDIT_COMPLETE' or audit['unexplained_reconciliation_failures']
        or any(not audit['bars'][cat]['pass'] or audit['bars'][cat]['measured_independent_games']<contract['audit_gate']['minimum_measured_independent_games_per_tour'] for cat in CATEGORIES)
        or not audit.get('all_part_hashes_verified') or audit.get('verified_parts')!=6482
        or not audit.get('remote_receipt_sha256')):
        raise ValueError('AUDIT_GATE_NOT_PASSED_AND_HASH_VERIFIED')
    if audit['binding']['recovery_receipt_sha256']!=pins['remote_recovery_receipt_sha256']:
        raise ValueError('AUDIT_RECOVERY_PIN_MISMATCH')
    durable=args.root/'arb-executor/data/durable'
    library=durable/'RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz'
    counts=durable/'RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz'
    gate_receipt=json.loads(args.gate_receipt.read_text(encoding='utf-8'))
    if (not gate_receipt['complete'] or gate_receipt['status']!='VERIFIED'
        or digest(args.gates)!=gate_receipt['output']['sha256']
        or digest(library)!=reservation['library_sha256']
        or gate_receipt['recovery_receipt_sha256']!=audit['binding']['recovery_receipt_sha256']
        or gate_receipt['library_sha256']!=reservation['library_sha256']):
        raise ValueError('GATE_SOURCE_BINDING_MISMATCH')
    source=json.loads(args.source_receipt.read_text(encoding='utf-8'))
    if digest(args.witnesses)!=source['outputs']['POSITIVE_PRINT_WITNESSES.jsonl.gz']['sha256']:
        raise ValueError('WITNESS_HASH_MISMATCH')
    count_receipt=json.loads(counts.with_name('RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS_RECEIPT.json').read_text())
    if digest(counts)!=count_receipt['output']['sha256'] or count_receipt['library']['sha256']!=reservation['library_sha256']:
        raise ValueError('SIDECAR_HASH_MISMATCH')
    binding=dict(contract_sha256=digest(contract_path),reservation_sha256=digest(reservation_path),
        input_pins_sha256=digest(contract_path.with_name('INPUTS.json')),
        audit_aggregate_sha256=digest(args.audit),remote_audit_receipt_sha256=audit['remote_receipt_sha256'],
        library_sha256=digest(library),counts_sha256=digest(counts),gate_inputs_sha256=digest(args.gates),
        gate_receipt_sha256=digest(args.gate_receipt),witness_sha256=digest(args.witnesses),source_receipt_sha256=digest(args.source_receipt),
        code={n:digest(Path(__file__).with_name(n)) for n in ('absorption_residual_run.py','absorption_residual_data.py',
            'absorption_residual_model.py','feature_panel_scoring.py','feature_panel_bench.py','feature_panel_run.py',
            'feature_panel_inventory_gate_extract.py','conduct_scoreboard_v2.py','conduct_scoreboard.py',
            'tune_bench_v2_survivorship.py','tune_bench_floor_calls.py')})
    if args.out.resolve().is_relative_to(args.root.resolve()):
        raise ValueError('PRIVATE_OUTPUT_MUST_BE_OUTSIDE_REPOSITORY')
    return contract,reservation,binding,library,counts


def run(args):
    contract,reservation,binding,library,counts=bind(args)
    args.out.mkdir(parents=True,exist_ok=True)
    boundfile=args.out/'INPUT_BINDING.json'
    if boundfile.exists() and json.loads(boundfile.read_text())!=binding:
        raise ValueError('RUN_BINDING_DRIFT')
    atomic(boundfile,binding)
    if (args.out/(args.phase.upper()+'_RESULTS.json')).exists():
        raise ValueError('FINAL_PHASE_ALREADY_REPORTED')
    if args.phase=='confirmation' and not (args.out/'DEVELOPMENT_RESULTS.json').exists():
        raise ValueError('BOTH_TOURS_DEVELOPMENT_MUST_FINISH_BEFORE_CONFIRMATION')
    phase_dir=args.out/args.phase
    phase_dir.mkdir(exist_ok=True)
    started=time.monotonic()
    combined=[]
    optimizers=[]
    for category in CATEGORIES:
        spec=reservation['categories'][category]
        metadata={r['event_id']:dict(r,event_date=__import__('tune_bench_v2_survivorship').date_key(r['event_id'])) for r in spec['development']}
        c,proof,par=numerical_contract(args.root,category)
        pairs,leg_meta=load_selected_pairs(library,counts,metadata)
        private=phase_dir/category
        private.mkdir(exist_ok=True)
        if args.phase=='development':
            rows=[]
            for event,items in prepare_rows(pairs,pairs,args.gates,args.witnesses,leg_meta,c,par):
                rows.extend(items)
                print('PREPARED '+json.dumps(dict(phase=args.phase,category=category,event=event,rows=len(rows))),flush=True)
            # Checkpoint preserves the exact preparation without publishing it.
            with gzip.open(private/'TRAINING_ROWS.json.gz','wt',encoding='utf-8') as out:
                json.dump(clean(rows),out,allow_nan=False,separators=(',',':'))
            learner=Learner(metadata,c['quantiles'])
            category_scores=[]
            for month in sorted({r['month'] for r in rows}):
                cutoff=learner.month_cutoffs[month]
                for side in (0,1):
                    training=[r for r in rows if r['side']==side and r['month']<month and r['bell']<cutoff and 'first_scores' in r]
                    testing=[r for r in rows if r['side']==side and r['month']==month]
                    fitted={m:learner.learn(training,m) for m in MODELS}
                    category_scores.extend(scored_rows(testing,fitted,par))
                    optimizers.append(dict(category=category,side=side,month=month,cutoff=cutoff,models=fit_receipt(fitted)))
                    print('MONTH_SCORED '+json.dumps(dict(category=category,side=side,month=month,rows=len(testing))),flush=True)
            # Freeze confirmation fits without opening any reserved data.
            min_date=min(__import__('tune_bench_v2_survivorship').date_key(r['event_id']) for r in spec['reserved'])
            frozen={}
            for side in (0,1):
                training=[r for r in rows if r['side']==side and r['bell']<spec['confirmation_cutoff'] and r['date']<min_date and 'first_scores' in r]
                frozen[side]={m:learner.learn(training,m) for m in MODELS}
                optimizers.append(dict(category=category,side=side,month='CONFIRMATION_FROZEN',cutoff=spec['confirmation_cutoff'],models=fit_receipt(frozen[side])))
            model_path=private/'CONFIRMATION_MODELS.pkl'
            model_path.write_bytes(pickle.dumps(frozen,protocol=pickle.HIGHEST_PROTOCOL))
            atomic(private/'MODEL_FREEZE.json',dict(binding=binding,model_sha256=digest(model_path),frozen_before_confirmation=True,
                first_reserved_formation=spec['confirmation_cutoff'],first_reserved_event_date=min_date,
                reference=proof,models={str(s):fit_receipt(v) for s,v in frozen.items()}))
            atomic(private/'SCORES.json',clean(category_scores))
            combined.extend(category_scores)
        else:
            saved=args.out/'development'/category
            freeze=json.loads((saved/'MODEL_FREEZE.json').read_text())
            model_path=saved/'CONFIRMATION_MODELS.pkl'
            if freeze['binding']!=binding or digest(model_path)!=freeze['model_sha256']:
                raise ValueError('FROZEN_MODEL_HASH_MISMATCH')
            frozen=pickle.loads(model_path.read_bytes())
            selected={r['event_id']:r for r in spec['reserved']}
            # This is the first reserved-outcome decode in the experiment.
            atomic(private/'CONFIRMATION_ACCESS.json',dict(started_at=now(),binding=binding,
                label=contract['reservation']['label'],model_sha256=freeze['model_sha256']))
            queries,query_meta=load_selected_pairs(library,counts,selected)
            members=[p for p in pairs if p.bell<spec['confirmation_cutoff']]
            category_scores=[]
            for event,items in prepare_rows(queries,members,args.gates,args.witnesses,query_meta,c,par):
                checkpoint=private/(event+'.json')
                if checkpoint.exists():
                    part=json.loads(checkpoint.read_text())
                    if part['binding']!=binding:
                        raise ValueError('CONFIRMATION_CHECKPOINT_BINDING_DRIFT')
                else:
                    scores=[]
                    for side in (0,1):
                        scores.extend(scored_rows([r for r in items if r['side']==side],frozen[side],par))
                    part=dict(binding=binding,scores=clean(scores))
                    atomic(checkpoint,part)
                category_scores.extend(part['scores'])
                print('CONFIRMATION_SCORED '+event,flush=True)
            atomic(private/'SCORES.json',clean(category_scores))
            combined.extend(category_scores)
        atomic(args.out/'RUN_STATE.json',dict(phase=args.phase,category_complete=category,elapsed_seconds=time.monotonic()-started,status='SCORING'))
    result=reports(combined,contract,binding,args.phase,reservation)
    # Source and code snapshot must still match after scoring, before any
    # result is marked complete or its frozen models can be confirmed.
    if bind(args)[2]!=binding:
        raise ValueError('INPUT_OR_CODE_CHANGED_DURING_RUN')
    atomic(args.out/(args.phase.upper()+'_RESULTS.json'),result)
    if optimizers:
        atomic(args.out/'OPTIMIZER_OUTCOMES.json',optimizers)
    atomic(args.out/'RUN_STATE.json',dict(status=args.phase.upper()+'_COMPLETE',elapsed_seconds=time.monotonic()-started,completed_at=now()))
    print(args.phase.upper()+'_COMPLETE '+json.dumps(dict(elapsed_seconds=time.monotonic()-started)),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('root','out','audit','gates','gate-receipt','witnesses','source-receipt'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--phase',choices=('development','confirmation'),required=True)
    args=p.parse_args()
    try:
        run(args)
    except BaseException as exc:
        if args.out.exists():
            atomic(args.out/'RUN_STATE.json',dict(status='FAILED',phase=args.phase,error=repr(exc),at=now()))
        raise


if __name__=='__main__':
    main()
