'use client';

import { useState } from 'react';
import { Activity, ChevronDown, ChevronUp, Zap, TrendingUp } from 'lucide-react';

interface CEQEdge {
  market: 'spread' | 'h2h' | 'total';
  side: 'home' | 'away' | 'over' | 'under';
  ceq: number;
  confidence: string;
  sideLabel: string;
  lineValue?: string;
  periodLabel?: string;
}

export interface EdgeCountBreakdown {
  total: number;
  fullGame: number;
  firstHalf: number;
  secondHalf: number;
  quarters: number;  // Q1-Q4 combined
  periods: number;   // P1-P3 combined (NHL)
  teamTotals: number;
}

interface GameEdgesPanelProps {
  gameId: string;
  sport: string;
  ceqEdges?: CEQEdge[];
  edgeCountBreakdown?: EdgeCountBreakdown;
}

export function GameEdgesPanel({ gameId, sport, ceqEdges = [], edgeCountBreakdown }: GameEdgesPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Filter CEQ edges to only show those with actual edge (>= 56%)
  const validCEQEdges = ceqEdges.filter(e => e.ceq >= 56);

  // Use edgeCountBreakdown.total as the source of truth (includes all periods)
  const totalEdges = edgeCountBreakdown?.total ?? 0;
  const hasEdges = totalEdges > 0;

  // Build breakdown string for display
  const buildBreakdownString = () => {
    if (!edgeCountBreakdown) return '';
    const parts: string[] = [];
    if (edgeCountBreakdown.fullGame > 0) parts.push(`Full: ${edgeCountBreakdown.fullGame}`);
    if (edgeCountBreakdown.firstHalf > 0) parts.push(`1H: ${edgeCountBreakdown.firstHalf}`);
    if (edgeCountBreakdown.secondHalf > 0) parts.push(`2H: ${edgeCountBreakdown.secondHalf}`);
    if (edgeCountBreakdown.quarters > 0) parts.push(`Quarters: ${edgeCountBreakdown.quarters}`);
    if (edgeCountBreakdown.periods > 0) parts.push(`Periods: ${edgeCountBreakdown.periods}`);
    if (edgeCountBreakdown.teamTotals > 0) parts.push(`Team Totals: ${edgeCountBreakdown.teamTotals}`);
    return parts.length > 0 ? `(${parts.join(', ')})` : '';
  };

  return (
    <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
      {/* Header - Clickable to toggle collapse */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full flex items-center justify-between px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 hover:bg-zinc-800/70 transition-colors"
      >
        <div className="flex items-center gap-2 flex-wrap">
          <Zap className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-100">Detected Edges</h3>
          {totalEdges > 0 && (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
              </span>
              {totalEdges} total
            </span>
          )}
          {edgeCountBreakdown && totalEdges > 0 && (
            <span className="text-[10px] text-zinc-500 hidden sm:inline">
              {buildBreakdownString()}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-zinc-500">
          {isCollapsed && totalEdges > 0 && (
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
              Edges appear when CEQ (Composite Edge Quotient) reaches 56% or higher
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* CEQ-Calculated Edges for current period */}
            {validCEQEdges.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  Current Period Edges
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
                        {ceqEdge.periodLabel === 'Team Total'
                          ? 'Team Total market'
                          : `${ceqEdge.periodLabel || 'Full Game'} ${ceqEdge.market === 'spread' ? 'Spread' : ceqEdge.market === 'h2h' ? 'Moneyline' : 'Total'} market`}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Show message when there are edges in other periods but not current */}
            {validCEQEdges.length === 0 && totalEdges > 0 && (
              <div className="text-center py-4">
                <p className="text-sm text-zinc-400">
                  {totalEdges} edge{totalEdges !== 1 ? 's' : ''} detected in other periods
                </p>
                <p className="text-xs text-zinc-500 mt-1">
                  Switch tabs to view edges in different periods
                </p>
              </div>
            )}
          </div>
        )}
        </div>
      )}

      {/* Summary Footer - always visible when there are edges */}
      {totalEdges > 0 && (
        <div className="px-4 py-2 bg-zinc-800/30 border-t border-zinc-800/50">
          <div className="flex items-center justify-between text-[10px] text-zinc-500">
            <span>
              {totalEdges} total edge{totalEdges !== 1 ? 's' : ''} across all periods (CEQ &ge; 56%)
            </span>
            {validCEQEdges.length > 0 && (
              <span className="text-emerald-500">
                Best CEQ: {Math.max(...validCEQEdges.map(e => e.ceq))}%
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default GameEdgesPanel;
