"use client";

import React from "react";
import type { Balances, Position, TradeEntry } from "../types";

interface Props {
  balances: Balances | undefined;
  positions: Position[];
  totalPnl: { netTotal: number; totalFees: number };
}

export function PnlSummaryBar({ balances, positions, totalPnl }: Props) {
  const currentBalance = balances?.total_portfolio ?? 0;
  const realizedPnl = totalPnl.netTotal;
  const unrealizedPnl = positions.reduce((sum, p) => sum + (p.unrealised_pnl || 0), 0);
  const feesPaid = totalPnl.totalFees;
  const netPnl = realizedPnl + unrealizedPnl;
  const startingBalance = currentBalance - netPnl;
  const reconciles = Math.abs(startingBalance + netPnl - currentBalance) < 0.05;

  const items = [
    { label: "Starting", value: startingBalance, color: "text-gray-300" },
    { label: "Current", value: currentBalance, color: "text-white" },
    { label: "Realized", value: realizedPnl, color: realizedPnl >= 0 ? "text-emerald-400" : "text-red-400" },
    { label: "Unrealized", value: unrealizedPnl, color: unrealizedPnl >= 0 ? "text-emerald-400" : "text-red-400" },
    { label: "Fees", value: -feesPaid, color: "text-yellow-400" },
    { label: "Net P&L", value: netPnl, color: netPnl >= 0 ? "text-emerald-400" : "text-red-400" },
  ];

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <div className="flex items-center gap-2 mb-2">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          P&L Reconciliation
        </h3>
        <span className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium ${
          reconciles ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
        }`}>
          {reconciles ? "Reconciled" : "Mismatch"}
        </span>
      </div>
      <div className="grid grid-cols-6 gap-3">
        {items.map((item) => (
          <div key={item.label}>
            <p className="text-[10px] text-gray-500 uppercase">{item.label}</p>
            <p className={`text-sm font-bold font-mono ${item.color}`}>
              ${Math.abs(item.value).toFixed(2)}
              {item.label !== "Starting" && item.label !== "Current" && (
                <span className="text-[10px] ml-0.5">
                  {item.value >= 0 ? "" : "-"}
                </span>
              )}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
