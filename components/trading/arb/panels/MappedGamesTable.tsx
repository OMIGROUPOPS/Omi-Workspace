"use client";

import React, { useState, useMemo } from "react";
import type { MappedGame } from "../types";
import { sportBadge, spreadColor, isToday, depthColor, fmtNum, todayET } from "../helpers";
import { FilterButton } from "../shared/FilterButton";

type SportFilter = "all" | "CBB" | "NBA" | "NHL";
type DateFilter = "today" | "tomorrow" | "all";

function tomorrowET(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toLocaleDateString("en-CA", { timeZone: "America/New_York" });
}

interface Props {
  games: MappedGame[];
}

export function MappedGamesTable({ games }: Props) {
  const [sportFilter, setSportFilter] = useState<SportFilter>("all");
  const [dateFilter, setDateFilter] = useState<DateFilter>("today");

  const today = todayET();
  const tomorrow = tomorrowET();

  const filtered = useMemo(() => {
    return games.filter((g) => {
      if (sportFilter !== "all" && g.sport.toUpperCase() !== sportFilter) return false;
      if (dateFilter === "today" && g.date !== today) return false;
      if (dateFilter === "tomorrow" && g.date !== tomorrow) return false;
      return true;
    });
  }, [games, sportFilter, dateFilter, today, tomorrow]);

  // Derive available sports from data
  const sports = useMemo(() => {
    const s = new Set(games.map((g) => g.sport.toUpperCase()));
    return Array.from(s).sort();
  }, [games]);

  if (games.length === 0) {
    return (
      <div className="text-center py-6">
        <span className="text-xs text-gray-600">No mapped games data — waiting for executor push</span>
      </div>
    );
  }

  return (
    <div>
      {/* ── Filters ──────────────────────────────────────────── */}
      <div className="px-3 py-2 border-b border-gray-800 flex items-center gap-2">
        <div className="flex items-center gap-1">
          <FilterButton active={dateFilter === "today"} onClick={() => setDateFilter("today")}>Today</FilterButton>
          <FilterButton active={dateFilter === "tomorrow"} onClick={() => setDateFilter("tomorrow")}>Tomorrow</FilterButton>
          <FilterButton active={dateFilter === "all"} onClick={() => setDateFilter("all")}>All</FilterButton>
        </div>
        <span className="text-gray-700">|</span>
        <div className="flex items-center gap-1">
          <FilterButton active={sportFilter === "all"} onClick={() => setSportFilter("all")}>All</FilterButton>
          {sports.map((s) => (
            <FilterButton key={s} active={sportFilter === s as SportFilter} onClick={() => setSportFilter(s as SportFilter)}>
              {s}
            </FilterButton>
          ))}
        </div>
        <span className="ml-auto text-[10px] text-gray-500 font-mono">
          {filtered.length} / {games.length}
        </span>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-6">
          <span className="text-xs text-gray-600">No games match filters</span>
        </div>
      ) : (
        <div className="overflow-auto" style={{ maxHeight: "400px" }}>
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-[#111] z-10">
              <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
                <th className="px-2 py-1.5">Game</th>
                <th className="px-2 py-1.5">Sport</th>
                <th className="px-2 py-1.5">Date</th>
                <th className="px-2 py-1.5">Status</th>
                <th className="px-2 py-1.5 text-right">Best Spread</th>
                <th className="px-2 py-1.5 text-right">K Depth</th>
                <th className="px-2 py-1.5 text-right">PM Depth</th>
                <th className="px-2 py-1.5">Traded</th>
                <th className="px-2 py-1.5">PM Slug</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((g) => {
                const isTodayGame = isToday(g.date);
                return (
                  <tr
                    key={g.cache_key}
                    className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${g.traded ? "bg-emerald-500/5" : ""}`}
                  >
                    <td className="px-2 py-1.5 whitespace-nowrap">
                      <span className="text-white font-medium">{g.team1_full || g.team1}</span>
                      <span className="text-gray-600 mx-1">vs</span>
                      <span className="text-white font-medium">{g.team2_full || g.team2}</span>
                    </td>
                    <td className="px-2 py-1.5">
                      <span className={`inline-block rounded px-1 py-0.5 text-[10px] font-medium ${sportBadge(g.sport)}`}>
                        {g.sport}
                      </span>
                    </td>
                    <td className="px-2 py-1.5 font-mono text-gray-400">
                      {isTodayGame ? <span className="text-emerald-400">Today</span> : g.date.slice(5)}
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
                    <td className={`px-2 py-1.5 text-right font-mono text-[10px] ${depthColor(g.k_depth ?? null)}`}>
                      {g.k_depth != null && g.k_depth > 0 ? fmtNum(g.k_depth) : "\u2014"}
                    </td>
                    <td className={`px-2 py-1.5 text-right font-mono text-[10px] ${depthColor(g.pm_depth ?? null)}`}>
                      {g.pm_depth != null && g.pm_depth > 0 ? fmtNum(g.pm_depth) : "\u2014"}
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
      )}
    </div>
  );
}
