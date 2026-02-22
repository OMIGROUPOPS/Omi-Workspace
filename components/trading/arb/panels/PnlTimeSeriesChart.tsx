"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Scatter,
  ScatterChart,
} from "recharts";
import { formatTimeHM } from "../helpers";

interface ChartPoint {
  index: number;
  date: string;
  time: string;
  pnl: number;
  tradePnl: number;
  team: string;
  phase: string;
  isMaker: boolean;
}

interface Props {
  data: ChartPoint[];
}

export function PnlTimeSeriesChart({ data }: Props) {
  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-gray-800 bg-[#111] p-4 text-center text-sm text-gray-500">
        No P&L data
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
        Cumulative P&L
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            dataKey="index"
            tick={{ fill: "#6b7280", fontSize: 10 }}
            label={{ value: "Trade #", position: "insideBottom", fill: "#6b7280", fontSize: 10, offset: -5 }}
          />
          <YAxis
            tick={{ fill: "#6b7280", fontSize: 10 }}
            label={{ value: "$", angle: -90, position: "insideLeft", fill: "#6b7280", fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#111", border: "1px solid #374151", borderRadius: "8px", fontSize: "11px" }}
            formatter={(value: any, name: any) => {
              const v = Number(value);
              if (name === "pnl") return [`$${v.toFixed(4)}`, "Cumulative"];
              if (name === "tradePnl") return [`$${v.toFixed(4)}`, "This trade"];
              return [v, String(name)];
            }}
            labelFormatter={(label) => {
              const point = data.find((d) => d.index === label);
              return point ? `#${label} ${point.team} (${formatTimeHM(point.time)})` : `#${label}`;
            }}
          />
          <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="2 2" />
          <Line
            type="monotone"
            dataKey="pnl"
            stroke="#10b981"
            dot={(props: any) => {
              const { cx, cy, payload } = props;
              const color = payload.tradePnl >= 0 ? "#10b981" : "#ef4444";
              return <circle cx={cx} cy={cy} r={3} fill={color} stroke="none" />;
            }}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
