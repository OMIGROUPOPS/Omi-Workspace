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
  kYes: number;       // This team's K YES ask
  pmYes: number;      // This team's PM YES ask
  oppPmYes: number;   // Opponent's PM YES ask (used in combined)
  combined: number;   // Arb cost: K YES this team + PM YES opponent
  netArb: number;     // 100 - combined - fees
  feeEst: number;
  gameStatus?: string;
  period?: string;
  clock?: string;
  date: string;
  gameTime?: string;
  isLive: boolean;
  rowGroup: number;
  isFirstOfPair: boolean;
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

/** Build a pair of rows for one game — one per team. */
function buildGameRows(g: MappedGame, rowGroup: number): MarketRow[] {
  const t1 = g.team1_prices;
  const t2 = g.team2_prices;
  // Need prices from both platforms on both teams
  if (!t1 || !t2) return [];
  if ((!t1.k_ask && !t1.k_bid) || (!t2.k_ask && !t2.k_bid)) return [];
  if ((!t1.pm_ask && !t1.pm_bid) || (!t2.pm_ask && !t2.pm_bid)) return [];

  const base = {
    gameId: g.game_id,
    cacheKey: g.cache_key,
    sport: g.sport,
    gameStatus: g.game_status,
    period: g.period,
    clock: g.clock,
    date: g.date,
    gameTime: g.game_time,
    isLive: g.game_status === "in",
    rowGroup,
  };

  // Row 1: Buy K YES team1 + Buy PM YES team2
  const k1 = t1.k_ask || t1.k_bid;
  const pm1 = t1.pm_ask || t1.pm_bid;
  const pm2opp = t2.pm_ask || t2.pm_bid;
  const combined1 = k1 + pm2opp;
  const fee1 = computeFeeEst(k1);
  const net1 = 100 - combined1 - fee1;

  // Row 2: Buy K YES team2 + Buy PM YES team1
  const k2 = t2.k_ask || t2.k_bid;
  const pm2 = t2.pm_ask || t2.pm_bid;
  const pm1opp = t1.pm_ask || t1.pm_bid;
  const combined2 = k2 + pm1opp;
  const fee2 = computeFeeEst(k2);
  const net2 = 100 - combined2 - fee2;

  return [
    {
      ...base,
      team: g.team1_full || g.team1,
      opponent: g.team2_full || g.team2,
      kYes: k1,
      pmYes: pm1,
      oppPmYes: pm2opp,
      combined: combined1,
      netArb: net1,
      feeEst: fee1,
      isFirstOfPair: true,
    },
    {
      ...base,
      team: g.team2_full || g.team2,
      opponent: g.team1_full || g.team1,
      kYes: k2,
      pmYes: pm2,
      oppPmYes: pm1opp,
      combined: combined2,
      netArb: net2,
      feeEst: fee2,
      isFirstOfPair: false,
    },
  ];
}

export function LiveMarketsTable({ games }: Props) {
  // Build pairs sorted by best net arb in each game
  const gamePairs = useMemo(() => {
    const pairs: MarketRow[][] = [];
    games.forEach((g, gi) => {
      const rows = buildGameRows(g, gi);
      if (rows.length === 2) pairs.push(rows);
    });
    // Sort games by the better net arb of the pair (descending)
    pairs.sort((a, b) => Math.max(b[0].netArb, b[1].netArb) - Math.max(a[0].netArb, a[1].netArb));
    return pairs;
  }, [games]);

  if (gamePairs.length === 0) {
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
            <th className="px-2 py-1.5">TEAM</th>
            <th className="px-2 py-1.5 text-right">K YES</th>
            <th className="px-2 py-1.5 text-right">PM YES</th>
            <th className="px-2 py-1.5 text-right">COMBINED</th>
            <th className="px-2 py-1.5 text-right">NET ARB</th>
            <th className="px-2 py-1.5 text-right">FEE EST</th>
            <th className="px-2 py-1.5">STATUS</th>
          </tr>
        </thead>
        <tbody>
          {gamePairs.map((pair, gi) => {
            const stripe = gi % 2 === 1 ? "bg-white/[0.02]" : "";
            const liveBorder = pair[0].isLive ? "border-l-2 border-l-[#00bfff]" : "";
            // Highlight the better arb direction
            const bestIdx = pair[0].netArb >= pair[1].netArb ? 0 : 1;

            return (
              <React.Fragment key={pair[0].cacheKey}>
                {pair.map((r, ri) => (
                  <tr
                    key={`${r.cacheKey}-${r.team}`}
                    className={`${ri === 0 ? "border-t border-[#1a1a2e]/80" : "border-b border-[#1a1a2e]/50"} hover:bg-[#00bfff]/[0.04] transition-colors font-mono ${stripe} ${liveBorder}`}
                  >
                    <td className="px-2 py-1 whitespace-nowrap">
                      {ri === 0 && (
                        <span className={`inline-block rounded-none px-1 py-0.5 text-[8px] font-medium mr-1 ${sportBadge(r.sport)}`}>
                          {r.sport}
                        </span>
                      )}
                      <span className="text-[#ff8c00] font-medium">{r.team}</span>
                    </td>
                    <td className="px-2 py-1 text-right font-mono text-[#00bfff]">
                      {r.kYes}c
                    </td>
                    <td className="px-2 py-1 text-right font-mono text-[#00ff88]">
                      {r.pmYes}c
                    </td>
                    <td className="px-2 py-1 text-right font-mono text-[#ff8c00]">
                      {r.combined.toFixed(0)}c
                    </td>
                    <td className={`px-2 py-1 text-right font-mono font-bold ${arbColor(r.netArb)} ${ri === bestIdx ? "" : "opacity-50"}`}>
                      {r.netArb > 0 ? "+" : ""}{r.netArb.toFixed(1)}c
                    </td>
                    <td className="px-2 py-1 text-right font-mono text-[#4a4a6a]">
                      {r.feeEst.toFixed(1)}c
                    </td>
                    {ri === 0 && (
                      <td className="px-2 py-1 whitespace-nowrap text-[10px]" rowSpan={2}>
                        {gameClockCell(r)}
                      </td>
                    )}
                  </tr>
                ))}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
