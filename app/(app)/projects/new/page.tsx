"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

type Client = {
  id: string;
  name: string;
};

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [clients, setClients] = useState<Client[]>([]);
  const [loadingClients, setLoadingClients] = useState(true);

  // Fetch clients for dropdown
  useEffect(() => {
    async function fetchClients() {
      const response = await fetch("/api/clients");
      if (response.ok) {
        const data = await response.json();
        setClients(data.data || []);
      }
      setLoadingClients(false);
    }
    fetchClients();
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const formData = new FormData(e.currentTarget);
    const name = formData.get("name") as string;
    const client_id = formData.get("client_id") as string;

    if (!name.trim()) {
      setError("Project name is required");
      setLoading(false);
      return;
    }

    if (!client_id) {
      setError("Please select a client");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim(), client_id }),
      });

      if (!response.ok) {
        throw new Error("Failed to create project");
      }

      router.push("/projects");
      router.refresh();
    } catch (err) {
      setError("Failed to create project. Please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <h1 className="text-2xl font-semibold text-gray-900">Add New Project</h1>
          <p className="text-sm text-gray-500 mt-1">Create a new project for a client</p>
        </div>
      </div>

      <div className="px-8 py-8">
        <div className="max-w-2xl">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <div className="mb-6">
              <label htmlFor="client_id" className="block text-sm font-medium text-gray-700 mb-2">
                Client *
              </label>
              {loadingClients ? (
                <p className="text-sm text-gray-500">Loading clients...</p>
              ) : (
                <select
                  id="client_id"
                  name="client_id"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                >
                  <option value="">Select a client</option>
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      {client.name}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div className="mb-6">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Project Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                placeholder="Enter project name"
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-md shadow-sm transition-colors"
              >
                {loading ? "Creating..." : "Create Project"}
              </button>

              <button
                type="button"
                onClick={() => router.push("/projects")}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-md transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}