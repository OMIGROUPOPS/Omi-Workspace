"use client";

import React from "react";
import type { ArbDataReturn } from "../hooks/useArbData";
import type { TimeHorizon } from "../types";
import { FilterButton } from "../shared/FilterButton";
import { DashboardCard } from "../shared/DashboardCard";
import { PnlSummaryBar } from "../panels/PnlSummaryBar";
import { PnlTimeSeriesChart } from "../panels/PnlTimeSeriesChart";
import { PnlTradeTable } from "../panels/PnlTradeTable";
import { DailyPnlChart } from "../panels/DailyPnlChart";
import { FillRateAnalytics } from "../panels/FillRateAnalytics";

interface Props {
  data: ArbDataReturn;
}

export function PnlHistoryTab({ data }: Props) {
  const {
    state,
    pnlHorizon,
    setPnlHorizon,
    pnlSport,
    setPnlSport,
    availableSports,
    pnlSummaryStats,
    cumulativeChartData,
    dailyPnlData,
    fillRateStats,
    sortedPnlTrades,
    tradeSortKey,
    tradeSortAsc,
    handleSort,
    sortArrow,
    expandedTrade,
    setExpandedTrade,
    exportCsv,
    totalPnl,
    activePositions,
    depthGateStats,
  } = data;

  const horizons: TimeHorizon[] = ["1D", "1W", "1M", "YTD", "ALL"];

  return (
    <div className="p-4 space-y-4">
      {/* ── Filters ──────────────────────────────────────────── */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          {horizons.map((h) => (
            <FilterButton key={h} active={pnlHorizon === h} onClick={() => setPnlHorizon(h)}>
              {h}
            </FilterButton>
          ))}
        </div>
        <span className="text-gray-700">|</span>
        <div className="flex items-center gap-1">
          {availableSports.map((s) => (
            <FilterButton key={s} active={pnlSport === s} onClick={() => setPnlSport(s)}>
              {s === "all" ? "All Sports" : s}
            </FilterButton>
          ))}
        </div>
        <button
          onClick={exportCsv}
          className="ml-auto rounded px-2 py-1 text-[10px] font-medium bg-gray-800 text-gray-400 hover:text-gray-300"
        >
          Export CSV
        </button>
      </div>

      {/* ── Summary Metrics ──────────────────────────────────── */}
      <div className="grid grid-cols-6 gap-3">
        <DashboardCard
          label="Net P&L"
          value={`$${pnlSummaryStats.totalPnl.toFixed(2)}`}
          accent={pnlSummaryStats.totalPnl >= 0 ? "text-emerald-400" : "text-red-400"}
        />
        <DashboardCard
          label="Win Rate"
          value={`${pnlSummaryStats.winRate}%`}
          sub={`${pnlSummaryStats.wins}W / ${pnlSummaryStats.losses}L`}
        />
        <DashboardCard
          label="Avg Profit"
          value={`$${pnlSummaryStats.avgProfit.toFixed(4)}`}
          accent={pnlSummaryStats.avgProfit >= 0 ? "text-emerald-400" : "text-red-400"}
        />
        <DashboardCard
          label="Best / Worst"
          value={`$${pnlSummaryStats.best.toFixed(4)}`}
          sub={`Worst: $${pnlSummaryStats.worst.toFixed(4)}`}
        />
        <DashboardCard
          label="Trades"
          value={`${pnlSummaryStats.totalTrades}`}
          sub={`${pnlSummaryStats.totalContracts} contracts`}
        />
        <DashboardCard
          label="No-Fills"
          value={`${pnlSummaryStats.noFills}`}
          sub={`GTC: ${pnlSummaryStats.gtcFills}/${pnlSummaryStats.gtcAttempts} (${pnlSummaryStats.gtcFillRate}%)`}
        />
      </div>

      {/* ── Depth Gate Stats ──────────────────────────────────── */}
      <div className="rounded-lg border border-gray-800 bg-[#111] px-3 py-2 flex items-center gap-6 text-xs">
        <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wide">Depth Gate</span>
        <div>
          <span className="text-gray-500">Skips Today: </span>
          <span className="text-white font-bold font-mono">{depthGateStats.skippedToday}</span>
        </div>
        <div>
          <span className="text-gray-500">Threshold: </span>
          <span className="text-white font-mono">{depthGateStats.threshold}</span>
        </div>
        <div>
          <span className="text-gray-500">&lt;{depthGateStats.threshold}: </span>
          <span className="text-red-400 font-bold font-mono">{depthGateStats.belowUnwindRate}%</span>
          <span className="text-gray-600"> unwind ({depthGateStats.belowThreshold})</span>
        </div>
        <div>
          <span className="text-gray-500">&ge;{depthGateStats.threshold}: </span>
          <span className="text-emerald-400 font-bold font-mono">{depthGateStats.aboveUnwindRate}%</span>
          <span className="text-gray-600"> unwind ({depthGateStats.aboveThreshold})</span>
        </div>
      </div>

      {/* ── P&L Reconciliation Bar ────────────────────────────── */}
      <PnlSummaryBar
        balances={state?.balances}
        positions={activePositions}
        totalPnl={totalPnl}
      />

      {/* ── Charts Row ────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-4">
        <PnlTimeSeriesChart data={cumulativeChartData} />
        <DailyPnlChart data={dailyPnlData} />
      </div>

      {/* ── Fill Rate Analytics ───────────────────────────────── */}
      <FillRateAnalytics data={fillRateStats} />

      {/* ── Trade Table ───────────────────────────────────────── */}
      <PnlTradeTable
        trades={sortedPnlTrades}
        tradeSortKey={tradeSortKey}
        tradeSortAsc={tradeSortAsc}
        handleSort={handleSort}
        sortArrow={sortArrow}
        expandedTrade={expandedTrade}
        setExpandedTrade={setExpandedTrade}
      />
    </div>
  );
}
