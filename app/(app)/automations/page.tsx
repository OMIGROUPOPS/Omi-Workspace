export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";
import DeleteAutomationButton from "./DeleteAutomationButton";

export default async function AutomationsPage() {
  const supabase = createServerSupabaseClient();

  const { data: automations } = await supabase
    .from("automations")
    .select("*")
    .order("created_at", { ascending: true });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Automations</h1>
              <p className="text-sm text-gray-500 mt-1">Manage and monitor system automations</p>
            </div>
            <Link href="/automations/new" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors">
              + Add Automation
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {automations && automations.length > 0 ? (
                automations.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{a.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{a.description}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                        {a.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/automations/${a.id}/edit`} className="text-blue-600 hover:text-blue-800 text-sm font-medium mr-4">
                        Edit
                      </Link>
                      <DeleteAutomationButton id={a.id} name={a.name} />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-sm text-gray-500">No automations yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}