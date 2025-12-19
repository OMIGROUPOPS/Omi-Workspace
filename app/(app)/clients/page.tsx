export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";

export default async function ClientsPage() {
  const supabase = await createServerSupabaseClient();

  const { data: clients, error } = await supabase
    .from("client_intakes")
    .select("id, user_id, name, company, email, industry, phone, created_at")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("CLIENTS ERROR:", error);
    return <div className="p-6">Failed to load clients.</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Clients</h1>
              <p className="text-sm text-gray-500 mt-1">All clients who signed up through the portal</p>
            </div>
          </div>
        </div>
      </div>

      <div className="px-8 py-8">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Industry</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {clients && clients.length > 0 ? (
                clients.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{c.name || "-"}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{c.company || "-"}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{c.email || "-"}</td>
                    <td className="px-6 py-4">
                      {c.industry ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {c.industry}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">{c.phone || "-"}</td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/clients/${c.id}`}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-sm text-gray-500">No clients yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}