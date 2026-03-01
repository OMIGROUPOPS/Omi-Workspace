"use client";

import React, { useMemo } from "react";
import type { TradeEntry } from "../types";
import { tradePnl } from "../helpers";

interface Props {
  settledTrades: TradeEntry[];
  totalPnl: number;
}

export function PnlBox({ settledTrades, totalPnl }: Props) {
  const stats = useMemo(() => {
    let wins = 0;
    let losses = 0;
    let sum = 0;
    for (const t of settledTrades) {
      const pnl = tradePnl(t);
      if (pnl.totalDollars != null) {
        sum += pnl.totalDollars;
        if (pnl.totalDollars >= 0) wins++;
        else losses++;
      }
    }
    const total = wins + losses;
    const winRate = total > 0 ? ((wins / total) * 100).toFixed(0) : "0";
    const avg = total > 0 ? sum / total : 0;
    return { wins, losses, winRate, avg, total, sum };
  }, [settledTrades]);

  if (stats.total === 0) return null;

  return (
    <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-[#00ff88]/30" />
      <div className="flex items-center gap-0 divide-x divide-[#1a1a2e]">
        <div className="px-2 py-1.5 flex-shrink-0">
          <span className="text-[9px] font-mono uppercase tracking-widest text-[#4a4a6a]">REALIZED P&L</span>
        </div>
        <div className="px-3 py-1.5">
          <span className={`text-sm font-bold font-mono ${totalPnl >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
            ${totalPnl.toFixed(2)}
          </span>
        </div>
        <div className="px-3 py-1.5">
          <span className="text-[#00ff88] font-mono font-bold">{stats.wins}W</span>
          <span className="text-[#3a3a5a] font-mono mx-1">/</span>
          <span className="text-[#ff3333] font-mono font-bold">{stats.losses}L</span>
        </div>
        <div className="px-3 py-1.5">
          <span className="text-[9px] text-[#4a4a6a] font-mono uppercase mr-1">Win Rate</span>
          <span className="text-[#ff8c00] font-mono font-bold">{stats.winRate}%</span>
        </div>
        <div className="px-3 py-1.5">
          <span className="text-[9px] text-[#4a4a6a] font-mono uppercase mr-1">Avg/Trade</span>
          <span className={`font-mono font-bold ${stats.avg >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
            ${stats.avg.toFixed(4)}
          </span>
        </div>
      </div>
    </div>
  );
}
