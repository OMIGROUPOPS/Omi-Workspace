import { NextResponse } from "next/server";
import { getFills } from "@/lib/kalshi/client";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const fills = await getFills(20);
    return NextResponse.json(fills);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
