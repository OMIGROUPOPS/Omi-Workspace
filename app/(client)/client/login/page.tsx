"use client";

import { useState } from "react";
import { createBrowserClient } from "@supabase/ssr";
import Link from "next/link";

export default function ClientLoginPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  const handleMagicLink = async () => {
    setLoading(true);
    setError("");

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/portal`,
      },
    });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    setSent(true);
    setLoading(false);
  };

  if (sent) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <header className="px-6 py-4 border-b border-gray-200">
          <div className="max-w-md mx-auto flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors">
              <span className="text-xl">←</span>
              <span className="text-sm font-medium">Back to OMI Group</span>
            </Link>
            <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
              OMI
            </div>
          </div>
        </header>

        <div className="flex-1 flex items-center justify-center px-4">
          <div className="w-full max-w-md text-center">
            <div className="inline-flex items-center justify-center h-14 w-14 rounded-xl bg-green-600 text-xl font-bold text-white mb-4">
              ✓
            </div>
            <h1 className="text-2xl font-semibold text-gray-900">Check your email</h1>
            <p className="text-gray-500 mt-2">We sent a login link to <span className="font-medium text-gray-700">{email}</span></p>
            <p className="text-gray-400 text-sm mt-4">Click the link in your email to access the portal.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="px-6 py-4 border-b border-gray-200">
        <div className="max-w-md mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors">
            <span className="text-xl">←</span>
            <span className="text-sm font-medium">Back to OMI Group</span>
          </Link>
          <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
            OMI
          </div>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-semibold text-gray-900">Client Portal</h1>
            <p className="text-gray-500 mt-1">Enter your email to sign in</p>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <button
                onClick={handleMagicLink}
                disabled={loading || !email}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium rounded-lg"
              >
                {loading ? "Sending link..." : "Send login link"}
              </button>

              <p className="text-center text-gray-500 text-sm">
                New to OMI Solutions?{" "}
                <Link href="/client/signup" className="text-indigo-600 hover:text-indigo-700">
                  Get started
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}