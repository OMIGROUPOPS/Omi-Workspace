// [C-BRING-IT-HOME v1, 07-16 — operator ruling: the trading console is
// LOCALHOST, never Vercel] Self-contained bundle of Plex's pair-lens Day
// Sheet panel for the fund tracker (port 8788). The panel + its parser
// are used VERBATIM (zero edits to merged files): a fetch shim answers
// the panel's relative `/api/daysheet` call by pulling the raw LATEST.md
// from the tracker (same origin, same token) and parsing CLIENT-side
// with Plex's own pure parser — the parser was built "no network/
// filesystem access ... reusable" and this is that reuse.
import React from "react";
import { createRoot } from "react-dom/client";
import { DaySheetPanel } from "../../components/trading/arb/panels/daysheet/DaySheetPanel";
import { parseDaySheet } from "../../lib/trading/daysheet-parser";

const token = new URLSearchParams(window.location.search).get("token") ?? "";

const realFetch = window.fetch.bind(window);
window.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
  const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
  if (url.startsWith("/api/daysheet")) {
    const res = await realFetch(`/daysheet.md?token=${token}`, { cache: "no-store" });
    if (!res.ok) {
      return new Response(JSON.stringify({ error: `sheet fetch ${res.status}` }), {
        status: 502, headers: { "Content-Type": "application/json" },
      });
    }
    const md = await res.text();
    const mtime = res.headers.get("x-sheet-mtime") ?? new Date().toISOString();
    const sheet = parseDaySheet(md, mtime);
    return new Response(JSON.stringify(sheet), {
      status: 200, headers: { "Content-Type": "application/json" },
    });
  }
  return realFetch(input as RequestInfo, init);
}) as typeof window.fetch;

const el = document.getElementById("daysheet-root")!;
createRoot(el).render(
  <div className="bg-[#0a0a0a] min-h-screen text-white p-3">
    <DaySheetPanel />
  </div>
);
