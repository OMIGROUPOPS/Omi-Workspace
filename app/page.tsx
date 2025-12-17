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
        </div>
      </header>

      {/* Hero */}
      <main className="px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-white mb-6">
            OMI Group
          </h1>
          <p className="text-xl text-gray-400 mb-16">
            Two divisions. Two markets. One standard of intelligence.
          </p>

          {/* Division Cards */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* OMI Solutions */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left hover:border-indigo-500/50 transition-colors">
              <div className="h-12 w-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-lg font-bold mb-4">
                S
              </div>
              <h2 className="text-2xl font-semibold text-white mb-1">OMI Solutions</h2>
              <p className="text-indigo-400 text-sm font-medium mb-4">Adaptive Enterprise Systems</p>
              <p className="text-gray-400 mb-6">
                AI-powered operating environments that unify workflows, knowledge, automation, and decision support for your business.
              </p>
              <Link
                href="/client/login"
                className="inline-flex px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Client Portal
              </Link>
            </div>

            {/* OMI Edge */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left opacity-75">
              <div className="h-12 w-12 rounded-xl bg-emerald-600 flex items-center justify-center text-white text-lg font-bold mb-4">
                E
              </div>
              <h2 className="text-2xl font-semibold text-white mb-1">OMI Edge</h2>
              <p className="text-emerald-400 text-sm font-medium mb-4">Predictive Market Intelligence</p>
              <p className="text-gray-400 mb-6">
                Quantitative analysis and AI-driven insights for sports and event markets. Institutional-grade intelligence.
              </p>
              <span className="inline-flex px-6 py-3 bg-gray-700 text-gray-400 font-medium rounded-lg cursor-not-allowed">
                Coming Soon
              </span>
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