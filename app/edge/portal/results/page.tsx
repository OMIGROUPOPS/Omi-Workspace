'use client';

import { useState, useEffect } from 'react';

const BACKEND_URL = 'http://localhost:8000';

interface GameResult {
  game_id: string;
  sport_key: string;
  home_team: string;
  away_team: string;
  commence_time: string;
  home_score: number;
  away_score: number;
  final_spread: number;
  final_total: number;
  winner: string;
  closing_spread_home: number;
  closing_total_line: number;
  our_edge_spread_home: number;
  our_edge_ml_home: number;
  our_edge_total_over: number;
  composite_score: number;
  confidence_level: string;
  best_bet_market: string;
  best_bet_edge: number;
  best_bet_result: string;
  spread_result: string;
  ml_result: string;
  total_result: string;
  graded_at: string;
}

interface PerformanceSummary {
  total_games: number;
  period_days: number;
  best_bet_record: string;
  best_bet_win_pct: number;
  spread_record: string;
  ml_record: string;
  total_record: string;
  by_confidence: Record<string, { record: string; win_pct: number; games: number }>;
  by_sport: Record<string, { record: string; win_pct: number; games: number }>;
}

const SPORT_ICONS: Record<string, string> = {
  'NFL': '🏈',
  'NBA': '🏀',
  'NHL': '🏒',
  'NCAAF': '🏈',
  'NCAAB': '🏀',
};

const CONFIDENCE_COLORS: Record<string, string> = {
  'STRONG_EDGE': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  'EDGE': 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
  'WATCH': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  'PASS': 'bg-zinc-800 text-zinc-500 border-zinc-700',
};

const RESULT_COLORS: Record<string, string> = {
  'win': 'text-emerald-400',
  'loss': 'text-red-400',
  'push': 'text-yellow-400',
};

function StatCard({ label, value, subValue, color }: { label: string; value: string | number; subValue?: string; color?: string }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
      <div className="text-xs text-zinc-500 uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color || 'text-zinc-100'}`}>{value}</div>
      {subValue && <div className="text-sm text-zinc-400 mt-1">{subValue}</div>}
    </div>
  );
}

function ResultBadge({ result }: { result: string | null }) {
  if (!result) return <span className="text-zinc-600">-</span>;
  
  const colors = {
    'win': 'bg-emerald-500/20 text-emerald-400',
    'loss': 'bg-red-500/20 text-red-400',
    'push': 'bg-yellow-500/20 text-yellow-400',
  };
  
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${colors[result as keyof typeof colors] || 'bg-zinc-800 text-zinc-500'}`}>
      {result}
    </span>
  );
}

export default function ResultsPage() {
  const [results, setResults] = useState<GameResult[]>([]);
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSport, setSelectedSport] = useState<string>('all');
  const [selectedPeriod, setSelectedPeriod] = useState<number>(30);
  const [view, setView] = useState<'results' | 'stats'>('stats');

  useEffect(() => {
    fetchData();
  }, [selectedSport, selectedPeriod]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const sportParam = selectedSport !== 'all' ? `&sport=${selectedSport}` : '';
      
      const [resultsRes, summaryRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/results/recent?limit=100${sportParam}`),
        fetch(`${BACKEND_URL}/api/results/summary?days=${selectedPeriod}${sportParam}`),
      ]);
      
      if (resultsRes.ok) {
        const data = await resultsRes.json();
        setResults(data.results || []);
      }
      
      if (summaryRes.ok) {
        const data = await summaryRes.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Failed to fetch results:', error);
    }
    setLoading(false);
  };

  const winPctColor = (pct: number) => {
    if (pct >= 55) return 'text-emerald-400';
    if (pct >= 52) return 'text-emerald-300';
    if (pct >= 48) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Results & Performance</h1>
          <p className="text-zinc-400">Track prediction accuracy and ROI over time</p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-6">
          {/* Sport Filter */}
          <div className="flex gap-2">
            {['all', 'NFL', 'NBA', 'NHL', 'NCAAF', 'NCAAB'].map((sport) => (
              <button
                key={sport}
                onClick={() => setSelectedSport(sport)}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
                  selectedSport === sport
                    ? 'bg-emerald-500 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                }`}
              >
                {sport === 'all' ? 'All Sports' : `${SPORT_ICONS[sport] || ''} ${sport}`}
              </button>
            ))}
          </div>

          {/* Period Filter */}
          <div className="flex gap-2 ml-auto">
            {[7, 14, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setSelectedPeriod(days)}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
                  selectedPeriod === days
                    ? 'bg-zinc-700 text-zinc-100'
                    : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800'
                }`}
              >
                {days}D
              </button>
            ))}
          </div>

          {/* View Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setView('stats')}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
                view === 'stats' ? 'bg-zinc-700 text-zinc-100' : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800'
              }`}
            >
              📊 Stats
            </button>
            <button
              onClick={() => setView('results')}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
                view === 'results' ? 'bg-zinc-700 text-zinc-100' : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800'
              }`}
            >
              📋 Results
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-zinc-500">Loading...</div>
        ) : view === 'stats' ? (
          /* Stats View */
          <div className="space-y-6">
            {/* Main Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="Best Bet Record"
                value={summary?.best_bet_record || '0-0-0'}
                subValue={`${summary?.best_bet_win_pct || 0}% win rate`}
                color={winPctColor(summary?.best_bet_win_pct || 0)}
              />
              <StatCard
                label="Spread Record"
                value={summary?.spread_record || '0-0-0'}
              />
              <StatCard
                label="Moneyline Record"
                value={summary?.ml_record || '0-0-0'}
              />
              <StatCard
                label="Totals Record"
                value={summary?.total_record || '0-0-0'}
              />
            </div>

            {/* By Confidence */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
                <h2 className="font-semibold">Performance by Confidence Level</h2>
                <p className="text-xs text-zinc-500 mt-1">Best bet results grouped by our confidence rating</p>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-4 gap-4 mb-3 text-xs text-zinc-500 uppercase tracking-wide">
                  <div>Confidence</div>
                  <div>Record</div>
                  <div>Win %</div>
                  <div>Games</div>
                </div>
                {['STRONG_EDGE', 'EDGE', 'WATCH', 'PASS'].map((conf) => {
                  const data = summary?.by_confidence?.[conf] || { record: '0-0-0', win_pct: 0, games: 0 };
                  return (
                    <div key={conf} className="grid grid-cols-4 gap-4 py-3 border-t border-zinc-800/50 items-center">
                      <div>
                        <span className={`px-2 py-1 rounded text-xs font-medium border ${CONFIDENCE_COLORS[conf]}`}>
                          {conf.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="font-medium">{data.record}</div>
                      <div className={winPctColor(data.win_pct)}>{data.win_pct}%</div>
                      <div className="text-zinc-400">{data.games}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* By Sport */}
            {summary?.by_sport && Object.keys(summary.by_sport).length > 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
                <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
                  <h2 className="font-semibold">Performance by Sport</h2>
                </div>
                <div className="p-4">
                  <div className="grid grid-cols-4 gap-4 mb-3 text-xs text-zinc-500 uppercase tracking-wide">
                    <div>Sport</div>
                    <div>Record</div>
                    <div>Win %</div>
                    <div>Games</div>
                  </div>
                  {Object.entries(summary.by_sport).map(([sport, data]) => (
                    <div key={sport} className="grid grid-cols-4 gap-4 py-3 border-t border-zinc-800/50 items-center">
                      <div className="flex items-center gap-2">
                        <span>{SPORT_ICONS[sport] || '🏆'}</span>
                        <span className="font-medium">{sport}</span>
                      </div>
                      <div className="font-medium">{data.record}</div>
                      <div className={winPctColor(data.win_pct)}>{data.win_pct}%</div>
                      <div className="text-zinc-400">{data.games}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ROI Note */}
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 text-sm text-zinc-400">
              <strong className="text-zinc-200">Note:</strong> Win rate above 52.4% on -110 odds indicates positive ROI. 
              55%+ is considered excellent. Track STRONG_EDGE and EDGE plays separately for best insight into system performance.
            </div>
          </div>
        ) : (
          /* Results View */
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
            <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 flex items-center justify-between">
              <h2 className="font-semibold">Recent Results</h2>
              <span className="text-xs text-zinc-500">{results.length} games</span>
            </div>
            
            {results.length === 0 ? (
              <div className="p-8 text-center text-zinc-500">
                No graded games yet. Games will appear here after they're completed and graded.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-xs text-zinc-500 uppercase tracking-wide border-b border-zinc-800">
                      <th className="text-left px-4 py-3">Game</th>
                      <th className="text-left px-4 py-3">Score</th>
                      <th className="text-center px-4 py-3">Confidence</th>
                      <th className="text-center px-4 py-3">Edge</th>
                      <th className="text-center px-4 py-3">Best Bet</th>
                      <th className="text-center px-4 py-3">Spread</th>
                      <th className="text-center px-4 py-3">ML</th>
                      <th className="text-center px-4 py-3">Total</th>
                      <th className="text-right px-4 py-3">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((game) => (
                      <tr key={game.game_id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span>{SPORT_ICONS[game.sport_key] || '🏆'}</span>
                            <div>
                              <div className="font-medium">{game.away_team}</div>
                              <div className="text-zinc-400">@ {game.home_team}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-mono">
                            <span className={game.winner === 'away' ? 'text-emerald-400' : ''}>{game.away_score}</span>
                            <span className="text-zinc-600"> - </span>
                            <span className={game.winner === 'home' ? 'text-emerald-400' : ''}>{game.home_score}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-medium border ${CONFIDENCE_COLORS[game.confidence_level] || CONFIDENCE_COLORS['PASS']}`}>
                            {game.confidence_level?.replace('_', ' ') || 'PASS'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={game.composite_score >= 0.5 ? 'text-emerald-400' : 'text-red-400'}>
                            {((game.composite_score || 0.5) * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="flex flex-col items-center gap-1">
                            <ResultBadge result={game.best_bet_result} />
                            {game.best_bet_market && (
                              <span className="text-xs text-zinc-500">{game.best_bet_market.replace('_', ' ')}</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <ResultBadge result={game.spread_result} />
                        </td>
                        <td className="px-4 py-3 text-center">
                          <ResultBadge result={game.ml_result} />
                        </td>
                        <td className="px-4 py-3 text-center">
                          <ResultBadge result={game.total_result} />
                        </td>
                        <td className="px-4 py-3 text-right text-zinc-400">
                          {new Date(game.commence_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}