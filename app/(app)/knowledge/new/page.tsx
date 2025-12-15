import { createServerSupabaseClient } from "@/lib/supabaseClient";

export default function NewArticlePage() {
  async function createArticle(formData: FormData) {
    "use server";

    const supabase = createServerSupabaseClient();

    const title = formData.get("title") as string;
    const category = formData.get("category") as string;
    const content = formData.get("content") as string;

    await supabase.from("knowledge").insert([{ title, category, content }]);
  }

  return (
    <div className="px-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-semibold mb-4">Add Knowledge Article</h1>

      <form action={createArticle} className="space-y-4 bg-white p-6 rounded-lg">
        <input
          name="title"
          placeholder="Article Title"
          className="w-full border p-2 rounded"
          required
        />

        <input
          name="category"
          placeholder="Category"
          className="w-full border p-2 rounded"
        />

        <textarea
          name="content"
          placeholder="Write your content here..."
          className="w-full border p-2 rounded h-40"
        />

        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Create Article
        </button>
      </form>
    </div>
  );
}
