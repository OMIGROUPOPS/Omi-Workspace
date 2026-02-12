'use client';

import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';

interface ExchangeMarket {
  id: string;
  exchange: 'kalshi' | 'polymarket';
  event_id: string;
  event_title: string;
  contract_ticker: string | null;
  yes_price: number | null;
  no_price: number | null;
  yes_bid: number | null;
  yes_ask: number | null;
  no_bid: number | null;
  no_ask: number | null;
  volume: number | null;
  open_interest: number | null;
  last_price: number | null;
  previous_yes_price: number | null;
  price_change: number | null;
  snapshot_time: string;
  mapped_game_id: string | null;
  mapped_sport_key: string | null;
  expiration_time: string | null;
  status: string;
}

interface ExchangeStats {
  total: number;
  kalshi: number;
  polymarket: number;
  totalVolume: number;
}

type Exchange = 'all' | 'kalshi' | 'polymarket';

const EXCHANGE_CONFIG: Record<Exchange, { label: string; color: string; bgColor: string }> = {
  all: { label: 'All Exchanges', color: 'text-zinc-400', bgColor: 'bg-zinc-800' },
  kalshi: { label: 'Kalshi', color: 'text-sky-400', bgColor: 'bg-sky-500/20' },
  polymarket: { label: 'Polymarket', color: 'text-violet-400', bgColor: 'bg-violet-500/20' },
};

function formatVolume(volume: number | null): string {
  if (volume === null || volume === undefined) return '-';
  if (volume >= 1000000) return `$${(volume / 1000000).toFixed(1)}M`;
  if (volume >= 1000) return `$${(volume / 1000).toFixed(1)}K`;
  return `$${volume.toFixed(0)}`;
}

function formatPrice(price: number | null): string {
  if (price === null || price === undefined) return '-';
  return `${price.toFixed(0)}\u00A2`;
}

function formatTimeUntil(dateStr: string | null): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';
  const now = new Date();
  const diff = date.getTime() - now.getTime();
  if (diff < 0) return 'Expired';
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  if (days > 30) return `${Math.floor(days / 30)}mo`;
  if (days > 0) return `${days}d`;
  if (hours > 0) return `${hours}h`;
  return '<1h';
}

/** Derive a usable YES/NO price from whatever fields are available */
function derivePrice(market: ExchangeMarket): { yes: number | null; no: number | null } {
  // Priority: yes_price > midpoint of bid/ask > last_price
  let yes = market.yes_price;
  let no = market.no_price;

  if (yes === null || yes === undefined) {
    // Try bid/ask midpoint
    if (market.yes_bid !== null && market.yes_ask !== null && market.yes_ask > 0) {
      yes = Math.round((market.yes_bid + market.yes_ask) / 2);
    } else if (market.last_price !== null && market.last_price > 0) {
      yes = market.last_price;
    }
  }

  if (no === null || no === undefined) {
    if (market.no_bid !== null && market.no_ask !== null && market.no_ask > 0) {
      no = Math.round((market.no_bid + market.no_ask) / 2);
    } else if (yes !== null && yes > 0) {
      no = 100 - yes;
    }
  }

  // If only no exists, derive yes
  if ((yes === null || yes === 0) && no !== null && no > 0) {
    yes = 100 - no;
  }

  return { yes, no };
}

/** Clean up multi-leg Kalshi titles into readable format */
function cleanTitle(title: string): { display: string; isMultiLeg: boolean; legCount: number } {
  if (!title) return { display: title, isMultiLeg: false, legCount: 0 };

  // Split comma-separated legs
  const legs = title.split(',').map(s => s.trim()).filter(Boolean);
  if (legs.length <= 1) return { display: title, isMultiLeg: false, legCount: 1 };

  // Multi-leg parlay — extract meaningful info
  const cleanLegs: string[] = [];
  const teams = new Set<string>();

  for (const leg of legs) {
    // Remove "yes "/"no " prefix
    const cleaned = leg.replace(/^(yes|no)\s+/i, '').trim();
    if (!cleaned) continue;

    // Extract team names (before "wins by" or standalone city/team)
    const winMatch = cleaned.match(/^(.+?)\s+wins?\s+by/i);
    const overMatch = cleaned.match(/^Over\s+[\d.]+\s+points/i);
    if (winMatch) {
      teams.add(winMatch[1]);
    } else if (overMatch) {
      // totals leg
    } else if (cleaned.includes(':')) {
      // Player prop like "James Harden: 6+"
    } else {
      // Standalone team name
      teams.add(cleaned);
    }

    if (cleanLegs.length < 3) {
      cleanLegs.push(cleaned);
    }
  }

  // Build display: if we found teams, lead with them
  const teamArr = Array.from(teams);
  let display: string;
  if (teamArr.length >= 2) {
    display = `${legs.length}-leg parlay: ${teamArr.slice(0, 4).join(', ')}`;
  } else if (cleanLegs.length > 0) {
    display = cleanLegs.slice(0, 2).join(' + ');
    if (legs.length > 2) display += ` +${legs.length - 2} more`;
  } else {
    display = title.slice(0, 80);
    if (title.length > 80) display += '...';
  }

  return { display, isMultiLeg: true, legCount: legs.length };
}

function PriceChangeIndicator({ change }: { change: number | null }) {
  if (change === null || change === undefined || change === 0) return null;
  const isUp = change > 0;
  return (
    <span className={`inline-flex items-center gap-0.5 text-[10px] font-mono ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
      <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20">
        {isUp ? (
          <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
        ) : (
          <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
        )}
      </svg>
      {Math.abs(change).toFixed(1)}
    </span>
  );
}

function MarketCard({ market }: { market: ExchangeMarket }) {
  const isKalshi = market.exchange === 'kalshi';
  const { display: cleanedTitle, isMultiLeg, legCount } = cleanTitle(market.event_title);
  const { yes: yesPrice, no: noPrice } = derivePrice(market);
  const hasPrice = yesPrice !== null && yesPrice > 0 && yesPrice < 100;
  const impliedPct = hasPrice ? yesPrice : null;
  const expiryStr = formatTimeUntil(market.expiration_time);

  // Calculate spread from bid/ask if available
  const spread = (market.yes_bid !== null && market.yes_ask !== null && market.yes_ask > market.yes_bid)
    ? Math.round((market.yes_ask - market.yes_bid) * 10) / 10
    : null;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 hover:border-zinc-700 transition-all group">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3
            className="text-[13px] font-medium text-zinc-100 leading-tight line-clamp-2 group-hover:text-white transition-colors"
            title={market.event_title}
          >
            {cleanedTitle}
          </h3>
          {isMultiLeg && (
            <span className="text-[9px] font-mono text-zinc-600 mt-0.5 inline-block">
              {legCount} legs
            </span>
          )}
        </div>
        <div className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wide flex-shrink-0 ${
          isKalshi ? 'bg-sky-500/20 text-sky-400' : 'bg-violet-500/20 text-violet-400'
        }`}>
          {isKalshi ? 'KALSHI' : 'POLY'}
        </div>
      </div>

      {/* Price Display */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-zinc-800/50 rounded-md p-2.5">
          <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider mb-1">YES</div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-lg font-mono font-semibold text-emerald-400">
              {formatPrice(yesPrice)}
            </span>
            <PriceChangeIndicator change={market.price_change} />
          </div>
          {hasPrice && (
            <div className="text-[10px] font-mono text-emerald-400/50 mt-0.5">
              {impliedPct}% implied
            </div>
          )}
        </div>
        <div className="bg-zinc-800/50 rounded-md p-2.5">
          <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider mb-1">NO</div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-lg font-mono font-semibold text-red-400">
              {formatPrice(noPrice)}
            </span>
          </div>
          {noPrice !== null && noPrice > 0 && noPrice < 100 && (
            <div className="text-[10px] font-mono text-red-400/50 mt-0.5">
              {noPrice.toFixed(0)}% implied
            </div>
          )}
        </div>
      </div>

      {/* Metrics Row */}
      <div className="flex items-center gap-3 text-[11px]">
        {/* Volume */}
        <div className="flex items-center gap-1">
          <svg className="w-3.5 h-3.5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="font-mono text-zinc-400">{formatVolume(market.volume)}</span>
        </div>

        {/* Spread */}
        {spread !== null && spread > 0 && (
          <div className="flex items-center gap-1">
            <span className="text-zinc-600">Spread:</span>
            <span className={`font-mono ${spread <= 3 ? 'text-emerald-400' : spread <= 6 ? 'text-amber-400' : 'text-red-400'}`}>
              {spread}\u00A2
            </span>
          </div>
        )}

        {/* Open Interest */}
        {market.open_interest !== null && market.open_interest > 0 && (
          <div className="flex items-center gap-1">
            <span className="text-zinc-600">OI:</span>
            <span className="font-mono text-zinc-400">{market.open_interest.toLocaleString()}</span>
          </div>
        )}

        {/* Time until expiry — only show if we have real data */}
        {expiryStr && (
          <div className="flex items-center gap-1 ml-auto">
            <svg className="w-3.5 h-3.5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-mono text-zinc-500">{expiryStr}</span>
          </div>
        )}
      </div>

      {/* Game Link — prominent button when matched */}
      {market.mapped_game_id && (
        <div className="mt-3 pt-3 border-t border-zinc-800/60">
          <Link
            href={`/edge/portal/sports/game/${market.mapped_game_id}`}
            className="flex items-center justify-center gap-2 w-full px-3 py-2 rounded-md bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:text-cyan-300 transition-all text-[11px] font-medium"
          >
            View Game Analysis
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, subValue, icon, color = 'emerald' }: {
  label: string;
  value: string | number;
  subValue?: string;
  icon: JSX.Element;
  color?: 'emerald' | 'sky' | 'violet' | 'amber';
}) {
  const colorClasses = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    sky: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    violet: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  };

  return (
    <div className={`rounded-lg p-3 border ${colorClasses[color]}`}>
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-[10px] font-mono uppercase tracking-wider opacity-70">{label}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-xl font-mono font-bold">{value}</span>
        {subValue && <span className="text-xs font-mono opacity-60">{subValue}</span>}
      </div>
    </div>
  );
}

export function ExchangesGrid() {
  const [markets, setMarkets] = useState<ExchangeMarket[]>([]);
  const [stats, setStats] = useState<ExchangeStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exchange, setExchange] = useState<Exchange>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        params.set('limit', '50');
        if (exchange !== 'all') params.set('exchange', exchange);

        const res = await fetch(`/api/exchanges?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch exchange data');

        const data = await res.json();
        setMarkets(data.markets || []);
        setStats(data.stats || null);
      } catch (e: any) {
        setError(e.message || 'Failed to load');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [exchange]);

  // Filter by search query
  const filteredMarkets = useMemo(() => {
    if (!searchQuery.trim()) return markets;
    const q = searchQuery.toLowerCase();
    return markets.filter(m =>
      m.event_title.toLowerCase().includes(q) ||
      (m.contract_ticker || '').toLowerCase().includes(q)
    );
  }, [markets, searchQuery]);

  const exchanges: Exchange[] = ['all', 'kalshi', 'polymarket'];

  return (
    <div className="space-y-4">
      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard
            label="Sports Markets"
            value={stats.total}
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>}
            color="emerald"
          />
          <StatCard
            label="Kalshi"
            value={stats.kalshi}
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
            color="sky"
          />
          <StatCard
            label="Polymarket"
            value={stats.polymarket}
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="violet"
          />
          <StatCard
            label="Total Volume"
            value={formatVolume(stats.totalVolume)}
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="amber"
          />
        </div>
      )}

      {/* Filters Row */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-2">
          <div className="flex bg-zinc-800/50 rounded-md p-0.5">
            {exchanges.map((ex) => (
              <button
                key={ex}
                onClick={() => setExchange(ex)}
                className={`px-3 py-1 rounded text-[11px] font-medium transition-all ${
                  exchange === ex
                    ? `${EXCHANGE_CONFIG[ex].bgColor} ${EXCHANGE_CONFIG[ex].color}`
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {EXCHANGE_CONFIG[ex].label}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <svg className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search markets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-48 pl-8 pr-3 py-1.5 bg-zinc-800/50 border border-zinc-700/50 rounded-md text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-emerald-500/50"
            />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
            <span className="text-xs font-mono text-zinc-600 uppercase tracking-wider">Loading markets...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-center">
          <span className="text-sm text-red-400">{error}</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && filteredMarkets.length === 0 && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-8 text-center">
          <div className="text-zinc-600 mb-2">
            <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          </div>
          <p className="text-sm text-zinc-500 mb-1">No sports markets found</p>
          <p className="text-xs text-zinc-600">Exchange data syncs every 15 minutes with odds updates</p>
        </div>
      )}

      {/* Markets Grid */}
      {!loading && !error && filteredMarkets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredMarkets.map((market) => (
            <MarketCard key={`${market.exchange}-${market.event_id}`} market={market} />
          ))}
        </div>
      )}
    </div>
  );
}
