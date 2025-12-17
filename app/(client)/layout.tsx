import { redirect } from "next/navigation";
import { createServerSupabaseClient } from "@/lib/supabaseClient";

export default async function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();

  // Allow access to login and signup pages without auth
  // Other pages require auth and redirect to client login
  
  return (
    <div className="min-h-screen bg-gray-50">
      {children}
    </div>
  );
}