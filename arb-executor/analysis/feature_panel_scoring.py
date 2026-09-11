"""Streaming, report-only feature-panel scoring; no fitting or engine imports.

``FeaturePanelScorer.add_receipt(identity, targets, forecasts)`` accepts one
forecast per variant and scores that *same* distribution against each target.
Identity requires category/event_id/side/receipt_id and may contain month,
gate, role and stream (use distinct streams for gates and all receipts).
Targets are ``{name: {floor_cents, floor_mtb, has_future_print, family}}``.
Forecasts contain absolute candidate ``values``, ``weights`` and optional
``times``/``families``; weights are already learned and causally filtered by
the caller. Alternatively supply ``ess``, ``status`` and ``metrics`` or
``metrics_by_target`` for metrics already evaluated by the caller. Explicit
NO-CALL statuses are respected even when ESS is sufficient.

No-call, quantiles and the filed strict-win criterion come from the supplied
baseline receipt. Missing truth or measurements stay missing. Positive-weight
missing candidate floors are explicitly removed from the floor distribution;
their weight share and the resulting floor ESS are reported. No independent
reachable predictor is constructed. June partitioning belongs to the caller;
this module performs no training or model selection.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
import math
import numpy as np


def _finite(value):
    return isinstance(value, (int, float, np.integer, np.floating, np.bool_)) and math.isfinite(value)


def _array(value, name):
    result = np.asarray(value, dtype=float)
    if result.ndim != 1:
        raise ValueError("EXPECTED_ONE_DIMENSION:" + name)
    return result


def effective_sample_size(weights):
    """Scale invariant ESS, including empty/all-zero candidate pools."""
    w = _array(weights, "weights")
    if np.any(~np.isfinite(w)) or np.any(w < 0):
        raise ValueError("INVALID_WEIGHTS")
    if not len(w) or not np.any(w):
        return 0.0
    w = w / np.max(w)
    return float(w.sum() ** 2 / np.dot(w, w))


def _normalized(values, weights, order=None):
    x, w = _array(values, "values"), _array(weights, "weights")
    if x.shape != w.shape:
        raise ValueError("CANDIDATE_LENGTH_MISMATCH")
    effective_sample_size(w)  # Validate before masking, including inactive rows.
    active = np.isfinite(x) & (w > 0)
    if not np.any(active):
        return np.array([], dtype=float), np.array([], dtype=float)
    if order is None:
        w = w[active] / np.max(w[active])
        order = np.argsort(x[active], kind="stable")
        return x[active][order], (w / w.sum())[order]
    selected = order[active[order]]
    scaled = np.zeros_like(w)
    scaled[active] = w[active] / np.max(w[active])
    return x[selected], scaled[selected] / scaled[active].sum()


@dataclass(frozen=True, slots=True)
class PreparedCandidateSupport:
    """Immutable candidate arrays and reusable orders across variant weights."""
    values: np.ndarray
    times: np.ndarray | None
    families: np.ndarray | None
    floor_order: np.ndarray
    time_order: np.ndarray | None


def prepare_candidate_support(values, times=None, families=None):
    """Sort one shared candidate support once; does not fit or change weights.

    Pass the result as ``forecast['support']`` instead of ``values``/``times``/
    ``families``. Every variant still supplies its own ``weights`` and status.
    Owned read-only copies prevent a caller's later array edits changing the
    prepared distribution. Candidate ordering and inverse-CDF ties are exact.
    """
    values = _array(values, "values").copy()
    if times is not None:
        times = _array(times, "times").copy()
        if len(times) != len(values):
            raise ValueError("CANDIDATE_TIME_LENGTH_MISMATCH")
    if families is not None:
        families = np.asarray(families, dtype=object).copy()
        if families.ndim != 1 or len(families) != len(values):
            raise ValueError("CANDIDATE_FAMILY_LENGTH_MISMATCH")
    floor_order = np.argsort(values, kind="stable")
    time_order = np.argsort(times, kind="stable") if times is not None else None
    for array in (values, times, families, floor_order, time_order):
        if array is not None:
            array.flags.writeable = False
    return PreparedCandidateSupport(values, times, families, floor_order, time_order)


def prepared_quantiles(support, weights, quantiles):
    """Independent price/time inverse-CDF marginals with reusable sort orders.

    This is a mechanical substitute for repeated weighted-quantile calls, not
    a call/authority decision. The caller retains its filed status/ESS gate.
    """
    if not isinstance(support, PreparedCandidateSupport):
        raise ValueError("INVALID_PREPARED_SUPPORT")
    x, p = _normalized(support.values, weights, support.floor_order)
    cumulative = np.cumsum(p)
    if support.times is not None:
        t, tw = _normalized(support.times, weights, support.time_order)
        time_cumulative = np.cumsum(tw)
    else:
        t = []
    output = {}
    for q in quantiles:
        if not 0 <= q <= 1:
            raise ValueError("INVALID_QUANTILE")
        output[_qname(q)] = dict(level_cents=_sorted_quantile(x, cumulative, q) if len(x) else None,
            minutes_to_bell=_sorted_quantile(t, time_cumulative, q) if len(t) else None)
    return output


def weighted_quantile(values, weights, quantile):
    """Exact inverse weighted CDF, with earliest sorted support at a tie."""
    if not 0 <= quantile <= 1:
        raise ValueError("INVALID_QUANTILE")
    x, p = _normalized(values, weights)
    if not len(x):
        return None
    return _sorted_quantile(x, np.cumsum(p), quantile)


def _sorted_quantile(values, cumulative, quantile):
    index = min(int(np.searchsorted(cumulative, quantile, side="left")), len(values)-1)
    return float(values[index])


def weighted_crps(values, weights, truth):
    """E|X-y| - E|X-X'|/2 in O(n log n), without a quadratic matrix."""
    if not _finite(truth):
        return None
    x, p = _normalized(values, weights)
    if not len(x):
        return None
    return _sorted_crps(x, p, truth)


def _sorted_crps(x, p, truth):
    # Translation reduces cancellation for large absolute price coordinates.
    z = x - x[0]
    previous_mass = np.cumsum(p) - p
    previous_value = np.cumsum(p*z) - p*z
    half_pair_distance = np.sum(p * (z * previous_mass - previous_value))
    return float(max(0.0, np.dot(p, np.abs(x-truth)) - half_pair_distance))


@dataclass(frozen=True)
class ScoreContract:
    no_call_ess_floor: float
    quantiles: tuple
    minimum_matched_queries: int
    minimum_strictly_closer_share: float

    @classmethod
    def from_baseline(cls, receipt):
        organ = receipt["organ_contract"]
        criterion = receipt["matched_step_first"]["criterion"]
        contract = cls(float(organ["no_call_ess_floor"]),
                       tuple(float(q) for q in organ["quantiles"]),
                       int(criterion["minimum_matched_queries"]),
                       float(criterion["minimum_step_strictly_closer_share"]))
        if (not _finite(contract.no_call_ess_floor) or contract.no_call_ess_floor <= 0
                or contract.minimum_matched_queries <= 0
                or not 0 <= contract.minimum_strictly_closer_share <= 1
                or not contract.quantiles or len(set(contract.quantiles)) != len(contract.quantiles)
                or any(not 0 <= q <= 1 for q in contract.quantiles)
                or .5 not in contract.quantiles):
            raise ValueError("INVALID_BASELINE_SCORE_CONTRACT")
        return contract

    def criterion_met(self, n, strictly_closer):
        return (n >= self.minimum_matched_queries
                and strictly_closer >= self.minimum_strictly_closer_share*n)

    def as_dict(self):
        return dict(no_call_ess_floor=self.no_call_ess_floor, quantiles=list(self.quantiles),
                    minimum_matched_queries=self.minimum_matched_queries,
                    minimum_strictly_closer_share=self.minimum_strictly_closer_share,
                    ties="included in denominator, not strict wins", engine_authorship_enabled=False)


class _FrozenMapping(dict):
    """Ordered, pickleable read-only mapping for prepared receipt journals."""

    def _immutable(self, *args, **kwargs):
        raise TypeError("PREPARED_RECEIPT_IS_IMMUTABLE")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _immutable

    def __reduce__(self):
        # Reconstruct through dict's constructor, never its blocked mutators.
        return type(self), (dict(self),)


def _freeze_receipt_value(value):
    if isinstance(value, _FrozenMapping):
        return value
    if isinstance(value, Mapping):
        return _FrozenMapping((key, _freeze_receipt_value(item)) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_receipt_value(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class PreparedReceipt:
    """Pure scored result; worker preparation never updates aggregate state.

    Configuration and identity travel with every row. The parent validates them
    and applies rows in original receipt order; no partial sums are reduced.
    Nested mappings are immutable and pickle preserves shared variant rows.
    """
    configuration: tuple
    identity: _FrozenMapping
    eligible: bool
    scored: _FrozenMapping


def _qname(q):
    return "q" + format(q*100, ".12g")


def _probability(value):
    if not _finite(value) or not 0 <= value <= 1:
        raise ValueError("INVALID_PROBABILITY")
    return float(value)


def _core_metric(name):
    if name.startswith("quantiles."):
        return name.endswith(".signed_error_cents")
    if name.startswith("floor_band."):
        return not name.endswith(".width_cents")
    if name.startswith("reach."):
        return name.startswith(("reach.support.", "reach."+_qname(.5)+"."))
    return True


def score_distribution(forecast, target, contract, *, target_name=None):
    """Evaluate one already-frozen forecast; never consult truth to author it.

    Signed price errors are prediction minus truth. Signed timing errors are
    predicted minutes-to-bell minus realized minutes-to-bell (positive means
    predicted earlier). Reach is strict-future truth only when the caller
    supplies ``has_future_print`` or ``reach_floor_cents``. Optional target
    ``reach_levels`` supplies a shared evaluation grid across variants; absent
    that field, each forecast's unique support is used. Candidate-support
    reach metrics average support levels within each receipt, then the panel
    averages receipts; candidate count never becomes a query count.
    """
    target, forecast = target or {}, forecast or {}
    support = forecast.get("support")
    if support is not None and not isinstance(support, PreparedCandidateSupport):
        raise ValueError("INVALID_PREPARED_SUPPORT")
    if support is not None and any(key in forecast for key in ("values", "times", "families")):
        raise ValueError("AMBIGUOUS_PREPARED_SUPPORT")
    candidate = "values" in forecast or support is not None
    x = p = np.array([], dtype=float)
    raw_weights = None
    available_share = None
    if candidate:
        values = support.values if support is not None else _array(forecast["values"], "values")
        raw_weights = _array(forecast["weights"], "weights")
        x, p = _normalized(values, raw_weights, support.floor_order if support is not None else None)
        active = np.isfinite(values) & (raw_weights > 0)
        ess = effective_sample_size(raw_weights * active)
        if np.any(raw_weights):
            scaled = raw_weights / np.max(raw_weights)
            available_share = float(scaled[active].sum() / scaled.sum())
        else:
            available_share = 0.0
    else:
        ess = forecast.get("ess", 0.0)
        if not _finite(ess) or ess < 0:
            raise ValueError("INVALID_ESS")
    status = forecast.get("status", "OK" if forecast else "MISSING_FORECAST")
    called = status == "OK" and ess >= contract.no_call_ess_floor
    if status == "OK" and not called:
        status = "NO_CALL_ESS"
    result = dict(status=status, called=bool(called), ess=float(ess),
                  candidate_floor_available_weight_share=available_share,
                  target_floor_available=_finite(target.get("floor_cents")),
                  metrics={}, quantiles={})
    if not called:
        return result
    metrics = result["metrics"]
    if not candidate:
        supplied = forecast.get("metrics_by_target", {}).get(target_name, forecast.get("metrics", {}))
        for name, value in supplied.items():
            if value is not None:
                if not _finite(value):
                    raise ValueError("NONFINITE_READY_METRIC:" + name)
                metrics[str(name)] = float(value)
        return result

    truth = target.get("floor_cents")
    time_truth = target.get("floor_mtb")
    times = support.times if support is not None else forecast.get("times")
    if times is not None:
        times = _array(times, "times")
        if len(times) != len(raw_weights):
            raise ValueError("CANDIDATE_TIME_LENGTH_MISMATCH")
        # The independent timing marginal uses the same active floor members.
        time_weights = raw_weights * active
        finite_times = np.isfinite(times)
        time_ess = effective_sample_size(time_weights * finite_times)
        metrics["timing_candidate_ess"] = time_ess
        time_values, time_probabilities = _normalized(times, time_weights, support.time_order if support is not None else None)
        time_cumulative = np.cumsum(time_probabilities)
    else:
        time_weights, time_ess = None, 0.0
    if _finite(truth):
        metrics["floor_crps_cents"] = _sorted_crps(x, p, truth)
    quantiles = result["quantiles"]
    cumulative = np.cumsum(p)
    for q in contract.quantiles:
        name = _qname(q)
        level = _sorted_quantile(x, cumulative, q)
        at = (_sorted_quantile(time_values, time_cumulative, q)
              if times is not None and time_ess >= contract.no_call_ess_floor else None)
        quantiles[name] = dict(level_cents=level, minutes_to_bell=at)
        if _finite(truth):
            metrics[f"quantiles.{name}.signed_error_cents"] = level-truth
            metrics[f"quantiles.{name}.absolute_error_cents"] = abs(level-truth)
            metrics[f"quantiles.{name}.cdf_hit"] = float(truth <= level)
            metrics[f"quantiles.{name}.nominal_calibration_gap"] = float(truth <= level)-q
        if _finite(time_truth) and at is not None:
            metrics[f"quantiles.{name}.timing_signed_error_minutes"] = at-time_truth
            metrics[f"quantiles.{name}.timing_absolute_error_minutes"] = abs(at-time_truth)
    median = quantiles[_qname(.5)]
    if _finite(truth):
        metrics["floor_signed_error_cents"] = median["level_cents"]-truth
        metrics["floor_absolute_error_cents"] = abs(median["level_cents"]-truth)
    if _finite(time_truth) and median["minutes_to_bell"] is not None:
        metrics["floor_timing_signed_error_minutes"] = median["minutes_to_bell"]-time_truth
        metrics["floor_timing_absolute_error_minutes"] = abs(median["minutes_to_bell"]-time_truth)
    for lo in contract.quantiles:
        highs = [hi for hi in contract.quantiles if lo < .5 < hi and math.isclose(lo+hi, 1)]
        for hi in highs:
            prefix = f"floor_band.{_qname(lo)}_{_qname(hi)}"
            low, high = quantiles[_qname(lo)]["level_cents"], quantiles[_qname(hi)]["level_cents"]
            metrics[prefix+".width_cents"] = high-low
            if _finite(truth):
                hit = float(low <= truth <= high)
                metrics[prefix+".coverage"] = hit
                metrics[prefix+".nominal_calibration_gap"] = hit-(hi-lo)

    # Support levels are derived from this forecast; there are no chosen depths
    # or fitted calibration bins. A no-positive-print target has zero reach.
    has_print = target.get("has_future_print")
    reach_truth = target.get("reach_floor_cents", truth if has_print is True else None)
    if has_print is False or _finite(reach_truth):
        reach_grid = np.unique(_array(target.get("reach_levels", x), "reach_levels"))
        if not len(reach_grid) or not np.all(np.isfinite(reach_grid)):
            raise ValueError("INVALID_REACH_LEVELS")
        indices = np.searchsorted(x, reach_grid, side="right")
        probabilities = np.concatenate(([0.0], cumulative))[indices]
        outcomes = (reach_grid >= reach_truth).astype(float) if _finite(reach_truth) else np.zeros(len(reach_grid))
        gaps = outcomes-probabilities
        metrics.update({"reach.support.level_count": float(len(reach_grid)),
                        "reach.support.mean_probability": float(probabilities.mean()),
                        "reach.support.observed_rate": float(outcomes.mean()),
                        "reach.support.calibration_gap": float(gaps.mean()),
                        "reach.support.brier": float(np.mean(gaps**2))})
        for q in contract.quantiles:
            level = quantiles[_qname(q)]["level_cents"]
            probability = float(p[x <= level].sum())
            outcome = float(_finite(reach_truth) and reach_truth <= level)
            prefix = f"reach.{_qname(q)}"
            metrics.update({prefix+".probability": probability, prefix+".outcome": outcome,
                            prefix+".calibration_gap": outcome-probability,
                            prefix+".brier": (outcome-probability)**2})

    probabilities = forecast.get("family_probabilities")
    family_values = support.families if support is not None else forecast.get("families")
    if probabilities is None and family_values is not None:
        families = np.asarray(family_values, dtype=object)
        if families.ndim != 1 or len(families) != len(raw_weights):
            raise ValueError("CANDIDATE_FAMILY_LENGTH_MISMATCH")
        probabilities = defaultdict(float)
        scaled = raw_weights[active] / np.max(raw_weights[active])
        for label, weight in zip(families[active], scaled/scaled.sum()):
            if label is None:
                probabilities = None
                break
            probabilities[str(label)] += float(weight)
    actual_family = target.get("family")
    if probabilities and actual_family is not None:
        probabilities = {str(k): _probability(v) for k, v in probabilities.items()}
        if not math.isclose(sum(probabilities.values()), 1):
            raise ValueError("FAMILY_PROBABILITIES_DO_NOT_SUM_TO_ONE")
        predicted = sorted(probabilities, key=lambda k: (-probabilities[k], k))[0]
        probability = probabilities.get(str(actual_family), 0)
        metrics["family_accuracy"] = float(predicted == str(actual_family))
        metrics["family_brier"] = sum((p-float(k == str(actual_family)))**2
                                      for k, p in probabilities.items()) + float(str(actual_family) not in probabilities)
        result["family"] = dict(predicted=predicted, actual=str(actual_family),
                                log_loss=-math.log(probability) if probability > 0 else "INF")
    return result


class _Moments:
    __slots__ = ("n", "total", "minimum", "maximum")

    def __init__(self):
        self.n, self.total, self.minimum, self.maximum = 0, 0.0, None, None

    def add(self, value):
        if not _finite(value):
            raise ValueError("NONFINITE_METRIC")
        value = float(value)
        self.n += 1
        self.total += value
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)

    def finish(self):
        return dict(n=self.n, mean=self.total/self.n if self.n else None,
                    min=self.minimum, max=self.maximum)


class _Cell:
    __slots__ = ("eligible", "calls", "targets", "statuses", "metrics", "ess",
                 "candidate_availability", "family_confusion", "family_losses", "infinite_losses")

    def __init__(self):
        self.eligible = self.calls = self.targets = 0
        self.statuses, self.metrics = Counter(), defaultdict(_Moments)
        self.ess, self.candidate_availability = _Moments(), _Moments()
        self.family_confusion, self.family_losses, self.infinite_losses = Counter(), _Moments(), 0

    def add(self, row):
        self.eligible += 1
        self.calls += row["called"]
        self.targets += row["target_floor_available"]
        self.statuses[row["status"]] += 1
        self.ess.add(row["ess"])
        if row["candidate_floor_available_weight_share"] is not None:
            self.candidate_availability.add(row["candidate_floor_available_weight_share"])
        for name, value in row["metrics"].items():
            self.metrics[name].add(value)
        if "family" in row:
            family = row["family"]
            self.family_confusion[(family["actual"], family["predicted"])] += 1
            if family["log_loss"] == "INF":
                self.infinite_losses += 1
            else:
                self.family_losses.add(family["log_loss"])

    def finish(self):
        n = self.eligible
        return dict(eligible_receipts=n, called_receipts=self.calls,
                    abstained_receipts=n-self.calls, call_coverage=self.calls/n if n else None,
                    target_available_receipts=self.targets, target_missing_receipts=n-self.targets,
                    statuses=dict(sorted(self.statuses.items())), ess=self.ess.finish(),
                    candidate_floor_available_weight_share=self.candidate_availability.finish(),
                    metrics={k: v.finish() for k, v in sorted(self.metrics.items())},
                    family=dict(confusion=[dict(actual=a, predicted=p, n=v)
                                           for (a, p), v in sorted(self.family_confusion.items())],
                                n=self.family_losses.n+self.infinite_losses,
                                zero_truth_probability_calls=self.infinite_losses,
                                log_loss="INF" if self.infinite_losses else self.family_losses.finish()["mean"]))


class _Matched:
    __slots__ = ("eligible", "both_called", "n", "wins", "ties", "games", "metrics")

    def __init__(self):
        self.eligible = self.both_called = self.n = self.wins = self.ties = 0
        self.games, self.metrics = set(), defaultdict(lambda: (_Moments(), _Moments(), _Moments()))

    def add(self, event_id, variant, baseline):
        self.eligible += 1
        if not (variant["called"] and baseline["called"]):
            return
        self.both_called += 1
        a, b = variant["metrics"], baseline["metrics"]
        for name in a.keys() & b.keys():
            av, bv, delta = self.metrics[name]
            av.add(a[name])
            bv.add(b[name])
            delta.add(a[name]-b[name])
        key = "floor_absolute_error_cents"
        if key in a and key in b:
            self.n += 1
            self.games.add(event_id)
            self.wins += a[key] < b[key]
            self.ties += a[key] == b[key]

    def finish(self, contract, group, authorization_streams=None):
        n = self.n
        distinct = len(self.games)
        # Filed criterion counts queries at one side/gate. All-receipt or
        # multi-gate aggregation must not multiply a game's authorizing votes.
        scope = (group.get("side") is not None and group.get("gate") is not None
                 and n == distinct)
        if authorization_streams is not None:
            scope = scope and group.get("stream") in authorization_streams
        return dict(eligible_receipts=self.eligible, both_called_receipts=self.both_called,
                    matched_call_coverage=self.both_called/self.eligible if self.eligible else None,
                    n=n, distinct_matched_games=distinct,
                    matched_floor_coverage=n/self.eligible if self.eligible else None,
                    strictly_closer=self.wins, tied=self.ties, strictly_worse=n-self.wins-self.ties,
                    strictly_closer_share=self.wins/n if n else None,
                    criterion_met_on_matched_receipts=contract.criterion_met(n, self.wins),
                    filed_side_gate_scope=scope,
                    qualifies=contract.criterion_met(n, self.wins) if scope else None,
                    engine_authorship_enabled=False,
                    metrics={k: dict(variant=a.finish(), baseline=b.finish(), delta=d.finish())
                             for k, (a, b, d) in sorted(self.metrics.items())})


class FeaturePanelScorer:
    """Fixed variant registry and exact identity matching in one streaming pass.

    Every eligible identity is presented once, with all available variants.
    Missing variant forecasts count as abstentions. All-variant matched cells
    supplement pairwise FIRST matching so changing coverage remains visible.
    Only aggregate moments/counters and identity sets are retained.

    ``identity_mode='contiguous_event'`` bounds retained receipt identities to
    one game/stream while retaining completed keys to reject reappearing
    game/stream blocks. Default ``'all'`` accepts arbitrary event order.
    ``common_variant_metrics=False`` retains the exact
    all-variant matched count but omits its duplicate metric accumulators.
    ``metric_profile='core'`` retains primary floor/timing/CRPS/family metrics,
    all signed price quantile errors, bound band coverage/calibration and
    support plus median-level reach calibration; auxiliary quantile errors and
    band widths remain available in the default ``'full'`` profile.
    For all receipts, group by category/month/side instead of arbitrary native
    gate values. Use a separate scorer for the finite atlas side/gate groups.
    Variants may reference the same forecast object when their coefficients
    and inputs are exactly equal: each distinct object is scored once per
    target/receipt, while every variant keeps its independent accumulators.
    ``prepare_receipt`` performs only that scoring and returns an immutable,
    pickleable row. ``apply_prepared_receipt`` performs the original identity
    checks and aggregate updates, in caller-supplied receipt order. This split
    permits workers to score without changing the parent summation order.
    """
    def __init__(self, baseline_receipt, variants, baseline="FIRST", target_kinds=("carried", "reachable"),
                 groupings=(("category", "stream"), ("category", "stream", "month"),
                            ("category", "stream", "side", "gate", "role"),
                            ("category", "stream", "month", "side", "gate", "role")),
                 identity_mode="all", common_variant_metrics=True, metric_profile="full",
                 authorization_streams=None):
        self.contract = ScoreContract.from_baseline(baseline_receipt)
        self.variants, self.baseline, self.target_kinds = tuple(variants), baseline, tuple(target_kinds)
        if len(set(self.variants)) != len(self.variants) or baseline not in self.variants:
            raise ValueError("INVALID_VARIANT_REGISTRY")
        self.groupings = tuple(tuple(g) for g in groupings)
        if any("category" not in group for group in self.groupings):
            raise ValueError("CATEGORY_MUST_REMAIN_SEPARATE")
        if identity_mode not in ("all", "contiguous_event"):
            raise ValueError("INVALID_IDENTITY_MODE")
        if metric_profile not in ("full", "core"):
            raise ValueError("INVALID_METRIC_PROFILE")
        self.identity_mode = identity_mode
        self.metric_profile = metric_profile
        self.authorization_streams = None if authorization_streams is None else tuple(authorization_streams)
        self.common_variant_metrics = bool(common_variant_metrics)
        self.current_event, self.completed_events, self.seen_receipts = None, set(), 0
        self.groups, self.identities, self.excluded = {}, set(), 0
        self.conduct, self.conduct_identities = {}, set()

    def _receipt_configuration(self):
        return (self.contract, self.variants, self.baseline, self.target_kinds,
                self.groupings, self.identity_mode, self.common_variant_metrics,
                self.metric_profile, self.authorization_streams)

    def _check_receipt_identity(self, identity):
        required = ("category", "event_id", "side", "receipt_id")
        key = tuple(identity[k] for k in required) + (identity.get("stream"),)
        event_key = (identity["category"], identity["event_id"], identity.get("stream"))
        same_event = self.identity_mode == "all" or event_key == self.current_event
        if same_event and key in self.identities:
            raise ValueError("DUPLICATE_RECEIPT_IDENTITY:" + repr(key))
        if self.identity_mode == "contiguous_event" and event_key in self.completed_events:
            raise ValueError("NONCONTIGUOUS_EVENT:" + repr(event_key))
        return key, event_key

    def prepare_receipt(self, identity, targets, forecasts, *, eligible=True):
        """Score without identity/aggregate mutation, including in a worker.

        Duplicate and contiguous-event checks belong to ordered parent apply.
        Required identity fields and forecast registration are still checked
        here, even for an excluded receipt. Inputs are never retained by alias.
        """
        for field in ("category", "event_id", "side", "receipt_id"):
            identity[field]
        unknown = set(forecasts)-set(self.variants)
        if unknown:
            raise ValueError("UNREGISTERED_VARIANTS:" + repr(sorted(unknown)))
        # Score before mutation: a malformed forecast cannot leave half a row.
        scored = {}
        if eligible:
            for target in self.target_kinds:
                rows, cache = {}, {}
                for variant in self.variants:
                    forecast = forecasts.get(variant)
                    cache_key = id(forecast)
                    if cache_key not in cache:
                        row = score_distribution(forecast, targets.get(target), self.contract, target_name=target)
                        if self.metric_profile == "core":
                            row["metrics"] = {name: value for name, value in row["metrics"].items() if _core_metric(name)}
                        cache[cache_key] = _freeze_receipt_value(row)
                    rows[variant] = cache[cache_key]
                scored[target] = rows
        return PreparedReceipt(self._receipt_configuration(), _freeze_receipt_value(identity),
                               bool(eligible), _freeze_receipt_value(scored))

    def add_receipt(self, identity, targets, forecasts, *, eligible=True):
        # Keep the serial API's original validation priority: identity guards
        # precede forecast checks, and malformed scoring cannot partly add.
        self._check_receipt_identity(identity)
        self.apply_prepared_receipt(self.prepare_receipt(identity, targets, forecasts, eligible=eligible))

    def apply_prepared_receipt(self, prepared):
        """Apply one worker-scored row in original order, without rescoring."""
        if not isinstance(prepared, PreparedReceipt):
            raise ValueError("INVALID_PREPARED_RECEIPT")
        if prepared.configuration != self._receipt_configuration():
            raise ValueError("PREPARED_RECEIPT_CONFIGURATION_MISMATCH")
        if (not isinstance(prepared.identity, _FrozenMapping)
                or not isinstance(prepared.scored, _FrozenMapping)
                or tuple(prepared.scored) != (self.target_kinds if prepared.eligible else ())
                or any(not isinstance(rows, _FrozenMapping) or tuple(rows) != self.variants
                       for rows in prepared.scored.values())):
            raise ValueError("MALFORMED_PREPARED_RECEIPT")
        identity, eligible, scored = prepared.identity, prepared.eligible, prepared.scored
        key, event_key = self._check_receipt_identity(identity)
        if self.identity_mode == "contiguous_event" and event_key != self.current_event:
            if self.current_event is not None:
                self.completed_events.add(self.current_event)
            self.identities.clear()
            self.current_event = event_key
        self.identities.add(key)
        self.seen_receipts += 1
        if not eligible:
            self.excluded += 1
            return
        for fields in self.groupings:
            group = {field: identity.get(field) for field in fields}
            group_key = tuple(group.items())
            entry = self.groups.setdefault(group_key, {})
            for target, rows in scored.items():
                cells = entry.setdefault(target, dict(variants=defaultdict(_Cell), matched=defaultdict(_Matched),
                                                      common=defaultdict(_Cell), common_n=0))
                for variant, row in rows.items():
                    cells["variants"][variant].add(row)
                    if variant != self.baseline:
                        cells["matched"][variant].add(identity["event_id"], row, rows[self.baseline])
                if all(row["called"] and row["target_floor_available"] for row in rows.values()):
                    cells["common_n"] += 1
                    if self.common_variant_metrics:
                        for variant, row in rows.items():
                            cells["common"][variant].add(row)

    def add_conduct_event(self, identity, results):
        """Aggregate existing R0 results once per event; never run the engine.

        A missing result has unknown utility and is reported missing. An actual
        no-fill R0 result contributes zero capture per eligible game, consistent
        with the existing conduct scoreboards. Category/month/stream are kept.
        """
        key = (identity["category"], identity["event_id"], identity.get("stream"))
        if key in self.conduct_identities:
            raise ValueError("DUPLICATE_CONDUCT_EVENT")
        if set(results)-set(self.variants):
            raise ValueError("UNREGISTERED_CONDUCT_VARIANT")
        for variant, row in results.items():
            if row.get("rule") not in (None, "R0 CURRENT"):
                raise ValueError("ONLY_EXISTING_R0_CONDUCT_ALLOWED")
            if row.get("event_id", identity["event_id"]) != identity["event_id"]:
                raise ValueError("CONDUCT_EVENT_IDENTITY_MISMATCH")
            for name in ("completed", "one_sided", "captured_cents"):
                if not _finite(row[name]):
                    raise ValueError("INVALID_CONDUCT_METRIC:" + name)
            if row["completed"] and row["one_sided"]:
                raise ValueError("COMPLETED_AND_ONE_SIDED")
            if not row["completed"] and row["captured_cents"] != 0:
                raise ValueError("CAPTURE_REQUIRES_BOTH_SIDES")
        self.conduct_identities.add(key)
        for fields in (("category", "stream"), ("category", "stream", "month")):
            group_key = tuple((field, identity.get(field)) for field in fields)
            group = self.conduct.setdefault(group_key, dict(eligible=0, variants={}, matched={}))
            group["eligible"] += 1
            for variant in self.variants:
                stats = group["variants"].setdefault(variant, defaultdict(_Moments))
                row = results.get(variant)
                if row is None:
                    continue
                for name in ("completed", "one_sided", "captured_cents"):
                    stats[name].add(row[name])
                if row["completed"]:
                    stats["captured_cents_completed"].add(row["captured_cents"])
                base = results.get(self.baseline)
                if base is not None and variant != self.baseline:
                    matched = group["matched"].setdefault(variant, defaultdict(_Moments))
                    for name in ("completed", "one_sided", "captured_cents"):
                        matched[name+"_delta"].add(float(row[name])-float(base[name]))

    def finish(self):
        groups = []
        for key, entry in sorted(self.groups.items(), key=lambda item: repr(item[0])):
            group = dict(key)
            targets = {}
            for target, cells in sorted(entry.items()):
                targets[target] = dict(
                    all_eligible={variant: cells["variants"][variant].finish() for variant in self.variants},
                    matched_to_first={variant: cells["matched"][variant].finish(self.contract, group, self.authorization_streams)
                                      for variant in self.variants if variant != self.baseline},
                    all_variant_matched=dict(n=cells["common_n"], metrics_enabled=self.common_variant_metrics,
                        variants={variant: cells["common"][variant].finish() for variant in self.variants}
                        if self.common_variant_metrics else {}))
            groups.append(dict(group=group, targets=targets))
        conduct = []
        for key, group in sorted(self.conduct.items(), key=lambda item: repr(item[0])):
            variants = {}
            for variant, stats in group["variants"].items():
                n = stats["completed"].n
                variants[variant] = dict(eligible_events=group["eligible"], evaluated_events=n,
                    missing_events=group["eligible"]-n,
                    metrics={k: v.finish() for k, v in sorted(stats.items())})
            conduct.append(dict(group=dict(key), variants=variants,
                matched_to_first={variant: {k: v.finish() for k, v in sorted(stats.items())}
                                  for variant, stats in group["matched"].items()}))
        return dict(contract=self.contract.as_dict(), baseline=self.baseline, variants=list(self.variants),
                    target_kinds=list(self.target_kinds), seen_receipts=self.seen_receipts,
                    metric_profile=self.metric_profile,
                    excluded_receipts=self.excluded, groups=groups, r0_conduct=conduct,
                    definitions=dict(error_sign="prediction minus target; positive timing means earlier",
                        errors="own finite scored denominators; abstentions and missing targets are not zero errors",
                        matched="exact category/event/side/receipt/stream identity; per-metric finite intersection",
                        reach="strict-future truth against unchanged predictor; unique forecast support, averaged per receipt",
                        bands="inclusive equal-tail intervals bound to baseline quantiles; nominal coverage gaps include discreteness",
                        authorization="filed criterion only for one side/gate with one matched receipt per distinct game; report only",
                        conduct="event denominator; completed pairs alone receive captured cents; missing runs stay unknown",
                        training="none; same supplied forecast scored against every target"))
