"use client";

import React from "react";
import type { GameLiquidity } from "../types";
import { timeAgo } from "../helpers";

interface Props {
  games: GameLiquidity[];
  filter: string;
  setFilter: (v: string) => void;
}

export function DepthSummaryTable({ games, filter, setFilter }: Props) {
  const filtered = filter.trim()
    ? games.filter((g) => g.game_id.toUpperCase().includes(filter.trim().toUpperCase()))
    : games;

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] overflow-hidden">
      <div className="px-3 py-2 border-b border-gray-800 flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          Per-Game Depth ({filtered.length})
        </h3>
        <input
          type="text"
          placeholder="Filter games..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-2 py-0.5 text-xs text-gray-300 w-40 focus:outline-none focus:border-gray-600"
        />
      </div>
      <div className="overflow-auto" style={{ maxHeight: "400px" }}>
        <table className="w-full text-xs">
          <thead className="sticky top-0 bg-[#111] z-10">
            <tr className="border-b border-gray-800 text-gray-500">
              <th className="px-2 py-1.5 text-left font-medium">GAME</th>
              <th className="px-2 py-1.5 text-left font-medium">PLATFORM</th>
              <th className="px-2 py-1.5 text-right font-medium">AVG BID</th>
              <th className="px-2 py-1.5 text-right font-medium">AVG ASK</th>
              <th className="px-2 py-1.5 text-right font-medium">AVG SPREAD</th>
              <th className="px-2 py-1.5 text-right font-medium">MIN</th>
              <th className="px-2 py-1.5 text-right font-medium">MAX</th>
              <th className="px-2 py-1.5 text-right font-medium">SNAPS</th>
              <th className="px-2 py-1.5 text-right font-medium">LAST</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((g, i) => (
              <tr key={`${g.game_id}-${g.platform}-${i}`} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                <td className="px-2 py-1.5 font-mono text-gray-300 text-[10px] truncate max-w-[120px]" title={g.game_id}>
                  {g.game_id}
                </td>
                <td className="px-2 py-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${
                    g.platform === "kalshi" ? "bg-orange-500/20 text-orange-400" : "bg-blue-500/20 text-blue-400"
                  }`}>
                    {g.platform === "kalshi" ? "K" : "PM"}
                  </span>
                </td>
                <td className="px-2 py-1.5 text-right font-mono text-gray-400">{g.avg_bid_depth}</td>
                <td className="px-2 py-1.5 text-right font-mono text-gray-400">{g.avg_ask_depth}</td>
                <td className="px-2 py-1.5 text-right font-mono text-gray-400">{g.avg_spread}</td>
                <td className="px-2 py-1.5 text-right font-mono text-emerald-400">{g.min_spread}</td>
                <td className="px-2 py-1.5 text-right font-mono text-red-400">{g.max_spread}</td>
                <td className="px-2 py-1.5 text-right font-mono text-gray-500">{g.snapshots}</td>
                <td className="px-2 py-1.5 text-right text-gray-500 text-[10px]">{timeAgo(g.last_snapshot)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
