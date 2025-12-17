"use client";

import { useState, useEffect } from "react";
import { createBrowserClient } from "@supabase/ssr";
import { useRouter, useSearchParams } from "next/navigation";

interface Client {
  id: string;
  user_id: string;
  name: string;
  company: string;
}

export default function NewDeliverablePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedUserId = searchParams.get("user_id");

  const [clients, setClients] = useState<Client[]>([]);
  const [selectedUserId, setSelectedUserId] = useState(preselectedUserId || "");
  const [description, setDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    const { data } = await supabase
      .from("client_intakes")
      .select("*")
      .order("created_at", { ascending: false });
    if (data) setClients(data);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedFile || !selectedUserId) {
      setError("Please select a client and file");
      return;
    }

    setLoading(true);
    setError("");

    const fileExt = selectedFile.name.split(".").pop();
    const fileName = `${selectedUserId}/${Date.now()}.${fileExt}`;

    const { error: uploadError } = await supabase.storage
      .from("documents")
      .upload(fileName, selectedFile);

    if (uploadError) {
      setError("Failed to upload file: " + uploadError.message);
      setLoading(false);
      return;
    }

    const { data: urlData } = supabase.storage
      .from("documents")
      .getPublicUrl(fileName);

    const { error: dbError } = await supabase.from("deliverables").insert({
      user_id: selectedUserId,
      file_url: urlData.publicUrl,
      file_name: selectedFile.name,
      description: description,
    });

    if (dbError) {
      setError(dbError.message);
      setLoading(false);
      return;
    }

    router.push("/deliverables");
  };

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">Upload Deliverable</h1>
        <p className="text-gray-400">Send a file to a client</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-[#1a1a1f] border border-gray-800 rounded-xl p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Select Client</label>
          <select
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            className="w-full px-4 py-2 bg-[#0f0f13] border border-gray-700 rounded-lg text-white"
            required
          >
            <option value="">Choose a client...</option>
            {clients.map((client) => (
              <option key={client.id} value={client.user_id}>
                {client.name} - {client.company}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">File</label>
          <input
            type="file"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="w-full px-4 py-2 bg-[#0f0f13] border border-gray-700 rounded-lg text-white"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-4 py-2 bg-[#0f0f13] border border-gray-700 rounded-lg text-white"
            placeholder="What is this deliverable?"
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-indigo-400"
          >
            {loading ? "Uploading..." : "Upload Deliverable"}
          </button>
          <button
            type="button"
            onClick={() => router.push("/deliverables")}
            className="px-6 py-2 bg-gray-700 text-white font-medium rounded-lg hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}