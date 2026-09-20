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
} from "lucide-react";
import { api } from "@/lib/api/client";
import { Application } from "@/types";
import { formatDate } from "@/lib/utils";

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [reviewLoading, setReviewLoading] = useState(false);

  const fetchApplications = async () => {
    setLoading(true);
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Application History & Tracking
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Track real submission statuses, timestamps, and multi-step browser logs.
          </p>
        </div>

        {/* Filter */}
        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-slate-200 px-3.5 py-2 text-sm focus:border-indigo-600 focus:outline-none bg-white font-medium text-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="submitted">Submitted</option>
            <option value="verification_required">Verification Required</option>
            <option value="needs_human_review">Needs Human Review</option>
            <option value="application_started">In Progress</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

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
                    onClick={() => setSelectedApp(app)}
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
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedApp(app);
                        }}
                        className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                      >
                        Timeline &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Application Timeline Modal */}
      {selectedApp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="relative w-full max-w-xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl">
            <button
              onClick={() => setSelectedApp(null)}
              className="absolute top-5 right-5 p-1 text-slate-400 hover:text-slate-600 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="text-xs font-semibold text-slate-400 uppercase">
              Application #{selectedApp.id}
            </div>
            <h2 className="mt-1 text-lg font-bold text-slate-900">
              {selectedApp.job?.title}
            </h2>
            <div className="text-sm text-slate-600">
              {selectedApp.job?.company} • {selectedApp.job?.location}
            </div>

            <div className="mt-4 flex items-center gap-3">
              <div>{getStatusBadge(selectedApp.status)}</div>
              <span className="text-xs text-slate-400">
                Match: {selectedApp.match_score}%
              </span>
            </div>

            {/* Human Review Gate Actions */}
            {selectedApp.status === "needs_human_review" && (
              <div className="mt-6 rounded-xl border border-indigo-200 bg-indigo-50 p-4">
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
                    <ThumbsUp className="h-3.5 w-3.5" /> Approve Application
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

            {/* Timeline Audit Events */}
            <div className="mt-6">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-4">
                Application Lifecycle Events
              </h4>

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
                <div className="text-xs text-slate-400">
                  Application recorded. Awaiting browser automation events.
                </div>
              )}
            </div>

            {/* Error or Verification Alert */}
            {selectedApp.error_message && (
              <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
                <strong>Error:</strong> {selectedApp.error_message}
              </div>
            )}

            <div className="mt-8 flex justify-end">
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
