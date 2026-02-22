"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

interface DailyData {
  date: string;
  label: string;
  pnl: number;
  trades: number;
  successes: number;
  noFills: number;
  contracts: number;
  makerFills: number;
}

interface Props {
  data: DailyData[];
}

export function DailyPnlChart({ data }: Props) {
  if (data.length === 0) return null;

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
        Daily P&L
      </h3>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="label" tick={{ fill: "#6b7280", fontSize: 10 }} />
          <YAxis tick={{ fill: "#6b7280", fontSize: 10 }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#111", border: "1px solid #374151", borderRadius: "8px", fontSize: "11px" }}
            formatter={(value: any) => [`$${Number(value).toFixed(4)}`, "P&L"]}
            labelFormatter={(label, payload) => {
              const item = payload?.[0]?.payload as DailyData | undefined;
              return item ? `${item.date} (${item.trades} trades, ${item.contracts} contracts)` : label;
            }}
          />
          <ReferenceLine y={0} stroke="#6b7280" />
          <Bar dataKey="pnl" radius={[2, 2, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.pnl >= 0 ? "#10b981" : "#ef4444"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
