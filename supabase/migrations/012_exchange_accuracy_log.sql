-- Exchange accuracy log: tracks whether exchange or sportsbook was closer to actual result
-- Populated by the grading pipeline after each game is graded

CREATE TABLE IF NOT EXISTS exchange_accuracy_log (
    id BIGSERIAL PRIMARY KEY,
    game_id TEXT NOT NULL,
    sport_key TEXT NOT NULL,
    market_type TEXT NOT NULL,          -- spread, total, moneyline
    exchange TEXT NOT NULL,             -- kalshi, polymarket
    book_name TEXT NOT NULL,            -- fanduel, draftkings
    exchange_implied_prob REAL,         -- exchange yes_price / 100
    book_implied_prob REAL,             -- vig-removed book implied prob
    omi_fair_prob REAL,                 -- OMI fair line implied prob
    actual_result TEXT,                 -- home_covered, away_covered, over, under, etc.
    actual_value REAL,                  -- final spread or final total
    exchange_error REAL,                -- abs(exchange_implied - actual_binary)
    book_error REAL,                    -- abs(book_implied - actual_binary)
    exchange_closer BOOLEAN,            -- exchange_error < book_error
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exchange_accuracy_game ON exchange_accuracy_log(game_id);
CREATE INDEX IF NOT EXISTS idx_exchange_accuracy_sport ON exchange_accuracy_log(sport_key);
CREATE INDEX IF NOT EXISTS idx_exchange_accuracy_created ON exchange_accuracy_log(created_at);
