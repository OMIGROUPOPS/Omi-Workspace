'use client';

import { useState, useEffect } from 'react';

/**
 * Python Backend Pillar Scores
 *
 * These are the REAL 6 pillars calculated by the Python backend:
 * 1. Execution (20%) - Injuries, lineup uncertainty
 * 2. Incentives (10%) - Playoffs, motivation, rivalries
 * 3. Shocks (25%) - Line movement, velocity, steam moves
 * 4. Time Decay (10%) - Rest days, back-to-back, travel
 * 5. Flow (25%) - Sharp money, book disagreement
 * 6. Game Environment (10%) - Pace, weather, expected totals
 */

interface PillarScores {
  execution: number;
  incentives: number;
  shocks: number;
  timeDecay: number;
  flow: number;
  gameEnvironment: number;
  composite: number;
}

interface PillarDetail {
  score: number;
  reasoning: string;
  [key: string]: any;
}

interface PillarData {
  game_id: string;
  sport: string;
  home_team: string;
  away_team: string;
  pillar_scores: PillarScores;
  pillars?: {
    execution?: PillarDetail;
    incentives?: PillarDetail;
    shocks?: PillarDetail;
    time_decay?: PillarDetail;
    flow?: PillarDetail;
    game_environment?: PillarDetail;
  };
  overall_confidence: 'PASS' | 'WATCH' | 'EDGE' | 'STRONG' | 'RARE';
  best_bet: string | null;
  best_edge: number;
  source: string;
}

// Pillar weight configuration matching backend config.py
const PILLAR_CONFIG = {
  execution: { name: 'Execution', weight: 0.20, description: 'Injuries, lineup availability' },
  incentives: { name: 'Incentives', weight: 0.10, description: 'Playoffs, motivation, rivalries' },
  shocks: { name: 'Shocks', weight: 0.25, description: 'Line movement, velocity, steam' },
  timeDecay: { name: 'Time Decay', weight: 0.10, description: 'Rest, travel, fatigue' },
  flow: { name: 'Flow', weight: 0.25, description: 'Sharp money, book disagreement' },
  gameEnvironment: { name: 'Game Env', weight: 0.10, description: 'Pace, weather, totals' },
};

type MarketType = 'spread' | 'total' | 'moneyline';

/**
 * Transform pillar score to directional display
 *
 * For spreads/moneyline: <50% = home edge, >50% = away edge
 * For totals: <50% = under edge, >50% = over edge
 *
 * Returns: { displayPct, direction, barPosition }
 * - displayPct: The strength percentage (always shows how strong the lean is)
 * - direction: 'left' (home/under) or 'right' (away/over) or 'neutral'
 * - barPosition: 0-100 position for the visual bar
 */
function getDirectionalDisplay(rawScore: number, marketType: MarketType): {
  displayPct: number;
  direction: 'left' | 'right' | 'neutral';
  barPosition: number;
  strengthLabel: string;
} {
  // For totals, the interpretation is:
  // rawScore < 50 = under lean (display as left/under edge)
  // rawScore > 50 = over lean (display as right/over edge)

  // For spreads/moneyline:
  // rawScore < 50 = home edge (display as left/home edge)
  // rawScore > 50 = away edge (display as right/away edge)

  const deviation = Math.abs(rawScore - 50);

  if (deviation < 5) {
    return { displayPct: rawScore, direction: 'neutral', barPosition: rawScore, strengthLabel: 'Neutral' };
  }

  if (rawScore < 50) {
    // Left side (home/under)
    const strength = 50 + deviation; // Convert 35% to "65% edge"
    return {
      displayPct: strength,
      direction: 'left',
      barPosition: rawScore,
      strengthLabel: deviation >= 25 ? 'Strong' : deviation >= 10 ? 'Lean' : 'Slight'
    };
  } else {
    // Right side (away/over)
    const strength = rawScore; // 65% stays as 65%
    return {
      displayPct: strength,
      direction: 'right',
      barPosition: rawScore,
      strengthLabel: deviation >= 25 ? 'Strong' : deviation >= 10 ? 'Lean' : 'Slight'
    };
  }
}

function getScoreColor(direction: 'left' | 'right' | 'neutral', strength: number) {
  if (direction === 'neutral') {
    return { bg: 'bg-zinc-700/50', border: 'border-zinc-600', text: 'text-zinc-400', dot: 'bg-zinc-400' };
  }
  if (strength >= 70) {
    return direction === 'left'
      ? { bg: 'bg-amber-500/20', border: 'border-amber-500/40', text: 'text-amber-400', dot: 'bg-amber-400' }
      : { bg: 'bg-emerald-500/20', border: 'border-emerald-500/40', text: 'text-emerald-400', dot: 'bg-emerald-400' };
  }
  if (strength >= 58) {
    return direction === 'left'
      ? { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-300', dot: 'bg-amber-300' }
      : { bg: 'bg-blue-500/20', border: 'border-blue-500/40', text: 'text-blue-400', dot: 'bg-blue-400' };
  }
  return { bg: 'bg-zinc-700/30', border: 'border-zinc-600', text: 'text-zinc-400', dot: 'bg-zinc-400' };
}

function getConfidenceStyle(conf: string) {
  switch (conf) {
    case 'RARE': return { bg: 'bg-purple-500/20', border: 'border-purple-500/40', text: 'text-purple-400' };
    case 'STRONG': return { bg: 'bg-emerald-500/20', border: 'border-emerald-500/40', text: 'text-emerald-400' };
    case 'EDGE': return { bg: 'bg-blue-500/20', border: 'border-blue-500/40', text: 'text-blue-400' };
    case 'WATCH': return { bg: 'bg-amber-500/20', border: 'border-amber-500/40', text: 'text-amber-400' };
    default: return { bg: 'bg-zinc-800/50', border: 'border-zinc-700/50', text: 'text-zinc-500' };
  }
}

interface PythonPillarBreakdownProps {
  gameId: string;
  sport: string;
  homeTeam: string;
  awayTeam: string;
  marketType?: MarketType;
  spreadLine?: number;  // e.g., -5.5 for home team
  totalLine?: number;   // e.g., 220.5
  compact?: boolean;
}

export function PythonPillarBreakdown({
  gameId,
  sport,
  homeTeam,
  awayTeam,
  marketType = 'spread',
  spreadLine,
  totalLine,
  compact = false
}: PythonPillarBreakdownProps) {
  const [pillarData, setPillarData] = useState<PillarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPillars() {
      setLoading(true);
      setError(null);

      console.log(`[PythonPillarBreakdown] Fetching pillars for gameId=${gameId}, sport=${sport}`);

      try {
        const url = `/api/pillars/calculate?game_id=${encodeURIComponent(gameId)}&sport=${encodeURIComponent(sport)}`;
        console.log(`[PythonPillarBreakdown] Calling: ${url}`);

        const response = await fetch(url);
        console.log(`[PythonPillarBreakdown] Response status: ${response.status}`);

        if (!response.ok) {
          const data = await response.json();
          console.error(`[PythonPillarBreakdown] Error response:`, data);
          throw new Error(data.error || `Failed to fetch pillars: ${response.status}`);
        }

        const data = await response.json();
        console.log(`[PythonPillarBreakdown] Got pillar data:`, data);
        setPillarData(data);
      } catch (err) {
        console.error(`[PythonPillarBreakdown] Fetch error:`, err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    if (gameId && sport) {
      fetchPillars();
    } else {
      console.log(`[PythonPillarBreakdown] Skipping fetch - gameId=${gameId}, sport=${sport}`);
    }
  }, [gameId, sport]);

  // Generate labels based on market type
  const getLabels = () => {
    if (marketType === 'total') {
      return {
        left: 'Under',
        right: 'Over',
        leftFull: totalLine ? `Under ${totalLine}` : 'Under',
        rightFull: totalLine ? `Over ${totalLine}` : 'Over',
      };
    }
    // For spread and moneyline
    const homeLabel = spreadLine !== undefined && marketType === 'spread'
      ? `${homeTeam} ${spreadLine > 0 ? '+' : ''}${spreadLine}`
      : homeTeam;
    const awayLabel = spreadLine !== undefined && marketType === 'spread'
      ? `${awayTeam} ${spreadLine > 0 ? -spreadLine : '+' + Math.abs(spreadLine)}`
      : awayTeam;
    return {
      left: homeTeam.slice(0, 8),
      right: awayTeam.slice(0, 8),
      leftFull: marketType === 'moneyline' ? `${homeTeam} ML` : homeLabel,
      rightFull: marketType === 'moneyline' ? `${awayTeam} ML` : awayLabel,
    };
  };

  const labels = getLabels();

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <div className="animate-pulse space-y-2">
          <div className="h-4 bg-zinc-700 rounded w-1/3"></div>
          <div className="space-y-1">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-3 bg-zinc-800 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    const isConnectionError = error.includes('connect') || error.includes('ECONNREFUSED') || error.includes('fetch');
    return (
      <div className="bg-zinc-900 border border-amber-500/30 rounded-lg p-4">
        <div className="text-center">
          <p className="text-amber-400 text-sm mb-1">
            {isConnectionError ? 'Python Backend Offline' : 'Pillar Calculation Error'}
          </p>
          <p className="text-zinc-500 text-xs mb-2">{error}</p>
          {isConnectionError && (
            <p className="text-zinc-600 text-xs">
              Run: <code className="bg-zinc-800 px-1 rounded">cd backend && python main.py</code>
            </p>
          )}
          <button
            onClick={() => window.location.reload()}
            className="mt-2 text-xs text-emerald-400 hover:text-emerald-300"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!pillarData) {
    return null;
  }

  const { pillar_scores, pillars, overall_confidence } = pillarData;
  const confStyle = getConfidenceStyle(overall_confidence);

  // Get directional display for composite
  const compositeDir = getDirectionalDisplay(pillar_scores.composite, marketType);
  const compositeColor = getScoreColor(compositeDir.direction, compositeDir.displayPct);

  // Build composite direction label
  const getCompositeLabel = () => {
    if (compositeDir.direction === 'neutral') return 'Neutral';
    const side = compositeDir.direction === 'left' ? labels.left : labels.right;
    return `${compositeDir.displayPct}% ${side}`;
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
      {/* Header */}
      <div className={`px-3 py-2 ${confStyle.bg} border-b ${confStyle.border}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-zinc-100">6-Pillar Analysis</h3>
            <span className="text-[10px] text-zinc-400">
              {marketType === 'total' ? 'Totals' : marketType === 'moneyline' ? 'Moneyline' : 'Spread'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-right">
              <span className={`text-lg font-bold font-mono ${compositeColor.text}`}>
                {getCompositeLabel()}
              </span>
            </div>
            <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${confStyle.bg} ${confStyle.text}`}>
              {overall_confidence}
            </span>
          </div>
        </div>
      </div>

      {/* Column Headers */}
      <div className="px-3 py-1.5 border-b border-zinc-800 flex items-center text-[9px] text-zinc-500">
        <span className="w-20"></span>
        <div className="flex-1 flex justify-between px-1">
          <span className="text-amber-400/70">{labels.leftFull}</span>
          <span className="text-zinc-600">50%</span>
          <span className="text-emerald-400/70">{labels.rightFull}</span>
        </div>
        <span className="w-20 text-right">Edge</span>
      </div>

      {/* Pillar Bars */}
      <div className="p-3 space-y-2">
        {Object.entries(PILLAR_CONFIG).map(([key, config]) => {
          const rawScore = pillar_scores[key as keyof PillarScores] ?? 50;
          // Map camelCase keys to snake_case for pillar details
          const detailKey = key === 'timeDecay' ? 'time_decay' : key === 'gameEnvironment' ? 'game_environment' : key;
          const detail = pillars?.[detailKey as keyof typeof pillars];
          const hasDetail = detail?.reasoning;

          // Get directional display
          const dir = getDirectionalDisplay(rawScore, marketType);
          const color = getScoreColor(dir.direction, dir.displayPct);

          // Build edge label
          const edgeLabel = dir.direction === 'neutral'
            ? 'Neutral'
            : `${dir.displayPct}% ${dir.direction === 'left' ? labels.left : labels.right}`;

          return (
            <div key={key}>
              <div
                className={`flex items-center gap-2 ${hasDetail ? 'cursor-pointer hover:bg-zinc-800/50' : ''} rounded px-1 -mx-1`}
                onClick={() => hasDetail && setExpanded(expanded === key ? null : key)}
              >
                <span className="text-[10px] text-zinc-400 w-20 truncate" title={config.description}>
                  {config.name}
                  <span className="text-zinc-600 ml-1">({Math.round(config.weight * 100)}%)</span>
                </span>

                {/* Score bar - visual representation */}
                <div className="flex-1 h-4 bg-zinc-800 rounded-full overflow-hidden relative">
                  {/* Center line at 50% */}
                  <div className="absolute left-1/2 top-0 bottom-0 w-px bg-zinc-600 z-10"></div>

                  {/* Left zone background (subtle) */}
                  <div className="absolute left-0 top-0 bottom-0 w-1/2 bg-amber-500/5"></div>

                  {/* Right zone background (subtle) */}
                  <div className="absolute right-0 top-0 bottom-0 w-1/2 bg-emerald-500/5"></div>

                  {/* Score fill - from center to position */}
                  {dir.direction !== 'neutral' && (
                    <div
                      className={`absolute top-0 bottom-0 ${
                        dir.direction === 'left' ? 'bg-amber-500/30' : 'bg-emerald-500/30'
                      }`}
                      style={{
                        left: dir.direction === 'left' ? `${dir.barPosition}%` : '50%',
                        width: dir.direction === 'left'
                          ? `${50 - dir.barPosition}%`
                          : `${dir.barPosition - 50}%`,
                      }}
                    ></div>
                  )}

                  {/* Score dot */}
                  <div
                    className={`absolute top-1/2 w-3 h-3 rounded-full border-2 border-zinc-900 ${color.dot} z-20`}
                    style={{
                      left: `${dir.barPosition}%`,
                      transform: 'translateX(-50%) translateY(-50%)'
                    }}
                  ></div>
                </div>

                {/* Edge label */}
                <span className={`text-[10px] w-20 text-right font-mono ${color.text}`}>
                  {edgeLabel}
                </span>

                {hasDetail && (
                  <svg
                    className={`w-3 h-3 text-zinc-500 transition-transform ${expanded === key ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                )}
              </div>

              {/* Expanded reasoning */}
              {expanded === key && detail?.reasoning && (
                <div className={`mt-1 ml-[88px] p-2 rounded ${color.bg} border ${color.border}`}>
                  <p className="text-[10px] text-zinc-300 leading-relaxed">{detail.reasoning}</p>

                  {/* Show breakdown details if available */}
                  {key === 'execution' && detail.breakdown && (
                    <div className="mt-2 text-[9px] text-zinc-400 space-y-0.5">
                      <div>Home Injuries: {(detail.home_injury_impact * 100).toFixed(0)}%</div>
                      <div>Away Injuries: {(detail.away_injury_impact * 100).toFixed(0)}%</div>
                    </div>
                  )}
                  {key === 'incentives' && detail.breakdown && (
                    <div className="mt-2 text-[9px] text-zinc-400 space-y-0.5">
                      <div>Home Motivation: {(detail.home_motivation * 100).toFixed(0)}%</div>
                      <div>Away Motivation: {(detail.away_motivation * 100).toFixed(0)}%</div>
                      {detail.is_rivalry && <div className="text-amber-400">Rivalry Game</div>}
                    </div>
                  )}
                  {key === 'timeDecay' && detail.breakdown && (
                    <div className="mt-2 text-[9px] text-zinc-400 space-y-0.5">
                      <div>Home Rest: {detail.home_rest_days} days</div>
                      <div>Away Rest: {detail.away_rest_days} days</div>
                    </div>
                  )}
                  {key === 'flow' && detail.breakdown && (
                    <div className="mt-2 text-[9px] text-zinc-400 space-y-0.5">
                      <div>Consensus Line: {detail.consensus_line}</div>
                      <div>Sharp Line: {detail.sharpest_line}</div>
                      <div>Book Agreement: {(detail.book_agreement * 100).toFixed(0)}%</div>
                    </div>
                  )}
                  {key === 'gameEnvironment' && detail.breakdown && (
                    <div className="mt-2 text-[9px] text-zinc-400 space-y-0.5">
                      {detail.breakdown.pace_factor && <div>Pace Factor: {detail.breakdown.pace_factor}</div>}
                      {detail.breakdown.expected_total && <div>Expected Total: {detail.breakdown.expected_total}</div>}
                      {detail.breakdown.weather_impact && <div>Weather: {detail.breakdown.weather_impact}</div>}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      {!compact && (
        <div className="px-3 pb-2 border-t border-zinc-800 pt-2">
          <div className="flex items-center justify-between text-[9px] text-zinc-500">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              {labels.leftFull}
            </span>
            <span className="text-zinc-600">50% = No Edge</span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              {labels.rightFull}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact version for dashboard cards
 */
export function PythonPillarSummary({ gameId, sport }: { gameId: string; sport: string }) {
  const [pillarData, setPillarData] = useState<PillarData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPillars() {
      try {
        const response = await fetch(
          `/api/pillars/calculate?game_id=${encodeURIComponent(gameId)}&sport=${encodeURIComponent(sport)}`
        );
        if (response.ok) {
          const data = await response.json();
          setPillarData(data);
        }
      } catch (err) {
        // Silently fail for summary
      } finally {
        setLoading(false);
      }
    }

    if (gameId && sport) {
      fetchPillars();
    }
  }, [gameId, sport]);

  if (loading || !pillarData) {
    return null;
  }

  const { pillar_scores, overall_confidence } = pillarData;
  const confStyle = getConfidenceStyle(overall_confidence);

  return (
    <div className="flex items-center gap-2">
      <span className={`text-sm font-bold font-mono ${confStyle.text}`}>{pillar_scores.composite}%</span>
      <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${confStyle.bg} ${confStyle.text}`}>
        {overall_confidence}
      </span>
    </div>
  );
}
