"use client";

import { useMemo, useState } from "react";
import type { Trade, Position, PnLPeriod, FullAnalytics } from "@/lib/trading/types";
import PnLChart from "../charts/PnLChart";
import DrawdownChart from "../charts/DrawdownChart";
import MetricCard from "../shared/MetricCard";
import Panel from "../shared/Panel";

interface DashboardTabProps {
  trades: Trade[];
  positions: Position[];
  profitHistory: number[];
  analytics: FullAnalytics;
}

export default function DashboardTab({
  trades,
  positions,
  profitHistory,
  analytics,
}: DashboardTabProps) {
  const [pnlPeriod, setPnlPeriod] = useState<PnLPeriod>("ALL");

  const filteredProfitHistory = useMemo(() => {
    if (pnlPeriod === "ALL") return profitHistory;
    const now = Date.now();
    const periodMs = { "1H": 3600000, "6H": 21600000, "24H": 86400000 }[pnlPeriod];
    // profitHistory is an array of cumulative P&L values, not timestamped,
    // so we slice based on approximate data density
    const keepRatio = Math.min(periodMs / (3600000 * 24), 1);
    const keepCount = Math.max(2, Math.floor(profitHistory.length * keepRatio));
    return profitHistory.slice(-keepCount);
  }, [profitHistory, pnlPeriod]);

  const exposureDeployed = positions.reduce(
    (sum, p) => sum + Math.abs((p.market_exposure || 0) / 100),
    0
  );

  return (
    <div className="flex flex-col gap-2 overflow-y-auto scrollbar-thin h-full">
      {/* Metric Cards */}
      <div className="grid grid-cols-4 gap-2">
        <MetricCard
          label="Total P&L"
          value={`${analytics.totalPnL >= 0 ? "+" : ""}$${analytics.totalPnL.toFixed(2)}`}
          color={analytics.totalPnL >= 0 ? "text-emerald-400" : "text-red-400"}
          sparkData={profitHistory}
          sparkColor={analytics.totalPnL >= 0 ? "#10b981" : "#ef4444"}
        />
        <MetricCard
          label="Win Rate"
          value={`${analytics.winRate.toFixed(1)}%`}
          color={analytics.winRate >= 60 ? "text-emerald-400" : analytics.winRate >= 40 ? "text-amber-400" : "text-red-400"}
        />
        <MetricCard
          label="Avg Profit"
          value={`$${analytics.avgProfit.toFixed(2)}`}
          color={analytics.avgProfit >= 0 ? "text-emerald-400" : "text-red-400"}
        />
        <MetricCard
          label="Max Drawdown"
          value={`${analytics.maxDrawdown.toFixed(1)}%`}
          color={analytics.maxDrawdown > -10 ? "text-amber-400" : "text-red-400"}
        />
      </div>

      {/* P&L Chart */}
      <Panel
        title="Profit & Loss"
        headerRight={
          <span className={`font-mono text-sm font-bold tabular-nums ${analytics.totalPnL >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            {analytics.totalPnL >= 0 ? "+" : ""}${analytics.totalPnL.toFixed(2)}
          </span>
        }
      >
        <div className="px-3 py-2 flex justify-center">
          <PnLChart
            data={filteredProfitHistory}
            width={700}
            height={150}
            period={pnlPeriod}
            onPeriodChange={setPnlPeriod}
            showPeriodSelector
          />
        </div>
      </Panel>

      {/* Exposure Summary */}
      <Panel title="Exposure">
        <div className="px-3 py-3">
          <div className="flex items-center justify-between text-[11px] mb-2">
            <span className="text-slate-500">Capital Deployed</span>
            <span className="font-mono text-slate-300 tabular-nums">${exposureDeployed.toFixed(2)}</span>
          </div>
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-500/60 rounded-full transition-all"
              style={{ width: `${Math.min((exposureDeployed / 1000) * 100, 100)}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-[10px] mt-1">
            <span className="text-slate-700">0</span>
            <span className="text-slate-700">$1,000</span>
          </div>
        </div>
      </Panel>

      {/* Positions */}
      <Panel
        title="Positions"
        headerRight={
          <span className="text-[10px] font-mono text-slate-600">{positions.length} open</span>
        }
      >
        {positions.length === 0 ? (
          <div className="px-3 py-6 text-center text-[11px] text-slate-700 font-mono">
            NO OPEN POSITIONS
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="text-slate-600 text-left border-b border-slate-800/50">
                  <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest">Ticker</th>
                  <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest text-right">Qty</th>
                  <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest text-right">Exposure</th>
                  <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest text-right">Cost</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos) => (
                  <tr key={pos.ticker} className="table-row border-b border-slate-800/30">
                    <td className="px-3 py-2 font-mono text-cyan-400">{pos.ticker}</td>
                    <td className={`px-3 py-2 text-right font-mono font-bold tabular-nums ${pos.position > 0 ? "text-emerald-400" : "text-red-400"}`}>
                      {pos.position > 0 ? "+" : ""}{pos.position}
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-slate-300 tabular-nums">
                      ${((pos.market_exposure || 0) / 100).toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-slate-500 tabular-nums">
                      ${((pos.total_cost || 0) / 100).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {/* Drawdown Chart */}
      <Panel title="Drawdown">
        <div className="px-3 py-2 flex justify-center">
          <DrawdownChart data={analytics.drawdownSeries} width={700} height={90} />
        </div>
      </Panel>
    </div>
  );
}
