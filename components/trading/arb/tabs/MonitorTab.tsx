"use client";

import React, { useState } from "react";
import type { ArbDataReturn } from "../hooks/useArbData";
import type { BottomTab } from "../types";
import { DashboardCard } from "../shared/DashboardCard";
import { FilterButton } from "../shared/FilterButton";
import { SpreadHeatmapTable } from "../panels/SpreadHeatmapTable";
import { SpreadTimeSeriesChart } from "../panels/SpreadTimeSeriesChart";
import { TradeLog } from "../panels/TradeLog";
import { PositionsTable } from "../panels/PositionsTable";
import { MappedGamesTable } from "../panels/MappedGamesTable";
import { formatUptime, formatDateLabel } from "../helpers";

interface Props {
  data: ArbDataReturn;
}

export function MonitorTab({ data }: Props) {
  const {
    state,
    sortedSpreads,
    filteredTrades,
    filteredPnl,
    totalPnl,
    activePositions,
    positionValues,
    portfolioDelta,
    tradeFilter,
    setTradeFilter,
    statusFilter,
    setStatusFilter,
    dateOffset,
    setDateOffset,
    dateAll,
    setDateAll,
    dateLabel,
    tradeSearch,
    setTradeSearch,
    bottomTab,
    setBottomTab,
    expandedMonitorTrade,
    setExpandedMonitorTrade,
    markSettled,
  } = data;

  const [chartOpen, setChartOpen] = useState(false);

  const specs = state?.specs;
  const spreadMinCents = specs?.config?.spread_min_cents ?? 4;

  return (
    <div className="p-4 space-y-4">
      {/* ── Metrics Row ──────────────────────────────────────── */}
      <div className="grid grid-cols-6 gap-3">
        <DashboardCard
          label="Portfolio"
          value={`$${(state?.balances?.total_portfolio ?? 0).toFixed(2)}`}
          sub={portfolioDelta.total !== 0 ? `${portfolioDelta.total >= 0 ? "+" : ""}$${portfolioDelta.total.toFixed(2)}` : undefined}
        />
        <DashboardCard
          label="P&L (All)"
          value={`$${totalPnl.netTotal.toFixed(2)}`}
          accent={totalPnl.netTotal >= 0 ? "text-emerald-400" : "text-red-400"}
          sub={`${totalPnl.realizedWins}W / ${totalPnl.realizedLosses}L${totalPnl.openCount > 0 ? ` (${totalPnl.openCount} open)` : ""}`}
        />
        <DashboardCard
          label="Spreads"
          value={`${sortedSpreads.filter((s) => Math.max(s.spread_buy_pm, s.spread_buy_k) >= 4).length}`}
          sub={`${state?.spreads?.length ?? 0} total monitored`}
          accent="text-emerald-400"
        />
        <DashboardCard
          label="Positions"
          value={`${activePositions.length}`}
          sub={`$${positionValues.total.toFixed(2)} exposure`}
        />
        <DashboardCard
          label="K Balance"
          value={`$${(state?.balances?.k_portfolio ?? 0).toFixed(2)}`}
          sub={`Cash: $${(state?.balances?.k_cash ?? 0).toFixed(2)}`}
        />
        <DashboardCard
          label="PM Balance"
          value={`$${(state?.balances?.pm_portfolio ?? 0).toFixed(2)}`}
          sub={`Cash: $${(state?.balances?.pm_cash ?? 0).toFixed(2)}`}
        />
      </div>

      {/* ── Trades Section ────────────────────────────────────── */}
      <div className="rounded-lg border border-gray-800 bg-[#111]">
        <div className="px-3 py-2 border-b border-gray-800 flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1">
            <button
              onClick={() => { setDateAll(false); setDateOffset((o) => o - 1); }}
              className="px-1.5 py-0.5 text-xs text-gray-500 hover:text-gray-300"
            >
              {"<"}
            </button>
            <button
              onClick={() => { setDateAll(false); setDateOffset(0); }}
              className={`px-2 py-0.5 text-xs font-medium rounded ${!dateAll && dateOffset === 0 ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
            >
              {dateLabel}
            </button>
            <button
              onClick={() => { setDateAll(false); setDateOffset((o) => Math.min(o + 1, 0)); }}
              className="px-1.5 py-0.5 text-xs text-gray-500 hover:text-gray-300"
            >
              {">"}
            </button>
            <FilterButton active={dateAll} onClick={() => setDateAll(!dateAll)}>ALL</FilterButton>
          </div>
          <span className="text-gray-700">|</span>
          <div className="flex items-center gap-1">
            <FilterButton active={tradeFilter === "all"} onClick={() => setTradeFilter("all")}>All</FilterButton>
            <FilterButton active={tradeFilter === "live"} onClick={() => setTradeFilter("live")} variant="green">Live</FilterButton>
            <FilterButton active={tradeFilter === "paper"} onClick={() => setTradeFilter("paper")} variant="purple">Paper</FilterButton>
          </div>
          <span className="text-gray-700">|</span>
          <div className="flex items-center gap-1">
            {(["all", "SUCCESS", "PM_NO_FILL", "EXITED", "UNHEDGED"] as const).map((s) => (
              <FilterButton key={s} active={statusFilter === s} onClick={() => setStatusFilter(s)}>
                {s === "all" ? "All" : s}
              </FilterButton>
            ))}
          </div>
          <input
            type="text"
            placeholder="Search team..."
            value={tradeSearch}
            onChange={(e) => setTradeSearch(e.target.value)}
            className="ml-auto bg-gray-800 border border-gray-700 rounded px-2 py-0.5 text-xs text-gray-300 w-32 focus:outline-none focus:border-gray-600"
          />
          <span className={`text-xs font-mono ${filteredPnl.netTotal >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            ${filteredPnl.netTotal.toFixed(2)} ({filteredPnl.fills} fills)
          </span>
        </div>

        <TradeLog
          trades={filteredTrades}
          expandedTrade={expandedMonitorTrade}
          setExpandedTrade={setExpandedMonitorTrade}
        />
      </div>

      {/* ── Positions / Mapped Games ──────────────────────────── */}
      <div className="rounded-lg border border-gray-800 bg-[#111]">
        <div className="px-3 py-2 border-b border-gray-800 flex items-center gap-2">
          <button
            onClick={() => setBottomTab("positions")}
            className={`rounded px-2 py-0.5 text-xs font-medium ${bottomTab === "positions" ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            Positions ({activePositions.length})
          </button>
          <button
            onClick={() => setBottomTab("mapped_games")}
            className={`rounded px-2 py-0.5 text-xs font-medium ${bottomTab === "mapped_games" ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            Mapped Games ({state?.mapped_games?.length ?? 0})
          </button>
        </div>
        {bottomTab === "positions" && (
          <PositionsTable positions={activePositions} markSettled={markSettled} />
        )}
        {bottomTab === "mapped_games" && (
          <MappedGamesTable games={state?.mapped_games || []} />
        )}
      </div>

      {/* ── Spread Heatmap ────────────────────────────────────── */}
      <SpreadHeatmapTable
        spreads={sortedSpreads}
        mappedGames={state?.mapped_games || []}
      />

      {/* ── Spread Time Series (collapsible) ─────────────────── */}
      <div className="rounded-lg border border-gray-800 bg-[#111]">
        <button
          onClick={() => setChartOpen((o) => !o)}
          className="w-full px-3 py-2 flex items-center justify-between text-xs font-semibold text-gray-400 uppercase tracking-wide hover:text-gray-300"
        >
          <span>Spread Time Series (60 min)</span>
          <span className="text-gray-600">{chartOpen ? "\u25B2" : "\u25BC"}</span>
        </button>
        {chartOpen && (
          <div className="px-3 pb-3">
            <SpreadTimeSeriesChart
              spreadHistory={state?.spread_history || []}
              spreadMinCents={spreadMinCents}
              compact
            />
          </div>
        )}
      </div>
    </div>
  );
}
