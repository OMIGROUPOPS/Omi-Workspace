"use client";

import React, { useState, useMemo } from "react";
import type { TradeEntry } from "../types";
import { tradePnl, sportBadge, normPmCents, formatDateTime, netColor } from "../helpers";
import { TradeSpecs } from "./TradeLog";

interface Props {
  trades: TradeEntry[];
  expandedTrade: number | null;
  setExpandedTrade: (idx: number | null) => void;
}

export function SettledTrades({ trades, expandedTrade, setExpandedTrade }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  const stats = useMemo(() => {
    let totalPnl = 0;
    let wins = 0;
    let losses = 0;
    for (const t of trades) {
      const pnl = tradePnl(t);
      if (pnl.totalDollars != null) {
        totalPnl += pnl.totalDollars;
        if (pnl.totalDollars >= 0) wins++;
        else losses++;
      }
    }
    const total = wins + losses;
    const winRate = total > 0 ? ((wins / total) * 100).toFixed(0) : "0";
    return { totalPnl, wins, losses, winRate, total };
  }, [trades]);

  return (
    <div>
      {/* Collapsible header */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full px-3 py-1.5 bg-black border-b border-[#1a1a2e] flex items-center gap-3 text-[9px] font-mono hover:bg-[#00ff88]/[0.02] transition-colors"
      >
        <span className="text-[#00ff88]">{collapsed ? "▶" : "▼"}</span>
        <span className="text-[#4a4a6a] uppercase tracking-widest">SETTLED</span>
        <span className="text-[#ff8c00]">{trades.length} trades</span>
        <span className="text-[#1a1a2e]">|</span>
        <span className={`font-bold ${stats.totalPnl >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
          ${stats.totalPnl.toFixed(2)}
        </span>
        <span className="text-[#1a1a2e]">|</span>
        <span className="text-[#4a4a6a]">{stats.winRate}% win rate</span>
      </button>

      {!collapsed && (
        <>
          {trades.length === 0 ? (
            <div className="p-4 text-center text-[10px] font-mono text-[#3a3a5a]">
              NO SETTLED TRADES
            </div>
          ) : (
            <div className="overflow-x-auto" style={{ maxHeight: "400px" }}>
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
                  <tr className="text-[#4a4a6a]">
                    <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">GAME</th>
                    <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">TEAM</th>
                    <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">K @</th>
                    <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">PM @</th>
                    <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">COMBINED</th>
                    <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">NET P&L</th>
                    <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">SETTLED</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((t, i) => {
                    const pnl = tradePnl(t);
                    const isExpanded = expandedTrade === i;
                    const isOdd = i % 2 === 1;
                    const kCents = typeof t.k_price === "number" ? t.k_price : 0;
                    const pmCents = normPmCents(t.pm_price);
                    const combined = kCents + pmCents;

                    return (
                      <React.Fragment key={`${t.timestamp}-${t.team}-${i}`}>
                        <tr
                          className={`border-b border-[#1a1a2e]/50 hover:bg-[#00ff88]/[0.04] cursor-pointer transition-colors ${isOdd ? "bg-white/[0.02]" : ""}`}
                          onClick={() => setExpandedTrade(isExpanded ? null : i)}
                        >
                          <td className="px-2 py-1.5 whitespace-nowrap">
                            <span className={`inline-block rounded-none px-1 py-0.5 text-[8px] font-mono mr-1 ${sportBadge(t.sport)}`}>
                              {t.sport}
                            </span>
                          </td>
                          <td className="px-2 py-1.5 whitespace-nowrap">
                            <span className="font-bold font-mono text-[#ff8c00]">{t.team_full_name || t.team}</span>
                            {(t.opponent_full_name || t.opponent) ? (
                              <span className="text-[#4a4a6a] font-mono text-[10px] ml-1">vs {t.opponent_full_name || t.opponent}</span>
                            ) : null}
                          </td>
                          <td className="px-2 py-1.5 text-right font-mono text-[#00bfff]">
                            {kCents > 0 ? `${kCents}c` : "—"}
                          </td>
                          <td className="px-2 py-1.5 text-right font-mono text-[#00ff88]">
                            {pmCents > 0 ? `${pmCents.toFixed(0)}c` : "—"}
                          </td>
                          <td className="px-2 py-1.5 text-right font-mono text-[#ff8c00]">
                            {combined > 0 ? `${combined.toFixed(0)}c` : "—"}
                          </td>
                          <td className={`px-2 py-1.5 text-right font-mono font-bold ${
                            pnl.totalDollars === null ? "text-[#4a4a6a]" : netColor(pnl.totalDollars)
                          }`}>
                            {pnl.totalDollars !== null ? `$${pnl.totalDollars.toFixed(4)}` : "—"}
                          </td>
                          <td className="px-2 py-1.5 text-right font-mono text-[#4a4a6a] text-[10px]">
                            {t.settlement_time ? formatDateTime(t.settlement_time) : "—"}
                          </td>
                        </tr>
                        {isExpanded && (
                          <tr className="bg-[#0a0a12]">
                            <td colSpan={7} className="px-4 py-3">
                              <TradeSpecs t={t} />
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
