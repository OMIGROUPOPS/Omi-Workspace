#!/usr/bin/env python3
"""T31c — Layer B v1 coherence read.

Implements the four-check validation gate from layer_b_spec.md (post-T31a-patch-5):

1. Capture distributions are bounded by physical limits.
   - SPOT-CHECK: 10 (cell, limit_policy) pairs, re-walk a few tickers per pair,
     verify every fired trajectory has capture >= limit_c/100. This validates
     producer correctness directly (the spec wording 'capture_p10 across fired
     trajectories >= +Xc' is a tautology by the producer's fire condition;
     spot-checking individual fired captures is tighter than the percentile).
   - FLOOR: capture_p10 across all trajectories >= -1.00 from parquet.

2. Fire rates monotonic with policy aggressiveness.
   - Per (cell, limit policies sorted by limit_c), fire_rate non-increasing.
   - PASS if >= 95% of cells exhibit the trend.

3. Time-stop horizons capture more in positive-mean-bounce cells.
   - Filter Layer A cell_stats to cells with bounce_60min_mean > 0.
   - For each, sort Layer B time-stop policies by horizon, check capture_mean
     trends upward (Spearman correlation > 0). PASS if >= 60% of cells trend up.

4. Premarket vs in_match capture distributions differ in T21 Check 2's direction.
   - Self-join on (category, entry_band_lo, entry_band_hi, spread_band,
     volume_intensity, policy_type, policy_params).
   - Compute delta = in_match.capture_mean - premarket.capture_mean.
   - PASS if median(delta) > 0 (signed-rank test reported for completeness).

Foundation pointers: Layer B v1 (commit 28e8ab7), Layer A v1 (commit 1398c39),
G9 (commit ea84e74). T31a patch 5 corrected Check 1 wording.

Output: data/durable/layer_b_v1/coherence_report.md
Exit code: 0 = all PASS, 1 = any FAIL, 2 = any INCONCLUSIVE.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
import statistics
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).parent))
import cell_key_helpers as ckh
import build_layer_b_v1 as producer

LAYER_B_PARQUET = Path('data/durable/layer_b_v1/exit_policy_per_cell.parquet')
LAYER_A_PARQUET = Path('data/durable/layer_a_v1/cell_stats.parquet')
SAMPLE_MANIFEST = Path('data/durable/layer_a_v1/sample_manifest.json')
G9_CANDLES = Path('data/durable/g9_candles.parquet')
G9_METADATA = Path('data/durable/g9_metadata.parquet')
OUTPUT_REPORT = Path('data/durable/layer_b_v1/coherence_report.md')


def now_et():
    return datetime.now().strftime('%Y-%m-%d %I:%M:%S %p ET')


def log(msg, lines):
    print(msg)
    lines.append(msg)


def run_check_1_spot_check(layer_b_df, manifest, lines):
    """Spot-check: every fired trajectory has capture >= threshold."""
    log('', lines)
    log('## Check 1: Capture bounded by physical limits', lines)
    log('', lines)

    # Floor part — from parquet
    capture_p10_min = layer_b_df['capture_p10'].min()
    floor_pass = capture_p10_min >= -1.001
    log(f'Floor check (capture_p10 across all >= -100c): min={capture_p10_min:.4f} '
        f'-> {"PASS" if floor_pass else "FAIL"}', lines)

    # Spot-check part — re-walk trajectories for sampled (cell, limit_policy) pairs
    log('', lines)
    log('Spot-check: walking sampled trajectories to verify producer fire-condition', lines)

    # Pick 10 representative (cell, limit_c) pairs
    limit_rows = layer_b_df[layer_b_df['policy_type'] == 'limit'].copy()
    limit_rows['limit_c'] = limit_rows['policy_params'].apply(lambda s: json.loads(s)['limit_c'])

    # Sample: spread across channels, categories, limit thresholds
    sample_pairs = []
    rng_seed = 42
    rng = pd.np.random if hasattr(pd, 'np') else None
    import random
    random.seed(rng_seed)

    # Stratified sample: 5 premarket + 5 in_match, varied limit_c and category
    pre = limit_rows[limit_rows['channel'] == 'premarket']
    inm = limit_rows[limit_rows['channel'] == 'in_match']
    pre_sample = pre.sample(n=min(5, len(pre)), random_state=rng_seed)
    inm_sample = inm.sample(n=min(5, len(inm)), random_state=rng_seed)
    sample_df = pd.concat([pre_sample, inm_sample], ignore_index=True)

    log(f'Sampled {len(sample_df)} (cell, limit_policy) pairs '
        f'({len(pre_sample)} premarket, {len(inm_sample)} in_match)', lines)

    # Build cell_key string from row to look up manifest
    def regime_for_channel(ch):
        return 'premarket' if ch == 'premarket' else 'in_match'

    # ENTRY_BANDS index lookup
    eb_lookup = {(lo, hi): idx for idx, (lo, hi) in enumerate(ckh.ENTRY_BANDS)}

    policies = producer.build_policy_grid()
    policies_by_keystr = {(p['type'], json.dumps(p['params'])): p for p in policies}

    # Pre-load metadata
    all_tickers = set()
    for _, row in sample_df.iterrows():
        eb_idx = eb_lookup.get((row['entry_band_lo'], row['entry_band_hi']))
        if eb_idx is None:
            continue
        regime = regime_for_channel(row['channel'])
        ck = f'{regime}__{eb_idx}__{row["spread_band"]}__{row["volume_intensity"]}__{row["category"]}'
        if ck in manifest:
            for t in manifest[ck]['tickers'][:5]:  # First 5 tickers per cell — enough for spot check
                all_tickers.add(t)

    log(f'Loading metadata for {len(all_tickers)} unique tickers in spot sample', lines)
    meta_table = pq.read_table(
        str(G9_METADATA),
        columns=['ticker', 'result', 'settlement_ts'],
        filters=[('ticker', 'in', list(all_tickers))],
    )
    meta_df = meta_table.to_pandas().set_index('ticker')

    n_fired_total = 0
    n_violations = 0
    violations = []

    for _, row in sample_df.iterrows():
        eb_idx = eb_lookup.get((row['entry_band_lo'], row['entry_band_hi']))
        if eb_idx is None:
            continue
        regime = regime_for_channel(row['channel'])
        ck = f'{regime}__{eb_idx}__{row["spread_band"]}__{row["volume_intensity"]}__{row["category"]}'
        if ck not in manifest:
            log(f'  SKIP: cell {ck} not in manifest', lines)
            continue
        limit_c = row['limit_c']
        threshold_dollars = limit_c / 100.0
        the_policy = policies_by_keystr[('limit', json.dumps({'limit_c': int(limit_c)}))]

        tickers = manifest[ck]['tickers'][:5]
        cell_fired = 0
        cell_violations = 0

        for ticker in tickers:
            if ticker not in meta_df.index:
                continue
            meta_row = meta_df.loc[ticker]
            if meta_row['result'] not in ('yes', 'no'):
                continue

            candles_table = pq.read_table(
                str(G9_CANDLES),
                columns=['ticker', 'end_period_ts', 'yes_bid_close',
                         'yes_ask_close', 'volume_fp'],
                filters=[('ticker', '=', ticker)],
            )
            candles_df = candles_table.to_pandas()
            if len(candles_df) == 0:
                continue
            candles_df = candles_df.sort_values('end_period_ts').reset_index(drop=True)

            results = producer.walk_trajectory(
                ticker=ticker,
                candles_df=candles_df,
                metadata_row=meta_row,
                target_cell_key=ck,
                policies=[the_policy],
                helpers=ckh,
            )

            for moment_idx, p_idx, outcome in results:
                if outcome['outcome'] == 'fired':
                    cell_fired += 1
                    if outcome['capture_dollars'] < threshold_dollars - 1e-6:
                        cell_violations += 1
                        violations.append({
                            'cell': ck, 'ticker': ticker, 'limit_c': limit_c,
                            'capture': outcome['capture_dollars'],
                            'threshold': threshold_dollars,
                        })

        n_fired_total += cell_fired
        n_violations += cell_violations
        log(f'  cell={ck} limit_c={limit_c}: {cell_fired} fired, '
            f'{cell_violations} violations', lines)

    spot_pass = (n_violations == 0)
    log('', lines)
    log(f'Spot-check total: {n_fired_total} fired trajectories, '
        f'{n_violations} violations -> {"PASS" if spot_pass else "FAIL"}', lines)

    if violations:
        log('', lines)
        log('Violations:', lines)
        for v in violations[:10]:
            log(f'  {v}', lines)

    overall = 'PASS' if (floor_pass and spot_pass) else 'FAIL'
    log('', lines)
    log(f'**Check 1 overall: {overall}**', lines)
    return overall


def run_check_2_fire_rate_monotonic(layer_b_df, lines):
    """Per cell, fire_rate of limit policies should be monotone non-increasing as limit_c increases."""
    log('', lines)
    log('## Check 2: Fire rates monotonic with policy aggressiveness', lines)
    log('', lines)

    limit_rows = layer_b_df[layer_b_df['policy_type'] == 'limit'].copy()
    limit_rows['limit_c'] = limit_rows['policy_params'].apply(lambda s: json.loads(s)['limit_c'])

    cell_keys = ['channel', 'category', 'entry_band_lo', 'entry_band_hi',
                 'spread_band', 'volume_intensity']

    n_cells = 0
    n_monotone = 0
    n_strict_violations = 0

    for cell_key, grp in limit_rows.groupby(cell_keys):
        grp_sorted = grp.sort_values('limit_c')
        rates = grp_sorted['fire_rate'].tolist()
        is_monotone = all(rates[i] >= rates[i+1] - 1e-9 for i in range(len(rates) - 1))
        n_cells += 1
        if is_monotone:
            n_monotone += 1
        else:
            n_strict_violations += 1

    pct_pass = 100.0 * n_monotone / n_cells if n_cells else 0
    threshold_pass = pct_pass >= 95.0

    log(f'Cells evaluated: {n_cells}', lines)
    log(f'Cells with monotone non-increasing fire rate: {n_monotone} ({pct_pass:.1f}%)', lines)
    log(f'Cells with at least one violation: {n_strict_violations}', lines)
    log(f'Threshold (>= 95% monotone): {"PASS" if threshold_pass else "FAIL"}', lines)
    log('', lines)
    log(f'**Check 2 overall: {"PASS" if threshold_pass else "FAIL"}**', lines)
    return 'PASS' if threshold_pass else 'FAIL'


def run_check_3_time_stop_horizon(layer_b_df, lines):
    """In positive-mean-bounce cells, time-stop capture_mean should trend up with horizon."""
    log('', lines)
    log('## Check 3: Time-stop horizons capture more in positive-bounce cells', lines)
    log('', lines)

    layer_a = pq.read_table(str(LAYER_A_PARQUET)).to_pandas()
    log(f'Layer A cell_stats rows: {len(layer_a)}', lines)
    log(f'Layer A bounce columns available: '
        f'{[c for c in layer_a.columns if "bounce" in c.lower() and "mean" in c.lower()][:10]}', lines)

    # Use bounce_60min_mean as the canonical positive-bounce filter
    if 'bounce_60min_mean' not in layer_a.columns:
        log('INCONCLUSIVE: Layer A does not expose bounce_60min_mean', lines)
        log('', lines)
        log('**Check 3 overall: INCONCLUSIVE**', lines)
        return 'INCONCLUSIVE'

    pos_cells = layer_a[layer_a['bounce_60min_mean'] > 0].copy()
    log(f'Positive-bounce cells (bounce_60min_mean > 0): {len(pos_cells)}', lines)

    # Layer A cell key has different shape than Layer B; need to align.
    # Layer A: regime, entry_band_lo, entry_band_hi, spread_band, volume_intensity, category
    # Layer B: channel, entry_band_lo, entry_band_hi, spread_band, volume_intensity, category
    # regime in {premarket, in_match, settlement_zone}; channel in {premarket, in_match}.
    # We use Layer A regime as channel (filtered to non-settlement).
    pos_cells = pos_cells[pos_cells['regime'].isin(['premarket', 'in_match'])].copy()
    pos_cells['channel'] = pos_cells['regime']

    join_keys = ['channel', 'entry_band_lo', 'entry_band_hi',
                 'spread_band', 'volume_intensity', 'category']

    ts_rows = layer_b_df[layer_b_df['policy_type'] == 'time_stop'].copy()
    ts_rows['horizon_min'] = ts_rows['policy_params'].apply(
        lambda s: json.loads(s)['horizon_min']
    )
    # Drop 'settle' for the horizon-trend check
    ts_rows = ts_rows[ts_rows['horizon_min'] != 'settle'].copy()
    ts_rows['horizon_min'] = ts_rows['horizon_min'].astype(float)

    pos_keys_set = set(zip(*[pos_cells[k] for k in join_keys]))
    ts_pos = ts_rows[
        ts_rows[join_keys].apply(tuple, axis=1).isin(pos_keys_set)
    ].copy()
    log(f'Positive-bounce cells × time-stop policies: {len(ts_pos)} rows', lines)

    cell_keys_b = join_keys
    n_cells = 0
    n_trend_up = 0
    spearman_corrs = []

    for cell_key, grp in ts_pos.groupby(cell_keys_b):
        if len(grp) < 3:
            continue
        grp_sorted = grp.sort_values('horizon_min')
        horizons = grp_sorted['horizon_min'].values
        captures = grp_sorted['capture_mean'].values

        # Spearman: rank correlation between horizon and capture
        from scipy.stats import spearmanr
        rho, _ = spearmanr(horizons, captures)

        n_cells += 1
        spearman_corrs.append(rho)
        if rho > 0:
            n_trend_up += 1

    pct_up = 100.0 * n_trend_up / n_cells if n_cells else 0
    median_rho = statistics.median(spearman_corrs) if spearman_corrs else float('nan')
    threshold_pass = pct_up >= 60.0

    log(f'Cells with >= 3 time-stop horizons evaluated: {n_cells}', lines)
    log(f'Cells with positive horizon-vs-capture Spearman: {n_trend_up} ({pct_up:.1f}%)', lines)
    log(f'Median Spearman across cells: {median_rho:.3f}', lines)
    log(f'Threshold (>= 60% positive-rho): {"PASS" if threshold_pass else "FAIL"}', lines)
    log('', lines)
    log(f'**Check 3 overall: {"PASS" if threshold_pass else "FAIL"}**', lines)
    return 'PASS' if threshold_pass else 'FAIL'


def run_check_4_premarket_vs_in_match(layer_b_df, lines):
    """median(in_match - premarket) capture_mean over matched (category, ..., policy) tuples > 0."""
    log('', lines)
    log('## Check 4: Premarket vs in_match capture distributions', lines)
    log('', lines)

    join_keys = ['category', 'entry_band_lo', 'entry_band_hi',
                 'spread_band', 'volume_intensity', 'policy_type', 'policy_params']

    pre = layer_b_df[layer_b_df['channel'] == 'premarket'][join_keys + ['capture_mean']].copy()
    inm = layer_b_df[layer_b_df['channel'] == 'in_match'][join_keys + ['capture_mean']].copy()
    pre = pre.rename(columns={'capture_mean': 'cap_pre'})
    inm = inm.rename(columns={'capture_mean': 'cap_inm'})

    matched = pre.merge(inm, on=join_keys, how='inner')
    log(f'Matched (category, ..., policy) tuples in both channels: {len(matched)}', lines)

    if len(matched) == 0:
        log('INCONCLUSIVE: no matching tuples', lines)
        log('', lines)
        log('**Check 4 overall: INCONCLUSIVE**', lines)
        return 'INCONCLUSIVE'

    matched['delta'] = matched['cap_inm'] - matched['cap_pre']
    median_delta = matched['delta'].median()
    mean_delta = matched['delta'].mean()
    pct_positive = 100.0 * (matched['delta'] > 0).sum() / len(matched)

    from scipy.stats import wilcoxon
    try:
        wstat, wpval = wilcoxon(matched['delta'], alternative='greater')
    except ValueError:
        wstat, wpval = float('nan'), float('nan')

    threshold_pass = median_delta > 0 and wpval < 0.05

    log(f'Median delta (in_match - premarket): {median_delta:+.4f}', lines)
    log(f'Mean delta: {mean_delta:+.4f}', lines)
    log(f'% of tuples where in_match > premarket: {pct_positive:.1f}%', lines)
    log(f'Wilcoxon signed-rank (one-sided, in_match > premarket): '
        f'stat={wstat:.4g}, p={wpval:.4g}', lines)
    log(f'Direction (median > 0 and p < 0.05): {"PASS" if threshold_pass else "FAIL"}', lines)
    log('', lines)
    log(f'**Check 4 overall: {"PASS" if threshold_pass else "FAIL"}**', lines)
    return 'PASS' if threshold_pass else 'FAIL'


def main():
    lines = []
    log('# T31c — Layer B v1 Coherence Report', lines)
    log('', lines)
    log(f'Generated: {now_et()}', lines)
    log(f'Layer B parquet: {LAYER_B_PARQUET}', lines)
    log(f'Layer A parquet: {LAYER_A_PARQUET}', lines)
    log(f'Producer commit: 28e8ab7', lines)
    log(f'Spec: layer_b_spec.md Validation Gate (post-T31a-patch-5)', lines)

    t_start = time.time()

    # Load main parquet
    layer_b_df = pq.read_table(str(LAYER_B_PARQUET)).to_pandas()
    log('', lines)
    log(f'Layer B rows loaded: {len(layer_b_df)}', lines)
    log(f'Layer B columns: {list(layer_b_df.columns)}', lines)

    # Load sample manifest for Check 1 spot-check
    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)

    # Run checks
    c1 = run_check_1_spot_check(layer_b_df, manifest, lines)
    c2 = run_check_2_fire_rate_monotonic(layer_b_df, lines)
    c3 = run_check_3_time_stop_horizon(layer_b_df, lines)
    c4 = run_check_4_premarket_vs_in_match(layer_b_df, lines)

    elapsed = time.time() - t_start

    # Summary
    log('', lines)
    log('---', lines)
    log('', lines)
    log('## Summary', lines)
    log('', lines)
    verdicts = [('Check 1 (capture bounded)', c1),
                ('Check 2 (fire rate monotonic)', c2),
                ('Check 3 (time-stop horizon trend)', c3),
                ('Check 4 (premarket vs in_match)', c4)]
    for label, v in verdicts:
        log(f'- {label}: **{v}**', lines)
    log('', lines)
    log(f'Runtime: {elapsed:.1f}s', lines)

    # Overall verdict
    has_fail = any(v == 'FAIL' for _, v in verdicts)
    has_inc = any(v == 'INCONCLUSIVE' for _, v in verdicts)
    n_pass = sum(1 for _, v in verdicts if v == 'PASS')
    overall = 'FAIL' if has_fail else ('INCONCLUSIVE' if has_inc else 'PASS')
    log('', lines)
    log(f'**T31c overall verdict: {overall}** ({n_pass}/4 PASS)', lines)
    log('', lines)
    log(f'Layer B v1 outputs are {"cleared for downstream Layer C consumption" if overall == "PASS" else "NOT cleared"}.', lines)

    # Write report
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text('\n'.join(lines) + '\n')

    print()
    print(f'Coherence report written to: {OUTPUT_REPORT}')

    if overall == 'FAIL':
        sys.exit(1)
    elif overall == 'INCONCLUSIVE':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
