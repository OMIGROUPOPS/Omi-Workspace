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
  try {
    const { searchParams } = new URL(request.url);
    const sportKey = searchParams.get("sport_key");

    const supabase = getSupabase();

    let query = supabase
      .from("cached_odds")
      .select("sport_key, game_id, game_data, updated_at")
      .order("updated_at", { ascending: false });

    if (sportKey) {
      query = query.eq("sport_key", sportKey);
    }

    const { data, error } = await query;

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const cachedAt = data && data.length > 0 ? data[0].updated_at : null;

    return NextResponse.json({
      games: data || [],
      cachedAt,
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
