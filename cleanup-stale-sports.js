// Cleanup stale sports from database - Run with: node cleanup-stale-sports.js
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Load .env.local manually
const envFile = fs.readFileSync('.env.local', 'utf8');
envFile.split('\n').forEach(line => {
  const [key, ...vals] = line.split('=');
  if (key && vals.length) {
    process.env[key.trim()] = vals.join('=').trim();
  }
});

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

// Active sports - DO NOT DELETE these
const ACTIVE_SPORTS = [
  'americanfootball_nfl',
  'americanfootball_ncaaf',
  'basketball_nba',
  'basketball_ncaab',
  'icehockey_nhl',
  'soccer_epl',
  'tennis_atp_australian_open',
  'tennis_atp_french_open',
  'tennis_atp_us_open',
  'tennis_atp_wimbledon',
];

// Active sports in UPPERCASE format (used by line_snapshots table)
// Based on actual values found in the table
const ACTIVE_SPORTS_UPPER = [
  'NFL',
  'NCAAF',
  'NBA',
  'NCAAB',
  'NHL',
  'EPL',
];

async function cleanupCachedOdds() {
  console.log('\n=== CACHED_ODDS CLEANUP ===\n');

  // First, get count of rows to delete
  const { data: toDelete, error: countError } = await supabase
    .from('cached_odds')
    .select('sport_key')
    .not('sport_key', 'in', `(${ACTIVE_SPORTS.join(',')})`);

  if (countError) {
    console.log('Error counting:', countError.message);
    return 0;
  }

  const deleteCount = toDelete?.length || 0;
  console.log(`Found ${deleteCount} rows to delete`);

  if (deleteCount === 0) {
    console.log('Nothing to delete');
    return 0;
  }

  // Show what will be deleted
  const sportCounts = {};
  for (const row of toDelete) {
    sportCounts[row.sport_key] = (sportCounts[row.sport_key] || 0) + 1;
  }
  console.log('Sports to delete:');
  for (const [sport, count] of Object.entries(sportCounts)) {
    console.log(`  - ${sport}: ${count} rows`);
  }

  // Delete the rows
  const { error: deleteError } = await supabase
    .from('cached_odds')
    .delete()
    .not('sport_key', 'in', `(${ACTIVE_SPORTS.join(',')})`);

  if (deleteError) {
    console.log('Delete error:', deleteError.message);
    return 0;
  }

  console.log(`\n✓ Deleted ${deleteCount} rows from cached_odds`);
  return deleteCount;
}

async function cleanupOddsSnapshots() {
  console.log('\n=== ODDS_SNAPSHOTS CLEANUP ===\n');

  // Delete in batches to avoid timeout
  let totalDeleted = 0;
  let batchNum = 0;

  while (true) {
    batchNum++;
    console.log(`Batch ${batchNum}: Fetching rows to delete...`);

    // Get a batch of IDs to delete
    const { data: toDelete, error: selectError } = await supabase
      .from('odds_snapshots')
      .select('id, sport_key')
      .not('sport_key', 'in', `(${ACTIVE_SPORTS.join(',')})`)
      .limit(1000);

    if (selectError) {
      console.log('Select error:', selectError.message);
      break;
    }

    if (!toDelete || toDelete.length === 0) {
      console.log('No more rows to delete');
      break;
    }

    const ids = toDelete.map(r => r.id);
    console.log(`  Found ${ids.length} rows to delete`);

    // Delete by IDs
    const { error: deleteError } = await supabase
      .from('odds_snapshots')
      .delete()
      .in('id', ids);

    if (deleteError) {
      console.log('Delete error:', deleteError.message);
      break;
    }

    totalDeleted += ids.length;
    console.log(`  Deleted batch. Total so far: ${totalDeleted}`);

    // Safety limit
    if (batchNum > 100) {
      console.log('Safety limit reached (100 batches)');
      break;
    }
  }

  console.log(`\n✓ Deleted ${totalDeleted} rows from odds_snapshots`);
  return totalDeleted;
}

async function cleanupLineSnapshots() {
  console.log('\n=== LINE_SNAPSHOTS CLEANUP ===\n');
  console.log('Note: line_snapshots uses UPPERCASE sport keys (NFL, NBA, etc.)');
  console.log('Keeping:', ACTIVE_SPORTS_UPPER.join(', '));

  // First, get list of all sport_keys that are NOT in active list
  const { data: allSports, error: listError } = await supabase
    .from('line_snapshots')
    .select('sport_key')
    .limit(10000);

  if (listError) {
    console.log('Error listing sports:', listError.message);
    return 0;
  }

  const uniqueSports = [...new Set(allSports.map(r => r.sport_key))];
  const sportsToDelete = uniqueSports.filter(s => !ACTIVE_SPORTS_UPPER.includes(s));

  console.log('Sports to delete:', sportsToDelete.join(', '));

  if (sportsToDelete.length === 0) {
    console.log('No stale sports found');
    return 0;
  }

  // Delete each stale sport one at a time
  let totalDeleted = 0;
  for (const sport of sportsToDelete) {
    console.log(`Deleting sport: ${sport}...`);

    const { data: deleted, error: deleteError } = await supabase
      .from('line_snapshots')
      .delete()
      .eq('sport_key', sport)
      .select('id');

    if (deleteError) {
      console.log(`  Delete error for ${sport}:`, deleteError.message);
      continue;
    }

    const count = deleted?.length || 0;
    totalDeleted += count;
    console.log(`  Deleted ${count} rows for ${sport}`);
  }

  console.log(`\n✓ Deleted ${totalDeleted} rows from line_snapshots`);
  return totalDeleted;
}

async function main() {
  console.log('='.repeat(50));
  console.log('STALE SPORTS CLEANUP');
  console.log('='.repeat(50));
  console.log('\nActive sports (will NOT be deleted):');
  ACTIVE_SPORTS.forEach(s => console.log(`  ✓ ${s}`));

  const cachedOddsDeleted = await cleanupCachedOdds();
  const oddsSnapshotsDeleted = await cleanupOddsSnapshots();
  const lineSnapshotsDeleted = await cleanupLineSnapshots();

  console.log('\n' + '='.repeat(50));
  console.log('CLEANUP SUMMARY');
  console.log('='.repeat(50));
  console.log(`cached_odds:     ${cachedOddsDeleted} rows deleted`);
  console.log(`odds_snapshots:  ${oddsSnapshotsDeleted} rows deleted`);
  console.log(`line_snapshots:  ${lineSnapshotsDeleted} rows deleted`);
  console.log(`TOTAL:           ${cachedOddsDeleted + oddsSnapshotsDeleted + lineSnapshotsDeleted} rows deleted`);
  console.log('='.repeat(50) + '\n');
}

main().catch(console.error);
