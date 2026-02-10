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
  updated_at: string;
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
  actual_pnl: number | null;
  paper_mode: boolean;
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

export interface ArbState {
  spreads: SpreadRow[];
  trades: TradeEntry[];
  positions: Position[];
  balances: Balances;
  system: SystemStatus;
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
    arbState.updated_at = new Date().toISOString();

    return NextResponse.json({ ok: true, updated_at: arbState.updated_at });
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
}
