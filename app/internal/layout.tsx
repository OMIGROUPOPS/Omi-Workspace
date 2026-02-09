import { redirect } from "next/navigation";
import { createServerSupabaseClient } from "@/lib/supabaseClient";

const ALLOWED_OPERATORS = [
  "omigroup.ops@outlook.com",
];

export default async function InternalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  if (!ALLOWED_OPERATORS.includes(user.email || "")) {
    await supabase.auth.signOut();
    redirect("/");
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-950">
      {children}
    </div>
  );
}
