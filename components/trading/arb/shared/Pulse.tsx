import React from "react";

export function Pulse({ active }: { active: boolean }) {
  return (
    <span className="relative flex h-2.5 w-2.5">
      {active && (
        <span className="absolute inline-flex h-full w-full animate-ping rounded-none bg-[#ff8c00] opacity-75" />
      )}
      <span
        className={`relative inline-flex h-2.5 w-2.5 rounded-none ${
          active ? "bg-[#ff8c00]" : "bg-[#ff3333]"
        }`}
      />
    </span>
  );
}
