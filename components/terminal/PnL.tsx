"use client";

// OMI Terminal — P&L panel
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

  return (
    <div className="h-full flex flex-col">
      {/* Total */}
      <div style={{ marginBottom: "6px" }}>
        <div style={{ fontSize: "8px", color: "#444", textTransform: "uppercase", letterSpacing: "0.1em" }}>
          Session P&L
        </div>
        <div style={{ fontSize: "20px", fontWeight: 700, fontVariantNumeric: "tabular-nums", color: pnlColor, lineHeight: 1.2 }}>
          {totalPnl >= 0 ? "+" : ""}{(totalPnl / 100).toFixed(2)}
          <span style={{ fontSize: "10px", color: "#333", marginLeft: "4px" }}>USD</span>
        </div>
        <div style={{ fontSize: "8px", color: "#444", marginTop: "1px" }}>
          {openTrades} open
        </div>
      </div>

      {/* Strategy breakdown */}
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {breakdowns.length === 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ fontSize: "9px", color: "#FF6600", fontWeight: 600, letterSpacing: "0.05em" }}>
              PAPER MODE
            </div>

            {/* Activity log */}
            {recentActivity.length > 0 ? (
              <div>
                <div style={{ fontSize: "7px", color: "#444", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "3px", marginTop: "2px" }}>
                  Activity Log
                </div>
                {recentActivity.map((a, i) => {
                  const stratColor = STRAT_COLOR[a.scan_type] || "#888";
                  // Truncate description
                  const desc = a.description.length > 40 ? a.description.slice(0, 38) + "\u2026" : a.description;
                  return (
                    <div
                      key={`${a.ticker}-${a.timestamp}-${i}`}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                        fontSize: "8px",
                        padding: "1px 0",
                        lineHeight: "12px",
                      }}
                    >
                      <span style={{ color: "#333", fontVariantNumeric: "tabular-nums", flexShrink: 0, fontSize: "7px" }} suppressHydrationWarning>
                        {formatTimestamp(a.timestamp)}
                      </span>
                      <span style={{
                        width: "3px",
                        height: "3px",
                        borderRadius: "50%",
                        background: stratColor,
                        flexShrink: 0,
                      }} />
                      <span style={{
                        color: "#555",
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
            ) : (
              <>
                <div style={{ fontSize: "8px", color: "#444" }}>Monitoring for opportunities...</div>
                {signalCount !== undefined && (
                  <div style={{ fontSize: "8px", color: "#555", marginTop: "4px" }}>
                    <span style={{ color: "#00BCD4" }}>{signalCount}</span> signals detected
                  </div>
                )}
                {categoryCount !== undefined && (
                  <div style={{ fontSize: "8px", color: "#555" }}>
                    <span style={{ color: "#888" }}>{categoryCount}</span> categories active
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          breakdowns.map((b) => {
            const c = b.total_pnl > 0 ? "#00FF88" : b.total_pnl < 0 ? "#FF3366" : "#555";
            const stratColor = STRAT_COLOR[b.scan_type] || "#888";
            const label = b.scan_type.replace("_", " ");

            return (
              <div
                key={b.scan_type}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  fontSize: "9px",
                  padding: "2px 0",
                  borderBottom: "1px solid #111",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <span style={{ width: "3px", height: "10px", borderRadius: "1px", background: stratColor, flexShrink: 0 }} />
                  <span style={{ color: "#777", fontSize: "8px" }}>{label}</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ color: "#444", fontVariantNumeric: "tabular-nums", fontSize: "8px" }}>
                    {b.trade_count}t {b.winners}W/{b.losers}L
                  </span>
                  <span style={{ fontVariantNumeric: "tabular-nums", fontWeight: 600, color: c, minWidth: "36px", textAlign: "right" }}>
                    {b.total_pnl >= 0 ? "+" : ""}{b.total_pnl}&cent;
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
