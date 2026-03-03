"use client";

// OMI Terminal — Orderbook / Depth panel (Redesigned v2)
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
        color: "#444",
        fontSize: "10px",
        gap: "10px",
      }}>
        <div style={{
          width: "36px",
          height: "36px",
          borderRadius: "50%",
          border: "2px solid #1a1a1a",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          <span style={{ fontSize: "16px", color: "#222" }}>{"\u25A4"}</span>
        </div>
        <span>No book loaded</span>
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
      <div className="flex items-center justify-between shrink-0" style={{ marginBottom: "4px" }}>
        <span style={{ fontSize: "9px", color: "#666", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
          Depth
        </span>
        <span style={{ fontSize: "8px", color: "#444" }}>
          {ticker.length > 14 ? ticker.slice(0, 12) + "\u2026" : ticker}
        </span>
      </div>

      {/* Column headers */}
      <div
        className="flex items-center justify-between px-1 shrink-0"
        style={{
          fontSize: "8px",
          color: "#555",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginBottom: "3px",
          padding: "3px 4px",
          background: "rgba(255,255,255,0.015)",
          borderRadius: "3px",
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
          fontSize: "9px",
          padding: "4px 4px",
          borderBottom: "1px solid #1a1a1a",
          marginBottom: "3px",
          background: "rgba(255,255,255,0.02)",
          borderRadius: "3px 3px 0 0",
        }}
      >
        <span style={{ color: "#00FF88", fontVariantNumeric: "tabular-nums", fontWeight: 700 }}>
          {"\u03A3"} {totalBidDepth.toLocaleString()}
        </span>
        <span style={{ color: "#555", fontSize: "8px", letterSpacing: "0.05em", fontWeight: 600 }}>TOTAL</span>
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
                height: "22px",
                fontSize: "10px",
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
                  background: isBest ? "rgba(255,51,102,0.2)" : "rgba(255,51,102,0.08)",
                  transition: "width 0.3s ease-out",
                }}
              />
              <span style={{
                color: "#777",
                zIndex: 1,
                minWidth: "36px",
                fontVariantNumeric: "tabular-nums",
                fontSize: "9px",
              }}>
                {level.size}
              </span>
              <span style={{
                color: isBest ? "#FF3366" : "#994455",
                fontWeight: isBest ? 700 : 400,
                zIndex: 1,
                fontVariantNumeric: "tabular-nums",
                fontSize: isBest ? "11px" : "10px",
                textShadow: isBest ? "0 0 10px rgba(255,51,102,0.3)" : "none",
              }}>
                {level.price}&cent;
              </span>
              <span style={{ minWidth: "36px", color: "transparent", fontSize: "9px" }}>&mdash;</span>
            </div>
          );
        })}
      </div>

      {/* Spread + Mid — prominent */}
      <div
        className="flex items-center justify-center shrink-0"
        style={{
          padding: "6px 0",
          borderTop: "1px solid #222",
          borderBottom: "1px solid #222",
          background: "rgba(255,102,0,0.06)",
          position: "relative",
        }}
      >
        {/* Glow effect */}
        <div style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at center, rgba(255,102,0,0.08) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <span style={{
          fontSize: "18px",
          color: "#FF6600",
          fontWeight: 700,
          fontVariantNumeric: "tabular-nums",
          zIndex: 1,
          textShadow: "0 0 14px rgba(255,102,0,0.4)",
        }}>
          {midPrice}&cent;
        </span>
        <span style={{ fontSize: "9px", color: "#666", marginLeft: "8px", zIndex: 1 }}>
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
                height: "22px",
                fontSize: "10px",
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
                  background: isBest ? "rgba(0,255,136,0.2)" : "rgba(0,255,136,0.08)",
                  transition: "width 0.3s ease-out",
                }}
              />
              <span style={{ minWidth: "36px", color: "transparent", fontSize: "9px" }}>&mdash;</span>
              <span style={{
                color: isBest ? "#00FF88" : "#338855",
                fontWeight: isBest ? 700 : 400,
                zIndex: 1,
                fontVariantNumeric: "tabular-nums",
                fontSize: isBest ? "11px" : "10px",
                textShadow: isBest ? "0 0 10px rgba(0,255,136,0.3)" : "none",
              }}>
                {level.price}&cent;
              </span>
              <span style={{
                color: "#777",
                zIndex: 1,
                minWidth: "36px",
                textAlign: "right",
                fontVariantNumeric: "tabular-nums",
                fontSize: "9px",
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
