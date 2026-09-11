"""Numerical-only refinement of stalled feature fits; unchanged CRPS/KKT rule.

The live full-cadence run keeps importing feature_panel_model unchanged. The
atlas adapter opts into this module in its own process. No scientific cutoff,
feature, likelihood, validation cohort or objective is changed here.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import math
import numpy as np
import feature_panel_model as model

LEGACY_FIT = model.fit_joint_model


def prepared_objective(samples, names):
    ordered = []
    for sample in samples:
        sample = sample if isinstance(sample, model.PoolSample) else model.PoolSample.from_mapping(sample)
        order = np.argsort(sample.candidate_levels, kind="stable")
        ordered.append(model.PoolSample(sample.candidate_levels[order], sample.base_weights[order],
            sample.block_log_k[order], sample.actual, sample.gameid))
    counts = Counter(s.gameid for s in ordered)
    mass = np.asarray([1 / (len(counts) * counts[s.gameid]) for s in ordered])

    def objective(beta):
        values, gradients = [], []
        for sample in ordered:
            w = model.joint_weights(sample.base_weights, sample.block_log_k, beta)
            value, gradient = model._sorted_crps_and_gradient(sample.candidate_levels,
                w / w.sum(), sample.block_log_k, sample.actual)
            values.append(value)
            gradients.append(gradient)
        return float(np.dot(mass, values)), mass @ np.asarray(gradients)
    return objective


def projected_gradient(beta, gradient):
    return np.where((beta > 0) | (gradient < 0), gradient, 0)


def polish(objective, initial, options):
    """Bounded Newton polishing; central differences of the analytic gradient.

    Difference step is machine-epsilon^(1/3), scaled by coefficient magnitude:
    a numerical precision choice, not a learned weight or acceptance threshold.
    Positive-definite free Hessians give Newton directions; otherwise use the
    existing projected-gradient direction. The original Armijo test and
    projected-gradient tolerance remain the sole convergence requirements.
    """
    beta = np.asarray(initial, dtype=float).copy()
    evaluations = 0

    def evaluate(x):
        nonlocal evaluations
        evaluations += 1
        return objective(x)

    score, gradient = evaluate(beta)
    history = []
    status = "REFINEMENT_MAXIMUM_ITERATIONS"
    for iteration in range(options.maximum_iterations):
        pg = projected_gradient(beta, gradient)
        norm = float(np.max(np.abs(pg)))
        history.append(dict(iteration=iteration, crps=score, projected_gradient_max=norm,
                            beta=beta.tolist()))
        if norm <= options.gradient_tolerance:
            status = "PROJECTED_GRADIENT_CONVERGED"
            break
        free = np.flatnonzero((beta > 0) | (gradient < 0))
        hessian = np.empty((len(free), len(free)))
        for column, index in enumerate(free):
            h = np.cbrt(np.finfo(float).eps) * max(1., abs(beta[index]))
            upper = beta.copy()
            upper[index] += h
            _, gu = evaluate(upper)
            if beta[index] >= h:
                lower = beta.copy()
                lower[index] -= h
                _, gl = evaluate(lower)
                derivative = (gu - gl) / (h + h)
            else:
                derivative = (gu - gradient) / h
            hessian[:, column] = derivative[free]
        hessian = (hessian + hessian.T) / (1 + 1)
        direction = -pg
        if np.all(np.isfinite(hessian)):
            try:
                np.linalg.cholesky(hessian)
                direction = np.zeros_like(beta)
                direction[free] = np.linalg.solve(hessian, -gradient[free])
            except np.linalg.LinAlgError:
                pass
        accepted = False
        step = options.initial_step
        for _ in range(options.maximum_backtracks):
            candidate = np.maximum(0, beta + step * direction)
            delta = candidate - beta
            descent = float(np.dot(gradient, delta))
            if np.any(delta) and descent < 0:
                proposed, next_gradient = evaluate(candidate)
                if (math.isfinite(proposed)
                        and proposed <= score + options.armijo_fraction * descent):
                    beta, score, gradient = candidate, proposed, next_gradient
                    accepted = True
                    break
            step *= options.backtrack_fraction
        if not accepted:
            status = "REFINEMENT_LINE_SEARCH_STALLED"
            break
        # Small objective improvement is NOT a convergence or stopping test.
    pg = projected_gradient(beta, gradient)
    if float(np.max(np.abs(pg))) <= options.gradient_tolerance:
        status = "PROJECTED_GRADIENT_CONVERGED"
    return beta, dict(status=status, fitted_crps=score, evaluations=evaluations,
        projected_gradient_max=float(np.max(np.abs(pg))), history=history,
        numerical_controls=asdict(options),
        optimizer="bounded finite-difference Newton polish of analytic CRPS gradient; original Armijo/KKT tolerance",
        finite_difference_step="cbrt(float64 epsilon) * max(1, abs(coefficient))",
        no_objective_stall_early_exit=True, global_optimum_claimed=False)


def fit_joint_model(samples, block_names, *, options=None):
    options = options or model.NumericalOptions()
    samples = list(samples)
    result = LEGACY_FIT(samples, block_names, options=options)
    prior = result.report
    if prior['status'] in ('PROJECTED_GRADIENT_CONVERGED', 'UNTRAINED_FIRST_CONTROL'):
        result.report = dict(prior, optimizer_outcome=("CONVERGED" if samples else "NO_TRAINING"),
                             refinement_attempted=False)
        return result
    objective = prepared_objective(samples, tuple(block_names))
    beta, refined = polish(objective, result.beta, options)
    result.beta = beta
    result.report = dict(prior, **{k: v for k, v in refined.items() if k not in ('history',)},
        beta=dict(zip(block_names, map(float, beta))), refinement_attempted=True,
        legacy_attempt=prior, refinement_history=refined['history'],
        optimizer_outcome=("CONVERGED" if refined['status']=='PROJECTED_GRADIENT_CONVERGED' else "STALLED"))
    return result
