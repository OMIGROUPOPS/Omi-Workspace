import { NextResponse } from "next/server";
import { parseDaySheet } from "@/lib/trading/daysheet-parser";

// ── Day Sheet API route ──────────────────────────────────────────────────────
// Pulls the raw LATEST.md from the deploy branch (regenerates 5:55a/11a/4p ET),
// parses it server-side, and returns typed JSON to the client.
//
// Unlike /api/arb this is pull-based, not push-based — the source file already
// regenerates on its own schedule inside the repo, so there is nothing for the
// VPS bot to push. We just need to fetch + parse the current file on read.

const RAW_URL =
  "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/blend/kalshi-occ-fallback/.claude/today_sheet/LATEST.md";

export const revalidate = 60; // seconds — matches the "as of" staleness strip cadence elsewhere in this shell

export async function GET() {
  try {
    const res = await fetch(RAW_URL, { cache: "no-store" });
    if (!res.ok) {
      return NextResponse.json(
        { error: `upstream fetch failed: ${res.status}` },
        { status: 502 }
      );
    }
    const markdown = await res.text();
    const lastModified = res.headers.get("last-modified");
    const sourceMtimeIso = lastModified ? new Date(lastModified).toISOString() : new Date().toISOString();

    const sheet = parseDaySheet(markdown, sourceMtimeIso);
    return NextResponse.json(sheet);
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "unknown error" },
      { status: 500 }
    );
  }
}
