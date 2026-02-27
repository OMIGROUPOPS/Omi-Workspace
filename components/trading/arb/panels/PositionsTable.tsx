"use client";

import React from "react";
import type { Position } from "../types";
import { sportBadge, timeAgo } from "../helpers";

interface Props {
  positions: Position[];
  markSettled: (gameId: string) => void;
}

export function PositionsTable({ positions, markSettled }: Props) {
  if (positions.length === 0) {
    return (
      <div className="text-center py-6">
        <span className="text-xs text-gray-600">No open positions</span>
      </div>
    );
  }

  const hedged = positions.filter((p) => p.hedged);
  const unhedged = positions.filter((p) => !p.hedged);
  const totPmExp = positions.reduce((s, p) => s + p.pm_cost_dollars, 0);
  const totKExp = positions.reduce((s, p) => s + p.k_cost_dollars, 0);
  const totPnl = positions.reduce((s, p) => s + p.unrealised_pnl, 0);

  return (
    <div>
      {/* Summary row */}
      <div className="px-3 py-2 bg-gray-800/30 border-b border-gray-800 flex flex-wrap items-center gap-4 text-[10px]">
        <span className="text-gray-400">
          {positions.length} position{positions.length !== 1 ? "s" : ""}
          {hedged.length > 0 && <span className="text-emerald-500 ml-1">({hedged.length} hedged)</span>}
          {unhedged.length > 0 && <span className="text-red-400 ml-1">({unhedged.length} directional)</span>}
        </span>
        <span className="text-blue-400">PM: ${totPmExp.toFixed(2)}</span>
        <span className="text-orange-400">K: ${totKExp.toFixed(2)}</span>
        <span className={`font-mono font-bold ${totPnl > 0 ? "text-emerald-400" : totPnl < 0 ? "text-red-400" : "text-gray-400"}`}>
          P&L: {totPnl >= 0 ? "+" : ""}${totPnl.toFixed(4)}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr className="text-gray-500 text-[9px] uppercase tracking-wider border-b border-gray-800">
              <th className="py-2 px-2 text-left font-medium">Game</th>
              <th className="py-2 px-2 text-left font-medium">Team</th>
              <th className="py-2 px-2 text-center font-medium">Status</th>
              <th className="py-2 px-2 text-center font-medium">K Qty</th>
              <th className="py-2 px-2 text-center font-medium">PM Qty</th>
              <th className="py-2 px-2 text-right font-medium">PM Fill</th>
              <th className="py-2 px-2 text-right font-medium">PM Now</th>
              <th className="py-2 px-2 text-right font-medium">K Fill</th>
              <th className="py-2 px-2 text-right font-medium">K Now</th>
              <th className="py-2 px-2 text-right font-medium">Fees</th>
              <th className="py-2 px-2 text-right font-medium">Net P&L</th>
              <th className="py-2 px-2 text-center font-medium">Signal</th>
              <th className="py-2 px-2 text-center font-medium w-6"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/50">
            {positions.map((p, i) => {
              const pmDir = p.direction === "BUY_PM_SELL_K" ? "L" : p.direction === "BUY_K_SELL_PM" ? "S" : "?";
              const kDir = p.direction === "BUY_PM_SELL_K" ? "S" : p.direction === "BUY_K_SELL_PM" ? "L" : "?";
              const statusColor = p.hedged
                ? "bg-emerald-500/20 text-emerald-400"
                : p.status === "TIER3A_HOLD" ? "bg-yellow-500/20 text-yellow-400"
                : p.status === "TIER3_OPPOSITE_HEDGE" ? "bg-blue-500/20 text-blue-400"
                : p.status === "TIER3_OPPOSITE_OVERWEIGHT" ? "bg-cyan-500/20 text-cyan-400"
                : "bg-red-500/20 text-red-400";
              const statusLabel = p.hedged ? "HEDGED" : p.status;
              const pnlColor = p.unrealised_pnl > 0 ? "text-emerald-400" : p.unrealised_pnl < 0 ? "text-red-400" : "text-gray-400";
              const signalColor = p.signal === "MAX EDGE" ? "text-emerald-400"
                : p.signal === "HIGH EDGE" ? "text-blue-400"
                : p.signal === "MID EDGE" ? "text-yellow-400"
                : p.signal === "LOW EDGE" ? "text-orange-400"
                : "text-gray-500";

              return (
                <tr key={i} className={`hover:bg-gray-800/30 ${!p.hedged ? "bg-red-500/[0.02]" : ""}`}>
                  <td className="py-2 px-2">
                    <div className="flex items-center gap-1">
                      <span className={`inline-block rounded px-1 py-0.5 text-[8px] font-medium ${sportBadge(p.sport)}`}>{p.sport}</span>
                      <span className="text-gray-500 text-[10px] truncate max-w-[80px]" title={p.game_id}>{p.game_id}</span>
                    </div>
                    <div className="text-[9px] text-gray-600 mt-0.5">{timeAgo(p.timestamp)}</div>
                  </td>
                  <td className="py-2 px-2">
                    <span className="text-white font-medium">{p.team_full_name || p.team}</span>
                    {(p.opponent_full_name || p.opponent) ? (
                      <span className="text-gray-500 text-[10px] ml-1">vs {p.opponent_full_name || p.opponent}</span>
                    ) : null}
                  </td>
                  <td className="py-2 px-2 text-center">
                    <span className={`text-[9px] font-medium rounded px-1.5 py-0.5 ${statusColor}`}>{statusLabel}</span>
                  </td>
                  <td className="py-2 px-2 text-center font-mono">
                    <span className="text-blue-400">{p.kalshi_fill ?? (p.hedged ? p.contracts : 0)}x</span>
                    <div className="text-[9px] text-gray-600">@{p.k_fill_cents}c</div>
                  </td>
                  <td className="py-2 px-2 text-center font-mono">
                    <span className="text-emerald-400">{p.pm_fill_qty ?? p.contracts}x</span>
                    <div className="text-[9px] text-gray-600">@{p.pm_fill_cents.toFixed(1)}c</div>
                  </td>
                  <td className="py-2 px-2 text-right font-mono">
                    <span className="text-blue-300">{pmDir} {p.pm_fill_cents.toFixed(1)}c</span>
                    <div className="text-[9px] text-gray-600">${p.pm_cost_dollars.toFixed(2)}</div>
                  </td>
                  <td className="py-2 px-2 text-right font-mono">
                    {p.pm_bid_now > 0 ? (
                      <><span className="text-blue-400">{p.pm_bid_now.toFixed(1)}</span><span className="text-gray-600">/</span><span className="text-blue-400">{p.pm_ask_now.toFixed(1)}</span></>
                    ) : <span className="text-gray-600">{"\u2014"}</span>}
                  </td>
                  <td className="py-2 px-2 text-right font-mono">
                    {p.hedged ? (
                      <><span className="text-orange-300">{kDir} {p.k_fill_cents}c</span><div className="text-[9px] text-gray-600">${p.k_cost_dollars.toFixed(2)}</div></>
                    ) : <span className="text-gray-600">{"\u2014"}</span>}
                  </td>
                  <td className="py-2 px-2 text-right font-mono">
                    {p.hedged && p.k_bid_now > 0 ? (
                      <><span className="text-orange-400">{p.k_bid_now}</span><span className="text-gray-600">/</span><span className="text-orange-400">{p.k_ask_now}</span></>
                    ) : <span className="text-gray-600">{"\u2014"}</span>}
                  </td>
                  <td className="py-2 px-2 text-right font-mono text-gray-400">
                    {p.total_fees > 0 ? `${(p.total_fees * 100 / p.contracts).toFixed(1)}c` : "\u2014"}
                    {p.total_fees > 0 && <div className="text-[9px] text-gray-600">${p.total_fees.toFixed(3)}</div>}
                  </td>
                  <td className={`py-2 px-2 text-right font-mono font-bold ${pnlColor}`}>
                    {p.unrealised_pnl >= 0 ? "+" : ""}${p.unrealised_pnl.toFixed(4)}
                    {p.hedged && p.spread_cents > 0 && <div className="text-[9px] text-gray-600 font-normal">{p.spread_cents.toFixed(1)}c spread</div>}
                  </td>
                  <td className="py-2 px-2 text-center">
                    {p.signal ? (
                      <div>
                        <span className={`text-[9px] font-medium ${signalColor}`}>{p.signal}</span>
                        {p.ceq !== null && <div className="text-[9px] text-gray-600">{p.ceq.toFixed(1)}%</div>}
                      </div>
                    ) : <span className="text-gray-600">{"\u2014"}</span>}
                  </td>
                  <td className="py-2 px-2 text-center">
                    <button onClick={() => markSettled(p.game_id)} className="text-[9px] text-gray-600 hover:text-gray-400" title="Hide">
                      {"\u2715"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
