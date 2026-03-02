"use client";

// OMNI Terminal — Orderbook / Depth panel
// Mock bid/ask ladder with depth bars.

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

  // Asks: highest at top, best ask (lowest) at bottom
  return { bids, asks: asks.reverse() };
}

export default function Orderbook({ ticker }: OrderbookProps) {
  const book = useMemo(
    () => (ticker ? generateMockBook(ticker) : null),
    [ticker],
  );

  if (!ticker || !book) {
    return (
      <div className="h-full flex items-center justify-center text-zinc-700 text-xs">
        No book loaded
      </div>
    );
  }

  const maxSize = Math.max(
    ...book.bids.map((l) => l.size),
    ...book.asks.map((l) => l.size),
  );

  const spreadVal =
    book.asks.length > 0 && book.bids.length > 0
      ? book.asks[book.asks.length - 1].price - book.bids[0].price
      : 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-1 shrink-0">
        <span
          style={{
            fontSize: "10px",
            color: "#aaa",
            fontWeight: 600,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
          }}
        >
          Depth
        </span>
        <span style={{ fontSize: "9px", color: "#555" }}>
          {ticker.length > 20 ? ticker.slice(0, 18) + "\u2026" : ticker}
        </span>
      </div>

      {/* Column headers */}
      <div
        className="flex items-center justify-between px-1 mb-1 shrink-0"
        style={{
          fontSize: "8px",
          color: "#555",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}
      >
        <span>Size</span>
        <span>Price</span>
        <span>Size</span>
      </div>

      {/* Asks (sells) */}
      <div className="flex-1 flex flex-col justify-end overflow-hidden">
        {book.asks.map((level, i) => (
          <div
            key={`a-${i}`}
            className="flex items-center justify-between px-1 relative"
            style={{ height: "20px", fontSize: "10px" }}
          >
            <div
              style={{
                position: "absolute",
                right: 0,
                top: 0,
                bottom: 0,
                width: `${(level.size / maxSize) * 100}%`,
                background: "rgba(239,68,68,0.08)",
                borderRight: "1px solid rgba(239,68,68,0.2)",
              }}
            />
            <span style={{ color: "#555", zIndex: 1, minWidth: "32px" }}>
              {level.size}
            </span>
            <span style={{ color: "#ef4444", fontWeight: 600, zIndex: 1 }}>
              {level.price}¢
            </span>
            <span style={{ color: "transparent", minWidth: "32px" }}>—</span>
          </div>
        ))}
      </div>

      {/* Spread */}
      <div
        className="flex items-center justify-center py-1 shrink-0"
        style={{ fontSize: "9px" }}
      >
        <span style={{ color: "#FF6600", fontWeight: 700 }}>
          {spreadVal}¢ spread
        </span>
      </div>

      {/* Bids (buys) */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {book.bids.map((level, i) => (
          <div
            key={`b-${i}`}
            className="flex items-center justify-between px-1 relative"
            style={{ height: "20px", fontSize: "10px" }}
          >
            <div
              style={{
                position: "absolute",
                left: 0,
                top: 0,
                bottom: 0,
                width: `${(level.size / maxSize) * 100}%`,
                background: "rgba(34,197,94,0.08)",
                borderRight: "1px solid rgba(34,197,94,0.2)",
              }}
            />
            <span style={{ color: "transparent", minWidth: "32px" }}>—</span>
            <span style={{ color: "#22c55e", fontWeight: 600, zIndex: 1 }}>
              {level.price}¢
            </span>
            <span
              style={{
                color: "#555",
                zIndex: 1,
                minWidth: "32px",
                textAlign: "right",
              }}
            >
              {level.size}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
