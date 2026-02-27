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
  { key: "monitor", label: "MONITOR" },
  { key: "pnl_history", label: "P&L" },
  { key: "depth", label: "DEPTH" },
  { key: "operations", label: "OPS" },
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

  const isLive = !!hasData && !isStale && !fetchError;

  return (
    <div className="border-b border-[#1a1a2e] bg-black">
      {/* Top amber accent line */}
      <div className="h-[2px] bg-[#ff8c00] w-full" />

      {/* Alert banner */}
      {alerts.length > 0 && (
        <div className="px-4 py-1 flex items-center gap-3 overflow-x-auto bg-[#ff8c00]/10 border-b border-[#ff8c00]/20">
          {alerts.map((a, i) => (
            <span
              key={i}
              className={`text-[9px] font-mono uppercase tracking-wider whitespace-nowrap ${
                a.type === "error" ? "text-[#ff3333]" : a.type === "warning" ? "text-[#ff8c00]" : "text-[#00bfff]"
              }`}
            >
              {a.type === "error" ? "■ ERR:" : a.type === "warning" ? "▲ WARN:" : "● INFO:"} {a.message}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between px-4 py-2">
        {/* Left: Title + Status */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono font-bold text-[#ff8c00] uppercase tracking-widest">
              OMI ARB TERMINAL
            </span>
            <span className="text-[#1a1a2e] font-mono">|</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Pulse active={isLive} />
            <span className={`text-[9px] font-mono uppercase tracking-wider ${isLive ? "text-[#ff8c00]" : "text-[#ff3333]"}`}>
              {fetchError
                ? "CONN ERR"
                : isStale
                ? "STALE"
                : hasData
                ? "LIVE"
                : "CONNECTING"}
            </span>
          </div>

          {/* Clock */}
          <span className="text-[11px] font-mono text-[#00ff88] border-l border-[#1a1a2e] pl-4 ml-1">
            {clock} <span className="text-[#3a3a5a]">ET</span>
          </span>

          {/* System info */}
          {system && (
            <span className="text-[9px] font-mono text-[#4a4a6a] border-l border-[#1a1a2e] pl-3">
              UP: {formatUptime(system.uptime_seconds)}
              <span className="mx-1.5 text-[#1a1a2e]">|</span>
              {system.games_monitored} GAMES
            </span>
          )}
        </div>

        {/* Right: Tabs + Controls */}
        <div className="flex items-center gap-0">
          {/* Tab bar */}
          <div className="flex items-center border-l border-[#1a1a2e]">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setTopTab(tab.key)}
                className={`px-3 py-2 text-[9px] font-mono tracking-wider border-b-2 transition-colors ${
                  topTab === tab.key
                    ? "text-[#ff8c00] border-[#ff8c00]"
                    : "text-[#4a4a6a] border-transparent hover:text-[#ff8c00]/70"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Controls */}
          <div className="flex items-center gap-1 ml-3 border-l border-[#1a1a2e] pl-3">
            <button
              onClick={() => setPaused(!paused)}
              className={`rounded-none px-2 py-1 text-[9px] font-mono border transition-colors ${
                paused
                  ? "bg-[#ff8c00]/20 text-[#ff8c00] border-[#ff8c00]/40"
                  : "bg-transparent text-[#4a4a6a] border-[#1a1a2e] hover:text-[#00bfff] hover:border-[#00bfff]/40"
              }`}
            >
              {paused ? "PAUSED" : "PAUSE"}
            </button>
            <button
              onClick={fetchData}
              className="rounded-none px-2 py-1 text-[9px] font-mono border border-[#1a1a2e] text-[#4a4a6a] hover:text-[#00bfff] hover:border-[#00bfff]/40 transition-colors"
            >
              REFRESH
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
