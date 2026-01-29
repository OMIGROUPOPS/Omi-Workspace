'use client';

import { useState, useMemo } from 'react';

interface LineMovementDataPoint {
  timestamp: Date;
  spread: number;
  total: number;
  homeML: number;
  awayML: number;
  book?: string;
}

interface LineMovementChartProps {
  data?: LineMovementDataPoint[];
  homeTeam: string;
  awayTeam: string;
  gameTime: Date;
}

type ChartType = 'spread' | 'total' | 'ml';

// Premium TradingView-inspired chart
export function LineMovementChart({ data, homeTeam, awayTeam, gameTime }: LineMovementChartProps) {
  const [chartType, setChartType] = useState<ChartType>('spread');
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);

  const chartData = data && data.length > 0 ? data : [];

  const chartConfig = {
    spread: { label: 'Spread', color: '#10b981', gradientId: 'spreadGrad' },
    total: { label: 'Total', color: '#3b82f6', gradientId: 'totalGrad' },
    ml: { label: 'Moneyline', color: '#a855f7', gradientId: 'mlGrad' },
  };

  const config = chartConfig[chartType];

  // Empty state
  if (chartData.length === 0) {
    return (
      <div className="bg-[#0c0c0c] border border-zinc-800/80 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-zinc-800/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-1 h-6 bg-emerald-500 rounded-full" />
            <h2 className="text-base font-semibold text-zinc-100">Line Movement</h2>
          </div>
          <ChartTypeTabs chartType={chartType} onChange={setChartType} />
        </div>
        <div className="p-12 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-zinc-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <p className="text-zinc-300 text-sm font-medium mb-1">No Line Movement Data</p>
          <p className="text-zinc-600 text-xs max-w-xs">Historical line data will appear once the system begins collecting snapshots for this game</p>
        </div>
      </div>
    );
  }

  const getValues = (type: ChartType) => {
    switch (type) {
      case 'spread': return chartData.map(d => d.spread);
      case 'total': return chartData.map(d => d.total);
      case 'ml': return chartData.map(d => d.homeML);
    }
  };

  const values = getValues(chartType);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  const padding = range * 0.15;

  // Chart dimensions
  const width = 700;
  const height = 280;
  const paddingLeft = 60;
  const paddingRight = 30;
  const paddingTop = 30;
  const paddingBottom = 50;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  // Calculate points
  const points = values.map((val, i) => {
    const x = paddingLeft + (i / Math.max(values.length - 1, 1)) * chartWidth;
    const y = paddingTop + chartHeight - ((val - minVal + padding) / (range + 2 * padding)) * chartHeight;
    return { x, y, value: val, timestamp: chartData[i].timestamp };
  });

  // Smooth curve path using bezier curves
  const createSmoothPath = (pts: typeof points) => {
    if (pts.length < 2) return `M ${pts[0]?.x || 0} ${pts[0]?.y || 0}`;

    let path = `M ${pts[0].x} ${pts[0].y}`;
    for (let i = 1; i < pts.length; i++) {
      const prev = pts[i - 1];
      const curr = pts[i];
      const cpx = (prev.x + curr.x) / 2;
      path += ` Q ${prev.x + (cpx - prev.x) * 0.5} ${prev.y}, ${cpx} ${(prev.y + curr.y) / 2}`;
      path += ` Q ${cpx + (curr.x - cpx) * 0.5} ${curr.y}, ${curr.x} ${curr.y}`;
    }
    return path;
  };

  const smoothPath = createSmoothPath(points);

  // Y-axis labels (5 levels)
  const yLabelCount = 5;
  const yLabels = Array.from({ length: yLabelCount }, (_, i) => {
    const ratio = i / (yLabelCount - 1);
    const value = maxVal + padding - ratio * (range + 2 * padding);
    const y = paddingTop + ratio * chartHeight;
    return { value, y };
  });

  // X-axis labels (smart time formatting)
  const xLabelIndices = chartData.length <= 5
    ? chartData.map((_, i) => i)
    : [0, Math.floor(chartData.length * 0.25), Math.floor(chartData.length * 0.5), Math.floor(chartData.length * 0.75), chartData.length - 1];

  const formatTimestamp = (ts: Date) => {
    const now = new Date();
    const diffHours = (now.getTime() - ts.getTime()) / (1000 * 60 * 60);
    if (diffHours < 24) {
      return ts.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }
    return ts.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const openValue = values[0];
  const currentValue = values[values.length - 1];
  const movement = currentValue - openValue;
  const movementPct = openValue !== 0 ? ((movement / Math.abs(openValue)) * 100) : 0;

  const formatValue = (val: number, type: ChartType) => {
    switch (type) {
      case 'spread': return val > 0 ? `+${val.toFixed(1)}` : val.toFixed(1);
      case 'total': return val.toFixed(1);
      case 'ml': return val > 0 ? `+${val}` : val.toString();
    }
  };

  // Hover tooltip point
  const activePoint = hoveredPoint !== null ? points[hoveredPoint] : points[points.length - 1];

  return (
    <div className="bg-[#0c0c0c] border border-zinc-800/80 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-zinc-800/60 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-1 h-6 rounded-full" style={{ backgroundColor: config.color }} />
          <h2 className="text-base font-semibold text-zinc-100">Line Movement</h2>
          <span className="text-xs text-zinc-600 font-mono">
            {awayTeam.split(' ').pop()} @ {homeTeam.split(' ').pop()}
          </span>
        </div>
        <ChartTypeTabs chartType={chartType} onChange={setChartType} />
      </div>

      {/* Stats Bar */}
      <div className="px-5 py-3 border-b border-zinc-800/40 bg-zinc-900/30 grid grid-cols-4 gap-4">
        <StatBox label="Open" value={formatValue(openValue, chartType)} />
        <StatBox label="Current" value={formatValue(currentValue, chartType)} highlight />
        <StatBox
          label="Movement"
          value={`${movement >= 0 ? '+' : ''}${movement.toFixed(1)}`}
          color={movement > 0 ? 'emerald' : movement < 0 ? 'red' : 'zinc'}
        />
        <StatBox label="Data Points" value={chartData.length.toString()} muted />
      </div>

      {/* Chart */}
      <div className="p-4 relative">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto"
          style={{ maxHeight: '280px' }}
          onMouseLeave={() => setHoveredPoint(null)}
        >
          <defs>
            {/* Gradient for area fill */}
            <linearGradient id={config.gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={config.color} stopOpacity="0.25" />
              <stop offset="50%" stopColor={config.color} stopOpacity="0.1" />
              <stop offset="100%" stopColor={config.color} stopOpacity="0" />
            </linearGradient>
            {/* Glow filter */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Grid lines */}
          {yLabels.map((label, i) => (
            <line
              key={`grid-${i}`}
              x1={paddingLeft}
              y1={label.y}
              x2={width - paddingRight}
              y2={label.y}
              stroke="#27272a"
              strokeWidth="1"
            />
          ))}

          {/* Y-axis labels */}
          {yLabels.map((label, i) => (
            <text
              key={`y-${i}`}
              x={paddingLeft - 12}
              y={label.y + 4}
              textAnchor="end"
              fill="#52525b"
              fontSize="11"
              fontFamily="ui-monospace, monospace"
            >
              {formatValue(label.value, chartType)}
            </text>
          ))}

          {/* X-axis labels */}
          {xLabelIndices.map((idx) => (
            <text
              key={`x-${idx}`}
              x={points[idx]?.x || 0}
              y={height - 15}
              textAnchor="middle"
              fill="#52525b"
              fontSize="10"
              fontFamily="ui-monospace, monospace"
            >
              {formatTimestamp(chartData[idx].timestamp)}
            </text>
          ))}

          {/* Area fill */}
          <path
            d={`${smoothPath} L ${points[points.length - 1].x} ${paddingTop + chartHeight} L ${paddingLeft} ${paddingTop + chartHeight} Z`}
            fill={`url(#${config.gradientId})`}
          />

          {/* Line */}
          <path
            d={smoothPath}
            fill="none"
            stroke={config.color}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            filter="url(#glow)"
          />

          {/* Interactive hover areas */}
          {points.map((point, i) => (
            <rect
              key={`hover-${i}`}
              x={point.x - chartWidth / points.length / 2}
              y={paddingTop}
              width={chartWidth / points.length}
              height={chartHeight}
              fill="transparent"
              onMouseEnter={() => setHoveredPoint(i)}
              style={{ cursor: 'crosshair' }}
            />
          ))}

          {/* Hover line */}
          {hoveredPoint !== null && (
            <line
              x1={points[hoveredPoint].x}
              y1={paddingTop}
              x2={points[hoveredPoint].x}
              y2={paddingTop + chartHeight}
              stroke={config.color}
              strokeWidth="1"
              strokeDasharray="4 2"
              opacity="0.5"
            />
          )}

          {/* Opening point */}
          <circle
            cx={points[0].x}
            cy={points[0].y}
            r="5"
            fill="#18181b"
            stroke="#52525b"
            strokeWidth="2"
          />

          {/* Current/Active point */}
          <circle
            cx={activePoint.x}
            cy={activePoint.y}
            r="6"
            fill="#0c0c0c"
            stroke={config.color}
            strokeWidth="3"
            filter="url(#glow)"
          />
          <circle
            cx={activePoint.x}
            cy={activePoint.y}
            r="3"
            fill={config.color}
          />

          {/* Tooltip */}
          {hoveredPoint !== null && (
            <g transform={`translate(${points[hoveredPoint].x}, ${points[hoveredPoint].y - 45})`}>
              <rect x="-45" y="-10" width="90" height="36" rx="6" fill="#18181b" stroke="#3f3f46" />
              <text x="0" y="6" textAnchor="middle" fill="#fafafa" fontSize="12" fontWeight="600" fontFamily="ui-monospace, monospace">
                {formatValue(points[hoveredPoint].value, chartType)}
              </text>
              <text x="0" y="20" textAnchor="middle" fill="#71717a" fontSize="9" fontFamily="ui-monospace, monospace">
                {formatTimestamp(chartData[hoveredPoint].timestamp)}
              </text>
            </g>
          )}
        </svg>
      </div>

      {/* Footer Legend */}
      <div className="px-5 py-3 bg-zinc-900/40 border-t border-zinc-800/40 flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-zinc-600 border border-zinc-500" />
            <span className="text-zinc-500 font-medium">Opening</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: config.color }} />
            <span className="text-zinc-400 font-medium">Current</span>
          </div>
        </div>
        <div className="text-[10px] font-mono text-zinc-600">
          Updated {formatTimestamp(chartData[chartData.length - 1].timestamp)}
        </div>
      </div>
    </div>
  );
}

// Chart type toggle tabs
function ChartTypeTabs({ chartType, onChange }: { chartType: ChartType; onChange: (t: ChartType) => void }) {
  const tabs: { key: ChartType; label: string; color: string }[] = [
    { key: 'spread', label: 'Spread', color: '#10b981' },
    { key: 'total', label: 'Total', color: '#3b82f6' },
    { key: 'ml', label: 'ML', color: '#a855f7' },
  ];

  return (
    <div className="flex bg-zinc-900/80 rounded-lg p-0.5 border border-zinc-800/60">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
            chartType === tab.key
              ? 'bg-zinc-800 text-zinc-100 shadow-sm'
              : 'text-zinc-500 hover:text-zinc-300'
          }`}
        >
          {chartType === tab.key && (
            <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5" style={{ backgroundColor: tab.color }} />
          )}
          {tab.label}
        </button>
      ))}
    </div>
  );
}

// Stat box component
function StatBox({ label, value, highlight, color, muted }: {
  label: string;
  value: string;
  highlight?: boolean;
  color?: 'emerald' | 'red' | 'zinc';
  muted?: boolean;
}) {
  const valueColor = color === 'emerald' ? 'text-emerald-400' :
                     color === 'red' ? 'text-red-400' :
                     highlight ? 'text-zinc-100' :
                     muted ? 'text-zinc-600' : 'text-zinc-300';

  return (
    <div>
      <div className="text-[10px] font-mono text-zinc-600 uppercase tracking-wider mb-0.5">{label}</div>
      <div className={`text-sm font-semibold font-mono ${valueColor}`}>{value}</div>
    </div>
  );
}
