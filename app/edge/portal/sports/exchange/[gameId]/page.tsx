import { createClient } from '@supabase/supabase-js';
import Link from 'next/link';
import { ExchangeGameClient } from './ExchangeGameClient';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { global: { fetch: (url, options) => fetch(url, { ...options, cache: 'no-store' }) } }
  );
}

// Fetch latest composite_history for fair lines
async function fetchFairLines(gameId: string) {
  const supabase = getSupabase();
  const { data } = await supabase
    .from('composite_history')
    .select('fair_spread, fair_total, fair_ml_home, fair_ml_away')
    .eq('game_id', gameId)
    .order('timestamp', { ascending: false })
    .limit(1)
    .single();
  return data;
}

// Fetch all exchange snapshots for probability chart
async function fetchExchangeHistory(gameId: string, platform: string) {
  const supabase = getSupabase();
  const { data } = await supabase
    .from('exchange_data')
    .select('exchange, market_type, yes_price, no_price, subtitle, event_title, snapshot_time')
    .eq('mapped_game_id', gameId)
    .eq('exchange', platform)
    .order('snapshot_time', { ascending: true })
    .limit(2000);
  return data || [];
}

// Fetch latest contracts (deduped)
async function fetchLatestContracts(gameId: string) {
  const supabase = getSupabase();
  const { data } = await supabase
    .from('exchange_data')
    .select('exchange, market_type, yes_price, no_price, subtitle, event_title, mapped_game_id, snapshot_time')
    .eq('mapped_game_id', gameId)
    .order('snapshot_time', { ascending: false })
    .limit(500);
  return data || [];
}

// Fetch game info from cached_odds
async function fetchGameInfo(gameId: string) {
  const supabase = getSupabase();
  const { data } = await supabase
    .from('cached_odds')
    .select('sport_key, game_data')
    .eq('game_id', gameId)
    .single();
  return data;
}

export default async function ExchangeGamePage({
  params,
  searchParams,
}: {
  params: Promise<{ gameId: string }>;
  searchParams: Promise<{ sport?: string; platform?: string }>;
}) {
  const { gameId } = await params;
  const { sport, platform = 'kalshi' } = await searchParams;

  const [gameInfo, fairLines, history, latestContracts] = await Promise.all([
    fetchGameInfo(gameId),
    fetchFairLines(gameId),
    fetchExchangeHistory(gameId, platform),
    fetchLatestContracts(gameId),
  ]);

  const gameData = gameInfo?.game_data;
  const homeTeam = gameData?.home_team || 'Home';
  const awayTeam = gameData?.away_team || 'Away';
  const commenceTime = gameData?.commence_time;
  const sportKey = sport || gameInfo?.sport_key || '';

  // Deduplicate latest contracts: keep only most recent per (exchange, market_type, subtitle)
  const seen = new Set<string>();
  const contracts = latestContracts.filter(c => {
    const key = `${c.exchange}|${c.market_type}|${c.subtitle ?? ''}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  return (
    <div className="py-4 px-4 max-w-[1200px] mx-auto">
      <div className="mb-4">
        <Link
          href="/edge/portal/sports"
          className="text-xs font-medium"
          style={{ color: '#6b7280', textDecoration: 'none' }}
        >
          &larr; Back to Markets
        </Link>
      </div>
      <ExchangeGameClient
        gameId={gameId}
        homeTeam={homeTeam}
        awayTeam={awayTeam}
        commenceTime={commenceTime}
        sportKey={sportKey}
        platform={platform}
        fairLines={fairLines}
        history={history}
        contracts={contracts}
      />
    </div>
  );
}
