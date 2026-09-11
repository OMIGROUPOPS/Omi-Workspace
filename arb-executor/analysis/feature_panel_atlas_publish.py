"""Verify screens, publish only compact aggregates, never raw private arrays."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import feature_panel_atlas as atlas
import feature_panel_atlas_run as screen
import feature_panel_bench as bench
import feature_panel_report as report
import feature_panel_run as launcher


def validate_screen(directory):
    run=report.read_run(directory)
    receipt=run['receipt']
    if receipt.get('evaluation_cadence')!='GATE-SIM' or receipt.get('screen_only') is not True:
        raise ValueError('NOT_AN_ATLAS_SCREEN')
    queries_file=launcher.json_file(Path(directory)/'FEATURE_PANEL_QUERIES.json')
    counts={}
    for stream in ('PRIMARY','STRICT_HOLDOUT'):
        queries=[q for q in queries_file if q['stream']==stream]
        if any(q['counts'].get('receipts',0)!=q['counts'].get('atlas_receipts',0) for q in queries):
            raise ValueError('NON_ATLAS_RECEIPT_IN_SCREEN')
        counts[stream]=dict(games=len(queries),gate_receipts=sum(q['counts'].get('receipts',0) for q in queries))
    selections=run['board'].get('selection_filed_scorable_gates')
    if not selections:raise ValueError('MISSING_NON_JUNE_SELECTION')
    if selections['contract']!=run['contract']:raise ValueError('SELECTION_CONTRACT_DRIFT')
    for cell in selections['groups']:
        group=cell['group']
        if group['stream']!='NON_JUNE_SELECTION_FILED_SCORABLE_GATES':raise ValueError('INVALID_SELECTION_STREAM')
        for target in cell['targets'].values():
            for result in target['matched_to_first'].values():
                expected=(result['n']>=run['contract']['minimum_matched_queries'] and
                    result['strictly_closer']>=run['contract']['minimum_strictly_closer_share']*result['n'])
                if (not result['filed_side_gate_scope'] or result['n']!=result['distinct_matched_games']
                        or result['qualifies']!=expected):raise ValueError('SELECTION_CRITERION_DRIFT')
    return run,counts


def first_gate_parity(screen_run,full_directory):
    other=launcher.json_file(Path(full_directory)/'FEATURE_PANEL_SCOREBOARD.json')
    def first(board):
        return {json.dumps(cell['group'],sort_keys=True):{name:target['all_eligible']['FIRST']
                for name,target in cell['targets'].items()} for cell in board['gates']['groups']}
    a,b=first(screen_run['board']),first(other)
    if a!=b:raise ValueError('UNCHANGED_FIRST_GATE_PARITY_FAILED')
    return dict(status='EXACT_FIRST_GATE_SCORE_PARITY',side_gate_cells=len(a),
        original_scoreboard_sha256=launcher.digest(Path(full_directory)/'FEATURE_PANEL_SCOREBOARD.json'))


def formatted(value):return '—' if value is None else f'{value:.6f}'


def markdown(result):
    out=[f"# {result['category']} — full-universe atlas screen",'',
        'GATE-SIM only; not a receipt-cadence proof. June is frozen and cannot select finalists.','']
    for stream in ('PRIMARY_ALL_RECEIPTS','STRICT_HOLDOUT_ALL_RECEIPTS'):
        out += ['## '+('Primary walk-forward' if stream.startswith('PRIMARY') else 'Separate frozen June holdout'),'',
            '| Variant | Called / eligible sides | CRPS ¢ | Floor MAE ¢ | Signed error ¢ | Timing MAE min | ESS | Δ floor MAE vs FIRST ¢ |',
            '|---|---:|---:|---:|---:|---:|---:|---:|']
        for row in result['rows']:
            if row['cohort']!='all_receipts' or row['stream']!=stream or row['target']!='reachable':continue
            metrics=row['metrics'];match=row.get('matched_to_first',{})
            values=[metrics[k]['mean'] for k in ('floor_crps_cents','floor_absolute_error_cents','floor_signed_error_cents','floor_timing_absolute_error_minutes')]
            delta=match.get('metrics',{}).get('floor_absolute_error_cents',{}).get('delta',{}).get('mean')
            out.append('| '+row['variant']+f" | {row['called_receipts']} / {row['eligible_receipts']} | "+
                ' | '.join(map(formatted,values+[row['ess']['mean'],delta]))+' |')
        out += ['','Displayed target: strictly later positive-size print floor; paired with its own timing target.','',
            '| Variant | Carried floor MAE ¢ | Carried timing MAE min | Family accuracy | 25–75% band coverage | q50 reach calibration gap |',
            '|---|---:|---:|---:|---:|---:|']
        for row in result['rows']:
            if row['cohort']!='all_receipts' or row['stream']!=stream or row['target']!='carried':continue
            metrics=row['metrics']
            values=[metrics[k]['mean'] for k in ('floor_absolute_error_cents','floor_timing_absolute_error_minutes',
                'family_accuracy','floor_band.q25_q75.coverage','reach.q50.calibration_gap')]
            out.append('| '+row['variant']+' | '+' | '.join(map(formatted,values))+' |')
        out += ['','All finite denominators, signed errors, quantiles and matched deltas are retained in JSON.','']
        conduct_stream='PRIMARY' if stream.startswith('PRIMARY') else 'STRICT_HOLDOUT'
        for cell in result.get('conduct_gate_sim',[]) or []:
            if cell['group']['stream']!=conduct_stream:continue
            out += ['### R0 — GATE-SIM only','',
                '| Variant | Eligible games | Completion | One-sided | Captured ¢ / eligible | Δ capture vs FIRST ¢ |',
                '|---|---:|---:|---:|---:|---:|']
            names=['FIRST']+[name for name in cell['variants'] if name!='FIRST']
            for name in names:
                row=cell['variants'][name];metrics=row['metrics']
                values=[metrics[k]['mean'] for k in ('completed','one_sided','captured_cents')]
                delta=cell['matched_to_first'].get(name,{}).get('captured_cents_delta',{}).get('mean')
                out.append('| '+name+f" | {row['eligible_events']} | "+' | '.join(map(formatted,values+[delta]))+' |')
            out += ['']
    out += ['## Filed selection — June excluded','',
        '| Variant | Cells with n ≥ filed minimum | Maximum strictly-closer share | Qualifying cells |',
        '|---|---:|---:|---:|']
    for name in sorted({r['variant'] for r in result['selection_cells']}):
        cells=[r for r in result['selection_cells'] if r['variant']==name and r['target']=='reachable']
        enough=[r for r in cells if r['n']>=result['score_contract']['minimum_matched_queries']]
        maximum=max((r['strictly_closer']/r['n'] for r in enough),default=None)
        out.append(f"| {name} | {len(enough)} | {formatted(maximum)} | {sum(bool(r['qualifies']) for r in cells)} |")
    out += ['','Advancing variants: '+(', '.join(result['advancement']['variants']) or 'NONE'),'',
        '## Optimizer outcomes','',
        '| Month | Variant | Outcome | Validation games | Inner statuses | Refit status |',
        '|---|---|---|---:|---|---|']
    for r in result['optimizer_outcomes']:
        statuses='; '.join(a['month']+': '+str(a['status']) for a in r['attempts']) or 'no inner fold'
        out.append(f"| {r['month']} | {r['variant']} | {r['outcome']} | {r['choice']['validation_games']} | {statuses} | {r['refit_status'] or 'not selected'} |")
    return '\n'.join(out)+'\n'


def publish(directory,destination,main_full=None):
    run,counts=validate_screen(directory)
    result=screen.summaries(directory)
    result['gate_counts']=counts
    result['score_contract']=run['contract']
    result['conduct_gate_sim']=[x for x in run['board']['all_receipts'].get('r0_conduct',[])
        if set(x['group'])=={'category','stream'}]
    result['first_parity']=(first_gate_parity(run,main_full) if main_full else
        dict(status='FIRST_EMITTER_IS_REFERENCE; synthetic byte-parity tests; no prior full feature run available'))
    result['publisher_sha256']=launcher.digest(Path(__file__))
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    bench.write_json(destination/'ATLAS_SCREEN_RESULTS.json',result)
    bench.write_json(destination/'OPTIMIZER_OUTCOMES.json',result['optimizer_outcomes'])
    # Source receipt contains hashes and aggregate lineage, never raw rows.
    bench.write_json(destination/'ATLAS_SCREEN_RECEIPT.json',dict(schema='FEATURE_PANEL_ATLAS_PUBLICATION_V1',
        category=result['category'],gate_counts=counts,source_receipt=run['receipt'],
        source_receipt_sha256=result['receipt_sha256'],
        source_scoreboard_sha256=launcher.digest(Path(directory)/'FEATURE_PANEL_SCOREBOARD.json'),
        results_sha256=launcher.digest(destination/'ATLAS_SCREEN_RESULTS.json'),
        optimizer_sha256=launcher.digest(destination/'OPTIMIZER_OUTCOMES.json'),
        private_data_copied=False,full_cadence_proof=False,first_parity=result['first_parity'],
        advancement=result['advancement'],publisher_sha256=result['publisher_sha256']))
    (destination/'SUMMARY.md').write_text(markdown(result),encoding='utf-8',newline='\n')
    print(json.dumps(dict(category=result['category'],counts=counts,advancing=result['advancement']['variants'],
        optimizer_outcomes=dict(Counter(r['outcome'] for r in result['optimizer_outcomes'])),
        results_sha256=launcher.digest(destination/'ATLAS_SCREEN_RESULTS.json'))),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--main-full',type=Path)
    a=p.parse_args();publish(a.run,a.out,a.main_full)


if __name__=='__main__':main()
