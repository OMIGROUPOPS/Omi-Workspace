"use client";

import React from "react";
import type { MappedGame } from "../types";
import { sportBadge, spreadColor, isToday } from "../helpers";

interface Props {
  games: MappedGame[];
}

export function MappedGamesTable({ games }: Props) {
  if (games.length === 0) {
    return (
      <div className="text-center py-6">
        <span className="text-xs text-gray-600">No mapped games data — waiting for executor push</span>
      </div>
    );
  }

  return (
    <div className="overflow-auto" style={{ maxHeight: "400px" }}>
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#111] z-10">
          <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
            <th className="px-2 py-1.5">Game</th>
            <th className="px-2 py-1.5">Sport</th>
            <th className="px-2 py-1.5">Date</th>
            <th className="px-2 py-1.5">Status</th>
            <th className="px-2 py-1.5 text-right">Best Spread</th>
            <th className="px-2 py-1.5">Traded</th>
            <th className="px-2 py-1.5">PM Slug</th>
          </tr>
        </thead>
        <tbody>
          {games.map((g) => {
            const today = isToday(g.date);
            return (
              <tr
                key={g.cache_key}
                className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${g.traded ? "bg-emerald-500/5" : ""}`}
              >
                <td className="px-2 py-1.5 whitespace-nowrap">
                  <span className="text-white font-medium">{g.team1}</span>
                  <span className="text-gray-600 mx-1">vs</span>
                  <span className="text-white font-medium">{g.team2}</span>
                </td>
                <td className="px-2 py-1.5">
                  <span className={`inline-block rounded px-1 py-0.5 text-[10px] font-medium ${sportBadge(g.sport)}`}>
                    {g.sport}
                  </span>
                </td>
                <td className="px-2 py-1.5 font-mono text-gray-400">
                  {today ? <span className="text-emerald-400">Today</span> : g.date.slice(5)}
                </td>
                <td className="px-2 py-1.5">
                  <span className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${
                    g.status === "Active" ? "bg-emerald-500/20 text-emerald-400" : "bg-gray-500/20 text-gray-500"
                  }`}>
                    {g.status}
                  </span>
                </td>
                <td className={`px-2 py-1.5 text-right font-mono font-bold ${spreadColor(g.best_spread)}`}>
                  {g.best_spread > 0 ? g.best_spread.toFixed(1) : "-"}
                </td>
                <td className="px-2 py-1.5">
                  {g.traded
                    ? <span className="text-emerald-400 text-[9px] font-medium">YES</span>
                    : <span className="text-gray-600 text-[9px]">-</span>}
                </td>
                <td className="px-2 py-1.5 text-[9px] text-gray-600 font-mono truncate max-w-[160px]">
                  {g.pm_slug}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
