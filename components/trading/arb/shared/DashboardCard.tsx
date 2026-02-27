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
    <div className="border border-[#1a1a2e] bg-[#0a0a0a] px-2 py-1.5 rounded-none relative overflow-hidden">
      {/* Amber top accent line */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#ff8c00]" />
      <p className="text-[9px] font-mono uppercase tracking-widest text-[#4a4a6a] mt-0.5">
        {label}
      </p>
      <p className={`mt-0.5 text-base font-bold font-mono ${accent || "text-[#ff8c00]"}`}>
        {value}
      </p>
      {sub && <p className="text-[9px] font-mono text-[#3a3a5a]">{sub}</p>}
    </div>
  );
}
