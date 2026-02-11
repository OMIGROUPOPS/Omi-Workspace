"use client";

import { useEffect, useState, useCallback } from "react";

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
  if (cents >= 3) return "text-emerald-400";
  if (cents >= 2) return "text-yellow-400";
  if (cents > 0) return "text-gray-400";
  return "text-red-400";
}

function spreadBg(cents: number): string {
  if (cents >= 3) return "bg-emerald-500/10";
  if (cents >= 2) return "bg-yellow-500/10";
  return "";
}

function statusBadge(status: string): { bg: string; text: string } {
  if (status === "HEDGED" || status === "FILLED")
    return { bg: "bg-emerald-500/20", text: "text-emerald-400" };
  if (status.includes("NO_FILL"))
    return { bg: "bg-yellow-500/20", text: "text-yellow-400" };
  if (status === "FAILED" || status === "ERROR")
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
    <div className="rounded-lg border border-gray-800 bg-[#111] p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
        {label}
      </p>
      <p className={`mt-1 text-2xl font-bold ${accent || "text-white"}`}>
        {value}
      </p>
      {sub && <p className="mt-0.5 text-xs text-gray-500">{sub}</p>}
    </div>
  );
}

// ── Main Component ──────────────────────────────────────────────────────────

export default function ArbDashboard() {
  const [state, setState] = useState<ArbState | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  const [fetchError, setFetchError] = useState(false);
  const [paused, setPaused] = useState(false);

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

  // ── Sort spreads: executable first, then by best spread desc ───────────
  const sortedSpreads = [...(state?.spreads || [])].sort((a, b) => {
    if (a.is_executable !== b.is_executable)
      return a.is_executable ? -1 : 1;
    const aMax = Math.max(a.spread_buy_pm, a.spread_buy_k);
    const bMax = Math.max(b.spread_buy_pm, b.spread_buy_k);
    return bMax - aMax;
  });

  // ── Recent trades (newest first) ──────────────────────────────────────
  const recentTrades = [...(state?.trades || [])]
    .sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )
    .slice(0, 50);

  // ── Group positions by hedged pairs ───────────────────────────────────
  const hedgedPositions = (state?.positions || []).filter(
    (p) => p.hedged_with
  );
  const unhedgedPositions = (state?.positions || []).filter(
    (p) => !p.hedged_with
  );

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-200">
      {/* Header */}
      <div className="border-b border-gray-800 bg-[#0f0f0f]">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-white">Arb Monitor</h1>
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
          <div className="flex items-center gap-3">
            <button
              onClick={() => setPaused(!paused)}
              className={`rounded px-3 py-1.5 text-xs font-medium transition-colors ${
                paused
                  ? "bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {paused ? "Paused" : "Pause"}
            </button>
            <button
              onClick={fetchData}
              className="rounded bg-gray-800 px-3 py-1.5 text-xs font-medium text-gray-400 hover:bg-gray-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* ── Top Metrics Row ────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
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
            label="Games Monitored"
            value={String(state?.system.games_monitored || 0)}
          />
          <MetricCard
            label="WS Messages"
            value={String(state?.system.ws_messages_processed || 0)}
          />
          <MetricCard
            label="Uptime"
            value={formatUptime(state?.system.uptime_seconds || 0)}
            sub={state?.system.executor_version || ""}
          />
        </div>

        {/* ── System Status Banner ───────────────────────────────────────── */}
        {state?.system.error_count ? (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-red-400 text-sm font-medium">
                {state.system.error_count} error
                {state.system.error_count > 1 ? "s" : ""}
              </span>
              {state.system.last_error && (
                <span className="text-red-400/70 text-xs truncate max-w-xl">
                  {state.system.last_error}
                </span>
              )}
            </div>
          </div>
        ) : null}

        {/* ── Live Spread Table ──────────────────────────────────────────── */}
        <div className="rounded-lg border border-gray-800 bg-[#111]">
          <div className="flex items-center justify-between border-b border-gray-800 px-4 py-3">
            <h2 className="text-sm font-semibold text-white">
              Live Spreads
              {sortedSpreads.length > 0 && (
                <span className="ml-2 text-xs text-gray-500">
                  ({sortedSpreads.length} games)
                </span>
              )}
            </h2>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-emerald-500" /> 3c+
              </span>
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-yellow-500" /> 2-3c
              </span>
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-gray-500" /> &lt;2c
              </span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-2">Game</th>
                  <th className="px-3 py-2">Sport</th>
                  <th className="px-3 py-2">Team</th>
                  <th className="px-3 py-2 text-right">K Bid</th>
                  <th className="px-3 py-2 text-right">K Ask</th>
                  <th className="px-3 py-2 text-right">PM Bid</th>
                  <th className="px-3 py-2 text-right">PM Ask</th>
                  <th className="px-3 py-2 text-right">BUY_PM</th>
                  <th className="px-3 py-2 text-right">BUY_K</th>
                  <th className="px-3 py-2 text-right">Size</th>
                  <th className="px-3 py-2 text-center">Exec</th>
                </tr>
              </thead>
              <tbody>
                {sortedSpreads.length === 0 ? (
                  <tr>
                    <td
                      colSpan={11}
                      className="px-4 py-8 text-center text-gray-600"
                    >
                      {hasData
                        ? "No spreads currently monitored"
                        : "Waiting for executor data..."}
                    </td>
                  </tr>
                ) : (
                  sortedSpreads.map((s) => {
                    const best = Math.max(s.spread_buy_pm, s.spread_buy_k);
                    return (
                      <tr
                        key={`${s.game_id}-${s.team}`}
                        className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${
                          s.is_executable ? "bg-emerald-500/5" : ""
                        } ${spreadBg(best)}`}
                      >
                        <td className="px-4 py-2 font-medium text-white whitespace-nowrap">
                          {s.game_name || s.game_id}
                        </td>
                        <td className="px-3 py-2">
                          <span
                            className={`inline-block rounded px-1.5 py-0.5 text-xs font-medium ${sportBadge(
                              s.sport
                            )}`}
                          >
                            {s.sport}
                          </span>
                        </td>
                        <td className="px-3 py-2 font-mono text-xs">
                          {s.team}
                        </td>
                        <td className="px-3 py-2 text-right font-mono">
                          {s.k_bid}
                        </td>
                        <td className="px-3 py-2 text-right font-mono">
                          {s.k_ask}
                        </td>
                        <td className="px-3 py-2 text-right font-mono">
                          {s.pm_bid.toFixed(1)}
                        </td>
                        <td className="px-3 py-2 text-right font-mono">
                          {s.pm_ask.toFixed(1)}
                        </td>
                        <td
                          className={`px-3 py-2 text-right font-mono font-bold ${spreadColor(
                            s.spread_buy_pm
                          )}`}
                        >
                          {s.spread_buy_pm.toFixed(1)}c
                        </td>
                        <td
                          className={`px-3 py-2 text-right font-mono font-bold ${spreadColor(
                            s.spread_buy_k
                          )}`}
                        >
                          {s.spread_buy_k.toFixed(1)}c
                        </td>
                        <td className="px-3 py-2 text-right font-mono text-gray-400">
                          {s.pm_size}
                        </td>
                        <td className="px-3 py-2 text-center">
                          {s.is_executable ? (
                            <span className="inline-block h-5 w-5 rounded-full bg-emerald-500/20 text-emerald-400 text-xs leading-5">
                              ✓
                            </span>
                          ) : (
                            <span className="text-gray-600">-</span>
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

        {/* ── Bottom Grid: Trades + Positions ───────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trade Log (2/3 width) */}
          <div className="lg:col-span-2 rounded-lg border border-gray-800 bg-[#111]">
            <div className="border-b border-gray-800 px-4 py-3">
              <h2 className="text-sm font-semibold text-white">
                Trade Log
                {recentTrades.length > 0 && (
                  <span className="ml-2 text-xs text-gray-500">
                    (last {recentTrades.length})
                  </span>
                )}
              </h2>
            </div>
            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-[#111]">
                  <tr className="border-b border-gray-800 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    <th className="px-4 py-2">Time</th>
                    <th className="px-3 py-2">Game</th>
                    <th className="px-3 py-2">Dir</th>
                    <th className="px-3 py-2 text-right">Spread</th>
                    <th className="px-3 py-2 text-right">Net</th>
                    <th className="px-3 py-2 text-center">Hedged</th>
                    <th className="px-3 py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTrades.length === 0 ? (
                    <tr>
                      <td
                        colSpan={7}
                        className="px-4 py-8 text-center text-gray-600"
                      >
                        No trades recorded
                      </td>
                    </tr>
                  ) : (
                    recentTrades.map((t, i) => {
                      const badge = statusBadge(t.status);
                      return (
                        <tr
                          key={`${t.timestamp}-${i}`}
                          className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
                        >
                          <td className="px-4 py-2 font-mono text-xs text-gray-400 whitespace-nowrap">
                            {formatTime(t.timestamp)}
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap">
                            <span className="text-white font-medium">
                              {t.team}
                            </span>
                            <span
                              className={`ml-1.5 inline-block rounded px-1 py-0.5 text-[10px] font-medium ${sportBadge(
                                t.sport
                              )}`}
                            >
                              {t.sport}
                            </span>
                            {t.paper_mode && (
                              <span className="ml-1 inline-block rounded px-1 py-0.5 text-[10px] font-medium bg-purple-500/20 text-purple-400">
                                PAPER
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-2 text-xs font-mono">
                            {t.direction === "BUY_PM_SELL_K" ? (
                              <span className="text-blue-400">BUY_PM</span>
                            ) : (
                              <span className="text-orange-400">BUY_K</span>
                            )}
                          </td>
                          <td
                            className={`px-3 py-2 text-right font-mono ${spreadColor(
                              t.spread_cents
                            )}`}
                          >
                            {t.spread_cents.toFixed(1)}c
                          </td>
                          <td className="px-3 py-2 text-right font-mono text-gray-400">
                            {t.estimated_net_profit_cents != null
                              ? `${t.estimated_net_profit_cents.toFixed(1)}c`
                              : "-"}
                          </td>
                          <td className="px-3 py-2 text-center">
                            {t.hedged ? (
                              <span className="text-emerald-400 text-xs">
                                ✓
                              </span>
                            ) : (
                              <span className="text-red-400 text-xs">✗</span>
                            )}
                          </td>
                          <td className="px-3 py-2">
                            <span
                              className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-medium ${badge.bg} ${badge.text}`}
                            >
                              {t.status}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Positions (1/3 width) */}
          <div className="rounded-lg border border-gray-800 bg-[#111]">
            <div className="border-b border-gray-800 px-4 py-3">
              <h2 className="text-sm font-semibold text-white">
                Positions
                <span className="ml-2 text-xs text-gray-500">
                  ({(state?.positions || []).length} open)
                </span>
              </h2>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {(state?.positions || []).length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-600 text-sm">
                  No open positions
                </div>
              ) : (
                <div className="divide-y divide-gray-800/50">
                  {/* Unhedged positions first (with warning) */}
                  {unhedgedPositions.map((p, i) => (
                    <div
                      key={`uh-${i}`}
                      className="px-4 py-3 bg-red-500/5"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-white font-medium text-sm">
                            {p.team}
                          </span>
                          <span className="ml-1.5 text-xs text-gray-500">
                            {p.platform}
                          </span>
                        </div>
                        <span className="text-[10px] font-medium rounded px-1.5 py-0.5 bg-red-500/20 text-red-400">
                          UNHEDGED
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-3 text-xs text-gray-400">
                        <span>
                          {p.side} x{p.quantity}
                        </span>
                        <span>@ {p.avg_price}c</span>
                        <span
                          className={`font-medium ${sportBadge(p.sport)
                            .split(" ")
                            .pop()}`}
                        >
                          {p.sport}
                        </span>
                      </div>
                    </div>
                  ))}

                  {/* Hedged positions */}
                  {hedgedPositions.map((p, i) => (
                    <div key={`h-${i}`} className="px-4 py-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-white font-medium text-sm">
                            {p.team}
                          </span>
                          <span className="ml-1.5 text-xs text-gray-500">
                            {p.platform}
                          </span>
                        </div>
                        <span className="text-[10px] font-medium rounded px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400">
                          HEDGED
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-3 text-xs text-gray-400">
                        <span>
                          {p.side} x{p.quantity}
                        </span>
                        <span>@ {p.avg_price}c</span>
                        <span className="text-gray-600">
                          pair: {p.hedged_with}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Connection Details Footer ──────────────────────────────────── */}
        <div className="rounded-lg border border-gray-800 bg-[#111] px-4 py-3">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-gray-500">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-400">WebSocket</span>
              <Pulse active={state?.system.ws_connected ?? false} />
              <span>
                {state?.system.ws_connected ? "Connected" : "Disconnected"}
              </span>
            </div>
            <div>
              <span className="font-medium text-gray-400">Last Scan</span>{" "}
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
              <span className="font-medium text-gray-400">Dashboard Poll</span>{" "}
              {lastFetch ? `${timeAgo(lastFetch.toISOString())}` : "-"}
              {paused && " (paused)"}
            </div>
            <div>
              <span className="font-medium text-gray-400">Version</span>{" "}
              {state?.system.executor_version || "-"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
