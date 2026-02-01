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
// Python Backend Pillar Scores (Harmonization)
// ============================================================================
// When Python backend is available, we use its pillar scores to boost/adjust
// the TypeScript CEQ calculation. This combines:
// - Python's game-level analysis (injuries, motivation, rest, sharp money)
// - TypeScript's market-specific analysis (per-book odds comparison)

export interface PythonPillarScores {
  execution: number;    // 0-100: Injuries, weather, lineup (→ Player Utilization)
  incentives: number;   // 0-100: Playoffs, motivation, rivalries (→ Game Environment)
  shocks: number;       // 0-100: Breaking news, line movement timing (→ Market Efficiency boost)
  timeDecay: number;    // 0-100: Rest days, back-to-back, travel (→ Game Environment)
  flow: number;         // 0-100: Sharp money, book disagreement (→ Sentiment)
  composite: number;    // 0-100: Weighted average of all pillars
}

/**
 * Maps Python pillar scores to TypeScript pillar adjustments
 * Returns adjustments to be applied to each TypeScript pillar
 */
function mapPythonToTypeScriptPillars(pythonPillars: PythonPillarScores): {
  marketEfficiencyBoost: number;
  playerUtilizationScore: number;
  gameEnvironmentScore: number;
  sentimentScore: number;
} {
  // Python Execution (injuries) → TypeScript Player Utilization
  // Score is 0-100, 50 = neutral
  const playerUtilizationScore = pythonPillars.execution;

  // Python Incentives + Time Decay → TypeScript Game Environment
  // Weighted average: incentives 60%, time decay 40%
  const gameEnvironmentScore = Math.round(
    pythonPillars.incentives * 0.6 + pythonPillars.timeDecay * 0.4
  );

  // Python Shocks → Market Efficiency boost
  // If shocks detected (score != 50), boost market efficiency signal
  const shockDeviation = Math.abs(pythonPillars.shocks - 50);
  const marketEfficiencyBoost = shockDeviation > 10 ? shockDeviation * 0.5 : 0;

  // Python Flow (sharp money) → TypeScript Sentiment
  const sentimentScore = pythonPillars.flow;

  return {
    marketEfficiencyBoost,
    playerUtilizationScore,
    gameEnvironmentScore,
    sentimentScore,
  };
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
// PILLAR 3: GAME ENVIRONMENT (ESPN + Weather data)
// ============================================================================

export interface TeamStatsData {
  team_id: string;
  team_name: string;
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
  bookLine?: number       // Selected book's line for FDV comparison
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
  let playerUtilization = calculatePlayerUtilizationPillar();
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

    // Player Utilization: Use Python's Execution (injuries) if available
    if (pythonPillars.execution !== 50) {
      playerUtilization = {
        score: mapped.playerUtilizationScore,
        weight: 0.20,  // Now has real weight
        variables: [{
          name: 'Injuries',
          value: pythonPillars.execution - 50,
          score: mapped.playerUtilizationScore,
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

  // Calculate weighted CEQ from all pillars
  const pillars = [marketEfficiency, playerUtilization, gameEnvironment, matchupDynamics, sentiment];
  const totalWeight = pillars.reduce((acc, p) => acc + p.weight, 0);

  let ceq = 50;
  if (totalWeight > 0) {
    ceq = pillars.reduce((acc, p) => acc + p.score * p.weight, 0) / totalWeight;
  }

  // If Python pillars available, also blend with Python composite (30% Python, 70% TS)
  if (pythonPillars && pythonPillars.composite !== 50) {
    ceq = ceq * 0.7 + pythonPillars.composite * 0.3;
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

  // Calculate data quality metrics
  const pillarsWithData = pillars.filter(p => p.weight > 0).length;
  const allVariables = [
    ...marketEfficiency.variables,
    ...playerUtilization.variables,
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
  const significantVars = allVariables
    .filter(v => v.available && Math.abs(v.score - 50) >= 5);

  // Sort by deviation from neutral (50)
  significantVars.sort((a, b) => Math.abs(b.score - 50) - Math.abs(a.score - 50));

  // Take top 3
  for (const v of significantVars.slice(0, 3)) {
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
  }
): GameCEQ {
  const result: GameCEQ = { bestEdge: null };

  // Filter snapshots by market type
  // Note: outcome_type contains team names (not 'home'/'away'), so we include all outcomes for that market
  // MMI (momentum) calculation uses line movement which works with any side's data
  const spreadSnapshots = snapshots.filter(s => s.market === 'spreads');
  const h2hSnapshots = snapshots.filter(s => s.market === 'h2h');
  const totalSnapshots = snapshots.filter(s => s.market === 'totals' && (s.outcome_type === 'Over' || s.outcome_type === 'Under'));

  // Calculate spreads CEQ - ONLY ONE SIDE CAN HAVE EDGE
  // We calculate for home, then derive away as inverse (100 - home)
  if (gameOdds.spreads) {
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
      bookLines?.spreads?.home       // Selected book's home spread line
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
        side: awayCEQValue >= 56 ? 'away' : awayCEQValue <= 44 ? 'home' : null,
        topDrivers: awayCEQValue >= 56 ? homeCEQ.topDrivers : ['No edge on this side'],
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
      undefined       // No book line for h2h
    );

    // Away CEQ is the inverse
    const awayCEQValue = 100 - homeCEQ.ceq;
    const awayConfidence = getCEQConfidence(awayCEQValue);

    result.h2h = {
      home: homeCEQ,
      away: {
        ...homeCEQ,
        ceq: awayCEQValue,
        confidence: awayConfidence,
        side: awayCEQValue >= 56 ? 'away' : awayCEQValue <= 44 ? 'home' : null,
        topDrivers: awayCEQValue >= 56 ? homeCEQ.topDrivers : ['No edge on this side'],
      },
    };
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
      bookLines?.totals       // Selected book's total line
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
        side: underCEQValue >= 56 ? 'under' : underCEQValue <= 44 ? 'over' : null,
        topDrivers: underCEQValue >= 56 ? overCEQ.topDrivers : ['No edge on this side'],
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

  if (result.spreads) {
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
  if (!supabase) return {};

  try {
    const sportFilter = sport.split('_')[0] || sport;

    // Fetch team stats for both teams
    const { data: teamStats } = await supabase
      .from('team_stats')
      .select('*')
      .eq('sport', sportFilter)
      .or(`team_name.ilike.%${homeTeamName}%,team_name.ilike.%${awayTeamName}%`)
      .order('updated_at', { ascending: false })
      .limit(10);

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

    const league = sport.split('_')[1] || sport;

    return {
      homeTeam,
      awayTeam,
      weather,
      league,
    };
  } catch (error) {
    console.error('[fetchGameContext] Error:', error);
    return {};
  }
}
