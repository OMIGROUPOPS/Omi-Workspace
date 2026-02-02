'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import { RefreshCw, User, TrendingUp, Filter, ExternalLink, Clock, ChevronDown, ChevronRight } from 'lucide-react';
import Link from 'next/link';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const SPORTS = [
  { key: 'all', label: 'All Sports', emoji: '' },
  { key: 'basketball_nba', label: 'NBA', emoji: '\u{1F3C0}' },
  { key: 'americanfootball_nfl', label: 'NFL', emoji: '\u{1F3C8}' },
  { key: 'icehockey_nhl', label: 'NHL', emoji: '\u{1F3D2}' },
  { key: 'baseball_mlb', label: 'MLB', emoji: '\u{26BE}' },
  { key: 'basketball_ncaab', label: 'NCAAB', emoji: '\u{1F3C0}' },
];

// Prop type labels for clarity
const PROP_TYPE_LABELS: Record<string, string> = {
  player_points: 'Points',
  player_assists: 'Assists',
  player_rebounds: 'Rebounds',
  player_steals: 'Steals',
  player_blocks: 'Blocks',
  player_threes: '3-Pointers',
  player_points_rebounds_assists: 'Pts+Rebs+Asts',
  player_points_rebounds: 'Pts+Rebs',
  player_points_assists: 'Pts+Asts',
  player_rebounds_assists: 'Rebs+Asts',
  player_double_double: 'Double-Double',
  player_triple_double: 'Triple-Double',
  player_pass_yds: 'Pass Yards',
  player_pass_tds: 'Pass TDs',
  player_pass_completions: 'Completions',
  player_pass_attempts: 'Pass Attempts',
  player_pass_interceptions: 'INTs',
  player_rush_yds: 'Rush Yards',
  player_rush_attempts: 'Rush Attempts',
  player_reception_yds: 'Rec Yards',
  player_receptions: 'Receptions',
  player_anytime_td: 'Anytime TD',
  player_goals: 'Goals',
  player_shots_on_goal: 'Shots on Goal',
  player_blocked_shots: 'Blocked Shots',
  batter_hits: 'Hits',
  batter_home_runs: 'Home Runs',
  batter_total_bases: 'Total Bases',
  batter_rbis: 'RBIs',
  batter_runs_scored: 'Runs',
  batter_strikeouts: 'Strikeouts',
  pitcher_strikeouts: 'Strikeouts',
  pitcher_hits_allowed: 'Hits Allowed',
  pitcher_outs: 'Outs',
};

// Preferred books for CEQ calculation
const SHARP_BOOKS = ['pinnacle', 'betcris', 'bookmaker'];
const RETAIL_BOOKS = ['fanduel', 'draftkings', 'betmgm', 'caesars'];

interface PropOutcome {
  player: string;
  propType: string;
  line: number;
  side: 'Over' | 'Under';
  odds: number;
  book: string;
}

interface ParsedProp {
  player: string;
  propType: string;
  propTypeLabel: string;
  line: number;
  overOdds: { book: string; odds: number }[];
  underOdds: { book: string; odds: number }[];
  overCEQ: number;
  underCEQ: number;
  bestOverBook: string;
  bestUnderBook: string;
  bestOverOdds: number;
  bestUnderOdds: number;
}

interface GameWithProps {
  gameId: string;
  homeTeam: string;
  awayTeam: string;
  sport: string;
  commenceTime: string;
  props: ParsedProp[];
}

// Convert American odds to implied probability
function oddsToProb(americanOdds: number): number {
  if (americanOdds > 0) {
    return 100 / (americanOdds + 100);
  } else {
    return Math.abs(americanOdds) / (Math.abs(americanOdds) + 100);
  }
}

// Calculate CEQ for a prop side based on odds comparison
// CEQ represents edge confidence: 50 = neutral, higher = more confident edge
function calculatePropCEQ(
  sideOdds: { book: string; odds: number }[],
  oppositeSideOdds: { book: string; odds: number }[]
): number {
  if (sideOdds.length === 0) return 50;

  // Get best odds for this side
  const bestOdds = Math.max(...sideOdds.map(o => o.odds));
  const bestProb = oddsToProb(bestOdds);

  // Calculate consensus probability from all books
  const allProbs = sideOdds.map(o => oddsToProb(o.odds));
  const avgProb = allProbs.reduce((a, b) => a + b, 0) / allProbs.length;

  // Calculate fair value using opposite side (removes vig)
  let fairProb = 0.5; // default
  if (oppositeSideOdds.length > 0) {
    const oppProbs = oppositeSideOdds.map(o => oddsToProb(o.odds));
    const avgOppProb = oppProbs.reduce((a, b) => a + b, 0) / oppProbs.length;
    // Fair value: normalize to remove vig
    const totalProb = avgProb + avgOppProb;
    if (totalProb > 0) {
      fairProb = avgProb / totalProb;
    }
  }

  // Check for sharp book line
  const sharpOdds = sideOdds.filter(o => SHARP_BOOKS.includes(o.book.toLowerCase()));
  let sharpProb = avgProb;
  if (sharpOdds.length > 0) {
    sharpProb = sharpOdds.map(o => oddsToProb(o.odds)).reduce((a, b) => a + b, 0) / sharpOdds.length;
  }

  // CEQ Calculation:
  // 1. Base: 50 (neutral)
  // 2. Edge from best odds vs consensus (retail vs market)
  // 3. Edge from sharp line disagreement

  let ceq = 50;

  // Odds edge: if best odds imply lower probability than average, that's value
  const oddsEdge = (avgProb - bestProb) * 100; // positive = edge
  ceq += oddsEdge * 3; // Scale up the edge

  // Sharp disagreement: if sharp books have worse odds, retail has value
  const sharpEdge = (sharpProb - bestProb) * 100;
  ceq += sharpEdge * 2;

  // Normalize to 0-100 range
  ceq = Math.max(0, Math.min(100, ceq));

  return Math.round(ceq);
}

export default function PlayerPropsPage() {
  const [gamesWithProps, setGamesWithProps] = useState<GameWithProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSport, setSelectedSport] = useState('all');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [expandedGames, setExpandedGames] = useState<Set<string>>(new Set());
  const [expandedPlayers, setExpandedPlayers] = useState<Set<string>>(new Set());
  const [minCEQ, setMinCEQ] = useState(56); // Minimum CEQ to show

  // Fetch games with prop markets
  const fetchPropsFromCachedOdds = useCallback(async () => {
    setLoading(true);
    try {
      let query = supabase
        .from('cached_odds')
        .select('game_data');

      if (selectedSport !== 'all') {
        query = query.eq('game_data->>sport_key', selectedSport);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;

      const gamesData: GameWithProps[] = [];

      for (const row of data || []) {
        const game = row.game_data;
        if (!game?.bookmakers) continue;

        // Parse all prop outcomes from all bookmakers
        const propOutcomes: PropOutcome[] = [];

        for (const bookmaker of game.bookmakers) {
          for (const market of bookmaker.markets || []) {
            // Check if this is a prop market
            const isProp = market.key.startsWith('player_') ||
                          market.key.startsWith('pitcher_') ||
                          market.key.startsWith('batter_');

            if (!isProp) continue;

            for (const outcome of market.outcomes || []) {
              if (!outcome.description || !outcome.name || outcome.point === undefined) continue;

              propOutcomes.push({
                player: outcome.description,
                propType: market.key,
                line: outcome.point,
                side: outcome.name as 'Over' | 'Under',
                odds: outcome.price,
                book: bookmaker.key,
              });
            }
          }
        }

        if (propOutcomes.length === 0) continue;

        // Group outcomes by player + propType + line
        const groupedProps = new Map<string, {
          player: string;
          propType: string;
          line: number;
          overOdds: { book: string; odds: number }[];
          underOdds: { book: string; odds: number }[];
        }>();

        for (const outcome of propOutcomes) {
          const key = `${outcome.player}|${outcome.propType}|${outcome.line}`;

          if (!groupedProps.has(key)) {
            groupedProps.set(key, {
              player: outcome.player,
              propType: outcome.propType,
              line: outcome.line,
              overOdds: [],
              underOdds: [],
            });
          }

          const prop = groupedProps.get(key)!;
          if (outcome.side === 'Over') {
            prop.overOdds.push({ book: outcome.book, odds: outcome.odds });
          } else {
            prop.underOdds.push({ book: outcome.book, odds: outcome.odds });
          }
        }

        // Calculate CEQ for each prop and create ParsedProp objects
        const parsedProps: ParsedProp[] = [];

        for (const [, prop] of groupedProps) {
          const overCEQ = calculatePropCEQ(prop.overOdds, prop.underOdds);
          const underCEQ = calculatePropCEQ(prop.underOdds, prop.overOdds);

          // Find best odds
          const bestOverOdds = prop.overOdds.length > 0
            ? Math.max(...prop.overOdds.map(o => o.odds))
            : 0;
          const bestUnderOdds = prop.underOdds.length > 0
            ? Math.max(...prop.underOdds.map(o => o.odds))
            : 0;
          const bestOverBook = prop.overOdds.find(o => o.odds === bestOverOdds)?.book || '';
          const bestUnderBook = prop.underOdds.find(o => o.odds === bestUnderOdds)?.book || '';

          parsedProps.push({
            player: prop.player,
            propType: prop.propType,
            propTypeLabel: PROP_TYPE_LABELS[prop.propType] || prop.propType.replace('player_', '').replace(/_/g, ' '),
            line: prop.line,
            overOdds: prop.overOdds,
            underOdds: prop.underOdds,
            overCEQ,
            underCEQ,
            bestOverBook,
            bestUnderBook,
            bestOverOdds,
            bestUnderOdds,
          });
        }

        // Sort props by highest CEQ
        parsedProps.sort((a, b) => Math.max(b.overCEQ, b.underCEQ) - Math.max(a.overCEQ, a.underCEQ));

        gamesData.push({
          gameId: game.id,
          homeTeam: game.home_team,
          awayTeam: game.away_team,
          sport: game.sport_key,
          commenceTime: game.commence_time,
          props: parsedProps,
        });
      }

      // Sort games by number of high-CEQ props
      gamesData.sort((a, b) => {
        const aHighCEQ = a.props.filter(p => p.overCEQ >= 56 || p.underCEQ >= 56).length;
        const bHighCEQ = b.props.filter(p => p.overCEQ >= 56 || p.underCEQ >= 56).length;
        return bHighCEQ - aHighCEQ;
      });

      setGamesWithProps(gamesData);
      setLastUpdated(new Date());
      setError(null);

      // Auto-expand games with edges
      const gamesWithEdges = new Set(
        gamesData
          .filter(g => g.props.some(p => p.overCEQ >= minCEQ || p.underCEQ >= minCEQ))
          .slice(0, 3)
          .map(g => g.gameId)
      );
      setExpandedGames(gamesWithEdges);

    } catch (e: any) {
      setError(e?.message || 'Failed to load player props');
    } finally {
      setLoading(false);
    }
  }, [selectedSport, minCEQ]);

  useEffect(() => {
    fetchPropsFromCachedOdds();
  }, [fetchPropsFromCachedOdds]);

  // Format time
  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    if (date < now) {
      return 'LIVE';
    }
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  // Format odds display
  const formatOdds = (odds: number): string => {
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  // Get sport emoji
  const getSportEmoji = (sport: string): string => {
    return SPORTS.find((s) => s.key === sport)?.emoji || '\u{1F3C6}';
  };

  // Toggle game expansion
  const toggleGame = (gameId: string) => {
    const newExpanded = new Set(expandedGames);
    if (newExpanded.has(gameId)) {
      newExpanded.delete(gameId);
    } else {
      newExpanded.add(gameId);
    }
    setExpandedGames(newExpanded);
  };

  // Toggle player expansion
  const togglePlayer = (playerId: string) => {
    const newExpanded = new Set(expandedPlayers);
    if (newExpanded.has(playerId)) {
      newExpanded.delete(playerId);
    } else {
      newExpanded.add(playerId);
    }
    setExpandedPlayers(newExpanded);
  };

  // Get CEQ color class
  const getCEQColor = (ceq: number): string => {
    if (ceq >= 70) return 'text-emerald-400';
    if (ceq >= 60) return 'text-blue-400';
    if (ceq >= 56) return 'text-amber-400';
    return 'text-zinc-500';
  };

  // Get CEQ badge color class
  const getCEQBadgeColor = (ceq: number): string => {
    if (ceq >= 70) return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    if (ceq >= 60) return 'bg-blue-500/15 text-blue-400 border-blue-500/30';
    if (ceq >= 56) return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    return 'bg-zinc-800/50 text-zinc-500 border-zinc-700';
  };

  // Count props with edges
  const totalPropsWithEdges = gamesWithProps.reduce(
    (acc, game) => acc + game.props.filter(p => p.overCEQ >= minCEQ || p.underCEQ >= minCEQ).length,
    0
  );

  const totalPlayers = new Set(
    gamesWithProps.flatMap(g => g.props.filter(p => p.overCEQ >= minCEQ || p.underCEQ >= minCEQ).map(p => p.player))
  ).size;

  const gamesWithEdges = gamesWithProps.filter(
    g => g.props.some(p => p.overCEQ >= minCEQ || p.underCEQ >= minCEQ)
  ).length;

  return (
    <div className="py-4 px-4 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 flex items-center gap-2">
            <User className="w-6 h-6 text-purple-400" />
            Player Props
          </h1>
          <p className="text-sm text-zinc-500 mt-1">
            Find edges on player prop markets across all games
          </p>
        </div>

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span className="text-xs text-zinc-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchPropsFromCachedOdds}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Filters Row */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        {/* Sport Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-zinc-500" />
          <div className="flex gap-1">
            {SPORTS.map((sport) => (
              <button
                key={sport.key}
                onClick={() => setSelectedSport(sport.key)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                  selectedSport === sport.key
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                    : 'bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-transparent'
                }`}
              >
                {sport.emoji} {sport.label}
              </button>
            ))}
          </div>
        </div>

        {/* Min CEQ Filter */}
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-zinc-500">Min CEQ:</span>
          <div className="flex gap-1">
            {[50, 56, 60, 65].map((val) => (
              <button
                key={val}
                onClick={() => setMinCEQ(val)}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  minCEQ === val
                    ? 'bg-zinc-700 text-zinc-200'
                    : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-400'
                }`}
              >
                {val}%
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-zinc-100">{totalPropsWithEdges}</div>
          <div className="text-xs text-zinc-500">Props with Edges</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-400">{totalPlayers}</div>
          <div className="text-xs text-zinc-500">Players</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-emerald-400">{gamesWithEdges}</div>
          <div className="text-xs text-zinc-500">Games with Edges</div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && gamesWithProps.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-6 h-6 text-zinc-500 animate-spin" />
        </div>
      )}

      {/* Empty State */}
      {!loading && totalPropsWithEdges === 0 && !error && (
        <div className="text-center py-12">
          <TrendingUp className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-zinc-400 mb-2">No Player Props Edges</h3>
          <p className="text-sm text-zinc-600">
            No player prop edges detected above {minCEQ}% CEQ. Try lowering the threshold or check back later.
          </p>
        </div>
      )}

      {/* Games List */}
      {!loading && gamesWithProps.length > 0 && (
        <div className="space-y-4">
          {gamesWithProps
            .filter(game => game.props.some(p => p.overCEQ >= minCEQ || p.underCEQ >= minCEQ))
            .map((game) => {
              const propsWithEdges = game.props.filter(p => p.overCEQ >= minCEQ || p.underCEQ >= minCEQ);
              const isExpanded = expandedGames.has(game.gameId);
              const bestCEQ = Math.max(...propsWithEdges.map(p => Math.max(p.overCEQ, p.underCEQ)));

              return (
                <div
                  key={game.gameId}
                  className="bg-zinc-900/50 border border-zinc-800 rounded-lg overflow-hidden"
                >
                  {/* Game Header */}
                  <button
                    onClick={() => toggleGame(game.gameId)}
                    className="w-full px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 hover:bg-zinc-800/70 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4 text-zinc-500" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-zinc-500" />
                        )}
                        <span className="text-lg">{getSportEmoji(game.sport)}</span>
                        <span className="font-semibold text-zinc-100">
                          {game.awayTeam} @ {game.homeTeam}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded border ${getCEQBadgeColor(bestCEQ)}`}>
                          {propsWithEdges.length} edges
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`text-xs font-medium ${formatTime(game.commenceTime) === 'LIVE' ? 'text-red-400' : 'text-zinc-500'}`}>
                          {formatTime(game.commenceTime)}
                        </span>
                        <Link
                          href={`/edge/portal/sports/game/${game.gameId}?sport=${game.sport}`}
                          onClick={(e) => e.stopPropagation()}
                          className="text-zinc-500 hover:text-emerald-400 transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  </button>

                  {/* Props Table */}
                  {isExpanded && (
                    <div className="p-3">
                      {/* Table Header */}
                      <div className="grid grid-cols-12 gap-2 px-3 py-2 text-xs text-zinc-500 font-medium border-b border-zinc-800 mb-2">
                        <div className="col-span-3">Player</div>
                        <div className="col-span-2">Prop Type</div>
                        <div className="col-span-1 text-center">Line</div>
                        <div className="col-span-3 text-center">Over</div>
                        <div className="col-span-3 text-center">Under</div>
                      </div>

                      {/* Props Rows */}
                      <div className="space-y-1">
                        {propsWithEdges.map((prop, idx) => {
                          const showOver = prop.overCEQ >= minCEQ;
                          const showUnder = prop.underCEQ >= minCEQ;

                          return (
                            <div
                              key={`${prop.player}-${prop.propType}-${prop.line}-${idx}`}
                              className="grid grid-cols-12 gap-2 px-3 py-2 bg-zinc-800/30 rounded-lg hover:bg-zinc-800/50 transition-colors items-center"
                            >
                              {/* Player */}
                              <div className="col-span-3 flex items-center gap-2">
                                <User className="w-3 h-3 text-purple-400 flex-shrink-0" />
                                <span className="text-sm font-medium text-zinc-100 truncate">
                                  {prop.player}
                                </span>
                              </div>

                              {/* Prop Type */}
                              <div className="col-span-2">
                                <span className="text-xs text-zinc-400">{prop.propTypeLabel}</span>
                              </div>

                              {/* Line */}
                              <div className="col-span-1 text-center">
                                <span className="text-sm font-mono text-zinc-200">{prop.line}</span>
                              </div>

                              {/* Over */}
                              <div className="col-span-3">
                                {prop.overOdds.length > 0 ? (
                                  <div className={`flex items-center justify-center gap-2 ${showOver ? '' : 'opacity-40'}`}>
                                    <span className="text-xs text-emerald-400">O</span>
                                    <span className="text-sm font-mono text-zinc-200">
                                      {formatOdds(prop.bestOverOdds)}
                                    </span>
                                    <span className="text-[10px] text-zinc-500 capitalize">
                                      @{prop.bestOverBook.slice(0, 3)}
                                    </span>
                                    <span className={`text-xs font-bold ${getCEQColor(prop.overCEQ)}`}>
                                      {prop.overCEQ}%
                                    </span>
                                  </div>
                                ) : (
                                  <span className="text-xs text-zinc-600 text-center block">-</span>
                                )}
                              </div>

                              {/* Under */}
                              <div className="col-span-3">
                                {prop.underOdds.length > 0 ? (
                                  <div className={`flex items-center justify-center gap-2 ${showUnder ? '' : 'opacity-40'}`}>
                                    <span className="text-xs text-red-400">U</span>
                                    <span className="text-sm font-mono text-zinc-200">
                                      {formatOdds(prop.bestUnderOdds)}
                                    </span>
                                    <span className="text-[10px] text-zinc-500 capitalize">
                                      @{prop.bestUnderBook.slice(0, 3)}
                                    </span>
                                    <span className={`text-xs font-bold ${getCEQColor(prop.underCEQ)}`}>
                                      {prop.underCEQ}%
                                    </span>
                                  </div>
                                ) : (
                                  <span className="text-xs text-zinc-600 text-center block">-</span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      )}
    </div>
  );
}
