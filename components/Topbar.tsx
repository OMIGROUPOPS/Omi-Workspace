"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";

function getPageTitle(pathname: string): string {
  const map: { prefix: string; title: string }[] = [
    { prefix: "/dashboard", title: "Dashboard" },
    { prefix: "/clients", title: "Clients" },
    { prefix: "/projects", title: "Projects" },
    { prefix: "/automations", title: "Automations" },
    { prefix: "/tasks", title: "Tasks" },
    { prefix: "/knowledge", title: "Knowledge Base" },
    { prefix: "/integrations", title: "Integrations" },
    { prefix: "/billing", title: "Billing" },
    { prefix: "/settings/account", title: "Account Settings" },
    { prefix: "/settings/security", title: "Security" },
    { prefix: "/settings/preferences", title: "Preferences" },
    { prefix: "/settings", title: "Settings" },
  ];

  const match =
    map.find((m) => pathname === m.prefix || pathname.startsWith(m.prefix + "/")) ??
    map.find((m) => m.prefix === "/dashboard");

  return match ? match.title : "OMI Workspace";
}

export default function Topbar() {
  const pathname = usePathname();
  const pageTitle = useMemo(() => getPageTitle(pathname), [pathname]);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200/40 bg-white/70 backdrop-blur-xl backdrop-saturate-150 shadow-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">

        {/* LEFT */}
        <div className="flex flex-col">
          <span className="text-[11px] uppercase tracking-[0.18em] text-gray-500">
            OMI Workspace
          </span>
          <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
            {pageTitle}
          </h1>
        </div>

        {/* RIGHT */}
        <div className="flex items-center gap-4">

          {/* Search */}
          <button
            className="hidden sm:flex items-center gap-2 rounded-full border border-gray-300/50 bg-white/70 px-4 py-1.5 text-xs text-gray-600 shadow-sm hover:bg-white/90 transition-all backdrop-blur-md"
          >
            <span>Search workspace...</span>
            <span className="rounded-full border border-gray-400/40 bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-700 shadow-sm">
              ⌘K
            </span>
          </button>

          {/* Notifications */}
          <button
            className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-gray-300/40 bg-white/70 text-[16px] text-gray-700 shadow hover:bg-white transition-all backdrop-blur-md"
          >
            •
          </button>

          {/* Avatar */}
          <button
            className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-blue-500 border border-indigo-500/40 text-xs font-semibold text-white shadow-md hover:shadow-lg hover:shadow-indigo-500/40 transition-all"
          >
            OG
          </button>

        </div>

      </div>
    </header>
  );
}
