'use client';

import { useState, useEffect, useMemo } from 'react';

interface ExchangeMarket {
  id: string;
  exchange: 'kalshi' | 'polymarket';
  market_id: string;
  market_title: string;
  category: string;
  sport: string | null;
  yes_price: number | null;
  no_price: number | null;
  yes_bid: number | null;
  yes_ask: number | null;
  no_bid: number | null;
  no_ask: number | null;
  spread: number | null;
  volume_24h: number | null;
  open_interest: number | null;
  liquidity_depth: any;
  snapshot_time: string;
  expires_at: string | null;
}

interface ExchangeStats {
  total: number;
  kalshi: number;
  polymarket: number;
  totalVolume: number;
  categories: Record<string, number>;
}

type Category = 'all' | 'sports' | 'politics' | 'economics' | 'crypto' | 'entertainment' | 'other';
type Exchange = 'all' | 'kalshi' | 'polymarket';

const CATEGORY_CONFIG: Record<Category, { label: string; icon: JSX.Element; color: string }> = {
  all: {
    label: 'All Markets',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
      </svg>
    ),
    color: 'zinc',
  },
  sports: {
    label: 'Sports',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" strokeWidth="1.5" />
        <path strokeLinecap="round" strokeWidth="1.5" d="M12 2c-2.5 3-4 6.5-4 10s1.5 7 4 10M12 2c2.5 3 4 6.5 4 10s-1.5 7-4 10M2 12h20" />
      </svg>
    ),
    color: 'emerald',
  },
  politics: {
    label: 'Politics',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
    color: 'blue',
  },
  economics: {
    label: 'Economics',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    color: 'amber',
  },
  crypto: {
    label: 'Crypto',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'purple',
  },
  entertainment: {
    label: 'Entertainment',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
      </svg>
    ),
    color: 'pink',
  },
  other: {
    label: 'Other',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
      </svg>
    ),
    color: 'zinc',
  },
};

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
  return `${price}¢`;
}

function formatSpread(spread: number | null): string {
  if (spread === null || spread === undefined) return '-';
  return `${spread}¢`;
}

function formatTimeUntil(dateStr: string | null): string {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
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

function OrderBookMini({ depth }: { depth: any }) {
  if (!depth?.yes) return null;

  const yesBids = depth.yes.bids?.slice(0, 3) || [];
  const yesAsks = depth.yes.asks?.slice(0, 3) || [];

  const maxSize = Math.max(
    ...yesBids.map((b: number[]) => b[1] || 0),
    ...yesAsks.map((a: number[]) => a[1] || 0),
    1
  );

  return (
    <div className="flex gap-1 h-6">
      {/* Bids */}
      <div className="flex gap-0.5 items-end">
        {yesBids.map((bid: number[], i: number) => (
          <div
            key={`bid-${i}`}
            className="w-1.5 bg-emerald-500/60 rounded-t-sm"
            style={{ height: `${Math.max(20, (bid[1] / maxSize) * 100)}%` }}
            title={`Bid: ${bid[0]}¢ × ${bid[1]}`}
          />
        ))}
      </div>
      <div className="w-px bg-zinc-700" />
      {/* Asks */}
      <div className="flex gap-0.5 items-end">
        {yesAsks.map((ask: number[], i: number) => (
          <div
            key={`ask-${i}`}
            className="w-1.5 bg-red-500/60 rounded-t-sm"
            style={{ height: `${Math.max(20, (ask[1] / maxSize) * 100)}%` }}
            title={`Ask: ${ask[0]}¢ × ${ask[1]}`}
          />
        ))}
      </div>
    </div>
  );
}

function MarketCard({ market }: { market: ExchangeMarket }) {
  const isKalshi = market.exchange === 'kalshi';
  const hasSpread = market.spread !== null && market.spread > 0;
  const hasDepth = market.liquidity_depth?.yes;

  // Determine implied probability edge
  const yesPrice = market.yes_price || 0;
  const hasPricing = yesPrice > 0 && yesPrice < 100;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 hover:border-zinc-700 transition-all group">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-[13px] font-medium text-zinc-100 leading-tight line-clamp-2 group-hover:text-white transition-colors">
            {market.market_title}
          </h3>
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
              {formatPrice(market.yes_price)}
            </span>
            {market.yes_bid !== null && market.yes_ask !== null && (
              <span className="text-[10px] font-mono text-zinc-600">
                {market.yes_bid}/{market.yes_ask}
              </span>
            )}
          </div>
        </div>
        <div className="bg-zinc-800/50 rounded-md p-2.5">
          <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider mb-1">NO</div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-lg font-mono font-semibold text-red-400">
              {formatPrice(market.no_price)}
            </span>
            {market.no_bid !== null && market.no_ask !== null && (
              <span className="text-[10px] font-mono text-zinc-600">
                {market.no_bid}/{market.no_ask}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="flex items-center gap-3 text-[11px]">
        {/* Volume */}
        <div className="flex items-center gap-1">
          <svg className="w-3.5 h-3.5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="font-mono text-zinc-400">{formatVolume(market.volume_24h)}</span>
        </div>

        {/* Spread */}
        {hasSpread && (
          <div className="flex items-center gap-1">
            <span className="text-zinc-600">Spread:</span>
            <span className={`font-mono ${market.spread! <= 3 ? 'text-emerald-400' : market.spread! <= 6 ? 'text-amber-400' : 'text-red-400'}`}>
              {formatSpread(market.spread)}
            </span>
          </div>
        )}

        {/* Open Interest */}
        {market.open_interest !== null && (
          <div className="flex items-center gap-1">
            <span className="text-zinc-600">OI:</span>
            <span className="font-mono text-zinc-400">{market.open_interest.toLocaleString()}</span>
          </div>
        )}

        {/* Time until expiry */}
        <div className="flex items-center gap-1 ml-auto">
          <svg className="w-3.5 h-3.5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-mono text-zinc-500">{formatTimeUntil(market.expires_at)}</span>
        </div>
      </div>

      {/* Order Book Mini-Visualization */}
      {hasDepth && (
        <div className="mt-3 pt-3 border-t border-zinc-800/60">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-wider">Depth</span>
            <OrderBookMini depth={market.liquidity_depth} />
          </div>
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
  const [snapshotTime, setSnapshotTime] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState<Category>('all');
  const [exchange, setExchange] = useState<Exchange>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (category !== 'all') params.set('category', category);
        if (exchange !== 'all') params.set('exchange', exchange);

        const res = await fetch(`/api/exchanges?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch exchange data');

        const data = await res.json();
        setMarkets(data.markets || []);
        setStats(data.stats || null);
        setSnapshotTime(data.snapshot_time);
      } catch (e: any) {
        setError(e.message || 'Failed to load');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [category, exchange]);

  // Filter by search query
  const filteredMarkets = useMemo(() => {
    if (!searchQuery.trim()) return markets;
    const q = searchQuery.toLowerCase();
    return markets.filter(m =>
      m.market_title.toLowerCase().includes(q) ||
      m.market_id.toLowerCase().includes(q)
    );
  }, [markets, searchQuery]);

  const categories: Category[] = ['all', 'sports', 'politics', 'economics', 'crypto', 'entertainment', 'other'];
  const exchanges: Exchange[] = ['all', 'kalshi', 'polymarket'];

  return (
    <div className="space-y-4">
      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard
            label="Total Markets"
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
            label="24h Volume"
            value={formatVolume(stats.totalVolume)}
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="amber"
          />
        </div>
      )}

      {/* Filters Row */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Category Pills */}
        <div className="flex flex-wrap gap-1.5">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-3 py-1.5 rounded-md text-[11px] font-medium transition-all flex items-center gap-1.5 ${
                category === cat
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 border border-transparent'
              }`}
            >
              {CATEGORY_CONFIG[cat].icon}
              {CATEGORY_CONFIG[cat].label}
              {stats?.categories[cat] && cat !== 'all' && (
                <span className="text-[9px] font-mono opacity-60">({stats.categories[cat]})</span>
              )}
            </button>
          ))}
        </div>

        {/* Exchange Toggle + Search */}
        <div className="flex gap-2 sm:ml-auto">
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

      {/* Last Updated */}
      {snapshotTime && (
        <div className="flex items-center gap-2 text-[11px] text-zinc-600">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>Last sync: {new Date(snapshotTime).toLocaleString()}</span>
        </div>
      )}

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
          <p className="text-sm text-zinc-500 mb-1">No markets found</p>
          <p className="text-xs text-zinc-600">Try adjusting your filters or run the exchange sync</p>
        </div>
      )}

      {/* Markets Grid */}
      {!loading && !error && filteredMarkets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredMarkets.map((market) => (
            <MarketCard key={`${market.exchange}-${market.market_id}`} market={market} />
          ))}
        </div>
      )}
    </div>
  );
}
