"use client";

import type { ROIBucket } from "@/lib/trading/types";

interface HistogramChartProps {
  data: ROIBucket[];
  width?: number;
  height?: number;
}

export default function HistogramChart({
  data,
  width = 300,
  height = 160,
}: HistogramChartProps) {
  if (data.length === 0 || data.every((d) => d.count === 0)) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-slate-600 text-xs font-mono">
        NO DATA
      </div>
    );
  }

  const pad = { top: 8, right: 8, bottom: 28, left: 28 };
  const w = width - pad.left - pad.right;
  const h = height - pad.top - pad.bottom;
  const maxCount = Math.max(...data.map((d) => d.count), 1);

  const barWidth = (w - (data.length - 1) * 2) / data.length;

  return (
    <svg width={width} height={height}>
      <line
        x1={pad.left} y1={pad.top + h}
        x2={width - pad.right} y2={pad.top + h}
        stroke="#1e293b" strokeWidth="1"
      />
      {data.map((bucket, i) => {
        const barH = (bucket.count / maxCount) * h;
        const x = pad.left + i * (barWidth + 2);
        const y = pad.top + h - barH;
        const isNeg = bucket.min < 0;

        return (
          <g key={i}>
            <rect
              x={x} y={y} width={barWidth} height={barH}
              rx="2" fill={isNeg ? "#ef4444" : "#10b981"} opacity="0.7"
            />
            <text
              x={x + barWidth / 2} y={pad.top + h + 12}
              textAnchor="middle" fill="#475569" fontSize="7" fontFamily="monospace"
            >
              {bucket.range}
            </text>
            {bucket.count > 0 && (
              <text
                x={x + barWidth / 2} y={y - 3}
                textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace"
              >
                {bucket.count}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
