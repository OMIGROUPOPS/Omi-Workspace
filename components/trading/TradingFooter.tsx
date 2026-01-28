"use client";

import { BOT_SERVER_URL } from "@/lib/trading/config";

interface TradingFooterProps {
  mode: "paper" | "live";
  tradeCount: number;
}

export default function TradingFooter({ mode, tradeCount }: TradingFooterProps) {
  return (
    <footer className="flex-shrink-0 border-t border-[#151c28] px-4 py-1.5 flex items-center justify-between text-[9px] font-mono text-slate-700">
      <div className="flex items-center gap-3">
        <span>{BOT_SERVER_URL}</span>
        <span className="text-slate-800">|</span>
        <span>
          {mode === "live" ? (
            <span className="text-red-500">LIVE</span>
          ) : (
            <span className="text-blue-500">PAPER</span>
          )}
        </span>
        <span className="text-slate-800">|</span>
        <span className="tabular-nums">{tradeCount} trades</span>
      </div>
      <span className="text-slate-800">OMI Edge Terminal v3.0</span>
    </footer>
  );
}
