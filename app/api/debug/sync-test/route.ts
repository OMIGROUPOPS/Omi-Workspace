import { NextResponse } from "next/server";

const ODDS_API_KEY = process.env.ODDS_API_KEY || "";
const ODDS_API_BASE = "https://api.the-odds-api.com/v4";

export async function GET() {
  if (!ODDS_API_KEY) {
    return NextResponse.json({ error: "ODDS_API_KEY not configured" });
  }

  // Fetch NBA games (same as sync does)
  const params = new URLSearchParams({
    apiKey: ODDS_API_KEY,
    regions: "us",
    markets: "h2h,spreads,totals",
    oddsFormat: "american",
    bookmakers: "fanduel,draftkings",
  });

  const url = `${ODDS_API_BASE}/sports/basketball_nba/odds?${params}`;

  try {
    const res = await fetch(url);
    if (!res.ok) {
      return NextResponse.json({
        error: `API returned ${res.status}`,
        remaining: res.headers.get("x-requests-remaining")
      });
    }

    const games = await res.json();

    // Analyze what we got
    const analysis = games.slice(0, 3).map((game: any) => ({
      id: game.id,
      teams: `${game.away_team} @ ${game.home_team}`,
      has_bookmakers: !!game.bookmakers,
      bookmaker_count: game.bookmakers?.length || 0,
      bookmakers: game.bookmakers?.map((bk: any) => ({
        key: bk.key,
        market_count: bk.markets?.length || 0,
        markets: bk.markets?.map((m: any) => m.key) || []
      })) || []
    }));

    // Count how many games have bookmakers with markets
    const gamesWithBookmakers = games.filter((g: any) => g.bookmakers?.length > 0).length;
    const gamesWithMarkets = games.filter((g: any) =>
      g.bookmakers?.some((bk: any) => bk.markets?.length > 0)
    ).length;

    return NextResponse.json({
      total_games: games.length,
      games_with_bookmakers: gamesWithBookmakers,
      games_with_markets: gamesWithMarkets,
      sample_games: analysis,
      diagnosis: gamesWithMarkets === 0
        ? "PROBLEM: API returns games but NO bookmakers/markets! Check API key or bookmaker parameter."
        : `OK: ${gamesWithMarkets}/${games.length} games have market data.`
    });
  } catch (e: any) {
    return NextResponse.json({ error: e.message });
  }
}
