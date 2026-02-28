"use client";

import React, { useState, useMemo } from "react";
import type { ArbDataReturn } from "../hooks/useArbData";
import type { MappedGame, TeamPrices } from "../types";
import { sportBadge, fmtNum } from "../helpers";

interface Props {
  data: ArbDataReturn;
}

type SortKey = "spread" | "sport" | "team" | "k_depth" | "pm_depth" | "imbalance";
type SportFilter = "ALL" | "CBB" | "NBA" | "NHL" | "UFC";

/* ── Helpers ─────────────────────────────────────────────────────────── */

function calcSpread(t: TeamPrices | undefined): { buyPM: number; buyK: number; best: number } {
  if (!t) return { buyPM: 0, buyK: 0, best: 0 };
  const buyPM = (t.k_bid && t.pm_ask) ? t.k_bid - t.pm_ask : 0;
  const buyK = (t.pm_bid && t.k_ask) ? t.pm_bid - t.k_ask : 0;
  return { buyPM, buyK, best: Math.max(buyPM, buyK) };
}

function imbInfo(kDepth: number, pmDepth: number): { label: string; color: string } {
  if (!kDepth || !pmDepth) return { label: "—", color: "text-[#3a3a5a]" };
  const r = kDepth / pmDepth;
  if (r > 5) return { label: `K ${r.toFixed(0)}x`, color: "text-[#ff8c00]" };
  if (r > 2) return { label: `K ${r.toFixed(1)}x`, color: "text-[#ff8c00]/70" };
  if (r < 0.2) return { label: `PM ${(1/r).toFixed(0)}x`, color: "text-[#00bfff]" };
  if (r < 0.5) return { label: `PM ${(1/r).toFixed(1)}x`, color: "text-[#00bfff]/70" };
  return { label: "~1:1", color: "text-[#4a4a6a]" };
}

function DepthBar({ k, pm }: { k: number; pm: number }) {
  const total = k + pm;
  if (!total) return <span className="text-[#2a2a4a]">—</span>;
  const kPct = (k / total) * 100;
  return (
    <div className="flex h-[6px] w-full overflow-hidden">
      <div className="h-full bg-[#ff8c00]/50" style={{ width: `${kPct}%` }} />
      <div className="h-full bg-[#00bfff]/50" style={{ width: `${100 - kPct}%` }} />
    </div>
  );
}

function P({ v }: { v: number }) {
  if (!v) return <span className="text-[#2a2a4a]">—</span>;
  return <>{v}</>;
}

/* ── Main Component ──────────────────────────────────────────────────── */

export function LiveGamesTab({ data }: Props) {
  const { state } = data;
  const [sortKey, setSortKey] = useState<SortKey>("spread");
  const [sortAsc, setSortAsc] = useState(false);
  const [sportFilter, setSportFilter] = useState<SportFilter>("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedGame, setExpandedGame] = useState<string | null>(null);

  const games = state?.mapped_games ?? [];

  const activeGames = useMemo(() => {
    return games.filter((g) => {
      if (g.game_status === "post") return false;
      if (g.status !== "Active") return false;
      if (sportFilter !== "ALL" && g.sport.toUpperCase() !== sportFilter) return false;
      if (searchTerm) {
        const s = searchTerm.toLowerCase();
        if (!(g.team1 || "").toLowerCase().includes(s) &&
            !(g.team2 || "").toLowerCase().includes(s) &&
            !(g.team1_full || "").toLowerCase().includes(s) &&
            !(g.team2_full || "").toLowerCase().includes(s)) return false;
      }
      return true;
    });
  }, [games, sportFilter, searchTerm]);

  const sorted = useMemo(() => {
    const arr = [...activeGames];
    arr.sort((a, b) => {
      let va = 0, vb = 0;
      switch (sortKey) {
        case "spread": va = a.best_spread; vb = b.best_spread; break;
        case "sport": return sortAsc ? a.sport.localeCompare(b.sport) : b.sport.localeCompare(a.sport);
        case "team": return sortAsc ? (a.team1 || "").localeCompare(b.team1 || "") : (b.team1 || "").localeCompare(a.team1 || "");
        case "k_depth": va = a.k_depth ?? 0; vb = b.k_depth ?? 0; break;
        case "pm_depth": va = a.pm_depth ?? 0; vb = b.pm_depth ?? 0; break;
        case "imbalance":
          va = (a.k_depth ?? 0) / Math.max(a.pm_depth ?? 1, 1);
          vb = (b.k_depth ?? 0) / Math.max(b.pm_depth ?? 1, 1); break;
      }
      return sortAsc ? va - vb : vb - va;
    });
    return arr;
  }, [activeGames, sortKey, sortAsc]);

  const stats = useMemo(() => {
    let arb = 0, watch = 0, kD = 0, pmD = 0, max = 0;
    for (const g of activeGames) {
      if (g.best_spread >= 4) arb++;
      else if (g.best_spread >= 2) watch++;
      if (g.best_spread > max) max = g.best_spread;
      kD += g.k_depth ?? 0;
      pmD += g.pm_depth ?? 0;
    }
    return { arb, watch, kD, pmD, max, total: activeGames.length };
  }, [activeGames]);

  const sports = useMemo(() => {
    const s = new Set(games.filter((g) => g.status === "Active").map((g) => g.sport.toUpperCase()));
    return Array.from(s).sort();
  }, [games]);

  const liveCount = useMemo(() => games.filter((g) => g.game_status === "in").length, [games]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortAsc(!sortAsc);
    else { setSortKey(key); setSortAsc(false); }
  }
  function si(key: SortKey) { return sortKey === key ? (sortAsc ? " ▲" : " ▼") : ""; }

  return (
    <div className="p-0">
      {/* ── Ticker Strip ─────────────────────────────────── */}
      <div className="flex items-center gap-2 px-2 py-1 bg-[#06060c] border-b border-[#1a1a2e] text-[9px] font-mono overflow-x-auto">
        {stats.arb > 0 && <span className="text-[#00ff88] font-bold animate-pulse">⚡ {stats.arb} ARB</span>}
        {stats.watch > 0 && <span className="text-[#ff8c00]">{stats.watch} WATCH</span>}
        <span className="text-[#1a1a2e]">│</span>
        {liveCount > 0 && (<><span className="text-[#00ff88]">● {liveCount} IN-PLAY</span><span className="text-[#1a1a2e]">│</span></>)}
        <span className="text-[#4a4a6a]">{stats.total} MKT</span>
        <span className="text-[#1a1a2e]">│</span>
        <span className="text-[#4a4a6a]">MAX <span className={stats.max >= 4 ? "text-[#00ff88] font-bold" : stats.max >= 2 ? "text-[#ff8c00]" : "text-[#4a4a6a]"}>{stats.max.toFixed(1)}c</span></span>
        <span className="text-[#1a1a2e]">│</span>
        <span className="text-[#ff8c00]/60">K Σ{fmtNum(stats.kD)}</span>
        <span className="text-[#00bfff]/60">PM Σ{fmtNum(stats.pmD)}</span>

        <div className="ml-auto flex items-center gap-1 shrink-0">
          {(["ALL", ...sports] as SportFilter[]).map((s) => (
            <button key={s} onClick={() => setSportFilter(s)}
              className={`px-1.5 py-0.5 text-[8px] tracking-wider border transition-colors ${
                sportFilter === s ? "text-[#ff8c00] border-[#ff8c00]/40 bg-[#ff8c00]/10" : "text-[#3a3a5a] border-[#1a1a2e] hover:text-[#ff8c00]/60"
              }`}>{s}</button>
          ))}
          <span className="text-[#1a1a2e]">│</span>
          <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="SEARCH" className="w-16 bg-transparent border border-[#1a1a2e] px-1 py-0.5 text-[8px] font-mono text-[#ff8c00] placeholder-[#2a2a4a] focus:border-[#ff8c00]/40 focus:outline-none" />
        </div>
      </div>

      {/* ── Data Grid ────────────────────────────────────── */}
      <div className="overflow-auto" style={{ maxHeight: "calc(100vh - 120px)" }}>
        <table className="w-full text-[10px] font-mono border-collapse">
          <thead className="sticky top-0 z-10 bg-[#06060c]">
            <tr className="text-[8px] text-[#4a4a6a] uppercase tracking-wider border-b-2 border-[#1a1a2e]">
              <th className="px-1 py-1 text-left w-5 cursor-pointer select-none hover:text-[#ff8c00]" onClick={() => toggleSort("sport")}>S{si("sport")}</th>
              <th className="px-1 py-1 text-left cursor-pointer select-none hover:text-[#ff8c00]" onClick={() => toggleSort("team")}>GAME{si("team")}</th>
              <th className="px-1 py-1 text-center w-5">⊕</th>
              <th className="px-1 py-1 text-center border-l border-[#ff8c00]/20 text-[#ff8c00]/50">K BID</th>
              <th className="px-1 py-1 text-center text-[#ff8c00]/50">K ASK</th>
              <th className="px-1 py-1 text-center border-l border-[#00bfff]/20 text-[#00bfff]/50">PM BID</th>
              <th className="px-1 py-1 text-center text-[#00bfff]/50">PM ASK</th>
              <th className="px-1 py-1 text-center border-l border-[#1a1a2e] cursor-pointer select-none hover:text-[#ff8c00] w-10" onClick={() => toggleSort("spread")}>SPRD{si("spread")}</th>
              <th className="px-1 py-1 text-right border-l border-[#1a1a2e] cursor-pointer select-none hover:text-[#ff8c00]" onClick={() => toggleSort("k_depth")}>K DPT{si("k_depth")}</th>
              <th className="px-1 py-1 text-right cursor-pointer select-none hover:text-[#ff8c00]" onClick={() => toggleSort("pm_depth")}>PM DPT{si("pm_depth")}</th>
              <th className="px-1 py-1 text-center cursor-pointer select-none hover:text-[#ff8c00] w-9" onClick={() => toggleSort("imbalance")}>BAL{si("imbalance")}</th>
              <th className="px-1 py-1 w-14">LIQ</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((g, gi) => {
              const t1 = g.team1_prices;
              const t2 = g.team2_prices;
              const s1 = calcSpread(t1);
              const s2 = calcSpread(t2);
              const gs = g.best_spread;
              const isArb = gs >= 4;
              const isWatch = gs >= 2;
              const isLive = g.game_status === "in";
              const imb = imbInfo(g.k_depth ?? 0, g.pm_depth ?? 0);
              const isExp = expandedGame === g.cache_key;
              const bg = isArb ? "bg-[#00ff88]/[0.04]" : isWatch ? "bg-[#ff8c00]/[0.02]" : gi % 2 === 0 ? "" : "bg-white/[0.01]";
              const liveBdr = isLive ? "border-l-2 border-l-[#00ff88]" : "";

              return (
                <React.Fragment key={g.cache_key}>
                  {/* Team 1 */}
                  <tr className={`border-t border-[#1a1a2e]/40 hover:bg-[#ff8c00]/[0.05] cursor-pointer ${bg} ${liveBdr}`}
                    onClick={() => setExpandedGame(isExp ? null : g.cache_key)}>
                    <td className="px-1 py-[2px]" rowSpan={2}>
                      <span className={`text-[7px] font-bold px-0.5 ${sportBadge(g.sport)}`}>{g.sport}</span>
                    </td>
                    <td className="px-1 py-[2px]">
                      <span className="text-[#ff8c00]">{g.team1}</span>
                      {isLive && g.team1_score != null && <span className="text-[#00ff88] font-bold ml-1 text-[9px]">{g.team1_score}</span>}
                    </td>
                    <td className="px-1 py-[2px] text-center" rowSpan={2}>
                      {isLive ? <span className="inline-block w-1.5 h-1.5 bg-[#00ff88] animate-pulse" />
                        : g.traded ? <span className="text-[#00ff88] text-[7px]">✓</span>
                        : <span className="text-[#2a2a4a] text-[7px]">·</span>}
                    </td>
                    <td className="px-1 py-[2px] text-center border-l border-[#ff8c00]/10 text-[#00ff88]"><P v={t1?.k_bid ?? 0} /></td>
                    <td className="px-1 py-[2px] text-center text-[#ff6666]"><P v={t1?.k_ask ?? 0} /></td>
                    <td className="px-1 py-[2px] text-center border-l border-[#00bfff]/10 text-[#00ff88]"><P v={t1?.pm_bid ?? 0} /></td>
                    <td className="px-1 py-[2px] text-center text-[#ff6666]"><P v={t1?.pm_ask ?? 0} /></td>
                    <td className="px-1 py-[2px] text-center border-l border-[#1a1a2e]" rowSpan={2}>
                      {gs > 0 ? (
                        <span className={`font-bold ${isArb ? "text-[#00ff88] bg-[#00ff88]/10 px-1 border border-[#00ff88]/30" : isWatch ? "text-[#ff8c00]" : "text-[#4a4a6a]"}`}>
                          {gs.toFixed(1)}
                        </span>
                      ) : <span className="text-[#2a2a4a]">·</span>}
                    </td>
                    <td className="px-1 py-[2px] text-right border-l border-[#1a1a2e] text-[#ff8c00]/70" rowSpan={2}>{g.k_depth ? fmtNum(g.k_depth) : "—"}</td>
                    <td className="px-1 py-[2px] text-right text-[#00bfff]/70" rowSpan={2}>{g.pm_depth ? fmtNum(g.pm_depth) : "—"}</td>
                    <td className={`px-1 py-[2px] text-center text-[8px] ${imb.color}`} rowSpan={2}>{imb.label}</td>
                    <td className="px-1 py-[2px]" rowSpan={2}><DepthBar k={g.k_depth ?? 0} pm={g.pm_depth ?? 0} /></td>
                  </tr>
                  {/* Team 2 */}
                  <tr className={`hover:bg-[#ff8c00]/[0.05] cursor-pointer ${bg} ${liveBdr}`}
                    onClick={() => setExpandedGame(isExp ? null : g.cache_key)}>
                    <td className="px-1 py-[2px]">
                      <span className="text-[#ff8c00]/60">{g.team2}</span>
                      {isLive && g.team2_score != null && <span className="text-[#00ff88] font-bold ml-1 text-[9px]">{g.team2_score}</span>}
                    </td>
                    <td className="px-1 py-[2px] text-center border-l border-[#ff8c00]/10 text-[#00ff88]/60"><P v={t2?.k_bid ?? 0} /></td>
                    <td className="px-1 py-[2px] text-center text-[#ff6666]/60"><P v={t2?.k_ask ?? 0} /></td>
                    <td className="px-1 py-[2px] text-center border-l border-[#00bfff]/10 text-[#00ff88]/60"><P v={t2?.pm_bid ?? 0} /></td>
                    <td className="px-1 py-[2px] text-center text-[#ff6666]/60"><P v={t2?.pm_ask ?? 0} /></td>
                  </tr>
                  {/* Expanded detail */}
                  {isExp && (
                    <tr className="bg-[#0c0c14]">
                      <td colSpan={12} className="px-2 py-2 border-t border-[#ff8c00]/20">
                        <div className="grid grid-cols-4 gap-2 text-[9px] font-mono">
                          {/* Arb Breakdown */}
                          <div className="border border-[#1a1a2e] p-1.5">
                            <div className="text-[7px] text-[#4a4a6a] uppercase tracking-wider mb-1">ARB VECTORS</div>
                            {[{ l: g.team1, s: s1 }, { l: g.team2, s: s2 }].map(({ l, s }) => (
                              <div key={l} className="flex justify-between py-0.5">
                                <span className="text-[#4a4a6a]">{l}</span>
                                <span>
                                  <span className={s.buyPM >= 4 ? "text-[#00ff88] font-bold" : s.buyPM > 0 ? "text-[#ff8c00]" : "text-[#3a3a5a]"}>
                                    {s.buyPM > 0 ? `↑PM ${s.buyPM}c` : "—"}
                                  </span>
                                  <span className="text-[#2a2a4a] mx-1">│</span>
                                  <span className={s.buyK >= 4 ? "text-[#00ff88] font-bold" : s.buyK > 0 ? "text-[#ff8c00]" : "text-[#3a3a5a]"}>
                                    {s.buyK > 0 ? `↑K ${s.buyK}c` : "—"}
                                  </span>
                                </span>
                              </div>
                            ))}
                          </div>
                          {/* Price delta */}
                          <div className="border border-[#1a1a2e] p-1.5">
                            <div className="text-[7px] text-[#4a4a6a] uppercase tracking-wider mb-1">K – PM DELTA (BID)</div>
                            {[{ l: g.team1, k: t1?.k_bid ?? 0, p: t1?.pm_bid ?? 0 },
                              { l: g.team2, k: t2?.k_bid ?? 0, p: t2?.pm_bid ?? 0 }].map(({ l, k, p }) => {
                              const d = k - p;
                              return (
                                <div key={l} className="flex items-center gap-1 py-0.5">
                                  <span className="text-[#4a4a6a] w-8">{l}</span>
                                  <div className="flex-1 h-[8px] bg-[#1a1a2e] relative overflow-hidden">
                                    {d > 0 && <div className="absolute left-1/2 h-full bg-[#ff8c00]/50" style={{ width: `${Math.min(Math.abs(d), 50)}%` }} />}
                                    {d < 0 && <div className="absolute right-1/2 h-full bg-[#00bfff]/50" style={{ width: `${Math.min(Math.abs(d), 50)}%` }} />}
                                    {d === 0 && <div className="absolute left-1/2 w-px h-full bg-[#4a4a6a]" />}
                                  </div>
                                  <span className={`w-6 text-right ${d > 0 ? "text-[#ff8c00]" : d < 0 ? "text-[#00bfff]" : "text-[#4a4a6a]"}`}>
                                    {d > 0 ? "+" : ""}{d}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                          {/* Depth */}
                          <div className="border border-[#1a1a2e] p-1.5">
                            <div className="text-[7px] text-[#4a4a6a] uppercase tracking-wider mb-1">DEPTH PROFILE</div>
                            <div className="flex justify-between py-0.5">
                              <span className="text-[#ff8c00]">K: {g.k_depth ? fmtNum(g.k_depth) : "—"}</span>
                              <span className="text-[#00bfff]">PM: {g.pm_depth ? fmtNum(g.pm_depth) : "—"}</span>
                            </div>
                            <DepthBar k={g.k_depth ?? 0} pm={g.pm_depth ?? 0} />
                            <div className={`text-center mt-1 ${imb.color}`}>{imb.label}</div>
                          </div>
                          {/* Meta */}
                          <div className="border border-[#1a1a2e] p-1.5">
                            <div className="text-[7px] text-[#4a4a6a] uppercase tracking-wider mb-1">MARKET META</div>
                            <div className="space-y-0.5 text-[#4a4a6a]">
                              <div className="flex justify-between"><span>Date</span><span className="text-[#ff8c00]">{g.date}</span></div>
                              <div className="flex justify-between"><span>Slug</span><span className="text-[#00bfff] text-[7px]">{g.pm_slug?.slice(0, 22)}</span></div>
                              {isLive && <div className="flex justify-between border-t border-[#1a1a2e] pt-0.5 mt-0.5"><span>Score</span><span className="text-[#00ff88] font-bold">{g.team1_score} – {g.team2_score} {g.period} {g.clock}</span></div>}
                              {g.traded && <div className="flex justify-between border-t border-[#1a1a2e] pt-0.5 mt-0.5"><span>Traded</span><span className="text-[#00ff88] font-bold">✓</span></div>}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
        {sorted.length === 0 && (
          <div className="text-center py-12">
            <span className="text-[#3a3a5a] font-mono text-[10px] uppercase tracking-wider">
              NO ACTIVE BOOKS{sportFilter !== "ALL" ? ` FOR ${sportFilter}` : ""} — WAITING FOR MARKETS
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
