"use client";

import type { DrawdownPoint } from "@/lib/trading/types";

interface DrawdownChartProps {
  data: DrawdownPoint[];
  width?: number;
  height?: number;
}

export default function DrawdownChart({
  data,
  width = 500,
  height = 100,
}: DrawdownChartProps) {
  if (data.length < 2) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-slate-600 text-xs font-mono">
        NO DATA
      </div>
    );
  }

  const pad = { top: 8, right: 12, bottom: 8, left: 48 };
  const w = width - pad.left - pad.right;
  const h = height - pad.top - pad.bottom;

  const minDD = Math.min(...data.map((d) => d.drawdown), 0);
  const range = Math.abs(minDD) || 1;

  const toX = (i: number) => pad.left + (i / (data.length - 1)) * w;
  const toY = (dd: number) => pad.top + (Math.abs(dd) / range) * h;

  const zeroY = pad.top;
  const points = data.map((d, i) => `${toX(i)},${toY(d.drawdown)}`).join(" ");
  const areaPoints = `${toX(0)},${zeroY} ${points} ${toX(data.length - 1)},${zeroY}`;

  return (
    <svg width={width} height={height}>
      <defs>
        <linearGradient id="dd-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ef4444" stopOpacity="0.05" />
          <stop offset="100%" stopColor="#ef4444" stopOpacity="0.25" />
        </linearGradient>
      </defs>

      {/* Zero line */}
      <line
        x1={pad.left} y1={zeroY} x2={width - pad.right} y2={zeroY}
        stroke="#334155" strokeWidth="1"
      />

      <text
        x={pad.left - 4} y={zeroY + 3} textAnchor="end"
        fill="#475569" fontSize="8" fontFamily="monospace"
      >
        0%
      </text>
      <text
        x={pad.left - 4} y={pad.top + h + 3} textAnchor="end"
        fill="#475569" fontSize="8" fontFamily="monospace"
      >
        {minDD.toFixed(1)}%
      </text>

      <polygon points={areaPoints} fill="url(#dd-grad)" />
      <polyline
        points={points} fill="none" stroke="#ef4444"
        strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
        opacity="0.7"
      />
    </svg>
  );
}
