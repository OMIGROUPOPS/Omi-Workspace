'use client';

import { useState } from 'react';
import Link from 'next/link';
import { formatOdds } from '@/lib/edge/utils/odds-math';
import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';

const NFL_TEAMS: Record<string, string> = {
  'Arizona Cardinals': 'ari', 'Atlanta Falcons': 'atl', 'Baltimore Ravens': 'bal', 'Buffalo Bills': 'buf',
  'Carolina Panthers': 'car', 'Chicago Bears': 'chi', 'Cincinnati Bengals': 'cin', 'Cleveland Browns': 'cle',
  'Dallas Cowboys': 'dal', 'Denver Broncos': 'den', 'Detroit Lions': 'det', 'Green Bay Packers': 'gb',
  'Houston Texans': 'hou', 'Indianapolis Colts': 'ind', 'Jacksonville Jaguars': 'jax', 'Kansas City Chiefs': 'kc',
  'Las Vegas Raiders': 'lv', 'Los Angeles Chargers': 'lac', 'Los Angeles Rams': 'lar', 'Miami Dolphins': 'mia',
  'Minnesota Vikings': 'min', 'New England Patriots': 'ne', 'New Orleans Saints': 'no', 'New York Giants': 'nyg',
  'New York Jets': 'nyj', 'Philadelphia Eagles': 'phi', 'Pittsburgh Steelers': 'pit', 'San Francisco 49ers': 'sf',
  'Seattle Seahawks': 'sea', 'Tampa Bay Buccaneers': 'tb', 'Tennessee Titans': 'ten', 'Washington Commanders': 'wsh',
};

const NBA_TEAMS: Record<string, string> = {
  'Atlanta Hawks': 'atl', 'Boston Celtics': 'bos', 'Brooklyn Nets': 'bkn', 'Charlotte Hornets': 'cha',
  'Chicago Bulls': 'chi', 'Cleveland Cavaliers': 'cle', 'Dallas Mavericks': 'dal', 'Denver Nuggets': 'den',
  'Detroit Pistons': 'det', 'Golden State Warriors': 'gs', 'Houston Rockets': 'hou', 'Indiana Pacers': 'ind',
  'LA Clippers': 'lac', 'Los Angeles Clippers': 'lac', 'Los Angeles Lakers': 'lal', 'LA Lakers': 'lal',
  'Memphis Grizzlies': 'mem', 'Miami Heat': 'mia', 'Milwaukee Bucks': 'mil', 'Minnesota Timberwolves': 'min',
  'New Orleans Pelicans': 'no', 'New York Knicks': 'ny', 'Oklahoma City Thunder': 'okc', 'Orlando Magic': 'orl',
  'Philadelphia 76ers': 'phi', 'Phoenix Suns': 'phx', 'Portland Trail Blazers': 'por', 'Sacramento Kings': 'sac',
  'San Antonio Spurs': 'sa', 'Toronto Raptors': 'tor', 'Utah Jazz': 'utah', 'Washington Wizards': 'wsh',
};

const NHL_TEAMS: Record<string, string> = {
  'Anaheim Ducks': 'ana', 'Boston Bruins': 'bos', 'Buffalo Sabres': 'buf', 'Calgary Flames': 'cgy',
  'Carolina Hurricanes': 'car', 'Chicago Blackhawks': 'chi', 'Colorado Avalanche': 'col',
  'Columbus Blue Jackets': 'cbj', 'Dallas Stars': 'dal', 'Detroit Red Wings': 'det', 'Edmonton Oilers': 'edm',
  'Florida Panthers': 'fla', 'Los Angeles Kings': 'la', 'Minnesota Wild': 'min', 'Montreal Canadiens': 'mtl',
  'Nashville Predators': 'nsh', 'New Jersey Devils': 'nj', 'New York Islanders': 'nyi', 'New York Rangers': 'nyr',
  'Ottawa Senators': 'ott', 'Philadelphia Flyers': 'phi', 'Pittsburgh Penguins': 'pit', 'San Jose Sharks': 'sj',
  'Seattle Kraken': 'sea', 'St. Louis Blues': 'stl', 'Tampa Bay Lightning': 'tb', 'Toronto Maple Leafs': 'tor',
  'Utah Hockey Club': 'utah', 'Vancouver Canucks': 'van', 'Vegas Golden Knights': 'vgk',
  'Washington Capitals': 'wsh', 'Winnipeg Jets': 'wpg',
};

function getTeamLogo(teamName: string, sportKey: string): string | null {
  if (sportKey.includes('nfl')) {
    const abbrev = NFL_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nfl/500/${abbrev}.png`;
  }
  if (sportKey.includes('nba')) {
    const abbrev = NBA_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nba/500/${abbrev}.png`;
  }
  if (sportKey.includes('nhl') || sportKey.includes('icehockey')) {
    const abbrev = NHL_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nhl/500/${abbrev}.png`;
  }
  return null;
}

function getTeamColor(teamName: string): string {
  const colors = ['#1d4ed8', '#dc2626', '#059669', '#d97706', '#7c3aed', '#db2777', '#0891b2', '#65a30d'];
  const hash = teamName.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

function getTeamInitials(teamName: string): string {
  const words = teamName.split(' ');
  if (words.length === 1) return teamName.slice(0, 2).toUpperCase();
  return words[0].slice(0, 2).toUpperCase();
}

// Get short team name (last word, usually mascot)
function getShortTeamName(teamName: string): string {
  const words = teamName.split(' ');
  // Handle special cases like "Los Angeles Chargers" -> "Chargers"
  return words[words.length - 1];
}

function TeamLogo({ teamName, sportKey }: { teamName: string; sportKey: string }) {
  const logo = getTeamLogo(teamName, sportKey);
  if (logo) return <img src={logo} alt={teamName} className="w-5 h-5 object-contain" />;
  
  return (
    <div 
      className="w-5 h-5 rounded-full flex items-center justify-center text-[7px] font-bold text-white flex-shrink-0"
      style={{ backgroundColor: getTeamColor(teamName) }}
    >
      {getTeamInitials(teamName)}
    </div>
  );
}

// Generate mock edge based on game ID for consistency
function getMockEdge(gameId: string, marketIndex: number): number {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const x = Math.sin(seed + marketIndex) * 10000;
  return ((x - Math.floor(x)) - 0.5) * 10; // -5% to +5%
}

// Mini sparkline component
function MiniSparkline({ gameId, marketIndex }: { gameId: string; marketIndex: number }) {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + marketIndex;
  const points: number[] = [];
  for (let i = 0; i < 8; i++) {
    const x = Math.sin(seed + i * 0.7) * 10000;
    points.push((x - Math.floor(x)) * 10);
  }
  
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const height = 12;
  const width = 24;
  
  const pathData = points
    .map((p, i) => {
      const x = (i / (points.length - 1)) * width;
      const y = height - ((p - min) / range) * height;
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    })
    .join(' ');
  
  const trend = points[points.length - 1] - points[0];
  const color = trend >= 0 ? '#10b981' : '#ef4444';
  
  return (
    <svg width={width} height={height} className="opacity-60">
      <path d={pathData} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  );
}

function OddsCell({ line, price, gameId, marketIndex }: { line?: number | string; price: number; gameId: string; marketIndex: number }) {
  const edge = getMockEdge(gameId, marketIndex);
  const edgeColor = edge >= 0 ? 'text-emerald-400' : 'text-red-400';
  const bgTint = edge >= 2 ? 'bg-emerald-500/10' : edge <= -2 ? 'bg-red-500/5' : 'bg-zinc-800';
  
  return (
    <div className={`flex flex-col items-center justify-center p-1.5 ${bgTint} border border-zinc-700/50 rounded hover:border-zinc-600 transition-all cursor-pointer`}>
      <div className="flex items-center gap-1">
        <span className="text-xs font-semibold text-zinc-100">
          {line !== undefined && (typeof line === 'number' ? (line > 0 ? `+${line}` : line) : line)}
        </span>
      </div>
      <span className={`text-xs ${price > 0 ? 'text-emerald-400' : 'text-zinc-300'}`}>
        {formatOdds(price)}
      </span>
      <div className="flex items-center gap-1 mt-0.5">
        <MiniSparkline gameId={gameId} marketIndex={marketIndex} />
        <span className={`text-[10px] ${edgeColor}`}>
          {edge >= 0 ? '+' : ''}{edge.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

function MoneylineCell({ price, gameId, marketIndex }: { price: number; gameId: string; marketIndex: number }) {
  const edge = getMockEdge(gameId, marketIndex);
  const edgeColor = edge >= 0 ? 'text-emerald-400' : 'text-red-400';
  const bgTint = edge >= 2 ? 'bg-emerald-500/10' : edge <= -2 ? 'bg-red-500/5' : 'bg-zinc-800';
  
  return (
    <div className={`flex flex-col items-center justify-center p-1.5 ${bgTint} border border-zinc-700/50 rounded hover:border-zinc-600 transition-all cursor-pointer`}>
      <span className={`text-xs font-semibold ${price > 0 ? 'text-emerald-400' : 'text-zinc-100'}`}>
        {formatOdds(price)}
      </span>
      <div className="flex items-center gap-1 mt-0.5">
        <MiniSparkline gameId={gameId} marketIndex={marketIndex} />
        <span className={`text-[10px] ${edgeColor}`}>
          {edge >= 0 ? '+' : ''}{edge.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

const SPORT_PILLS = [
  { key: 'americanfootball_nfl', label: 'NFL' },
  { key: 'americanfootball_ncaaf', label: 'NCAAF' },
  { key: 'basketball_nba', label: 'NBA' },
  { key: 'icehockey_nhl', label: 'NHL' },
  { key: 'basketball_ncaab', label: 'NCAAB' },
  { key: 'soccer_epl', label: 'Soccer' },
  { key: 'basketball_wnba', label: 'WNBA' },
  { key: 'baseball_mlb', label: 'MLB' },
  { key: 'mma_mixed_martial_arts', label: 'MMA' },
];

interface SportsHomeGridProps {
  games: Record<string, any[]>;
}

export function SportsHomeGrid({ games }: SportsHomeGridProps) {
  const [activeSport, setActiveSport] = useState<string | null>(null);

  const displayGames = activeSport ? { [activeSport]: games[activeSport] || [] } : games;

  return (
    <div>
      {/* Sport Pills */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        <button
          onClick={() => setActiveSport(null)}
          className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all ${
            activeSport === null
              ? 'bg-emerald-500 text-white'
              : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
          }`}
        >
          All
        </button>
        {SPORT_PILLS.map((sport) => (
          <button
            key={sport.key}
            onClick={() => setActiveSport(sport.key)}
            className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all ${
              activeSport === sport.key
                ? 'bg-emerald-500 text-white'
                : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
            }`}
          >
            {sport.label}
          </button>
        ))}
      </div>

      {/* Games by Sport */}
      <div className="space-y-8">
        {Object.entries(displayGames).map(([sportKey, sportGames]) => {
          if (!sportGames || sportGames.length === 0) return null;
          
          const sportInfo = SUPPORTED_SPORTS.find(s => s.key === sportKey);
          const sportName = sportInfo?.name || sportKey;

          return (
            <div key={sportKey}>
              {/* Sport Header */}
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-zinc-100">{sportName}</h2>
                <Link
                  href={`/edge/portal/sports/${sportKey}`}
                  className="text-sm text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                >
                  More {sportName}
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>

              {/* Games Grid - wider cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {sportGames.map((game: any) => {
                  const gameTime = new Date(game.commenceTime).toLocaleString('en-US', {
                    weekday: 'short',
                    hour: 'numeric',
                    minute: '2-digit',
                  });

                  return (
                    <Link
                      key={game.id}
                      href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                      className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden hover:border-zinc-700 transition-all"
                    >
                      {/* Card Header */}
                      <div className="px-3 py-2 bg-zinc-800/50 border-b border-zinc-800 flex items-center justify-between">
                        <span className="text-xs text-zinc-400">{gameTime}</span>
                      </div>

                      {/* Column Headers */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1.5 border-b border-zinc-800/50">
                        <span className="text-[10px] text-zinc-500 uppercase"></span>
                        <span className="text-[10px] text-zinc-500 uppercase text-center">Spread</span>
                        <span className="text-[10px] text-zinc-500 uppercase text-center">ML</span>
                        <span className="text-[10px] text-zinc-500 uppercase text-center">Total</span>
                      </div>

                      {/* Away Team */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-2 items-center">
                        <div className="flex items-center gap-2 min-w-0">
                          <TeamLogo teamName={game.awayTeam} sportKey={game.sportKey} />
                          <span className="text-xs text-zinc-100 truncate">{getShortTeamName(game.awayTeam)}</span>
                        </div>
                        {game.consensus?.spreads ? (
                          <OddsCell 
                            line={-game.consensus.spreads.line} 
                            price={game.consensus.spreads.awayPrice} 
                            gameId={game.id}
                            marketIndex={0}
                          />
                        ) : <div className="text-center text-zinc-600 text-xs">-</div>}
                        {game.consensus?.h2h ? (
                          <MoneylineCell 
                            price={game.consensus.h2h.awayPrice} 
                            gameId={game.id}
                            marketIndex={1}
                          />
                        ) : <div className="text-center text-zinc-600 text-xs">-</div>}
                        {game.consensus?.totals ? (
                          <OddsCell 
                            line={`O${game.consensus.totals.line}`} 
                            price={game.consensus.totals.overPrice} 
                            gameId={game.id}
                            marketIndex={2}
                          />
                        ) : <div className="text-center text-zinc-600 text-xs">-</div>}
                      </div>

                      {/* Home Team */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-2 items-center">
                        <div className="flex items-center gap-2 min-w-0">
                          <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                          <span className="text-xs text-zinc-100 truncate">{getShortTeamName(game.homeTeam)}</span>
                        </div>
                        {game.consensus?.spreads ? (
                          <OddsCell 
                            line={game.consensus.spreads.line} 
                            price={game.consensus.spreads.homePrice} 
                            gameId={game.id}
                            marketIndex={3}
                          />
                        ) : <div className="text-center text-zinc-600 text-xs">-</div>}
                        {game.consensus?.h2h ? (
                          <MoneylineCell 
                            price={game.consensus.h2h.homePrice} 
                            gameId={game.id}
                            marketIndex={4}
                          />
                        ) : <div className="text-center text-zinc-600 text-xs">-</div>}
                        {game.consensus?.totals ? (
                          <OddsCell 
                            line={`U${game.consensus.totals.line}`} 
                            price={game.consensus.totals.underPrice} 
                            gameId={game.id}
                            marketIndex={5}
                          />
                        ) : <div className="text-center text-zinc-600 text-xs">-</div>}
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}