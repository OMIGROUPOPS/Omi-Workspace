import { redirect } from "next/navigation";
import { createServerSupabaseClient } from "@/lib/supabaseClient";
import dynamic from "next/dynamic";

const Sidebar = dynamic(() => import("@/components/Sidebar"), { ssr: false });
const Topbar = dynamic(() => import("@/components/Topbar"), { ssr: false });

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