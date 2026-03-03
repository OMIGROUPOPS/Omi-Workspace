"use client";

// OMI Terminal — Order Book (Redesigned)
// Depth bars scale to max visible qty on each side.
// Best bid/ask pulse. Spread displays in basis points.

import type { OrderbookData } from "@/lib/terminal/types";

interface OrderbookProps {
  data?: OrderbookData;
}

// ── Depth fill helpers ────────────────────────────────────────────────────

/** Scale factor for depth bar fill (0..1) relative to max qty on that side */
function depthFill(qty: number, maxQty: number): number {
  if (maxQty <= 0) return 0;
  return Math.min(1, qty / maxQty);
}

// ── Spread badge ─────────────────────────────────────────────────────────

function SpreadBadge({ spread, mid }: { spread: number; mid: number }) {
  const bps = mid > 0 ? Math.round((spread / mid) * 10000) : 0;
  const color = spread <= 1 ? "#00FF88" : spread <= 3 ? "#FF6600" : "#FF3366";
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "6px",
      padding: "2px 0",
      fontSize: "8px",
      borderTop: "1px solid #1a1a1a",
      borderBottom: "1px solid #1a1a1a",
      background: "#0a0a0a",
      color: "#333",
    }}>
      <span>MID</span>
      <span style={{ color: "#888", fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>{mid.toFixed(1)}¢</span>
      <span style={{ color: "#222" }}>|</span>
      <span>SPR</span>
      <span style={{ color, fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>{spread.toFixed(1)}</span>
      <span style={{ color: color, fontSize: "7px" }}>{bps}bps</span>
    </div>
  );
}

// ── Row component ─────────────────────────────────────────────────────────

function OrderRow({
  price, qty, side, maxQty, isBest,
}: {
  price: number;
  qty: number;
  side: "bid" | "ask";
  maxQty: number;
  isBest: boolean;
}) {
  const fill = depthFill(qty, maxQty);
  const isBid = side === "bid";
  const barColor = isBid ? "rgba(0,255,136,0.12)" : "rgba(255,51,102,0.12)";
  const barColorBest = isBid ? "rgba(0,255,136,0.22)" : "rgba(255,51,102,0.22)";
  const priceColor = isBid ? "#00FF88" : "#FF3366";
  const priceShadow = isBid ? "0 0 6px rgba(0,255,136,0.25)" : "0 0 6px rgba(255,51,102,0.25)";

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "4px",
        padding: "1.5px 4px",
        position: "relative",
        overflow: "hidden",
        animation: isBest ? "terminal-row-glow 2s ease-in-out infinite" : undefined,
      }}
    >
      {/* Depth bar */}
      <div style={{
        position: "absolute",
        top: 0,
        bottom: 0,
        [isBid ? "right" : "left"]: 0,
        width: `${fill * 100}%`,
        background: isBest ? barColorBest : barColor,
        transition: "width 0.3s ease",
      }} />

      {/* Price */}
      <div style={{
        fontSize: "9px",
        fontVariantNumeric: "tabular-nums",
        fontWeight: isBest ? 700 : 400,
        color: isBest ? priceColor : "#666",
        textShadow: isBest ? priceShadow : undefined,
        textAlign: isBid ? "right" : "left",
        position: "relative",
        zIndex: 1,
        order: isBid ? 1 : 0,
      }}>
        {price.toFixed(0)}¢
      </div>

      {/* Qty */}
      <div style={{
        fontSize: "9px",
        fontVariantNumeric: "tabular-nums",
        color: "#444",
        textAlign: isBid ? "left" : "right",
        position: "relative",
        zIndex: 1,
        order: isBid ? 0 : 1,
      }}>
        {qty}
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────

export default function Orderbook({ data }: OrderbookProps) {
  if (!data) {
    return (
      <div style={{
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#222",
        fontSize: "9px",
      }}>
        No book data
      </div>
    );
  }

  const asks = [...data.asks].sort((a, b) => a.price - b.price);
  const bids = [...data.bids].sort((a, b) => b.price - a.price);
  const spread = asks.length && bids.length ? asks[0].price - bids[0].price : 0;
  const mid = asks.length && bids.length ? (asks[0].price + bids[0].price) / 2 : 0;

  const maxAskQty = asks.reduce((m, r) => Math.max(m, r.qty), 0);
  const maxBidQty = bids.reduce((m, r) => Math.max(m, r.qty), 0);

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* Column headers */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "4px",
        padding: "2px 4px 3px",
        borderBottom: "1px solid #1a1a1a",
      }}>
        <div style={{ fontSize: "7px", color: "#333", textAlign: "right", textTransform: "uppercase", letterSpacing: "0.08em" }}>QTY</div>
        <div style={{ fontSize: "7px", color: "#333", textAlign: "left", textTransform: "uppercase", letterSpacing: "0.08em" }}>ASK</div>
      </div>

      {/* Asks — reversed so lowest ask at bottom */}
      <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column", justifyContent: "flex-end" }}>
        {[...asks].reverse().map((level, i) => (
          <OrderRow
            key={level.price}
            price={level.price}
            qty={level.qty}
            side="ask"
            maxQty={maxAskQty}
            isBest={i === asks.length - 1}
          />
        ))}
      </div>

      {/* Spread badge */}
      <SpreadBadge spread={spread} mid={mid} />

      {/* Bids */}
      <div style={{ flex: 1, overflow: "hidden" }}>
        {bids.map((level, i) => (
          <OrderRow
            key={level.price}
            price={level.price}
            qty={level.qty}
            side="bid"
            maxQty={maxBidQty}
            isBest={i === 0}
          />
        ))}
      </div>

      {/* Column headers */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "4px",
        padding: "3px 4px 2px",
        borderTop: "1px solid #1a1a1a",
      }}>
        <div style={{ fontSize: "7px", color: "#333", textAlign: "right", textTransform: "uppercase", letterSpacing: "0.08em" }}>BID</div>
        <div style={{ fontSize: "7px", color: "#333", textAlign: "left", textTransform: "uppercase", letterSpacing: "0.08em" }}>QTY</div>
      </div>
    </div>
  );
}
