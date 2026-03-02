"use client";

// OMNI Terminal — Watchlist sidebar
// Compact ticker list: team, mid, spread, 30s move indicator.

import { useState } from "react";
import type { WatchlistItem } from "@/lib/terminal/types";

interface WatchlistProps {
  items?: WatchlistItem[];
  selectedTicker?: string;
  onSelect?: (ticker: string) => void;
}

export default function Watchlist({
  items = [],
  selectedTicker,
  onSelect,
}: WatchlistProps) {
  const [query, setQuery] = useState("");

  const filtered = query
    ? items.filter(
        (item) =>
          item.info.team.toLowerCase().includes(query.toLowerCase()) ||
          item.ticker.toLowerCase().includes(query.toLowerCase()),
      )
    : items;

  return (
    <div className="h-full flex flex-col" style={{ fontFamily: "'Courier New', monospace" }}>
      {/* Search */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
        style={{
          width: "100%",
          background: "#111",
          border: "1px solid #222",
          borderRadius: "3px",
          padding: "4px 8px",
          fontSize: "10px",
          color: "#aaa",
          outline: "none",
          marginBottom: "6px",
          fontFamily: "inherit",
          boxSizing: "border-box",
        }}
      />

      {/* Header */}
      <div
        className="flex items-center justify-between shrink-0"
        style={{
          fontSize: "8px",
          color: "#555",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          padding: "0 4px 4px",
          borderBottom: "1px solid #1a1a1a",
          marginBottom: "2px",
        }}
      >
        <span>Ticker</span>
        <span>Mid / Mv</span>
      </div>

      {/* Ticker list */}
      <div
        className="flex-1 overflow-y-auto"
        style={{ scrollbarWidth: "thin", scrollbarColor: "#333 transparent" }}
      >
        {filtered.length === 0 ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "64px",
              color: "#555",
              fontSize: "10px",
            }}
          >
            {query ? "No matches" : "Awaiting WS relay"}
          </div>
        ) : (
          filtered.map((item) => {
            const isSelected = selectedTicker === item.ticker;
            const mv = item.move_30s;
            const mvColor =
              mv !== null && mv > 0
                ? "#00FF88"
                : mv !== null && mv < 0
                  ? "#FF3366"
                  : "#555";

            return (
              <button
                key={item.ticker}
                onClick={() => onSelect?.(item.ticker)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  width: "100%",
                  padding: "4px 4px",
                  borderRadius: "2px",
                  fontSize: "10px",
                  textAlign: "left",
                  cursor: "pointer",
                  border: "none",
                  fontFamily: "inherit",
                  transition: "background 0.1s",
                  background: isSelected
                    ? "rgba(255,102,0,0.1)"
                    : "transparent",
                  color: isSelected ? "#FF6600" : "#aaa",
                  borderLeft: isSelected
                    ? "2px solid #FF6600"
                    : "2px solid transparent",
                }}
              >
                {/* Left: team + spread */}
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    minWidth: 0,
                    overflow: "hidden",
                  }}
                >
                  <span
                    style={{
                      fontWeight: 600,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {item.info.team || item.ticker.slice(-8)}
                  </span>
                  <span style={{ fontSize: "8px", color: "#444" }}>
                    {item.spread}s &middot; {item.bid_size}/{item.ask_size}
                  </span>
                </div>

                {/* Right: mid + move */}
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-end",
                    flexShrink: 0,
                    marginLeft: "4px",
                  }}
                >
                  <span
                    style={{
                      fontWeight: 600,
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {item.mid ?? "\u2014"}¢
                  </span>
                  {mv !== null && mv !== 0 && (
                    <span
                      style={{
                        fontSize: "8px",
                        color: mvColor,
                        fontWeight: 700,
                      }}
                    >
                      {mv > 0 ? "\u25B2" : "\u25BC"}
                      {Math.abs(mv)}
                    </span>
                  )}
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
