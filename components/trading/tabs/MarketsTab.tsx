"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import type {
  MarketData,
  MarketView,
  MatchupInfo,
  GamePriceHistory,
  GamePricePoint,
  TimeRange,
} from "@/lib/trading/types";
import { fetchMatchups, fetchGamePrices } from "@/lib/trading/api";
import { SPORT_COLORS } from "@/lib/trading/config";
import Panel from "../shared/Panel";

interface MarketsTabProps {
  marketData: MarketData | null;
}

const SPORTS = ["NBA", "NHL", "CBB", "MLB", "NFL"];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function formatTime(dateStr: string | null): string {
  if (!dateStr) return "--";
  const d = new Date(dateStr);
  return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function getStatusBadge(status: "ARB" | "CLOSE" | "NO_EDGE", isLive: boolean) {
  if (isLive) {
    return (
      <span className="px-1.5 py-0.5 text-[9px] font-bold bg-emerald-500/20 text-emerald-400 rounded flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        LIVE
      </span>
    );
  }
  switch (status) {
    case "ARB":
      return (
        <span className="px-1.5 py-0.5 text-[9px] font-bold bg-emerald-500/20 text-emerald-400 rounded">
          ARB
        </span>
      );
    case "CLOSE":
      return (
        <span className="px-1.5 py-0.5 text-[9px] font-bold bg-amber-500/20 text-amber-400 rounded">
          CLOSE
        </span>
      );
    default:
      return (
        <span className="px-1.5 py-0.5 text-[9px] font-bold bg-slate-700/50 text-slate-500 rounded">
          --
        </span>
      );
  }
}

// ============================================================================
// PRICE CHART COMPONENT - Bloomberg Terminal Style
// ============================================================================

interface PriceChartProps {
  prices: GamePricePoint[];
  height?: number;
  isLive?: boolean;
}

function parseTimestamp(ts: string): Date {
  // Handle various timestamp formats
  if (!ts) return new Date();

  // If it's already a valid ISO string
  const d = new Date(ts);
  if (!isNaN(d.getTime())) return d;

  // Try parsing "YYYY-MM-DD HH:MM:SS" format
  const parts = ts.match(/(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})/);
  if (parts) {
    return new Date(
      parseInt(parts[1]),
      parseInt(parts[2]) - 1,
      parseInt(parts[3]),
      parseInt(parts[4]),
      parseInt(parts[5]),
      parseInt(parts[6])
    );
  }

  return new Date();
}

function formatChartTime(ts: string, showDate: boolean = false): string {
  const d = parseTimestamp(ts);
  if (showDate) {
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  }
  return d.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  });
}

// Calculate time span in hours from price data
function getTimeSpanHours(prices: GamePricePoint[]): number {
  if (prices.length < 2) return 0;
  const start = parseTimestamp(prices[0].timestamp);
  const end = parseTimestamp(prices[prices.length - 1].timestamp);
  return (end.getTime() - start.getTime()) / (1000 * 60 * 60);
}

// Time range selector component
function TimeRangeSelector({
  value,
  onChange,
  totalHours,
}: {
  value: TimeRange;
  onChange: (range: TimeRange) => void;
  totalHours: number;
}) {
  const ranges: { key: TimeRange; label: string; hours: number }[] = [
    { key: "1H", label: "1H", hours: 1 },
    { key: "3H", label: "3H", hours: 3 },
    { key: "6H", label: "6H", hours: 6 },
    { key: "ALL", label: "ALL", hours: 0 },
  ];

  return (
    <div className="flex items-center gap-1">
      {ranges.map((r) => {
        // Disable if total data is less than this range
        const disabled = r.hours > 0 && totalHours < r.hours * 0.5;
        return (
          <button
            key={r.key}
            onClick={() => !disabled && onChange(r.key)}
            disabled={disabled}
            className={`px-2 py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-colors ${
              value === r.key
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : disabled
                ? "text-slate-700 cursor-not-allowed"
                : "text-slate-500 hover:text-slate-300 hover:bg-slate-800"
            }`}
          >
            {r.label}
          </button>
        );
      })}
      {totalHours > 0 && (
        <span className="ml-2 text-[9px] text-slate-600 font-mono">
          {totalHours.toFixed(1)}h total
        </span>
      )}
    </div>
  );
}

function PriceChart({ prices, height = 280, isLive = false }: PriceChartProps) {
  if (!prices || prices.length < 1) {
    return (
      <div
        className="flex flex-col items-center justify-center text-slate-600 text-[11px] gap-2"
        style={{ height }}
      >
        <div className="w-8 h-8 border-2 border-slate-700 border-t-cyan-500 rounded-full animate-spin" />
        <span>Collecting price data...</span>
      </div>
    );
  }

  const width = 700;
  const padding = { top: 30, right: 80, bottom: 40, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Get all price values for range calculation
  const allPrices = prices.flatMap((p) => [
    p.kalshi_bid || 0,
    p.kalshi_ask || 0,
    p.pm_bid || 0,
    p.pm_ask || 0,
  ].filter(v => v > 0));

  // Round to nearest 10 for clean grid
  const dataMin = Math.min(...allPrices);
  const dataMax = Math.max(...allPrices);
  const minPrice = Math.max(0, Math.floor((dataMin - 5) / 10) * 10);
  const maxPrice = Math.min(100, Math.ceil((dataMax + 5) / 10) * 10);
  const priceRange = maxPrice - minPrice || 10;

  // Helper to convert price to Y coordinate
  const priceToY = (price: number) =>
    padding.top + chartHeight - ((price - minPrice) / priceRange) * chartHeight;

  // Generate chart points for all four lines
  const chartPoints = prices.map((p, i) => ({
    x: padding.left + (prices.length === 1 ? chartWidth / 2 : (i / (prices.length - 1)) * chartWidth),
    kBid: priceToY(p.kalshi_bid || 0),
    kAsk: priceToY(p.kalshi_ask || p.kalshi_bid || 0),
    pmBid: priceToY(p.pm_bid || 0),
    pmAsk: priceToY(p.pm_ask || p.pm_bid || 0),
    data: p,
  }));

  // Generate SVG paths
  const makePath = (points: typeof chartPoints, yKey: keyof typeof chartPoints[0]) =>
    points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p[yKey]}`).join(" ");

  const kBidPath = makePath(chartPoints, "kBid");
  const kAskPath = makePath(chartPoints, "kAsk");
  const pmBidPath = makePath(chartPoints, "pmBid");
  const pmAskPath = makePath(chartPoints, "pmAsk");

  // Generate arb highlight regions
  const arbRegions: { path: string; type: "sellK" | "sellPM" }[] = [];

  for (let i = 0; i < chartPoints.length - 1; i++) {
    const p1 = chartPoints[i];
    const p2 = chartPoints[i + 1];
    const d1 = p1.data;
    const d2 = p2.data;

    // Check for K_Bid > PM_Ask (sell Kalshi, buy PM)
    if ((d1.kalshi_bid > d1.pm_ask) || (d2.kalshi_bid > d2.pm_ask)) {
      const path = `M ${p1.x} ${p1.kBid} L ${p2.x} ${p2.kBid} L ${p2.x} ${p2.pmAsk} L ${p1.x} ${p1.pmAsk} Z`;
      arbRegions.push({ path, type: "sellK" });
    }

    // Check for PM_Bid > K_Ask (sell PM, buy Kalshi)
    if ((d1.pm_bid > d1.kalshi_ask) || (d2.pm_bid > d2.kalshi_ask)) {
      const path = `M ${p1.x} ${p1.pmBid} L ${p2.x} ${p2.pmBid} L ${p2.x} ${p2.kAsk} L ${p1.x} ${p1.kAsk} Z`;
      arbRegions.push({ path, type: "sellPM" });
    }
  }

  // Y-axis grid lines (every 10 cents)
  const yTicks: { value: number; y: number }[] = [];
  for (let v = minPrice; v <= maxPrice; v += 10) {
    yTicks.push({ value: v, y: priceToY(v) });
  }

  // Calculate time span to determine label format
  const timeSpanHours = getTimeSpanHours(prices);
  const showDate = timeSpanHours > 12; // Show date if more than 12 hours of data

  // X-axis time labels (auto-adjust count based on data density)
  const xLabelCount = Math.min(timeSpanHours > 6 ? 7 : 5, prices.length);
  const xLabels = Array.from({ length: xLabelCount }, (_, i) => {
    const idx = prices.length === 1 ? 0 : Math.floor((i / (xLabelCount - 1)) * (prices.length - 1));
    return {
      x: chartPoints[idx]?.x || padding.left,
      label: formatChartTime(prices[idx]?.timestamp || "", showDate),
    };
  });

  // Current values (last point)
  const current = prices[prices.length - 1];
  const currentSpread = (current?.kalshi_bid || 0) - (current?.pm_ask || 0);
  const hasArb = currentSpread > 0 || ((current?.pm_bid || 0) - (current?.kalshi_ask || 0)) > 0;

  return (
    <div className="space-y-3">
      {/* Chart SVG */}
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
        className="transition-all duration-300"
      >
        <defs>
          {/* Gradient for arb regions */}
          <linearGradient id="arbGreenGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0.05" />
          </linearGradient>
          <linearGradient id="arbCyanGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.05" />
          </linearGradient>
        </defs>

        {/* Background */}
        <rect
          x={padding.left}
          y={padding.top}
          width={chartWidth}
          height={chartHeight}
          fill="#080b10"
          rx={4}
        />

        {/* Grid lines */}
        {yTicks.map((tick) => (
          <g key={tick.value}>
            <line
              x1={padding.left}
              y1={tick.y}
              x2={padding.left + chartWidth}
              y2={tick.y}
              stroke="#1a2332"
              strokeWidth={1}
            />
            <text
              x={padding.left - 8}
              y={tick.y + 4}
              fill="#4a5568"
              fontSize={10}
              textAnchor="end"
              fontFamily="monospace"
            >
              {tick.value}¢
            </text>
          </g>
        ))}

        {/* Arb highlight regions */}
        {arbRegions.map((region, i) => (
          <path
            key={i}
            d={region.path}
            fill={region.type === "sellK" ? "url(#arbGreenGrad)" : "url(#arbCyanGrad)"}
            className="transition-opacity duration-300"
          />
        ))}

        {/* Kalshi Bid - Dark Blue Dashed */}
        <path
          d={kBidPath}
          fill="none"
          stroke="#1e40af"
          strokeWidth={2}
          strokeDasharray="6,3"
          className="transition-all duration-300"
        />

        {/* Kalshi Ask - Light Blue Solid */}
        <path
          d={kAskPath}
          fill="none"
          stroke="#3b82f6"
          strokeWidth={2}
          className="transition-all duration-300"
        />

        {/* PM Bid - Dark Green Dashed */}
        <path
          d={pmBidPath}
          fill="none"
          stroke="#166534"
          strokeWidth={2}
          strokeDasharray="6,3"
          className="transition-all duration-300"
        />

        {/* PM Ask - Light Green Solid */}
        <path
          d={pmAskPath}
          fill="none"
          stroke="#22c55e"
          strokeWidth={2}
          className="transition-all duration-300"
        />

        {/* Game start marker (vertical line at start) */}
        {chartPoints.length > 1 && (
          <g>
            <line
              x1={chartPoints[0].x}
              y1={padding.top}
              x2={chartPoints[0].x}
              y2={padding.top + chartHeight}
              stroke="#4a5568"
              strokeWidth={1}
              strokeDasharray="4,4"
            />
            <text
              x={chartPoints[0].x + 4}
              y={padding.top + 12}
              fill="#4a5568"
              fontSize={8}
            >
              START
            </text>
          </g>
        )}

        {/* Current price dots and NOW indicator */}
        {chartPoints.length > 0 && (
          <g className="transition-all duration-300">
            {/* Vertical NOW line */}
            <line
              x1={chartPoints[chartPoints.length - 1].x}
              y1={padding.top}
              x2={chartPoints[chartPoints.length - 1].x}
              y2={padding.top + chartHeight}
              stroke="#06b6d4"
              strokeWidth={1}
              strokeDasharray="2,2"
              opacity={0.5}
            />
            {/* NOW label */}
            <rect
              x={chartPoints[chartPoints.length - 1].x - 15}
              y={padding.top - 12}
              width={30}
              height={14}
              fill="#06b6d4"
              rx={3}
            />
            <text
              x={chartPoints[chartPoints.length - 1].x}
              y={padding.top - 2}
              fill="#000"
              fontSize={8}
              fontWeight="bold"
              textAnchor="middle"
            >
              NOW
            </text>
            {/* Price dots */}
            <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].kBid} r={4} fill="#1e40af" />
            <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].kAsk} r={4} fill="#3b82f6" />
            <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].pmBid} r={4} fill="#166534" />
            <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].pmAsk} r={4} fill="#22c55e" />
          </g>
        )}

        {/* X-axis time labels */}
        {xLabels.map((label, i) => (
          <text
            key={i}
            x={label.x}
            y={height - 10}
            fill="#4a5568"
            fontSize={9}
            textAnchor="middle"
            fontFamily="monospace"
          >
            {label.label}
          </text>
        ))}

        {/* Legend - Right Side */}
        <g transform={`translate(${width - padding.right + 10}, ${padding.top + 10})`}>
          {/* Kalshi Bid */}
          <g transform="translate(0, 0)">
            <line x1={0} y1={0} x2={20} y2={0} stroke="#1e40af" strokeWidth={2} strokeDasharray="4,2" />
            <text x={25} y={4} fill="#64748b" fontSize={9}>K Bid</text>
            <text x={25} y={16} fill="#1e40af" fontSize={10} fontFamily="monospace" fontWeight="bold">
              {current?.kalshi_bid || 0}¢
            </text>
          </g>
          {/* Kalshi Ask */}
          <g transform="translate(0, 35)">
            <line x1={0} y1={0} x2={20} y2={0} stroke="#3b82f6" strokeWidth={2} />
            <text x={25} y={4} fill="#64748b" fontSize={9}>K Ask</text>
            <text x={25} y={16} fill="#3b82f6" fontSize={10} fontFamily="monospace" fontWeight="bold">
              {current?.kalshi_ask || 0}¢
            </text>
          </g>
          {/* PM Bid */}
          <g transform="translate(0, 70)">
            <line x1={0} y1={0} x2={20} y2={0} stroke="#166534" strokeWidth={2} strokeDasharray="4,2" />
            <text x={25} y={4} fill="#64748b" fontSize={9}>PM Bid</text>
            <text x={25} y={16} fill="#166534" fontSize={10} fontFamily="monospace" fontWeight="bold">
              {current?.pm_bid || 0}¢
            </text>
          </g>
          {/* PM Ask */}
          <g transform="translate(0, 105)">
            <line x1={0} y1={0} x2={20} y2={0} stroke="#22c55e" strokeWidth={2} />
            <text x={25} y={4} fill="#64748b" fontSize={9}>PM Ask</text>
            <text x={25} y={16} fill="#22c55e" fontSize={10} fontFamily="monospace" fontWeight="bold">
              {current?.pm_ask || 0}¢
            </text>
          </g>
        </g>

        {/* LIVE indicator */}
        {isLive && (
          <g transform={`translate(${padding.left + 10}, ${padding.top + 10})`}>
            <rect x={0} y={-6} width={50} height={16} fill="#0c1018" fillOpacity={0.9} rx={4} stroke="#10b981" strokeWidth={1} />
            <circle cx={10} cy={2} r={3} fill="#10b981" className="animate-pulse" />
            <text x={18} y={6} fill="#10b981" fontSize={10} fontWeight="bold">LIVE</text>
          </g>
        )}

        {/* Current spread indicator */}
        {hasArb && chartPoints.length > 0 && (
          <g transform={`translate(${chartPoints[chartPoints.length - 1].x - 30}, ${(chartPoints[chartPoints.length - 1].kBid + chartPoints[chartPoints.length - 1].pmAsk) / 2})`}>
            <rect x={-15} y={-10} width={60} height={20} fill="#10b981" fillOpacity={0.2} rx={4} stroke="#10b981" strokeWidth={1} />
            <text x={15} y={5} fill="#10b981" fontSize={11} fontWeight="bold" textAnchor="middle" fontFamily="monospace">
              +{Math.abs(currentSpread)}¢
            </text>
          </g>
        )}
      </svg>
    </div>
  );
}

// ============================================================================
// PRICE INFO PANEL
// ============================================================================

function PriceInfoPanel({ prices, isLive }: { prices: GamePricePoint[]; isLive: boolean }) {
  if (!prices || prices.length === 0) return null;

  const current = prices[prices.length - 1];
  const kBid = current?.kalshi_bid || 0;
  const kAsk = current?.kalshi_ask || 0;
  const pmBid = current?.pm_bid || 0;
  const pmAsk = current?.pm_ask || 0;

  const kSpread = kAsk - kBid;
  const pmSpread = pmAsk - pmBid;

  // Arb calculations
  const sellKEdge = kBid - pmAsk; // Sell Kalshi, Buy PM
  const sellPMEdge = pmBid - kAsk; // Sell PM, Buy Kalshi

  const hasArb = sellKEdge > 0 || sellPMEdge > 0;
  const arbEdge = Math.max(sellKEdge, sellPMEdge, 0);
  const arbDirection = sellKEdge > sellPMEdge ? "Sell Kalshi / Buy PM" : "Sell PM / Buy Kalshi";

  // Estimate max contracts (simplified)
  const maxContracts = Math.min(150, Math.floor(1000 / Math.max(kBid, pmAsk, 1)));

  return (
    <div className="space-y-3">
      {/* Current Prices Table */}
      <div className="panel rounded-lg overflow-hidden">
        <div className="panel-header px-3 py-2 flex items-center justify-between">
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Current Prices</span>
          {isLive && (
            <span className="flex items-center gap-1 text-[10px] text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              UPDATING
            </span>
          )}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-[11px]">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left px-3 py-2 text-slate-500 font-medium">Platform</th>
                <th className="text-right px-3 py-2 text-slate-500 font-medium">Bid</th>
                <th className="text-right px-3 py-2 text-slate-500 font-medium">Ask</th>
                <th className="text-right px-3 py-2 text-slate-500 font-medium">Spread</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/50">
                <td className="px-3 py-2 text-blue-400 font-bold">Kalshi</td>
                <td className="px-3 py-2 text-right font-mono text-blue-300 tabular-nums">{kBid}¢</td>
                <td className="px-3 py-2 text-right font-mono text-blue-400 tabular-nums">{kAsk}¢</td>
                <td className="px-3 py-2 text-right font-mono text-slate-500 tabular-nums">{kSpread}¢</td>
              </tr>
              <tr>
                <td className="px-3 py-2 text-green-400 font-bold">PM US</td>
                <td className="px-3 py-2 text-right font-mono text-green-300 tabular-nums">{pmBid}¢</td>
                <td className="px-3 py-2 text-right font-mono text-green-400 tabular-nums">{pmAsk}¢</td>
                <td className="px-3 py-2 text-right font-mono text-slate-500 tabular-nums">{pmSpread}¢</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Arb Status Panel */}
      <div className={`panel rounded-lg p-4 ${hasArb ? "border border-emerald-500/30 bg-emerald-500/5" : ""}`}>
        <div className="flex items-start justify-between">
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Arb Status</div>
            <div className="flex items-center gap-2">
              {hasArb ? (
                <>
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded text-xs font-bold">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    ARB AVAILABLE
                  </span>
                  <span className="text-slate-400 text-sm">
                    {sellKEdge > 0
                      ? `K_Bid ${kBid}¢ > PM_Ask ${pmAsk}¢ = ${sellKEdge}¢ edge`
                      : `PM_Bid ${pmBid}¢ > K_Ask ${kAsk}¢ = ${sellPMEdge}¢ edge`
                    }
                  </span>
                </>
              ) : (
                <>
                  <span className="px-2 py-1 bg-slate-700/50 text-slate-500 rounded text-xs font-bold">
                    NO EDGE
                  </span>
                  <span className="text-slate-500 text-sm">
                    Waiting for spread to open...
                  </span>
                </>
              )}
            </div>
          </div>

          {hasArb && (
            <div className="text-right">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Edge</div>
              <div className="text-2xl font-mono font-bold text-emerald-400 tabular-nums">
                +{arbEdge}¢
              </div>
            </div>
          )}
        </div>

        {hasArb && (
          <div className="mt-4 pt-3 border-t border-slate-800 grid grid-cols-2 gap-4">
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Direction</div>
              <div className="text-sm text-slate-200 font-mono">{arbDirection}</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Est. Max Contracts</div>
              <div className="text-sm text-slate-200 font-mono">{maxContracts}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// LEAGUE VIEW
// ============================================================================

function LeagueView({
  marketData,
  onSelectLeague,
}: {
  marketData: MarketData | null;
  onSelectLeague: (sport: string) => void;
}) {
  const leagueStats = useMemo(() => {
    if (!marketData) return [];

    return SPORTS.map((sport) => {
      const stats = marketData.match_stats?.[sport];
      const spreads = marketData.spreads?.filter((s) => s.sport === sport) || [];
      const arbCount = spreads.filter((s) => s.status === "ARB").length;

      return {
        sport,
        matched: stats?.matched ?? 0,
        total: stats?.total ?? 0,
        rate: stats?.rate ?? 0,
        arbCount,
        color: SPORT_COLORS[sport] || SPORT_COLORS.DEFAULT,
      };
    }).filter((s) => s.total > 0);
  }, [marketData]);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
      {leagueStats.map((league) => (
        <button
          key={league.sport}
          onClick={() => onSelectLeague(league.sport)}
          className="panel rounded-lg p-4 text-left hover:bg-slate-800/50 transition-all group"
        >
          <div className="flex items-center justify-between mb-3">
            <span
              className="text-lg font-bold"
              style={{ color: league.color }}
            >
              {league.sport}
            </span>
            <svg
              className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">Matched</span>
              <span className="font-mono text-sm text-slate-200 tabular-nums">
                {league.matched}/{league.total}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">Rate</span>
              <span
                className={`font-mono text-sm tabular-nums ${
                  league.rate >= 50
                    ? "text-emerald-400"
                    : league.rate >= 25
                    ? "text-amber-400"
                    : "text-slate-500"
                }`}
              >
                {league.rate.toFixed(0)}%
              </span>
            </div>

            {league.arbCount > 0 && (
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">Arbs</span>
                <span className="font-mono text-sm text-emerald-400 tabular-nums">
                  {league.arbCount}
                </span>
              </div>
            )}
          </div>

          {/* Progress bar */}
          <div className="mt-3 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${league.rate}%`,
                backgroundColor: league.color,
                opacity: 0.7,
              }}
            />
          </div>
        </button>
      ))}

      {leagueStats.length === 0 && (
        <div className="col-span-full text-center py-12 text-slate-600">
          No markets available
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MATCHUP LIST VIEW
// ============================================================================

function MatchupListView({
  sport,
  marketData,
  onSelectGame,
  onBack,
}: {
  sport: string;
  marketData: MarketData | null;
  onSelectGame: (matchup: MatchupInfo) => void;
  onBack: () => void;
}) {
  const [matchups, setMatchups] = useState<MatchupInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchMatchups(sport).then((data) => {
      setMatchups(data);
      setLoading(false);
    });
  }, [sport]);

  // Fallback to spreads data if API not available
  const displayMatchups = useMemo(() => {
    if (matchups.length > 0) return matchups;
    if (!marketData?.spreads) return [];

    // Helper to extract game_id from ticker (KXNBAGAME-26JAN30BKNUTA-BKN -> 26JAN30BKNUTA)
    const extractGameId = (ticker: string, game: string) => {
      if (ticker) {
        const parts = ticker.split("-");
        if (parts.length >= 2) {
          return parts[1]; // Second part is the game_id
        }
      }
      return game;
    };

    // Group by game
    const gameMap = new Map<string, MatchupInfo>();
    marketData.spreads
      .filter((s) => s.sport === sport)
      .forEach((s) => {
        const gameKey = s.game;
        if (!gameMap.has(gameKey)) {
          const gameId = extractGameId(s.ticker, s.game);
          gameMap.set(gameKey, {
            game_id: `${gameId}-${s.team}`,
            sport: s.sport,
            game: s.game,
            teams: [s.team],
            kalshi_price: s.k_bid,
            pm_price: s.pm_ask,
            spread: s.spread,
            status: s.status,
            is_live: false,
            start_time: null,
            ticker: s.ticker,
            pm_slug: s.pm_slug,
          });
        }
      });
    return Array.from(gameMap.values());
  }, [matchups, marketData?.spreads, sport]);

  const sportColor = SPORT_COLORS[sport] || SPORT_COLORS.DEFAULT;

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="p-1.5 rounded hover:bg-slate-800 transition-colors"
        >
          <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="text-lg font-bold" style={{ color: sportColor }}>
          {sport} Markets
        </h2>
        <span className="text-xs text-slate-500 font-mono">
          {displayMatchups.length} matchups
        </span>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-6 h-6 border-2 border-slate-700 border-t-cyan-500 rounded-full animate-spin" />
        </div>
      )}

      {/* Matchups table */}
      {!loading && (
        <Panel title="Matchups">
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left px-3 py-2 text-slate-500 font-medium">Game</th>
                  <th className="text-right px-3 py-2 text-slate-500 font-medium">Kalshi</th>
                  <th className="text-right px-3 py-2 text-slate-500 font-medium">PM US</th>
                  <th className="text-right px-3 py-2 text-slate-500 font-medium">Spread</th>
                  <th className="text-center px-3 py-2 text-slate-500 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {displayMatchups.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-3 py-8 text-center text-slate-600">
                      No matchups found for {sport}
                    </td>
                  </tr>
                )}
                {displayMatchups.map((matchup, idx) => (
                  <tr
                    key={`${matchup.game_id}-${idx}`}
                    onClick={() => onSelectGame(matchup)}
                    className="table-row border-b border-slate-800/50 cursor-pointer hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="px-3 py-3">
                      <div className="font-mono text-slate-200">{matchup.game}</div>
                      {matchup.start_time && !matchup.is_live && (
                        <div className="text-[10px] text-slate-500">
                          Starts {formatTime(matchup.start_time)}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-3 text-right font-mono text-cyan-400 tabular-nums">
                      {matchup.kalshi_price}c
                    </td>
                    <td className="px-3 py-3 text-right font-mono text-violet-400 tabular-nums">
                      {matchup.pm_price}c
                    </td>
                    <td
                      className={`px-3 py-3 text-right font-mono font-bold tabular-nums ${
                        matchup.spread > 0
                          ? "text-emerald-400"
                          : matchup.spread < 0
                          ? "text-red-400"
                          : "text-slate-500"
                      }`}
                    >
                      {matchup.spread > 0 ? "+" : ""}
                      {matchup.spread}c
                    </td>
                    <td className="px-3 py-3 text-center">
                      {getStatusBadge(matchup.status, matchup.is_live)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </div>
  );
}

// ============================================================================
// GAME DETAIL VIEW
// ============================================================================

function GameDetailView({
  matchup,
  onBack,
}: {
  matchup: MatchupInfo;
  onBack: () => void;
}) {
  const [priceHistory, setPriceHistory] = useState<GamePriceHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dataPoints, setDataPoints] = useState(0);
  const [totalDataPoints, setTotalDataPoints] = useState(0);
  const [timeRange, setTimeRange] = useState<TimeRange>("ALL");
  const [gameDuration, setGameDuration] = useState(0);

  // Convert time range to hours for API
  const timeRangeToHours = (range: TimeRange): number => {
    switch (range) {
      case "1H": return 1;
      case "3H": return 3;
      case "6H": return 6;
      case "ALL": return 0;
    }
  };

  // Extract proper game_id from ticker (format: KXNBA-26JAN30BKNUTA-BKN -> 26JAN30BKNUTA)
  const getGameId = useCallback(() => {
    if (matchup.ticker) {
      const tickerParts = matchup.ticker.split("-");
      if (tickerParts.length >= 2) {
        const gameIdPart = tickerParts[1];
        const teamPart = tickerParts[tickerParts.length - 1];
        return `${gameIdPart}-${teamPart}`;
      }
    }
    const team = matchup.teams?.[0] || "";
    return `${matchup.game}-${team}`;
  }, [matchup]);

  const loadPrices = useCallback(async (range: TimeRange = timeRange) => {
    const gameId = getGameId();
    const hours = timeRangeToHours(range);
    // Request more points when zoomed in for detail
    const maxPoints = range === "ALL" ? 500 : range === "6H" ? 800 : 1000;

    console.log("[UI] Fetching prices for:", gameId, "hours:", hours, "maxPoints:", maxPoints);

    try {
      const data = await fetchGamePrices(gameId, hours, maxPoints);
      console.log("[UI] API response:", data);

      if (data && !data.error) {
        setPriceHistory(data);
        setDataPoints(data.data_points || data.prices?.length || 0);
        setTotalDataPoints(data.total_data_points || data.data_points || 0);
        setGameDuration(data.game_duration_hours || 0);
        setError(null);
      } else if (data?.error) {
        setError(data.error);
        setPriceHistory({
          game_id: gameId,
          sport: matchup.sport,
          game: matchup.game,
          team: matchup.teams[0] || "",
          ticker: matchup.ticker,
          pm_slug: matchup.pm_slug,
          is_live: false,
          start_time: null,
          prices: [],
          current_spread: matchup.spread,
          arb_status: matchup.status,
        });
      }
    } catch (e) {
      console.error("[UI] Error fetching prices:", e);
      setError(e instanceof Error ? e.message : "Failed to load prices");
    }

    setLastUpdate(new Date());
    setLoading(false);
  }, [matchup, getGameId, timeRange]);

  // Handle time range change
  const handleTimeRangeChange = useCallback((range: TimeRange) => {
    setTimeRange(range);
    setLoading(true);
    loadPrices(range);
  }, [loadPrices]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    loadPrices();

    // Poll every 5 seconds
    const interval = setInterval(() => loadPrices(timeRange), 5000);
    return () => clearInterval(interval);
  }, [loadPrices, timeRange]);

  const sportColor = SPORT_COLORS[matchup.sport] || SPORT_COLORS.DEFAULT;
  const isLive = dataPoints > 10;
  const hasData = priceHistory?.prices && priceHistory.prices.length > 1;

  return (
    <div className="space-y-3">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-[11px]">
        <button onClick={onBack} className="text-slate-500 hover:text-slate-300 transition-colors">
          Markets
        </button>
        <span className="text-slate-600">/</span>
        <button onClick={onBack} className="text-slate-500 hover:text-slate-300 transition-colors">
          {matchup.sport}
        </button>
        <span className="text-slate-600">/</span>
        <span className="text-slate-300">{matchup.game}</span>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-1.5 rounded hover:bg-slate-800 transition-colors"
          >
            <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <h2 className="text-lg font-bold text-slate-200">{matchup.game}</h2>
            <div className="flex items-center gap-2 text-[10px]">
              <span style={{ color: sportColor }}>{matchup.sport}</span>
              {isLive && (
                <span className="flex items-center gap-1 text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  LIVE
                </span>
              )}
              {lastUpdate && (
                <span className="text-slate-600 ml-2">
                  Updated {lastUpdate.toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Current spread badge */}
        <div className="text-right">
          <div
            className={`text-2xl font-mono font-bold tabular-nums ${
              (priceHistory?.current_spread ?? matchup.spread) > 0
                ? "text-emerald-400"
                : "text-slate-400"
            }`}
          >
            {(priceHistory?.current_spread ?? matchup.spread) > 0 ? "+" : ""}
            {priceHistory?.current_spread ?? matchup.spread}¢
          </div>
          <div className="text-[10px] text-slate-500">Net Spread</div>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-slate-700 border-t-cyan-500 rounded-full animate-spin" />
        </div>
      )}

      {/* Error message */}
      {!loading && error && (
        <div className="panel rounded-lg p-4 border border-amber-500/30 bg-amber-500/5">
          <div className="flex items-center gap-2 text-amber-400 text-sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
          <div className="mt-2 text-[10px] text-slate-500 font-mono">
            Game ID: {matchup.game_id} | Ticker: {matchup.ticker}
          </div>
        </div>
      )}

      {/* Price Chart */}
      {!loading && (
        <Panel
          title="Price History"
          headerRight={
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-slate-500 font-mono">
                {dataPoints}/{totalDataPoints} points
              </span>
              {isLive && (
                <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Auto-refresh 5s
                </span>
              )}
            </div>
          }
        >
          {/* Time Range Selector */}
          <div className="px-4 pt-3 pb-2 border-b border-slate-800 flex items-center justify-between">
            <TimeRangeSelector
              value={timeRange}
              onChange={handleTimeRangeChange}
              totalHours={gameDuration}
            />
            {gameDuration > 0 && (
              <span className="text-[10px] text-slate-500">
                Game duration: {gameDuration.toFixed(1)}h
              </span>
            )}
          </div>

          <div className="p-4">
            {hasData ? (
              <PriceChart
                prices={priceHistory?.prices || []}
                height={320}
                isLive={isLive}
              />
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-slate-500">
                <div className="w-10 h-10 border-2 border-slate-700 border-t-cyan-500 rounded-full animate-spin mb-4" />
                <div className="text-sm">Collecting price data...</div>
                <div className="text-[10px] text-slate-600 mt-1">
                  Data will appear as the bot scans this market
                </div>
              </div>
            )}
          </div>
        </Panel>
      )}

      {/* Price Info Panel - show with current matchup data even if no historical prices */}
      {!loading && (
        <PriceInfoPanel
          prices={hasData ? priceHistory!.prices : [{
            timestamp: new Date().toISOString(),
            kalshi_bid: matchup.kalshi_price,
            kalshi_ask: matchup.kalshi_price + 1,
            pm_bid: matchup.pm_price - 1,
            pm_ask: matchup.pm_price,
            spread: matchup.spread,
          }]}
          isLive={isLive}
        />
      )}

      {/* Market Identifiers */}
      <div className="grid grid-cols-2 gap-3">
        <Panel title="Kalshi Market">
          <div className="p-3 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-slate-500 uppercase">Ticker</span>
              <span className="font-mono text-[11px] text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                {matchup.ticker}
              </span>
            </div>
          </div>
        </Panel>

        <Panel title="Polymarket">
          <div className="p-3 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-slate-500 uppercase">Slug</span>
              <span className="font-mono text-[10px] text-green-400 bg-green-500/10 px-2 py-0.5 rounded truncate max-w-[180px]">
                {matchup.pm_slug}
              </span>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function MarketsTab({ marketData }: MarketsTabProps) {
  const [view, setView] = useState<MarketView>("leagues");
  const [selectedSport, setSelectedSport] = useState<string | null>(null);
  const [selectedMatchup, setSelectedMatchup] = useState<MatchupInfo | null>(null);

  const handleSelectLeague = (sport: string) => {
    setSelectedSport(sport);
    setView("matchups");
  };

  const handleSelectGame = (matchup: MatchupInfo) => {
    setSelectedMatchup(matchup);
    setView("game");
  };

  const handleBack = () => {
    if (view === "game") {
      setSelectedMatchup(null);
      setView("matchups");
    } else if (view === "matchups") {
      setSelectedSport(null);
      setView("leagues");
    }
  };

  return (
    <div className="flex flex-col gap-3 overflow-y-auto scrollbar-thin h-full p-1">
      {/* View transitions */}
      <div
        className={`transition-all duration-200 ${
          view === "leagues" ? "opacity-100" : "opacity-0 hidden"
        }`}
      >
        <LeagueView marketData={marketData} onSelectLeague={handleSelectLeague} />
      </div>

      <div
        className={`transition-all duration-200 ${
          view === "matchups" ? "opacity-100" : "opacity-0 hidden"
        }`}
      >
        {selectedSport && (
          <MatchupListView
            sport={selectedSport}
            marketData={marketData}
            onSelectGame={handleSelectGame}
            onBack={handleBack}
          />
        )}
      </div>

      <div
        className={`transition-all duration-200 ${
          view === "game" ? "opacity-100" : "opacity-0 hidden"
        }`}
      >
        {selectedMatchup && (
          <GameDetailView matchup={selectedMatchup} onBack={handleBack} />
        )}
      </div>

      {/* Timestamp */}
      {view === "leagues" && marketData?.timestamp && (
        <div className="text-[10px] text-slate-600 text-center font-mono mt-2">
          Last updated: {new Date(marketData.timestamp).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
