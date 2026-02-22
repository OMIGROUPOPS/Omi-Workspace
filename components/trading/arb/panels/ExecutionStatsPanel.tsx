"use client";

import React from "react";

interface Props {
  specs: any;
}

export function ExecutionStatsPanel({ specs }: Props) {
  const lat = specs?.latency || {};
  const tiers = specs?.tiers || {};
  const lastTrade = lat.last_trade || {};
  const rolling10 = lat.rolling_10 || {};
  const allTime = lat.all_time || {};

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
        Execution Stats
      </h3>

      {/* Latency */}
      <div className="mb-4">
        <p className="text-[10px] text-gray-500 uppercase mb-2">Latency</p>
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded bg-gray-800/50 p-2">
            <span className="text-[10px] text-gray-500 block">Last Trade</span>
            {lastTrade.total_ms ? (
              <>
                <span className="text-sm text-white font-mono font-bold">{lastTrade.total_ms}ms</span>
                <span className="text-[10px] text-gray-500 block">
                  K:{lastTrade.k_ms}ms PM:{lastTrade.pm_ms}ms
                </span>
                <span className="text-[10px] text-gray-600 block">{lastTrade.team}</span>
              </>
            ) : <span className="text-sm text-gray-600">-</span>}
          </div>
          <div className="rounded bg-gray-800/50 p-2">
            <span className="text-[10px] text-gray-500 block">Avg (Last 10)</span>
            {rolling10.avg_total_ms ? (
              <>
                <span className="text-sm text-white font-mono font-bold">{rolling10.avg_total_ms}ms</span>
                <span className="text-[10px] text-gray-500 block">
                  K:{rolling10.avg_k_ms}ms PM:{rolling10.avg_pm_ms}ms
                </span>
              </>
            ) : <span className="text-sm text-gray-600">-</span>}
          </div>
          <div className="rounded bg-gray-800/50 p-2">
            <span className="text-[10px] text-gray-500 block">All Time</span>
            {allTime.fastest_ms ? (
              <>
                <span className="text-sm text-white font-mono">
                  {allTime.fastest_ms}-{allTime.slowest_ms}ms
                </span>
                <span className="text-[10px] text-gray-500 block">
                  SDK: {allTime.sdk_success_rate}%
                </span>
              </>
            ) : <span className="text-sm text-gray-600">-</span>}
          </div>
        </div>
      </div>

      {/* Tier breakdown */}
      <div>
        <p className="text-[10px] text-gray-500 uppercase mb-2">Tier Breakdown</p>
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div>
            <span className="text-gray-500">Total Filled</span>
            <p className="text-white font-bold">{tiers.total_filled ?? 0}</p>
          </div>
          <div>
            <span className="text-gray-500">SUCCESS</span>
            <p className="text-emerald-400 font-bold">{tiers.success_count ?? 0}</p>
          </div>
          <div>
            <span className="text-gray-500">TIER1 Hedge</span>
            <p className="text-emerald-400 font-bold">{tiers.tier1_count ?? 0}</p>
          </div>
          <div>
            <span className="text-gray-500">TIER2 Exit</span>
            <p className="text-yellow-400 font-bold">{tiers.tier2_count ?? 0}</p>
          </div>
          <div>
            <span className="text-gray-500">TIER3A Hold</span>
            <p className="text-yellow-400 font-bold">{tiers.tier3a_count ?? 0}</p>
          </div>
          <div>
            <span className="text-gray-500">Opp Hedge</span>
            <p className="text-blue-400 font-bold">{tiers.opp_hedge_count ?? 0}</p>
          </div>
          <div>
            <span className="text-gray-500">K Fail Rate</span>
            <p className="text-red-400 font-bold">{tiers.kalshi_fail_rate ?? 0}%</p>
          </div>
          <div>
            <span className="text-gray-500">Dir Win Rate</span>
            <p className="text-emerald-400 font-bold">{tiers.directional_win_rate ?? 0}%</p>
          </div>
        </div>
      </div>
    </div>
  );
}
