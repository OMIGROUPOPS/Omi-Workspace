"use client";

import React, { useState } from "react";

interface Props {
  title: string;
  count: number;
  countLabel?: number; // optional: header count from source, may differ from actual rows
  accent: string; // hex
  summary?: React.ReactNode;
  defaultCollapsed?: boolean;
  children: React.ReactNode;
}

export function CollapsibleSection({ title, count, countLabel, accent, summary, defaultCollapsed = false, children }: Props) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const countMismatch = countLabel != null && !Number.isNaN(countLabel) && countLabel !== count;

  return (
    <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-[2px]" style={{ backgroundColor: accent }} />
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full px-3 py-1.5 bg-black border-b border-[#1a1a2e] flex items-center gap-3 text-[9px] font-mono hover:bg-white/[0.02] transition-colors"
      >
        <span style={{ color: accent }}>{collapsed ? "▶" : "▼"}</span>
        <span className="text-[#ffffff] uppercase tracking-widest">{title}</span>
        <span className="font-bold" style={{ color: accent }}>
          {count}
          {countMismatch && (
            <span className="text-[#c0505a] ml-1" title={`Source heading says (${countLabel}) — actual parsed row count is ${count}. Flagging, not silently reconciling.`}>
              ⚠ hdr says {countLabel}
            </span>
          )}
        </span>
        {summary && (
          <>
            <span className="text-[#1a1a2e]">|</span>
            {summary}
          </>
        )}
      </button>
      {!collapsed && <div>{children}</div>}
    </div>
  );
}
