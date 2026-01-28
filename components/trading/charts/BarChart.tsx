"use client";

interface BarChartProps {
  data: { label: string; value: number; color?: string; value2?: number; color2?: string }[];
  width?: number;
  height?: number;
  horizontal?: boolean;
  showValues?: boolean;
}

export default function BarChart({
  data,
  width = 400,
  height = 200,
  horizontal = false,
  showValues = true,
}: BarChartProps) {
  if (data.length === 0) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-slate-600 text-xs font-mono">
        NO DATA
      </div>
    );
  }

  const pad = horizontal
    ? { top: 8, right: 12, bottom: 8, left: 60 }
    : { top: 8, right: 8, bottom: 28, left: 32 };
  const w = width - pad.left - pad.right;
  const h = height - pad.top - pad.bottom;

  const maxVal = Math.max(...data.map((d) => d.value + (d.value2 || 0)), 1);

  if (horizontal) {
    const barHeight = Math.min(20, (h - (data.length - 1) * 4) / data.length);

    return (
      <svg width={width} height={height}>
        {data.map((d, i) => {
          const y = pad.top + i * (barHeight + 4);
          const barW1 = (d.value / maxVal) * w;
          const barW2 = d.value2 ? (d.value2 / maxVal) * w : 0;
          const c1 = d.color || "#06b6d4";
          const c2 = d.color2 || "#8b5cf6";

          return (
            <g key={i}>
              <text
                x={pad.left - 4} y={y + barHeight / 2 + 3}
                textAnchor="end" fill="#64748b" fontSize="9" fontFamily="monospace"
              >
                {d.label}
              </text>
              <rect x={pad.left} y={y} width={barW1} height={barHeight} rx="2" fill={c1} opacity="0.8" />
              {barW2 > 0 && (
                <rect x={pad.left + barW1} y={y} width={barW2} height={barHeight} rx="2" fill={c2} opacity="0.8" />
              )}
              {showValues && (
                <text
                  x={pad.left + barW1 + barW2 + 4} y={y + barHeight / 2 + 3}
                  fill="#94a3b8" fontSize="9" fontFamily="monospace"
                >
                  {d.value}{d.value2 ? ` / ${d.value2}` : ""}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    );
  }

  const barWidth = Math.min(28, (w - (data.length - 1) * 4) / data.length);

  return (
    <svg width={width} height={height}>
      {/* Zero line */}
      <line
        x1={pad.left} y1={pad.top + h} x2={width - pad.right} y2={pad.top + h}
        stroke="#1e293b" strokeWidth="1"
      />
      {data.map((d, i) => {
        const x = pad.left + i * (barWidth + 4) + (w - data.length * (barWidth + 4) + 4) / 2;
        const total = d.value + (d.value2 || 0);
        const barH = (Math.abs(total) / maxVal) * h;
        const y = total >= 0 ? pad.top + h - barH : pad.top + h;
        const c1 = d.color || "#10b981";

        return (
          <g key={i}>
            <rect x={x} y={y} width={barWidth} height={barH} rx="2" fill={c1} opacity="0.8" />
            <text
              x={x + barWidth / 2} y={pad.top + h + 14}
              textAnchor="middle" fill="#475569" fontSize="8" fontFamily="monospace"
            >
              {d.label}
            </text>
            {showValues && (
              <text
                x={x + barWidth / 2} y={y - 4}
                textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace"
              >
                {total > 0 ? total : ""}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
