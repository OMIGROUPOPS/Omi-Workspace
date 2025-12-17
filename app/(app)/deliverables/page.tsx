import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";

export default async function DeliverablesPage() {
  const supabase = await createServerSupabaseClient();

  const { data: deliverables } = await supabase
    .from("deliverables")
    .select("*")
    .order("created_at", { ascending: false });

  const { data: clients } = await supabase
    .from("client_intakes")
    .select("*")
    .order("created_at", { ascending: false });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Deliverables</h1>
          <p className="text-gray-400">Upload files for clients to download</p>
        </div>
        <Link
          href="/deliverables/new"
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700"
        >
          + New Deliverable
        </Link>
      </div>

      <div className="space-y-6">
        {clients && clients.length > 0 ? (
          clients.map((client) => {
            const clientDeliverables = deliverables?.filter(
              (d) => d.user_id === client.user_id
            );
            return (
              <div key={client.id} className="bg-[#1a1a1f] border border-gray-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-medium text-white">{client.name}</h2>
                    <p className="text-sm text-gray-400">{client.company}</p>
                  </div>
                  <Link
                    href={`/deliverables/new?user_id=${client.user_id}`}
                    className="px-3 py-1.5 bg-gray-700 text-white text-sm rounded-lg hover:bg-gray-600"
                  >
                    Upload for this client
                  </Link>
                </div>

                {clientDeliverables && clientDeliverables.length > 0 ? (
                  <div className="space-y-2">
                    {clientDeliverables.map((d) => (
                      <div key={d.id} className="flex items-center justify-between p-3 bg-[#0f0f13] rounded-lg">
                        <div>
                          <p className="text-white">{d.file_name}</p>
                          <p className="text-sm text-gray-500">{d.description}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-gray-500">
                            {new Date(d.created_at).toLocaleDateString()}
                          </span>
                          <a href={d.file_url} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 text-sm">
                            View
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No deliverables yet</p>
                )}
              </div>
            );
          })
        ) : (
          <div className="bg-[#1a1a1f] border border-gray-800 rounded-xl p-6 text-center">
            <p className="text-gray-400">No clients have completed onboarding yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}