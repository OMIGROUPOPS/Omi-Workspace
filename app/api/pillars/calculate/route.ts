/**
 * API Route: /api/pillars/calculate
 *
 * Fetches the REAL 6-pillar scores from the Python backend.
 * The Python backend calculates:
 * - Execution (injuries, weather, lineup)
 * - Incentives (playoffs, motivation, rivalries)
 * - Shocks (news, line movement timing)
 * - Time Decay (rest days, back-to-back, travel)
 * - Flow (sharp money, book disagreement)
 * - Game Environment (pace, expected totals, weather)
 *
 * These are the ACTUAL working pillar calculations, not the frontend placeholders.
 */
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export interface PillarScores {
  execution: number;
  incentives: number;
  shocks: number;
  timeDecay: number;
  flow: number;
  gameEnvironment: number;
  composite: number;
}

export interface PillarBreakdown {
  execution: {
    score: number;
    home_injury_impact: number;
    away_injury_impact: number;
    weather_factor: number;
    reasoning: string;
  };
  incentives: {
    score: number;
    home_motivation: number;
    away_motivation: number;
    is_rivalry: boolean;
    reasoning: string;
  };
  shocks: {
    score: number;
    line_movement: number;
    shock_detected: boolean;
    shock_direction: string;
    reasoning: string;
  };
  time_decay: {
    score: number;
    home_fatigue: number;
    away_fatigue: number;
    home_rest_days: number;
    away_rest_days: number;
    reasoning: string;
  };
  flow: {
    score: number;
    spread_variance: number;
    consensus_line: number;
    sharpest_line: number;
    book_agreement: number;
    reasoning: string;
  };
  game_environment: {
    score: number;
    expected_total: number | null;
    breakdown: Record<string, any>;
    reasoning: string;
  };
}

export interface PillarResponse {
  game_id: string;
  sport: string;
  home_team: string;
  away_team: string;
  pillar_scores: PillarScores;
  pillars: PillarBreakdown;
  overall_confidence: 'PASS' | 'WATCH' | 'EDGE' | 'STRONG' | 'RARE';
  best_bet: string | null;
  best_edge: number;
  source: 'python_backend' | 'cached';
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const gameId = searchParams.get('game_id');
  const sport = searchParams.get('sport');

  if (!gameId || !sport) {
    return NextResponse.json(
      { error: 'Missing required parameters: game_id and sport' },
      { status: 400 }
    );
  }

  try {
    console.log(`[Pillars API] Fetching pillars for game=${gameId} sport=${sport}`);

    // Try the dedicated pillar endpoint first
    let response = await fetch(
      `${BACKEND_URL}/api/pillars/${sport.toUpperCase()}/${gameId}`,
      { cache: 'no-store' }
    ).catch(err => {
      console.log(`[Pillars API] Pillar endpoint failed: ${err.message}`);
      return null;
    });

    // Fall back to the edges endpoint which also returns pillar_scores
    if (!response || !response.ok) {
      console.log(`[Pillars API] Falling back to /api/edges endpoint`);
      response = await fetch(
        `${BACKEND_URL}/api/edges/${sport.toUpperCase()}/${gameId}`,
        { cache: 'no-store' }
      );
    }

    if (!response.ok) {
      // Try to get error message from backend
      const errorText = await response.text();
      console.error(`[Pillars API] Backend error: ${response.status} - ${errorText}`);

      return NextResponse.json(
        { error: `Backend returned ${response.status}: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`[Pillars API] Got data:`, JSON.stringify(data).slice(0, 200));

    // Transform Python backend response to frontend format
    // Python uses 0-1 scale, frontend displays as percentage
    // Note: Python uses snake_case (time_decay, game_environment), frontend uses camelCase
    const pillarScores: PillarScores = {
      execution: Math.round((data.pillar_scores?.execution || 0.5) * 100),
      incentives: Math.round((data.pillar_scores?.incentives || 0.5) * 100),
      shocks: Math.round((data.pillar_scores?.shocks || 0.5) * 100),
      timeDecay: Math.round((data.pillar_scores?.time_decay || 0.5) * 100),
      flow: Math.round((data.pillar_scores?.flow || 0.5) * 100),
      gameEnvironment: Math.round((data.pillar_scores?.game_environment || 0.5) * 100),
      composite: Math.round((data.composite_score || 0.5) * 100),
    };

    const result: PillarResponse = {
      game_id: data.game_id,
      sport: data.sport,
      home_team: data.home_team,
      away_team: data.away_team,
      pillar_scores: pillarScores,
      pillars: data.pillars || {},
      overall_confidence: data.overall_confidence || 'PASS',
      best_bet: data.best_bet,
      best_edge: data.best_edge || 0,
      source: 'python_backend',
    };

    return NextResponse.json(result);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error(`[Pillars API] Error fetching from backend: ${errorMessage}`);

    // Check if it's a connection error
    const isConnectionError = errorMessage.includes('ECONNREFUSED') ||
                              errorMessage.includes('fetch failed') ||
                              errorMessage.includes('network');

    return NextResponse.json(
      {
        error: isConnectionError
          ? 'Cannot connect to Python backend'
          : 'Failed to fetch pillar scores from backend',
        details: errorMessage,
        backend_url: BACKEND_URL,
        hint: isConnectionError
          ? `Make sure Python backend is running: cd backend && python main.py`
          : 'Check backend logs for details'
      },
      { status: 503 }
    );
  }
}

/**
 * POST endpoint for batch pillar calculation
 * Useful for calculating pillars for multiple games at once
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { games } = body;

    if (!games || !Array.isArray(games)) {
      return NextResponse.json(
        { error: 'Request body must contain a "games" array' },
        { status: 400 }
      );
    }

    // Fetch pillar scores for all games in parallel
    const results = await Promise.all(
      games.map(async (game: { game_id: string; sport: string }) => {
        try {
          const response = await fetch(
            `${BACKEND_URL}/api/pillars/${game.sport.toUpperCase()}/${game.game_id}`,
            { cache: 'no-store' }
          );

          if (!response.ok) {
            return {
              game_id: game.game_id,
              error: `Backend returned ${response.status}`,
            };
          }

          const data = await response.json();

          return {
            game_id: data.game_id,
            sport: data.sport,
            pillar_scores: {
              execution: Math.round((data.pillar_scores?.execution || 0.5) * 100),
              incentives: Math.round((data.pillar_scores?.incentives || 0.5) * 100),
              shocks: Math.round((data.pillar_scores?.shocks || 0.5) * 100),
              timeDecay: Math.round((data.pillar_scores?.time_decay || 0.5) * 100),
              flow: Math.round((data.pillar_scores?.flow || 0.5) * 100),
              gameEnvironment: Math.round((data.pillar_scores?.game_environment || 0.5) * 100),
              composite: Math.round((data.composite_score || 0.5) * 100),
            },
            overall_confidence: data.overall_confidence || 'PASS',
          };
        } catch (error) {
          return {
            game_id: game.game_id,
            error: error instanceof Error ? error.message : 'Unknown error',
          };
        }
      })
    );

    return NextResponse.json({ results });
  } catch (error) {
    console.error('[Pillars API] Batch error:', error);
    return NextResponse.json(
      { error: 'Failed to process batch request' },
      { status: 500 }
    );
  }
}
