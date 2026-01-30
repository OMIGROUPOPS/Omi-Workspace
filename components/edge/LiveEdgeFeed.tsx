'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import { LiveEdge, EDGE_TYPE_CONFIG } from '@/lib/edge/types/edge';
import { LiveEdgeCard } from './LiveEdgeCard';
import { Activity, Filter, RefreshCw, Volume2, VolumeX } from 'lucide-react';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface LiveEdgeFeedProps {
  sport?: string;
  maxEdges?: number;
  showFilters?: boolean;
  autoRefresh?: boolean;
  onEdgeCount?: (count: number) => void;
}

export function LiveEdgeFeed({
  sport,
  maxEdges = 20,
  showFilters = true,
  autoRefresh = true,
  onEdgeCount,
}: LiveEdgeFeedProps) {
  const [edges, setEdges] = useState<LiveEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'fading'>('active');
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [newEdgeIds, setNewEdgeIds] = useState<Set<string>>(new Set());

  // Fetch edges from API
  const fetchEdges = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (sport) params.set('sport', sport);
      params.set('status', filterStatus === 'all' ? 'active,fading' : filterStatus);
      params.set('limit', maxEdges.toString());
      if (filterType) params.set('edge_type', filterType);

      const res = await fetch(`/api/edges/live?${params}`);
      if (!res.ok) throw new Error('Failed to fetch edges');

      const data = await res.json();
      setEdges(data.edges || []);
      onEdgeCount?.(data.edges?.length || 0);
      setError(null);
    } catch (e: any) {
      console.error('[LiveEdgeFeed] Error:', e);
      setError(e?.message || 'Failed to load edges');
    } finally {
      setLoading(false);
    }
  }, [sport, maxEdges, filterType, filterStatus, onEdgeCount]);

  // Initial fetch
  useEffect(() => {
    fetchEdges();
  }, [fetchEdges]);

  // Realtime subscription
  useEffect(() => {
    if (!autoRefresh) return;

    const channel = supabase
      .channel('live-edges-feed')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'live_edges',
          filter: sport ? `sport=eq.${sport}` : undefined,
        },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            const newEdge = payload.new as LiveEdge;

            // Check if it passes our filters
            if (filterStatus !== 'all' && newEdge.status !== filterStatus) return;
            if (filterType && newEdge.edge_type !== filterType) return;

            setEdges((prev) => {
              const updated = [newEdge, ...prev].slice(0, maxEdges);
              onEdgeCount?.(updated.length);
              return updated;
            });

            // Mark as new for animation
            setNewEdgeIds((prev) => new Set([...prev, newEdge.id]));
            setTimeout(() => {
              setNewEdgeIds((prev) => {
                const next = new Set(prev);
                next.delete(newEdge.id);
                return next;
              });
            }, 3000);

            // Play sound if enabled
            if (soundEnabled) {
              playNotificationSound();
            }
          } else if (payload.eventType === 'UPDATE') {
            const updatedEdge = payload.new as LiveEdge;
            setEdges((prev) =>
              prev.map((e) => (e.id === updatedEdge.id ? updatedEdge : e))
            );
          } else if (payload.eventType === 'DELETE') {
            const deletedId = payload.old.id;
            setEdges((prev) => {
              const updated = prev.filter((e) => e.id !== deletedId);
              onEdgeCount?.(updated.length);
              return updated;
            });
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [autoRefresh, sport, filterType, filterStatus, maxEdges, soundEnabled, onEdgeCount]);

  // Simple notification sound
  function playNotificationSound() {
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      gainNode.gain.value = 0.1;

      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.15);
    } catch (e) {
      // Audio not supported
    }
  }

  // Group edges by sport
  const groupedBySport = edges.reduce((acc, edge) => {
    const sportKey = edge.sport;
    if (!acc[sportKey]) acc[sportKey] = [];
    acc[sportKey].push(edge);
    return acc;
  }, {} as Record<string, LiveEdge[]>);

  const activeCount = edges.filter((e) => e.status === 'active').length;
  const fadingCount = edges.filter((e) => e.status === 'fading').length;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-100">Live Edges</h3>
          {edges.length > 0 && (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
              </span>
              {activeCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`p-1.5 rounded-md transition-colors ${
              soundEnabled
                ? 'bg-emerald-500/20 text-emerald-400'
                : 'bg-zinc-800 text-zinc-500 hover:text-zinc-400'
            }`}
            title={soundEnabled ? 'Mute notifications' : 'Enable sound notifications'}
          >
            {soundEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={fetchEdges}
            className="p-1.5 rounded-md bg-zinc-800 text-zinc-500 hover:text-zinc-400 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="px-4 py-2 border-b border-zinc-800/50 space-y-2">
          {/* Status Filter */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setFilterStatus('active')}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                filterStatus === 'active'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-zinc-800 text-zinc-500 hover:text-zinc-400'
              }`}
            >
              Active ({activeCount})
            </button>
            <button
              onClick={() => setFilterStatus('fading')}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                filterStatus === 'fading'
                  ? 'bg-yellow-500/20 text-yellow-400'
                  : 'bg-zinc-800 text-zinc-500 hover:text-zinc-400'
              }`}
            >
              Fading ({fadingCount})
            </button>
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                filterStatus === 'all'
                  ? 'bg-zinc-700 text-zinc-300'
                  : 'bg-zinc-800 text-zinc-500 hover:text-zinc-400'
              }`}
            >
              All
            </button>
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-1 flex-wrap">
            <button
              onClick={() => setFilterType(null)}
              className={`px-2 py-0.5 text-[10px] rounded-md transition-colors ${
                !filterType
                  ? 'bg-zinc-700 text-zinc-300'
                  : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-400'
              }`}
            >
              All Types
            </button>
            {Object.entries(EDGE_TYPE_CONFIG).map(([key, config]) => (
              <button
                key={key}
                onClick={() => setFilterType(filterType === key ? null : key)}
                className={`px-2 py-0.5 text-[10px] rounded-md transition-colors ${
                  filterType === key
                    ? `bg-${config.color}-500/20 text-${config.color}-400`
                    : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-400'
                }`}
              >
                {config.shortLabel}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Edge List */}
      <div className="flex-1 overflow-y-auto">
        {loading && edges.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <div className="flex items-center gap-2 text-zinc-500">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span className="text-sm">Loading edges...</span>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-32">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        ) : edges.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-center px-4">
            <Activity className="w-8 h-8 text-zinc-700 mb-2" />
            <p className="text-sm text-zinc-500">No edges detected</p>
            <p className="text-xs text-zinc-600 mt-1">
              Edges will appear here when detected
            </p>
          </div>
        ) : sport ? (
          // Single sport view - flat list
          <div className="p-3 space-y-2">
            {edges.map((edge) => (
              <div
                key={edge.id}
                className={`transition-all duration-300 ${
                  newEdgeIds.has(edge.id)
                    ? 'ring-2 ring-emerald-500/50 ring-offset-1 ring-offset-zinc-900'
                    : ''
                }`}
              >
                <LiveEdgeCard edge={edge} compact />
              </div>
            ))}
          </div>
        ) : (
          // Multi-sport view - grouped
          <div className="p-3 space-y-4">
            {Object.entries(groupedBySport).map(([sportKey, sportEdges]) => (
              <div key={sportKey}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                    {sportKey.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] text-zinc-600">
                    ({sportEdges.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {sportEdges.map((edge) => (
                    <div
                      key={edge.id}
                      className={`transition-all duration-300 ${
                        newEdgeIds.has(edge.id)
                          ? 'ring-2 ring-emerald-500/50 ring-offset-1 ring-offset-zinc-900'
                          : ''
                      }`}
                    >
                      <LiveEdgeCard edge={edge} compact />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default LiveEdgeFeed;
