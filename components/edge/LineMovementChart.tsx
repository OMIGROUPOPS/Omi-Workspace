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

// Generate mock line movement data
function generateMockData(gameId: string, gameTime: Date): LineMovementDataPoint[] {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const points: LineMovementDataPoint[] = [];
  
  const startTime = new Date(gameTime);
  startTime.setDate(startTime.getDate() - 7);
  
  let spread = -3 + (seed % 10) - 5;
  let total = 42 + (seed % 15);
  let homeML = -150 + (seed % 100);
  let awayML = 130 - (seed % 80);
  
  const hoursInWeek = 24 * 7;
  const pointsToGenerate = 50;
  const interval = Math.floor(hoursInWeek / pointsToGenerate);
  
  for (let i = 0; i <= pointsToGenerate; i++) {
    const timestamp = new Date(startTime);
    timestamp.setHours(timestamp.getHours() + (i * interval));
    
    const x = Math.sin(seed * i) * 10000;
    const drift = (x - Math.floor(x) - 0.5) * 0.3;
    const timeWeight = i / pointsToGenerate;
    const volatility = 0.5 + (timeWeight * 0.5);
    
    spread = Math.round((spread + drift * volatility) * 2) / 2;
    total = Math.round((total + drift * 2 * volatility) * 2) / 2;
    homeML = Math.round(homeML + drift * 10 * volatility);
    awayML = Math.round(awayML - drift * 8 * volatility);
    
    points.push({ timestamp, spread, total, homeML, awayML });
  }
  
  return points;
}

type ChartType = 'spread' | 'total' | 'ml';

export function LineMovementChart({ data, homeTeam, awayTeam, gameTime }: LineMovementChartProps) {
  const [chartType, setChartType] = useState<ChartType>('spread');
  
  const chartData = useMemo(() => {
    if (data && data.length > 0) return data;
    const mockId = `${homeTeam}-${awayTeam}`;
    return generateMockData(mockId, gameTime);
  }, [data, homeTeam, awayTeam, gameTime]);
  
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
  const padding = range * 0.1;
  
  const width = 600;
  const height = 200;
  const paddingLeft = 50;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 40;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  
  const points = values.map((val, i) => {
    const x = paddingLeft + (i / (values.length - 1)) * chartWidth;
    const y = paddingTop + chartHeight - ((val - minVal + padding) / (range + 2 * padding)) * chartHeight;
    return { x, y, value: val, timestamp: chartData[i].timestamp };
  });
  
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  
  const yLabels = [
    { value: maxVal + padding * 0.5, y: paddingTop },
    { value: (maxVal + minVal) / 2, y: paddingTop + chartHeight / 2 },
    { value: minVal - padding * 0.5, y: paddingTop + chartHeight },
  ];
  
  const xLabels = [0, Math.floor(points.length / 2), points.length - 1].map(i => ({
    x: points[i].x,
    label: chartData[i].timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }));
  
  const openValue = values[0];
  const currentValue = values[values.length - 1];
  const movement = currentValue - openValue;
  
  const formatValue = (val: number, type: ChartType) => {
    switch (type) {
      case 'spread': return val > 0 ? `+${val}` : val.toString();
      case 'total': return val.toString();
      case 'ml': return val > 0 ? `+${val}` : val.toString();
    }
  };
  
  const getLabel = (type: ChartType) => {
    switch (type) {
      case 'spread': return 'Spread';
      case 'total': return 'Total';
      case 'ml': return 'Moneyline';
    }
  };
  
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 flex items-center justify-between">
        <h2 className="font-semibold text-zinc-100">Line Movement</h2>
        <div className="flex gap-1">
          {(['spread', 'total', 'ml'] as ChartType[]).map((type) => (
            <button
              key={type}
              onClick={() => setChartType(type)}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                chartType === type
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {getLabel(type)}
            </button>
          ))}
        </div>
      </div>
      
      <div className="px-4 py-3 border-b border-zinc-800/50 flex gap-6">
        <div>
          <span className="text-xs text-zinc-500">Open</span>
          <p className="text-sm font-medium text-zinc-300">{formatValue(openValue, chartType)}</p>
        </div>
        <div>
          <span className="text-xs text-zinc-500">Current</span>
          <p className="text-sm font-medium text-zinc-100">{formatValue(currentValue, chartType)}</p>
        </div>
        <div>
          <span className="text-xs text-zinc-500">Movement</span>
          <p className={`text-sm font-medium ${movement > 0 ? 'text-emerald-400' : movement < 0 ? 'text-red-400' : 'text-zinc-400'}`}>
            {movement > 0 ? '+' : ''}{movement.toFixed(1)}
          </p>
        </div>
      </div>
      
      <div className="p-4">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto" style={{ maxHeight: '200px' }}>
          {yLabels.map((label, i) => (
            <line key={i} x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#3f3f46" strokeWidth="1" strokeDasharray="4 4" />
          ))}
          {yLabels.map((label, i) => (
            <text key={i} x={paddingLeft - 8} y={label.y + 4} textAnchor="end" className="text-xs fill-zinc-500" fontSize="11">
              {formatValue(label.value, chartType)}
            </text>
          ))}
          {xLabels.map((label, i) => (
            <text key={i} x={label.x} y={height - 10} textAnchor="middle" className="text-xs fill-zinc-500" fontSize="11">
              {label.label}
            </text>
          ))}
          <defs>
            <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={`${pathD} L ${points[points.length - 1].x} ${paddingTop + chartHeight} L ${paddingLeft} ${paddingTop + chartHeight} Z`} fill="url(#lineGradient)" />
          <path d={pathD} fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx={points[points.length - 1].x} cy={points[points.length - 1].y} r="4" fill="#10b981" stroke="#0d9488" strokeWidth="2" />
          <circle cx={points[0].x} cy={points[0].y} r="3" fill="#71717a" stroke="#52525b" strokeWidth="2" />
        </svg>
      </div>
      
      <div className="px-4 py-2 bg-zinc-800/30 text-xs text-zinc-500 flex items-center gap-2">
        <span className="w-3 h-3 rounded-full bg-zinc-500 inline-block"></span>
        <span>Opening line</span>
        <span className="mx-2">•</span>
        <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span>
        <span>Current line</span>
      </div>
    </div>
  );
}