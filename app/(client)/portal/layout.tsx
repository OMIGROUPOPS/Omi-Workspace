import { redirect } from "next/navigation";
import { createServerSupabaseClient } from "@/lib/supabaseClient";

export default async function PortalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect("/client/login");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-sm font-bold">
              OMI
            </div>
            <span className="font-semibold text-gray-900">Client Portal</span>
          </div>
          <nav className="flex gap-6 text-sm">
            <a href="/portal" className="text-gray-600 hover:text-gray-900">Dashboard</a>
            <a href="/portal/upload" className="text-gray-600 hover:text-gray-900">Upload</a>
            <a href="/portal/deliverables" className="text-gray-600 hover:text-gray-900">Deliverables</a>
          </nav>
        </div>
      </header>
      
      <main className="max-w-4xl mx-auto py-8 px-6">
        {children}
      </main>
    </div>
  );
}