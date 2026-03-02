"use client";

// OMNI Terminal — Status bar
// Shows WS connection status, balances, system info at bottom of terminal.

import type { ConnectionStatus } from "@/lib/terminal/types";

interface StatusBarProps {
  status: ConnectionStatus;
  balance?: number;
  openTrades?: number;
  tickerCount?: number;
}

export default function StatusBar({
  status,
  balance = 460,
  openTrades = 0,
  tickerCount = 0,
}: StatusBarProps) {
  const statusColor: Record<ConnectionStatus, string> = {
    connected: "text-emerald-400",
    connecting: "text-amber-400",
    disconnected: "text-zinc-500",
    error: "text-red-400",
  };

  const statusLabel: Record<ConnectionStatus, string> = {
    connected: "CONNECTED",
    connecting: "CONNECTING...",
    disconnected: "DISCONNECTED",
    error: "ERROR",
  };

  return (
    <div className="flex items-center justify-between px-4 h-6 bg-[#111111] border-t border-[#222] text-[10px] shrink-0">
      <div className="flex items-center gap-4">
        <span className={statusColor[status]}>
          {status === "connected" ? "●" : "○"} WS: {statusLabel[status]}
        </span>
        <span className="text-zinc-600">|</span>
        <span className="text-zinc-500">Tickers: {tickerCount.toLocaleString()}</span>
        <span className="text-zinc-600">|</span>
        <span className="text-zinc-500">Open: {openTrades}</span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-zinc-500">Balance: ${balance.toFixed(2)}</span>
        <span className="text-zinc-600">|</span>
        <span className="text-zinc-600">OMNI Terminal v0.1.0</span>
      </div>
    </div>
  );
}
