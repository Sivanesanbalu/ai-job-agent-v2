"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Preferences } from "@/types";
import { 
  Sliders, MapPin, DollarSign, Target, ShieldCheck, 
  Save, CheckCircle2, AlertCircle, Plus, X, Sparkles, Filter
} from "lucide-react";

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState<Partial<Preferences>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // Input states for tag arrays
  const [newRole, setNewRole] = useState("");
  const [newLocation, setNewLocation] = useState("");
  const [newKeyword, setNewKeyword] = useState("");
  const [newExcludedKeyword, setNewExcludedKeyword] = useState("");

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const data = await api.preferences.get();
      setPreferences(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load job preferences.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof Preferences, value: any) => {
    setPreferences((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddTag = (
    field: "preferred_roles" | "preferred_locations" | "keywords" | "excluded_keywords",
    value: string,
    clearFn: (val: string) => void
  ) => {
    if (!value.trim()) return;
    const current = preferences[field] || [];
    if (!current.includes(value.trim())) {
      handleChange(field, [...current, value.trim()]);
    }
    clearFn("");
  };

  const handleRemoveTag = (
    field: "preferred_roles" | "preferred_locations" | "keywords" | "excluded_keywords",
    tagToRemove: string
  ) => {
    const current = preferences[field] || [];
    handleChange(field, current.filter((t) => t !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      const updated = await api.preferences.update(preferences);
      setPreferences(updated);
      setSuccessMessage("Target job preferences saved successfully!");
      setTimeout(() => setSuccessMessage(""), 4000);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to save preferences.");
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
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job Discovery & Matching Preferences</h1>
        <p className="text-sm text-slate-500 mt-1">
          Configure matching criteria, filters, and safety thresholds. The agent will discover and auto-qualify jobs matching these rules.
        </p>
      </div>

      {successMessage && (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-emerald-800 text-sm">
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
        {/* Section 1: Target Roles & Titles */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Target Roles & Titles</h2>
              <p className="text-xs text-slate-500">The specific titles and roles the agent should scout for.</p>
            </div>
          </div>

          <div>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                placeholder="Add role title (e.g. Senior Frontend Engineer, Full Stack Developer)"
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddTag("preferred_roles", newRole, setNewRole);
                  }
                }}
                className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={() => handleAddTag("preferred_roles", newRole, setNewRole)}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold transition"
              >
                <Plus className="h-4 w-4" /> Add
              </button>
            </div>

            <div className="flex flex-wrap gap-2 min-h-[44px] p-3 rounded-xl bg-slate-50 border border-slate-200">
              {preferences.preferred_roles && preferences.preferred_roles.length > 0 ? (
                preferences.preferred_roles.map((role) => (
                  <span
                    key={role}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 text-xs font-medium shadow-sm"
                  >
                    {role}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag("preferred_roles", role)}
                      className="text-slate-400 hover:text-rose-600 transition"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-400">No target roles specified. Add at least one role.</span>
              )}
            </div>
          </div>
        </div>

        {/* Section 2: Locations & Work Arrangement */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
              <MapPin className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Locations & Work Modes</h2>
              <p className="text-xs text-slate-500">Geographical boundaries and remote preferences.</p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-50/50 border border-emerald-100">
            <input
              type="checkbox"
              id="remote_friendly"
              checked={preferences.remote_friendly ?? true}
              onChange={(e) => handleChange("remote_friendly", e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
            />
            <label htmlFor="remote_friendly" className="text-sm font-semibold text-slate-800 cursor-pointer">
              Include Remote Opportunities (Worldwide / Country-wide)
            </label>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Target Cities / Regions</label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                placeholder="e.g. Bangalore, San Francisco, London, Remote"
                value={newLocation}
                onChange={(e) => setNewLocation(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddTag("preferred_locations", newLocation, setNewLocation);
                  }
                }}
                className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={() => handleAddTag("preferred_locations", newLocation, setNewLocation)}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold transition"
              >
                <Plus className="h-4 w-4" /> Add
              </button>
            </div>

            <div className="flex flex-wrap gap-2 min-h-[44px] p-3 rounded-xl bg-slate-50 border border-slate-200">
              {preferences.preferred_locations && preferences.preferred_locations.length > 0 ? (
                preferences.preferred_locations.map((loc) => (
                  <span
                    key={loc}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 text-xs font-medium shadow-sm"
                  >
                    {loc}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag("preferred_locations", loc)}
                      className="text-slate-400 hover:text-rose-600 transition"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-400">No specific locations added.</span>
              )}
            </div>
          </div>
        </div>

        {/* Section 3: Compensation & Experience Thresholds */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
              <DollarSign className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Salary & Experience Bounds</h2>
              <p className="text-xs text-slate-500">Filter out underpaying or over-experienced roles automatically.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Minimum Salary (LPA / $K)
              </label>
              <input
                type="number"
                min="0"
                value={preferences.min_salary_lpa ?? 0}
                onChange={(e) => handleChange("min_salary_lpa", parseFloat(e.target.value) || 0)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Max Experience Required (Years)
              </label>
              <input
                type="number"
                min="0"
                value={preferences.max_experience_years ?? 10}
                onChange={(e) => handleChange("max_experience_years", parseInt(e.target.value) || 0)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Min Match Score ({preferences.min_match_score ?? 70}%)
              </label>
              <div className="flex items-center gap-3 pt-1">
                <input
                  type="range"
                  min="40"
                  max="95"
                  value={preferences.min_match_score ?? 70}
                  onChange={(e) => handleChange("min_match_score", parseInt(e.target.value))}
                  className="w-full accent-indigo-600"
                />
                <span className="text-sm font-bold text-indigo-600 w-12 text-right">
                  {preferences.min_match_score ?? 70}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Section 4: Keyword Filters */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
              <Filter className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Must-Have & Excluded Keywords</h2>
              <p className="text-xs text-slate-500">Fine-tune matching criteria with positive and negative keyword constraints.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Must-have keywords */}
            <div>
              <label className="block text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1.5">
                Must Include (Keywords)
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  placeholder="e.g. Next.js, FastAPI"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddTag("keywords", newKeyword, setNewKeyword);
                    }
                  }}
                  className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <button
                  type="button"
                  onClick={() => handleAddTag("keywords", newKeyword, setNewKeyword)}
                  className="px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold"
                >
                  Add
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5 min-h-[40px] p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                {preferences.keywords && preferences.keywords.length > 0 ? (
                  preferences.keywords.map((kw) => (
                    <span
                      key={kw}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium"
                    >
                      {kw}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag("keywords", kw)}
                        className="text-emerald-500 hover:text-rose-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">No required keywords.</span>
                )}
              </div>
            </div>

            {/* Excluded keywords */}
            <div>
              <label className="block text-xs font-semibold text-rose-700 uppercase tracking-wider mb-1.5">
                Exclude (Negative Keywords)
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  placeholder="e.g. unpaid, junior, php"
                  value={newExcludedKeyword}
                  onChange={(e) => setNewExcludedKeyword(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddTag("excluded_keywords", newExcludedKeyword, setNewExcludedKeyword);
                    }
                  }}
                  className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <button
                  type="button"
                  onClick={() => handleAddTag("excluded_keywords", newExcludedKeyword, setNewExcludedKeyword)}
                  className="px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold"
                >
                  Add
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5 min-h-[40px] p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                {preferences.excluded_keywords && preferences.excluded_keywords.length > 0 ? (
                  preferences.excluded_keywords.map((kw) => (
                    <span
                      key={kw}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium"
                    >
                      {kw}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag("excluded_keywords", kw)}
                        className="text-rose-500 hover:text-rose-700"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">No excluded keywords.</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Section 5: Automation Governance & Safety */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Automation Governance & Mode</h2>
              <p className="text-xs text-slate-500">Determine whether applications require manual one-click approval before submission.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              onClick={() => {
                handleChange("auto_submit", false);
                handleChange("require_human_review", true);
              }}
              className={`p-4 rounded-xl border-2 cursor-pointer transition ${
                !preferences.auto_submit
                  ? "border-indigo-600 bg-indigo-50/40"
                  : "border-slate-200 hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-900 text-sm">Human-in-the-Loop Mode</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">Recommended</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Agent prepares full application drafts and pre-fills forms, but halts before clicking Submit until you click Approve.
              </p>
            </div>

            <div 
              onClick={() => {
                handleChange("auto_submit", true);
                handleChange("require_human_review", false);
              }}
              className={`p-4 rounded-xl border-2 cursor-pointer transition ${
                preferences.auto_submit
                  ? "border-emerald-600 bg-emerald-50/40"
                  : "border-slate-200 hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-900 text-sm">Full Auto-Pilot Mode</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">Autonomous</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Agent matches, fills out, and automatically submits applications whenever score meets your minimum threshold.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Max Daily Application Limit
              </label>
              <input
                type="number"
                min="1"
                max="200"
                value={preferences.max_applications_per_day ?? 25}
                onChange={(e) => handleChange("max_applications_per_day", parseInt(e.target.value) || 25)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <p className="text-xs text-slate-400 mt-1">Prevents over-applying and stays well within portal rate limits.</p>
            </div>

            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="sponsorship_required"
                  checked={preferences.sponsorship_required ?? false}
                  onChange={(e) => handleChange("sponsorship_required", e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="sponsorship_required" className="text-sm text-slate-700 cursor-pointer">
                  Require Visa Sponsorship (H-1B, Tier 2, etc.)
                </label>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="relocation"
                  checked={preferences.relocation ?? false}
                  onChange={(e) => handleChange("relocation", e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="relocation" className="text-sm text-slate-700 cursor-pointer">
                  Willing to Relocate for the right role
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={fetchPreferences}
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
                Saving Preferences...
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save Preferences
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
