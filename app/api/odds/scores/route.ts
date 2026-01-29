import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

const ODDS_API_KEY = process.env.ODDS_API_KEY || "";
const ODDS_API_BASE = "https://api.the-odds-api.com/v4";

// Sport keys we support
const SPORT_KEYS = [
  "americanfootball_nfl",
  "americanfootball_ncaaf",
  "basketball_nba",
  "icehockey_nhl",
  "basketball_ncaab",
  "baseball_mlb",
  "basketball_wnba",
];

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

interface ScoreData {
  id: string;
  sport_key: string;
  sport_title: string;
  commence_time: string;
  completed: boolean;
  home_team: string;
  away_team: string;
  scores: { name: string; score: string }[] | null;
  last_update: string | null;
}

async function fetchScoresForSport(sportKey: string): Promise<ScoreData[]> {
  const params = new URLSearchParams({
    apiKey: ODDS_API_KEY,
    daysFrom: "1", // Get scores from last 1 day
  });

  const url = `${ODDS_API_BASE}/sports/${sportKey}/scores?${params}`;

  try {
    const res = await fetch(url);
    if (!res.ok) {
      if (res.status === 422) {
        // Sport not in season
        return [];
      }
      console.error(`[Scores] ${sportKey} error: ${res.status}`);
      return [];
    }
    return res.json();
  } catch (e) {
    console.error(`[Scores] ${sportKey} fetch failed:`, e);
    return [];
  }
}

// GET - Fetch and cache scores for all sports
export async function GET(request: Request) {
  if (!ODDS_API_KEY) {
    return NextResponse.json(
      { error: "ODDS_API_KEY not configured" },
      { status: 500 }
    );
  }

  const supabase = getSupabase();
  const allScores: Record<string, any> = {};
  let totalGames = 0;

  // Fetch scores for each sport
  for (const sportKey of SPORT_KEYS) {
    try {
      const scores = await fetchScoresForSport(sportKey);

      if (scores.length > 0) {
        // Transform to a simpler format keyed by game ID
        for (const game of scores) {
          if (game.scores && game.scores.length >= 2) {
            const homeScore = game.scores.find(s => s.name === game.home_team);
            const awayScore = game.scores.find(s => s.name === game.away_team);

            allScores[game.id] = {
              home: homeScore?.score || "0",
              away: awayScore?.score || "0",
              completed: game.completed,
              lastUpdate: game.last_update,
            };
            totalGames++;
          }
        }
      }
    } catch (e) {
      console.error(`[Scores] ${sportKey} processing failed:`, e);
    }
  }

  // Cache scores in Supabase for quick access
  if (Object.keys(allScores).length > 0) {
    const { error } = await supabase
      .from("game_scores")
      .upsert(
        Object.entries(allScores).map(([gameId, scores]) => ({
          game_id: gameId,
          home_score: parseInt(scores.home) || 0,
          away_score: parseInt(scores.away) || 0,
          completed: scores.completed,
          updated_at: new Date().toISOString(),
        })),
        { onConflict: "game_id" }
      );

    if (error) {
      console.error("[Scores] Cache save failed:", error.message);
    }
  }

  return NextResponse.json({
    scores: allScores,
    totalGames,
    fetchedAt: new Date().toISOString(),
  });
}

// POST - Get scores for specific game IDs
export async function POST(request: Request) {
  try {
    const { gameIds } = await request.json();

    if (!gameIds || !Array.isArray(gameIds)) {
      return NextResponse.json(
        { error: "gameIds array required" },
        { status: 400 }
      );
    }

    const supabase = getSupabase();

    // Get cached scores from Supabase
    const { data, error } = await supabase
      .from("game_scores")
      .select("*")
      .in("game_id", gameIds);

    if (error) {
      console.error("[Scores] Fetch error:", error.message);
      return NextResponse.json({ scores: {} });
    }

    // Transform to map
    const scores: Record<string, any> = {};
    for (const row of data || []) {
      scores[row.game_id] = {
        home: row.home_score,
        away: row.away_score,
        completed: row.completed,
      };
    }

    return NextResponse.json({ scores });
  } catch (e) {
    console.error("[Scores] POST error:", e);
    return NextResponse.json({ scores: {} });
  }
}
