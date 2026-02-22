"use client";

import React from "react";
import type { SpreadRow, MappedGame } from "../types";
import { SpreadCell } from "../shared/SpreadCell";
import { sportBadge, timeAgo } from "../helpers";

interface Props {
  spreads: SpreadRow[];
  mappedGames: MappedGame[];
}

export function SpreadHeatmapTable({ spreads, mappedGames }: Props) {
  // Merge: show all spreads + mapped games that have no spread data
  const spreadGameIds = new Set(spreads.map((s) => s.game_id));
  const grayRows: SpreadRow[] = mappedGames
    .filter((g) => !spreadGameIds.has(g.game_id))
    .map((g) => ({
      game_id: g.game_id,
      game_name: g.game_id,
      sport: g.sport,
      team: `${g.team1}/${g.team2}`,
      k_bid: 0,
      k_ask: 0,
      pm_bid: 0,
      pm_ask: 0,
      spread_buy_pm: 0,
      spread_buy_k: 0,
      pm_size: 0,
      is_executable: false,
      game_date: g.date,
      updated_at: "",
    }));

  const allRows = [...spreads, ...grayRows].sort((a, b) => {
    const aMax = Math.max(a.spread_buy_pm, a.spread_buy_k);
    const bMax = Math.max(b.spread_buy_pm, b.spread_buy_k);
    return bMax - aMax;
  });

  if (allRows.length === 0) {
    return (
      <div className="rounded-lg border border-gray-800 bg-[#111] p-4 text-center text-sm text-gray-500">
        No mapped games
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] overflow-hidden">
      <div className="px-3 py-2 border-b border-gray-800 flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          Spread Heatmap ({allRows.length} games)
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-800 text-gray-500">
              <th className="px-2 py-1.5 text-left font-medium">GAME</th>
              <th className="px-2 py-1.5 text-left font-medium">TEAM</th>
              <th className="px-2 py-1.5 text-right font-medium">K BID</th>
              <th className="px-2 py-1.5 text-right font-medium">K ASK</th>
              <th className="px-2 py-1.5 text-right font-medium">PM BID</th>
              <th className="px-2 py-1.5 text-right font-medium">PM ASK</th>
              <th className="px-2 py-1.5 text-right font-medium">BUY PM</th>
              <th className="px-2 py-1.5 text-right font-medium">BUY K</th>
              <th className="px-2 py-1.5 text-right font-medium">BEST</th>
              <th className="px-2 py-1.5 text-right font-medium">AGO</th>
            </tr>
          </thead>
          <tbody>
            {allRows.map((row, i) => {
              const best = Math.max(row.spread_buy_pm, row.spread_buy_k);
              const hasData = row.k_bid > 0;
              return (
                <tr
                  key={`${row.game_id}-${row.team}-${i}`}
                  className={`border-b border-gray-800/50 ${
                    hasData ? "hover:bg-gray-800/30" : "opacity-40"
                  }`}
                >
                  <td className="px-2 py-1.5 font-mono text-gray-300 whitespace-nowrap">
                    <span className={`inline-block rounded px-1 py-0.5 text-[10px] mr-1 ${sportBadge(row.sport)}`}>
                      {row.sport}
                    </span>
                    {row.game_id.slice(0, 20)}
                  </td>
                  <td className="px-2 py-1.5 font-bold text-white">{row.team}</td>
                  <td className="px-2 py-1.5 text-right font-mono text-gray-400">
                    {hasData ? row.k_bid : "-"}
                  </td>
                  <td className="px-2 py-1.5 text-right font-mono text-gray-400">
                    {hasData ? row.k_ask : "-"}
                  </td>
                  <td className="px-2 py-1.5 text-right font-mono text-gray-400">
                    {hasData ? row.pm_bid.toFixed(1) : "-"}
                  </td>
                  <td className="px-2 py-1.5 text-right font-mono text-gray-400">
                    {hasData ? row.pm_ask.toFixed(1) : "-"}
                  </td>
                  <td className="px-2 py-1.5 text-right">
                    {hasData ? <SpreadCell cents={row.spread_buy_pm} /> : <span className="text-gray-600">-</span>}
                  </td>
                  <td className="px-2 py-1.5 text-right">
                    {hasData ? <SpreadCell cents={row.spread_buy_k} /> : <span className="text-gray-600">-</span>}
                  </td>
                  <td className="px-2 py-1.5 text-right">
                    {hasData ? <SpreadCell cents={best} /> : <span className="text-gray-600">-</span>}
                  </td>
                  <td className="px-2 py-1.5 text-right text-gray-500 whitespace-nowrap">
                    {row.updated_at ? timeAgo(row.updated_at) : "-"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
