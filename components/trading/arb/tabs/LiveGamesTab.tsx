"use client";

import React, { useState, useMemo } from "react";
import type { ArbDataReturn } from "../hooks/useArbData";
import type { MappedGame, TeamPrices } from "../types";
import { spreadColor, sportBadge, depthColor, fmtNum } from "../helpers";

interface Props {
  data: ArbDataReturn;
}

/** Price cell: shows bid/ask in cents with coloring */
function PriceCell({ prices, field }: { prices: TeamPrices | undefined; field: "k" | "pm" }) {
  if (!prices) return <span className="text-[#2a2a4a]">—</span>;
  const bid = field === "k" ? prices.k_bid : prices.pm_bid;
  const ask = field === "k" ? prices.k_ask : prices.pm_ask;
  if (!bid && !ask) return <span className="text-[#2a2a4a]">—</span>;
  return (
    <span className="font-mono">
      <span className="text-[#00ff88]">{bid || "—"}</span>
      <span className="text-[#2a2a4a] mx-px">/</span>
      <span className="text-[#ff6666]">{ask || "—"}</span>
    </span>
  );
}

/** Spread badge with background color based on arb profitability */
function SpreadBadge({ cents }: { cents: number }) {
  if (cents <= 0) return <span className="text-[#2a2a4a]">—</span>;
  const isArb = cents >= 4;
  const bg = isArb
    ? "bg-[#00ff88]/15 border-[#00ff88]/30"
    : cents >= 2
    ? "bg-[#ff8c00]/10 border-[#ff8c00]/20"
    : "bg-transparent border-[#2a2a4a]";
  const text = isArb ? "text-[#00ff88]" : cents >= 2 ? "text-[#ff8c00]" : "text-[#4a4a6a]";
  return (
    <span className={`inline-block px-1.5 py-0.5 border font-mono font-bold text-[10px] ${bg} ${text}`}>
      {cents.toFixed(1)}c
    </span>
  );
}

/** Score display for live games */
function ScoreDisplay({ game }: { game: MappedGame }) {
  const isLive = game.game_status === "in";
  const isFinal = game.game_status === "post";
  if (!isLive && !isFinal) return null;

  return (
    <div className="flex items-center gap-2">
      <div className="flex flex-col items-center gap-0.5">
        <span className={`font-mono font-bold text-sm ${isLive ? "text-[#00ff88]" : "text-[#4a4a6a]"}`}>
          {game.team1_score ?? "—"}
        </span>
        <span className={`font-mono font-bold text-sm ${isLive ? "text-[#00ff88]" : "text-[#4a4a6a]"}`}>
          {game.team2_score ?? "—"}
        </span>
      </div>
      {isLive && (
        <div className="flex flex-col items-center">
          <span className="text-[8px] font-mono text-[#00ff88] uppercase tracking-wider">
            {game.period}
          </span>
          <span className="text-[9px] font-mono text-[#00ff88] font-bold">
            {game.clock}
          </span>
        </div>
      )}
      {isFinal && (
        <span className="text-[8px] font-mono text-[#4a4a6a] uppercase">FINAL</span>
      )}
    </div>
  );
}

/** Price comparison bar - visual representation of K vs PM price */
function PriceBar({ kPrice, pmPrice, label }: { kPrice: number; pmPrice: number; label: string }) {
  if (!kPrice && !pmPrice) return null;
  const diff = kPrice - pmPrice;
  const absDiff = Math.abs(diff);
  const maxPrice = Math.max(kPrice, pmPrice, 1);
  const kWidth = (kPrice / maxPrice) * 100;
  const pmWidth = (pmPrice / maxPrice) * 100;

  return (
    <div className="flex items-center gap-1.5 w-full">
      <span className="text-[8px] font-mono text-[#4a4a6a] w-5 text-right shrink-0">{label}</span>
      <div className="flex-1 flex items-center gap-0.5 h-3">
        {/* K bar */}
        <div className="flex-1 relative h-full bg-[#1a1a2e] overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 bg-[#ff8c00]/30 border-r border-[#ff8c00]/60"
            style={{ width: `${kWidth}%` }}
          />
          <span className="absolute inset-0 flex items-center justify-center text-[7px] font-mono text-[#ff8c00] font-bold">
            {kPrice > 0 ? `K:${kPrice}` : ""}
          </span>
        </div>
        {/* PM bar */}
        <div className="flex-1 relative h-full bg-[#1a1a2e] overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 bg-[#00bfff]/30 border-r border-[#00bfff]/60"
            style={{ width: `${pmWidth}%` }}
          />
          <span className="absolute inset-0 flex items-center justify-center text-[7px] font-mono text-[#00bfff] font-bold">
            {pmPrice > 0 ? `PM:${pmPrice}` : ""}
          </span>
        </div>
      </div>
      {/* Diff */}
      <span className={`text-[8px] font-mono font-bold w-6 text-right shrink-0 ${
        absDiff >= 4 ? "text-[#00ff88]" : absDiff >= 2 ? "text-[#ff8c00]" : "text-[#3a3a5a]"
      }`}>
        {absDiff > 0 ? `${diff > 0 ? "+" : ""}${diff}` : "="}
      </span>
    </div>
  );
}

/** Single live game card */
function LiveGameCard({ game }: { game: MappedGame }) {
  const t1 = game.team1_prices;
  const t2 = game.team2_prices;
  const isLive = game.game_status === "in";
  const bestSpread = game.best_spread;
  const isArb = bestSpread >= 4;

  return (
    <div className={`border ${
      isArb ? "border-[#00ff88]/40 bg-[#00ff88]/[0.03]" : 
      isLive ? "border-[#ff8c00]/30 bg-[#ff8c00]/[0.02]" : 
      "border-[#1a1a2e] bg-[#0a0a0f]"
    } relative`}>
      {/* Arb flash indicator */}
      {isArb && (
        <div className="absolute top-0 right-0 px-1.5 py-0.5 bg-[#00ff88]/20 border-l border-b border-[#00ff88]/30">
          <span className="text-[8px] font-mono font-bold text-[#00ff88] uppercase tracking-wider animate-pulse">
            ARB {bestSpread.toFixed(0)}c
          </span>
        </div>
      )}

      {/* Header: Sport badge + Teams + Score */}
      <div className="px-3 py-2 border-b border-[#1a1a2e]/60 flex items-start justify-between">
        <div className="flex items-start gap-2">
          <span className={`inline-block rounded-none px-1 py-0.5 text-[8px] font-mono font-medium mt-0.5 ${sportBadge(game.sport)}`}>
            {game.sport}
          </span>
          <div className="flex flex-col">
            <span className="text-[#ff8c00] font-mono font-medium text-[11px]">
              {game.team1_full || game.team1}
            </span>
            <span className="text-[#ff8c00] font-mono font-medium text-[11px]">
              {game.team2_full || game.team2}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <ScoreDisplay game={game} />
          {isLive && (
            <span className="inline-block w-1.5 h-1.5 bg-[#00ff88] animate-pulse" />
          )}
        </div>
      </div>

      {/* Price comparison table */}
      <div className="px-3 py-2">
        <table className="w-full text-[10px] font-mono">
          <thead>
            <tr className="text-[8px] text-[#4a4a6a] uppercase tracking-wider">
              <th className="text-left py-0.5 w-16">TEAM</th>
              <th className="text-center py-0.5">K BID</th>
              <th className="text-center py-0.5">K ASK</th>
              <th className="text-center py-0.5 text-[#1a1a2e]">│</th>
              <th className="text-center py-0.5">PM BID</th>
              <th className="text-center py-0.5">PM ASK</th>
              <th className="text-center py-0.5 text-[#1a1a2e]">│</th>
              <th className="text-right py-0.5">SPREAD</th>
            </tr>
          </thead>
          <tbody>
            {[
              { label: game.team1, prices: t1 },
              { label: game.team2, prices: t2 },
            ].map(({ label, prices }) => {
              const kBid = prices?.k_bid ?? 0;
              const kAsk = prices?.k_ask ?? 0;
              const pmBid = prices?.pm_bid ?? 0;
              const pmAsk = prices?.pm_ask ?? 0;
              const spread = prices?.spread ?? 0;
              const hasData = kBid > 0 || pmBid > 0;

              return (
                <tr key={label} className={`border-t border-[#1a1a2e]/40 ${spread >= 4 ? "bg-[#00ff88]/[0.04]" : ""}`}>
                  <td className="py-1 text-[#ff8c00] font-medium">{label}</td>
                  <td className="py-1 text-center text-[#00ff88]">{kBid || "—"}</td>
                  <td className="py-1 text-center text-[#ff6666]">{kAsk || "—"}</td>
                  <td className="py-1 text-center text-[#1a1a2e]">│</td>
                  <td className="py-1 text-center text-[#00ff88]">{pmBid || "—"}</td>
                  <td className="py-1 text-center text-[#ff6666]">{pmAsk || "—"}</td>
                  <td className="py-1 text-center text-[#1a1a2e]">│</td>
                  <td className="py-1 text-right">
                    <SpreadBadge cents={spread} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Visual price bars */}
      <div className="px-3 pb-2 space-y-1">
        <PriceBar
          kPrice={t1?.k_bid ?? 0}
          pmPrice={t1?.pm_bid ?? 0}
          label={game.team1}
        />
        <PriceBar
          kPrice={t2?.k_bid ?? 0}
          pmPrice={t2?.pm_bid ?? 0}
          label={game.team2}
        />
      </div>

      {/* Footer: Depth + Status */}
      <div className="px-3 py-1.5 border-t border-[#1a1a2e]/60 flex items-center justify-between text-[9px] font-mono">
        <span className="text-[#4a4a6a]">
          Depth:{" "}
          <span className={depthColor(game.k_depth ?? null)}>K:{game.k_depth ? fmtNum(game.k_depth) : "—"}</span>
          <span className="text-[#2a2a4a] mx-1">|</span>
          <span className={depthColor(game.pm_depth ?? null)}>PM:{game.pm_depth ? fmtNum(game.pm_depth) : "—"}</span>
        </span>
        <span className="text-[#4a4a6a]">
          {game.traded ? (
            <span className="text-[#00ff88] font-bold">TRADED ✓</span>
          ) : game.status === "Active" ? (
            <span className="text-[#ff8c00]">ACTIVE</span>
          ) : (
            <span className="text-[#3a3a5a]">WAITING</span>
          )}
        </span>
      </div>
    </div>
  );
}

export function LiveGamesTab({ data }: Props) {
  const { state } = data;
  const [showAll, setShowAll] = useState(false);

  const games = state?.mapped_games ?? [];

  // Separate live, active (with prices), and upcoming
  const { liveGames, activeGames, upcomingCount } = useMemo(() => {
    const live: MappedGame[] = [];
    const active: MappedGame[] = [];
    let upcoming = 0;

    for (const g of games) {
      if (g.game_status === "in") {
        live.push(g);
      } else if (g.status === "Active" && g.game_status !== "post") {
        active.push(g);
      } else if (g.game_status !== "post") {
        upcoming++;
      }
    }

    // Sort live by best spread descending (biggest arb opportunity first)
    live.sort((a, b) => b.best_spread - a.best_spread);
    active.sort((a, b) => b.best_spread - a.best_spread);

    return { liveGames: live, activeGames: active, upcomingCount: upcoming };
  }, [games]);

  const displayActive = showAll ? activeGames : activeGames.slice(0, 6);

  return (
    <div className="p-3 space-y-3">
      {/* Summary bar */}
      <div className="flex items-center gap-4 px-3 py-2 border border-[#1a1a2e] bg-[#0a0a0f]">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-2 h-2 bg-[#00ff88] animate-pulse" />
          <span className="text-[10px] font-mono font-bold text-[#00ff88] uppercase tracking-wider">
            {liveGames.length} LIVE
          </span>
        </div>
        <span className="text-[#1a1a2e]">│</span>
        <span className="text-[10px] font-mono text-[#ff8c00]">
          {activeGames.length} ACTIVE
        </span>
        <span className="text-[#1a1a2e]">│</span>
        <span className="text-[10px] font-mono text-[#4a4a6a]">
          {upcomingCount} UPCOMING
        </span>
        <span className="text-[#1a1a2e]">│</span>
        <span className="text-[10px] font-mono text-[#4a4a6a]">
          Refresh: 3s
        </span>
        {liveGames.some((g) => g.best_spread >= 4) && (
          <>
            <span className="text-[#1a1a2e]">│</span>
            <span className="text-[10px] font-mono font-bold text-[#00ff88] animate-pulse">
              ⚡ ARB OPPORTUNITIES DETECTED
            </span>
          </>
        )}
      </div>

      {/* Live Games Section */}
      {liveGames.length > 0 ? (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[9px] font-mono font-bold text-[#00ff88] uppercase tracking-widest">
              ● LIVE GAMES
            </span>
            <div className="flex-1 h-px bg-[#00ff88]/20" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2">
            {liveGames.map((g) => (
              <LiveGameCard key={g.cache_key} game={g} />
            ))}
          </div>
        </div>
      ) : (
        <div className="border border-[#1a1a2e] bg-[#0a0a0f] px-4 py-8 text-center">
          <span className="text-[#3a3a5a] font-mono text-[10px] uppercase tracking-wider">
            NO LIVE GAMES — WAITING FOR TIP-OFF
          </span>
        </div>
      )}

      {/* Active Games Section (pre-game with orderbooks) */}
      {activeGames.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[9px] font-mono font-bold text-[#ff8c00] uppercase tracking-widest">
              ▲ ACTIVE BOOKS
            </span>
            <div className="flex-1 h-px bg-[#ff8c00]/20" />
            <span className="text-[9px] font-mono text-[#4a4a6a]">
              {activeGames.length} games
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2">
            {displayActive.map((g) => (
              <LiveGameCard key={g.cache_key} game={g} />
            ))}
          </div>
          {activeGames.length > 6 && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="mt-2 w-full py-1.5 border border-[#1a1a2e] text-[9px] font-mono text-[#4a4a6a] hover:text-[#ff8c00] hover:border-[#ff8c00]/30 transition-colors uppercase tracking-wider"
            >
              {showAll ? "SHOW LESS" : `SHOW ALL ${activeGames.length} ACTIVE GAMES`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
