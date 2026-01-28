"use client";

import type { PnLPeriod } from "@/lib/trading/types";

interface PnLChartProps {
  data: number[];
  width?: number;
  height?: number;
  period?: PnLPeriod;
  onPeriodChange?: (period: PnLPeriod) => void;
  showPeriodSelector?: boolean;
}

const PERIODS: PnLPeriod[] = ["1H", "6H", "24H", "ALL"];

export default function PnLChart({
  data,
  width = 500,
  height = 140,
  period = "ALL",
  onPeriodChange,
  showPeriodSelector = false,
}: PnLChartProps) {
  if (data.length < 2) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-slate-600 text-xs font-mono">
        AWAITING DATA
      </div>
    );
  }

  const pad = { top: 20, right: 12, bottom: 20, left: 48 };
  const w = width - pad.left - pad.right;
  const h = height - pad.top - pad.bottom;

  const min = Math.min(...data, 0);
  const max = Math.max(...data, 0);
  const range = max - min || 1;

  const toX = (i: number) => pad.left + (i / (data.length - 1)) * w;
  const toY = (v: number) => pad.top + h - ((v - min) / range) * h;

  const zeroY = toY(0);
  const points = data.map((v, i) => `${toX(i)},${toY(v)}`).join(" ");
  const areaPoints = `${toX(0)},${zeroY} ${points} ${toX(data.length - 1)},${zeroY}`;

  const last = data[data.length - 1];
  const lastX = toX(data.length - 1);
  const lastY = toY(last);
  const isPositive = last >= 0;
  const lineColor = isPositive ? "#10b981" : "#ef4444";

  const gridCount = 4;
  const gridLines = Array.from({ length: gridCount + 1 }, (_, i) => {
    const val = min + (range / gridCount) * i;
    return {
      y: toY(val),
      label: val >= 0 ? `+$${val.toFixed(2)}` : `-$${Math.abs(val).toFixed(2)}`,
    };
  });

  const gradId = `pnl-grad-${isPositive ? "g" : "r"}`;

  return (
    <div>
      {showPeriodSelector && onPeriodChange && (
        <div className="flex gap-0.5 mb-2 bg-slate-800/40 p-0.5 rounded w-fit">
          {PERIODS.map((p) => (
            <button
              key={p}
              onClick={() => onPeriodChange(p)}
              className={`px-2 py-0.5 text-[9px] font-bold tracking-wider rounded transition-all
                ${period === p
                  ? "bg-slate-700/60 text-slate-200"
                  : "text-slate-600 hover:text-slate-400"
                }`}
            >
              {p}
            </button>
          ))}
        </div>
      )}
      <svg width={width} height={height} className="overflow-visible">
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={lineColor} stopOpacity="0.25" />
            <stop offset="100%" stopColor={lineColor} stopOpacity="0" />
          </linearGradient>
        </defs>

        {gridLines.map((g, i) => (
          <g key={i}>
            <line
              x1={pad.left} y1={g.y} x2={width - pad.right} y2={g.y}
              stroke="#1e293b" strokeWidth="1" strokeDasharray="2,4"
            />
            <text
              x={pad.left - 6} y={g.y + 3} textAnchor="end"
              fill="#475569" fontSize="9" fontFamily="monospace"
            >
              {g.label}
            </text>
          </g>
        ))}

        {min < 0 && max > 0 && (
          <line
            x1={pad.left} y1={zeroY} x2={width - pad.right} y2={zeroY}
            stroke="#334155" strokeWidth="1"
          />
        )}

        <polygon points={areaPoints} fill={`url(#${gradId})`} />

        <polyline
          points={points} fill="none" stroke={lineColor}
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        />

        <circle cx={lastX} cy={lastY} r="4" fill={lineColor} />
        <circle cx={lastX} cy={lastY} r="7" fill={lineColor} opacity="0.2">
          <animate attributeName="r" values="7;12;7" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.2;0;0.2" dur="2s" repeatCount="indefinite" />
        </circle>
        <text
          x={lastX - 8} y={lastY - 12} textAnchor="end"
          fill={lineColor} fontSize="11" fontWeight="bold" fontFamily="monospace"
        >
          {last >= 0 ? "+" : ""}${last.toFixed(2)}
        </text>
      </svg>
    </div>
  );
}
