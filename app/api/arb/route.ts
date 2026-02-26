import { NextRequest, NextResponse } from "next/server";

// ── Types ──────────────────────────────────────────────────────────────────

export interface SpreadRow {
  game_id: string;
  game_name: string;
  sport: string;
  team: string;
  k_bid: number;
  k_ask: number;
  pm_bid: number;
  pm_ask: number;
  spread_buy_pm: number;
  spread_buy_k: number;
  pm_size: number;
  is_executable: boolean;
  game_date?: string;
  updated_at: string;
}

export interface PerContractPnl {
  k_cost: number;
  pm_cost: number;
  total_cost: number;
  payout: number;
  gross: number;
  fees: number;
  net: number;
  direction: string;
}

export interface ActualPnl {
  contracts: number;
  total_cost_dollars: number;
  total_payout_dollars: number;
  gross_profit_dollars: number;
  fees_dollars: number;
  net_profit_dollars: number;
  per_contract: PerContractPnl;
  is_profitable: boolean;
}

export interface DepthWalkLevel {
  level: number;
  k_price: number;
  pm_cost: number;
  spread: number;
  fees: number;
  marginal_profit: number;
  k_remaining: number;
  pm_remaining: number;
  cumulative_contracts: number;
  contracts_at_level?: number;
  stopped?: boolean;
}

export interface DepthProfileLevel {
  level: number;
  k_price: number;
  pm_cost: number;
  spread: number;
  net: number;
  available: number;
  cumulative: number;
}

export interface SizingDetails {
  avg_spread_cents: number;
  expected_profit_cents: number;
  k_depth: number;
  pm_depth: number;
  limit_reason: string;
  depth_walk_log?: DepthWalkLevel[];
  depth_profile?: DepthProfileLevel[];
  max_profitable_contracts?: number;
  max_theoretical_profit_cents?: number;
  traded_contracts?: number;
  captured_profit_cents?: number;
}

export interface TradeEntry {
  timestamp: string;
  game_id: string;
  team: string;
  sport: string;
  direction: string;
  spread_cents: number;
  estimated_net_profit_cents: number;
  hedged: boolean;
  status: string;
  k_price: number;
  pm_price: number;
  contracts_filled: number;
  contracts_intended?: number;
  actual_pnl: ActualPnl | null;
  paper_mode: boolean;
  sizing_details?: SizingDetails | null;
  execution_phase?: string;
  is_maker?: boolean;
  gtc_rest_time_ms?: number;
  gtc_spread_checks?: number;
  gtc_cancel_reason?: string;
  unwind_loss_cents?: number | null;
  unwind_pnl_cents?: number | null;
  unwind_fill_price?: number | null;
  unwind_qty?: number;
  execution_time_ms?: number;
  pm_order_ms?: number;
  k_order_ms?: number;
  tier?: string;
  pm_fee?: number;
  k_fee?: number;
  settlement_pnl?: number | null;
  settlement_time?: string | null;
  settlement_winner_index?: number | null;
  opponent?: string;
  team_full_name?: string;
  opponent_full_name?: string;
  cache_key?: string;
  pm_slug?: string;
  kalshi_ticker?: string;
  reconciled_pnl?: number | null;
  skip_reason?: string;
  abort_reason?: string;
}

export interface PnlSummary {
  total_pnl_dollars: number;
  profitable_count: number;
  losing_count: number;
  total_trades: number;
  total_attempts: number;
  total_filled: number;
  hedged_count: number;
  unhedged_filled: number;
  cash_pnl?: number;
  portfolio_total?: number;
  starting_balance?: number;
}

export interface Position {
  game_id: string;
  team: string;
  team_full_name?: string;
  opponent?: string;
  opponent_full_name?: string;
  sport: string;
  direction: string;
  status: string;
  tier: string;
  hedged: boolean;
  timestamp: string;
  contracts: number;
  pm_fill_cents: number;
  k_fill_cents: number;
  pm_bid_now: number;
  pm_ask_now: number;
  k_bid_now: number;
  k_ask_now: number;
  pm_cost_dollars: number;
  k_cost_dollars: number;
  pm_mkt_val_dollars: number;
  k_mkt_val_dollars: number;
  pm_fee: number;
  k_fee: number;
  total_fees: number;
  unrealised_pnl: number;
  spread_cents: number;
  ceq: number | null;
  signal: string | null;
}

export interface Balances {
  k_cash: number;
  k_portfolio: number;
  pm_cash: number;
  pm_portfolio: number;
  pm_positions?: number;
  k_positions?: number;
  pm_positions_source?: string;
  total_portfolio: number;
  kalshi_balance: number;
  pm_balance: number;
  updated_at: string;
}

export interface SystemStatus {
  ws_connected: boolean;
  ws_messages_processed: number;
  uptime_seconds: number;
  last_scan_at: string;
  games_monitored: number;
  executor_version: string;
  error_count: number;
  last_error: string | null;
}

export interface MappedGame {
  cache_key: string;
  game_id: string;
  sport: string;
  date: string;
  team1: string;
  team2: string;
  team1_full?: string;
  team2_full?: string;
  pm_slug: string;
  kalshi_tickers: string[];
  best_spread: number;
  k_depth?: number;
  pm_depth?: number;
  status: string;
  traded: boolean;
}

export interface GameLiquidity {
  game_id: string;
  platform: string;
  snapshots: number;
  avg_bid_depth: number;
  avg_ask_depth: number;
  avg_spread: number;
  min_spread: number;
  max_spread: number;
  best_bid_seen: number;
  best_ask_seen: number;
  last_snapshot: string;
}

export interface SpreadSnapshot {
  game_id: string;
  platform: string;
  timestamp: string;
  best_bid: number;
  best_ask: number;
  bid_depth: number;
  ask_depth: number;
  spread: number;
}

export interface LiquidityAggregate {
  total_snapshots: number;
  unique_games: number;
  overall_avg_bid_depth: number;
  overall_avg_ask_depth: number;
  overall_avg_spread: number;
}

export interface LiquidityStats {
  per_game: GameLiquidity[];
  spread_history: SpreadSnapshot[];
  aggregate: LiquidityAggregate;
}

export interface SpreadHistoryPoint {
  timestamp: string;
  game_id: string;
  team: string;
  sport: string;
  spread_buy_pm: number;
  spread_buy_k: number;
  best_spread: number;
}

export interface ArbState {
  spreads: SpreadRow[];
  spread_history: SpreadHistoryPoint[];
  trades: TradeEntry[];
  positions: Position[];
  balances: Balances;
  system: SystemStatus;
  pnl_summary: PnlSummary;
  mapped_games: MappedGame[];
  liquidity_stats: LiquidityStats;
  specs?: any;
  mappings_last_refreshed: string;
  updated_at: string;
}

// ── In-memory store ────────────────────────────────────────────────────────

const DEFAULT_STATE: ArbState = {
  spreads: [],
  spread_history: [],
  trades: [],
  positions: [],
  balances: {
    k_cash: 0,
    k_portfolio: 0,
    pm_cash: 0,
    pm_portfolio: 0,
    total_portfolio: 0,
    kalshi_balance: 0,
    pm_balance: 0,
    updated_at: "",
  },
  system: {
    ws_connected: false,
    ws_messages_processed: 0,
    uptime_seconds: 0,
    last_scan_at: "",
    games_monitored: 0,
    executor_version: "",
    error_count: 0,
    last_error: null,
  },
  pnl_summary: {
    total_pnl_dollars: 0,
    profitable_count: 0,
    losing_count: 0,
    total_trades: 0,
    total_attempts: 0,
    total_filled: 0,
    hedged_count: 0,
    unhedged_filled: 0,
  },
  mapped_games: [],
  liquidity_stats: {
    per_game: [],
    spread_history: [],
    aggregate: {
      total_snapshots: 0,
      unique_games: 0,
      overall_avg_bid_depth: 0,
      overall_avg_ask_depth: 0,
      overall_avg_spread: 0,
    },
  },
  specs: undefined,
  mappings_last_refreshed: "",
  updated_at: "",
};

// Simple auth token - set ARB_API_TOKEN env var on Vercel
const AUTH_TOKEN = process.env.ARB_API_TOKEN || "";

let arbState: ArbState = { ...DEFAULT_STATE };

// ── Handlers ───────────────────────────────────────────────────────────────

export async function GET() {
  return NextResponse.json(arbState);
}

export async function POST(req: NextRequest) {
  // Verify token if set
  if (AUTH_TOKEN) {
    const token = req.headers.get("Authorization")?.replace("Bearer ", "");
    if (token !== AUTH_TOKEN) {
      return NextResponse.json({ error: "unauthorized" }, { status: 401 });
    }
  }

  try {
    const body = await req.json();

    // Support partial updates - merge whatever fields are sent
    if (body.spreads !== undefined) arbState.spreads = body.spreads;
    if (body.spread_history !== undefined) arbState.spread_history = body.spread_history;
    if (body.trades !== undefined) arbState.trades = body.trades;
    if (body.positions !== undefined) arbState.positions = body.positions;
    if (body.balances !== undefined) arbState.balances = body.balances;
    if (body.system !== undefined) arbState.system = body.system;
    if (body.pnl_summary !== undefined) arbState.pnl_summary = body.pnl_summary;
    if (body.mapped_games !== undefined) arbState.mapped_games = body.mapped_games;
    if (body.liquidity_stats !== undefined) arbState.liquidity_stats = body.liquidity_stats;
    if (body.specs !== undefined) arbState.specs = body.specs;
    if (body.mappings_last_refreshed !== undefined) arbState.mappings_last_refreshed = body.mappings_last_refreshed;
    arbState.updated_at = new Date().toISOString();

    return NextResponse.json({ ok: true, updated_at: arbState.updated_at });
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
}
