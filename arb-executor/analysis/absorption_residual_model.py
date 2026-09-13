"""Direct residual model specified by absorption_residual_v1/CONTRACT.json.

Pure array operations. No source loading, engine, order or population launcher.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import math
import numpy as np

from feature_panel_scoring import weighted_quantile, weighted_crps


def game_weights(events):
    events = np.asarray(events)
    _, inverse, counts = np.unique(events, return_inverse=True, return_counts=True)
    weights = 1.0 / counts[inverse]
    return weights / weights.sum()


@dataclass
class RankDesign:
    names: tuple
    quantiles: tuple
    sorted_values: tuple
    active: tuple
    baseline_hinges: tuple

    @classmethod
    def fit(cls, x, names, quantiles):
        x = np.asarray(x, dtype=float)
        observed = tuple(np.sort(column[np.isfinite(column)]) for column in x.T)
        active = tuple(i for i, values in enumerate(observed) if len(values))
        return cls(tuple(names), tuple(quantiles), observed, active,
                   tuple(i for i in active if names[i] in ('first_own', 'first_partner', 'log_mtb')))

    def transform(self, x):
        x = np.asarray(x, dtype=float)
        if x.shape[1] != len(self.names):
            raise ValueError('DESIGN_FIELD_MISMATCH')
        columns = []
        for i in self.active:
            value, observed = x[:, i], self.sorted_values[i]
            missing = ~np.isfinite(value)
            if self.names[i].startswith('role:'):
                rank = value.copy()
            else:
                rank = (np.searchsorted(observed, value, side='left') +
                        np.searchsorted(observed, value, side='right'))/(2*len(observed))
            # Model-matrix rank median only; source values never overwritten.
            observed_ranks = (np.searchsorted(observed, observed, side='left') +
                              np.searchsorted(observed, observed, side='right'))/(2*len(observed))
            rank[missing] = float(np.median(observed_ranks))
            columns.extend((rank, missing.astype(float)))
            if i in self.baseline_hinges:
                for probability in self.quantiles:
                    knot = weighted_quantile(observed_ranks, np.ones(len(observed_ranks)), probability)
                    columns.append(np.maximum(0, rank-knot))
        return np.column_stack(columns) if columns else np.empty((len(x), 0))


@dataclass
class RidgeFamily:
    design: RankDesign
    xmean: np.ndarray
    ymean: float
    eigenvalues: np.ndarray
    vectors: np.ndarray
    projection: np.ndarray
    training_x: np.ndarray
    training_y: np.ndarray
    weights: np.ndarray
    strengths: dict
    coefficient_cache: dict = field(default_factory=dict)

    @classmethod
    def fit(cls, x, residual, events, names, quantiles):
        y = np.asarray(residual, dtype=float)
        if not len(y) or not np.isfinite(y).all():
            raise ValueError('FINITE_NONEMPTY_TRAINING_REQUIRED')
        design = RankDesign.fit(x, names, quantiles)
        z, w = design.transform(x), game_weights(events)
        xmean, ymean = w @ z, float(w @ y)
        centered = z-xmean
        gram = centered.T @ (w[:, None]*centered)
        values, vectors = np.linalg.eigh(gram)
        tolerance = np.finfo(float).eps * max(gram.shape, default=1) * max(float(values.max(initial=0)), 1)
        values = np.where(values > tolerance, values, 0)
        projection = vectors.T @ (centered.T @ (w*(y-ymean)))
        positive = values[values > 0]
        strengths = {'OLS': 0.0}
        for q in quantiles:
            strengths['EIGEN_Q'+str(q)] = weighted_quantile(positive, np.ones(len(positive)), q) if len(positive) else 0.0
        fitted = cls(design, xmean, ymean, values, vectors, projection, z, y, w, strengths)
        # Identical operations, once per strength: do not retain every fold's
        # dense training design after its median recenter has been computed.
        for choice in strengths:
            fitted.coefficient_cache[choice] = fitted.coefficients(choice)
        fitted.training_x = None
        return fitted

    def coefficients(self, choice):
        if choice in self.coefficient_cache:
            return self.coefficient_cache[choice]
        strength = self.strengths[choice]
        divisor = self.eigenvalues+strength
        scaled = np.divide(self.projection, divisor, out=np.zeros_like(divisor), where=divisor > 0)
        beta = self.vectors @ scaled
        initial = self.ymean+(self.training_x-self.xmean) @ beta
        recenter = weighted_quantile(self.training_y-initial, self.weights, .5)
        return beta, self.ymean+recenter-float(self.xmean @ beta)

    def predict(self, x, choice):
        if choice == 'ZERO':
            return np.zeros(len(x))
        beta, intercept = self.coefficients(choice)
        return self.design.transform(x) @ beta+intercept

    def receipt(self, choice):
        if choice == 'ZERO':
            return dict(choice=choice, correction=0)
        beta, intercept = self.coefficients(choice)
        return dict(choice=choice, ridge_strength=self.strengths[choice], intercept=intercept,
                    coefficients=beta.tolist(), active_fields=[self.design.names[i] for i in self.design.active],
                    training_rows=len(self.training_y), design_columns=len(beta),
                    objective='equal-game ridge squared residual, then training weighted-median intercept recenter',
                    status='EIGEN_SOLVE_COMPLETE')


def translated_scores(row, correction):
    values, weights = np.asarray(row['values'], dtype=float), np.asarray(row['weights'], dtype=float)
    target = row['target']
    q = float(row['q'])+float(correction)
    return dict(q=q, signed=q-target, mae=abs(q-target),
                crps=weighted_crps(values+correction, weights, target))


def paired_game_losses(rows, variant, control, metric):
    grouped = {}
    for row in rows:
        if row.get('target') is None or variant not in row['scores'] or control not in row['scores']:
            continue
        key = (row['event'], row['date'])
        a, b = row['scores'][variant][metric], row['scores'][control][metric]
        grouped.setdefault(key, []).append((a, b))
    return [dict(event=e, date=d, variant=math.fsum(a for a,b in values)/len(values),
                 control=math.fsum(b for a,b in values)/len(values))
            for (e,d), values in sorted(grouped.items())]


def clustered_interval(games, *, seed_material, draws, comparisons, confidence=.95):
    """Two-stage resampling of dates then games; no receipt pseudoreplication."""
    if not games:
        return dict(n_games=0, n_dates=0, delta=None, interval=None)
    dates = {}
    for game in games:
        dates.setdefault(game['date'], []).append(game['variant']-game['control'])
    delta = math.fsum(g['variant']-g['control'] for g in games)/len(games)
    if len(dates) < 2:
        return dict(n_games=len(games), n_dates=len(dates), delta=delta, interval=None,
                    reason='FEWER_THAN_TWO_DATE_CLUSTERS')
    seed = int.from_bytes(hashlib.sha256(seed_material.encode()).digest(), 'big')
    rng = np.random.default_rng(seed)
    clusters = [np.asarray(v) for _, v in sorted(dates.items())]
    # Generate one within-date game bootstrap per replicate/date. A repeated
    # date in the outer draw gets independent within-date replicates below.
    totals, denominators = np.zeros(draws), np.zeros(draws)
    for position in range(len(clusters)):
        chosen = rng.integers(0, len(clusters), size=draws)
        for index, values in enumerate(clusters):
            selected = np.flatnonzero(chosen == index)
            if not len(selected):
                continue
            sampled = rng.integers(0, len(values), size=(len(selected), len(values)))
            totals[selected] += values[sampled].sum(axis=1)
            denominators[selected] += len(values)
    distribution = np.sort(totals/denominators)
    tail = (1-confidence)/(2*comparisons)
    lo, hi = np.quantile(distribution, [tail, 1-tail])
    return dict(n_games=len(games), n_dates=len(dates), delta=delta, interval=[float(lo), float(hi)],
                confidence=confidence, comparisons=comparisons, method='date then game hierarchical percentile bootstrap',
                draws=draws, seed_sha256=hashlib.sha256(seed_material.encode()).hexdigest())


def promotion_bar(mae, crps, *, minimum_games, minimum_effect, coverage_preserved, unsafe):
    checks = dict(enough_games=mae['n_games'] >= minimum_games,
                  useful_effect=mae['delta'] is not None and mae['delta'] <= -minimum_effect,
                  adjusted_interval=mae['interval'] is not None and mae['interval'][1] < 0,
                  crps_nonincreasing=crps['delta'] is not None and crps['delta'] <= 0,
                  coverage_preserved=bool(coverage_preserved), safe=not unsafe)
    return dict(pass_bar=all(checks.values()), checks=checks)
