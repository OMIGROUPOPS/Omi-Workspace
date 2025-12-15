import Link from "next/link";
import { createServerSupabaseClient } from "@/lib/supabaseClient";

export default async function ArticlePage({ params }: any) {
  const supabase = createServerSupabaseClient();

  const { data: article, error } = await supabase
    .from("knowledge")
    .select("*")
    .eq("id", params.id)
    .single();

  if (!article) {
    return (
      <div className="px-6 max-w-3xl mx-auto">
        <p className="text-gray-500">Article not found.</p>
        <Link href="/knowledge" className="text-blue-600 underline mt-4 block">
          ← Back to Knowledge Base
        </Link>
      </div>
    );
  }

  return (
    <div className="px-6 max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">{article.title}</h1>
        <p className="text-gray-600">{article.category}</p>

        <Link
          href="/knowledge"
          className="text-blue-600 hover:underline mt-4 inline-block"
        >
          ← Back to Knowledge Base
        </Link>
      </div>

      <div className="bg-white border rounded-lg p-6">
        {article.content || "No content available."}
      </div>
    </div>
  );
}
