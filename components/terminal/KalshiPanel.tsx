"use client";

// OMI Terminal — Kalshi Trading Panel
// Live positions, fills, balance, order entry + cancel.
// Polls /api/kalshi/* endpoints. Styling matches Bloomberg terminal aesthetic.
// DO NOT change API routes or data fetching logic in other components.

import { useState, useEffect, useCallback } from "react";

// ── Types ───────────────────────────────────────────────────

interface KalshiBalance {
  balance: number;
  portfolio_value: number;
}

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

interface KalshiOrder {
  order_id: string;
  ticker: string;
  action: "buy" | "sell";
  side: "yes" | "no";
  type: "limit" | "market";
  status: string;
  yes_price: number;
  no_price: number;
  remaining_count: number;
  count: number;
  created_time: string;
}

type Tab = "positions" | "fills" | "orders" | "trade";

// ── Helpers ─────────────────────────────────────────────────

function centsToUsd(cents: number): string {
  return (cents / 100).toFixed(2);
}

function parseTicker(ticker: string): string {
  // KXNHLGAME-26MAR02DALVAN-VAN → VAN (DAL vs VAN)
  const parts = ticker.split("-");
  if (parts.length >= 3) return parts[parts.length - 1];
  if (parts.length === 2) return parts[1];
  return ticker;
}

function parseEvent(ticker: string): string {
  // KXNHLGAME-26MAR02DALVAN-VAN → NHL · DAL vs VAN
  const parts = ticker.split("-");
  if (parts.length < 2) return ticker;
  const prefix = parts[0];
  // Extract league
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

interface KalshiPanelProps {
  onBalanceUpdate?: (balance: number) => void;
}

export default function KalshiPanel({ onBalanceUpdate }: KalshiPanelProps) {
  const [tab, setTab] = useState<Tab>("positions");
  const [balance, setBalance] = useState<KalshiBalance | null>(null);
  const [positions, setPositions] = useState<MarketPosition[]>([]);
  const [fills, setFills] = useState<KalshiFill[]>([]);
  const [orders, setOrders] = useState<KalshiOrder[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Order entry state
  const [orderTicker, setOrderTicker] = useState("");
  const [orderSide, setOrderSide] = useState<"yes" | "no">("yes");
  const [orderAction, setOrderAction] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"limit" | "market">("market");
  const [orderCount, setOrderCount] = useState(10);
  const [orderPrice, setOrderPrice] = useState(50);
  const [submitting, setSubmitting] = useState(false);
  const [orderResult, setOrderResult] = useState<string | null>(null);

  // ── Data fetching ─────────────────────────────────────────

  const fetchAll = useCallback(async () => {
    try {
      const [balRes, posRes, fillRes, ordRes] = await Promise.allSettled([
        fetch("/api/kalshi/balance", { cache: "no-store" }),
        fetch("/api/kalshi/positions", { cache: "no-store" }),
        fetch("/api/kalshi/fills", { cache: "no-store" }),
        fetch("/api/kalshi/orders", { cache: "no-store" }),
      ]);

      if (balRes.status === "fulfilled" && balRes.value.ok) {
        const b = await balRes.value.json();
        setBalance(b);
        onBalanceUpdate?.(b.balance);
      }
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
      if (ordRes.status === "fulfilled" && ordRes.value.ok) {
        const o = await ordRes.value.json();
        setOrders(o.orders || []);
      }

      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection error");
    } finally {
      setLoading(false);
    }
  }, [onBalanceUpdate]);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 8000);
    return () => clearInterval(id);
  }, [fetchAll]);

  // ── Order submission ──────────────────────────────────────

  const submitOrder = async () => {
    if (!orderTicker.trim()) return;
    setSubmitting(true);
    setOrderResult(null);
    try {
      const body: Record<string, unknown> = {
        ticker: orderTicker.trim().toUpperCase(),
        action: orderAction,
        side: orderSide,
        type: orderType,
        count: orderCount,
      };
      if (orderType === "limit") {
        if (orderSide === "yes") body.yes_price = orderPrice;
        else body.no_price = orderPrice;
      }
      const res = await fetch("/api/kalshi/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (res.ok) {
        setOrderResult(`✓ Order placed: ${data.order?.order_id?.slice(0, 8)}`);
        fetchAll();
      } else {
        setOrderResult(`✗ ${data.error || "Order failed"}`);
      }
    } catch {
      setOrderResult("✗ Network error");
    } finally {
      setSubmitting(false);
    }
  };

  const cancelOrderById = async (orderId: string) => {
    try {
      await fetch(`/api/kalshi/orders?order_id=${orderId}`, { method: "DELETE" });
      fetchAll();
    } catch {
      // silent
    }
  };

  // ── Styles ────────────────────────────────────────────────

  const s = {
    panel: {
      display: "flex",
      flexDirection: "column" as const,
      height: "100%",
      overflow: "hidden",
      fontSize: "10px",
    },
    header: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "4px 6px",
      borderBottom: "1px solid #1a1a1a",
      flexShrink: 0,
    },
    title: {
      color: "#FF6600",
      fontWeight: 800,
      fontSize: "10px",
      letterSpacing: "0.12em",
    },
    balanceBox: {
      display: "flex",
      gap: "8px",
      alignItems: "center",
    },
    balanceVal: {
      color: "#00FF88",
      fontWeight: 700,
      fontVariantNumeric: "tabular-nums" as const,
      fontSize: "11px",
    },
    portfolioVal: {
      color: "#888",
      fontVariantNumeric: "tabular-nums" as const,
      fontSize: "9px",
    },
    tabs: {
      display: "flex",
      gap: "0px",
      padding: "0 4px",
      borderBottom: "1px solid #1a1a1a",
      flexShrink: 0,
    },
    tab: (active: boolean) => ({
      padding: "4px 8px",
      cursor: "pointer",
      color: active ? "#FF6600" : "#555",
      fontWeight: active ? 700 : 500,
      fontSize: "9px",
      letterSpacing: "0.08em",
      borderBottom: active ? "1px solid #FF6600" : "1px solid transparent",
      transition: "color 0.15s",
    }),
    body: {
      flex: 1,
      overflow: "auto",
      padding: "4px 6px",
      minHeight: 0,
    },
    row: (i: number) => ({
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "3px 4px",
      background: i % 2 === 0 ? "rgba(255,255,255,0.015)" : "transparent",
      borderRadius: "2px",
      gap: "4px",
    }),
    ticker: {
      color: "#ccc",
      fontWeight: 600,
      fontSize: "9px",
      whiteSpace: "nowrap" as const,
      overflow: "hidden" as const,
      textOverflow: "ellipsis" as const,
      maxWidth: "120px",
    },
    label: {
      color: "#555",
      fontSize: "8px",
      letterSpacing: "0.05em",
    },
    green: { color: "#00FF88", fontWeight: 600, fontVariantNumeric: "tabular-nums" as const },
    red: { color: "#FF3366", fontWeight: 600, fontVariantNumeric: "tabular-nums" as const },
    dim: { color: "#444", fontVariantNumeric: "tabular-nums" as const },
    // Order entry
    input: {
      background: "#111",
      border: "1px solid #222",
      color: "#ccc",
      padding: "3px 6px",
      fontSize: "10px",
      borderRadius: "2px",
      outline: "none",
      fontFamily: "inherit",
      width: "100%",
    },
    btnGroup: {
      display: "flex",
      gap: "2px",
    },
    toggleBtn: (active: boolean, color?: string) => ({
      padding: "3px 8px",
      fontSize: "9px",
      fontWeight: active ? 700 : 500,
      color: active ? (color || "#FF6600") : "#555",
      background: active ? "rgba(255,102,0,0.1)" : "transparent",
      border: `1px solid ${active ? (color || "#FF6600") + "44" : "#222"}`,
      borderRadius: "2px",
      cursor: "pointer",
      fontFamily: "inherit",
      letterSpacing: "0.05em",
    }),
    submitBtn: {
      padding: "5px 12px",
      fontSize: "10px",
      fontWeight: 700,
      color: "#000",
      background: "#FF6600",
      border: "none",
      borderRadius: "2px",
      cursor: "pointer",
      fontFamily: "inherit",
      letterSpacing: "0.08em",
      width: "100%",
      marginTop: "4px",
    },
  };

  // ── Render ────────────────────────────────────────────────

  if (loading) {
    return (
      <div style={s.panel}>
        <div style={s.header}>
          <span style={s.title}>KALSHI</span>
          <span style={{ color: "#FFD600", fontSize: "9px" }}>CONNECTING...</span>
        </div>
        <div style={{ ...s.body, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ color: "#333", fontSize: "10px" }}>Authenticating...</span>
        </div>
      </div>
    );
  }

  if (error && !balance) {
    return (
      <div style={s.panel}>
        <div style={s.header}>
          <span style={s.title}>KALSHI</span>
          <span style={{ color: "#FF3366", fontSize: "9px" }}>ERROR</span>
        </div>
        <div style={{ ...s.body, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ color: "#FF3366", fontSize: "9px" }}>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div style={s.panel}>
      {/* Header with balance */}
      <div style={s.header}>
        <span style={s.title}>KALSHI</span>
        <div style={s.balanceBox}>
          {balance && (
            <>
              <span style={s.balanceVal}>${centsToUsd(balance.balance)}</span>
              <span style={s.portfolioVal}>+${centsToUsd(balance.portfolio_value)} pos</span>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div style={s.tabs}>
        {(["positions", "fills", "orders", "trade"] as Tab[]).map((t) => (
          <span key={t} style={s.tab(tab === t)} onClick={() => setTab(t)}>
            {t === "positions"
              ? `POS (${positions.length})`
              : t === "fills"
                ? `FILLS`
                : t === "orders"
                  ? `ORD (${orders.length})`
                  : "TRADE"}
          </span>
        ))}
      </div>

      {/* Body */}
      <div style={s.body}>
        {/* ── Positions tab ── */}
        {tab === "positions" && (
          <>
            {positions.length === 0 ? (
              <div style={{ color: "#333", textAlign: "center", padding: "20px 0", fontSize: "9px" }}>
                No open positions
              </div>
            ) : (
              positions.map((p, i) => (
                <div key={p.ticker} style={s.row(i)}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={s.ticker} title={p.ticker}>
                      {parseEvent(p.ticker)}
                    </div>
                    <div style={s.label}>{parseTicker(p.ticker)}</div>
                  </div>
                  <div style={{ textAlign: "right", flexShrink: 0 }}>
                    <div style={p.position > 0 ? s.green : s.red}>
                      {p.position > 0 ? "+" : ""}
                      {p.position} contracts
                    </div>
                    <div style={s.dim}>
                      ${p.market_exposure_dollars} exp
                    </div>
                  </div>
                </div>
              ))
            )}
          </>
        )}

        {/* ── Fills tab ── */}
        {tab === "fills" && (
          <>
            {fills.length === 0 ? (
              <div style={{ color: "#333", textAlign: "center", padding: "20px 0", fontSize: "9px" }}>
                No recent fills
              </div>
            ) : (
              fills.map((f, i) => (
                <div key={f.fill_id} style={s.row(i)}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <span
                        style={{
                          color: f.action === "buy" ? "#00FF88" : "#FF3366",
                          fontWeight: 700,
                          fontSize: "8px",
                          letterSpacing: "0.05em",
                        }}
                      >
                        {f.action.toUpperCase()}
                      </span>
                      <span
                        style={{
                          color: f.side === "yes" ? "#00BCD4" : "#FF9800",
                          fontWeight: 600,
                          fontSize: "8px",
                        }}
                      >
                        {f.side.toUpperCase()}
                      </span>
                      <span style={s.ticker} title={f.ticker}>
                        {parseEvent(f.ticker)}
                      </span>
                    </div>
                    <div style={s.label}>
                      {parseTicker(f.ticker)} · {timeAgo(f.created_time)}
                    </div>
                  </div>
                  <div style={{ textAlign: "right", flexShrink: 0 }}>
                    <div style={{ color: "#ccc", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                      {f.count} @ {f.side === "yes" ? f.yes_price : f.no_price}¢
                    </div>
                    <div style={s.dim}>
                      fee ${f.fee_cost}
                    </div>
                  </div>
                </div>
              ))
            )}
          </>
        )}

        {/* ── Orders tab ── */}
        {tab === "orders" && (
          <>
            {orders.length === 0 ? (
              <div style={{ color: "#333", textAlign: "center", padding: "20px 0", fontSize: "9px" }}>
                No resting orders
              </div>
            ) : (
              orders.map((o, i) => (
                <div key={o.order_id} style={s.row(i)}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <span
                        style={{
                          color: o.action === "buy" ? "#00FF88" : "#FF3366",
                          fontWeight: 700,
                          fontSize: "8px",
                        }}
                      >
                        {o.action.toUpperCase()}
                      </span>
                      <span style={s.ticker}>{parseEvent(o.ticker)}</span>
                    </div>
                    <div style={s.label}>
                      {o.remaining_count}/{o.count} @ {o.yes_price}¢ · {o.type}
                    </div>
                  </div>
                  <button
                    onClick={() => cancelOrderById(o.order_id)}
                    style={{
                      background: "rgba(255,51,102,0.1)",
                      border: "1px solid rgba(255,51,102,0.3)",
                      color: "#FF3366",
                      fontSize: "8px",
                      fontWeight: 700,
                      padding: "2px 6px",
                      borderRadius: "2px",
                      cursor: "pointer",
                      fontFamily: "inherit",
                    }}
                  >
                    CANCEL
                  </button>
                </div>
              ))
            )}
          </>
        )}

        {/* ── Trade tab ── */}
        {tab === "trade" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", padding: "2px 0" }}>
            {/* Ticker input */}
            <div>
              <div style={{ ...s.label, marginBottom: "2px" }}>TICKER</div>
              <input
                style={s.input}
                value={orderTicker}
                onChange={(e) => setOrderTicker(e.target.value)}
                placeholder="KXNHLGAME-26MAR02DALVAN-VAN"
                spellCheck={false}
              />
            </div>

            {/* Action: Buy / Sell */}
            <div>
              <div style={{ ...s.label, marginBottom: "2px" }}>ACTION</div>
              <div style={s.btnGroup}>
                <button
                  style={s.toggleBtn(orderAction === "buy", "#00FF88")}
                  onClick={() => setOrderAction("buy")}
                >
                  BUY
                </button>
                <button
                  style={s.toggleBtn(orderAction === "sell", "#FF3366")}
                  onClick={() => setOrderAction("sell")}
                >
                  SELL
                </button>
              </div>
            </div>

            {/* Side: Yes / No */}
            <div>
              <div style={{ ...s.label, marginBottom: "2px" }}>SIDE</div>
              <div style={s.btnGroup}>
                <button
                  style={s.toggleBtn(orderSide === "yes", "#00BCD4")}
                  onClick={() => setOrderSide("yes")}
                >
                  YES
                </button>
                <button
                  style={s.toggleBtn(orderSide === "no", "#FF9800")}
                  onClick={() => setOrderSide("no")}
                >
                  NO
                </button>
              </div>
            </div>

            {/* Type: Market / Limit */}
            <div>
              <div style={{ ...s.label, marginBottom: "2px" }}>TYPE</div>
              <div style={s.btnGroup}>
                <button
                  style={s.toggleBtn(orderType === "market")}
                  onClick={() => setOrderType("market")}
                >
                  MARKET
                </button>
                <button
                  style={s.toggleBtn(orderType === "limit")}
                  onClick={() => setOrderType("limit")}
                >
                  LIMIT
                </button>
              </div>
            </div>

            {/* Count */}
            <div>
              <div style={{ ...s.label, marginBottom: "2px" }}>CONTRACTS</div>
              <input
                style={s.input}
                type="number"
                min={1}
                max={500}
                value={orderCount}
                onChange={(e) => setOrderCount(Math.max(1, parseInt(e.target.value) || 1))}
              />
            </div>

            {/* Price (limit only) */}
            {orderType === "limit" && (
              <div>
                <div style={{ ...s.label, marginBottom: "2px" }}>PRICE (¢)</div>
                <input
                  style={s.input}
                  type="number"
                  min={1}
                  max={99}
                  value={orderPrice}
                  onChange={(e) => setOrderPrice(Math.max(1, Math.min(99, parseInt(e.target.value) || 50)))}
                />
              </div>
            )}

            {/* Cost preview */}
            <div style={{ color: "#666", fontSize: "9px", padding: "2px 0" }}>
              {orderType === "market"
                ? `Est. max cost: $${((orderCount * (orderSide === "yes" ? 99 : 99)) / 100).toFixed(2)}`
                : `Est. cost: $${((orderCount * orderPrice) / 100).toFixed(2)}`}
            </div>

            {/* Submit */}
            <button
              style={{
                ...s.submitBtn,
                opacity: submitting ? 0.5 : 1,
                background: orderAction === "buy" ? "#00FF88" : "#FF3366",
              }}
              onClick={submitOrder}
              disabled={submitting}
            >
              {submitting
                ? "SUBMITTING..."
                : `${orderAction.toUpperCase()} ${orderCount} ${orderSide.toUpperCase()}`}
            </button>

            {/* Result feedback */}
            {orderResult && (
              <div
                style={{
                  color: orderResult.startsWith("✓") ? "#00FF88" : "#FF3366",
                  fontSize: "9px",
                  padding: "2px 0",
                }}
              >
                {orderResult}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
