"use client";

import React, { useState, useEffect } from "react";
import type { TopTab, AlertInfo } from "./types";
import { Pulse } from "./shared/Pulse";
import { formatUptime, timeAgo } from "./helpers";

interface Props {
  hasData: boolean;
  isStale: boolean | string | undefined;
  fetchError: boolean;
  paused: boolean;
  setPaused: (v: boolean) => void;
  topTab: TopTab;
  setTopTab: (v: TopTab) => void;
  system: { ws_connected: boolean; uptime_seconds: number; last_scan_at: string; games_monitored: number } | undefined;
  alerts: AlertInfo[];
  fetchData: () => void;
}

const TABS: { key: TopTab; label: string }[] = [
  { key: "monitor", label: "Monitor" },
  { key: "pnl_history", label: "P&L" },
  { key: "depth", label: "Depth" },
  { key: "operations", label: "Operations" },
];

export function ArbDashboardHeader({
  hasData,
  isStale,
  fetchError,
  paused,
  setPaused,
  topTab,
  setTopTab,
  system,
  alerts,
  fetchData,
}: Props) {
  const [clock, setClock] = useState("");

  useEffect(() => {
    const update = () => {
      setClock(
        new Date().toLocaleTimeString("en-US", {
          timeZone: "America/New_York",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        })
      );
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="border-b border-gray-800 bg-[#0f0f0f]">
      {/* Alert banner */}
      {alerts.length > 0 && (
        <div className="px-4 py-1.5 flex items-center gap-3 overflow-x-auto bg-yellow-500/5 border-b border-yellow-500/20">
          {alerts.map((a, i) => (
            <span
              key={i}
              className={`text-[10px] font-medium whitespace-nowrap ${
                a.type === "error" ? "text-red-400" : a.type === "warning" ? "text-yellow-400" : "text-blue-400"
              }`}
            >
              {a.type === "error" ? "\u26A0" : a.type === "warning" ? "\u26A0" : "\u2139"} {a.message}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-bold text-white">Arb Monitor</h1>
          <div className="flex items-center gap-2">
            <Pulse active={!!hasData && !isStale && !fetchError} />
            <span className="text-xs text-gray-500">
              {fetchError
                ? "Connection error"
                : isStale
                ? "Stale"
                : hasData
                ? "Live"
                : "Connecting..."}
            </span>
          </div>
          {/* EST Clock */}
          <span className="text-xs font-mono text-gray-500 border-l border-gray-800 pl-3 ml-1">
            {clock} ET
          </span>
          {/* Uptime */}
          {system && (
            <span className="text-xs text-gray-600">
              {formatUptime(system.uptime_seconds)} up | {system.games_monitored} games
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Tabs */}
          <div className="flex items-center gap-0.5 rounded-lg bg-gray-800/50 p-0.5">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setTopTab(tab.key)}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                  topTab === tab.key
                    ? "bg-gray-700 text-white"
                    : "text-gray-500 hover:text-gray-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Controls */}
          <button
            onClick={() => setPaused(!paused)}
            className={`rounded px-2 py-1 text-[10px] font-medium ${
              paused ? "bg-yellow-500/20 text-yellow-400" : "bg-gray-800 text-gray-400 hover:text-gray-300"
            }`}
          >
            {paused ? "Paused" : "Pause"}
          </button>
          <button
            onClick={fetchData}
            className="rounded px-2 py-1 text-[10px] font-medium bg-gray-800 text-gray-400 hover:text-gray-300"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
}
