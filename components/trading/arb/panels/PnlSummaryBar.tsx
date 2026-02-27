"use client";

import React from "react";
import type { Balances, Position, PnlSummary } from "../types";

const STARTING_BALANCE = 910.31;

interface Props {
  balances: Balances | undefined;
  positions: Position[];
  totalPnl: { netTotal: number; totalFees: number };
  pnlSummary?: PnlSummary;
  isStale?: boolean;
}

export function PnlSummaryBar({ balances, positions, totalPnl, pnlSummary, isStale }: Props) {
  const startingBalance = pnlSummary?.starting_balance ?? STARTING_BALANCE;
  const currentBalance = pnlSummary?.portfolio_total ?? balances?.total_portfolio ?? 0;
  const cashPnl = pnlSummary?.cash_pnl ?? (currentBalance - startingBalance);
  const realizedPnl = totalPnl.netTotal;
  const unrealizedPnl = positions.reduce((sum, p) => sum + (p.unrealised_pnl || 0), 0);
  const feesPaid = totalPnl.totalFees;
  const recon = pnlSummary?.reconciliation;

  // Cash P&L is the single source of truth
  const netPnl = cashPnl;
  const reconciles = currentBalance > 0 && Math.abs(startingBalance + netPnl - currentBalance) < 0.10;

  const items = [
    { label: "Starting", value: startingBalance, color: "text-gray-300" },
    { label: "Current", value: currentBalance, color: "text-white" },
    { label: "Arb P&L", value: realizedPnl, color: realizedPnl >= 0 ? "text-emerald-400" : "text-red-400" },
    { label: "Unrealized", value: unrealizedPnl, color: unrealizedPnl >= 0 ? "text-emerald-400" : "text-red-400" },
    { label: "Fees", value: -feesPaid, color: "text-yellow-400" },
    { label: "Net P&L", value: netPnl, color: netPnl >= 0 ? "text-emerald-400" : "text-red-400" },
  ];

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      {/* Stale data warning banner */}
      {isStale && (
        <div className="mb-2 flex items-center gap-2 rounded border border-yellow-700/50 bg-yellow-900/20 px-3 py-1.5">
          <span className="text-yellow-400 text-[10px] font-bold uppercase tracking-wide">⚠ Stale Data</span>
          <span className="text-yellow-300/80 text-[10px]">
            Data is from last executor push. Actual balances may differ.
          </span>
        </div>
      )}
      <div className="flex items-center gap-2 mb-2">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          P&L Reconciliation
        </h3>
        {currentBalance > 0 && (
          <span className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium ${
            reconciles ? "bg-emerald-500/20 text-emerald-400" : "bg-yellow-500/20 text-yellow-400"
          }`}>
            {reconciles ? "Reconciled" : "Pending"}
          </span>
        )}
      </div>
      <div className="grid grid-cols-6 gap-3">
        {items.map((item) => (
          <div key={item.label}>
            <p className="text-[10px] text-gray-500 uppercase">{item.label}</p>
            <p className={`text-sm font-bold font-mono ${item.color}`}>
              {item.value < 0 ? "-" : ""}${Math.abs(item.value).toFixed(2)}
            </p>
          </div>
        ))}
      </div>
      {/* API Truth comparison when reconciliation data is available */}
      {recon && (
        <div className="mt-3 border-t border-gray-800 pt-2">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">API Truth</span>
            {recon.stale && (
              <span className="rounded bg-yellow-500/20 px-1.5 py-0.5 text-[9px] text-yellow-400">
                {recon.stale_seconds}s old
              </span>
            )}
          </div>
          <div className="grid grid-cols-4 gap-3">
            <div>
              <p className="text-[9px] text-gray-500 uppercase">K API Total</p>
              <p className="text-xs font-bold font-mono text-blue-400">${recon.k_api_total.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-[9px] text-gray-500 uppercase">PM API Total</p>
              <p className="text-xs font-bold font-mono text-emerald-400">${recon.pm_api_total.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-[9px] text-gray-500 uppercase">Combined API</p>
              <p className="text-xs font-bold font-mono text-white">${recon.combined_api.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-[9px] text-gray-500 uppercase">Dashboard Gap</p>
              {(() => {
                const gap = recon.combined_api - currentBalance;
                return (
                  <p className={`text-xs font-bold font-mono ${
                    Math.abs(gap) < 0.10 ? "text-emerald-400" : gap > 0 ? "text-yellow-400" : "text-red-400"
                  }`}>
                    {gap >= 0 ? "+" : ""}{gap.toFixed(2)}
                  </p>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
