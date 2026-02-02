'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import { RefreshCw, User, TrendingUp, Filter, ExternalLink, Clock, ChevronDown, ChevronRight, Info } from 'lucide-react';
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

// Prop type labels and display order
const PROP_TYPE_ORDER = [
  'player_points',
  'player_rebounds',
  'player_assists',
  'player_threes',
  'player_steals',
  'player_blocks',
  'player_points_rebounds_assists',
  'player_points_rebounds',
  'player_points_assists',
  'player_rebounds_assists',
  'player_double_double',
  'player_triple_double',
  'player_pass_yds',
  'player_pass_tds',
  'player_rush_yds',
  'player_reception_yds',
  'player_receptions',
  'player_anytime_td',
  'player_goals',
  'player_shots_on_goal',
];

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

// Sharp book for benchmark (used internally, NOT displayed)
const SHARP_BOOK = 'pinnacle';

// Retail books to display and compare
const RETAIL_BOOKS = ['fanduel', 'draftkings'];

// Edge signal types
type EdgeSignal = 'sharp_div' | 'juice_edge';

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
  // Sharp benchmark (Pinnacle) - used for calculation only
  pinnacleOverOdds: number | null;
  pinnacleUnderOdds: number | null;
  // Retail odds (FanDuel, DraftKings) - displayed
  retailOverOdds: { book: string; odds: number }[];
  retailUnderOdds: { book: string; odds: number }[];
  // CEQ for each side
  overCEQ: number;
  underCEQ: number;
  // The edge side (only one can have edge)
  edgeSide: 'Over' | 'Under' | null;
  edgeCEQ: number;
  edgeOdds: number;
  edgeBook: string;
  // Edge signal info
  edgeSignal: EdgeSignal;
  edgeSignalDetail: string;
}

interface GameWithProps {
  gameId: string;
  homeTeam: string;
  awayTeam: string;
  sport: string;
  commenceTime: string;
  propsByType: Map<string, ParsedProp[]>;
}

// Convert American odds to implied probability
function oddsToProb(americanOdds: number): number {
  if (americanOdds > 0) {
    return 100 / (americanOdds + 100);
  } else {
    return Math.abs(americanOdds) / (Math.abs(americanOdds) + 100);
  }
}

// Calculate CEQ comparing retail odds to sharp (Pinnacle) odds
// Returns: { ceq, signal, detail }
function calculateSharpDivCEQ(
  retailOdds: number,
  sharpOdds: number
): { ceq: number; detail: string } {
  const retailProb = oddsToProb(retailOdds);
  const sharpProb = oddsToProb(sharpOdds);

  // Edge = sharp probability - retail probability
  // If retail offers better odds (lower implied prob), we have an edge
  const edge = sharpProb - retailProb;

  // Convert edge to CEQ (50 = neutral, higher = more edge)
  // Scale: 1% edge = ~6 CEQ points
  const ceq = 50 + (edge * 100 * 6);
  const clampedCeq = Math.max(0, Math.min(100, Math.round(ceq)));

  const detail = `Sharp: ${sharpOdds > 0 ? '+' : ''}${sharpOdds}, Retail: ${retailOdds > 0 ? '+' : ''}${retailOdds}`;

  return { ceq: clampedCeq, detail };
}

// Calculate CEQ comparing FanDuel to DraftKings (cross-book)
// When Pinnacle isn't available, we compare retail books
function calculateJuiceEdgeCEQ(
  bestOdds: number,
  worstOdds: number,
  bestBook: string
): { ceq: number; detail: string } {
  const bestProb = oddsToProb(bestOdds);
  const worstProb = oddsToProb(worstOdds);

  // Edge = how much better the best odds are vs worst
  const edge = worstProb - bestProb;

  // Scale: smaller edges for cross-book (less reliable than sharp div)
  // 1% edge = ~4 CEQ points
  const ceq = 50 + (edge * 100 * 4);
  const clampedCeq = Math.max(0, Math.min(100, Math.round(ceq)));

  const otherBook = bestBook.toLowerCase() === 'fanduel' ? 'DK' : 'FD';
  const detail = `${bestBook.toLowerCase() === 'fanduel' ? 'FD' : 'DK'}: ${bestOdds > 0 ? '+' : ''}${bestOdds} vs ${otherBook}: ${worstOdds > 0 ? '+' : ''}${worstOdds}`;

  return { ceq: clampedCeq, detail };
}

export default function PlayerPropsPage() {
  const [gamesWithProps, setGamesWithProps] = useState<GameWithProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSport, setSelectedSport] = useState('all');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [expandedGames, setExpandedGames] = useState<Set<string>>(new Set());
  const [minCEQ, setMinCEQ] = useState(56);

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
          pinnacleOver: number | null;
          pinnacleUnder: number | null;
          retailOver: { book: string; odds: number }[];
          retailUnder: { book: string; odds: number }[];
        }>();

        for (const outcome of propOutcomes) {
          const key = `${outcome.player}|${outcome.propType}|${outcome.line}`;

          if (!groupedProps.has(key)) {
            groupedProps.set(key, {
              player: outcome.player,
              propType: outcome.propType,
              line: outcome.line,
              pinnacleOver: null,
              pinnacleUnder: null,
              retailOver: [],
              retailUnder: [],
            });
          }

          const prop = groupedProps.get(key)!;
          const bookLower = outcome.book.toLowerCase();

          if (bookLower === SHARP_BOOK) {
            // Store Pinnacle odds for benchmark (not displayed)
            if (outcome.side === 'Over') {
              prop.pinnacleOver = outcome.odds;
            } else {
              prop.pinnacleUnder = outcome.odds;
            }
          } else if (RETAIL_BOOKS.includes(bookLower)) {
            // Store retail odds (displayed)
            if (outcome.side === 'Over') {
              prop.retailOver.push({ book: outcome.book, odds: outcome.odds });
            } else {
              prop.retailUnder.push({ book: outcome.book, odds: outcome.odds });
            }
          }
        }

        // Calculate CEQ for each prop and determine edge side
        const propsByType = new Map<string, ParsedProp[]>();

        for (const [, prop] of groupedProps) {
          // Skip if no retail odds
          if (prop.retailOver.length === 0 && prop.retailUnder.length === 0) continue;

          // Find best and worst retail odds for each side
          const bestRetailOver = prop.retailOver.length > 0
            ? prop.retailOver.reduce((best, curr) => curr.odds > best.odds ? curr : best)
            : null;
          const worstRetailOver = prop.retailOver.length > 1
            ? prop.retailOver.reduce((worst, curr) => curr.odds < worst.odds ? curr : worst)
            : null;
          const bestRetailUnder = prop.retailUnder.length > 0
            ? prop.retailUnder.reduce((best, curr) => curr.odds > best.odds ? curr : best)
            : null;
          const worstRetailUnder = prop.retailUnder.length > 1
            ? prop.retailUnder.reduce((worst, curr) => curr.odds < worst.odds ? curr : worst)
            : null;

          // Determine which CEQ method to use
          const hasPinnacle = prop.pinnacleOver !== null || prop.pinnacleUnder !== null;

          let overCEQ = 50;
          let underCEQ = 50;
          let overSignal: EdgeSignal = 'juice_edge';
          let underSignal: EdgeSignal = 'juice_edge';
          let overDetail = '';
          let underDetail = '';

          if (hasPinnacle && prop.pinnacleOver !== null && bestRetailOver) {
            // Sharp divergence method for Over
            const result = calculateSharpDivCEQ(bestRetailOver.odds, prop.pinnacleOver);
            overCEQ = result.ceq;
            overSignal = 'sharp_div';
            overDetail = result.detail;
          } else if (bestRetailOver && worstRetailOver && bestRetailOver.odds !== worstRetailOver.odds) {
            // Cross-book (juice edge) method for Over
            const result = calculateJuiceEdgeCEQ(bestRetailOver.odds, worstRetailOver.odds, bestRetailOver.book);
            overCEQ = result.ceq;
            overSignal = 'juice_edge';
            overDetail = result.detail;
          }

          if (hasPinnacle && prop.pinnacleUnder !== null && bestRetailUnder) {
            // Sharp divergence method for Under
            const result = calculateSharpDivCEQ(bestRetailUnder.odds, prop.pinnacleUnder);
            underCEQ = result.ceq;
            underSignal = 'sharp_div';
            underDetail = result.detail;
          } else if (bestRetailUnder && worstRetailUnder && bestRetailUnder.odds !== worstRetailUnder.odds) {
            // Cross-book (juice edge) method for Under
            const result = calculateJuiceEdgeCEQ(bestRetailUnder.odds, worstRetailUnder.odds, bestRetailUnder.book);
            underCEQ = result.ceq;
            underSignal = 'juice_edge';
            underDetail = result.detail;
          }

          // ONLY ONE SIDE CAN HAVE EDGE - the one with higher CEQ
          let edgeSide: 'Over' | 'Under' | null = null;
          let edgeCEQ = 50;
          let edgeOdds = 0;
          let edgeBook = '';
          let edgeSignal: EdgeSignal = 'juice_edge';
          let edgeSignalDetail = '';

          if (overCEQ > underCEQ && overCEQ >= minCEQ && bestRetailOver) {
            edgeSide = 'Over';
            edgeCEQ = overCEQ;
            edgeOdds = bestRetailOver.odds;
            edgeBook = bestRetailOver.book;
            edgeSignal = overSignal;
            edgeSignalDetail = overDetail;
          } else if (underCEQ > overCEQ && underCEQ >= minCEQ && bestRetailUnder) {
            edgeSide = 'Under';
            edgeCEQ = underCEQ;
            edgeOdds = bestRetailUnder.odds;
            edgeBook = bestRetailUnder.book;
            edgeSignal = underSignal;
            edgeSignalDetail = underDetail;
          }

          // Only include props with an edge
          if (edgeSide === null) continue;

          const parsedProp: ParsedProp = {
            player: prop.player,
            propType: prop.propType,
            propTypeLabel: PROP_TYPE_LABELS[prop.propType] || prop.propType.replace('player_', '').replace(/_/g, ' '),
            line: prop.line,
            pinnacleOverOdds: prop.pinnacleOver,
            pinnacleUnderOdds: prop.pinnacleUnder,
            retailOverOdds: prop.retailOver,
            retailUnderOdds: prop.retailUnder,
            overCEQ,
            underCEQ,
            edgeSide,
            edgeCEQ,
            edgeOdds,
            edgeBook,
            edgeSignal,
            edgeSignalDetail,
          };

          // Group by prop type
          if (!propsByType.has(prop.propType)) {
            propsByType.set(prop.propType, []);
          }
          propsByType.get(prop.propType)!.push(parsedProp);
        }

        // Sort players alphabetically within each prop type
        for (const [, props] of propsByType) {
          props.sort((a, b) => a.player.localeCompare(b.player));
        }

        if (propsByType.size === 0) continue;

        gamesData.push({
          gameId: game.id,
          homeTeam: game.home_team,
          awayTeam: game.away_team,
          sport: game.sport_key,
          commenceTime: game.commence_time,
          propsByType,
        });
      }

      // Sort games by total number of edges
      gamesData.sort((a, b) => {
        const aEdges = Array.from(a.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0);
        const bEdges = Array.from(b.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0);
        return bEdges - aEdges;
      });

      setGamesWithProps(gamesData);
      setLastUpdated(new Date());
      setError(null);

      // Auto-expand first 3 games with edges
      const gamesWithEdges = new Set(gamesData.slice(0, 3).map(g => g.gameId));
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

  const formatOdds = (odds: number): string => {
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  const formatBook = (book: string): string => {
    if (book.toLowerCase() === 'fanduel') return 'FD';
    if (book.toLowerCase() === 'draftkings') return 'DK';
    return book.slice(0, 2).toUpperCase();
  };

  const getSportEmoji = (sport: string): string => {
    return SPORTS.find((s) => s.key === sport)?.emoji || '\u{1F3C6}';
  };

  const toggleGame = (gameId: string) => {
    const newExpanded = new Set(expandedGames);
    if (newExpanded.has(gameId)) {
      newExpanded.delete(gameId);
    } else {
      newExpanded.add(gameId);
    }
    setExpandedGames(newExpanded);
  };

  const getCEQColor = (ceq: number): string => {
    if (ceq >= 70) return 'text-emerald-400';
    if (ceq >= 60) return 'text-blue-400';
    if (ceq >= 56) return 'text-amber-400';
    return 'text-zinc-500';
  };

  const getCEQBadgeColor = (ceq: number): string => {
    if (ceq >= 70) return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    if (ceq >= 60) return 'bg-blue-500/15 text-blue-400 border-blue-500/30';
    if (ceq >= 56) return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    return 'bg-zinc-800/50 text-zinc-500 border-zinc-700';
  };

  const getSignalBadge = (signal: EdgeSignal): { label: string; color: string; icon: string } => {
    if (signal === 'sharp_div') {
      return { label: 'Sharp', color: 'text-purple-400', icon: '📊' };
    }
    return { label: 'Juice', color: 'text-blue-400', icon: '💧' };
  };

  // Get sorted prop types for a game
  const getSortedPropTypes = (propsByType: Map<string, ParsedProp[]>): string[] => {
    const types = Array.from(propsByType.keys());
    return types.sort((a, b) => {
      const aIndex = PROP_TYPE_ORDER.indexOf(a);
      const bIndex = PROP_TYPE_ORDER.indexOf(b);
      if (aIndex === -1 && bIndex === -1) return a.localeCompare(b);
      if (aIndex === -1) return 1;
      if (bIndex === -1) return -1;
      return aIndex - bIndex;
    });
  };

  const totalPropsWithEdges = gamesWithProps.reduce(
    (acc, game) => acc + Array.from(game.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0),
    0
  );

  const totalPlayers = new Set(
    gamesWithProps.flatMap(g =>
      Array.from(g.propsByType.values()).flat().map(p => p.player)
    )
  ).size;

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
            Edges on player prop markets (FanDuel & DraftKings)
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

      {/* Signal Legend */}
      <div className="flex items-center gap-4 mb-4 text-xs text-zinc-500">
        <span className="flex items-center gap-1">
          <span>📊</span>
          <span className="text-purple-400">Sharp</span>
          <span>= vs Pinnacle line</span>
        </span>
        <span className="flex items-center gap-1">
          <span>💧</span>
          <span className="text-blue-400">Juice</span>
          <span>= FD vs DK odds</span>
        </span>
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
          <div className="text-2xl font-bold text-emerald-400">{gamesWithProps.length}</div>
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
          {gamesWithProps.map((game) => {
            const isExpanded = expandedGames.has(game.gameId);
            const totalEdges = Array.from(game.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0);
            const bestCEQ = Math.max(
              ...Array.from(game.propsByType.values()).flat().map(p => p.edgeCEQ)
            );

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
                        {totalEdges} edge{totalEdges !== 1 ? 's' : ''}
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

                {/* Props by Type */}
                {isExpanded && (
                  <div className="p-3 space-y-4">
                    {getSortedPropTypes(game.propsByType).map((propType) => {
                      const props = game.propsByType.get(propType)!;
                      const propLabel = PROP_TYPE_LABELS[propType] || propType;

                      return (
                        <div key={propType}>
                          {/* Prop Type Header */}
                          <div className="flex items-center gap-2 mb-2 px-2">
                            <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
                            <span className="text-sm font-semibold text-zinc-300">{propLabel}</span>
                            <span className="text-xs text-zinc-600">({props.length})</span>
                          </div>

                          {/* Table Header */}
                          <div className="grid grid-cols-12 gap-2 px-3 py-1.5 text-[10px] text-zinc-500 font-medium uppercase tracking-wide">
                            <div className="col-span-4">Player</div>
                            <div className="col-span-2 text-center">Line</div>
                            <div className="col-span-2 text-center">Side</div>
                            <div className="col-span-2 text-center">Odds</div>
                            <div className="col-span-2 text-center">CEQ</div>
                          </div>

                          {/* Props Rows */}
                          <div className="space-y-1">
                            {props.map((prop, idx) => {
                              const signalInfo = getSignalBadge(prop.edgeSignal);

                              return (
                                <div
                                  key={`${prop.player}-${prop.line}-${idx}`}
                                  className="grid grid-cols-12 gap-2 px-3 py-2 bg-zinc-800/30 rounded-lg hover:bg-zinc-800/50 transition-colors items-center group"
                                >
                                  {/* Player */}
                                  <div className="col-span-4 flex items-center gap-2">
                                    <User className="w-3 h-3 text-purple-400 flex-shrink-0" />
                                    <span className="text-sm font-medium text-zinc-100 truncate">
                                      {prop.player}
                                    </span>
                                  </div>

                                  {/* Line */}
                                  <div className="col-span-2 text-center">
                                    <span className="text-sm font-mono text-zinc-200">{prop.line}</span>
                                  </div>

                                  {/* Edge Side */}
                                  <div className="col-span-2 text-center">
                                    <span className={`text-sm font-semibold ${
                                      prop.edgeSide === 'Over' ? 'text-emerald-400' : 'text-red-400'
                                    }`}>
                                      {prop.edgeSide === 'Over' ? 'O' : 'U'}
                                    </span>
                                  </div>

                                  {/* Odds @ Book */}
                                  <div className="col-span-2 text-center">
                                    <span className="text-sm font-mono text-zinc-200">
                                      {formatOdds(prop.edgeOdds)}
                                    </span>
                                    <span className="text-[10px] text-zinc-500 ml-1">
                                      @{formatBook(prop.edgeBook)}
                                    </span>
                                  </div>

                                  {/* CEQ + Signal */}
                                  <div className="col-span-2 text-center relative">
                                    <div className="flex items-center justify-center gap-1">
                                      <span className={`text-sm font-bold ${getCEQColor(prop.edgeCEQ)}`}>
                                        {prop.edgeCEQ}%
                                      </span>
                                      <span className="text-[10px]" title={prop.edgeSignalDetail}>
                                        {signalInfo.icon}
                                      </span>
                                    </div>
                                    {/* Tooltip on hover */}
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-zinc-700 rounded text-[10px] text-zinc-300 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                      {prop.edgeSignalDetail}
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
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
