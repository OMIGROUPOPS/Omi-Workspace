-- Variable Engine storage tables
-- Stores per-game variable scores and dynamic pillar weights

CREATE TABLE IF NOT EXISTS game_variables (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    game_id TEXT NOT NULL,
    sport_key TEXT NOT NULL,
    variable_code TEXT NOT NULL,
    variable_name TEXT NOT NULL,
    pillar TEXT NOT NULL,
    raw_value FLOAT,
    normalized FLOAT,
    confidence FLOAT,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(game_id, variable_code)
);

CREATE TABLE IF NOT EXISTS game_pillar_weights (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    game_id TEXT NOT NULL,
    sport_key TEXT NOT NULL,
    market_type TEXT NOT NULL,
    execution_weight FLOAT,
    incentives_weight FLOAT,
    shocks_weight FLOAT,
    time_decay_weight FLOAT,
    flow_weight FLOAT,
    game_env_weight FLOAT,
    context_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(game_id, market_type)
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_game_variables_game_id ON game_variables(game_id);
CREATE INDEX IF NOT EXISTS idx_game_variables_pillar ON game_variables(pillar);
CREATE INDEX IF NOT EXISTS idx_game_pillar_weights_game_id ON game_pillar_weights(game_id);
