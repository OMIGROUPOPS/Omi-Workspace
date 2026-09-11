"""Full-universe atlas screen; opt-in adapter, never edits the live bench/OS.

Exact cached feature states, the original FIRST/role/clock/span rules, the
original nested earlier-only training and frozen June library. Only evaluation
cadence and the numerical stall repair differ from the filed full run.
"""
from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import struct
from unittest.mock import patch
import numpy as np

import feature_panel as panel
import feature_panel_bench as bench
import feature_panel_atlas_optimizer as optimizer

BASE_SAMPLER = bench.DirectFeatureSampler
BASE_PROJECTOR = bench.FeatureProjector


def span_hash(pair):
    span = dict(event=pair.event_id, category=pair.category,
        legs=[dict(leg=leg.leg_id, formation=float(leg.formation).hex(), bell=float(leg.bell).hex())
              for leg in pair.legs])
    return hashlib.sha256(json.dumps(span, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class ExactStateCache:
    """In-process LRU: immutable source scope + exact member/clock/span key."""
    def __init__(self, sample, source_scope, maximum_bytes):
        if maximum_bytes <= 0:
            raise ValueError('POSITIVE_STATE_CACHE_BUDGET_REQUIRED')
        self.sample_raw, self.scope, self.maximum_bytes = sample, source_scope, maximum_bytes
        self.rows, self.used = OrderedDict(), 0
        self.hits = self.misses = self.evictions = 0

    def sample(self, pair, gates):
        gates = np.asarray(gates, dtype=float)
        if not np.all(np.isfinite(gates)):
            raise ValueError('NONFINITE_CACHE_CLOCK')
        span = span_hash(pair)
        keys = [(self.scope, pair.event_id, struct.pack('>d', float(g)), span) for g in gates]
        values, missing = {}, OrderedDict()
        for key, gate in zip(keys, gates):
            if key in self.rows:
                self.hits += 1
                self.rows.move_to_end(key)
                values[key] = self.rows[key]
            elif key not in missing:
                missing[key] = gate
                self.misses += 1
        if missing:
            sampled = self.sample_raw(pair, np.asarray(list(missing.values())))
            for key, row in zip(missing, sampled):
                row = np.array(row, copy=True)
                row.setflags(write=False)
                values[key] = row
                if row.nbytes <= self.maximum_bytes:
                    while self.used + row.nbytes > self.maximum_bytes:
                        _, old = self.rows.popitem(last=False)
                        self.used -= old.nbytes
                        self.evictions += 1
                    self.rows[key] = row
                    self.used += row.nbytes
        if not keys:
            return self.sample_raw(pair, gates)
        return np.stack([values[key] for key in keys])

    def receipt(self):
        return dict(hits=self.hits, misses=self.misses, evictions=self.evictions,
            bytes=self.used, budget_bytes=self.maximum_bytes, source_scope=self.scope,
            key=['source manifest hash', 'member event', 'exact float64 minutes-to-bell bytes', 'span sha256'],
            clocks_rounded=False, cache_changes_membership=False)


def cached_sampler_type(source_scope, maximum_bytes):
    class CachedSampler(BASE_SAMPLER):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Store an unbound sampler call so compact_sampler_copy's shallow
            # copy cannot retain obsolete raw witness/source dictionaries.
            self.state_cache = ExactStateCache(None, source_scope, maximum_bytes)

        def sample(self, pair, gates):
            self.state_cache.sample_raw = lambda p, g: BASE_SAMPLER.sample(self, p, g)
            return self.state_cache.sample(pair, gates)
    return CachedSampler


class AtlasProjector(BASE_PROJECTOR):
    def receipts(self, query, mode='GATE-SIM'):
        yield from super().receipts(query, 'GATE-SIM')


def write_atlas_diagnostics(output_dir, query, frozen, sampler, stream, scale_proof):
    gates = np.asarray([g for g in sampler.contract['gates_minutes_to_bell'] if 0 < g <= query.first_mtb])
    data = panel.build_pair_panel(query, sampler.metadata, sampler.sources, sampler.witnesses,
        sampler.contract, sampler.par, sampler.codebooks, evaluation_gates=gates)
    ranks = frozen.kernel.rank(data['values'])
    folder = Path(output_dir)/'receipt_diagnostics'
    folder.mkdir(exist_ok=True)
    name = query.event_id+'__'+stream+'.npz'
    extra = {leg+'__'+key: values for leg, fields in data['diagnostic_arrays'].items()
             for key, values in fields.items()}
    field_names = [f.name for f in frozen.kernel.fields]
    if 'prefix_cadence_seconds' in field_names:
        rank = ranks[..., field_names.index('prefix_cadence_seconds')]
        quantiles = np.asarray(sampler.contract['quantiles'])
        extra['cadence_rank_interval'] = np.where(np.isfinite(rank),
            np.searchsorted(quantiles, rank, side='right'), np.nan)
        for side, leg in enumerate(query.legs):
            data['coverage'][leg.leg_id]['fields']['cadence_class'] = int(np.isfinite(rank[:,side]).sum())
    np.savez_compressed(folder/name, epoch=data['epochs'], gate=data['gates'], is_gate=data['is_gate'],
        raw_value=data['values'], empirical_rank=ranks, feature_names=np.asarray(field_names), **extra)
    return dict(path='receipt_diagnostics/'+name, sha256=panel.sha256(folder/name), receipts=len(ranks),
        category=query.category, month=query.date[:7], event_id=query.event_id, stream=stream,
        scale_file=scale_proof['path'], scale_sha256=scale_proof['sha256'], scale_cutoff=frozen.cutoff,
        coverage=data['coverage'], diagnostics=data['diagnostics'], evaluation_cadence='GATE-SIM',
        rank_definition='Earlier-only frozen empirical mid-CDF; categorical unchanged; missing stays NaN',
        cadence_class='Diagnostic interval at filed organ_contract.quantiles',
        cadence_interval_boundaries=list(sampler.contract['quantiles']))


def optimizer_rows(receipt):
    """Every variant/month and inner optimizer, including absent evidence."""
    rows = []
    plan = receipt['plan']
    for variant, choice in receipt['model_class_choices'].items():
        attempts = []
        for fold in receipt['inner_folds']:
            item = fold.get('variants', {}).get(variant, {})
            fit = item.get('fit', {})
            attempts.append(dict(month=fold['month'], status=fit.get('status', fold.get('status')),
                outcome=fit.get('optimizer_outcome', 'NO_INNER_TRAINING_OR_VALIDATION'),
                gradient=fit.get('projected_gradient_max'),
                legacy_status=fit.get('legacy_attempt', {}).get('status'),
                validation_games=fold.get('validation_games'), refinement=fit.get('refinement_attempted',False)))
        refit = receipt.get('refits', {}).get(variant)
        if not plan['training_games']:
            outcome = 'NO_EARLIER_TRAINING'
        elif not choice['validation_games']:
            outcome = 'STALLED' if any(a['outcome']=='STALLED' for a in attempts) else 'NO_INNER_VALIDATION'
        elif choice['reason']=='REFIT_NOT_CONVERGED':
            outcome = 'STALLED'
        elif choice['selected']=='FIRST_ZERO':
            outcome = 'ZERO_WEIGHT_BY_VALIDATION'
        else:
            outcome = 'CONVERGED'
        rows.append(dict(category=plan['category'], month=plan['month'], variant=variant,
            outcome=outcome, choice=choice, attempts=attempts,
            refit_status=None if refit is None else refit['status'],
            refit_gradient=None if refit is None else refit.get('projected_gradient_max'),
            coefficients=receipt['coefficients'][variant],
            zero_control_is_not_a_converged_feature_fit=outcome in
                ('STALLED','NO_INNER_VALIDATION','NO_EARLIER_TRAINING')))
    return rows


@contextmanager
def adapter(source_scope, state_cache_bytes, *, screen=True):
    """Process-local adapters only; original full-run source bytes untouched."""
    with patch.object(bench, 'DirectFeatureSampler', cached_sampler_type(source_scope,state_cache_bytes)), \
         patch.object(bench.model, 'fit_joint_model', optimizer.fit_joint_model):
        if screen:
            with patch.object(bench, 'FeatureProjector', AtlasProjector), \
                 patch.object(bench, 'write_query_diagnostics', write_atlas_diagnostics):
                yield
        else:
            yield
