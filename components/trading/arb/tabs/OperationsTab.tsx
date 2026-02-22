"use client";

import React from "react";
import type { ArbDataReturn } from "../hooks/useArbData";
import { WsHealthPanel } from "../panels/WsHealthPanel";
import { BookCoveragePanel } from "../panels/BookCoveragePanel";
import { ExecutionStatsPanel } from "../panels/ExecutionStatsPanel";
import { ConfigPanel } from "../panels/ConfigPanel";

interface Props {
  data: ArbDataReturn;
}

export function OperationsTab({ data }: Props) {
  const specs = data.state?.specs;

  if (!specs) {
    return (
      <div className="p-4">
        <div className="rounded-lg border border-gray-800 bg-[#111] p-8 text-center text-sm text-gray-500">
          No specs data — waiting for executor push
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <WsHealthPanel specs={specs} system={data.state?.system} />
        <BookCoveragePanel specs={specs} />
      </div>
      <ExecutionStatsPanel specs={specs} />
      <ConfigPanel specs={specs} />
    </div>
  );
}
