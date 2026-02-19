-- RPC function: aggregate prediction_grades server-side instead of
-- transferring 1000+ raw rows to the Python backend.
--
-- Returns a single JSON object with the same shape as get_performance():
--   total_predictions, by_confidence_tier, by_market, by_sport, by_signal,
--   by_pillar, calibration

CREATE OR REPLACE FUNCTION get_performance_summary(
    p_sport text DEFAULT NULL,
    p_market text DEFAULT NULL,
    p_confidence_tier int DEFAULT NULL,
    p_signal text DEFAULT NULL,
    p_days int DEFAULT 30,
    p_since text DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_cutoff timestamptz;
    v_total int;
    v_by_tier jsonb;
    v_by_market jsonb;
    v_by_sport jsonb;
    v_by_signal jsonb;
    v_by_pillar jsonb;
    v_calibration jsonb;
    v_valid_ids text[];
BEGIN
    v_cutoff := now() - (p_days || ' days')::interval;

    -- Optional since filter: restrict to game_ids with commence_time >= p_since
    IF p_since IS NOT NULL THEN
        SELECT array_agg(game_id) INTO v_valid_ids
        FROM game_results
        WHERE commence_time >= p_since::timestamptz;
    END IF;

    -- Build a temp table of filtered rows for reuse across aggregations
    CREATE TEMP TABLE _perf_rows ON COMMIT DROP AS
    SELECT
        game_id,
        CASE
            WHEN sport_key IN ('basketball_nba', 'BASKETBALL_NBA', 'NBA') THEN 'NBA'
            WHEN sport_key IN ('americanfootball_nfl', 'AMERICANFOOTBALL_NFL', 'NFL') THEN 'NFL'
            WHEN sport_key IN ('icehockey_nhl', 'ICEHOCKEY_NHL', 'NHL') THEN 'NHL'
            WHEN sport_key IN ('americanfootball_ncaaf', 'AMERICANFOOTBALL_NCAAF', 'NCAAF') THEN 'NCAAF'
            WHEN sport_key IN ('basketball_ncaab', 'BASKETBALL_NCAAB', 'NCAAB') THEN 'NCAAB'
            WHEN sport_key IN ('soccer_epl', 'SOCCER_EPL', 'EPL') THEN 'EPL'
            ELSE sport_key
        END AS sport_norm,
        market_type,
        confidence_tier::text AS confidence_tier,
        signal,
        is_correct,
        pillar_composite
    FROM prediction_grades
    WHERE graded_at IS NOT NULL
      AND created_at >= v_cutoff
      AND (p_sport IS NULL OR sport_key = p_sport)
      AND (p_market IS NULL OR market_type = p_market)
      AND (p_confidence_tier IS NULL OR confidence_tier = p_confidence_tier)
      AND (p_signal IS NULL OR signal = p_signal)
      AND (v_valid_ids IS NULL OR game_id = ANY(v_valid_ids))
    ORDER BY created_at DESC
    LIMIT 5000;

    SELECT count(*) INTO v_total FROM _perf_rows;

    -- ── by_confidence_tier ──
    SELECT coalesce(jsonb_object_agg(grp, jsonb_build_object(
        'total', total, 'correct', correct, 'wrong', wrong, 'push', push,
        'hit_rate', hit_rate, 'roi', roi
    )), '{}'::jsonb) INTO v_by_tier
    FROM (
        SELECT
            confidence_tier AS grp,
            count(*)::int AS total,
            count(*) FILTER (WHERE is_correct = true)::int AS correct,
            count(*) FILTER (WHERE is_correct = false)::int AS wrong,
            count(*) FILTER (WHERE is_correct IS NULL)::int AS push,
            round(count(*) FILTER (WHERE is_correct = true)::numeric
                / NULLIF(count(*) FILTER (WHERE is_correct IS NOT NULL), 0), 4) AS hit_rate,
            round((count(*) FILTER (WHERE is_correct = true) * 0.91
                - count(*) FILTER (WHERE is_correct = false))::numeric
                / NULLIF(count(*), 0), 4) AS roi
        FROM _perf_rows
        WHERE confidence_tier IS NOT NULL
        GROUP BY confidence_tier
    ) s;

    -- ── by_market ──
    SELECT coalesce(jsonb_object_agg(grp, jsonb_build_object(
        'total', total, 'correct', correct, 'wrong', wrong, 'push', push,
        'hit_rate', hit_rate, 'roi', roi
    )), '{}'::jsonb) INTO v_by_market
    FROM (
        SELECT
            market_type AS grp,
            count(*)::int AS total,
            count(*) FILTER (WHERE is_correct = true)::int AS correct,
            count(*) FILTER (WHERE is_correct = false)::int AS wrong,
            count(*) FILTER (WHERE is_correct IS NULL)::int AS push,
            round(count(*) FILTER (WHERE is_correct = true)::numeric
                / NULLIF(count(*) FILTER (WHERE is_correct IS NOT NULL), 0), 4) AS hit_rate,
            round((count(*) FILTER (WHERE is_correct = true) * 0.91
                - count(*) FILTER (WHERE is_correct = false))::numeric
                / NULLIF(count(*), 0), 4) AS roi
        FROM _perf_rows
        WHERE market_type IS NOT NULL
        GROUP BY market_type
    ) s;

    -- ── by_sport ──
    SELECT coalesce(jsonb_object_agg(grp, jsonb_build_object(
        'total', total, 'correct', correct, 'wrong', wrong, 'push', push,
        'hit_rate', hit_rate, 'roi', roi
    )), '{}'::jsonb) INTO v_by_sport
    FROM (
        SELECT
            sport_norm AS grp,
            count(*)::int AS total,
            count(*) FILTER (WHERE is_correct = true)::int AS correct,
            count(*) FILTER (WHERE is_correct = false)::int AS wrong,
            count(*) FILTER (WHERE is_correct IS NULL)::int AS push,
            round(count(*) FILTER (WHERE is_correct = true)::numeric
                / NULLIF(count(*) FILTER (WHERE is_correct IS NOT NULL), 0), 4) AS hit_rate,
            round((count(*) FILTER (WHERE is_correct = true) * 0.91
                - count(*) FILTER (WHERE is_correct = false))::numeric
                / NULLIF(count(*), 0), 4) AS roi
        FROM _perf_rows
        WHERE sport_norm IS NOT NULL
        GROUP BY sport_norm
    ) s;

    -- ── by_signal ──
    SELECT coalesce(jsonb_object_agg(grp, jsonb_build_object(
        'total', total, 'correct', correct, 'wrong', wrong, 'push', push,
        'hit_rate', hit_rate, 'roi', roi
    )), '{}'::jsonb) INTO v_by_signal
    FROM (
        SELECT
            signal AS grp,
            count(*)::int AS total,
            count(*) FILTER (WHERE is_correct = true)::int AS correct,
            count(*) FILTER (WHERE is_correct = false)::int AS wrong,
            count(*) FILTER (WHERE is_correct IS NULL)::int AS push,
            round(count(*) FILTER (WHERE is_correct = true)::numeric
                / NULLIF(count(*) FILTER (WHERE is_correct IS NOT NULL), 0), 4) AS hit_rate,
            round((count(*) FILTER (WHERE is_correct = true) * 0.91
                - count(*) FILTER (WHERE is_correct = false))::numeric
                / NULLIF(count(*), 0), 4) AS roi
        FROM _perf_rows
        WHERE signal IS NOT NULL
        GROUP BY signal
    ) s;

    -- ── by_pillar (composite averages for correct vs wrong) ──
    SELECT jsonb_build_object('composite', jsonb_build_object(
        'avg_correct', round(coalesce(avg(pillar_composite) FILTER (WHERE is_correct = true), 0) * 100, 1),
        'avg_wrong',   round(coalesce(avg(pillar_composite) FILTER (WHERE is_correct = false), 0) * 100, 1),
        'correct_count', count(*) FILTER (WHERE is_correct = true AND pillar_composite IS NOT NULL),
        'wrong_count',   count(*) FILTER (WHERE is_correct = false AND pillar_composite IS NOT NULL)
    )) INTO v_by_pillar
    FROM _perf_rows
    WHERE pillar_composite IS NOT NULL;

    IF v_by_pillar IS NULL THEN
        v_by_pillar := '{"composite":{"avg_correct":0,"avg_wrong":0,"correct_count":0,"wrong_count":0}}'::jsonb;
    END IF;

    -- ── calibration by signal tier ──
    -- Step 1: compute raw stats per tier (no JSON aggregation here)
    CREATE TEMP TABLE _cal ON COMMIT DROP AS
    SELECT
        t.tier_name,
        t.predicted,
        count(*) FILTER (WHERE r.is_correct = true)  AS n_correct,
        count(*) FILTER (WHERE r.is_correct IS NOT NULL) AS n_decided
    FROM (VALUES
        ('NO EDGE',   52),
        ('LOW EDGE',  57),
        ('MID EDGE',  63),
        ('HIGH EDGE', 68),
        ('MAX EDGE',  73)
    ) AS t(tier_name, predicted)
    LEFT JOIN _perf_rows r ON r.signal = t.tier_name
    GROUP BY t.tier_name, t.predicted;

    -- Step 2: build JSON array from the flat stats
    SELECT coalesce(jsonb_agg(
        jsonb_build_object(
            'predicted', predicted,
            'actual',    round(coalesce(n_correct::numeric / NULLIF(n_decided, 0), 0) * 100, 1),
            'sample_size', n_decided,
            'tier',      tier_name
        ) ORDER BY predicted
    ), '[]'::jsonb) INTO v_calibration
    FROM _cal;

    RETURN jsonb_build_object(
        'total_predictions', v_total,
        'by_confidence_tier', v_by_tier,
        'by_market', v_by_market,
        'by_sport', v_by_sport,
        'by_signal', v_by_signal,
        'by_pillar', v_by_pillar,
        'calibration', v_calibration
    );
END;
$$;
