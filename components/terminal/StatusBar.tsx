"use client";

// OMI Terminal — Status bar (Redesigned v2)
// Dense single-line status with animated counters, pulse dot, and branding.

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
  return `${h}h${m.toString().padStart(2, "00")}m`;
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
        height: "24px",
        background: "#060606",
        borderTop: "1px solid rgba(255,102,0,0.1)",
        fontSize: "9px",
        flexShrink: 0,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {/* Connection status */}
        <span style={{ display: "flex", alignItems: "center", gap: "5px", color: dotColor[status] }}>
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              background: dotColor[status],
              boxShadow: status === "connected" ? `0 0 8px ${dotColor[status]}` : "none",
              animation:
                status === "connected"
                  ? "terminal-pulse 2s ease-in-out infinite"
                  : status === "connecting"
                    ? "terminal-pulse 0.8s ease-in-out infinite"
                    : "none",
            }}
          />
          <span style={{ fontWeight: 600, letterSpacing: "0.05em" }}>
            WS: {statusLabel[status]}
          </span>
        </span>

        <span style={{ color: "#1a1a1a" }}>|</span>
        <span style={{ color: "#666", fontVariantNumeric: "tabular-nums" }}>
          <span style={{ color: "#888", fontWeight: 600 }}>{animatedTickers.toLocaleString()}</span> tickers
        </span>

        {signalCount !== undefined && (
          <>
            <span style={{ color: "#1a1a1a" }}>|</span>
            <span style={{ color: "#666", fontVariantNumeric: "tabular-nums" }}>
              <span style={{ color: "#00BCD4", fontWeight: 600 }}>{animatedSignals}</span> signals
            </span>
          </>
        )}

        <span style={{ color: "#1a1a1a" }}>|</span>
        <span style={{ color: "#555" }}>{openTrades} open</span>

        {uptime !== undefined && (
          <>
            <span style={{ color: "#1a1a1a" }}>|</span>
            <span style={{ color: "#555", fontVariantNumeric: "tabular-nums" }}>
              up {formatUptime(uptime)}
            </span>
          </>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <span style={{ color: "#777", fontVariantNumeric: "tabular-nums", fontWeight: 600 }}>
          ${balance.toFixed(2)}
        </span>
        <span style={{ color: "#1a1a1a" }}>|</span>
        <span style={{ color: "#FF6600", fontWeight: 700, letterSpacing: "0.1em", fontSize: "8px" }}>
          OMI v0.3
        </span>
      </div>
    </div>
  );
}
