"use client";

import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { SpreadHistoryPoint } from "../types";
import { sportChartColor, formatTimeHM } from "../helpers";

interface Props {
  spreadHistory: SpreadHistoryPoint[];
  spreadMinCents?: number;
}

export function SpreadTimeSeriesChart({ spreadHistory, spreadMinCents = 4 }: Props) {
  // Group by game, pick top 10 by data points
  const { chartData, gameKeys } = useMemo(() => {
    if (!spreadHistory || spreadHistory.length === 0) {
      return { chartData: [], gameKeys: [] };
    }

    // Count points per game
    const gameCounts: Record<string, { count: number; sport: string; team: string }> = {};
    for (const p of spreadHistory) {
      const key = `${p.game_id}_${p.team}`;
      if (!gameCounts[key]) gameCounts[key] = { count: 0, sport: p.sport, team: p.team };
      gameCounts[key].count++;
    }

    // Top 10 games
    const topGames = Object.entries(gameCounts)
      .sort(([, a], [, b]) => b.count - a.count)
      .slice(0, 10)
      .map(([key]) => key);

    const topSet = new Set(topGames);

    // Build time-series data: group by timestamp, one column per game
    const timeMap: Record<string, Record<string, number>> = {};
    for (const p of spreadHistory) {
      const key = `${p.game_id}_${p.team}`;
      if (!topSet.has(key)) continue;
      const ts = p.timestamp;
      if (!timeMap[ts]) timeMap[ts] = {};
      timeMap[ts][key] = p.best_spread;
    }

    const data = Object.entries(timeMap)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([ts, vals]) => ({
        time: formatTimeHM(ts),
        ...vals,
      }));

    const keys = topGames.map((key) => ({
      key,
      team: gameCounts[key].team,
      sport: gameCounts[key].sport,
      color: sportChartColor(gameCounts[key].sport),
    }));

    return { chartData: data, gameKeys: keys };
  }, [spreadHistory]);

  if (chartData.length === 0) {
    return (
      <div className="rounded-lg border border-gray-800 bg-[#111] p-4 text-center text-sm text-gray-500">
        Spread history will populate after ~30s of data
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
        Spread Time Series (60 min)
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            dataKey="time"
            tick={{ fill: "#6b7280", fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#6b7280", fontSize: 10 }}
            label={{ value: "cents", angle: -90, position: "insideLeft", fill: "#6b7280", fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#111", border: "1px solid #374151", borderRadius: "8px", fontSize: "11px" }}
            labelStyle={{ color: "#9ca3af" }}
          />
          <ReferenceLine
            y={spreadMinCents}
            stroke="#6b7280"
            strokeDasharray="4 4"
            label={{ value: `min ${spreadMinCents}c`, fill: "#6b7280", fontSize: 10, position: "right" }}
          />
          {gameKeys.map(({ key, team, color }) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              name={team}
              stroke={color}
              dot={false}
              strokeWidth={1.5}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
