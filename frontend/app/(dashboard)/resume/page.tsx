"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  Upload,
  CheckCircle2,
  Trash2,
  Download,
  Sparkles,
  Edit2,
  Save,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { api } from "@/lib/api/client";
import { Resume } from "@/types";
import { formatDate } from "@/lib/utils";

export default function ResumeVaultPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);

  const fetchResumes = async () => {
    setLoading(true);
    try {
      const data = await api.resumes.list();
      setResumes(data);
      if (data.length > 0 && !selectedResume) {
        setSelectedResume(data.find((r) => r.is_active) || data[0]);
      }
    } catch (err: any) {
      setError("Failed to load resumes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setSuccess(null);
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("set_active", "true");

      const uploaded = await api.resumes.upload(formData);
      setSuccess(`Resume '${uploaded.filename}' uploaded and parsed successfully.`);
      await fetchResumes();
      setSelectedResume(uploaded);
    } catch (err: any) {
      setError(err.message || "Failed to upload resume.");
    } finally {
      setUploading(false);
    }
  };

  const handleSetActive = async (id: number) => {
    try {
      await api.resumes.update(id, { is_active: true });
      await fetchResumes();
      setSuccess("Active resume updated for browser automation.");
    } catch (err: any) {
      setError("Failed to update active status.");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this resume?")) return;
    try {
      await api.resumes.delete(id);
      await fetchResumes();
      if (selectedResume?.id === id) {
        setSelectedResume(null);
      }
      setSuccess("Resume removed.");
    } catch (err: any) {
      setError("Failed to delete resume.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Resume Vault
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Upload and manage your tailored resumes. The active resume is automatically attached during applications.
          </p>
        </div>

        {/* Upload Button */}
        <div>
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition">
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Parsing Resume...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Upload New Resume
              </>
            )}
            <input
              type="file"
              accept=".pdf,.docx"
              disabled={uploading}
              onChange={handleUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
          <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" />
          <span>{success}</span>
        </div>
      )}

      {/* Two Column Layout: List & Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Resume List */}
        <div className="space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Stored Versions ({resumes.length})
          </h2>

          {loading ? (
            <div className="py-8 text-center text-sm text-slate-500">
              Loading resumes...
            </div>
          ) : resumes.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center">
              <FileText className="mx-auto h-8 w-8 text-slate-400" />
              <p className="mt-2 text-xs text-slate-500">
                No resumes uploaded yet. Click Upload New Resume to begin.
              </p>
            </div>
          ) : (
            resumes.map((r) => (
              <div
                key={r.id}
                onClick={() => setSelectedResume(r)}
                className={`cursor-pointer rounded-xl border p-4 transition ${
                  selectedResume?.id === r.id
                    ? "border-indigo-600 bg-indigo-50/50 shadow-xs"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2.5">
                    <FileText className="h-5 w-5 text-indigo-600 shrink-0" />
                    <div>
                      <div className="text-sm font-bold text-slate-900 truncate max-w-[160px]">
                        {r.filename}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        {formatDate(r.created_at)} • v{r.version}
                      </div>
                    </div>
                  </div>

                  {r.is_active && (
                    <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 border border-emerald-200">
                      Active
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Right: Parsed Data Viewer */}
        <div className="lg:col-span-2">
          {selectedResume ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    {selectedResume.filename}
                  </h3>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Size: {(selectedResume.file_size / 1024).toFixed(1)} KB • Version {selectedResume.version}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {!selectedResume.is_active && (
                    <button
                      onClick={() => handleSetActive(selectedResume.id)}
                      className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                    >
                      Set As Active
                    </button>
                  )}
                  <a
                    href={api.resumes.getDownloadUrl(selectedResume.id)}
                    target="_blank"
                    className="p-2 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition"
                    title="Download original file"
                  >
                    <Download className="h-4 w-4" />
                  </a>
                  <button
                    onClick={() => handleDelete(selectedResume.id)}
                    className="p-2 text-rose-500 hover:text-rose-700 rounded-lg hover:bg-rose-50 transition"
                    title="Delete resume"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Extracted Profile Details */}
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Extracted Candidate Info
                  </h4>
                  <div className="mt-2 grid grid-cols-2 gap-3 text-xs bg-slate-50 p-4 rounded-xl border border-slate-100">
                    <div>
                      <span className="text-slate-500">Name:</span>{" "}
                      <span className="font-semibold text-slate-900">
                        {selectedResume.parsed_data.name || "N/A"}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Email:</span>{" "}
                      <span className="font-semibold text-slate-900">
                        {selectedResume.parsed_data.email || "N/A"}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Phone:</span>{" "}
                      <span className="font-semibold text-slate-900">
                        {selectedResume.parsed_data.phone || "N/A"}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Experience:</span>{" "}
                      <span className="font-semibold text-slate-900">
                        {selectedResume.parsed_data.experience_years || 0} years
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Extracted Technical Skills
                  </h4>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(selectedResume.parsed_data.skills || []).map(
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

                {selectedResume.parsed_data.education && (
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Education
                    </h4>
                    <p className="mt-1 text-sm text-slate-800">
                      {selectedResume.parsed_data.education}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center rounded-2xl border border-slate-200 bg-white text-sm text-slate-400">
              Select a resume to inspect its extracted details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
