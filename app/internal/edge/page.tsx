"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TierData {
  total: number;
  correct: number;
  wrong: number;
  push: number;
  hit_rate: number;
  roi: number;
}

interface CalibrationPoint {
  predicted: number;
  actual: number;
  sample_size: number;
  tier?: string;
}

interface PillarData {
  composite: {
    avg_correct: number;
    avg_wrong: number;
    correct_count: number;
    wrong_count: number;
  };
}

interface PerformanceData {
  total_predictions: number;
  days: number;
  by_confidence_tier: Record<string, TierData>;
  by_market: Record<string, TierData>;
  by_sport: Record<string, TierData>;
  by_signal: Record<string, TierData>;
  by_pillar: PillarData;
  calibration: CalibrationPoint[];
}

interface BookDetail {
  line: number;
  odds: number | null;
  fair_price: number;
  edge: number;
  signal: string;
  call: string;
  book_offer: string;
  side: string;
  correct: boolean | null;
}

interface GradedGameRow {
  game_id: string;
  sport_key: string;
  home_team: string;
  away_team: string;
  commence_time: string;
  home_score: number | null;
  away_score: number | null;
  market_type: string;
  omi_fair_line: number | null;
  omi_fair_display: string;
  confidence_tier: number;
  pillar_composite: number | null;
  best_edge: number | null;
  best_book: string | null;
  is_correct: boolean | null;
  fd: BookDetail | null;
  dk: BookDetail | null;
}

interface LiveMarketRow {
  game_id: string;
  sport_key: string;
  home_team: string;
  away_team: string;
  commence_time: string;
  market_type: string;
  omi_fair: string;
  omi_fair_line: number | null;
  fd_line: number | null;
  fd_odds: number | null;
  fd_edge: number | null;
  fd_signal: string | null;
  dk_line: number | null;
  dk_odds: number | null;
  dk_edge: number | null;
  dk_signal: string | null;
  best_edge: number | null;
  signal: string;
}

interface LiveMarketsResponse {
  rows: LiveMarketRow[];
  count: number;
}

interface GradedGamesSummary {
  total_graded: number;
  wins: number;
  losses: number;
  pushes: number;
  hit_rate: number;
  roi: number;
  best_sport: { key: string; hit_rate: number; count: number } | null;
  best_market: { key: string; hit_rate: number; count: number } | null;
}

interface GradedGamesDiagnostics {
  db_total_prediction_grades: number;
  raw_query_rows: number;
  valid_game_ids_count: number | string;
  unique_game_ids_in_rows: number;
}

interface GradedGamesResponse {
  rows: GradedGameRow[];
  summary: GradedGamesSummary;
  count: number;
  diagnostics?: GradedGamesDiagnostics;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SPORT_TO_ODDS_KEY: Record<string, string> = {
  NBA: "basketball_nba",
  NFL: "americanfootball_nfl",
  NHL: "icehockey_nhl",
  NCAAF: "americanfootball_ncaaf",
  NCAAB: "basketball_ncaab",
  EPL: "soccer_epl",
};

const SPORT_BADGE_COLORS: Record<string, string> = {
  NBA: "bg-orange-500/20 text-orange-400",
  NFL: "bg-green-500/20 text-green-400",
  NHL: "bg-blue-500/20 text-blue-400",
  NCAAF: "bg-green-500/20 text-green-300",
  NCAAB: "bg-orange-500/20 text-orange-300",
  EPL: "bg-purple-500/20 text-purple-400",
};

const SIGNAL_COLORS: Record<string, string> = {
  "MAX EDGE": "text-red-400",
  "HIGH EDGE": "text-cyan-400",
  "MID EDGE": "text-amber-400",
  "LOW EDGE": "text-zinc-400",
  "NO EDGE": "text-zinc-500",
  "STALE": "text-zinc-600",
  "PENDING": "text-zinc-600",
  // Legacy fallbacks
  MISPRICED: "text-red-400",
  VALUE: "text-amber-400",
  FAIR: "text-zinc-400",
  SHARP: "text-zinc-500",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function calibrationLabel(
  predicted: number,
  actual: number,
  sampleSize: number
): { text: string; color: string } {
  if (sampleSize < 20)
    return { text: "Insufficient Data", color: "text-zinc-500" };
  if (sampleSize < 50)
    return { text: `Early (${actual.toFixed(1)}%)`, color: "text-zinc-400" };
  const diff = Math.abs(actual - predicted);
  if (diff <= 5) return { text: "Strong", color: "text-emerald-400" };
  if (diff <= 10) return { text: "Good", color: "text-cyan-400" };
  if (diff <= 15) return { text: "Weak", color: "text-amber-400" };
  return { text: "Broken", color: "text-red-400" };
}

function pillarFlag(
  avgCorrect: number,
  avgWrong: number
): { text: string; color: string } {
  const diff = avgCorrect - avgWrong;
  if (Math.abs(diff) < 3)
    return { text: "NOT CONTRIBUTING", color: "text-amber-400" };
  if (diff > 10) return { text: "STRONG SIGNAL", color: "text-emerald-400" };
  return { text: "WEAK SIGNAL", color: "text-zinc-400" };
}

function roiColor(roi: number): string {
  if (roi > 0) return "text-emerald-400";
  if (roi < -0.05) return "text-red-400";
  return "text-zinc-400";
}

function fmtLine(val: number | null, market: string): string {
  if (val == null) return "—";
  const n = Number(val);
  if (market === "moneyline") return `${n.toFixed(1)}%`;
  if (n > 0) return `+${n.toFixed(1)}`;
  return n.toFixed(1);
}

function fmtEdgePct(val: number | null): string {
  if (val == null) return "—";
  const n = Number(val);
  const sign = n >= 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

function fmtOdds(val: number | null): string {
  if (val == null) return "—";
  const n = Number(val);
  if (n > 0) return `+${n}`;
  return String(n);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function EdgeInternalPage() {
  const router = useRouter();

  // Shared state
  const [activeTab, setActiveTab] = useState<"performance" | "graded" | "live">(
    "performance"
  );
  const [grading, setGrading] = useState(false);
  const [gradeResult, setGradeResult] = useState<string | null>(null);

  // Shared filters
  const [sport, setSport] = useState("");
  const [market, setMarket] = useState("");
  const [days, setDays] = useState(30);
  const [cleanDataOnly, setCleanDataOnly] = useState(true);

  // Performance tab state
  const [data, setData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [tier, setTier] = useState("");

  // Graded games tab state
  const [gradedData, setGradedData] = useState<GradedGamesResponse | null>(
    null
  );
  const [gradedLoading, setGradedLoading] = useState(false);
  const [verdictFilter, setVerdictFilter] = useState("");
  const [sortField, setSortField] = useState("commence_time");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  // Pregame markets tab state
  const [liveData, setLiveData] = useState<LiveMarketsResponse | null>(null);
  const [liveLoading, setLiveLoading] = useState(false);

  // ------- Performance fetch -------
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (sport) params.set("sport", sport);
      if (market) params.set("market", market);
      if (days !== 30) params.set("days", String(days));
      if (tier) params.set("signal", tier);
      if (cleanDataOnly) params.set("since", "2026-02-10T00:00:00+00:00");
      const res = await fetch(
        `${BACKEND_URL}/api/internal/edge/performance?${params.toString()}`
      );
      if (res.ok) setData(await res.json());
    } catch (e) {
      console.error("Failed to fetch performance data:", e);
    } finally {
      setLoading(false);
    }
  }, [sport, market, days, tier, cleanDataOnly]);

  useEffect(() => {
    if (activeTab === "performance") fetchData();
  }, [activeTab, fetchData]);

  // ------- Graded games fetch -------
  const fetchGradedGames = useCallback(async () => {
    setGradedLoading(true);
    try {
      const params = new URLSearchParams();
      if (sport) params.set("sport", sport);
      if (market) params.set("market", market);
      if (days !== 30) params.set("days", String(days));
      if (verdictFilter) params.set("verdict", verdictFilter);
      if (cleanDataOnly) params.set("since", "2026-02-10T00:00:00+00:00");
      const res = await fetch(
        `${BACKEND_URL}/api/internal/edge/graded-games?${params.toString()}`
      );
      if (res.ok) setGradedData(await res.json());
    } catch (e) {
      console.error("Failed to fetch graded games:", e);
    } finally {
      setGradedLoading(false);
    }
  }, [sport, market, days, verdictFilter, cleanDataOnly]);

  useEffect(() => {
    if (activeTab === "graded") fetchGradedGames();
  }, [activeTab, fetchGradedGames]);

  // ------- Pregame markets fetch -------
  const fetchLiveMarkets = useCallback(async () => {
    setLiveLoading(true);
    try {
      const params = new URLSearchParams();
      if (sport) params.set("sport", sport);
      const res = await fetch(
        `${BACKEND_URL}/api/internal/edge/live-markets?${params.toString()}`
      );
      if (res.ok) setLiveData(await res.json());
    } catch (e) {
      console.error("Failed to fetch pregame markets:", e);
    } finally {
      setLiveLoading(false);
    }
  }, [sport]);

  useEffect(() => {
    if (activeTab === "live") fetchLiveMarkets();
  }, [activeTab, fetchLiveMarkets]);

  // ------- Grade handler -------
  const handleGrade = async () => {
    setGrading(true);
    setGradeResult(null);
    try {
      const params = sport ? `?sport=${sport}` : "";
      const res = await fetch(
        `${BACKEND_URL}/api/internal/grade-games${params}`,
        { method: "POST" }
      );
      if (res.ok) {
        const result = await res.json();
        const graded = result.auto_grader?.graded || 0;
        const checked = result.auto_grader?.checked || 0;
        const notFound = result.auto_grader?.not_found || 0;
        const pgCreated = result.prediction_grades_created || 0;
        const bootstrapped = result.bootstrapped_game_results || 0;
        let msg = `Graded ${graded}/${checked} games, ${pgCreated} prediction grades`;
        if (bootstrapped > 0) msg += `, ${bootstrapped} bootstrapped`;
        if (notFound > 0) msg += ` (${notFound} no ESPN match)`;
        setGradeResult(msg);
        if (result.auto_grader?.not_found_details?.length > 0) {
          console.log("[Grade] Not found details:", result.auto_grader.not_found_details);
          console.log("[Grade] Diagnostics:", result.auto_grader.diagnostics);
        }
        if (activeTab === "performance") fetchData();
        else fetchGradedGames();
      } else {
        setGradeResult("Grade failed");
      }
    } catch {
      setGradeResult("Grade request failed");
    } finally {
      setGrading(false);
    }
  };

  // ------- Sort logic -------
  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const sortedRows = useMemo(() => {
    if (!gradedData?.rows) return [];
    return [...gradedData.rows].sort((a, b) => {
      // Handle nested book fields like "fd.edge", "dk.edge"
      let aVal: string | number | boolean | null | undefined;
      let bVal: string | number | boolean | null | undefined;
      if (sortField === "fd_edge") {
        aVal = a.fd?.edge;
        bVal = b.fd?.edge;
      } else if (sortField === "dk_edge") {
        aVal = a.dk?.edge;
        bVal = b.dk?.edge;
      } else {
        aVal = a[sortField as keyof GradedGameRow] as string | number | boolean | null;
        bVal = b[sortField as keyof GradedGameRow] as string | number | boolean | null;
      }
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === "boolean") {
        return sortDir === "asc"
          ? Number(aVal) - Number(bVal as boolean)
          : Number(bVal as boolean) - Number(aVal);
      }
      if (typeof aVal === "string") {
        return sortDir === "asc"
          ? aVal.localeCompare(bVal as string)
          : (bVal as string).localeCompare(aVal);
      }
      return sortDir === "asc"
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number);
    });
  }, [gradedData?.rows, sortField, sortDir]);

  // ------- Render helpers -------
  const EDGE_TIERS = ["NO EDGE", "LOW EDGE", "MID EDGE", "HIGH EDGE", "MAX EDGE"];
  const EDGE_TIER_RANGES: Record<string, string> = {
    "NO EDGE": "<1%", "LOW EDGE": "1-3%", "MID EDGE": "3-6%",
    "HIGH EDGE": "6-10%", "MAX EDGE": "10%+",
  };

  const SortHeader = ({
    field,
    label,
    align = "left",
  }: {
    field: string;
    label: string;
    align?: string;
  }) => (
    <th
      className={`text-${align} px-3 py-2 cursor-pointer hover:text-zinc-300 select-none whitespace-nowrap`}
      onClick={() => handleSort(field)}
    >
      {label}
      {sortField === field && (
        <span className="ml-1 text-cyan-400">
          {sortDir === "asc" ? "\u25B2" : "\u25BC"}
        </span>
      )}
    </th>
  );

  // =====================================================================
  return (
    <div className="px-6 py-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-2xl font-bold text-white font-mono">
            OMI Edge — Performance & Grading
          </h1>
          <p className="text-zinc-500 text-sm mt-1">
            System self-critique dashboard
          </p>
        </div>
        <Link
          href="/internal"
          className="text-sm text-zinc-500 hover:text-white transition-colors"
        >
          Back to Hub
        </Link>
      </div>

      {/* Tab Bar */}
      <div className="mt-4 flex gap-1 border-b border-zinc-800">
        <button
          onClick={() => setActiveTab("performance")}
          className={`px-4 py-2.5 text-sm font-mono border-b-2 transition-colors ${
            activeTab === "performance"
              ? "text-cyan-400 border-cyan-400"
              : "text-zinc-500 border-transparent hover:text-zinc-300"
          }`}
        >
          PERFORMANCE
        </button>
        <button
          onClick={() => setActiveTab("graded")}
          className={`px-4 py-2.5 text-sm font-mono border-b-2 transition-colors ${
            activeTab === "graded"
              ? "text-cyan-400 border-cyan-400"
              : "text-zinc-500 border-transparent hover:text-zinc-300"
          }`}
        >
          GRADED GAMES
        </button>
        <button
          onClick={() => setActiveTab("live")}
          className={`px-4 py-2.5 text-sm font-mono border-b-2 transition-colors ${
            activeTab === "live"
              ? "text-cyan-400 border-cyan-400"
              : "text-zinc-500 border-transparent hover:text-zinc-300"
          }`}
        >
          PREGAME MARKETS
        </button>
      </div>

      {/* Filters */}
      <div className="mt-4 flex flex-wrap items-center gap-3 bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <select
          value={sport}
          onChange={(e) => setSport(e.target.value)}
          className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-white"
        >
          <option value="">All Sports</option>
          <option value="NFL">NFL</option>
          <option value="NBA">NBA</option>
          <option value="NHL">NHL</option>
          <option value="NCAAF">NCAAF</option>
          <option value="NCAAB">NCAAB</option>
          <option value="EPL">EPL</option>
        </select>

        <select
          value={market}
          onChange={(e) => setMarket(e.target.value)}
          className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-white"
        >
          <option value="">All Markets</option>
          <option value="spread">Spread</option>
          <option value="total">Total</option>
          <option value="moneyline">Moneyline</option>
        </select>

        <select
          value={String(days)}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-white"
        >
          <option value="7">7 days</option>
          <option value="14">14 days</option>
          <option value="30">30 days</option>
          <option value="90">90 days</option>
          <option value="365">All time</option>
        </select>

        {activeTab === "performance" && (
          <select
            value={tier}
            onChange={(e) => setTier(e.target.value)}
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-white"
          >
            <option value="">All Edge Tiers</option>
            <option value="NO EDGE">No Edge (&lt;1%)</option>
            <option value="LOW EDGE">Low Edge (1-3%)</option>
            <option value="MID EDGE">Mid Edge (3-6%)</option>
            <option value="HIGH EDGE">High Edge (6-10%)</option>
            <option value="MAX EDGE">Max Edge (10%+)</option>
          </select>
        )}

        {activeTab === "graded" && (
          <select
            value={verdictFilter}
            onChange={(e) => setVerdictFilter(e.target.value)}
            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-white"
          >
            <option value="">All Verdicts</option>
            <option value="win">Wins</option>
            <option value="loss">Losses</option>
            <option value="push">Pushes</option>
          </select>
        )}

        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={cleanDataOnly}
            onChange={(e) => setCleanDataOnly(e.target.checked)}
            className="accent-cyan-500 w-4 h-4"
          />
          <span className="text-sm text-zinc-300">Clean Data Only</span>
          <span className="text-xs text-zinc-600">(Feb 10+)</span>
        </label>

        <div className="ml-auto flex items-center gap-3">
          {gradeResult && (
            <span className="text-xs text-zinc-400">{gradeResult}</span>
          )}
          <button
            onClick={handleGrade}
            disabled={grading}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-600/50 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {grading ? "Grading..." : "Grade New Games"}
          </button>
          <button
            onClick={async () => {
              setGrading(true);
              setGradeResult(null);
              try {
                const res = await fetch(
                  `${BACKEND_URL}/api/internal/grade-games?regrade=true`,
                  { method: "POST" }
                );
                if (res.ok) {
                  const r = await res.json();
                  setGradeResult(
                    `Regrade: purged ${r.purged}, regenerated ${r.created} from ${r.games} games ` +
                    `(${r.zero_grade_games || 0} produced 0, ${r.errors} errors)`
                  );
                  if (r.sample_diagnostics?.length > 0) {
                    console.log("[Regrade] Sample diagnostics:", r.sample_diagnostics);
                  }
                  if (activeTab === "performance") fetchData();
                  else fetchGradedGames();
                } else {
                  setGradeResult("Regrade failed");
                }
              } catch {
                setGradeResult("Regrade request failed");
              } finally {
                setGrading(false);
              }
            }}
            disabled={grading}
            className="px-3 py-2 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-600/50 text-white text-xs font-medium rounded-lg transition-colors"
          >
            Regrade All
          </button>
        </div>
      </div>

      {/* ================================================================= */}
      {/* PERFORMANCE TAB                                                   */}
      {/* ================================================================= */}
      {activeTab === "performance" && (
        <>
          {loading ? (
            <div className="mt-12 text-center text-zinc-500">
              Loading performance data...
            </div>
          ) : !data || data.total_predictions === 0 ? (
            <div className="mt-12 text-center text-zinc-500">
              No prediction grades found. Click &ldquo;Grade New Games&rdquo; to
              generate data.
            </div>
          ) : (
            <>
              <div className="mt-4 text-sm text-zinc-500">
                {data.total_predictions} predictions over {data.days} days
              </div>

              {/* Edge Tier Breakdown Table */}
              <div className="mt-4 bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
                <div className="px-4 py-3 border-b border-zinc-800">
                  <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                    EDGE TIER BREAKDOWN
                  </h2>
                </div>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-zinc-500 border-b border-zinc-800">
                      <th className="text-left px-4 py-2">Tier</th>
                      <th className="text-left px-4 py-2">Range</th>
                      <th className="text-right px-4 py-2">Signals</th>
                      <th className="text-right px-4 py-2">W-L-P</th>
                      <th className="text-right px-4 py-2">Hit Rate</th>
                      <th className="text-right px-4 py-2">ROI</th>
                      <th className="text-right px-4 py-2">Calibration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {EDGE_TIERS.map((t) => {
                      const d = data.by_signal[t];
                      if (!d) return null;
                      const cal = data.calibration.find(
                        (c) => c.tier === t
                      );
                      const calLabel = cal
                        ? calibrationLabel(
                            cal.predicted,
                            cal.actual,
                            cal.sample_size
                          )
                        : null;
                      const sigColor = SIGNAL_COLORS[t] || "text-zinc-400";
                      return (
                        <tr
                          key={t}
                          className="border-b border-zinc-800/50 text-white"
                        >
                          <td className={`px-4 py-2 font-mono font-bold ${sigColor}`}>{t}</td>
                          <td className="px-4 py-2 text-zinc-500 text-xs">{EDGE_TIER_RANGES[t]}</td>
                          <td className="px-4 py-2 text-right">{d.total}</td>
                          <td className="px-4 py-2 text-right text-zinc-400 font-mono">
                            {d.correct}-{d.wrong}-{d.push}
                          </td>
                          <td className="px-4 py-2 text-right font-mono">
                            {(d.hit_rate * 100).toFixed(1)}%
                          </td>
                          <td
                            className={`px-4 py-2 text-right font-mono ${roiColor(d.roi)}`}
                          >
                            {d.roi >= 0 ? "+" : ""}
                            {(d.roi * 100).toFixed(1)}%
                          </td>
                          <td className="px-4 py-2 text-right">
                            {calLabel && (
                              <span className={calLabel.color}>
                                {calLabel.text}
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Signal Breakdown Cards */}
              {Object.keys(data.by_signal).length > 0 && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
                  {EDGE_TIERS.map((sig) => {
                    const d = data.by_signal[sig];
                    if (!d) return null;
                    const sigColor = SIGNAL_COLORS[sig] || "text-zinc-400";
                    return (
                      <div key={sig} className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
                        <div className={`text-xs font-mono font-bold ${sigColor}`}>
                          {sig}
                        </div>
                        <div className="text-white text-xl font-bold mt-1">
                          {(d.hit_rate * 100).toFixed(1)}%
                        </div>
                        <div className={`text-xs font-mono ${roiColor(d.roi)}`}>
                          {d.roi >= 0 ? "+" : ""}
                          {(d.roi * 100).toFixed(1)}% ROI
                        </div>
                        <div className="text-zinc-600 text-xs mt-1">
                          {d.total} signals
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Market + Pillar */}
              <div className="mt-4 grid md:grid-cols-2 gap-4">
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
                  <div className="px-4 py-3 border-b border-zinc-800">
                    <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                      MARKET BREAKDOWN
                    </h2>
                  </div>
                  <div className="p-4 space-y-3">
                    {Object.entries(data.by_market).map(([mkt, d]) => (
                      <div
                        key={mkt}
                        className="flex items-center justify-between text-sm"
                      >
                        <span className="text-white capitalize font-mono">
                          {mkt}
                        </span>
                        <div className="flex items-center gap-4">
                          <span className="text-zinc-400">
                            {(d.hit_rate * 100).toFixed(1)}% hit
                          </span>
                          <span className={roiColor(d.roi)}>
                            {d.roi >= 0 ? "+" : ""}
                            {(d.roi * 100).toFixed(1)}% ROI
                          </span>
                          <span className="text-zinc-600 text-xs">
                            ({d.total})
                          </span>
                        </div>
                      </div>
                    ))}
                    {Object.keys(data.by_market).length === 0 && (
                      <p className="text-zinc-600 text-sm">No market data</p>
                    )}
                  </div>
                </div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
                  <div className="px-4 py-3 border-b border-zinc-800">
                    <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                      PILLAR PERFORMANCE
                    </h2>
                  </div>
                  <div className="p-4 space-y-3">
                    {data.by_pillar.composite && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-white font-mono">Composite</span>
                        <div className="flex items-center gap-3">
                          <span className="text-emerald-400">
                            {data.by_pillar.composite.avg_correct.toFixed(1)}{" "}
                            correct
                          </span>
                          <span className="text-zinc-500">vs</span>
                          <span className="text-red-400">
                            {data.by_pillar.composite.avg_wrong.toFixed(1)}{" "}
                            wrong
                          </span>
                          <span
                            className={`text-xs ${pillarFlag(data.by_pillar.composite.avg_correct, data.by_pillar.composite.avg_wrong).color}`}
                          >
                            {
                              pillarFlag(
                                data.by_pillar.composite.avg_correct,
                                data.by_pillar.composite.avg_wrong
                              ).text
                            }
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Calibration Chart — Edge Tiers on X-axis */}
              {data.calibration.length > 0 && (
                <div className="mt-4 bg-zinc-900 border border-zinc-800 rounded-lg">
                  <div className="px-4 py-3 border-b border-zinc-800">
                    <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                      CALIBRATION — EDGE TIER vs ACTUAL HIT RATE
                    </h2>
                  </div>
                  <div className="p-4 flex justify-center">
                    <svg viewBox="0 0 340 260" className="w-full max-w-lg">
                      <rect x="50" y="10" width="270" height="200" fill="#18181b" rx="4" />
                      {/* Y-axis gridlines and labels (0% - 100%) */}
                      {[0, 25, 50, 75, 100].map((v) => {
                        const y = 210 - (v / 100) * 200;
                        return (
                          <g key={`y-${v}`}>
                            <line x1="50" y1={y} x2="320" y2={y} stroke="#27272a" strokeWidth="0.5" />
                            <text x="45" y={y + 4} textAnchor="end" fill="#52525b" fontSize="10">{v}%</text>
                          </g>
                        );
                      })}
                      {/* Perfect calibration dashed line connecting expected confidence midpoints */}
                      {(() => {
                        const tierMidpoints = [52, 57, 63, 68, 73]; // NO EDGE→MAX EDGE
                        const tierXPositions = [0, 1, 2, 3, 4].map((i) => 77 + i * 60);
                        const points = tierMidpoints.map((mp, i) => {
                          const x = tierXPositions[i];
                          const y = 210 - (mp / 100) * 200;
                          return `${x},${y}`;
                        });
                        return (
                          <polyline
                            points={points.join(" ")}
                            fill="none"
                            stroke="#3f3f46"
                            strokeWidth="1"
                            strokeDasharray="4 4"
                          />
                        );
                      })()}
                      {/* Tier columns with dots */}
                      {data.calibration.map((point, i) => {
                        if (point.sample_size === 0) return null;
                        const x = 77 + i * 60; // evenly spaced across 5 tiers
                        const y = 210 - (point.actual / 100) * 200;
                        const expectedY = 210 - (point.predicted / 100) * 200;
                        const tierName = point.tier || EDGE_TIERS[i] || "";
                        const tierColor = SIGNAL_COLORS[tierName] || "text-zinc-400";
                        // Map tier color class to hex
                        const dotColor = tierName === "MAX EDGE" ? "#f87171"
                          : tierName === "HIGH EDGE" ? "#22d3ee"
                          : tierName === "MID EDGE" ? "#fbbf24"
                          : tierName === "LOW EDGE" ? "#a1a1aa"
                          : "#71717a";
                        return (
                          <g key={i}>
                            {/* Expected confidence marker (small hollow circle) */}
                            <circle cx={x} cy={expectedY} r="3" fill="none" stroke="#3f3f46" strokeWidth="1" />
                            {/* Actual hit rate dot */}
                            <circle cx={x} cy={y} r="7" fill={dotColor} opacity="0.9" />
                            {/* Actual value label */}
                            <text x={x} y={y - 12} textAnchor="middle" fill={dotColor} fontSize="10" fontFamily="monospace">
                              {point.actual.toFixed(1)}%
                            </text>
                            {/* X-axis tier label */}
                            <text x={x} y="230" textAnchor="middle" fill={dotColor} fontSize="8" fontFamily="monospace" fontWeight="bold">
                              {tierName.replace(" EDGE", "").replace("NO", "NONE")}
                            </text>
                          </g>
                        );
                      })}
                      {/* Axis labels */}
                      <text x="185" y="250" textAnchor="middle" fill="#71717a" fontSize="10">
                        Edge Tier
                      </text>
                      <text x="15" y="110" textAnchor="middle" fill="#71717a" fontSize="10" transform="rotate(-90, 15, 110)">
                        Actual Hit Rate
                      </text>
                    </svg>
                  </div>
                </div>
              )}

              {/* Sport Breakdown — always show if any sports exist */}
              {Object.keys(data.by_sport).length >= 1 && (
                <div className="mt-4 bg-zinc-900 border border-zinc-800 rounded-lg">
                  <div className="px-4 py-3 border-b border-zinc-800">
                    <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                      BY SPORT
                    </h2>
                  </div>
                  <div className="p-4 space-y-2">
                    {Object.entries(data.by_sport).map(([s, d]) => (
                      <div
                        key={s}
                        className="flex items-center justify-between text-sm"
                      >
                        <span className="text-white font-mono">{s}</span>
                        <div className="flex items-center gap-4">
                          <span className="text-zinc-400">
                            {d.correct}-{d.wrong}-{d.push}
                          </span>
                          <span className="text-zinc-400">
                            {(d.hit_rate * 100).toFixed(1)}%
                          </span>
                          <span className={roiColor(d.roi)}>
                            {d.roi >= 0 ? "+" : ""}
                            {(d.roi * 100).toFixed(1)}% ROI
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}

      {/* ================================================================= */}
      {/* GRADED GAMES TAB                                                  */}
      {/* ================================================================= */}
      {activeTab === "graded" && (
        <>
          {gradedLoading ? (
            <div className="mt-12 text-center text-zinc-500">
              Loading graded games...
            </div>
          ) : !gradedData || gradedData.count === 0 ? (
            <div className="mt-12 text-center text-zinc-500">
              No graded games found. Click &ldquo;Grade New Games&rdquo; to
              generate data.
            </div>
          ) : (
            <>
              {/* Summary Stats */}
              <div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
                  <div className="text-xs text-zinc-500 font-mono">
                    TOTAL GRADED
                  </div>
                  <div className="text-xl font-bold text-white mt-1">
                    {gradedData.summary.total_graded}
                  </div>
                </div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
                  <div className="text-xs text-zinc-500 font-mono">
                    HIT RATE
                  </div>
                  <div
                    className={`text-xl font-bold mt-1 ${gradedData.summary.hit_rate >= 0.524 ? "text-emerald-400" : "text-red-400"}`}
                  >
                    {(gradedData.summary.hit_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-zinc-600">
                    {gradedData.summary.wins}W-{gradedData.summary.losses}L-
                    {gradedData.summary.pushes}P
                  </div>
                </div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
                  <div className="text-xs text-zinc-500 font-mono">
                    ROI (1u flat)
                  </div>
                  <div
                    className={`text-xl font-bold mt-1 ${roiColor(gradedData.summary.roi)}`}
                  >
                    {gradedData.summary.roi >= 0 ? "+" : ""}
                    {(gradedData.summary.roi * 100).toFixed(1)}%
                  </div>
                </div>
                {gradedData.summary.best_sport && (
                  <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
                    <div className="text-xs text-zinc-500 font-mono">
                      BEST SPORT
                    </div>
                    <div className="text-xl font-bold text-cyan-400 mt-1">
                      {gradedData.summary.best_sport.key}
                    </div>
                    <div className="text-xs text-zinc-600">
                      {(gradedData.summary.best_sport.hit_rate * 100).toFixed(1)}
                      % ({gradedData.summary.best_sport.count})
                    </div>
                  </div>
                )}
                {gradedData.summary.best_market && (
                  <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
                    <div className="text-xs text-zinc-500 font-mono">
                      BEST MARKET
                    </div>
                    <div className="text-xl font-bold text-cyan-400 mt-1 capitalize">
                      {gradedData.summary.best_market.key}
                    </div>
                    <div className="text-xs text-zinc-600">
                      {(gradedData.summary.best_market.hit_rate * 100).toFixed(1)}
                      % ({gradedData.summary.best_market.count})
                    </div>
                  </div>
                )}
              </div>

              {/* DB Diagnostics */}
              {gradedData.diagnostics && (
                <div className="mt-2 text-xs text-zinc-600 font-mono flex gap-4">
                  <span>DB rows: {gradedData.diagnostics.db_total_prediction_grades}</span>
                  <span>Query returned: {gradedData.diagnostics.raw_query_rows}</span>
                  <span>Valid game IDs: {gradedData.diagnostics.valid_game_ids_count}</span>
                  <span>Unique games: {gradedData.diagnostics.unique_game_ids_in_rows}</span>
                </div>
              )}

              {/* Graded Games Table */}
              <div className="mt-4 bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-zinc-500 border-b border-zinc-800 text-xs uppercase tracking-wide">
                        <SortHeader field="commence_time" label="Date" />
                        <th className="text-left px-3 py-2">Sport</th>
                        <SortHeader field="home_team" label="Matchup" />
                        <SortHeader field="market_type" label="Mkt" />
                        <th className="text-left px-3 py-2">OMI Fair</th>
                        <SortHeader
                          field="fd_edge"
                          label="FD Edge"
                          align="left"
                        />
                        <SortHeader
                          field="dk_edge"
                          label="DK Edge"
                          align="left"
                        />
                        <SortHeader
                          field="confidence_tier"
                          label="Tier"
                          align="center"
                        />
                        <th className="text-center px-3 py-2">Verdict</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sortedRows.map((row, i) => (
                        <tr
                          key={`${row.game_id}-${row.market_type}-${i}`}
                          onClick={() =>
                            router.push(
                              `/edge/portal/sports/game/${row.game_id}?sport=${SPORT_TO_ODDS_KEY[row.sport_key] || row.sport_key.toLowerCase()}`
                            )
                          }
                          className={`border-b border-zinc-800/50 cursor-pointer transition-colors ${
                            row.is_correct === true
                              ? "bg-emerald-500/5 hover:bg-emerald-500/10"
                              : row.is_correct === false
                                ? "bg-red-500/5 hover:bg-red-500/10"
                                : "hover:bg-zinc-800/30"
                          }`}
                        >
                          {/* Date */}
                          <td className="px-3 py-2.5 text-zinc-400 whitespace-nowrap text-xs">
                            {row.commence_time
                              ? new Date(
                                  row.commence_time
                                ).toLocaleDateString("en-US", {
                                  month: "short",
                                  day: "numeric",
                                })
                              : "—"}
                          </td>

                          {/* Sport */}
                          <td className="px-3 py-2.5">
                            <span
                              className={`px-1.5 py-0.5 rounded text-xs font-mono ${SPORT_BADGE_COLORS[row.sport_key] || "bg-zinc-800 text-zinc-400"}`}
                            >
                              {row.sport_key}
                            </span>
                          </td>

                          {/* Matchup */}
                          <td className="px-3 py-2.5 whitespace-nowrap">
                            <div className="text-white text-xs">
                              {row.away_team || "—"}{" "}
                              <span className="text-zinc-600">@</span>{" "}
                              {row.home_team || "—"}
                            </div>
                            {row.home_score != null &&
                              row.away_score != null && (
                                <div className="text-zinc-500 text-xs font-mono">
                                  {row.away_score}–{row.home_score}
                                </div>
                              )}
                          </td>

                          {/* Market */}
                          <td className="px-3 py-2.5 whitespace-nowrap">
                            <span className="text-white text-xs capitalize">
                              {row.market_type}
                            </span>
                          </td>

                          {/* OMI Fair */}
                          <td className="px-3 py-2.5 text-xs whitespace-nowrap text-cyan-400 font-mono">
                            {row.omi_fair_display || fmtLine(row.omi_fair_line, row.market_type)}
                          </td>

                          {/* FD Edge */}
                          <td className="px-3 py-2.5 text-xs whitespace-nowrap">
                            {row.fd ? (
                              row.fd.signal === "STALE" ? (
                                <span className="text-zinc-600 font-mono">STALE</span>
                              ) : (
                                <div
                                  className={
                                    row.fd.correct === true
                                      ? "text-emerald-400"
                                      : row.fd.correct === false
                                        ? "text-red-400"
                                        : "text-zinc-300"
                                  }
                                >
                                  <div className="font-medium">
                                    {row.fd.call}
                                  </div>
                                  <div className="flex items-center gap-1.5 mt-0.5">
                                    <span className="text-zinc-500">
                                      FD {fmtOdds(row.fd.odds)}
                                    </span>
                                    <span className="font-mono">
                                      {fmtEdgePct(row.fd.edge)}
                                    </span>
                                    <span
                                      className={`text-[10px] font-mono font-bold ${SIGNAL_COLORS[row.fd.signal] || "text-zinc-500"}`}
                                    >
                                      {row.fd.signal}
                                    </span>
                                  </div>
                                </div>
                              )
                            ) : (
                              <span className="text-zinc-600">—</span>
                            )}
                          </td>

                          {/* DK Edge */}
                          <td className="px-3 py-2.5 text-xs whitespace-nowrap">
                            {row.dk ? (
                              row.dk.signal === "STALE" ? (
                                <span className="text-zinc-600 font-mono">STALE</span>
                              ) : (
                                <div
                                  className={
                                    row.dk.correct === true
                                      ? "text-emerald-400"
                                      : row.dk.correct === false
                                        ? "text-red-400"
                                        : "text-zinc-300"
                                  }
                                >
                                  <div className="font-medium">
                                    {row.dk.call}
                                  </div>
                                  <div className="flex items-center gap-1.5 mt-0.5">
                                    <span className="text-zinc-500">
                                      DK {fmtOdds(row.dk.odds)}
                                    </span>
                                    <span className="font-mono">
                                      {fmtEdgePct(row.dk.edge)}
                                    </span>
                                    <span
                                      className={`text-[10px] font-mono font-bold ${SIGNAL_COLORS[row.dk.signal] || "text-zinc-500"}`}
                                    >
                                      {row.dk.signal}
                                    </span>
                                  </div>
                                </div>
                              )
                            ) : (
                              <span className="text-zinc-600">—</span>
                            )}
                          </td>

                          {/* Tier */}
                          <td className="px-3 py-2.5 text-center text-xs font-mono text-zinc-400">
                            {row.confidence_tier != null ? `${Number(row.confidence_tier).toFixed(1)}%` : "—"}
                          </td>

                          {/* Verdict */}
                          <td className="px-3 py-2.5 text-center">
                            {row.is_correct === true ? (
                              <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">
                                WIN
                              </span>
                            ) : row.is_correct === false ? (
                              <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-400">
                                LOSS
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded text-xs font-bold bg-yellow-500/20 text-yellow-400">
                                PUSH
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </>
      )}

      {/* ================================================================= */}
      {/* PREGAME MARKETS TAB                                               */}
      {/* ================================================================= */}
      {activeTab === "live" && (
        <>
          {liveLoading ? (
            <div className="mt-12 text-center text-zinc-500">
              Loading pregame markets...
            </div>
          ) : !liveData || liveData.count === 0 ? (
            <div className="mt-12 text-center text-zinc-500">
              No upcoming games found.
            </div>
          ) : (
            <>
              <div className="mt-4 text-sm text-zinc-500">
                {liveData.count} markets across upcoming games
              </div>

              <div className="mt-4 bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-zinc-500 border-b border-zinc-800 text-xs uppercase tracking-wide">
                        <th className="text-left px-3 py-2">Time</th>
                        <th className="text-left px-3 py-2">Sport</th>
                        <th className="text-left px-3 py-2">Matchup</th>
                        <th className="text-left px-3 py-2">Mkt</th>
                        <th className="text-left px-3 py-2">OMI Fair</th>
                        <th className="text-left px-3 py-2">FD Line</th>
                        <th className="text-left px-3 py-2">FD Edge</th>
                        <th className="text-left px-3 py-2">DK Line</th>
                        <th className="text-left px-3 py-2">DK Edge</th>
                        <th className="text-center px-3 py-2">Signal</th>
                      </tr>
                    </thead>
                    <tbody>
                      {liveData.rows.map((row, i) => {
                        const sigColor = SIGNAL_COLORS[row.signal] || "text-zinc-500";
                        return (
                          <tr
                            key={`${row.game_id}-${row.market_type}-${i}`}
                            onClick={() =>
                              router.push(
                                `/edge/portal/sports/game/${row.game_id}?sport=${SPORT_TO_ODDS_KEY[row.sport_key] || row.sport_key.toLowerCase()}`
                              )
                            }
                            className="border-b border-zinc-800/50 cursor-pointer hover:bg-zinc-800/30 transition-colors"
                          >
                            {/* Time */}
                            <td className="px-3 py-2.5 text-zinc-400 whitespace-nowrap text-xs">
                              {row.commence_time
                                ? new Date(row.commence_time).toLocaleString("en-US", {
                                    month: "short", day: "numeric",
                                    hour: "numeric", minute: "2-digit",
                                  })
                                : "—"}
                            </td>

                            {/* Sport */}
                            <td className="px-3 py-2.5">
                              <span className={`px-1.5 py-0.5 rounded text-xs font-mono ${SPORT_BADGE_COLORS[row.sport_key] || "bg-zinc-800 text-zinc-400"}`}>
                                {row.sport_key}
                              </span>
                            </td>

                            {/* Matchup */}
                            <td className="px-3 py-2.5 whitespace-nowrap text-white text-xs">
                              {row.away_team} <span className="text-zinc-600">@</span> {row.home_team}
                            </td>

                            {/* Market */}
                            <td className="px-3 py-2.5 text-white text-xs capitalize">
                              {row.market_type}
                            </td>

                            {/* OMI Fair */}
                            <td className={`px-3 py-2.5 font-mono text-xs whitespace-nowrap ${row.omi_fair_line != null ? "text-cyan-400" : "text-zinc-600 italic"}`}>
                              {row.omi_fair}
                            </td>

                            {/* FD Line */}
                            <td className="px-3 py-2.5 text-zinc-300 font-mono text-xs whitespace-nowrap">
                              {row.fd_line != null ? (
                                row.market_type === "moneyline" ? fmtOdds(row.fd_line) :
                                row.market_type === "spread" ? (row.fd_line > 0 ? `+${row.fd_line}` : String(row.fd_line)) :
                                String(row.fd_line)
                              ) : "—"}
                            </td>

                            {/* FD Edge */}
                            <td className="px-3 py-2.5 text-xs whitespace-nowrap">
                              {row.fd_signal === "STALE" ? (
                                <span className="text-zinc-600 font-mono">STALE</span>
                              ) : row.fd_edge != null ? (
                                <span className={`font-mono ${SIGNAL_COLORS[row.fd_signal || ""] || "text-zinc-400"}`}>
                                  {fmtEdgePct(row.fd_edge)}
                                </span>
                              ) : <span className="text-zinc-600">—</span>}
                            </td>

                            {/* DK Line */}
                            <td className="px-3 py-2.5 text-zinc-300 font-mono text-xs whitespace-nowrap">
                              {row.dk_line != null ? (
                                row.market_type === "moneyline" ? fmtOdds(row.dk_line) :
                                row.market_type === "spread" ? (row.dk_line > 0 ? `+${row.dk_line}` : String(row.dk_line)) :
                                String(row.dk_line)
                              ) : "—"}
                            </td>

                            {/* DK Edge */}
                            <td className="px-3 py-2.5 text-xs whitespace-nowrap">
                              {row.dk_signal === "STALE" ? (
                                <span className="text-zinc-600 font-mono">STALE</span>
                              ) : row.dk_edge != null ? (
                                <span className={`font-mono ${SIGNAL_COLORS[row.dk_signal || ""] || "text-zinc-400"}`}>
                                  {fmtEdgePct(row.dk_edge)}
                                </span>
                              ) : <span className="text-zinc-600">—</span>}
                            </td>

                            {/* Signal */}
                            <td className="px-3 py-2.5 text-center">
                              <span className={`text-xs font-mono font-bold ${sigColor}`}>
                                {row.signal}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
