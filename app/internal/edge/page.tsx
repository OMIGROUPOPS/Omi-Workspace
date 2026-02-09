"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

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

function calibrationLabel(predicted: number, actual: number): { text: string; color: string } {
  const diff = actual - predicted;
  if (diff > 0) return { text: "Underconfident", color: "text-cyan-400" };
  if (Math.abs(diff) <= 3) return { text: "Calibrated", color: "text-emerald-400" };
  if (Math.abs(diff) <= 8) return { text: "Overconfident", color: "text-amber-400" };
  return { text: "Broken", color: "text-red-400" };
}

function pillarFlag(avgCorrect: number, avgWrong: number): { text: string; color: string } {
  const diff = avgCorrect - avgWrong;
  if (Math.abs(diff) < 3) return { text: "NOT CONTRIBUTING", color: "text-amber-400" };
  if (diff > 10) return { text: "STRONG SIGNAL", color: "text-emerald-400" };
  return { text: "WEAK SIGNAL", color: "text-zinc-400" };
}

function roiColor(roi: number): string {
  if (roi > 0) return "text-emerald-400";
  if (roi < -0.05) return "text-red-400";
  return "text-zinc-400";
}

export default function EdgeInternalPage() {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [grading, setGrading] = useState(false);
  const [gradeResult, setGradeResult] = useState<string | null>(null);

  // Filters
  const [sport, setSport] = useState("");
  const [market, setMarket] = useState("");
  const [days, setDays] = useState(30);
  const [tier, setTier] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (sport) params.set("sport", sport);
      if (market) params.set("market", market);
      if (days !== 30) params.set("days", String(days));
      if (tier) params.set("confidence_tier", tier);

      const res = await fetch(
        `${BACKEND_URL}/api/internal/edge/performance?${params.toString()}`
      );
      if (res.ok) {
        setData(await res.json());
      }
    } catch (e) {
      console.error("Failed to fetch performance data:", e);
    } finally {
      setLoading(false);
    }
  }, [sport, market, days, tier]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGrade = async () => {
    setGrading(true);
    setGradeResult(null);
    try {
      const params = sport ? `?sport=${sport}` : "";
      const res = await fetch(`${BACKEND_URL}/api/internal/grade-games${params}`, {
        method: "POST",
      });
      if (res.ok) {
        const result = await res.json();
        const graded = result.auto_grader?.graded || 0;
        const pgCreated = result.prediction_grades_created || 0;
        setGradeResult(`Graded ${graded} games, created ${pgCreated} prediction grades`);
        fetchData();
      } else {
        setGradeResult("Grade failed");
      }
    } catch {
      setGradeResult("Grade request failed");
    } finally {
      setGrading(false);
    }
  };

  const tierOrder = ["55", "60", "65", "70"];

  return (
    <div className="px-6 py-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-2xl font-bold text-white font-mono">
            OMI Edge — Performance & Grading
          </h1>
          <p className="text-zinc-500 text-sm mt-1">System self-critique dashboard</p>
        </div>
        <Link
          href="/internal"
          className="text-sm text-zinc-500 hover:text-white transition-colors"
        >
          Back to Hub
        </Link>
      </div>

      {/* Filters */}
      <div className="mt-6 flex flex-wrap items-center gap-3 bg-zinc-900 border border-zinc-800 rounded-lg p-4">
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

        <select
          value={tier}
          onChange={(e) => setTier(e.target.value)}
          className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-white"
        >
          <option value="">All Tiers</option>
          <option value="55">55%</option>
          <option value="60">60%</option>
          <option value="65">65%</option>
          <option value="70">70%</option>
        </select>

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
        </div>
      </div>

      {loading ? (
        <div className="mt-12 text-center text-zinc-500">Loading performance data...</div>
      ) : !data || data.total_predictions === 0 ? (
        <div className="mt-12 text-center text-zinc-500">
          No prediction grades found. Click &ldquo;Grade New Games&rdquo; to generate data.
        </div>
      ) : (
        <>
          {/* Summary */}
          <div className="mt-4 text-sm text-zinc-500">
            {data.total_predictions} predictions over {data.days} days
          </div>

          {/* A) Confidence Tier Table */}
          <div className="mt-6 bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
            <div className="px-4 py-3 border-b border-zinc-800">
              <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                CONFIDENCE TIER BREAKDOWN
              </h2>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-left px-4 py-2">Tier</th>
                  <th className="text-right px-4 py-2">Signals</th>
                  <th className="text-right px-4 py-2">Correct</th>
                  <th className="text-right px-4 py-2">Wrong</th>
                  <th className="text-right px-4 py-2">Hit Rate</th>
                  <th className="text-right px-4 py-2">ROI</th>
                  <th className="text-right px-4 py-2">Calibration</th>
                </tr>
              </thead>
              <tbody>
                {tierOrder.map((t) => {
                  const d = data.by_confidence_tier[t];
                  if (!d) return null;
                  const cal = data.calibration.find((c) => c.predicted === Number(t));
                  const calLabel = cal ? calibrationLabel(cal.predicted, cal.actual) : null;
                  return (
                    <tr key={t} className="border-b border-zinc-800/50 text-white">
                      <td className="px-4 py-2 font-mono">{t}%</td>
                      <td className="px-4 py-2 text-right">{d.total}</td>
                      <td className="px-4 py-2 text-right text-emerald-400">{d.correct}</td>
                      <td className="px-4 py-2 text-right text-red-400">{d.wrong}</td>
                      <td className="px-4 py-2 text-right">
                        {(d.hit_rate * 100).toFixed(1)}%
                      </td>
                      <td className={`px-4 py-2 text-right ${roiColor(d.roi)}`}>
                        {d.roi >= 0 ? "+" : ""}
                        {(d.roi * 100).toFixed(1)}%
                      </td>
                      <td className="px-4 py-2 text-right">
                        {calLabel && (
                          <span className={calLabel.color}>{calLabel.text}</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* B + C: Market Breakdown + Pillar Performance */}
          <div className="mt-6 grid md:grid-cols-2 gap-6">
            {/* Market Breakdown */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg">
              <div className="px-4 py-3 border-b border-zinc-800">
                <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                  MARKET BREAKDOWN
                </h2>
              </div>
              <div className="p-4 space-y-3">
                {Object.entries(data.by_market).map(([mkt, d]) => (
                  <div key={mkt} className="flex items-center justify-between text-sm">
                    <span className="text-white capitalize font-mono">{mkt}</span>
                    <div className="flex items-center gap-4">
                      <span className="text-zinc-400">
                        {(d.hit_rate * 100).toFixed(1)}% hit
                      </span>
                      <span className={roiColor(d.roi)}>
                        {d.roi >= 0 ? "+" : ""}
                        {(d.roi * 100).toFixed(1)}% ROI
                      </span>
                      <span className="text-zinc-600 text-xs">({d.total})</span>
                    </div>
                  </div>
                ))}
                {Object.keys(data.by_market).length === 0 && (
                  <p className="text-zinc-600 text-sm">No market data</p>
                )}
              </div>
            </div>

            {/* Pillar Performance */}
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
                        {data.by_pillar.composite.avg_correct.toFixed(1)} correct
                      </span>
                      <span className="text-zinc-500">vs</span>
                      <span className="text-red-400">
                        {data.by_pillar.composite.avg_wrong.toFixed(1)} wrong
                      </span>
                      <span
                        className={`text-xs ${pillarFlag(data.by_pillar.composite.avg_correct, data.by_pillar.composite.avg_wrong).color}`}
                      >
                        {pillarFlag(data.by_pillar.composite.avg_correct, data.by_pillar.composite.avg_wrong).text}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Signal Breakdown */}
          {Object.keys(data.by_signal).length > 0 && (
            <div className="mt-6 bg-zinc-900 border border-zinc-800 rounded-lg">
              <div className="px-4 py-3 border-b border-zinc-800">
                <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                  SIGNAL BREAKDOWN
                </h2>
              </div>
              <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                {["MISPRICED", "VALUE", "FAIR", "SHARP"].map((sig) => {
                  const d = data.by_signal[sig];
                  if (!d) return null;
                  const sigColor =
                    sig === "MISPRICED"
                      ? "text-emerald-400"
                      : sig === "VALUE"
                        ? "text-amber-400"
                        : sig === "SHARP"
                          ? "text-cyan-400"
                          : "text-zinc-400";
                  return (
                    <div key={sig} className="text-center">
                      <div className={`text-sm font-mono font-bold ${sigColor}`}>
                        {sig}
                      </div>
                      <div className="text-white text-lg mt-1">
                        {(d.hit_rate * 100).toFixed(1)}%
                      </div>
                      <div className={`text-xs ${roiColor(d.roi)}`}>
                        {d.roi >= 0 ? "+" : ""}
                        {(d.roi * 100).toFixed(1)}% ROI
                      </div>
                      <div className="text-zinc-600 text-xs mt-1">{d.total} signals</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* D) Calibration Chart (SVG) */}
          {data.calibration.length > 0 && (
            <div className="mt-6 bg-zinc-900 border border-zinc-800 rounded-lg">
              <div className="px-4 py-3 border-b border-zinc-800">
                <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                  CALIBRATION CHART
                </h2>
              </div>
              <div className="p-4 flex justify-center">
                <svg viewBox="0 0 300 300" className="w-full max-w-md">
                  {/* Background */}
                  <rect x="50" y="10" width="240" height="240" fill="#18181b" rx="4" />

                  {/* Grid lines */}
                  {[0, 25, 50, 75, 100].map((v) => {
                    const y = 250 - (v / 100) * 240;
                    const x = 50 + (v / 100) * 240;
                    return (
                      <g key={v}>
                        <line x1="50" y1={y} x2="290" y2={y} stroke="#27272a" strokeWidth="0.5" />
                        <line x1={x} y1="10" x2={x} y2="250" stroke="#27272a" strokeWidth="0.5" />
                        <text x="45" y={y + 4} textAnchor="end" fill="#52525b" fontSize="10">
                          {v}%
                        </text>
                        <text x={x} y="265" textAnchor="middle" fill="#52525b" fontSize="10">
                          {v}%
                        </text>
                      </g>
                    );
                  })}

                  {/* Perfect calibration line */}
                  <line
                    x1="50"
                    y1="250"
                    x2="290"
                    y2="10"
                    stroke="#3f3f46"
                    strokeWidth="1"
                    strokeDasharray="4 4"
                  />

                  {/* Data points */}
                  {data.calibration.map((point, i) => {
                    if (point.sample_size === 0) return null;
                    const x = 50 + (point.predicted / 100) * 240;
                    const y = 250 - (point.actual / 100) * 240;
                    const cal = calibrationLabel(point.predicted, point.actual);
                    const color =
                      cal.text === "Calibrated"
                        ? "#34d399"
                        : cal.text === "Overconfident"
                          ? "#fbbf24"
                          : cal.text === "Broken"
                            ? "#f87171"
                            : "#22d3ee";
                    return (
                      <g key={i}>
                        <circle cx={x} cy={y} r="6" fill={color} opacity="0.8" />
                        <text
                          x={x}
                          y={y - 10}
                          textAnchor="middle"
                          fill={color}
                          fontSize="9"
                          fontFamily="monospace"
                        >
                          {point.actual.toFixed(1)}%
                        </text>
                      </g>
                    );
                  })}

                  {/* Axis labels */}
                  <text x="170" y="285" textAnchor="middle" fill="#71717a" fontSize="11">
                    Predicted
                  </text>
                  <text
                    x="15"
                    y="130"
                    textAnchor="middle"
                    fill="#71717a"
                    fontSize="11"
                    transform="rotate(-90, 15, 130)"
                  >
                    Actual
                  </text>
                </svg>
              </div>
            </div>
          )}

          {/* Sport Breakdown */}
          {Object.keys(data.by_sport).length > 1 && (
            <div className="mt-6 bg-zinc-900 border border-zinc-800 rounded-lg">
              <div className="px-4 py-3 border-b border-zinc-800">
                <h2 className="text-sm font-semibold text-zinc-300 font-mono">
                  BY SPORT
                </h2>
              </div>
              <div className="p-4 space-y-2">
                {Object.entries(data.by_sport).map(([s, d]) => (
                  <div key={s} className="flex items-center justify-between text-sm">
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
    </div>
  );
}
