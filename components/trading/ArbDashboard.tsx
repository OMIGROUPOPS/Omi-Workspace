"use client";

import { useEffect, useState, useCallback, useMemo } from "react";

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
  actual_pnl: ActualPnl | null;
  paper_mode: boolean;
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
  kalshi_balance: number;
  pm_balance: number;
  total_portfolio: number;
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

interface ArbState {
  spreads: SpreadRow[];
  trades: TradeEntry[];
  positions: Position[];
  balances: Balances;
  system: SystemStatus;
  pnl_summary: PnlSummary;
  mapped_games: MappedGame[];
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

function statusBadge(status: string): { bg: string; text: string } {
  if (status === "HEDGED" || status === "FILLED" || status === "SUCCESS")
    return { bg: "bg-emerald-500/20", text: "text-emerald-400" };
  if (status.includes("NO_FILL"))
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

type TradeFilter = "all" | "live" | "paper";
type StatusFilter = "all" | "SUCCESS" | "PM_NO_FILL" | "UNHEDGED" | "SKIPPED";
type BottomTab = "positions" | "mapped_games";

// ── Main Component ──────────────────────────────────────────────────────────

export default function ArbDashboard() {
  const [state, setState] = useState<ArbState | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  const [fetchError, setFetchError] = useState(false);
  const [paused, setPaused] = useState(false);
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
    let total = 0;
    let successes = 0;
    let fills = 0;
    for (const t of filteredTrades) {
      if (t.status === "SUCCESS") successes++;
      if (t.contracts_filled > 0) fills++;
      if (t.actual_pnl) {
        total += t.actual_pnl.net_profit_dollars;
      } else if (
        t.status === "SUCCESS" &&
        t.estimated_net_profit_cents != null
      ) {
        total +=
          (t.estimated_net_profit_cents * (t.contracts_filled || 1)) / 100;
      }
    }
    return { total, successes, fills, count: filteredTrades.length };
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

  const mappedGames = state?.mapped_games || [];

  const markSettled = (gameId: string) => {
    setHiddenPositions((prev) => new Set(prev).add(gameId));
  };

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
      </div>

      <div className="p-4 space-y-4">
        {/* ── Metrics Row ──────────────────────────────────────────── */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          <MetricCard
            label="Kalshi Balance"
            value={
              state?.balances.kalshi_balance
                ? `$${state.balances.kalshi_balance.toFixed(2)}`
                : "-"
            }
          />
          <MetricCard
            label="PM Balance"
            value={
              state?.balances.pm_balance
                ? `$${state.balances.pm_balance.toFixed(2)}`
                : "-"
            }
          />
          <MetricCard
            label="Total Portfolio"
            value={
              state?.balances.total_portfolio
                ? `$${state.balances.total_portfolio.toFixed(2)}`
                : "-"
            }
            accent="text-emerald-400"
          />
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
                        : f === "PM_NO_FILL"
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
                      filteredPnl.total > 0
                        ? "text-emerald-400"
                        : filteredPnl.total < 0
                        ? "text-red-400"
                        : "text-gray-500"
                    }
                  >
                    P&L: {filteredPnl.total >= 0 ? "+" : ""}$
                    {filteredPnl.total.toFixed(2)}
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
                    <th className="px-2 py-1.5 text-right">Spread</th>
                    <th className="px-2 py-1.5 text-right">Net</th>
                    <th className="px-2 py-1.5">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTrades.length === 0 ? (
                    <tr>
                      <td
                        colSpan={5}
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
                      return (
                        <tr
                          key={`${t.timestamp}-${i}`}
                          className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
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
                          </td>
                          <td
                            className={`px-2 py-1 text-right font-mono ${spreadColor(t.spread_cents)}`}
                          >
                            {t.spread_cents.toFixed(1)}
                          </td>
                          <td
                            className={`px-2 py-1 text-right font-mono font-medium ${netColor(
                              t.actual_pnl
                                ? t.actual_pnl.per_contract.net
                                : t.estimated_net_profit_cents
                            )}`}
                          >
                            {t.actual_pnl
                              ? `${t.actual_pnl.per_contract.net >= 0 ? "+" : ""}${t.actual_pnl.per_contract.net.toFixed(1)}`
                              : t.estimated_net_profit_cents != null
                              ? `${t.estimated_net_profit_cents > 0 ? "+" : ""}${t.estimated_net_profit_cents.toFixed(1)}~`
                              : "-"}
                          </td>
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

                        {hasFillData && (
                          <div className="mt-1.5 flex items-center gap-3 text-[10px]">
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
                        )}
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
                <div className="overflow-auto" style={{ maxHeight: "400px" }}>
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
                                <span className="text-emerald-400">Today</span>
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
    </div>
  );
}
