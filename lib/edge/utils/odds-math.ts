// American odds to implied probability
export function americanToImplied(odds: number): number {
  if (odds > 0) {
    return 100 / (odds + 100);
  }
  return Math.abs(odds) / (Math.abs(odds) + 100);
}

// Implied probability to American odds
export function impliedToAmerican(prob: number): number {
  if (prob >= 0.5) {
    return Math.round(-100 * prob / (1 - prob));
  }
  return Math.round(100 * (1 - prob) / prob);
}

// Remove vig and get true probabilities
export function removeVig(prob1: number, prob2: number): { 
  true1: number; 
  true2: number; 
  vig: number 
} {
  const total = prob1 + prob2;
  const vig = total - 1;
  return {
    true1: prob1 / total,
    true2: prob2 / total,
    vig: vig * 100,
  };
}

// Remove vig from American odds directly
export function removeVigFromAmerican(odds1: number, odds2: number) {
  const implied1 = americanToImplied(odds1);
  const implied2 = americanToImplied(odds2);
  return removeVig(implied1, implied2);
}

// Format American odds for display
export function formatOdds(odds: number | undefined | null): string {
  if (odds === undefined || odds === null) return '-';
  if (odds > 0) return `+${odds}`;
  return odds.toString();
}

// Format probability as percentage
export function formatProb(prob: number, decimals: number = 1): string {
  return `${(prob * 100).toFixed(decimals)}%`;
}

// Calculate edge delta
export function calculateEdgeDelta(omiProb: number, bookImpliedProb: number): number {
  return omiProb - bookImpliedProb;
}

// Format edge delta for display
export function formatEdgeDelta(delta: number): string {
  const pct = (delta * 100).toFixed(1);
  if (delta > 0) return `+${pct}%`;
  return `${pct}%`;
}

// Format spread for display
export function formatSpread(point: number): string {
  if (point > 0) return `+${point}`;
  return point.toString();
}

// ============================================================================
// EdgeScout Helper Functions
// ============================================================================

/**
 * Filter snapshots to a specific time window
 */
export function filterSnapshotsByTime<T extends { snapshot_time: string }>(
  snapshots: T[],
  hoursToAnalyze: number
): T[] {
  const now = new Date();
  const cutoff = new Date(now.getTime() - hoursToAnalyze * 60 * 60 * 1000);
  return snapshots.filter(s => new Date(s.snapshot_time) > cutoff);
}

/**
 * Calculate line movement statistics from snapshots
 */
export function calculateMovements<T extends { snapshot_time: string; line: number | null }>(
  snapshots: T[]
): {
  totalChange: number;
  timeSpanHours: number;
  sameDirection: number;
  total: number;
  velocity: number;
  consistency: number;
} {
  const sorted = [...snapshots]
    .filter(s => s.line !== null)
    .sort((a, b) => new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime());

  if (sorted.length < 2) {
    return { totalChange: 0, timeSpanHours: 0, sameDirection: 0, total: 0, velocity: 0, consistency: 0 };
  }

  const firstLine = sorted[0].line!;
  const lastLine = sorted[sorted.length - 1].line!;
  const totalChange = lastLine - firstLine;

  const firstTime = new Date(sorted[0].snapshot_time).getTime();
  const lastTime = new Date(sorted[sorted.length - 1].snapshot_time).getTime();
  const timeSpanHours = (lastTime - firstTime) / (1000 * 60 * 60);

  // Count movements in same direction as overall trend
  let sameDirection = 0;
  let total = 0;
  for (let i = 1; i < sorted.length; i++) {
    const change = sorted[i].line! - sorted[i - 1].line!;
    if (Math.abs(change) >= 0.25) {
      total++;
      if ((totalChange > 0 && change > 0) || (totalChange < 0 && change < 0)) {
        sameDirection++;
      }
    }
  }

  const velocity = timeSpanHours > 0 ? Math.abs(totalChange) / timeSpanHours : 0;
  const consistency = total > 0 ? sameDirection / total : 0;

  return { totalChange, timeSpanHours, sameDirection, total, velocity, consistency };
}

/**
 * Group items by a key function
 */
export function groupBy<T>(items: T[], keyFn: (item: T) => string): Record<string, T[]> {
  return items.reduce((acc, item) => {
    const key = keyFn(item);
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(item);
    return acc;
  }, {} as Record<string, T[]>);
}

/**
 * Get median value from array of numbers
 */
export function median(arr: number[]): number | undefined {
  if (arr.length === 0) return undefined;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}