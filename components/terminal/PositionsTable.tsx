"use client";

// OMI Terminal — Positions Table (Visual Overhaul v3)
// Center-column positions/fills/orders display.
// Data fetching preserved from KalshiPanel — polls same endpoints.
// DO NOT change API routes or data fetching logic.

import { useState, useEffect, useCallback } from "react";

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

// ── Component ───────────────────────────────────────────────

export default function PositionsTable() {
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
            (mp: MarketPosition) => mp.position !== 0,
          ),
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

  const tabs: { key: Tab; label: string }[] = [
    { key: "positions", label: `Positions (${positions.length})` },
    { key: "fills", label: "Fills" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
      {/* Tab bar */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "0",
        borderBottom: "1px solid #1a1a1a",
        flexShrink: 0,
      }}>
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
              borderBottom: tab === t.key ? "1px solid #FF6600" : "1px solid transparent",
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
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "#333", fontSize: "9px" }}>
            Loading...
          </div>
        ) : tab === "positions" ? (
          positions.length === 0 ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "#333", fontSize: "9px" }}>
              No open positions
            </div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "9px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #1a1a1a" }}>
                  <th style={thStyle}>Market</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Position</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Exposure</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Realized P&L</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p, i) => (
                  <tr
                    key={p.ticker}
                    style={{
                      background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                      borderBottom: "1px solid #111",
                    }}
                  >
                    <td style={{ padding: "4px 6px", color: "#ccc", fontWeight: 500 }}>
                      <div style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: "200px" }} title={p.ticker}>
                        {parseEvent(p.ticker)}
                      </div>
                    </td>
                    <td style={{
                      padding: "4px 6px",
                      textAlign: "right",
                      fontVariantNumeric: "tabular-nums",
                      color: p.position > 0 ? "#00FF88" : "#FF3366",
                      fontWeight: 600,
                    }}>
                      {p.position > 0 ? "+" : ""}{p.position}
                    </td>
                    <td style={{
                      padding: "4px 6px",
                      textAlign: "right",
                      fontVariantNumeric: "tabular-nums",
                      color: "#777",
                    }}>
                      ${p.market_exposure_dollars}
                    </td>
                    <td style={{
                      padding: "4px 6px",
                      textAlign: "right",
                      fontVariantNumeric: "tabular-nums",
                      color: p.realized_pnl > 0 ? "#00FF88" : p.realized_pnl < 0 ? "#FF3366" : "#555",
                      fontWeight: 600,
                    }}>
                      ${p.realized_pnl_dollars}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        ) : (
          fills.length === 0 ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "#333", fontSize: "9px" }}>
              No recent fills
            </div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "9px" }}>
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
                      background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                      borderBottom: "1px solid #111",
                    }}
                  >
                    <td style={{ padding: "4px 6px", color: "#555", fontVariantNumeric: "tabular-nums" }}>
                      {timeAgo(f.created_time)}
                    </td>
                    <td style={{ padding: "4px 6px" }}>
                      <span style={{
                        color: f.action === "buy" ? "#00FF88" : "#FF3366",
                        fontWeight: 700,
                        fontSize: "8px",
                      }}>
                        {f.action.toUpperCase()}
                      </span>
                      {" "}
                      <span style={{
                        color: f.side === "yes" ? "#00BCD4" : "#FF9800",
                        fontSize: "8px",
                      }}>
                        {f.side.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: "4px 6px", color: "#999", maxWidth: "150px", overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }} title={f.ticker}>
                      {parseEvent(f.ticker)}
                    </td>
                    <td style={{ padding: "4px 6px", textAlign: "right", color: "#ccc", fontVariantNumeric: "tabular-nums" }}>
                      {f.count}
                    </td>
                    <td style={{ padding: "4px 6px", textAlign: "right", color: "#ccc", fontVariantNumeric: "tabular-nums" }}>
                      {f.side === "yes" ? f.yes_price : f.no_price}c
                    </td>
                    <td style={{ padding: "4px 6px", textAlign: "right", color: "#444", fontVariantNumeric: "tabular-nums" }}>
                      ${f.fee_cost}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}
      </div>
    </div>
  );
}

const thStyle: React.CSSProperties = {
  padding: "4px 6px",
  textAlign: "left",
  fontWeight: 600,
  color: "#555",
  fontSize: "8px",
  letterSpacing: "0.06em",
  textTransform: "uppercase",
};
