"use client";

import { useState, useMemo } from "react";
import type { Trade, TradeFilter, SortField, FullAnalytics } from "@/lib/trading/types";
import TradeRow from "../shared/TradeRow";
import ScatterPlot from "../charts/ScatterPlot";
import Panel from "../shared/Panel";

interface TradesTabProps {
  trades: Trade[];
  analytics: FullAnalytics;
}

export default function TradesTab({ trades, analytics }: TradesTabProps) {
  const [tradeFilter, setTradeFilter] = useState<TradeFilter>("all");
  const [sortField, setSortField] = useState<SortField>("timestamp");
  const [sortAsc, setSortAsc] = useState(false);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const filteredTrades = useMemo(() => {
    let result = trades.filter((t) => {
      if (tradeFilter === "all") return true;
      if (tradeFilter === "live") return t.execution_mode === "live" && t.status === "SUCCESS";
      if (tradeFilter === "paper") return t.execution_mode === "paper" || t.status === "PAPER";
      if (tradeFilter === "failed")
        return t.status === "NO_FILL" || t.status === "UNHEDGED" || t.status === "FAILED";
      return true;
    });

    result = [...result].sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case "timestamp": cmp = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(); break;
        case "profit": cmp = a.expected_profit - b.expected_profit; break;
        case "roi": cmp = a.roi - b.roi; break;
        case "status": cmp = a.status.localeCompare(b.status); break;
        case "team": cmp = a.team.localeCompare(b.team); break;
      }
      return sortAsc ? cmp : -cmp;
    });

    return result;
  }, [trades, tradeFilter, sortField, sortAsc]);

  const handleSort = (field: SortField) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else { setSortField(field); setSortAsc(false); }
  };

  const bestTrade = useMemo(() => {
    const successful = trades.filter((t) => t.status === "SUCCESS" || t.status === "PAPER");
    if (successful.length === 0) return null;
    return successful.reduce((best, t) => t.expected_profit > best.expected_profit ? t : best);
  }, [trades]);

  const worstTrade = useMemo(() => {
    const successful = trades.filter((t) => t.status === "SUCCESS" || t.status === "PAPER");
    if (successful.length === 0) return null;
    return successful.reduce((worst, t) => t.expected_profit < worst.expected_profit ? t : worst);
  }, [trades]);

  return (
    <div className="flex gap-2 h-full min-h-0">
      {/* Main trade table */}
      <div className="flex-1 flex flex-col min-h-0">
        <Panel
          title="Trades"
          className="flex-1 flex flex-col min-h-0"
          headerRight={
            <div className="flex gap-0.5 bg-slate-800/40 p-0.5 rounded">
              {(["all", "live", "paper", "failed"] as TradeFilter[]).map((key) => {
                const count =
                  key === "all" ? trades.length :
                  key === "live" ? analytics.liveTrades.length :
                  key === "paper" ? analytics.paperTrades.length :
                  analytics.failedTrades.length;
                const active = tradeFilter === key;
                return (
                  <button
                    key={key}
                    onClick={() => setTradeFilter(key)}
                    className={`px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded transition-all
                      ${active
                        ? key === "live" ? "bg-emerald-500/15 text-emerald-400"
                          : key === "paper" ? "bg-amber-500/15 text-amber-400"
                          : key === "failed" ? "bg-red-500/15 text-red-400"
                          : "bg-slate-700/60 text-slate-200"
                        : "text-slate-600 hover:text-slate-400"}`}
                  >
                    {key} <span className="opacity-50">{count}</span>
                  </button>
                );
              })}
            </div>
          }
        >
          <div className="flex-1 overflow-y-auto scrollbar-thin min-h-0">
            {filteredTrades.length === 0 ? (
              <div className="px-3 py-10 text-center text-[11px] text-slate-700 font-mono">
                {trades.length === 0 ? "NO TRADES RECORDED" : `NO ${tradeFilter.toUpperCase()} TRADES`}
              </div>
            ) : (
              <table className="w-full text-[11px]">
                <thead className="sticky top-0 bg-[#0c1018] z-10">
                  <tr className="text-slate-600 text-left border-b border-slate-800/50">
                    {([
                      { field: "timestamp" as SortField, label: "Time", align: "left" },
                      { field: "status" as SortField, label: "Status", align: "left" },
                      { field: "team" as SortField, label: "Team", align: "left" },
                      { field: "team" as SortField, label: "Direction", align: "left" },
                      { field: "team" as SortField, label: "Size", align: "right" },
                      { field: "profit" as SortField, label: "P&L", align: "right" },
                      { field: "roi" as SortField, label: "ROI", align: "right" },
                    ]).map(({ field, label, align }, idx) => (
                      <th
                        key={idx}
                        onClick={() => handleSort(field)}
                        className={`px-3 py-2 font-medium text-[9px] uppercase tracking-widest cursor-pointer
                          hover:text-slate-400 transition-colors select-none
                          ${align === "right" ? "text-right" : ""}`}
                      >
                        {label}
                        {sortField === field && (
                          <span className="ml-0.5 text-cyan-500">{sortAsc ? "\u25B2" : "\u25BC"}</span>
                        )}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredTrades.map((trade, i) => (
                    <TradeRow
                      key={i}
                      trade={trade}
                      index={i}
                      isExpanded={expandedRow === i}
                      onToggle={setExpandedRow}
                    />
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </Panel>

        {/* Scatter plot */}
        <Panel title="Trade Timeline" className="mt-2">
          <div className="px-3 py-2 flex justify-center">
            <ScatterPlot trades={trades} width={600} height={160} />
          </div>
        </Panel>
      </div>

      {/* Analytics sidebar */}
      <div className="w-[200px] flex-shrink-0 flex flex-col gap-2">
        <Panel title="Analytics">
          <div className="p-3 space-y-2 text-[11px]">
            {[
              { label: "Win Rate", value: `${analytics.winRate.toFixed(1)}%`, color: analytics.winRate >= 50 ? "text-emerald-400" : "text-amber-400" },
              { label: "Avg Profit", value: `$${analytics.avgProfit.toFixed(2)}`, color: analytics.avgProfit >= 0 ? "text-emerald-400" : "text-red-400" },
              { label: "Sharpe", value: analytics.sharpe.toFixed(2), color: analytics.sharpe >= 1 ? "text-emerald-400" : "text-amber-400" },
              { label: "Total P&L", value: `$${analytics.totalPnL.toFixed(2)}`, color: analytics.totalPnL >= 0 ? "text-emerald-400" : "text-red-400" },
              { label: "Fill Rate", value: `${analytics.fillRate.toFixed(0)}%`, color: analytics.fillRate >= 50 ? "text-emerald-400" : "text-slate-500" },
            ].map(({ label, value, color }) => (
              <div key={label} className="flex items-center justify-between py-1">
                <span className="text-slate-600">{label}</span>
                <span className={`font-mono tabular-nums font-bold ${color}`}>{value}</span>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Best Trade">
          <div className="p-3 text-[11px] font-mono">
            {bestTrade ? (
              <>
                <div className="text-emerald-400 font-bold">+${bestTrade.expected_profit.toFixed(2)}</div>
                <div className="text-slate-500 text-[10px]">{bestTrade.team}</div>
                <div className="text-slate-700 text-[9px]">{bestTrade.sport}</div>
              </>
            ) : (
              <div className="text-slate-700">{"\u2014"}</div>
            )}
          </div>
        </Panel>

        <Panel title="Worst Trade">
          <div className="p-3 text-[11px] font-mono">
            {worstTrade ? (
              <>
                <div className="text-red-400 font-bold">${worstTrade.expected_profit.toFixed(2)}</div>
                <div className="text-slate-500 text-[10px]">{worstTrade.team}</div>
                <div className="text-slate-700 text-[9px]">{worstTrade.sport}</div>
              </>
            ) : (
              <div className="text-slate-700">{"\u2014"}</div>
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
}
