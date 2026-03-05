"use client";

// OMI Terminal — Status bar (Visual Overhaul v4 — Modular Box Pattern)
// Two-row layout: RISK RULES row + STATUS row. Props interface preserved + totalPnl added.

import type { ConnectionStatus } from "@/lib/terminal/types";
import { useAnimatedNumber } from "@/lib/terminal/hooks";

interface StatusBarProps {
  status: ConnectionStatus;
  balance?: number;
  openTrades?: number;
  tickerCount?: number;
  signalCount?: number;
  uptime?: number;
  totalPnl?: number; // session P&L in cents
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
  balance = 0,
  openTrades = 0,
  tickerCount = 0,
  signalCount,
  uptime,
  totalPnl,
}: StatusBarProps) {
  const animatedTickers = useAnimatedNumber(tickerCount, 500);
  const animatedSignals = useAnimatedNumber(signalCount ?? 0, 500);

  const dotColor: Record<ConnectionStatus, string> = {
    connected: "#00FF88",
    connecting: "#FFD600",
    disconnected: "#555",
    error: "#FF3366",
  };

  const statusLabel: Record<ConnectionStatus, string> = {
    connected: "CONNECTED",
    connecting: "SYNCING",
    disconnected: "OFFLINE",
    error: "ERROR",
  };

  const statusDot = dotColor[status];

  // P&L display
  const pnlCents = totalPnl ?? 0;
  const pnlDollars = pnlCents / 100;
  const pnlColor = pnlCents > 0 ? "#00FF88" : pnlCents < 0 ? "#FF3366" : "#5a6577";
  const pnlSign = pnlCents > 0 ? "+" : "";
  const pnlDisplay = `${pnlSign}$${pnlDollars.toFixed(2)}`;

  return (
    <div
      style={{
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        gap: "4px",
        padding: "4px 8px 5px",
        background: "#060606",
        borderTop: "1px solid #1a1a1a",
        fontFamily: "'JetBrains Mono', 'Courier New', monospace",
      }}
    >
      {/* Row 1: RISK RULES */}
      <div
        style={{
          background: "#0d0d0d",
          border: "1px solid #FF336640",
          borderRadius: "5px",
          display: "flex",
          alignItems: "center",
          padding: "0 10px",
          height: "20px",
          gap: "8px",
        }}
      >
        {/* Header tint label */}
        <span
          style={{
            fontSize: "8px",
            fontWeight: 700,
            color: "#FF3366",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            background: "#FF336615",
            padding: "1px 6px",
            borderRadius: "3px",
            flexShrink: 0,
          }}
        >
          RISK RULES
        </span>
        <span style={{ color: "#1a1a1a", fontSize: "8px" }}>│</span>
        <span
          style={{
            fontSize: "8px",
            color: "#5a6577",
            letterSpacing: "0.04em",
            fontVariantNumeric: "tabular-nums",
          }}
        >
          λ&gt;0.012→PULL
        </span>
        <span style={{ color: "#1a1a1a", fontSize: "8px" }}>·</span>
        <span style={{ fontSize: "8px", color: "#5a6577", letterSpacing: "0.04em" }}>
          VPIN&gt;0.30→WIDEN 2x
        </span>
        <span style={{ color: "#1a1a1a", fontSize: "8px" }}>·</span>
        <span style={{ fontSize: "8px", color: "#5a6577", letterSpacing: "0.04em" }}>
          |inv|&gt;8→SKEW
        </span>
        <span style={{ color: "#1a1a1a", fontSize: "8px" }}>·</span>
        <span
          style={{
            fontSize: "8px",
            color: "#FF6600",
            fontWeight: 700,
            letterSpacing: "0.08em",
          }}
        >
          POST_ONLY
        </span>
      </div>

      {/* Row 2: STATUS */}
      <div
        style={{
          background: "#0d0d0d",
          border: "1px solid #1a1a1a",
          borderRadius: "5px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 10px",
          height: "20px",
        }}
      >
        {/* Left cluster */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            fontSize: "8px",
          }}
        >
          {/* Brand */}
          <span
            style={{
              color: "#FF6600",
              fontWeight: 800,
              fontSize: "9px",
              letterSpacing: "0.15em",
            }}
          >
            OMI
          </span>
          <span
            style={{
              color: "#333",
              fontSize: "7px",
              letterSpacing: "0.2em",
            }}
          >
            TERMINAL v0.3
          </span>

          <span style={{ color: "#1a1a1a" }}>│</span>

          {/* WS status */}
          <span
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
              color: statusDot,
            }}
          >
            <span
              style={{
                width: "5px",
                height: "5px",
                borderRadius: "50%",
                background: statusDot,
                display: "inline-block",
                boxShadow:
                  status === "connected" ? `0 0 6px ${statusDot}` : "none",
                animation:
                  status === "connected"
                    ? "terminal-pulse 2s ease-in-out infinite"
                    : status === "connecting"
                      ? "terminal-pulse 0.8s ease-in-out infinite"
                      : "none",
              }}
            />
            <span style={{ fontWeight: 700, letterSpacing: "0.06em", fontSize: "8px" }}>
              WS: {statusLabel[status]}
            </span>
          </span>

          <span style={{ color: "#1a1a1a" }}>│</span>

          {/* Ticker count */}
          <span
            style={{
              fontVariantNumeric: "tabular-nums",
              color: "#777",
            }}
          >
            <span style={{ color: "#e0e0e0", fontWeight: 600 }}>
              {animatedTickers.toLocaleString()}
            </span>{" "}
            tickers
          </span>

          {/* Signal count */}
          {signalCount !== undefined && (
            <>
              <span style={{ color: "#1a1a1a" }}>│</span>
              <span
                style={{
                  fontVariantNumeric: "tabular-nums",
                  color: "#777",
                }}
              >
                <span style={{ color: "#00BCD4", fontWeight: 600 }}>
                  {animatedSignals}
                </span>{" "}
                signals
              </span>
            </>
          )}

          {/* Open trades */}
          <span style={{ color: "#1a1a1a" }}>│</span>
          <span style={{ color: "#777" }}>
            <span style={{ color: "#e0e0e0", fontWeight: 600 }}>{openTrades}</span> open
          </span>
        </div>

        {/* Right cluster */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            fontSize: "8px",
          }}
        >
          {/* Kalshi balance */}
          <span style={{ color: "#777" }}>
            K:{" "}
            <span
              style={{
                color: "#00FF88",
                fontVariantNumeric: "tabular-nums",
                fontWeight: 600,
                fontSize: "9px",
              }}
            >
              ${balance.toFixed(2)}
            </span>
          </span>

          {/* Session P&L */}
          {totalPnl !== undefined && (
            <>
              <span style={{ color: "#1a1a1a" }}>│</span>
              <span style={{ color: "#777" }}>
                Session:{" "}
                <span
                  style={{
                    color: pnlColor,
                    fontVariantNumeric: "tabular-nums",
                    fontWeight: 600,
                  }}
                >
                  {pnlDisplay}
                </span>
              </span>
            </>
          )}

          {/* Uptime */}
          {uptime !== undefined && (
            <>
              <span style={{ color: "#1a1a1a" }}>│</span>
              <span
                style={{ fontVariantNumeric: "tabular-nums", color: "#555" }}
              >
                up {formatUptime(uptime)}
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
