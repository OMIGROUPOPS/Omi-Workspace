"use client";

// OMI Terminal — Countdown Board (Redesigned v2)
// Visual cards with Greeks, progress bars, and settlement countdowns.
// Falls back to "Nearest to Settlement" from upcomingMarkets when no resolution signals.

import type { CountdownItem } from "@/lib/terminal/types";
import { calcGreeks } from "@/lib/terminal/greeks";
import { parseTickerLabel } from "@/lib/terminal/ticker-labels";

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
          fontSize: "9px",
          color: "#666",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          padding: "2px 2px 6px",
          borderBottom: "1px solid #1a1a1a",
          marginBottom: "4px",
          fontWeight: 700,
        }}
      >
        <span style={{ color: hasCountdown ? "#FF6600" : "#666" }}>
          {hasCountdown ? "\u23F1 Settlement" : hasUpcoming ? "Near Settlement" : "Settlement"}
        </span>
        {hasCountdown && (
          <span style={{ fontSize: "8px", color: "#444" }}>{sorted.length} active</span>
        )}
        {!hasCountdown && hasUpcoming && (
          <span style={{ fontSize: "8px", color: "#444" }}>{upcomingMarkets.length} markets</span>
        )}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {hasCountdown ? (
          // Active resolution countdown — card style
          sorted.map((item, i) => {
            const urgent = item.secs_to_close < 60;
            const confPct = (item.bridge_confidence * 100).toFixed(0);
            const confColor = item.bridge_confidence >= 0.98 ? "#00FF88" : item.bridge_confidence >= 0.95 ? "#FFD600" : "#666";
            const hoursLeft = item.secs_to_close / 3600;
            const greeks = calcGreeks(item.price / 100, hoursLeft, item.sigma || 0.5);

            // Readable label
            const eventTicker = item.ticker.replace(/-[YN]$/, "");
            const label = parseTickerLabel(item.ticker, item.info.team, eventTicker);

            // Time bar: 0-300s mapped to width
            const timePct = Math.max(0, Math.min(100, (item.secs_to_close / 300) * 100));

            return (
              <button
                key={item.ticker}
                onClick={() => onSelect?.(item.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  flexDirection: "column",
                  padding: "6px 5px",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  background: urgent ? "rgba(255,51,102,0.06)" : (i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"),
                  borderLeft: urgent ? "3px solid #FF3366" : "3px solid transparent",
                  animation: urgent ? "terminal-urgent-pulse 2s ease-in-out infinite" : "none",
                  transition: "background 0.1s",
                  marginBottom: "2px",
                  borderRadius: "2px",
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = urgent ? "rgba(255,51,102,0.06)" : (i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"); }}
              >
                {/* Row 1: Direction + Name + Price + Time */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "5px", overflow: "hidden", minWidth: 0 }}>
                    <span style={{ color: item.side === "near_100" ? "#00FF88" : "#FF3366", fontSize: "9px", flexShrink: 0 }}>
                      {item.side === "near_100" ? "\u25B2" : "\u25BC"}
                    </span>
                    <span style={{
                      color: urgent ? "#FF3366" : "#ddd",
                      fontWeight: 600,
                      fontSize: "10px",
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}>
                      {label}
                    </span>
                    <span style={{ color: "#666", fontVariantNumeric: "tabular-nums", flexShrink: 0, fontSize: "9px" }}>
                      {item.price}&cent;
                    </span>
                  </div>
                  <span
                    style={{
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 700,
                      fontSize: urgent ? "13px" : "11px",
                      color: urgent ? "#FF3366" : "#888",
                      textShadow: urgent ? "0 0 10px rgba(255,51,102,0.5)" : "none",
                      flexShrink: 0,
                      marginLeft: "8px",
                    }}
                  >
                    {formatTime(item.secs_to_close)}
                  </span>
                </div>

                {/* Row 2: Greeks + Confidence */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "4px", width: "100%" }}>
                  <div style={{ display: "flex", gap: "8px", fontSize: "8px" }}>
                    <span style={{ color: "#00BCD4" }}>
                      <span style={{ fontWeight: 700 }}>{"\u0394"}</span> {greeks.delta.toFixed(2)}
                    </span>
                    <span style={{ color: greeks.theta < 0 ? "#FF3366" : "#00FF88" }}>
                      <span style={{ fontWeight: 700 }}>{"\u0398"}</span> {greeks.theta.toFixed(1)}&cent;/h
                    </span>
                    <span style={{ color: "#c084fc" }}>
                      <span style={{ fontWeight: 700 }}>{"\u0393"}</span> {greeks.gamma.toFixed(2)}
                    </span>
                  </div>
                  <span style={{
                    fontVariantNumeric: "tabular-nums",
                    color: confColor,
                    fontSize: "9px",
                    fontWeight: 700,
                  }}>
                    {confPct}%
                  </span>
                </div>

                {/* Row 3: Time progress bar */}
                <div style={{
                  height: "2px",
                  background: "#1a1a1a",
                  borderRadius: "1px",
                  marginTop: "4px",
                  width: "100%",
                  overflow: "hidden",
                }}>
                  <div style={{
                    height: "100%",
                    width: `${timePct}%`,
                    background: urgent
                      ? "linear-gradient(90deg, #FF3366, #FF3366)"
                      : "linear-gradient(90deg, #FF6600, #FFD600)",
                    borderRadius: "1px",
                    transition: "width 1s linear",
                  }} />
                </div>
              </button>
            );
          })
        ) : hasUpcoming ? (
          // Nearest to settlement fallback — card style
          upcomingMarkets.map((m, i) => {
            const distFromBoundary = Math.min(m.mid, 100 - m.mid);
            const nearHigh = m.mid >= 50;
            const dirColor = nearHigh ? "#00FF88" : "#FF3366";
            const dirArrow = nearHigh ? "\u25B2" : "\u25BC";
            const greeks = calcGreeks(m.mid / 100, 2, 0.5);

            // Readable label
            const eventTicker = m.ticker.replace(/-[YN]$/, "");
            const label = parseTickerLabel(m.ticker, m.team, eventTicker);

            // Proximity bar: 0 away = full, 50 away = empty
            const proxPct = Math.max(0, 100 - (distFromBoundary / 50) * 100);

            return (
              <button
                key={m.ticker}
                onClick={() => onSelect?.(m.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  flexDirection: "column",
                  padding: "6px 5px",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                  borderLeft: distFromBoundary <= 3 ? `3px solid ${dirColor}` : "3px solid transparent",
                  transition: "background 0.1s",
                  marginBottom: "2px",
                  borderRadius: "2px",
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"; }}
              >
                {/* Row 1: Direction + Name + Price */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "5px", overflow: "hidden", minWidth: 0 }}>
                    <span style={{ color: dirColor, fontSize: "9px", flexShrink: 0 }}>
                      {dirArrow}
                    </span>
                    <span style={{
                      color: "#ddd",
                      fontWeight: 600,
                      fontSize: "10px",
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}>
                      {label}
                    </span>
                    <span style={{
                      fontSize: "7px",
                      padding: "1px 5px",
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
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", flexShrink: 0 }}>
                    <span style={{
                      fontVariantNumeric: "tabular-nums",
                      color: dirColor,
                      fontSize: "11px",
                      fontWeight: 700,
                    }}>
                      {m.mid}&cent;
                    </span>
                    <span
                      style={{
                        fontVariantNumeric: "tabular-nums",
                        fontSize: "9px",
                        color: distFromBoundary <= 3 ? dirColor : "#555",
                        fontWeight: distFromBoundary <= 3 ? 700 : 400,
                      }}
                    >
                      {distFromBoundary}&cent;
                    </span>
                  </div>
                </div>

                {/* Row 2: Greeks */}
                <div style={{ display: "flex", gap: "8px", fontSize: "8px", marginTop: "3px" }}>
                  <span style={{ color: "#00BCD4" }}>
                    <span style={{ fontWeight: 700 }}>{"\u0394"}</span> {greeks.delta.toFixed(2)}
                  </span>
                  <span style={{ color: greeks.theta < 0 ? "#FF3366" : "#00FF88" }}>
                    <span style={{ fontWeight: 700 }}>{"\u0398"}</span> {greeks.theta.toFixed(1)}&cent;/h
                  </span>
                  <span style={{ color: "#FFD600" }}>
                    IV {(greeks.iv * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Row 3: Proximity bar */}
                <div style={{
                  height: "2px",
                  background: "#1a1a1a",
                  borderRadius: "1px",
                  marginTop: "4px",
                  width: "100%",
                  overflow: "hidden",
                }}>
                  <div style={{
                    height: "100%",
                    width: `${proxPct}%`,
                    background: `linear-gradient(90deg, ${dirColor}60, ${dirColor})`,
                    borderRadius: "1px",
                  }} />
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
            gap: "12px",
          }}>
            <div style={{
              width: "40px",
              height: "40px",
              borderRadius: "50%",
              border: "2px solid #1a1a1a",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
              color: "#222",
              animation: "terminal-pulse 3s ease-in-out infinite",
            }}>
              {"\u23F1"}
            </div>
            <span style={{ color: "#444", fontSize: "10px" }}>No settlement signals</span>
            <span style={{ color: "#333", fontSize: "8px" }}>Monitoring markets...</span>
          </div>
        )}
      </div>
    </div>
  );
}
