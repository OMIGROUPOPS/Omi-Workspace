"""Joint feature-panel benchmark orchestration; no OS import or engine replay.

FIRST membership, receipt clock, role masks, Q/X emitter and R0 conduct come
from the existing benchmark helpers. This module only changes member weights.
All fitting uses atlas receipts. Predictions use exact feature states at each
query/member phase, not the member's preceding receipt's derived features.

An outer calendar month freezes scales and model selection before its earliest
query formation. Inner validation uses already-resolved subsets of preceding
calendar months, with expanding earlier-month training prefixes. Explicit
held-out months never supply fitted outcomes or normalizers. A strict held-out
evaluation additionally freezes the member library for FIRST and all variants.
This is a new-experiment holdout, not a claim the month was never inspected.

Scientific choices are supplied in the protocol and receipts. Batch/cache
budgets are execution-only: exceeding a budget aborts, never truncates queries.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import time
from typing import Mapping, Sequence

import numpy as np

import conduct_scoreboard as conduct
import conduct_scoreboard_v2 as cv2
import feature_panel as panel
import feature_panel_model as model
import feature_panel_scoring as scoring
import tune_bench_v2_survivorship as b


@dataclass(frozen=True)
class Variant:
    name: str
    blocks: tuple[str, ...]


def variant_registry(blocks):
    blocks = tuple(blocks)
    if not blocks or len(set(blocks)) != len(blocks):
        raise ValueError("INVALID_BLOCK_REGISTRY")
    cumulative = [Variant(f"CUMULATIVE_{i}", blocks[:i]) for i in range(1, len(blocks)+1)]
    leave_out = [Variant("LEAVE_OUT_"+name, tuple(b for b in blocks if b != name)) for name in blocks]
    return tuple([Variant("FIRST", ())] + cumulative + leave_out)


def pair_record(pair):
    return dict(event_id=pair.event_id, category=pair.category, date=pair.date,
                formation=float(pair.formation), bell=float(pair.bell))


def month_prefix(pairs, category, month, cutoff, heldout_months):
    """No later month, unresolved event, or held-out outcome enters fitting."""
    excluded = set(heldout_months)
    return sorted((p for p in pairs if p.category == category and p.date[:7] < month
                   and p.date[:7] not in excluded and p.bell < cutoff),
                  key=lambda p: (p.date, p.event_id))


def outer_month_plan(pairs, category, month, heldout_months):
    queries = sorted((p for p in pairs if p.category == category and p.date[:7] == month),
                     key=lambda p: p.event_id)
    if not queries:
        raise ValueError("EMPTY_OUTER_MONTH")
    cutoff = min(p.formation for p in queries)
    training = month_prefix(pairs, category, month, cutoff, heldout_months)
    inner = []
    for earlier_month in sorted({p.date[:7] for p in training}):
        # Each month's model is frozen before its first original query, not
        # before a retrospectively chosen easy/complete subset.
        all_month = [p for p in pairs if p.category == category and p.date[:7] == earlier_month]
        inner_cutoff = min(p.formation for p in all_month)
        inner_train = month_prefix(pairs, category, earlier_month, inner_cutoff, heldout_months)
        validation = [p for p in training if p.date[:7] == earlier_month]
        inner.append(dict(month=earlier_month, cutoff=float(inner_cutoff), training=inner_train,
                          validation=validation, original_month_games=len(all_month),
                          partial_resolved_validation=len(validation) != len(all_month)))
    return dict(category=category, month=month, cutoff=float(cutoff), queries=queries,
                training=training, inner=inner,
                strict_holdout=month in set(heldout_months))


def plan_receipt(plan):
    return dict(category=plan["category"], month=plan["month"], cutoff=plan["cutoff"],
        query_games=len(plan["queries"]), training_games=len(plan["training"]),
        strict_holdout=plan["strict_holdout"],
        training_event_ids=[p.event_id for p in plan["training"]],
        inner=[dict(month=f["month"], cutoff=f["cutoff"], training_games=len(f["training"]),
                    validation_games=len(f["validation"]), original_month_games=f["original_month_games"],
                    partial_resolved_validation=f["partial_resolved_validation"])
               for f in plan["inner"]])


class DirectFeatureSampler:
    def __init__(self, metadata, sources, witnesses, contract, par):
        self.metadata, self.sources, self.witnesses = metadata, sources, witnesses
        self.contract, self.par = contract, par
        self.codebooks = panel.categorical_codes(metadata)
        panel.prepare_sources(sources, witnesses, minute_seconds=contract["minute_seconds"])

    def sample(self, pair, gates):
        return panel.build_pair_panel(pair, self.metadata, self.sources, self.witnesses,
            self.contract, self.par, self.codebooks, evaluation_gates=np.asarray(gates, dtype=float),
            values_only=True)


class RankedBlockKernel:
    """Vectorized equivalent of model.block_likelihoods across both legs."""
    def __init__(self, fields, blocks, scales):
        self.fields, self.blocks, self.scales = tuple(fields), tuple(blocks), scales
        self.indices = {name: np.asarray([i for i, f in enumerate(fields) if f.block == name], dtype=int)
                        for name in blocks}
        self.categorical = np.asarray([f.kind == "categorical" for f in fields])
        if any(not len(v) for v in self.indices.values()):
            raise ValueError("EMPTY_REGISTERED_BLOCK")

    def rank(self, values):
        raw = np.asarray(values, dtype=float)
        if raw.shape[-1] != len(self.fields):
            raise ValueError("RAW_FEATURE_WIDTH_MISMATCH")
        ranked = raw.copy()
        for column, feature in enumerate(self.fields):
            if feature.kind == "categorical":
                continue
            scale = self.scales[feature.name].sorted_values
            if not len(scale):
                ranked[..., column] = np.nan
                continue
            x = raw[..., column]
            left = np.searchsorted(scale, x, side="left")
            right = np.searchsorted(scale, x, side="right")
            ranked[..., column] = np.where(np.isfinite(x), (left+right)/(len(scale)+len(scale)), np.nan)
        return ranked

    def compare_ranked(self, query, members):
        q, m = np.asarray(query), np.asarray(members)
        if m.ndim != q.ndim+1 or m.shape[1:] != q.shape:
            raise ValueError("PAIR_FEATURE_SHAPE_MISMATCH")
        observed = np.isfinite(m) & np.isfinite(q)
        distance = np.abs(m-q)
        distance[..., self.categorical] = (m[..., self.categorical] != q[..., self.categorical]).astype(float)
        distance = np.where(observed, distance, 0)
        logs = np.zeros((len(m), len(self.blocks)))
        support = np.zeros_like(logs)
        for column, name in enumerate(self.blocks):
            ix = self.indices[name]
            count = observed[..., ix].sum(axis=(1, 2))
            total = distance[..., ix].sum(axis=(1, 2))
            mean = np.divide(total, count, out=np.zeros(len(m)), where=count > 0)
            logs[:, column] = -np.log1p(mean)
            support[:, column] = count/(q.shape[0]*len(ix))
        return logs, support


def fit_category_scales(training, sampler, fields, contract):
    numeric = [f for f in fields if f.kind == "numeric"]
    values = {f.name: [] for f in numeric}
    indices = {f.name: i for i, f in enumerate(fields)}
    sampled_receipts = 0
    for pair in training:
        gates = [g for g in contract["gates_minutes_to_bell"] if 0 < g <= pair.first_mtb]
        raw = sampler.sample(pair, gates)
        sampled_receipts += len(gates)
        for feature in numeric:
            column = raw[..., indices[feature.name]].ravel()
            values[feature.name].extend(column[np.isfinite(column)].tolist())
    scales = {name: model.EmpiricalRankScale.fit(column) for name, column in values.items()}
    receipt = dict(training_games=len(training), sampled_atlas_receipts=sampled_receipts,
                   sampling="all available training atlas side states, never full-span metadata",
                   features={name: dict(n=len(scale.sorted_values),
                     sha256=hashlib.sha256(scale.sorted_values.tobytes()).hexdigest())
                     for name, scale in scales.items()})
    return scales, receipt


class CausalRankCache:
    """Small raw-atlas cache; historical training points cannot normalize themselves.

    Training normalizers freeze at the earliest formation on the query's
    category/event-name date. Only earlier-resolved other-date events contribute.
    Inner/outer validation still uses its own earlier-month frozen normalizers.
    The daily cache is conservative relative to per-query formation, not a
    price/timing threshold and not an extra member-selection rule.
    """
    def __init__(self, pairs, sampler, fields, blocks, contract, heldout_months):
        self.pairs, self.sampler, self.fields = pairs, sampler, fields
        self.blocks, self.contract, self.excluded = blocks, contract, set(heldout_months)
        self.raw, self.kernels, self.proofs, self.cutoffs = {}, {}, {}, {}
        for p in pairs:
            key = (p.category, p.date)
            self.cutoffs[key] = min(self.cutoffs.get(key, p.formation), p.formation)

    def raw_pair(self, pair):
        if pair.event_id not in self.raw:
            gates = [g for g in self.contract["gates_minutes_to_bell"] if 0 < g <= pair.first_mtb]
            self.raw[pair.event_id] = self.sampler.sample(pair, gates)
        return self.raw[pair.event_id]

    def kernel_for(self, query):
        key = (query.category, query.date)
        if key in self.kernels:
            return self.kernels[key]
        cutoff = min(self.cutoffs.get(key, query.formation), query.formation)
        prior = [p for p in self.pairs if p.category == query.category and p.date != query.date
                 and p.event_id != query.event_id and p.date[:7] not in self.excluded and p.bell < cutoff]
        arrays = [self.raw_pair(p) for p in prior]
        scales = {}
        for index, feature in enumerate(self.fields):
            if feature.kind == "categorical":
                continue
            columns = [a[..., index].ravel() for a in arrays]
            joined = np.concatenate(columns) if columns else np.array([], dtype=float)
            scales[feature.name] = model.EmpiricalRankScale(np.sort(joined[np.isfinite(joined)], kind="stable"))
        self.kernels[key] = RankedBlockKernel(self.fields, self.blocks, scales)
        self.proofs[key] = dict(category=query.category, event_date=query.date, cutoff=float(cutoff),
            prior_games=len(prior), latest_prior_bell=max((p.bell for p in prior), default=None),
            prior_event_ids=[p.event_id for p in prior],
            fields={name: dict(n=len(scale.sorted_values), sha256=hashlib.sha256(scale.sorted_values.tobytes()).hexdigest())
                    for name, scale in scales.items()})
        return self.kernels[key]

    def receipt(self):
        return dict(method="training query category/event-date prefix: scales frozen before earliest formation; exclude self/date/heldout",
                    cached_raw_games=len(self.raw), raw_array_bytes=sum(a.nbytes for a in self.raw.values()),
                    days=[value for _, value in sorted(self.proofs.items())])


@dataclass
class ReceiptCandidates:
    baseline: dict
    member_ids: tuple[str, ...]
    base_weights: np.ndarray
    block_log_k: np.ndarray
    block_support: np.ndarray
    side_masks: tuple[np.ndarray, ...]
    levels: np.ndarray
    floor_times: np.ndarray


class FeatureProjector:
    def __init__(self, member_pairs, sampler, contract, kernel, *, batch_size):
        if batch_size <= 0:
            raise ValueError("INVALID_EXECUTION_BATCH")
        self.members, self.sampler, self.contract, self.kernel = member_pairs, sampler, contract, kernel
        self.batch_size = batch_size

    def receipts(self, query, mode="RECEIPT-SIM"):
        contract = self.contract
        baseline = cv2.ReceiptProjector(self.members, contract, self.batch_size).project(query, mode)
        members, w0 = b.initial_pool(query, self.members)
        first = np.asarray([m.first_mtb for m in members])
        opens = np.asarray([[leg.open for leg in m.legs] for m in members]).reshape((-1, len(query.legs)))
        gates = np.asarray([row["source_gate_minutes"] for row in baseline])
        own = query.levels(gates)
        for start in range(0, len(gates), self.batch_size):
            gs = gates[start:start+self.batch_size]
            count, total = len(gs), len(members)
            sampled = np.empty((count, total, len(b.SERIES)))
            floors = np.empty((count, total, len(query.legs)))
            times = np.empty_like(floors)
            ranked = np.empty((count, total, len(query.legs), len(self.kernel.fields)))
            qfeatures = self.kernel.rank(self.sampler.sample(query, gs))
            for mi, member in enumerate(members):
                sampled[:, mi] = member.levels(gs)
                ranked[:, mi] = self.kernel.rank(self.sampler.sample(member, gs))
                for side, leg in enumerate(member.legs):
                    epochs = leg.bell-gs*contract["minute_seconds"]
                    ix = np.searchsorted(leg.epoch, epochs, side="right")
                    fi = leg.remaining_floor_index[np.minimum(ix, len(leg.epoch)-1)]
                    current, future = sampled[:, mi, side*3], leg.values[fi, 0]
                    carried = (ix == len(leg.epoch)) | (current <= future)
                    floors[:, mi, side] = np.where(carried, current, future)
                    times[:, mi, side] = np.where(carried, gs, (leg.bell-leg.epoch[fi])/contract["minute_seconds"])
            for offset, gate in enumerate(gs):
                index = start+offset
                row = baseline[index]
                logs, support = self.kernel.compare_ranked(qfeatures[offset], ranked[offset])
                drift = sampled[offset, :, [0, 3]].T-opens
                # Advanced-index transpose above is explicit for numpy's axis rule.
                member_roles = np.where(drift >= contract["role_drift_cents"], "CLIMBER",
                    np.where(drift <= -contract["role_drift_cents"], "FALLER", "NOT_CALLABLE"))
                masks, levels = [], np.empty((total, len(query.legs)))
                for side, leg in enumerate(query.legs):
                    state = row["sides"][leg.leg_id]
                    mask = ((member_roles[:, side] == state["role"]) | (state["role"] == "NOT_CALLABLE"))
                    mask &= first >= gate
                    mask &= np.isfinite(sampled[offset, :, side*3:side*3+3]).all(axis=1)
                    if int(mask.sum()) != state["member_count"]:
                        raise ValueError("REFERENCE_MEMBER_MASK_DRIFT:"+query.event_id)
                    if not math.isclose(float(b.ess(w0*mask) or 0), state["ess"], abs_tol=1e-9):
                        raise ValueError("REFERENCE_ESS_DRIFT:"+query.event_id)
                    levels[:, side] = own[index, side*3] + floors[offset, :, side]-sampled[offset, :, side*3]
                    masks.append(mask)
                yield ReceiptCandidates(row, tuple(m.event_id for m in members), w0, logs, support,
                                        tuple(masks), levels, times[offset])


def collect_training_samples(queries, projector, *, cache_budget_bytes, causal_kernel_cache=None):
    """One finite fold cache shared by all variants; never cache raw source rows."""
    samples, used = [], 0
    for query in queries:
        query_projector = projector if causal_kernel_cache is None else FeatureProjector(projector.members,
            projector.sampler, projector.contract, causal_kernel_cache.kernel_for(query), batch_size=projector.batch_size)
        for receipt in query_projector.receipts(query, "GATE-SIM"):
            gate = receipt.baseline["source_gate_minutes"]
            if not query.scorable(gate):
                continue
            for side, leg in enumerate(query.legs):
                mask = receipt.side_masks[side]
                if not np.any(mask):
                    continue
                actual, _ = b.remaining_floor(leg, gate)
                if actual is None or not np.isfinite(actual):
                    continue
                sample = model.PoolSample(receipt.levels[mask, side].copy(), receipt.base_weights[mask].copy(),
                    receipt.block_log_k[mask].copy(), float(actual), query.event_id)
                used += sample.candidate_levels.nbytes+sample.base_weights.nbytes+sample.block_log_k.nbytes
                if used > cache_budget_bytes:
                    raise MemoryError(f"FOLD_CACHE_BUDGET_EXCEEDED:{used}>{cache_budget_bytes}; no query dropped")
                samples.append(sample)
    return samples, dict(samples=len(samples), games=len({s.gameid for s in samples}), array_bytes=used)


def subset_samples(samples, active_columns):
    return [model.PoolSample(s.candidate_levels, s.base_weights, s.block_log_k[:, active_columns],
                             s.actual, s.gameid) for s in samples]


def optimizer_usable(fitted):
    return fitted.report["status"] in {"PROJECTED_GRADIENT_CONVERGED", "UNTRAINED_FIRST_CONTROL"}


@dataclass
class FrozenMonthModel:
    category: str
    month: str
    cutoff: float
    kernel: RankedBlockKernel
    coefficients: dict[str, np.ndarray]
    receipt: dict


def fit_outer_month(plan, all_pairs, sampler, fields, blocks, registry, contract, *,
                    heldout_months, batch_size, cache_budget_bytes, numerical_options=None):
    """Nested class choice is fit-versus-zero, not a reused alpha grid."""
    training_library = [p for p in all_pairs if p.date[:7] not in set(heldout_months)]
    causal_scales = CausalRankCache(all_pairs, sampler, fields, blocks, contract, heldout_months)
    evidence = {v.name: [] for v in registry if v.name != "FIRST"}
    fold_receipts = []
    columns = {v.name: [blocks.index(name) for name in v.blocks] for v in registry}
    for fold in plan["inner"]:
        proof = dict(month=fold["month"], cutoff=fold["cutoff"], training_games=len(fold["training"]),
                     validation_games=len(fold["validation"]), original_month_games=fold["original_month_games"],
                     partial_resolved_validation=fold["partial_resolved_validation"])
        if not fold["training"] or not fold["validation"]:
            proof["status"] = "NO_INNER_TRAINING_OR_VALIDATION"
            fold_receipts.append(proof)
            continue
        scales, scale_receipt = fit_category_scales(fold["training"], sampler, fields, contract)
        kernel = RankedBlockKernel(fields, blocks, scales)
        projector = FeatureProjector(training_library, sampler, contract, kernel, batch_size=batch_size)
        train, train_cache = collect_training_samples(fold["training"], projector, cache_budget_bytes=cache_budget_bytes,
                                                      causal_kernel_cache=causal_scales)
        valid, valid_cache = collect_training_samples(fold["validation"], projector,
            cache_budget_bytes=max(0, cache_budget_bytes-train_cache["array_bytes"]))
        proof.update(scales=scale_receipt, train_cache=train_cache, validation_cache=valid_cache, variants={})
        for variant in registry:
            if variant.name == "FIRST":
                continue
            train_variant, valid_variant = subset_samples(train, columns[variant.name]), subset_samples(valid, columns[variant.name])
            fitted = model.fit_joint_model(train_variant, variant.blocks, options=numerical_options)
            proof["variants"][variant.name] = dict(fit=fitted.report)
            if not optimizer_usable(fitted) or not train_variant or not valid_variant:
                proof["variants"][variant.name]["status"] = "NO_USABLE_INNER_FIT"
                continue
            candidate = model.evaluate_joint_model(valid_variant, fitted.beta)
            first = model.evaluate_joint_model(valid_variant, np.zeros(len(variant.blocks)))
            if set(candidate["per_game_crps"]) != set(first["per_game_crps"]):
                raise ValueError("INNER_VALIDATION_COHORT_DRIFT")
            evidence[variant.name].extend(dict(game=game, candidate=candidate["per_game_crps"][game],
                first=first["per_game_crps"][game]) for game in candidate["per_game_crps"])
            proof["variants"][variant.name].update(status="EVALUATED_FROZEN_MODEL", candidate=candidate, first=first)
        fold_receipts.append(proof)
        del train, valid
    scales, scale_receipt = fit_category_scales(plan["training"], sampler, fields, contract)
    kernel = RankedBlockKernel(fields, blocks, scales)
    choices = {}
    for variant in registry:
        if variant.name == "FIRST":
            continue
        rows = evidence[variant.name]
        if len({row["game"] for row in rows}) != len(rows):
            raise ValueError("INNER_GAME_SCORED_MORE_THAN_ONCE")
        first = math.fsum(row["first"] for row in rows)/len(rows) if rows else None
        candidate = math.fsum(row["candidate"] for row in rows)/len(rows) if rows else None
        choices[variant.name] = dict(validation_games=len(rows), first_crps=first, candidate_crps=candidate,
            selected="CONTINUOUS" if rows and candidate < first else "FIRST_ZERO",
            reason="STRICT_INNER_CRPS_IMPROVEMENT" if rows and candidate < first else
                   "NO_USABLE_INNER_VALIDATION" if not rows else "FIRST_BETTER_OR_TIED")
    coefficients = {v.name: np.zeros(len(blocks)) for v in registry}
    refits = {}
    if any(choice["selected"] == "CONTINUOUS" for choice in choices.values()):
        projector = FeatureProjector(training_library, sampler, contract, kernel, batch_size=batch_size)
        samples, cache = collect_training_samples(plan["training"], projector, cache_budget_bytes=cache_budget_bytes,
                                                 causal_kernel_cache=causal_scales)
        for variant in registry:
            if variant.name == "FIRST" or choices[variant.name]["selected"] != "CONTINUOUS":
                continue
            fitted = model.fit_joint_model(subset_samples(samples, columns[variant.name]), variant.blocks,
                                           options=numerical_options)
            refits[variant.name] = fitted.report
            if optimizer_usable(fitted):
                coefficients[variant.name][columns[variant.name]] = fitted.beta
            else:
                choices[variant.name].update(selected="FIRST_ZERO", reason="REFIT_NOT_CONVERGED")
        del samples
    else:
        cache = None
    receipt = dict(plan=plan_receipt(plan), scales=scale_receipt, inner_folds=fold_receipts,
        model_class_choices=choices, refits=refits, refit_cache=cache,
        coefficients={name: dict(zip(blocks, map(float, beta))) for name, beta in coefficients.items()},
        method="continuous nonnegative fit versus zero selected by inner equal-game CRPS; exact ties zero",
        heldout_months=list(heldout_months), optimization_claim="local stationarity only, never global optimum",
        training_normalizers=causal_scales.receipt(),
        normalization_strategy="training samples use their earlier-only event-date scales; validation/evaluation use frozen earlier-month scales",
        model_library="fitting examples and their member libraries exclude held-out event-date months")
    return FrozenMonthModel(plan["category"], plan["month"], plan["cutoff"], kernel, coefficients, receipt)


class PositivePrintTarget:
    """Strictly later positive-size target, with earliest tied minimum time."""
    def __init__(self, rows, formation, bell, seconds):
        accepted = sorted((r for r in rows if formation <= r[0] < bell
                           and np.isfinite(r[2]) and r[2] > 0), key=lambda r: (r[0], r[3]))
        self.epochs = np.asarray([r[0] for r in accepted], dtype=float)
        self.prices = np.asarray([r[1] for r in accepted], dtype=float)
        self.bell, self.seconds = bell, seconds
        self.suffix_index = np.empty(len(accepted), dtype=np.int64)
        best = None
        for index in range(len(accepted)-1, -1, -1):
            if best is None or self.prices[index] <= self.prices[best]:
                best = index
            self.suffix_index[index] = best

    def at(self, epoch):
        index = int(np.searchsorted(self.epochs, epoch, side="right"))
        if index == len(self.epochs):
            return dict(floor_cents=None, floor_mtb=None, has_future_print=False)
        where = self.suffix_index[index]
        return dict(floor_cents=float(self.prices[where]),
                    floor_mtb=float((self.bell-self.epochs[where])/self.seconds),
                    has_future_print=True)


def causal_families(query, all_pairs, member_ids, contract, heldout_months, *, frozen_cutoff=None, cache=None):
    """Earlier-only SLEEPER scale; full paths are labels, never model features."""
    cutoff = min(query.formation, frozen_cutoff) if frozen_cutoff is not None else query.formation
    prior = [p for p in all_pairs if p.category == query.category and p.event_id != query.event_id
             and p.date != query.date and p.date[:7] not in set(heldout_months) and p.bell < cutoff]
    counts = [b.taxonomy_print_count(leg) for p in prior for leg in p.legs]
    counts = np.asarray([c for c in counts if c is not None and np.isfinite(c)], dtype=float)
    threshold = b.inverse_weighted_quantile(counts, np.ones(len(counts)),
                  contract["sleeper_category_quantile"]) if len(counts) else None
    lookup = {p.event_id: p for p in all_pairs}
    family_cache = cache if cache is not None else {}

    def labels(pair):
        result = []
        for leg in pair.legs:
            key = (pair.event_id, leg.leg_id, threshold)
            if key not in family_cache:
                family_cache[key] = b.classify_leg(leg, threshold)["family"]
            result.append(family_cache[key])
        return result

    members = np.asarray([labels(lookup[event]) for event in member_ids], dtype=object).reshape((-1, len(query.legs)))
    actual = labels(query)
    return members, actual, dict(sleeper_threshold=threshold, earlier_count_legs=len(counts),
        latest_training_bell=max((p.bell for p in prior), default=None), cutoff=cutoff,
        heldout_outcomes_excluded=True,
        difference_from_archived_family_diagnostic="earlier-only p10 replaces retrospective whole-category p10; FIRST Q/X unchanged")


def emit_variants(query, candidate, frozen, registry, contract, member_families=None):
    forecasts, conduct_rows, reused = {}, {}, {}
    reused_conduct = {}
    supports = []
    for side in range(len(query.legs)):
        mask = candidate.side_masks[side]
        supports.append(scoring.prepare_candidate_support(candidate.levels[mask, side],
            candidate.floor_times[mask, side], member_families[mask, side] if member_families is not None else None))
    for variant in registry:
        beta = frozen.coefficients[variant.name]
        row = dict(candidate.baseline, sides={})
        sides = {}
        for side, leg in enumerate(query.legs):
            mask = candidate.side_masks[side]
            key = (side, beta.tobytes())
            if key not in reused:
                weights = model.joint_weights(candidate.base_weights[mask], candidate.block_log_k[mask], beta)
                effective = float(b.ess(weights) or 0)
                state = dict(candidate.baseline["sides"][leg.leg_id])
                state.update(ess=effective, member_count=int(mask.sum()),
                    status="OK" if effective >= contract["no_call_ess_floor"] else "INSUFFICIENT_EVIDENCE")
                if np.any(beta):
                    state.pop("floors", None)
                    if state["status"] == "OK":
                        state["floors"] = scoring.prepared_quantiles(supports[side], weights,
                            [q for q in contract["quantiles"] if q in (.25, .5, .75)])
                elif weights.tobytes() != candidate.base_weights[mask].tobytes():
                    raise ValueError("ZERO_COEFFICIENT_FIRST_WEIGHT_DRIFT")
                payload = dict(support=supports[side], weights=weights, ess=effective, status=state["status"],
                               block_support=candidate.block_support[mask], block_names=frozen.kernel.blocks)
                reused[key] = (payload, state)
            payload, common_state = reused[key]
            state = dict(common_state, writer="POOL_FIRST_TICK" if not np.any(beta) else "FEATURE_PANEL:"+variant.name)
            if variant.name == "FIRST" and state.get("floors") != candidate.baseline["sides"][leg.leg_id].get("floors"):
                raise ValueError("FIRST_Q_X_EMITTER_DRIFT:"+query.event_id)
            sides[leg.leg_id], row["sides"][leg.leg_id] = payload, state
        # Equal coefficients produce equal conduct inputs only when the writer
        # also matches. Zero variants share FIRST's writer; nonzero variant
        # names remain distinct. Conduct readers never mutate these rows.
        conduct_key = (beta.tobytes(), "POOL_FIRST_TICK" if not np.any(beta) else "FEATURE_PANEL:"+variant.name)
        forecasts[variant.name], conduct_rows[variant.name] = sides, reused_conduct.setdefault(conduct_key, row)
    return forecasts, conduct_rows


def evaluate_query(query, projector, frozen, registry, scorer, all_pairs, witnesses, conduct_spec,
                   heldout_months, *, stream, family_cache=None, frozen_library_cutoff=None,
                   include_receipt_output=False, gate_scorer=None, filed_gate_scorer=None):
    own_tapes, targets = {}, {}
    for leg in query.legs:
        ticker = query.event_id+"-"+leg.leg_id
        if ticker not in witnesses:
            raise ValueError("MISSING_POSITIVE_PRINT_WITNESS:"+ticker)
        source = witnesses[ticker]
        if (source["formation_end_epoch"], source["bell_epoch"]) != (leg.formation, leg.bell):
            raise ValueError("PRINT_SPAN_MISMATCH:"+ticker)
        rows = source.get("prints", source.get("positive_prints"))
        if rows is None:
            raise ValueError("MISSING_WITNESS_ROWS:"+ticker)
        own_tapes[leg.leg_id] = rows
        targets[leg.leg_id] = PositivePrintTarget(rows, leg.formation, leg.bell, projector.contract["minute_seconds"])
    forecast_rows = {v.name: [] for v in registry}
    counts = Counter()
    block_support_sum = np.zeros(len(frozen.kernel.blocks))
    block_support_n = 0
    family_proof = None
    members_family, actual_family = None, None
    excerpt = []
    for index, candidate in enumerate(projector.receipts(query, "RECEIPT-SIM")):
        if family_proof is None:
            members_family, actual_family, family_proof = causal_families(query, all_pairs,
                candidate.member_ids, projector.contract, heldout_months,
                frozen_cutoff=frozen_library_cutoff, cache=family_cache)
        forecasts, rows = emit_variants(query, candidate, frozen, registry, projector.contract, members_family)
        gate, epoch = candidate.baseline["source_gate_minutes"], candidate.baseline["epoch"]
        is_gate = gate in projector.contract["gates_minutes_to_bell"]
        counts["receipts"] += 1
        counts["atlas_receipts"] += is_gate
        if len(candidate.block_support):
            block_support_sum += candidate.block_support.sum(axis=0)
            block_support_n += len(candidate.block_support)
        for side, leg in enumerate(query.legs):
            low, at = b.remaining_floor(leg, gate)
            reachable = targets[leg.leg_id].at(epoch)
            reachable["family"] = actual_family[side]
            shared_reach_levels = np.unique(candidate.levels[np.isfinite(candidate.levels[:, side]), side])
            reachable["reach_levels"] = shared_reach_levels
            carried = dict(floor_cents=low, floor_mtb=at, family=actual_family[side],
                           reach_floor_cents=reachable["floor_cents"], has_future_print=reachable["has_future_print"],
                           reach_levels=shared_reach_levels)
            identity = dict(category=query.category, event_id=query.event_id, month=query.date[:7],
                side=b.SIDES[side], receipt_id=str(index), gate=None,
                role=candidate.baseline["sides"][leg.leg_id]["role"], stream=stream+"_ALL_RECEIPTS")
            side_forecasts = {name: f[leg.leg_id] for name, f in forecasts.items()}
            scorer.add_receipt(identity, dict(carried=carried, reachable=reachable), side_forecasts)
            if is_gate:
                (gate_scorer or scorer).add_receipt(dict(identity, stream=stream+"_GATES", gate=gate),
                    dict(carried=carried, reachable=reachable), side_forecasts)
                if filed_gate_scorer is not None and query.scorable(gate):
                    filed_gate_scorer.add_receipt(dict(identity, stream=stream+"_FILED_SCORABLE_GATES", gate=gate),
                        dict(carried=carried, reachable=reachable), side_forecasts)
        for name, row in rows.items():
            forecast_rows[name].append(row)
        if include_receipt_output:
            excerpt.append(dict(receipt_index=index, epoch=epoch, minutes_to_bell=gate,
                variants={name: row["sides"] for name, row in rows.items()}))
    results = {}
    spec = dict(conduct_spec, positive_size_fills=True)
    for variant in registry:
        result = conduct.simulate_conduct(query.event_id, [leg.leg_id for leg in query.legs],
            forecast_rows[variant.name], own_tapes, query.formation, query.bell, spec, 0)
        cv2.verify_fills(result, own_tapes)
        results[variant.name] = result
    scorer.add_conduct_event(dict(category=query.category, event_id=query.event_id,
        month=query.date[:7], stream=stream), results)
    return dict(event_id=query.event_id, category=query.category, month=query.date[:7], stream=stream,
        counts=dict(counts), family_scale=family_proof,
        mean_block_comparable_fraction={name: float(total/block_support_n) if block_support_n else None
            for name, total in zip(frozen.kernel.blocks, block_support_sum)},
        conduct={name: {key: value for key, value in result.items()
                       if key not in ("actions", "stepped_off_exposures", "joint_decisions")}
                 for name, result in results.items()},
        receipts=excerpt if include_receipt_output else None)


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name+".partial")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(b.clean(value), indent=2, sort_keys=True, allow_nan=False)+"\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def source_proof(paths):
    return {str(Path(path).resolve()): dict(bytes=Path(path).stat().st_size, sha256=panel.sha256(path))
            for path in paths}


def write_scale_diagnostics(output_dir, frozen, contract):
    """Exact frozen empirical distributions are local arrays, not hidden scales."""
    name = "SCALES_"+frozen.month+".npz"
    arrays = {feature: scale.sorted_values for feature, scale in frozen.kernel.scales.items()}
    np.savez_compressed(Path(output_dir)/name, **arrays)
    quantiles = contract["quantiles"]
    return dict(path=name, sha256=panel.sha256(Path(output_dir)/name), cutoff=frozen.cutoff,
        category=frozen.category, month=frozen.month,
        quantiles_from_filed_contract=list(quantiles),
        fields={feature: dict(n=len(values), quantiles={str(q):
            b.inverse_weighted_quantile(values, np.ones(len(values)), q) if len(values) else None
            for q in quantiles}) for feature, values in arrays.items()},
        meaning="Sorted observed values of earlier-only category atlas side states; missing values excluded from scale, not from pool")


def write_query_diagnostics(output_dir, query, frozen, sampler, stream, scale_proof):
    """One bounded query matrix of raw-source availability and empirical ranks."""
    data = panel.build_pair_panel(query, sampler.metadata, sampler.sources, sampler.witnesses,
        sampler.contract, sampler.par, sampler.codebooks)
    ranks = frozen.kernel.rank(data["values"])
    folder = Path(output_dir)/"receipt_diagnostics"
    folder.mkdir(exist_ok=True)
    name = query.event_id+"__"+stream+".npz"
    extra = {leg+"__"+key: values for leg, fields in data["diagnostic_arrays"].items()
             for key, values in fields.items()}
    field_names = [f.name for f in frozen.kernel.fields]
    if "prefix_cadence_seconds" in field_names:
        cadence_rank = ranks[..., field_names.index("prefix_cadence_seconds")]
        quantiles = np.asarray(sampler.contract["quantiles"])
        extra["cadence_rank_interval"] = np.where(np.isfinite(cadence_rank),
            np.searchsorted(quantiles, cadence_rank, side="right"), np.nan)
        for side, leg in enumerate(query.legs):
            data["coverage"][leg.leg_id]["fields"]["cadence_class"] = int(np.isfinite(cadence_rank[:, side]).sum())
    np.savez_compressed(folder/name, epoch=data["epochs"], gate=data["gates"], is_gate=data["is_gate"],
        raw_value=data["values"], empirical_rank=ranks, feature_names=np.asarray(field_names), **extra)
    return dict(path="receipt_diagnostics/"+name, sha256=panel.sha256(folder/name),
        receipts=len(ranks), category=query.category, month=query.date[:7], event_id=query.event_id, stream=stream,
        scale_file=scale_proof["path"], scale_sha256=scale_proof["sha256"], scale_cutoff=frozen.cutoff,
        coverage=data["coverage"], diagnostics=data["diagnostics"],
        rank_definition="Numeric empirical mid-CDF in frozen earlier-only category distribution; categorical code is unchanged, not an ordinal rank; missing stays NaN",
        cadence_class="Diagnostic interval at filed organ_contract.quantiles; right-side insertion, no new threshold",
        cadence_interval_boundaries=list(sampler.contract["quantiles"]))


def disable_unfiled_authorization(scoreboard):
    """Coverage cohorts do not acquire the filed gate's authorizing status."""
    for group in scoreboard.get("groups", []):
        for target in group.get("targets", {}).values():
            for comparison in target.get("matched_to_first", {}).values():
                comparison["qualifies"] = None
                comparison["filed_side_gate_scope"] = False
                comparison["authorization_scope_note"] = "Coverage cohort only; qualification is published solely in filed_scorable_gates"
    return scoreboard


def flush_checkpoint_output(path):
    # Publish the referenced artifact's bytes before committing its score state.
    with Path(path).open("r+b") as stream:
        os.fsync(stream.fileno())


def validate_checkpoint_outputs(output_dir, state, completed, expected):
    """Validate the exact ordered score prefix and its independently stored files."""
    completed = [tuple(identity) for identity in completed]
    if completed != expected[:len(completed)]:
        raise ValueError("CHECKPOINT_EVALUATION_PREFIX_MISMATCH")
    if state is None:
        if completed:
            raise ValueError("CHECKPOINT_STATE_PREFIX_MISMATCH")
        return
    results, diagnostics = state["all_query_results"], state["diagnostics"]
    if len(results) != len(completed) or len(diagnostics) != len(completed):
        raise ValueError("CHECKPOINT_RESULT_PREFIX_MISMATCH")
    for identity, result, diagnostic in zip(completed, results, diagnostics):
        if (result["event_id"], result["stream"]) != identity[:2]:
            raise ValueError("CHECKPOINT_RESULT_IDENTITY_MISMATCH")
        if result["receipt_diagnostics"] != diagnostic["path"]:
            raise ValueError("CHECKPOINT_DIAGNOSTIC_IDENTITY_MISMATCH")
        path = (Path(output_dir)/diagnostic["path"]).resolve()
        if not path.is_relative_to(Path(output_dir).resolve()) or path.is_symlink():
            raise ValueError("CHECKPOINT_DIAGNOSTIC_PATH_INVALID")
        if not path.is_file() or panel.sha256(path) != diagnostic["sha256"]:
            raise ValueError("CHECKPOINT_DIAGNOSTIC_HASH_MISMATCH:"+str(path))
    if state["evaluation_receipts"] != sum(r["counts"].get("receipts", 0) for r in results):
        raise ValueError("CHECKPOINT_RECEIPT_COUNT_MISMATCH")


def run_category(pairs, sampler, baseline_receipt, conduct_spec, category, output_dir, *,
                 heldout_months, batch_size, cache_budget_bytes, source_registry,
                 numerical_options=None, progress=None, named_pairs=(), workers=1,
                 checkpoint_store=None, import_models=None):
    """Public driver API. Source extraction/hash validation precedes this call.

    All category queries run; no silent --limit, no source availability selector.
    Named checks never enter library, fitting or scales. Root supplies their
    corrected source metadata/witnesses to the same sampler before invocation.
    """
    if not source_registry:
        raise ValueError("HASH_BOUND_SOURCE_REGISTRY_REQUIRED")
    if workers < 1:
        raise ValueError("POSITIVE_WORKER_COUNT_REQUIRED")
    contract = baseline_receipt["organ_contract"]
    fields = tuple(f for f in panel.FIELDS if f.block is not None)
    blocks, registry = tuple(panel.BLOCKS), variant_registry(panel.BLOCKS)
    population = [p for p in pairs if p.category == category]
    if not population:
        raise ValueError("EMPTY_CATEGORY")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scorer = scoring.FeaturePanelScorer(baseline_receipt, [v.name for v in registry],
        groupings=(("category", "stream"), ("category", "stream", "month"),
                   ("category", "stream", "month", "side")),
        identity_mode="contiguous_event", common_variant_metrics=False, metric_profile="core", authorization_streams=())
    gate_scorer = scoring.FeaturePanelScorer(baseline_receipt, [v.name for v in registry],
        groupings=(("category", "stream", "side", "gate"),),
        identity_mode="contiguous_event", common_variant_metrics=False, metric_profile="core", authorization_streams=())
    filed_gate_scorer = scoring.FeaturePanelScorer(baseline_receipt, [v.name for v in registry],
        groupings=(("category", "stream", "side", "gate"),),
        identity_mode="contiguous_event", common_variant_metrics=False, metric_profile="core",
        authorization_streams=("PRIMARY_FILED_SCORABLE_GATES", "STRICT_HOLDOUT_FILED_SCORABLE_GATES"))
    progress = progress or (lambda row: print("PROGRESS "+json.dumps(b.clean(row)), flush=True))
    began = time.monotonic()
    models, all_query_results, family_cache, diagnostics = {}, [], {}, []
    evaluation_seconds = 0.0
    evaluation_receipts = 0
    total_evaluations = len(population)+sum(p.date[:7] in set(heldout_months) for p in population)
    months = sorted({p.date[:7] for p in population})
    plans = {month: outer_month_plan(pairs, category, month, heldout_months) for month in months}
    expected = [(query.event_id, stream, month) for month in months
                for stream in (["PRIMARY", "STRICT_HOLDOUT"] if month in set(heldout_months) else ["PRIMARY"])
                for query in plans[month]["queries"]]
    restored = None if checkpoint_store is None else checkpoint_store.load_state()
    completed_prefix = [] if checkpoint_store is None else list(checkpoint_store.completed)
    validate_checkpoint_outputs(output_dir, restored, completed_prefix, expected)
    if restored is not None:
        scorer, gate_scorer, filed_gate_scorer = (restored["channels"][key] for key in ("all", "gates", "filed"))
        all_query_results, diagnostics = restored["all_query_results"], restored["diagnostics"]
        evaluation_receipts = restored["evaluation_receipts"]
        evaluation_seconds = restored["evaluation_seconds"]
        progress(dict(phase="RESUME_EXACT_SCORES", category=category,
            completed_evaluations=len(completed_prefix), evaluated_receipts=evaluation_receipts))
    completed_set = set(map(tuple, completed_prefix))
    channels = dict(all=scorer, gates=gate_scorer, filed=filed_gate_scorer)
    parallel_pool = None
    if workers > 1 and len(completed_prefix) < total_evaluations:
        from feature_panel_parallel import QueryPool
        parallel_pool = QueryPool(pairs, sampler, baseline_receipt, conduct_spec, registry,
            heldout_months, batch_size, output_dir, workers)
    evaluation_complete = False
    try:
        for month in months:
            plan = plans[month]
            progress(dict(phase="FIT_MONTH", category=category, month=month,
                training_games=len(plan["training"]), cutoff=plan["cutoff"]))
            saved = None if checkpoint_store is None else checkpoint_store.load_model(month)
            if saved is not None:
                frozen, prior_scale_proof = saved
                from feature_panel_recovery import load_recovered_model
                verified, checked_scale = load_recovered_model(output_dir, category, month, plan, contract)
                if verified.receipt != frozen.receipt or checked_scale != prior_scale_proof:
                    raise ValueError("CHECKPOINT_MODEL_OUTPUT_MISMATCH")
            elif import_models is not None:
                from feature_panel_recovery import load_recovered_model
                frozen, prior_scale_proof = load_recovered_model(import_models, category, month, plan, contract)
                progress(dict(phase="MODEL_RECOVERED", category=category, month=month,
                    source=str(import_models)))
            else:
                frozen = fit_outer_month(plan, pairs, sampler, fields, blocks, registry, contract,
                    heldout_months=heldout_months, batch_size=batch_size, cache_budget_bytes=cache_budget_bytes,
                    numerical_options=numerical_options)
            if frozen.receipt["heldout_months"] != list(heldout_months):
                raise ValueError("RECOVERED_MODEL_HELDOUT_MONTHS_MISMATCH")
            models[month] = frozen
            if saved is not None:
                # Never overwrite files referenced by an already durable state.
                scale_proof = prior_scale_proof
            else:
                scale_proof = write_scale_diagnostics(output_dir, frozen, contract)
                frozen.receipt["empirical_distributions"] = scale_proof
                write_json(output_dir/("MODEL_"+month+".json"), frozen.receipt)
                if checkpoint_store is not None:
                    flush_checkpoint_output(output_dir/scale_proof["path"])
                    flush_checkpoint_output(output_dir/("MODEL_"+month+".json"))
                    checkpoint_store.save_model(month, (frozen, scale_proof))
            evaluation_library = pairs
            streams = [("PRIMARY", evaluation_library, None)]
            if month in set(heldout_months):
                locked = [p for p in pairs if p.bell < plan["cutoff"] and p.date[:7] not in set(heldout_months)]
                streams.append(("STRICT_HOLDOUT", locked, plan["cutoff"]))
            for stream, library, library_cutoff in streams:
                queries = [q for q in plan["queries"] if (q.event_id, stream, month) not in completed_set]
                projector = FeatureProjector(library, sampler, contract, frozen.kernel, batch_size=batch_size)
                completed_workers = None if parallel_pool is None else iter(parallel_pool.evaluate(
                    queries, frozen, scale_proof, stream, library_cutoff, channels))
                for query in queries:
                    started = time.monotonic()
                    if completed_workers is None:
                        result = evaluate_query(query, projector, frozen, registry, scorer, pairs,
                            sampler.witnesses, conduct_spec, heldout_months, stream=stream,
                            family_cache=family_cache, frozen_library_cutoff=library_cutoff,
                            gate_scorer=gate_scorer, filed_gate_scorer=filed_gate_scorer)
                        diagnostic = write_query_diagnostics(output_dir, query, frozen, sampler, stream, scale_proof)
                        result["receipt_diagnostics"] = diagnostic["path"]
                        query_seconds = time.monotonic()-started
                    else:
                        completed = next(completed_workers)
                        result, diagnostic = completed["result"], completed["diagnostic"]
                        if result["event_id"] != query.event_id or result["stream"] != stream:
                            raise ValueError("PARALLEL_QUERY_ORDER_MISMATCH")
                        query_seconds = completed["query_seconds"]
                    diagnostics.append(diagnostic)
                    all_query_results.append(result)
                    # Actual parent wall time, not the sum of overlapping worker
                    # durations. Scientific artifacts contain neither rate nor workers.
                    evaluation_seconds += time.monotonic()-started
                    evaluation_receipts += result["counts"].get("receipts", 0)
                    if checkpoint_store is not None:
                        flush_checkpoint_output(output_dir/diagnostic["path"])
                        checkpoint_store.commit_state(dict(channels=channels,
                            all_query_results=all_query_results, diagnostics=diagnostics,
                            evaluation_receipts=evaluation_receipts, evaluation_seconds=evaluation_seconds),
                            completed=[*checkpoint_store.completed, (query.event_id, stream, month)])
                    progress(dict(phase="QUERY_COMPLETE", category=category, month=month, stream=stream,
                        event_id=query.event_id, receipts=result["counts"].get("receipts", 0),
                        query_seconds=query_seconds, elapsed_seconds=time.monotonic()-began,
                        completed_evaluations=len(all_query_results), total_evaluations=total_evaluations,
                        evaluated_receipts=evaluation_receipts, workers=workers,
                        receipts_per_second=evaluation_receipts/evaluation_seconds if evaluation_seconds else None,
                        projected_remaining_evaluation_seconds=evaluation_seconds/len(all_query_results)
                            * (total_evaluations-len(all_query_results)),
                        projection_excludes_future_month_model_fitting=True))
        evaluation_complete = True
    finally:
        if parallel_pool is not None:
            parallel_pool.close(success=evaluation_complete)
    named = []
    for query in named_pairs:
        if query.category != category:
            continue
        # Named games are outside the model-selection census. Build a plan at
        # their own first formation with the same expanding inner-month method.
        plan = outer_month_plan(pairs+[query], category, query.date[:7], heldout_months)
        plan["cutoff"] = min(plan["cutoff"], query.formation)
        frozen = models.get(query.date[:7])
        if frozen is None:
            frozen = fit_outer_month(plan, pairs, sampler, fields, blocks, registry, contract,
                heldout_months=heldout_months, batch_size=batch_size, cache_budget_bytes=cache_budget_bytes,
                numerical_options=numerical_options)
        projector = FeatureProjector(pairs, sampler, contract, frozen.kernel, batch_size=batch_size)
        named_scorer = scoring.FeaturePanelScorer(baseline_receipt, [v.name for v in registry])
        named.append(evaluate_query(query, projector, frozen, registry, named_scorer, pairs+[query],
            sampler.witnesses, conduct_spec, heldout_months, stream="NAMED", family_cache=family_cache,
            include_receipt_output=True))
    scoreboard = dict(all_receipts=disable_unfiled_authorization(scorer.finish()),
        gates=disable_unfiled_authorization(gate_scorer.finish()),
        filed_scorable_gates=filed_gate_scorer.finish())
    write_json(output_dir/"FEATURE_PANEL_DIAGNOSTICS.json", diagnostics)
    write_json(output_dir/"FEATURE_PANEL_SCOREBOARD.json", scoreboard)
    write_json(output_dir/"FEATURE_PANEL_QUERIES.json", all_query_results)
    write_json(output_dir/"FEATURE_PANEL_NAMED_CHECKS.json", named)
    receipt = dict(status="BENCH_ONLY_NO_ENGINE_CHANGE", category=category,
        eligible_games=len(population), evaluated_stream_games=len(all_query_results),
        heldout_months=list(heldout_months), baseline_receipt_sha256=hashlib.sha256(
            json.dumps(baseline_receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        source_registry=source_registry, variants=[dict(name=v.name, blocks=list(v.blocks)) for v in registry],
        model_files=["MODEL_"+month+".json" for month in months],
        fields=panel.field_registry(), protocol=dict(
            primary="original FIRST walk-forward library for every query; held-out query outcomes never fit models",
            strict_holdout="models/scales and member library frozen before held-out month's earliest formation; same FIRST library",
            nested="expanding calendar prefixes; inner validation only already-resolved prior-month subsets; equal-game CRPS",
            no_inner_history="FIRST_ZERO, no invented coefficient",
            kernel="snapshot as-of both legs at same minutes-to-bell; per-block mean comparable-feature distance",
            missing="neutral with support reported, never impute zero or delete a member",
            conduct="unchanged R0, size-positive strictly later pre-bell accepted prints; reachable not certain",
            targets="unchanged carried-state predictor scored separately against carried-state and strictly-later positive-print floors",
            reach_calibration_grid="Same finite unique candidate levels for every variant, including zero-underflow-weight candidates",
            qualification="FILED_SCORABLE_GATES only: query.scorable(gate); all-eligible gates retained separately for coverage, not authorization",
            historical_exposure="held-out month was inspected by older studies; this is an untouched fitting/evaluation partition for this experiment"),
        numerical_execution=dict(batch_size=batch_size, cache_budget_bytes=cache_budget_bytes,
            cache_limit_exceeded="abort, never omit queries", elapsed_seconds=time.monotonic()-began),
        outputs={p.name: dict(bytes=p.stat().st_size, sha256=panel.sha256(p)) for p in output_dir.iterdir()
                 if p.is_file() and p.name != "FEATURE_PANEL_RECEIPT.json"})
    write_json(output_dir/"FEATURE_PANEL_RECEIPT.json", receipt)
    return receipt, scoreboard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show-protocol", action="store_true",
                        help="Print the variant registry; no population run without bound source adapter.")
    args = parser.parse_args()
    if not args.show_protocol:
        parser.error("Use run_category with verified source registry; raw-source paths are bound by the extraction driver.")
    print(json.dumps(dict(blocks=list(panel.BLOCKS), variants=[dict(name=v.name, blocks=list(v.blocks))
        for v in variant_registry(panel.BLOCKS)]), indent=2))


if __name__ == "__main__":
    main()
