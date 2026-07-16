"use client";

import React, { useMemo, useState } from "react";
import type { SettledRow } from "./types";
import { catBadgeColor, fmtSignedCents } from "./helpers";
import { CollapsibleSection } from "./CollapsibleSection";
import { TimelineGlyph } from "./TimelineGlyph";

interface Props {
  rows: SettledRow[];
  countLabel: number;
}

/** Small badge for the placed-vs-scheduled delta, replacing a dedicated column. */
function SchedDeltaBadge({ deltaMin }: { deltaMin: number }) {
  if (!deltaMin) return <span className="text-[#ffffff]/30">Δ0</span>;
  const hrs = deltaMin / 60;
  const color = Math.abs(deltaMin) >= 180 ? "#c0505a" : Math.abs(deltaMin) >= 60 ? "#ff8c00" : "#7aa8d6";
  return (
    <span
      className="text-[8px] font-mono px-1 rounded-none border"
      style={{ color, borderColor: `${color}55` }}
      title={`Real bell vs Kalshi's scheduled start: ${deltaMin >= 0 ? "+" : ""}${deltaMin}m`}
    >
      Δ{deltaMin >= 0 ? "+" : ""}{hrs.toFixed(1)}h
    </span>
  );
}

/** Hover-only detail: W1-best and best-tick-after-fill, collapsed out of the
 * visible column set per the adversarial pass (both are context-on-demand,
 * not decision-critical at a glance). */
function DetailHover({ row }: { row: SettledRow }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-block">
      <button
        onClick={() => setOpen(!open)}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        className="text-[8px] font-mono text-[#ffffff]/40 border border-[#1a1a2e] px-1 hover:text-[#00bfff] hover:border-[#00bfff]/40 rounded-none"
      >
        i
      </button>
      {open && (
        <div className="absolute z-30 right-0 top-full mt-1 bg-black border border-[#1a1a2e] px-2 py-1.5 text-[8px] font-mono whitespace-nowrap text-left">
          <div className="text-[#ffffff]/50 uppercase tracking-wider mb-1">detail</div>
          <div className="text-[#ffffff]">
            W1-best:{" "}
            <span className="text-[#00bfff]">
              {row.w1BestCents != null ? `${row.w1BestCents}¢ @${row.w1BestAt}` : row.w1BestNote ?? "—"}
            </span>
          </div>
          <div className="text-[#ffffff]">
            Best tick after fill:{" "}
            <span className="text-[#00bfff]">
              {row.bestTickAfterFillCents != null ? `${row.bestTickAfterFillCents}¢ @${row.bestTickAfterFillAt}` : row.bestTickAfterFillNote ?? "—"}
            </span>
          </div>
          <div className="text-[#ffffff]">
            Bell src: <span className="text-[#ff8c00]">{row.realBellSource || "—"}</span>
          </div>
          <div className="text-[#ffffff]">
            Exit required: <span className="text-[#ff8c00]">{row.exitRequiredCents}¢ (+{row.exitRequiredDeltaCents})</span>
          </div>
        </div>
      )}
    </span>
  );
}

type SortMode = "default" | "lossesFirst";

export function SettledSection({ rows, countLabel }: Props) {
  const [sortMode, setSortMode] = useState<SortMode>("default");

  const stats = useMemo(() => {
    let totalCents = 0;
    let wins = 0;
    let losses = 0;
    for (const r of rows) {
      totalCents += r.pnlCents;
      if (r.outcome === "win") wins++;
      else losses++;
    }
    return { totalCents, wins, losses, winRate: rows.length ? ((wins / rows.length) * 100).toFixed(0) : "0" };
  }, [rows]);

  const displayRows = useMemo(() => {
    if (sortMode === "default") return rows;
    // losses to top, preserving relative order within each group
    return [...rows].sort((a, b) => {
      const aLoss = a.outcome === "loss" ? 0 : 1;
      const bLoss = b.outcome === "loss" ? 0 : 1;
      return aLoss - bLoss;
    });
  }, [rows, sortMode]);

  return (
    <CollapsibleSection
      title="① SETTLED"
      count={rows.length}
      countLabel={countLabel}
      accent="#00ff88"
      summary={
        <>
          <span className={`font-bold ${stats.totalCents >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
            {fmtSignedCents(stats.totalCents)}
          </span>
          <span className="text-[#1a1a2e]">|</span>
          <span className="text-[#00ff88]">{stats.wins}W</span>
          <span className="text-[#ff3333]">{stats.losses}L</span>
          <span className="text-[#ffffff]/50">({stats.winRate}%)</span>
        </>
      }
    >
      <div className="px-2 pt-1.5 flex items-center justify-end">
        <button
          onClick={() => setSortMode(sortMode === "default" ? "lossesFirst" : "default")}
          className={`text-[8px] font-mono px-1.5 py-0.5 border rounded-none ${
            sortMode === "lossesFirst"
              ? "bg-[#ff3333]/20 text-[#ff3333] border-[#ff3333]/40"
              : "text-[#ffffff]/50 border-[#1a1a2e] hover:text-[#ff8c00]"
          }`}
        >
          {sortMode === "lossesFirst" ? "✓ LOSSES ON TOP" : "SORT: LOSSES ON TOP"}
        </button>
      </div>
      <div className="overflow-x-hidden" style={{ maxHeight: 420, overflowY: "auto" }}>
        <table className="w-full text-xs table-fixed">
          <colgroup>
            <col style={{ width: "26%" }} />
            <col style={{ width: "8%" }} />
            <col style={{ width: "5%" }} />
            <col style={{ width: "8%" }} />
            <col style={{ width: "17%" }} />
            <col style={{ width: "10%" }} />
            <col style={{ width: "16%" }} />
            <col style={{ width: "10%" }} />
          </colgroup>
          <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
            <tr className="text-[#ffffff]">
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">MATCH</th>
              <th className="px-1 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">CAT</th>
              <th className="px-1 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">LEG</th>
              <th className="px-1 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">BASIS</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">TIMELINE</th>
              <th className="px-1 py-1.5 text-center font-mono text-[9px] uppercase tracking-wider font-medium">vs SCHED</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">CLOSE</th>
              <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">$</th>
            </tr>
          </thead>
          <tbody>
            {displayRows.map((r, i) => {
              const isOdd = i % 2 === 1;
              const rowLossHighlight = r.outcome === "loss" ? "bg-[#c0505a]/[0.04]" : "";
              return (
                <tr
                  key={`${r.match}-${r.leg}-${i}`}
                  className={`border-b border-[#1a1a2e]/50 hover:bg-white/[0.03] transition-colors ${isOdd ? "bg-white/[0.02]" : ""} ${rowLossHighlight}`}
                >
                  <td className="px-2 py-1 truncate" title={r.match}>
                    <span className="font-mono text-[10px] text-[#ffffff]">{r.match}</span>
                    {r.carried && <span className="text-[#7aa8d6] ml-1" title="Carried over from a prior session">◐</span>}
                  </td>
                  <td className="px-1 py-1">
                    <span className={`inline-block rounded-none px-1 py-0.5 text-[7px] font-mono ${catBadgeColor(r.cat)}`}>
                      {r.cat.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-1 py-1 font-mono text-[10px] text-[#ff8c00] font-bold">{r.leg}</td>
                  <td className="px-1 py-1 text-right font-mono text-[9px] text-[#ffffff]/70">{r.bandCents}¢</td>
                  <td className="px-2 py-1">
                    <div className="flex items-center gap-1">
                      <TimelineGlyph row={r} />
                      <DetailHover row={r} />
                    </div>
                  </td>
                  <td className="px-1 py-1 text-center">
                    <SchedDeltaBadge deltaMin={r.schedDeltaMin} />
                  </td>
                  <td className="px-2 py-1 font-mono text-[9px] text-[#ffffff]/80 truncate" title={r.closeLabel}>
                    {r.closeLabel}
                  </td>
                  <td className="px-2 py-1 text-right font-mono text-[10px] font-bold">
                    <span className={r.outcome === "win" ? "text-[#00ff88]" : "text-[#ff3333]"}>
                      {fmtSignedCents(r.pnlCents)}
                    </span>
                    <span className="text-[#ffffff]/40 text-[8px] ml-1">
                      ({r.pnlPctOfBasis >= 0 ? "+" : ""}{r.pnlPctOfBasis}% of {r.fillCents}¢)
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </CollapsibleSection>
  );
}
