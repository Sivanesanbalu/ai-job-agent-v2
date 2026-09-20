"use client";

import React, { useState, useEffect } from "react";
import {
  Send,
  CheckCircle2,
  AlertTriangle,
  Clock,
  XCircle,
  FileText,
  ExternalLink,
  ShieldAlert,
  Loader2,
  X,
  ThumbsUp,
  ThumbsDown,
  UserCheck,
  Check,
  Briefcase,
  Sparkles,
} from "lucide-react";
import { api } from "@/lib/api/client";
import { Application } from "@/types";
import { formatDate } from "@/lib/utils";

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [activeTab, setActiveTab] = useState<"data" | "timeline">("data");
  const [submittingId, setSubmittingId] = useState<number | null>(null);
  const [bulkSubmitting, setBulkSubmitting] = useState(false);
  const [reviewLoading, setReviewLoading] = useState(false);

  const fetchApplications = async () => {
    try {
      const data = await api.applications.list({
        status: statusFilter || undefined,
      });
      setApplications(data);
    } catch (err) {
      console.error("Failed to load applications:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
    const interval = setInterval(fetchApplications, 5000);
    return () => clearInterval(interval);
  }, [statusFilter]);

  const handleSingleSubmit = async (appId: number) => {
    setSubmittingId(appId);
    try {
      await api.applications.submit(appId);
      await fetchApplications();
      if (selectedApp && selectedApp.id === appId) {
        const updated = await api.applications.get(appId);
        setSelectedApp(updated);
      }
    } catch (err) {
      console.error("Failed to submit application:", err);
    } finally {
      setSubmittingId(null);
    }
  };

  const handleBulkSubmit = async () => {
    setBulkSubmitting(true);
    try {
      await api.applications.submitAllReady();
      await fetchApplications();
    } catch (err) {
      console.error("Failed bulk submission:", err);
    } finally {
      setBulkSubmitting(false);
    }
  };

  const handleReviewAction = async (appId: number, action: "approve" | "reject") => {
    setReviewLoading(true);
    try {
      if (action === "approve") await api.applications.approve(appId);
      else await api.applications.reject(appId);
      await fetchApplications();
      setSelectedApp(null);
    } catch (err) {
      console.error(`Failed to ${action} application:`, err);
    } finally {
      setReviewLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "submitted":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" /> Submitted
          </span>
        );
      case "ready_to_submit":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 border border-blue-200">
            <Clock className="h-3 w-3 text-blue-600" /> Ready To Submit
          </span>
        );
      case "verification_required":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 border border-amber-200">
            <ShieldAlert className="h-3 w-3 text-amber-600" /> Verification Required
          </span>
        );
      case "needs_human_review":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 border border-indigo-200">
            <Clock className="h-3 w-3 text-indigo-600" /> Needs Review
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700 border border-rose-200">
            <XCircle className="h-3 w-3 text-rose-600" /> Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700 capitalize">
            {status.replace(/_/g, " ")}
          </span>
        );
    }
  };

  const readyApps = applications.filter(
    (a) => a.status === "ready_to_submit" || a.status === "needs_human_review"
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Application History & Tracking
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Track real submission statuses, applied candidate profiles, screening responses, and audit logs.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-slate-200 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none bg-white font-medium text-slate-700 shadow-xs"
          >
            <option value="">All Statuses</option>
            <option value="ready_to_submit">Ready To Submit</option>
            <option value="submitted">Submitted</option>
            <option value="needs_human_review">Needs Review</option>
            <option value="verification_required">Verification Required</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Bulk Ready Submissions Alert Banner */}
      {readyApps.length > 0 && (
        <div className="rounded-2xl border border-blue-200 bg-linear-to-r from-blue-50 to-indigo-50 p-4 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-xs">
                <Clock className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  {readyApps.length} Application{readyApps.length > 1 ? "s" : ""} Ready To Submit
                </h3>
                <p className="text-xs text-slate-600 mt-0.5">
                  Forms have been prepared with your candidate profile and AI-tailored answers.
                </p>
              </div>
            </div>
            <button
              onClick={handleBulkSubmit}
              disabled={bulkSubmitting}
              className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-blue-700 transition"
            >
              {bulkSubmitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Submit All Ready ({readyApps.length}) &rarr;
            </button>
          </div>
        </div>
      )}

      {/* Applications Table */}
      {loading && applications.length === 0 ? (
        <div className="py-16 text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-indigo-600" />
          <p className="mt-3 text-sm text-slate-500">Loading applications...</p>
        </div>
      ) : applications.length === 0 ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
          <Send className="mx-auto h-12 w-12 text-slate-300" />
          <h3 className="mt-4 text-base font-bold text-slate-900">No applications recorded</h3>
          <p className="mt-1 text-sm text-slate-500">
            When your agent finds matching jobs, applications will automatically be processed here.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs uppercase font-semibold text-slate-500">
                <tr>
                  <th className="px-6 py-3.5">Company & Role</th>
                  <th className="px-6 py-3.5">Source</th>
                  <th className="px-6 py-3.5">Match Score</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5">Date</th>
                  <th className="px-6 py-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app) => (
                  <tr
                    key={app.id}
                    className="hover:bg-slate-50/70 transition cursor-pointer"
                    onClick={() => {
                      setSelectedApp(app);
                      setActiveTab("data");
                    }}
                  >
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-900">{app.job?.title}</div>
                      <div className="text-xs text-slate-500">{app.job?.company} • {app.job?.location}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-semibold uppercase text-slate-700">
                        {app.job?.source}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-bold text-indigo-700">
                      {app.match_score}%
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(app.status)}</td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {formatDate(app.submitted_at || app.created_at)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                        {app.status === "ready_to_submit" && (
                          <button
                            onClick={() => handleSingleSubmit(app.id)}
                            disabled={submittingId === app.id}
                            className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-emerald-700 transition shadow-xs"
                          >
                            {submittingId === app.id ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            ) : (
                              <Send className="h-3.5 w-3.5" />
                            )}
                            Submit Now
                          </button>
                        )}
                        <button
                          onClick={() => {
                            setSelectedApp(app);
                            setActiveTab("data");
                          }}
                          className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold text-indigo-600 hover:bg-indigo-50 transition"
                        >
                          View Data &rarr;
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Application Details & Submission Data Modal */}
      {selectedApp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl">
            <button
              onClick={() => setSelectedApp(null)}
              className="absolute top-5 right-5 p-1 text-slate-400 hover:text-slate-600 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="text-xs font-semibold text-slate-400 uppercase">
              Application #{selectedApp.id}
            </div>
            <h2 className="mt-1 text-xl font-bold text-slate-900">
              {selectedApp.job?.title}
            </h2>
            <div className="text-sm text-slate-600 flex items-center gap-2 mt-0.5">
              <span>{selectedApp.job?.company}</span>
              <span>•</span>
              <span>{selectedApp.job?.location}</span>
              {selectedApp.job?.url && (
                <a
                  href={selectedApp.job.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-indigo-600 hover:underline text-xs"
                >
                  <ExternalLink className="h-3 w-3" /> Job Link
                </a>
              )}
            </div>

            <div className="mt-3 flex items-center gap-3">
              <div>{getStatusBadge(selectedApp.status)}</div>
              <span className="text-xs font-medium text-slate-500">
                Match Score: <strong className="text-indigo-600">{selectedApp.match_score}%</strong>
              </span>
            </div>

            {/* Quick Submit button if ready */}
            {selectedApp.status === "ready_to_submit" && (
              <div className="mt-5 flex items-center justify-between rounded-xl border border-blue-200 bg-blue-50 p-3.5">
                <div>
                  <div className="text-xs font-bold text-blue-900">Form Prepared & Verified</div>
                  <div className="text-xs text-blue-700">Ready for instant submission to company portal.</div>
                </div>
                <button
                  onClick={() => handleSingleSubmit(selectedApp.id)}
                  disabled={submittingId === selectedApp.id}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-700 transition shadow-xs"
                >
                  {submittingId === selectedApp.id ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Check className="h-3.5 w-3.5" />
                  )}
                  Submit Application Now
                </button>
              </div>
            )}

            {/* Human Review Gate Actions */}
            {selectedApp.status === "needs_human_review" && (
              <div className="mt-5 rounded-xl border border-indigo-200 bg-indigo-50 p-4">
                <h4 className="text-xs font-bold text-indigo-900 uppercase">
                  Human Approval Required
                </h4>
                <p className="mt-1 text-xs text-indigo-700">
                  Review this application package before permitting the agent to submit.
                </p>
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={() => handleReviewAction(selectedApp.id, "approve")}
                    disabled={reviewLoading}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 transition"
                  >
                    <ThumbsUp className="h-3.5 w-3.5" /> Approve & Submit
                  </button>
                  <button
                    onClick={() => handleReviewAction(selectedApp.id, "reject")}
                    disabled={reviewLoading}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                  >
                    <ThumbsDown className="h-3.5 w-3.5" /> Reject
                  </button>
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="mt-6 flex border-b border-slate-200">
              <button
                onClick={() => setActiveTab("data")}
                className={`flex items-center gap-1.5 border-b-2 px-4 py-2 text-xs font-bold transition ${
                  activeTab === "data"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <FileText className="h-3.5 w-3.5" /> Applied Form & Candidate Data
              </button>
              <button
                onClick={() => setActiveTab("timeline")}
                className={`flex items-center gap-1.5 border-b-2 px-4 py-2 text-xs font-bold transition ${
                  activeTab === "timeline"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <Clock className="h-3.5 w-3.5" /> Audit Events ({selectedApp.events?.length || 0})
              </button>
            </div>

            {/* Tab 1: Submission Data */}
            {activeTab === "data" && (
              <div className="mt-4 space-y-4">
                {selectedApp.submission_data && Object.keys(selectedApp.submission_data).length > 0 ? (
                  <>
                    {/* Candidate Snapshot */}
                    {selectedApp.submission_data.candidate && (
                      <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                        <div className="text-xs font-bold uppercase text-slate-500 mb-2 flex items-center gap-1.5">
                          <UserCheck className="h-3.5 w-3.5 text-indigo-600" />
                          Candidate Profile Snapshot
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                          <div>
                            <span className="text-slate-400 block">Name:</span>
                            <strong className="text-slate-800">{selectedApp.submission_data.candidate.name || "N/A"}</strong>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Email:</span>
                            <strong className="text-slate-800">{selectedApp.submission_data.candidate.email || "N/A"}</strong>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Phone:</span>
                            <strong className="text-slate-800">{selectedApp.submission_data.candidate.phone || "N/A"}</strong>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Headline:</span>
                            <strong className="text-slate-800">{selectedApp.submission_data.candidate.headline || "N/A"}</strong>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Location:</span>
                            <strong className="text-slate-800">
                              {[selectedApp.submission_data.candidate.city, selectedApp.submission_data.candidate.country].filter(Boolean).join(", ") || "N/A"}
                            </strong>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Experience:</span>
                            <strong className="text-slate-800">{selectedApp.submission_data.candidate.experience_years || 2} Years</strong>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Screening Answers */}
                    {selectedApp.submission_data.screening_answers && (
                      <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                        <div className="text-xs font-bold uppercase text-slate-500 mb-2 flex items-center gap-1.5">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                          AI Screening Responses
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {Object.entries(selectedApp.submission_data.screening_answers).map(([key, val]) => (
                            <div key={key}>
                              <span className="text-slate-400 capitalize block">{key.replace(/_/g, " ")}:</span>
                              <strong className="text-slate-800">{String(val)}</strong>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tailored AI Pitch */}
                    {selectedApp.submission_data.application_pitch && (
                      <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-4">
                        <div className="text-xs font-bold uppercase text-indigo-700 mb-1 flex items-center gap-1.5">
                          <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
                          Tailored Application Pitch
                        </div>
                        <p className="text-xs text-slate-700 italic">
                          "{selectedApp.submission_data.application_pitch}"
                        </p>
                      </div>
                    )}

                    {/* Resume Used */}
                    <div className="flex items-center justify-between text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <span>Resume File Attached:</span>
                      <strong className="text-slate-800">{selectedApp.submission_data.resume_filename || "Active Resume PDF"}</strong>
                    </div>
                  </>
                ) : (
                  <div className="rounded-xl border border-slate-200 p-6 text-center text-xs text-slate-500">
                    Candidate profile and answers are saved automatically as browser automation progresses.
                  </div>
                )}
              </div>
            )}

            {/* Tab 2: Timeline */}
            {activeTab === "timeline" && (
              <div className="mt-4">
                {selectedApp.events && selectedApp.events.length > 0 ? (
                  <div className="relative border-l-2 border-slate-200 ml-3 space-y-6 pl-5">
                    {selectedApp.events.map((ev) => (
                      <div key={ev.id} className="relative">
                        <span className="absolute -left-[27px] top-1 h-3.5 w-3.5 rounded-full border-2 border-white bg-indigo-600 shadow-xs" />
                        <div className="text-xs font-bold text-slate-900">
                          {ev.message}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {formatDate(ev.created_at)} • Stage: {ev.stage || "workflow"}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-slate-400 text-center py-6">
                    Application recorded. Awaiting browser automation events.
                  </div>
                )}
              </div>
            )}

            {/* Error Alert */}
            {selectedApp.error_message && (
              <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
                <strong>Error:</strong> {selectedApp.error_message}
              </div>
            )}

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedApp(null)}
                className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
