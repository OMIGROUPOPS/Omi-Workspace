import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

function getSupabase() {
  const cookieStore = cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { get(name: string) { return cookieStore.get(name)?.value; } } }
  );
}

export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase.from("projects").select("*").eq("id", params.id).single();
    if (error) return NextResponse.json({ error: error.message }, { status: 404 });
    return NextResponse.json({ data }, { status: 200 });
  } catch (error) {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function PUT(request: Request, { params }: { params: { id: string } }) {
  try {
    const body = await request.json();
    const { name } = body;
    if (!name || !name.trim()) return NextResponse.json({ error: "Project name is required" }, { status: 400 });
    const supabase = getSupabase();
    const { data, error } = await supabase.from("projects").update({ name: name.trim() }).eq("id", params.id).select().single();
    if (error) return NextResponse.json({ error: "Failed to update project" }, { status: 500 });
    return NextResponse.json({ data }, { status: 200 });
  } catch (error) {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(request: Request, { params }: { params: { id: string } }) {
  try {
    const supabase = getSupabase();
    const { error } = await supabase.from("projects").delete().eq("id", params.id);
    if (error) return NextResponse.json({ error: "Failed to delete project" }, { status: 500 });
    return NextResponse.json({ success: true }, { status: 200 });
  } catch (error) {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}