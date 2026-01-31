'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import { LiveEdge, EDGE_TYPE_CONFIG } from '@/lib/edge/types/edge';
import { RefreshCw, User, TrendingUp, Filter, ExternalLink, Clock } from 'lucide-react';
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
  points: 'Points',
  assists: 'Assists',
  rebounds: 'Rebounds',
  steals: 'Steals',
  blocks: 'Blocks',
  threes: '3-Pointers',
  three_pointers: '3-Pointers',
  pts_rebs_asts: 'Pts+Rebs+Asts',
  double_double: 'Double-Double',
  triple_double: 'Triple-Double',
  passing_yards: 'Pass Yards',
  rushing_yards: 'Rush Yards',
  receiving_yards: 'Rec Yards',
  touchdowns: 'Touchdowns',
  receptions: 'Receptions',
  goals: 'Goals',
  shots: 'Shots',
  saves: 'Saves',
  strikeouts: 'Strikeouts',
  hits: 'Hits',
  home_runs: 'Home Runs',
};

// Game data type
interface GameInfo {
  gameId: string;
  homeTeam: string;
  awayTeam: string;
  sport: string;
  commenceTime: string;
}

export default function PlayerPropsPage() {
  const [edges, setEdges] = useState<LiveEdge[]>([]);
  const [games, setGames] = useState<Map<string, GameInfo>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSport, setSelectedSport] = useState('all');
  const [groupBy, setGroupBy] = useState<'game' | 'player' | 'prop'>('game');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Fetch game info for context
  const fetchGameInfo = useCallback(async (gameIds: string[]) => {
    if (gameIds.length === 0) return;

    const { data, error } = await supabase
      .from('cached_odds')
      .select('game_data')
      .in('game_data->>id', gameIds);

    if (!error && data) {
      const gameMap = new Map<string, GameInfo>();
      for (const row of data) {
        const game = row.game_data;
        if (game?.id) {
          gameMap.set(game.id, {
            gameId: game.id,
            homeTeam: game.home_team,
            awayTeam: game.away_team,
            sport: game.sport_key,
            commenceTime: game.commence_time,
          });
        }
      }
      setGames(gameMap);
    }
  }, []);

  // Fetch player prop edges
  const fetchPlayerPropEdges = useCallback(async () => {
    setLoading(true);
    try {
      let query = supabase
        .from('live_edges')
        .select('*')
        .eq('market_type', 'player_props')
        .in('status', ['active', 'fading'])
        .order('confidence', { ascending: false })
        .limit(100);

      if (selectedSport !== 'all') {
        query = query.eq('sport', selectedSport);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;

      const edgesData = data || [];
      setEdges(edgesData);
      setLastUpdated(new Date());
      setError(null);

      // Fetch game info for all edges
      const gameIds = [...new Set(edgesData.map((e) => e.game_id).filter(Boolean))];
      await fetchGameInfo(gameIds);
    } catch (e: any) {
      setError(e?.message || 'Failed to load player props');
    } finally {
      setLoading(false);
    }
  }, [selectedSport, fetchGameInfo]);

  useEffect(() => {
    fetchPlayerPropEdges();
  }, [fetchPlayerPropEdges]);

  // Parse player name and side from outcome_key
  const parseOutcomeKey = (outcomeKey: string): { player: string; side: string; propType: string } => {
    // Format: "PLAYER_NAME|OVER" or "player_points|LEBRON_JAMES|OVER"
    const parts = outcomeKey.split('|');

    if (parts.length >= 2) {
      const playerPart = parts[0].replace(/_/g, ' ');
      const side = parts[parts.length - 1];

      // Extract prop type if present
      let propType = '';
      if (parts.length >= 3) {
        propType = parts[1];
      }

      const player = playerPart
        .split(' ')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
        .join(' ');

      return {
        player,
        side: side.charAt(0).toUpperCase() + side.slice(1).toLowerCase(),
        propType: PROP_TYPE_LABELS[propType.toLowerCase()] || propType || 'Unknown',
      };
    }

    return { player: outcomeKey, side: '', propType: '' };
  };

  // Get prop type from market_type
  const getPropType = (edge: LiveEdge): string => {
    const market = edge.market_type || '';
    // player_points, player_assists, etc.
    const parts = market.split('_');
    if (parts.length >= 2) {
      const propKey = parts.slice(1).join('_');
      return PROP_TYPE_LABELS[propKey] || propKey;
    }
    return market;
  };

  // Format time
  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZoneName: 'short',
    });
  };

  // Get sport emoji
  const getSportEmoji = (sport: string): string => {
    return SPORTS.find((s) => s.key === sport)?.emoji || '\u{1F3C6}';
  };

  // Group edges by game
  const groupByGame = () => {
    const grouped: Record<string, { game: GameInfo | null; edges: LiveEdge[] }> = {};

    for (const edge of edges) {
      const gameId = edge.game_id || 'unknown';
      if (!grouped[gameId]) {
        grouped[gameId] = {
          game: games.get(gameId) || null,
          edges: [],
        };
      }
      grouped[gameId].edges.push(edge);
    }

    return Object.entries(grouped);
  };

  // Group edges by player
  const groupByPlayer = () => {
    const grouped: Record<string, LiveEdge[]> = {};

    for (const edge of edges) {
      const { player } = parseOutcomeKey(edge.outcome_key || '');
      if (!grouped[player]) {
        grouped[player] = [];
      }
      grouped[player].push(edge);
    }

    return Object.entries(grouped).sort((a, b) => b[1].length - a[1].length);
  };

  // Group edges by prop type
  const groupByProp = () => {
    const grouped: Record<string, LiveEdge[]> = {};

    for (const edge of edges) {
      const propType = getPropType(edge);
      if (!grouped[propType]) {
        grouped[propType] = [];
      }
      grouped[propType].push(edge);
    }

    return Object.entries(grouped).sort((a, b) => b[1].length - a[1].length);
  };

  // Render edge row
  const renderEdgeRow = (edge: LiveEdge, showPlayer = true, showProp = true) => {
    const { player, side } = parseOutcomeKey(edge.outcome_key || '');
    const propType = getPropType(edge);
    const game = games.get(edge.game_id || '');
    const typeConfig = EDGE_TYPE_CONFIG[edge.edge_type as keyof typeof EDGE_TYPE_CONFIG];

    // Confidence color
    const confColor =
      edge.confidence && edge.confidence >= 60
        ? 'text-emerald-400'
        : edge.confidence && edge.confidence >= 40
        ? 'text-blue-400'
        : 'text-amber-400';

    return (
      <div
        key={edge.id}
        className="flex items-center justify-between py-2 px-3 bg-zinc-800/30 rounded-lg hover:bg-zinc-800/50 transition-colors"
      >
        <div className="flex-1 min-w-0">
          {showPlayer && (
            <div className="flex items-center gap-2 mb-1">
              <User className="w-3 h-3 text-purple-400" />
              <span className="text-sm font-medium text-zinc-100 truncate">{player}</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-xs">
            {showProp && (
              <span className="text-zinc-400">{propType}:</span>
            )}
            <span className="text-emerald-400 font-medium">
              {side} {edge.initial_value || edge.current_value}
            </span>
            <span className="text-zinc-600">@</span>
            <span className="text-zinc-300 capitalize">{edge.best_current_book}</span>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          {/* Edge type badge */}
          <span
            className={`text-[10px] px-1.5 py-0.5 rounded ${
              typeConfig?.color === 'blue'
                ? 'bg-blue-500/15 text-blue-400'
                : typeConfig?.color === 'green'
                ? 'bg-emerald-500/15 text-emerald-400'
                : typeConfig?.color === 'purple'
                ? 'bg-purple-500/15 text-purple-400'
                : 'bg-orange-500/15 text-orange-400'
            }`}
          >
            {typeConfig?.label || edge.edge_type}
          </span>

          {/* Confidence */}
          <span className={`text-xs font-mono font-bold ${confColor}`}>
            {edge.confidence?.toFixed(0)}%
          </span>

          {/* Game link */}
          {edge.game_id && (
            <Link
              href={`/edge/portal/sports/game/${edge.game_id}?sport=${edge.sport}`}
              className="text-zinc-500 hover:text-emerald-400 transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>
      </div>
    );
  };

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
            Live edges on player prop markets across all games
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
            onClick={fetchPlayerPropEdges}
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

        {/* Group By */}
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-zinc-500">Group by:</span>
          <div className="flex gap-1">
            {[
              { key: 'game', label: 'Game' },
              { key: 'player', label: 'Player' },
              { key: 'prop', label: 'Prop Type' },
            ].map((opt) => (
              <button
                key={opt.key}
                onClick={() => setGroupBy(opt.key as any)}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  groupBy === opt.key
                    ? 'bg-zinc-700 text-zinc-200'
                    : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-400'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-zinc-100">{edges.length}</div>
          <div className="text-xs text-zinc-500">Active Edges</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-400">
            {new Set(edges.map((e) => parseOutcomeKey(e.outcome_key || '').player)).size}
          </div>
          <div className="text-xs text-zinc-500">Players</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-emerald-400">
            {new Set(edges.map((e) => e.game_id)).size}
          </div>
          <div className="text-xs text-zinc-500">Games</div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && edges.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-6 h-6 text-zinc-500 animate-spin" />
        </div>
      )}

      {/* Empty State */}
      {!loading && edges.length === 0 && !error && (
        <div className="text-center py-12">
          <TrendingUp className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-zinc-400 mb-2">No Player Props Edges</h3>
          <p className="text-sm text-zinc-600">
            No active player prop edges detected. Check back when more games are available.
          </p>
        </div>
      )}

      {/* Content */}
      {!loading && edges.length > 0 && (
        <div className="space-y-6">
          {/* Group by Game */}
          {groupBy === 'game' &&
            groupByGame().map(([gameId, { game, edges: gameEdges }]) => (
              <div
                key={gameId}
                className="bg-zinc-900/50 border border-zinc-800 rounded-lg overflow-hidden"
              >
                {/* Game Header */}
                <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getSportEmoji(game?.sport || '')}</span>
                      <span className="font-semibold text-zinc-100">
                        {game ? `${game.awayTeam} @ ${game.homeTeam}` : 'Unknown Game'}
                      </span>
                    </div>
                    {game?.commenceTime && (
                      <span className="text-xs text-zinc-500">
                        {formatTime(game.commenceTime)}
                      </span>
                    )}
                  </div>
                </div>

                {/* Edges */}
                <div className="p-3 space-y-2">
                  {gameEdges.map((edge) => renderEdgeRow(edge, true, true))}
                </div>
              </div>
            ))}

          {/* Group by Player */}
          {groupBy === 'player' &&
            groupByPlayer().map(([player, playerEdges]) => (
              <div
                key={player}
                className="bg-zinc-900/50 border border-zinc-800 rounded-lg overflow-hidden"
              >
                <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 flex items-center gap-2">
                  <User className="w-4 h-4 text-purple-400" />
                  <span className="font-semibold text-zinc-100">{player}</span>
                  <span className="text-xs text-zinc-500">
                    ({playerEdges.length} edge{playerEdges.length !== 1 ? 's' : ''})
                  </span>
                </div>
                <div className="p-3 space-y-2">
                  {playerEdges.map((edge) => renderEdgeRow(edge, false, true))}
                </div>
              </div>
            ))}

          {/* Group by Prop Type */}
          {groupBy === 'prop' &&
            groupByProp().map(([propType, propEdges]) => (
              <div
                key={propType}
                className="bg-zinc-900/50 border border-zinc-800 rounded-lg overflow-hidden"
              >
                <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <span className="font-semibold text-zinc-100">{propType}</span>
                  <span className="text-xs text-zinc-500">
                    ({propEdges.length} edge{propEdges.length !== 1 ? 's' : ''})
                  </span>
                </div>
                <div className="p-3 space-y-2">
                  {propEdges.map((edge) => renderEdgeRow(edge, true, false))}
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
