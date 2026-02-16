"use client";

import React, { useEffect, useState, useCallback, useMemo, useRef } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

// ── Types ──────────────────────────────────────────────────────────────────

interface SpreadRow {
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

interface PerContractPnl {
  k_cost: number;
  pm_cost: number;
  total_cost: number;
  payout: number;
  gross: number;
  fees: number;
  net: number;
  direction: string;
}

interface ActualPnl {
  contracts: number;
  total_cost_dollars: number;
  total_payout_dollars: number;
  gross_profit_dollars: number;
  fees_dollars: number;
  net_profit_dollars: number;
  per_contract: PerContractPnl;
  is_profitable: boolean;
}

interface SizingDetails {
  avg_spread_cents: number;
  expected_profit_cents: number;
  k_depth: number;
  pm_depth: number;
  limit_reason: string;
}

interface TradeEntry {
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
  execution_time_ms?: number;
  pm_order_ms?: number;
}

interface PnlSummary {
  total_pnl_dollars: number;
  profitable_count: number;
  losing_count: number;
  total_trades: number;
  total_attempts: number;
  total_filled: number;
  hedged_count: number;
  unhedged_filled: number;
}

interface Position {
  platform: string;
  game_id: string;
  team: string;
  sport: string;
  side: string;
  quantity: number;
  avg_price: number;
  current_value: number;
  hedged_with: string | null;
  hedge_source?: "API_MATCHED" | "CONFIRMED" | "UNHEDGED" | null;
  pm_fill_price?: number;
  k_fill_price?: number;
  direction?: string;
  locked_profit_cents?: number;
  net_profit_cents?: number;
  contracts?: number;
  trade_timestamp?: string;
}

interface Balances {
  k_cash: number;
  k_portfolio: number;
  pm_cash: number;
  pm_portfolio: number;
  total_portfolio: number;
  kalshi_balance: number;
  pm_balance: number;
  updated_at: string;
}

interface SystemStatus {
  ws_connected: boolean;
  ws_messages_processed: number;
  uptime_seconds: number;
  last_scan_at: string;
  games_monitored: number;
  executor_version: string;
  error_count: number;
  last_error: string | null;
}

interface MappedGame {
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

interface GameLiquidity {
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

interface SpreadSnapshot {
  game_id: string;
  platform: string;
  timestamp: string;
  best_bid: number;
  best_ask: number;
  bid_depth: number;
  ask_depth: number;
  spread: number;
}

interface LiquidityAggregate {
  total_snapshots: number;
  unique_games: number;
  overall_avg_bid_depth: number;
  overall_avg_ask_depth: number;
  overall_avg_spread: number;
}

interface LiquidityStats {
  per_game: GameLiquidity[];
  spread_history: SpreadSnapshot[];
  aggregate: LiquidityAggregate;
}

interface ArbState {
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

// ── Helpers ────────────────────────────────────────────────────────────────

function spreadColor(cents: number): string {
  if (cents >= 4) return "text-emerald-400";
  if (cents >= 3) return "text-yellow-400";
  if (cents > 0) return "text-gray-400";
  return "text-red-400";
}

function spreadBg(cents: number): string {
  if (cents >= 4) return "bg-emerald-500/10";
  if (cents >= 3) return "bg-yellow-500/10";
  return "";
}

function netColor(cents: number | null | undefined): string {
  if (cents == null) return "text-gray-500";
  if (cents > 0) return "text-emerald-400";
  if (cents < 0) return "text-red-400";
  return "text-gray-400";
}

/** Uniform P&L calculation for any trade status.
 *  Returns per-contract cents and total dollars. */
function tradePnl(t: TradeEntry): { perContract: number | null; totalDollars: number | null; qty: number } {
  const qty = t.contracts_filled > 0 ? t.contracts_filled : (t.contracts_intended || 0);

  if (t.status === "EXITED") {
    if (t.unwind_loss_cents != null && t.unwind_loss_cents !== 0) {
      // unwind_loss_cents is already total across all contracts
      const totalLoss = Math.abs(t.unwind_loss_cents);
      const perContract = qty > 0 ? -(totalLoss / qty) : -totalLoss;
      return { perContract, totalDollars: -(totalLoss / 100), qty };
    }
    return { perContract: null, totalDollars: null, qty };
  }

  if (t.status === "SUCCESS") {
    if (t.actual_pnl) {
      return {
        perContract: t.actual_pnl.per_contract.net,
        totalDollars: t.actual_pnl.net_profit_dollars,
        qty,
      };
    }
    if (t.estimated_net_profit_cents != null) {
      const pc = t.estimated_net_profit_cents;
      return { perContract: pc, totalDollars: (pc * qty) / 100, qty };
    }
  }

  if (t.status === "UNHEDGED") {
    // Unhedged = exposed, show estimated spread as potential
    if (t.estimated_net_profit_cents != null) {
      const pc = t.estimated_net_profit_cents;
      return { perContract: pc, totalDollars: (pc * qty) / 100, qty };
    }
  }

  // PM_NO_FILL, SKIPPED, or no data
  return { perContract: null, totalDollars: null, qty };
}

function statusBadge(status: string): { bg: string; text: string } {
  if (status === "HEDGED" || status === "FILLED" || status === "SUCCESS")
    return { bg: "bg-emerald-500/20", text: "text-emerald-400" };
  if (status.includes("NO_FILL") || status === "EXITED")
    return { bg: "bg-yellow-500/20", text: "text-yellow-400" };
  if (status === "FAILED" || status === "ERROR" || status === "UNHEDGED")
    return { bg: "bg-red-500/20", text: "text-red-400" };
  if (status === "SKIPPED")
    return { bg: "bg-gray-500/20", text: "text-gray-400" };
  return { bg: "bg-gray-500/20", text: "text-gray-400" };
}

function sportBadge(sport: string): string {
  switch (sport) {
    case "NBA":
      return "bg-orange-500/20 text-orange-400";
    case "CBB":
      return "bg-blue-500/20 text-blue-400";
    case "NHL":
      return "bg-cyan-500/20 text-cyan-400";
    default:
      return "bg-gray-500/20 text-gray-400";
  }
}

function timeAgo(iso: string): string {
  if (!iso) return "never";
  const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
  const diff = Date.now() - new Date(s).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 0) return "just now";
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function formatUptime(seconds: number): string {
  if (!seconds) return "0s";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function formatDateTime(iso: string): string {
  if (!iso) return "-";
  try {
    const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
    const d = new Date(s);
    const mon = d.toLocaleString("en-US", { month: "short" });
    const day = d.getDate();
    const time = d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    return `${mon} ${day} ${time}`;
  } catch {
    return iso;
  }
}

function isToday(dateStr: string | undefined): boolean {
  if (!dateStr) return false;
  const today = new Date().toISOString().slice(0, 10);
  return dateStr === today;
}

function toDateStr(iso: string): string {
  if (!iso) return "";
  try {
    const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
    return new Date(s).toISOString().slice(0, 10);
  } catch {
    return "";
  }
}

function formatDateLabel(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr + "T12:00:00Z");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return dateStr;
  }
}

function formatShortDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr + "T12:00:00Z");
    return d.toLocaleDateString("en-US", { month: "numeric", day: "numeric" });
  } catch {
    return dateStr;
  }
}

function mappingsHealthColor(iso: string): string {
  if (!iso) return "bg-gray-500";
  const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
  const hours = (Date.now() - new Date(s).getTime()) / 3600000;
  if (hours < 3) return "bg-emerald-500";
  if (hours < 6) return "bg-yellow-500";
  return "bg-red-500";
}

function formatTimeOnly(iso: string): string {
  if (!iso) return "";
  try {
    const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
    const d = new Date(s);
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  } catch {
    return "";
  }
}

// ── Components ─────────────────────────────────────────────────────────────

function Pulse({ active }: { active: boolean }) {
  return (
    <span className="relative flex h-2.5 w-2.5">
      {active && (
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
      )}
      <span
        className={`relative inline-flex h-2.5 w-2.5 rounded-full ${
          active ? "bg-emerald-500" : "bg-red-500"
        }`}
      />
    </span>
  );
}

function MetricCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] px-3 py-2.5">
      <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500">
        {label}
      </p>
      <p className={`mt-0.5 text-xl font-bold ${accent || "text-white"}`}>
        {value}
      </p>
      {sub && <p className="text-[10px] text-gray-500">{sub}</p>}
    </div>
  );
}

function FilterButton({
  active,
  onClick,
  children,
  variant = "default",
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  variant?: "default" | "green" | "purple" | "red" | "yellow";
}) {
  const activeColors = {
    default: "bg-gray-700 text-white",
    green: "bg-emerald-500/20 text-emerald-400",
    purple: "bg-purple-500/20 text-purple-400",
    red: "bg-red-500/20 text-red-400",
    yellow: "bg-yellow-500/20 text-yellow-400",
  };
  return (
    <button
      onClick={onClick}
      className={`rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
        active ? activeColors[variant] : "text-gray-500 hover:text-gray-300"
      }`}
    >
      {children}
    </button>
  );
}

type TopTab = "monitor" | "pnl_history" | "liquidity";
type TradeFilter = "all" | "live" | "paper";
type StatusFilter = "all" | "SUCCESS" | "PM_NO_FILL" | "EXITED" | "UNHEDGED" | "SKIPPED";
type BottomTab = "positions" | "mapped_games";
type TimeHorizon = "1D" | "1W" | "1M" | "YTD" | "ALL";
type TradeSortKey = "time" | "spread" | "net" | "qty" | "phase";

// ── Main Component ──────────────────────────────────────────────────────────

export default function ArbDashboard() {
  const [state, setState] = useState<ArbState | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  const [fetchError, setFetchError] = useState(false);
  const [paused, setPaused] = useState(false);
  const [topTab, setTopTab] = useState<TopTab>("monitor");
  const [tradeFilter, setTradeFilter] = useState<TradeFilter>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [dateOffset, setDateOffset] = useState(0);
  const [dateAll, setDateAll] = useState(false);
  const [showAllSpreads, setShowAllSpreads] = useState(false);
  const [tradeSearch, setTradeSearch] = useState("");
  const [bottomTab, setBottomTab] = useState<BottomTab>("positions");
  const [hiddenPositions, setHiddenPositions] = useState<Set<string>>(
    new Set()
  );
  const [pnlHorizon, setPnlHorizon] = useState<TimeHorizon>("ALL");
  const [pnlSport, setPnlSport] = useState("all");
  const [tradeSortKey, setTradeSortKey] = useState<TradeSortKey>("time");
  const [tradeSortAsc, setTradeSortAsc] = useState(false);
  const [expandedTrade, setExpandedTrade] = useState<number | null>(null);
  const [expandedMonitorTrade, setExpandedMonitorTrade] = useState<number | null>(null);
  const [liqGameFilter, setLiqGameFilter] = useState("");
  const prevPortfolioRef = useRef<{ k: number; pm: number; total: number } | null>(null);
  const [portfolioDelta, setPortfolioDelta] = useState<{ k: number; pm: number; total: number }>({ k: 0, pm: 0, total: 0 });

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch("/api/arb", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        setState(data);
        setLastFetch(new Date());
        setFetchError(false);
      } else {
        setFetchError(true);
      }
    } catch {
      setFetchError(true);
    }
  }, []);

  useEffect(() => {
    fetchData();
    if (paused) return;
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData, paused]);

  // Track portfolio changes for rate-of-change indicators
  useEffect(() => {
    if (!state?.balances) return;
    const { k_portfolio, pm_portfolio, total_portfolio } = state.balances;
    if (total_portfolio === 0) return;
    const prev = prevPortfolioRef.current;
    if (prev && (prev.k !== k_portfolio || prev.pm !== pm_portfolio)) {
      setPortfolioDelta({
        k: k_portfolio - prev.k,
        pm: pm_portfolio - prev.pm,
        total: total_portfolio - prev.total,
      });
    }
    prevPortfolioRef.current = { k: k_portfolio, pm: pm_portfolio, total: total_portfolio };
  }, [state?.balances?.k_portfolio, state?.balances?.pm_portfolio, state?.balances?.total_portfolio]);

  const hasData = state && state.updated_at;
  const isStale =
    state?.updated_at &&
    Date.now() - new Date(state.updated_at).getTime() > 60_000;

  // ── Date navigation ─────────────────────────────────────────────────
  const selectedDate = useMemo(() => {
    if (dateAll) return null;
    const d = new Date();
    d.setUTCDate(d.getUTCDate() + dateOffset);
    return d.toISOString().slice(0, 10);
  }, [dateOffset, dateAll]);

  const dateLabel = useMemo(() => {
    if (dateAll) return "All Time";
    if (dateOffset === 0) return "Today";
    if (dateOffset === -1) return "Yesterday";
    return formatDateLabel(selectedDate || "");
  }, [dateAll, dateOffset, selectedDate]);

  // ── Spreads ─────────────────────────────────────────────────────────
  const sortedSpreads = useMemo(() => {
    const raw = state?.spreads || [];
    const filtered = showAllSpreads
      ? raw
      : raw.filter((s) => s.spread_buy_pm > 0 || s.spread_buy_k > 0);
    return [...filtered].sort((a, b) => {
      const aMax = Math.max(a.spread_buy_pm, a.spread_buy_k);
      const bMax = Math.max(b.spread_buy_pm, b.spread_buy_k);
      return bMax - aMax;
    });
  }, [state?.spreads, showAllSpreads]);

  const totalSpreadCount = state?.spreads?.length || 0;

  // ── Trades ──────────────────────────────────────────────────────────
  const allTrades = useMemo(() => {
    return [...(state?.trades || [])].sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [state?.trades]);

  const filteredTrades = useMemo(() => {
    let trades = allTrades;

    if (selectedDate) {
      trades = trades.filter((t) => toDateStr(t.timestamp) === selectedDate);
    }

    if (tradeFilter === "paper") {
      trades = trades.filter((t) => t.paper_mode);
    } else if (tradeFilter === "live") {
      trades = trades.filter((t) => !t.paper_mode);
    }

    if (statusFilter !== "all") {
      trades = trades.filter((t) => t.status === statusFilter);
    }

    if (tradeSearch.trim()) {
      const q = tradeSearch.trim().toUpperCase();
      trades = trades.filter(
        (t) =>
          t.team.toUpperCase().includes(q) ||
          t.game_id.toUpperCase().includes(q)
      );
    }

    return trades;
  }, [allTrades, selectedDate, tradeFilter, statusFilter, tradeSearch]);

  const filteredPnl = useMemo(() => {
    let successPnl = 0;
    let exitedLoss = 0;
    let successes = 0;
    let fills = 0;
    for (const t of filteredTrades) {
      if (t.status === "SUCCESS") successes++;
      if (t.contracts_filled > 0) fills++;
      const pnl = tradePnl(t);
      if (pnl.totalDollars != null) {
        if (t.status === "SUCCESS") {
          successPnl += pnl.totalDollars;
        } else if (t.status === "EXITED") {
          exitedLoss += pnl.totalDollars;
        }
      }
    }
    const netTotal = successPnl + exitedLoss;
    return { successPnl, exitedLoss, netTotal, successes, fills, count: filteredTrades.length };
  }, [filteredTrades]);

  const pnl = state?.pnl_summary;

  // ── Positions ───────────────────────────────────────────────────────
  const activePositions = useMemo(() => {
    return (state?.positions || []).filter(
      (p) => p.quantity > 0 && !hiddenPositions.has(p.game_id)
    );
  }, [state?.positions, hiddenPositions]);

  const unhedgedPositions = activePositions.filter((p) => !p.hedged_with);
  const hedgedPositions = activePositions.filter((p) => p.hedged_with);

  // Position market value = portfolio - cash per platform
  const positionValues = useMemo(() => {
    const b = state?.balances;
    if (!b) return { pm: 0, kalshi: 0, total: 0 };
    const pm = (b.pm_portfolio ?? 0) - (b.pm_cash ?? 0);
    const kalshi = (b.k_portfolio ?? 0) - (b.k_cash ?? 0);
    return { pm, kalshi, total: pm + kalshi };
  }, [state?.balances]);

  const mappedGames = state?.mapped_games || [];

  const markSettled = (gameId: string) => {
    setHiddenPositions((prev) => new Set(prev).add(gameId));
  };

  // ── P&L History data ────────────────────────────────────────────────
  const availableSports = useMemo(() => {
    const sports = new Set<string>();
    for (const t of allTrades) {
      if (t.sport) sports.add(t.sport);
    }
    return ["all", ...Array.from(sports).sort()];
  }, [allTrades]);

  const pnlTrades = useMemo(() => {
    let trades = allTrades.filter(
      (t) =>
        t.status === "SUCCESS" &&
        t.actual_pnl &&
        !t.paper_mode &&
        t.contracts_filled > 0
    );

    if (pnlSport !== "all") {
      trades = trades.filter((t) => t.sport === pnlSport);
    }

    if (pnlHorizon !== "ALL") {
      const now = new Date();
      let cutoff: Date;
      switch (pnlHorizon) {
        case "1D":
          cutoff = new Date(now.getTime() - 86400000);
          break;
        case "1W":
          cutoff = new Date(now.getTime() - 7 * 86400000);
          break;
        case "1M":
          cutoff = new Date(now.getTime() - 30 * 86400000);
          break;
        case "YTD":
          cutoff = new Date(now.getFullYear(), 0, 1);
          break;
        default:
          cutoff = new Date(0);
      }
      trades = trades.filter(
        (t) => new Date(t.timestamp).getTime() >= cutoff.getTime()
      );
    }

    return [...trades].sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }, [allTrades, pnlSport, pnlHorizon]);

  const pnlAllFiltered = useMemo(() => {
    let trades = allTrades.filter((t) => !t.paper_mode);
    if (pnlSport !== "all") {
      trades = trades.filter((t) => t.sport === pnlSport);
    }
    if (pnlHorizon !== "ALL") {
      const now = new Date();
      let cutoff: Date;
      switch (pnlHorizon) {
        case "1D":
          cutoff = new Date(now.getTime() - 86400000);
          break;
        case "1W":
          cutoff = new Date(now.getTime() - 7 * 86400000);
          break;
        case "1M":
          cutoff = new Date(now.getTime() - 30 * 86400000);
          break;
        case "YTD":
          cutoff = new Date(now.getFullYear(), 0, 1);
          break;
        default:
          cutoff = new Date(0);
      }
      trades = trades.filter(
        (t) => new Date(t.timestamp).getTime() >= cutoff.getTime()
      );
    }
    return trades;
  }, [allTrades, pnlSport, pnlHorizon]);

  const pnlSummaryStats = useMemo(() => {
    let totalPnl = 0;
    let wins = 0;
    let losses = 0;
    let best = -Infinity;
    let worst = Infinity;
    let totalContracts = 0;
    let makerFills = 0;
    let gtcAttempts = 0;
    let gtcFills = 0;

    for (const t of pnlTrades) {
      const net = t.actual_pnl!.net_profit_dollars;
      totalPnl += net;
      totalContracts += t.contracts_filled || 1;
      if (net > 0) wins++;
      else losses++;
      if (net > best) best = net;
      if (net < worst) worst = net;
      if (t.is_maker) makerFills++;
    }

    // GTC stats from all attempts (not just successes)
    for (const t of pnlAllFiltered) {
      if (t.execution_phase === "gtc") {
        gtcAttempts++;
        if (t.contracts_filled > 0) gtcFills++;
      }
    }

    const totalAttempts = pnlAllFiltered.length;
    const noFills = pnlAllFiltered.filter((t) =>
      t.status.includes("NO_FILL")
    ).length;

    return {
      totalTrades: pnlTrades.length,
      totalAttempts,
      wins,
      losses,
      winRate:
        pnlTrades.length > 0
          ? ((wins / pnlTrades.length) * 100).toFixed(1)
          : "0",
      totalPnl,
      avgProfit:
        pnlTrades.length > 0 ? totalPnl / pnlTrades.length : 0,
      best: best === -Infinity ? 0 : best,
      worst: worst === Infinity ? 0 : worst,
      noFills,
      totalContracts,
      makerFills,
      gtcAttempts,
      gtcFills,
      gtcFillRate: gtcAttempts > 0 ? ((gtcFills / gtcAttempts) * 100).toFixed(1) : "0",
    };
  }, [pnlTrades, pnlAllFiltered]);

  const cumulativeChartData = useMemo(() => {
    let cumulative = 0;
    return pnlTrades.map((t, i) => {
      cumulative += t.actual_pnl!.net_profit_dollars;
      return {
        index: i + 1,
        date: toDateStr(t.timestamp),
        time: formatDateTime(t.timestamp),
        pnl: Number(cumulative.toFixed(4)),
        tradePnl: Number(t.actual_pnl!.net_profit_dollars.toFixed(4)),
        team: t.team,
        phase: t.execution_phase || "ioc",
        isMaker: t.is_maker || false,
      };
    });
  }, [pnlTrades]);

  // Per-trade scatter data
  const scatterData = useMemo(() => {
    return pnlTrades.map((t, i) => ({
      index: i + 1,
      net: Number(t.actual_pnl!.net_profit_dollars.toFixed(4)),
      spread: t.spread_cents,
      team: t.team,
      contracts: t.contracts_filled || 1,
      phase: t.execution_phase || "ioc",
      isMaker: t.is_maker || false,
    }));
  }, [pnlTrades]);

  const dailyPnlData = useMemo(() => {
    const byDay: Record<
      string,
      { pnl: number; trades: number; successes: number; noFills: number; contracts: number; makerFills: number }
    > = {};

    for (const t of pnlAllFiltered) {
      const day = toDateStr(t.timestamp);
      if (!day) continue;
      if (!byDay[day])
        byDay[day] = { pnl: 0, trades: 0, successes: 0, noFills: 0, contracts: 0, makerFills: 0 };
      byDay[day].trades++;
      if (t.status === "SUCCESS" && t.actual_pnl) {
        byDay[day].pnl += t.actual_pnl.net_profit_dollars;
        byDay[day].successes++;
        byDay[day].contracts += t.contracts_filled || 1;
        if (t.is_maker) byDay[day].makerFills++;
      }
      if (t.status.includes("NO_FILL")) {
        byDay[day].noFills++;
      }
    }

    return Object.entries(byDay)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, data]) => ({
        date,
        label: formatShortDate(date),
        pnl: Number(data.pnl.toFixed(4)),
        trades: data.trades,
        successes: data.successes,
        noFills: data.noFills,
        contracts: data.contracts,
        makerFills: data.makerFills,
      }));
  }, [pnlAllFiltered]);

  // Fill rate analytics
  const fillRateStats = useMemo(() => {
    const iocAttempts = pnlAllFiltered.filter((t) => (t.execution_phase || "ioc") === "ioc").length;
    const iocFills = pnlAllFiltered.filter((t) => (t.execution_phase || "ioc") === "ioc" && t.contracts_filled > 0).length;
    const gtcAttempts = pnlAllFiltered.filter((t) => t.execution_phase === "gtc").length;
    const gtcFills = pnlAllFiltered.filter((t) => t.execution_phase === "gtc" && t.contracts_filled > 0).length;

    // By spread bucket
    const spreadBuckets: Record<string, { attempts: number; fills: number }> = {};
    for (const t of pnlAllFiltered) {
      const bucket = t.spread_cents < 3 ? "<3c" : t.spread_cents < 4 ? "3-4c" : t.spread_cents < 5 ? "4-5c" : "5c+";
      if (!spreadBuckets[bucket]) spreadBuckets[bucket] = { attempts: 0, fills: 0 };
      spreadBuckets[bucket].attempts++;
      if (t.contracts_filled > 0) spreadBuckets[bucket].fills++;
    }

    // No-fill reasons
    const noFillReasons: Record<string, number> = {};
    for (const t of pnlAllFiltered) {
      if (t.status.includes("NO_FILL")) {
        const reason = t.gtc_cancel_reason || "ioc_expired";
        noFillReasons[reason] = (noFillReasons[reason] || 0) + 1;
      }
    }

    return {
      iocAttempts, iocFills,
      iocRate: iocAttempts > 0 ? ((iocFills / iocAttempts) * 100).toFixed(1) : "0",
      gtcAttempts, gtcFills,
      gtcRate: gtcAttempts > 0 ? ((gtcFills / gtcAttempts) * 100).toFixed(1) : "0",
      spreadBuckets,
      noFillReasons,
    };
  }, [pnlAllFiltered]);

  // Sortable P&L trade table
  const sortedPnlTrades = useMemo(() => {
    const trades = [...pnlAllFiltered];
    trades.sort((a, b) => {
      let cmp = 0;
      switch (tradeSortKey) {
        case "time":
          cmp = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          break;
        case "spread":
          cmp = a.spread_cents - b.spread_cents;
          break;
        case "net": {
          const aNet = tradePnl(a).totalDollars ?? 0;
          const bNet = tradePnl(b).totalDollars ?? 0;
          cmp = aNet - bNet;
          break;
        }
        case "qty":
          cmp = (a.contracts_intended || a.contracts_filled || 0) - (b.contracts_intended || b.contracts_filled || 0);
          break;
        case "phase":
          cmp = (a.execution_phase || "ioc").localeCompare(b.execution_phase || "ioc");
          break;
      }
      return tradeSortAsc ? cmp : -cmp;
    });
    return trades;
  }, [pnlAllFiltered, tradeSortKey, tradeSortAsc]);

  const handleSort = (key: TradeSortKey) => {
    if (tradeSortKey === key) {
      setTradeSortAsc(!tradeSortAsc);
    } else {
      setTradeSortKey(key);
      setTradeSortAsc(false);
    }
  };

  const sortArrow = (key: TradeSortKey) => {
    if (tradeSortKey !== key) return "";
    return tradeSortAsc ? " \u25B2" : " \u25BC";
  };

  // CSV export
  const exportCsv = useCallback(() => {
    const headers = ["Time", "Team", "Sport", "Direction", "Status", "Qty", "Spread", "Net P&L", "Phase", "Maker", "K Price", "PM Price"];
    const rows = sortedPnlTrades.map((t) => [
      t.timestamp,
      t.team,
      t.sport,
      t.direction,
      t.status,
      t.contracts_filled || 0,
      t.spread_cents,
      t.actual_pnl?.net_profit_dollars?.toFixed(4) ?? "",
      t.execution_phase || "ioc",
      t.is_maker ? "Y" : "N",
      t.k_price,
      t.pm_price,
    ]);
    const csv = [headers, ...rows].map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `arb_trades_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [sortedPnlTrades]);

  // ── Liquidity data ──────────────────────────────────────────────────
  const liq = state?.liquidity_stats;

  const filteredLiqGames = useMemo(() => {
    const games = liq?.per_game || [];
    if (!liqGameFilter.trim()) return games;
    const q = liqGameFilter.trim().toUpperCase();
    return games.filter((g) => g.game_id.toUpperCase().includes(q));
  }, [liq?.per_game, liqGameFilter]);

  // Spread history chart data — group by game+platform, pick latest game
  const liqChartGames = useMemo(() => {
    const games = new Set<string>();
    for (const s of liq?.spread_history || []) {
      games.add(s.game_id);
    }
    return Array.from(games).slice(0, 6);
  }, [liq?.spread_history]);

  const [liqChartGame, setLiqChartGame] = useState("");

  const liqSpreadChartData = useMemo(() => {
    const history = liq?.spread_history || [];
    const game = liqChartGame || liqChartGames[0] || "";
    if (!game) return [];
    return history
      .filter((s) => s.game_id === game)
      .map((s) => ({
        time: formatTimeOnly(s.timestamp),
        timestamp: s.timestamp,
        spread: s.spread,
        bid_depth: s.bid_depth,
        ask_depth: s.ask_depth,
        platform: s.platform,
      }));
  }, [liq?.spread_history, liqChartGame, liqChartGames]);

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-200">
      {/* Header */}
      <div className="border-b border-gray-800 bg-[#0f0f0f]">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-white">Arb Monitor</h1>
            <div className="flex items-center gap-2">
              <Pulse active={!!hasData && !isStale && !fetchError} />
              <span className="text-xs text-gray-500">
                {fetchError
                  ? "Connection error"
                  : isStale
                  ? "Stale data"
                  : hasData
                  ? `Updated ${timeAgo(state!.updated_at)}`
                  : "Waiting for data..."}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPaused(!paused)}
              className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                paused
                  ? "bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {paused ? "Paused" : "Pause"}
            </button>
            <button
              onClick={fetchData}
              className="rounded bg-gray-800 px-2.5 py-1 text-xs font-medium text-gray-400 hover:bg-gray-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
        {/* Top-level tabs */}
        <div className="flex px-4 gap-1">
          {(["monitor", "pnl_history", "liquidity"] as TopTab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setTopTab(tab)}
              className={`px-3 py-1.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
                topTab === tab
                  ? "border-emerald-500 text-white"
                  : "border-transparent text-gray-500 hover:text-gray-300"
              }`}
            >
              {tab === "monitor" ? "Monitor" : tab === "pnl_history" ? "P&L History" : "Liquidity"}
            </button>
          ))}
        </div>
      </div>

      {/* ══════════ MONITOR TAB ══════════ */}
      {topTab === "monitor" && (
        <div className="p-4 space-y-4">
          {/* ── Metrics Row ──────────────────────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {/* Column 1: Cash */}
            <div className="rounded-lg border border-gray-800 bg-[#111] px-3 py-2.5">
              <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500 mb-1.5">Cash (Trading)</p>
              <div className="space-y-1">
                <div className="flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400">PM</span>
                  <span className="text-sm font-mono text-white">{state?.balances.pm_cash != null ? `$${state.balances.pm_cash.toFixed(2)}` : "-"}</span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400">Kalshi</span>
                  <span className="text-sm font-mono text-white">{state?.balances.k_cash != null ? `$${state.balances.k_cash.toFixed(2)}` : "-"}</span>
                </div>
                <div className="border-t border-gray-800 pt-1 flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400 font-medium">Total</span>
                  <span className="text-base font-mono font-bold text-white">
                    {state?.balances.pm_cash != null && state?.balances.k_cash != null
                      ? `$${(state.balances.pm_cash + state.balances.k_cash).toFixed(2)}`
                      : "-"}
                  </span>
                </div>
              </div>
            </div>

            {/* Column 2: Positions (Mkt Value) — from actual open positions */}
            <div className="rounded-lg border border-gray-800 bg-[#111] px-3 py-2.5">
              <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500 mb-1.5">Positions (Mkt Value)</p>
              <div className="space-y-1">
                <div className="flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400">PM</span>
                  <span className="text-sm font-mono text-yellow-400">${positionValues.pm.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400">Kalshi</span>
                  <span className="text-sm font-mono text-yellow-400">${positionValues.kalshi.toFixed(2)}</span>
                </div>
                <div className="border-t border-gray-800 pt-1 flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400 font-medium">Total</span>
                  <span className="text-base font-mono font-bold text-yellow-400">${positionValues.total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Column 3: Portfolio */}
            <div className="rounded-lg border border-gray-800 bg-[#111] px-3 py-2.5">
              <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500 mb-1.5">Portfolio (Total)</p>
              <div className="space-y-1">
                <div className="flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400">PM</span>
                  <span className="text-sm font-mono text-white">
                    {state?.balances.pm_portfolio != null ? `$${state.balances.pm_portfolio.toFixed(2)}` : "-"}
                    {portfolioDelta.pm !== 0 && (
                      <span className={`ml-1 text-[10px] ${portfolioDelta.pm > 0 ? "text-emerald-400" : "text-red-400"}`}>
                        {portfolioDelta.pm > 0 ? "\u25B2" : "\u25BC"}{Math.abs(portfolioDelta.pm).toFixed(2)}
                      </span>
                    )}
                  </span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400">Kalshi</span>
                  <span className="text-sm font-mono text-white">
                    {state?.balances.k_portfolio != null ? `$${state.balances.k_portfolio.toFixed(2)}` : "-"}
                    {portfolioDelta.k !== 0 && (
                      <span className={`ml-1 text-[10px] ${portfolioDelta.k > 0 ? "text-emerald-400" : "text-red-400"}`}>
                        {portfolioDelta.k > 0 ? "\u25B2" : "\u25BC"}{Math.abs(portfolioDelta.k).toFixed(2)}
                      </span>
                    )}
                  </span>
                </div>
                <div className="border-t border-gray-800 pt-1 flex justify-between items-baseline">
                  <span className="text-[11px] text-gray-400 font-medium">Total</span>
                  <span className="text-base font-mono font-bold text-emerald-400">
                    {state?.balances.total_portfolio ? `$${state.balances.total_portfolio.toFixed(2)}` : "-"}
                    {portfolioDelta.total !== 0 && (
                      <span className={`ml-1 text-[10px] ${portfolioDelta.total > 0 ? "text-emerald-400" : "text-red-400"}`}>
                        {portfolioDelta.total > 0 ? "\u25B2" : "\u25BC"}{Math.abs(portfolioDelta.total).toFixed(2)}
                      </span>
                    )}
                  </span>
                </div>
              </div>
            </div>

            {/* Column 4: P&L + System */}
            <div className="grid grid-cols-2 gap-3">
              <MetricCard
                label="P&L"
                value={
                  pnl && pnl.total_trades > 0
                    ? `${pnl.total_pnl_dollars >= 0 ? "+$" : "-$"}${Math.abs(pnl.total_pnl_dollars).toFixed(2)}`
                    : "-"
                }
                sub={
                  pnl && pnl.total_trades > 0
                    ? `${pnl.profitable_count}W / ${pnl.losing_count}L · ${pnl.hedged_count} hedged`
                    : undefined
                }
                accent={
                  pnl && pnl.total_pnl_dollars > 0
                    ? "text-emerald-400"
                    : pnl && pnl.total_pnl_dollars < 0
                    ? "text-red-400"
                    : "text-white"
                }
              />
              <MetricCard
                label="Games"
                value={String(state?.system.games_monitored || 0)}
              />
              <MetricCard
                label="WS Messages"
                value={
                  (state?.system.ws_messages_processed || 0) > 1000
                    ? `${((state?.system.ws_messages_processed || 0) / 1000).toFixed(1)}k`
                    : String(state?.system.ws_messages_processed || 0)
                }
              />
              <MetricCard
                label="Uptime"
                value={formatUptime(state?.system.uptime_seconds || 0)}
                sub={state?.system.executor_version || ""}
              />
            </div>
          </div>

          {/* ── Error Banner ─────────────────────────────────────────── */}
          {state?.system.error_count ? (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 flex items-center gap-2">
              <span className="text-red-400 text-xs font-medium">
                {state.system.error_count} error
                {state.system.error_count > 1 ? "s" : ""}
              </span>
              {state.system.last_error && (
                <span className="text-red-400/70 text-xs truncate max-w-xl">
                  {state.system.last_error}
                </span>
              )}
            </div>
          ) : null}

          {/* ── Spreads (60%) + Trades (40%) ─────────────────────────── */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
            {/* Live Spreads */}
            <div
              className="lg:col-span-3 rounded-lg border border-gray-800 bg-[#111] flex flex-col"
              style={{ maxHeight: "440px" }}
            >
              <div className="flex items-center justify-between border-b border-gray-800 px-3 py-2 shrink-0">
                <h2 className="text-sm font-semibold text-white">
                  Live Spreads
                  <span className="ml-1.5 text-xs text-gray-500">
                    {sortedSpreads.length}
                    {!showAllSpreads &&
                      totalSpreadCount > sortedSpreads.length && (
                        <span>/{totalSpreadCount}</span>
                      )}
                  </span>
                </h2>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setShowAllSpreads(!showAllSpreads)}
                    className={`rounded px-2 py-0.5 text-[10px] font-medium transition-colors ${
                      showAllSpreads
                        ? "bg-gray-700 text-white"
                        : "bg-emerald-500/20 text-emerald-400"
                    }`}
                  >
                    {showAllSpreads ? "All" : "Opps only"}
                  </button>
                  <div className="flex items-center gap-2 text-[10px] text-gray-500">
                    <span className="flex items-center gap-0.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />{" "}
                      4c+
                    </span>
                    <span className="flex items-center gap-0.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-yellow-500" />{" "}
                      3-4c
                    </span>
                  </div>
                </div>
              </div>
              <div className="overflow-auto flex-1">
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-[#111] z-10">
                    <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
                      <th className="px-2 py-1.5">Game</th>
                      <th className="px-2 py-1.5">Team</th>
                      <th className="px-2 py-1.5 text-right">K Bid</th>
                      <th className="px-2 py-1.5 text-right">K Ask</th>
                      <th className="px-2 py-1.5 text-right">PM Bid</th>
                      <th className="px-2 py-1.5 text-right">PM Ask</th>
                      <th className="px-2 py-1.5 text-right">BUY_PM</th>
                      <th className="px-2 py-1.5 text-right">BUY_K</th>
                      <th className="px-2 py-1.5 text-right">Size</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedSpreads.length === 0 ? (
                      <tr>
                        <td
                          colSpan={9}
                          className="px-3 py-6 text-center text-gray-600 text-xs"
                        >
                          {hasData
                            ? showAllSpreads
                              ? "No spreads monitored"
                              : "No positive spreads"
                            : "Waiting for executor data..."}
                        </td>
                      </tr>
                    ) : (
                      sortedSpreads.map((s) => {
                        const best = Math.max(s.spread_buy_pm, s.spread_buy_k);
                        const today = isToday(s.game_date);
                        return (
                          <tr
                            key={`${s.game_id}-${s.team}`}
                            className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${spreadBg(best)}`}
                          >
                            <td className="px-2 py-1 text-white whitespace-nowrap">
                              <span className="font-medium">{s.game_id}</span>
                              {s.game_date && (
                                <span
                                  className={`ml-1 inline-block rounded px-0.5 text-[9px] font-medium ${
                                    today
                                      ? "bg-emerald-500/20 text-emerald-400"
                                      : "bg-gray-500/20 text-gray-500"
                                  }`}
                                >
                                  {today ? "LIVE" : s.game_date.slice(5)}
                                </span>
                              )}
                            </td>
                            <td className="px-2 py-1 font-mono">
                              <span
                                className={`inline-block rounded px-1 py-0.5 text-[10px] font-medium ${sportBadge(s.sport)}`}
                              >
                                {s.team}
                              </span>
                            </td>
                            <td className="px-2 py-1 text-right font-mono">
                              {s.k_bid}
                            </td>
                            <td className="px-2 py-1 text-right font-mono">
                              {s.k_ask}
                            </td>
                            <td className="px-2 py-1 text-right font-mono">
                              {s.pm_bid.toFixed(1)}
                            </td>
                            <td className="px-2 py-1 text-right font-mono">
                              {s.pm_ask.toFixed(1)}
                            </td>
                            <td
                              className={`px-2 py-1 text-right font-mono font-bold ${spreadColor(s.spread_buy_pm)}`}
                            >
                              {s.spread_buy_pm.toFixed(1)}
                            </td>
                            <td
                              className={`px-2 py-1 text-right font-mono font-bold ${spreadColor(s.spread_buy_k)}`}
                            >
                              {s.spread_buy_k.toFixed(1)}
                            </td>
                            <td className="px-2 py-1 text-right font-mono text-gray-500">
                              {s.pm_size}
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ── Trade Log ──────────────────────────────────────────── */}
            <div
              className="lg:col-span-2 rounded-lg border border-gray-800 bg-[#111] flex flex-col"
              style={{ maxHeight: "440px" }}
            >
              <div className="border-b border-gray-800 px-3 py-2 shrink-0 space-y-1.5">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-white">
                    Trades
                    <span className="ml-1.5 text-xs text-gray-500">
                      {filteredTrades.length}
                    </span>
                  </h2>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => {
                        setDateAll(false);
                        setDateOffset((d) => d - 1);
                      }}
                      className="text-gray-500 hover:text-gray-300 text-[10px] px-1"
                    >
                      &lt;
                    </button>
                    <button
                      onClick={() => {
                        setDateAll(false);
                        setDateOffset(0);
                      }}
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
                        !dateAll
                          ? "bg-gray-700 text-white"
                          : "text-gray-500 hover:text-gray-300"
                      }`}
                    >
                      {dateLabel}
                    </button>
                    <button
                      onClick={() => {
                        setDateAll(false);
                        setDateOffset((d) => Math.min(d + 1, 0));
                      }}
                      className="text-gray-500 hover:text-gray-300 text-[10px] px-1"
                      disabled={dateOffset >= 0 && !dateAll}
                    >
                      &gt;
                    </button>
                    <FilterButton
                      active={dateAll}
                      onClick={() => setDateAll(!dateAll)}
                    >
                      All
                    </FilterButton>
                    <span className="text-gray-700">|</span>
                    {(["all", "live", "paper"] as TradeFilter[]).map((f) => (
                      <FilterButton
                        key={f}
                        active={tradeFilter === f}
                        onClick={() => setTradeFilter(f)}
                        variant={
                          f === "live"
                            ? "green"
                            : f === "paper"
                            ? "purple"
                            : "default"
                        }
                      >
                        {f === "all" ? "All" : f === "live" ? "Live" : "Paper"}
                      </FilterButton>
                    ))}
                  </div>
                </div>
                {/* Status filter + search */}
                <div className="flex items-center gap-1.5">
                  {(
                    [
                      "all",
                      "SUCCESS",
                      "PM_NO_FILL",
                      "EXITED",
                      "UNHEDGED",
                      "SKIPPED",
                    ] as StatusFilter[]
                  ).map((f) => (
                    <FilterButton
                      key={f}
                      active={statusFilter === f}
                      onClick={() => setStatusFilter(f)}
                      variant={
                        f === "SUCCESS"
                          ? "green"
                          : f === "PM_NO_FILL" || f === "EXITED"
                          ? "yellow"
                          : f === "UNHEDGED"
                          ? "red"
                          : "default"
                      }
                    >
                      {f === "all" ? "Any Status" : f}
                    </FilterButton>
                  ))}
                  <input
                    type="text"
                    placeholder="Search team..."
                    value={tradeSearch}
                    onChange={(e) => setTradeSearch(e.target.value)}
                    className="ml-auto w-20 rounded bg-gray-800 px-1.5 py-0.5 text-[10px] text-gray-300 placeholder-gray-600 border border-gray-700 focus:border-gray-500 focus:outline-none"
                  />
                </div>
                {/* Summary */}
                {filteredTrades.length > 0 && (
                  <div className="flex items-center gap-3 text-[10px] text-gray-500 pt-0.5">
                    <span>
                      {filteredPnl.successes} success
                      {filteredPnl.successes !== 1 ? "es" : ""}
                    </span>
                    <span>{filteredPnl.fills} filled</span>
                    <span
                      className={
                        filteredPnl.netTotal > 0
                          ? "text-emerald-400"
                          : filteredPnl.netTotal < 0
                          ? "text-red-400"
                          : "text-gray-500"
                      }
                    >
                      P&L:{" "}
                      {filteredPnl.exitedLoss !== 0 ? (
                        <>
                          <span className="text-emerald-400">+${filteredPnl.successPnl.toFixed(2)}</span>
                          {" "}
                          <span className="text-red-400">{filteredPnl.exitedLoss >= 0 ? "+" : ""}${filteredPnl.exitedLoss.toFixed(2)}</span>
                          {" = "}
                        </>
                      ) : null}
                      {filteredPnl.netTotal >= 0 ? "+" : ""}$
                      {filteredPnl.netTotal.toFixed(2)}
                    </span>
                  </div>
                )}
              </div>
              <div className="overflow-auto flex-1">
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-[#111] z-10">
                    <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
                      <th className="px-2 py-1.5">Time</th>
                      <th className="px-2 py-1.5">Game</th>
                      <th className="px-2 py-1.5 text-right">Qty</th>
                      <th className="px-2 py-1.5 text-right">Spread</th>
                      <th className="px-2 py-1.5 text-right">Net</th>
                      <th className="px-2 py-1.5">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTrades.length === 0 ? (
                      <tr>
                        <td
                          colSpan={6}
                          className="px-3 py-6 text-center text-gray-600 text-xs"
                        >
                          No trades{" "}
                          {selectedDate
                            ? dateOffset === 0
                              ? "today"
                              : `on ${formatDateLabel(selectedDate)}`
                            : "recorded"}
                        </td>
                      </tr>
                    ) : (
                      filteredTrades.map((t, i) => {
                        const badge = statusBadge(t.status);
                        const isMonExpanded = expandedMonitorTrade === i;
                        return (
                          <React.Fragment key={`${t.timestamp}-${i}`}>
                          <tr
                            className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors cursor-pointer ${isMonExpanded ? "bg-gray-800/20" : ""}`}
                            onClick={() => setExpandedMonitorTrade(isMonExpanded ? null : i)}
                          >
                            <td className="px-2 py-1 font-mono text-gray-400 whitespace-nowrap text-[10px]">
                              {formatDateTime(t.timestamp)}
                            </td>
                            <td className="px-2 py-1 whitespace-nowrap">
                              <span className="text-white font-medium">
                                {t.team}
                              </span>
                              <span
                                className={`ml-1 inline-block rounded px-0.5 text-[9px] font-medium ${sportBadge(t.sport)}`}
                              >
                                {t.sport}
                              </span>
                              {t.paper_mode && (
                                <span className="ml-0.5 text-[9px] text-purple-400">
                                  P
                                </span>
                              )}
                              {t.execution_phase === "gtc" && (
                                <span className="ml-0.5 text-[9px] text-blue-400">
                                  G
                                </span>
                              )}
                              {t.is_maker && (
                                <span className="ml-0.5 text-[9px] text-cyan-400">
                                  M
                                </span>
                              )}
                            </td>
                            <td
                              className={`px-2 py-1 text-right font-mono ${
                                (t.contracts_intended || t.contracts_filled || 1) > 1
                                  ? "text-white font-bold"
                                  : "text-gray-500"
                              }`}
                              title={
                                t.sizing_details
                                  ? `Depth: K=${t.sizing_details.k_depth} PM=${t.sizing_details.pm_depth} | Est: ${(t.sizing_details.expected_profit_cents / 100).toFixed(2)} | Limit: ${t.sizing_details.limit_reason}`
                                  : undefined
                              }
                            >
                              {t.contracts_intended && t.contracts_intended !== t.contracts_filled
                                ? <>{t.contracts_filled}<span className="text-gray-600">/{t.contracts_intended}</span></>
                                : (t.contracts_intended ?? t.contracts_filled ?? 1)}
                            </td>
                            <td
                              className={`px-2 py-1 text-right font-mono ${spreadColor(t.spread_cents)}`}
                            >
                              {t.spread_cents.toFixed(1)}
                            </td>
                            {(() => {
                              const pnl = tradePnl(t);
                              return (
                                <td className={`px-2 py-1 text-right font-mono font-medium ${netColor(pnl.perContract)}`}>
                                  {pnl.perContract != null ? (
                                    <div>
                                      <span>{pnl.perContract >= 0 ? "+" : ""}{pnl.perContract.toFixed(1)}c</span>
                                      {pnl.totalDollars != null && pnl.qty > 1 && (
                                        <div className="text-[9px] text-gray-500">
                                          ({pnl.totalDollars >= 0 ? "+$" : "-$"}{Math.abs(pnl.totalDollars).toFixed(2)})
                                        </div>
                                      )}
                                    </div>
                                  ) : "-"}
                                </td>
                              );
                            })()}
                            <td className="px-2 py-1">
                              <span
                                className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${badge.bg} ${badge.text}`}
                              >
                                {t.status}
                              </span>
                              {t.hedged && (
                                <span className="ml-0.5 text-emerald-400 text-[9px]">
                                  H
                                </span>
                              )}
                            </td>
                          </tr>
                          {isMonExpanded && (
                            <tr className="bg-gray-800/10">
                              <td colSpan={6} className="px-4 py-2">
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[10px]">
                                  <div>
                                    <span className="text-gray-500">Direction:</span>{" "}
                                    <span className="text-white">{t.direction}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Game ID:</span>{" "}
                                    <span className="text-white font-mono">{t.game_id}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Phase:</span>{" "}
                                    <span className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${
                                      (t.execution_phase || "ioc") === "gtc"
                                        ? "bg-blue-500/20 text-blue-400"
                                        : "bg-gray-500/20 text-gray-500"
                                    }`}>
                                      {(t.execution_phase || "ioc").toUpperCase()}
                                    </span>
                                    {t.is_maker && <span className="ml-1 text-cyan-400">(MAKER)</span>}
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Timing:</span>{" "}
                                    <span className="text-white">
                                      pm={t.pm_order_ms ?? 0}ms
                                      {(t.execution_time_ms ?? 0) > 0 && <> total={t.execution_time_ms}ms</>}
                                    </span>
                                  </div>
                                  {(t.gtc_rest_time_ms ?? 0) > 0 && (
                                    <div>
                                      <span className="text-gray-500">GTC Rest:</span>{" "}
                                      <span className="text-blue-400">{t.gtc_rest_time_ms}ms ({t.gtc_spread_checks} checks)</span>
                                    </div>
                                  )}
                                  {t.gtc_cancel_reason ? (
                                    <div>
                                      <span className="text-gray-500">GTC Cancel:</span>{" "}
                                      <span className="text-yellow-400">{t.gtc_cancel_reason}</span>
                                    </div>
                                  ) : null}
                                  {t.actual_pnl && (
                                    <>
                                      <div>
                                        <span className="text-gray-500">Gross:</span>{" "}
                                        <span className="text-white">${t.actual_pnl.gross_profit_dollars.toFixed(4)}</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Fees:</span>{" "}
                                        <span className="text-red-400">${t.actual_pnl.fees_dollars.toFixed(4)}</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Total Cost:</span>{" "}
                                        <span className="text-white">${t.actual_pnl.total_cost_dollars.toFixed(4)}</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Net:</span>{" "}
                                        <span className={t.actual_pnl.is_profitable ? "text-emerald-400" : "text-red-400"}>
                                          ${t.actual_pnl.net_profit_dollars.toFixed(4)}
                                        </span>
                                      </div>
                                    </>
                                  )}
                                  {t.sizing_details && (
                                    <div>
                                      <span className="text-gray-500">Sizing:</span>{" "}
                                      <span className="text-gray-300">K={t.sizing_details.k_depth} PM={t.sizing_details.pm_depth} ({t.sizing_details.limit_reason})</span>
                                    </div>
                                  )}
                                  <div>
                                    <span className="text-gray-500">Prices:</span>{" "}
                                    <span className="text-gray-300">K={t.k_price}c PM={t.pm_price}c</span>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                          </React.Fragment>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* ── Bottom Tabs: Positions / Mapped Games ────────────────── */}
          <div className="rounded-lg border border-gray-800 bg-[#111]">
            <div className="flex items-center border-b border-gray-800 px-3">
              <button
                onClick={() => setBottomTab("positions")}
                className={`px-3 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                  bottomTab === "positions"
                    ? "border-emerald-500 text-white"
                    : "border-transparent text-gray-500 hover:text-gray-300"
                }`}
              >
                Open Positions
                {activePositions.length > 0 && (
                  <span className="ml-1 text-xs text-gray-500">
                    {activePositions.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setBottomTab("mapped_games")}
                className={`px-3 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                  bottomTab === "mapped_games"
                    ? "border-emerald-500 text-white"
                    : "border-transparent text-gray-500 hover:text-gray-300"
                }`}
              >
                Mapped Games
                {mappedGames.length > 0 && (
                  <span className="ml-1 text-xs text-gray-500">
                    {mappedGames.length}
                  </span>
                )}
              </button>
              {bottomTab === "mapped_games" &&
                state?.mappings_last_refreshed && (
                  <div className="ml-auto flex items-center gap-1.5 text-[10px] text-gray-500">
                    <span
                      className={`inline-block h-2 w-2 rounded-full ${mappingsHealthColor(state.mappings_last_refreshed)}`}
                    />
                    <span>
                      Last refreshed:{" "}
                      {timeAgo(state.mappings_last_refreshed)}
                    </span>
                  </div>
                )}
            </div>

            {/* ── Open Positions ──────────────────────────────────── */}
            {bottomTab === "positions" && (
              <div>
                {activePositions.length === 0 ? (
                  <div className="text-center py-6">
                    <span className="text-xs text-gray-600">
                      No open positions
                    </span>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-800/50">
                    {unhedgedPositions.map((p, i) => (
                      <div
                        key={`uh-${i}`}
                        className="px-4 py-3 border-l-2 border-red-500 bg-red-500/5"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-white font-medium text-xs">
                              {p.team || p.game_id}
                            </span>
                            <span
                              className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${sportBadge(p.sport)}`}
                            >
                              {p.sport}
                            </span>
                            {p.trade_timestamp && (
                              <span className="text-[9px] text-gray-600">
                                {timeAgo(p.trade_timestamp)}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-[9px] font-medium rounded px-1.5 py-0.5 bg-red-500/20 text-red-400">
                              UNHEDGED
                            </span>
                            <button
                              onClick={() => markSettled(p.game_id)}
                              className="text-[9px] text-gray-600 hover:text-gray-400 px-1"
                              title="Hide this position (mark as settled)"
                            >
                              Mark Settled
                            </button>
                          </div>
                        </div>
                        <div className="mt-1.5 flex items-center gap-3 text-[11px]">
                          <span className="text-gray-400">
                            {p.platform}: {p.side} x{p.quantity}
                          </span>
                          {p.avg_price > 0 && (
                            <span className="text-gray-500">
                              @{p.avg_price}c
                            </span>
                          )}
                          <span className="text-red-400/80 text-[10px]">
                            Exposure: $
                            {(
                              ((p.avg_price || 50) * p.quantity) /
                              100
                            ).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}

                    {hedgedPositions.map((p, i) => {
                      const dir = p.direction || "";
                      const hasFillData =
                        (p.pm_fill_price ?? 0) > 0 ||
                        (p.k_fill_price ?? 0) > 0;
                      const pmDir =
                        dir === "BUY_PM_SELL_K"
                          ? "LONG"
                          : dir === "BUY_K_SELL_PM"
                          ? "SHORT"
                          : "";
                      const kDir =
                        dir === "BUY_PM_SELL_K"
                          ? "SHORT"
                          : dir === "BUY_K_SELL_PM"
                          ? "LONG"
                          : "";
                      const locked = p.locked_profit_cents ?? 0;
                      const netProfit = p.net_profit_cents ?? 0;
                      const pmFill = p.pm_fill_price ?? 0;
                      const kFill = p.k_fill_price ?? 0;
                      const qty = p.contracts || p.quantity || 0;

                      return (
                        <div
                          key={`h-${i}`}
                          className="px-4 py-3 border-l-2 border-emerald-500"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-white font-medium text-xs">
                                {p.team || p.game_id}
                              </span>
                              <span
                                className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${sportBadge(p.sport)}`}
                              >
                                {p.sport}
                              </span>
                              {p.trade_timestamp && (
                                <span className="text-[9px] text-gray-600">
                                  {timeAgo(p.trade_timestamp)}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-2">
                              {hasFillData && (
                                <span
                                  className={`text-[10px] font-mono font-bold ${
                                    netProfit > 0
                                      ? "text-emerald-400"
                                      : netProfit < 0
                                      ? "text-red-400"
                                      : "text-gray-400"
                                  }`}
                                >
                                  {netProfit >= 0 ? "+" : ""}
                                  {netProfit.toFixed(1)}c net
                                </span>
                              )}
                              <span className="text-[9px] font-medium rounded px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400">
                                HEDGED
                              </span>
                              <button
                                onClick={() => markSettled(p.game_id)}
                                className="text-[9px] text-gray-600 hover:text-gray-400 px-1"
                                title="Hide this position (mark as settled)"
                              >
                                Mark Settled
                              </button>
                            </div>
                          </div>

                          {hasFillData ? (
                            <div className="mt-2 grid grid-cols-2 gap-3">
                              <div className="rounded bg-blue-500/5 border border-blue-500/20 px-2.5 py-1.5">
                                <div className="text-[9px] text-blue-400 font-medium mb-0.5">
                                  PM LEG
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-[11px] font-mono text-blue-300">
                                    {pmDir} x{qty}
                                  </span>
                                  <span className="text-[11px] font-mono text-white">
                                    @{pmFill.toFixed(1)}c
                                  </span>
                                </div>
                              </div>
                              <div className="rounded bg-orange-500/5 border border-orange-500/20 px-2.5 py-1.5">
                                <div className="text-[9px] text-orange-400 font-medium mb-0.5">
                                  KALSHI LEG
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-[11px] font-mono text-orange-300">
                                    {kDir} x{qty}
                                  </span>
                                  <span className="text-[11px] font-mono text-white">
                                    @{kFill.toFixed(1)}c
                                  </span>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="mt-1 flex items-center gap-2 text-[10px] text-gray-400">
                              <span>
                                {p.side} x{p.quantity}
                              </span>
                              {p.avg_price > 0 && (
                                <span>PM@{p.avg_price}c</span>
                              )}
                              {p.current_value > 0 && (
                                <span>K@{p.current_value}c</span>
                              )}
                            </div>
                          )}

                          {hasFillData && (() => {
                            const feesPerContract = 2.0;
                            const netPerContract = locked - feesPerContract;
                            const totalPnlDollars = (netPerContract * qty) / 100;
                            return (
                              <div className="mt-1.5 space-y-0.5">
                                <div className="flex items-center gap-3 text-[10px]">
                                  <span
                                    className={`font-mono font-bold ${
                                      locked > 0
                                        ? "text-emerald-400"
                                        : locked < 0
                                        ? "text-red-400"
                                        : "text-gray-400"
                                    }`}
                                  >
                                    Locked: {locked >= 0 ? "+" : ""}
                                    {locked.toFixed(1)}c gross
                                  </span>
                                  <span className="text-gray-600">
                                    ({pmFill.toFixed(1)} + {kFill.toFixed(1)} ={" "}
                                    {(pmFill + kFill).toFixed(1)}c cost)
                                  </span>
                                </div>
                                <div className="flex items-center gap-3 text-[10px]">
                                  <span
                                    className={`font-mono font-bold ${
                                      netPerContract > 0
                                        ? "text-emerald-400"
                                        : netPerContract < 0
                                        ? "text-red-400"
                                        : "text-gray-400"
                                    }`}
                                  >
                                    {netPerContract >= 0 ? "+" : ""}{netPerContract.toFixed(1)}c net/contract
                                  </span>
                                  <span
                                    className={`font-mono font-bold ${
                                      totalPnlDollars > 0
                                        ? "text-emerald-400"
                                        : totalPnlDollars < 0
                                        ? "text-red-400"
                                        : "text-gray-400"
                                    }`}
                                  >
                                    {totalPnlDollars >= 0 ? "+" : ""}${totalPnlDollars.toFixed(3)} total ({qty}x)
                                  </span>
                                </div>
                              </div>
                            );
                          })()}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ── Mapped Games ───────────────────────────────────── */}
            {bottomTab === "mapped_games" && (
              <div>
                {mappedGames.length === 0 ? (
                  <div className="text-center py-6">
                    <span className="text-xs text-gray-600">
                      No mapped games data — waiting for executor push
                    </span>
                  </div>
                ) : (
                  <div
                    className="overflow-auto"
                    style={{ maxHeight: "400px" }}
                  >
                    <table className="w-full text-xs">
                      <thead className="sticky top-0 bg-[#111] z-10">
                        <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
                          <th className="px-2 py-1.5">Game</th>
                          <th className="px-2 py-1.5">Sport</th>
                          <th className="px-2 py-1.5">Date</th>
                          <th className="px-2 py-1.5">Status</th>
                          <th className="px-2 py-1.5 text-right">
                            Best Spread
                          </th>
                          <th className="px-2 py-1.5">Traded</th>
                          <th className="px-2 py-1.5">PM Slug</th>
                        </tr>
                      </thead>
                      <tbody>
                        {mappedGames.map((g) => {
                          const today = isToday(g.date);
                          return (
                            <tr
                              key={g.cache_key}
                              className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${
                                g.traded ? "bg-emerald-500/5" : ""
                              }`}
                            >
                              <td className="px-2 py-1.5 whitespace-nowrap">
                                <span className="text-white font-medium">
                                  {g.team1}
                                </span>
                                <span className="text-gray-600 mx-1">vs</span>
                                <span className="text-white font-medium">
                                  {g.team2}
                                </span>
                              </td>
                              <td className="px-2 py-1.5">
                                <span
                                  className={`inline-block rounded px-1 py-0.5 text-[10px] font-medium ${sportBadge(g.sport)}`}
                                >
                                  {g.sport}
                                </span>
                              </td>
                              <td className="px-2 py-1.5 font-mono text-gray-400">
                                {today ? (
                                  <span className="text-emerald-400">
                                    Today
                                  </span>
                                ) : (
                                  g.date.slice(5)
                                )}
                              </td>
                              <td className="px-2 py-1.5">
                                <span
                                  className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${
                                    g.status === "Active"
                                      ? "bg-emerald-500/20 text-emerald-400"
                                      : "bg-gray-500/20 text-gray-500"
                                  }`}
                                >
                                  {g.status}
                                </span>
                              </td>
                              <td
                                className={`px-2 py-1.5 text-right font-mono font-bold ${spreadColor(g.best_spread)}`}
                              >
                                {g.best_spread > 0
                                  ? g.best_spread.toFixed(1)
                                  : "-"}
                              </td>
                              <td className="px-2 py-1.5">
                                {g.traded ? (
                                  <span className="text-emerald-400 text-[9px] font-medium">
                                    YES
                                  </span>
                                ) : (
                                  <span className="text-gray-600 text-[9px]">
                                    -
                                  </span>
                                )}
                              </td>
                              <td className="px-2 py-1.5 text-[9px] text-gray-600 font-mono truncate max-w-[160px]">
                                {g.pm_slug}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ── Footer ──────────────────────────────────────────────── */}
          <div className="rounded-lg border border-gray-800 bg-[#111] px-3 py-2">
            <div className="flex flex-wrap items-center gap-x-5 gap-y-1 text-[10px] text-gray-500">
              <div className="flex items-center gap-1.5">
                <span className="font-medium text-gray-400">WS</span>
                <Pulse active={state?.system.ws_connected ?? false} />
                <span>
                  {state?.system.ws_connected ? "Connected" : "Disconnected"}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-400">Scan</span>{" "}
                {state?.system.last_scan_at
                  ? timeAgo(state.system.last_scan_at)
                  : "-"}
              </div>
              <div>
                <span className="font-medium text-gray-400">Errors</span>{" "}
                <span
                  className={
                    (state?.system.error_count || 0) > 0
                      ? "text-red-400"
                      : "text-gray-500"
                  }
                >
                  {state?.system.error_count || 0}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-400">Poll</span>{" "}
                {lastFetch ? `${timeAgo(lastFetch.toISOString())}` : "-"}
                {paused && " (paused)"}
              </div>
              <div>
                <span className="font-medium text-gray-400">Ver</span>{" "}
                {state?.system.executor_version || "-"}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ══════════ P&L HISTORY TAB ══════════ */}
      {topTab === "pnl_history" && (
        <div className="p-4 space-y-4">
          {/* ── Filters ──────────────────────────────────────────── */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1">
              {(["1D", "1W", "1M", "YTD", "ALL"] as TimeHorizon[]).map(
                (h) => (
                  <button
                    key={h}
                    onClick={() => setPnlHorizon(h)}
                    className={`rounded px-2 py-1 text-xs font-medium transition-colors ${
                      pnlHorizon === h
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "bg-gray-800 text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    {h}
                  </button>
                )
              )}
            </div>
            <span className="text-gray-700">|</span>
            <div className="flex items-center gap-1">
              {availableSports.map((s) => (
                <button
                  key={s}
                  onClick={() => setPnlSport(s)}
                  className={`rounded px-2 py-1 text-xs font-medium transition-colors ${
                    pnlSport === s
                      ? "bg-blue-500/20 text-blue-400"
                      : "bg-gray-800 text-gray-500 hover:text-gray-300"
                  }`}
                >
                  {s === "all" ? "All Sports" : s}
                </button>
              ))}
            </div>
          </div>

          {/* ── Summary Stats ────────────────────────────────────── */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-10 gap-3">
            <MetricCard
              label="Total P&L"
              value={`${pnlSummaryStats.totalPnl >= 0 ? "+$" : "-$"}${Math.abs(pnlSummaryStats.totalPnl).toFixed(2)}`}
              accent={
                pnlSummaryStats.totalPnl > 0
                  ? "text-emerald-400"
                  : pnlSummaryStats.totalPnl < 0
                  ? "text-red-400"
                  : "text-white"
              }
            />
            <MetricCard
              label="Trades"
              value={String(pnlSummaryStats.totalTrades)}
              sub={`of ${pnlSummaryStats.totalAttempts} attempts`}
            />
            <MetricCard
              label="Win Rate"
              value={`${pnlSummaryStats.winRate}%`}
              sub={`${pnlSummaryStats.wins}W / ${pnlSummaryStats.losses}L`}
              accent={
                Number(pnlSummaryStats.winRate) > 50
                  ? "text-emerald-400"
                  : Number(pnlSummaryStats.winRate) < 50
                  ? "text-red-400"
                  : "text-white"
              }
            />
            <MetricCard
              label="Total Contracts"
              value={String(pnlSummaryStats.totalContracts)}
            />
            <MetricCard
              label="Avg Profit"
              value={`${pnlSummaryStats.avgProfit >= 0 ? "+$" : "-$"}${Math.abs(pnlSummaryStats.avgProfit).toFixed(4)}`}
              accent={
                pnlSummaryStats.avgProfit > 0
                  ? "text-emerald-400"
                  : pnlSummaryStats.avgProfit < 0
                  ? "text-red-400"
                  : "text-white"
              }
            />
            <MetricCard
              label="Best Trade"
              value={`+$${pnlSummaryStats.best.toFixed(4)}`}
              accent="text-emerald-400"
            />
            <MetricCard
              label="Worst Trade"
              value={`${pnlSummaryStats.worst >= 0 ? "+$" : "-$"}${Math.abs(pnlSummaryStats.worst).toFixed(4)}`}
              accent="text-red-400"
            />
            <MetricCard
              label="Maker Fills"
              value={String(pnlSummaryStats.makerFills)}
              sub={`${pnlSummaryStats.totalTrades > 0 ? ((pnlSummaryStats.makerFills / pnlSummaryStats.totalTrades) * 100).toFixed(0) : 0}% of trades`}
              accent="text-cyan-400"
            />
            <MetricCard
              label="GTC Fill Rate"
              value={`${pnlSummaryStats.gtcFillRate}%`}
              sub={`${pnlSummaryStats.gtcFills}/${pnlSummaryStats.gtcAttempts} attempts`}
              accent="text-blue-400"
            />
            <MetricCard
              label="PM No-Fills"
              value={String(pnlSummaryStats.noFills)}
            />
          </div>

          {/* ── Charts Row: Cumulative + Scatter ───────────────────── */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Cumulative P&L Line Chart */}
            <div className="rounded-lg border border-gray-800 bg-[#111] p-4">
              <h3 className="text-sm font-semibold text-white mb-3">
                Cumulative P&L
              </h3>
              {cumulativeChartData.length === 0 ? (
                <div className="text-center py-8 text-xs text-gray-600">
                  No P&L data for selected filters
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <LineChart data={cumulativeChartData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#1f2937"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="index"
                      stroke="#4b5563"
                      fontSize={10}
                      label={{ value: "Trade #", position: "insideBottom", offset: -2, fontSize: 10, fill: "#6b7280" }}
                    />
                    <YAxis
                      stroke="#4b5563"
                      fontSize={10}
                      tickFormatter={(v: number) => `$${v.toFixed(2)}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#111",
                        border: "1px solid #374151",
                        borderRadius: "6px",
                        fontSize: "11px",
                      }}
                      formatter={(value: number | undefined, name: string | undefined) => {
                        const v = value ?? 0;
                        if (name === "pnl")
                          return [`$${v.toFixed(4)}`, "Cumulative"];
                        return [v, name ?? ""];
                      }}
                      labelFormatter={(label) => `Trade #${label}`}
                    />
                    <ReferenceLine y={0} stroke="#374151" strokeDasharray="3 3" />
                    <Line
                      type="monotone"
                      dataKey="pnl"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4, fill: "#10b981" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Per-Trade Scatter Plot */}
            <div className="rounded-lg border border-gray-800 bg-[#111] p-4">
              <h3 className="text-sm font-semibold text-white mb-3">
                Per-Trade P&L
                <span className="ml-2 text-[10px] text-gray-500 font-normal">
                  (size = contracts)
                </span>
              </h3>
              {scatterData.length === 0 ? (
                <div className="text-center py-8 text-xs text-gray-600">
                  No trade data for selected filters
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <ScatterChart>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#1f2937"
                    />
                    <XAxis
                      dataKey="spread"
                      stroke="#4b5563"
                      fontSize={10}
                      name="Spread"
                      label={{ value: "Spread (c)", position: "insideBottom", offset: -2, fontSize: 10, fill: "#6b7280" }}
                    />
                    <YAxis
                      dataKey="net"
                      stroke="#4b5563"
                      fontSize={10}
                      name="Net P&L"
                      tickFormatter={(v: number) => `$${v.toFixed(3)}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#111",
                        border: "1px solid #374151",
                        borderRadius: "6px",
                        fontSize: "11px",
                      }}
                      formatter={(value: number | undefined, name: string | undefined) => {
                        const v = value ?? 0;
                        if (name === "Net P&L") return [`$${v.toFixed(4)}`, name];
                        if (name === "Spread") return [`${v.toFixed(1)}c`, name];
                        return [v, name ?? ""];
                      }}
                    />
                    <ReferenceLine y={0} stroke="#374151" strokeDasharray="3 3" />
                    <Scatter data={scatterData} fill="#10b981">
                      {scatterData.map((entry, index) => (
                        <Cell
                          key={`sc-${index}`}
                          fill={entry.net >= 0 ? "#10b981" : "#ef4444"}
                          fillOpacity={entry.isMaker ? 1 : 0.6}
                          r={Math.max(3, Math.min(entry.contracts * 2, 10))}
                        />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* ── Fill Rate Analytics ────────────────────────────────── */}
          <div className="rounded-lg border border-gray-800 bg-[#111] p-4">
            <h3 className="text-sm font-semibold text-white mb-3">
              Fill Rate Analytics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* IOC vs GTC */}
              <div className="space-y-2">
                <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500">IOC vs GTC Breakdown</p>
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">IOC</span>
                    <span className="font-mono text-white">{fillRateStats.iocFills}/{fillRateStats.iocAttempts} ({fillRateStats.iocRate}%)</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-800 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${fillRateStats.iocRate}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">GTC</span>
                    <span className="font-mono text-white">{fillRateStats.gtcFills}/{fillRateStats.gtcAttempts} ({fillRateStats.gtcRate}%)</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-800 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-blue-500"
                      style={{ width: `${fillRateStats.gtcRate}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* By Spread Bucket */}
              <div className="space-y-2">
                <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500">Fill Rate by Spread</p>
                <div className="space-y-1">
                  {["<3c", "3-4c", "4-5c", "5c+"].map((bucket) => {
                    const data = fillRateStats.spreadBuckets[bucket] || { attempts: 0, fills: 0 };
                    const rate = data.attempts > 0 ? ((data.fills / data.attempts) * 100).toFixed(0) : "0";
                    return (
                      <div key={bucket} className="flex items-center justify-between text-xs">
                        <span className="text-gray-400 w-10">{bucket}</span>
                        <div className="flex-1 mx-2 h-1.5 rounded-full bg-gray-800 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-emerald-500/70"
                            style={{ width: `${rate}%` }}
                          />
                        </div>
                        <span className="font-mono text-gray-300 text-[10px] w-16 text-right">
                          {data.fills}/{data.attempts} ({rate}%)
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* No-Fill Reasons */}
              <div className="space-y-2">
                <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500">No-Fill Reasons</p>
                <div className="space-y-1">
                  {Object.entries(fillRateStats.noFillReasons).length === 0 ? (
                    <span className="text-xs text-gray-600">No no-fills recorded</span>
                  ) : (
                    Object.entries(fillRateStats.noFillReasons)
                      .sort(([, a], [, b]) => b - a)
                      .map(([reason, count]) => (
                        <div key={reason} className="flex items-center justify-between text-xs">
                          <span className="text-gray-400 truncate max-w-[120px]">{reason}</span>
                          <span className="font-mono text-yellow-400">{count}</span>
                        </div>
                      ))
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* ── Daily P&L Bar Chart ──────────────────────────────── */}
          <div className="rounded-lg border border-gray-800 bg-[#111] p-4">
            <h3 className="text-sm font-semibold text-white mb-3">
              Daily P&L
            </h3>
            {dailyPnlData.length === 0 ? (
              <div className="text-center py-8 text-xs text-gray-600">
                No daily data for selected filters
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={dailyPnlData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#1f2937"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="label"
                    stroke="#4b5563"
                    fontSize={10}
                  />
                  <YAxis
                    stroke="#4b5563"
                    fontSize={10}
                    tickFormatter={(v: number) => `$${v.toFixed(2)}`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#111",
                      border: "1px solid #374151",
                      borderRadius: "6px",
                      fontSize: "11px",
                    }}
                    formatter={(value: number | undefined) => [
                      `$${(value ?? 0).toFixed(4)}`,
                      "Net P&L",
                    ]}
                  />
                  <ReferenceLine y={0} stroke="#374151" strokeDasharray="3 3" />
                  <Bar dataKey="pnl" radius={[3, 3, 0, 0]}>
                    {dailyPnlData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.pnl >= 0 ? "#10b981" : "#ef4444"}
                        fillOpacity={0.8}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* ── Trade Details Table ────────────────────────────────── */}
          <div className="rounded-lg border border-gray-800 bg-[#111]">
            <div className="border-b border-gray-800 px-3 py-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Trade Details
                <span className="ml-1.5 text-xs text-gray-500">{sortedPnlTrades.length}</span>
              </h3>
              <button
                onClick={exportCsv}
                className="rounded bg-gray-800 px-2 py-1 text-[10px] font-medium text-gray-400 hover:bg-gray-700 transition-colors"
              >
                Export CSV
              </button>
            </div>
            <div className="overflow-auto" style={{ maxHeight: "400px" }}>
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-[#111] z-10">
                  <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
                    <th className="px-2 py-1.5 cursor-pointer hover:text-gray-300" onClick={() => handleSort("time")}>
                      Time{sortArrow("time")}
                    </th>
                    <th className="px-2 py-1.5">Team</th>
                    <th className="px-2 py-1.5">Status</th>
                    <th className="px-2 py-1.5 text-right cursor-pointer hover:text-gray-300" onClick={() => handleSort("qty")}>
                      Qty{sortArrow("qty")}
                    </th>
                    <th className="px-2 py-1.5 text-right cursor-pointer hover:text-gray-300" onClick={() => handleSort("spread")}>
                      Spread{sortArrow("spread")}
                    </th>
                    <th className="px-2 py-1.5 text-right cursor-pointer hover:text-gray-300" onClick={() => handleSort("net")}>
                      Net P&L{sortArrow("net")}
                    </th>
                    <th className="px-2 py-1.5 text-center cursor-pointer hover:text-gray-300" onClick={() => handleSort("phase")}>
                      Phase{sortArrow("phase")}
                    </th>
                    <th className="px-2 py-1.5 text-center">Maker</th>
                    <th className="px-2 py-1.5 text-right">K/PM</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedPnlTrades.length === 0 ? (
                    <tr>
                      <td
                        colSpan={9}
                        className="px-3 py-6 text-center text-gray-600"
                      >
                        No data
                      </td>
                    </tr>
                  ) : (
                    sortedPnlTrades.map((t, i) => {
                      const badge = statusBadge(t.status);
                      const isExpanded = expandedTrade === i;
                      return (
                        <>
                          <tr
                            key={`trade-${i}`}
                            className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors cursor-pointer ${isExpanded ? "bg-gray-800/20" : ""}`}
                            onClick={() => setExpandedTrade(isExpanded ? null : i)}
                          >
                            <td className="px-2 py-1.5 font-mono text-gray-400 whitespace-nowrap text-[10px]">
                              {formatDateTime(t.timestamp)}
                            </td>
                            <td className="px-2 py-1.5 whitespace-nowrap">
                              <span className="text-white font-medium">{t.team}</span>
                              <span className={`ml-1 inline-block rounded px-0.5 text-[9px] font-medium ${sportBadge(t.sport)}`}>
                                {t.sport}
                              </span>
                            </td>
                            <td className="px-2 py-1.5">
                              <span className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${badge.bg} ${badge.text}`}>
                                {t.status}
                              </span>
                            </td>
                            <td className={`px-2 py-1.5 text-right font-mono ${(t.contracts_intended || t.contracts_filled || 0) > 1 ? "text-white font-bold" : "text-gray-500"}`}>
                              {t.contracts_intended && t.contracts_intended !== t.contracts_filled
                                ? <>{t.contracts_filled}<span className="text-gray-600">/{t.contracts_intended}</span></>
                                : (t.contracts_intended ?? t.contracts_filled ?? 0)}
                            </td>
                            <td className={`px-2 py-1.5 text-right font-mono ${spreadColor(t.spread_cents)}`}>
                              {t.spread_cents.toFixed(1)}c
                            </td>
                            {(() => {
                              const pnl = tradePnl(t);
                              return (
                                <td className={`px-2 py-1.5 text-right font-mono font-medium ${netColor(pnl.perContract)}`}>
                                  {pnl.totalDollars != null ? (
                                    <div>
                                      <span>{pnl.totalDollars >= 0 ? "+$" : "-$"}{Math.abs(pnl.totalDollars).toFixed(4)}</span>
                                      {pnl.perContract != null && pnl.qty > 1 && (
                                        <div className="text-[9px] text-gray-500">
                                          {pnl.perContract >= 0 ? "+" : ""}{pnl.perContract.toFixed(1)}c x{pnl.qty}
                                        </div>
                                      )}
                                    </div>
                                  ) : "-"}
                                </td>
                              );
                            })()}
                            <td className="px-2 py-1.5 text-center">
                              <span className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${
                                (t.execution_phase || "ioc") === "gtc"
                                  ? "bg-blue-500/20 text-blue-400"
                                  : "bg-gray-500/20 text-gray-500"
                              }`}>
                                {(t.execution_phase || "ioc").toUpperCase()}
                              </span>
                            </td>
                            <td className="px-2 py-1.5 text-center">
                              {t.is_maker ? (
                                <span className="text-cyan-400 text-[9px] font-medium">YES</span>
                              ) : (
                                <span className="text-gray-600 text-[9px]">-</span>
                              )}
                            </td>
                            <td className="px-2 py-1.5 text-right font-mono text-gray-500 text-[10px]">
                              {t.k_price}/{t.pm_price}
                            </td>
                          </tr>
                          {isExpanded && (
                            <tr key={`trade-exp-${i}`} className="bg-gray-800/10">
                              <td colSpan={9} className="px-4 py-2">
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[10px]">
                                  <div>
                                    <span className="text-gray-500">Direction:</span>{" "}
                                    <span className="text-white">{t.direction}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Game ID:</span>{" "}
                                    <span className="text-white font-mono">{t.game_id}</span>
                                  </div>
                                  {t.gtc_rest_time_ms ? (
                                    <div>
                                      <span className="text-gray-500">GTC Rest:</span>{" "}
                                      <span className="text-blue-400">{t.gtc_rest_time_ms}ms ({t.gtc_spread_checks} checks)</span>
                                    </div>
                                  ) : null}
                                  {t.gtc_cancel_reason ? (
                                    <div>
                                      <span className="text-gray-500">GTC Cancel:</span>{" "}
                                      <span className="text-yellow-400">{t.gtc_cancel_reason}</span>
                                    </div>
                                  ) : null}
                                  {t.actual_pnl && (
                                    <>
                                      <div>
                                        <span className="text-gray-500">Gross:</span>{" "}
                                        <span className="text-white">${t.actual_pnl.gross_profit_dollars.toFixed(4)}</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Fees:</span>{" "}
                                        <span className="text-red-400">${t.actual_pnl.fees_dollars.toFixed(4)}</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Total Cost:</span>{" "}
                                        <span className="text-white">${t.actual_pnl.total_cost_dollars.toFixed(4)}</span>
                                      </div>
                                    </>
                                  )}
                                  {t.sizing_details && (
                                    <div>
                                      <span className="text-gray-500">Sizing:</span>{" "}
                                      <span className="text-gray-300">K={t.sizing_details.k_depth} PM={t.sizing_details.pm_depth} ({t.sizing_details.limit_reason})</span>
                                    </div>
                                  )}
                                </div>
                              </td>
                            </tr>
                          )}
                        </>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ══════════ LIQUIDITY TAB ══════════ */}
      {topTab === "liquidity" && (
        <div className="p-4 space-y-4">
          {/* Aggregate Stats */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <MetricCard
              label="Snapshots (24h)"
              value={String(liq?.aggregate?.total_snapshots || 0)}
            />
            <MetricCard
              label="Games Tracked"
              value={String(liq?.aggregate?.unique_games || 0)}
            />
            <MetricCard
              label="Avg Bid Depth"
              value={String(liq?.aggregate?.overall_avg_bid_depth || 0)}
            />
            <MetricCard
              label="Avg Ask Depth"
              value={String(liq?.aggregate?.overall_avg_ask_depth || 0)}
            />
            <MetricCard
              label="Avg Spread"
              value={`${liq?.aggregate?.overall_avg_spread || 0}c`}
              accent={
                (liq?.aggregate?.overall_avg_spread || 0) >= 4
                  ? "text-emerald-400"
                  : (liq?.aggregate?.overall_avg_spread || 0) >= 2
                  ? "text-yellow-400"
                  : "text-white"
              }
            />
          </div>

          {/* Spread Over Time Chart */}
          <div className="rounded-lg border border-gray-800 bg-[#111] p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-white">
                Spread Over Time
                <span className="ml-2 text-[10px] text-gray-500 font-normal">(6h)</span>
              </h3>
              <div className="flex items-center gap-1">
                {liqChartGames.map((g) => (
                  <button
                    key={g}
                    onClick={() => setLiqChartGame(g)}
                    className={`rounded px-2 py-0.5 text-[10px] font-medium transition-colors ${
                      (liqChartGame || liqChartGames[0]) === g
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    {g.length > 20 ? g.slice(0, 20) + "..." : g}
                  </button>
                ))}
              </div>
            </div>
            {liqSpreadChartData.length === 0 ? (
              <div className="text-center py-8 text-xs text-gray-600">
                No spread history data — waiting for orderbook snapshots
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={liqSpreadChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="time" stroke="#4b5563" fontSize={10} />
                  <YAxis yAxisId="left" stroke="#4b5563" fontSize={10} tickFormatter={(v: number) => `${v}c`} />
                  <YAxis yAxisId="right" orientation="right" stroke="#4b5563" fontSize={10} tickFormatter={(v: number) => `${v}`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#111",
                      border: "1px solid #374151",
                      borderRadius: "6px",
                      fontSize: "11px",
                    }}
                    formatter={(value: number | undefined, name: string | undefined) => {
                      const v = value ?? 0;
                      if (name === "spread") return [`${v}c`, "Spread"];
                      if (name === "bid_depth") return [`${v} contracts`, "Bid Depth"];
                      if (name === "ask_depth") return [`${v} contracts`, "Ask Depth"];
                      return [v, name ?? ""];
                    }}
                  />
                  <Line yAxisId="left" type="stepAfter" dataKey="spread" stroke="#10b981" strokeWidth={2} dot={false} />
                  <Line yAxisId="right" type="stepAfter" dataKey="bid_depth" stroke="#3b82f6" strokeWidth={1} dot={false} strokeDasharray="3 3" />
                  <Line yAxisId="right" type="stepAfter" dataKey="ask_depth" stroke="#f59e0b" strokeWidth={1} dot={false} strokeDasharray="3 3" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Per-Game Liquidity Table */}
          <div className="rounded-lg border border-gray-800 bg-[#111]">
            <div className="border-b border-gray-800 px-3 py-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Per-Game Liquidity
                <span className="ml-1.5 text-xs text-gray-500">(24h)</span>
              </h3>
              <input
                type="text"
                placeholder="Filter game..."
                value={liqGameFilter}
                onChange={(e) => setLiqGameFilter(e.target.value)}
                className="w-32 rounded bg-gray-800 px-2 py-0.5 text-[10px] text-gray-300 placeholder-gray-600 border border-gray-700 focus:border-gray-500 focus:outline-none"
              />
            </div>
            <div className="overflow-auto" style={{ maxHeight: "400px" }}>
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-[#111] z-10">
                  <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
                    <th className="px-2 py-1.5">Game</th>
                    <th className="px-2 py-1.5">Platform</th>
                    <th className="px-2 py-1.5 text-right">Snapshots</th>
                    <th className="px-2 py-1.5 text-right">Avg Bid</th>
                    <th className="px-2 py-1.5 text-right">Avg Ask</th>
                    <th className="px-2 py-1.5 text-right">Avg Spread</th>
                    <th className="px-2 py-1.5 text-right">Min Spread</th>
                    <th className="px-2 py-1.5 text-right">Max Spread</th>
                    <th className="px-2 py-1.5">Last Seen</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLiqGames.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="px-3 py-6 text-center text-gray-600">
                        No liquidity data — orderbook DB may be empty
                      </td>
                    </tr>
                  ) : (
                    filteredLiqGames.map((g, i) => (
                      <tr
                        key={`liq-${i}`}
                        className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
                      >
                        <td className="px-2 py-1.5 text-white font-medium whitespace-nowrap font-mono text-[10px]">
                          {g.game_id.length > 30 ? g.game_id.slice(0, 30) + "..." : g.game_id}
                        </td>
                        <td className="px-2 py-1.5">
                          <span className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${
                            g.platform === "kalshi" ? "bg-orange-500/20 text-orange-400" : "bg-blue-500/20 text-blue-400"
                          }`}>
                            {g.platform}
                          </span>
                        </td>
                        <td className="px-2 py-1.5 text-right font-mono text-gray-400">{g.snapshots}</td>
                        <td className="px-2 py-1.5 text-right font-mono text-gray-300">{g.avg_bid_depth}</td>
                        <td className="px-2 py-1.5 text-right font-mono text-gray-300">{g.avg_ask_depth}</td>
                        <td className={`px-2 py-1.5 text-right font-mono font-bold ${spreadColor(g.avg_spread)}`}>
                          {g.avg_spread}c
                        </td>
                        <td className="px-2 py-1.5 text-right font-mono text-gray-400">{g.min_spread}c</td>
                        <td className="px-2 py-1.5 text-right font-mono text-gray-400">{g.max_spread}c</td>
                        <td className="px-2 py-1.5 text-[10px] text-gray-500">{timeAgo(g.last_snapshot)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
