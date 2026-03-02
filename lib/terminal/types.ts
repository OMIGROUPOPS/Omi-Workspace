// OMNI Terminal — TypeScript types

export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export type SignalSeverity = "HIGH" | "MEDIUM" | "LOW";

export type ScanType =
  | "momentum_lag"
  | "mean_reversion"
  | "contradiction_mono"
  | "contradiction_cross"
  | "resolution"
  | "whale_momentum";

export type TakerSide = "yes" | "no";

export interface BBOEntry {
  ts: number;
  bid: number;
  ask: number;
  bid_size: number;
  ask_size: number;
}

export interface OrderbookLevel {
  price: number;
  size: number;
}

export interface Orderbook {
  ticker: string;
  bids: OrderbookLevel[];
  asks: OrderbookLevel[];
  best_bid: number | null;
  best_ask: number | null;
  best_bid_size: number;
  best_ask_size: number;
  last_update: number;
}

export interface MarketInfo {
  ticker: string;
  event_ticker: string;
  game_id: string;
  market_type: "moneyline" | "spread" | "total" | "variant";
  team: string;
  floor_strike: number | null;
  close_time: string | null;
  category: string;
}

export interface ScanSignal {
  scan_type: ScanType;
  severity: SignalSeverity;
  ticker: string;
  game_id: string;
  entry_side: "buy_yes" | "buy_no";
  entry_price: number;
  target: number;
  stop: number;
  description: string;
  depth: number;
  bridge_confidence?: number;
  sigma_estimate?: number;
  time_remaining?: number;
  optimal_size?: number;
  timestamp: number;
}

export interface PaperTrade {
  id: string;
  scan_type: ScanType;
  ticker: string;
  game_id: string;
  side: "buy_yes" | "buy_no";
  entry_price: number;
  entry_time: number;
  target: number;
  stop: number;
  exit_price?: number;
  exit_time?: number;
  pnl_cents?: number;
  exit_reason?: "TARGET" | "STOP" | "TIMEOUT";
  description: string;
  kyle_lambda?: number;
  conv_time?: number;
  bridge_confidence?: number;
  sigma_estimate?: number;
  time_remaining?: number;
  optimal_contracts?: number;
  depth_mult?: number;
  cv_edge?: number;
  adjusted_kelly?: number;
}

export interface WhaleFill {
  ticker: string;
  category: string;
  price: number;
  count: number;
  taker_side: TakerSide;
  timestamp: number;
}

export interface ScannerStats {
  uptime: number;
  ws_connected: boolean;
  ws_messages: number;
  bbo_updates: number;
  scan_signals: number;
  paper_trades_opened: number;
  paper_trades_closed: number;
  open_trades: number;
  total_pnl: number;
  winners: number;
  losers: number;
  whale_fills_interval: number;
  whale_fills_total: number;
  lambda_median: number;
  tickers_subscribed: number;
  active_books: number;
}

export interface WatchlistItem {
  ticker: string;
  info: MarketInfo;
  best_bid: number | null;
  best_ask: number | null;
  mid: number | null;
  spread: number;
  bid_size: number;
  ask_size: number;
  move_30s: number | null;
  kyle_lambda: number | null;
}

export interface CountdownItem {
  ticker: string;
  info: MarketInfo;
  price: number;
  side: "near_100" | "near_0";
  secs_to_close: number;
  bridge_confidence: number;
  sigma: number;
  depth: number;
  kelly_size: number;
}

export interface CorrelationPair {
  primary_ticker: string;
  other_ticker: string;
  primary_type: string;
  other_type: string;
  team: string;
  primary_mid: number;
  other_mid: number;
  expected_corr: number;
  actual_ratio: number;
  lag_detected: boolean;
}

export interface PnLBreakdown {
  scan_type: ScanType;
  total_pnl: number;
  trade_count: number;
  winners: number;
  losers: number;
  avg_hold_time: number;
  avg_edge: number;
}
