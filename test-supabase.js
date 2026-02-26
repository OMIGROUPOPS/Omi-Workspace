const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log('Supabase URL:', url);
console.log('Anon Key:', key ? key.substring(0, 20) + '...[REDACTED]' : 'NOT SET');

if (!url || !key) {
  console.log('ERROR: Missing environment variables');
  process.exit(1);
}

const supabase = createClient(url, key);

async function test() {
  const start = Date.now();
  try {
    const { data, error, count } = await supabase
      .from('cached_odds')
      .select('*', { count: 'exact', head: true });

    const elapsed = Date.now() - start;

    if (error) {
      console.log('ERROR:', error.message);
      console.log('Code:', error.code);
    } else {
      console.log('SUCCESS - Row count:', count);
      console.log('Response time:', elapsed + 'ms');
    }
  } catch (e) {
    console.log('EXCEPTION:', e.message);
  }
}

test();
