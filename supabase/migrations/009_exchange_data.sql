-- Exchange Data table for Kalshi and Polymarket sports markets
-- Stores snapshots of exchange contract prices, matched to our sportsbook games

CREATE TABLE IF NOT EXISTS exchange_data (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  exchange text NOT NULL,                    -- 'kalshi' or 'polymarket'
  event_id text NOT NULL,                    -- exchange-specific event identifier
  event_title text NOT NULL,                 -- human-readable title
  contract_ticker text,                      -- exchange contract ticker/slug
  yes_price numeric,                         -- 0-100 cents
  no_price numeric,                          -- 0-100 cents
  yes_bid numeric,
  yes_ask numeric,
  no_bid numeric,
  no_ask numeric,
  volume integer,
  open_interest integer,
  last_price numeric,
  previous_yes_price numeric,                -- for calculating movement
  price_change numeric,                      -- yes_price - previous_yes_price
  snapshot_time timestamptz DEFAULT now(),
  mapped_game_id text,                       -- our game_id if matched to a sportsbook game
  mapped_sport_key text,                     -- our sport_key if matched
  expiration_time timestamptz,
  status text DEFAULT 'open'                 -- 'open', 'closed', 'settled'
);

-- Fast lookups by exchange and time
CREATE INDEX idx_exchange_data_exchange_time
  ON exchange_data (exchange, snapshot_time DESC);

-- Fast lookups for game-matched contracts
CREATE INDEX idx_exchange_data_mapped_game
  ON exchange_data (mapped_game_id)
  WHERE mapped_game_id IS NOT NULL;

-- RLS enabled but no policies = open access with service role key
ALTER TABLE exchange_data ENABLE ROW LEVEL SECURITY;

-- Fast deduplicated query: latest snapshot per (exchange, event_id)
CREATE OR REPLACE FUNCTION get_latest_exchange_markets(
  p_exchange text DEFAULT NULL,
  p_search text DEFAULT NULL,
  p_limit integer DEFAULT 50
)
RETURNS SETOF exchange_data
LANGUAGE sql STABLE
AS $$
  SELECT DISTINCT ON (exchange, event_id) *
  FROM exchange_data
  WHERE status = 'open'
    AND (p_exchange IS NULL OR exchange = p_exchange)
    AND (p_search IS NULL OR event_title ILIKE '%' || p_search || '%')
  ORDER BY exchange, event_id, snapshot_time DESC
$$;

-- Wrapper that also sorts by volume and applies limit
CREATE OR REPLACE FUNCTION get_exchange_markets(
  p_exchange text DEFAULT NULL,
  p_search text DEFAULT NULL,
  p_limit integer DEFAULT 50
)
RETURNS SETOF exchange_data
LANGUAGE sql STABLE
AS $$
  SELECT * FROM get_latest_exchange_markets(p_exchange, p_search, p_limit)
  ORDER BY volume DESC NULLS LAST
  LIMIT p_limit
$$;
