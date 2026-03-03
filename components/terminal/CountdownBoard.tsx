"use client";

// OMI Terminal — Countdown Board
// Markets near settlement with live countdown timers.
// Falls back to "Nearest to Settlement" from upcomingMarkets when no resolution signals.

import type { CountdownItem } from "@/lib/terminal/types";

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
        style={{ fontSize: "8px", color: "#444", textTransform: "uppercase", letterSpacing: "0.1em", padding: "0 2px 3px", borderBottom: "1px solid #222", marginBottom: "2px" }}
      >
        <span>{hasCountdown ? "Settlement" : hasUpcoming ? "Nearest to Settlement" : "Settlement"}</span>
        {hasCountdown && (
          <div style={{ display: "flex", gap: "12px" }}>
            <span>Conf</span>
            <span style={{ width: "36px", textAlign: "right" }}>Time</span>
          </div>
        )}
        {!hasCountdown && hasUpcoming && (
          <div style={{ display: "flex", gap: "12px" }}>
            <span>Mid</span>
            <span style={{ width: "36px", textAlign: "right" }}>Away</span>
          </div>
        )}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {hasCountdown ? (
          // Active resolution countdown
          sorted.map((item) => {
            const urgent = item.secs_to_close < 60;
            const confPct = (item.bridge_confidence * 100).toFixed(0);
            const confColor = item.bridge_confidence >= 0.98 ? "#00FF88" : item.bridge_confidence >= 0.95 ? "#FFD600" : "#666";

            return (
              <button
                key={item.ticker}
                onClick={() => onSelect?.(item.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "3px 2px",
                  border: "none",
                  cursor: "pointer",
                  fontSize: "9px",
                  textAlign: "left",
                  background: urgent ? "rgba(255,51,102,0.06)" : "transparent",
                  borderLeft: urgent ? "2px solid #FF3366" : "2px solid transparent",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "4px", minWidth: 0, overflow: "hidden" }}>
                  <span style={{ color: item.side === "near_100" ? "#00FF88" : "#FF3366", fontSize: "8px", flexShrink: 0 }}>
                    {item.side === "near_100" ? "\u25B2" : "\u25BC"}
                  </span>
                  <span style={{ color: urgent ? "#FF3366" : "#999", fontWeight: 500, overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                    {item.info.team}
                  </span>
                  <span style={{ color: "#333", fontVariantNumeric: "tabular-nums", flexShrink: 0, fontSize: "8px" }}>
                    {item.price}&cent;
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", flexShrink: 0 }}>
                  <span style={{ fontVariantNumeric: "tabular-nums", color: confColor, fontSize: "9px", fontWeight: 600 }}>
                    {confPct}%
                  </span>
                  <span
                    style={{
                      fontVariantNumeric: "tabular-nums", fontWeight: 600, fontSize: "9px",
                      width: "36px", textAlign: "right",
                      color: urgent ? "#FF3366" : "#888",
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
          upcomingMarkets.map((m) => {
            const distFromBoundary = Math.min(m.mid, 100 - m.mid);
            const nearHigh = m.mid >= 50;
            const dirColor = nearHigh ? "#00FF88" : "#FF3366";
            const dirArrow = nearHigh ? "\u25B2" : "\u25BC";

            return (
              <button
                key={m.ticker}
                onClick={() => onSelect?.(m.ticker)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "3px 2px",
                  border: "none",
                  cursor: "pointer",
                  fontSize: "9px",
                  textAlign: "left",
                  background: "transparent",
                  borderLeft: "2px solid transparent",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "4px", minWidth: 0, overflow: "hidden" }}>
                  <span style={{ color: dirColor, fontSize: "8px", flexShrink: 0 }}>
                    {dirArrow}
                  </span>
                  <span style={{ color: "#999", fontWeight: 500, overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                    {m.team || m.ticker.slice(-8)}
                  </span>
                  <span style={{
                    fontSize: "7px",
                    padding: "0 3px",
                    borderRadius: "2px",
                    background: "rgba(255,102,0,0.08)",
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
                <div style={{ display: "flex", alignItems: "center", gap: "12px", flexShrink: 0 }}>
                  <span style={{ fontVariantNumeric: "tabular-nums", color: dirColor, fontSize: "9px", fontWeight: 600 }}>
                    {m.mid}&cent;
                  </span>
                  <span
                    style={{
                      fontVariantNumeric: "tabular-nums", fontSize: "8px",
                      width: "36px", textAlign: "right",
                      color: "#555",
                    }}
                  >
                    {distFromBoundary}&cent; away
                  </span>
                </div>
              </button>
            );
          })
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", gap: "6px" }}>
            <span style={{ color: "#333", fontSize: "9px" }}>No resolution signals</span>
            <span style={{ color: "#222", fontSize: "8px" }}>Monitoring for settlement opportunities...</span>
          </div>
        )}
      </div>
    </div>
  );
}
