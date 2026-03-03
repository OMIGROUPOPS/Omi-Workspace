import { NextResponse } from "next/server";
import { getPositions } from "@/lib/kalshi/client";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const positions = await getPositions(100, "unsettled");
    return NextResponse.json(positions);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
