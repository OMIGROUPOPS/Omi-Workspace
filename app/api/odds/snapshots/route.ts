import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

function getSupabase() {
  const cookieStore = cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
      },
    }
  );
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const gameId = searchParams.get("game_id");
  const market = searchParams.get("market");
  const book = searchParams.get("book");

  if (!gameId) {
    return NextResponse.json({ error: "game_id is required" }, { status: 400 });
  }

  const supabase = getSupabase();

  let query = supabase
    .from("odds_snapshots")
    .select("*")
    .eq("game_id", gameId)
    .order("snapshot_time", { ascending: true });

  if (market) {
    query = query.eq("market", market);
  }
  if (book) {
    query = query.eq("book_key", book);
  }

  const { data, error } = await query;

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ snapshots: data || [] });
}
