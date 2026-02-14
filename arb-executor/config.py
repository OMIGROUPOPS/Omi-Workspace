"""
Shared Configuration for Arbitrage Executors

This module provides a single source of truth for configuration values
that are shared between arb_executor_v7.py and arb_executor_ws.py.

IMPORTANT: Both executors should import Config and use its values.
Never use module-level globals in v7 for values that affect execution behavior.
"""

from enum import Enum


class ExecutionMode(Enum):
    """Execution mode enum."""
    PAPER = "paper"
    LIVE = "live"


class Config:
    """
    Shared configuration - single source of truth for both executors.

    All execution-controlling values should be here, not as module-level
    globals in individual executor files.

    Usage:
        from config import Config, ExecutionMode

        # At startup:
        Config.set_live()
        Config.min_contracts = 1

        # In functions:
        if Config.is_live():
            send_real_order()
    """

    # ==========================================================================
    # EXECUTION MODE
    # ==========================================================================
    execution_mode: ExecutionMode = ExecutionMode.PAPER
    paper_no_limits: bool = True  # In paper mode, skip contract/cost limits
    dry_run_mode: bool = False    # Show what would happen but don't submit

    # ==========================================================================
    # CONTRACT SIZING
    # ==========================================================================
    min_contracts: int = 1        # Minimum contracts per order
    max_contracts: int = 20       # Maximum contracts per trade
    max_cost_cents: int = 1500    # Maximum cost per trade ($15)
    min_liquidity: int = 50       # Minimum bid/ask depth required

    # ==========================================================================
    # SPREAD THRESHOLDS
    # ==========================================================================
    spread_min_cents: int = 4     # Minimum spread to execute
    spread_log_min_cents: int = 2  # Minimum spread to log/watch (for data collection)
    min_hedge_spread_cents: int = 4  # Minimum spread to proceed with trade

    # ==========================================================================
    # FEES & PROFIT CALCULATIONS
    # ==========================================================================
    kalshi_fee_cents: int = 2           # Kalshi taker fee per contract
    pm_us_fee_rate: float = 0.001       # PM US fee rate (0.10%)
    expected_slippage_cents: int = 1    # Expected slippage per side
    min_profit_cents: int = 0           # Let PM buffer handle profitability

    # ==========================================================================
    # PRICE BUFFERS
    # ==========================================================================
    price_buffer_cents: int = 1         # Kalshi limit order buffer
    pm_price_buffer_cents: int = 3      # PM limit order buffer (3c to account for latency)

    # ==========================================================================
    # TIMING & STALENESS
    # ==========================================================================
    max_price_staleness_ms: int = 2000  # Max age for prices
    max_price_age_ms: int = 500         # Reject prices older than this
    pm_poll_interval_ms: int = 100      # PM REST polling interval (faster for fresher prices)
    cooldown_seconds: int = 10          # Seconds between trade attempts
    scan_interval_ms: int = 500         # Target scan interval

    # ==========================================================================
    # SAFETY LIMITS
    # ==========================================================================
    min_pm_price: int = 5               # Safety floor 5c
    min_buy_price: int = 5              # Safety floor 5c on buy side
    max_roi: float = 50.0               # Max ROI before flagging as bad data
    unhedged_exposure_limit: int = 1000 # Max unhedged cents before kill switch
    max_concurrent_positions: int = 15  # Max open positions across all platforms
    max_contracts_per_game: int = 20    # Max contracts per game (sizing algo is real governor)
    max_crashes_per_game: int = 2       # Blacklist game after this many execution crashes

    # ==========================================================================
    # LIQUIDITY
    # ==========================================================================
    liquidity_utilization: float = 0.66  # Use 66% of available liquidity

    # ==========================================================================
    # DEPTH-AWARE SIZING
    # ==========================================================================
    depth_cap: float = 0.70              # Fraction of book depth to consume (--depth-factor)
    min_profit_per_contract: float = 1.0  # Min expected net cents per marginal contract (--min-profit)

    # ==========================================================================
    # GTC (MAKER) EXECUTION
    # ==========================================================================
    enable_gtc: bool = True               # Enable IOC-then-GTC two-phase execution
    gtc_timeout_seconds: float = 3.0      # Max time to rest a GTC order
    gtc_recheck_interval_ms: int = 200    # Spread recheck interval during GTC rest
    gtc_cooldown_seconds: int = 5         # Per-game cooldown after GTC timeout

    # ==========================================================================
    # CLASS METHODS FOR MODE CONTROL
    # ==========================================================================

    @classmethod
    def set_live(cls):
        """Set execution mode to LIVE."""
        cls.execution_mode = ExecutionMode.LIVE
        cls.paper_no_limits = False  # Enforce limits in live mode

    @classmethod
    def set_paper(cls, no_limits: bool = True):
        """Set execution mode to PAPER."""
        cls.execution_mode = ExecutionMode.PAPER
        cls.paper_no_limits = no_limits

    @classmethod
    def is_live(cls) -> bool:
        """Check if running in live mode."""
        return cls.execution_mode == ExecutionMode.LIVE

    @classmethod
    def is_paper(cls) -> bool:
        """Check if running in paper mode."""
        return cls.execution_mode == ExecutionMode.PAPER

    @classmethod
    def is_paper_unlimited(cls) -> bool:
        """Check if running in paper mode with no limits."""
        return cls.execution_mode == ExecutionMode.PAPER and cls.paper_no_limits

    @classmethod
    def configure_from_args(cls, args):
        """
        Configure from argparse args object.

        Expected args attributes:
            - live: bool
            - spread_min: int (optional)
            - contracts: int (optional)
            - no_limits: bool (optional)
            - dry_run: bool (optional)
        """
        if getattr(args, 'live', False):
            cls.set_live()
        else:
            no_limits = getattr(args, 'no_limits', True)
            cls.set_paper(no_limits=no_limits)

        if hasattr(args, 'spread_min') and args.spread_min is not None:
            cls.spread_min_cents = args.spread_min

        if hasattr(args, 'contracts') and args.contracts is not None:
            cls.max_contracts = args.contracts
            # If max_contracts is set low, also lower min_contracts
            cls.min_contracts = min(cls.min_contracts, args.contracts)

        if hasattr(args, 'max_positions') and args.max_positions is not None:
            cls.max_concurrent_positions = args.max_positions

        if hasattr(args, 'dry_run') and args.dry_run:
            cls.dry_run_mode = True

        if hasattr(args, 'min_profit') and args.min_profit is not None:
            cls.min_profit_per_contract = args.min_profit

        if hasattr(args, 'depth_factor') and args.depth_factor is not None:
            cls.depth_cap = args.depth_factor

        if hasattr(args, 'gtc_timeout') and args.gtc_timeout is not None:
            cls.gtc_timeout_seconds = args.gtc_timeout
        if hasattr(args, 'spread_recheck_interval') and args.spread_recheck_interval is not None:
            cls.gtc_recheck_interval_ms = args.spread_recheck_interval
        if hasattr(args, 'enable_gtc') and args.enable_gtc is not None:
            cls.enable_gtc = args.enable_gtc

        # Sync max_contracts_per_game with max_contracts
        cls.max_contracts_per_game = cls.max_contracts

    @classmethod
    def get_min_execution_spread(cls) -> int:
        """Calculate minimum spread needed for profitable execution."""
        return cls.kalshi_fee_cents + 1 + cls.expected_slippage_cents + cls.min_profit_cents

    @classmethod
    def summary(cls) -> str:
        """Return a summary string of current configuration."""
        mode = "LIVE" if cls.is_live() else "PAPER"
        if cls.is_paper() and cls.paper_no_limits:
            mode += " (no limits)"
        if cls.dry_run_mode:
            mode += " [DRY RUN]"

        return (
            f"Mode: {mode} | "
            f"Spread: {cls.spread_min_cents}c min | "
            f"Contracts: {cls.min_contracts}-{cls.max_contracts} | "
            f"Max cost: ${cls.max_cost_cents/100:.0f}"
        )
