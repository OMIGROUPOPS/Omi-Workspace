import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";
import { calculateGameCEQ, type ExtendedOddsSnapshot } from "@/lib/edge/engine/edgescout";

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

export async function GET() {
  const supabase = getSupabase();

  // Step 1: Find Lakers @ Wizards in cached_odds
  const { data: cachedGames, error: cacheError } = await supabase
    .from("cached_odds")
    .select("game_id, sport_key, game_data, updated_at")
    .or("game_data->>home_team.ilike.%Lakers%,game_data->>home_team.ilike.%Wizards%")
    .limit(10);

  // CRITICAL: Check if game_data.id exists and matches game_id column
  // The dashboard uses game_data.id for snapshot lookup, not game_id column!

  if (cacheError) {
    return NextResponse.json({ error: "Cache query failed", details: cacheError.message });
  }

  // Find the specific game
  const lakersWizards = cachedGames?.find((g: any) => {
    const home = g.game_data?.home_team || "";
    const away = g.game_data?.away_team || "";
    return (home.includes("Lakers") || home.includes("Wizards")) &&
           (away.includes("Lakers") || away.includes("Wizards"));
  });

  if (!lakersWizards) {
    // List what games we DO have
    const { data: allGames } = await supabase
      .from("cached_odds")
      .select("game_id, game_data")
      .eq("sport_key", "basketball_nba")
      .limit(20);

    return NextResponse.json({
      error: "Lakers @ Wizards not found",
      available_nba_games: allGames?.map((g: any) => ({
        game_id: g.game_id,
        matchup: `${g.game_data?.away_team} @ ${g.game_data?.home_team}`
      }))
    });
  }

  const gameId = lakersWizards.game_id;
  const gameData = lakersWizards.game_data;

  // Step 2: Count snapshots for this game_id
  const { count: snapshotCount, error: countError } = await supabase
    .from("odds_snapshots")
    .select("*", { count: "exact", head: true })
    .eq("game_id", gameId);

  // Step 3: Get actual snapshot data
  const { data: snapshots, error: snapError } = await supabase
    .from("odds_snapshots")
    .select("game_id, market, book_key, outcome_type, line, odds, snapshot_time")
    .eq("game_id", gameId)
    .order("snapshot_time", { ascending: true })
    .limit(100);

  // Step 4: Get opening line
  const { data: openingData } = await supabase
    .from("odds_snapshots")
    .select("line")
    .eq("game_id", gameId)
    .eq("market", "spreads")
    .not("line", "is", null)
    .order("snapshot_time", { ascending: true })
    .limit(1);

  const openingLine = openingData?.[0]?.line;

  // Step 5: Build consensus from game_data
  const consensus = gameData?.bookmakers?.[0]?.markets?.reduce((acc: any, m: any) => {
    if (m.key === "spreads") {
      const home = m.outcomes?.find((o: any) => o.name === gameData.home_team);
      const away = m.outcomes?.find((o: any) => o.name === gameData.away_team);
      acc.spreads = {
        home: { line: home?.point, odds: home?.price },
        away: { line: away?.point, odds: away?.price }
      };
    }
    if (m.key === "h2h") {
      const home = m.outcomes?.find((o: any) => o.name === gameData.home_team);
      const away = m.outcomes?.find((o: any) => o.name === gameData.away_team);
      acc.h2h = { home: home?.price, away: away?.price };
    }
    if (m.key === "totals") {
      const over = m.outcomes?.find((o: any) => o.name === "Over");
      const under = m.outcomes?.find((o: any) => o.name === "Under");
      acc.totals = { line: over?.point, over: over?.price, under: under?.price };
    }
    return acc;
  }, {}) || {};

  // Step 6: Calculate CEQ
  const extendedSnapshots: ExtendedOddsSnapshot[] = (snapshots || []).map((s: any) => ({
    game_id: s.game_id,
    market: s.market,
    book_key: s.book_key,
    outcome_type: s.outcome_type,
    line: s.line,
    odds: s.odds,
    snapshot_time: s.snapshot_time,
  }));

  const hasSpread = consensus.spreads?.home?.line !== undefined;
  const hasH2h = consensus.h2h?.home !== undefined;
  const hasTotals = consensus.totals?.line !== undefined;

  let ceqResult = null;
  if (hasSpread || hasH2h || hasTotals) {
    const gameOdds = {
      spreads: hasSpread ? {
        home: { line: consensus.spreads.home.line, odds: consensus.spreads.home.odds },
        away: { line: consensus.spreads.away.line, odds: consensus.spreads.away.odds },
      } : undefined,
      h2h: hasH2h ? {
        home: consensus.h2h.home,
        away: consensus.h2h.away,
      } : undefined,
      totals: hasTotals ? {
        line: consensus.totals.line,
        over: consensus.totals.over,
        under: consensus.totals.under,
      } : undefined,
    };

    const openingData = {
      spreads: openingLine !== undefined ? {
        home: openingLine,
        away: -openingLine,
      } : undefined,
    };

    ceqResult = calculateGameCEQ(
      gameOdds,
      openingData,
      extendedSnapshots,
      {},
      {
        spreads: hasSpread ? { home: consensus.spreads.home.odds, away: consensus.spreads.away.odds } : undefined,
        h2h: hasH2h ? { home: consensus.h2h.home, away: consensus.h2h.away } : undefined,
        totals: hasTotals ? { over: consensus.totals.over, under: consensus.totals.under } : undefined,
      }
    );
  }

  // Step 7: Check what the dashboard flow sees
  // The dashboard first tries the backend, then falls back to cached_odds
  const BACKEND_URL = process.env.BACKEND_URL || "https://api.omigroup.io";
  let backendGame = null;
  let backendGameId = null;
  try {
    const res = await fetch(`${BACKEND_URL}/api/edges/NBA`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      const games = data.games || [];
      backendGame = games.find((g: any) =>
        (g.home_team?.includes("Lakers") || g.home_team?.includes("Wizards")) &&
        (g.away_team?.includes("Lakers") || g.away_team?.includes("Wizards"))
      );
      if (backendGame) {
        backendGameId = backendGame.game_id;
      }
    }
  } catch (e) {
    // Backend not available
  }

  // Step 8: If backend path is used, check if its game_id matches cached_odds
  const idMismatch = backendGameId && backendGameId !== gameId;

  // CRITICAL CHECK: Does game_data.id match the game_id column?
  // Dashboard uses game_data.id for snapshot lookup!
  const gameDataId = gameData?.id;
  const columnGameId = lakersWizards.game_id;
  const idMismatchInternal = gameDataId !== columnGameId;

  return NextResponse.json({
    step1_game_found: {
      game_id_column: columnGameId,
      game_data_id: gameDataId,
      INTERNAL_ID_MISMATCH: idMismatchInternal,
      matchup: `${gameData.away_team} @ ${gameData.home_team}`,
      sport_key: lakersWizards.sport_key,
      updated_at: lakersWizards.updated_at
    },
    step2_snapshot_count: snapshotCount,
    step3_snapshot_sample: snapshots?.slice(0, 5),
    step4_opening_line: openingLine,
    step5_consensus: consensus,
    step6_ceq_result: {
      bestEdge: ceqResult?.bestEdge,
      spreads_home_ceq: ceqResult?.spreads?.home?.ceq,
      h2h_home_ceq: ceqResult?.h2h?.home?.ceq,
      totals_over_ceq: ceqResult?.totals?.over?.ceq,
    },
    step7_backend_check: {
      backend_url: BACKEND_URL,
      backend_found_game: !!backendGame,
      backend_game_id: backendGameId,
      cached_game_id: gameId,
      ID_MISMATCH: idMismatch,
    },
    diagnosis: idMismatch
      ? `CRITICAL: Backend game_id (${backendGameId}) != cached_odds game_id (${gameId}). Dashboard uses backend ID but snapshots use cached ID!`
      : snapshotCount === 0
        ? "BROKEN: No snapshots for this game_id."
        : ceqResult?.bestEdge
          ? `CEQ works: ${ceqResult.bestEdge.ceq}% ${ceqResult.bestEdge.confidence}. If dashboard shows different value, check which code path it takes.`
          : "CEQ returned null/neutral"
  });
}
