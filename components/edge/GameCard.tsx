'use client';

import { useState } from 'react';
import Link from 'next/link';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import type { Game, ConsensusOdds, EdgeCalculation } from '@/types/edge';

function getEdgeColor(delta: number): string {
  if (delta >= 0.03) return 'text-emerald-400';
  if (delta >= 0.01) return 'text-emerald-300/70';
  if (delta <= -0.03) return 'text-red-400';
  if (delta <= -0.01) return 'text-red-300/70';
  return 'text-zinc-500';
}

function getEdgeBg(delta: number): string {
  if (delta >= 0.03) return 'bg-emerald-500/10 border-emerald-500/30';
  if (delta <= -0.03) return 'bg-red-500/10 border-red-500/30';
  return 'bg-zinc-800/50 border-zinc-700/50';
}

function getMockEdge(gameId: string, offset: number): number {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + offset;
  const x = Math.sin(seed) * 10000;
  return (x - Math.floor(x) - 0.5) * 0.08;
}

function getTeamAbbrev(teamName: string): string {
  const words = teamName.split(' ');
  if (words.length === 1) return teamName.slice(0, 6);
  // Return last word (usually the mascot) truncated
  return words[words.length - 1].slice(0, 6);
}

function MiniSparkline({ seed, value, data: realData }: { seed: string; value: number; data?: number[] }) {
  if (realData && realData.length >= 2) {
    // Use real snapshot data
    const min = Math.min(...realData);
    const max = Math.max(...realData);
    const range = max - min || 1;
    const pathPoints = realData.map((val, i) => `${(i / (realData.length - 1)) * 24},${8 - ((val - min) / range) * 8}`).join(' ');
    const trend = realData[realData.length - 1] - realData[0];
    let color = '#71717a';
    if (trend > 0.05) color = '#10b981';
    else if (trend < -0.05) color = '#ef4444';
    return (
      <svg width="24" height="8" className="inline-block opacity-70">
        <polyline points={pathPoints} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }

  // No real data — show flat neutral line
  return (
    <svg width="24" height="8" className="inline-block opacity-40">
      <line x1="0" y1="4" x2="24" y2="4" stroke="#71717a" strokeWidth="1" strokeDasharray="2 2" />
    </svg>
  );
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

const formatEdge = (delta: number) => {
  const pct = (delta * 100).toFixed(1);
  return delta > 0 ? `+${pct}%` : `${pct}%`;
};

interface GameCardProps {
  game: Game;
  consensus?: ConsensusOdds;
  edge?: EdgeCalculation;
}

export function GameCard({ game, consensus, edge }: GameCardProps) {
  const formatGameTime = (date: Date) => {
    return date.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
  };

  return (
    <Link
      href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
      className="block bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden hover:border-zinc-700 hover:bg-zinc-900/80 transition-all"
    >
      {/* Header */}
      <div className="px-3 py-2 bg-zinc-800/50 border-b border-zinc-800 flex justify-between items-center">
        <span className="text-xs text-zinc-400">{formatGameTime(game.commenceTime)}</span>
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
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 1))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(-consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.awayPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-sp-a`} value={getMockEdge(game.id, 1)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 1))}`}>{formatEdge(getMockEdge(game.id, 1))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Away ML */}
        {consensus?.h2h ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 2))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.awayPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-ml-a`} value={getMockEdge(game.id, 2)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 2))}`}>{formatEdge(getMockEdge(game.id, 2))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Over */}
        {consensus?.totals ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 3))}`}>
            <div className="text-[11px] font-medium text-zinc-100">O{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.overPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-to-o`} value={getMockEdge(game.id, 3)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 3))}`}>{formatEdge(getMockEdge(game.id, 3))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>

      {/* Home Team Row */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1.5 items-center gap-1">
        <TeamDisplay teamName={game.homeTeam} sportKey={game.sportKey} />

        {/* Home Spread */}
        {consensus?.spreads ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 4))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.homePrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-sp-h`} value={getMockEdge(game.id, 4)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 4))}`}>{formatEdge(getMockEdge(game.id, 4))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Home ML */}
        {consensus?.h2h ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 5))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.homePrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-ml-h`} value={getMockEdge(game.id, 5)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 5))}`}>{formatEdge(getMockEdge(game.id, 5))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Under */}
        {consensus?.totals ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 6))}`}>
            <div className="text-[11px] font-medium text-zinc-100">U{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.underPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-to-u`} value={getMockEdge(game.id, 6)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 6))}`}>{formatEdge(getMockEdge(game.id, 6))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>
    </Link>
  );
}