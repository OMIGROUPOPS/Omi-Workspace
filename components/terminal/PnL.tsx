"use client";

// OMNI Terminal — P&L panel
// Session P&L and strategy breakdown.
// TODO: Full implementation with sparkline chart and per-strategy rows.

import type { PnLBreakdown } from "@/lib/terminal/types";

interface PnLProps {
  totalPnl?: number;
  breakdowns?: PnLBreakdown[];
  openTrades?: number;
}

export default function PnL({ totalPnl = 0, breakdowns = [], openTrades = 0 }: PnLProps) {
  const pnlColor = totalPnl > 0 ? "text-emerald-400" : totalPnl < 0 ? "text-red-400" : "text-zinc-400";

  return (
    <div className="h-full flex flex-col">
      {/* Total */}
      <div className="mb-3">
        <div className="text-[10px] text-zinc-600 uppercase tracking-wider">Session P&L</div>
        <div className={`text-2xl font-bold tabular-nums ${pnlColor}`}>
          {totalPnl >= 0 ? "+" : ""}{(totalPnl / 100).toFixed(2)}
          <span className="text-sm text-zinc-600 ml-1">USD</span>
        </div>
        <div className="text-[10px] text-zinc-600 mt-0.5">{openTrades} open</div>
      </div>

      {/* Strategy breakdown */}
      <div className="flex-1 overflow-y-auto space-y-1">
        {breakdowns.length === 0 ? (
          <div className="text-zinc-700 text-xs">No trades yet</div>
        ) : (
          breakdowns.map((b) => {
            const c = b.total_pnl > 0 ? "text-emerald-400" : b.total_pnl < 0 ? "text-red-400" : "text-zinc-500";
            return (
              <div key={b.scan_type} className="flex items-center justify-between text-[10px] px-1">
                <span className="text-zinc-400">{b.scan_type.replace("_", " ")}</span>
                <div className="flex items-center gap-3">
                  <span className="text-zinc-600">{b.trade_count}t W{b.winners}/L{b.losers}</span>
                  <span className={`tabular-nums font-medium ${c}`}>
                    {b.total_pnl >= 0 ? "+" : ""}{b.total_pnl}¢
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
