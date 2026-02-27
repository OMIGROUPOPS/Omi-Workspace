import React from "react";

export function SpreadCell({ cents }: { cents: number }) {
  let color = "text-[#3a3a5a]";
  let bg = "";
  if (cents >= 5) { color = "text-[#00ff88]"; bg = "bg-[#00ff88]/10"; }
  else if (cents >= 3) { color = "text-[#ff8c00]"; bg = "bg-[#ff8c00]/10"; }
  else if (cents > 0) { color = "text-[#4a4a6a]"; }
  else if (cents < 0) { color = "text-[#ff3333]"; bg = "bg-[#ff3333]/10"; }

  return (
    <span className={`rounded-none px-1.5 py-0.5 text-xs font-mono font-medium ${color} ${bg}`}>
      {cents > 0 ? "+" : ""}{cents.toFixed(1)}c
    </span>
  );
}
