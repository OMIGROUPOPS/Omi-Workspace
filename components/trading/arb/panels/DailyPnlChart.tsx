"use client";

import React, { useMemo } from "react";
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
  LabelList,
} from "recharts";
import { todayET } from "../helpers";

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

function renderBarLabel(props: any) {
  const { x, y, width, value } = props;
  if (value === 0) return null;
  return (
    <text
      x={x + width / 2}
      y={value >= 0 ? y - 4 : y + 14}
      fill={value >= 0 ? "#10b981" : "#ef4444"}
      fontSize={9}
      fontFamily="monospace"
      textAnchor="middle"
    >
      ${Math.abs(value).toFixed(2)}
    </text>
  );
}

export function DailyPnlChart({ data }: Props) {
  const summary = useMemo(() => {
    const etToday = todayET();
    const todayData = data.find((d) => d.date === etToday);
    const now = new Date();
    // Get start of week (Sunday) in ET
    const weekStart = new Date(now);
    weekStart.setDate(weekStart.getDate() - weekStart.getDay());
    const weekStartStr = weekStart.toISOString().slice(0, 10);
    const weekPnl = data
      .filter((d) => d.date >= weekStartStr)
      .reduce((s, d) => s + d.pnl, 0);
    const allTimePnl = data.reduce((s, d) => s + d.pnl, 0);
    return {
      today: todayData?.pnl ?? 0,
      todayTrades: todayData?.trades ?? 0,
      week: weekPnl,
      allTime: allTimePnl,
    };
  }, [data]);

  if (data.length === 0) return null;

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
        Daily P&L
      </h3>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 16, right: 4, bottom: 0, left: 4 }}>
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
            <LabelList content={renderBarLabel} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {/* Summary row */}
      <div className="flex items-center gap-4 mt-2 pt-2 border-t border-gray-800 text-[10px]">
        <div>
          <span className="text-gray-500">Today: </span>
          <span className={`font-mono font-bold ${summary.today >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            ${summary.today.toFixed(2)}
          </span>
          <span className="text-gray-600 ml-1">({summary.todayTrades}t)</span>
        </div>
        <div>
          <span className="text-gray-500">This Week: </span>
          <span className={`font-mono font-bold ${summary.week >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            ${summary.week.toFixed(2)}
          </span>
        </div>
        <div>
          <span className="text-gray-500">All Time: </span>
          <span className={`font-mono font-bold ${summary.allTime >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            ${summary.allTime.toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  );
}
