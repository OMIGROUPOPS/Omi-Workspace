"use client";

import React, { useMemo } from "react";
import type { MappedGame } from "../types";
import { sportBadge, computeFeeEst, arbColor } from "../helpers";

interface Props {
  games: MappedGame[];
}

interface MarketRow {
  gameId: string;
  cacheKey: string;
  sport: string;
  team: string;
  opponent: string;
  kYes: number;       // K YES price for THIS team (buy leg)
  oppPmYes: number;   // PM YES price for OPPONENT (hedge leg)
  combined: number;   // kYes + oppPmYes = arb cost
  netArb: number;     // 100 - combined - fees
  feeEst: number;
  gameStatus?: string;
  period?: string;
  clock?: string;
  date: string;
  gameTime?: string;
  isLive: boolean;
  isFirstOfPair: boolean;
}

/** Build a pair of rows for one game — one per team. */
function buildGameRows(g: MappedGame): MarketRow[] {
  const t1 = g.team1_prices;
  const t2 = g.team2_prices;
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
  };

  // Row 1: Buy K YES team1 + Buy PM YES team2 (opponent)
  const k1 = t1.k_ask || t1.k_bid;
  const pm2forOpp = t2.pm_ask || t2.pm_bid;
  const combined1 = k1 + pm2forOpp;
  const fee1 = computeFeeEst(k1);

  // Row 2: Buy K YES team2 + Buy PM YES team1 (opponent)
  const k2 = t2.k_ask || t2.k_bid;
  const pm1forOpp = t1.pm_ask || t1.pm_bid;
  const combined2 = k2 + pm1forOpp;
  const fee2 = computeFeeEst(k2);

  return [
    { ...base, team: g.team1_full || g.team1, opponent: g.team2_full || g.team2, kYes: k1, oppPmYes: pm2forOpp, combined: combined1, netArb: 100 - combined1 - fee1, feeEst: fee1, isFirstOfPair: true },
    { ...base, team: g.team2_full || g.team2, opponent: g.team1_full || g.team1, kYes: k2, oppPmYes: pm1forOpp, combined: combined2, netArb: 100 - combined2 - fee2, feeEst: fee2, isFirstOfPair: false },
  ];
}

function timeCell(r: MarketRow): React.ReactNode {
  if (r.gameStatus === "in") {
    return (
      <span className="text-[#00ff88] font-mono font-medium">
        <span className="inline-block w-1.5 h-1.5 bg-[#00ff88] mr-1 animate-pulse" />
        {r.period && r.clock ? `${r.period} ${r.clock}` : "LIVE"}
      </span>
    );
  }
  if (r.gameStatus === "post") {
    return <span className="text-[#4a4a6a] font-mono">FINAL</span>;
  }
  return (
    <span className="font-mono text-[#4a4a6a]">
      {r.gameTime || r.date.slice(5)}
    </span>
  );
}

const TH = "px-2 py-1.5 text-[9px] font-mono font-medium uppercase tracking-wider text-[#4a4a6a]";

function SectionTable({ pairs, sectionIdx }: { pairs: MarketRow[][]; sectionIdx: number }) {
  return (
    <>
      {pairs.map((pair, gi) => {
        const globalIdx = sectionIdx + gi;
        const stripe = globalIdx % 2 === 1 ? "bg-white/[0.02]" : "";
        const liveBorder = pair[0].isLive ? "border-l-2 border-l-[#00ff88]" : "";
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
                <td className="px-2 py-1 text-right font-mono text-[#00bfff]">{r.kYes}c</td>
                <td className="px-2 py-1 text-right font-mono text-[#00ff88]">{r.oppPmYes}c</td>
                <td className="px-2 py-1 text-right font-mono text-[#ff8c00]">{r.combined.toFixed(0)}c</td>
                <td className={`px-2 py-1 text-right font-mono font-bold ${arbColor(r.netArb)} ${ri === bestIdx ? "" : "opacity-50"}`}>
                  {r.netArb > 0 ? "+" : ""}{r.netArb.toFixed(1)}c
                </td>
                <td className="px-2 py-1 text-right font-mono text-[#4a4a6a]">{r.feeEst.toFixed(1)}c</td>
                {ri === 0 && (
                  <td className="px-2 py-1 whitespace-nowrap text-[10px]" rowSpan={2}>
                    {timeCell(r)}
                  </td>
                )}
              </tr>
            ))}
          </React.Fragment>
        );
      })}
    </>
  );
}

export function LiveMarketsTable({ games }: Props) {
  const { livePairs, mappedPairs } = useMemo(() => {
    const live: MarketRow[][] = [];
    const mapped: MarketRow[][] = [];

    for (const g of games) {
      const rows = buildGameRows(g);
      if (rows.length !== 2) continue;
      if (g.game_status === "in") {
        live.push(rows);
      } else if (g.game_status !== "post") {
        mapped.push(rows);
      }
    }

    // Live: sort by best net arb descending
    live.sort((a, b) => Math.max(b[0].netArb, b[1].netArb) - Math.max(a[0].netArb, a[1].netArb));

    // Mapped: sort by start time ascending (game_time string, then date)
    mapped.sort((a, b) => {
      const da = a[0].date;
      const db = b[0].date;
      if (da !== db) return da.localeCompare(db);
      const ta = a[0].gameTime || "99:99";
      const tb = b[0].gameTime || "99:99";
      return ta.localeCompare(tb);
    });

    return { livePairs: live, mappedPairs: mapped };
  }, [games]);

  if (livePairs.length === 0 && mappedPairs.length === 0) {
    return (
      <div className="text-center py-6">
        <span className="text-[9px] font-mono text-[#3a3a5a] uppercase tracking-wider">NO MARKET DATA</span>
      </div>
    );
  }

  return (
    <div className="overflow-auto" style={{ maxHeight: "500px" }}>
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
          <tr className="text-left">
            <th className={TH}>TEAM</th>
            <th className={`${TH} text-right`}>K YES</th>
            <th className={`${TH} text-right`}>PM OPP</th>
            <th className={`${TH} text-right`}>COMBINED</th>
            <th className={`${TH} text-right`}>NET ARB</th>
            <th className={`${TH} text-right`}>FEE EST</th>
            <th className={TH}>TIME</th>
          </tr>
        </thead>
        <tbody>
          {/* ── Live games ─────────────────────────────────── */}
          {livePairs.length > 0 && (
            <>
              <tr>
                <td colSpan={7} className="px-2 py-1 bg-[#00ff88]/[0.06] border-y border-[#00ff88]/20">
                  <span className="text-[9px] font-mono font-bold uppercase tracking-widest text-[#00ff88]">
                    <span className="inline-block w-1.5 h-1.5 bg-[#00ff88] mr-1.5 animate-pulse" />
                    LIVE MARKETS ({livePairs.length})
                  </span>
                </td>
              </tr>
              <SectionTable pairs={livePairs} sectionIdx={0} />
            </>
          )}

          {/* ── Upcoming / mapped games ────────────────────── */}
          {mappedPairs.length > 0 && (
            <>
              <tr>
                <td colSpan={7} className="px-2 py-1 bg-[#00bfff]/[0.06] border-y border-[#00bfff]/20">
                  <span className="text-[9px] font-mono font-bold uppercase tracking-widest text-[#00bfff]">
                    MAPPED GAMES ({mappedPairs.length})
                  </span>
                </td>
              </tr>
              <SectionTable pairs={mappedPairs} sectionIdx={livePairs.length} />
            </>
          )}
        </tbody>
      </table>
    </div>
  );
}
