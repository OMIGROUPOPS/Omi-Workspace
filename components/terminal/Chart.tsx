"use client";

// OMNI Terminal — Chart panel
// Mock price bar chart with price axis, grid lines, and stats.

import { useMemo } from "react";

interface ChartProps {
  ticker?: string;
}

function generateChartData(ticker: string) {
  let seed = 0;
  for (let i = 0; i < ticker.length; i++) seed += ticker.charCodeAt(i);

  const base = (seed % 60) + 20;
  const prices: number[] = [];
  let p = base;
  for (let i = 0; i < 60; i++) {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    const delta = ((seed % 5) - 2) * 0.5;
    p = Math.max(1, Math.min(99, p + delta));
    prices.push(Math.round(p * 10) / 10);
  }

  return {
    prices,
    vol: ((seed * 7) % 500) + 150,
    lambda: (((seed * 3) % 200) / 10000 + 0.003),
  };
}

export default function Chart({ ticker }: ChartProps) {
  const data = useMemo(
    () => (ticker ? generateChartData(ticker) : null),
    [ticker],
  );

  if (!ticker || !data) {
    return (
      <div className="h-full flex items-center justify-center text-zinc-700 text-xs">
        Select a ticker from watchlist
      </div>
    );
  }

  const { prices, vol, lambda } = data;
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 1;
  const latest = prices[prices.length - 1];
  const first = prices[0];
  const change = latest - first;
  const changeColor = change >= 0 ? "#22c55e" : "#ef4444";

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-2 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-300 font-medium">{ticker}</span>
          <span style={{ color: changeColor, fontSize: "11px", fontWeight: 600 }}>
            {latest}¢
          </span>
          <span style={{ color: changeColor, fontSize: "10px" }}>
            {change >= 0 ? "+" : ""}
            {change.toFixed(1)}
          </span>
        </div>
        <div className="flex gap-2 text-[10px]">
          <button
            style={{
              color: "#FF6600",
              borderBottom: "1px solid #FF6600",
              paddingBottom: "1px",
              background: "none",
              border: "none",
              borderBottomStyle: "solid",
              borderBottomWidth: "1px",
              borderBottomColor: "#FF6600",
              cursor: "pointer",
              fontFamily: "inherit",
              fontSize: "inherit",
            }}
          >
            1m
          </button>
          <button
            className="text-zinc-600 hover:text-zinc-400"
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              fontFamily: "inherit",
              fontSize: "inherit",
            }}
          >
            5m
          </button>
          <button
            className="text-zinc-600 hover:text-zinc-400"
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              fontFamily: "inherit",
              fontSize: "inherit",
            }}
          >
            15m
          </button>
        </div>
      </div>

      {/* Chart area */}
      <div className="flex-1 flex min-h-0">
        <div className="flex-1 relative">
          {/* Horizontal grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => (
            <div
              key={pct}
              style={{
                position: "absolute",
                left: 0,
                right: "40px",
                bottom: `${pct * 100}%`,
                borderBottom: "1px solid #1a1a1a",
              }}
            />
          ))}

          {/* Price bars */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              right: "40px",
              display: "flex",
              alignItems: "flex-end",
              gap: "1px",
              padding: "4px 0",
            }}
          >
            {prices.map((p, i) => {
              const pct = ((p - min) / range) * 100;
              const isUp = i > 0 ? p >= prices[i - 1] : true;
              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    height: `${Math.max(3, pct)}%`,
                    background: isUp
                      ? "rgba(34,197,94,0.5)"
                      : "rgba(239,68,68,0.5)",
                    borderRadius: "1px 1px 0 0",
                    minWidth: "1px",
                    transition: "height 0.15s ease",
                  }}
                />
              );
            })}
          </div>

          {/* Current price line */}
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              bottom: `${((latest - min) / range) * 100}%`,
              borderBottom: "1px dashed rgba(255,102,0,0.5)",
              zIndex: 2,
              pointerEvents: "none",
            }}
          >
            <span
              style={{
                position: "absolute",
                right: 0,
                top: "-8px",
                background: "#FF6600",
                color: "#000",
                fontSize: "9px",
                fontWeight: 700,
                padding: "1px 4px",
                borderRadius: "2px",
                lineHeight: "14px",
              }}
            >
              {latest}
            </span>
          </div>

          {/* Y-axis labels */}
          <div
            style={{
              position: "absolute",
              right: 0,
              top: 0,
              bottom: 0,
              width: "36px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              padding: "2px 0",
            }}
          >
            <span style={{ fontSize: "8px", color: "#555", textAlign: "right" }}>
              {max.toFixed(0)}¢
            </span>
            <span style={{ fontSize: "8px", color: "#555", textAlign: "right" }}>
              {((max + min) / 2).toFixed(0)}¢
            </span>
            <span style={{ fontSize: "8px", color: "#555", textAlign: "right" }}>
              {min.toFixed(0)}¢
            </span>
          </div>
        </div>
      </div>

      {/* Bottom stats */}
      <div
        className="flex items-center gap-4 mt-1 shrink-0"
        style={{ fontSize: "9px", color: "#555" }}
      >
        <span>H: {max.toFixed(0)}¢</span>
        <span>L: {min.toFixed(0)}¢</span>
        <span>Vol: {vol.toLocaleString()}ct</span>
        <span>λ: {lambda.toFixed(4)}</span>
      </div>
    </div>
  );
}
