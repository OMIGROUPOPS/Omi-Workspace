import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";

export default async function ClientPortalPage() {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: intake } = await supabase
    .from("client_intakes")
    .select("*")
    .eq("user_id", user?.id)
    .single();

  const { count: uploadsCount } = await supabase
    .from("document_uploads")
    .select("*", { count: "exact", head: true })
    .eq("user_id", user?.id);

  const { count: deliverablesCount } = await supabase
    .from("deliverables")
    .select("*", { count: "exact", head: true })
    .eq("user_id", user?.id);

  if (!intake) {
    return (
      <div className="text-center py-12">
        <div className="h-16 w-16 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">👋</span>
        </div>
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">Welcome to OMI Solutions</h1>
        <p className="text-gray-600 mb-6">Get started by learning about your business.</p>
        <Link
          href="/portal/onboarding"
          className="inline-flex px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          Start Onboarding
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Welcome back, {intake.name}</h1>
          <p className="text-gray-600">{intake.company}</p>
        </div>
        <Link
          href="/portal/profile"
          className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          Edit Profile
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-1">Documents Uploaded</p>
          <p className="text-3xl font-semibold text-gray-900">{uploadsCount || 0}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-1">Deliverables Ready</p>
          <p className="text-3xl font-semibold text-gray-900">{deliverablesCount || 0}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-1">Project Status</p>
          <p className="text-lg font-medium text-indigo-600">In Progress</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <Link
            href="/portal/upload"
            className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Upload Documents
          </Link>
          <Link
            href="/portal/deliverables"
            className="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            View Deliverables
          </Link>
        </div>
      </div>
    </div>
  );
}