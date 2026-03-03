"use client";

// OMI Terminal — P&L panel (Redesigned v2)
// Visual stat cards, strategy breakdown with bar charts, activity feed.

import type { PnLBreakdown, ScanType, SignalSeverity } from "@/lib/terminal/types";

interface RecentActivityItem {
  scan_type: ScanType;
  ticker: string;
  severity: SignalSeverity;
  description: string;
  timestamp: number;
}

interface PnLProps {
  totalPnl?: number;
  breakdowns?: PnLBreakdown[];
  openTrades?: number;
  signalCount?: number;
  categoryCount?: number;
  recentActivity?: RecentActivityItem[];
}

const STRAT_COLOR: Record<string, string> = {
  resolution: "#00FF88",
  momentum_lag: "#FFD600",
  contradiction_mono: "#c084fc",
  contradiction_cross: "#c084fc",
  whale_momentum: "#00BCD4",
};

const STRAT_LABEL: Record<string, string> = {
  resolution: "Resolution",
  momentum_lag: "Momentum",
  contradiction_mono: "Mono",
  contradiction_cross: "Cross",
  whale_momentum: "Whale",
};

function formatTimestamp(ts: number): string {
  const d = new Date(ts);
  return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
}

export default function PnL({
  totalPnl = 0,
  breakdowns = [],
  openTrades = 0,
  signalCount,
  categoryCount,
  recentActivity = [],
}: PnLProps) {
  const pnlColor = totalPnl > 0 ? "#00FF88" : totalPnl < 0 ? "#FF3366" : "#666";
  const hasTrades = breakdowns.length > 0;

  return (
    <div className="h-full flex flex-col">
      {/* Total P&L header — prominent */}
      <div style={{
        marginBottom: "6px",
        padding: "6px 4px",
        borderBottom: "1px solid #1a1a1a",
        background: "rgba(255,255,255,0.01)",
        borderRadius: "4px 4px 0 0",
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
          <span style={{
            fontSize: "9px",
            color: "#666",
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            fontWeight: 700,
          }}>
            Session P&L
          </span>
          {hasTrades ? (
            <span style={{ fontSize: "9px", color: "#555" }}>{openTrades} open</span>
          ) : (
            <span style={{
              fontSize: "8px",
              fontWeight: 700,
              padding: "2px 6px",
              borderRadius: "3px",
              background: "rgba(255,102,0,0.12)",
              color: "#FF6600",
              letterSpacing: "0.05em",
            }}>
              PAPER
            </span>
          )}
        </div>
        <div style={{
          fontSize: "26px",
          fontWeight: 700,
          fontVariantNumeric: "tabular-nums",
          color: pnlColor,
          lineHeight: 1.1,
          textShadow: totalPnl !== 0 ? `0 0 16px ${pnlColor}40` : "none",
        }}>
          {totalPnl >= 0 ? "+" : ""}{(totalPnl / 100).toFixed(2)}
          <span style={{ fontSize: "10px", color: "#444", marginLeft: "4px", fontWeight: 400 }}>USD</span>
        </div>
      </div>

      {/* Strategy breakdown or Activity log */}
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {hasTrades ? (
          // Real trades — strategy breakdown with visual bars
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            {breakdowns.map((b) => {
              const c = b.total_pnl > 0 ? "#00FF88" : b.total_pnl < 0 ? "#FF3366" : "#555";
              const stratColor = STRAT_COLOR[b.scan_type] || "#888";
              const label = STRAT_LABEL[b.scan_type] || b.scan_type;
              const winRate = b.trade_count > 0 ? (b.winners / b.trade_count) * 100 : 0;

              return (
                <div
                  key={b.scan_type}
                  style={{
                    padding: "6px 5px",
                    borderLeft: `3px solid ${stratColor}`,
                    background: "rgba(255,255,255,0.015)",
                    borderRadius: "0 3px 3px 0",
                    marginBottom: "2px",
                  }}
                >
                  {/* Strategy header */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{
                        fontSize: "9px",
                        fontWeight: 700,
                        color: stratColor,
                      }}>
                        {label}
                      </span>
                      <span style={{ color: "#555", fontSize: "8px", fontVariantNumeric: "tabular-nums" }}>
                        {b.trade_count}t · {b.winners}W/{b.losers}L
                      </span>
                    </div>
                    <span style={{
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 700,
                      fontSize: "11px",
                      color: c,
                    }}>
                      {b.total_pnl >= 0 ? "+" : ""}{b.total_pnl}&cent;
                    </span>
                  </div>
                  {/* Win rate bar */}
                  <div style={{
                    height: "3px",
                    background: "#1a1a1a",
                    borderRadius: "2px",
                    overflow: "hidden",
                  }}>
                    <div style={{
                      height: "100%",
                      width: `${winRate}%`,
                      background: `linear-gradient(90deg, ${stratColor}80, ${stratColor})`,
                      borderRadius: "2px",
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          // Paper mode — Visual stats + Activity log
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {/* Stats cards */}
            <div style={{ display: "flex", gap: "6px" }}>
              {signalCount !== undefined && (
                <div style={{
                  flex: 1,
                  background: "rgba(0,188,212,0.05)",
                  border: "1px solid rgba(0,188,212,0.15)",
                  borderRadius: "4px",
                  padding: "8px 6px",
                  textAlign: "center",
                }}>
                  <div style={{ fontSize: "18px", fontWeight: 700, color: "#00BCD4", fontVariantNumeric: "tabular-nums", lineHeight: 1.2 }}>
                    {signalCount}
                  </div>
                  <div style={{ fontSize: "8px", color: "#555", textTransform: "uppercase", letterSpacing: "0.08em", marginTop: "2px" }}>Signals</div>
                </div>
              )}
              {categoryCount !== undefined && (
                <div style={{
                  flex: 1,
                  background: "rgba(255,102,0,0.05)",
                  border: "1px solid rgba(255,102,0,0.15)",
                  borderRadius: "4px",
                  padding: "8px 6px",
                  textAlign: "center",
                }}>
                  <div style={{ fontSize: "18px", fontWeight: 700, color: "#FF6600", fontVariantNumeric: "tabular-nums", lineHeight: 1.2 }}>
                    {categoryCount}
                  </div>
                  <div style={{ fontSize: "8px", color: "#555", textTransform: "uppercase", letterSpacing: "0.08em", marginTop: "2px" }}>Markets</div>
                </div>
              )}
            </div>

            {/* Activity log */}
            {recentActivity.length > 0 && (
              <div>
                <div style={{
                  fontSize: "8px",
                  color: "#555",
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  marginBottom: "6px",
                  fontWeight: 700,
                }}>
                  Activity Log
                </div>
                {recentActivity.map((a, i) => {
                  const stratColor = STRAT_COLOR[a.scan_type] || "#888";
                  const desc = a.description.length > 40 ? a.description.slice(0, 38) + "\u2026" : a.description;
                  return (
                    <div
                      key={`${a.ticker}-${a.timestamp}-${i}`}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "5px",
                        fontSize: "8px",
                        padding: "3px 0",
                        lineHeight: "14px",
                        borderLeft: `2px solid ${stratColor}`,
                        paddingLeft: "6px",
                        marginBottom: "2px",
                      }}
                    >
                      <span style={{
                        color: "#444",
                        fontVariantNumeric: "tabular-nums",
                        flexShrink: 0,
                        fontSize: "7px",
                      }} suppressHydrationWarning>
                        {formatTimestamp(a.timestamp)}
                      </span>
                      <span style={{
                        color: "#777",
                        overflow: "hidden",
                        whiteSpace: "nowrap",
                        textOverflow: "ellipsis",
                        minWidth: 0,
                      }}>
                        {desc}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}

            {recentActivity.length === 0 && (
              <div style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: "20px 0",
                gap: "8px",
              }}>
                <div style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "50%",
                  border: "2px solid #1a1a1a",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  animation: "terminal-pulse 3s ease-in-out infinite",
                }}>
                  <span style={{ fontSize: "16px", color: "#222" }}>{"\u25B6"}</span>
                </div>
                <span style={{ fontSize: "9px", color: "#444" }}>Scanning for opportunities...</span>
                <span style={{ fontSize: "8px", color: "#333" }}>Signals appear here when detected</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
