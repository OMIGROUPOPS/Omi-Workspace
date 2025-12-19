export const dynamic = "force-dynamic";

import { createServerSupabaseClient } from "@/lib/supabaseClient";
import Link from "next/link";

export default async function ClientDetailPage({ params }: { params: { id: string } }) {
  const supabase = await createServerSupabaseClient();

  const { data: client, error } = await supabase
    .from("client_intakes")
    .select("*")
    .eq("id", params.id)
    .single();

  if (error || !client) {
    return (
      <div className="p-8">
        <p className="text-red-500">Client not found.</p>
        <Link href="/clients" className="text-blue-600 hover:underline mt-4 inline-block">
          Back to Clients
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <Link href="/clients" className="text-sm text-gray-500 hover:text-gray-700 mb-2 inline-block">
            ← Back to Clients
          </Link>
          <h1 className="text-2xl font-semibold text-gray-900">{client.name}</h1>
          <p className="text-gray-500">{client.company}</p>
        </div>
      </div>

      <div className="px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Contact Info */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="text-gray-900">{client.email || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <p className="text-gray-900">{client.phone || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Industry</p>
                <p className="text-gray-900">{client.industry || "-"}</p>
              </div>
            </div>
          </div>

          {/* Business Info */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Business Details</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Description</p>
                <p className="text-gray-900">{client.business_description || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Current Tools</p>
                <p className="text-gray-900">{client.current_tools || "-"}</p>
              </div>
            </div>
          </div>

          {/* Pain Points */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Pain Points</h2>
            <p className="text-gray-900">{client.pain_points || "-"}</p>
          </div>

          {/* Goals */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Goals</h2>
            <p className="text-gray-900">{client.goals || "-"}</p>
          </div>
        </div>

        {/* Upload Deliverable Button */}
        <div className="mt-8">
          <Link
            href={`/deliverables/new?user_id=${client.user_id}`}
            className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Upload Deliverable for this Client
          </Link>
        </div>
      </div>
    </div>
  );
}