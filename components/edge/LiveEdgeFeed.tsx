'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { createClient } from '@supabase/supabase-js';
import { LiveEdge, EDGE_TYPE_CONFIG, formatEdgeDescription } from '@/lib/edge/types/edge';
import { Activity, RefreshCw, ChevronDown, Clock, ExternalLink } from 'lucide-react';
import Link from 'next/link';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// League tabs configuration
const LEAGUE_TABS = [
  { key: 'all', label: 'All', emoji: '' },
  { key: 'basketball_nba', label: 'NBA', emoji: '' },
  { key: 'americanfootball_nfl', label: 'NFL', emoji: '' },
  { key: 'icehockey_nhl', label: 'NHL', emoji: '' },
  { key: 'basketball_ncaab', label: 'NCAAB', emoji: '' },
  { key: 'soccer', label: 'Soccer', emoji: '' },
  { key: 'tennis', label: 'Tennis', emoji: '' },
];

// Sharp/baseline books that users CANNOT bet on (used for comparison only)
const SHARP_BOOKS = ['pinnacle', 'pinnacle_dpi', 'betcris', 'bookmaker'];

// Retail books users CAN bet on
const RETAIL_BOOKS = ['fanduel', 'draftkings', 'betmgm', 'caesars', 'pointsbet', 'bet365', 'wynnbet', 'unibet'];

// Check if a book is a retail book (bettable)
const isRetailBook = (book: string | null): boolean => {
  if (!book) return false;
  return RETAIL_BOOKS.includes(book.toLowerCase()) || !SHARP_BOOKS.includes(book.toLowerCase());
};

interface LiveEdgeFeedProps {
  sport?: string;
  selectedBook?: string;
  maxEdges?: number;
  onEdgeCount?: (count: number) => void;
}

export function LiveEdgeFeed({
  sport,
  selectedBook,
  maxEdges = 30,
  onEdgeCount,
}: LiveEdgeFeedProps) {
  const [edges, setEdges] = useState<LiveEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterLeague, setFilterLeague] = useState<string>('all');
  const [expandedEdgeId, setExpandedEdgeId] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Format exact timestamp
  const formatExactTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZoneName: 'short',
    });
  };

  // Format countdown (precise)
  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);

    if (diffSecs < 60) return `${diffSecs} seconds ago`;
    if (diffSecs < 3600) {
      const mins = Math.floor(diffSecs / 60);
      const secs = diffSecs % 60;
      return `${mins}m ${secs}s ago`;
    }
    const hours = Math.floor(diffSecs / 3600);
    const mins = Math.floor((diffSecs % 3600) / 60);
    return `${hours}h ${mins}m ago`;
  };

  // Fetch edges from API
  const fetchEdges = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (sport) params.set('sport', sport);
      params.set('status', 'active');
      params.set('limit', maxEdges.toString());

      const res = await fetch(`/api/edges/live?${params}`);
      if (!res.ok) throw new Error('Failed to fetch edges');

      const data = await res.json();
      let fetchedEdges: LiveEdge[] = data.edges || [];

      // Filter by book if selected - show edges where this retail book offers value
      if (selectedBook) {
        const selectedBookLower = selectedBook.toLowerCase();
        fetchedEdges = fetchedEdges.filter((e) => {
          const bestBook = e.best_current_book?.toLowerCase();
          const triggeringBook = e.triggering_book?.toLowerCase();

          // If the selected book is the best current book for this edge, show it
          if (bestBook === selectedBookLower) return true;

          // If the selected book triggered this edge (they moved first), show it
          if (triggeringBook === selectedBookLower) return true;

          // For sharp divergence edges, show if the selected book is involved
          // and the best_current_book is a sharp book (means the retail book has value)
          if (SHARP_BOOKS.includes(bestBook || '')) {
            // Show this edge for any retail book since it indicates retail books have edge vs sharp
            return true;
          }

          return false;
        });
      }

      // Also filter out edges where sharp books are shown as "destination"
      // Re-assign best_current_book to nearest retail book if it's a sharp book
      fetchedEdges = fetchedEdges.map((e) => {
        if (SHARP_BOOKS.includes(e.best_current_book?.toLowerCase() || '')) {
          // Use triggering book as the retail destination if available and retail
          if (e.triggering_book && isRetailBook(e.triggering_book)) {
            return { ...e, best_current_book: e.triggering_book };
          }
          // Otherwise default to FanDuel (most common retail book)
          return { ...e, best_current_book: 'fanduel' };
        }
        return e;
      });

      setEdges(fetchedEdges);
      onEdgeCount?.(fetchedEdges.length);
      setError(null);
    } catch (e: any) {
      setError(e?.message || 'Failed to load edges');
    } finally {
      setLoading(false);
    }
  }, [sport, maxEdges, selectedBook, onEdgeCount]);

  // Initial fetch
  useEffect(() => {
    fetchEdges();
  }, [fetchEdges]);

  // Realtime subscription
  useEffect(() => {
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
        () => {
          fetchEdges();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [sport, fetchEdges]);

  // Update times every 5 seconds for precise countdowns
  const [, setTick] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 5000);
    return () => clearInterval(interval);
  }, []);

  // Filter by league tab
  const filteredEdges = edges.filter((edge) => {
    if (filterLeague === 'all') return true;
    if (filterLeague === 'soccer') return edge.sport?.includes('soccer');
    if (filterLeague === 'tennis') return edge.sport?.includes('tennis');
    return edge.sport === filterLeague;
  });

  // Count edges per league for badges
  const leagueCounts = LEAGUE_TABS.reduce((acc, tab) => {
    if (tab.key === 'all') {
      acc[tab.key] = edges.length;
    } else if (tab.key === 'soccer') {
      acc[tab.key] = edges.filter((e) => e.sport?.includes('soccer')).length;
    } else if (tab.key === 'tennis') {
      acc[tab.key] = edges.filter((e) => e.sport?.includes('tennis')).length;
    } else {
      acc[tab.key] = edges.filter((e) => e.sport === tab.key).length;
    }
    return acc;
  }, {} as Record<string, number>);

  // Get human-readable market label
  const getMarketLabel = (edge: LiveEdge): string => {
    if (edge.market_type === 'h2h') return 'Moneyline';
    if (edge.market_type === 'spreads') return 'Spread';
    if (edge.market_type === 'totals') return 'Total';
    if (edge.market_type === 'player_props') return 'Player Prop';
    return edge.market_type || 'Unknown';
  };

  // Get sport emoji
  const getSportEmoji = (sport: string): string => {
    if (sport?.includes('basketball')) return '\u{1F3C0}';
    if (sport?.includes('football')) return '\u{1F3C8}';
    if (sport?.includes('hockey')) return '\u{1F3D2}';
    if (sport?.includes('baseball')) return '\u{26BE}';
    if (sport?.includes('soccer')) return '\u{26BD}';
    if (sport?.includes('tennis')) return '\u{1F3BE}';
    if (sport?.includes('mma')) return '\u{1F94A}';
    return '\u{1F3C6}';
  };

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
              {edges.length}
            </span>
          )}
        </div>

        <button
          onClick={fetchEdges}
          className="p-1.5 rounded-md bg-zinc-800 text-zinc-500 hover:text-zinc-400 transition-colors"
          title="Refresh"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* League Tabs */}
      <div className="px-2 py-2 border-b border-zinc-800/50 overflow-x-auto">
        <div className="flex gap-1">
          {LEAGUE_TABS.map((tab) => {
            const count = leagueCounts[tab.key] || 0;
            // Hide tabs with 0 edges (except "All")
            if (count === 0 && tab.key !== 'all') return null;

            return (
              <button
                key={tab.key}
                onClick={() => setFilterLeague(tab.key)}
                className={`px-2 py-1 text-xs rounded-md whitespace-nowrap transition-colors flex items-center gap-1 ${
                  filterLeague === tab.key
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-zinc-800 text-zinc-500 hover:text-zinc-400'
                }`}
              >
                {tab.label}
                {count > 0 && (
                  <span className="text-[10px] opacity-70">({count})</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Book Filter Indicator */}
      {selectedBook && (
        <div className="px-4 py-2 bg-zinc-800/30 border-b border-zinc-800/50">
          <span className="text-[10px] text-zinc-500">
            Showing edges for{' '}
            <span className="text-zinc-300 capitalize font-medium">{selectedBook}</span>
          </span>
        </div>
      )}

      {/* Edge List */}
      <div className="flex-1 overflow-y-auto" ref={listRef}>
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
        ) : filteredEdges.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-center px-4">
            <Activity className="w-8 h-8 text-zinc-700 mb-2" />
            <p className="text-sm text-zinc-500">No active edges</p>
            <p className="text-xs text-zinc-600 mt-1">
              {selectedBook ? `No edges on ${selectedBook}` : 'Waiting for edge detection'}
            </p>
          </div>
        ) : (
          <div className="p-3 space-y-2">
            {filteredEdges.map((edge) => (
              <EdgeCard
                key={edge.id}
                edge={edge}
                isExpanded={expandedEdgeId === edge.id}
                onToggle={() =>
                  setExpandedEdgeId(expandedEdgeId === edge.id ? null : edge.id)
                }
                formatExactTime={formatExactTime}
                formatTimeAgo={formatTimeAgo}
                getMarketLabel={getMarketLabel}
                getSportEmoji={getSportEmoji}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Individual edge card with full context
interface EdgeCardProps {
  edge: LiveEdge;
  isExpanded: boolean;
  onToggle: () => void;
  formatExactTime: (date: string) => string;
  formatTimeAgo: (date: string) => string;
  getMarketLabel: (edge: LiveEdge) => string;
  getSportEmoji: (sport: string) => string;
}

function EdgeCard({
  edge,
  isExpanded,
  onToggle,
  formatExactTime,
  formatTimeAgo,
  getMarketLabel,
  getSportEmoji,
}: EdgeCardProps) {
  const typeConfig = EDGE_TYPE_CONFIG[edge.edge_type as keyof typeof EDGE_TYPE_CONFIG];

  // Build full headline with teams context
  const getHeadline = (): string => {
    const market = getMarketLabel(edge);
    const outcome = edge.outcome_key || '';

    // For player props
    if (edge.market_type === 'player_props') {
      const parts = outcome.split('|');
      const player = parts[0]?.replace(/_/g, ' ')?.split(' ').map(w =>
        w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()
      ).join(' ');
      const side = parts[1] || '';
      return `${player} ${side}`;
    }

    // For game markets
    if (edge.market_type === 'totals') {
      const side = outcome.toLowerCase() === 'over' ? 'Over' : 'Under';
      return `${side} ${edge.initial_value || edge.current_value || ''}`;
    }

    // Default
    return `${outcome} ${market}`;
  };

  // Get edge value description
  const getEdgeValue = (): string => {
    if (edge.edge_type === 'juice_improvement') {
      return `${Math.round(edge.edge_magnitude)}¢ savings`;
    }
    if (edge.market_type === 'h2h') {
      return `${edge.edge_magnitude > 0 ? '+' : ''}${Math.round(edge.edge_magnitude)}¢ value`;
    }
    return `${edge.edge_magnitude > 0 ? '+' : ''}${edge.edge_magnitude.toFixed(1)} pts`;
  };

  // Confidence color
  const getConfidenceColor = (conf: number): string => {
    if (conf >= 70) return 'text-emerald-400';
    if (conf >= 50) return 'text-blue-400';
    if (conf >= 35) return 'text-amber-400';
    return 'text-zinc-400';
  };

  const confidenceColor = edge.confidence ? getConfidenceColor(edge.confidence) : 'text-zinc-400';

  return (
    <div
      className={`rounded-lg border transition-all ${
        edge.status === 'active'
          ? 'bg-zinc-900 border-zinc-700 hover:border-zinc-600'
          : 'bg-zinc-900/50 border-yellow-500/20'
      }`}
    >
      {/* Main Card - Click to expand */}
      <div className="p-3 cursor-pointer" onClick={onToggle}>
        {/* Sport + Type Row */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm">{getSportEmoji(edge.sport)}</span>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              typeConfig?.color === 'blue' ? 'bg-blue-500/15 text-blue-400' :
              typeConfig?.color === 'green' ? 'bg-emerald-500/15 text-emerald-400' :
              typeConfig?.color === 'purple' ? 'bg-purple-500/15 text-purple-400' :
              'bg-orange-500/15 text-orange-400'
            }`}>
              {typeConfig?.label || edge.edge_type}
            </span>
          </div>
          <div className={`text-xs font-mono font-bold ${confidenceColor}`}>
            {edge.confidence?.toFixed(0)}%
          </div>
        </div>

        {/* Headline */}
        <div className="text-sm font-semibold text-zinc-100 mb-1">
          {getHeadline()}
        </div>

        {/* Value + Book + Sharp Comparison */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-emerald-400 font-medium">{getEdgeValue()}</span>
          <div className="flex items-center gap-1 text-zinc-500">
            {edge.best_current_book && (
              <span>
                <span className="capitalize text-emerald-400 font-medium">{edge.best_current_book}</span>
              </span>
            )}
            {edge.sharp_book_line !== null && (
              <span className="text-zinc-600">
                vs sharp {edge.sharp_book_line > 0 ? '+' : ''}{edge.sharp_book_line}
              </span>
            )}
          </div>
        </div>

        {/* Timestamp */}
        <div className="flex items-center gap-1 mt-2 text-[10px] text-zinc-500">
          <Clock className="w-3 h-3" />
          <span>{formatTimeAgo(edge.detected_at)}</span>
          <span className="text-zinc-700">|</span>
          <span>{formatExactTime(edge.detected_at)}</span>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="px-3 pb-3 pt-2 border-t border-zinc-800 space-y-2">
          {/* Full description */}
          <p className="text-xs text-zinc-300">{formatEdgeDescription(edge)}</p>

          {/* Details grid */}
          <div className="grid grid-cols-2 gap-2 text-[10px]">
            <div>
              <span className="text-zinc-500">Market:</span>{' '}
              <span className="text-zinc-300">{getMarketLabel(edge)}</span>
            </div>
            <div>
              <span className="text-zinc-500">Outcome:</span>{' '}
              <span className="text-zinc-300">{edge.outcome_key}</span>
            </div>
            {edge.sharp_book_line !== null && (
              <div>
                <span className="text-zinc-500">Pinnacle Line:</span>{' '}
                <span className="text-zinc-300">{edge.sharp_book_line}</span>
              </div>
            )}
            <div>
              <span className="text-zinc-500">Best Book:</span>{' '}
              <span className="text-zinc-300 capitalize">{edge.best_current_book}</span>
            </div>
          </div>

          {/* Confidence bar */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-zinc-500 w-16">Confidence</span>
            <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  edge.confidence && edge.confidence >= 70 ? 'bg-emerald-500' :
                  edge.confidence && edge.confidence >= 50 ? 'bg-blue-500' :
                  'bg-amber-500'
                }`}
                style={{ width: `${edge.confidence || 0}%` }}
              />
            </div>
            <span className={`text-[10px] font-mono ${confidenceColor}`}>
              {edge.confidence?.toFixed(0)}%
            </span>
          </div>

          {/* Game link */}
          {edge.game_id && (
            <Link
              href={`/edge/portal/sports/game/${edge.game_id}?sport=${edge.sport}`}
              className="flex items-center gap-1 text-[10px] text-emerald-400 hover:text-emerald-300"
              onClick={(e) => e.stopPropagation()}
            >
              <ExternalLink className="w-3 h-3" />
              View Game Details
            </Link>
          )}
        </div>
      )}
    </div>
  );
}

export default LiveEdgeFeed;
