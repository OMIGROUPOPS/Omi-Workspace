"use client";

import React, { useMemo } from "react";
import type { MappedGame, TeamPrices } from "../types";
import { sportBadge, computeFeeEst, arbColor, isToday } from "../helpers";

interface Props {
  games: MappedGame[];
}

interface MarketRow {
  gameId: string;
  cacheKey: string;
  sport: string;
  team: string;
  opponent: string;
  kYes: number;
  pmYes: number;
  combined: number;
  netArb: number;
  feeEst: number;
  spread: number;
  gameStatus?: string;
  period?: string;
  clock?: string;
  date: string;
  gameTime?: string;
  isLive: boolean;
  rowGroup: number;
}

function gameClockCell(r: MarketRow): React.ReactNode {
  if (r.gameStatus === "in") {
    return (
      <span className="text-[#00ff88] font-mono font-medium">
        <span className="inline-block w-1.5 h-1.5 bg-[#00ff88] mr-1 animate-pulse" />
        {r.period}{r.clock ? ` ${r.clock}` : ""}
      </span>
    );
  }
  if (r.gameStatus === "post") {
    return <span className="text-[#4a4a6a] font-mono">FINAL</span>;
  }
  const isTodayGame = isToday(r.date);
  return (
    <span className="font-mono text-[#4a4a6a]">
      {isTodayGame ? <span className="text-[#00ff88]">TODAY</span> : r.date.slice(5)}
      {r.gameTime ? <span className="text-[#3a3a5a] ml-1 text-[9px]">{r.gameTime}</span> : null}
    </span>
  );
}

function buildRow(
  g: MappedGame,
  teamName: string,
  oppName: string,
  tp: TeamPrices | undefined,
  rowGroup: number,
): MarketRow | null {
  if (!tp) return null;
  const { k_bid, k_ask, pm_bid, pm_ask } = tp;
  if (!k_bid && !k_ask && !pm_bid && !pm_ask) return null;

  // Dir A: BUY PM SELL K → buy PM ask, sell K bid
  const feeA = computeFeeEst(k_bid || 0);
  const combinedA = (pm_ask || 0) + (100 - (k_bid || 0));
  const netA = 100 - combinedA - feeA;

  // Dir B: BUY K SELL PM → buy K ask, sell PM bid
  const feeB = computeFeeEst(k_ask || 0);
  const combinedB = (k_ask || 0) + (100 - (pm_bid || 0));
  const netB = 100 - combinedB - feeB;

  // Pick better direction
  const useA = netA >= netB;
  return {
    gameId: g.game_id,
    cacheKey: g.cache_key,
    sport: g.sport,
    team: teamName,
    opponent: oppName,
    kYes: useA ? (k_bid || 0) : (k_ask || 0),
    pmYes: useA ? (pm_ask || 0) : (pm_bid || 0),
    combined: useA ? combinedA : combinedB,
    netArb: useA ? netA : netB,
    feeEst: useA ? feeA : feeB,
    spread: tp.spread,
    gameStatus: g.game_status,
    period: g.period,
    clock: g.clock,
    date: g.date,
    gameTime: g.game_time,
    isLive: g.game_status === "in",
    rowGroup,
  };
}

export function LiveMarketsTable({ games }: Props) {
  const rows = useMemo(() => {
    const all: MarketRow[] = [];
    games.forEach((g, gi) => {
      const r1 = buildRow(g, g.team1_full || g.team1, g.team2_full || g.team2, g.team1_prices, gi);
      if (r1) all.push(r1);
      const r2 = buildRow(g, g.team2_full || g.team2, g.team1_full || g.team1, g.team2_prices, gi);
      if (r2) all.push(r2);
    });
    all.sort((a, b) => b.netArb - a.netArb);
    return all;
  }, [games]);

  if (rows.length === 0) {
    return (
      <div className="text-center py-6">
        <span className="text-[9px] font-mono text-[#3a3a5a] uppercase tracking-wider">NO LIVE MARKET DATA</span>
      </div>
    );
  }

  return (
    <div className="overflow-auto" style={{ maxHeight: "500px" }}>
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
          <tr className="text-left text-[9px] font-mono font-medium uppercase tracking-wider text-[#4a4a6a]">
            <th className="px-2 py-1.5">GAME</th>
            <th className="px-2 py-1.5 text-right">K YES</th>
            <th className="px-2 py-1.5 text-right">PM YES</th>
            <th className="px-2 py-1.5 text-right">COMBINED</th>
            <th className="px-2 py-1.5 text-right">NET ARB</th>
            <th className="px-2 py-1.5 text-right">FEE EST</th>
            <th className="px-2 py-1.5 text-right">SPREAD</th>
            <th className="px-2 py-1.5">STATUS</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => {
            const stripe = r.rowGroup % 2 === 1 ? "bg-white/[0.02]" : "";
            const liveBorder = r.isLive ? "border-l-2 border-l-[#00bfff]" : "";
            return (
              <tr
                key={`${r.cacheKey}-${r.team}-${i}`}
                className={`border-b border-[#1a1a2e]/50 hover:bg-[#00bfff]/[0.04] transition-colors font-mono ${stripe} ${liveBorder}`}
              >
                <td className="px-2 py-1.5 whitespace-nowrap">
                  <span className={`inline-block rounded-none px-1 py-0.5 text-[8px] font-medium mr-1 ${sportBadge(r.sport)}`}>
                    {r.sport}
                  </span>
                  <span className="text-[#ff8c00] font-medium">{r.team}</span>
                  <span className="text-[#4a4a6a] text-[9px] ml-1">vs {r.opponent}</span>
                </td>
                <td className="px-2 py-1.5 text-right font-mono text-[#00bfff]">
                  {r.kYes > 0 ? `${r.kYes}c` : "—"}
                </td>
                <td className="px-2 py-1.5 text-right font-mono text-[#00ff88]">
                  {r.pmYes > 0 ? `${r.pmYes}c` : "—"}
                </td>
                <td className="px-2 py-1.5 text-right font-mono text-[#ff8c00]">
                  {r.combined > 0 ? `${r.combined.toFixed(1)}c` : "—"}
                </td>
                <td className={`px-2 py-1.5 text-right font-mono font-bold ${arbColor(r.netArb)}`}>
                  {r.netArb > 0 ? "+" : ""}{r.netArb.toFixed(1)}c
                </td>
                <td className="px-2 py-1.5 text-right font-mono text-[#4a4a6a]">
                  {r.feeEst.toFixed(1)}c
                </td>
                <td className={`px-2 py-1.5 text-right font-mono font-bold text-[10px] ${arbColor(r.spread)}`}>
                  {r.spread > 0 ? `${r.spread.toFixed(1)}c` : "—"}
                </td>
                <td className="px-2 py-1.5 whitespace-nowrap text-[10px]">
                  {gameClockCell(r)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
