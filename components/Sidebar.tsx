"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { label: "Dashboard", href: "/dashboard", key: "D" },
  { label: "Clients", href: "/clients", key: "C" },
  { label: "Projects", href: "/projects", key: "P" },
  { label: "Automations", href: "/automations", key: "A" },
  { label: "Tasks", href: "/tasks", key: "T" },
  { label: "Knowledge", href: "/knowledge", key: "K" },
  { label: "Integrations", href: "/integrations", key: "I" },
  { label: "Billing", href: "/billing", key: "B" },
  { label: "Settings", href: "/settings", key: "S" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`relative flex h-screen flex-col border-r border-gray-800 bg-[#1a1a1a] transition-all duration-300 ${
        collapsed ? "w-[72px]" : "w-64"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-5 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 shadow-sm text-sm font-bold text-white">
            OMI
          </div>

          {!collapsed && (
            <div className="leading-tight">
              <p className="text-[10px] uppercase tracking-wider text-gray-500 font-medium">
                Workspace
              </p>
              <p className="text-sm font-semibold text-white mt-0.5">
                OMI Dashboard
              </p>
            </div>
          )}
        </div>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex h-7 w-7 items-center justify-center rounded-md bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white transition-colors"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? "›" : "‹"}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                active
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:bg-gray-800/50 hover:text-gray-200"
              }`}
            >
              {/* Icon Circle */}
              <div
                className={`flex h-8 w-8 flex-none items-center justify-center rounded-lg text-xs font-semibold transition-colors ${
                  active
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-800 text-gray-400 group-hover:bg-gray-700 group-hover:text-gray-300"
                }`}
              >
                {item.key}
              </div>

              {/* Label */}
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="border-t border-gray-800 px-5 py-4">
          <p className="text-xs text-gray-500">OMI Group Solutions</p>
          <p className="text-xs text-gray-600 mt-0.5">Internal Workspace</p>
        </div>
      )}
    </aside>
  );
}