export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";
import DeleteTaskButton from "./DeleteTaskButton";

export default async function TasksPage() {
  const supabase = createServerSupabaseClient();

  const { data: tasks } = await supabase
    .from("tasks")
    .select(`
      id, 
      title, 
      status, 
      created_at,
      projects (
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
              <h1 className="text-2xl font-semibold text-gray-900">Tasks</h1>
              <p className="text-sm text-gray-500 mt-1">Manage and track task execution</p>
            </div>
            <Link href="/tasks/new" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors">
              + Add Task
            </Link>
          </div>
        </div>
      </div>

      <div className="px-8 py-8">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tasks && tasks.length > 0 ? (
                tasks.map((t: any) => (
                  <tr key={t.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{t.title}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{t.projects?.name || "—"}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 capitalize">
                        {t.status || "pending"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/tasks/${t.id}/edit`} className="text-blue-600 hover:text-blue-800 text-sm font-medium mr-4">
                        Edit
                      </Link>
                      <DeleteTaskButton id={t.id} title={t.title} />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-sm text-gray-500">No tasks yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}