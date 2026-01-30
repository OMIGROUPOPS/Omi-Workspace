import { ExchangesGrid } from '@/components/edge/ExchangesGrid';

export const dynamic = 'force-dynamic';

export default function ExchangesPage() {
  return (
    <div className="py-4 px-4 max-w-[1600px] mx-auto">
      <ExchangesGrid />
    </div>
  );
}
