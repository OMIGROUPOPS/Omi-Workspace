"use client";

import type { FullAnalytics } from "@/lib/trading/types";
import HeatmapChart from "../charts/HeatmapChart";
import BarChart from "../charts/BarChart";
import HistogramChart from "../charts/HistogramChart";
import Panel from "../shared/Panel";
import { SPORT_COLORS } from "@/lib/trading/config";

interface ResearchTabProps {
  analytics: FullAnalytics;
}

export default function ResearchTab({ analytics }: ResearchTabProps) {
  const volumeData = analytics.volumeBySport.map((v) => ({
    label: v.sport,
    value: v.kalshi,
    color: "#06b6d4",
    value2: v.pm,
    color2: "#8b5cf6",
  }));

  const profitData = analytics.profitBySport.map((p) => ({
    label: p.sport,
    value: p.profit,
    color: SPORT_COLORS[p.sport] || SPORT_COLORS.DEFAULT,
  }));

  const hourData = analytics.tradesByHour.map((count, hour) => ({
    label: hour.toString(),
    value: count,
    color: hour >= 18 && hour <= 23 ? "#10b981" : hour >= 11 && hour < 18 ? "#06b6d4" : "#334155",
  }));

  return (
    <div className="flex flex-col gap-2 overflow-y-auto scrollbar-thin h-full">
      {/* 2x2 Grid */}
      <div className="grid grid-cols-2 gap-2">
        {/* Arb Heatmap */}
        <Panel title="Arb Heatmap (Hour x Sport)">
          <div className="px-3 py-2 flex justify-center">
            <HeatmapChart data={analytics.heatmapData} width={420} height={180} />
          </div>
        </Panel>

        {/* Volume by Sport */}
        <Panel
          title="Volume by Sport"
          headerRight={
            <div className="flex items-center gap-3 text-[9px] font-mono">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-sm bg-cyan-500" />
                <span className="text-slate-600">Kalshi</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-sm bg-violet-500" />
                <span className="text-slate-600">PM</span>
              </div>
            </div>
          }
        >
          <div className="px-3 py-2 flex justify-center">
            <BarChart data={volumeData} width={420} height={180} horizontal />
          </div>
        </Panel>

        {/* ROI Distribution */}
        <Panel title="ROI Distribution">
          <div className="px-3 py-2 flex justify-center">
            <HistogramChart data={analytics.roiDistribution} width={420} height={180} />
          </div>
        </Panel>

        {/* Profitability by Sport */}
        <Panel title="Profit by Sport">
          <div className="px-3 py-2 flex justify-center">
            <BarChart data={profitData} width={420} height={180} />
          </div>
        </Panel>
      </div>

      {/* Time of Day */}
      <Panel title="Trades by Hour (EST)">
        <div className="px-3 py-2 flex justify-center">
          <BarChart data={hourData} width={860} height={120} showValues={false} />
        </div>
      </Panel>
    </div>
  );
}
