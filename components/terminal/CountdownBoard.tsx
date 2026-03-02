"use client";

// OMNI Terminal — Countdown Board
// Markets sorted by time to settlement, filtered to >95¢ or <5¢,
// showing bridge confidence and depth.
// TODO: Full implementation with live countdown timers and Kelly sizing.

import type { CountdownItem } from "@/lib/terminal/types";

interface CountdownBoardProps {
  items?: CountdownItem[];
  onSelect?: (ticker: string) => void;
}

function formatTime(secs: number): string {
  if (secs <= 0) return "0:00";
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function CountdownBoard({ items = [], onSelect }: CountdownBoardProps) {
  const sorted = [...items].sort((a, b) => a.secs_to_close - b.secs_to_close);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-2 text-[10px] text-zinc-600 uppercase tracking-wider px-1">
        <span>Ticker</span>
        <div className="flex gap-4">
          <span>Bridge</span>
          <span>Depth</span>
          <span className="w-12 text-right">Time</span>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto space-y-px scrollbar-thin">
        {sorted.length === 0 ? (
          <div className="flex items-center justify-center h-full text-zinc-700 text-xs">
            No markets near settlement
          </div>
        ) : (
          sorted.map((item) => {
            const urgent = item.secs_to_close < 60;
            const confColor = item.bridge_confidence >= 0.98
              ? "text-emerald-400"
              : item.bridge_confidence >= 0.95
              ? "text-amber-400"
              : "text-zinc-500";

            return (
              <button
                key={item.ticker}
                onClick={() => onSelect?.(item.ticker)}
                className={`w-full text-left flex items-center justify-between px-2 py-1 rounded text-[10px] transition-colors ${
                  urgent
                    ? "bg-red-900/10 hover:bg-red-900/20 text-red-300"
                    : "bg-[#111] hover:bg-[#1a1a1a] text-zinc-400"
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <span className={item.side === "near_100" ? "text-emerald-500" : "text-red-400"}>
                    {item.side === "near_100" ? "▲" : "▼"}
                  </span>
                  <span className="truncate font-medium">{item.info.team}</span>
                  <span className="text-zinc-600">{item.price}¢</span>
                </div>
                <div className="flex items-center gap-4 shrink-0">
                  <span className={`tabular-nums ${confColor}`}>{(item.bridge_confidence * 100).toFixed(0)}%</span>
                  <span className="text-zinc-600 tabular-nums">{item.depth}</span>
                  <span className={`w-12 text-right tabular-nums font-medium ${urgent ? "text-red-400" : "text-zinc-300"}`}>
                    {formatTime(item.secs_to_close)}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
