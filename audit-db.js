// Database audit script - Run with: node audit-db.js
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

// Expected active sports (should match sync route)
const EXPECTED_ACTIVE = [
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

async function auditCachedOdds() {
  console.log('\n========================================');
  console.log('CACHED_ODDS TABLE');
  console.log('========================================\n');

  const { data, error } = await supabase
    .from('cached_odds')
    .select('sport_key, updated_at');

  if (error) {
    console.log('Error:', error.message);
    return;
  }

  const stats = {};
  for (const row of data) {
    if (!stats[row.sport_key]) {
      stats[row.sport_key] = { count: 0, latest: null };
    }
    stats[row.sport_key].count++;
    if (!stats[row.sport_key].latest || row.updated_at > stats[row.sport_key].latest) {
      stats[row.sport_key].latest = row.updated_at;
    }
  }

  const sorted = Object.entries(stats).sort((a, b) => b[1].count - a[1].count);

  for (const [key, val] of sorted) {
    const isExpected = EXPECTED_ACTIVE.includes(key);
    const flag = isExpected ? '✓' : '⚠️ UNEXPECTED';
    console.log(`${flag} ${key}: ${val.count} rows, latest: ${val.latest}`);
  }

  console.log(`\nTotal: ${data.length} rows across ${Object.keys(stats).length} sports`);

  // Flag unexpected
  const unexpected = Object.keys(stats).filter(k => !EXPECTED_ACTIVE.includes(k));
  if (unexpected.length > 0) {
    console.log('\n⚠️  UNEXPECTED SPORTS IN DATABASE:');
    unexpected.forEach(k => console.log(`   - ${k}`));
  }
}

async function auditOddsSnapshots() {
  console.log('\n========================================');
  console.log('ODDS_SNAPSHOTS TABLE');
  console.log('========================================\n');

  const { data, error } = await supabase
    .from('odds_snapshots')
    .select('sport_key, snapshot_time')
    .order('snapshot_time', { ascending: false })
    .limit(10000);

  if (error) {
    console.log('Error:', error.message);
    return;
  }

  const stats = {};
  for (const row of data) {
    if (!stats[row.sport_key]) {
      stats[row.sport_key] = { count: 0, latest: null };
    }
    stats[row.sport_key].count++;
    if (!stats[row.sport_key].latest || row.snapshot_time > stats[row.sport_key].latest) {
      stats[row.sport_key].latest = row.snapshot_time;
    }
  }

  const sorted = Object.entries(stats).sort((a, b) => b[1].count - a[1].count);

  for (const [key, val] of sorted) {
    const isExpected = EXPECTED_ACTIVE.includes(key);
    const flag = isExpected ? '✓' : '⚠️ UNEXPECTED';
    console.log(`${flag} ${key}: ${val.count} rows (last 10k), latest: ${val.latest}`);
  }

  const unexpected = Object.keys(stats).filter(k => !EXPECTED_ACTIVE.includes(k));
  if (unexpected.length > 0) {
    console.log('\n⚠️  UNEXPECTED SPORTS IN SNAPSHOTS:');
    unexpected.forEach(k => console.log(`   - ${k}`));
  }
}

async function auditLineSnapshots() {
  console.log('\n========================================');
  console.log('LINE_SNAPSHOTS TABLE');
  console.log('========================================\n');

  const { data, error } = await supabase
    .from('line_snapshots')
    .select('sport_key, snapshot_time')
    .order('snapshot_time', { ascending: false })
    .limit(10000);

  if (error) {
    console.log('Error:', error.message);
    if (error.message.includes('does not exist')) {
      console.log('(Table does not exist - skipping)');
    }
    return;
  }

  if (!data || data.length === 0) {
    console.log('No data in table');
    return;
  }

  const stats = {};
  for (const row of data) {
    if (!stats[row.sport_key]) {
      stats[row.sport_key] = { count: 0, latest: null };
    }
    stats[row.sport_key].count++;
    if (!stats[row.sport_key].latest || row.snapshot_time > stats[row.sport_key].latest) {
      stats[row.sport_key].latest = row.snapshot_time;
    }
  }

  const sorted = Object.entries(stats).sort((a, b) => b[1].count - a[1].count);

  for (const [key, val] of sorted) {
    const isExpected = EXPECTED_ACTIVE.includes(key);
    const flag = isExpected ? '✓' : '⚠️ UNEXPECTED';
    console.log(`${flag} ${key}: ${val.count} rows (last 10k), latest: ${val.latest}`);
  }
}

async function main() {
  console.log('='.repeat(50));
  console.log('ODDS API DATABASE AUDIT');
  console.log('='.repeat(50));
  console.log('\nExpected active sports:');
  EXPECTED_ACTIVE.forEach(s => console.log(`  - ${s}`));

  await auditCachedOdds();
  await auditOddsSnapshots();
  await auditLineSnapshots();

  console.log('\n' + '='.repeat(50));
  console.log('AUDIT COMPLETE');
  console.log('='.repeat(50) + '\n');
}

main().catch(console.error);
