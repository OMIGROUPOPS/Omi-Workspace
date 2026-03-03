"use client";

// OMI Terminal — Orderbook / Depth panel (Redesigned)
// Full-row depth fills, total depth display, prominent center row.

import { useMemo } from "react";

interface OrderbookProps {
  ticker?: string;
}

interface Level {
  price: number;
  size: number;
}

function generateMockBook(ticker: string): { bids: Level[]; asks: Level[] } {
  let seed = 0;
  for (let i = 0; i < ticker.length; i++) seed += ticker.charCodeAt(i);
  const mid = (seed % 60) + 20;
  const bids: Level[] = [];
  const asks: Level[] = [];
  for (let i = 0; i < 8; i++) {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    bids.push({ price: mid - 1 - i, size: (seed % 300) + 20 });
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    asks.push({ price: mid + 1 + i, size: (seed % 300) + 20 });
  }
  return { bids, asks: asks.reverse() };
}

export default function Orderbook({ ticker }: OrderbookProps) {
  const book = useMemo(() => (ticker ? generateMockBook(ticker) : null), [ticker]);

  if (!ticker || !book) {
    return (
      <div style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        color: "#333",
        fontSize: "9px",
        gap: "6px",
      }}>
        <span style={{ fontSize: "16px", opacity: 0.2 }}>{"\u25A4"}</span>
        No book loaded
      </div>
    );
  }

  const maxSize = Math.max(...book.bids.map((l) => l.size), ...book.asks.map((l) => l.size));
  const bestAsk = book.asks.length > 0 ? book.asks[book.asks.length - 1].price : 0;
  const bestBid = book.bids.length > 0 ? book.bids[0].price : 0;
  const spreadVal = bestAsk - bestBid;
  const midPrice = ((bestAsk + bestBid) / 2).toFixed(1);

  // Total depth
  const totalBidDepth = book.bids.reduce((s, l) => s + l.size, 0);
  const totalAskDepth = book.asks.reduce((s, l) => s + l.size, 0);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0" style={{ marginBottom: "3px" }}>
        <span style={{ fontSize: "8px", color: "#666", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
          Depth
        </span>
        <span style={{ fontSize: "7px", color: "#333" }}>
          {ticker.length > 16 ? ticker.slice(0, 14) + "\u2026" : ticker}
        </span>
      </div>

      {/* Column headers */}
      <div
        className="flex items-center justify-between px-1 shrink-0"
        style={{
          fontSize: "7px",
          color: "#444",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginBottom: "2px",
          padding: "2px 4px",
          background: "rgba(255,255,255,0.01)",
          borderRadius: "2px",
        }}
      >
        <span>Size</span>
        <span>Price</span>
        <span>Size</span>
      </div>

      {/* Total depth row */}
      <div
        className="flex items-center justify-between shrink-0"
        style={{
          fontSize: "8px",
          padding: "3px 4px",
          borderBottom: "1px solid #1a1a1a",
          marginBottom: "2px",
          background: "rgba(255,255,255,0.015)",
        }}
      >
        <span style={{ color: "#00FF88", fontVariantNumeric: "tabular-nums", fontWeight: 700 }}>
          {"\u03A3"} {totalBidDepth.toLocaleString()}
        </span>
        <span style={{ color: "#555", fontSize: "7px", letterSpacing: "0.05em", fontWeight: 600 }}>TOTAL</span>
        <span style={{ color: "#FF3366", fontVariantNumeric: "tabular-nums", fontWeight: 700 }}>
          {totalAskDepth.toLocaleString()} {"\u03A3"}
        </span>
      </div>

      {/* Asks (sells) — highest at top, best ask at bottom */}
      <div className="flex-1 flex flex-col justify-end overflow-hidden">
        {book.asks.map((level, i) => {
          const pct = (level.size / maxSize) * 100;
          const isBest = i === book.asks.length - 1;
          const fillOpacity = 0.03 + (level.size / maxSize) * 0.15;
          return (
            <div
              key={`a-${i}`}
              className="flex items-center justify-between relative"
              style={{
                height: "20px",
                fontSize: "9px",
                padding: "0 4px",
                background: `rgba(255,51,102,${fillOpacity})`,
                borderBottom: isBest ? "none" : "1px solid rgba(255,51,102,0.05)",
              }}
            >
              {/* Depth bar — from right */}
              <div
                style={{
                  position: "absolute", right: 0, top: 0, bottom: 0,
                  width: `${pct}%`,
                  background: isBest ? "rgba(255,51,102,0.18)" : "rgba(255,51,102,0.08)",
                  transition: "width 0.3s ease-out",
                }}
              />
              <span style={{
                color: "#666",
                zIndex: 1,
                minWidth: "32px",
                fontVariantNumeric: "tabular-nums",
                fontSize: "8px",
              }}>
                {level.size}
              </span>
              <span style={{
                color: isBest ? "#FF3366" : "#994455",
                fontWeight: isBest ? 700 : 400,
                zIndex: 1,
                fontVariantNumeric: "tabular-nums",
                fontSize: isBest ? "10px" : "9px",
                textShadow: isBest ? "0 0 8px rgba(255,51,102,0.3)" : "none",
              }}>
                {level.price}&cent;
              </span>
              <span style={{ minWidth: "32px", color: "transparent", fontSize: "8px" }}>&mdash;</span>
            </div>
          );
        })}
      </div>

      {/* Spread + Mid — prominent */}
      <div
        className="flex items-center justify-center shrink-0"
        style={{
          padding: "5px 0",
          borderTop: "1px solid #222",
          borderBottom: "1px solid #222",
          background: "rgba(255,102,0,0.05)",
          position: "relative",
        }}
      >
        {/* Glow effect */}
        <div style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at center, rgba(255,102,0,0.06) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <span style={{
          fontSize: "16px",
          color: "#FF6600",
          fontWeight: 700,
          fontVariantNumeric: "tabular-nums",
          zIndex: 1,
          textShadow: "0 0 12px rgba(255,102,0,0.3)",
        }}>
          {midPrice}&cent;
        </span>
        <span style={{ fontSize: "8px", color: "#555", marginLeft: "8px", zIndex: 1 }}>
          {spreadVal}&cent; spread
        </span>
      </div>

      {/* Bids (buys) — best bid at top */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {book.bids.map((level, i) => {
          const pct = (level.size / maxSize) * 100;
          const isBest = i === 0;
          const fillOpacity = 0.03 + (level.size / maxSize) * 0.15;
          return (
            <div
              key={`b-${i}`}
              className="flex items-center justify-between relative"
              style={{
                height: "20px",
                fontSize: "9px",
                padding: "0 4px",
                background: `rgba(0,255,136,${fillOpacity})`,
                borderBottom: "1px solid rgba(0,255,136,0.05)",
              }}
            >
              {/* Depth bar — from left */}
              <div
                style={{
                  position: "absolute", left: 0, top: 0, bottom: 0,
                  width: `${pct}%`,
                  background: isBest ? "rgba(0,255,136,0.18)" : "rgba(0,255,136,0.08)",
                  transition: "width 0.3s ease-out",
                }}
              />
              <span style={{ minWidth: "32px", color: "transparent", fontSize: "8px" }}>&mdash;</span>
              <span style={{
                color: isBest ? "#00FF88" : "#338855",
                fontWeight: isBest ? 700 : 400,
                zIndex: 1,
                fontVariantNumeric: "tabular-nums",
                fontSize: isBest ? "10px" : "9px",
                textShadow: isBest ? "0 0 8px rgba(0,255,136,0.3)" : "none",
              }}>
                {level.price}&cent;
              </span>
              <span style={{
                color: "#666",
                zIndex: 1,
                minWidth: "32px",
                textAlign: "right",
                fontVariantNumeric: "tabular-nums",
                fontSize: "8px",
              }}>
                {level.size}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
