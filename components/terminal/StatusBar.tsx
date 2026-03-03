"use client";

// OMI Terminal — Status Bar (Redesigned)
// Bloomberg-style bottom info bar.

import type { TerminalStatus } from "@/lib/terminal/types";

interface StatusBarProps {
  status: TerminalStatus;
}

export default function StatusBar({ status }: StatusBarProps) {
  const isLive = status.feed_status === "LIVE";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: "100%",
        padding: "0 8px",
        fontSize: "8px",
        color: "#333",
        borderTop: "1px solid #111",
        background: "#050505",
        gap: "12px",
        overflow: "hidden",
      }}
    >
      {/* Left cluster */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
        {/* LIVE / DELAYED badge */}
        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <div
            style={{
              width: "5px",
              height: "5px",
              borderRadius: "50%",
              background: isLive ? "#00FF88" : "#FF6600",
              animation: isLive ? "terminal-pulse 1.5s ease-in-out infinite" : undefined,
              boxShadow: isLive ? "0 0 4px rgba(0,255,136,0.5)" : undefined,
            }}
          />
          <span style={{ color: isLive ? "#00FF88" : "#FF6600", fontWeight: 700, letterSpacing: "0.1em" }}>
            {status.feed_status}
          </span>
        </div>

        {/* Latency */}
        <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
          <span style={{ color: "#222" }}>LAT</span>
          <span style={{
            color: status.latency_ms < 50 ? "#00FF88" : status.latency_ms < 150 ? "#FF6600" : "#FF3366",
            fontVariantNumeric: "tabular-nums",
            fontWeight: 600,
          }}>
            {status.latency_ms}ms
          </span>
        </div>

        {/* Positions count */}
        <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
          <span style={{ color: "#222" }}>POS</span>
          <span style={{ color: "#444", fontVariantNumeric: "tabular-nums" }}>{status.position_count}</span>
        </div>

        {/* Total P&L */}
        <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
          <span style={{ color: "#222" }}>P&L</span>
          <span style={{
            color: status.total_pnl >= 0 ? "#00FF88" : "#FF3366",
            fontWeight: 700,
            fontVariantNumeric: "tabular-nums",
            textShadow: status.total_pnl >= 0 ? "0 0 6px rgba(0,255,136,0.3)" : "0 0 6px rgba(255,51,102,0.3)",
          }}>
            {status.total_pnl >= 0 ? "+" : ""}${status.total_pnl.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Center — scrolling market summary */}
      <div style={{
        flex: 1,
        overflow: "hidden",
        textAlign: "center",
        color: "#222",
        whiteSpace: "nowrap",
        textOverflow: "ellipsis",
      }}>
        {status.market_summary ?? "OMI TERMINAL — PREDICTION MARKETS"}
      </div>

      {/* Right cluster */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
        {/* Active markets */}
        <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
          <span style={{ color: "#222" }}>MKT</span>
          <span style={{ color: "#444", fontVariantNumeric: "tabular-nums" }}>{status.active_markets}</span>
        </div>

        {/* Volume */}
        <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
          <span style={{ color: "#222" }}>VOL</span>
          <span style={{ color: "#444", fontVariantNumeric: "tabular-nums" }}>
            {status.daily_volume >= 1000000
              ? `$${(status.daily_volume / 1000000).toFixed(1)}M`
              : `$${(status.daily_volume / 1000).toFixed(0)}K`}
          </span>
        </div>

        {/* Timestamp */}
        <span style={{ color: "#1f1f1f", fontVariantNumeric: "tabular-nums" }}>
          {status.timestamp}
        </span>
      </div>
    </div>
  );
}
