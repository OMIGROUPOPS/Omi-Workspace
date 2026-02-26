"use client";

import React, { useState, useMemo } from "react";
import type { MappedGame, TeamPrices } from "../types";
import { sportBadge, spreadColor, isToday, depthColor, fmtNum, todayET } from "../helpers";
import { FilterButton } from "../shared/FilterButton";

type SportFilter = "all" | "CBB" | "NBA" | "NHL";
type DateFilter = "today" | "tomorrow" | "all";

function tomorrowET(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toLocaleDateString("en-CA", { timeZone: "America/New_York" });
}

/** Format bid/ask as compact "42/45" string, or "—" if no data. */
function ba(p: TeamPrices | undefined, field: "k" | "pm"): React.ReactNode {
  if (!p) return <span className="text-gray-700">&mdash;</span>;
  const bid = field === "k" ? p.k_bid : p.pm_bid;
  const ask = field === "k" ? p.k_ask : p.pm_ask;
  if (!bid && !ask) return <span className="text-gray-700">&mdash;</span>;
  return (
    <>
      <span className="text-gray-300">{bid || "—"}</span>
      <span className="text-gray-600">/</span>
      <span className="text-gray-300">{ask || "—"}</span>
    </>
  );
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
        <div className="overflow-auto" style={{ maxHeight: "500px" }}>
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-[#111] z-10">
              <tr className="border-b border-gray-800 text-left text-[10px] font-medium uppercase tracking-wider text-gray-500">
                <th className="px-2 py-1.5">Team</th>
                <th className="px-2 py-1.5 text-center">K Bid/Ask</th>
                <th className="px-2 py-1.5 text-center">PM Bid/Ask</th>
                <th className="px-2 py-1.5 text-right">Spread</th>
                <th className="px-2 py-1.5">Sport</th>
                <th className="px-2 py-1.5">Date</th>
                <th className="px-2 py-1.5 text-right">Depth</th>
                <th className="px-2 py-1.5">Status</th>
                <th className="px-2 py-1.5">Traded</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((g) => {
                const isTodayGame = isToday(g.date);
                const t1 = g.team1_prices;
                const t2 = g.team2_prices;
                const arbThreshold = 4;

                return (
                  <React.Fragment key={g.cache_key}>
                    {/* ── Team 1 row (includes game info) ── */}
                    <tr className={`border-t border-gray-800/80 hover:bg-gray-800/30 transition-colors ${g.traded ? "bg-emerald-500/5" : ""}`}>
                      <td className="px-2 py-1 whitespace-nowrap">
                        <span className="text-white font-medium">{g.team1_full || g.team1}</span>
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t1, "k")}
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t1, "pm")}
                      </td>
                      <td className={`px-2 py-1 text-right font-mono font-bold text-[10px] ${
                        t1 && t1.spread >= arbThreshold ? "text-emerald-400" : spreadColor(t1?.spread ?? 0)
                      }`}>
                        {t1 && t1.spread > 0 ? `${t1.spread.toFixed(1)}c` : "—"}
                      </td>
                      <td className="px-2 py-1" rowSpan={2}>
                        <span className={`inline-block rounded px-1 py-0.5 text-[10px] font-medium ${sportBadge(g.sport)}`}>
                          {g.sport}
                        </span>
                      </td>
                      <td className="px-2 py-1 font-mono text-gray-400" rowSpan={2}>
                        {isTodayGame ? <span className="text-emerald-400">Today</span> : g.date.slice(5)}
                      </td>
                      <td className="px-2 py-1 text-right font-mono text-[10px] whitespace-nowrap" rowSpan={2}>
                        <span className={depthColor(g.k_depth ?? null)}>K:{g.k_depth != null && g.k_depth > 0 ? fmtNum(g.k_depth) : "—"}</span>
                        <span className="text-gray-700 mx-0.5">|</span>
                        <span className={depthColor(g.pm_depth ?? null)}>PM:{g.pm_depth != null && g.pm_depth > 0 ? fmtNum(g.pm_depth) : "—"}</span>
                      </td>
                      <td className="px-2 py-1" rowSpan={2}>
                        <span className={`inline-block rounded px-1 py-0.5 text-[9px] font-medium ${
                          g.status === "Active" ? "bg-emerald-500/20 text-emerald-400" : "bg-gray-500/20 text-gray-500"
                        }`}>
                          {g.status}
                        </span>
                      </td>
                      <td className="px-2 py-1" rowSpan={2}>
                        {g.traded
                          ? <span className="text-emerald-400 text-[9px] font-medium">YES</span>
                          : <span className="text-gray-600 text-[9px]">-</span>}
                      </td>
                    </tr>
                    {/* ── Team 2 row ── */}
                    <tr className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${g.traded ? "bg-emerald-500/5" : ""}`}>
                      <td className="px-2 py-1 whitespace-nowrap">
                        <span className="text-white font-medium">{g.team2_full || g.team2}</span>
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t2, "k")}
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t2, "pm")}
                      </td>
                      <td className={`px-2 py-1 text-right font-mono font-bold text-[10px] ${
                        t2 && t2.spread >= arbThreshold ? "text-emerald-400" : spreadColor(t2?.spread ?? 0)
                      }`}>
                        {t2 && t2.spread > 0 ? `${t2.spread.toFixed(1)}c` : "—"}
                      </td>
                      {/* Sport, Date, Depth, Status, Traded handled by rowSpan above */}
                    </tr>
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
