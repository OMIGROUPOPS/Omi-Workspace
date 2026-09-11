"""Joint FIRST feature likelihood, isolated bench helper (never imports the OS).

Model choices: numeric differences use earlier-only empirical mid-ranks;
categorical differences are Hamming distances. A block uses the mean distance
over comparable features. Missing values have no fabricated value: a block
with no comparable features is neutral, and support is reported separately.
Coefficients are continuous and nonnegative. Zero coefficients reproduce the
unmodified FIRST weights exactly. There is no learned member selector.

CRPS is averaged within game, then across games. Its gradient is exact up to
floating arithmetic, including tied atoms. The coefficient objective is NOT
claimed convex: the deterministic projected-gradient optimizer starts at zero
and reports convergence/local-stationarity, never a global optimum. Optimizer
tolerances and iteration/backtracking limits below are numerical controls, not
pool, price, callability, or economic thresholds. No coefficient grid or
regularization penalty is introduced.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import math
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


def _number(value: Any) -> bool:
    return not isinstance(value, (bool, np.bool_)) and isinstance(
        value, (int, float, np.integer, np.floating)) and math.isfinite(float(value))


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (float, np.floating)) and not math.isfinite(float(value)):
        return False
    return True


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    kind: str  # numeric or categorical

    def __post_init__(self):
        if self.kind not in {"numeric", "categorical"}:
            raise ValueError("UNKNOWN_FEATURE_KIND:" + self.kind)


@dataclass(frozen=True)
class EmpiricalRankScale:
    """Mid empirical CDF, with ties sharing their probability rank."""
    sorted_values: np.ndarray

    @classmethod
    def fit(cls, values: Iterable[Any]) -> "EmpiricalRankScale":
        observed = np.asarray([float(v) for v in values if _number(v)], dtype=float)
        return cls(np.sort(observed, kind="stable"))

    def rank(self, value: Any) -> float | None:
        if not _number(value) or not len(self.sorted_values):
            return None
        left = np.searchsorted(self.sorted_values, float(value), side="left")
        right = np.searchsorted(self.sorted_values, float(value), side="right")
        return float((left + right) / (len(self.sorted_values) + len(self.sorted_values)))


def select_training_records(records: Iterable[Mapping[str, Any]],
                            query: Mapping[str, Any], *,
                            heldout_months: Sequence[str] = ()):
    """Pure temporal filter; caller supplies filed event-name dates.

    Required query keys: event_id, category, date, formation. Records require
    event_id, category, date, bell. All outcomes from held-out event-date months
    are excluded, including when selecting for later queries in those months.
    No event name parsing, month selection, or missing metadata inference.
    """
    for key in ("event_id", "category", "date", "formation"):
        if key not in query:
            raise ValueError("MISSING_QUERY_METADATA:" + key)
    if not _number(query["formation"]):
        raise ValueError("INVALID_QUERY_FORMATION")
    selected, reasons = [], Counter()
    heldout = set(heldout_months)
    for record in records:
        for key in ("event_id", "category", "date", "bell"):
            if key not in record:
                raise ValueError("MISSING_TRAINING_METADATA:" + key)
        if not _number(record["bell"]):
            raise ValueError("INVALID_TRAINING_BELL")
        if record["event_id"] == query["event_id"]:
            reason = "SELF"
        elif record["category"] != query["category"]:
            reason = "OTHER_CATEGORY"
        elif record["date"] == query["date"]:
            reason = "SAME_EVENT_DATE"
        elif record["date"][:len("YYYY-MM")] in heldout:
            reason = "HELDOUT_MONTH"
        elif record["bell"] >= query["formation"]:
            reason = "NOT_EARLIER_RESOLVED"
        else:
            selected.append(record)
            continue
        reasons[reason] += 1
    return selected, dict(sorted(reasons.items()))


def fit_rank_scales(records: Sequence[Mapping[str, Any]],
                    features: Sequence[FeatureSpec]):
    """Fit from caller-filtered earlier records; never reads query/member futures."""
    return {f.name: EmpiricalRankScale.fit(r.get(f.name) for r in records)
            for f in features if f.kind == "numeric"}


def block_likelihoods(query: Mapping[str, Any], members: Sequence[Mapping[str, Any]],
                      blocks: Mapping[str, Sequence[FeatureSpec]],
                      scales: Mapping[str, EmpiricalRankScale]):
    """Return per-member, per-block log likelihood plus observed support.

    Duplicate feature names inside a block are refused. Matching zero remains
    an observation; missing never becomes zero. Categorical values must be
    scalar stored tokens, never target/future labels. The caller owns this
    causal field contract and the frozen category-specific scale provenance.
    """
    names = tuple(blocks)
    logs = np.zeros((len(members), len(names)), dtype=float)
    comparable = np.zeros(logs.shape, dtype=np.int64)
    declared = np.asarray([len(blocks[name]) for name in names], dtype=np.int64)
    if np.any(declared == 0):
        raise ValueError("EMPTY_FEATURE_BLOCK")
    for column, name in enumerate(names):
        features = blocks[name]
        if len({f.name for f in features}) != len(features):
            raise ValueError("DUPLICATE_FEATURE_IN_BLOCK:" + name)
        for index, member in enumerate(members):
            distances = []
            for feature in features:
                q, m = query.get(feature.name), member.get(feature.name)
                if feature.kind == "numeric":
                    if feature.name not in scales:
                        raise ValueError("MISSING_NUMERIC_SCALE:" + feature.name)
                    qr, mr = scales[feature.name].rank(q), scales[feature.name].rank(m)
                    if qr is not None and mr is not None:
                        distances.append(abs(qr - mr))
                elif _present(q) and _present(m):
                    distances.append(float(q != m))
            comparable[index, column] = len(distances)
            if distances:
                logs[index, column] = -math.log1p(math.fsum(distances) / len(distances))
    return dict(block_names=names, block_log_k=logs,
                comparable_feature_counts=comparable,
                declared_feature_counts=declared,
                support_fraction=comparable / declared,
                missing_policy="NEUTRAL_IF_NO_COMPARABLE_FEATURE; MEAN_OVER_COMPARABLE",
                member_count=len(members))


def joint_weights(base_weights, block_log_k, beta):
    base = np.asarray(base_weights, dtype=float)
    logs = np.asarray(block_log_k, dtype=float)
    coefficients = np.asarray(beta, dtype=float)
    if base.ndim != 1 or logs.shape != (len(base), len(coefficients)):
        raise ValueError("WEIGHT_SHAPE_MISMATCH")
    if coefficients.ndim != 1 or not np.all(np.isfinite(coefficients)) or np.any(coefficients < 0):
        raise ValueError("INVALID_NONNEGATIVE_COEFFICIENTS")
    if not np.all(np.isfinite(base)) or np.any(base < 0):
        raise ValueError("INVALID_FIRST_WEIGHTS")
    if not np.all(np.isfinite(logs)) or np.any(logs > 0):
        raise ValueError("INVALID_BLOCK_LOG_LIKELIHOOD")
    if not np.any(coefficients):
        return base.copy()  # exact FIRST control, including its original scale
    active = base > 0
    weights = np.zeros_like(base)
    if np.any(active):
        combined = np.log(base[active]) + logs[active] @ coefficients
        if not np.all(np.isfinite(combined)):
            raise FloatingPointError("NONFINITE_JOINT_LOG_WEIGHT")
        weights[active] = np.exp(combined - np.max(combined))
    return weights


def effective_sample_size(weights):
    weights = np.asarray(weights, dtype=float)
    if not len(weights) or not np.any(weights > 0):
        return None
    relative = weights / np.max(weights)
    return float(relative.sum() ** 2 / np.dot(relative, relative))


def crps_and_gradient(candidate_levels, base_weights, block_log_k, actual, beta):
    """Sorted weighted CRPS and exact coefficient gradient, ties included."""
    levels = np.asarray(candidate_levels, dtype=float)
    logs = np.asarray(block_log_k, dtype=float)
    weights = joint_weights(base_weights, logs, beta)
    if levels.shape != weights.shape or not np.all(np.isfinite(levels)) or not _number(actual):
        raise ValueError("INVALID_CRPS_TARGET_OR_CANDIDATES")
    if not np.any(weights > 0):
        raise ValueError("NO_FIRST_MASS")
    order = np.argsort(levels, kind="stable")
    x, p, feature_logs = levels[order], weights[order] / weights.sum(), logs[order]
    return _sorted_crps_and_gradient(x, p, feature_logs, actual)


def _sorted_crps_and_gradient(x, p, feature_logs, actual):
    """Arithmetic kernel; fixed candidate ordering can be cached during fit."""
    cumulative_p = np.cumsum(p)
    cumulative_px = np.cumsum(p * x)
    left_p, left_px = cumulative_p - p, cumulative_px - p * x
    right_p, right_px = p.sum() - cumulative_p, cumulative_px[-1] - cumulative_px
    expected_distance = x * left_p - left_px + right_px - x * right_p
    absolute_error = np.abs(x - float(actual))
    score = float(np.dot(p, absolute_error) - np.dot(p, expected_distance) / (1 + 1))
    derivative_p = absolute_error - expected_distance
    centered = derivative_p - np.dot(p, derivative_p)
    gradient = (p * centered) @ feature_logs
    return score, np.asarray(gradient, dtype=float)


@dataclass(frozen=True)
class PoolSample:
    candidate_levels: np.ndarray
    base_weights: np.ndarray
    block_log_k: np.ndarray
    actual: float
    gameid: str

    @classmethod
    def from_mapping(cls, value):
        return cls(np.asarray(value["candidate_levels"], dtype=float),
                   np.asarray(value["base_weights"], dtype=float),
                   np.asarray(value["block_log_k"], dtype=float),
                   float(value["actual"]), str(value["gameid"]))


@dataclass(frozen=True)
class NumericalOptions:
    """Numerical controls only. Changing these cannot change feature definitions."""
    gradient_tolerance: float = 1e-8
    objective_tolerance: float = 1e-12
    maximum_iterations: int = 2000
    maximum_backtracks: int = 60
    armijo_fraction: float = 1e-4
    backtrack_fraction: float = 0.5
    initial_step: float = 1.0

    def __post_init__(self):
        if not (self.gradient_tolerance > 0 and self.objective_tolerance > 0
                and self.maximum_iterations > 0 and self.maximum_backtracks > 0
                and 0 < self.armijo_fraction < 1 and 0 < self.backtrack_fraction < 1
                and self.initial_step > 0):
            raise ValueError("INVALID_NUMERICAL_CONTROLS")


@dataclass
class JointModel:
    block_names: tuple[str, ...]
    beta: np.ndarray
    report: dict

    def predict(self, base_weights, block_log_k):
        weights = joint_weights(base_weights, block_log_k, self.beta)
        return dict(weights=weights, ess=effective_sample_size(weights),
                    member_count=int(np.count_nonzero(np.asarray(base_weights) > 0)),
                    represented_member_count=int(np.count_nonzero(weights)),
                    numerically_underflowed_members=int(np.count_nonzero(
                        (np.asarray(base_weights) > 0) & (weights == 0))),
                    beta=dict(zip(self.block_names, map(float, self.beta))))


def evaluate_joint_model(samples: Sequence[PoolSample | Mapping[str, Any]], beta):
    """Frozen-model validation: exactly the fitting objective, with game detail."""
    game_values: dict[str, list[float]] = {}
    for raw in samples:
        sample = raw if isinstance(raw, PoolSample) else PoolSample.from_mapping(raw)
        value, _ = crps_and_gradient(sample.candidate_levels, sample.base_weights,
                                    sample.block_log_k, sample.actual, beta)
        game_values.setdefault(sample.gameid, []).append(value)
    means = {game: math.fsum(values) / len(values) for game, values in game_values.items()}
    return dict(crps=math.fsum(means.values()) / len(means) if means else None,
                games=len(means), samples=sum(map(len, game_values.values())),
                per_game_crps=means,
                objective="mean game CRPS, mean receipt/side CRPS within each game")


def fit_joint_model(samples: Sequence[PoolSample | Mapping[str, Any]],
                    block_names: Sequence[str], *, options: NumericalOptions | None = None):
    """Fit a finite, caller-bounded cache of earlier-only samples.

    Caller must apply select_training_records before constructing samples and
    fitting rank scales. This function does not read any dates, tables, files,
    engine state, future query observations, or validation outcomes itself.
    It returns diagnostics; caller must not publish nonconverged coefficients
    as though they were the selected optimum.
    """
    opts = options or NumericalOptions()
    names = tuple(block_names)
    if not names or len(set(names)) != len(names):
        raise ValueError("EMPTY_OR_DUPLICATED_BLOCK_NAMES")
    prepared = [s if isinstance(s, PoolSample) else PoolSample.from_mapping(s) for s in samples]
    beta = np.zeros(len(names), dtype=float)
    if not prepared:
        return JointModel(names, beta, dict(status="UNTRAINED_FIRST_CONTROL", samples=0,
            games=0, numerical_controls=asdict(opts), beta=dict(zip(names, map(float, beta)))))
    # Candidate levels do not depend on beta. Cache their stable ordering once,
    # not once per optimizer evaluation. No member, atom, or tie is removed.
    ordered_samples = []
    for sample in prepared:
        levels = np.asarray(sample.candidate_levels, dtype=float)
        base = np.asarray(sample.base_weights, dtype=float)
        logs = np.asarray(sample.block_log_k, dtype=float)
        if levels.ndim != 1 or not np.all(np.isfinite(levels)) or not _number(sample.actual):
            raise ValueError("INVALID_CRPS_TARGET_OR_CANDIDATES")
        if base.shape != levels.shape or logs.shape != (len(levels), len(names)):
            raise ValueError("SAMPLE_BLOCK_WIDTH_MISMATCH")
        order = np.argsort(levels, kind="stable")
        ordered_samples.append(PoolSample(levels[order], base[order], logs[order],
                                         sample.actual, sample.gameid))
    prepared = ordered_samples
    counts = Counter(s.gameid for s in prepared)
    sample_mass = np.asarray([1 / (len(counts) * counts[s.gameid]) for s in prepared])
    evaluations = 0

    def objective(coefficients):
        nonlocal evaluations
        evaluations += 1
        values, derivatives = [], []
        for sample in prepared:
            weights = joint_weights(sample.base_weights, sample.block_log_k, coefficients)
            if not np.any(weights > 0):
                raise ValueError("NO_FIRST_MASS")
            value, gradient = _sorted_crps_and_gradient(sample.candidate_levels,
                weights / weights.sum(), sample.block_log_k, sample.actual)
            if gradient.shape != coefficients.shape:
                raise ValueError("SAMPLE_BLOCK_WIDTH_MISMATCH")
            values.append(value)
            derivatives.append(gradient)
        return float(np.dot(sample_mass, values)), sample_mass @ np.asarray(derivatives)

    score, gradient = objective(beta)
    first_score = score
    step = opts.initial_step
    status = "MAXIMUM_ITERATIONS"
    iterations = 0
    history = [dict(iteration=0, crps=score, beta=beta.tolist())]
    for iteration in range(opts.maximum_iterations):
        projected = np.where((beta > 0) | (gradient < 0), gradient, 0)
        if np.max(np.abs(projected)) <= opts.gradient_tolerance:
            status = "PROJECTED_GRADIENT_CONVERGED"
            break
        accepted = False
        for _ in range(opts.maximum_backtracks):
            candidate = np.maximum(0, beta - step * gradient)
            direction = candidate - beta
            if not np.any(direction):
                step *= opts.backtrack_fraction
                continue
            try:
                proposed, next_gradient = objective(candidate)
            except FloatingPointError:
                step *= opts.backtrack_fraction
                continue
            if proposed <= score + opts.armijo_fraction * np.dot(gradient, direction):
                accepted = True
                break
            step *= opts.backtrack_fraction
        if not accepted:
            status = "LINE_SEARCH_STALLED"
            break
        improvement = score - proposed
        old_gradient = gradient
        beta, score, gradient = candidate, proposed, next_gradient
        iterations = iteration + 1
        history.append(dict(iteration=iterations, crps=score, beta=beta.tolist()))
        projected = np.where((beta > 0) | (gradient < 0), gradient, 0)
        if np.max(np.abs(projected)) <= opts.gradient_tolerance:
            status = "PROJECTED_GRADIENT_CONVERGED"
            break
        if improvement <= opts.objective_tolerance * max(1, abs(score)):
            status = "OBJECTIVE_STALLED"
            break
        # Barzilai--Borwein trial step; Armijo still decides acceptance.
        curvature = float(np.dot(direction, gradient - old_gradient))
        step = float(np.dot(direction, direction) / curvature) if curvature > 0 else opts.initial_step
    final_projected = np.where((beta > 0) | (gradient < 0), gradient, 0)
    return JointModel(names, beta, dict(status=status, samples=len(prepared), games=len(counts),
        objective="mean game CRPS, mean receipt/side CRPS within each game",
        first_crps=first_score, fitted_crps=score, iterations=iterations, evaluations=evaluations,
        projected_gradient_max=float(np.max(np.abs(final_projected))),
        numerical_controls=asdict(opts), beta=dict(zip(names, map(float, beta))),
        optimizer="nonnegative projected gradient, Armijo backtracking, zero initialization",
        global_optimum_claimed=False, history=history))
