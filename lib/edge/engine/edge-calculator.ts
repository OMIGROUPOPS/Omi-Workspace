// EdgeScout 6-Pillar Edge Calculation Engine
// This is the core intelligence layer of OMI Edge

export interface PillarScore {
  score: number;        // 0-100
  signal: 'bullish' | 'bearish' | 'neutral';
  side: 'home' | 'away' | null;
  reason: string;
}

export interface EdgeCalculation {
  totalScore: number;   // 0-100
  confidence: 'PASS' | 'WATCH' | 'EDGE' | 'STRONG' | 'RARE';
  edgeSide: 'home' | 'away' | null;
  pillars: {
    lineMovement: PillarScore;
    juiceAnalysis: PillarScore;
    marketConsensus: PillarScore;
    priceEfficiency: PillarScore;
    steamMoves: PillarScore;
  };
  reasons: string[];
}

export interface OddsSnapshot {
  snapshot_time: string;
  book_key: string;
  outcome_type: string;
  line: number | null;
  odds: number;
}

export interface GameOdds {
  homeTeam: string;
  awayTeam: string;
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

export interface BookOdds {
  [bookKey: string]: GameOdds;
}

// Convert American odds to implied probability
function americanToImplied(odds: number): number {
  if (odds > 0) {
    return 100 / (odds + 100);
  } else {
    return Math.abs(odds) / (Math.abs(odds) + 100);
  }
}

// PILLAR 1: Line Movement Analysis (25% weight)
// Detects reverse line movement - when line moves opposite to expected direction
export function analyzeLineMovement(
  snapshots: OddsSnapshot[],
  currentSpread: number | undefined
): PillarScore {
  if (!snapshots || snapshots.length < 2 || currentSpread === undefined) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Insufficient line history' };
  }

  // Get opening and current spreads
  const spreadSnapshots = snapshots
    .filter(s => s.outcome_type === 'home' && s.line !== null)
    .sort((a, b) => new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime());

  if (spreadSnapshots.length < 2) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Not enough spread data' };
  }

  const openingLine = spreadSnapshots[0].line!;
  const movement = currentSpread - openingLine;
  const absMovement = Math.abs(movement);

  // Significant movement thresholds
  if (absMovement < 0.5) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Line stable (no significant movement)' };
  }

  // Movement toward home (home spread getting worse = more points)
  // means sharp money on away side
  const edgeSide: 'home' | 'away' = movement > 0 ? 'away' : 'home';

  let score = 50;
  let reason = '';

  if (absMovement >= 2) {
    score = 85;
    reason = `Major line move (${movement > 0 ? '+' : ''}${movement.toFixed(1)} pts) - strong action on ${edgeSide}`;
  } else if (absMovement >= 1.5) {
    score = 75;
    reason = `Significant move (${movement > 0 ? '+' : ''}${movement.toFixed(1)} pts) - notable flow on ${edgeSide}`;
  } else if (absMovement >= 1) {
    score = 65;
    reason = `Notable move (${movement > 0 ? '+' : ''}${movement.toFixed(1)} pts) - possible informed action`;
  } else {
    score = 55;
    reason = `Minor move (${movement > 0 ? '+' : ''}${movement.toFixed(1)} pts)`;
  }

  return {
    score,
    signal: score > 60 ? 'bullish' : 'neutral',
    side: score > 55 ? edgeSide : null,
    reason,
  };
}

// PILLAR 2: Juice/Vig Analysis (20% weight)
// Books charge more juice on the side they fear
export function analyzeJuice(
  homeOdds: number | undefined,
  awayOdds: number | undefined
): PillarScore {
  if (homeOdds === undefined || awayOdds === undefined) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Missing odds data' };
  }

  // Standard juice is -110 on both sides
  // If one side is -115 or worse, book is taxing that side
  const homeJuice = Math.abs(homeOdds);
  const awayJuice = Math.abs(awayOdds);
  const juiceDiff = homeJuice - awayJuice;

  if (Math.abs(juiceDiff) < 3) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Balanced juice (-110/-110 or similar)' };
  }

  // Side with LESS juice has edge (book fears the other side)
  const edgeSide: 'home' | 'away' = juiceDiff > 0 ? 'away' : 'home';
  const betterJuice = juiceDiff > 0 ? awayJuice : homeJuice;
  const worseJuice = juiceDiff > 0 ? homeJuice : awayJuice;

  let score = 50 + Math.min(Math.abs(juiceDiff) * 3, 30);
  const reason = `${edgeSide === 'home' ? 'Home' : 'Away'} getting better juice (-${betterJuice} vs -${worseJuice})`;

  return {
    score,
    signal: score > 60 ? 'bullish' : 'neutral',
    side: score > 55 ? edgeSide : null,
    reason,
  };
}

// PILLAR 3: Market Consensus Divergence (20% weight)
// When one book disagrees with the market, opportunity exists
export function analyzeConsensus(
  bookOdds: BookOdds,
  consensusSpread: number | undefined
): PillarScore {
  if (!consensusSpread || Object.keys(bookOdds).length < 2) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Need multiple books for consensus' };
  }

  let maxDeviation = 0;
  let outlierBook = '';
  let outlierLine = 0;

  for (const [book, odds] of Object.entries(bookOdds)) {
    if (odds.spreads?.home?.line !== undefined) {
      const deviation = Math.abs(odds.spreads.home.line - consensusSpread);
      if (deviation > maxDeviation) {
        maxDeviation = deviation;
        outlierBook = book;
        outlierLine = odds.spreads.home.line;
      }
    }
  }

  if (maxDeviation < 0.5) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Books aligned (consensus tight)' };
  }

  // Bet against the outlier's lean
  const edgeSide: 'home' | 'away' = outlierLine > consensusSpread ? 'home' : 'away';
  let score = 50 + Math.min(maxDeviation * 25, 35);
  const reason = `${outlierBook} off consensus by ${maxDeviation.toFixed(1)} pts - opportunity on ${edgeSide}`;

  return {
    score,
    signal: 'bullish',
    side: edgeSide,
    reason,
  };
}

// PILLAR 4: Price Efficiency (20% weight)
// Total vig indicates how sharp/efficient the market is
export function analyzePriceEfficiency(
  homeOdds: number | undefined,
  awayOdds: number | undefined
): PillarScore {
  if (homeOdds === undefined || awayOdds === undefined) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Missing odds for efficiency calc' };
  }

  const homeImplied = americanToImplied(homeOdds);
  const awayImplied = americanToImplied(awayOdds);
  const totalVig = (homeImplied + awayImplied) - 1;
  const vigPercent = totalVig * 100;

  // Standard vig is ~4.5% (from -110/-110)
  // Lower vig = sharper market, less inefficiency
  // Higher vig = more inefficient, potential edge exists

  let score: number;
  let reason: string;

  if (vigPercent < 4) {
    score = 40;
    reason = `Tight market (${vigPercent.toFixed(1)}% vig) - highly efficient, less edge`;
  } else if (vigPercent < 5) {
    score = 50;
    reason = `Standard market (${vigPercent.toFixed(1)}% vig) - normal efficiency`;
  } else if (vigPercent < 6) {
    score = 60;
    reason = `Soft market (${vigPercent.toFixed(1)}% vig) - some inefficiency`;
  } else {
    score = 70 + Math.min((vigPercent - 6) * 5, 20);
    reason = `Wide market (${vigPercent.toFixed(1)}% vig) - significant inefficiency`;
  }

  return {
    score,
    signal: score > 55 ? 'bullish' : score < 45 ? 'bearish' : 'neutral',
    side: null, // Efficiency doesn't indicate a side
    reason,
  };
}

// PILLAR 5: Steam Moves (15% weight)
// Sudden coordinated moves indicate sharp syndicate action
export function analyzeSteamMoves(
  snapshots: OddsSnapshot[],
  hoursToAnalyze: number = 2
): PillarScore {
  if (!snapshots || snapshots.length < 2) {
    return { score: 50, signal: 'neutral', side: null, reason: 'Insufficient data for steam detection' };
  }

  const now = new Date();
  const cutoff = new Date(now.getTime() - hoursToAnalyze * 60 * 60 * 1000);

  const recentSnapshots = snapshots
    .filter(s => s.outcome_type === 'home' && s.line !== null)
    .filter(s => new Date(s.snapshot_time) > cutoff)
    .sort((a, b) => new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime());

  if (recentSnapshots.length < 2) {
    return { score: 50, signal: 'neutral', side: null, reason: 'No recent line movement' };
  }

  const oldestRecent = recentSnapshots[0].line!;
  const newest = recentSnapshots[recentSnapshots.length - 1].line!;
  const recentMove = newest - oldestRecent;
  const absMove = Math.abs(recentMove);

  if (absMove < 0.5) {
    return { score: 50, signal: 'neutral', side: null, reason: 'No steam detected (line stable)' };
  }

  // Steam move = rapid movement in short time
  const edgeSide: 'home' | 'away' = recentMove > 0 ? 'away' : 'home';

  let score: number;
  let reason: string;

  if (absMove >= 1.5) {
    score = 85;
    reason = `Steam move detected! ${absMove.toFixed(1)} pts in ${hoursToAnalyze}h - follow the money on ${edgeSide}`;
  } else if (absMove >= 1) {
    score = 70;
    reason = `Rapid move (${absMove.toFixed(1)} pts in ${hoursToAnalyze}h) - sharp action on ${edgeSide}`;
  } else {
    score = 60;
    reason = `Minor recent move (${absMove.toFixed(1)} pts)`;
  }

  return {
    score,
    signal: score > 65 ? 'bullish' : 'neutral',
    side: score > 60 ? edgeSide : null,
    reason,
  };
}

// MAIN CALCULATION: Combine all pillars
export function calculateEdge(
  snapshots: OddsSnapshot[],
  currentOdds: GameOdds,
  bookOdds: BookOdds,
  consensusSpread?: number
): EdgeCalculation {
  // Calculate each pillar
  const lineMovement = analyzeLineMovement(snapshots, currentOdds.spreads?.home?.line);
  const juiceAnalysis = analyzeJuice(
    currentOdds.spreads?.home?.odds,
    currentOdds.spreads?.away?.odds
  );
  const marketConsensus = analyzeConsensus(bookOdds, consensusSpread);
  const priceEfficiency = analyzePriceEfficiency(
    currentOdds.spreads?.home?.odds,
    currentOdds.spreads?.away?.odds
  );
  const steamMoves = analyzeSteamMoves(snapshots);

  // Weighted sum (weights from plan)
  const totalScore =
    (lineMovement.score * 0.25) +
    (juiceAnalysis.score * 0.20) +
    (marketConsensus.score * 0.20) +
    (priceEfficiency.score * 0.20) +
    (steamMoves.score * 0.15);

  // Determine confidence level
  let confidence: EdgeCalculation['confidence'];
  if (totalScore >= 75) confidence = 'RARE';
  else if (totalScore >= 65) confidence = 'STRONG';
  else if (totalScore >= 55) confidence = 'EDGE';
  else if (totalScore >= 45) confidence = 'WATCH';
  else confidence = 'PASS';

  // Determine edge side by consensus of pillars
  const sides = [lineMovement.side, juiceAnalysis.side, marketConsensus.side, steamMoves.side]
    .filter(Boolean) as ('home' | 'away')[];

  const homeSides = sides.filter(s => s === 'home').length;
  const awaySides = sides.filter(s => s === 'away').length;

  let edgeSide: 'home' | 'away' | null = null;
  if (homeSides > awaySides && homeSides >= 2) edgeSide = 'home';
  else if (awaySides > homeSides && awaySides >= 2) edgeSide = 'away';

  // Collect reasons from pillars with signal
  const reasons: string[] = [];
  if (lineMovement.score > 55) reasons.push(lineMovement.reason);
  if (juiceAnalysis.score > 55) reasons.push(juiceAnalysis.reason);
  if (marketConsensus.score > 55) reasons.push(marketConsensus.reason);
  if (priceEfficiency.score > 55) reasons.push(priceEfficiency.reason);
  if (steamMoves.score > 55) reasons.push(steamMoves.reason);

  if (reasons.length === 0) {
    reasons.push('No significant edge signals detected');
  }

  return {
    totalScore: Math.round(totalScore),
    confidence,
    edgeSide,
    pillars: {
      lineMovement,
      juiceAnalysis,
      marketConsensus,
      priceEfficiency,
      steamMoves,
    },
    reasons,
  };
}

// Quick edge calculation when we only have basic data
export function calculateQuickEdge(
  openingSpread: number | undefined,
  currentSpread: number | undefined,
  homeOdds: number | undefined,
  awayOdds: number | undefined
): { score: number; confidence: EdgeCalculation['confidence']; side: 'home' | 'away' | null } {
  let score = 50;
  let side: 'home' | 'away' | null = null;

  // Line movement component
  if (openingSpread !== undefined && currentSpread !== undefined) {
    const movement = Math.abs(currentSpread - openingSpread);
    if (movement >= 1) {
      score += 15;
      side = currentSpread > openingSpread ? 'away' : 'home';
    } else if (movement >= 0.5) {
      score += 8;
    }
  }

  // Juice component
  if (homeOdds !== undefined && awayOdds !== undefined) {
    const juiceDiff = Math.abs(Math.abs(homeOdds) - Math.abs(awayOdds));
    if (juiceDiff >= 5) {
      score += 10;
      const juiceSide = Math.abs(homeOdds) > Math.abs(awayOdds) ? 'away' : 'home';
      if (!side) side = juiceSide;
    }
  }

  // Determine confidence
  let confidence: EdgeCalculation['confidence'];
  if (score >= 75) confidence = 'RARE';
  else if (score >= 65) confidence = 'STRONG';
  else if (score >= 55) confidence = 'EDGE';
  else if (score >= 45) confidence = 'WATCH';
  else confidence = 'PASS';

  return { score, confidence, side };
}
