"use client";

import React from "react";

interface Props {
  specs: any;
}

export function BookCoveragePanel({ specs }: Props) {
  const bc = specs?.book_coverage || {};
  const kTotal = bc.k_total ?? 0;
  const kActive = bc.k_active ?? 0;
  const pmTotal = bc.pm_total ?? 0;
  const pmActive = bc.pm_active ?? 0;
  const missingPm = bc.missing_pm || [];

  const kPct = kTotal > 0 ? ((kActive / kTotal) * 100).toFixed(0) : "0";
  const pmPct = pmTotal > 0 ? ((pmActive / pmTotal) * 100).toFixed(0) : "0";

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
        Book Coverage
      </h3>
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <span className="text-[10px] text-gray-500 uppercase">Kalshi Books</span>
          <p className="text-sm text-white font-mono">
            {kActive} / {kTotal} <span className="text-gray-500">({kPct}%)</span>
          </p>
          <div className="w-full bg-gray-800 rounded-full h-1.5 mt-1">
            <div className="bg-orange-500 h-1.5 rounded-full" style={{ width: `${kPct}%` }} />
          </div>
        </div>
        <div>
          <span className="text-[10px] text-gray-500 uppercase">PM Books</span>
          <p className="text-sm text-white font-mono">
            {pmActive} / {pmTotal} <span className="text-gray-500">({pmPct}%)</span>
          </p>
          <div className="w-full bg-gray-800 rounded-full h-1.5 mt-1">
            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${pmPct}%` }} />
          </div>
        </div>
      </div>
      {missingPm.length > 0 && (
        <div>
          <span className="text-[10px] text-gray-500 uppercase">Missing PM Books ({missingPm.length})</span>
          <div className="mt-1 flex flex-wrap gap-1">
            {missingPm.map((ck: string) => (
              <span key={ck} className="rounded bg-red-500/10 px-1.5 py-0.5 text-[10px] text-red-400 font-mono">
                {ck}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
