"use client";

import { useState, useMemo } from "react";
import type { MarketData } from "@/lib/trading/types";
import Panel from "../shared/Panel";

interface MarketsTabProps {
  marketData: MarketData | null;
}

type MarketFilter = "all" | "matched" | "unmatched";

const SPORTS = ["NBA", "NHL", "MLB", "NFL"];

export default function MarketsTab({ marketData }: MarketsTabProps) {
  const [marketFilter, setMarketFilter] = useState<MarketFilter>("all");

  const filteredKalshiGames = useMemo(() => {
    if (!marketData?.kalshi_games) return [];
    switch (marketFilter) {
      case "matched":
        return marketData.kalshi_games.filter((g) => g.matched);
      case "unmatched":
        return marketData.kalshi_games.filter((g) => !g.matched);
      default:
        return marketData.kalshi_games;
    }
  }, [marketData?.kalshi_games, marketFilter]);

  const getMatchRateColor = (rate: number) => {
    if (rate >= 50) return "text-emerald-400";
    if (rate >= 25) return "text-amber-400";
    return "text-slate-500";
  };

  const getStatusBadge = (status: "ARB" | "CLOSE" | "NO_EDGE") => {
    switch (status) {
      case "ARB":
        return (
          <span className="px-1.5 py-0.5 text-[9px] font-bold bg-emerald-500/20 text-emerald-400 rounded">
            ARB
          </span>
        );
      case "CLOSE":
        return (
          <span className="px-1.5 py-0.5 text-[9px] font-bold bg-amber-500/20 text-amber-400 rounded">
            CLOSE
          </span>
        );
      default:
        return (
          <span className="px-1.5 py-0.5 text-[9px] font-bold bg-slate-700/50 text-slate-500 rounded">
            NO EDGE
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col gap-2 overflow-y-auto scrollbar-thin h-full">
      {/* Match Rate Cards */}
      <div className="grid grid-cols-4 gap-2">
        {SPORTS.map((sport) => {
          const stats = marketData?.match_stats?.[sport];
          const matched = stats?.matched ?? 0;
          const total = stats?.total ?? 0;
          const rate = stats?.rate ?? 0;

          return (
            <div key={sport} className="panel rounded-lg p-3">
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">
                {sport}
              </div>
              <div className="font-mono text-lg font-bold text-slate-200 tabular-nums">
                {matched}/{total}
              </div>
              <div className={`font-mono text-sm tabular-nums ${getMatchRateColor(rate)}`}>
                {total > 0 ? `${rate.toFixed(0)}%` : "--"}
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Spreads Table */}
      <Panel
        title="Live Spreads"
        headerRight={
          <span className="text-[10px] text-slate-500 font-mono tabular-nums">
            {marketData?.spreads?.length ?? 0} matched markets
          </span>
        }
      >
        <div className="overflow-x-auto">
          <table className="w-full text-[11px]">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left px-3 py-2 text-slate-500 font-medium">Sport</th>
                <th className="text-left px-3 py-2 text-slate-500 font-medium">Game</th>
                <th className="text-left px-3 py-2 text-slate-500 font-medium">Team</th>
                <th className="text-right px-3 py-2 text-slate-500 font-medium">K Bid</th>
                <th className="text-right px-3 py-2 text-slate-500 font-medium">PM Ask</th>
                <th className="text-right px-3 py-2 text-slate-500 font-medium">Spread</th>
                <th className="text-right px-3 py-2 text-slate-500 font-medium">ROI</th>
                <th className="text-center px-3 py-2 text-slate-500 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {marketData?.spreads?.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-3 py-8 text-center text-slate-600">
                    No matched markets found
                  </td>
                </tr>
              )}
              {marketData?.spreads?.map((spread, idx) => (
                <tr key={`${spread.game}-${spread.team}-${idx}`} className="table-row border-b border-slate-800/50">
                  <td className="px-3 py-2 text-slate-400 font-medium">{spread.sport}</td>
                  <td className="px-3 py-2 text-slate-300 font-mono">{spread.game}</td>
                  <td className="px-3 py-2 text-slate-200 font-bold">{spread.team}</td>
                  <td className="px-3 py-2 text-right font-mono text-cyan-400 tabular-nums">
                    {spread.k_bid}c
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-violet-400 tabular-nums">
                    {spread.pm_ask}c
                  </td>
                  <td
                    className={`px-3 py-2 text-right font-mono font-bold tabular-nums ${
                      spread.spread > 0 ? "text-emerald-400" : spread.spread < 0 ? "text-red-400" : "text-slate-500"
                    }`}
                  >
                    {spread.spread > 0 ? "+" : ""}
                    {spread.spread}c
                  </td>
                  <td
                    className={`px-3 py-2 text-right font-mono font-bold tabular-nums ${
                      spread.roi >= 5 ? "text-emerald-400" : spread.roi >= 2 ? "text-amber-400" : "text-slate-500"
                    }`}
                  >
                    {spread.roi.toFixed(1)}%
                  </td>
                  <td className="px-3 py-2 text-center">{getStatusBadge(spread.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* All Kalshi Markets Table */}
      <Panel
        title="All Kalshi Markets"
        headerRight={
          <div className="flex gap-1">
            {(["all", "matched", "unmatched"] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => setMarketFilter(filter)}
                className={`px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded transition-colors ${
                  marketFilter === filter
                    ? "bg-slate-700 text-slate-200"
                    : "text-slate-600 hover:text-slate-400"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        }
      >
        <div className="overflow-x-auto max-h-[300px] overflow-y-auto scrollbar-thin">
          <table className="w-full text-[11px]">
            <thead className="sticky top-0 bg-[#0d1320]">
              <tr className="border-b border-slate-800">
                <th className="text-left px-3 py-2 text-slate-500 font-medium">Sport</th>
                <th className="text-left px-3 py-2 text-slate-500 font-medium">Game/Event</th>
                <th className="text-left px-3 py-2 text-slate-500 font-medium">Kalshi Ticker</th>
                <th className="text-left px-3 py-2 text-slate-500 font-medium">PM Slug</th>
                <th className="text-center px-3 py-2 text-slate-500 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredKalshiGames.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-3 py-8 text-center text-slate-600">
                    No markets found
                  </td>
                </tr>
              )}
              {filteredKalshiGames.map((market, idx) => (
                <tr key={`${market.game}-${market.team}-${idx}`} className="table-row border-b border-slate-800/50">
                  <td className="px-3 py-2 text-slate-400 font-medium">{market.sport}</td>
                  <td className="px-3 py-2 text-slate-300 font-mono">
                    {market.game}-{market.team}
                  </td>
                  <td className="px-3 py-2 text-cyan-400 font-mono text-[10px]">
                    {market.ticker || "--"}
                  </td>
                  <td className="px-3 py-2 text-violet-400 font-mono text-[10px]">
                    {market.pm_slug || "--"}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {market.matched ? (
                      <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" title="Matched" />
                    ) : (
                      <span className="inline-block w-2 h-2 rounded-full bg-red-500/60" title="Unmatched" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Timestamp */}
      {marketData?.timestamp && (
        <div className="text-[10px] text-slate-600 text-center font-mono">
          Last updated: {new Date(marketData.timestamp).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
