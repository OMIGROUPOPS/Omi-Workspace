export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";

export default async function UploadsPage() {
  const supabase = await createServerSupabaseClient();

  const { data: uploads, error } = await supabase
    .from("document_uploads")
    .select("id, file_name, file_url, notes, created_at, user_id")
    .order("created_at", { ascending: false });

  const { data: clients } = await supabase
    .from("client_intakes")
    .select("user_id, name, company");

  const clientMap = new Map();
  clients?.forEach((c) => clientMap.set(c.user_id, c));

  if (error) {
    return <div className="p-6">Failed to load uploads.</div>;
  }

  const hasUploads = uploads && uploads.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <h1 className="text-2xl font-semibold text-gray-900">Client Uploads</h1>
          <p className="text-sm text-gray-500 mt-1">Documents uploaded by clients</p>
        </div>
      </div>
      <div className="px-8 py-8">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {hasUploads ? (
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">File</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {uploads.map((upload) => {
                  const client = clientMap.get(upload.user_id);
                  return (
                    <tr key={upload.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <p className="text-sm font-medium text-gray-900">{client?.name || "Unknown"}</p>
                        <p className="text-xs text-gray-500">{client?.company || "-"}</p>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">{upload.file_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{upload.notes || "-"}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(upload.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <a
                          href={upload.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                        >
                          Download
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="px-6 py-12 text-center text-sm text-gray-500">No uploads yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}