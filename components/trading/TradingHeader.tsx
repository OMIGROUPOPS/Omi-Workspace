"use client";

import type { BotStatus, ConnectionStatus, ScanInfo } from "@/lib/trading/types";

interface TradingHeaderProps {
  currentTime: Date;
  mode: "paper" | "live";
  botState: BotStatus["bot_state"];
  isRunning: boolean;
  connectionStatus: ConnectionStatus;
  scanInfo: ScanInfo;
  fillRate: number;
  uptime: string;
  latency: number | null;
}

export default function TradingHeader({
  currentTime,
  mode,
  botState,
  isRunning,
  connectionStatus,
  scanInfo,
  fillRate,
  uptime,
  latency,
}: TradingHeaderProps) {
  const connColor =
    connectionStatus === "connected"
      ? "text-emerald-400"
      : connectionStatus === "connecting"
      ? "text-amber-400"
      : "text-red-400";
  const connDot =
    connectionStatus === "connected"
      ? "bg-emerald-400"
      : connectionStatus === "connecting"
      ? "bg-amber-400"
      : "bg-red-400";

  const getMarketStatus = () => {
    const estHour = currentTime.getUTCHours() - 5;
    const h = estHour < 0 ? estHour + 24 : estHour;
    if (h >= 18 && h <= 23) return { label: "PRIME", color: "text-emerald-400", dot: "bg-emerald-400" };
    if (h >= 11 && h < 18) return { label: "ACTIVE", color: "text-cyan-400", dot: "bg-cyan-400" };
    return { label: "OFF-PEAK", color: "text-slate-500", dot: "bg-slate-500" };
  };
  const marketStatus = getMarketStatus();

  return (
    <header className="flex-shrink-0 border-b border-[#151c28] bg-gradient-to-r from-[#0a0f18] via-[#0c1119] to-[#0a0f18]">
      {isRunning && scanInfo.isScanning && (
        <div className="h-[2px] w-full bg-[#0a0f18] overflow-hidden relative">
          <div className="scan-sweep absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-cyan-500/60 to-transparent" />
        </div>
      )}

      <div className="flex items-center justify-between px-4 py-2">
        {/* Left: Logo + version */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div
              className={`w-8 h-8 rounded flex items-center justify-center font-black text-[10px] tracking-tight
              ${isRunning
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 heartbeat"
                : "bg-slate-800 text-slate-500 border border-slate-700"
              }`}
            >
              OMI
            </div>
            <div className="leading-none">
              <div className="text-sm font-bold tracking-wide text-slate-100">EDGE</div>
              <div className="text-[9px] text-slate-600 font-mono tracking-widest">ARB EXECUTOR v7</div>
            </div>
          </div>

          <div className="w-px h-7 bg-slate-800" />

          <div
            className={`px-3 py-1 rounded text-[10px] font-bold tracking-widest
            ${mode === "live"
              ? "bg-red-500/15 text-red-400 border border-red-500/30"
              : "bg-blue-500/15 text-blue-400 border border-blue-500/30"
            }`}
          >
            {mode === "live" ? "LIVE TRADING" : "PAPER MODE"}
          </div>
        </div>

        {/* Center: Real-time metrics */}
        <div className="flex items-center gap-5 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="text-[9px] text-slate-600 uppercase tracking-widest">EST</span>
            <span className="font-mono text-slate-200 tabular-nums text-sm tracking-tight">
              {currentTime.toLocaleTimeString("en-US", { hour12: false, timeZone: "America/New_York" })}
            </span>
          </div>

          <div className="w-px h-5 bg-slate-800" />

          <div className="flex items-center gap-1.5">
            <div className={`w-1.5 h-1.5 rounded-full ${marketStatus.dot}`} />
            <span className={`font-mono text-[10px] tracking-wider ${marketStatus.color}`}>
              {marketStatus.label}
            </span>
          </div>

          <div className="w-px h-5 bg-slate-800" />

          <div className="flex items-center gap-3 font-mono">
            <div className="flex items-center gap-1.5">
              <span className="text-slate-600">SCN</span>
              <span className="text-slate-300 tabular-nums">{scanInfo.scanNumber}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-600">GMS</span>
              <span className="text-slate-300 tabular-nums">{scanInfo.gamesFound}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-600">ARB</span>
              <span className={`tabular-nums ${scanInfo.arbsFound > 0 ? "text-emerald-400" : "text-slate-500"}`}>
                {scanInfo.arbsFound}
              </span>
            </div>
          </div>

          <div className="w-px h-5 bg-slate-800" />

          <div className="flex items-center gap-1.5 font-mono">
            <span className="text-slate-600">FILL</span>
            <span className={`tabular-nums ${fillRate >= 50 ? "text-emerald-400" : fillRate >= 25 ? "text-amber-400" : "text-slate-500"}`}>
              {fillRate.toFixed(0)}%
            </span>
          </div>

          <div className="flex items-center gap-1.5 font-mono">
            <span className="text-slate-600">UP</span>
            <span className="text-slate-300 tabular-nums">{uptime}</span>
          </div>
        </div>

        {/* Right: Connection status */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 font-mono text-[10px]">
            <div className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${connDot} ${connectionStatus === "connecting" ? "animate-pulse" : ""}`} />
              <span className="text-slate-500">KSI</span>
              <span className={connColor}>{latency !== null ? `${latency}ms` : "\u2014"}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${connDot}`} />
              <span className="text-slate-500">PMU</span>
              <span className={connColor}>{latency !== null ? `${Math.round(latency * 1.2)}ms` : "\u2014"}</span>
            </div>
          </div>

          <div className="w-px h-5 bg-slate-800" />

          <div className="flex items-center gap-1.5">
            <div
              className={`w-2 h-2 rounded-full
              ${botState === "running" ? "bg-emerald-400 heartbeat" :
                botState === "error" ? "bg-red-400" :
                botState === "starting" || botState === "stopping" ? "bg-amber-400 animate-pulse" : "bg-slate-600"}`}
            />
            <span
              className={`text-[10px] font-bold font-mono tracking-wider
              ${botState === "running" ? "text-emerald-400" :
                botState === "error" ? "text-red-400" :
                botState === "starting" || botState === "stopping" ? "text-amber-400" : "text-slate-500"}`}
            >
              {botState.toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
