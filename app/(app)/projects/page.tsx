export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";
import DeleteProjectButton from "./DeleteProjectButton";

export default async function ProjectsPage() {
  const supabase = createServerSupabaseClient();

  const { data: projects } = await supabase
    .from("projects")
    .select(`
      id, 
      name, 
      status, 
      created_at,
      clients (
        id,
        name
      )
    `)
    .order("created_at", { ascending: true });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Projects</h1>
              <p className="text-sm text-gray-500 mt-1">Track and manage active projects</p>
            </div>
            <Link href="/projects/new" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors">
              + Add Project
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Client</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {projects && projects.length > 0 ? (
                projects.map((p: any) => (
                  <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{p.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{p.clients?.name || "—"}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                        {p.status || "planning"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/projects/${p.id}/edit`} className="text-blue-600 hover:text-blue-800 text-sm font-medium mr-4">
                        Edit
                      </Link>
                      <DeleteProjectButton id={p.id} name={p.name} />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-sm text-gray-500">No projects yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}