-- RPC function: aggregate prediction_accuracy_log server-side instead of
-- transferring 5000 raw rows to the Python backend.
--
-- Returns a single JSON object with the same shape as get_accuracy_summary():
--   overall, by_tier, pillar_correlation

CREATE OR REPLACE FUNCTION get_accuracy_summary(
    p_sport text DEFAULT NULL,
    p_days int DEFAULT 30
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_cutoff timestamptz;
    v_overall jsonb;
    v_by_tier jsonb;
    v_pillar_correlation jsonb;
    v_count int;
BEGIN
    v_cutoff := now() - (p_days || ' days')::interval;

    -- Build a temp table of filtered rows for reuse
    CREATE TEMP TABLE _acc_rows ON COMMIT DROP AS
    SELECT
        omi_spread_error,
        omi_total_error,
        book_spread_error,
        book_total_error,
        pinnacle_spread_error,
        pinnacle_total_error,
        omi_vs_book_spread_edge,
        omi_vs_book_total_edge,
        pillar_execution,
        pillar_incentives,
        pillar_shocks,
        pillar_time_decay,
        pillar_flow,
        pillar_game_environment,
        coalesce(signal_tier, edge_tier, 'UNKNOWN') AS tier
    FROM prediction_accuracy_log
    WHERE created_at >= v_cutoff
      AND (p_sport IS NULL OR sport_key = p_sport)
    ORDER BY created_at DESC
    LIMIT 5000;

    SELECT count(*) INTO v_count FROM _acc_rows;

    IF v_count = 0 THEN
        RETURN jsonb_build_object('games', 0, 'message', 'No accuracy data yet');
    END IF;

    -- ── overall ──
    SELECT jsonb_build_object(
        'games', count(*),
        'avg_omi_spread_error',     round(avg(omi_spread_error)::numeric, 2),
        'avg_book_spread_error',    round(avg(book_spread_error)::numeric, 2),
        'avg_pinnacle_spread_error', round(avg(pinnacle_spread_error)::numeric, 2),
        'avg_omi_total_error',      round(avg(omi_total_error)::numeric, 2),
        'avg_book_total_error',     round(avg(book_total_error)::numeric, 2),
        'avg_pinnacle_total_error', round(avg(pinnacle_total_error)::numeric, 2),
        'avg_omi_spread_edge',      round(avg(omi_vs_book_spread_edge)::numeric, 2),
        'avg_omi_total_edge',       round(avg(omi_vs_book_total_edge)::numeric, 2),
        'omi_closer_spread',  count(*) FILTER (WHERE omi_vs_book_spread_edge > 0),
        'book_closer_spread', count(*) FILTER (WHERE omi_vs_book_spread_edge < 0),
        'tied_spread',        count(*) FILTER (WHERE omi_vs_book_spread_edge = 0),
        'omi_closer_total',   count(*) FILTER (WHERE omi_vs_book_total_edge > 0),
        'book_closer_total',  count(*) FILTER (WHERE omi_vs_book_total_edge < 0),
        'spread_games',       count(*) FILTER (WHERE omi_vs_book_spread_edge IS NOT NULL),
        'total_games',        count(*) FILTER (WHERE omi_vs_book_total_edge IS NOT NULL)
    ) INTO v_overall
    FROM _acc_rows;

    -- ── by_tier ──
    -- Step 1: flat stats per tier
    CREATE TEMP TABLE _tier_stats ON COMMIT DROP AS
    SELECT
        tier AS grp,
        count(*)::int AS games,
        round(avg(omi_spread_error)::numeric, 2) AS avg_omi_spread_error,
        round(avg(book_spread_error)::numeric, 2) AS avg_book_spread_error,
        round(avg(omi_vs_book_spread_edge)::numeric, 2) AS avg_spread_edge,
        round(avg(omi_total_error)::numeric, 2) AS avg_omi_total_error,
        round(avg(book_total_error)::numeric, 2) AS avg_book_total_error,
        round(avg(omi_vs_book_total_edge)::numeric, 2) AS avg_total_edge
    FROM _acc_rows
    WHERE tier IS NOT NULL
    GROUP BY tier;

    -- Step 2: aggregate to JSON
    SELECT coalesce(jsonb_object_agg(grp, jsonb_build_object(
        'games', games,
        'avg_omi_spread_error', avg_omi_spread_error,
        'avg_book_spread_error', avg_book_spread_error,
        'avg_spread_edge', avg_spread_edge,
        'avg_omi_total_error', avg_omi_total_error,
        'avg_book_total_error', avg_book_total_error,
        'avg_total_edge', avg_total_edge
    )), '{}'::jsonb) INTO v_by_tier
    FROM _tier_stats;

    -- ── pillar_correlation ──
    -- Step 1: flat stats per pillar
    CREATE TEMP TABLE _pillar_stats ON COMMIT DROP AS
    SELECT
        pillar_name,
        count(*) FILTER (WHERE abs(pillar_val - 0.5) > 0.02 AND spread_err IS NOT NULL)::int AS active_games,
        count(*) FILTER (WHERE abs(pillar_val - 0.5) <= 0.02 AND spread_err IS NOT NULL)::int AS neutral_games,
        round(avg(spread_err) FILTER (WHERE abs(pillar_val - 0.5) > 0.02)::numeric, 2) AS avg_error_active,
        round(avg(spread_err) FILTER (WHERE abs(pillar_val - 0.5) <= 0.02)::numeric, 2) AS avg_error_neutral
    FROM (
        SELECT 'execution' AS pillar_name, pillar_execution AS pillar_val, omi_spread_error AS spread_err FROM _acc_rows
        UNION ALL
        SELECT 'incentives', pillar_incentives, omi_spread_error FROM _acc_rows
        UNION ALL
        SELECT 'shocks', pillar_shocks, omi_spread_error FROM _acc_rows
        UNION ALL
        SELECT 'time_decay', pillar_time_decay, omi_spread_error FROM _acc_rows
        UNION ALL
        SELECT 'flow', pillar_flow, omi_spread_error FROM _acc_rows
        UNION ALL
        SELECT 'game_environment', pillar_game_environment, omi_spread_error FROM _acc_rows
    ) pillars
    WHERE pillar_val IS NOT NULL
    GROUP BY pillar_name;

    -- Step 2: aggregate to JSON
    SELECT coalesce(jsonb_object_agg(pillar_name, jsonb_build_object(
        'active_games', active_games,
        'neutral_games', neutral_games,
        'avg_error_active', avg_error_active,
        'avg_error_neutral', avg_error_neutral,
        'accuracy_lift', CASE
            WHEN avg_error_active IS NOT NULL AND avg_error_neutral IS NOT NULL
            THEN round((avg_error_neutral - avg_error_active)::numeric, 2)
            ELSE NULL
        END
    )), '{}'::jsonb) INTO v_pillar_correlation
    FROM _pillar_stats;

    RETURN jsonb_build_object(
        'overall', v_overall,
        'by_tier', v_by_tier,
        'pillar_correlation', v_pillar_correlation
    );
END;
$$;
