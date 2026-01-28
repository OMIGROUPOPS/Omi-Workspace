"use client";

import type { Trade } from "@/lib/trading/types";

interface ScatterPlotProps {
  trades: Trade[];
  width?: number;
  height?: number;
}

export default function ScatterPlot({
  trades,
  width = 500,
  height = 200,
}: ScatterPlotProps) {
  const successful = trades.filter(
    (t) => t.status === "SUCCESS" || t.status === "PAPER"
  );

  if (successful.length === 0) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-slate-600 text-xs font-mono">
        NO DATA
      </div>
    );
  }

  const pad = { top: 12, right: 12, bottom: 20, left: 48 };
  const w = width - pad.left - pad.right;
  const h = height - pad.top - pad.bottom;

  const timestamps = successful.map((t) => new Date(t.timestamp).getTime());
  const profits = successful.map((t) => t.expected_profit);

  const minT = Math.min(...timestamps);
  const maxT = Math.max(...timestamps);
  const rangeT = maxT - minT || 1;

  const minP = Math.min(...profits, 0);
  const maxP = Math.max(...profits, 0);
  const rangeP = maxP - minP || 1;

  const toX = (t: number) => pad.left + ((t - minT) / rangeT) * w;
  const toY = (p: number) => pad.top + h - ((p - minP) / rangeP) * h;

  const zeroY = toY(0);
  const maxAbsProfit = Math.max(...profits.map(Math.abs), 0.01);

  return (
    <svg width={width} height={height}>
      {/* Zero line */}
      {minP < 0 && maxP > 0 && (
        <line
          x1={pad.left} y1={zeroY} x2={width - pad.right} y2={zeroY}
          stroke="#334155" strokeWidth="1" strokeDasharray="2,4"
        />
      )}

      {/* Grid */}
      {[0.25, 0.5, 0.75].map((frac, i) => {
        const val = minP + rangeP * frac;
        const y = toY(val);
        return (
          <g key={i}>
            <line
              x1={pad.left} y1={y} x2={width - pad.right} y2={y}
              stroke="#1e293b" strokeWidth="1" strokeDasharray="2,4"
            />
            <text
              x={pad.left - 4} y={y + 3} textAnchor="end"
              fill="#475569" fontSize="8" fontFamily="monospace"
            >
              ${val.toFixed(2)}
            </text>
          </g>
        );
      })}

      {/* Dots */}
      {successful.map((trade, i) => {
        const x = toX(new Date(trade.timestamp).getTime());
        const y = toY(trade.expected_profit);
        const isPos = trade.expected_profit >= 0;
        const r = 3 + (Math.abs(trade.expected_profit) / maxAbsProfit) * 5;

        return (
          <circle
            key={i}
            cx={x} cy={y} r={Math.min(r, 10)}
            fill={isPos ? "#10b981" : "#ef4444"}
            opacity="0.6"
          >
            <title>
              {`${trade.team}: ${trade.expected_profit >= 0 ? "+" : ""}$${trade.expected_profit.toFixed(2)} (${trade.roi.toFixed(1)}%)`}
            </title>
          </circle>
        );
      })}
    </svg>
  );
}
