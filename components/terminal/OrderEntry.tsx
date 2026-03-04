"use client";

// OMI Terminal — Order Entry sidebar (Visual Overhaul v3)
// Slim 260px right sidebar. Extracted from KalshiPanel.
// ALL data fetching logic preserved from KalshiPanel — only UI restructured.
// DO NOT change API routes or data fetching logic.

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

// ── Component ───────────────────────────────────────────────

interface OrderEntryProps {
  onBalanceUpdate?: (balance: number) => void;
  selectedTicker?: string;
}

export default function OrderEntry({ onBalanceUpdate, selectedTicker }: OrderEntryProps) {
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
      await fetch(`/api/kalshi/orders?order_id=${orderId}`, { method: "DELETE" });
      fetchAll();
    } catch {
      // silent
    }
  };

  // ── Render ────────────────────────────────────────────────

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <span style={styles.title}>ORDER ENTRY</span>
          <span style={{ color: "#FFD600", fontSize: "8px" }}>CONNECTING</span>
        </div>
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ color: "#333", fontSize: "9px" }}>Authenticating...</span>
        </div>
      </div>
    );
  }

  if (error && !balance) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <span style={styles.title}>ORDER ENTRY</span>
          <span style={{ color: "#FF3366", fontSize: "8px" }}>ERROR</span>
        </div>
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "0 8px" }}>
          <span style={{ color: "#FF3366", fontSize: "9px", textAlign: "center" }}>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header + Balance */}
      <div style={styles.header}>
        <span style={styles.title}>ORDER ENTRY</span>
        {balance && (
          <span style={{ color: "#00FF88", fontWeight: 700, fontVariantNumeric: "tabular-nums", fontSize: "10px" }}>
            ${(balance.balance / 100).toFixed(2)}
          </span>
        )}
      </div>

      {/* Portfolio value */}
      {balance && (
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          padding: "0 8px 6px",
          fontSize: "8px",
          color: "#555",
          borderBottom: "1px solid #1a1a1a",
        }}>
          <span>Portfolio</span>
          <span style={{ fontVariantNumeric: "tabular-nums", color: "#777" }}>
            ${(balance.portfolio_value / 100).toFixed(2)}
          </span>
        </div>
      )}

      {/* Order form */}
      <div style={{ flex: 1, overflow: "auto", padding: "8px", display: "flex", flexDirection: "column", gap: "8px" }}>
        {/* Ticker */}
        <div>
          <label style={styles.label}>TICKER</label>
          <input
            style={styles.input}
            value={orderTicker}
            onChange={(e) => setOrderTicker(e.target.value)}
            placeholder="Enter ticker..."
            spellCheck={false}
          />
        </div>

        {/* Action: Buy / Sell */}
        <div>
          <label style={styles.label}>ACTION</label>
          <div style={{ display: "flex", gap: "2px" }}>
            <button
              style={{
                ...styles.toggleBtn,
                flex: 1,
                color: orderAction === "buy" ? "#00FF88" : "#555",
                background: orderAction === "buy" ? "rgba(0,255,136,0.08)" : "transparent",
                borderColor: orderAction === "buy" ? "rgba(0,255,136,0.3)" : "#1a1a1a",
                fontWeight: orderAction === "buy" ? 700 : 500,
              }}
              onClick={() => setOrderAction("buy")}
            >
              BUY
            </button>
            <button
              style={{
                ...styles.toggleBtn,
                flex: 1,
                color: orderAction === "sell" ? "#FF3366" : "#555",
                background: orderAction === "sell" ? "rgba(255,51,102,0.08)" : "transparent",
                borderColor: orderAction === "sell" ? "rgba(255,51,102,0.3)" : "#1a1a1a",
                fontWeight: orderAction === "sell" ? 700 : 500,
              }}
              onClick={() => setOrderAction("sell")}
            >
              SELL
            </button>
          </div>
        </div>

        {/* Side: Yes / No */}
        <div>
          <label style={styles.label}>SIDE</label>
          <div style={{ display: "flex", gap: "2px" }}>
            <button
              style={{
                ...styles.toggleBtn,
                flex: 1,
                color: orderSide === "yes" ? "#00BCD4" : "#555",
                background: orderSide === "yes" ? "rgba(0,188,212,0.08)" : "transparent",
                borderColor: orderSide === "yes" ? "rgba(0,188,212,0.3)" : "#1a1a1a",
                fontWeight: orderSide === "yes" ? 700 : 500,
              }}
              onClick={() => setOrderSide("yes")}
            >
              YES
            </button>
            <button
              style={{
                ...styles.toggleBtn,
                flex: 1,
                color: orderSide === "no" ? "#FF9800" : "#555",
                background: orderSide === "no" ? "rgba(255,152,0,0.08)" : "transparent",
                borderColor: orderSide === "no" ? "rgba(255,152,0,0.3)" : "#1a1a1a",
                fontWeight: orderSide === "no" ? 700 : 500,
              }}
              onClick={() => setOrderSide("no")}
            >
              NO
            </button>
          </div>
        </div>

        {/* Type: Market / Limit */}
        <div>
          <label style={styles.label}>TYPE</label>
          <div style={{ display: "flex", gap: "2px" }}>
            <button
              style={{
                ...styles.toggleBtn,
                flex: 1,
                color: orderType === "market" ? "#FF6600" : "#555",
                background: orderType === "market" ? "rgba(255,102,0,0.08)" : "transparent",
                borderColor: orderType === "market" ? "rgba(255,102,0,0.3)" : "#1a1a1a",
                fontWeight: orderType === "market" ? 700 : 500,
              }}
              onClick={() => setOrderType("market")}
            >
              MKT
            </button>
            <button
              style={{
                ...styles.toggleBtn,
                flex: 1,
                color: orderType === "limit" ? "#FF6600" : "#555",
                background: orderType === "limit" ? "rgba(255,102,0,0.08)" : "transparent",
                borderColor: orderType === "limit" ? "rgba(255,102,0,0.3)" : "#1a1a1a",
                fontWeight: orderType === "limit" ? 700 : 500,
              }}
              onClick={() => setOrderType("limit")}
            >
              LMT
            </button>
          </div>
        </div>

        {/* Contracts */}
        <div>
          <label style={styles.label}>CONTRACTS</label>
          <input
            style={styles.input}
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
            <label style={styles.label}>PRICE (cents)</label>
            <input
              style={styles.input}
              type="number"
              min={1}
              max={99}
              value={orderPrice}
              onChange={(e) => setOrderPrice(Math.max(1, Math.min(99, parseInt(e.target.value) || 50)))}
            />
          </div>
        )}

        {/* Cost preview */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: "9px",
          color: "#555",
          padding: "2px 0",
          borderTop: "1px solid #1a1a1a",
          paddingTop: "6px",
        }}>
          <span>Est. cost</span>
          <span style={{ fontVariantNumeric: "tabular-nums", color: "#888" }}>
            ${orderType === "market"
              ? ((orderCount * 99) / 100).toFixed(2)
              : ((orderCount * orderPrice) / 100).toFixed(2)}
          </span>
        </div>

        {/* Submit */}
        <button
          style={{
            padding: "8px",
            fontSize: "10px",
            fontWeight: 700,
            color: "#000",
            background: orderAction === "buy" ? "#00FF88" : "#FF3366",
            border: "none",
            borderRadius: "3px",
            cursor: submitting ? "wait" : "pointer",
            fontFamily: "inherit",
            letterSpacing: "0.08em",
            opacity: submitting ? 0.5 : 1,
            transition: "opacity 0.15s",
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
              color: orderResult.startsWith("Order placed") ? "#00FF88" : "#FF3366",
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
          <div style={{ marginTop: "4px" }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "4px",
              paddingTop: "6px",
              borderTop: "1px solid #1a1a1a",
            }}>
              <span style={styles.label}>RESTING ORDERS</span>
              <span style={{ fontSize: "8px", color: "#444" }}>{orders.length}</span>
            </div>
            {orders.map((o) => (
              <div key={o.order_id} style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "3px 0",
                fontSize: "8px",
                borderBottom: "1px solid #111",
              }}>
                <div style={{ minWidth: 0, overflow: "hidden" }}>
                  <span style={{
                    color: o.action === "buy" ? "#00FF88" : "#FF3366",
                    fontWeight: 700,
                    marginRight: "3px",
                  }}>
                    {o.action === "buy" ? "B" : "S"}
                  </span>
                  <span style={{ color: "#777" }}>
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
    </div>
  );
}

// ── Styles ──────────────────────────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100%",
    overflow: "hidden",
    fontSize: "10px",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "6px 8px",
    borderBottom: "1px solid #1a1a1a",
    flexShrink: 0,
  },
  title: {
    color: "#FF6600",
    fontWeight: 800,
    fontSize: "9px",
    letterSpacing: "0.12em",
  },
  label: {
    display: "block",
    fontSize: "8px",
    color: "#555",
    letterSpacing: "0.08em",
    marginBottom: "3px",
    fontWeight: 600,
    textTransform: "uppercase" as const,
  },
  input: {
    background: "#0d0d0d",
    border: "1px solid #1a1a1a",
    color: "#ccc",
    padding: "5px 8px",
    fontSize: "10px",
    borderRadius: "3px",
    outline: "none",
    fontFamily: "inherit",
    width: "100%",
    boxSizing: "border-box" as const,
  },
  toggleBtn: {
    padding: "5px 8px",
    fontSize: "9px",
    border: "1px solid #1a1a1a",
    borderRadius: "3px",
    cursor: "pointer",
    fontFamily: "inherit",
    letterSpacing: "0.06em",
    transition: "all 0.12s",
  },
};
