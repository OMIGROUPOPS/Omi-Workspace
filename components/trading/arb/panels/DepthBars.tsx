"use client";

import React from "react";
import type { LiquidityAggregate } from "../types";

interface Props {
  aggregate: LiquidityAggregate;
}

export function DepthBars({ aggregate }: Props) {
  const items = [
    { label: "Total Snapshots", value: aggregate.total_snapshots.toLocaleString() },
    { label: "Unique Games", value: aggregate.unique_games },
    { label: "Avg Bid Depth", value: aggregate.overall_avg_bid_depth },
    { label: "Avg Ask Depth", value: aggregate.overall_avg_ask_depth },
    { label: "Avg Spread", value: `${aggregate.overall_avg_spread}c` },
  ];

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
        Aggregate Depth (24h)
      </h3>
      <div className="grid grid-cols-5 gap-3">
        {items.map((item) => (
          <div key={item.label}>
            <span className="text-[10px] text-gray-500 uppercase">{item.label}</span>
            <p className="text-lg text-white font-bold font-mono">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
