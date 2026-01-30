'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  LiveEdge,
  EDGE_TYPE_CONFIG,
  EDGE_STATUS_CONFIG,
  formatEdgeMagnitude,
  formatEdgeDescription,
} from '@/lib/edge/types/edge';
import { TrendingUp, DollarSign, GitBranch, RefreshCw, Clock } from 'lucide-react';

const iconMap = {
  TrendingUp,
  DollarSign,
  GitBranch,
  RefreshCw,
};

interface LiveEdgeCardProps {
  edge: LiveEdge;
  showGameLink?: boolean;
  compact?: boolean;
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function getEdgeTypeColor(edgeType: string): string {
  const config = EDGE_TYPE_CONFIG[edgeType as keyof typeof EDGE_TYPE_CONFIG];
  if (!config) return 'text-zinc-400';

  const colorMap: Record<string, string> = {
    blue: 'text-blue-400',
    green: 'text-emerald-400',
    purple: 'text-purple-400',
    orange: 'text-orange-400',
  };

  return colorMap[config.color] || 'text-zinc-400';
}

function getEdgeTypeBg(edgeType: string): string {
  const config = EDGE_TYPE_CONFIG[edgeType as keyof typeof EDGE_TYPE_CONFIG];
  if (!config) return 'bg-zinc-800';

  const bgMap: Record<string, string> = {
    blue: 'bg-blue-500/10',
    green: 'bg-emerald-500/10',
    purple: 'bg-purple-500/10',
    orange: 'bg-orange-500/10',
  };

  return bgMap[config.color] || 'bg-zinc-800';
}

// Parse outcome_key for player props: "PLAYER_NAME|OVER" -> { player: "Player Name", side: "Over" }
function parseOutcomeKey(outcomeKey: string | null | undefined): { player: string | null; side: string | null } {
  if (!outcomeKey) return { player: null, side: null };

  // Handle player prop format: "COOPER_KUPP|OVER" or "COOPER KUPP|OVER"
  if (outcomeKey.includes('|')) {
    const [playerPart, side] = outcomeKey.split('|');
    // Convert COOPER_KUPP to Cooper Kupp
    const player = playerPart
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
    return { player, side: side ? side.charAt(0).toUpperCase() + side.slice(1).toLowerCase() : null };
  }

  return { player: null, side: outcomeKey };
}

// Format market type for display
function formatMarketTypeDisplay(marketType: string | null | undefined): string {
  if (!marketType) return '';
  return marketType
    .replace(/_/g, ' ')
    .replace(/player props?/i, '')
    .replace(/^player /i, '')
    .trim()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export function LiveEdgeCard({ edge, showGameLink = true, compact = false }: LiveEdgeCardProps) {
  const typeConfig = EDGE_TYPE_CONFIG[edge.edge_type as keyof typeof EDGE_TYPE_CONFIG];
  const statusConfig = EDGE_STATUS_CONFIG[edge.status];
  const IconComponent = iconMap[typeConfig?.icon as keyof typeof iconMap] || TrendingUp;

  // Parse player info from outcome_key
  const { player, side } = parseOutcomeKey(edge.outcome_key);
  const isPlayerProp = !!player || (edge.market_type?.toLowerCase().includes('player') ?? false);
  const marketDisplay = formatMarketTypeDisplay(edge.market_type);

  const content = (
    <div
      className={`rounded-lg border transition-all duration-200 ${
        edge.status === 'active'
          ? 'bg-zinc-900 border-zinc-700 hover:border-zinc-600'
          : edge.status === 'fading'
          ? 'bg-zinc-900/50 border-yellow-500/20 hover:border-yellow-500/30'
          : 'bg-zinc-900/30 border-zinc-800 opacity-60'
      } ${compact ? 'p-2' : 'p-3'}`}
    >
      {/* Header Row */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Edge Type Badge */}
          <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full ${getEdgeTypeBg(edge.edge_type)}`}>
            <IconComponent className={`w-3 h-3 ${getEdgeTypeColor(edge.edge_type)}`} />
            <span className={`text-xs font-medium ${getEdgeTypeColor(edge.edge_type)}`}>
              {typeConfig?.shortLabel || edge.edge_type}
            </span>
          </div>
          {/* Market type badge for non-prop edges */}
          {!isPlayerProp && marketDisplay && (
            <span className="text-[10px] text-zinc-500 uppercase">{marketDisplay}</span>
          )}
        </div>

        {/* Status Badge */}
        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full ${statusConfig.bgClass} border ${statusConfig.borderClass}`}>
          {edge.status === 'active' && (
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
            </span>
          )}
          <span className={`text-[10px] font-medium ${statusConfig.textClass}`}>
            {statusConfig.label}
          </span>
        </div>
      </div>

      {/* Player Prop Headline - Make player name prominent */}
      {isPlayerProp && player && (
        <div className="mb-2">
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-bold text-zinc-100">{player}</span>
            {side && <span className="text-xs text-emerald-400 font-medium">{side}</span>}
          </div>
          {marketDisplay && (
            <span className="text-[11px] text-zinc-400">{marketDisplay}</span>
          )}
        </div>
      )}

      {/* Main Content */}
      <div className="space-y-1.5">
        {/* Magnitude + Description combined for clarity */}
        <div className="flex items-baseline gap-2 flex-wrap">
          <span className="text-lg font-bold text-zinc-100 font-mono">
            {formatEdgeMagnitude(edge)}
          </span>
          {!compact && (
            <span className="text-xs text-zinc-400">
              {formatEdgeDescription(edge)}
            </span>
          )}
          {edge.confidence && (
            <span className="text-xs text-zinc-500 font-mono">
              {edge.confidence.toFixed(0)}% conf
            </span>
          )}
        </div>

        {/* Book Info - Clearer wording */}
        <div className="flex items-center gap-2 text-[10px] flex-wrap">
          {edge.best_current_book && (
            <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium capitalize">
              Best: {edge.best_current_book}
            </span>
          )}
          {edge.triggering_book && edge.triggering_book !== edge.best_current_book && (
            <span className="text-zinc-500">
              Triggered by <span className="text-zinc-400 capitalize">{edge.triggering_book}</span> move
            </span>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-1 text-[10px] text-zinc-500">
            <Clock className="w-3 h-3" />
            <span>{formatTimeAgo(edge.detected_at)}</span>
          </div>

          {/* Only show market/outcome for non-player-props (already shown above) */}
          {!isPlayerProp && edge.outcome_key && (
            <span className="text-[10px] text-zinc-600">
              {edge.outcome_key}
            </span>
          )}
        </div>
      </div>
    </div>
  );

  if (showGameLink && edge.game_id) {
    return (
      <Link
        href={`/edge/portal/sports/game/${edge.game_id}?sport=${edge.sport}`}
        className="block hover:opacity-90 transition-opacity"
      >
        {content}
      </Link>
    );
  }

  return content;
}

// Mini version for dashboard badges
export function LiveEdgeMini({ edge }: { edge: LiveEdge }) {
  const typeConfig = EDGE_TYPE_CONFIG[edge.edge_type as keyof typeof EDGE_TYPE_CONFIG];

  return (
    <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full ${getEdgeTypeBg(edge.edge_type)} border border-zinc-700/50`}>
      <span className={`text-xs font-bold ${getEdgeTypeColor(edge.edge_type)}`}>
        {typeConfig?.shortLabel}
      </span>
      <span className="text-xs text-zinc-300 font-mono">
        {formatEdgeMagnitude(edge)}
      </span>
    </div>
  );
}

export default LiveEdgeCard;
