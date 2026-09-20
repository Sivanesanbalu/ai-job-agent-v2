"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Profile } from "@/types";
import { 
  User, Mail, Phone, MapPin, Briefcase, Globe, 
  Linkedin, Github, Award, Save, CheckCircle2, AlertCircle, Plus, X
} from "lucide-react";

export default function ProfilePage() {
  const [profile, setProfile] = useState<Partial<Profile>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [newSkill, setNewSkill] = useState("");

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await api.profile.get();
      setProfile(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load profile details.");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof Profile, value: any) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddSkill = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ("key" in e && e.key !== "Enter") return;
    e.preventDefault();
    if (!newSkill.trim()) return;
    const currentSkills = profile.skills || [];
    if (!currentSkills.includes(newSkill.trim())) {
      handleInputChange("skills", [...currentSkills, newSkill.trim()]);
    }
    setNewSkill("");
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    const currentSkills = profile.skills || [];
    handleInputChange("skills", currentSkills.filter((s) => s !== skillToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      const updated = await api.profile.update(profile);
      setProfile(updated);
      setSuccessMessage("Your profile has been saved successfully!");
      setTimeout(() => setSuccessMessage(""), 4000);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Personal & Professional Profile</h1>
        <p className="text-sm text-slate-500 mt-1">
          Provide complete and verified details. The AI application engine uses this exact data to fill out job portal application forms accurately.
        </p>
      </div>

      {successMessage && (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-emerald-800 text-sm animate-fade-in">
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-emerald-600" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2 rounded-xl bg-rose-50 border border-rose-200 p-4 text-rose-800 text-sm">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Section 1: Basic Identity */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <User className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Personal Identity</h2>
              <p className="text-xs text-slate-500">Legal names as they appear on official identification documents.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">First Name *</label>
              <input
                type="text"
                required
                value={profile.first_name || ""}
                onChange={(e) => handleInputChange("first_name", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Middle Name</label>
              <input
                type="text"
                value={profile.middle_name || ""}
                onChange={(e) => handleInputChange("middle_name", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Last Name *</label>
              <input
                type="text"
                required
                value={profile.last_name || ""}
                onChange={(e) => handleInputChange("last_name", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Preferred Name / Alias</label>
              <input
                type="text"
                value={profile.preferred_name || ""}
                onChange={(e) => handleInputChange("preferred_name", e.target.value)}
                placeholder="e.g. Alex"
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Date of Birth</label>
              <input
                type="date"
                value={profile.dob || ""}
                onChange={(e) => handleInputChange("dob", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Contact Information */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
              <Phone className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Contact Details</h2>
              <p className="text-xs text-slate-500">Recruiters and hiring portals will contact you via these credentials.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Contact Email *</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="email"
                  required
                  value={profile.email || ""}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 pl-10 pr-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Phone Number *</label>
              <div className="relative">
                <Phone className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="tel"
                  required
                  placeholder="+1 (555) 000-0000"
                  value={profile.phone || ""}
                  onChange={(e) => handleInputChange("phone", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 pl-10 pr-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Country *</label>
              <input
                type="text"
                required
                value={profile.country || ""}
                onChange={(e) => handleInputChange("country", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">State / Province</label>
              <input
                type="text"
                value={profile.state || ""}
                onChange={(e) => handleInputChange("state", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">City *</label>
              <input
                type="text"
                required
                value={profile.city || ""}
                onChange={(e) => handleInputChange("city", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Street Address</label>
              <input
                type="text"
                value={profile.address || ""}
                onChange={(e) => handleInputChange("address", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Postal / Pincode</label>
              <input
                type="text"
                value={profile.pincode || ""}
                onChange={(e) => handleInputChange("pincode", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Professional Overview & Links */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
              <Briefcase className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Professional Summary & Portfolios</h2>
              <p className="text-xs text-slate-500">Your professional title, bio summary, and online profiles.</p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Professional Headline *</label>
            <input
              type="text"
              required
              placeholder="e.g. Senior Full Stack Engineer | Python, React, AWS"
              value={profile.headline || ""}
              onChange={(e) => handleInputChange("headline", e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Executive Summary</label>
            <textarea
              rows={4}
              placeholder="Concise overview of your experience, impact, and engineering leadership..."
              value={profile.summary || ""}
              onChange={(e) => handleInputChange("summary", e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">LinkedIn Profile</label>
              <div className="relative">
                <Linkedin className="absolute left-3.5 top-2.5 h-4 w-4 text-blue-600" />
                <input
                  type="url"
                  placeholder="https://linkedin.com/in/username"
                  value={profile.linkedin_url || ""}
                  onChange={(e) => handleInputChange("linkedin_url", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 pl-10 pr-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">GitHub Profile</label>
              <div className="relative">
                <Github className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-700" />
                <input
                  type="url"
                  placeholder="https://github.com/username"
                  value={profile.github_url || ""}
                  onChange={(e) => handleInputChange("github_url", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 pl-10 pr-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Portfolio / Website</label>
              <div className="relative">
                <Globe className="absolute left-3.5 top-2.5 h-4 w-4 text-emerald-600" />
                <input
                  type="url"
                  placeholder="https://yourportfolio.dev"
                  value={profile.portfolio_url || ""}
                  onChange={(e) => handleInputChange("portfolio_url", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 pl-10 pr-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 4: Experience, Education & Skills */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
              <Award className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Experience & Skills</h2>
              <p className="text-xs text-slate-500">Core technical proficiencies used to calculate match relevance scores.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Years of Relevant Experience *</label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="50"
                required
                value={profile.experience_years ?? 0}
                onChange={(e) => handleInputChange("experience_years", parseFloat(e.target.value) || 0)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Highest Education Degree</label>
              <input
                type="text"
                placeholder="e.g. Master of Science in Computer Science"
                value={profile.education || ""}
                onChange={(e) => handleInputChange("education", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Skills Tag Management */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Technical & Domain Skills</label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                placeholder="Type a skill (e.g. Python, React, Kubernetes) and press Enter"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={handleAddSkill}
                className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={handleAddSkill}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold transition"
              >
                <Plus className="h-4 w-4" /> Add
              </button>
            </div>

            <div className="flex flex-wrap gap-2 min-h-[44px] p-3 rounded-xl bg-slate-50 border border-slate-200">
              {profile.skills && profile.skills.length > 0 ? (
                profile.skills.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 text-xs font-medium shadow-sm"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(skill)}
                      className="text-slate-400 hover:text-rose-600 transition"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-400">No skills added yet. Add skills to improve job matching.</span>
              )}
            </div>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={fetchProfile}
            className="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-sm shadow-indigo-200 transition disabled:opacity-50"
          >
            {saving ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Saving Profile...
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save Profile
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
