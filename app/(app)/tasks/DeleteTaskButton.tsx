"use client";

import { useRouter } from "next/navigation";

export default function DeleteTaskButton({ id, title }: { id: string; title: string }) {
  const router = useRouter();

  async function handleDelete() {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return;
    }

    const response = await fetch(`/api/tasks/${id}`, {
      method: "DELETE",
    });

    if (response.ok) {
      router.refresh();
    } else {
      alert("Failed to delete task");
    }
  }

  return (
    <button onClick={handleDelete} className="text-red-600 hover:text-red-800 text-sm font-medium">
      Delete
    </button>
  );
}