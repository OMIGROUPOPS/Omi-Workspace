"use client";

// OMI Terminal — P&L panel (Redesigned)
// Session P&L, strategy breakdown, activity feed in paper mode.

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
  resolution: "RES",
  momentum_lag: "MTM",
  contradiction_mono: "MONO",
  contradiction_cross: "XCON",
  whale_momentum: "WHL",
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
      {/* Total P&L header */}
      <div style={{
        marginBottom: "6px",
        padding: "4px 2px",
        borderBottom: "1px solid #1a1a1a",
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{
            fontSize: "8px",
            color: "#555",
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            fontWeight: 600,
          }}>
            Session P&L
          </span>
          {hasTrades ? (
            <span style={{ fontSize: "8px", color: "#444" }}>{openTrades} open</span>
          ) : (
            <span style={{
              fontSize: "7px",
              fontWeight: 700,
              padding: "1px 5px",
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
          fontSize: "22px",
          fontWeight: 700,
          fontVariantNumeric: "tabular-nums",
          color: pnlColor,
          lineHeight: 1.2,
          textShadow: totalPnl !== 0 ? `0 0 12px ${pnlColor}40` : "none",
        }}>
          {totalPnl >= 0 ? "+" : ""}{(totalPnl / 100).toFixed(2)}
          <span style={{ fontSize: "9px", color: "#444", marginLeft: "4px", fontWeight: 400 }}>USD</span>
        </div>
      </div>

      {/* Strategy breakdown or Activity log */}
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {hasTrades ? (
          // Real trades — strategy breakdown
          breakdowns.map((b) => {
            const c = b.total_pnl > 0 ? "#00FF88" : b.total_pnl < 0 ? "#FF3366" : "#555";
            const stratColor = STRAT_COLOR[b.scan_type] || "#888";
            const label = STRAT_LABEL[b.scan_type] || b.scan_type;

            return (
              <div
                key={b.scan_type}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  fontSize: "9px",
                  padding: "4px 2px",
                  borderBottom: "1px solid #111",
                  borderLeft: `2px solid ${stratColor}`,
                  marginLeft: "-2px",
                  paddingLeft: "6px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{
                    fontSize: "7px",
                    fontWeight: 600,
                    padding: "1px 4px",
                    borderRadius: "2px",
                    background: `${stratColor}20`,
                    color: stratColor,
                  }}>
                    {label}
                  </span>
                  <span style={{ color: "#555", fontSize: "8px", fontVariantNumeric: "tabular-nums" }}>
                    {b.trade_count}t {b.winners}W/{b.losers}L
                  </span>
                </div>
                <span style={{
                  fontVariantNumeric: "tabular-nums",
                  fontWeight: 700,
                  color: c,
                  minWidth: "42px",
                  textAlign: "right",
                }}>
                  {b.total_pnl >= 0 ? "+" : ""}{b.total_pnl}&cent;
                </span>
              </div>
            );
          })
        ) : (
          // Paper mode — Activity log + stats
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {/* Stats row */}
            <div style={{
              display: "flex",
              gap: "8px",
              padding: "4px 0",
              borderBottom: "1px solid #111",
            }}>
              {signalCount !== undefined && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
                  <span style={{ fontSize: "14px", fontWeight: 700, color: "#00BCD4", fontVariantNumeric: "tabular-nums" }}>
                    {signalCount}
                  </span>
                  <span style={{ fontSize: "7px", color: "#444", textTransform: "uppercase", letterSpacing: "0.08em" }}>Signals</span>
                </div>
              )}
              {categoryCount !== undefined && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
                  <span style={{ fontSize: "14px", fontWeight: 700, color: "#888", fontVariantNumeric: "tabular-nums" }}>
                    {categoryCount}
                  </span>
                  <span style={{ fontSize: "7px", color: "#444", textTransform: "uppercase", letterSpacing: "0.08em" }}>Categories</span>
                </div>
              )}
            </div>

            {/* Activity log */}
            {recentActivity.length > 0 && (
              <div>
                <div style={{
                  fontSize: "7px",
                  color: "#555",
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  marginBottom: "4px",
                  fontWeight: 600,
                }}>
                  Activity Log
                </div>
                {recentActivity.map((a, i) => {
                  const stratColor = STRAT_COLOR[a.scan_type] || "#888";
                  const desc = a.description.length > 35 ? a.description.slice(0, 33) + "\u2026" : a.description;
                  return (
                    <div
                      key={`${a.ticker}-${a.timestamp}-${i}`}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                        fontSize: "8px",
                        padding: "2px 0",
                        lineHeight: "13px",
                        borderLeft: `2px solid ${stratColor}`,
                        paddingLeft: "4px",
                        marginBottom: "1px",
                      }}
                    >
                      <span style={{
                        color: "#333",
                        fontVariantNumeric: "tabular-nums",
                        flexShrink: 0,
                        fontSize: "7px",
                      }} suppressHydrationWarning>
                        {formatTimestamp(a.timestamp)}
                      </span>
                      <span style={{
                        color: "#666",
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
                padding: "12px 0",
                gap: "4px",
              }}>
                <span style={{ fontSize: "14px", opacity: 0.2 }}>{"\u25B6"}</span>
                <span style={{ fontSize: "8px", color: "#333" }}>Monitoring for opportunities...</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
