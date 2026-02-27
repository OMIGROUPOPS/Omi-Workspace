import React from "react";

export function FilterButton({
  active,
  onClick,
  children,
  variant = "default",
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  variant?: "default" | "green" | "purple" | "red" | "yellow";
}) {
  const activeColors = {
    default: "bg-[#ff8c00]/20 text-[#ff8c00] border-[#ff8c00]/40",
    green: "bg-[#00ff88]/20 text-[#00ff88] border-[#00ff88]/40",
    purple: "bg-[#8b5cf6]/20 text-[#8b5cf6] border-[#8b5cf6]/40",
    red: "bg-[#ff3333]/20 text-[#ff3333] border-[#ff3333]/40",
    yellow: "bg-[#ff8c00]/20 text-[#ff8c00] border-[#ff8c00]/40",
  };
  return (
    <button
      onClick={onClick}
      className={`rounded-none px-1.5 py-0.5 text-[9px] font-mono border transition-colors ${
        active
          ? activeColors[variant]
          : "text-[#4a4a6a] border-transparent hover:text-[#ff8c00]"
      }`}
    >
      {children}
    </button>
  );
}
