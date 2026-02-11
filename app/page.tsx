import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-950">
      {/* Header */}
      <header className="px-6 py-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-sm font-bold">
              OMI
            </div>
            <span className="text-xl font-semibold text-white">OMI Group</span>
          </div>
          <Link
            href="/internal"
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Internal Login
          </Link>
        </div>
      </header>

      {/* Hero */}
      <main className="px-6 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-white mb-20">
            OMI Group
          </h1>

          {/* Division Cards */}
          <div className="grid md:grid-cols-3 gap-8">
            {/* OMI Solutions */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left hover:border-indigo-500/50 transition-colors">
              <div className="h-12 w-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-lg font-bold mb-4">
                S
              </div>
              <h2 className="text-2xl font-semibold text-white mb-1">OMI Solutions</h2>
              <p className="text-indigo-400 text-sm font-medium mb-6">Adaptive Enterprise Systems</p>
              <Link
                href="/client/login"
                className="inline-flex px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Client Portal
              </Link>
            </div>

            {/* OMI Edge */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left hover:border-emerald-500/50 transition-colors">
              <div className="h-12 w-12 rounded-xl bg-emerald-600 flex items-center justify-center text-white text-lg font-bold mb-4">
                E
              </div>
              <h2 className="text-2xl font-semibold text-white mb-1">OMI Edge</h2>
              <p className="text-emerald-400 text-sm font-medium mb-6">Predictive Market Intelligence</p>
              <Link
                href="/edge/portal/sports"
                className="inline-flex px-6 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors"
              >
                OMI Edge
              </Link>
            </div>

            {/* OMI Trading */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left hover:border-amber-500/50 transition-colors">
              <div className="h-12 w-12 rounded-xl bg-amber-600 flex items-center justify-center text-white mb-4">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-1">OMI Trading</h2>
              <p className="text-amber-400 text-sm font-medium mb-6">Automated Arbitrage Trading</p>
              <Link
                href="/internal"
                className="inline-flex px-6 py-3 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 transition-colors"
              >
                Trading Bot
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-8 mt-20 border-t border-gray-800">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-gray-500 text-sm">
            OMI Group
          </p>
        </div>
      </footer>
    </div>
  );
}