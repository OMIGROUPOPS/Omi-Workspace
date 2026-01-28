"use client";

import { useState, useMemo } from "react";
import type { MarketData, VolumeHistoryPoint } from "@/lib/trading/types";
import Panel from "../shared/Panel";

interface MarketsTabProps {
  marketData: MarketData | null;
}

type MarketFilter = "all" | "matched" | "unmatched";

const SPORTS = ["NBA", "NHL", "MLB", "NFL"];

function formatVolume(vol: number): string {
  if (vol >= 1000000) return `${(vol / 1000000).toFixed(1)}M`;
  if (vol >= 1000) return `${(vol / 1000).toFixed(1)}K`;
  return vol.toFixed(0);
}

function VolumeTrendsChart({ history }: { history: VolumeHistoryPoint[] }) {
  if (!history || history.length < 2) {
    return (
      <div className="h-[120px] flex items-center justify-center text-slate-600 text-[11px]">
        Collecting volume data...
      </div>
    );
  }

  const maxTotal = Math.max(...history.map((h) => h.total), 1);
  const width = 320;
  const height = 120;
  const padding = { top: 10, right: 10, bottom: 20, left: 10 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const points = history.map((h, i) => ({
    x: padding.left + (i / (history.length - 1)) * chartWidth,
    yKalshi: padding.top + chartHeight - (h.kalshi / maxTotal) * chartHeight,
    yPm: padding.top + chartHeight - (h.pm / maxTotal) * chartHeight,
    yTotal: padding.top + chartHeight - (h.total / maxTotal) * chartHeight,
  }));

  const kalshiPath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.yKalshi}`).join(" ");
  const pmPath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.yPm}`).join(" ");

  return (
    <svg width={width} height={height} className="overflow-visible">
      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
        <line
          key={ratio}
          x1={padding.left}
          y1={padding.top + chartHeight * (1 - ratio)}
          x2={width - padding.right}
          y2={padding.top + chartHeight * (1 - ratio)}
          stroke="#1e293b"
          strokeWidth={1}
        />
      ))}

      {/* Kalshi line */}
      <path d={kalshiPath} fill="none" stroke="#22d3ee" strokeWidth={2} strokeOpacity={0.8} />

      {/* PM line */}
      <path d={pmPath} fill="none" stroke="#a78bfa" strokeWidth={2} strokeOpacity={0.8} />

      {/* Time labels */}
      <text x={padding.left} y={height - 2} fill="#64748b" fontSize={9} textAnchor="start">
        {history.length > 0 ? new Date(history[0].timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
      </text>
      <text x={width - padding.right} y={height - 2} fill="#64748b" fontSize={9} textAnchor="end">
        {history.length > 0 ? new Date(history[history.length - 1].timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
      </text>

      {/* Legend */}
      <circle cx={padding.left + 5} cy={padding.top + 5} r={3} fill="#22d3ee" />
      <text x={padding.left + 12} y={padding.top + 8} fill="#64748b" fontSize={8}>K</text>
      <circle cx={padding.left + 30} cy={padding.top + 5} r={3} fill="#a78bfa" />
      <text x={padding.left + 37} y={padding.top + 8} fill="#64748b" fontSize={8}>PM</text>
    </svg>
  );
}

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

      {/* Volume Section */}
      <div className="grid grid-cols-2 gap-2">
        {/* Volume by Sport */}
        <Panel
          title="Volume by Sport"
          headerRight={
            <span className="text-[10px] text-slate-500 font-mono tabular-nums">
              Total: {formatVolume(marketData?.total_volume?.total ?? 0)}
            </span>
          }
        >
          <div className="p-3">
            <div className="space-y-3">
              {SPORTS.map((sport) => {
                const volume = marketData?.volume_by_sport?.[sport];
                const kalshiVol = volume?.kalshi ?? 0;
                const pmVol = volume?.pm ?? 0;
                const maxVol = Math.max(
                  ...SPORTS.map((s) => (marketData?.volume_by_sport?.[s]?.total ?? 0)),
                  1
                );
                const kalshiWidth = maxVol > 0 ? (kalshiVol / maxVol) * 100 : 0;
                const pmWidth = maxVol > 0 ? (pmVol / maxVol) * 100 : 0;

                return (
                  <div key={sport}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                        {sport}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono tabular-nums">
                        {formatVolume(kalshiVol + pmVol)}
                      </span>
                    </div>
                    <div className="flex gap-0.5 h-4">
                      <div
                        className="bg-cyan-500/60 rounded-l transition-all"
                        style={{ width: `${kalshiWidth}%` }}
                        title={`Kalshi: ${formatVolume(kalshiVol)}`}
                      />
                      <div
                        className="bg-violet-500/60 rounded-r transition-all"
                        style={{ width: `${pmWidth}%` }}
                        title={`PM US: ${formatVolume(pmVol)}`}
                      />
                      {kalshiWidth === 0 && pmWidth === 0 && (
                        <div className="bg-slate-800 rounded flex-1" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="flex gap-4 mt-3 pt-2 border-t border-slate-800">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-cyan-500/60" />
                <span className="text-[9px] text-slate-500">Kalshi</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-violet-500/60" />
                <span className="text-[9px] text-slate-500">PM US</span>
              </div>
            </div>
          </div>
        </Panel>

        {/* Volume Trends */}
        <Panel
          title="Volume Trends (24H)"
          headerRight={
            <div className="flex gap-2 text-[10px] font-mono tabular-nums">
              <span className="text-cyan-400">{formatVolume(marketData?.total_volume?.kalshi ?? 0)}</span>
              <span className="text-slate-600">/</span>
              <span className="text-violet-400">{formatVolume(marketData?.total_volume?.pm ?? 0)}</span>
            </div>
          }
        >
          <div className="p-3">
            <VolumeTrendsChart history={marketData?.volume_history ?? []} />
          </div>
        </Panel>
      </div>

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
