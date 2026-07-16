"use client";

import React, { useState } from "react";
import type { NotBidGroup, NotBidRow } from "./types";
import { catBadgeColor } from "./helpers";
import { CollapsibleSection } from "./CollapsibleSection";

interface Props {
  groups: NotBidGroup[];
  countLabel: number;
  totalRows: number;
}

function GroupRow({ group }: { group: NotBidGroup }) {
  const [expanded, setExpanded] = useState(false);
  const intent = group.rows[0]?.intent;
  const intentColor = intent === "intentional" ? "#4dd68c" : "#8993a3";

  return (
    <div className="border-b border-[#1a1a2e]">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-white/[0.02] transition-colors text-left"
      >
        <span className="text-[#ffffff]/50 text-[9px]">{expanded ? "▼" : "▶"}</span>
        <span className="font-mono text-[10px] text-[#ffffff]">{group.plainReason}</span>
        <span
          className="text-[7px] font-mono uppercase px-1 rounded-none border"
          style={{ color: intentColor, borderColor: `${intentColor}55` }}
        >
          {intent === "intentional" ? "INTENTIONAL" : "NEVER REACHED DECISION"}
        </span>
        <span className="font-mono text-[10px] font-bold text-[#f0c750] ml-auto">{group.count}</span>
        <span className="flex items-center gap-1 ml-2">
          {Object.entries(group.byCategory)
            .sort((a, b) => b[1] - a[1])
            .map(([cat, n]) => (
              <span key={cat} className={`inline-block rounded-none px-1 py-0.5 text-[7px] font-mono ${catBadgeColor(cat)}`}>
                {cat.replace("_", " ")} {n}
              </span>
            ))}
        </span>
      </button>
      {expanded && (
        <div className="max-h-64 overflow-y-auto bg-black/40">
          <table className="w-full text-xs table-fixed">
            <colgroup>
              <col style={{ width: "45%" }} />
              <col style={{ width: "15%" }} />
              <col style={{ width: "40%" }} />
            </colgroup>
            <tbody>
              {group.rows.map((r: NotBidRow, i: number) => (
                <tr key={`${r.match}-${i}`} className={`border-b border-[#1a1a2e]/30 ${i % 2 === 1 ? "bg-white/[0.02]" : ""}`}>
                  <td className="px-3 py-1 font-mono text-[9px] text-[#ffffff]/80 truncate" title={r.match}>{r.match}</td>
                  <td className="px-1 py-1">
                    <span className={`inline-block rounded-none px-1 py-0.5 text-[7px] font-mono ${catBadgeColor(r.cat)}`}>
                      {r.cat.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-2 py-1 font-mono text-[8px] text-[#ffffff]/40">{r.tapeNote}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export function NotBidSection({ groups, countLabel, totalRows }: Props) {
  return (
    <CollapsibleSection
      title="④ NOT BID"
      count={totalRows}
      countLabel={countLabel}
      accent="#8993a3"
      defaultCollapsed
      summary={<span className="text-[#ffffff]/50">grouped by reason, {groups.length} reasons</span>}
    >
      <div>
        {groups.map((g) => (
          <GroupRow key={g.plainReason} group={g} />
        ))}
      </div>
    </CollapsibleSection>
  );
}
