'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import { LiveEdge, EDGE_TYPE_CONFIG, EDGE_STATUS_CONFIG, formatEdgeMagnitude } from '@/lib/edge/types/edge';
import { LiveEdgeCard } from './LiveEdgeCard';
import { Activity, ChevronDown, ChevronUp, Zap, TrendingUp, DollarSign, GitBranch, RefreshCw } from 'lucide-react';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface CEQEdge {
  market: 'spread' | 'h2h' | 'total';
  side: 'home' | 'away' | 'over' | 'under';
  ceq: number;
  confidence: string;
  sideLabel: string;
  lineValue?: string;
}

interface GameEdgesPanelProps {
  gameId: string;
  sport: string;
  ceqEdges?: CEQEdge[];
}

export function GameEdgesPanel({ gameId, sport, ceqEdges = [] }: GameEdgesPanelProps) {
  const [edges, setEdges] = useState<LiveEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showExpired, setShowExpired] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false); // Start expanded, collapse if many edges

  // Fetch edges for this game
  const fetchEdges = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (showExpired) params.set('include_expired', 'true');

      const res = await fetch(`/api/edges/game/${gameId}?${params}`);
      if (!res.ok) throw new Error('Failed to fetch edges');

      const data = await res.json();
      setEdges(data.edges || []);
      setError(null);
    } catch (e: any) {
      console.error('[GameEdgesPanel] Error:', e);
      setError(e?.message || 'Failed to load edges');
    } finally {
      setLoading(false);
    }
  }, [gameId, showExpired]);

  // Initial fetch
  useEffect(() => {
    fetchEdges();
  }, [fetchEdges]);

  // Realtime subscription for this game
  useEffect(() => {
    const channel = supabase
      .channel(`game-edges-${gameId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'live_edges',
          filter: `game_id=eq.${gameId}`,
        },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setEdges((prev) => [payload.new as LiveEdge, ...prev]);
          } else if (payload.eventType === 'UPDATE') {
            const updated = payload.new as LiveEdge;
            setEdges((prev) =>
              prev.map((e) => (e.id === updated.id ? updated : e))
            );
          } else if (payload.eventType === 'DELETE') {
            setEdges((prev) => prev.filter((e) => e.id !== payload.old.id));
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [gameId]);

  // Group edges by status
  const activeEdges = edges.filter((e) => e.status === 'active');
  const fadingEdges = edges.filter((e) => e.status === 'fading');
  const expiredEdges = edges.filter((e) => e.status === 'expired');

  // Group by market type for display
  const groupByMarket = (edgeList: LiveEdge[]) => {
    return edgeList.reduce((acc, edge) => {
      const market = edge.market_type;
      if (!acc[market]) acc[market] = [];
      acc[market].push(edge);
      return acc;
    }, {} as Record<string, LiveEdge[]>);
  };

  if (loading) {
    return (
      <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
        <div className="flex items-center gap-2 text-zinc-500">
          <RefreshCw className="w-4 h-4 animate-spin" />
          <span className="text-sm">Loading edges...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-4">
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }

  // Filter CEQ edges to only show those with actual edge (>= 56%)
  const validCEQEdges = ceqEdges.filter(e => e.ceq >= 56);
  const hasEdges = edges.length > 0 || validCEQEdges.length > 0;
  const hasActiveEdges = activeEdges.length > 0 || fadingEdges.length > 0 || validCEQEdges.length > 0;

  return (
    <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
      {/* Header - Clickable to toggle collapse */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full flex items-center justify-between px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 hover:bg-zinc-800/70 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-100">Detected Edges</h3>
          {hasActiveEdges && (
            <div className="flex items-center gap-2">
              {activeEdges.length > 0 && (
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                  </span>
                  {activeEdges.length}
                </span>
              )}
              {fadingEdges.length > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 text-xs font-medium">
                  {fadingEdges.length} fading
                </span>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 text-zinc-500">
          {isCollapsed && hasActiveEdges && (
            <span className="text-xs">Click to expand</span>
          )}
          {isCollapsed ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronUp className="w-4 h-4" />
          )}
        </div>
      </button>

      {/* Content - Collapsible with max-height */}
      {!isCollapsed && (
        <div className="p-4 max-h-64 overflow-y-auto">
        {!hasEdges ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Activity className="w-8 h-8 text-zinc-700 mb-2" />
            <p className="text-sm text-zinc-500">No edges detected</p>
            <p className="text-xs text-zinc-600 mt-1">
              Edges will appear when line movements or opportunities are identified
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* CEQ-Calculated Edges (from pillar analysis) */}
            {validCEQEdges.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  CEQ Analysis Edges
                </h4>
                <div className="space-y-2">
                  {validCEQEdges
                    .sort((a, b) => b.ceq - a.ceq)
                    .map((ceqEdge, idx) => (
                    <div
                      key={`ceq-${idx}`}
                      className={`p-3 rounded-lg border ${
                        ceqEdge.ceq >= 86 ? 'bg-purple-500/10 border-purple-500/30' :
                        ceqEdge.ceq >= 76 ? 'bg-emerald-500/10 border-emerald-500/30' :
                        ceqEdge.ceq >= 66 ? 'bg-blue-500/10 border-blue-500/30' :
                        'bg-amber-500/10 border-amber-500/30'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <TrendingUp className={`w-4 h-4 ${
                            ceqEdge.ceq >= 86 ? 'text-purple-400' :
                            ceqEdge.ceq >= 76 ? 'text-emerald-400' :
                            ceqEdge.ceq >= 66 ? 'text-blue-400' :
                            'text-amber-400'
                          }`} />
                          <span className="text-sm font-semibold text-zinc-100">
                            {ceqEdge.sideLabel} {ceqEdge.lineValue && `${ceqEdge.lineValue}`}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`text-lg font-bold font-mono ${
                            ceqEdge.ceq >= 86 ? 'text-purple-400' :
                            ceqEdge.ceq >= 76 ? 'text-emerald-400' :
                            ceqEdge.ceq >= 66 ? 'text-blue-400' :
                            'text-amber-400'
                          }`}>
                            {ceqEdge.ceq}%
                          </span>
                          <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                            ceqEdge.ceq >= 86 ? 'bg-purple-500/20 text-purple-300' :
                            ceqEdge.ceq >= 76 ? 'bg-emerald-500/20 text-emerald-300' :
                            ceqEdge.ceq >= 66 ? 'bg-blue-500/20 text-blue-300' :
                            'bg-amber-500/20 text-amber-300'
                          }`}>
                            {ceqEdge.confidence}
                          </span>
                        </div>
                      </div>
                      <div className="text-xs text-zinc-400">
                        {ceqEdge.market === 'spread' ? 'Spread' : ceqEdge.market === 'h2h' ? 'Moneyline' : 'Total'} market
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Active Edges from Database */}
            {activeEdges.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  Line Movement Edges
                </h4>
                <div className="space-y-2">
                  {activeEdges.map((edge) => (
                    <LiveEdgeCard key={edge.id} edge={edge} showGameLink={false} />
                  ))}
                </div>
              </div>
            )}

            {/* Fading Edges */}
            {fadingEdges.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-yellow-400 uppercase tracking-wider mb-2">
                  Fading Edges
                </h4>
                <div className="space-y-2">
                  {fadingEdges.map((edge) => (
                    <LiveEdgeCard key={edge.id} edge={edge} showGameLink={false} />
                  ))}
                </div>
              </div>
            )}

            {/* Expired Edges (Collapsible) */}
            {expiredEdges.length > 0 && (
              <div>
                <button
                  onClick={() => setShowExpired(!showExpired)}
                  className="flex items-center gap-2 text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2 hover:text-zinc-400 transition-colors"
                >
                  {showExpired ? (
                    <ChevronUp className="w-3 h-3" />
                  ) : (
                    <ChevronDown className="w-3 h-3" />
                  )}
                  Expired Edges ({expiredEdges.length})
                </button>
                {showExpired && (
                  <div className="space-y-2">
                    {expiredEdges.map((edge) => (
                      <LiveEdgeCard key={edge.id} edge={edge} showGameLink={false} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        </div>
      )}

      {/* Summary Footer - always visible when there are active edges */}
      {hasActiveEdges && (
        <div className="px-4 py-2 bg-zinc-800/30 border-t border-zinc-800/50">
          <div className="flex items-center gap-4 text-[10px] text-zinc-500">
            <span>
              Total: {activeEdges.length + fadingEdges.length} active edge{activeEdges.length + fadingEdges.length !== 1 ? 's' : ''}
            </span>
            {activeEdges.length > 0 && (
              <span className="text-emerald-500">
                Best: {formatEdgeMagnitude(activeEdges.reduce((best, e) =>
                  e.edge_magnitude > best.edge_magnitude ? e : best
                ))}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Summary component for showing edge count inline
export function GameEdgesSummary({ gameId }: { gameId: string }) {
  const [edgeCount, setEdgeCount] = useState<{ active: number; fading: number } | null>(null);

  useEffect(() => {
    async function fetchCount() {
      try {
        const res = await fetch(`/api/edges/game/${gameId}`);
        if (!res.ok) return;
        const data = await res.json();
        setEdgeCount({
          active: data.summary?.active || 0,
          fading: data.summary?.fading || 0,
        });
      } catch {
        // Ignore errors for summary
      }
    }
    fetchCount();
  }, [gameId]);

  if (!edgeCount || (edgeCount.active === 0 && edgeCount.fading === 0)) {
    return null;
  }

  return (
    <div className="flex items-center gap-1">
      {edgeCount.active > 0 && (
        <span className="flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-medium">
          <Zap className="w-2.5 h-2.5" />
          {edgeCount.active}
        </span>
      )}
      {edgeCount.fading > 0 && (
        <span className="px-1.5 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 text-[10px] font-medium">
          {edgeCount.fading}
        </span>
      )}
    </div>
  );
}

export default GameEdgesPanel;
