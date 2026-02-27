"use client";

import React from "react";
import type { ArbDataReturn } from "../hooks/useArbData";
import { DashboardCard } from "../shared/DashboardCard";
import { FilterButton } from "../shared/FilterButton";
import { TradeLog } from "../panels/TradeLog";
import { PositionsTable } from "../panels/PositionsTable";
import { MappedGamesTable } from "../panels/MappedGamesTable";

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
    expandedMonitorTrade,
    setExpandedMonitorTrade,
    markSettled,
  } = data;

  return (
    <div className="p-3 space-y-2">
      {/* ── Metrics Row ──────────────────────────────────────── */}
      <div className="grid grid-cols-6 gap-2">
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
          label="Spreads"
          value={`${sortedSpreads.filter((s) => Math.max(s.spread_buy_pm, s.spread_buy_k) >= 4).length}`}
          sub={`${state?.spreads?.length ?? 0} total monitored`}
          accent="text-[#00ff88]"
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

      {/* ── Trade Category Breakdown — horizontal ticker tape ──────── */}
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

      {/* ── Trades Section ────────────────────────────────────── */}
      <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#ff8c00]" />
        {/* Filter bar */}
        <div className="px-3 py-1.5 border-b border-[#1a1a2e] flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1">
            <button
              onClick={() => { setDateAll(false); setDateOffset((o) => o - 1); }}
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
              onClick={() => { setDateAll(false); setDateOffset((o) => Math.min(o + 1, 0)); }}
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

      {/* ── Positions ────────────────────────────────────────── */}
      <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#ff8c00]" />
        <div className="px-3 py-1.5 border-b border-[#1a1a2e]">
          <h3 className="text-[9px] font-mono uppercase tracking-widest text-[#4a4a6a]">
            POSITIONS <span className="text-[#ff8c00] ml-1">({activePositions.length})</span>
          </h3>
        </div>
        <PositionsTable positions={activePositions} markSettled={markSettled} />
      </div>

      {/* ── Line Drops ───────────────────────────────────────── */}
      <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#00bfff]" />
        <div className="px-3 py-1.5 border-b border-[#1a1a2e] flex items-center justify-between">
          <div>
            <h3 className="text-[9px] font-mono uppercase tracking-widest text-[#ff8c00]">
              LINE DROP MONITOR
            </h3>
            <p className="text-[8px] font-mono text-[#3a3a5a] mt-0.5">
              Detecting new PM market lines and initial spread opportunities
            </p>
          </div>
          <span className="text-[8px] font-mono text-[#00bfff] border border-[#00bfff]/30 px-1.5 py-0.5">
            STANDBY
          </span>
        </div>
        {/* Column headers */}
        <div className="overflow-x-auto">
          <table className="w-full text-[9px] font-mono">
            <thead>
              <tr className="border-b border-[#1a1a2e] text-[#4a4a6a] uppercase tracking-wider">
                <th className="px-3 py-1.5 text-left font-medium">TIME</th>
                <th className="px-3 py-1.5 text-left font-medium">MARKET</th>
                <th className="px-3 py-1.5 text-center font-medium">OPENING BID/ASK</th>
                <th className="px-3 py-1.5 text-right font-medium">K PRICE</th>
                <th className="px-3 py-1.5 text-right font-medium">INITIAL SPREAD</th>
                <th className="px-3 py-1.5 text-center font-medium">STATUS</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={6} className="px-3 py-4 text-center">
                  <span className="text-[#3a3a5a] font-mono text-[9px]">
                    Monitoring for new line drops...
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Mapped Games ──────────────────────────────────────── */}
      <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#ff8c00]" />
        <div className="px-3 py-1.5 border-b border-[#1a1a2e]">
          <h3 className="text-[9px] font-mono uppercase tracking-widest text-[#4a4a6a]">
            MAPPED GAMES <span className="text-[#ff8c00] ml-1">({state?.mapped_games?.length ?? 0})</span>
          </h3>
        </div>
        <MappedGamesTable games={state?.mapped_games || []} />
      </div>
    </div>
  );
}
