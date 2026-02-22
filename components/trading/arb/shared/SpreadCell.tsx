import React from "react";

export function SpreadCell({ cents }: { cents: number }) {
  let color = "text-gray-500";
  let bg = "";
  if (cents >= 5) { color = "text-emerald-400"; bg = "bg-emerald-500/10"; }
  else if (cents >= 3) { color = "text-yellow-400"; bg = "bg-yellow-500/10"; }
  else if (cents > 0) { color = "text-gray-400"; }
  else if (cents < 0) { color = "text-red-400"; bg = "bg-red-500/10"; }

  return (
    <span className={`rounded px-1.5 py-0.5 text-xs font-mono font-medium ${color} ${bg}`}>
      {cents > 0 ? "+" : ""}{cents.toFixed(1)}c
    </span>
  );
}
