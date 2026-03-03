"use client";

// OMI Terminal — Watchlist (Redesigned)
// Price flash on tick change, animated counters, multi-column layout.

import { useEffect, useRef, useState } from "react";
import type { Market } from "@/lib/terminal/types";
import { calcGreeks } from "@/lib/terminal/greeks";

interface WatchlistProps {
  markets?: Market[];
  selectedTicker?: string;
  onSelect?: (ticker: string) => void;
}

// ── Animated price ────────────────────────────────────────────────────────

function AnimatedPrice({
  price,
  prev,
  selected,
}: {
  price: number;
  prev: number;
  selected: boolean;
}) {
  const [flash, setFlash] = useState<"up" | "down" | null>(null);
  const mounted = useRef(false);

  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;
      return;
    }
    if (price !== prev) {
      setFlash(price > prev ? "up" : "down");
      const t = setTimeout(() => setFlash(null), 400);
      return () => clearTimeout(t);
    }
  }, [price, prev]);

  const color = price >= 50 ? "#00FF88" : "#FF3366";
  const glow = price >= 50 ? "rgba(0,255,136,0.25)" : "rgba(255,51,102,0.25)";

  return (
    <span
      style={{
        fontSize: "11px",
        fontWeight: 700,
        color: selected ? color : price >= 50 ? "#00AA55" : "#AA2244",
        fontVariantNumeric: "tabular-nums",
        animation: flash ? `terminal-flash-${flash === "up" ? "green" : "red"} 0.4s ease-out` : undefined,
        textShadow: selected ? `0 0 8px ${glow}` : undefined,
        display: "inline-block",
      }}
    >
      {price.toFixed(0)}¢
    </span>
  );
}

// ── Row ───────────────────────────────────────────────────────────────────

function WatchRow({
  market,
  selected,
  onSelect,
}: {
  market: Market & { prevMid?: number };
  selected: boolean;
  onSelect: () => void;
}) {
  const greeks = calcGreeks(market.mid / 100, 4, 0.5);

  // Severity based on spread and volume proxy (spread < 2 = tight, > 5 = wide)
  const severity =
    market.spread < 2 ? "tight" :
    market.spread < 5 ? "normal" : "wide";
  const spreadColor =
    severity === "tight" ? "#00FF88" :
    severity === "normal" ? "#FF6600" : "#FF3366";

  return (
    <div
      onClick={onSelect}
      style={{
        display: "grid",
        gridTemplateColumns: "1fr auto",
        gap: "4px",
        padding: "4px 4px",
        cursor: "pointer",
        borderBottom: "1px solid #0f0f0f",
        background: selected ? "rgba(255,102,0,0.06)" : "transparent",
        borderLeft: selected ? "2px solid #FF6600" : "2px solid transparent",
        transition: "background 0.1s",
      }}
      onMouseEnter={(e) => {
        if (!selected) (e.currentTarget as HTMLDivElement).style.background = "rgba(255,255,255,0.02)";
      }}
      onMouseLeave={(e) => {
        if (!selected) (e.currentTarget as HTMLDivElement).style.background = "transparent";
      }}
    >
      {/* Left */}
      <div style={{ minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "4px", marginBottom: "2px" }}>
          <span style={{
            color: selected ? "#eee" : "#888",
            fontSize: "9px",
            fontWeight: selected ? 700 : 400,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}>
            {market.team}
          </span>
          <span style={{
            fontSize: "6px",
            color: "#222",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            whiteSpace: "nowrap",
          }}>
            {market.category}
          </span>
        </div>
        {/* Greeks strip */}
        <div style={{ display: "flex", gap: "6px", fontSize: "7px" }}>
          <span style={{ color: "#222" }}>Δ<span style={{ color: selected ? "#00BCD4" : "#2a2a2a" }}>{greeks.delta.toFixed(2)}</span></span>
          <span style={{ color: spreadColor, fontSize: "7px" }}>sprd:{market.spread.toFixed(1)}</span>
        </div>
      </div>

      {/* Right */}
      <AnimatedPrice
        price={market.mid}
        prev={market.prevMid ?? market.mid}
        selected={selected}
      />
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────

export default function Watchlist({ markets = [], selectedTicker, onSelect }: WatchlistProps) {
  const [prevPrices, setPrevPrices] = useState<Record<string, number>>({});

  // Track previous prices for flash animation
  useEffect(() => {
    setPrevPrices((prev) => {
      const next = { ...prev };
      for (const m of markets) {
        if (!(m.ticker in next)) next[m.ticker] = m.mid;
      }
      return next;
    });
  }, [markets]);

  if (markets.length === 0) {
    return (
      <div style={{
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#222",
        fontSize: "9px",
      }}>
        No markets
      </div>
    );
  }

  return (
    <div style={{ height: "100%", overflowY: "auto" }}>
      {markets.map((market) => (
        <WatchRow
          key={market.ticker}
          market={{ ...market, prevMid: prevPrices[market.ticker] }}
          selected={market.ticker === selectedTicker}
          onSelect={() => onSelect?.(market.ticker)}
        />
      ))}
    </div>
  );
}
