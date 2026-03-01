"use client";

import React from "react";
import { useArbData } from "./arb/hooks/useArbData";
import { useAlerts } from "./arb/hooks/useAlerts";
import { ArbDashboardHeader } from "./arb/ArbDashboardHeader";
import { DashboardCard } from "./arb/shared/DashboardCard";
import { FilterButton } from "./arb/shared/FilterButton";
import { TradeLog } from "./arb/panels/TradeLog";
import { PositionsTable } from "./arb/panels/PositionsTable";

export default function ArbDashboard() {
  const data = useArbData();
  const alerts = useAlerts(data.state);

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
    expandedMonitorTrade,
    setExpandedMonitorTrade,
    markSettled,
  } = data;

  return (
    <div className="min-h-screen bg-black text-gray-300 relative">
      {/* Scanline overlay */}
      <div
        className="pointer-events-none fixed inset-0 z-50"
        style={{
          backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
          backgroundSize: "100% 4px",
        }}
      />

      <ArbDashboardHeader
        hasData={!!data.hasData}
        isStale={data.isStale}
        fetchError={data.fetchError}
        paused={data.paused}
        setPaused={data.setPaused}
        system={data.state?.system}
        alerts={alerts}
        fetchData={data.fetchData}
      />

      <div className="p-3 space-y-2">
        {/* ── Stats Row ──────────────────────────────────────── */}
        <div className="grid grid-cols-4 gap-2">
          <DashboardCard
            label="Portfolio"
            value={`$${(state?.balances?.total_portfolio ?? 0).toFixed(2)}`}
            sub={portfolioDelta.total !== 0 ? `${portfolioDelta.total >= 0 ? "+" : ""}$${portfolioDelta.total.toFixed(2)}` : undefined}
          />
          {(() => {
            const cashPnl = state?.pnl_summary?.cash_pnl;
            const headline = cashPnl != null ? cashPnl : totalPnl.netTotal;
            const arbPnl = totalPnl.netTotal;
            const legacy = cashPnl != null ? cashPnl - arbPnl : null;
            const sub = cashPnl != null
              ? `Arb: $${arbPnl.toFixed(2)} | Legacy: $${legacy!.toFixed(2)}`
              : `${totalPnl.realizedWins}W / ${totalPnl.realizedLosses}L${totalPnl.openCount > 0 ? ` (${totalPnl.openCount} open)` : ""}`;
            return (
              <DashboardCard
                label="P&L (All)"
                value={`${headline < 0 ? "-" : ""}$${Math.abs(headline).toFixed(2)}`}
                accent={headline >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}
                sub={sub}
              />
            );
          })()}
          <DashboardCard
            label="Trades"
            value={`${totalPnl.fills}`}
            sub={`${totalPnl.count} attempts | ${activePositions.length} positions`}
            accent="text-[#00bfff]"
          />
          <DashboardCard
            label="Balances"
            value={`K: $${(state?.balances?.k_cash ?? 0).toFixed(0)} | PM: $${(state?.balances?.pm_cash ?? 0).toFixed(0)}`}
            sub={`K port: $${(state?.balances?.k_portfolio ?? 0).toFixed(2)} | PM port: $${(state?.balances?.pm_portfolio ?? 0).toFixed(2)}`}
          />
        </div>

        {/* ── Trade Category Breakdown ──────────────────────── */}
        {state?.trade_categories && (
          <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-[1px] bg-[#00bfff]/30" />
            <div className="flex items-center gap-0 divide-x divide-[#1a1a2e]">
              <div className="px-2 py-1.5 flex-shrink-0">
                <span className="text-[9px] font-mono uppercase tracking-widest text-[#4a4a6a]">TRADE BREAKDOWN</span>
              </div>
              {[
                { key: "arb_success", label: "ARB OK", color: "text-[#00ff88]", icon: "✓" },
                { key: "pm_no_fill", label: "NO FILL", color: "text-[#4a4a6a]", icon: "○" },
                { key: "exited", label: "EXITED", color: "text-[#ff8c00]", icon: "↩" },
                { key: "unhedged", label: "UNHEDGED", color: "text-[#ff3333]", icon: "▲" },
                { key: "directional", label: "DIR", color: "text-[#8b5cf6]", icon: "↗" },
              ].map(({ key, label, color, icon }) => {
                const cat = (state.trade_categories as Record<string, { count: number; pnl: number }>)?.[key];
                if (!cat) return null;
                return (
                  <div key={key} className="px-3 py-1.5 flex items-center gap-2">
                    <span className={`text-sm font-bold font-mono ${color}`}>{icon} {cat.count}</span>
                    <div>
                      <div className="text-[9px] text-[#4a4a6a] font-mono uppercase">{label}</div>
                      {cat.pnl !== 0 && (
                        <div className={`text-[9px] font-mono ${cat.pnl >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
                          {cat.pnl >= 0 ? "+" : ""}${cat.pnl.toFixed(2)}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── Trades Section ────────────────────────────────── */}
        <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#ff8c00]" />
          {/* Filter bar */}
          <div className="px-3 py-1.5 border-b border-[#1a1a2e] flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1">
              <button
                onClick={() => { setDateAll(false); setDateOffset((o: number) => o - 1); }}
                className="px-1 py-0.5 text-[9px] font-mono text-[#4a4a6a] hover:text-[#ff8c00]"
              >
                {"<"}
              </button>
              <button
                onClick={() => { setDateAll(false); setDateOffset(0); }}
                className={`px-2 py-0.5 text-[9px] font-mono border rounded-none transition-colors ${!dateAll && dateOffset === 0 ? "bg-[#ff8c00]/20 text-[#ff8c00] border-[#ff8c00]/40" : "text-[#4a4a6a] border-transparent hover:text-[#ff8c00]"}`}
              >
                {dateLabel}
              </button>
              <button
                onClick={() => { setDateAll(false); setDateOffset((o: number) => Math.min(o + 1, 0)); }}
                className="px-1 py-0.5 text-[9px] font-mono text-[#4a4a6a] hover:text-[#ff8c00]"
              >
                {">"}
              </button>
              <FilterButton active={dateAll} onClick={() => setDateAll(!dateAll)}>ALL</FilterButton>
            </div>
            <span className="text-[#1a1a2e] font-mono">|</span>
            <div className="flex items-center gap-1">
              <FilterButton active={tradeFilter === "all"} onClick={() => setTradeFilter("all")}>ALL</FilterButton>
              <FilterButton active={tradeFilter === "live"} onClick={() => setTradeFilter("live")} variant="green">LIVE</FilterButton>
              <FilterButton active={tradeFilter === "paper"} onClick={() => setTradeFilter("paper")} variant="purple">PAPER</FilterButton>
            </div>
            <span className="text-[#1a1a2e] font-mono">|</span>
            <div className="flex items-center gap-1">
              {(["all", "SUCCESS", "PM_NO_FILL", "EXITED", "UNHEDGED", "DIRECTIONAL"] as const).map((s) => (
                <FilterButton key={s} active={statusFilter === s} onClick={() => setStatusFilter(s)}>
                  {s === "all" ? "ALL" : s === "PM_NO_FILL" ? "NO FILL" : s === "DIRECTIONAL" ? "DIR" : s}
                </FilterButton>
              ))}
            </div>
            <input
              type="text"
              placeholder="Search team..."
              value={tradeSearch}
              onChange={(e) => setTradeSearch(e.target.value)}
              className="ml-auto bg-black border border-[#1a1a2e] rounded-none px-2 py-0.5 text-[9px] font-mono text-[#ff8c00] w-28 focus:outline-none focus:border-[#ff8c00]/40 placeholder-[#3a3a5a]"
            />
            <span className={`text-[10px] font-mono ${filteredPnl.netTotal >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
              ${filteredPnl.netTotal.toFixed(2)} <span className="text-[#4a4a6a]">({filteredPnl.fills} fills)</span>
            </span>
          </div>

          <TradeLog
            trades={filteredTrades}
            expandedTrade={expandedMonitorTrade}
            setExpandedTrade={setExpandedMonitorTrade}
          />
        </div>

        {/* ── Positions ────────────────────────────────────── */}
        <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#ff8c00]" />
          <div className="px-3 py-1.5 border-b border-[#1a1a2e]">
            <h3 className="text-[9px] font-mono uppercase tracking-widest text-[#4a4a6a]">
              POSITIONS <span className="text-[#ff8c00] ml-1">({activePositions.length})</span>
            </h3>
          </div>
          <PositionsTable positions={activePositions} markSettled={markSettled} />
        </div>
      </div>
    </div>
  );
}
