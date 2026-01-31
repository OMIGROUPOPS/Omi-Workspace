'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import { LiveEdge } from '@/lib/edge/types/edge';
import { LiveEdgeCard } from '@/components/edge/LiveEdgeCard';
import { RefreshCw, User, TrendingUp, Filter } from 'lucide-react';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const SPORTS = [
  { key: 'all', label: 'All Sports' },
  { key: 'basketball_nba', label: 'NBA' },
  { key: 'americanfootball_nfl', label: 'NFL' },
  { key: 'icehockey_nhl', label: 'NHL' },
  { key: 'baseball_mlb', label: 'MLB' },
];

export default function PlayerPropsPage() {
  const [edges, setEdges] = useState<LiveEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSport, setSelectedSport] = useState('all');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchPlayerPropEdges = useCallback(async () => {
    setLoading(true);
    try {
      let query = supabase
        .from('live_edges')
        .select('*')
        .eq('market_type', 'player_props')
        .in('status', ['active', 'fading'])
        .order('confidence', { ascending: false })
        .limit(50);

      if (selectedSport !== 'all') {
        query = query.eq('sport', selectedSport);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;

      setEdges(data || []);
      setLastUpdated(new Date());
      setError(null);
    } catch (e: any) {
      console.error('[PlayerProps] Error:', e);
      setError(e?.message || 'Failed to load player props');
    } finally {
      setLoading(false);
    }
  }, [selectedSport]);

  useEffect(() => {
    fetchPlayerPropEdges();
  }, [fetchPlayerPropEdges]);

  // Realtime subscription
  useEffect(() => {
    const channel = supabase
      .channel('player-props-edges')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'live_edges',
          filter: 'market_type=eq.player_props',
        },
        () => {
          fetchPlayerPropEdges();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [fetchPlayerPropEdges]);

  // Group edges by player
  const edgesByPlayer = edges.reduce((acc, edge) => {
    // Extract player name from outcome_key (e.g., "COOPER_KUPP|OVER")
    const playerKey = edge.outcome_key?.split('|')[0]?.replace(/_/g, ' ') || 'Unknown';
    const playerName = playerKey.split(' ').map(w =>
      w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()
    ).join(' ');

    if (!acc[playerName]) {
      acc[playerName] = [];
    }
    acc[playerName].push(edge);
    return acc;
  }, {} as Record<string, LiveEdge[]>);

  const playerCount = Object.keys(edgesByPlayer).length;

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
            Live edges on player prop markets
          </p>
        </div>

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span className="text-xs text-zinc-500">
              Updated {lastUpdated.toLocaleTimeString()}
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

      {/* Sport Filter */}
      <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
        <Filter className="w-4 h-4 text-zinc-500 flex-shrink-0" />
        {SPORTS.map((sport) => (
          <button
            key={sport.key}
            onClick={() => setSelectedSport(sport.key)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              selectedSport === sport.key
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                : 'bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-transparent'
            }`}
          >
            {sport.label}
          </button>
        ))}
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-zinc-100">{edges.length}</div>
          <div className="text-xs text-zinc-500">Active Edges</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-400">{playerCount}</div>
          <div className="text-xs text-zinc-500">Players</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-emerald-400">
            {edges.filter(e => e.status === 'active').length}
          </div>
          <div className="text-xs text-zinc-500">Active Now</div>
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

      {/* Edges Grid - Grouped by Player */}
      {!loading && edges.length > 0 && (
        <div className="space-y-6">
          {Object.entries(edgesByPlayer)
            .sort((a, b) => {
              // Sort by highest confidence edge for each player
              const aMaxConf = Math.max(...a[1].map(e => e.confidence || 0));
              const bMaxConf = Math.max(...b[1].map(e => e.confidence || 0));
              return bMaxConf - aMaxConf;
            })
            .map(([playerName, playerEdges]) => (
              <div key={playerName} className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3 pb-2 border-b border-zinc-800">
                  <User className="w-4 h-4 text-purple-400" />
                  <span className="font-semibold text-zinc-100">{playerName}</span>
                  <span className="text-xs text-zinc-500">
                    {playerEdges.length} edge{playerEdges.length !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                  {playerEdges
                    .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
                    .map((edge) => (
                      <LiveEdgeCard key={edge.id} edge={edge} showGameLink compact />
                    ))}
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
