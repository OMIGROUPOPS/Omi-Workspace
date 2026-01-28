"use client";

import type { Trade } from "@/lib/trading/types";
import StatusBadge from "./StatusBadge";

interface TradeRowProps {
  trade: Trade;
  index: number;
  isExpanded: boolean;
  onToggle: (index: number | null) => void;
}

export default function TradeRow({ trade, index, isExpanded, onToggle }: TradeRowProps) {
  const dir = trade.direction === "BUY_PM_SELL_K" ? "PM\u2192K" : "K\u2192PM";
  const dirColor = trade.direction === "BUY_PM_SELL_K" ? "text-cyan-400" : "text-violet-400";

  return (
    <>
      <tr
        onClick={() => onToggle(isExpanded ? null : index)}
        className={`table-row border-b border-slate-800/20 cursor-pointer transition-colors
          ${isExpanded ? "bg-slate-800/20" : ""}`}
      >
        <td className="px-3 py-2 font-mono text-slate-500 tabular-nums whitespace-nowrap">
          {new Date(trade.timestamp).toLocaleTimeString("en-US", { hour12: false })}
        </td>
        <td className="px-3 py-2">
          <StatusBadge trade={trade} />
        </td>
        <td className="px-3 py-2">
          <span className="font-mono font-bold text-slate-200">{trade.team}</span>
          <span className="text-slate-700 ml-1.5 text-[10px]">{trade.game}</span>
        </td>
        <td className={`px-3 py-2 font-mono font-bold text-[10px] ${dirColor}`}>{dir}</td>
        <td className="px-3 py-2 text-right font-mono text-slate-300 tabular-nums">
          {trade.k_fill_count}
        </td>
        <td className={`px-3 py-2 text-right font-mono font-bold tabular-nums
          ${trade.expected_profit >= 0 ? "text-emerald-400" : "text-red-400"}`}>
          {trade.expected_profit >= 0 ? "+" : ""}${trade.expected_profit.toFixed(2)}
        </td>
        <td className={`px-3 py-2 text-right font-mono tabular-nums
          ${trade.roi > 0 ? "text-emerald-400" : "text-slate-600"}`}>
          {trade.roi ? `${trade.roi.toFixed(1)}%` : "\u2014"}
        </td>
      </tr>
      {isExpanded && (
        <tr>
          <td colSpan={7} className="px-0 py-0">
            <div className="mx-2 mb-2 p-3 bg-slate-900/60 border border-slate-800/50 rounded-b text-[10px] font-mono">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-2">
                <div>
                  <span className="text-slate-600">Timestamp</span>
                  <div className="text-slate-300">{new Date(trade.timestamp).toISOString()}</div>
                </div>
                <div>
                  <span className="text-slate-600">Sport</span>
                  <div className="text-slate-300">{trade.sport}</div>
                </div>
                <div>
                  <span className="text-slate-600">Direction</span>
                  <div className="text-slate-300">{trade.direction}</div>
                </div>
                <div>
                  <span className="text-slate-600">Intended Size</span>
                  <div className="text-slate-300">{trade.intended_size}</div>
                </div>
                <div>
                  <span className="text-slate-600">K Fill Price</span>
                  <div className="text-cyan-400">{trade.k_fill_price ? `${trade.k_fill_price}\u00A2` : "\u2014"}</div>
                </div>
                <div>
                  <span className="text-slate-600">K Order ID</span>
                  <div className="text-slate-400 truncate max-w-[160px]">{trade.k_order_id || "\u2014"}</div>
                </div>
                <div>
                  <span className="text-slate-600">PM Fill</span>
                  <div className={trade.pm_success ? "text-emerald-400" : "text-red-400"}>
                    {trade.pm_fill_count !== undefined
                      ? `${trade.pm_fill_count} @ $${trade.pm_fill_price?.toFixed(2) ?? "\u2014"}`
                      : trade.pm_success ? "OK" : trade.pm_error || "\u2014"}
                  </div>
                </div>
                <div>
                  <span className="text-slate-600">PM Slug</span>
                  <div className="text-violet-400 truncate max-w-[160px]">{trade.pm_slug || trade.pm_order_id || "\u2014"}</div>
                </div>
                <div>
                  <span className="text-slate-600">Exec Mode</span>
                  <div className={trade.execution_mode === "live" ? "text-red-400" : "text-blue-400"}>
                    {trade.execution_mode?.toUpperCase() || "\u2014"}
                  </div>
                </div>
                <div>
                  <span className="text-slate-600">Raw Status</span>
                  <div className="text-slate-300">{trade.raw_status || trade.status}</div>
                </div>
                {trade.pm_error && (
                  <div className="col-span-2">
                    <span className="text-slate-600">PM Error</span>
                    <div className="text-red-400">{trade.pm_error}</div>
                  </div>
                )}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
