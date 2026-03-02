"use client";

// OMNI Terminal — Correlation / Multi-market view
// Shows related markets for the same game with lag detection.
// TODO: Full implementation with real-time spread comparison matrix.

import type { CorrelationPair } from "@/lib/terminal/types";

interface CorrelationProps {
  pairs?: CorrelationPair[];
  gameId?: string;
}

export default function Correlation({ pairs = [], gameId }: CorrelationProps) {
  if (!gameId) {
    return (
      <div className="h-full flex items-center justify-center text-zinc-700 text-xs">
        Select a game to view correlations
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-zinc-300 font-medium">CORRELATION</span>
        <span className="text-[10px] text-zinc-600">{gameId}</span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-1">
        {pairs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-zinc-700 text-xs">
            No correlation data
          </div>
        ) : (
          pairs.map((p, i) => (
            <div
              key={i}
              className={`flex items-center justify-between px-2 py-1 rounded text-[10px] ${
                p.lag_detected ? "bg-cyan-900/20 text-cyan-400" : "bg-[#111] text-zinc-400"
              }`}
            >
              <span>{p.primary_type} → {p.other_type}</span>
              <span className="tabular-nums">
                {p.primary_mid}¢ / {p.other_mid}¢
              </span>
              <span className={p.lag_detected ? "text-cyan-400 font-bold" : "text-zinc-600"}>
                {p.lag_detected ? "LAG" : "OK"}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
