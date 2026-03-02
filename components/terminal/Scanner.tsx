"use client";

// OMNI Terminal — Scanner / Signal feed
// Real-time signal feed with strategy/category filters.
// TODO: Full implementation with filter chips, severity badges, auto-scroll.

import type { ScanSignal, ScanType } from "@/lib/terminal/types";

interface ScannerProps {
  signals?: ScanSignal[];
  filter?: ScanType | null;
  onFilterChange?: (f: ScanType | null) => void;
}

const SCAN_COLORS: Record<string, string> = {
  momentum_lag: "text-cyan-400",
  resolution: "text-emerald-400",
  contradiction_mono: "text-amber-400",
  contradiction_cross: "text-amber-400",
  whale_momentum: "text-purple-400",
};

export default function Scanner({ signals = [], filter, onFilterChange }: ScannerProps) {
  const filtered = filter ? signals.filter((s) => s.scan_type === filter) : signals;

  return (
    <div className="h-full flex flex-col">
      {/* Filter bar */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <button
          onClick={() => onFilterChange?.(null)}
          className={`text-[10px] px-2 py-0.5 rounded ${!filter ? "bg-[#FF6600] text-black" : "text-zinc-500 hover:text-zinc-300"}`}
        >
          ALL
        </button>
        {(["momentum_lag", "resolution", "contradiction_mono", "whale_momentum"] as ScanType[]).map((t) => (
          <button
            key={t}
            onClick={() => onFilterChange?.(t)}
            className={`text-[10px] px-2 py-0.5 rounded ${filter === t ? "bg-zinc-700 text-white" : "text-zinc-600 hover:text-zinc-400"}`}
          >
            {t.replace("_", " ").toUpperCase()}
          </button>
        ))}
      </div>

      {/* Signal list */}
      <div className="flex-1 overflow-y-auto space-y-1 scrollbar-thin">
        {filtered.length === 0 ? (
          <div className="flex items-center justify-center h-full text-zinc-700 text-xs">
            0 signals
          </div>
        ) : (
          filtered.map((sig, i) => (
            <div
              key={`${sig.ticker}-${i}`}
              className="flex items-center gap-2 px-2 py-1 rounded bg-[#111] hover:bg-[#1a1a1a] cursor-pointer"
            >
              <span className={`text-[10px] font-bold ${SCAN_COLORS[sig.scan_type] || "text-zinc-400"}`}>
                {sig.severity}
              </span>
              <span className="text-[10px] text-zinc-400 truncate flex-1">{sig.description}</span>
              <span className="text-[10px] text-zinc-600">{sig.depth}ct</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
