// Re-export all types from the API route
export type {
  SpreadRow,
  TradeEntry,
  ActualPnl,
  PerContractPnl,
  SizingDetails,
  DepthWalkLevel,
  DepthProfileLevel,
  PnlSummary,
  Position,
  Balances,
  SystemStatus,
  MappedGame,
  GameLiquidity,
  SpreadSnapshot,
  LiquidityAggregate,
  LiquidityStats,
  SpreadHistoryPoint,
  ArbState,
} from "@/app/api/arb/route";

// ── Local UI types ──────────────────────────────────────────────────────────

export type TopTab = "monitor" | "pnl_history" | "depth" | "operations";
export type TradeFilter = "all" | "live" | "paper";
export type StatusFilter = "all" | "SUCCESS" | "PM_NO_FILL" | "EXITED" | "UNHEDGED" | "SKIPPED";
export type BottomTab = "positions" | "mapped_games";
export type TimeHorizon = "1D" | "1W" | "1M" | "YTD" | "ALL";
export type TradeSortKey = "time" | "spread" | "net" | "qty" | "phase";

export interface AlertInfo {
  type: "warning" | "error" | "info";
  message: string;
}
