// Quick script to check odds_snapshots table
// Run with: npx ts-node scripts/check-snapshots.ts

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

async function checkSnapshots() {
  const supabase = createClient(supabaseUrl, supabaseKey);

  // Count total snapshots
  const { count, error: countError } = await supabase
    .from('odds_snapshots')
    .select('*', { count: 'exact', head: true });

  console.log('\n=== ODDS_SNAPSHOTS TABLE ===');
  console.log('Total rows:', count ?? 'Error: ' + countError?.message);

  // Get recent snapshots
  const { data: recent, error: recentError } = await supabase
    .from('odds_snapshots')
    .select('game_id, sport_key, market, book_key, snapshot_time')
    .order('snapshot_time', { ascending: false })
    .limit(10);

  if (recentError) {
    console.log('Error fetching recent:', recentError.message);
  } else {
    console.log('\nRecent snapshots (last 10):');
    if (recent && recent.length > 0) {
      recent.forEach((row, i) => {
        console.log(`  ${i + 1}. ${row.game_id} | ${row.sport_key} | ${row.market} | ${row.book_key} | ${row.snapshot_time}`);
      });
    } else {
      console.log('  (none)');
    }
  }

  // Check distinct game IDs
  const { data: games, error: gamesError } = await supabase
    .from('odds_snapshots')
    .select('game_id')
    .limit(1000);

  if (!gamesError && games) {
    const uniqueGames = new Set(games.map(g => g.game_id));
    console.log('\nDistinct games with snapshots:', uniqueGames.size);
  }

  // Check if cached_odds has games
  const { count: cachedCount } = await supabase
    .from('cached_odds')
    .select('*', { count: 'exact', head: true });

  console.log('\n=== CACHED_ODDS TABLE ===');
  console.log('Total rows:', cachedCount);
}

checkSnapshots().catch(console.error);
