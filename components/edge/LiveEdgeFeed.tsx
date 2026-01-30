'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { createClient } from '@supabase/supabase-js';
import { LiveEdge, EDGE_TYPE_CONFIG, formatEdgeDescription } from '@/lib/edge/types/edge';
import { LiveEdgeCard } from './LiveEdgeCard';
import { Activity, RefreshCw, Volume2, VolumeX, ChevronDown, Clock } from 'lucide-react';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Session history with timestamps for tracking when edges were seen
interface EdgeHistoryItem {
  edge: LiveEdge;
  seenAt: Date;
  isNew: boolean;
}

interface LiveEdgeFeedProps {
  sport?: string;
  maxEdges?: number;
  maxHistory?: number; // Max edges to keep in history
  showFilters?: boolean;
  autoRefresh?: boolean;
  onEdgeCount?: (count: number) => void;
}

export function LiveEdgeFeed({
  sport,
  maxEdges = 20,
  maxHistory = 75, // Keep last 75 edges in history
  showFilters = true,
  autoRefresh = true,
  onEdgeCount,
}: LiveEdgeFeedProps) {
  // Session history - accumulates all edges seen this session
  const [edgeHistory, setEdgeHistory] = useState<EdgeHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'fading'>('active');
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [expandedEdgeId, setExpandedEdgeId] = useState<string | null>(null);
  const [showScrollHint, setShowScrollHint] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const seenEdgeIds = useRef<Set<string>>(new Set());

  // Add edge to history (accumulating, not replacing)
  const addEdgeToHistory = useCallback((edge: LiveEdge, isNew: boolean = false) => {
    if (seenEdgeIds.current.has(edge.id)) {
      // Update existing edge in history
      setEdgeHistory(prev =>
        prev.map(item =>
          item.edge.id === edge.id
            ? { ...item, edge, isNew: false }
            : item
        )
      );
      return;
    }

    seenEdgeIds.current.add(edge.id);

    setEdgeHistory(prev => {
      const newItem: EdgeHistoryItem = {
        edge,
        seenAt: new Date(),
        isNew,
      };
      // Prepend new edge, keep only maxHistory items
      const updated = [newItem, ...prev].slice(0, maxHistory);
      return updated;
    });

    // Clear "new" flag after animation
    if (isNew) {
      setTimeout(() => {
        setEdgeHistory(prev =>
          prev.map(item =>
            item.edge.id === edge.id ? { ...item, isNew: false } : item
          )
        );
      }, 3000);
    }
  }, [maxHistory]);

  // Fetch edges from API - merges with history instead of replacing
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
      const fetchedEdges: LiveEdge[] = data.edges || [];

      // Add fetched edges to history (without "new" animation on initial load)
      fetchedEdges.forEach(edge => addEdgeToHistory(edge, false));

      onEdgeCount?.(fetchedEdges.length);
      setError(null);
    } catch (e: any) {
      console.error('[LiveEdgeFeed] Error:', e);
      setError(e?.message || 'Failed to load edges');
    } finally {
      setLoading(false);
    }
  }, [sport, maxEdges, filterType, filterStatus, onEdgeCount, addEdgeToHistory]);

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

            // Add to history with "new" animation
            addEdgeToHistory(newEdge, true);

            // Show scroll hint if user has scrolled down
            if (listRef.current && listRef.current.scrollTop > 50) {
              setShowScrollHint(true);
              setTimeout(() => setShowScrollHint(false), 3000);
            }

            // Play sound if enabled
            if (soundEnabled) {
              playNotificationSound();
            }
          } else if (payload.eventType === 'UPDATE') {
            const updatedEdge = payload.new as LiveEdge;
            // Update in history
            setEdgeHistory(prev =>
              prev.map(item =>
                item.edge.id === updatedEdge.id
                  ? { ...item, edge: updatedEdge }
                  : item
              )
            );
          } else if (payload.eventType === 'DELETE') {
            // Mark as expired but keep in history
            const deletedId = payload.old.id;
            setEdgeHistory(prev =>
              prev.map(item =>
                item.edge.id === deletedId
                  ? { ...item, edge: { ...item.edge, status: 'expired' as const } }
                  : item
              )
            );
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [autoRefresh, sport, soundEnabled, addEdgeToHistory]);

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

  // Filter history based on current filters
  const filteredHistory = edgeHistory.filter(item => {
    const edge = item.edge;
    if (filterStatus !== 'all' && edge.status !== filterStatus) return false;
    if (filterType && edge.edge_type !== filterType) return false;
    if (sport && edge.sport !== sport) return false;
    return true;
  });

  // Group filtered edges by sport
  const groupedBySport = filteredHistory.reduce((acc, item) => {
    const sportKey = item.edge.sport;
    if (!acc[sportKey]) acc[sportKey] = [];
    acc[sportKey].push(item);
    return acc;
  }, {} as Record<string, EdgeHistoryItem[]>);

  // Counts from full history (not just filtered)
  const activeCount = edgeHistory.filter((item) => item.edge.status === 'active').length;
  const fadingCount = edgeHistory.filter((item) => item.edge.status === 'fading').length;
  const totalHistory = edgeHistory.length;

  // Scroll to top helper
  const scrollToTop = () => {
    listRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    setShowScrollHint(false);
  };

  // Format relative time for history
  const formatSeenAgo = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);

    if (diffSecs < 5) return 'just now';
    if (diffSecs < 60) return `${diffSecs}s ago`;

    const diffMins = Math.floor(diffSecs / 60);
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours}h ago`;
  };

  // Update relative times every 10 seconds
  const [, setTick] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-100">Live Edges</h3>
          {activeCount > 0 && (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
              </span>
              {activeCount}
            </span>
          )}
          {totalHistory > 0 && (
            <span className="text-[10px] text-zinc-500">
              ({totalHistory} in history)
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
      <div className="flex-1 overflow-y-auto relative" ref={listRef}>
        {/* New edge scroll hint */}
        {showScrollHint && (
          <button
            onClick={scrollToTop}
            className="absolute top-2 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500 text-white text-xs font-medium shadow-lg animate-bounce"
          >
            <ChevronDown className="w-3 h-3 rotate-180" />
            New edge detected
          </button>
        )}

        {loading && edgeHistory.length === 0 ? (
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
        ) : filteredHistory.length === 0 ? (
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
            {filteredHistory.map((item) => (
              <EdgeHistoryCard
                key={item.edge.id}
                item={item}
                isExpanded={expandedEdgeId === item.edge.id}
                onToggleExpand={() =>
                  setExpandedEdgeId(expandedEdgeId === item.edge.id ? null : item.edge.id)
                }
                formatSeenAgo={formatSeenAgo}
              />
            ))}
          </div>
        ) : (
          // Multi-sport view - grouped
          <div className="p-3 space-y-4">
            {Object.entries(groupedBySport).map(([sportKey, sportItems]) => (
              <div key={sportKey}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                    {sportKey.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] text-zinc-600">
                    ({sportItems.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {sportItems.map((item) => (
                    <EdgeHistoryCard
                      key={item.edge.id}
                      item={item}
                      isExpanded={expandedEdgeId === item.edge.id}
                      onToggleExpand={() =>
                        setExpandedEdgeId(expandedEdgeId === item.edge.id ? null : item.edge.id)
                      }
                      formatSeenAgo={formatSeenAgo}
                    />
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

// Individual edge card with expand/collapse and history info
interface EdgeHistoryCardProps {
  item: EdgeHistoryItem;
  isExpanded: boolean;
  onToggleExpand: () => void;
  formatSeenAgo: (date: Date) => string;
}

function EdgeHistoryCard({ item, isExpanded, onToggleExpand, formatSeenAgo }: EdgeHistoryCardProps) {
  const { edge, seenAt, isNew } = item;

  return (
    <div
      className={`transition-all duration-500 ${
        isNew
          ? 'ring-2 ring-emerald-500 ring-offset-2 ring-offset-zinc-900 animate-pulse'
          : ''
      }`}
    >
      <div
        onClick={onToggleExpand}
        className={`cursor-pointer transition-all duration-200 ${
          isExpanded ? 'scale-[1.01]' : ''
        }`}
      >
        <LiveEdgeCard edge={edge} compact={!isExpanded} showGameLink={false} />
      </div>

      {/* Expanded details panel */}
      {isExpanded && (
        <div className="mt-1 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50 space-y-2 animate-in slide-in-from-top-2 duration-200">
          {/* Full description */}
          <p className="text-xs text-zinc-300 leading-relaxed">
            {formatEdgeDescription(edge)}
          </p>

          {/* Metadata grid */}
          <div className="grid grid-cols-2 gap-2 text-[10px]">
            <div>
              <span className="text-zinc-500">Market:</span>{' '}
              <span className="text-zinc-300">{edge.market_type || 'N/A'}</span>
            </div>
            <div>
              <span className="text-zinc-500">Outcome:</span>{' '}
              <span className="text-zinc-300">{edge.outcome_key || 'N/A'}</span>
            </div>
            <div>
              <span className="text-zinc-500">Confidence:</span>{' '}
              <span className="text-zinc-300">{edge.confidence?.toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-zinc-500">Books:</span>{' '}
              <span className="text-zinc-300 capitalize">
                {edge.triggering_book} → {edge.best_current_book}
              </span>
            </div>
          </div>

          {/* Timestamps */}
          <div className="flex items-center justify-between pt-2 border-t border-zinc-700/50">
            <div className="flex items-center gap-1 text-[10px] text-zinc-500">
              <Clock className="w-3 h-3" />
              <span>Seen {formatSeenAgo(seenAt)}</span>
            </div>
            {edge.game_id && (
              <a
                href={`/edge/portal/sports/game/${edge.game_id}?sport=${edge.sport}`}
                className="text-[10px] text-emerald-400 hover:text-emerald-300 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                View Game →
              </a>
            )}
          </div>
        </div>
      )}

      {/* Seen timestamp (when collapsed) */}
      {!isExpanded && (
        <div className="flex items-center justify-between px-2 py-1">
          <span className="text-[9px] text-zinc-600">
            Seen {formatSeenAgo(seenAt)}
          </span>
          <span className="text-[9px] text-zinc-600">
            Click to expand
          </span>
        </div>
      )}
    </div>
  );
}

export default LiveEdgeFeed;
