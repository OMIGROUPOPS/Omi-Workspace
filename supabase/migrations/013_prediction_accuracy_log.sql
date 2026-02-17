CREATE TABLE IF NOT EXISTS prediction_accuracy_log (
    id BIGSERIAL PRIMARY KEY,
    game_id TEXT NOT NULL,
    sport_key TEXT NOT NULL,
    home_team TEXT,
    away_team TEXT,
    commence_time TIMESTAMPTZ,
    omi_fair_spread NUMERIC,
    omi_fair_total NUMERIC,
    omi_composite_score NUMERIC,
    book_spread NUMERIC,
    book_total NUMERIC,
    pinnacle_spread NUMERIC,
    pinnacle_total NUMERIC,
    home_score INTEGER,
    away_score INTEGER,
    actual_margin NUMERIC,
    actual_total NUMERIC,
    omi_spread_error NUMERIC,
    omi_total_error NUMERIC,
    book_spread_error NUMERIC,
    book_total_error NUMERIC,
    pinnacle_spread_error NUMERIC,
    pinnacle_total_error NUMERIC,
    omi_vs_book_spread_edge NUMERIC,
    omi_vs_book_total_edge NUMERIC,
    omi_vs_pinnacle_spread_edge NUMERIC,
    omi_vs_pinnacle_total_edge NUMERIC,
    pillar_execution NUMERIC,
    pillar_incentives NUMERIC,
    pillar_shocks NUMERIC,
    pillar_time_decay NUMERIC,
    pillar_flow NUMERIC,
    pillar_game_environment NUMERIC,
    edge_tier TEXT,
    signal_tier TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_accuracy_log_game ON prediction_accuracy_log(game_id);
CREATE INDEX IF NOT EXISTS idx_accuracy_log_sport ON prediction_accuracy_log(sport_key);
CREATE INDEX IF NOT EXISTS idx_accuracy_log_created ON prediction_accuracy_log(created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_accuracy_log_unique ON prediction_accuracy_log(game_id);
