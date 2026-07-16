"use client";

import React from "react";
import type { DaySheetHeader as Header } from "./types";
import { fmtSignedDollars } from "./helpers";

interface Props {
  header: Header;
  isStale: boolean;
  fetchError: boolean;
  sourceMtimeIso: string | null;
}

function fmtAsOf(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString("en-US", {
    timeZone: "America/New_York",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function DaySheetHeaderStrip({ header, isStale, fetchError, sourceMtimeIso }: Props) {
  const tailColor = header.tailCents >= 0 ? "text-[#00ff88]" : "text-[#ff3333]";
  const pathColor = header.pathCents >= 0 ? "text-[#00ff88]" : "text-[#ff3333]";

  return (
    <div className="border-b border-[#1a1a2e] bg-black">
      <div className="h-[2px] bg-[#ff8c00] w-full" />
      <div className="px-3 py-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <span className="text-[11px] font-mono font-bold text-[#ff8c00] uppercase tracking-widest">
          DAY SHEET
        </span>
        <span className="text-[9px] font-mono text-[#ffffff]/60">{header.dateLabel}</span>
        <span className="text-[#1a1a2e]">|</span>

        <span className="text-[9px] font-mono text-[#ffffff]">
          NAV <span className="text-[#ff8c00] font-bold">${header.nav.toFixed(2)}</span>
        </span>
        <span className="text-[#1a1a2e]">|</span>

        <span className="text-[9px] font-mono text-[#ffffff]">
          TAIL <span className={`font-bold ${tailColor}`}>{header.tailCents >= 0 ? "+" : ""}{header.tailCents}¢</span>
        </span>
        <span className="text-[9px] font-mono text-[#ffffff]">
          PATH <span className={`font-bold ${pathColor}`}>{header.pathCents >= 0 ? "+" : ""}{header.pathCents}¢</span>
        </span>
        <span className="text-[#1a1a2e]">|</span>

        <span className="text-[9px] font-mono text-[#ffffff]">
          WAGERED <span className="text-[#00bfff] font-bold">${header.wageredToday.toFixed(2)}</span>
        </span>
        <span className="text-[#1a1a2e]">|</span>

        <span className="text-[9px] font-mono text-[#ffffff]" title="Executor: filled / posted-unfilled">
          P-OFFERED <span className="text-[#8b5cf6] font-bold">{header.pOfferedPct}%</span>
          <span className="text-[#ffffff]/50 ml-1">({header.pOfferedFilled}/{header.pOfferedPosted})</span>
        </span>
        <span className="text-[9px] font-mono text-[#ffffff]" title="Funnel: filled legs / listed legs">
          P-MARKET <span className="text-[#8b5cf6] font-bold">{header.pMarketPct}%</span>
          <span className="text-[#ffffff]/50 ml-1">
            ({header.pMarketFilledLegs}/{header.pMarketListedLegsApprox ? "~" : ""}{header.pMarketListedLegs})
          </span>
        </span>

        <span className="ml-auto flex items-center gap-2">
          <span className={`text-[9px] font-mono uppercase tracking-wider ${fetchError ? "text-[#ff3333]" : isStale ? "text-[#ff8c00] animate-pulse" : "text-[#ffffff]/50"}`}>
            {fetchError ? "CONN ERR" : isStale ? "STALE" : `as of ${fmtAsOf(sourceMtimeIso)}`}
          </span>
        </span>
      </div>
    </div>
  );
}
