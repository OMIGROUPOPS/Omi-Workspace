"use client";

// OMI Terminal — Status bar
// Dense single-line status with animated counters and pulse dot.

import type { ConnectionStatus } from "@/lib/terminal/types";
import { useAnimatedNumber } from "@/lib/terminal/hooks";

interface StatusBarProps {
  status: ConnectionStatus;
  balance?: number;
  openTrades?: number;
  tickerCount?: number;
  signalCount?: number;
  uptime?: number;
}

function formatUptime(secs: number): string {
  if (secs < 60) return `${secs}s`;
  if (secs < 3600) return `${Math.floor(secs / 60)}m`;
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return `${h}h${m.toString().padStart(2, "0")}m`;
}

export default function StatusBar({
  status,
  balance = 460,
  openTrades = 0,
  tickerCount = 0,
  signalCount,
  uptime,
}: StatusBarProps) {
  const animatedTickers = useAnimatedNumber(tickerCount, 500);
  const animatedSignals = useAnimatedNumber(signalCount ?? 0, 500);

  const dotColor: Record<ConnectionStatus, string> = {
    connected: "#00FF88",
    connecting: "#FFD600",
    disconnected: "#666",
    error: "#FF3366",
  };

  const statusLabel: Record<ConnectionStatus, string> = {
    connected: "CONNECTED",
    connecting: "CONNECTING",
    disconnected: "OFFLINE",
    error: "ERROR",
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 12px",
        height: "20px",
        background: "#0a0a0a",
        borderTop: "1px solid #222",
        fontSize: "8px",
        flexShrink: 0,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        {/* Connection status */}
        <span style={{ display: "flex", alignItems: "center", gap: "4px", color: dotColor[status] }}>
          <span
            style={{
              width: "5px",
              height: "5px",
              borderRadius: "50%",
              background: dotColor[status],
              boxShadow: status === "connected" ? `0 0 4px ${dotColor[status]}` : "none",
              animation:
                status === "connected"
                  ? "terminal-pulse 2s ease-in-out infinite"
                  : status === "connecting"
                    ? "terminal-pulse 0.8s ease-in-out infinite"
                    : "none",
            }}
          />
          WS: {statusLabel[status]}
        </span>

        <span style={{ color: "#222" }}>|</span>
        <span style={{ color: "#555", fontVariantNumeric: "tabular-nums" }}>
          {animatedTickers.toLocaleString()} tickers
        </span>

        {signalCount !== undefined && (
          <>
            <span style={{ color: "#222" }}>|</span>
            <span style={{ color: "#555", fontVariantNumeric: "tabular-nums" }}>
              {animatedSignals} signals
            </span>
          </>
        )}

        <span style={{ color: "#222" }}>|</span>
        <span style={{ color: "#555" }}>{openTrades} open</span>

        {uptime !== undefined && (
          <>
            <span style={{ color: "#222" }}>|</span>
            <span style={{ color: "#444", fontVariantNumeric: "tabular-nums" }}>
              up {formatUptime(uptime)}
            </span>
          </>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <span style={{ color: "#555", fontVariantNumeric: "tabular-nums" }}>
          ${balance.toFixed(2)}
        </span>
        <span style={{ color: "#222" }}>|</span>
        <span style={{ color: "#333" }}>OMI v0.3</span>
      </div>
    </div>
  );
}
