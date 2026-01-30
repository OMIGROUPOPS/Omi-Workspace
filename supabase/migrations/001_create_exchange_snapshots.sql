-- Exchange Snapshots Table
-- Stores data from prediction market exchanges (Kalshi, Polymarket)

CREATE TABLE IF NOT EXISTS exchange_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  exchange TEXT NOT NULL,  -- 'kalshi' or 'polymarket'
  market_id TEXT NOT NULL,
  market_title TEXT,
  category TEXT,  -- 'sports', 'politics', 'economics', 'crypto', 'entertainment'

  -- For sports markets, link to our game
  sport TEXT,
  game_id TEXT,  -- nullable, only if it maps to a sportsbook game

  -- Prices (0-100 scale, representing cents)
  yes_price DECIMAL,
  no_price DECIMAL,

  -- Liquidity data (EXCHANGES HAVE THIS, SPORTSBOOKS DON'T)
  yes_bid DECIMAL,
  yes_ask DECIMAL,
  no_bid DECIMAL,
  no_ask DECIMAL,
  spread DECIMAL,

  -- Volume & depth
  volume_24h DECIMAL,
  open_interest DECIMAL,
  liquidity_depth JSONB,  -- order book depth at each price level

  -- Timestamps
  snapshot_time TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,  -- when the market closes

  -- Metadata
  metadata JSONB  -- additional market-specific data
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_exchange_snapshots_exchange ON exchange_snapshots(exchange);
CREATE INDEX IF NOT EXISTS idx_exchange_snapshots_category ON exchange_snapshots(category);
CREATE INDEX IF NOT EXISTS idx_exchange_snapshots_game ON exchange_snapshots(game_id);
CREATE INDEX IF NOT EXISTS idx_exchange_snapshots_time ON exchange_snapshots(snapshot_time DESC);
CREATE INDEX IF NOT EXISTS idx_exchange_snapshots_market ON exchange_snapshots(exchange, market_id);

-- Enable RLS (Row Level Security)
ALTER TABLE exchange_snapshots ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read access
CREATE POLICY "Allow public read access to exchange_snapshots"
  ON exchange_snapshots
  FOR SELECT
  TO public
  USING (true);

-- Policy: Allow insert from service role (cron jobs)
CREATE POLICY "Allow service role insert to exchange_snapshots"
  ON exchange_snapshots
  FOR INSERT
  TO service_role
  WITH CHECK (true);

-- Comment the table
COMMENT ON TABLE exchange_snapshots IS 'Stores price and liquidity data from prediction market exchanges (Kalshi, Polymarket)';
COMMENT ON COLUMN exchange_snapshots.yes_price IS 'Price for YES outcome in cents (0-100)';
COMMENT ON COLUMN exchange_snapshots.no_price IS 'Price for NO outcome in cents (0-100)';
COMMENT ON COLUMN exchange_snapshots.spread IS 'Bid-ask spread in cents';
COMMENT ON COLUMN exchange_snapshots.liquidity_depth IS 'Order book depth at each price level as JSON';
