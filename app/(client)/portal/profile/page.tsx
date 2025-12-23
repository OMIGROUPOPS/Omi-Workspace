"use client";

import { useState, useEffect } from "react";
import { createBrowserClient } from "@supabase/ssr";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState({
    name: "",
    company: "",
    phone: "",
    industry: "",
    customIndustry: "",
    business_description: "",
    current_tools: "",
    pain_points: "",
    goals: "",
  });

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  useEffect(() => {
    const loadProfile = async () => {
      setLoading(true);
      const { data: { user } } = await supabase.auth.getUser();
      
      if (user) {
        const { data: intake } = await supabase
          .from("client_intakes")
          .select("*")
          .eq("user_id", user.id)
          .single();
        
        if (intake) {
          const isCustomIndustry = intake.industry && ![
            "Real Estate", "Financial Services", "Healthcare", "Technology",
            "Manufacturing", "Retail / E-commerce", "Professional Services",
            "Construction", "Legal", "Insurance", "Education", "Hospitality"
          ].includes(intake.industry);
          
          setFormData({
            name: intake.name || "",
            company: intake.company || "",
            phone: intake.phone || "",
            industry: isCustomIndustry ? "Other" : (intake.industry || ""),
            customIndustry: isCustomIndustry ? intake.industry : "",
            business_description: intake.business_description || "",
            current_tools: intake.current_tools || "",
            pain_points: intake.pain_points || "",
            goals: intake.goals || "",
          });
        }
      }
      setLoading(false);
    };
    
    loadProfile();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess(false);

    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      setError("You must be logged in");
      setSaving(false);
      return;
    }

    const finalIndustry = formData.industry === "Other" ? formData.customIndustry : formData.industry;

    const { error } = await supabase
      .from("client_intakes")
      .update({
        name: formData.name,
        company: formData.company,
        phone: formData.phone,
        industry: finalIndustry,
        business_description: formData.business_description,
        current_tools: formData.current_tools,
        pain_points: formData.pain_points,
        goals: formData.goals,
      })
      .eq("user_id", user.id);

    if (error) {
      setError(error.message);
      setSaving(false);
      return;
    }

    setSuccess(true);
    setSaving(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Edit Profile</h1>
          <p className="text-gray-600">Update your business information</p>
        </div>
        <Link
          href="/portal"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          ← Back to Dashboard
        </Link>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-600">Profile updated successfully!</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Your Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
            <input
              type="text"
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number <span className="text-gray-400">(optional)</span></label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="(555) 123-4567"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Industry / Sector</label>
          <select
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="">Select your industry</option>
            <option value="Real Estate">Real Estate</option>
            <option value="Financial Services">Financial Services</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Technology">Technology</option>
            <option value="Manufacturing">Manufacturing</option>
            <option value="Retail / E-commerce">Retail / E-commerce</option>
            <option value="Professional Services">Professional Services</option>
            <option value="Construction">Construction</option>
            <option value="Legal">Legal</option>
            <option value="Insurance">Insurance</option>
            <option value="Education">Education</option>
            <option value="Hospitality">Hospitality</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {formData.industry === "Other" && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Please specify your industry</label>
            <input
              type="text"
              value={formData.customIndustry}
              onChange={(e) => setFormData({ ...formData, customIndustry: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your industry"
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Describe your business</label>
          <textarea
            value={formData.business_description}
            onChange={(e) => setFormData({ ...formData, business_description: e.target.value })}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="What does your company do? What is your core service or product?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">What tools or software do you currently use?</label>
          <textarea
            value={formData.current_tools}
            onChange={(e) => setFormData({ ...formData, current_tools: e.target.value })}
            rows={2}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="e.g., Excel, Salesforce, QuickBooks, custom software..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">What is slowing your business down?</label>
          <textarea
            value={formData.pain_points}
            onChange={(e) => setFormData({ ...formData, pain_points: e.target.value })}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="What processes are manual, repetitive, or frustrating? Where are the bottlenecks?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">What are your goals?</label>
          <textarea
            value={formData.goals}
            onChange={(e) => setFormData({ ...formData, goals: e.target.value })}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="What would success look like for you? What do you want to achieve?"
          />
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-indigo-400 transition-colors"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <Link
            href="/portal"
            className="px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}