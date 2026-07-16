"use client";

import React from "react";
import type { OpenRow } from "./types";
import { catBadgeColor } from "./helpers";
import { CollapsibleSection } from "./CollapsibleSection";

interface Props {
  rows: OpenRow[];
}

export function OpenSection({ rows }: Props) {
  return (
    <CollapsibleSection
      title="② OPEN"
      count={rows.length}
      accent="#00bfff"
      summary={<span className="text-[#ffffff]/50">live positions, unresolved</span>}
    >
      {rows.length === 0 ? (
        <div className="p-4 text-center text-[10px] font-mono text-[#ffffff]/50">NO OPEN POSITIONS</div>
      ) : (
        <div className="overflow-x-hidden">
          <table className="w-full text-xs table-fixed">
            <colgroup>
              <col style={{ width: "24%" }} />
              <col style={{ width: "8%" }} />
              <col style={{ width: "5%" }} />
              <col style={{ width: "8%" }} />
              <col style={{ width: "9%" }} />
              <col style={{ width: "9%" }} />
              <col style={{ width: "12%" }} />
              <col style={{ width: "25%" }} />
            </colgroup>
            <thead className="border-b border-[#1a1a2e]">
              <tr className="text-[#ffffff]">
                <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">MATCH</th>
                <th className="px-1 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">CAT</th>
                <th className="px-1 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">LEG</th>
                <th className="px-1 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">FILL</th>
                <th className="px-1 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">MARK</th>
                <th className="px-1 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">vs BASIS</th>
                <th className="px-1 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">EXIT REQ</th>
                <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">EXIT RESTING</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={`${r.match}-${r.leg}-${i}`} className={`border-b border-[#1a1a2e]/50 ${i % 2 === 1 ? "bg-white/[0.02]" : ""}`}>
                  <td className="px-2 py-1.5 truncate" title={r.match}>
                    <span className="font-mono text-[10px] text-[#ffffff]">{r.match}</span>
                    {r.carried && <span className="text-[#7aa8d6] ml-1" title="Carried over from a prior session">◐</span>}
                  </td>
                  <td className="px-1 py-1.5">
                    <span className={`inline-block rounded-none px-1 py-0.5 text-[7px] font-mono ${catBadgeColor(r.cat)}`}>
                      {r.cat.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-1 py-1.5 font-mono text-[10px] text-[#ff8c00] font-bold">{r.leg}</td>
                  <td className="px-1 py-1.5 text-right font-mono text-[10px] text-[#ffffff]">{r.fillCents}¢</td>
                  <td className="px-1 py-1.5 text-right font-mono text-[10px] text-[#00bfff] font-bold">{r.markCents}¢</td>
                  <td className={`px-1 py-1.5 text-right font-mono text-[10px] font-bold ${r.markVsBasisCents >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
                    {r.markVsBasisCents >= 0 ? "+" : ""}{r.markVsBasisCents}¢
                  </td>
                  <td className="px-1 py-1.5 text-right font-mono text-[9px] text-[#ffffff]/70">
                    {r.exitRequiredCents}¢ (+{r.exitRequiredDeltaCents})
                  </td>
                  <td className="px-2 py-1.5 font-mono text-[9px] text-[#ffffff]/70">
                    {r.exitRestingCents}¢ ×{r.exitRestingQty}{" "}
                    <span className="text-[#ffffff]/40">({r.exitOrderId})</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </CollapsibleSection>
  );
}
