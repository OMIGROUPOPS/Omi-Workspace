// EdgeScout 5-Pillar Framework - CEQ (Composite Edge Quotient) Calculator
// This is the core edge detection engine for OMI Edge

import type { OddsSnapshot } from './edge-calculator';

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface PillarVariable {
  name: string;           // Variable identifier (FDV, MMI, SBI, etc.)
  value: number;          // Raw calculated value
  score: number;          // 0-100 contribution to pillar score
  available: boolean;     // Has data to calculate?
  reason: string;         // Human-readable explanation
}

export interface PillarResult {
  score: number;          // 0-100, 50 = neutral
  weight: number;         // Dynamic weight for this pillar (0-1)
  variables: PillarVariable[];
}

export type CEQConfidence = 'PASS' | 'WATCH' | 'EDGE' | 'STRONG' | 'RARE';
export type MarketSide = 'home' | 'away' | 'over' | 'under';

export interface CEQResult {
  ceq: number;                    // 0-100, 50 = no edge
  confidence: CEQConfidence;
  side: MarketSide | null;        // Favored side
  pillars: {
    marketEfficiency: PillarResult;
    playerUtilization: PillarResult;
    gameEnvironment: PillarResult;
    matchupDynamics: PillarResult;
    sentiment: PillarResult;
  };
  topDrivers: string[];           // Top 3 reasons for the score
}

// Extended snapshot with game_id for grouping
export interface ExtendedOddsSnapshot extends OddsSnapshot {
  game_id?: string;
  market?: string;
}

// ============================================================================
// CEQ Confidence Thresholds (from plan)
// ============================================================================
// 50% = No edge (market efficient)
// <45% = Edge on OTHER side
// 45-55% = PASS (no actionable edge)
// 56-65% = WATCH (monitor for movement)
// 66-75% = EDGE (actionable)
// 76-85% = STRONG (high confidence)
// 86%+ = RARE (exceptional opportunity)

function getCEQConfidence(ceq: number): CEQConfidence {
  if (ceq >= 86) return 'RARE';
  if (ceq >= 76) return 'STRONG';
  if (ceq >= 66) return 'EDGE';
  if (ceq >= 56) return 'WATCH';
  return 'PASS';
}

// ============================================================================
// PILLAR 1: MARKET EFFICIENCY (Primary - calculable now)
// Variables: FDV, MMI, SBI
// ============================================================================

/**
 * FDV (Fair Delta Value)
 * Measures difference between opening line and current line
 * Positive delta = line moved against this side = edge signal
 */
function calculateFDV(openingLine: number | undefined, currentLine: number | undefined): PillarVariable {
  if (openingLine === undefined || currentLine === undefined) {
    return {
      name: 'FDV',
      value: 0,
      score: 50,
      available: false,
      reason: 'No opening line data available',
    };
  }

  const delta = currentLine - openingLine;
  const absDelta = Math.abs(delta);

  // Map delta to 0-100 score
  // Positive delta = line moved against this side (getting more points)
  // This means sharps bet the OTHER side
  let score: number;
  let reason: string;

  if (absDelta < 0.5) {
    score = 50;
    reason = 'Line stable (no significant movement)';
  } else if (delta >= 2) {
    // Line moved 2+ pts against this side - strong edge on opposite
    score = 80;
    reason = `Line moved +${delta.toFixed(1)} pts - strong sharp action opposite`;
  } else if (delta >= 1) {
    score = 65;
    reason = `Line moved +${delta.toFixed(1)} pts - moderate sharp signal`;
  } else if (delta >= 0.5) {
    score = 57;
    reason = `Line moved +${delta.toFixed(1)} pts - slight movement`;
  } else if (delta <= -2) {
    // Line moved 2+ pts toward this side - edge on THIS side
    score = 20;
    reason = `Line moved ${delta.toFixed(1)} pts toward this side - strong edge`;
  } else if (delta <= -1) {
    score = 35;
    reason = `Line moved ${delta.toFixed(1)} pts - moderate edge this side`;
  } else {
    score = 43;
    reason = `Line moved ${delta.toFixed(1)} pts - slight edge this side`;
  }

  return {
    name: 'FDV',
    value: delta,
    score,
    available: true,
    reason,
  };
}

/**
 * MMI (Market Momentum Index)
 * Measures velocity and consistency of line movement
 * Fast, consistent movement = high MMI = trending bias
 */
function calculateMMI(
  snapshots: ExtendedOddsSnapshot[],
  hoursToAnalyze: number = 4
): PillarVariable {
  if (!snapshots || snapshots.length < 2) {
    return {
      name: 'MMI',
      value: 0,
      score: 50,
      available: false,
      reason: 'Insufficient snapshot history',
    };
  }

  const now = new Date();
  const cutoff = new Date(now.getTime() - hoursToAnalyze * 60 * 60 * 1000);

  // Filter to recent snapshots with line data
  const recentSnapshots = snapshots
    .filter(s => s.line !== null && s.line !== undefined)
    .filter(s => new Date(s.snapshot_time) > cutoff)
    .sort((a, b) => new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime());

  if (recentSnapshots.length < 2) {
    return {
      name: 'MMI',
      value: 0,
      score: 50,
      available: false,
      reason: `No recent data in last ${hoursToAnalyze}h`,
    };
  }

  // Calculate movements
  const movements: { direction: number; magnitude: number }[] = [];
  for (let i = 1; i < recentSnapshots.length; i++) {
    const prev = recentSnapshots[i - 1].line!;
    const curr = recentSnapshots[i].line!;
    const change = curr - prev;
    if (Math.abs(change) >= 0.25) {
      movements.push({
        direction: change > 0 ? 1 : -1,
        magnitude: Math.abs(change),
      });
    }
  }

  if (movements.length === 0) {
    return {
      name: 'MMI',
      value: 0,
      score: 50,
      available: true,
      reason: 'No significant movement in analysis window',
    };
  }

  // Calculate total change and consistency
  const firstLine = recentSnapshots[0].line!;
  const lastLine = recentSnapshots[recentSnapshots.length - 1].line!;
  const totalChange = lastLine - firstLine;
  const timeSpanHours = (new Date(recentSnapshots[recentSnapshots.length - 1].snapshot_time).getTime() -
    new Date(recentSnapshots[0].snapshot_time).getTime()) / (1000 * 60 * 60);

  // Velocity: points per hour
  const velocity = timeSpanHours > 0 ? Math.abs(totalChange) / timeSpanHours : 0;

  // Consistency: how many movements went the same direction
  const sameDirection = movements.filter(m =>
    (totalChange > 0 && m.direction > 0) || (totalChange < 0 && m.direction < 0)
  ).length;
  const consistency = movements.length > 0 ? sameDirection / movements.length : 0;

  // Calculate score: high velocity + high consistency = strong momentum signal
  const velocityScore = Math.min(velocity * 15, 30); // Cap at 30 pts
  const consistencyBonus = consistency * velocityScore;
  const rawScore = 50 + velocityScore + consistencyBonus;
  const score = Math.min(Math.max(Math.round(rawScore), 0), 100);

  const direction = totalChange > 0 ? 'up' : 'down';
  const reason = velocity > 0.5
    ? `Strong momentum ${direction} (${velocity.toFixed(2)} pts/hr, ${Math.round(consistency * 100)}% consistent)`
    : `Mild movement ${direction} over ${hoursToAnalyze}h`;

  return {
    name: 'MMI',
    value: velocity * (totalChange > 0 ? 1 : -1),
    score,
    available: true,
    reason,
  };
}

/**
 * SBI (Sentiment Bias Index)
 * Compares juice across books to detect sharp action
 * If one book has worse juice than market, sharps might be on the other side
 */
function calculateSBI(
  bookOdds: number | undefined,
  consensusOdds: number | undefined,
  allBooksOdds: number[]
): PillarVariable {
  if (bookOdds === undefined || consensusOdds === undefined || allBooksOdds.length === 0) {
    return {
      name: 'SBI',
      value: 0,
      score: 50,
      available: false,
      reason: 'Insufficient odds data for comparison',
    };
  }

  // Compare this book's juice to consensus
  // More negative = more juice (worse for bettor)
  const bookJuice = Math.abs(bookOdds);
  const consensusJuice = Math.abs(consensusOdds);
  const juiceDiff = bookJuice - consensusJuice;

  // Also check variance across books
  const allJuice = allBooksOdds.map(o => Math.abs(o));
  const avgJuice = allJuice.reduce((a, b) => a + b, 0) / allJuice.length;
  const maxJuice = Math.max(...allJuice);
  const minJuice = Math.min(...allJuice);
  const spread = maxJuice - minJuice;

  let score: number;
  let reason: string;

  // Higher juice at this book = book fears this side = potential edge on opposite
  if (juiceDiff > 10) {
    score = 30;
    reason = `Book charging ${juiceDiff.toFixed(0)} extra juice - sharps likely opposite`;
  } else if (juiceDiff > 5) {
    score = 40;
    reason = `Above-market juice (+${juiceDiff.toFixed(0)}) - some sharp concern`;
  } else if (juiceDiff < -10) {
    score = 70;
    reason = `Book offering value (${juiceDiff.toFixed(0)} less juice) - potential edge`;
  } else if (juiceDiff < -5) {
    score = 60;
    reason = `Slight value (-${Math.abs(juiceDiff).toFixed(0)} juice) - monitoring`;
  } else if (spread > 15) {
    score = 55;
    reason = `High market spread (${spread.toFixed(0)}) - inefficiency detected`;
  } else {
    score = 50;
    reason = 'Juice aligned with market consensus';
  }

  return {
    name: 'SBI',
    value: juiceDiff,
    score,
    available: true,
    reason,
  };
}

/**
 * Calculate Market Efficiency Pillar
 * Combines FDV, MMI, and SBI
 */
function calculateMarketEfficiencyPillar(
  openingLine: number | undefined,
  currentLine: number | undefined,
  snapshots: ExtendedOddsSnapshot[],
  bookOdds: number | undefined,
  consensusOdds: number | undefined,
  allBooksOdds: number[]
): PillarResult {
  const fdv = calculateFDV(openingLine, currentLine);
  const mmi = calculateMMI(snapshots);
  const sbi = calculateSBI(bookOdds, consensusOdds, allBooksOdds);

  const variables = [fdv, mmi, sbi];
  const availableVars = variables.filter(v => v.available);

  // Dynamic weight based on available data
  let weight = 0;
  if (availableVars.length === 3) weight = 1.0;
  else if (availableVars.length === 2) weight = 0.7;
  else if (availableVars.length === 1) weight = 0.4;
  else weight = 0.1;

  // Calculate weighted average of available variables
  // FDV is most important (50%), then MMI (30%), then SBI (20%)
  let score = 50;
  if (availableVars.length > 0) {
    const fdvWeight = fdv.available ? 0.5 : 0;
    const mmiWeight = mmi.available ? 0.3 : 0;
    const sbiWeight = sbi.available ? 0.2 : 0;
    const totalWeight = fdvWeight + mmiWeight + sbiWeight;

    if (totalWeight > 0) {
      score = (
        (fdv.available ? fdv.score * fdvWeight : 0) +
        (mmi.available ? mmi.score * mmiWeight : 0) +
        (sbi.available ? sbi.score * sbiWeight : 0)
      ) / totalWeight;
    }
  }

  return {
    score: Math.round(score),
    weight,
    variables,
  };
}

// ============================================================================
// PILLAR 2: PLAYER UTILIZATION (Props only - N/A initially)
// ============================================================================

function calculatePlayerUtilizationPillar(): PillarResult {
  return {
    score: 50,
    weight: 0,
    variables: [
      { name: 'UVI', value: 0, score: 50, available: false, reason: 'Utilization data not available' },
      { name: 'RER', value: 0, score: 50, available: false, reason: 'Regression data not available' },
      { name: 'Z-Score', value: 0, score: 50, available: false, reason: 'Baseline stats not available' },
    ],
  };
}

// ============================================================================
// PILLAR 3: GAME ENVIRONMENT (N/A initially)
// ============================================================================

function calculateGameEnvironmentPillar(): PillarResult {
  return {
    score: 50,
    weight: 0,
    variables: [
      { name: 'PVI', value: 0, score: 50, available: false, reason: 'Pace data not available' },
      { name: 'TIR', value: 0, score: 50, available: false, reason: 'Tempo data not available' },
      { name: 'EPA', value: 0, score: 50, available: false, reason: 'Play-by-play not available' },
    ],
  };
}

// ============================================================================
// PILLAR 4: MATCHUP DYNAMICS (N/A initially)
// ============================================================================

function calculateMatchupDynamicsPillar(): PillarResult {
  return {
    score: 50,
    weight: 0,
    variables: [
      { name: 'DVA', value: 0, score: 50, available: false, reason: 'Defense stats not available' },
      { name: 'HPR', value: 0, score: 50, available: false, reason: 'Historical patterns not available' },
      { name: 'OVI', value: 0, score: 50, available: false, reason: 'Outcome volatility not available' },
    ],
  };
}

// ============================================================================
// PILLAR 5: SENTIMENT & CONTEXTUAL (Partial)
// ============================================================================

function calculateSentimentPillar(
  snapshots: ExtendedOddsSnapshot[],
  bookOdds: number | undefined,
  consensusOdds: number | undefined,
  allBooksOdds: number[]
): PillarResult {
  // Re-use SBI calculation for sentiment
  const sbi = calculateSBI(bookOdds, consensusOdds, allBooksOdds);

  // Calculate a simplified MMI for liquidity signals
  const mmi = calculateMMI(snapshots, 2); // Last 2 hours

  const variables = [
    sbi,
    mmi,
    { name: 'Liquidity', value: 0, score: 50, available: false, reason: 'Volume data not available' },
  ];

  const availableVars = variables.filter(v => v.available);
  const weight = availableVars.length > 0 ? 0.3 : 0;

  let score = 50;
  if (availableVars.length > 0) {
    score = availableVars.reduce((acc, v) => acc + v.score, 0) / availableVars.length;
  }

  return {
    score: Math.round(score),
    weight,
    variables,
  };
}

// ============================================================================
// MAIN CEQ CALCULATION
// ============================================================================

export function calculateCEQ(
  marketType: 'spread' | 'h2h' | 'total',
  side: MarketSide,
  bookOdds: number | undefined,
  openingLine: number | undefined,
  currentLine: number | undefined,
  snapshots: ExtendedOddsSnapshot[],
  allBooksOdds: number[],
  consensusOdds: number | undefined
): CEQResult {
  // Calculate all pillars
  const marketEfficiency = calculateMarketEfficiencyPillar(
    openingLine,
    currentLine,
    snapshots,
    bookOdds,
    consensusOdds,
    allBooksOdds
  );
  const playerUtilization = calculatePlayerUtilizationPillar();
  const gameEnvironment = calculateGameEnvironmentPillar();
  const matchupDynamics = calculateMatchupDynamicsPillar();
  const sentiment = calculateSentimentPillar(snapshots, bookOdds, consensusOdds, allBooksOdds);

  // Calculate weighted CEQ from all pillars
  const pillars = [marketEfficiency, playerUtilization, gameEnvironment, matchupDynamics, sentiment];
  const totalWeight = pillars.reduce((acc, p) => acc + p.weight, 0);

  let ceq = 50;
  if (totalWeight > 0) {
    ceq = pillars.reduce((acc, p) => acc + p.score * p.weight, 0) / totalWeight;
  }

  ceq = Math.round(Math.min(Math.max(ceq, 0), 100));

  // Determine confidence
  const confidence = getCEQConfidence(ceq);

  // Determine side (if CEQ indicates edge)
  let edgeSide: MarketSide | null = null;
  if (ceq < 45) {
    // Edge on OTHER side
    if (marketType === 'total') {
      edgeSide = side === 'over' ? 'under' : 'over';
    } else {
      edgeSide = side === 'home' ? 'away' : 'home';
    }
  } else if (ceq >= 56) {
    // Edge on THIS side
    edgeSide = side;
  }

  // Collect top drivers (reasons with significant scores)
  const topDrivers: string[] = [];
  const allVars = [
    ...marketEfficiency.variables,
    ...sentiment.variables,
  ].filter(v => v.available && Math.abs(v.score - 50) >= 5);

  // Sort by deviation from neutral (50)
  allVars.sort((a, b) => Math.abs(b.score - 50) - Math.abs(a.score - 50));

  // Take top 3
  for (const v of allVars.slice(0, 3)) {
    topDrivers.push(`${v.name}: ${v.reason}`);
  }

  if (topDrivers.length === 0) {
    topDrivers.push('No significant edge signals detected');
  }

  return {
    ceq,
    confidence,
    side: edgeSide,
    pillars: {
      marketEfficiency,
      playerUtilization,
      gameEnvironment,
      matchupDynamics,
      sentiment,
    },
    topDrivers,
  };
}

// ============================================================================
// GAME CEQ - Calculate CEQ for all markets of a game
// ============================================================================

export interface GameCEQ {
  spreads?: {
    home: CEQResult;
    away: CEQResult;
  };
  h2h?: {
    home: CEQResult;
    away: CEQResult;
  };
  totals?: {
    over: CEQResult;
    under: CEQResult;
  };
  bestEdge: {
    market: 'spread' | 'h2h' | 'total';
    side: MarketSide;
    ceq: number;
    confidence: CEQConfidence;
  } | null;
}

export interface GameOddsData {
  spreads?: {
    home: { line: number; odds: number };
    away: { line: number; odds: number };
  };
  h2h?: {
    home: number;
    away: number;
  };
  totals?: {
    line: number;
    over: number;
    under: number;
  };
}

export function calculateGameCEQ(
  gameOdds: GameOddsData,
  openingLines: {
    spreads?: { home: number; away: number };
    h2h?: { home: number; away: number };
    totals?: { over: number; under: number };
  },
  snapshots: ExtendedOddsSnapshot[],
  allBooksOdds: {
    spreads?: { home: number[]; away: number[] };
    h2h?: { home: number[]; away: number[] };
    totals?: { over: number[]; under: number[] };
  },
  consensusOdds: {
    spreads?: { home: number; away: number };
    h2h?: { home: number; away: number };
    totals?: { over: number; under: number };
  }
): GameCEQ {
  const result: GameCEQ = { bestEdge: null };

  // Filter snapshots by market type
  const spreadSnapshots = snapshots.filter(s => s.market === 'spreads' && s.outcome_type === 'home');
  const h2hSnapshots = snapshots.filter(s => s.market === 'h2h' && s.outcome_type === 'home');
  const totalSnapshots = snapshots.filter(s => s.market === 'totals' && (s.outcome_type === 'Over' || s.outcome_type === 'over'));

  // Calculate spreads CEQ
  if (gameOdds.spreads) {
    result.spreads = {
      home: calculateCEQ(
        'spread',
        'home',
        gameOdds.spreads.home.odds,
        openingLines.spreads?.home,
        gameOdds.spreads.home.line,
        spreadSnapshots,
        allBooksOdds.spreads?.home || [],
        consensusOdds.spreads?.home
      ),
      away: calculateCEQ(
        'spread',
        'away',
        gameOdds.spreads.away.odds,
        openingLines.spreads?.away,
        gameOdds.spreads.away.line,
        spreadSnapshots,
        allBooksOdds.spreads?.away || [],
        consensusOdds.spreads?.away
      ),
    };
  }

  // Calculate h2h CEQ
  if (gameOdds.h2h) {
    result.h2h = {
      home: calculateCEQ(
        'h2h',
        'home',
        gameOdds.h2h.home,
        openingLines.h2h?.home,
        undefined,
        h2hSnapshots,
        allBooksOdds.h2h?.home || [],
        consensusOdds.h2h?.home
      ),
      away: calculateCEQ(
        'h2h',
        'away',
        gameOdds.h2h.away,
        openingLines.h2h?.away,
        undefined,
        h2hSnapshots,
        allBooksOdds.h2h?.away || [],
        consensusOdds.h2h?.away
      ),
    };
  }

  // Calculate totals CEQ
  if (gameOdds.totals) {
    result.totals = {
      over: calculateCEQ(
        'total',
        'over',
        gameOdds.totals.over,
        openingLines.totals?.over,
        gameOdds.totals.line,
        totalSnapshots,
        allBooksOdds.totals?.over || [],
        consensusOdds.totals?.over
      ),
      under: calculateCEQ(
        'total',
        'under',
        gameOdds.totals.under,
        openingLines.totals?.under,
        gameOdds.totals.line,
        totalSnapshots,
        allBooksOdds.totals?.under || [],
        consensusOdds.totals?.under
      ),
    };
  }

  // Find best edge across all markets
  const candidates: { market: 'spread' | 'h2h' | 'total'; side: MarketSide; ceq: number; confidence: CEQConfidence }[] = [];

  if (result.spreads) {
    if (result.spreads.home.confidence !== 'PASS') {
      candidates.push({ market: 'spread', side: 'home', ceq: result.spreads.home.ceq, confidence: result.spreads.home.confidence });
    }
    if (result.spreads.away.confidence !== 'PASS') {
      candidates.push({ market: 'spread', side: 'away', ceq: result.spreads.away.ceq, confidence: result.spreads.away.confidence });
    }
  }

  if (result.h2h) {
    if (result.h2h.home.confidence !== 'PASS') {
      candidates.push({ market: 'h2h', side: 'home', ceq: result.h2h.home.ceq, confidence: result.h2h.home.confidence });
    }
    if (result.h2h.away.confidence !== 'PASS') {
      candidates.push({ market: 'h2h', side: 'away', ceq: result.h2h.away.ceq, confidence: result.h2h.away.confidence });
    }
  }

  if (result.totals) {
    if (result.totals.over.confidence !== 'PASS') {
      candidates.push({ market: 'total', side: 'over', ceq: result.totals.over.ceq, confidence: result.totals.over.confidence });
    }
    if (result.totals.under.confidence !== 'PASS') {
      candidates.push({ market: 'total', side: 'under', ceq: result.totals.under.ceq, confidence: result.totals.under.confidence });
    }
  }

  // Sort by CEQ (highest first) and take best
  candidates.sort((a, b) => b.ceq - a.ceq);
  if (candidates.length > 0) {
    result.bestEdge = candidates[0];
  }

  return result;
}

// ============================================================================
// Helper: Group snapshots by game_id
// ============================================================================

export function groupSnapshotsByGame(snapshots: ExtendedOddsSnapshot[]): Record<string, ExtendedOddsSnapshot[]> {
  return snapshots.reduce((acc, snapshot) => {
    const gameId = snapshot.game_id || 'unknown';
    if (!acc[gameId]) {
      acc[gameId] = [];
    }
    acc[gameId].push(snapshot);
    return acc;
  }, {} as Record<string, ExtendedOddsSnapshot[]>);
}
