"use client";

import type { HeatmapCell } from "@/lib/trading/types";

interface HeatmapChartProps {
  data: HeatmapCell[];
  width?: number;
  height?: number;
}

export default function HeatmapChart({
  data,
  width = 500,
  height = 200,
}: HeatmapChartProps) {
  if (data.length === 0) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-slate-600 text-xs font-mono">
        NO DATA
      </div>
    );
  }

  const sports = [...new Set(data.map((d) => d.sport))];
  const maxCount = Math.max(...data.map((d) => d.count), 1);

  const pad = { top: 8, right: 8, bottom: 20, left: 60 };
  const gridW = width - pad.left - pad.right;
  const gridH = height - pad.top - pad.bottom;
  const cellW = gridW / 24;
  const cellH = sports.length > 0 ? gridH / sports.length : gridH;

  const getColor = (count: number) => {
    if (count === 0) return "#0f172a";
    const intensity = count / maxCount;
    const r = Math.round(6 + intensity * 10);
    const g = Math.round(182 + intensity * 3);
    const b = Math.round(129 + intensity * 2);
    const a = 0.15 + intensity * 0.7;
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  };

  return (
    <svg width={width} height={height}>
      {sports.map((sport, si) => (
        <g key={sport}>
          <text
            x={pad.left - 4}
            y={pad.top + si * cellH + cellH / 2 + 3}
            textAnchor="end"
            fill="#64748b"
            fontSize="9"
            fontFamily="monospace"
          >
            {sport}
          </text>
          {Array.from({ length: 24 }, (_, hour) => {
            const cell = data.find((d) => d.sport === sport && d.hour === hour);
            const count = cell?.count || 0;
            return (
              <rect
                key={hour}
                x={pad.left + hour * cellW}
                y={pad.top + si * cellH}
                width={cellW - 1}
                height={cellH - 1}
                rx="2"
                fill={getColor(count)}
              >
                <title>{`${sport} ${hour}:00 - ${count} trades`}</title>
              </rect>
            );
          })}
        </g>
      ))}
      {/* Hour labels */}
      {[0, 6, 12, 18, 23].map((hour) => (
        <text
          key={hour}
          x={pad.left + hour * cellW + cellW / 2}
          y={height - 4}
          textAnchor="middle"
          fill="#475569"
          fontSize="8"
          fontFamily="monospace"
        >
          {hour}
        </text>
      ))}
    </svg>
  );
}
