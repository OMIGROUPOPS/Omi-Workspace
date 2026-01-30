import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

export interface ExchangeMarket {
  id: string;
  exchange: "kalshi" | "polymarket";
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

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get("category");
    const exchange = searchParams.get("exchange");
    const limit = parseInt(searchParams.get("limit") || "200");

    const supabase = getSupabase();

    // Get most recent snapshot time
    const { data: latestSnapshot } = await supabase
      .from("exchange_snapshots")
      .select("snapshot_time")
      .order("snapshot_time", { ascending: false })
      .limit(1)
      .single();

    if (!latestSnapshot) {
      return NextResponse.json({
        markets: [],
        snapshot_time: null,
        stats: { total: 0, kalshi: 0, polymarket: 0, categories: {} },
      });
    }

    // Build query for latest snapshot data
    let query = supabase
      .from("exchange_snapshots")
      .select("*")
      .eq("snapshot_time", latestSnapshot.snapshot_time)
      .order("volume_24h", { ascending: false, nullsFirst: false })
      .limit(limit);

    if (category && category !== "all") {
      query = query.eq("category", category);
    }

    if (exchange && exchange !== "all") {
      query = query.eq("exchange", exchange);
    }

    const { data, error } = await query;

    if (error) {
      console.error("[Exchanges API] Query error:", error.message);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    // Calculate stats
    const markets = data || [];
    const stats = {
      total: markets.length,
      kalshi: markets.filter((m) => m.exchange === "kalshi").length,
      polymarket: markets.filter((m) => m.exchange === "polymarket").length,
      totalVolume: markets.reduce((sum, m) => sum + (m.volume_24h || 0), 0),
      categories: {} as Record<string, number>,
    };

    for (const market of markets) {
      stats.categories[market.category] =
        (stats.categories[market.category] || 0) + 1;
    }

    return NextResponse.json({
      markets,
      snapshot_time: latestSnapshot.snapshot_time,
      stats,
    });
  } catch (error: any) {
    console.error("[Exchanges API] Fatal error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error", message: error?.message },
      { status: 500 }
    );
  }
}
