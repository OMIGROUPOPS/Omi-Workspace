"use client";

import type { ReactNode } from "react";

interface PanelProps {
  title: string;
  children: ReactNode;
  className?: string;
  headerRight?: ReactNode;
}

export default function Panel({ title, children, className = "", headerRight }: PanelProps) {
  return (
    <div className={`panel rounded-lg overflow-hidden ${className}`}>
      <div className="panel-header px-3 py-2 flex items-center justify-between">
        <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
          {title}
        </span>
        {headerRight}
      </div>
      {children}
    </div>
  );
}
