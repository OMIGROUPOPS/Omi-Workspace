// EdgeScout 6-Pillar Framework - CEQ (Composite Edge Quotient) Calculator
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

// ============================================================================
// IP Edge Signal Tiers (Implied Probability Edge)
// ============================================================================
// Edge = abs(fair - book) * 3% per point (industry standard)
// These labels are used across graded games and live game detail pages.

export type EdgeSignal = 'NO EDGE' | 'LOW EDGE' | 'MID EDGE' | 'HIGH EDGE' | 'MAX EDGE';

export function getEdgeSignal(edgePct: number): EdgeSignal {
  const ae = Math.abs(edgePct);
  if (ae >= 8) return 'MAX EDGE';
  if (ae >= 5) return 'HIGH EDGE';
  if (ae >= 3) return 'MID EDGE';
  if (ae >= 1) return 'LOW EDGE';
  return 'NO EDGE';
}

/** Map IP edge % to confidence % via linear interpolation within bands. */
export function edgeToConfidence(edgePct: number): number {
  const ae = Math.abs(edgePct);
  if (ae < 1)  return Math.round(50 + ae * 4);            // 0→50, 1→54
  if (ae < 3)  return Math.round(55 + (ae - 1) * 2);      // 1→55, 3→59
  if (ae < 5)  return Math.round(60 + (ae - 3) * 2.5);    // 3→60, 5→65
  if (ae < 8)  return Math.round(66 + (ae - 5) * 4 / 3);  // 5→66, 8→70
  return Math.min(75, Math.round(71 + (ae - 8) * 0.5));   // 8→71, capped at 75
}

/** Color class for edge signal tier. */
export function getEdgeSignalColor(signal: EdgeSignal): string {
  switch (signal) {
    case 'MAX EDGE':  return 'text-emerald-400';
    case 'HIGH EDGE': return 'text-cyan-400';
    case 'MID EDGE':  return 'text-amber-400';
    case 'LOW EDGE':  return 'text-zinc-400';
    default:          return 'text-zinc-500';
  }
}

/** Background color class for edge signal tier badges. */
export function getEdgeSignalBg(signal: EdgeSignal): string {
  switch (signal) {
    case 'MAX EDGE':  return 'bg-emerald-400/10';
    case 'HIGH EDGE': return 'bg-cyan-400/10';
    case 'MID EDGE':  return 'bg-amber-400/10';
    case 'LOW EDGE':  return 'bg-zinc-400/10';
    default:          return 'bg-zinc-500/10';
  }
}

// Points-to-probability: 1 spread point ≈ 3% win probability
export const PROB_PER_POINT = 0.03;
// Totals are higher-variance: 1 total point ≈ 1.5% win probability
export const PROB_PER_TOTAL_POINT = 0.015;
export type MarketSide = 'home' | 'away' | 'over' | 'under' | 'draw';

export interface CEQResult {
  ceq: number;                    // 0-100, 50 = no edge
  confidence: CEQConfidence;
  side: MarketSide | null;        // Favored side
  pillars: {
    marketEfficiency: PillarResult;
    lineupImpact: PillarResult;
    gameEnvironment: PillarResult;
    matchupDynamics: PillarResult;
    sentiment: PillarResult;
  };
  topDrivers: string[];           // Top 3 reasons for the score
  dataQuality: {
    pillarsWithData: number;      // 0-5, how many pillars have real data
    totalVariables: number;       // Total variables with data
    displayCEQ: boolean;          // Should CEQ be shown? (requires 2+ pillars)
    confidenceLabel: 'Low' | 'Medium' | 'High' | 'Insufficient';
  };
}

// Extended snapshot with game_id for grouping
export interface ExtendedOddsSnapshot extends OddsSnapshot {
  game_id?: string;
  market?: string;
}

// ============================================================================
// Fair Line Scale Factors
// ============================================================================
// Convert pillar composite deviation (from 50 = neutral) to point adjustments
// Easy to tune: change these constants to adjust fair line sensitivity

export const FAIR_LINE_SPREAD_FACTOR = 0.15; // 10-point deviation ≈ 1.5 spread points
export const FAIR_LINE_TOTAL_FACTOR = 0.10;  // 10-point deviation ≈ 1.0 total points (was 0.20)
export const FAIR_LINE_ML_FACTOR = 0.01;     // 1% implied probability shift per composite point

// Sport-specific caps — max adjustment from book consensus (prevents hallucinated edges)
export const SPREAD_CAP_BY_SPORT: Record<string, number> = {
  'basketball_ncaab': 4.0,
  'basketball_nba': 3.0,
  'americanfootball_nfl': 3.0,
  'americanfootball_ncaaf': 3.0,
  'icehockey_nhl': 1.5,
  'soccer_epl': 1.0,
};
export const TOTAL_CAP_BY_SPORT: Record<string, number> = {
  'basketball_ncaab': 6.0,
  'basketball_nba': 5.0,
  'americanfootball_nfl': 5.0,
  'americanfootball_ncaaf': 5.0,
  'icehockey_nhl': 1.0,
  'soccer_epl': 1.0,
};
export const DEFAULT_SPREAD_CAP = 3.0;
export const DEFAULT_TOTAL_CAP = 4.0;

// Sport-specific: how much win probability each spread point represents
// Used to convert fair spread → fair moneyline for cross-market consistency
export const SPREAD_TO_PROB_RATE: Record<string, number> = {
  'basketball_nba': 0.033,           // ~3.3% per point
  'basketball_ncaab': 0.030,         // ~3.0% per point
  'americanfootball_nfl': 0.027,     // ~2.7% per point
  'americanfootball_ncaaf': 0.025,   // ~2.5% per point
  'icehockey_nhl': 0.08,             // ~8% per goal
  'baseball_mlb': 0.09,              // ~9% per run
  'soccer_epl': 0.20,               // ~20% per goal (rare-scoring sport)
};

/**
 * Calculate a fair spread based on book spread + pillar composite deviation.
 * Pillar composite is 0-100, 50 = neutral.
 * Deviation from 50 is scaled by FAIR_LINE_SPREAD_FACTOR to get point adjustment.
 * Positive deviation (>50) → home favored more → fair line more negative.
 */
export function calculateFairSpread(
  bookSpread: number,
  pillarComposite: number,
  sportKey?: string
): { fairLine: number; gap: number; edgeSide: string | null } {
  const deviation = pillarComposite - 50;
  // Confidence scaling: adjustments are attenuated when composite is near 50 (low conviction)
  const confidence = Math.max(0.40, Math.abs(pillarComposite - 50) / 50 * 2);
  const rawAdj = (deviation / 10) * FAIR_LINE_SPREAD_FACTOR * confidence;
  // Cap adjustment to prevent extreme divergence from book consensus
  const cap = SPREAD_CAP_BY_SPORT[sportKey || ''] ?? DEFAULT_SPREAD_CAP;
  const adjustment = Math.max(-cap, Math.min(cap, rawAdj));
  // Positive pillar deviation = home-favored thesis → subtract from spread (more negative)
  const fairLine = Math.round((bookSpread - adjustment) * 2) / 2; // Round to 0.5
  const gap = Math.round((bookSpread - fairLine) * 10) / 10;
  const edgeSide = Math.abs(gap) < 0.5 ? null : gap > 0 ? 'away' : 'home';
  return { fairLine, gap, edgeSide };
}

/**
 * Calculate a fair total based on book total + game environment deviation.
 * Game environment score is 0-100, 50 = neutral.
 * >50 = expects OVER, <50 = expects UNDER.
 */
export function calculateFairTotal(
  bookTotal: number,
  gameEnvScore: number,
  sportKey?: string
): { fairLine: number; gap: number; edgeSide: string | null } {
  const deviation = gameEnvScore - 50;
  // Confidence scaling: attenuate when game env score is near 50
  const confidence = Math.max(0.40, Math.abs(gameEnvScore - 50) / 50 * 2);
  const rawAdj = (deviation / 10) * FAIR_LINE_TOTAL_FACTOR * confidence;
  // Cap adjustment to prevent extreme divergence from book consensus
  const cap = TOTAL_CAP_BY_SPORT[sportKey || ''] ?? DEFAULT_TOTAL_CAP;
  const adjustment = Math.max(-cap, Math.min(cap, rawAdj));
  // Positive deviation = over-favored → fair total is higher
  const fairLine = Math.round((bookTotal + adjustment) * 2) / 2; // Round to 0.5
  const gap = Math.round((fairLine - bookTotal) * 10) / 10;
  const edgeSide = Math.abs(gap) < 0.5 ? null : gap > 0 ? 'over' : 'under';
  return { fairLine, gap, edgeSide };
}

/**
 * Calculate fair moneyline odds from pillar composite.
 * Composite 50 = pick'em (-100/+100 fair, no vig).
 * Each point from 50 shifts implied probability by FAIR_LINE_ML_FACTOR (1%).
 * Composite 60 → home 60% implied → home -150, away +167.
 */
export function calculateFairMoneyline(
  pillarComposite: number
): { homeOdds: number; awayOdds: number } {
  const deviation = pillarComposite - 50;
  const confidence = Math.max(0.40, Math.abs(pillarComposite - 50) / 50 * 2);
  const homeProb = Math.max(0.05, Math.min(0.95, 0.50 + (deviation / 10) * FAIR_LINE_ML_FACTOR * confidence));
  const awayProb = 1 - homeProb;
  const probToAmerican = (prob: number) => {
    if (prob >= 0.5) return Math.round(-100 * prob / (1 - prob));
    return Math.round(100 * (1 - prob) / prob);
  };
  return { homeOdds: probToAmerican(homeProb), awayOdds: probToAmerican(awayProb) };
}

/**
 * Calculate fair ML by adjusting consensus book ML with pillar composite deviation.
 * Unlike calculateFairMoneyline (composite-only), this ANCHORS to the book odds.
 * Composite 50 = no adjustment. Each point from 50 shifts by FAIR_LINE_ML_FACTOR (1%).
 * Example: Book -150/+700, composite 40 → shift 10% toward away → ~-120/+550
 */
export function calculateFairMLFromBook(
  bookHomeOdds: number,
  bookAwayOdds: number,
  pillarComposite: number
): { homeOdds: number; awayOdds: number } {
  // Remove vig to get true 2-way fair probabilities
  const { fairHomeProb, fairAwayProb } = removeVig(bookHomeOdds, bookAwayOdds);
  // Shift by composite deviation with confidence scaling
  const deviation = pillarComposite - 50;
  const confidence = Math.max(0.40, Math.abs(pillarComposite - 50) / 50 * 2);
  const shift = (deviation / 10) * FAIR_LINE_ML_FACTOR * confidence;
  const adjustedHome = Math.max(0.05, Math.min(0.95, fairHomeProb + shift));
  const adjustedAway = 1 - adjustedHome;
  const probToAmerican = (prob: number) => {
    if (prob >= 0.5) return Math.round(-100 * prob / (1 - prob));
    return Math.round(100 * (1 - prob) / prob);
  };
  return { homeOdds: probToAmerican(adjustedHome), awayOdds: probToAmerican(adjustedAway) };
}

/**
 * Remove vig from 3-way odds (soccer: home/draw/away).
 * All 3 implied probabilities sum to >100%; normalize to 100%.
 */
export function removeVig3Way(
  homeOdds: number,
  drawOdds: number,
  awayOdds: number
): { fairHomeProb: number; fairDrawProb: number; fairAwayProb: number; vig: number } {
  const toImplied = (odds: number) =>
    odds < 0 ? Math.abs(odds) / (Math.abs(odds) + 100) : 100 / (odds + 100);
  const homeImplied = toImplied(homeOdds);
  const drawImplied = toImplied(drawOdds);
  const awayImplied = toImplied(awayOdds);
  const total = homeImplied + drawImplied + awayImplied;
  return {
    fairHomeProb: homeImplied / total,
    fairDrawProb: drawImplied / total,
    fairAwayProb: awayImplied / total,
    vig: total - 1,
  };
}

/**
 * 3-way book-anchored fair ML for soccer (home/draw/away).
 * Composite adjustment shifts between home and away; draw absorbs residual.
 */
export function calculateFairMLFromBook3Way(
  bookHomeOdds: number,
  bookDrawOdds: number,
  bookAwayOdds: number,
  pillarComposite: number
): { homeOdds: number; drawOdds: number; awayOdds: number } {
  const { fairHomeProb, fairDrawProb, fairAwayProb } = removeVig3Way(bookHomeOdds, bookDrawOdds, bookAwayOdds);
  const deviation = pillarComposite - 50;
  const confidence = Math.max(0.40, Math.abs(pillarComposite - 50) / 50 * 2);
  const shift = (deviation / 10) * FAIR_LINE_ML_FACTOR * confidence;
  let adjHome = fairHomeProb + shift;
  let adjAway = fairAwayProb - shift;
  let adjDraw = 1 - adjHome - adjAway;
  // Clamp all ≥ 2%
  adjHome = Math.max(0.02, adjHome);
  adjAway = Math.max(0.02, adjAway);
  adjDraw = Math.max(0.02, adjDraw);
  // Normalize to sum to 1.0
  const sum = adjHome + adjAway + adjDraw;
  adjHome /= sum; adjAway /= sum; adjDraw /= sum;
  const probToAmerican = (prob: number) => {
    if (prob >= 0.5) return Math.round(-100 * prob / (1 - prob));
    return Math.round(100 * (1 - prob) / prob);
  };
  return {
    homeOdds: probToAmerican(adjHome),
    drawOdds: probToAmerican(adjDraw),
    awayOdds: probToAmerican(adjAway),
  };
}

/**
 * Derive fair moneyline from a fair spread using sport-specific conversion rates.
 * This ensures ML and spread tell the same story for the same game.
 * fairSpread is from the HOME perspective (negative = home favored).
 * Example: fairSpread = +5.5 (home is 5.5pt underdog) → home ~31% / away ~69%
 */
export function spreadToMoneyline(
  fairSpread: number,
  sportKey: string
): { homeOdds: number; awayOdds: number } {
  const rate = SPREAD_TO_PROB_RATE[sportKey] || 0.03;
  // Negative fairSpread = home favored → higher home win prob
  const homeProb = Math.max(0.05, Math.min(0.95, 0.50 + (-fairSpread) * rate));
  const awayProb = 1 - homeProb;
  const probToAmerican = (prob: number) => {
    if (prob >= 0.5) return Math.round(-100 * prob / (1 - prob));
    return Math.round(100 * (1 - prob) / prob);
  };
  return { homeOdds: probToAmerican(homeProb), awayOdds: probToAmerican(awayProb) };
}

/**
 * Remove vig/overround from book odds to get true fair probabilities.
 * Both sides' implied probabilities sum to >100% (the vig).
 * Normalize so they sum to exactly 100%.
 */
export function removeVig(
  homeOdds: number,
  awayOdds: number
): { fairHomeProb: number; fairAwayProb: number; vig: number } {
  const homeImplied = homeOdds < 0
    ? Math.abs(homeOdds) / (Math.abs(homeOdds) + 100)
    : 100 / (homeOdds + 100);
  const awayImplied = awayOdds < 0
    ? Math.abs(awayOdds) / (Math.abs(awayOdds) + 100)
    : 100 / (awayOdds + 100);
  const totalImplied = homeImplied + awayImplied;
  const vig = totalImplied - 1; // overround as decimal (e.g., 0.045 = 4.5%)
  return {
    fairHomeProb: homeImplied / totalImplied,
    fairAwayProb: awayImplied / totalImplied,
    vig,
  };
}

/**
 * Key numbers by sport — crossing these amplifies spread signal.
 * NFL: 3, 7, 10, 14 are common margins of victory.
 */
export const SPORT_KEY_NUMBERS: Record<string, number[]> = {
  'americanfootball_nfl': [3, 7, 10, 14],
  'americanfootball_ncaaf': [3, 7, 10, 14],
};

// ============================================================================
// Python Backend Pillar Scores (Harmonization)
// ============================================================================
// When Python backend is available, we use its pillar scores to boost/adjust
// the TypeScript CEQ calculation. This combines:
// - Python's game-level analysis (injuries, motivation, rest, sharp money)
// - TypeScript's market-specific analysis (per-book odds comparison)

interface MarketPeriodComposite {
  composite: number;       // 0-100: Market/period-specific weighted composite
  confidence: string;      // PASS, WATCH, EDGE, STRONG, RARE
  weights: Record<string, number>;
  pillar_scores?: Record<string, number>; // Market-specific pillar scores (0-100)
}

interface PillarsByMarket {
  spread: Record<string, MarketPeriodComposite>;
  totals: Record<string, MarketPeriodComposite>;
  moneyline: Record<string, MarketPeriodComposite>;
}

export interface PythonPillarScores {
  execution: number;       // 0-100: Injuries, weather, lineup (→ Lineup Impact)
  incentives: number;      // 0-100: Playoffs, motivation, rivalries
  shocks: number;          // 0-100: Breaking news, line movement timing (→ Market Efficiency boost)
  timeDecay: number;       // 0-100: Rest days, back-to-back, travel
  flow: number;            // 0-100: Sharp money, book disagreement (→ Sentiment)
  gameEnvironment: number; // 0-100: Expected total vs line (→ Totals CEQ). <50 = UNDER lean, >50 = OVER lean
  composite: number;       // 0-100: Weighted average of all pillars (default spread/full)
  pillarsByMarket?: PillarsByMarket; // Market×Period-specific composites
}

/**
 * Maps Python pillar scores to TypeScript pillar adjustments
 * Returns adjustments to be applied to each TypeScript pillar
 */
function mapPythonToTypeScriptPillars(pythonPillars: PythonPillarScores): {
  marketEfficiencyBoost: number;
  lineupImpactScore: number;
  gameEnvironmentScore: number;
  totalsEnvironmentScore: number;  // Specifically for totals (over/under)
  sentimentScore: number;
} {
  // Python Execution (injuries) → TypeScript Lineup Impact
  // Score is 0-100, 50 = neutral
  const lineupImpactScore = pythonPillars.execution;

  // Python Incentives + Time Decay → TypeScript Game Environment (for spreads/h2h)
  // Weighted average: incentives 60%, time decay 40%
  const gameEnvironmentScore = Math.round(
    pythonPillars.incentives * 0.6 + pythonPillars.timeDecay * 0.4
  );

  // Python game_environment → For TOTALS markets
  // This score is based on expected total vs the line:
  // <50 = expects UNDER the line, >50 = expects OVER the line
  const totalsEnvironmentScore = pythonPillars.gameEnvironment ?? 50;

  // Python Shocks → Market Efficiency boost
  // If shocks detected (score != 50), boost market efficiency signal
  const shockDeviation = Math.abs(pythonPillars.shocks - 50);
  const marketEfficiencyBoost = shockDeviation > 10 ? shockDeviation * 0.5 : 0;

  // Python Flow (sharp money) → TypeScript Sentiment
  const sentimentScore = pythonPillars.flow;

  return {
    marketEfficiencyBoost,
    lineupImpactScore,
    gameEnvironmentScore,
    totalsEnvironmentScore,
    sentimentScore,
  };
}

// ============================================================================
// CEQ Confidence Thresholds (NEW FRAMEWORK)
// ============================================================================
// CEQ now represents pillar direction VALIDATED by market efficiency
// 50% = Neutral (no clear thesis)
// 55-59% = Slight lean (don't show as edge)
// 60-64% = WATCH (moderate edge, monitor)
// 65-69% = EDGE (actionable)
// 70%+ = STRONG (high conviction)

function getCEQConfidence(ceq: number): CEQConfidence {
  // CEQ represents distance from 50% (neutral)
  // Higher = stronger validated edge in pillar direction
  if (ceq >= 75) return 'STRONG';
  if (ceq >= 65) return 'EDGE';
  if (ceq >= 60) return 'WATCH';
  return 'PASS';
}

// ============================================================================
// MARKET VALIDATION MULTIPLIER
// ============================================================================
// CEQ factors determine if market has already priced in the pillar thesis
// Returns a multiplier: 0.7-1.3
// >1.0 = Market inefficient, amplify pillar signal
// =1.0 = Market neutral
// <1.0 = Market efficient, dampen pillar signal

interface MarketValidation {
  multiplier: number;  // 0.7 to 1.3
  reason: string;
  isEfficient: boolean;  // Has market priced in the thesis?
}

function calculateMarketValidation(
  marketEfficiencyScore: number,
  lineupImpactScore: number,
  sentimentScore: number,
  pillarDirection: 'home' | 'away' | 'over' | 'under'
): MarketValidation {
  // Market Efficiency: How much has the line moved? (50 = stable, >50 = moved)
  // If line moved in SAME direction as pillars suggest, market already priced it → dampen
  // If line moved OPPOSITE or stable, market hasn't priced it → amplify

  // Calculate average of CEQ factors (all on 0-100 scale, 50 = neutral)
  const avgCeqSignal = (marketEfficiencyScore + lineupImpactScore + sentimentScore) / 3;

  // Convert to multiplier
  // If CEQ factors strongly agree with pillar direction (>65), market is inefficient → amplify
  // If CEQ factors disagree or neutral, market may have priced it → dampen
  let multiplier = 1.0;
  let reason = '';
  let isEfficient = false;

  if (avgCeqSignal >= 70) {
    // Strong market inefficiency - amplify pillar signal
    multiplier = 1.15 + (avgCeqSignal - 70) * 0.005; // 1.15 to 1.30
    multiplier = Math.min(1.30, multiplier);
    reason = 'Market hasn\'t fully adjusted - edge amplified';
    isEfficient = false;
  } else if (avgCeqSignal >= 60) {
    // Moderate inefficiency - slight amplification
    multiplier = 1.0 + (avgCeqSignal - 60) * 0.015; // 1.0 to 1.15
    reason = 'Some market inefficiency detected';
    isEfficient = false;
  } else if (avgCeqSignal >= 40) {
    // Market neutral - keep pillar signal as-is
    multiplier = 1.0;
    reason = 'Market fairly priced';
    isEfficient = true;
  } else if (avgCeqSignal >= 30) {
    // Market efficient - dampen pillar signal
    multiplier = 0.85 + (avgCeqSignal - 30) * 0.015; // 0.85 to 1.0
    reason = 'Market already priced this in - reduced conviction';
    isEfficient = true;
  } else {
    // Strongly efficient - significant dampening
    multiplier = 0.70 + (avgCeqSignal) * 0.005; // 0.70 to 0.85
    reason = 'Market has fully adjusted - minimal edge remains';
    isEfficient = true;
  }

  return { multiplier, reason, isEfficient };
}

// ============================================================================
// JUICE ADJUSTMENT - Factor in book-specific pricing
// ============================================================================

/**
 * Convert American odds to implied probability
 * -120 = 54.55%, -125 = 55.56%, +150 = 40.00%
 */
function americanToImpliedProbability(odds: number): number {
  if (odds < 0) {
    return Math.abs(odds) / (Math.abs(odds) + 100);
  } else {
    return 100 / (odds + 100);
  }
}

/**
 * Calculate juice adjustment for CEQ based on book's odds vs consensus
 *
 * Better odds = positive adjustment (higher CEQ)
 * Worse odds = negative adjustment (lower CEQ)
 *
 * Example:
 * - DraftKings: -120 = 54.55% implied
 * - FanDuel: -125 = 55.56% implied
 * - Consensus: -122.5 = 55.05% implied
 * - DK adjustment: +0.5% (54.55 - 55.05 = -0.5 difference, inverted = +0.5)
 * - FD adjustment: -0.5% (55.56 - 55.05 = +0.5 difference, inverted = -0.5)
 *
 * The adjustment is scaled: 1% implied prob difference = ~2% CEQ adjustment
 */
export function calculateJuiceAdjustment(
  bookOdds: number | undefined,
  consensusOdds: number | undefined,
  allBooksOdds: number[]
): { adjustment: number; reason: string } {
  if (bookOdds === undefined || consensusOdds === undefined || allBooksOdds.length === 0) {
    return { adjustment: 0, reason: 'No odds data for juice comparison' };
  }

  const bookImplied = americanToImpliedProbability(bookOdds);
  const consensusImplied = americanToImpliedProbability(consensusOdds);

  // Implied probability difference (negative = book has better odds)
  // For betting: LOWER implied probability at our book = BETTER for us
  const impliedDiff = bookImplied - consensusImplied;

  // Scale: 1% implied diff = 2% CEQ adjustment
  // Invert sign: lower implied (better odds) = positive CEQ adjustment
  const adjustment = -impliedDiff * 200; // Convert to CEQ scale (0-100)

  // Cap the adjustment at ±5% CEQ
  const cappedAdjustment = Math.max(-5, Math.min(5, adjustment));

  // Generate reason
  let reason: string;
  const bookOddsStr = bookOdds >= 0 ? `+${bookOdds}` : `${bookOdds}`;
  const consensusOddsStr = consensusOdds >= 0 ? `+${Math.round(consensusOdds)}` : `${Math.round(consensusOdds)}`;

  if (Math.abs(cappedAdjustment) < 0.5) {
    reason = `Juice aligned with market (${bookOddsStr})`;
  } else if (cappedAdjustment > 0) {
    reason = `Better price: ${bookOddsStr} vs market ${consensusOddsStr} (+${cappedAdjustment.toFixed(1)}% edge)`;
  } else {
    reason = `Worse price: ${bookOddsStr} vs market ${consensusOddsStr} (${cappedAdjustment.toFixed(1)}% penalty)`;
  }

  return { adjustment: cappedAdjustment, reason };
}

// ============================================================================
// PILLAR 1: MARKET EFFICIENCY (Primary - calculable now)
// Variables: FDV, MMI, SBI
// ============================================================================

/**
 * FDV (Fair Delta Value)
 *
 * PRIMARY: Compare selected book's line vs Pinnacle (sharp baseline)
 * FALLBACK: Compare opening line vs current line
 *
 * Scoring (Pinnacle comparison):
 * - 0 pts diff = 50 (in line with sharp)
 * - 0.5 pts diff = 60 (slight value)
 * - 1.0 pts diff = 70 (good value)
 * - 1.5 pts diff = 78 (strong value)
 * - 2.0+ pts diff = 85 (excellent value)
 */
function calculateFDV(
  openingLine: number | undefined,
  currentLine: number | undefined,
  marketType: 'spread' | 'h2h' | 'total' = 'spread',
  pinnacleLine?: number,
  bookLine?: number
): PillarVariable {
  // Format line values based on market type
  const formatLine = (val: number) => {
    if (marketType === 'spread') {
      return val >= 0 ? `+${val}` : `${val}`;
    }
    return `${val}`;
  };

  const marketLabel = marketType === 'spread' ? 'Spread' : marketType === 'total' ? 'Total' : 'ML';

  // PRIMARY: Pinnacle baseline comparison (sharp vs retail book)
  if (pinnacleLine !== undefined && bookLine !== undefined) {
    const diff = Math.abs(bookLine - pinnacleLine);

    // Score based on difference from Pinnacle
    // More difference = more potential value at the retail book
    let score: number;
    if (diff >= 2.0) {
      score = 85;
    } else if (diff >= 1.5) {
      score = 78;
    } else if (diff >= 1.0) {
      score = 70;
    } else if (diff >= 0.5) {
      score = 60;
    } else {
      score = 50;
    }

    const pinnStr = formatLine(pinnacleLine);
    const bookStr = formatLine(bookLine);
    const reason = diff > 0
      ? `${marketLabel}: Book ${bookStr} vs Pinnacle ${pinnStr} (${diff.toFixed(1)} pts off sharp)`
      : `${marketLabel}: In line with Pinnacle at ${pinnStr}`;

    return {
      name: 'FDV',
      value: diff,
      score,
      available: true,
      reason,
    };
  }

  // FALLBACK: Opening vs current line movement
  if (openingLine === undefined || currentLine === undefined) {
    return {
      name: 'FDV',
      value: 0,
      score: 50,
      available: false,
      reason: 'No Pinnacle or opening line data available',
    };
  }

  const delta = currentLine - openingLine;
  const absDelta = Math.abs(delta);

  const openStr = formatLine(openingLine);
  const currentStr = formatLine(currentLine);
  const deltaStr = delta >= 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1);

  // More granular scoring for real variance
  // Each 0.5 point of movement = ~8 points away from 50
  let score: number;
  let reason: string;

  if (absDelta < 0.25) {
    score = 50;
    reason = `${marketLabel} stable at ${currentStr} (no movement)`;
  } else {
    // Continuous scaling: each point of movement = 15 score points
    const baseScore = 50 + (delta * 15);
    score = Math.max(10, Math.min(90, Math.round(baseScore)));

    const moveDesc = `${marketLabel} ${openStr} → ${currentStr} (${deltaStr})`;

    if (delta >= 2) {
      reason = `${moveDesc} - strong sharp action opposite`;
    } else if (delta >= 1) {
      reason = `${moveDesc} - moderate sharp signal`;
    } else if (delta >= 0.5) {
      reason = `${moveDesc} - some movement detected`;
    } else if (delta > 0) {
      reason = `${moveDesc} - slight movement`;
    } else if (delta <= -2) {
      reason = `${moveDesc} - strong edge this side`;
    } else if (delta <= -1) {
      reason = `${moveDesc} - moderate edge this side`;
    } else if (delta <= -0.5) {
      reason = `${moveDesc} - some edge this side`;
    } else {
      reason = `${moveDesc} - slight edge this side`;
    }
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
  // More aggressive scaling for real variance
  const velocityScore = Math.min(velocity * 25, 40); // Cap at 40 pts
  const consistencyBonus = consistency * velocityScore * 0.5;
  const directionSign = totalChange > 0 ? 1 : -1; // Positive = line moved up
  const rawScore = 50 + (velocityScore + consistencyBonus) * directionSign;
  const score = Math.min(Math.max(Math.round(rawScore), 10), 90);

  const direction = totalChange > 0 ? 'up' : 'down';
  const reason = velocity > 0.3
    ? `${velocity > 0.5 ? 'Strong' : 'Moderate'} momentum ${direction} (${velocity.toFixed(2)} pts/hr, ${Math.round(consistency * 100)}% consistent)`
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
 * FDV now uses Pinnacle as sharp baseline when available
 */
function calculateMarketEfficiencyPillar(
  openingLine: number | undefined,
  currentLine: number | undefined,
  snapshots: ExtendedOddsSnapshot[],
  bookOdds: number | undefined,
  consensusOdds: number | undefined,
  allBooksOdds: number[],
  marketType: 'spread' | 'h2h' | 'total' = 'spread',
  pinnacleLine?: number,
  bookLine?: number
): PillarResult {
  const fdv = calculateFDV(openingLine, currentLine, marketType, pinnacleLine, bookLine);
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
// PILLAR 2: LINEUP IMPACT (Injuries, lineup availability)
// ============================================================================

function calculateLineupImpactPillar(
  homeTeam?: TeamStatsData,
  awayTeam?: TeamStatsData,
  league: string = 'nfl'
): PillarResult {
  const variables: PillarVariable[] = [];
  let totalScore = 0;
  let availableCount = 0;

  // UVI (Utilization Variance Index)
  // For NFL: Estimate from win/loss patterns (consistent teams = more predictable utilization)
  // For NBA: Use pace data if available
  let uviScore = 50;
  let uviAvailable = false;
  let uviReason = 'Utilization data not available';

  if (homeTeam || awayTeam) {
    const homeWinPct = homeTeam?.win_pct ?? (homeTeam?.wins && homeTeam?.losses
      ? homeTeam.wins / (homeTeam.wins + homeTeam.losses)
      : null);
    const awayWinPct = awayTeam?.win_pct ?? (awayTeam?.wins && awayTeam?.losses
      ? awayTeam.wins / (awayTeam.wins + awayTeam.losses)
      : null);

    if (homeWinPct !== null || awayWinPct !== null) {
      // Teams with extreme records (very good or very bad) have more consistent utilization
      const homeConsistency = homeWinPct !== null ? Math.abs(homeWinPct - 0.5) : 0;
      const awayConsistency = awayWinPct !== null ? Math.abs(awayWinPct - 0.5) : 0;
      const avgConsistency = ((homeConsistency || 0) + (awayConsistency || 0)) / 2;

      // Higher consistency = more predictable game = slight edge on favorites
      uviScore = 50 + Math.round(avgConsistency * 30);
      uviAvailable = true;
      uviReason = `Team consistency: ${(avgConsistency * 100).toFixed(0)}% deviation from .500`;
    }
  }

  variables.push({
    name: 'UVI',
    value: uviScore - 50,
    score: uviScore,
    available: uviAvailable,
    reason: uviReason,
  });
  if (uviAvailable) {
    totalScore += uviScore;
    availableCount++;
  }

  // RER (Role Efficiency Rating)
  // Estimate from team scoring patterns
  let rerScore = 50;
  let rerAvailable = false;
  let rerReason = 'Role efficiency data not available';

  if (homeTeam?.points_per_game || awayTeam?.points_per_game) {
    const homePPG = homeTeam?.points_per_game ?? 22;
    const awayPPG = awayTeam?.points_per_game ?? 22;

    // Higher scoring teams = more efficient role utilization
    const avgPPG = (homePPG + awayPPG) / 2;
    const leagueAvg = league === 'nba' ? 115 : league === 'nfl' ? 22 : 3;

    const deviation = ((avgPPG - leagueAvg) / leagueAvg) * 100;
    rerScore = Math.round(50 + deviation * 2);
    rerScore = Math.max(30, Math.min(70, rerScore));
    rerAvailable = true;
    rerReason = `Scoring efficiency: ${avgPPG.toFixed(1)} PPG (league avg: ${leagueAvg})`;
  }

  variables.push({
    name: 'RER',
    value: rerScore - 50,
    score: rerScore,
    available: rerAvailable,
    reason: rerReason,
  });
  if (rerAvailable) {
    totalScore += rerScore;
    availableCount++;
  }

  // Z-Score (Statistical Baseline Deviation)
  // Compare team performance to league baseline
  let zScore = 50;
  let zAvailable = false;
  let zReason = 'Baseline stats not available';

  if (homeTeam?.points_allowed_per_game || awayTeam?.points_allowed_per_game) {
    const homeAllowed = homeTeam?.points_allowed_per_game ?? 22;
    const awayAllowed = awayTeam?.points_allowed_per_game ?? 22;

    // Lower points allowed = better defense = positive z-score for home
    const defDiff = awayAllowed - homeAllowed;
    zScore = Math.round(50 + defDiff * 2);
    zScore = Math.max(30, Math.min(70, zScore));
    zAvailable = true;
    zReason = `Defensive matchup: Home allows ${homeAllowed.toFixed(1)} vs Away ${awayAllowed.toFixed(1)}`;
  }

  variables.push({
    name: 'Z-Score',
    value: zScore - 50,
    score: zScore,
    available: zAvailable,
    reason: zReason,
  });
  if (zAvailable) {
    totalScore += zScore;
    availableCount++;
  }

  // Calculate final score
  const finalScore = availableCount > 0 ? Math.round(totalScore / availableCount) : 50;
  const weight = availableCount > 0 ? 0.10 : 0;  // Give some weight if we have data

  return {
    score: finalScore,
    weight,
    variables,
  };
}

// ============================================================================
// PILLAR 3: GAME ENVIRONMENT (ESPN + Weather data)
// ============================================================================

export interface TeamStatsData {
  team_id: string;
  team_name: string;
  team_abbrev?: string;
  pace?: number | null;
  offensive_rating?: number | null;
  defensive_rating?: number | null;
  net_rating?: number | null;
  wins?: number | null;
  losses?: number | null;
  win_pct?: number | null;
  home_wins?: number | null;
  home_losses?: number | null;
  away_wins?: number | null;
  away_losses?: number | null;
  streak?: number | null;
  points_per_game?: number | null;
  points_allowed_per_game?: number | null;
  injuries?: Array<{ player: string; type: string; status: string }>;
}

export interface WeatherData {
  temperature_f?: number | null;
  wind_speed_mph?: number | null;
  wind_gust_mph?: number | null;
  precipitation_pct?: number | null;
  conditions?: string | null;
  weather_impact_score?: number | null;
  is_dome?: boolean;
}

function calculatePaceVariable(
  homePace: number | null | undefined,
  awayPace: number | null | undefined,
  league: string = 'nba'
): PillarVariable {
  if (homePace === null || homePace === undefined || awayPace === null || awayPace === undefined) {
    return { name: 'PVI', value: 0, score: 50, available: false, reason: 'Pace data not available' };
  }

  const avgPace = (homePace + awayPace) / 2;

  // NBA average pace ~100, NFL ~65, MLB varies
  const leaguePace = league === 'nba' ? 100 : league === 'nfl' ? 65 : 70;
  const paceDeviation = avgPace - leaguePace;

  let score: number;
  let reason: string;

  if (paceDeviation > 5) {
    score = 65; // High pace = more possessions = more scoring variance
    reason = `High pace matchup (${avgPace.toFixed(1)}) - favors overs/variance`;
  } else if (paceDeviation > 2) {
    score = 58;
    reason = `Above-avg pace (${avgPace.toFixed(1)}) - slight over lean`;
  } else if (paceDeviation < -5) {
    score = 35;
    reason = `Low pace matchup (${avgPace.toFixed(1)}) - favors unders`;
  } else if (paceDeviation < -2) {
    score = 42;
    reason = `Below-avg pace (${avgPace.toFixed(1)}) - slight under lean`;
  } else {
    score = 50;
    reason = `Average pace matchup (${avgPace.toFixed(1)})`;
  }

  return {
    name: 'PVI',
    value: avgPace,
    score,
    available: true,
    reason,
  };
}

function calculateWeatherVariable(weather: WeatherData | undefined): PillarVariable {
  if (!weather || weather.is_dome) {
    return {
      name: 'WEA',
      value: 0,
      score: 50,
      available: weather?.is_dome === true,
      reason: weather?.is_dome ? 'Dome stadium - no weather impact' : 'Weather data not available',
    };
  }

  const impactScore = weather.weather_impact_score || 0;
  const wind = weather.wind_speed_mph || 0;
  const temp = weather.temperature_f || 70;
  const precip = weather.precipitation_pct || 0;

  let score = 50;
  let reasons: string[] = [];

  // High wind affects passing games (under-lean for totals)
  if (wind > 20) {
    score -= 15;
    reasons.push(`high wind (${wind}mph)`);
  } else if (wind > 12) {
    score -= 8;
    reasons.push(`moderate wind (${wind}mph)`);
  }

  // Cold weather affects scoring
  if (temp < 32) {
    score -= 10;
    reasons.push(`freezing (${temp}°F)`);
  } else if (temp < 45) {
    score -= 5;
    reasons.push(`cold (${temp}°F)`);
  }

  // Precipitation affects gameplay
  if (precip > 70) {
    score -= 10;
    reasons.push(`${precip}% rain chance`);
  }

  const reason = reasons.length > 0
    ? `Weather impact: ${reasons.join(', ')} - favors unders`
    : weather.conditions || 'Good weather conditions';

  return {
    name: 'WEA',
    value: impactScore,
    score: Math.max(25, Math.min(75, score)),
    available: true,
    reason,
  };
}

function calculateStreakVariable(
  homeStreak: number | null | undefined,
  awayStreak: number | null | undefined
): PillarVariable {
  if ((homeStreak === null || homeStreak === undefined) &&
      (awayStreak === null || awayStreak === undefined)) {
    return { name: 'STK', value: 0, score: 50, available: false, reason: 'Streak data not available' };
  }

  const hStreak = homeStreak || 0;
  const aStreak = awayStreak || 0;
  const streakDiff = hStreak - aStreak;

  let score: number;
  let reason: string;

  if (Math.abs(streakDiff) < 2) {
    score = 50;
    reason = `Similar momentum (home: ${hStreak > 0 ? `W${hStreak}` : `L${Math.abs(hStreak)}`}, away: ${aStreak > 0 ? `W${aStreak}` : `L${Math.abs(aStreak)}`})`;
  } else if (streakDiff >= 3) {
    score = 62;
    reason = `Home on ${hStreak > 0 ? `${hStreak}-game win streak` : 'hot streak'} vs cold away team`;
  } else if (streakDiff >= 2) {
    score = 56;
    reason = `Home momentum advantage (${hStreak > 0 ? `W${hStreak}` : 'coming off wins'})`;
  } else if (streakDiff <= -3) {
    score = 38;
    reason = `Away on ${aStreak > 0 ? `${aStreak}-game win streak` : 'hot streak'} vs cold home team`;
  } else {
    score = 44;
    reason = `Away momentum advantage (${aStreak > 0 ? `W${aStreak}` : 'coming off wins'})`;
  }

  return {
    name: 'STK',
    value: streakDiff,
    score,
    available: true,
    reason,
  };
}

function calculateGameEnvironmentPillar(
  homeTeam?: TeamStatsData,
  awayTeam?: TeamStatsData,
  weather?: WeatherData,
  league: string = 'nba'
): PillarResult {
  console.log(`[GameEnvironment] Inputs: homeTeam=${homeTeam?.team_name || 'undefined'}, awayTeam=${awayTeam?.team_name || 'undefined'}`);
  console.log(`[GameEnvironment] Pace: home=${homeTeam?.pace}, away=${awayTeam?.pace}`);
  console.log(`[GameEnvironment] Streak: home=${homeTeam?.streak}, away=${awayTeam?.streak}`);
  console.log(`[GameEnvironment] Weather: ${weather ? JSON.stringify(weather) : 'undefined'}`);

  const pvi = calculatePaceVariable(homeTeam?.pace, awayTeam?.pace, league);
  const wea = calculateWeatherVariable(weather);
  const stk = calculateStreakVariable(homeTeam?.streak, awayTeam?.streak);

  const variables = [pvi, wea, stk];
  const availableVars = variables.filter(v => v.available);

  let weight = 0;
  if (availableVars.length >= 2) weight = 0.6;
  else if (availableVars.length === 1) weight = 0.3;

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
// PILLAR 4: MATCHUP DYNAMICS (Team Stats from ESPN)
// ============================================================================

function calculateDefenseVariable(
  homeDefRtg: number | null | undefined,
  awayDefRtg: number | null | undefined,
  homeOffRtg: number | null | undefined,
  awayOffRtg: number | null | undefined
): PillarVariable {
  // Check if we have any rating data
  const hasDefense = homeDefRtg !== null && homeDefRtg !== undefined &&
                     awayDefRtg !== null && awayDefRtg !== undefined;
  const hasOffense = homeOffRtg !== null && homeOffRtg !== undefined &&
                     awayOffRtg !== null && awayOffRtg !== undefined;

  if (!hasDefense && !hasOffense) {
    return { name: 'DVA', value: 0, score: 50, available: false, reason: 'Efficiency data not available' };
  }

  // Lower defensive rating = better defense
  // Higher offensive rating = better offense
  let score = 50;
  const reasons: string[] = [];

  if (hasDefense && homeDefRtg !== null && awayDefRtg !== null) {
    const defDiff = awayDefRtg - homeDefRtg; // Positive = home defense better
    if (defDiff > 3) {
      score += 8;
      reasons.push(`home D elite (+${defDiff.toFixed(1)} rating edge)`);
    } else if (defDiff > 1.5) {
      score += 4;
      reasons.push('home D advantage');
    } else if (defDiff < -3) {
      score -= 8;
      reasons.push(`away D elite (+${Math.abs(defDiff).toFixed(1)} rating edge)`);
    } else if (defDiff < -1.5) {
      score -= 4;
      reasons.push('away D advantage');
    }
  }

  if (hasOffense && homeOffRtg !== null && awayOffRtg !== null) {
    const offDiff = homeOffRtg - awayOffRtg; // Positive = home offense better
    if (offDiff > 3) {
      score += 6;
      reasons.push(`home O efficient (+${offDiff.toFixed(1)})`);
    } else if (offDiff < -3) {
      score -= 6;
      reasons.push(`away O efficient (+${Math.abs(offDiff).toFixed(1)})`);
    }
  }

  const reason = reasons.length > 0 ? reasons.join(', ') : 'Evenly matched efficiency';

  return {
    name: 'DVA',
    value: score - 50,
    score: Math.max(30, Math.min(70, score)),
    available: true,
    reason,
  };
}

function calculateWinPctVariable(
  homeWinPct: number | null | undefined,
  awayWinPct: number | null | undefined,
  isHome: boolean = true
): PillarVariable {
  if (homeWinPct === null || homeWinPct === undefined ||
      awayWinPct === null || awayWinPct === undefined) {
    return { name: 'WPD', value: 0, score: 50, available: false, reason: 'Win % data not available' };
  }

  const winPctDiff = (homeWinPct - awayWinPct) * 100; // Convert to percentage points
  let score: number;
  let reason: string;

  if (Math.abs(winPctDiff) < 5) {
    score = 50;
    reason = `Even matchup (${(homeWinPct * 100).toFixed(0)}% vs ${(awayWinPct * 100).toFixed(0)}%)`;
  } else if (winPctDiff >= 15) {
    score = 68;
    reason = `Home heavily favored (${(homeWinPct * 100).toFixed(0)}% vs ${(awayWinPct * 100).toFixed(0)}%)`;
  } else if (winPctDiff >= 10) {
    score = 60;
    reason = `Home edge on record (${(homeWinPct * 100).toFixed(0)}% vs ${(awayWinPct * 100).toFixed(0)}%)`;
  } else if (winPctDiff >= 5) {
    score = 55;
    reason = `Slight home edge by record`;
  } else if (winPctDiff <= -15) {
    score = 32;
    reason = `Away heavily favored (${(awayWinPct * 100).toFixed(0)}% vs ${(homeWinPct * 100).toFixed(0)}%)`;
  } else if (winPctDiff <= -10) {
    score = 40;
    reason = `Away edge on record (${(awayWinPct * 100).toFixed(0)}% vs ${(homeWinPct * 100).toFixed(0)}%)`;
  } else {
    score = 45;
    reason = `Slight away edge by record`;
  }

  return {
    name: 'WPD',
    value: winPctDiff,
    score,
    available: true,
    reason,
  };
}

function calculateInjuryVariable(
  homeInjuries: Array<{ player: string; type: string; status: string }> | undefined,
  awayInjuries: Array<{ player: string; type: string; status: string }> | undefined
): PillarVariable {
  const homeCount = homeInjuries?.filter(i => i.status === 'Out' || i.status === 'Doubtful').length || 0;
  const awayCount = awayInjuries?.filter(i => i.status === 'Out' || i.status === 'Doubtful').length || 0;

  if (homeCount === 0 && awayCount === 0) {
    return { name: 'INJ', value: 0, score: 50, available: true, reason: 'No significant injuries reported' };
  }

  const injuryDiff = awayCount - homeCount; // Positive = away has more injuries = home advantage
  let score: number;
  let reason: string;

  if (injuryDiff >= 3) {
    score = 65;
    reason = `Away team depleted (${awayCount} out vs ${homeCount})`;
  } else if (injuryDiff >= 1) {
    score = 57;
    reason = `Injury edge to home (${homeCount} vs ${awayCount} out)`;
  } else if (injuryDiff <= -3) {
    score = 35;
    reason = `Home team depleted (${homeCount} out vs ${awayCount})`;
  } else if (injuryDiff <= -1) {
    score = 43;
    reason = `Injury edge to away (${awayCount} vs ${homeCount} out)`;
  } else {
    score = 50;
    reason = `Similar injury situations (${homeCount} vs ${awayCount} out)`;
  }

  return {
    name: 'INJ',
    value: injuryDiff,
    score,
    available: true,
    reason,
  };
}

function calculateMatchupDynamicsPillar(
  homeTeam?: TeamStatsData,
  awayTeam?: TeamStatsData
): PillarResult {
  const dva = calculateDefenseVariable(
    homeTeam?.defensive_rating,
    awayTeam?.defensive_rating,
    homeTeam?.offensive_rating,
    awayTeam?.offensive_rating
  );
  const wpd = calculateWinPctVariable(homeTeam?.win_pct, awayTeam?.win_pct);
  const inj = calculateInjuryVariable(homeTeam?.injuries, awayTeam?.injuries);

  const variables = [dva, wpd, inj];
  const availableVars = variables.filter(v => v.available);

  let weight = 0;
  if (availableVars.length >= 2) weight = 0.5;
  else if (availableVars.length === 1) weight = 0.25;

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

export interface GameContextData {
  homeTeam?: TeamStatsData;
  awayTeam?: TeamStatsData;
  weather?: WeatherData;
  league?: string;
}

export function calculateCEQ(
  marketType: 'spread' | 'h2h' | 'total',
  side: MarketSide,
  bookOdds: number | undefined,
  openingLine: number | undefined,
  currentLine: number | undefined,
  snapshots: ExtendedOddsSnapshot[],
  allBooksOdds: number[],
  consensusOdds: number | undefined,
  gameContext?: GameContextData,
  pythonPillars?: PythonPillarScores,  // Optional Python backend pillar scores
  pinnacleLine?: number,  // Pinnacle sharp line for FDV baseline
  bookLine?: number,      // Selected book's line for FDV comparison
  ev?: number             // Expected Value percentage (e.g., 5.0 means +5% EV)
): CEQResult {
  // Calculate TypeScript pillars (market-specific analysis)
  let marketEfficiency = calculateMarketEfficiencyPillar(
    openingLine,
    currentLine,
    snapshots,
    bookOdds,
    consensusOdds,
    allBooksOdds,
    marketType,
    pinnacleLine,
    bookLine
  );
  let lineupImpact = calculateLineupImpactPillar(
    gameContext?.homeTeam,
    gameContext?.awayTeam,
    gameContext?.league
  );
  let gameEnvironment = calculateGameEnvironmentPillar(
    gameContext?.homeTeam,
    gameContext?.awayTeam,
    gameContext?.weather,
    gameContext?.league
  );
  let matchupDynamics = calculateMatchupDynamicsPillar(
    gameContext?.homeTeam,
    gameContext?.awayTeam
  );
  let sentiment = calculateSentimentPillar(snapshots, bookOdds, consensusOdds, allBooksOdds);

  // HARMONIZATION: If Python pillars available, integrate them
  if (pythonPillars) {
    const mapped = mapPythonToTypeScriptPillars(pythonPillars);

    // Lineup Impact: Use Python's Execution (injuries) if available
    if (pythonPillars.execution !== 50) {
      lineupImpact = {
        score: mapped.lineupImpactScore,
        weight: 0.20,  // Now has real weight
        variables: [{
          name: 'Injuries',
          value: pythonPillars.execution - 50,
          score: mapped.lineupImpactScore,
          available: true,
          reason: `Python: Execution score ${pythonPillars.execution}% (injuries, lineup)`,
        }],
      };
    }

    // Game Environment: Use Python's Incentives + Time Decay
    if (pythonPillars.incentives !== 50 || pythonPillars.timeDecay !== 50) {
      const existingScore = gameEnvironment.score;
      const pythonScore = mapped.gameEnvironmentScore;
      // Blend: 40% existing, 60% Python
      gameEnvironment = {
        score: Math.round(existingScore * 0.4 + pythonScore * 0.6),
        weight: Math.max(gameEnvironment.weight, 0.15),
        variables: [
          ...gameEnvironment.variables,
          {
            name: 'Motivation',
            value: pythonPillars.incentives - 50,
            score: pythonPillars.incentives,
            available: true,
            reason: `Python: Incentives ${pythonPillars.incentives}%`,
          },
          {
            name: 'Rest/Fatigue',
            value: pythonPillars.timeDecay - 50,
            score: pythonPillars.timeDecay,
            available: true,
            reason: `Python: Time Decay ${pythonPillars.timeDecay}%`,
          },
        ],
      };
    }

    // Market Efficiency: Boost with Python's Shocks signal
    if (mapped.marketEfficiencyBoost > 0) {
      const boostedScore = Math.min(100, marketEfficiency.score + mapped.marketEfficiencyBoost);
      marketEfficiency = {
        ...marketEfficiency,
        score: Math.round(boostedScore),
        variables: [
          ...marketEfficiency.variables,
          {
            name: 'Shock Signal',
            value: pythonPillars.shocks - 50,
            score: pythonPillars.shocks,
            available: true,
            reason: `Python: Shocks ${pythonPillars.shocks}% (news, timing)`,
          },
        ],
      };
    }

    // Sentiment: Use Python's Flow (sharp money)
    if (pythonPillars.flow !== 50) {
      sentiment = {
        score: mapped.sentimentScore,
        weight: 0.15,  // Now has real weight
        variables: [{
          name: 'Sharp Money',
          value: pythonPillars.flow - 50,
          score: mapped.sentimentScore,
          available: true,
          reason: `Python: Flow ${pythonPillars.flow}% (sharp vs public)`,
        }],
      };
    }
  }

  // ============================================================================
  // ADD EV AS A VARIABLE IN MARKET EFFICIENCY (not a separate system)
  // EV is one signal among many - it should BOOST the pillar score, not replace it
  // ============================================================================
  if (ev !== undefined && !isNaN(ev)) {
    // Convert EV% to a 0-100 score (50 = neutral)
    // Each 1% EV = ~2 score points (so +10% EV = 70 score, +15% EV = 80 score)
    const evScore = Math.min(90, Math.max(10, 50 + (ev * 2)));

    // Add EV as a variable in Market Efficiency pillar
    marketEfficiency.variables.push({
      name: 'EV',
      value: ev,
      score: evScore,
      available: true,
      reason: ev >= 10
        ? `Strong +EV: ${ev.toFixed(1)}% edge vs consensus`
        : ev >= 5
          ? `Good +EV: ${ev.toFixed(1)}% vs consensus`
          : ev >= 2
            ? `Positive EV: ${ev.toFixed(1)}% vs consensus`
            : ev <= -5
              ? `Negative EV: ${ev.toFixed(1)}% vs consensus`
              : ev <= -2
                ? `Below market: ${ev.toFixed(1)}%`
                : `EV: ${ev.toFixed(1)}% vs consensus`,
    });

    // Recalculate Market Efficiency score with EV included
    // EV gets 25% weight within Market Efficiency (FDV 40%, MMI 20%, SBI 15%, EV 25%)
    const availableVars = marketEfficiency.variables.filter(v => v.available);
    if (availableVars.length > 0) {
      // Weight distribution: FDV=40%, MMI=20%, SBI=15%, EV=25%
      const fdv = marketEfficiency.variables.find(v => v.name === 'FDV');
      const mmi = marketEfficiency.variables.find(v => v.name === 'MMI');
      const sbi = marketEfficiency.variables.find(v => v.name === 'SBI');
      const evVar = marketEfficiency.variables.find(v => v.name === 'EV');

      let totalWeight = 0;
      let weightedSum = 0;

      if (fdv?.available) { weightedSum += fdv.score * 0.40; totalWeight += 0.40; }
      if (mmi?.available) { weightedSum += mmi.score * 0.20; totalWeight += 0.20; }
      if (sbi?.available) { weightedSum += sbi.score * 0.15; totalWeight += 0.15; }
      if (evVar?.available) { weightedSum += evVar.score * 0.25; totalWeight += 0.25; }

      if (totalWeight > 0) {
        marketEfficiency.score = Math.round(weightedSum / totalWeight);
      }
    }

    // Increase Market Efficiency weight when EV is available (more confident signal)
    marketEfficiency.weight = Math.max(marketEfficiency.weight, 1.0);
  }

  // ============================================================================
  // NEW FRAMEWORK: Pillars Set Direction, CEQ Validates Edge
  // ============================================================================
  // 1. Python pillars determine the BASE DIRECTION (the thesis)
  // 2. TypeScript CEQ factors determine MARKET VALIDATION (efficiency check)
  // 3. Final CEQ = 50 + (pillarDeviation * validationMultiplier)
  // 4. CEQ can NEVER flip the direction - only strengthen or weaken conviction

  // Calculate TypeScript CEQ score from local pillars (for market validation)
  const tsPillars = [marketEfficiency, lineupImpact, gameEnvironment, matchupDynamics, sentiment];
  const tsTotalWeight = tsPillars.reduce((acc, p) => acc + p.weight, 0);

  let tsCeq = 50;
  if (tsTotalWeight > 0) {
    tsCeq = tsPillars.reduce((acc, p) => acc + p.score * p.weight, 0) / tsTotalWeight;
  }

  // Get the BASE DIRECTION from Python pillars (the thesis)
  let basePillarScore = 50; // Neutral if no Python data
  let pillarDirection: 'home' | 'away' | 'over' | 'under' | null = null;

  if (pythonPillars) {
    // Map marketType to pillarsByMarket key
    const marketKey = marketType === 'h2h' ? 'moneyline' : marketType === 'total' ? 'totals' : 'spread';
    const marketSpecific = pythonPillars.pillarsByMarket?.[marketKey]?.['full'];

    if (marketType === 'total') {
      // TOTALS: Use market-specific composite or gameEnvironment
      // >50 = OVER lean, <50 = UNDER lean
      basePillarScore = marketSpecific?.composite ?? pythonPillars.gameEnvironment ?? 50;
      if (basePillarScore > 52) pillarDirection = 'over';
      else if (basePillarScore < 48) pillarDirection = 'under';
    } else {
      // SPREADS/H2H: Use market-specific composite
      // Python: >50 = AWAY edge, <50 = HOME edge
      // For HOME-side calculation, we invert
      const rawPyComposite = marketSpecific?.composite ?? pythonPillars.composite ?? 50;
      basePillarScore = side === 'home' ? (100 - rawPyComposite) : rawPyComposite;
      if (basePillarScore > 52) pillarDirection = side === 'home' ? 'home' : 'away';
      else if (basePillarScore < 48) pillarDirection = side === 'home' ? 'away' : 'home';
    }

    console.log(`CALIBRATION_DEBUG: Pillar direction - market=${marketType} side=${side} rawPy=${marketSpecific?.composite ?? pythonPillars.composite ?? 50} basePillar=${basePillarScore.toFixed(1)} direction=${pillarDirection}`);
  }

  // Calculate MARKET VALIDATION multiplier from TypeScript CEQ factors
  // This checks if the market has already priced in the pillar thesis
  const validation = calculateMarketValidation(
    marketEfficiency.score,
    lineupImpact.score,
    sentiment.score,
    pillarDirection || (side as 'home' | 'away' | 'over' | 'under')
  );

  // APPLY THE FRAMEWORK: Final CEQ = 50 + (pillarDeviation * validationMultiplier)
  // pillarDeviation = how far from neutral (50) the pillars lean
  // validationMultiplier = 0.7-1.3 based on market efficiency
  const pillarDeviation = basePillarScore - 50;
  let ceq = 50 + (pillarDeviation * validation.multiplier);

  console.log(`CALIBRATION_DEBUG: CEQ calculation - basePillar=${basePillarScore.toFixed(1)} deviation=${pillarDeviation.toFixed(1)} multiplier=${validation.multiplier.toFixed(2)} result=${ceq.toFixed(1)} reason="${validation.reason}"`);

  // BLEND with TypeScript signals if significant and Python is weak
  // If Python pillars are neutral (45-55), give more weight to TypeScript
  const pythonStrength = Math.abs(basePillarScore - 50);
  const tsStrength = Math.abs(tsCeq - 50);

  if (pythonStrength < 5 && tsStrength > 5) {
    // Python neutral, TypeScript has signal - blend 70/30 (TS/Py)
    const blendedCeq = tsCeq * 0.7 + ceq * 0.3;
    console.log(`CALIBRATION_DEBUG: Weak pillar blend - tsCeq=${tsCeq.toFixed(1)} pillars=${ceq.toFixed(1)} blended=${blendedCeq.toFixed(1)}`);
    ceq = blendedCeq;
  } else if (pythonStrength > 10) {
    // Strong Python signal - trust pillars more (blend 30/70)
    const blendedCeq = tsCeq * 0.3 + ceq * 0.7;
    console.log(`CALIBRATION_DEBUG: Strong pillar blend - tsCeq=${tsCeq.toFixed(1)} pillars=${ceq.toFixed(1)} blended=${blendedCeq.toFixed(1)}`);
    ceq = blendedCeq;
  } else {
    // Moderate Python signal - blend 50/50
    const blendedCeq = tsCeq * 0.5 + ceq * 0.5;
    console.log(`CALIBRATION_DEBUG: Moderate blend - tsCeq=${tsCeq.toFixed(1)} pillars=${ceq.toFixed(1)} blended=${blendedCeq.toFixed(1)}`);
    ceq = blendedCeq;
  }

  // ============================================================================
  // NO-FLIP GUARANTEE: CEQ can dampen pillar signal toward 50, but NEVER cross it
  // ============================================================================
  // If pillars have a clear direction (deviation >= 2), CEQ must not flip to other side
  // This prevents contradictions like: Pillars say Over, CEQ says Under
  if (pillarDirection && Math.abs(pillarDeviation) >= 2) {
    const preClamp = ceq;
    if (pillarDeviation > 0 && ceq < 50) {
      // Pillars lean positive (over/away) - CEQ can't go below 50
      ceq = 50;
    } else if (pillarDeviation < 0 && ceq > 50) {
      // Pillars lean negative (under/home) - CEQ can't go above 50
      ceq = 50;
    }
    if (ceq !== preClamp) {
      console.log(`CALIBRATION_DEBUG: NO-FLIP clamp - pillarDir=${pillarDirection} deviation=${pillarDeviation.toFixed(1)} pre=${preClamp.toFixed(1)} clamped=${ceq.toFixed(1)}`);
    }
  }

  // Apply juice adjustment based on book's odds vs market consensus
  const juiceAdj = calculateJuiceAdjustment(bookOdds, consensusOdds, allBooksOdds);
  ceq = ceq + juiceAdj.adjustment;

  ceq = Math.round(Math.min(Math.max(ceq, 0), 100));

  // Determine confidence
  const confidence = getCEQConfidence(ceq);

  // Determine side (if CEQ indicates edge)
  // Aligned with getCEQConfidence: 60+ = WATCH/EDGE/STRONG, <40 = OTHER side, 40-59 = PASS
  let edgeSide: MarketSide | null = null;
  if (ceq < 40) {
    // Strong signal on OTHER side (inverse calculation will show this)
    if (marketType === 'total') {
      edgeSide = side === 'over' ? 'under' : 'over';
    } else {
      edgeSide = side === 'home' ? 'away' : 'home';
    }
  } else if (ceq >= 60) {
    // Edge on THIS side (matches WATCH threshold)
    edgeSide = side;
  }

  // Calculate data quality metrics
  const pillarsWithData = tsPillars.filter((p: PillarResult) => p.weight > 0).length;
  const allVariables = [
    ...marketEfficiency.variables,
    ...lineupImpact.variables,
    ...gameEnvironment.variables,
    ...matchupDynamics.variables,
    ...sentiment.variables,
  ];
  const totalVariables = allVariables.filter(v => v.available).length;

  // Determine if CEQ should be displayed (need at least 2 pillars with data)
  const displayCEQ = pillarsWithData >= 2;
  const confidenceLabel: 'Low' | 'Medium' | 'High' | 'Insufficient' =
    pillarsWithData < 2 ? 'Insufficient' :
    pillarsWithData === 2 ? 'Low' :
    pillarsWithData === 3 ? 'Medium' : 'High';

  // Collect top drivers (reasons with significant scores)
  const topDrivers: string[] = [];

  // Add EV as the PRIMARY driver if significant
  if (ev !== undefined && !isNaN(ev) && Math.abs(ev) >= 2) {
    const evSign = ev > 0 ? '+' : '';
    if (ev >= 10) {
      topDrivers.push(`EV: Strong edge ${evSign}${ev.toFixed(1)}% vs market`);
    } else if (ev >= 5) {
      topDrivers.push(`EV: Good value ${evSign}${ev.toFixed(1)}% vs market`);
    } else if (ev >= 2) {
      topDrivers.push(`EV: ${evSign}${ev.toFixed(1)}% vs consensus`);
    } else if (ev <= -5) {
      topDrivers.push(`EV: Negative ${ev.toFixed(1)}% - avoid`);
    } else if (ev <= -2) {
      topDrivers.push(`EV: Below market ${ev.toFixed(1)}%`);
    }
  }

  const significantVars = allVariables
    .filter(v => v.available && Math.abs(v.score - 50) >= 5 && v.name !== 'EV');

  // Sort by deviation from neutral (50)
  significantVars.sort((a, b) => Math.abs(b.score - 50) - Math.abs(a.score - 50));

  // Take top 3 (or 2 if we already added juice)
  const remainingSlots = 3 - topDrivers.length;
  for (const v of significantVars.slice(0, remainingSlots)) {
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
      lineupImpact,
      gameEnvironment,
      matchupDynamics,
      sentiment,
    },
    topDrivers,
    dataQuality: {
      pillarsWithData,
      totalVariables,
      displayCEQ,
      confidenceLabel,
    },
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
    draw?: CEQResult;  // 3-way for soccer
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
    dataQuality: {
      pillarsWithData: number;
      totalVariables: number;
      displayCEQ: boolean;
      confidenceLabel: 'Low' | 'Medium' | 'High' | 'Insufficient';
    };
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
    draw?: number;  // 3-way for soccer
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
  },
  gameContext?: GameContextData,
  pythonPillars?: PythonPillarScores,  // Optional Python backend pillar scores
  pinnacleLines?: {  // Pinnacle sharp lines for FDV baseline
    spreads?: { home: number; away: number };
    totals?: number;
  },
  bookLines?: {  // Selected book's lines for FDV comparison
    spreads?: { home: number; away: number };
    totals?: number;
  },
  evData?: {  // EV percentages for each market/side
    spreads?: { home: number; away: number };
    h2h?: { home: number; away: number };
    totals?: { over: number; under: number };
  },
  sportKey?: string  // Sport key to determine market availability (e.g., soccer has no spreads)
): GameCEQ {
  const result: GameCEQ = { bestEdge: null };

  // Soccer doesn't have spreads - only moneyline (3-way) and totals
  const isSoccer = sportKey?.includes('soccer') ?? false;

  // Filter snapshots by market type
  // Note: outcome_type contains team names (not 'home'/'away'), so we include all outcomes for that market
  // MMI (momentum) calculation uses line movement which works with any side's data
  const spreadSnapshots = snapshots.filter(s => s.market === 'spreads');
  const h2hSnapshots = snapshots.filter(s => s.market === 'h2h');
  const totalSnapshots = snapshots.filter(s => s.market === 'totals' && (s.outcome_type === 'Over' || s.outcome_type === 'Under'));

  // Calculate spreads CEQ - ONLY ONE SIDE CAN HAVE EDGE
  // Skip spreads entirely for soccer (no spreads in soccer)
  // We calculate for home, then derive away as inverse (100 - home)
  if (gameOdds.spreads && !isSoccer) {
    const homeCEQ = calculateCEQ(
      'spread',
      'home',
      gameOdds.spreads.home.odds,
      openingLines.spreads?.home,
      gameOdds.spreads.home.line,
      spreadSnapshots,
      allBooksOdds.spreads?.home || [],
      consensusOdds.spreads?.home,
      gameContext,
      pythonPillars,  // Pass Python pillars
      pinnacleLines?.spreads?.home,  // Pinnacle home spread line
      bookLines?.spreads?.home,      // Selected book's home spread line
      evData?.spreads?.home          // EV for home spread
    );

    // Away CEQ is the inverse: if home is 78%, away is 22% (100 - 78)
    // This enforces mutual exclusivity - only one side can have edge
    const awayCEQValue = 100 - homeCEQ.ceq;
    const awayConfidence = getCEQConfidence(awayCEQValue);

    result.spreads = {
      home: homeCEQ,
      away: {
        ...homeCEQ,
        ceq: awayCEQValue,
        confidence: awayConfidence,
        side: awayCEQValue >= 53 ? 'away' : awayCEQValue <= 47 ? 'home' : null,
        topDrivers: awayCEQValue >= 53 ? homeCEQ.topDrivers : ['No edge on this side'],
      },
    };
  }

  // Calculate h2h CEQ - ONLY ONE SIDE CAN HAVE EDGE
  if (gameOdds.h2h) {
    const homeCEQ = calculateCEQ(
      'h2h',
      'home',
      gameOdds.h2h.home,
      openingLines.h2h?.home,
      undefined,
      h2hSnapshots,
      allBooksOdds.h2h?.home || [],
      consensusOdds.h2h?.home,
      gameContext,
      pythonPillars,  // Pass Python pillars
      undefined,      // No Pinnacle line for h2h (spreads only)
      undefined,      // No book line for h2h
      evData?.h2h?.home  // EV for home ML
    );

    // Check if this is a 3-way market (soccer)
    if (gameOdds.h2h.draw !== undefined) {
      // 3-way market: Calculate EV-based CEQ where only ONE outcome can have edge
      // Convert American odds to implied probabilities
      const homeOdds = gameOdds.h2h.home;
      const awayOdds = gameOdds.h2h.away;
      const drawOdds = gameOdds.h2h.draw;

      const homeImplied = americanToImpliedProbability(homeOdds);
      const awayImplied = americanToImpliedProbability(awayOdds);
      const drawImplied = americanToImpliedProbability(drawOdds);

      // Total implied > 100% due to juice
      const totalImplied = homeImplied + awayImplied + drawImplied;
      const juice = totalImplied - 1;

      // Remove juice to get fair probabilities (normalize to 100%)
      const homeFair = homeImplied / totalImplied;
      const awayFair = awayImplied / totalImplied;
      const drawFair = drawImplied / totalImplied;

      // Calculate edge for each outcome
      // Positive edge = book implied prob > fair prob (book is offering worse odds than fair)
      // Wait, that's backwards. Let me think...
      // If book implied = 57% and fair = 52%, the book thinks home is MORE likely
      // So betting home gives you LESS value (you're paying for 57% but only getting 52% true prob)
      // Edge = fair - implied (positive = value bet)
      const homeEdge = (homeFair - homeImplied) * 100;  // Scale to percentage
      const awayEdge = (awayFair - awayImplied) * 100;
      const drawEdge = (drawFair - drawImplied) * 100;

      // Find which outcome has the best edge
      const edges = [
        { side: 'home' as const, edge: homeEdge, implied: homeImplied, fair: homeFair },
        { side: 'away' as const, edge: awayEdge, implied: awayImplied, fair: awayFair },
        { side: 'draw' as const, edge: drawEdge, implied: drawImplied, fair: drawFair },
      ];
      edges.sort((a, b) => b.edge - a.edge);
      const bestEdge = edges[0];

      // Convert edge to CEQ (50 = neutral, >50 = edge on this side)
      // Scale: 5% edge = 70 CEQ, 10% edge = 80 CEQ, 15%+ edge = 85+ CEQ
      const edgeToCEQ = (edge: number): number => {
        if (edge <= 0) {
          // Negative edge: scale from 50 down to ~20
          return Math.max(20, Math.round(50 + edge * 3));
        } else {
          // Positive edge: scale from 50 up to ~85
          return Math.min(85, Math.round(50 + edge * 3));
        }
      };

      const homeCEQValue = Math.round(edgeToCEQ(homeEdge));
      const awayCEQValue = Math.round(edgeToCEQ(awayEdge));
      const drawCEQValue = Math.round(edgeToCEQ(drawEdge));

      const homeConfidence = getCEQConfidence(homeCEQValue);
      const awayConfidence = getCEQConfidence(awayCEQValue);
      const drawConfidence = getCEQConfidence(drawCEQValue);

      // Build reason strings
      const buildReason = (side: string, edge: number, implied: number, fair: number): string[] => {
        const edgeStr = edge > 0 ? `+${edge.toFixed(1)}%` : `${edge.toFixed(1)}%`;
        if (edge > 5) {
          return [`Strong value: ${side} (${edgeStr} edge vs fair odds)`];
        } else if (edge > 2) {
          return [`Slight value: ${side} (${edgeStr} edge)`];
        } else if (edge > 0) {
          return [`Marginal value: ${side} (${edgeStr})`];
        } else if (edge > -3) {
          return ['No significant edge on this side'];
        } else {
          return [`Negative value: ${edgeStr} (avoid)`];
        }
      };

      // Create base CEQ result structure for each outcome
      const createCEQResult = (ceq: number, confidence: CEQConfidence, side: MarketSide | null, reasons: string[]): CEQResult => ({
        ceq,
        confidence,
        side,
        pillars: homeCEQ.pillars,  // Use home pillars as base (they're all similar for h2h)
        topDrivers: reasons,
        dataQuality: homeCEQ.dataQuality,
      });

      result.h2h = {
        home: createCEQResult(
          homeCEQValue,
          homeConfidence,
          homeCEQValue >= 53 ? 'home' : null,
          buildReason('Home', homeEdge, homeImplied, homeFair)
        ),
        away: createCEQResult(
          awayCEQValue,
          awayConfidence,
          awayCEQValue >= 53 ? 'away' : null,
          buildReason('Away', awayEdge, awayImplied, awayFair)
        ),
        draw: createCEQResult(
          drawCEQValue,
          drawConfidence,
          drawCEQValue >= 53 ? 'draw' : null,
          buildReason('Draw', drawEdge, drawImplied, drawFair)
        ),
      };
    } else {
      // 2-way market: Away CEQ is the inverse
      const awayCEQValue = 100 - homeCEQ.ceq;
      const awayConfidence = getCEQConfidence(awayCEQValue);

      result.h2h = {
        home: homeCEQ,
        away: {
          ...homeCEQ,
          ceq: awayCEQValue,
          confidence: awayConfidence,
          side: awayCEQValue >= 53 ? 'away' : awayCEQValue <= 47 ? 'home' : null,
          topDrivers: awayCEQValue >= 53 ? homeCEQ.topDrivers : ['No edge on this side'],
        },
      };
    }
  }

  // Calculate totals CEQ - ONLY ONE SIDE CAN HAVE EDGE
  if (gameOdds.totals) {
    const overCEQ = calculateCEQ(
      'total',
      'over',
      gameOdds.totals.over,
      openingLines.totals?.over,
      gameOdds.totals.line,
      totalSnapshots,
      allBooksOdds.totals?.over || [],
      consensusOdds.totals?.over,
      gameContext,
      pythonPillars,  // Pass Python pillars
      pinnacleLines?.totals,  // Pinnacle total line
      bookLines?.totals,      // Selected book's total line
      evData?.totals?.over    // EV for over
    );

    // Under CEQ is the inverse
    const underCEQValue = 100 - overCEQ.ceq;
    const underConfidence = getCEQConfidence(underCEQValue);

    result.totals = {
      over: overCEQ,
      under: {
        ...overCEQ,
        ceq: underCEQValue,
        confidence: underConfidence,
        side: underCEQValue >= 53 ? 'under' : underCEQValue <= 47 ? 'over' : null,
        topDrivers: underCEQValue >= 53 ? overCEQ.topDrivers : ['No edge on this side'],
      },
    };
  }

  // Find best edge across all markets
  type BestEdgeCandidate = {
    market: 'spread' | 'h2h' | 'total';
    side: MarketSide;
    ceq: number;
    confidence: CEQConfidence;
    dataQuality: {
      pillarsWithData: number;
      totalVariables: number;
      displayCEQ: boolean;
      confidenceLabel: 'Low' | 'Medium' | 'High' | 'Insufficient';
    };
  };
  const candidates: BestEdgeCandidate[] = [];

  // Skip spread candidates for soccer (no spreads in soccer)
  if (result.spreads && !isSoccer) {
    if (result.spreads.home.confidence !== 'PASS') {
      candidates.push({ market: 'spread', side: 'home', ceq: result.spreads.home.ceq, confidence: result.spreads.home.confidence, dataQuality: result.spreads.home.dataQuality });
    }
    if (result.spreads.away.confidence !== 'PASS') {
      candidates.push({ market: 'spread', side: 'away', ceq: result.spreads.away.ceq, confidence: result.spreads.away.confidence, dataQuality: result.spreads.away.dataQuality });
    }
  }

  if (result.h2h) {
    if (result.h2h.home.confidence !== 'PASS') {
      candidates.push({ market: 'h2h', side: 'home', ceq: result.h2h.home.ceq, confidence: result.h2h.home.confidence, dataQuality: result.h2h.home.dataQuality });
    }
    if (result.h2h.away.confidence !== 'PASS') {
      candidates.push({ market: 'h2h', side: 'away', ceq: result.h2h.away.ceq, confidence: result.h2h.away.confidence, dataQuality: result.h2h.away.dataQuality });
    }
    // Include draw for 3-way markets (soccer)
    if (result.h2h.draw && result.h2h.draw.confidence !== 'PASS') {
      candidates.push({ market: 'h2h', side: 'draw', ceq: result.h2h.draw.ceq, confidence: result.h2h.draw.confidence, dataQuality: result.h2h.draw.dataQuality });
    }
  }

  if (result.totals) {
    if (result.totals.over.confidence !== 'PASS') {
      candidates.push({ market: 'total', side: 'over', ceq: result.totals.over.ceq, confidence: result.totals.over.confidence, dataQuality: result.totals.over.dataQuality });
    }
    if (result.totals.under.confidence !== 'PASS') {
      candidates.push({ market: 'total', side: 'under', ceq: result.totals.under.ceq, confidence: result.totals.under.confidence, dataQuality: result.totals.under.dataQuality });
    }
  }

  // Sort by CEQ (highest first) and take best
  // Include dataQuality so UI can decide whether to show the badge
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

// ============================================================================
// Helper: Fetch game context from Supabase
// ============================================================================

import { createClient, SupabaseClient } from '@supabase/supabase-js';

let supabaseClient: SupabaseClient | null = null;

function getSupabase(): SupabaseClient | null {
  if (typeof window !== 'undefined') {
    // Client-side - skip for now (data should be passed from server)
    return null;
  }

  if (!supabaseClient) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (url && key) {
      supabaseClient = createClient(url, key);
    }
  }
  return supabaseClient;
}

/**
 * Fetch game context data (team stats + weather) for EdgeScout pillar calculations
 * Call this on the server side to populate GameContextData
 */
export async function fetchGameContext(
  gameId: string,
  homeTeamName: string,
  awayTeamName: string,
  sport: string
): Promise<GameContextData> {
  const supabase = getSupabase();
  if (!supabase) {
    console.log(`[fetchGameContext] No supabase client`);
    return {};
  }

  try {
    // Map sport key to league format used in team_stats table
    // team_stats uses uppercase league names (NBA, NFL, NHL, etc.)
    const sportToLeague: Record<string, string> = {
      'basketball_nba': 'NBA',
      'basketball_ncaab': 'NCAAB',
      'americanfootball_nfl': 'NFL',
      'americanfootball_ncaaf': 'NCAAF',
      'icehockey_nhl': 'NHL',
      'soccer_epl': 'EPL',
      'baseball_mlb': 'MLB',
      // Also handle uppercase short format
      'NBA': 'NBA',
      'NCAAB': 'NCAAB',
      'NFL': 'NFL',
      'NCAAF': 'NCAAF',
      'NHL': 'NHL',
      'EPL': 'EPL',
      'MLB': 'MLB',
    };
    const league = sportToLeague[sport] || sport.toUpperCase();

    console.log(`[fetchGameContext] sport=${sport} -> league=${league}, home="${homeTeamName}", away="${awayTeamName}"`);

    // Fetch team stats for both teams
    const { data: teamStats, error } = await supabase
      .from('team_stats')
      .select('*')
      .eq('league', league)
      .or(`team_name.ilike.%${homeTeamName}%,team_name.ilike.%${awayTeamName}%`)
      .order('updated_at', { ascending: false })
      .limit(10);

    if (error) {
      console.log(`[fetchGameContext] Supabase error:`, error.message);
    }
    console.log(`[fetchGameContext] Found ${teamStats?.length || 0} team_stats rows`);

    // Find home and away team stats
    let homeTeam: TeamStatsData | undefined;
    let awayTeam: TeamStatsData | undefined;

    if (teamStats && teamStats.length > 0) {
      for (const stat of teamStats) {
        const name = stat.team_name?.toLowerCase() || '';
        const homeNameLower = homeTeamName.toLowerCase();
        const awayNameLower = awayTeamName.toLowerCase();

        if (!homeTeam && (name.includes(homeNameLower) || homeNameLower.includes(name))) {
          homeTeam = {
            team_id: stat.team_id,
            team_name: stat.team_name,
            pace: stat.pace,
            offensive_rating: stat.offensive_rating,
            defensive_rating: stat.defensive_rating,
            net_rating: stat.net_rating,
            wins: stat.wins,
            losses: stat.losses,
            win_pct: stat.win_pct,
            home_wins: stat.home_wins,
            home_losses: stat.home_losses,
            away_wins: stat.away_wins,
            away_losses: stat.away_losses,
            streak: stat.streak,
            points_per_game: stat.points_per_game,
            points_allowed_per_game: stat.points_allowed_per_game,
            injuries: stat.injuries || [],
          };
        }
        if (!awayTeam && (name.includes(awayNameLower) || awayNameLower.includes(name))) {
          awayTeam = {
            team_id: stat.team_id,
            team_name: stat.team_name,
            pace: stat.pace,
            offensive_rating: stat.offensive_rating,
            defensive_rating: stat.defensive_rating,
            net_rating: stat.net_rating,
            wins: stat.wins,
            losses: stat.losses,
            win_pct: stat.win_pct,
            home_wins: stat.home_wins,
            home_losses: stat.home_losses,
            away_wins: stat.away_wins,
            away_losses: stat.away_losses,
            streak: stat.streak,
            points_per_game: stat.points_per_game,
            points_allowed_per_game: stat.points_allowed_per_game,
            injuries: stat.injuries || [],
          };
        }
      }
    }

    // Fetch weather for outdoor games
    let weather: WeatherData | undefined;

    if (sport.includes('football') || sport.includes('baseball') || sport.includes('soccer')) {
      const { data: weatherData } = await supabase
        .from('game_weather')
        .select('*')
        .eq('game_id', gameId)
        .single();

      if (weatherData) {
        weather = {
          temperature_f: weatherData.temperature_f,
          wind_speed_mph: weatherData.wind_speed_mph,
          wind_gust_mph: weatherData.wind_gust_mph,
          precipitation_pct: weatherData.precipitation_pct,
          conditions: weatherData.conditions,
          weather_impact_score: weatherData.weather_impact_score,
          is_dome: weatherData.is_dome,
        };
      }
    }

    console.log(`[fetchGameContext] Result: homeTeam=${homeTeam?.team_name || 'NOT FOUND'}, awayTeam=${awayTeam?.team_name || 'NOT FOUND'}, weather=${weather ? 'present' : 'none'}`);

    return {
      homeTeam,
      awayTeam,
      weather,
      league,  // Use the league we calculated at the top
    };
  } catch (error) {
    console.error('[fetchGameContext] Error:', error);
    return {};
  }
}
