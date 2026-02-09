import Link from "next/link";

export default function InternalHubPage() {
  return (
    <div className="px-6 py-12">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-12">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-sm font-bold">
            OMI
          </div>
          <span className="text-xl font-semibold text-white">OMI Internal</span>
        </div>
        <p className="text-gray-500 text-sm">Operator dashboard</p>
      </div>

      {/* Cards */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8">
        {/* Solutions Internal */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left hover:border-indigo-500/50 transition-colors">
          <div className="h-12 w-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-lg font-bold mb-4">
            S
          </div>
          <h2 className="text-2xl font-semibold text-white mb-1">Solutions Internal</h2>
          <p className="text-indigo-400 text-sm font-medium mb-6">Client Management</p>
          <Link
            href="/dashboard"
            className="inline-flex px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Enter
          </Link>
        </div>

        {/* Edge Internal */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left hover:border-emerald-500/50 transition-colors">
          <div className="h-12 w-12 rounded-xl bg-emerald-600 flex items-center justify-center text-white text-lg font-bold mb-4">
            E
          </div>
          <h2 className="text-2xl font-semibold text-white mb-1">Edge Internal</h2>
          <p className="text-emerald-400 text-sm font-medium mb-6">Performance & Grading</p>
          <Link
            href="/internal/edge"
            className="inline-flex px-6 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors"
          >
            Enter
          </Link>
        </div>

        {/* Trading Internal */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-left hover:border-amber-500/50 transition-colors">
          <div className="h-12 w-12 rounded-xl bg-amber-600 flex items-center justify-center text-white text-lg font-bold mb-4">
            T
          </div>
          <h2 className="text-2xl font-semibold text-white mb-1">Trading Internal</h2>
          <p className="text-amber-400 text-sm font-medium mb-6">Arb Scanner & Trading Bot</p>
          <Link
            href="/internal/trading"
            className="inline-flex px-6 py-3 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 transition-colors"
          >
            Enter
          </Link>
        </div>
      </div>
    </div>
  );
}
