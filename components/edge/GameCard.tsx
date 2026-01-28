'use client';

import { useState } from 'react';
import Link from 'next/link';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import type { Game, ConsensusOdds, EdgeCalculation } from '@/types/edge';

function getTeamAbbrev(teamName: string): string {
  const words = teamName.split(' ');
  if (words.length === 1) return teamName.slice(0, 6);
  // Return last word (usually the mascot) truncated
  return words[words.length - 1].slice(0, 6);
}

// Team display component - shows logo or colored circle with initials
function TeamDisplay({ teamName, sportKey }: { teamName: string; sportKey: string }) {
  const logo = getTeamLogo(teamName, sportKey);
  const initials = getTeamInitials(teamName);
  const color = getTeamColor(teamName);
  const abbrev = getTeamAbbrev(teamName);
  const [imgError, setImgError] = useState(false);

  return (
    <div className="flex items-center gap-1.5 min-w-0">
      {logo && !imgError ? (
        <img src={logo} alt={teamName} className="w-5 h-5 object-contain flex-shrink-0" onError={() => setImgError(true)} />
      ) : (
        <div
          className="w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-bold text-white flex-shrink-0"
          style={{ backgroundColor: color }}
        >
          {initials}
        </div>
      )}
      <span className="text-[11px] text-zinc-300 truncate">{abbrev}</span>
    </div>
  );
}

interface GameCardProps {
  game: Game;
  consensus?: ConsensusOdds;
  edge?: EdgeCalculation;
}

// Check if game is currently live (started but not more than 4 hours ago)
function isGameLive(commenceTime: Date): boolean {
  const now = new Date();
  const gameStart = new Date(commenceTime);
  const diff = now.getTime() - gameStart.getTime();
  const hoursElapsed = diff / (1000 * 60 * 60);
  // Game is live if it started (diff > 0) and less than 4 hours ago
  return diff > 0 && hoursElapsed < 4;
}

export function GameCard({ game, consensus, edge }: GameCardProps) {
  const formatGameTime = (date: Date) => {
    return date.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
  };

  const isLive = isGameLive(game.commenceTime);

  return (
    <Link
      href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
      className={`block bg-zinc-900 border rounded-lg overflow-hidden hover:bg-zinc-900/80 transition-all ${
        isLive
          ? 'border-red-500/50 ring-1 ring-red-500/20 hover:border-red-500/70'
          : 'border-zinc-800 hover:border-zinc-700'
      }`}
    >
      {/* Header */}
      <div className="px-3 py-2 bg-zinc-800/50 border-b border-zinc-800 flex justify-between items-center">
        <div className="flex items-center gap-2">
          {isLive ? (
            <span className="flex items-center gap-1.5 text-xs font-medium text-red-400 bg-red-500/20 px-1.5 py-0.5 rounded">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
              </span>
              LIVE
            </span>
          ) : (
            <span className="text-xs text-zinc-400">{formatGameTime(game.commenceTime)}</span>
          )}
        </div>
        {edge && edge.status !== 'pass' && (
          <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
            edge.status === 'rare' ? 'bg-purple-500/20 text-purple-400' :
            edge.status === 'strong_edge' ? 'bg-emerald-500/20 text-emerald-400' :
            edge.status === 'edge' ? 'bg-blue-500/20 text-blue-400' :
            'bg-amber-500/20 text-amber-400'
          }`}>
            {edge.status === 'rare' ? '★ RARE' : edge.status === 'strong_edge' ? 'STRONG' : edge.status === 'edge' ? 'EDGE' : 'WATCH'}
          </span>
        )}
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1 border-b border-zinc-800/50">
        <span></span>
        <span className="text-[9px] text-zinc-500 text-center uppercase">Spread</span>
        <span className="text-[9px] text-zinc-500 text-center uppercase">ML</span>
        <span className="text-[9px] text-zinc-500 text-center uppercase">Total</span>
      </div>

      {/* Away Team Row */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1.5 items-center gap-1">
        <TeamDisplay teamName={game.awayTeam} sportKey={game.sportKey} />

        {/* Away Spread */}
        {consensus?.spreads ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(-consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.awayPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Away ML */}
        {consensus?.h2h ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.awayPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Over */}
        {consensus?.totals ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">O{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.overPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>

      {/* Home Team Row */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1.5 items-center gap-1">
        <TeamDisplay teamName={game.homeTeam} sportKey={game.sportKey} />

        {/* Home Spread */}
        {consensus?.spreads ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.homePrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Home ML */}
        {consensus?.h2h ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.homePrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Under */}
        {consensus?.totals ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">U{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.underPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>
    </Link>
  );
}