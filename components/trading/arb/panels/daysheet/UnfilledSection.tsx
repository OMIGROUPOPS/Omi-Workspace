"use client";

import React, { useMemo, useState } from "react";
import type { UnfilledRow, UnfilledReason } from "./types";
import { catBadgeColor } from "./helpers";
import { CollapsibleSection } from "./CollapsibleSection";

interface Props {
  rows: UnfilledRow[];
  countLabel: number;
}

const REASON_FILTERS: { key: UnfilledReason | "all"; label: string; color: string }[] = [
  { key: "all", label: "ALL", color: "#ffffff" },
  { key: "never_traded_that_low", label: "NEVER TRADED THAT LOW", color: "#7aa8d6" },
  { key: "we_pulled_it", label: "WE PULLED IT", color: "#ff8c00" },
  { key: "traded_but_late", label: "TRADED, ARRIVED LATE", color: "#c0505a" },
];

/** Renders the bucket's "Why unfilled" text exactly as sourced — this bucket's
 * language is required to stay verbatim, no paraphrasing or restyling. */
function WhyUnfilled({ row }: { row: UnfilledRow }) {
  return <span className="font-mono text-[9px] text-[#ffffff]/80">{row.reasonRaw}</span>;
}

export function UnfilledSection({ rows, countLabel }: Props) {
  const [filter, setFilter] = useState<UnfilledReason | "all">("all");

  const counts = useMemo(() => {
    const c: Record<string, number> = { never_traded_that_low: 0, we_pulled_it: 0, traded_but_late: 0 };
    for (const r of rows) c[r.reason] = (c[r.reason] ?? 0) + 1;
    return c;
  }, [rows]);

  const filteredRows = useMemo(() => (filter === "all" ? rows : rows.filter((r) => r.reason === filter)), [rows, filter]);

  return (
    <CollapsibleSection
      title="③ POSTED, DID NOT FILL"
      count={rows.length}
      countLabel={countLabel}
      accent="#f0c750"
      defaultCollapsed
      summary={
        <>
          <span className="text-[#7aa8d6]">{counts.never_traded_that_low} never traded low</span>
          <span className="text-[#ff8c00]">{counts.we_pulled_it} pulled</span>
          <span className="text-[#c0505a]">{counts.traded_but_late} arrived late</span>
        </>
      }
    >
      <div className="px-2 pt-1.5 flex items-center gap-1 flex-wrap">
        {REASON_FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className="text-[8px] font-mono px-1.5 py-0.5 border rounded-none transition-colors"
            style={
              filter === f.key
                ? { backgroundColor: `${f.color}22`, color: f.color, borderColor: `${f.color}66` }
                : { color: "#ffffff88", borderColor: "#1a1a2e" }
            }
          >
            {f.label}
          </button>
        ))}
      </div>
      <div className="overflow-x-hidden" style={{ maxHeight: 380, overflowY: "auto" }}>
        <table className="w-full text-xs table-fixed">
          <colgroup>
            <col style={{ width: "28%" }} />
            <col style={{ width: "10%" }} />
            <col style={{ width: "6%" }} />
            <col style={{ width: "8%" }} />
            <col style={{ width: "14%" }} />
            <col style={{ width: "34%" }} />
          </colgroup>
          <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
            <tr className="text-[#ffffff]">
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">MATCH</th>
              <th className="px-1 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">CAT</th>
              <th className="px-1 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">LEG</th>
              <th className="px-1 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">AIM</th>
              <th className="px-1 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">TAPE LOW</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">WHY UNFILLED</th>
            </tr>
          </thead>
          <tbody>
            {filteredRows.map((r, i) => (
              <tr key={`${r.match}-${r.leg}-${i}`} className={`border-b border-[#1a1a2e]/50 ${i % 2 === 1 ? "bg-white/[0.02]" : ""}`}>
                <td className="px-2 py-1 truncate font-mono text-[10px] text-[#ffffff]" title={r.match}>{r.match}</td>
                <td className="px-1 py-1">
                  <span className={`inline-block rounded-none px-1 py-0.5 text-[7px] font-mono ${catBadgeColor(r.cat)}`}>
                    {r.cat.replace("_", " ")}
                  </span>
                </td>
                <td className="px-1 py-1 font-mono text-[10px] text-[#ff8c00] font-bold">{r.leg}</td>
                <td className="px-1 py-1 text-right font-mono text-[9px] text-[#ffffff]/70">{r.aimCents}¢</td>
                <td className="px-1 py-1 text-right font-mono text-[9px] text-[#ffffff]/70">
                  {r.tapeLowCents != null ? `${r.tapeLowCents}¢ @${r.tapeLowAt}` : "—"}
                </td>
                <td className="px-2 py-1">
                  <WhyUnfilled row={r} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </CollapsibleSection>
  );
}
