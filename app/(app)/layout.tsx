import { redirect } from "next/navigation";
import { createServerSupabaseClient } from "@/lib/supabaseClient";
import dynamic from "next/dynamic";

const Sidebar = dynamic(() => import("@/components/Sidebar"), { ssr: false });
const Topbar = dynamic(() => import("@/components/Topbar"), { ssr: false });

// Only these emails can access the internal dashboard
const ALLOWED_OPERATORS = [
  "omigroup.ops@outlook.com",
  // Add more operator emails here as needed
];

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  // Check if user is an approved operator
  if (!ALLOWED_OPERATORS.includes(user.email || "")) {
    // Not authorized - sign them out and redirect
    await supabase.auth.signOut();
    redirect("/");
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}