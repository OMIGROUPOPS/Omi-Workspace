"use client";

import Sparkline from "../charts/Sparkline";

interface MetricCardProps {
  label: string;
  value: string;
  color?: string;
  sparkData?: number[];
  sparkColor?: string;
  suffix?: string;
}

export default function MetricCard({
  label,
  value,
  color = "text-slate-200",
  sparkData,
  sparkColor = "#10b981",
  suffix,
}: MetricCardProps) {
  return (
    <div className="panel rounded-lg p-3">
      <div className="text-[9px] text-slate-600 uppercase tracking-widest mb-1">
        {label}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <span className={`font-mono text-lg font-bold tabular-nums ${color}`}>
            {value}
          </span>
          {suffix && (
            <span className="text-[10px] text-slate-600 ml-1">{suffix}</span>
          )}
        </div>
        {sparkData && sparkData.length >= 2 && (
          <Sparkline data={sparkData} color={sparkColor} width={60} height={20} />
        )}
      </div>
    </div>
  );
}
