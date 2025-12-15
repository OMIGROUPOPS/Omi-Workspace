export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";

export default async function ClientsPage() {
  const supabase = createServerSupabaseClient();

  const { data: clients, error } = await supabase
    .from("clients")
    .select("id, name, status, created_at")
    .order("created_at", { ascending: true });

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
              <p className="text-sm text-gray-500 mt-1">Manage client relationships and accounts</p>
            </div>
            <Link href="/clients/new" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors">
              + Add Client
            </Link>
          </div>
        </div>
      </div>

      <div className="px-8 py-8">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {clients && clients.length > 0 ? (
                clients.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{c.name}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                        {c.status || "active"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/clients/${c.id}/edit`}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium mr-4"
                      >
                        Edit
                      </Link>
                      <button
                        className="text-red-600 hover:text-red-800 text-sm font-medium delete-btn"
                        data-id={c.id}
                        data-name={c.name}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="px-6 py-12 text-center text-sm text-gray-500">No clients yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <DeleteScript />
    </div>
  );
}

function DeleteScript() {
  return (
    <script
      dangerouslySetInnerHTML={{
        __html: `
          document.addEventListener('click', async function(e) {
            if (e.target.classList.contains('delete-btn')) {
              const id = e.target.dataset.id;
              const name = e.target.dataset.name;
              if (confirm('Are you sure you want to delete "' + name + '"?')) {
                const response = await fetch('/api/clients/' + id, {
                  method: 'DELETE',
                });
                if (response.ok) {
                  window.location.reload();
                } else {
                  alert('Failed to delete client');
                }
              }
            }
          });
        `,
      }}
    />
  );
}