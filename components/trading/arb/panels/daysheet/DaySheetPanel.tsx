"use client";

import React from "react";
import { useDaySheetData } from "./useDaySheetData";
import { DaySheetHeaderStrip } from "./DaySheetHeaderStrip";
import { SettledSection } from "./SettledSection";
import { OpenSection } from "./OpenSection";
import { UnfilledSection } from "./UnfilledSection";
import { NotBidSection } from "./NotBidSection";

/**
 * Drop-in panel for the arb tracker page (app/(app)/dashboard/arb). Renders
 * .claude/today_sheet/LATEST.md as a single fixed-viewport block — every
 * child section scrolls internally (see maxHeight + overflowY on each table
 * wrapper) rather than letting the page grow horizontally or vertically
 * unbounded. No element in this tree sets a fixed pixel width wider than its
 * parent, and every table uses table-fixed + truncate so long match names
 * never force horizontal scroll.
 */
export function DaySheetPanel() {
  const { sheet, fetchError, isStale, hasData, fetchData } = useDaySheetData();

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
          <SettledSection rows={sheet.settled} countLabel={sheet.meta.settledCountLabel} />
          <OpenSection rows={sheet.open} />
          <UnfilledSection rows={sheet.unfilled} countLabel={sheet.meta.unfilledCountLabel} />
          <NotBidSection
            groups={sheet.notBidGrouped}
            countLabel={sheet.meta.notBidCountLabel}
            totalRows={sheet.notBid.length}
          />
        </div>
      )}
    </div>
  );
}
