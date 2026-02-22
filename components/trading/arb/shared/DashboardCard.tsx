import React from "react";

export function DashboardCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] px-3 py-2.5">
      <p className="text-[10px] font-medium uppercase tracking-wide text-gray-500">
        {label}
      </p>
      <p className={`mt-0.5 text-xl font-bold ${accent || "text-white"}`}>
        {value}
      </p>
      {sub && <p className="text-[10px] text-gray-500">{sub}</p>}
    </div>
  );
}
