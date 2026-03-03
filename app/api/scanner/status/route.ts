import { NextResponse } from "next/server";

const SCANNER_URL = process.env.SCANNER_URL || "http://104.131.191.95:8080";

export async function GET() {
  try {
    const res = await fetch(`${SCANNER_URL}/api/scanner/status`, {
      cache: "no-store",
    });
    if (!res.ok)
      return NextResponse.json(
        { error: "Scanner error" },
        { status: res.status },
      );
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json({ error: "Scanner unavailable" }, { status: 502 });
  }
}
