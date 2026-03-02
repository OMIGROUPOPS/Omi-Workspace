"use client";

// OMNI Terminal — Watchlist sidebar
// Ticker list with live mid-price, spread, depth, and move indicators.
// TODO: Full implementation with category grouping, search, and sorting.

import type { WatchlistItem } from "@/lib/terminal/types";

interface WatchlistProps {
  items?: WatchlistItem[];
  selectedTicker?: string;
  onSelect?: (ticker: string) => void;
}

export default function Watchlist({ items = [], selectedTicker, onSelect }: WatchlistProps) {
  return (
    <div className="h-full flex flex-col">
      {/* Search */}
      <input
        type="text"
        placeholder="Search tickers..."
        className="w-full bg-[#111] border border-[#222] rounded px-2 py-1 text-xs text-zinc-300 placeholder-zinc-700 outline-none focus:border-[#FF6600]/50 mb-2"
      />

      {/* Ticker list */}
      <div className="flex-1 overflow-y-auto space-y-px scrollbar-thin">
        {items.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-zinc-700 text-xs">
            Awaiting WS relay
          </div>
        ) : (
          items.map((item) => (
            <button
              key={item.ticker}
              onClick={() => onSelect?.(item.ticker)}
              className={`w-full text-left px-2 py-1.5 rounded text-[10px] flex items-center justify-between transition-colors ${
                selectedTicker === item.ticker
                  ? "bg-[#FF6600]/10 text-[#FF6600]"
                  : "text-zinc-400 hover:bg-[#151515] hover:text-zinc-200"
              }`}
            >
              <span className="truncate font-medium">{item.info.team || item.ticker.slice(-8)}</span>
              <span className="tabular-nums">{item.mid ?? "—"}¢</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
