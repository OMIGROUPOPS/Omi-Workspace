"use client";

// OMI Terminal — Positions Table (Visual Overhaul v3)
// Center-column positions/fills/orders display.
// Data fetching preserved from KalshiPanel — polls same endpoints.
// DO NOT change API routes or data fetching logic.

import { useState, useEffect, useCallback } from "react";
import type { PnLBreakdown } from "@/lib/terminal/types";

// ── Types (preserved from KalshiPanel) ──────────────────────

interface MarketPosition {
  ticker: string;
  position: number;
  market_exposure: number;
  market_exposure_dollars: string;
  realized_pnl: number;
  realized_pnl_dollars: string;
  fees_paid_dollars: string;
  last_updated_ts: string;
}

interface KalshiFill {
  fill_id: string;
  ticker: string;
  market_ticker: string;
  side: "yes" | "no";
  action: "buy" | "sell";
  count: number;
  yes_price: number;
  no_price: number;
  price: number;
  fee_cost: string;
  created_time: string;
  is_taker: boolean;
}

type Tab = "positions" | "fills";

// ── New Props ────────────────────────────────────────────────

interface PositionsTableProps {
  totalPnl?: number;          // Session P&L in cents
  breakdowns?: PnLBreakdown[]; // Strategy breakdown
  openTrades?: number;        // Open trade count
  recentActivity?: Array<{
    scan_type: string;
    ticker: string;
    severity: string;
    description: string;
    timestamp: number;
  }>;
}

// ── Helpers ─────────────────────────────────────────────────

function parseEvent(ticker: string): string {
  const parts = ticker.split("-");
  if (parts.length < 2) return ticker;
  const prefix = parts[0];
  let league = "";
  if (prefix.includes("NHL")) league = "NHL";
  else if (prefix.includes("NBA")) league = "NBA";
  else if (prefix.includes("NCAAM")) league = "NCAAM";
  else if (prefix.includes("NCAAF")) league = "NCAAF";
  else if (prefix.includes("DOGE")) league = "CRYPTO";
  else league = prefix.replace("KX", "").replace("GAME", "");
  const team = parts.length >= 3 ? parts[parts.length - 1] : "";
  return team ? `${league} · ${team}` : league;
}

function timeAgo(isoStr: string): string {
  const diff = Date.now() - new Date(isoStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "now";
  if (mins < 60) return `${mins}m`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h`;
  return `${Math.floor(hrs / 24)}d`;
}

// ── Component ────────────────────────────────────────────────

export default function PositionsTable({
  totalPnl,
  breakdowns = [],
  openTrades,
  recentActivity,
}: PositionsTableProps) {
  const [tab, setTab] = useState<Tab>("positions");
  const [positions, setPositions] = useState<MarketPosition[]>([]);
  const [fills, setFills] = useState<KalshiFill[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [posRes, fillRes] = await Promise.allSettled([
        fetch("/api/kalshi/positions", { cache: "no-store" }),
        fetch("/api/kalshi/fills", { cache: "no-store" }),
      ]);

      if (posRes.status === "fulfilled" && posRes.value.ok) {
        const p = await posRes.value.json();
        setPositions(
          (p.market_positions || []).filter(
            (mp: MarketPosition) => mp.position !== 0
          )
        );
      }
      if (fillRes.status === "fulfilled" && fillRes.value.ok) {
        const f = await fillRes.value.json();
        setFills(f.fills || []);
      }
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 8000);
    return () => clearInterval(id);
  }, [fetchData]);

  // Derive wins/losses from breakdowns
  const totalWins = breakdowns.reduce((sum, b) => sum + b.winners, 0);
  const totalLosses = breakdowns.reduce((sum, b) => sum + b.losers, 0);
  const totalTrades = totalWins + totalLosses;

  // Average win / loss from breakdowns that have winners/losers
  const winnerBreakdowns = breakdowns.filter((b) => b.winners > 0);
  const loserBreakdowns = breakdowns.filter((b) => b.losers > 0);
  const avgWin =
    winnerBreakdowns.length > 0
      ? winnerBreakdowns.reduce((sum, b) => {
          // estimate: positive portion of total_pnl / winners
          const winPnl = b.total_pnl > 0 ? b.total_pnl : 0;
          return sum + (b.winners > 0 ? winPnl / b.winners : 0);
        }, 0) / winnerBreakdowns.length
      : null;
  const avgLoss =
    loserBreakdowns.length > 0
      ? loserBreakdowns.reduce((sum, b) => {
          const lossPnl = b.total_pnl < 0 ? b.total_pnl : 0;
          return sum + (b.losers > 0 ? lossPnl / b.losers : 0);
        }, 0) / loserBreakdowns.length
      : null;

  const pnlCents = totalPnl ?? 0;
  const pnlDollars = pnlCents / 100;
  const pnlColor =
    pnlDollars > 0 ? "#00FF88" : pnlDollars < 0 ? "#FF3366" : "#e0e0e0";
  const pnlPrefix = pnlDollars > 0 ? "+" : "";

  const hasPnlData = totalPnl !== undefined || breakdowns.length > 0;

  const tabs: { key: Tab; label: string }[] = [
    { key: "positions", label: `Positions (${positions.length})` },
    { key: "fills", label: "Fills" },
  ];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        overflow: "hidden",
      }}
    >
      {/* P&L Summary — shown when data is available */}
      {hasPnlData && (
        <div
          style={{
            padding: "6px 8px",
            borderBottom: "1px solid #1a1a1a",
            flexShrink: 0,
          }}
        >
          {/* Session P&L — large prominent display */}
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: "6px",
              marginBottom: "4px",
            }}
          >
            <span style={{ fontSize: "8px", color: "#5a6577", letterSpacing: "0.08em" }}>
              SESSION
            </span>
            <span
              style={{
                fontSize: "14px",
                fontWeight: 700,
                color: pnlColor,
                fontVariantNumeric: "tabular-nums",
                letterSpacing: "-0.01em",
              }}
            >
              {pnlPrefix}${Math.abs(pnlDollars).toFixed(2)}
            </span>
            {openTrades !== undefined && openTrades > 0 && (
              <span
                style={{
                  fontSize: "8px",
                  color: "#FF6600",
                  fontVariantNumeric: "tabular-nums",
                  marginLeft: "auto",
                }}
              >
                {openTrades} open
              </span>
            )}
          </div>

          {/* Wins / Losses + averages row */}
          {totalTrades > 0 && (
            <div
              style={{
                display: "flex",
                gap: "10px",
                fontSize: "8px",
                flexWrap: "wrap",
              }}
            >
              <span>
                <span style={{ color: "#5a6577" }}>Wins: </span>
                <span style={{ color: "#00FF88", fontVariantNumeric: "tabular-nums" }}>
                  {totalWins}
                </span>
              </span>
              <span>
                <span style={{ color: "#5a6577" }}>Losses: </span>
                <span style={{ color: "#FF3366", fontVariantNumeric: "tabular-nums" }}>
                  {totalLosses}
                </span>
              </span>
              {avgWin !== null && (
                <span>
                  <span style={{ color: "#5a6577" }}>Avg win: </span>
                  <span
                    style={{ color: "#00FF88", fontVariantNumeric: "tabular-nums" }}
                  >
                    +${(avgWin / 100).toFixed(2)}
                  </span>
                </span>
              )}
              {avgLoss !== null && (
                <span>
                  <span style={{ color: "#5a6577" }}>Avg loss: </span>
                  <span
                    style={{ color: "#FF3366", fontVariantNumeric: "tabular-nums" }}
                  >
                    -${(Math.abs(avgLoss) / 100).toFixed(2)}
                  </span>
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0",
          borderBottom: "1px solid #1a1a1a",
          flexShrink: 0,
        }}
      >
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            style={{
              padding: "5px 10px",
              fontSize: "9px",
              fontWeight: tab === t.key ? 700 : 500,
              color: tab === t.key ? "#FF6600" : "#555",
              background: "none",
              border: "none",
              borderBottom:
                tab === t.key
                  ? "1px solid #FF6600"
                  : "1px solid transparent",
              cursor: "pointer",
              fontFamily: "inherit",
              letterSpacing: "0.06em",
              transition: "color 0.12s",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: "auto", minHeight: 0 }}>
        {loading ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "#333",
              fontSize: "9px",
            }}
          >
            Loading...
          </div>
        ) : tab === "positions" ? (
          positions.length === 0 ? (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                color: "#333",
                fontSize: "9px",
              }}
            >
              No open positions
            </div>
          ) : (
            <table
              style={{ width: "100%", borderCollapse: "collapse", fontSize: "9px" }}
            >
              <thead>
                <tr style={{ borderBottom: "1px solid #1a1a1a" }}>
                  <th style={thStyle}>Market</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Position</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Exposure</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Realized P&amp;L</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p, i) => (
                  <tr
                    key={p.ticker}
                    style={{
                      background:
                        i % 2 === 0
                          ? "transparent"
                          : "rgba(255,255,255,0.01)",
                      borderBottom: "1px solid #111",
                    }}
                  >
                    <td
                      style={{
                        padding: "4px 6px",
                        color: "#ccc",
                        fontWeight: 500,
                      }}
                    >
                      <div
                        style={{
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          maxWidth: "200px",
                        }}
                        title={p.ticker}
                      >
                        {parseEvent(p.ticker)}
                      </div>
                    </td>
                    <td
                      style={{
                        padding: "4px 6px",
                        textAlign: "right",
                        fontVariantNumeric: "tabular-nums",
                        color: p.position > 0 ? "#00FF88" : "#FF3366",
                        fontWeight: 600,
                      }}
                    >
                      {p.position > 0 ? "+" : ""}
                      {p.position}
                    </td>
                    <td
                      style={{
                        padding: "4px 6px",
                        textAlign: "right",
                        fontVariantNumeric: "tabular-nums",
                        color: "#777",
                      }}
                    >
                      ${p.market_exposure_dollars}
                    </td>
                    <td
                      style={{
                        padding: "4px 6px",
                        textAlign: "right",
                        fontVariantNumeric: "tabular-nums",
                        color:
                          p.realized_pnl > 0
                            ? "#00FF88"
                            : p.realized_pnl < 0
                            ? "#FF3366"
                            : "#555",
                        fontWeight: 600,
                      }}
                    >
                      ${p.realized_pnl_dollars}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        ) : fills.length === 0 ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "#333",
              fontSize: "9px",
            }}
          >
            No recent fills
          </div>
        ) : (
          <table
            style={{ width: "100%", borderCollapse: "collapse", fontSize: "9px" }}
          >
            <thead>
              <tr style={{ borderBottom: "1px solid #1a1a1a" }}>
                <th style={thStyle}>Time</th>
                <th style={thStyle}>Action</th>
                <th style={thStyle}>Market</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Qty</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Price</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Fee</th>
              </tr>
            </thead>
            <tbody>
              {fills.map((f, i) => (
                <tr
                  key={f.fill_id}
                  style={{
                    background:
                      i % 2 === 0
                        ? "transparent"
                        : "rgba(255,255,255,0.01)",
                    borderBottom: "1px solid #111",
                  }}
                >
                  <td
                    style={{
                      padding: "4px 6px",
                      color: "#555",
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {timeAgo(f.created_time)}
                  </td>
                  <td style={{ padding: "4px 6px" }}>
                    <span
                      style={{
                        color: f.action === "buy" ? "#00FF88" : "#FF3366",
                        fontWeight: 700,
                        fontSize: "8px",
                      }}
                    >
                      {f.action.toUpperCase()}
                    </span>{" "}
                    <span
                      style={{
                        color: f.side === "yes" ? "#00BCD4" : "#FF9800",
                        fontSize: "8px",
                      }}
                    >
                      {f.side.toUpperCase()}
                    </span>
                  </td>
                  <td
                    style={{
                      padding: "4px 6px",
                      color: "#999",
                      maxWidth: "150px",
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}
                    title={f.ticker}
                  >
                    {parseEvent(f.ticker)}
                  </td>
                  <td
                    style={{
                      padding: "4px 6px",
                      textAlign: "right",
                      color: "#ccc",
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {f.count}
                  </td>
                  <td
                    style={{
                      padding: "4px 6px",
                      textAlign: "right",
                      color: "#ccc",
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {f.side === "yes" ? f.yes_price : f.no_price}c
                  </td>
                  <td
                    style={{
                      padding: "4px 6px",
                      textAlign: "right",
                      color: "#444",
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    ${f.fee_cost}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

// ── Table header style ────────────────────────────────────────

const thStyle: React.CSSProperties = {
  padding: "4px 6px",
  textAlign: "left",
  fontWeight: 600,
  color: "#555",
  fontSize: "8px",
  letterSpacing: "0.06em",
  textTransform: "uppercase",
};
