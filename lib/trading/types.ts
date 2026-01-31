export interface Position {
  ticker: string;
  position: number;
  market_exposure: number;
  resting_orders_count?: number;
  total_cost?: number;
}

export interface Trade {
  timestamp: string;
  sport: string;
  game: string;
  team: string;
  direction: string;
  intended_size: number;
  k_fill_count: number;
  k_fill_price?: number;
  k_order_id?: string;
  pm_success: boolean;
  pm_error?: string;
  pm_fill_count?: number;
  pm_fill_price?: number;
  pm_order_id?: string;
  pm_slug?: string;
  status: string;
  raw_status?: string;
  execution_mode?: "paper" | "live";
  expected_profit: number;
  roi: number;
}

export type TradeFilter = "all" | "live" | "paper" | "failed";
export type SortField = "timestamp" | "profit" | "roi" | "status" | "team";

export interface LogEntry {
  time: string;
  message: string;
}

export interface ScanInfo {
  scanNumber: number;
  gamesFound: number;
  arbsFound: number;
  isScanning: boolean;
}

export interface BotStatus {
  bot_state: "stopped" | "starting" | "running" | "stopping" | "error";
  mode: "paper" | "live";
  balance: number | null;
  positions: Position[];
  trade_count: number;
  timestamp: string;
}

export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export type ActiveTab = "dashboard" | "trades" | "markets" | "research" | "logs";

export type PnLPeriod = "1H" | "6H" | "24H" | "ALL";

export type LogLevel = "ALL" | "SUCCESS" | "ERROR" | "ORDER" | "INFO";

export interface TradeStatusDisplay {
  text: string;
  color: string;
  bg: string;
}

export interface CumulativePnLPoint {
  timestamp: number;
  value: number;
}

export interface DrawdownPoint {
  timestamp: number;
  drawdown: number;
}

export interface HeatmapCell {
  sport: string;
  hour: number;
  count: number;
}

export interface SportVolume {
  sport: string;
  kalshi: number;
  pm: number;
}

export interface ROIBucket {
  range: string;
  min: number;
  max: number;
  count: number;
}

export interface SportProfit {
  sport: string;
  profit: number;
  count: number;
}

export interface KalshiMarket {
  sport: string;
  game: string;
  team: string;
  ticker: string;
  k_bid: number;
  k_ask: number;
  k_volume: number;
  pm_volume: number;
  pm_slug: string | null;
  pm_bid: number | null;
  pm_ask: number | null;
  matched: boolean;
  date: string | null;
}

export interface SportVolumeData {
  kalshi: number;
  pm: number;
  total: number;
}

export interface VolumeHistoryPoint {
  timestamp: string;
  kalshi: number;
  pm: number;
  total: number;
}

export interface TotalVolume {
  kalshi: number;
  pm: number;
  total: number;
}

export interface MatchStats {
  matched: number;
  total: number;
  rate: number;
}

export interface SpreadData {
  sport: string;
  game: string;
  team: string;
  k_bid: number;
  k_ask: number;
  pm_bid: number;
  pm_ask: number;
  spread: number;
  roi: number;
  status: "ARB" | "CLOSE" | "NO_EDGE";
  pm_slug: string;
  ticker: string;
}

export interface MarketData {
  timestamp: string | null;
  kalshi_games: KalshiMarket[];
  match_stats: Record<string, MatchStats>;
  spreads: SpreadData[];
  total_kalshi: number;
  total_matched: number;
  volume_by_sport: Record<string, SportVolumeData>;
  volume_history: VolumeHistoryPoint[];
  total_volume: TotalVolume;
}

// Game Price History for drill-down charts
export interface GamePricePoint {
  timestamp: string;
  kalshi_bid: number;
  kalshi_ask: number;
  pm_bid: number;
  pm_ask: number;
  spread: number;
}

export interface GamePriceHistory {
  game_id: string;
  sport: string;
  game: string;
  team: string;
  ticker: string;
  pm_slug: string;
  is_live: boolean;
  start_time: string | null;
  prices: GamePricePoint[];
  current_spread: number;
  arb_status: "ARB" | "CLOSE" | "NO_EDGE";
  data_points?: number;
  total_data_points?: number;
  game_duration_hours?: number;
  time_filter_hours?: number;
  error?: string;
}

export type TimeRange = "1H" | "3H" | "6H" | "ALL";

export interface LeagueStats {
  sport: string;
  matched: number;
  total: number;
  rate: number;
  live_count: number;
  arb_count: number;
}

export interface MatchupInfo {
  game_id: string;
  sport: string;
  game: string;
  teams: string[];
  kalshi_price: number;
  pm_price: number;
  spread: number;
  status: "ARB" | "CLOSE" | "NO_EDGE";
  is_live: boolean;
  start_time: string | null;
  ticker: string;
  pm_slug: string;
}

export type MarketView = "leagues" | "matchups" | "game";

export interface FullAnalytics {
  liveTrades: Trade[];
  paperTrades: Trade[];
  failedTrades: Trade[];
  liveAttempts: Trade[];
  fillRate: number;
  totalPnL: number;
  lastSuccessfulTrade: Trade | undefined;
  totalTrades: number;
  winRate: number;
  avgProfit: number;
  sharpe: number;
  maxDrawdown: number;
  cumulativePnL: CumulativePnLPoint[];
  drawdownSeries: DrawdownPoint[];
  volumeBySport: SportVolume[];
  heatmapData: HeatmapCell[];
  roiDistribution: ROIBucket[];
  profitBySport: SportProfit[];
  tradesByHour: number[];
}
