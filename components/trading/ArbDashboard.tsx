"use client";

import { useEffect, useState, useCallback, useMemo } from "react";

// ── Types (mirrors API) ────────────────────────────────────────────────────

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
  actual_pnl: number | null;
  paper_mode: boolean;
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

interface ArbState {
  spreads: SpreadRow[];
  trades: TradeEntry[];
  positions: Position[];
  balances: Balances;
  system: SystemStatus;
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
  const diff = Date.now() - new Date(iso).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  return `${hrs}h ago`;
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

function formatTime(iso: string): string {
  if (!iso) return "-";
  try {
    return new Date(iso).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
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
    return new Date(iso).toISOString().slice(0, 10);
  } catch {
    return "";
  }
}

function yesterdayStr(): string {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

function todayStr(): string {
  return new Date().toISOString().slice(0, 10);
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

type TradeFilter = "all" | "live" | "paper";
type DateFilter = "today" | "yesterday" | "all";

// ── Main Component ──────────────────────────────────────────────────────────

export default function ArbDashboard() {
  const [state, setState] = useState<ArbState | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  const [fetchError, setFetchError] = useState(false);
  const [paused, setPaused] = useState(false);
  const [tradeFilter, setTradeFilter] = useState<TradeFilter>("all");
  const [dateFilter, setDateFilter] = useState<DateFilter>("today");
  const [showAllSpreads, setShowAllSpreads] = useState(false);

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

  // ── Spreads: filter + sort ──────────────────────────────────────────
  const sortedSpreads = useMemo(() => {
    const raw = state?.spreads || [];
    const filtered = showAllSpreads
      ? raw
      : raw.filter(
          (s) => s.spread_buy_pm > 0 || s.spread_buy_k > 0
        );
    return [...filtered].sort((a, b) => {
      const aMax = Math.max(a.spread_buy_pm, a.spread_buy_k);
      const bMax = Math.max(b.spread_buy_pm, b.spread_buy_k);
      return bMax - aMax;
    });
  }, [state?.spreads, showAllSpreads]);

  const totalSpreadCount = state?.spreads?.length || 0;

  // ── Trades: filter by mode + date, sort newest first ────────────────
  const allTrades = useMemo(() => {
    return [...(state?.trades || [])]
      .sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
      .slice(0, 50);
  }, [state?.trades]);

  const filteredTrades = useMemo(() => {
    const today = todayStr();
    const yesterday = yesterdayStr();

    let trades = allTrades;

    // Date filter
    if (dateFilter === "today") {
      trades = trades.filter((t) => toDateStr(t.timestamp) === today);
    } else if (dateFilter === "yesterday") {
      trades = trades.filter((t) => toDateStr(t.timestamp) === yesterday);
    }

    // Mode filter
    if (tradeFilter === "paper") {
      trades = trades.filter((t) => t.paper_mode);
    } else if (tradeFilter === "live") {
      trades = trades.filter((t) => !t.paper_mode);
    }

    return trades;
  }, [allTrades, dateFilter, tradeFilter]);

  // ── P&L summary ──────────────────────────────────────────────────────
  const executedTrades = allTrades.filter((t) => t.contracts_filled > 0);
  const totalPnlCents = executedTrades.reduce(
    (sum, t) => sum + (t.estimated_net_profit_cents ?? 0),
    0
  );
  const hedgedCount = executedTrades.filter((t) => t.hedged).length;
  const unhedgedCount = executedTrades.filter(
    (t) => !t.hedged && t.contracts_filled > 0
  ).length;

  // ── Positions: only active (quantity > 0) ───────────────────────────
  const activePositions = useMemo(() => {
    return (state?.positions || []).filter((p) => p.quantity > 0);
  }, [state?.positions]);

  const unhedgedPositions = activePositions.filter((p) => !p.hedged_with);
  const hedgedPositions = activePositions.filter((p) => p.hedged_with);

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
        {/* ── Top: Balances + P&L Row ──────────────────────────────────── */}
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
            label="Est. P&L"
            value={
              executedTrades.length > 0
                ? `${totalPnlCents >= 0 ? "+" : ""}${totalPnlCents.toFixed(1)}c`
                : "-"
            }
            sub={
              executedTrades.length > 0
                ? `${executedTrades.length} exec, ${hedgedCount} hedged${unhedgedCount > 0 ? `, ${unhedgedCount} unhedged` : ""}`
                : undefined
            }
            accent={
              totalPnlCents > 0
                ? "text-emerald-400"
                : totalPnlCents < 0
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

        {/* ── Error Banner ─────────────────────────────────────────────── */}
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

        {/* ── Middle: Spreads (60%) + Trades (40%) ─────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
          {/* Live Spreads (3/5 = 60%) */}
          <div className="lg:col-span-3 rounded-lg border border-gray-800 bg-[#111] flex flex-col" style={{ maxHeight: "440px" }}>
            <div className="flex items-center justify-between border-b border-gray-800 px-3 py-2 shrink-0">
              <h2 className="text-sm font-semibold text-white">
                Live Spreads
                <span className="ml-1.5 text-xs text-gray-500">
                  {sortedSpreads.length}
                  {!showAllSpreads && totalSpreadCount > sortedSpreads.length && (
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
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> 4c+
                  </span>
                  <span className="flex items-center gap-0.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-yellow-500" /> 3-4c
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
                              className={`inline-block rounded px-1 py-0.5 text-[10px] font-medium ${sportBadge(
                                s.sport
                              )}`}
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
                            className={`px-2 py-1 text-right font-mono font-bold ${spreadColor(
                              s.spread_buy_pm
                            )}`}
                          >
                            {s.spread_buy_pm.toFixed(1)}
                          </td>
                          <td
                            className={`px-2 py-1 text-right font-mono font-bold ${spreadColor(
                              s.spread_buy_k
                            )}`}
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

          {/* Trade Log (2/5 = 40%) */}
          <div className="lg:col-span-2 rounded-lg border border-gray-800 bg-[#111] flex flex-col" style={{ maxHeight: "440px" }}>
            <div className="border-b border-gray-800 px-3 py-2 flex items-center justify-between shrink-0">
              <h2 className="text-sm font-semibold text-white">
                Trades
                <span className="ml-1.5 text-xs text-gray-500">
                  {filteredTrades.length}
                </span>
              </h2>
              <div className="flex items-center gap-1.5">
                {/* Date filters */}
                {(["today", "yesterday", "all"] as DateFilter[]).map((f) => (
                  <button
                    key={f}
                    onClick={() => setDateFilter(f)}
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
                      dateFilter === f
                        ? "bg-gray-700 text-white"
                        : "text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    {f === "today" ? "Today" : f === "yesterday" ? "Yest" : "All"}
                  </button>
                ))}
                <span className="text-gray-700">|</span>
                {/* Mode filters */}
                {(["all", "live", "paper"] as TradeFilter[]).map((f) => (
                  <button
                    key={f}
                    onClick={() => setTradeFilter(f)}
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
                      tradeFilter === f
                        ? f === "live"
                          ? "bg-emerald-500/20 text-emerald-400"
                          : f === "paper"
                          ? "bg-purple-500/20 text-purple-400"
                          : "bg-gray-700 text-white"
                        : "text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    {f === "all" ? "All" : f === "live" ? "Live" : "Paper"}
                  </button>
                ))}
              </div>
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
                        No trades {dateFilter === "today" ? "today" : dateFilter === "yesterday" ? "yesterday" : "recorded"}
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
                          <td className="px-2 py-1 font-mono text-gray-400 whitespace-nowrap">
                            {formatTime(t.timestamp)}
                          </td>
                          <td className="px-2 py-1 whitespace-nowrap">
                            <span className="text-white font-medium">
                              {t.team}
                            </span>
                            <span
                              className={`ml-1 inline-block rounded px-0.5 text-[9px] font-medium ${sportBadge(
                                t.sport
                              )}`}
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
                            className={`px-2 py-1 text-right font-mono ${spreadColor(
                              t.spread_cents
                            )}`}
                          >
                            {t.spread_cents.toFixed(1)}
                          </td>
                          <td
                            className={`px-2 py-1 text-right font-mono font-medium ${netColor(
                              t.estimated_net_profit_cents
                            )}`}
                          >
                            {t.estimated_net_profit_cents != null
                              ? `${t.estimated_net_profit_cents > 0 ? "+" : ""}${t.estimated_net_profit_cents.toFixed(1)}`
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

        {/* ── Bottom: Positions (only if active) ───────────────────────── */}
        {activePositions.length > 0 ? (
          <div className="rounded-lg border border-gray-800 bg-[#111]">
            <div className="border-b border-gray-800 px-3 py-2">
              <h2 className="text-sm font-semibold text-white">
                Open Positions
                <span className="ml-1.5 text-xs text-gray-500">
                  {activePositions.length}
                </span>
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-0 divide-x divide-gray-800/50">
              {/* Unhedged first */}
              {unhedgedPositions.map((p, i) => (
                <div
                  key={`uh-${i}`}
                  className="px-3 py-2 bg-red-500/5"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-white font-medium text-xs">
                        {p.team}
                      </span>
                      <span className="ml-1 text-[10px] text-gray-500">
                        {p.platform}
                      </span>
                    </div>
                    <span className="text-[9px] font-medium rounded px-1 py-0.5 bg-red-500/20 text-red-400">
                      UNHEDGED
                    </span>
                  </div>
                  <div className="mt-0.5 flex items-center gap-2 text-[10px] text-gray-400">
                    <span>{p.side} x{p.quantity}</span>
                    <span>@ {p.avg_price}c</span>
                    <span className={sportBadge(p.sport).split(" ").pop()}>
                      {p.sport}
                    </span>
                  </div>
                </div>
              ))}
              {/* Hedged pairs — single row per game+team */}
              {hedgedPositions.map((p, i) => (
                <div key={`h-${i}`} className="px-3 py-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-white font-medium text-xs">
                        {p.team}
                      </span>
                      <span
                        className={`ml-1 inline-block rounded px-0.5 text-[9px] font-medium ${sportBadge(
                          p.sport
                        )}`}
                      >
                        {p.sport}
                      </span>
                    </div>
                    <span className="text-[9px] font-medium rounded px-1 py-0.5 bg-emerald-500/20 text-emerald-400">
                      HEDGED
                    </span>
                  </div>
                  <div className="mt-0.5 flex items-center gap-2 text-[10px] text-gray-400">
                    <span>{p.side} x{p.quantity}</span>
                    <span>PM@{p.avg_price}c</span>
                    {p.current_value > 0 && (
                      <span>K@{p.current_value}c</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-1">
            <span className="text-[10px] text-gray-600">No open positions</span>
          </div>
        )}

        {/* ── Connection Footer ────────────────────────────────────────── */}
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
