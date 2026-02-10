import { ExchangesGrid } from '@/components/edge/ExchangesGrid';

export const dynamic = 'force-dynamic';

// When built: each game will have an exchange detail view showing:
// - Kalshi/Polymarket Yes/No contract prices over time
// - Order book depth visualization
// - Volume and trade history
// - Exchange implied probability vs OMI fair probability vs sportsbook implied probability
// - Cross-market arbitrage detection (exchange vs sportsbook)

export default function ExchangesPage() {
  return (
    <div className="py-4 px-4 max-w-[1600px] mx-auto">
      <ExchangesGrid />
    </div>
  );
}
