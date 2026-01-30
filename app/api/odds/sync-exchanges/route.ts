import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

const CRON_SECRET = process.env.CRON_SECRET || "";

// Kalshi API (public, no auth needed for market data)
const KALSHI_API_BASE = "https://api.elections.kalshi.com/trade-api/v2";

// Polymarket Gamma API
const POLYMARKET_API_BASE = "https://gamma-api.polymarket.com";

// Category mapping for Kalshi series
const KALSHI_CATEGORY_MAP: Record<string, string> = {
  "sports": "sports",
  "politics": "politics",
  "economics": "economics",
  "finance": "economics",
  "crypto": "crypto",
  "tech": "crypto",
  "entertainment": "entertainment",
  "culture": "entertainment",
};

// Use direct Supabase client
function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// ============================================================================
// KALSHI API
// ============================================================================

interface KalshiMarket {
  ticker: string;
  title: string;
  category: string;
  yes_bid: number;
  yes_ask: number;
  no_bid: number;
  no_ask: number;
  last_price: number;
  volume: number;
  open_interest: number;
  close_time: string;
}

async function fetchKalshiMarkets(): Promise<KalshiMarket[]> {
  try {
    // Fetch active markets
    const url = `${KALSHI_API_BASE}/markets?status=active&limit=500`;
    const res = await fetch(url, {
      headers: {
        "Accept": "application/json",
      },
    });

    if (!res.ok) {
      console.error(`[Exchange Sync] Kalshi API error: ${res.status}`);
      return [];
    }

    const data = await res.json();
    return data.markets || [];
  } catch (e: any) {
    console.error("[Exchange Sync] Kalshi fetch error:", e?.message);
    return [];
  }
}

async function fetchKalshiOrderBook(ticker: string): Promise<{ yes_bid: number; yes_ask: number; no_bid: number; no_ask: number; depth: any } | null> {
  try {
    const url = `${KALSHI_API_BASE}/markets/${ticker}/orderbook`;
    const res = await fetch(url);

    if (!res.ok) return null;

    const data = await res.json();
    const orderbook = data.orderbook;

    // Extract best bid/ask from order book
    const yesBids = orderbook?.yes?.bids || [];
    const yesAsks = orderbook?.yes?.asks || [];
    const noBids = orderbook?.no?.bids || [];
    const noAsks = orderbook?.no?.asks || [];

    return {
      yes_bid: yesBids[0]?.[0] || 0,
      yes_ask: yesAsks[0]?.[0] || 0,
      no_bid: noBids[0]?.[0] || 0,
      no_ask: noAsks[0]?.[0] || 0,
      depth: {
        yes: { bids: yesBids.slice(0, 5), asks: yesAsks.slice(0, 5) },
        no: { bids: noBids.slice(0, 5), asks: noAsks.slice(0, 5) },
      },
    };
  } catch (e) {
    return null;
  }
}

// ============================================================================
// POLYMARKET API
// ============================================================================

interface PolymarketMarket {
  id: string;
  question: string;
  category: string;
  outcomePrices: string; // JSON string of outcome prices
  volume: string;
  liquidityClob: string;
  endDate: string;
}

async function fetchPolymarketMarkets(): Promise<PolymarketMarket[]> {
  try {
    // Fetch active markets
    const url = `${POLYMARKET_API_BASE}/markets?active=true&limit=500`;
    const res = await fetch(url, {
      headers: {
        "Accept": "application/json",
      },
    });

    if (!res.ok) {
      console.error(`[Exchange Sync] Polymarket API error: ${res.status}`);
      return [];
    }

    const data = await res.json();
    return data || [];
  } catch (e: any) {
    console.error("[Exchange Sync] Polymarket fetch error:", e?.message);
    return [];
  }
}

// ============================================================================
// MAIN SYNC LOGIC
// ============================================================================

async function runSync() {
  const supabase = getSupabase();
  const snapshotTime = new Date().toISOString();
  const rows: any[] = [];
  let kalshiCount = 0;
  let polymarketCount = 0;

  // Fetch Kalshi markets
  console.log("[Exchange Sync] Fetching Kalshi markets...");
  const kalshiMarkets = await fetchKalshiMarkets();

  for (const market of kalshiMarkets) {
    // Determine category
    const category = KALSHI_CATEGORY_MAP[market.category?.toLowerCase()] || "other";

    // Try to match sports markets to our games (basic matching by title)
    let sport: string | null = null;
    let gameId: string | null = null;

    const titleLower = market.title.toLowerCase();
    if (titleLower.includes("nfl") || titleLower.includes("football")) {
      sport = "americanfootball_nfl";
    } else if (titleLower.includes("nba") || titleLower.includes("basketball")) {
      sport = "basketball_nba";
    } else if (titleLower.includes("mlb") || titleLower.includes("baseball")) {
      sport = "baseball_mlb";
    } else if (titleLower.includes("nhl") || titleLower.includes("hockey")) {
      sport = "icehockey_nhl";
    }

    // Fetch order book for liquidity depth (only for high-volume markets to conserve API calls)
    let orderBook = null;
    if (market.volume > 1000) {
      orderBook = await fetchKalshiOrderBook(market.ticker);
    }

    rows.push({
      exchange: "kalshi",
      market_id: market.ticker,
      market_title: market.title,
      category: sport ? "sports" : category,
      sport,
      game_id: gameId,
      yes_price: market.last_price,
      no_price: market.last_price ? 100 - market.last_price : null,
      yes_bid: orderBook?.yes_bid || market.yes_bid || null,
      yes_ask: orderBook?.yes_ask || market.yes_ask || null,
      no_bid: orderBook?.no_bid || market.no_bid || null,
      no_ask: orderBook?.no_ask || market.no_ask || null,
      spread: orderBook ? Math.abs((orderBook.yes_ask || 0) - (orderBook.yes_bid || 0)) : null,
      volume_24h: market.volume,
      open_interest: market.open_interest,
      liquidity_depth: orderBook?.depth || null,
      snapshot_time: snapshotTime,
      expires_at: market.close_time,
      metadata: { source: "kalshi_v2" },
    });

    kalshiCount++;
  }

  // Fetch Polymarket markets
  console.log("[Exchange Sync] Fetching Polymarket markets...");
  const polymarkets = await fetchPolymarketMarkets();

  for (const market of polymarkets) {
    // Parse outcome prices
    let prices: number[] = [];
    try {
      prices = JSON.parse(market.outcomePrices || "[]");
    } catch (e) {
      // Skip invalid price data
      continue;
    }

    if (prices.length < 2) continue;

    // Determine category
    const categoryLower = (market.category || "").toLowerCase();
    const category = KALSHI_CATEGORY_MAP[categoryLower] || "other";

    // Try to match sports markets
    let sport: string | null = null;
    const questionLower = market.question.toLowerCase();
    if (questionLower.includes("nfl") || questionLower.includes("football")) {
      sport = "americanfootball_nfl";
    } else if (questionLower.includes("nba") || questionLower.includes("basketball")) {
      sport = "basketball_nba";
    } else if (questionLower.includes("mlb") || questionLower.includes("baseball")) {
      sport = "baseball_mlb";
    }

    const yesPrice = Math.round(prices[0] * 100);
    const noPrice = Math.round(prices[1] * 100);

    rows.push({
      exchange: "polymarket",
      market_id: market.id,
      market_title: market.question,
      category: sport ? "sports" : category,
      sport,
      game_id: null,
      yes_price: yesPrice,
      no_price: noPrice,
      yes_bid: null, // Polymarket doesn't expose order book easily
      yes_ask: null,
      no_bid: null,
      no_ask: null,
      spread: null,
      volume_24h: parseFloat(market.volume) || null,
      open_interest: null,
      liquidity_depth: null,
      snapshot_time: snapshotTime,
      expires_at: market.endDate,
      metadata: { source: "polymarket_gamma" },
    });

    polymarketCount++;
  }

  // Insert to Supabase
  if (rows.length > 0) {
    // Batch insert in chunks
    for (let i = 0; i < rows.length; i += 500) {
      const chunk = rows.slice(i, i + 500);
      const { error } = await supabase.from("exchange_snapshots").insert(chunk);
      if (error) {
        console.error("[Exchange Sync] Insert error:", error.message);
      }
    }
  }

  console.log(`[Exchange Sync] Done: Kalshi ${kalshiCount}, Polymarket ${polymarketCount}`);

  return NextResponse.json({
    synced: rows.length,
    kalshi: kalshiCount,
    polymarket: polymarketCount,
    snapshot_time: snapshotTime,
  });
}

// Vercel cron max duration
export const maxDuration = 120;

// GET handler for cron
export async function GET(request: Request) {
  try {
    const authHeader = request.headers.get("authorization") || "";
    const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";
    if (!CRON_SECRET || token !== CRON_SECRET) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    return await runSync();
  } catch (error: any) {
    console.error("[Exchange Sync] Fatal error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error", message: error?.message },
      { status: 500 }
    );
  }
}

// POST handler for manual sync
export async function POST(request: Request) {
  try {
    const authHeader = request.headers.get("x-cron-secret");
    if (!CRON_SECRET || authHeader !== CRON_SECRET) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    return await runSync();
  } catch (error) {
    console.error("[Exchange Sync] Fatal error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
