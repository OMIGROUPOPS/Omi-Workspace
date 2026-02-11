import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export interface ExchangeMarket {
  id: string;
  exchange: "kalshi" | "polymarket";
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

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const exchange = searchParams.get("exchange");
    const search = searchParams.get("search");
    const limit = searchParams.get("limit") || "200";

    const params = new URLSearchParams();
    if (exchange && exchange !== "all") params.set("exchange", exchange);
    if (search) params.set("search", search);
    params.set("limit", limit);

    const res = await fetch(
      `${BACKEND_URL}/api/exchange/markets?${params.toString()}`,
      { cache: "no-store" }
    );

    if (!res.ok) {
      console.error("[Exchanges API] Backend error:", res.status);
      return NextResponse.json(
        { error: `Backend returned ${res.status}` },
        { status: 502 }
      );
    }

    const data = await res.json();
    const markets: ExchangeMarket[] = data.markets || [];

    // Calculate stats from returned markets
    const stats = {
      total: markets.length,
      kalshi: markets.filter((m) => m.exchange === "kalshi").length,
      polymarket: markets.filter((m) => m.exchange === "polymarket").length,
      totalVolume: markets.reduce((sum, m) => sum + (m.volume || 0), 0),
    };

    return NextResponse.json({ markets, stats });
  } catch (error: any) {
    console.error("[Exchanges API] Fatal error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error", message: error?.message },
      { status: 500 }
    );
  }
}
