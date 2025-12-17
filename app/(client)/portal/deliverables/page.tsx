"use client";

import { useState, useEffect } from "react";
import { createBrowserClient } from "@supabase/ssr";

interface Deliverable {
  id: string;
  file_name: string;
  file_url: string;
  description: string;
  created_at: string;
}

export default function DeliverablesPage() {
  const [deliverables, setDeliverables] = useState<Deliverable[]>([]);
  const [loading, setLoading] = useState(true);

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  useEffect(() => {
    fetchDeliverables();
  }, []);

  const fetchDeliverables = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      setLoading(false);
      return;
    }

    const { data } = await supabase
      .from("deliverables")
      .select("*")
      .eq("user_id", user.id)
      .order("created_at", { ascending: false });

    if (data) setDeliverables(data);
    setLoading(false);
  };

  if (loading) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-gray-900">Your Deliverables</h1>
          <p className="text-gray-600">Files and documents prepared for you by our team.</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <p className="text-gray-500 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  if (deliverables.length === 0) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-gray-900">Your Deliverables</h1>
          <p className="text-gray-600">Files and documents prepared for you by our team.</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="text-center py-8">
            <p className="text-gray-500">No deliverables yet.</p>
            <p className="text-gray-400 text-sm">Check back soon - we are working on your project.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Your Deliverables</h1>
        <p className="text-gray-600">Files and documents prepared for you by our team.</p>
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="space-y-3">
          {deliverables.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{item.file_name}</p>
                <p className="text-sm text-gray-500">{item.description}</p>
                <p className="text-xs text-gray-400">{new Date(item.created_at).toLocaleDateString()}</p>
              </div>
              <a href={item.file_url} target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700">
                Download
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}