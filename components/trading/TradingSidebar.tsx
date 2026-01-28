"use client";

import type { ActiveTab, BotStatus } from "@/lib/trading/types";

interface TradingSidebarProps {
  mode: "paper" | "live";
  botState: BotStatus["bot_state"];
  isRunning: boolean;
  isLoading: boolean;
  balance: number | null;
  pmBalance: number;
  combinedBalance: number;
  stats: {
    liveTrades: { length: number };
    paperTrades: { length: number };
    failedTrades: { length: number };
    fillRate: number;
    lastSuccessfulTrade?: { timestamp: string };
  };
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  onStart: () => void;
  onStop: () => void;
  onModeChange: (mode: "paper" | "live") => void;
  onClearData: () => void;
}

const TABS: { key: ActiveTab; label: string }[] = [
  { key: "dashboard", label: "Dashboard" },
  { key: "trades", label: "Trades" },
  { key: "research", label: "Research" },
  { key: "logs", label: "Logs" },
];

export default function TradingSidebar({
  mode,
  botState,
  isRunning,
  isLoading,
  balance,
  pmBalance,
  combinedBalance,
  stats,
  activeTab,
  onTabChange,
  onStart,
  onStop,
  onModeChange,
  onClearData,
}: TradingSidebarProps) {
  return (
    <div className="w-[220px] flex-shrink-0 flex flex-col gap-2 overflow-y-auto scrollbar-thin pr-1">
      {/* Tab Navigation */}
      <div className="panel rounded-lg overflow-hidden">
        <div className="p-1.5 flex flex-col gap-0.5">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => onTabChange(tab.key)}
              className={`w-full px-3 py-2 text-left text-[11px] font-bold tracking-wider rounded transition-all
                ${activeTab === tab.key
                  ? "bg-slate-700/50 text-slate-100"
                  : "text-slate-600 hover:text-slate-400 hover:bg-slate-800/30"
                }`}
            >
              {tab.label.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Bot Controls */}
      <div className="panel rounded-lg overflow-hidden">
        <div className="panel-header px-3 py-2">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Controls</span>
        </div>
        <div className="p-3 space-y-3">
          <div>
            <div className="text-[9px] text-slate-600 mb-1.5 uppercase tracking-widest">Execution Mode</div>
            <div className="flex rounded overflow-hidden border border-slate-700/50">
              <button
                onClick={() => onModeChange("paper")}
                disabled={isLoading || isRunning}
                className={`flex-1 py-2 text-[11px] font-bold tracking-wider transition-all
                  ${mode === "paper" ? "bg-blue-500/15 text-blue-400" : "bg-slate-800/50 text-slate-600 hover:text-slate-400"}
                  disabled:opacity-30 disabled:cursor-not-allowed`}
              >
                PAPER
              </button>
              <button
                onClick={() => onModeChange("live")}
                disabled={isLoading || isRunning}
                className={`flex-1 py-2 text-[11px] font-bold tracking-wider transition-all
                  ${mode === "live" ? "bg-red-500/15 text-red-400" : "bg-slate-800/50 text-slate-600 hover:text-slate-400"}
                  disabled:opacity-30 disabled:cursor-not-allowed`}
              >
                LIVE
              </button>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={onStart}
              disabled={isLoading || isRunning || botState === "starting"}
              className={`flex-1 py-2.5 rounded text-[11px] font-bold tracking-wider transition-all
                border disabled:opacity-20 disabled:cursor-not-allowed
                ${isRunning
                  ? "border-slate-700 text-slate-600"
                  : "border-emerald-500/30 text-emerald-400 bg-emerald-500/8 hover:bg-emerald-500/15 glow-green"
                }`}
            >
              {botState === "starting" ? "STARTING" : "START"}
            </button>
            <button
              onClick={onStop}
              disabled={isLoading || botState === "stopped" || botState === "stopping"}
              className={`flex-1 py-2.5 rounded text-[11px] font-bold tracking-wider transition-all
                border disabled:opacity-20 disabled:cursor-not-allowed
                ${botState === "stopped"
                  ? "border-slate-700 text-slate-600"
                  : "border-red-500/30 text-red-400 bg-red-500/8 hover:bg-red-500/15 glow-red"
                }`}
            >
              {botState === "stopping" ? "STOPPING" : "STOP"}
            </button>
          </div>
        </div>
      </div>

      {/* Balances */}
      <div className="panel rounded-lg overflow-hidden">
        <div className="panel-header px-3 py-2">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Balances</span>
        </div>
        <div className="p-3 space-y-2">
          <div className="flex items-center justify-between py-1.5">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-4 rounded-full bg-cyan-500/60" />
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">Kalshi</span>
            </div>
            <span className="font-mono text-base font-bold text-cyan-400 tabular-nums">
              {balance !== null ? `$${balance.toFixed(2)}` : "\u2014"}
            </span>
          </div>
          <div className="flex items-center justify-between py-1.5">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-4 rounded-full bg-violet-500/60" />
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">PM US</span>
            </div>
            <span className="font-mono text-base font-bold text-violet-400 tabular-nums">
              ${pmBalance.toFixed(2)}
            </span>
          </div>
          <div className="border-t border-slate-800" />
          <div className="flex items-center justify-between py-1">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider">Combined</span>
            <span className="font-mono text-lg font-bold text-slate-100 tabular-nums">
              ${combinedBalance.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Session Stats */}
      <div className="panel rounded-lg overflow-hidden">
        <div className="panel-header px-3 py-2 flex items-center justify-between">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Session</span>
          <button
            onClick={onClearData}
            className="text-[9px] text-red-400/40 hover:text-red-400 font-mono tracking-wider transition-colors"
          >
            CLR
          </button>
        </div>
        <div className="p-3 space-y-1.5">
          {[
            { label: "Live Fills", value: stats.liveTrades.length, color: "text-emerald-400" },
            { label: "Paper", value: stats.paperTrades.length, color: "text-amber-400" },
            { label: "No Fill", value: stats.failedTrades.length, color: "text-slate-500" },
            {
              label: "Fill Rate",
              value: `${stats.fillRate.toFixed(0)}%`,
              color: stats.fillRate >= 50 ? "text-emerald-400" : stats.fillRate >= 25 ? "text-amber-400" : "text-slate-500",
            },
            {
              label: "Last Fill",
              value: stats.lastSuccessfulTrade
                ? new Date(stats.lastSuccessfulTrade.timestamp).toLocaleTimeString("en-US", { hour12: false })
                : "\u2014",
              color: "text-slate-300",
            },
          ].map(({ label, value, color }) => (
            <div key={label} className="flex items-center justify-between py-1 text-[11px]">
              <span className="text-slate-600">{label}</span>
              <span className={`font-mono tabular-nums ${color}`}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
