"use client";

import React, { useState, useMemo } from "react";
import type { MappedGame, TeamPrices } from "../types";
import { sportBadge, spreadColor, isToday, depthColor, fmtNum, todayET } from "../helpers";
import { FilterButton } from "../shared/FilterButton";

type SportFilter = "all" | "CBB" | "NBA" | "NHL" | "UFC";
type DateFilter = "today" | "tomorrow" | "all";

function tomorrowET(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toLocaleDateString("en-CA", { timeZone: "America/New_York" });
}

/** Format bid/ask as compact "42/45" string, or "—" if no data. */
function ba(p: TeamPrices | undefined, field: "k" | "pm"): React.ReactNode {
  if (!p) return <span className="text-[#3a3a5a]">&mdash;</span>;
  const bid = field === "k" ? p.k_bid : p.pm_bid;
  const ask = field === "k" ? p.k_ask : p.pm_ask;
  if (!bid && !ask) return <span className="text-[#3a3a5a]">&mdash;</span>;
  return (
    <>
      <span className="text-[#ff8c00]">{bid || "—"}</span>
      <span className="text-[#3a3a5a]">/</span>
      <span className="text-[#ff8c00]">{ask || "—"}</span>
    </>
  );
}

/** Render the game clock/status cell content based on ESPN data. */
function gameClockCell(g: MappedGame): React.ReactNode {
  const gs = g.game_status;
  if (gs === "in") {
    // Live: amber block + period + clock
    return (
      <span className="text-[#00ff88] font-mono font-medium">
        <span className="inline-block w-1.5 h-1.5 bg-[#00ff88] mr-1 animate-pulse" />
        {g.period}{g.clock ? ` ${g.clock}` : ""}
      </span>
    );
  }
  if (gs === "post") {
    return <span className="text-[#4a4a6a] font-mono">FINAL</span>;
  }
  // Pre-game or no ESPN data — show date + optional start time
  const isTodayGame = isToday(g.date);
  return (
    <span className="font-mono text-[#4a4a6a]">
      {isTodayGame ? <span className="text-[#00ff88]">TODAY</span> : g.date.slice(5)}
      {g.game_time ? <span className="text-[#3a3a5a] ml-1 text-[9px]">{g.game_time}</span> : null}
    </span>
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

  const liveCount = useMemo(() => filtered.filter((g) => g.game_status === "in").length, [filtered]);

  if (games.length === 0) {
    return (
      <div className="text-center py-6">
        <span className="text-[9px] font-mono text-[#3a3a5a] uppercase tracking-wider">NO MAPPED GAMES — WAITING FOR EXECUTOR PUSH</span>
      </div>
    );
  }

  return (
    <div>
      {/* ── Filters ──────────────────────────────────────────── */}
      <div className="px-3 py-1.5 border-b border-[#1a1a2e] flex items-center gap-2">
        <div className="flex items-center gap-1">
          <FilterButton active={dateFilter === "today"} onClick={() => setDateFilter("today")}>TODAY</FilterButton>
          <FilterButton active={dateFilter === "tomorrow"} onClick={() => setDateFilter("tomorrow")}>TMRW</FilterButton>
          <FilterButton active={dateFilter === "all"} onClick={() => setDateFilter("all")}>ALL</FilterButton>
        </div>
        <span className="text-[#1a1a2e] font-mono">|</span>
        <div className="flex items-center gap-1">
          <FilterButton active={sportFilter === "all"} onClick={() => setSportFilter("all")}>ALL</FilterButton>
          {sports.map((s) => (
            <FilterButton key={s} active={sportFilter === s as SportFilter} onClick={() => setSportFilter(s as SportFilter)}>
              {s}
            </FilterButton>
          ))}
        </div>
        <span className="ml-auto text-[9px] text-[#4a4a6a] font-mono">
          {liveCount > 0 && <span className="text-[#00ff88] mr-2">{liveCount} LIVE</span>}
          {filtered.length}<span className="text-[#3a3a5a]">/{games.length}</span>
        </span>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-6">
          <span className="text-[9px] font-mono text-[#3a3a5a] uppercase tracking-wider">NO GAMES MATCH FILTERS</span>
        </div>
      ) : (
        <div className="overflow-auto" style={{ maxHeight: "500px" }}>
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
              <tr className="text-left text-[9px] font-mono font-medium uppercase tracking-wider text-[#4a4a6a]">
                <th className="px-2 py-1.5">TEAM</th>
                <th className="px-2 py-1.5 text-center">K BID/ASK</th>
                <th className="px-2 py-1.5 text-center">PM BID/ASK</th>
                <th className="px-2 py-1.5 text-right">SPREAD</th>
                <th className="px-2 py-1.5">SPORT</th>
                <th className="px-2 py-1.5">GAME</th>
                <th className="px-2 py-1.5 text-right">DEPTH</th>
                <th className="px-2 py-1.5">STATUS</th>
                <th className="px-2 py-1.5">TRADED</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((g, gi) => {
                const t1 = g.team1_prices;
                const t2 = g.team2_prices;
                const arbThreshold = 4;
                const isLive = g.game_status === "in";
                const isFinal = g.game_status === "post";
                const hasScore = isLive || isFinal;
                const stripe = gi % 2 === 1 ? "bg-white/[0.02]" : "";
                const tradedBg = g.traded ? "bg-[#00ff88]/[0.03]" : "";
                const liveBorder = isLive ? "border-l-2 border-l-[#00ff88]" : "";
                const rowBg = tradedBg || stripe;

                return (
                  <React.Fragment key={g.cache_key}>
                    {/* ── Team 1 row (includes game info) ── */}
                    <tr className={`border-t border-[#1a1a2e]/80 hover:bg-[#ff8c00]/[0.03] transition-colors font-mono ${rowBg} ${liveBorder}`}>
                      <td className="px-2 py-1 whitespace-nowrap">
                        <span className="text-[#ff8c00] font-medium">{g.team1_full || g.team1}</span>
                        {hasScore && (
                          <span className={`ml-2 font-mono font-bold ${isLive ? "text-[#00ff88]" : "text-[#4a4a6a]"}`}>
                            {g.team1_score}
                          </span>
                        )}
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t1, "k")}
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t1, "pm")}
                      </td>
                      <td className={`px-2 py-1 text-right font-mono font-bold text-[10px] ${
                        t1 && t1.spread >= arbThreshold ? "text-[#00ff88]" : spreadColor(t1?.spread ?? 0)
                      }`}>
                        {t1 && t1.spread > 0 ? `${t1.spread.toFixed(1)}c` : "—"}
                      </td>
                      <td className="px-2 py-1" rowSpan={2}>
                        <span className={`inline-block rounded-none px-1 py-0.5 text-[9px] font-mono font-medium ${sportBadge(g.sport)}`}>
                          {g.sport}
                        </span>
                      </td>
                      <td className="px-2 py-1 whitespace-nowrap" rowSpan={2}>
                        {gameClockCell(g)}
                      </td>
                      <td className="px-2 py-1 text-right font-mono text-[10px] whitespace-nowrap" rowSpan={2}>
                        <span className={depthColor(g.k_depth ?? null)}>K:{g.k_depth != null && g.k_depth > 0 ? fmtNum(g.k_depth) : "—"}</span>
                        <span className="text-[#3a3a5a] mx-0.5">|</span>
                        <span className={depthColor(g.pm_depth ?? null)}>PM:{g.pm_depth != null && g.pm_depth > 0 ? fmtNum(g.pm_depth) : "—"}</span>
                      </td>
                      <td className="px-2 py-1" rowSpan={2}>
                        <span className={`inline-block rounded-none border px-1 py-0.5 text-[9px] font-mono font-medium ${
                          g.status === "Active"
                            ? "bg-[#00ff88]/10 text-[#00ff88] border-[#00ff88]/30"
                            : "bg-[#4a4a6a]/10 text-[#4a4a6a] border-[#4a4a6a]/30"
                        }`}>
                          {g.status}
                        </span>
                      </td>
                      <td className="px-2 py-1" rowSpan={2}>
                        {g.traded
                          ? <span className="text-[#00ff88] text-[9px] font-mono font-bold">YES</span>
                          : <span className="text-[#3a3a5a] text-[9px] font-mono">-</span>}
                      </td>
                    </tr>
                    {/* ── Team 2 row ── */}
                    <tr className={`border-b border-[#1a1a2e]/50 hover:bg-[#ff8c00]/[0.03] transition-colors font-mono ${rowBg} ${liveBorder}`}>
                      <td className="px-2 py-1 whitespace-nowrap">
                        <span className="text-[#ff8c00] font-medium">{g.team2_full || g.team2}</span>
                        {hasScore && (
                          <span className={`ml-2 font-mono font-bold ${isLive ? "text-[#00ff88]" : "text-[#4a4a6a]"}`}>
                            {g.team2_score}
                          </span>
                        )}
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t2, "k")}
                      </td>
                      <td className="px-2 py-1 text-center font-mono text-[10px]">
                        {ba(t2, "pm")}
                      </td>
                      <td className={`px-2 py-1 text-right font-mono font-bold text-[10px] ${
                        t2 && t2.spread >= arbThreshold ? "text-[#00ff88]" : spreadColor(t2?.spread ?? 0)
                      }`}>
                        {t2 && t2.spread > 0 ? `${t2.spread.toFixed(1)}c` : "—"}
                      </td>
                      {/* Sport, Game, Depth, Status, Traded handled by rowSpan above */}
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
