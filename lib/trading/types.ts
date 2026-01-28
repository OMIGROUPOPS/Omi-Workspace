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

export type ActiveTab = "dashboard" | "trades" | "research" | "logs";

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
