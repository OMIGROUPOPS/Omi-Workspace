"use client";

// OMI Terminal — Countdown Board (Visual Overhaul v3)
// Full market names, theta display, cleaner cards.
// Props interface preserved: { items, onSelect, upcomingMarkets }

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
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontSize: "9px",
          color: "#666",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          padding: "2px 2px 4px",
          borderBottom: "1px solid #1a1a1a",
          marginBottom: "4px",
          fontWeight: 700,
          flexShrink: 0,
        }}
      >
        <span style={{ color: hasCountdown ? "#FF6600" : "#555" }}>
          {hasCountdown ? "Settlement" : hasUpcoming ? "Near Settlement" : "Settlement"}
        </span>
        <span style={{ fontSize: "8px", color: "#3a3a3a" }}>
          {hasCountdown ? `${sorted.length} active` : hasUpcoming ? `${upcomingMarkets.length}` : ""}
        </span>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {hasCountdown ? (
          sorted.map((item, i) => {
            const urgent = item.secs_to_close < 60;
            const confPct = (item.bridge_confidence * 100).toFixed(0);
            const confColor = item.bridge_confidence >= 0.98 ? "#00FF88" : item.bridge_confidence >= 0.95 ? "#FFD600" : "#555";
            const hoursLeft = item.secs_to_close / 3600;
            const greeks = calcGreeks(item.price / 100, hoursLeft, item.sigma || 0.5);

            // Readable label
            const eventTicker = item.ticker.replace(/-[YN]$/, "");
            const cdParts = item.ticker.split("-");
            let cdTeam = cdParts.length >= 3 ? cdParts[cdParts.length - 2] : item.info.team;
            if (/^\d+[A-Z]+\d+/.test(cdTeam) && cdParts.length >= 4) {
              cdTeam = cdParts[cdParts.length - 3] || cdTeam;
            }
            const label = parseTickerLabel(item.ticker, cdTeam || item.info.team, eventTicker);

            const timePct = Math.max(0, Math.min(100, (item.secs_to_close / 300) * 100));

            return (
              <button
                key={item.ticker}
                onClick={() => onSelect?.(item.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  flexDirection: "column",
                  padding: "5px 4px",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  background: urgent ? "rgba(255,51,102,0.04)" : "transparent",
                  borderLeft: urgent ? "2px solid #FF3366" : "2px solid transparent",
                  animation: urgent ? "terminal-urgent-pulse 2s ease-in-out infinite" : "none",
                  transition: "background 0.1s",
                  marginBottom: "1px",
                  borderRadius: "0 2px 2px 0",
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = urgent ? "rgba(255,51,102,0.04)" : "transparent"; }}
              >
                {/* Row 1: Name + Time */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px", overflow: "hidden", minWidth: 0 }}>
                    <span style={{ color: item.side === "near_100" ? "#00FF88" : "#FF3366", fontSize: "8px", flexShrink: 0 }}>
                      {item.side === "near_100" ? "▲" : "▼"}
                    </span>
                    <span style={{
                      color: urgent ? "#FF3366" : "#ccc",
                      fontWeight: 600,
                      fontSize: "9px",
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}>
                      {label}
                    </span>
                    <span style={{ color: "#555", fontVariantNumeric: "tabular-nums", flexShrink: 0, fontSize: "8px" }}>
                      {item.price}c
                    </span>
                  </div>
                  <span
                    style={{
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 700,
                      fontSize: urgent ? "12px" : "10px",
                      color: urgent ? "#FF3366" : "#777",
                      textShadow: urgent ? "0 0 8px rgba(255,51,102,0.4)" : "none",
                      flexShrink: 0,
                      marginLeft: "6px",
                    }}
                  >
                    {formatTime(item.secs_to_close)}
                  </span>
                </div>

                {/* Row 2: Greeks + Confidence */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "3px", width: "100%" }}>
                  <div style={{ display: "flex", gap: "6px", fontSize: "7px" }}>
                    <span style={{ color: "#00BCD4" }}>
                      Δ{greeks.delta.toFixed(2)}
                    </span>
                    <span style={{ color: greeks.theta < 0 ? "#FF3366" : "#00FF88" }}>
                      Θ{greeks.theta.toFixed(1)}c/h
                    </span>
                    <span style={{ color: "#c084fc" }}>
                      Γ{greeks.gamma.toFixed(2)}
                    </span>
                  </div>
                  <span style={{
                    fontVariantNumeric: "tabular-nums",
                    color: confColor,
                    fontSize: "8px",
                    fontWeight: 700,
                  }}>
                    {confPct}%
                  </span>
                </div>

                {/* Row 3: Progress bar */}
                <div style={{
                  height: "2px",
                  background: "#151515",
                  borderRadius: "1px",
                  marginTop: "3px",
                  width: "100%",
                  overflow: "hidden",
                }}>
                  <div style={{
                    height: "100%",
                    width: `${timePct}%`,
                    background: urgent
                      ? "#FF3366"
                      : "linear-gradient(90deg, #FF6600, #FFD600)",
                    borderRadius: "1px",
                    transition: "width 1s linear",
                  }} />
                </div>
              </button>
            );
          })
        ) : hasUpcoming ? (
          upcomingMarkets.map((m, i) => {
            const distFromBoundary = Math.min(m.mid, 100 - m.mid);
            const nearHigh = m.mid >= 50;
            const dirColor = nearHigh ? "#00FF88" : "#FF3366";
            const dirArrow = nearHigh ? "▲" : "▼";
            const greeks = calcGreeks(m.mid / 100, 2, 0.5);

            const eventTicker = m.ticker.replace(/-[YN]$/, "");
            const label = parseTickerLabel(m.ticker, m.team, eventTicker);

            const proxPct = Math.max(0, 100 - (distFromBoundary / 50) * 100);

            return (
              <button
                key={m.ticker}
                onClick={() => onSelect?.(m.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  flexDirection: "column",
                  padding: "5px 4px",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  background: "transparent",
                  borderLeft: distFromBoundary <= 3 ? `2px solid ${dirColor}` : "2px solid transparent",
                  transition: "background 0.1s",
                  marginBottom: "1px",
                  borderRadius: "0 2px 2px 0",
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}
              >
                {/* Row 1: Name + Price */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px", overflow: "hidden", minWidth: 0 }}>
                    <span style={{ color: dirColor, fontSize: "8px", flexShrink: 0 }}>
                      {dirArrow}
                    </span>
                    <span style={{
                      color: "#ccc",
                      fontWeight: 600,
                      fontSize: "9px",
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}>
                      {label}
                    </span>
                    <span style={{
                      fontSize: "7px",
                      padding: "1px 4px",
                      borderRadius: "2px",
                      background: "rgba(255,102,0,0.06)",
                      color: "#666",
                      lineHeight: "11px",
                      flexShrink: 0,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      maxWidth: "50px",
                    }}>
                      {m.category}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px", flexShrink: 0 }}>
                    <span style={{
                      fontVariantNumeric: "tabular-nums",
                      color: dirColor,
                      fontSize: "10px",
                      fontWeight: 700,
                    }}>
                      {m.mid}c
                    </span>
                    <span style={{
                      fontVariantNumeric: "tabular-nums",
                      fontSize: "8px",
                      color: distFromBoundary <= 3 ? dirColor : "#444",
                      fontWeight: distFromBoundary <= 3 ? 700 : 400,
                    }}>
                      {distFromBoundary}c
                    </span>
                  </div>
                </div>

                {/* Row 2: Greeks */}
                <div style={{ display: "flex", gap: "6px", fontSize: "7px", marginTop: "3px" }}>
                  <span style={{ color: "#00BCD4" }}>
                    Δ{greeks.delta.toFixed(2)}
                  </span>
                  <span style={{ color: greeks.theta < 0 ? "#FF3366" : "#00FF88" }}>
                    Θ{greeks.theta.toFixed(1)}c/h
                  </span>
                  <span style={{ color: "#FFD600" }}>
                    IV {(greeks.iv * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Row 3: Proximity bar */}
                <div style={{
                  height: "2px",
                  background: "#151515",
                  borderRadius: "1px",
                  marginTop: "3px",
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
            gap: "8px",
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              border: "1px solid #1a1a1a",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "14px",
              color: "#1a1a1a",
              animation: "terminal-pulse 3s ease-in-out infinite",
            }}>
              ⏱
            </div>
            <span style={{ color: "#333", fontSize: "9px" }}>No settlement signals</span>
          </div>
        )}
      </div>
    </div>
  );
}
