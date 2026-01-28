"use client";

import type { Trade, TradeStatusDisplay } from "@/lib/trading/types";

export function getTradeStatus(trade: Trade): TradeStatusDisplay {
  if (trade.status === "PAPER" || trade.execution_mode === "paper")
    return { text: "PAPER", color: "text-amber-400", bg: "bg-amber-500/8" };
  if (trade.status === "SUCCESS")
    return { text: "FILLED", color: "text-emerald-400", bg: "bg-emerald-500/8" };
  if (trade.status === "NO_FILL")
    return { text: "NO FILL", color: "text-slate-500", bg: "bg-slate-500/8" };
  if (trade.status === "UNHEDGED")
    return { text: "UNHEDGED", color: "text-red-400", bg: "bg-red-500/8" };
  if (trade.status === "FAILED")
    return { text: "FAILED", color: "text-red-400", bg: "bg-red-500/8" };
  return { text: trade.status || "\u2014", color: "text-orange-400", bg: "bg-orange-500/8" };
}

export default function StatusBadge({ trade }: { trade: Trade }) {
  const st = getTradeStatus(trade);
  return (
    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${st.color} ${st.bg}`}>
      {st.text}
    </span>
  );
}
