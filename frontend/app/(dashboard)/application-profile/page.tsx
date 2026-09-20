"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { ApplicationProfile } from "@/types";
import { 
  FileText, Clock, DollarSign, ShieldAlert, 
  HelpCircle, Save, CheckCircle2, AlertCircle, Plus, Trash2 
} from "lucide-react";

export default function ApplicationProfilePage() {
  const [profile, setProfile] = useState<Partial<ApplicationProfile>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // Key-value editor state for custom_answers
  const [customQuestion, setCustomQuestion] = useState("");
  const [customAnswer, setCustomAnswer] = useState("");

  useEffect(() => {
    fetchApplicationProfile();
  }, []);

  const fetchApplicationProfile = async () => {
    try {
      setLoading(true);
      const data = await api.applicationProfile.get();
      setProfile(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load application profile.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof ApplicationProfile, value: any) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddCustomAnswer = () => {
    if (!customQuestion.trim() || !customAnswer.trim()) return;
    const current = profile.custom_answers || {};
    handleChange("custom_answers", {
      ...current,
      [customQuestion.trim()]: customAnswer.trim(),
    });
    setCustomQuestion("");
    setCustomAnswer("");
  };

  const handleRemoveCustomAnswer = (key: string) => {
    const current = { ...(profile.custom_answers || {}) };
    delete current[key];
    handleChange("custom_answers", current);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      const updated = await api.applicationProfile.update(profile);
      setProfile(updated);
      setSuccessMessage("Application answers and profile updated successfully!");
      setTimeout(() => setSuccessMessage(""), 4000);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to save application profile.");
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
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Application Answers & Screening Vault</h1>
        <p className="text-sm text-slate-500 mt-1">
          Store standardized answers for repetitive recruiter questions, notice periods, salary benchmarks, and demographic disclosures.
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
        {/* Section 1: Employment & Availability */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <Clock className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Availability & Work Authorization</h2>
              <p className="text-xs text-slate-500">Crucial fields checked early by ATS filters.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Notice Period (Days) *
              </label>
              <input
                type="number"
                min="0"
                max="180"
                required
                value={profile.notice_period_days ?? 30}
                onChange={(e) => handleChange("notice_period_days", parseInt(e.target.value) || 0)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <span className="text-[11px] text-slate-400">0 for immediate joiner.</span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Work Authorization *
              </label>
              <select
                value={profile.work_authorization || "Citizen"}
                onChange={(e) => handleChange("work_authorization", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              >
                <option value="Citizen">Citizen / Permanent Resident</option>
                <option value="Authorized - No Sponsorship">Authorized to work (No sponsorship needed)</option>
                <option value="Requires Sponsorship">Requires Visa Sponsorship</option>
                <option value="Student / OPT / CPT">F-1 OPT / STEM OPT</option>
                <option value="EU Blue Card">EU Blue Card / Work Permit</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Total Experience (Years)
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={profile.years_of_experience ?? 5}
                onChange={(e) => handleChange("years_of_experience", parseFloat(e.target.value) || 0)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Current Compensation (LPA / $K)
              </label>
              <input
                type="number"
                min="0"
                value={profile.current_salary_lpa ?? ""}
                onChange={(e) => handleChange("current_salary_lpa", e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="Optional"
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Expected Compensation (LPA / $K) *
              </label>
              <input
                type="number"
                min="0"
                required
                value={profile.expected_salary_lpa ?? 25}
                onChange={(e) => handleChange("expected_salary_lpa", parseFloat(e.target.value) || 0)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Equal Opportunity & Demographic Disclosures */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Equal Opportunity Disclosures (EEO)</h2>
              <p className="text-xs text-slate-500">Standardized responses for US/EU mandatory EEO voluntary questions.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Gender</label>
              <select
                value={profile.gender || "Decline to state"}
                onChange={(e) => handleChange("gender", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Non-binary">Non-binary</option>
                <option value="Decline to state">Decline to Self-Identify</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Ethnicity / Race</label>
              <select
                value={profile.ethnicity || "Decline to state"}
                onChange={(e) => handleChange("ethnicity", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              >
                <option value="Asian">Asian</option>
                <option value="White">White</option>
                <option value="Black or African American">Black or African American</option>
                <option value="Hispanic or Latino">Hispanic or Latino</option>
                <option value="Two or More Races">Two or More Races</option>
                <option value="Decline to state">Decline to Self-Identify</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Veteran Status</label>
              <select
                value={profile.veteran_status || "Not a veteran"}
                onChange={(e) => handleChange("veteran_status", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              >
                <option value="Not a veteran">I am not a protected veteran</option>
                <option value="Veteran">I identify as one or more classifications of protected veteran</option>
                <option value="Decline to state">Decline to Self-Identify</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Disability Status</label>
              <select
                value={profile.disability_status || "No"}
                onChange={(e) => handleChange("disability_status", e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              >
                <option value="No">No, I do not have a disability</option>
                <option value="Yes">Yes, I have a disability</option>
                <option value="Decline to state">Decline to Self-Identify</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 3: Custom Screening Q&A Answers */}
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
              <HelpCircle className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Custom Screening Q&A Bank</h2>
              <p className="text-xs text-slate-500">
                When portal application forms present custom questions, the agent will check this bank first for exact or fuzzy matches.
              </p>
            </div>
          </div>

          {/* New Q&A Input */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Add Common Question & Answer</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                type="text"
                placeholder="Question (e.g. 'Are you comfortable working in an agile environment?')"
                value={customQuestion}
                onChange={(e) => setCustomQuestion(e.target.value)}
                className="rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Answer (e.g. 'Yes, I have 6+ years working in sprint cycles.')"
                  value={customAnswer}
                  onChange={(e) => setCustomAnswer(e.target.value)}
                  className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <button
                  type="button"
                  onClick={handleAddCustomAnswer}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold transition shadow-sm"
                >
                  <Plus className="h-4 w-4" /> Add
                </button>
              </div>
            </div>
          </div>

          {/* List of Custom Answers */}
          <div className="space-y-3">
            {profile.custom_answers && Object.keys(profile.custom_answers).length > 0 ? (
              Object.entries(profile.custom_answers).map(([question, answer]) => (
                <div
                  key={question}
                  className="flex items-start justify-between p-4 rounded-xl border border-slate-200 bg-white shadow-xs"
                >
                  <div className="space-y-1 pr-4">
                    <p className="text-sm font-semibold text-slate-900">{question}</p>
                    <p className="text-xs text-slate-600">{String(answer)}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveCustomAnswer(question)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 py-2">No custom Q&A items saved yet. You can add common questions above.</p>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={fetchApplicationProfile}
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
                Saving Answers...
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save Screening Vault
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
