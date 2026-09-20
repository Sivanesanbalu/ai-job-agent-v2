"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  User,
  Upload,
  Sparkles,
  CheckCircle2,
  Sliders,
  FileSpreadsheet,
  Link2,
  Zap,
  ArrowRight,
  ArrowLeft,
  Loader2,
  AlertCircle,
  FileText,
} from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/AuthContext";

const STEPS = [
  { id: 1, name: "Personal Details" },
  { id: 2, name: "Upload Resume" },
  { id: 3, name: "AI Parsing" },
  { id: 4, name: "Review Profile" },
  { id: 5, name: "Job Preferences" },
  { id: 6, name: "Application Q&A" },
  { id: 7, name: "Job Portals" },
  { id: 8, name: "Agent Settings" },
  { id: 9, name: "Launch" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const { profile, preferences, applicationProfile, refreshUserData } = useAuth();

  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [personal, setPersonal] = useState({
    first_name: profile?.first_name || "",
    middle_name: profile?.middle_name || "",
    last_name: profile?.last_name || "",
    preferred_name: profile?.preferred_name || "",
    phone: profile?.phone || "",
    dob: profile?.dob || "",
    country: profile?.country || "India",
    state: profile?.state || "",
    city: profile?.city || "Bangalore",
    address: profile?.address || "",
    pincode: profile?.pincode || "",
  });

  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [parsedResume, setParsedResume] = useState<any>(null);

  const [pref, setPref] = useState({
    preferred_roles: preferences?.preferred_roles?.join(", ") || "AI Engineer, Generative AI Engineer, Python Developer",
    preferred_locations: preferences?.preferred_locations?.join(", ") || "Bangalore, Chennai, Hyderabad, Remote",
    remote_friendly: preferences?.remote_friendly ?? true,
    min_salary_lpa: preferences?.min_salary_lpa || 5.0,
    max_experience_years: preferences?.max_experience_years || 2.0,
    min_match_score: preferences?.min_match_score || 70,
  });

  const [appData, setAppData] = useState({
    notice_period_days: applicationProfile?.notice_period_days || 15,
    work_authorization: applicationProfile?.work_authorization || "Authorized to work in India",
    expected_salary_lpa: applicationProfile?.expected_salary_lpa || 6.0,
    years_of_experience: applicationProfile?.years_of_experience || 1.0,
    disability_status: applicationProfile?.disability_status || "No",
  });

  const [automationSettings, setAutomationSettings] = useState({
    auto_submit: true,
    require_human_review: false,
  });

  const handleNext = async () => {
    setError(null);
    setLoading(true);

    try {
      if (currentStep === 1) {
        await api.profile.update(personal);
        setCurrentStep(2);
      } else if (currentStep === 2) {
        if (!resumeFile) {
          setError("Please select a resume file (PDF or DOCX) to continue.");
          setLoading(false);
          return;
        }
        setCurrentStep(3); // Start AI parsing
        const formData = new FormData();
        formData.append("file", resumeFile);
        formData.append("set_active", "true");

        const uploaded = await api.resumes.upload(formData);
        setParsedResume(uploaded.parsed_data);
        await refreshUserData();
        setTimeout(() => setCurrentStep(4), 1000);
      } else if (currentStep === 4) {
        setCurrentStep(5);
      } else if (currentStep === 5) {
        const rolesArray = pref.preferred_roles.split(",").map((r) => r.trim()).filter(Boolean);
        const locsArray = pref.preferred_locations.split(",").map((l) => l.trim()).filter(Boolean);
        await api.preferences.update({
          preferred_roles: rolesArray,
          preferred_locations: locsArray,
          remote_friendly: pref.remote_friendly,
          min_salary_lpa: Number(pref.min_salary_lpa),
          max_experience_years: Number(pref.max_experience_years),
          min_match_score: Number(pref.min_match_score),
        });
        setCurrentStep(6);
      } else if (currentStep === 6) {
        await api.applicationProfile.update({
          notice_period_days: Number(appData.notice_period_days),
          work_authorization: appData.work_authorization,
          expected_salary_lpa: Number(appData.expected_salary_lpa),
          years_of_experience: Number(appData.years_of_experience),
          disability_status: appData.disability_status,
        });
        setCurrentStep(7);
      } else if (currentStep === 7) {
        setCurrentStep(8);
      } else if (currentStep === 8) {
        await api.preferences.update(automationSettings);
        setCurrentStep(9);
      } else if (currentStep === 9) {
        await api.automation.start();
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Failed to save step data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl py-8">
      {/* Progress Bar */}
      <div className="mb-10">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-500 mb-2">
          <span>
            Step {currentStep} of {STEPS.length}: {STEPS[currentStep - 1].name}
          </span>
          <span>{Math.round((currentStep / STEPS.length) * 100)}% Completed</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
          <div
            className="h-full bg-indigo-600 transition-all duration-300 ease-out"
            style={{ width: `${(currentStep / STEPS.length) * 100}%` }}
          />
        </div>
      </div>

      {error && (
        <div className="mb-6 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Card Content */}
      <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-xs">
        {/* Step 1: Personal Details */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Personal & Contact Details</h2>
              <p className="mt-1 text-sm text-slate-500">
                These details will be filled into job application portals.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">First Name</label>
                <input
                  type="text"
                  required
                  value={personal.first_name}
                  onChange={(e) => setPersonal({ ...personal, first_name: e.target.value })}
                  placeholder="Jane"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Last Name</label>
                <input
                  type="text"
                  required
                  value={personal.last_name}
                  onChange={(e) => setPersonal({ ...personal, last_name: e.target.value })}
                  placeholder="Doe"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Phone Number</label>
                <input
                  type="text"
                  value={personal.phone}
                  onChange={(e) => setPersonal({ ...personal, phone: e.target.value })}
                  placeholder="+91 9876543210"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Country</label>
                <input
                  type="text"
                  value={personal.country}
                  onChange={(e) => setPersonal({ ...personal, country: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">City</label>
                <input
                  type="text"
                  value={personal.city}
                  onChange={(e) => setPersonal({ ...personal, city: e.target.value })}
                  placeholder="Bangalore"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Postal / Pincode</label>
                <input
                  type="text"
                  value={personal.pincode}
                  onChange={(e) => setPersonal({ ...personal, pincode: e.target.value })}
                  placeholder="560001"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Resume Upload */}
        {currentStep === 2 && (
          <div className="space-y-6 text-center py-6">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
              <Upload className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">Upload Your Resume</h2>
              <p className="mt-1 text-sm text-slate-500">
                Upload your primary PDF or DOCX resume. Max 10MB.
              </p>
            </div>

            <div className="mx-auto max-w-md rounded-2xl border-2 border-dashed border-slate-300 p-8 hover:border-indigo-500 transition">
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="hidden"
                id="resume-input"
              />
              <label
                htmlFor="resume-input"
                className="cursor-pointer flex flex-col items-center gap-2"
              >
                <FileText className="h-10 w-10 text-slate-400" />
                <span className="text-sm font-semibold text-indigo-600 hover:text-indigo-500">
                  {resumeFile ? resumeFile.name : "Choose a file from your device"}
                </span>
                <span className="text-xs text-slate-400">PDF or DOCX</span>
              </label>
            </div>
          </div>
        )}

        {/* Step 3: AI Resume Parsing */}
        {currentStep === 3 && (
          <div className="space-y-6 text-center py-16">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-600 text-white animate-bounce">
              <Sparkles className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">AI Resume Parsing in Progress</h2>
              <p className="mt-2 text-sm text-slate-500">
                Extracting technical skills, experience metrics, and education history...
              </p>
            </div>
            <div className="mx-auto max-w-xs flex justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
            </div>
          </div>
        )}

        {/* Step 4: Resume Review */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Review Extracted Profile</h2>
              <p className="mt-1 text-sm text-slate-500">
                Verify the skills and experience extracted from your resume.
              </p>
            </div>

            <div className="rounded-xl border border-slate-100 bg-slate-50 p-6 space-y-4">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase">Detected Skills</span>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(parsedResume?.skills || profile?.skills || ["Python", "FastAPI", "SQL", "Docker"]).map(
                    (s: string, idx: number) => (
                      <span
                        key={idx}
                        className="rounded-lg border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700"
                      >
                        {s}
                      </span>
                    )
                  )}
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase">Education</span>
                <p className="mt-1 text-sm text-slate-800">
                  {parsedResume?.education || profile?.education || "Bachelor of Technology / Computer Science"}
                </p>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase">Estimated Experience</span>
                <p className="mt-1 text-sm text-slate-800">
                  {parsedResume?.experience_years || profile?.experience_years || 1.0} years
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Job Preferences */}
        {currentStep === 5 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Job Preferences & Targeting</h2>
              <p className="mt-1 text-sm text-slate-500">
                Set the parameters for roles you want the agent to pursue.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Roles (comma-separated)
                </label>
                <input
                  type="text"
                  value={pref.preferred_roles}
                  onChange={(e) => setPref({ ...pref, preferred_roles: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Preferred Locations (comma-separated)
                </label>
                <input
                  type="text"
                  value={pref.preferred_locations}
                  onChange={(e) => setPref({ ...pref, preferred_locations: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Minimum Salary (₹ LPA)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={pref.min_salary_lpa}
                    onChange={(e) => setPref({ ...pref, min_salary_lpa: Number(e.target.value) })}
                    className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Max Allowed Experience (Years)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={pref.max_experience_years}
                    onChange={(e) => setPref({ ...pref, max_experience_years: Number(e.target.value) })}
                    className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 6: Application Q&A */}
        {currentStep === 6 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Application Q&A Profile</h2>
              <p className="mt-1 text-sm text-slate-500">
                Common questions asked across application forms.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Notice Period (Days)</label>
                <input
                  type="number"
                  value={appData.notice_period_days}
                  onChange={(e) => setAppData({ ...appData, notice_period_days: Number(e.target.value) })}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Expected Salary (₹ LPA)</label>
                <input
                  type="number"
                  step="0.5"
                  value={appData.expected_salary_lpa}
                  onChange={(e) => setAppData({ ...appData, expected_salary_lpa: Number(e.target.value) })}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Work Authorization</label>
                <input
                  type="text"
                  value={appData.work_authorization}
                  onChange={(e) => setAppData({ ...appData, work_authorization: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Disability Declaration</label>
                <select
                  value={appData.disability_status}
                  onChange={(e) => setAppData({ ...appData, disability_status: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none bg-white"
                >
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Step 7: Job Portals */}
        {currentStep === 7 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Supported Job Portals</h2>
              <p className="mt-1 text-sm text-slate-500">
                The agent connects with these platforms to discover verified jobs.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
                <div className="font-bold text-slate-900">LinkedIn</div>
                <span className="mt-1 inline-block rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-800">
                  Ready
                </span>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
                <div className="font-bold text-slate-900">Naukri</div>
                <span className="mt-1 inline-block rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-800">
                  Ready
                </span>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
                <div className="font-bold text-slate-900">Indeed</div>
                <span className="mt-1 inline-block rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-800">
                  Ready
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Step 8: Automation Preferences */}
        {currentStep === 8 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Automation Policy & Controls</h2>
              <p className="mt-1 text-sm text-slate-500">
                Choose how autonomous the application agent should be.
              </p>
            </div>

            <div className="space-y-4">
              <label className="flex items-start gap-3 rounded-xl border border-slate-200 p-4 cursor-pointer hover:bg-slate-50">
                <input
                  type="checkbox"
                  checked={automationSettings.auto_submit}
                  onChange={(e) =>
                    setAutomationSettings({ ...automationSettings, auto_submit: e.target.checked })
                  }
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <div>
                  <div className="text-sm font-semibold text-slate-900">Automatic Submission</div>
                  <div className="text-xs text-slate-500">
                    Automatically submit forms when all required fields have valid answers.
                  </div>
                </div>
              </label>

              <label className="flex items-start gap-3 rounded-xl border border-slate-200 p-4 cursor-pointer hover:bg-slate-50">
                <input
                  type="checkbox"
                  checked={automationSettings.require_human_review}
                  onChange={(e) =>
                    setAutomationSettings({
                      ...automationSettings,
                      require_human_review: e.target.checked,
                    })
                  }
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <div>
                  <div className="text-sm font-semibold text-slate-900">
                    Require Human Review Gate
                  </div>
                  <div className="text-xs text-slate-500">
                    Pause before submitting each application and wait for your manual approval.
                  </div>
                </div>
              </label>
            </div>
          </div>
        )}

        {/* Step 9: Launch */}
        {currentStep === 9 && (
          <div className="space-y-6 text-center py-8">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Onboarding Complete!</h2>
              <p className="mt-2 text-sm text-slate-600 max-w-md mx-auto">
                Your profile, resume, and preferences are configured. Your account has 100 free application credits.
              </p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-8 flex items-center justify-between border-t border-slate-100 pt-6">
          {currentStep > 1 && currentStep !== 3 ? (
            <button
              onClick={() => setCurrentStep(currentStep - 1)}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50 transition"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </button>
          ) : (
            <div />
          )}

          {currentStep !== 3 && (
            <button
              onClick={handleNext}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : currentStep === 9 ? (
                <>
                  Launch Agent Dashboard
                  <Zap className="h-4 w-4" />
                </>
              ) : (
                <>
                  Continue
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
