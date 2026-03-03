"use client";

// OMI Terminal — Countdown Board (Redesigned)
// Markets near settlement with live countdown timers + Greeks display.
// Falls back to "Nearest to Settlement" from upcomingMarkets when no resolution signals.

import type { CountdownItem } from "@/lib/terminal/types";
import { calcGreeks } from "@/lib/terminal/greeks";

interface UpcomingMarket {
  ticker: string;
  team: string;
  mid: number;
  spread: number;
  category: string;
}

interface CountdownBoardProps {
  items?: CountdownItem[];
  onSelect?: (ticker: string) => void;
  upcomingMarkets?: UpcomingMarket[];
}

function formatTime(secs: number): string {
  if (secs <= 0) return "0:00";
  if (secs >= 3600) {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    return `${h}h${m.toString().padStart(2, "0")}m`;
  }
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function CountdownBoard({ items = [], onSelect, upcomingMarkets = [] }: CountdownBoardProps) {
  const sorted = [...items].sort((a, b) => a.secs_to_close - b.secs_to_close);
  const hasCountdown = sorted.length > 0;
  const hasUpcoming = upcomingMarkets.length > 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div
        className="flex items-center justify-between shrink-0"
        style={{
          fontSize: "8px",
          color: "#555",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          padding: "0 2px 4px",
          borderBottom: "1px solid #1a1a1a",
          marginBottom: "3px",
          fontWeight: 600,
        }}
      >
        <span style={{ color: hasCountdown ? "#FF6600" : "#555" }}>
          {hasCountdown ? "\u23F1 Settlement" : hasUpcoming ? "Nearest to Settlement" : "Settlement"}
        </span>
        {hasCountdown && (
          <div style={{ display: "flex", gap: "12px" }}>
            <span>Conf</span>
            <span style={{ width: "40px", textAlign: "right" }}>Time</span>
          </div>
        )}
      </div>

      {/* Countdown items */}
      {hasCountdown && (
        <div className="flex-1 overflow-y-auto" style={{ minHeight: 0 }}>
          {sorted.map((item) => {
            const urgent = item.secs_to_close < 300;
            const greeks = calcGreeks(item.price / 100, item.secs_to_close / 3600, 0.5);
            const confLabel =
              item.confidence === "HIGH"
                ? { label: "HIGH", color: "#FF3366" }
                : item.confidence === "MED"
                  ? { label: "MED", color: "#FF6600" }
                  : { label: "LOW", color: "#444" };
            return (
              <div
                key={item.ticker}
                onClick={() => onSelect?.(item.ticker)}
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr auto",
                  gap: "4px",
                  padding: "5px 2px",
                  borderBottom: "1px solid #0f0f0f",
                  cursor: "pointer",
                  animation: urgent ? "terminal-urgent-pulse 2s ease-in-out infinite" : undefined,
                }}
              >
                {/* Left col */}
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "5px", marginBottom: "3px" }}>
                    <span style={{
                      color: urgent ? "#FF3366" : "#ddd",
                      fontWeight: 700,
                      fontSize: "10px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      textShadow: urgent ? "0 0 8px rgba(255,51,102,0.4)" : undefined,
                    }}>
                      {item.ticker}
                    </span>
                    <span style={{
                      fontSize: "9px",
                      fontWeight: 700,
                      color: item.price >= 50 ? "#00FF88" : "#FF3366",
                      fontVariantNumeric: "tabular-nums",
                      textShadow: item.price >= 50 ? "0 0 6px rgba(0,255,136,0.3)" : "0 0 6px rgba(255,51,102,0.3)",
                    }}>
                      {item.price.toFixed(0)}¢
                    </span>
                  </div>
                  {/* Greeks mini-row */}
                  <div style={{ display: "flex", gap: "8px", fontSize: "8px", color: "#444" }}>
                    <span>Δ<span style={{ color: "#00BCD4" }}>{greeks.delta.toFixed(2)}</span></span>
                    <span>Θ<span style={{ color: "#00BCD4" }}>{greeks.theta.toFixed(1)}</span></span>
                    <span>IV<span style={{ color: "#00BCD4" }}>{(greeks.iv * 100).toFixed(0)}%</span></span>
                  </div>
                </div>

                {/* Right col */}
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "3px" }}>
                  <span style={{ fontSize: "8px", color: confLabel.color, fontWeight: 700, letterSpacing: "0.05em" }}>
                    {confLabel.label}
                  </span>
                  <span style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    color: urgent ? "#FF3366" : "#888",
                    fontVariantNumeric: "tabular-nums",
                    animation: urgent ? "terminal-counter-tick 0.3s ease-out" : undefined,
                    textShadow: urgent ? "0 0 8px rgba(255,51,102,0.4)" : undefined,
                  }}>
                    {formatTime(item.secs_to_close)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Upcoming markets fallback */}
      {!hasCountdown && hasUpcoming && (
        <div className="flex-1 overflow-y-auto" style={{ minHeight: 0 }}>
          {upcomingMarkets.slice(0, 8).map((mkt) => {
            const greeks = calcGreeks(mkt.mid / 100, 4, 0.5);
            return (
              <div
                key={mkt.ticker}
                onClick={() => onSelect?.(mkt.ticker)}
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr auto",
                  gap: "4px",
                  padding: "5px 2px",
                  borderBottom: "1px solid #0f0f0f",
                  cursor: "pointer",
                }}
              >
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "5px", marginBottom: "3px" }}>
                    <span style={{
                      color: "#888",
                      fontSize: "8px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}>
                      {mkt.team}
                    </span>
                    <span style={{
                      fontSize: "9px",
                      fontWeight: 700,
                      color: mkt.mid >= 50 ? "#00FF88" : "#FF3366",
                      fontVariantNumeric: "tabular-nums",
                    }}>
                      {mkt.mid.toFixed(0)}¢
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: "8px", fontSize: "8px", color: "#444" }}>
                    <span>Δ<span style={{ color: "#555" }}>{greeks.delta.toFixed(2)}</span></span>
                    <span>IV<span style={{ color: "#555" }}>{(greeks.iv * 100).toFixed(0)}%</span></span>
                    <span style={{ color: mkt.spread < 3 ? "#00FF88" : mkt.spread < 6 ? "#FF6600" : "#FF3366" }}>sprd:{mkt.spread.toFixed(1)}</span>
                  </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
                  <span style={{ fontSize: "7px", color: "#333", textTransform: "uppercase", letterSpacing: "0.06em" }}>{mkt.category}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!hasCountdown && !hasUpcoming && (
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#222", fontSize: "9px" }}>
          No settlement data
        </div>
      )}
    </div>
  );
}
