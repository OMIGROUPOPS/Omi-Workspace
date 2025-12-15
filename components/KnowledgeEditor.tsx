"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";

export default function KnowledgeEditor({ content, onChange }: any) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: content || "",
    onUpdate({ editor }) {
      onChange(editor.getHTML());
    },
  });

  return (
    <div className="border rounded-lg bg-white p-4">
      <EditorContent editor={editor} />
    </div>
  );
}
