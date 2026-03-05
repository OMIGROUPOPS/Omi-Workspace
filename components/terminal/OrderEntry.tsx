"use client";

// OMI Terminal — Order Entry sidebar (Visual Overhaul v3)
// Slim right column. Extracted from KalshiPanel.
// ALL data fetching logic preserved from KalshiPanel — only UI restructured.
// DO NOT change API routes or data fetching logic.
// Renders TWO OEBox sections: ORDER ENTRY + CONTEXT.

import { useState, useEffect, useCallback } from "react";

// ── Types (preserved from KalshiPanel) ──────────────────────

interface KalshiBalance {
  balance: number;
  portfolio_value: number;
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

// ── Props ────────────────────────────────────────────────────

interface OrderEntryProps {
  onBalanceUpdate?: (balance: number) => void;
  selectedTicker?: string;
}

// ── OEBox helper ─────────────────────────────────────────────

function OEBox({
  title,
  icon,
  borderColor,
  children,
}: {
  title: string;
  icon: string;
  borderColor: string;
  children: React.ReactNode;
}) {
  return (
    <div
      style={{
        background: "#0d0d0d",
        border: `1px solid ${borderColor}`,
        borderRadius: "8px",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          padding: "6px 10px",
          background: `${borderColor}15`,
          borderBottom: `1px solid ${borderColor}30`,
          display: "flex",
          alignItems: "center",
          gap: "6px",
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: "10px" }}>{icon}</span>
        <span
          style={{
            fontSize: "9px",
            fontWeight: 700,
            color: borderColor,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
          }}
        >
          {title}
        </span>
      </div>
      <div style={{ padding: "8px" }}>{children}</div>
    </div>
  );
}

// ── Quick-quantity preset buttons ────────────────────────────

const QTY_PRESETS = [1, 5, 10, 25, 50, 100];

// ── Ticker context parser ────────────────────────────────────

function parseTickerContext(ticker: string): {
  league: string;
  event: string;
  marketType: string;
  team: string;
} {
  if (!ticker) {
    return { league: "", event: "", marketType: "", team: "" };
  }
  const parts = ticker.split("-");
  const prefix = parts[0] || "";
  let league = "";
  if (prefix.includes("NHL")) league = "NHL";
  else if (prefix.includes("NBA")) league = "NBA";
  else if (prefix.includes("NCAAM")) league = "NCAAM";
  else if (prefix.includes("NCAAF")) league = "NCAAF";
  else if (prefix.includes("DOGE") || prefix.includes("BTC") || prefix.includes("ETH"))
    league = "CRYPTO";
  else league = prefix.replace("KX", "").replace("GAME", "") || prefix;

  // Team: second-to-last segment (before Y/N suffix)
  const hasSuffix = parts[parts.length - 1] === "Y" || parts[parts.length - 1] === "N";
  const team = hasSuffix
    ? parts[parts.length - 2] || ""
    : parts[parts.length - 1] || "";

  // Market type: look for common patterns
  let marketType = "MONEYLINE";
  if (ticker.includes("SPREAD") || ticker.includes("SPR")) marketType = "SPREAD";
  else if (ticker.includes("TOTAL") || ticker.includes("TOT")) marketType = "TOTAL";
  else if (ticker.includes("HALF")) marketType = "1H/2H";

  const event = parts.slice(1, hasSuffix ? -2 : -1).join("-") || ticker;

  return { league, event, marketType, team };
}

// ── Component ────────────────────────────────────────────────

export default function OrderEntry({
  onBalanceUpdate,
  selectedTicker,
}: OrderEntryProps) {
  const [balance, setBalance] = useState<KalshiBalance | null>(null);
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

  // Sync selected ticker from parent
  useEffect(() => {
    if (selectedTicker) {
      setOrderTicker(selectedTicker);
    }
  }, [selectedTicker]);

  // ── Data fetching (preserved from KalshiPanel) ─────────────

  const fetchAll = useCallback(async () => {
    try {
      const [balRes, ordRes] = await Promise.allSettled([
        fetch("/api/kalshi/balance", { cache: "no-store" }),
        fetch("/api/kalshi/orders", { cache: "no-store" }),
      ]);

      if (balRes.status === "fulfilled" && balRes.value.ok) {
        const b = await balRes.value.json();
        setBalance(b);
        onBalanceUpdate?.(b.balance);
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

  // ── Order submission (preserved from KalshiPanel) ──────────

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
        setOrderResult(`Order placed: ${data.order?.order_id?.slice(0, 8)}`);
        fetchAll();
      } else {
        setOrderResult(`Error: ${data.error || "Order failed"}`);
      }
    } catch {
      setOrderResult("Network error");
    } finally {
      setSubmitting(false);
    }
  };

  const cancelOrderById = async (orderId: string) => {
    try {
      await fetch(`/api/kalshi/orders?order_id=${orderId}`, {
        method: "DELETE",
      });
      fetchAll();
    } catch {
      // silent
    }
  };

  // ── Derived state ──────────────────────────────────────────

  const estCost =
    orderType === "market"
      ? (orderCount * 99) / 100
      : (orderCount * orderPrice) / 100;

  const actionColor = orderAction === "buy" ? "#00FF88" : "#FF3366";
  const ctx = parseTickerContext(orderTicker);

  // ── Render ────────────────────────────────────────────────

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        height: "100%",
        overflow: "hidden",
      }}
    >
      {/* ── BOX 1: ORDER ENTRY ─────────────────────────────── */}
      <OEBox title="Order Entry" icon="⚡" borderColor="#FF6600">
        {/* Balance in header area */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "8px",
            paddingBottom: "6px",
            borderBottom: "1px solid #1a1a1a",
          }}
        >
          {loading ? (
            <span style={{ fontSize: "8px", color: "#FFD600" }}>
              CONNECTING
            </span>
          ) : error && !balance ? (
            <span style={{ fontSize: "8px", color: "#FF3366" }}>{error}</span>
          ) : balance ? (
            <>
              <span style={{ fontSize: "8px", color: "#5a6577" }}>Balance</span>
              <div style={{ display: "flex", gap: "10px", alignItems: "baseline" }}>
                <span
                  style={{
                    color: "#00FF88",
                    fontWeight: 700,
                    fontVariantNumeric: "tabular-nums",
                    fontSize: "11px",
                  }}
                >
                  ${(balance.balance / 100).toFixed(2)}
                </span>
                <span
                  style={{
                    fontSize: "8px",
                    color: "#555",
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  Portfolio ${(balance.portfolio_value / 100).toFixed(2)}
                </span>
              </div>
            </>
          ) : null}
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "6px",
          }}
        >
          {/* Ticker input */}
          <div>
            <label style={labelStyle}>Ticker</label>
            <input
              style={inputStyle}
              value={orderTicker}
              onChange={(e) => setOrderTicker(e.target.value)}
              placeholder="Enter ticker..."
              spellCheck={false}
            />
          </div>

          {/* Action toggle: BUY / SELL */}
          <div>
            <label style={labelStyle}>Action</label>
            <div style={{ display: "flex", gap: "2px" }}>
              <button
                style={{
                  ...toggleBtnStyle,
                  flex: 1,
                  color: orderAction === "buy" ? "#00FF88" : "#555",
                  background:
                    orderAction === "buy"
                      ? "rgba(0,255,136,0.08)"
                      : "transparent",
                  borderColor:
                    orderAction === "buy"
                      ? "rgba(0,255,136,0.3)"
                      : "#1a1a1a",
                  fontWeight: orderAction === "buy" ? 700 : 500,
                }}
                onClick={() => setOrderAction("buy")}
              >
                BUY
              </button>
              <button
                style={{
                  ...toggleBtnStyle,
                  flex: 1,
                  color: orderAction === "sell" ? "#FF3366" : "#555",
                  background:
                    orderAction === "sell"
                      ? "rgba(255,51,102,0.08)"
                      : "transparent",
                  borderColor:
                    orderAction === "sell"
                      ? "rgba(255,51,102,0.3)"
                      : "#1a1a1a",
                  fontWeight: orderAction === "sell" ? 700 : 500,
                }}
                onClick={() => setOrderAction("sell")}
              >
                SELL
              </button>
            </div>
          </div>

          {/* Side toggle: YES / NO */}
          <div>
            <label style={labelStyle}>Side</label>
            <div style={{ display: "flex", gap: "2px" }}>
              <button
                style={{
                  ...toggleBtnStyle,
                  flex: 1,
                  color: orderSide === "yes" ? "#00BCD4" : "#555",
                  background:
                    orderSide === "yes"
                      ? "rgba(0,188,212,0.08)"
                      : "transparent",
                  borderColor:
                    orderSide === "yes"
                      ? "rgba(0,188,212,0.3)"
                      : "#1a1a1a",
                  fontWeight: orderSide === "yes" ? 700 : 500,
                }}
                onClick={() => setOrderSide("yes")}
              >
                YES
              </button>
              <button
                style={{
                  ...toggleBtnStyle,
                  flex: 1,
                  color: orderSide === "no" ? "#FF9800" : "#555",
                  background:
                    orderSide === "no"
                      ? "rgba(255,152,0,0.08)"
                      : "transparent",
                  borderColor:
                    orderSide === "no"
                      ? "rgba(255,152,0,0.3)"
                      : "#1a1a1a",
                  fontWeight: orderSide === "no" ? 700 : 500,
                }}
                onClick={() => setOrderSide("no")}
              >
                NO
              </button>
            </div>
          </div>

          {/* Quick quantity preset buttons — NEW */}
          <div>
            <label style={labelStyle}>Qty</label>
            <div style={{ display: "flex", gap: "2px", flexWrap: "wrap" }}>
              {QTY_PRESETS.map((q) => {
                const isSelected = orderCount === q;
                return (
                  <button
                    key={q}
                    onClick={() => setOrderCount(q)}
                    style={{
                      flex: "1 1 auto",
                      padding: "4px 2px",
                      fontSize: "9px",
                      fontWeight: isSelected ? 700 : 400,
                      color: isSelected ? "#000" : "#555",
                      background: isSelected ? "#FF6600" : "transparent",
                      border: `1px solid ${isSelected ? "#FF6600" : "#1a1a1a"}`,
                      borderRadius: "3px",
                      cursor: "pointer",
                      fontFamily: "inherit",
                      letterSpacing: "0.04em",
                      transition: "all 0.1s",
                      fontVariantNumeric: "tabular-nums",
                      minWidth: "28px",
                    }}
                  >
                    {q}
                  </button>
                );
              })}
            </div>
            {/* Manual count input — shown when a non-preset value is needed */}
            <input
              style={{
                ...inputStyle,
                marginTop: "4px",
                fontSize: "10px",
              }}
              type="number"
              min={1}
              max={500}
              value={orderCount}
              onChange={(e) =>
                setOrderCount(Math.max(1, parseInt(e.target.value) || 1))
              }
            />
          </div>

          {/* Order type + limit price */}
          <div>
            <label style={labelStyle}>Type</label>
            <div style={{ display: "flex", gap: "2px", alignItems: "center" }}>
              <button
                style={{
                  ...toggleBtnStyle,
                  flex: 1,
                  color: orderType === "market" ? "#FF6600" : "#555",
                  background:
                    orderType === "market"
                      ? "rgba(255,102,0,0.08)"
                      : "transparent",
                  borderColor:
                    orderType === "market"
                      ? "rgba(255,102,0,0.3)"
                      : "#1a1a1a",
                  fontWeight: orderType === "market" ? 700 : 500,
                }}
                onClick={() => setOrderType("market")}
              >
                MKT
              </button>
              <button
                style={{
                  ...toggleBtnStyle,
                  flex: 1,
                  color: orderType === "limit" ? "#FF6600" : "#555",
                  background:
                    orderType === "limit"
                      ? "rgba(255,102,0,0.08)"
                      : "transparent",
                  borderColor:
                    orderType === "limit"
                      ? "rgba(255,102,0,0.3)"
                      : "#1a1a1a",
                  fontWeight: orderType === "limit" ? 700 : 500,
                }}
                onClick={() => setOrderType("limit")}
              >
                LMT
              </button>
              {orderType === "limit" && (
                <>
                  <span
                    style={{ fontSize: "8px", color: "#5a6577", flexShrink: 0, marginLeft: "4px" }}
                  >
                    Price
                  </span>
                  <input
                    style={{
                      ...inputStyle,
                      width: "52px",
                      marginLeft: "4px",
                      flex: "0 0 auto",
                    }}
                    type="number"
                    min={1}
                    max={99}
                    value={orderPrice}
                    onChange={(e) =>
                      setOrderPrice(
                        Math.max(1, Math.min(99, parseInt(e.target.value) || 50))
                      )
                    }
                  />
                </>
              )}
            </div>
          </div>

          {/* Cost estimate */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              fontSize: "9px",
              color: "#5a6577",
              padding: "4px 0",
              borderTop: "1px solid #1a1a1a",
            }}
          >
            <span>
              Est: {orderCount} ×{" "}
              {orderType === "market" ? "99" : `${orderPrice}`}¢
            </span>
            <span
              style={{
                fontVariantNumeric: "tabular-nums",
                color: "#e0e0e0",
                fontWeight: 600,
              }}
            >
              = ${estCost.toFixed(2)}
            </span>
          </div>

          {/* Submit button */}
          <button
            style={{
              padding: "8px",
              fontSize: "10px",
              fontWeight: 700,
              color: "#000",
              background: actionColor,
              border: "none",
              borderRadius: "3px",
              cursor: submitting ? "wait" : "pointer",
              fontFamily: "inherit",
              letterSpacing: "0.08em",
              opacity: submitting ? 0.5 : 1,
              transition: "opacity 0.15s",
              width: "100%",
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
                color: orderResult.startsWith("Order placed")
                  ? "#00FF88"
                  : "#FF3366",
                fontSize: "9px",
                padding: "2px 0",
                textAlign: "center",
              }}
            >
              {orderResult}
            </div>
          )}

          {/* Resting orders */}
          {orders.length > 0 && (
            <div style={{ marginTop: "2px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "4px",
                  paddingTop: "6px",
                  borderTop: "1px solid #1a1a1a",
                }}
              >
                <span style={labelStyle}>Resting Orders</span>
                <span style={{ fontSize: "8px", color: "#444" }}>
                  {orders.length}
                </span>
              </div>
              {orders.map((o) => (
                <div
                  key={o.order_id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "3px 0",
                    fontSize: "8px",
                    borderBottom: "1px solid #111",
                  }}
                >
                  <div style={{ minWidth: 0, overflow: "hidden" }}>
                    <span
                      style={{
                        color: o.action === "buy" ? "#00FF88" : "#FF3366",
                        fontWeight: 700,
                        marginRight: "3px",
                      }}
                    >
                      {o.action === "buy" ? "B" : "S"}
                    </span>
                    <span style={{ color: "#777", fontVariantNumeric: "tabular-nums" }}>
                      {o.remaining_count}/{o.count} @ {o.yes_price}c
                    </span>
                  </div>
                  <button
                    onClick={() => cancelOrderById(o.order_id)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#FF3366",
                      fontSize: "7px",
                      fontWeight: 700,
                      cursor: "pointer",
                      fontFamily: "inherit",
                      padding: "2px 4px",
                      flexShrink: 0,
                    }}
                  >
                    CANCEL
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </OEBox>

      {/* ── BOX 2: CONTEXT ─────────────────────────────────── */}
      <OEBox title="Context" icon="◎" borderColor="#333">
        {!orderTicker ? (
          <div
            style={{
              fontSize: "9px",
              color: "#333",
              textAlign: "center",
              padding: "8px 0",
            }}
          >
            No market selected
          </div>
        ) : (
          <div
            style={{ display: "flex", flexDirection: "column", gap: "4px" }}
          >
            {/* Ticker */}
            <div
              style={{
                fontSize: "10px",
                fontWeight: 700,
                color: "#e0e0e0",
                letterSpacing: "0.04em",
                wordBreak: "break-all",
              }}
            >
              {orderTicker.toUpperCase()}
            </div>

            {/* Parsed context rows */}
            {ctx.league && (
              <div style={ctxRowStyle}>
                <span style={ctxLabelStyle}>League</span>
                <span style={ctxValueStyle}>{ctx.league}</span>
              </div>
            )}
            {ctx.team && (
              <div style={ctxRowStyle}>
                <span style={ctxLabelStyle}>Team</span>
                <span style={ctxValueStyle}>{ctx.team}</span>
              </div>
            )}
            {ctx.marketType && (
              <div style={ctxRowStyle}>
                <span style={ctxLabelStyle}>Type</span>
                <span
                  style={{
                    ...ctxValueStyle,
                    color: "#00BCD4",
                    fontWeight: 600,
                  }}
                >
                  {ctx.marketType}
                </span>
              </div>
            )}
            {ctx.event && ctx.event !== orderTicker && (
              <div
                style={{
                  marginTop: "2px",
                  fontSize: "8px",
                  color: "#3a3a3a",
                  wordBreak: "break-all",
                }}
              >
                {ctx.event}
              </div>
            )}
          </div>
        )}
      </OEBox>
    </div>
  );
}

// ── Shared styles ─────────────────────────────────────────────

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: "8px",
  color: "#5a6577",
  letterSpacing: "0.08em",
  marginBottom: "3px",
  fontWeight: 600,
  textTransform: "uppercase",
};

const inputStyle: React.CSSProperties = {
  background: "#0d0d0d",
  border: "1px solid #1a1a1a",
  color: "#ccc",
  padding: "5px 8px",
  fontSize: "10px",
  borderRadius: "3px",
  outline: "none",
  fontFamily: "inherit",
  width: "100%",
  boxSizing: "border-box",
  fontVariantNumeric: "tabular-nums",
};

const toggleBtnStyle: React.CSSProperties = {
  padding: "5px 8px",
  fontSize: "9px",
  border: "1px solid #1a1a1a",
  borderRadius: "3px",
  cursor: "pointer",
  fontFamily: "inherit",
  letterSpacing: "0.06em",
  transition: "all 0.12s",
};

const ctxRowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  fontSize: "8px",
};

const ctxLabelStyle: React.CSSProperties = {
  color: "#5a6577",
};

const ctxValueStyle: React.CSSProperties = {
  color: "#e0e0e0",
  fontVariantNumeric: "tabular-nums",
};
