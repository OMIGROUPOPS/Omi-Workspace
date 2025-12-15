export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";

export default async function DashboardPage() {
  const supabase = createServerSupabaseClient();

  const { data: stats, error } = await supabase.rpc("get_dashboard_stats");

  if (error) {
    console.error("Dashboard stats error:", error);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Section */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
              <p className="text-sm text-gray-500 mt-1">
                System overview and operational metrics
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Clients Card */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  Total Clients
                </h3>
              </div>
              <div className="flex items-baseline">
                <p className="text-4xl font-semibold text-gray-900">
                  {stats?.total_clients ?? "-"}
                </p>
              </div>
            </div>
          </div>

          {/* Total Projects Card */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  Total Projects
                </h3>
              </div>
              <div className="flex items-baseline">
                <p className="text-4xl font-semibold text-gray-900">
                  {stats?.total_projects ?? "-"}
                </p>
              </div>
            </div>
          </div>

          {/* Total Tasks Card */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  Total Tasks
                </h3>
              </div>
              <div className="flex items-baseline">
                <p className="text-4xl font-semibold text-gray-900">
                  {stats?.total_tasks ?? "-"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Future: Activity Feed, Quick Actions, etc. */}
      </div>
    </div>
  );
}