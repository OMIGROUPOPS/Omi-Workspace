"use client";

import { useRouter } from "next/navigation";

export default function DeleteAutomationButton({ id, name }: { id: string; name: string }) {
  const router = useRouter();

  async function handleDelete() {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    const response = await fetch(`/api/automations/${id}`, {
      method: "DELETE",
    });

    if (response.ok) {
      router.refresh();
    } else {
      alert("Failed to delete automation");
    }
  }

  return (
    <button onClick={handleDelete} className="text-red-600 hover:text-red-800 text-sm font-medium">
      Delete
    </button>
  );
}