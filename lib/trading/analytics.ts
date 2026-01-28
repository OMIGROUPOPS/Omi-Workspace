import type {
  Trade,
  CumulativePnLPoint,
  DrawdownPoint,
  SportVolume,
  HeatmapCell,
  ROIBucket,
  SportProfit,
  FullAnalytics,
} from "./types";
import { ROI_BUCKETS } from "./config";

export function computeBasicStats(trades: Trade[]) {
  const liveTrades = trades.filter(
    (t) => t.execution_mode === "live" && t.status === "SUCCESS"
  );
  const paperTrades = trades.filter(
    (t) => t.execution_mode === "paper" || t.status === "PAPER"
  );
  const failedTrades = trades.filter(
    (t) =>
      t.status === "NO_FILL" || t.status === "UNHEDGED" || t.status === "FAILED"
  );
  const liveAttempts = trades.filter((t) => t.execution_mode === "live");
  const fillRate =
    liveAttempts.length > 0
      ? (liveTrades.length / liveAttempts.length) * 100
      : 0;
  const totalPnL = trades.reduce((sum, t) => {
    if (t.status === "SUCCESS" || t.status === "PAPER")
      return sum + t.expected_profit;
    return sum;
  }, 0);
  const lastSuccessfulTrade = [...trades]
    .filter((t) => t.status === "SUCCESS" || t.status === "PAPER")
    .sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )[0];

  return {
    liveTrades,
    paperTrades,
    failedTrades,
    liveAttempts,
    fillRate,
    totalPnL,
    lastSuccessfulTrade,
    totalTrades: trades.length,
  };
}

export function computeCumulativePnL(trades: Trade[]): CumulativePnLPoint[] {
  const successful = [...trades]
    .filter((t) => t.status === "SUCCESS" || t.status === "PAPER")
    .sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

  let cumulative = 0;
  return successful.map((t) => {
    cumulative += t.expected_profit;
    return { timestamp: new Date(t.timestamp).getTime(), value: cumulative };
  });
}

export function computeDrawdown(trades: Trade[]): DrawdownPoint[] {
  const pnlSeries = computeCumulativePnL(trades);
  if (pnlSeries.length === 0) return [];

  let peak = 0;
  return pnlSeries.map((p) => {
    if (p.value > peak) peak = p.value;
    const dd = peak > 0 ? ((p.value - peak) / peak) * 100 : 0;
    return { timestamp: p.timestamp, drawdown: Math.min(dd, 0) };
  });
}

export function computeMaxDrawdown(trades: Trade[]): number {
  const series = computeDrawdown(trades);
  if (series.length === 0) return 0;
  return Math.min(...series.map((s) => s.drawdown));
}

export function computeWinRate(trades: Trade[]): number {
  const successful = trades.filter(
    (t) => t.status === "SUCCESS" || t.status === "PAPER"
  );
  if (successful.length === 0) return 0;
  const profitable = successful.filter((t) => t.expected_profit > 0);
  return (profitable.length / successful.length) * 100;
}

export function computeAvgProfit(trades: Trade[]): number {
  const successful = trades.filter(
    (t) => t.status === "SUCCESS" || t.status === "PAPER"
  );
  if (successful.length === 0) return 0;
  const total = successful.reduce((s, t) => s + t.expected_profit, 0);
  return total / successful.length;
}

export function computeSharpeApprox(trades: Trade[]): number {
  const successful = trades.filter(
    (t) => t.status === "SUCCESS" || t.status === "PAPER"
  );
  if (successful.length < 2) return 0;

  const profits = successful.map((t) => t.expected_profit);
  const mean = profits.reduce((s, v) => s + v, 0) / profits.length;
  const variance =
    profits.reduce((s, v) => s + (v - mean) ** 2, 0) / (profits.length - 1);
  const stddev = Math.sqrt(variance);
  if (stddev === 0) return 0;

  return (mean / stddev) * Math.sqrt(profits.length);
}

export function computeVolumeBySport(trades: Trade[]): SportVolume[] {
  const map = new Map<string, { kalshi: number; pm: number }>();

  for (const t of trades) {
    const sport = t.sport || "Unknown";
    if (!map.has(sport)) map.set(sport, { kalshi: 0, pm: 0 });
    const entry = map.get(sport)!;
    entry.kalshi += t.k_fill_count || 0;
    entry.pm += t.pm_fill_count || 0;
  }

  return Array.from(map.entries())
    .map(([sport, vol]) => ({ sport, ...vol }))
    .sort((a, b) => b.kalshi + b.pm - (a.kalshi + a.pm));
}

export function computeHeatmapData(trades: Trade[]): HeatmapCell[] {
  const map = new Map<string, number>();

  for (const t of trades) {
    const sport = t.sport || "Unknown";
    const hour = new Date(t.timestamp).getHours();
    const key = `${sport}-${hour}`;
    map.set(key, (map.get(key) || 0) + 1);
  }

  const sports = [...new Set(trades.map((t) => t.sport || "Unknown"))];
  const cells: HeatmapCell[] = [];

  for (const sport of sports) {
    for (let hour = 0; hour < 24; hour++) {
      const key = `${sport}-${hour}`;
      cells.push({ sport, hour, count: map.get(key) || 0 });
    }
  }

  return cells;
}

export function computeROIDistribution(trades: Trade[]): ROIBucket[] {
  const successful = trades.filter(
    (t) => t.status === "SUCCESS" || t.status === "PAPER"
  );

  return ROI_BUCKETS.map((bucket) => ({
    range: bucket.range,
    min: bucket.min,
    max: bucket.max,
    count: successful.filter((t) => t.roi >= bucket.min && t.roi < bucket.max)
      .length,
  }));
}

export function computeProfitBySport(trades: Trade[]): SportProfit[] {
  const map = new Map<string, { profit: number; count: number }>();

  for (const t of trades) {
    if (t.status !== "SUCCESS" && t.status !== "PAPER") continue;
    const sport = t.sport || "Unknown";
    if (!map.has(sport)) map.set(sport, { profit: 0, count: 0 });
    const entry = map.get(sport)!;
    entry.profit += t.expected_profit;
    entry.count += 1;
  }

  return Array.from(map.entries())
    .map(([sport, data]) => ({ sport, ...data }))
    .sort((a, b) => b.profit - a.profit);
}

export function computeTradesByHour(trades: Trade[]): number[] {
  const hours = new Array(24).fill(0);
  for (const t of trades) {
    const hour = new Date(t.timestamp).getHours();
    hours[hour]++;
  }
  return hours;
}

export function computeFullAnalytics(trades: Trade[]): FullAnalytics {
  const basic = computeBasicStats(trades);
  return {
    ...basic,
    winRate: computeWinRate(trades),
    avgProfit: computeAvgProfit(trades),
    sharpe: computeSharpeApprox(trades),
    maxDrawdown: computeMaxDrawdown(trades),
    cumulativePnL: computeCumulativePnL(trades),
    drawdownSeries: computeDrawdown(trades),
    volumeBySport: computeVolumeBySport(trades),
    heatmapData: computeHeatmapData(trades),
    roiDistribution: computeROIDistribution(trades),
    profitBySport: computeProfitBySport(trades),
    tradesByHour: computeTradesByHour(trades),
  };
}
