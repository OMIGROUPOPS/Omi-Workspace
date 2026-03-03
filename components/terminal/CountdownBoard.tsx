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
        {!hasCountdown && hasUpcoming && (
          <div style={{ display: "flex", gap: "12px" }}>
            <span>Mid</span>
            <span style={{ width: "40px", textAlign: "right" }}>Away</span>
          </div>
        )}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {hasCountdown ? (
          // Active resolution countdown
          sorted.map((item, i) => {
            const urgent = item.secs_to_close < 60;
            const confPct = (item.bridge_confidence * 100).toFixed(0);
            const confColor = item.bridge_confidence >= 0.98 ? "#00FF88" : item.bridge_confidence >= 0.95 ? "#FFD600" : "#666";

            // Calculate theta for this item
            const hoursLeft = item.secs_to_close / 3600;
            const greeks = calcGreeks(item.price / 100, hoursLeft, item.sigma || 0.5);

            return (
              <button
                key={item.ticker}
                onClick={() => onSelect?.(item.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "4px 3px",
                  border: "none",
                  cursor: "pointer",
                  fontSize: "9px",
                  textAlign: "left",
                  background: urgent ? "rgba(255,51,102,0.06)" : (i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"),
                  borderLeft: urgent ? "3px solid #FF3366" : "3px solid transparent",
                  animation: urgent ? "terminal-urgent-pulse 2s ease-in-out infinite" : "none",
                  transition: "background 0.1s",
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = urgent ? "rgba(255,51,102,0.06)" : (i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"); }}
              >
                <div style={{ display: "flex", flexDirection: "column", gap: "1px", minWidth: 0, overflow: "hidden" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <span style={{ color: item.side === "near_100" ? "#00FF88" : "#FF3366", fontSize: "8px", flexShrink: 0 }}>
                      {item.side === "near_100" ? "\u25B2" : "\u25BC"}
                    </span>
                    <span style={{
                      color: urgent ? "#FF3366" : "#ccc",
                      fontWeight: 600,
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}>
                      {item.info.team}
                    </span>
                    <span style={{ color: "#444", fontVariantNumeric: "tabular-nums", flexShrink: 0, fontSize: "8px" }}>
                      {item.price}&cent;
                    </span>
                  </div>
                  {/* Greeks sub-row */}
                  <div style={{ display: "flex", gap: "6px", fontSize: "7px", paddingLeft: "16px" }}>
                    <span style={{ color: "#00BCD4" }}>{"\u0398"} {greeks.theta.toFixed(1)}</span>
                    <span style={{ color: "#444" }}>{"\u0394"} {greeks.delta.toFixed(2)}</span>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
                  <span style={{
                    fontVariantNumeric: "tabular-nums",
                    color: confColor,
                    fontSize: "9px",
                    fontWeight: 700,
                  }}>
                    {confPct}%
                  </span>
                  <span
                    style={{
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 700,
                      fontSize: urgent ? "11px" : "9px",
                      width: "40px",
                      textAlign: "right",
                      color: urgent ? "#FF3366" : "#888",
                      textShadow: urgent ? "0 0 8px rgba(255,51,102,0.4)" : "none",
                    }}
                  >
                    {formatTime(item.secs_to_close)}
                  </span>
                </div>
              </button>
            );
          })
        ) : hasUpcoming ? (
          // Nearest to settlement fallback
          upcomingMarkets.map((m, i) => {
            const distFromBoundary = Math.min(m.mid, 100 - m.mid);
            const nearHigh = m.mid >= 50;
            const dirColor = nearHigh ? "#00FF88" : "#FF3366";
            const dirArrow = nearHigh ? "\u25B2" : "\u25BC";

            // Calculate theta for display
            const greeks = calcGreeks(m.mid / 100, 2, 0.5);

            return (
              <button
                key={m.ticker}
                onClick={() => onSelect?.(m.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "4px 3px",
                  border: "none",
                  cursor: "pointer",
                  fontSize: "9px",
                  textAlign: "left",
                  background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                  borderLeft: distFromBoundary <= 3 ? `3px solid ${dirColor}` : "3px solid transparent",
                  transition: "background 0.1s",
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"; }}
              >
                <div style={{ display: "flex", flexDirection: "column", gap: "1px", minWidth: 0, overflow: "hidden" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <span style={{ color: dirColor, fontSize: "8px", flexShrink: 0 }}>
                      {dirArrow}
                    </span>
                    <span style={{
                      color: "#ccc",
                      fontWeight: 500,
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}>
                      {m.team || m.ticker.slice(-8)}
                    </span>
                    <span style={{
                      fontSize: "7px",
                      padding: "0 4px",
                      borderRadius: "3px",
                      background: "rgba(255,102,0,0.08)",
                      color: "#777",
                      lineHeight: "12px",
                      flexShrink: 0,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      maxWidth: "55px",
                    }}>
                      {m.category}
                    </span>
                  </div>
                  {/* Greeks sub-row */}
                  <div style={{ display: "flex", gap: "6px", fontSize: "7px", paddingLeft: "16px" }}>
                    <span style={{ color: "#00BCD4" }}>{"\u0398"} {greeks.theta.toFixed(1)}</span>
                    <span style={{ color: "#444" }}>{"\u0394"} {greeks.delta.toFixed(2)}</span>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
                  <span style={{
                    fontVariantNumeric: "tabular-nums",
                    color: dirColor,
                    fontSize: "10px",
                    fontWeight: 700,
                  }}>
                    {m.mid}&cent;
                  </span>
                  <span
                    style={{
                      fontVariantNumeric: "tabular-nums",
                      fontSize: "8px",
                      width: "40px",
                      textAlign: "right",
                      color: distFromBoundary <= 3 ? dirColor : "#555",
                      fontWeight: distFromBoundary <= 3 ? 700 : 400,
                    }}
                  >
                    {distFromBoundary}&cent; away
                  </span>
                </div>
              </button>
            );
          })
        ) : (
          <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            gap: "8px",
          }}>
            <span style={{ fontSize: "18px", color: "#222", opacity: 0.5 }}>{"\u23F1"}</span>
            <span style={{ color: "#333", fontSize: "9px" }}>No resolution signals</span>
            <span style={{ color: "#222", fontSize: "8px" }}>Monitoring for settlement...</span>
          </div>
        )}
      </div>
    </div>
  );
}
