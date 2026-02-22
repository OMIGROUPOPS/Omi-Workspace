"use client";

import React from "react";

interface FillRateData {
  iocAttempts: number;
  iocFills: number;
  iocRate: string;
  gtcAttempts: number;
  gtcFills: number;
  gtcRate: string;
  spreadBuckets: Record<string, { attempts: number; fills: number }>;
  noFillReasons: Record<string, number>;
}

interface Props {
  data: FillRateData;
}

export function FillRateAnalytics({ data }: Props) {
  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
        Fill Rate Analytics
      </h3>
      <div className="grid grid-cols-2 gap-4">
        {/* IOC vs GTC */}
        <div>
          <p className="text-[10px] text-gray-500 mb-1">By Execution Phase</p>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">IOC</span>
              <span className="text-gray-300 font-mono">
                {data.iocFills}/{data.iocAttempts} ({data.iocRate}%)
              </span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-1.5">
              <div
                className="bg-emerald-500 h-1.5 rounded-full"
                style={{ width: `${parseFloat(data.iocRate)}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">GTC</span>
              <span className="text-gray-300 font-mono">
                {data.gtcFills}/{data.gtcAttempts} ({data.gtcRate}%)
              </span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-1.5">
              <div
                className="bg-purple-500 h-1.5 rounded-full"
                style={{ width: `${parseFloat(data.gtcRate)}%` }}
              />
            </div>
          </div>
        </div>

        {/* By spread bucket */}
        <div>
          <p className="text-[10px] text-gray-500 mb-1">By Spread Bucket</p>
          <div className="space-y-1">
            {Object.entries(data.spreadBuckets).map(([bucket, { attempts, fills }]) => {
              const rate = attempts > 0 ? ((fills / attempts) * 100).toFixed(1) : "0";
              return (
                <div key={bucket} className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{bucket}</span>
                  <span className="text-gray-300 font-mono">
                    {fills}/{attempts} ({rate}%)
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* No-fill reasons */}
        {Object.keys(data.noFillReasons).length > 0 && (
          <div className="col-span-2">
            <p className="text-[10px] text-gray-500 mb-1">No-Fill Reasons</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.noFillReasons)
                .sort(([, a], [, b]) => b - a)
                .map(([reason, count]) => (
                  <span
                    key={reason}
                    className="rounded bg-gray-800 px-1.5 py-0.5 text-[10px] text-gray-400"
                  >
                    {reason}: {count}
                  </span>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
