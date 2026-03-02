#!/usr/bin/env python3
"""
Monte Carlo Arb Strategy Simulator
====================================
Simulates 10,000 sessions x 100 trades across 5 execution strategies,
2 spread minimums, and 5 variant modifiers using observed live trade data.

Usage:  python monte_carlo_sim.py
"""

import numpy as np
from dataclasses import dataclass, field
from copy import deepcopy
from typing import Callable, List, Tuple

# ============================================================================
# OBSERVED PARAMETERS (from live K↔PM arb trading)
# ============================================================================

@dataclass
class Params:
    """All tunable simulation parameters in one place."""
    # Fill rates
    k_fill_rate: float = 0.50
    pm_fill_rate: float = 0.50       # conditional on K filling (Strategy A)
    k_fill_rate_after_pm: float = 0.90  # K fill rate when PM goes first (Strategy B)
    k_same_exchange_fill: float = 0.95  # same-exchange Kalshi (Strategy D)

    # Spreads
    spread_min: int = 4              # minimum spread to trade (cents)
    spread_max: int = 6              # max observed spread
    spread_mean: float = 3.0         # for regime model

    # Costs
    unwind_cost_min: int = 4         # cents, before smart unwind
    unwind_cost_max: int = 13

    # Settlement (for HOLD_TO_SETTLE)
    settle_win_prob: float = 0.50    # 50/50 settlement outcome

    # Price movement during execution
    price_move_max: int = 5          # 0-5c uniform

    # Sizing
    contracts: int = 1

    # Same-exchange opportunity rate (for Strategy D/E)
    same_exchange_rate: float = 0.05  # 5% of opportunities are same-exchange

    # Capital velocity
    quick_exit_cost: int = 2         # market ±2c for quick exit

    # Daily loss cap (cents)
    loss_cap: int = 2000             # $20 = 2000c


# ============================================================================
# STRATEGY SIMULATORS
# Each returns cents P&L for a single trade.
# ============================================================================

def strategy_A_k_first(rng: np.random.Generator, p: Params) -> float:
    """
    A  -- K-FIRST (current strategy):
    K fires first. If K fills, fire PM. PM no-fill → HOLD_TO_SETTLE.
    """
    spread = rng.integers(p.spread_min, p.spread_max + 1)
    entry_price = rng.integers(20, 81)  # K entry price 20-80c

    # Step 1: K order
    if rng.random() > p.k_fill_rate:
        return 0.0  # K didn't fill  -- no trade

    # Step 2: PM order (K filled)
    if rng.random() < p.pm_fill_rate:
        return spread * p.contracts  # Both filled  -- arb profit

    # PM didn't fill  -- HOLD_TO_SETTLE
    if rng.random() < p.settle_win_prob:
        return (100 - entry_price) * p.contracts  # Win settlement
    else:
        return -entry_price * p.contracts  # Lose settlement


def strategy_B_pm_first(rng: np.random.Generator, p: Params) -> float:
    """
    B  -- PM-FIRST:
    PM fires first. No fill = clean abort. PM fills → K at 90%.
    K no-fill → smart unwind PM, cost capped at spread.
    """
    spread = rng.integers(p.spread_min, p.spread_max + 1)

    # Step 1: PM order
    if rng.random() > p.pm_fill_rate:
        return 0.0  # PM didn't fill  -- clean abort

    # Step 2: K order (PM filled)
    if rng.random() < p.k_fill_rate_after_pm:
        return spread * p.contracts  # Both filled  -- arb profit

    # K didn't fill  -- smart unwind PM, cost capped at spread
    unwind = rng.integers(0, spread + 1)  # smart unwind: 0 to spread
    return -unwind * p.contracts


def strategy_C_parallel(rng: np.random.Generator, p: Params) -> float:
    """
    C  -- PARALLEL:
    Fire both simultaneously. Unwind filled leg if other fails.
    """
    spread = rng.integers(p.spread_min, p.spread_max + 1)

    k_filled = rng.random() < p.k_fill_rate
    pm_filled = rng.random() < p.pm_fill_rate

    if k_filled and pm_filled:
        return spread * p.contracts  # Both filled

    if not k_filled and not pm_filled:
        return 0.0  # Neither filled

    # One filled, one didn't  -- unwind the filled leg
    raw_unwind = rng.integers(p.unwind_cost_min, p.unwind_cost_max + 1)
    unwind = min(raw_unwind, spread)  # capped at spread
    return -unwind * p.contracts


def strategy_D_same_exchange(rng: np.random.Generator, p: Params) -> float:
    """
    D  -- SAME-EXCHANGE KALSHI:
    Both legs on K. 30ms, 95% fill. Scarcer opportunities.
    Returns P&L only for this one opportunity (caller handles frequency).
    """
    spread = rng.integers(p.spread_min, p.spread_max + 1)

    leg1_filled = rng.random() < p.k_same_exchange_fill
    leg2_filled = rng.random() < p.k_same_exchange_fill

    if leg1_filled and leg2_filled:
        return spread * p.contracts

    if not leg1_filled and not leg2_filled:
        return 0.0

    # One leg filled  -- unwind on same exchange (fast, cheap: 0-2c)
    unwind = rng.integers(0, 3)
    return -unwind * p.contracts


def strategy_E_hybrid(rng: np.random.Generator, p: Params) -> float:
    """
    E  -- HYBRID: Strategy D when available, Strategy B fallback.
    """
    if rng.random() < p.same_exchange_rate:
        return strategy_D_same_exchange(rng, p)
    else:
        return strategy_B_pm_first(rng, p)


# ============================================================================
# SESSION RUNNER
# ============================================================================

def run_session(
    strategy_fn: Callable,
    rng: np.random.Generator,
    p: Params,
    n_trades: int = 100,
    loss_cap: int = 0,
) -> np.ndarray:
    """Run one session of n_trades. Returns array of per-trade P&L (cents)."""
    pnl = np.zeros(n_trades)
    cumulative = 0.0

    for i in range(n_trades):
        if loss_cap > 0 and cumulative < -loss_cap:
            break  # Hit daily loss cap  -- stop trading
        trade_pnl = strategy_fn(rng, p)
        pnl[i] = trade_pnl
        cumulative += trade_pnl

    return pnl


# ============================================================================
# STATISTICS
# ============================================================================

@dataclass
class SessionStats:
    label: str = ""
    ev_per_trade: float = 0.0
    sharpe: float = 0.0
    win_pct: float = 0.0
    max_drawdown: float = 0.0
    loss_session_pct: float = 0.0
    median_pnl: float = 0.0
    pct_5: float = 0.0
    pct_95: float = 0.0
    mean_session_pnl: float = 0.0
    trades_per_session: float = 0.0


def compute_stats(
    label: str,
    all_sessions: np.ndarray,  # shape (n_sessions, n_trades)
) -> SessionStats:
    """Compute summary statistics across all sessions."""
    s = SessionStats(label=label)

    # Per-session totals
    session_totals = all_sessions.sum(axis=1)
    # Flatten all trades
    all_trades = all_sessions.flatten()
    # Only count non-zero trades (actual fills)
    active_trades = all_trades[all_trades != 0]

    if len(active_trades) == 0:
        s.ev_per_trade = 0.0
        s.sharpe = 0.0
        s.win_pct = 0.0
        s.trades_per_session = 0.0
    else:
        s.ev_per_trade = float(np.mean(active_trades))
        std = float(np.std(active_trades))
        s.sharpe = s.ev_per_trade / std if std > 0 else 0.0
        s.win_pct = float(np.mean(active_trades > 0) * 100)
        s.trades_per_session = len(active_trades) / len(session_totals)

    # Session-level stats
    s.mean_session_pnl = float(np.mean(session_totals))
    s.median_pnl = float(np.median(session_totals))
    s.pct_5 = float(np.percentile(session_totals, 5))
    s.pct_95 = float(np.percentile(session_totals, 95))
    s.loss_session_pct = float(np.mean(session_totals < 0) * 100)

    # Max drawdown (worst peak-to-trough across all sessions)
    drawdowns = []
    for sess in all_sessions:
        cumsum = np.cumsum(sess)
        peak = np.maximum.accumulate(cumsum)
        dd = peak - cumsum
        drawdowns.append(float(np.max(dd)) if len(dd) > 0 else 0.0)
    s.max_drawdown = float(np.mean(drawdowns))  # average max DD

    return s


# ============================================================================
# VARIANT PARAM MODIFIERS
# ============================================================================

def variant_base(p: Params) -> Params:
    """No modification  -- baseline."""
    return deepcopy(p)

def variant_fill_gate(p: Params) -> Params:
    """Fill probability gate: PM fill rate 50% → 70%."""
    p2 = deepcopy(p)
    p2.pm_fill_rate = 0.70
    return p2

def variant_kelly(p: Params) -> Params:
    """Quarter-Kelly sizing: 5 contracts instead of 1."""
    p2 = deepcopy(p)
    p2.contracts = 5
    return p2

def variant_regime(p: Params) -> Params:
    """Regime detection marker  -- handled in special session runner."""
    return deepcopy(p)

def variant_loss_cap(p: Params) -> Params:
    """Daily loss cap $20 = 2000c  -- handled by session runner."""
    return deepcopy(p)

def variant_velocity(p: Params) -> Params:
    """Capital velocity  -- handled in special strategy wrapper."""
    return deepcopy(p)


# ============================================================================
# REGIME-AWARE SESSION RUNNER
# ============================================================================

def run_session_regime(
    strategy_fn: Callable,
    rng: np.random.Generator,
    base_p: Params,
    n_trades: int = 100,
) -> np.ndarray:
    """
    70% stable regime (spread~3c padded to spread_min, 65% fill)
    30% volatile regime (spread~5c, 40% fill)
    """
    pnl = np.zeros(n_trades)
    for i in range(n_trades):
        p = deepcopy(base_p)
        if rng.random() < 0.70:
            # Stable regime
            p.spread_min = max(base_p.spread_min, 3)
            p.spread_max = max(base_p.spread_min, 4)
            p.k_fill_rate = 0.65
            p.pm_fill_rate = 0.65
        else:
            # Volatile regime
            p.spread_min = max(base_p.spread_min, 5)
            p.spread_max = max(base_p.spread_min + 2, 7)
            p.k_fill_rate = 0.40
            p.pm_fill_rate = 0.40
        pnl[i] = strategy_fn(rng, p)
    return pnl


# ============================================================================
# VELOCITY-AWARE STRATEGY WRAPPERS
# ============================================================================

def make_velocity_strategy(base_fn: Callable) -> Callable:
    """
    Capital velocity: quick exits instead of hold-to-settle.
    Wraps Strategy A to replace HOLD_TO_SETTLE with quick exit at ±2c.
    Only affects Strategy A (the one with settlement exposure).
    """
    def wrapper(rng: np.random.Generator, p: Params) -> float:
        spread = rng.integers(p.spread_min, p.spread_max + 1)
        entry_price = rng.integers(20, 81)

        if rng.random() > p.k_fill_rate:
            return 0.0

        if rng.random() < p.pm_fill_rate:
            return spread * p.contracts

        # Quick exit instead of hold-to-settle: sell at market ±2c
        price_move = rng.integers(-p.quick_exit_cost, p.quick_exit_cost + 1)
        exit_pnl = price_move * p.contracts  # small loss/gain from market exit
        return exit_pnl

    return wrapper


# ============================================================================
# MAIN SIMULATION
# ============================================================================

N_SESSIONS = 10_000
N_TRADES = 100

STRATEGIES = {
    'A K-FIRST':       strategy_A_k_first,
    'B PM-FIRST':      strategy_B_pm_first,
    'C PARALLEL':      strategy_C_parallel,
    'D SAME-EXCH':     strategy_D_same_exchange,
    'E HYBRID':        strategy_E_hybrid,
}

SPREAD_MINS = [4, 6]

# Strategy D frequency variants
D_RATES = {1: 0.01, 5: 0.05, 10: 0.10}


def run_core_simulations(rng: np.random.Generator) -> List[SessionStats]:
    """Run all 5 strategies x 2 spread minimums."""
    results = []

    for spread_min in SPREAD_MINS:
        for name, fn in STRATEGIES.items():
            p = Params(spread_min=spread_min, spread_max=spread_min + 2)

            # Strategy D: run at 3 opportunity rates
            if name == 'D SAME-EXCH':
                for rate_pct, rate in D_RATES.items():
                    p_d = deepcopy(p)
                    all_sessions = np.zeros((N_SESSIONS, N_TRADES))
                    for s in range(N_SESSIONS):
                        for t in range(N_TRADES):
                            if rng.random() < rate:
                                all_sessions[s, t] = strategy_D_same_exchange(rng, p_d)
                            # else: 0 (no opportunity)
                    label = f"D SAME({rate_pct}%) s{spread_min}"
                    results.append(compute_stats(label, all_sessions))
                continue

            # Strategy E: run at 3 same-exchange rates
            if name == 'E HYBRID':
                for rate_pct, rate in D_RATES.items():
                    p_e = deepcopy(p)
                    p_e.same_exchange_rate = rate
                    all_sessions = np.zeros((N_SESSIONS, N_TRADES))
                    for s in range(N_SESSIONS):
                        all_sessions[s] = run_session(fn, rng, p_e, N_TRADES)
                    label = f"E HYBRID({rate_pct}%) s{spread_min}"
                    results.append(compute_stats(label, all_sessions))
                continue

            # Strategies A, B, C
            all_sessions = np.zeros((N_SESSIONS, N_TRADES))
            for s in range(N_SESSIONS):
                all_sessions[s] = run_session(fn, rng, p, N_TRADES)
            label = f"{name} s{spread_min}"
            results.append(compute_stats(label, all_sessions))

    return results


def run_variant_simulations(rng: np.random.Generator) -> List[SessionStats]:
    """Run variant modifiers across key strategies."""
    results = []

    # Test variants on A, B, E (the main contenders)
    test_strategies = {
        'A K-FIRST': strategy_A_k_first,
        'B PM-FIRST': strategy_B_pm_first,
        'E HYBRID': strategy_E_hybrid,
    }

    spread_min = 4  # Test variants at spread_min=4
    base_p = Params(spread_min=spread_min, spread_max=spread_min + 2)

    for sname, sfn in test_strategies.items():

        # --- Variant 1: Fill probability gate ---
        p = variant_fill_gate(base_p)
        all_sessions = np.zeros((N_SESSIONS, N_TRADES))
        for s in range(N_SESSIONS):
            all_sessions[s] = run_session(sfn, rng, p, N_TRADES)
        results.append(compute_stats(f"{sname} +FillGate", all_sessions))

        # --- Variant 2: Quarter-Kelly (5 contracts) ---
        p = variant_kelly(base_p)
        all_sessions = np.zeros((N_SESSIONS, N_TRADES))
        for s in range(N_SESSIONS):
            all_sessions[s] = run_session(sfn, rng, p, N_TRADES)
        results.append(compute_stats(f"{sname} +Kelly5x", all_sessions))

        # --- Variant 3: Regime detection ---
        all_sessions = np.zeros((N_SESSIONS, N_TRADES))
        for s in range(N_SESSIONS):
            all_sessions[s] = run_session_regime(sfn, rng, base_p, N_TRADES)
        results.append(compute_stats(f"{sname} +Regime", all_sessions))

        # --- Variant 4: Daily loss cap $20 ---
        p = deepcopy(base_p)
        all_sessions = np.zeros((N_SESSIONS, N_TRADES))
        for s in range(N_SESSIONS):
            all_sessions[s] = run_session(sfn, rng, p, N_TRADES, loss_cap=2000)
        results.append(compute_stats(f"{sname} +LossCap", all_sessions))

        # --- Variant 5: Capital velocity (quick exit) ---
        if sname == 'A K-FIRST':
            vel_fn = make_velocity_strategy(sfn)
            p = deepcopy(base_p)
            all_sessions = np.zeros((N_SESSIONS, N_TRADES))
            for s in range(N_SESSIONS):
                all_sessions[s] = run_session(vel_fn, rng, p, N_TRADES)
            results.append(compute_stats(f"{sname} +QuickExit", all_sessions))
        else:
            # B and E don't hold to settle  -- velocity = same as base
            results.append(compute_stats(f"{sname} +QuickExit", all_sessions))

    return results


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def print_table(title: str, results: List[SessionStats]):
    """Print formatted comparison table."""
    print(f"\n{'='*120}")
    print(f"  {title}")
    print(f"{'='*120}")

    header = (
        f"{'Strategy':<25} {'EV/trade':>9} {'Sharpe':>7} {'Win%':>6} "
        f"{'AvgMaxDD':>9} {'P(loss)':>8} {'MedSess':>9} {'5th%':>9} {'95th%':>9} "
        f"{'Trades':>7} {'SessPnL':>9}"
    )
    print(header)
    print('-' * 120)

    for r in results:
        row = (
            f"{r.label:<25} "
            f"{r.ev_per_trade:>+8.1f}c "
            f"{r.sharpe:>7.3f} "
            f"{r.win_pct:>5.1f}% "
            f"{r.max_drawdown:>8.0f}c "
            f"{r.loss_session_pct:>6.1f}% "
            f"{r.median_pnl:>+8.0f}c "
            f"{r.pct_5:>+8.0f}c "
            f"{r.pct_95:>+8.0f}c "
            f"{r.trades_per_session:>6.1f} "
            f"{r.mean_session_pnl:>+8.0f}c"
        )
        print(row)


def print_recommendation(core: List[SessionStats], variants: List[SessionStats]):
    """Print final recommendation based on risk-adjusted return."""
    print(f"\n{'='*120}")
    print("  RECOMMENDATION  -- Ranked by Sharpe (risk-adjusted return)")
    print(f"{'='*120}\n")

    # Combine and sort by Sharpe
    all_results = core + variants
    # Filter out zero-trade strategies
    active = [r for r in all_results if r.trades_per_session > 0]
    ranked = sorted(active, key=lambda r: r.sharpe, reverse=True)

    for i, r in enumerate(ranked[:15], 1):
        flag = ""
        if r.loss_session_pct < 10:
            flag = " [LOW RISK]"
        elif r.loss_session_pct > 50:
            flag = " [HIGH RISK]"
        ev_dollar = r.mean_session_pnl / 100
        print(
            f"  #{i:>2}  {r.label:<25}  "
            f"Sharpe={r.sharpe:>+.3f}  "
            f"EV={r.ev_per_trade:>+.1f}c/trade  "
            f"Session=${ev_dollar:>+.2f}  "
            f"P(loss)={r.loss_session_pct:.0f}%"
            f"{flag}"
        )

    print()

    # Key insights
    print("  KEY INSIGHTS:")
    print("  " + "-" * 60)

    # Best Sharpe
    best = ranked[0]
    print(f"  - Best risk-adjusted: {best.label} (Sharpe {best.sharpe:+.3f})")

    # Best absolute EV
    best_ev = max(active, key=lambda r: r.ev_per_trade)
    print(f"  - Highest EV/trade: {best_ev.label} ({best_ev.ev_per_trade:+.1f}c)")

    # Lowest loss probability
    safest = min(active, key=lambda r: r.loss_session_pct)
    print(f"  - Safest: {safest.label} (P(loss)={safest.loss_session_pct:.0f}%)")

    # Strategy A vs B head-to-head
    a_base = next((r for r in core if r.label.startswith('A') and 's4' in r.label), None)
    b_base = next((r for r in core if r.label.startswith('B') and 's4' in r.label), None)
    if a_base and b_base:
        print(f"\n  HEAD-TO-HEAD (spread_min=4):")
        print(f"  - A K-FIRST:  EV={a_base.ev_per_trade:+.1f}c  Sharpe={a_base.sharpe:+.3f}  P(loss)={a_base.loss_session_pct:.0f}%")
        print(f"  - B PM-FIRST: EV={b_base.ev_per_trade:+.1f}c  Sharpe={b_base.sharpe:+.3f}  P(loss)={b_base.loss_session_pct:.0f}%")
        winner = "A K-FIRST" if a_base.sharpe > b_base.sharpe else "B PM-FIRST"
        print(f"  >> Winner: {winner}")

    print()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 120)
    print("  MONTE CARLO ARB STRATEGY SIMULATOR")
    print("  10,000 sessions x 100 trades per session")
    print("=" * 120)
    print()
    print("  Observed parameters:")
    print("    K fill: 50% | PM fill: 50% | K-after-PM: 90% | Same-exch: 95%")
    print("    K latency: 30ms | PM latency: 150-250ms")
    print("    Unwind: 4-13c raw | Arb profit: 2-4c net | Price move: 0-5c")
    print("    Settlement: 50/50 win/loss")
    print()

    rng = np.random.default_rng(seed=42)  # Deterministic

    print("Running core simulations (5 strategies x 2 spreads)...")
    core = run_core_simulations(rng)
    print_table("CORE STRATEGIES (baseline parameters)", core)

    print("\nRunning variant simulations...")
    variants = run_variant_simulations(rng)
    print_table("VARIANT MODIFIERS (spread_min=4, strategies A/B/E)", variants)

    print_recommendation(core, variants)


if __name__ == '__main__':
    main()
