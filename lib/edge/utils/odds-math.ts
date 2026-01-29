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

// ============================================================================
// EV (Expected Value) Calculation Functions
// ============================================================================

/**
 * Calculate EV% for a bet given the book's odds and fair/true probability
 * EV% = (True Prob × Decimal Payout) - 1
 * Simplified: EV% ≈ True Prob - Implied Prob (for display purposes)
 */
export function calculateEV(bookOdds: number, fairProb: number): number {
  const impliedProb = americanToImplied(bookOdds);
  // EV as percentage points difference
  return (fairProb - impliedProb) * 100;
}

/**
 * Calculate fair probability from a two-way market (removes vig)
 * Returns the no-vig probability for side 1
 */
export function getFairProbTwoWay(odds1: number, odds2: number): { fair1: number; fair2: number; vig: number } {
  const implied1 = americanToImplied(odds1);
  const implied2 = americanToImplied(odds2);
  const total = implied1 + implied2;
  const vig = (total - 1) * 100;
  return {
    fair1: implied1 / total,
    fair2: implied2 / total,
    vig,
  };
}

/**
 * Calculate EV% for a two-way market (spread, ML, total O/U)
 * Uses no-vig fair odds from the same book
 */
export function calculateTwoWayEV(
  targetOdds: number,
  oppositeOdds: number,
  isFirstSide: boolean = true
): number {
  const { fair1, fair2 } = getFairProbTwoWay(targetOdds, oppositeOdds);
  const fairProb = isFirstSide ? fair1 : fair2;
  return calculateEV(targetOdds, fairProb);
}

/**
 * Calculate EV% using market consensus as fair value
 * Compare one book's odds to the market average (more accurate for finding +EV)
 */
export function calculateConsensusEV(
  bookOdds: number,
  allBooksOdds: number[],
  oppositeAllBooksOdds: number[]
): number {
  if (allBooksOdds.length === 0 || oppositeAllBooksOdds.length === 0) {
    return 0;
  }

  // Get median odds across all books
  const medianOdds = median(allBooksOdds);
  const medianOpposite = median(oppositeAllBooksOdds);

  if (medianOdds === undefined || medianOpposite === undefined) {
    return 0;
  }

  // Calculate fair prob from market consensus
  const { fair1 } = getFairProbTwoWay(medianOdds, medianOpposite);

  // EV = fair prob - implied prob at this book
  return calculateEV(bookOdds, fair1);
}

/**
 * Full EV calculation result with all details
 */
export interface EVResult {
  ev: number;           // EV as percentage (e.g., 2.5 means +2.5%)
  fairProb: number;     // True probability (0-1)
  impliedProb: number;  // Book's implied probability (0-1)
  vig: number;          // Vig percentage
  edge: 'positive' | 'negative' | 'neutral';
}

/**
 * Calculate comprehensive EV result for a market
 */
export function calculateFullEV(
  bookOdds: number,
  oppositeOdds: number,
  consensusOdds?: number,
  consensusOpposite?: number
): EVResult {
  const impliedProb = americanToImplied(bookOdds);

  // Use consensus if available, otherwise use book's own odds
  let fairProb: number;
  let vig: number;

  if (consensusOdds !== undefined && consensusOpposite !== undefined) {
    const consensus = getFairProbTwoWay(consensusOdds, consensusOpposite);
    fairProb = consensus.fair1;
    vig = consensus.vig;
  } else {
    const bookFair = getFairProbTwoWay(bookOdds, oppositeOdds);
    fairProb = bookFair.fair1;
    vig = bookFair.vig;
  }

  const ev = (fairProb - impliedProb) * 100;

  return {
    ev,
    fairProb,
    impliedProb,
    vig,
    edge: ev > 1 ? 'positive' : ev < -1 ? 'negative' : 'neutral',
  };
}

/**
 * Format EV for display
 */
export function formatEV(ev: number): string {
  if (Math.abs(ev) < 0.1) return '0%';
  const sign = ev > 0 ? '+' : '';
  return `${sign}${ev.toFixed(1)}%`;
}

/**
 * Get EV color class based on value
 */
export function getEVColor(ev: number): string {
  if (ev >= 3) return 'text-emerald-400';
  if (ev >= 1) return 'text-emerald-400/80';
  if (ev <= -3) return 'text-red-400';
  if (ev <= -1) return 'text-red-400/80';
  return 'text-zinc-500';
}

/**
 * Get EV background tint class
 */
export function getEVBgClass(ev: number): string {
  if (ev >= 3) return 'bg-emerald-500/20 border-emerald-500/40';
  if (ev >= 1) return 'bg-emerald-500/10 border-emerald-500/30';
  if (ev <= -3) return 'bg-red-500/15 border-red-500/30';
  if (ev <= -1) return 'bg-red-500/10 border-red-500/20';
  return 'bg-zinc-800/60 border-zinc-700/50';
}