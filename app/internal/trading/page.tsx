import Link from "next/link";

export default function TradingInternalPage() {
  return (
    <div className="px-6 py-12">
      <div className="max-w-2xl mx-auto text-center">
        <div className="h-16 w-16 rounded-xl bg-amber-600 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-6">
          T
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">
          OMI Trading — Arbitrage Scanner
        </h1>
        <p className="text-zinc-500 text-lg mb-8">
          Trading bot interface coming soon.
        </p>
        <Link
          href="/internal"
          className="text-sm text-zinc-400 hover:text-white transition-colors"
        >
          Back to Hub
        </Link>
      </div>
    </div>
  );
}
