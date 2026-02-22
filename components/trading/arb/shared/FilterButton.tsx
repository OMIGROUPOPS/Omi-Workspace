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
    default: "bg-gray-700 text-white",
    green: "bg-emerald-500/20 text-emerald-400",
    purple: "bg-purple-500/20 text-purple-400",
    red: "bg-red-500/20 text-red-400",
    yellow: "bg-yellow-500/20 text-yellow-400",
  };
  return (
    <button
      onClick={onClick}
      className={`rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
        active ? activeColors[variant] : "text-gray-500 hover:text-gray-300"
      }`}
    >
      {children}
    </button>
  );
}
