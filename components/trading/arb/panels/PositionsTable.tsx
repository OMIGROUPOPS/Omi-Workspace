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
        <span className="text-[9px] font-mono text-[#3a3a5a] uppercase tracking-wider">NO OPEN POSITIONS</span>
      </div>
    );
  }

  const hedged = positions.filter((p) => p.hedged);
  const unhedged = positions.filter((p) => !p.hedged);
  const totExposure = positions.reduce((s, p) => s + p.pm_cost_dollars + p.k_cost_dollars, 0);
  const totPnl = positions.reduce((s, p) => s + p.unrealised_pnl, 0);

  return (
    <div>
      {/* Summary row */}
      <div className="px-3 py-1.5 bg-black border-b border-[#1a1a2e] flex flex-wrap items-center gap-4 text-[9px] font-mono">
        <span className="text-[#4a4a6a]">
          {positions.length} POSITION{positions.length !== 1 ? "S" : ""}
          {hedged.length > 0 && <span className="text-[#00ff88] ml-1">({hedged.length} HEDGED)</span>}
          {unhedged.length > 0 && <span className="text-[#ff3333] ml-1">({unhedged.length} DIRECTIONAL)</span>}
        </span>
        <span className="text-[#4a4a6a]">|</span>
        <span className="text-[#ff8c00]">Exposure: ${totExposure.toFixed(2)}</span>
        <span className={`font-mono font-bold ${totPnl > 0 ? "text-[#00ff88]" : totPnl < 0 ? "text-[#ff3333]" : "text-[#4a4a6a]"}`}>
          P&L: {totPnl >= 0 ? "+" : ""}${totPnl.toFixed(4)}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr className="text-[#4a4a6a] text-[9px] uppercase tracking-wider border-b border-[#1a1a2e] font-mono">
              <th className="py-1.5 px-2 text-left font-medium">GAME</th>
              <th className="py-1.5 px-2 text-left font-medium">TEAM</th>
              <th className="py-1.5 px-2 text-center font-medium">STATUS</th>
              <th className="py-1.5 px-2 text-center font-medium">QTY</th>
              <th className="py-1.5 px-2 text-right font-medium">EXPOSURE</th>
              <th className="py-1.5 px-2 text-right font-medium">NET P&L</th>
              <th className="py-1.5 px-2 text-center font-medium w-6"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1a1a2e]/50">
            {positions.map((p, i) => {
              const statusColor = p.hedged
                ? "bg-[#00ff88]/10 text-[#00ff88] border-[#00ff88]/30"
                : p.status === "TIER3A_HOLD" ? "bg-[#ff8c00]/10 text-[#ff8c00] border-[#ff8c00]/30"
                : p.status === "TIER3_OPPOSITE_HEDGE" ? "bg-[#00bfff]/10 text-[#00bfff] border-[#00bfff]/30"
                : p.status === "TIER3_OPPOSITE_OVERWEIGHT" ? "bg-[#00bfff]/10 text-[#00bfff] border-[#00bfff]/30"
                : "bg-[#ff3333]/10 text-[#ff3333] border-[#ff3333]/30";
              const statusLabel = p.hedged ? "HEDGED" : p.status;
              const pnlColor = p.unrealised_pnl > 0 ? "text-[#00ff88]" : p.unrealised_pnl < 0 ? "text-[#ff3333]" : "text-[#4a4a6a]";
              const exposure = p.pm_cost_dollars + p.k_cost_dollars;
              const kQty = p.kalshi_fill ?? (p.hedged ? p.contracts : 0);
              const pmQty = p.pm_fill_qty ?? p.contracts;

              return (
                <tr key={i} className={`hover:bg-[#ff8c00]/[0.03] transition-colors font-mono ${!p.hedged ? "bg-[#ff3333]/[0.02]" : ""}`}>
                  <td className="py-1.5 px-2">
                    <div className="flex items-center gap-1">
                      <span className={`inline-block rounded-none px-1 py-0.5 text-[8px] font-medium ${sportBadge(p.sport)}`}>{p.sport}</span>
                      <span className="text-[#4a4a6a] text-[9px] truncate max-w-[80px]" title={p.game_id}>{p.game_id}</span>
                    </div>
                    <div className="text-[8px] text-[#3a3a5a] mt-0.5">{timeAgo(p.timestamp)}</div>
                  </td>
                  <td className="py-1.5 px-2">
                    <span className="text-[#ff8c00] font-medium">{p.team_full_name || p.team}</span>
                    {(p.opponent_full_name || p.opponent) ? (
                      <span className="text-[#4a4a6a] text-[9px] ml-1">vs {p.opponent_full_name || p.opponent}</span>
                    ) : null}
                  </td>
                  <td className="py-1.5 px-2 text-center">
                    <span className={`text-[9px] font-medium rounded-none border px-1.5 py-0.5 ${statusColor}`}>{statusLabel}</span>
                  </td>
                  <td className="py-1.5 px-2 text-center font-mono">
                    <span className="text-[#00bfff]">K:{kQty}</span>
                    <span className="text-[#3a3a5a] mx-0.5">/</span>
                    <span className="text-[#00ff88]">PM:{pmQty}</span>
                  </td>
                  <td className="py-1.5 px-2 text-right font-mono text-[#ff8c00]">
                    ${exposure.toFixed(2)}
                  </td>
                  <td className={`py-1.5 px-2 text-right font-mono font-bold ${pnlColor}`}>
                    {p.unrealised_pnl >= 0 ? "+" : ""}${p.unrealised_pnl.toFixed(4)}
                    {(p as any).arb_net_cents_per_contract != null ? (
                      <div className={`text-[9px] font-normal ${(p as any).arb_net_cents_per_contract < 0 ? 'text-[#ff3333]' : 'text-[#00ff88]'}`}>
                        {(p as any).arb_net_cents_per_contract}c/ct
                      </div>
                    ) : p.hedged && p.spread_cents > 0 ? (
                      <div className="text-[9px] text-[#3a3a5a] font-normal">{p.spread_cents.toFixed(1)}c spread</div>
                    ) : null}
                  </td>
                  <td className="py-1.5 px-2 text-center">
                    <button onClick={() => markSettled(p.game_id)} className="text-[9px] text-[#3a3a5a] hover:text-[#ff3333] font-mono transition-colors" title="Hide">
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
