"use client";

import React, { useState } from "react";
import { buildTimelinePoints } from "./helpers";
import type { SettledRow } from "./types";

interface Props {
  row: SettledRow;
}

const GLYPH_WIDTH = 96;
const GLYPH_HEIGHT = 16;

/**
 * Compact per-row timeline: placed -> filled -> bell -> close on one small
 * time axis. Points are plotted at even intervals along the axis (this is a
 * sequence glyph, not a true-to-scale time chart — spans can range from
 * minutes to over 24h for ◐carried rows, so literal proportional spacing
 * would make most points collide at one end). Hovering a dot shows the exact
 * clock time. Post-bell fills are flagged red per spec.
 */
export function TimelineGlyph({ row }: Props) {
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const points = buildTimelinePoints(row);
  const n = points.length;
  const usableWidth = GLYPH_WIDTH - 8;

  const xFor = (i: number) => 4 + (usableWidth * i) / (n - 1);
  const midY = GLYPH_HEIGHT / 2;

  return (
    <div className="relative inline-block" style={{ width: GLYPH_WIDTH, height: GLYPH_HEIGHT }}>
      <svg width={GLYPH_WIDTH} height={GLYPH_HEIGHT} className="block">
        {/* connecting line */}
        <line x1={xFor(0)} y1={midY} x2={xFor(n - 1)} y2={midY} stroke="#232834" strokeWidth={1} />
        {points.map((p, i) => {
          const isFilled = p.key === "filled";
          const flagRed = isFilled && row.postBellFill;
          const color = flagRed ? "#c0505a" : p.color;
          return (
            <g
              key={p.key}
              onMouseEnter={() => setHoverIdx(i)}
              onMouseLeave={() => setHoverIdx(null)}
              style={{ cursor: "pointer" }}
            >
              <circle cx={xFor(i)} cy={midY} r={hoverIdx === i ? 4 : 2.75} fill={color} stroke={flagRed ? "#c0505a" : "none"} strokeWidth={flagRed ? 1.5 : 0} />
            </g>
          );
        })}
      </svg>
      {hoverIdx !== null && (
        <div
          className="absolute z-20 bg-black border border-[#1a1a2e] px-1.5 py-1 text-[8px] font-mono whitespace-nowrap text-white"
          style={{
            left: Math.min(Math.max(xFor(hoverIdx) - 30, 0), GLYPH_WIDTH - 60),
            top: GLYPH_HEIGHT + 2,
          }}
        >
          <span className="uppercase text-[#ffffff]/60">{points[hoverIdx].key}</span>{" "}
          <span className={hoverIdx === 1 && row.postBellFill ? "text-[#c0505a] font-bold" : "text-[#ff8c00]"}>
            {points[hoverIdx].label}
          </span>
          {hoverIdx === 1 && row.postBellFill && (
            <div className="text-[#c0505a] text-[7px] mt-0.5">FILLED AFTER BELL</div>
          )}
        </div>
      )}
    </div>
  );
}
