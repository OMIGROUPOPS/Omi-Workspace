import { NextResponse } from "next/server";
import { createOrder, getOrders, cancelOrder } from "@/lib/kalshi/client";
import type { KalshiCreateOrderRequest } from "@/lib/kalshi/client";

export const dynamic = "force-dynamic";

// GET — list resting orders
export async function GET() {
  try {
    const orders = await getOrders("resting", 50);
    return NextResponse.json(orders);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}

// POST — place a new order
export async function POST(req: Request) {
  try {
    const body = (await req.json()) as KalshiCreateOrderRequest;

    // Validate required fields
    if (!body.ticker || !body.action || !body.side || !body.type || !body.count) {
      return NextResponse.json(
        { error: "Missing required fields: ticker, action, side, type, count" },
        { status: 400 },
      );
    }
    if (body.count < 1 || body.count > 500) {
      return NextResponse.json(
        { error: "Count must be between 1 and 500" },
        { status: 400 },
      );
    }

    const result = await createOrder(body);
    return NextResponse.json(result);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}

// DELETE — cancel an order by ID (passed as ?order_id=...)
export async function DELETE(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const orderId = searchParams.get("order_id");
    if (!orderId) {
      return NextResponse.json({ error: "Missing order_id" }, { status: 400 });
    }
    await cancelOrder(orderId);
    return NextResponse.json({ success: true });
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
