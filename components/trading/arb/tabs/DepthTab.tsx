"use client";

import React from "react";
import type { ArbDataReturn } from "../hooks/useArbData";
import { DepthBars } from "../panels/DepthBars";
import { DepthSummaryTable } from "../panels/DepthSummaryTable";

interface Props {
  data: ArbDataReturn;
}

export function DepthTab({ data }: Props) {
  const liq = data.state?.liquidity_stats;

  if (!liq || (liq.per_game.length === 0 && liq.aggregate.total_snapshots === 0)) {
    return (
      <div className="p-4">
        <div className="rounded-lg border border-gray-800 bg-[#111] p-8 text-center text-sm text-gray-500">
          No depth data available — orderbook_data.db may be empty
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <DepthBars aggregate={liq.aggregate} />
      <DepthSummaryTable
        games={liq.per_game}
        filter={data.liqGameFilter}
        setFilter={data.setLiqGameFilter}
      />
    </div>
  );
}
