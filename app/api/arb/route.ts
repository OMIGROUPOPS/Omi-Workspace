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

export interface SizingDetails {
  avg_spread_cents: number;
  expected_profit_cents: number;
  k_depth: number;
  pm_depth: number;
  limit_reason: string;
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
}

export interface Position {
  platform: string;
  game_id: string;
  team: string;
  sport: string;
  side: string;
  quantity: number;
  avg_price: number;
  current_value: number;
  hedged_with: string | null;
  hedge_source?: string | null;
  pm_fill_price?: number;
  k_fill_price?: number;
  direction?: string;
  locked_profit_cents?: number;
  net_profit_cents?: number;
  contracts?: number;
  trade_timestamp?: string;
}

export interface Balances {
  kalshi_balance: number;
  pm_balance: number;
  total_portfolio: number;
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
  pm_slug: string;
  kalshi_tickers: string[];
  best_spread: number;
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

export interface ArbState {
  spreads: SpreadRow[];
  trades: TradeEntry[];
  positions: Position[];
  balances: Balances;
  system: SystemStatus;
  pnl_summary: PnlSummary;
  mapped_games: MappedGame[];
  liquidity_stats: LiquidityStats;
  mappings_last_refreshed: string;
  updated_at: string;
}

// ── In-memory store ────────────────────────────────────────────────────────

const DEFAULT_STATE: ArbState = {
  spreads: [],
  trades: [],
  positions: [],
  balances: {
    kalshi_balance: 0,
    pm_balance: 0,
    total_portfolio: 0,
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
    if (body.trades !== undefined) arbState.trades = body.trades;
    if (body.positions !== undefined) arbState.positions = body.positions;
    if (body.balances !== undefined) arbState.balances = body.balances;
    if (body.system !== undefined) arbState.system = body.system;
    if (body.pnl_summary !== undefined) arbState.pnl_summary = body.pnl_summary;
    if (body.mapped_games !== undefined) arbState.mapped_games = body.mapped_games;
    if (body.liquidity_stats !== undefined) arbState.liquidity_stats = body.liquidity_stats;
    if (body.mappings_last_refreshed !== undefined) arbState.mappings_last_refreshed = body.mappings_last_refreshed;
    arbState.updated_at = new Date().toISOString();

    return NextResponse.json({ ok: true, updated_at: arbState.updated_at });
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
}
