"use client";

import React, { useState } from "react";
import { useDaySheetData } from "./useDaySheetData";
import { DaySheetHeaderStrip } from "./DaySheetHeaderStrip";
import { PairsSection } from "./PairsSection";
import { SettledSection } from "./SettledSection";
import { OpenSection } from "./OpenSection";
import { UnfilledSection } from "./UnfilledSection";
import { NotBidSection } from "./NotBidSection";

type ViewTab = "pairs" | "buckets";

/**
 * Drop-in panel for the arb tracker page (app/(app)/dashboard/arb). Renders
 * .claude/today_sheet/LATEST.md as a single fixed-viewport block — every
 * child section scrolls internally (see maxHeight + overflowY on each table
 * wrapper) rather than letting the page grow horizontally or vertically
 * unbounded. No element in this tree sets a fixed pixel width wider than its
 * parent, and every table uses table-fixed + truncate so long match names
 * never force horizontal scroll.
 *
 * PRIMARY VIEW (operator instruction, 2026-07-16): PER-GAME PAIRS — both legs
 * of each match side by side, per §0A's frame that the whole game is filling
 * BOTH sides of a match in Window 1 at a fair price. The four original
 * buckets (SETTLED / OPEN / UNFILLED / NOT-BID) are demoted to a secondary
 * "BUCKETS" tab — still fully present, just no longer the default view.
 */
export function DaySheetPanel() {
  const { sheet, fetchError, isStale, hasData, fetchData } = useDaySheetData();
  const [tab, setTab] = useState<ViewTab>("pairs");

  return (
    <div className="w-full max-w-full overflow-x-hidden flex flex-col gap-2">
      <DaySheetHeaderStrip
        header={
          sheet?.header ?? {
            dateLabel: "—",
            generatedAt: "—",
            nav: 0,
            tailCents: 0,
            pathCents: 0,
            wageredToday: 0,
            pOfferedPct: 0,
            pOfferedFilled: 0,
            pOfferedPosted: 0,
            pMarketPct: 0,
            pMarketFilledLegs: 0,
            pMarketListedLegs: 0,
            pMarketListedLegsApprox: false,
          }
        }
        isStale={isStale}
        fetchError={fetchError}
        sourceMtimeIso={sheet?.meta.sourceMtimeIso ?? null}
      />

      {!hasData && !fetchError && (
        <div className="p-6 text-center text-[10px] font-mono text-[#ffffff]/50">LOADING DAY SHEET…</div>
      )}
      {fetchError && (
        <div className="p-3 text-center text-[10px] font-mono text-[#ff3333]">
          COULD NOT REACH /api/daysheet —{" "}
          <button onClick={fetchData} className="underline hover:text-[#ff8c00]">
            retry
          </button>
        </div>
      )}

      {sheet && (
        <div className="flex flex-col gap-2 px-0">
          <div className="flex items-center gap-1.5 px-0.5">
            <button
              onClick={() => setTab("pairs")}
              className={`text-[9px] font-mono px-2.5 py-1 border rounded-none uppercase tracking-widest ${
                tab === "pairs"
                  ? "bg-[#ff8c00]/20 text-[#ff8c00] border-[#ff8c00]/50 font-bold"
                  : "text-[#ffffff]/50 border-[#1a1a2e] hover:text-[#ff8c00]"
              }`}
            >
              PER-GAME PAIRS
            </button>
            <button
              onClick={() => setTab("buckets")}
              className={`text-[9px] font-mono px-2.5 py-1 border rounded-none uppercase tracking-widest ${
                tab === "buckets"
                  ? "bg-white/10 text-[#ffffff] border-white/30 font-bold"
                  : "text-[#ffffff]/50 border-[#1a1a2e] hover:text-[#ffffff]"
              }`}
            >
              SETTLED / OPEN / UNFILLED / NOT-BID
            </button>
          </div>

          {tab === "pairs" && (
            <PairsSection settled={sheet.settled} open={sheet.open} unfilled={sheet.unfilled} notBid={sheet.notBid} />
          )}

          {tab === "buckets" && (
            <>
              <SettledSection rows={sheet.settled} countLabel={sheet.meta.settledCountLabel} />
              <OpenSection rows={sheet.open} />
              <UnfilledSection rows={sheet.unfilled} countLabel={sheet.meta.unfilledCountLabel} />
              <NotBidSection
                groups={sheet.notBidGrouped}
                countLabel={sheet.meta.notBidCountLabel}
                totalRows={sheet.notBid.length}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}
